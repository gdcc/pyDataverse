import io
from pathlib import Path
from typing import IO, Optional, Union

from ...models.file.filemeta import UploadBody


def file_input(
    file: Union[str, Path, IO[str], IO[bytes]],
    metadata: Optional[UploadBody] = None,
) -> dict[str, IO[bytes]]:
    """Convert various file input types to a format suitable for HTTP requests.

    This function takes different types of file inputs (file paths as strings,
    Path objects, or file-like objects) and converts them to a dictionary format
    that can be used with HTTP request libraries like requests.

    Args:
        file: File input - can be a string path, Path object, or file-like object
              with a read() method.

    Returns:
        dict: Dictionary with 'file' key containing the file object ready for upload.
    """
    if isinstance(file, str):
        return {"file": open(file, "rb")}
    elif isinstance(file, Path):
        return {"file": open(file, "rb")}
    elif isinstance(file, (io.StringIO, io.BytesIO)):
        assert metadata is not None, (
            "Metadata is required for file-like objects. You have to at least proviee the UploadBody object with a filename. Otherwise, it is impossible to determine the filename for the file."
        )

        setattr(file, "name", metadata.filename)
        return {"file": file}  # type: ignore[dict-item]
    elif isinstance(file, io.IOBase):
        return {"file": file}  # type: ignore[dict-item]

    raise ValueError(f"Invalid file type: {type(file)}")
