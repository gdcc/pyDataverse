import warnings
from typing import Any, Dict, List, Literal, Optional, Set, Union, overload
from urllib.parse import parse_qs, urlparse

from pyDataverse.models.file import update

# Suppress pkg_resources deprecation warnings from fs package
# Must be before fs import to suppress warnings during import
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fs")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

import pandas as pd  # noqa: E402
from cachetools import TTLCache  # noqa: E402
from fs.base import FS  # noqa: E402
from typing_extensions import Self  # noqa: E402

from ..api import DataAccessApi, NativeApi  # noqa: E402
from ..models.dataset.edit_get import DataFile, File, GetDatasetResponse  # noqa: E402
from ..models.file.filemeta import UploadBody  # noqa: E402
from .reader import DataverseFileReader  # noqa: E402
from .tab import TABULAR_MIME_TYPES, TabSpecs  # noqa: E402
from .writer import DataverseFileWriter  # noqa: E402


class Info(DataFile):
    @property
    def raw(self) -> dict:
        return self.model_dump()


class DataverseFS(FS):
    """
    A PyFilesystem2 implementation for Dataverse datasets.

    Provides filesystem-like access to Dataverse datasets, allowing you to
    browse, read, write, and manage files within a dataset using standard
    filesystem operations.

    Attributes:
        base_url: The base URL of the Dataverse instance
        identifier: Dataset identifier (DOI or numeric ID)
        version: Dataset version to access
        native_api: Native API client for Dataverse operations
        data_access_api: Data Access API client for file downloads

    Example:
        >>> # Using from_url
        >>> fs = DataverseFS.from_url(
        ...     "https://demo.dataverse.org/dataset.xhtml?persistentId=doi:10.5072/FK2/ABCDEF",
        ...     api_token="your-token"
        ... )
        >>>
        >>> # Using direct initialization
        >>> fs = DataverseFS(
        ...     base_url="https://demo.dataverse.org",
        ...     identifier="doi:10.5072/FK2/ABCDEF",
        ...     api_token="your-token"
        ... )
        >>>
        >>> # Read a file
        >>> with fs.openbin("data/file.csv", "rb") as f:
        ...     data = f.read()
        >>>
        >>> # Write a file
        >>> with fs.openbin("data/newfile.csv", "wb") as f:
        ...     f.write(b"column1,column2\\n")
        ...     f.write(b"value1,value2\\n")
    """

    def __init__(
        self,
        base_url: str,
        identifier: Union[str, int],
        version: Union[
            str, Literal[":latest", ":latest-published", ":draft"]
        ] = ":latest",
        api_token: Optional[str] = None,
        cache_ttl: int = 60,
        native_api: Optional[NativeApi] = None,
        data_access_api: Optional[DataAccessApi] = None,
    ):
        """
        Initialize a DataverseFS instance.

        Args:
            base_url: Base URL of the Dataverse instance (e.g., "https://demo.dataverse.org")
            identifier: Dataset identifier (DOI string or numeric database ID)
            version: Dataset version to access. Can be a version number, or one of:
                ":latest" (default) - latest published or draft version
                ":latest-published" - latest published version only
                ":draft" - draft version
            api_token: Optional API token for authentication
            cache_ttl: Cache TTL in seconds (default: 60, set to 0 to disable)
            native_api: Optional existing NativeApi instance to reuse
            data_access_api: Optional existing DataAccessApi instance to reuse
        """
        super().__init__()

        self.base_url = base_url
        self.identifier = identifier
        self.version = version
        self.native_api = native_api or NativeApi(
            base_url=base_url,
            api_token=api_token,
        )
        self.data_access_api = data_access_api or DataAccessApi.from_api(
            self.native_api
        )
        self._cache = TTLCache(maxsize=1, ttl=cache_ttl) if cache_ttl > 0 else {}

    @classmethod
    def from_url(cls, url: str, api_token: Optional[str] = None) -> Self:
        """
        Create a DataverseFS instance from a Dataverse dataset URL.

        Parses standard Dataverse dataset URLs to extract connection details.

        Args:
            url: Dataverse dataset URL. Supported formats:
                - https://host/dataset.xhtml?persistentId=doi:10.xxxxx
                - https://host/dataset.xhtml?id=12345
                - Optional: &version=1.0 or &version=:draft
            api_token: Optional API token for authentication

        Returns:
            DataverseFS instance configured for the specified dataset

        Raises:
            ValueError: If URL format is invalid, scheme is not http/https,
                hostname is missing, or neither persistentId nor id is provided

        Example:
            >>> fs = DataverseFS.from_url(
            ...     "https://demo.dataverse.org/dataset.xhtml?persistentId=doi:10.5072/FK2/ABC",
            ...     api_token="token"
            ... )
        """
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            raise ValueError(
                f"Invalid URL scheme '{parsed.scheme}': must be 'http' or 'https'"
            )

        if not parsed.netloc:
            raise ValueError(f"Missing hostname in URL: {url}")

        params = parse_qs(parsed.query)
        persistent_id = params.get("persistentId", [None])[0]
        id_param = params.get("id", [None])[0]
        version = params.get("version", [":latest"])[0]

        if not persistent_id and not id_param:
            raise ValueError(
                "URL must contain either 'persistentId' or 'id' query parameter. "
                f"Example: {parsed.scheme}://{parsed.netloc}/dataset.xhtml?persistentId=doi:..."
            )

        if persistent_id and id_param:
            raise ValueError(
                "URL must contain only one of 'persistentId' or 'id', not both"
            )

        identifier = persistent_id if persistent_id else int(id_param)  # type: ignore
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        return cls(
            base_url=base_url,
            identifier=identifier,
            version=version,
            api_token=api_token,
        )

    def getinfo(self, path: str, namespace: Optional[str] = None) -> Info:
        """
        Get information about a file.

        Args:
            path: Path to the file (e.g., "data/file.csv")
            namespace: Optional namespace for additional info (not currently used)

        Returns:
            Info object with file metadata

        Raises:
            FileNotFoundError: If file doesn't exist

        Example:
            >>> fs = DataverseFS(base_url="...", identifier="...")
            >>> info = fs.getinfo("data/myfile.csv")
            >>> print(info.size)
        """
        file = self._find_file(path)

        if file.data_file is None:
            raise FileNotFoundError(f"File '{path}' has no metadata")

        return Info(**file.data_file.model_dump())

    def listdir(self, path: str) -> List[str]:
        """
        List immediate children (files and directories) at a given path.

        Args:
            path: Directory path to list (e.g., "/" or "" for root, "dir1/dir2" for subdirectory)

        Returns:
            Sorted list of immediate children names

        Example:
            >>> fs = DataverseFS(base_url="...", identifier="...")
            >>> fs.listdir("/")  # List root directory
            ['data', 'README.txt']
            >>> fs.listdir("data")  # List subdirectory
            ['file1.csv', 'file2.csv']
        """
        dataset = self._get_dataset()
        path = path.strip("/")

        children: Set[str] = set()

        assert dataset.files is not None

        for file in dataset.files:
            file_path = self._build_file_path(file)

            if not path:
                children.add(file_path.split("/")[0])
                continue

            if file_path.startswith(path + "/"):
                relative_path = file_path[len(path) + 1 :]
                immediate_child = relative_path.split("/")[0]
                children.add(immediate_child)

        return sorted(children)

    def makedir(
        self, path: str, permissions: Optional[int] = None, recreate: bool = False
    ):
        """
        Create a directory.

        Note: Directories in Dataverse are implicit (based on file paths).
        This operation is not supported as a standalone action.

        Args:
            path: Directory path to create
            permissions: Permissions (ignored)
            recreate: Whether to recreate if exists (ignored)

        Raises:
            NotImplementedError: Always raised (directories are implicit)
        """
        raise NotImplementedError(
            "Cannot create directories in DataverseFS. "
            "Directories are created implicitly when uploading files with directory paths."
        )

    @overload
    def openbin(
        self,
        path: str,
        mode: Literal["r", "rb"] = "r",
        buffering: int = -1,
        metadata: Optional[UploadBody] = None,
    ) -> DataverseFileReader: ...

    @overload
    def openbin(
        self,
        path: str,
        mode: Literal["w", "wb"],
        buffering: int = -1,
        metadata: Optional[UploadBody] = None,
    ) -> DataverseFileWriter: ...

    def openbin(
        self,
        path: str,
        mode: Literal["r", "rb", "w", "wb"] = "r",
        buffering: int = -1,
        metadata: Optional[UploadBody] = None,
    ) -> Union[DataverseFileReader, DataverseFileWriter]:
        """
        Open a file in binary mode.

        Args:
            path: Path to the file in the dataset
            mode: File mode. Supported modes:
                - 'r', 'rb': Read (default)
                - 'w', 'wb': Write (creates new file or replaces existing)
            buffering: Buffering policy (ignored)
            **metadata: File metadata

        Returns:
            DataverseFileReader or DataverseFileWriter: File-like object

        Raises:
            FileNotFoundError: If file doesn't exist (read mode)
            ValueError: If file has no ID (read mode) or invalid mode

        Example:
            >>> # Read a file
            >>> fs = DataverseFS(base_url="...", identifier="...")
            >>> with fs.openbin("data/file.csv") as f:
            ...     content = f.read()
            >>>
            >>> # Write a new file or replace existing
            >>> with fs.openbin("data/newfile.csv", mode="wb") as f:
            ...     f.write(b"data")
        """
        if mode in ("r", "rb"):
            return self._openbin_read(path, mode=mode)
        elif mode in ("w", "wb"):
            return self._openbin_write(path, metadata=metadata)
        else:
            raise ValueError(
                f"Invalid mode '{mode}'. Supported modes: 'r', 'rb', 'w', 'wb'"
            )

    def _openbin_read(
        self,
        path: str,
        mode: Literal["r", "rb"] = "r",
    ) -> DataverseFileReader:
        """
        Open a file for reading.

        Args:
            path: Path to the file in the dataset

        Returns:
            DataverseFileReader: File-like object for reading

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file has no ID
        """
        file = self._find_file(path)

        if file.data_file is None or file.data_file.id is None:
            raise ValueError(f"File '{path}' has no file ID")

        return DataverseFileReader(self.data_access_api, file.data_file.id, mode=mode)

    def _openbin_write(
        self,
        path: str,
        metadata: Optional[UploadBody] = None,
    ) -> DataverseFileWriter:
        """
        Open a file for writing.

        Creates a new file or replaces an existing one.

        Args:
            path: Path to the file in the dataset
            **options: Additional options, may include 'metadata' dict

        Returns:
            DataverseFileWriter: File-like object for writing
        """
        path = path.strip("/")

        # Split path into directory and filename
        if "/" in path:
            directory_label, label = path.rsplit("/", 1)
        else:
            directory_label = ""
            label = path

        if metadata is None:
            metadata = UploadBody(
                directory_label=directory_label if directory_label else None,
                filename=label,
            )

        # Check if file exists to get its ID for replacement
        file_id = None
        try:
            existing_file = self._find_file(path)
            if existing_file.data_file:
                file_id = existing_file.data_file.id
        except FileNotFoundError:
            pass

        # Create writer (replaces file if it exists)
        writer = DataverseFileWriter(
            native_api=self.native_api,
            ds_identifier=self.identifier,
            metadata=metadata,
            file_identifier=file_id,
        )

        # Clear cache to ensure fresh data on next read
        self._cache.clear()

        return writer

    def stream_tabular(
        self,
        path: str,
        api_token: Optional[str],
        chunk_size: int = 10_000,
        no_header: bool = False,
        sep: str = ",",
        **kwargs,
    ):
        """
        Stream a tabular file as a chunked pandas DataFrame iterator.

        Args:
            path: Path to the file.
            chunk_size: Number of rows per chunk.
            no_header: If True, the file has no header row. Column names will
                be integers (0, 1, 2, ...). Default is False.
            sep: Delimiter to use. Default is ",".
            **kwargs: Additional keyword arguments passed to pandas.read_csv().
                Common options include:
                - usecols: List of column names or indices to read
                - dtype: Dictionary of column names to data types
                - na_values: Values to recognize as NA/NaN
                - skiprows: Number of rows to skip at the start
                - nrows: Number of rows to read
                - encoding: File encoding (e.g., 'utf-8', 'latin-1')
                - delimiter: Alternative to sep
                - header: Override header behavior (overrides no_header if provided)
                See pandas.read_csv() documentation for full list.

        Yields:
            pd.DataFrame: Chunked DataFrame for each portion of the file.

        Example:
            >>> # CSV with header (default)
            >>> for chunk in fs.stream_tabular("data/file.csv"):
            ...     print(chunk.columns)  # Uses first row as column names
            >>>
            >>> # CSV without header
            >>> for chunk in fs.stream_tabular("data/file.csv", no_header=True):
            ...     print(chunk.columns)  # Uses integer column names (0, 1, 2, ...)
            >>>
            >>> # Using pandas kwargs
            >>> for chunk in fs.stream_tabular(
            ...     "data/file.csv",
            ...     usecols=[0, 1, 2],
            ...     dtype={"col1": str, "col2": int},
            ... ):
            ...     process(chunk)
        """
        download_link = self._get_tabular_download_link(path)

        # Get tab specs
        tab_specs = self._get_tab_specs(path)
        if tab_specs is None:
            raise ValueError(f"File '{path}' has no tab specs")

        request_headers = {}
        if api_token is not None:
            request_headers["X-Dataverse-key"] = api_token

        # Build read_csv arguments
        read_kwargs: Dict[str, Any] = {
            "chunksize": chunk_size,
            "delimiter": tab_specs.delimiter,
        }

        # Handle header parameter
        if "header" not in kwargs:
            read_kwargs["header"] = None if no_header else 0

        # Merge with user-provided kwargs (user kwargs take precedence)
        read_kwargs.update(kwargs)

        if tab_specs.tab_type == "spreadsheet":
            raise ValueError("Spreadsheet files are not supported for streaming")

        return pd.read_csv(
            download_link,
            storage_options=request_headers,
            **read_kwargs,
        )

    def open_tabular(
        self,
        path: str,
        api_token: Optional[str],
        no_header: bool = False,
        **kwargs,
    ):
        """
        Open the entire tabular file as a pandas DataFrame.

        Args:
            path: Path to the file.
            sep: Delimiter to use. Default is ",".
            no_header: If True, the file has no header row. Column names will
                be integers (0, 1, 2, ...). Default is False.
            **kwargs: Additional keyword arguments passed to pandas.read_csv().
                Common options include:
                - usecols: List of column names or indices to read
                - dtype: Dictionary of column names to data types
                - na_values: Values to recognize as NA/NaN
                - skiprows: Number of rows to skip at the start
                - nrows: Number of rows to read
                - encoding: File encoding (e.g., 'utf-8', 'latin-1')
                - delimiter: Alternative to sep
                - header: Override header behavior (overrides no_header if provided)
                See pandas.read_csv() documentation for full list.

        Returns:
            pd.DataFrame: The loaded DataFrame.

        Example:
            >>> # CSV with header (default)
            >>> df = fs.open_tabular("data/file.csv")
            >>> print(df.columns)  # Uses first row as column names
            >>>
            >>> # CSV without header
            >>> df = fs.open_tabular("data/file.csv", no_header=True)
            >>> print(df.columns)  # Uses integer column names (0, 1, 2, ...)
            >>> # Optionally rename columns after loading
            >>> df.columns = ["col1", "col2", "col3"]
            >>>
            >>> # Using pandas kwargs
            >>> df = fs.open_tabular(
            ...     "data/file.csv",
            ...     usecols=["col1", "col2"],
            ...     dtype={"col1": str, "col2": int},
            ...     na_values=["N/A", "null"],
            ... )
        """
        download_link = self._get_tabular_download_link(path)

        # Build read_csv arguments
        read_kwargs: Dict[str, Any] = {}

        # Handle header parameter
        if "header" not in kwargs:
            read_kwargs["header"] = None if no_header else 0

        # Merge with user-provided kwargs (user kwargs take precedence)
        read_kwargs.update(kwargs)
        tab_specs = self._get_tab_specs(path)

        if tab_specs is None:
            raise ValueError(f"File '{path}' has no tab specs")

        return tab_specs.parse(
            download_link,
            api_token=api_token,
            **read_kwargs,
        )

    def _get_tabular_download_link(self, path: str) -> str:
        """
        Helper to validate file is tabular and return the download link.

        Args:
            path (str): Path to the file.

        Returns:
            str: Direct download URL for the file.
        """
        if "dataset" not in self._cache:
            self._cache["dataset"] = self._get_dataset()
        file = self._find_file(path)

        # Check if file is tabular
        if file.data_file is None or file.data_file.tabular_data is None:
            raise ValueError(f"File '{path}' is not tabular")

        assert file.data_file.id is not None, f"File '{path}' has no file ID"

        return self.data_access_api.get_datafile_download_url(
            file.data_file.id,
        )

    def _get_tab_specs(self, path: str) -> Optional[TabSpecs]:
        """
        Get the tab specs for a file.
        """
        file = self._find_file(path)
        if file.data_file is None or file.data_file.content_type is None:
            raise ValueError(f"File '{path}' has no content type")

        if file.data_file.content_type not in TABULAR_MIME_TYPES:
            raise ValueError(
                f"File '{path}' may not be tabular or not supported by pyDataverse. Please use the 'open' method instead."
            )

        return TABULAR_MIME_TYPES[file.data_file.content_type]

    def remove(self, path: str):
        """
        Delete a file from the dataset.

        Args:
            path: Path to the file to delete

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file has no ID

        Example:
            >>> fs = DataverseFS(base_url="...", identifier="...", api_token="...")
            >>> fs.remove("data/old_file.csv")
        """
        file = self._find_file(path)

        if file.data_file is None or file.data_file.id is None:
            raise ValueError(f"File '{path}' has no file ID")

        self.native_api.delete_datafile(file.data_file.id)
        self._cache.clear()

    def removedir(self, path: str):
        """
        Remove a directory.

        Note: Directories in Dataverse are implicit and cannot be deleted directly.
        Files must be removed individually.

        Args:
            path: Directory path to remove

        Raises:
            NotImplementedError: Always raised (directories cannot be deleted)
        """
        raise NotImplementedError(
            "Cannot remove directories in DataverseFS. "
            "Directories are implicit and disappear when all contained files are removed."
        )

    def setinfo(self, path: str, info: update.UpdateBody):
        """
        Update file metadata.

        Args:
            path: Path to the file
            info: File metadata to update

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file has no ID

        Example:
            >>> from pyDataverse.models.file.filemeta import UploadBody
            >>> fs = DataverseFS(base_url="...", identifier="...", api_token="...")
            >>> metadata = UploadBody(description="Updated description")
            >>> fs.setinfo("data/file.csv", metadata)
        """
        file = self._find_file(path)

        if file.data_file is None or file.data_file.id is None:
            raise ValueError(f"File '{path}' has no file ID")

        self.native_api.update_datafile_metadata(file.data_file.id, metadata=info)
        self._cache.clear()

    def _get_dataset(self) -> GetDatasetResponse:
        """Fetch dataset metadata from Dataverse."""
        if "dataset" in self._cache:
            return self._cache["dataset"]

        dataset = self.native_api.get_dataset(self.identifier, self.version)

        if dataset.files is None:
            raise FileNotFoundError(
                f"Dataset {self.identifier} (version {self.version}) contains no files"
            )

        self._cache["dataset"] = dataset
        return dataset

    @staticmethod
    def _build_file_path(file: File) -> str:
        """Build full path for a file from its metadata."""
        return "/".join(filter(None, [file.directory_label, file.label]))

    def _find_file(self, path: str) -> File:
        """Find a file by its path in the dataset."""
        dataset = self._get_dataset()
        path = path.strip("/")

        assert dataset.files is not None

        for file in dataset.files:
            if self._build_file_path(file) == path:
                if file.data_file is None:
                    raise FileNotFoundError(
                        f"File '{path}' exists but has no data_file metadata"
                    )
                return file

        raise FileNotFoundError(f"File not found: {path}")
