import base64
import io
from typing import Annotated, List, Optional, Union

import fitz
import nbformat
from fastmcp import Context
from fastmcp.dependencies import CurrentContext
from mcp.types import BlobResourceContents, EmbeddedResource, ImageContent, TextContent
from nbconvert import ScriptExporter
from PIL import Image
from pydantic import AnyUrl
from toon_format import encode

from .utils import ensure_dataverse

# Maximum file size allowed for reading (20 MB)
MAX_FILE_SIZE = 20 * 1024 * 1024

# Maximum size for base64-encoded image data (1 MB)
MAX_IMAGE_SIZE = 1024 * 1024

# MIME types that should be returned as binary blobs
BLOB_MIME_TYPES = {
    # Document formats
    "application/msword",  # .doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/vnd.oasis.opendocument.text",  # .odt
    #
    # Spreadsheet formats
    #
    "application/vnd.ms-excel",  # .xls
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.oasis.opendocument.spreadsheet",  # .ods
    #
    # Presentation formats
    #
    "application/vnd.ms-powerpoint",  # .ppt
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
    #
    # Archive formats
    #
    "application/zip",
    "application/gzip",
    "application/x-tar",
    "application/x-7z-compressed",
    "application/x-rar-compressed",
    #
    # Scientific data formats
    #
    "application/x-netcdf",
    "application/x-hdf",
    "application/x-hdf5",
    #
    # Database formats
    #
    "application/x-sqlite3",
    "application/vnd.sqlite3",
    "application/x-parquet",
    #
    # Generic binary
    #
    "application/octet-stream",
}

# MIME types for image files
IMAGE_MIME_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    "image/tiff",
    "image/bmp",
]

# PDF MIME type
PDF_MIME_TYPE = "application/pdf"
IPYNB_MIME_TYPE = "application/x-ipynb+json"


def read_file(
    identifier: Annotated[
        Union[str, int],
        "Dataset identifier: persistent identifier (string) or Dataverse database ID (integer).",
    ],
    path: Annotated[
        str,
        "Full path to the file within the dataset (e.g., 'data/file.csv').",
    ],
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse this MCP server is connected to by default.",
    ] = None,
    ctx: Context = CurrentContext(),
) -> Union[ImageContent, List[TextContent], EmbeddedResource, TextContent]:
    """
    Read a file from a Dataverse dataset and return it in an appropriate format.

    This function handles different file types:
    - Images: Returns as ImageContent with base64-encoded data
    - PDFs: Extracts text from all pages and returns as TextContent list
    - Binary files: Returns as EmbeddedResource with base64-encoded blob
    - Text files: Returns as plain text string

    Args:
        identifier: Dataset identifier (persistent ID like "doi:10.123/456" or integer ID)
        path: Full path to the file within the dataset
        ctx: MCP context (automatically injected)

    Returns:
        Union[ImageContent, List[TextContent], EmbeddedResource, str]:
            - ImageContent for image files
            - List[TextContent] for PDF files (one per page)
            - EmbeddedResource for binary files
            - str for plain text files

    Raises:
        RuntimeError: If file exceeds MAX_FILE_SIZE or Dataverse is not configured
        KeyError: If the file path is not found in the dataset
        ValueError: If the file cannot be read or processed

    Example:
        >>> # Read an image file
        >>> image_content = read_file("doi:10.123/456", "images/photo.jpg")
        >>>
        >>> # Read a PDF file
        >>> pdf_pages = read_file("doi:10.123/456", "documents/report.pdf")
        >>>
        >>> # Read a text file
        >>> text = read_file("doi:10.123/456", "data/readme.txt")
    """
    file = _get_file_from_dataset(identifier, path, ctx, base_url=base_url)

    # Check file size limit
    if file.size > MAX_FILE_SIZE:
        raise RuntimeError(
            f"File '{path}' exceeds maximum size of {MAX_FILE_SIZE / (1024 * 1024):.0f} MB"
        )

    # Handle images
    if file.content_type in IMAGE_MIME_TYPES:
        file_bytes = _read_file_bytes(file)
        compressed_bytes, mime_type = _compress_image_if_needed(
            file_bytes, file.content_type
        )
        return ImageContent(
            type="image",
            data=base64.b64encode(compressed_bytes).decode("utf-8"),
            mimeType=mime_type,
        )

    # Handle IPYNB files
    if file.content_type == IPYNB_MIME_TYPE:
        contents = file.open("r").read()
        nb = nbformat.reads(contents, as_version=4)
        exporter = ScriptExporter()
        body, _ = exporter.from_notebook_node(nb)
        return TextContent(
            type="text",
            text=body,
        )

    # Handle PDFs
    if file.content_type == PDF_MIME_TYPE:
        file_bytes = _read_file_bytes(file)
        return _extract_pdf_text(file_bytes)

    # Handle binary files
    if file.content_type in BLOB_MIME_TYPES:
        file_bytes = _read_file_bytes(file)
        return EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=AnyUrl(file.url),
                mimeType=file.content_type,
                blob=base64.b64encode(file_bytes).decode("utf-8"),
            ),
        )

    # Handle text files (default)
    return TextContent(
        type="text",
        text=file.open("r").read(),  # pyright: ignore[reportArgumentType]
    )


def read_tabular(
    identifier: Annotated[
        Union[str, int],
        "Dataset identifier: persistent identifier (string) or Dataverse database ID (integer).",
    ],
    path: Annotated[
        str,
        "Full path to the tabular file within the dataset (e.g., 'data/file.csv').",
    ],
    summarize: Annotated[
        bool,
        "If True, return statistical summary (describe()) instead of data rows.",
    ] = False,
    n_rows: Annotated[
        Optional[int],
        "Number of rows to read. If None, reads entire file. Ignored if summarize=True.",
    ] = None,
    read_kwargs: Annotated[
        Optional[dict],
        "Additional keyword arguments passed to pandas read_csv/read_excel. "
        "Delimiters are automatically detected.",
    ] = None,
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse this MCP server is connected to by default.",
    ] = None,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Read a tabular file (CSV, TSV, Excel, etc.) from a Dataverse dataset.

    This function loads tabular data using pandas and returns it in a structured format.
    It supports reading partial data (first N rows), full data, or statistical summaries.

    Args:
        identifier: Dataset identifier (persistent ID like "doi:10.123/456" or integer ID)
        path: Full path to the tabular file within the dataset
        summarize: If True, return statistical summary instead of actual data
        n_rows: Number of rows to read (only used if summarize=False)
        read_kwargs: Additional arguments for pandas read_csv/read_excel
            (e.g., {'sep': ';', 'encoding': 'utf-8'})
        ctx: MCP context (automatically injected)

    Returns:
        str: JSON-encoded string containing the data as a list of records
            (or summary statistics if summarize=True)

    Raises:
        RuntimeError: If Dataverse is not configured in the context
        KeyError: If the file path is not found in the dataset
        ValueError: If the file is not tabular or cannot be parsed

    Example:
        >>> # Read first 100 rows
        >>> data = read_tabular("doi:10.123/456", "data/file.csv", n_rows=100)
        >>>
        >>> # Get statistical summary
        >>> summary = read_tabular("doi:10.123/456", "data/file.csv", summarize=True)
        >>>
        >>> # Read with custom pandas options
        >>> data = read_tabular(
        ...     "doi:10.123/456",
        ...     "data/file.csv",
        ...     read_kwargs={"sep": ";", "encoding": "latin-1"}
        ... )
    """
    file = _get_file_from_dataset(identifier, path, ctx, base_url=base_url)
    read_kwargs = read_kwargs or {}

    # Determine reading strategy based on parameters
    if summarize:
        # Read entire file and compute statistics
        df = file.open_tabular(**read_kwargs).describe()
    elif n_rows is not None:
        # Read only first n_rows
        df = file.open_tabular(nrows=n_rows, **read_kwargs)
    else:
        # Read entire file
        df = file.open_tabular(**read_kwargs)

    # Convert DataFrame to list of records and encode
    return encode(df.to_dict(orient="records"))


def tabular_schema(
    identifier: Annotated[
        Union[str, int],
        "Dataset identifier: persistent identifier (string) or Dataverse ID (integer).",
    ],
    path: Annotated[
        str,
        "Full path to the tabular file within the dataset (e.g., 'data/file.csv').",
    ],
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse this MCP server is connected to by default.",
    ] = None,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Get the schema information for a tabular file.

    Returns metadata about the columns in a tabular file, including column names,
    data types, and other schema information.

    Args:
        identifier: Dataset identifier (persistent ID like "doi:10.123/456" or integer ID)
        path: Full path to the tabular file within the dataset
        ctx: MCP context (automatically injected)

    Returns:
        str: JSON-encoded string containing the schema information

    Raises:
        RuntimeError: If Dataverse is not configured in the context
        KeyError: If the file path is not found in the dataset
        AttributeError: If the file does not have schema information

    Example:
        >>> schema = tabular_schema("doi:10.123/456", "data/file.csv")
        >>> # Returns schema with column names, types, etc.
    """
    file = _get_file_from_dataset(identifier, path, ctx, base_url=base_url)
    return encode(file.tabular_schema)


def _read_file_bytes(file) -> bytes:
    """
    Read file contents as bytes.

    Args:
        file: The file object to read from

    Returns:
        bytes: The file contents as bytes
    """
    with file.open("rb") as f:
        return f.read()


def _extract_pdf_text(file_bytes: bytes) -> List[TextContent]:
    """
    Extract text content from a PDF file.

    Args:
        file_bytes: The PDF file contents as bytes

    Returns:
        List[TextContent]: List of text content objects, one per page
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    results = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        results.append(
            TextContent(
                type="text",
                text=f"Page {page_num + 1}:\n{text}",
            )
        )

    return results


def _get_file_from_dataset(
    identifier: Union[str, int],
    path: str,
    ctx: Context,
    base_url: Optional[str] = None,
):
    """
    Retrieve a file object from a Dataverse dataset.

    Args:
        identifier: Dataset identifier (persistent ID or integer ID)
        path: Full path to the file within the dataset
        ctx: MCP context

    Returns:
        File: The file object from the dataset

    Raises:
        RuntimeError: If Dataverse is not configured in the context
        KeyError: If the file path is not found in the dataset
    """
    dataverse = ensure_dataverse(ctx, base_url=base_url)
    dataset = dataverse.fetch_dataset(identifier=identifier)
    return dataset.files[path]


def _compress_image_if_needed(file_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    """
    Compress an image if its base64-encoded size exceeds MAX_IMAGE_SIZE.

    Args:
        file_bytes: The original image bytes
        mime_type: The MIME type of the image

    Returns:
        tuple[bytes, str]: Compressed image bytes and updated MIME type
    """
    # Check if base64-encoded size exceeds limit
    # Base64 encoding increases size by ~33%, so check raw size * 1.34
    if len(file_bytes) * 1.34 <= MAX_IMAGE_SIZE:
        return file_bytes, mime_type

    try:
        # Open image
        img = Image.open(io.BytesIO(file_bytes))

        # Convert RGBA/LA/P to RGB for JPEG compatibility
        if img.mode in ("RGBA", "LA", "P"):
            # Create white background
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            rgb_img.paste(
                img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None
            )
            img = rgb_img
        elif img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Use JPEG format for better compression
        output_format = "JPEG"
        output_mime = "image/jpeg"

        # Binary search for optimal quality
        min_quality = 10
        max_quality = 95
        best_bytes = file_bytes
        best_mime = mime_type

        while min_quality <= max_quality:
            quality = (min_quality + max_quality) // 2

            output = io.BytesIO()
            img.save(output, format=output_format, quality=quality, optimize=True)
            compressed_bytes = output.getvalue()

            # Check base64-encoded size
            base64_size = len(base64.b64encode(compressed_bytes))

            if base64_size <= MAX_IMAGE_SIZE:
                # This quality works, try higher
                best_bytes = compressed_bytes
                best_mime = output_mime
                min_quality = quality + 1
            else:
                # Too large, reduce quality
                max_quality = quality - 1

        # If we couldn't get under limit, resize the image
        if len(base64.b64encode(best_bytes)) > MAX_IMAGE_SIZE:
            # Calculate scale factor needed
            current_size = len(base64.b64encode(best_bytes))
            scale_factor = (MAX_IMAGE_SIZE / current_size) ** 0.5

            new_size = (
                int(img.size[0] * scale_factor),
                int(img.size[1] * scale_factor),
            )
            img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

            output = io.BytesIO()
            img_resized.save(output, format=output_format, quality=75, optimize=True)
            best_bytes = output.getvalue()
            best_mime = output_mime

        return best_bytes, best_mime

    except Exception:
        # If compression fails, return original
        return file_bytes, mime_type
