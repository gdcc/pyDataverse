from typing import Any, Dict, List, Literal, Optional, Union, overload
from urllib.parse import parse_qs, urlparse

import pandas as pd
from cachetools import TTLCache
from fsspec.spec import AbstractFileSystem
from typing_extensions import Self

from pyDataverse.models.file import update

from ..api import DataAccessApi, NativeApi
from ..models.dataset.edit_get import DataFile, File, GetDatasetResponse
from ..models.file.filemeta import UploadBody
from .reader import DataverseFileReader
from .tab import TABULAR_MIME_TYPES, TabSpecs
from .writer import DataverseFileWriter, DataverseTextIO


class Info(DataFile):
    @property
    def raw(self) -> dict:
        return self.model_dump()


class DataverseFS(AbstractFileSystem):
    """
    An fsspec filesystem implementation for Dataverse datasets.

    Provides filesystem-like access to a single Dataverse dataset version,
    allowing you to browse, read, write, and manage files using the standard
    fsspec interface (``ls``, ``info``, ``open``, ``cat``, ``rm``, ...) as well
    as a set of Dataverse-specific convenience helpers (``open_tabular``,
    ``stream_tabular``).

    Reads stream lazily via HTTP Range requests, and writes stream to Dataverse
    in bounded chunks, so neither path holds an entire file in memory.

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
        >>> with fs.open("data/file.csv", "rb") as f:
        ...     data = f.read()
        >>>
        >>> # Write a file
        >>> with fs.open("data/newfile.csv", "wb") as f:
        ...     f.write(b"column1,column2\\n")
        ...     f.write(b"value1,value2\\n")
    """

    protocol = "dataverse"
    # Each dataset gets its own instance; do not share via fsspec's cache.
    cachable = False

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
        **kwargs,
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
            **kwargs: Forwarded to fsspec's AbstractFileSystem.
        """
        super().__init__(**kwargs)

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
    def _strip_protocol(cls, path: str) -> str:
        """Normalize an input to a dataset-relative, slash-trimmed file path.

        Accepts either a plain relative path (e.g. ``data/file.csv``) or a full
        ``dataverse://host/data/file.csv?persistentId=...`` URL, in which case
        only the in-dataset file path is returned (the connection details live
        in the query string and are handled by ``_get_kwargs_from_urls``).
        """
        if isinstance(path, (list, tuple)):
            return [cls._strip_protocol(p) for p in path]  # type: ignore[return-value]
        path = str(path)
        if "://" in path:
            return urlparse(path).path.strip("/")
        return path.strip("/")

    @staticmethod
    def _get_kwargs_from_urls(url: str) -> Dict[str, Any]:
        """Extract constructor kwargs from a ``dataverse://`` URL.

        Recognized URL form::

            dataverse://<host>/<file/path>?persistentId=doi:...&version=:latest
            dataverse://<host>/<file/path>?id=12345

        The scheme defaults to ``https`` and can be overridden with a
        ``?scheme=http`` query parameter. The API token is *not* read from the
        URL; pass it via ``storage_options={"api_token": ...}``.
        """
        parsed = urlparse(url)
        kwargs: Dict[str, Any] = {}

        if not parsed.netloc:
            return kwargs

        params = parse_qs(parsed.query)
        scheme = params.get("scheme", ["https"])[0]
        kwargs["base_url"] = f"{scheme}://{parsed.netloc}"

        persistent_id = params.get("persistentId", [None])[0]
        id_param = params.get("id", [None])[0]
        if persistent_id:
            kwargs["identifier"] = persistent_id
        elif id_param:
            kwargs["identifier"] = int(id_param)

        if "version" in params:
            kwargs["version"] = params["version"][0]

        return kwargs

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

    # ------------------------------------------------------------------
    # fsspec interface
    # ------------------------------------------------------------------

    def info(self, path: str, **kwargs) -> Dict[str, Any]:
        """
        Return an fsspec info dict for a file or (implicit) directory.

        Args:
            path: Path within the dataset ("" or "/" for the root).

        Returns:
            Dict with at least ``name``, ``size`` and ``type`` keys. Files also
            carry ``id`` and ``content_type``.

        Raises:
            FileNotFoundError: If no file or directory matches the path.
        """
        path = self._strip_protocol(path)

        if path == "":
            return {"name": "", "size": 0, "type": "directory"}

        dataset = self._get_dataset()
        prefix = f"{path}/"
        is_dir = False

        for file in dataset.files or []:
            full = self._build_file_path(file)
            if full == path:
                return self._file_info(path, file)
            if full.startswith(prefix):
                is_dir = True

        if is_dir:
            return {"name": path, "size": 0, "type": "directory"}

        raise FileNotFoundError(f"File not found: {path}")

    def ls(
        self, path: str, detail: bool = True, **kwargs
    ) -> Union[List[Dict[str, Any]], List[str]]:
        """
        List the immediate children of a path.

        Args:
            path: Directory path ("" or "/" for the root). If ``path`` points
                at a file, a single-entry listing for that file is returned
                (standard fsspec behavior).
            detail: If True, return info dicts; if False, return path strings.

        Returns:
            List of info dicts (or names) for the immediate children.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        path = self._strip_protocol(path)

        info = self.info(path)
        if info["type"] == "file":
            return [info] if detail else [info["name"]]

        dataset = self._get_dataset()
        prefix = f"{path}/" if path else ""

        entries: Dict[str, Dict[str, Any]] = {}
        for file in dataset.files or []:
            full = self._build_file_path(file)
            if prefix and not full.startswith(prefix):
                continue

            remainder = full[len(prefix) :] if prefix else full
            if not remainder:
                continue

            head, _, rest = remainder.partition("/")
            child = prefix + head

            if rest:
                entries.setdefault(
                    child, {"name": child, "size": 0, "type": "directory"}
                )
            else:
                entries[child] = self._file_info(child, file)

        result = [entries[key] for key in sorted(entries)]
        return result if detail else [entry["name"] for entry in result]

    def _open(
        self,
        path: str,
        mode: str = "rb",
        block_size: Optional[int] = None,
        autocommit: bool = True,
        cache_options: Optional[dict] = None,
        metadata: Optional[UploadBody] = None,
        **kwargs,
    ) -> Union[DataverseFileReader, DataverseFileWriter]:
        """fsspec hook returning a binary file object (see ``open``)."""
        path = self._strip_protocol(path)
        block = block_size if block_size is not None else "default"

        if mode in ("rb", "r"):
            file = self._find_file(path)
            if file.data_file is None or file.data_file.id is None:
                raise ValueError(f"File '{path}' has no file ID")
            return DataverseFileReader(
                self,
                path,
                file_identifier=file.data_file.id,
                size=file.data_file.filesize,
                block_size=block,
                cache_options=cache_options,
            )

        if mode in ("wb", "w"):
            self._cache.clear()
            return DataverseFileWriter(
                self,
                path,
                metadata=metadata,
                block_size=block,
            )

        raise ValueError(
            f"Invalid mode '{mode}'. Supported modes: 'r', 'rb', 'w', 'wb'"
        )

    def _rm(self, path: str) -> None:
        """fsspec hook to delete a single file."""
        self.remove(path)

    def invalidate_cache(self, path: Optional[str] = None) -> None:
        """Clear cached dataset metadata in addition to fsspec's dir cache."""
        self._cache.clear()
        super().invalidate_cache(path)

    def mkdir(self, path: str, create_parents: bool = True, **kwargs) -> None:
        """No-op: Dataverse directories are implicit in file paths."""

    def makedirs(self, path: str, exist_ok: bool = False) -> None:
        """No-op: Dataverse directories are implicit in file paths."""

    # ------------------------------------------------------------------
    # Dataverse-specific / legacy convenience API
    # ------------------------------------------------------------------

    def getinfo(self, path: str, namespace: Optional[str] = None) -> Info:
        """
        Get rich Dataverse metadata about a file.

        Args:
            path: Path to the file (e.g., "data/file.csv")
            namespace: Optional namespace for additional info (not currently used)

        Returns:
            Info object with file metadata

        Raises:
            FileNotFoundError: If file doesn't exist

        Example:
            >>> info = fs.getinfo("data/myfile.csv")
            >>> print(info.filesize)
        """
        file = self._find_file(path)

        if file.data_file is None:
            raise FileNotFoundError(f"File '{path}' has no metadata")

        return Info(**file.data_file.model_dump())

    def listdir(self, path: str) -> List[str]:
        """
        List immediate child names (files and directories) at a path.

        Args:
            path: Directory path to list ("/" or "" for root)

        Returns:
            Sorted list of immediate child names

        Example:
            >>> fs.listdir("/")
            ['data', 'README.txt']
            >>> fs.listdir("data")
            ['file1.csv', 'file2.csv']
        """
        names = self.ls(path, detail=False)
        return sorted(name.split("/")[-1] for name in names)  # type: ignore[union-attr]

    def makedir(
        self, path: str, permissions: Optional[int] = None, recreate: bool = False
    ):
        """
        Create a directory.

        Note: Directories in Dataverse are implicit (based on file paths).
        This operation is not supported as a standalone action.

        Raises:
            NotImplementedError: Always raised (directories are implicit)
        """
        raise NotImplementedError(
            "Cannot create directories in DataverseFS. "
            "Directories are created implicitly when uploading files with directory paths."
        )

    def open(  # type: ignore[override]
        self,
        path: str,
        mode: str = "rb",
        block_size=None,
        cache_options=None,
        compression=None,
        metadata: Optional[UploadBody] = None,
        **kwargs,
    ):
        """Open a file, returning a Dataverse-aware handle.

        Binary modes defer to fsspec, which returns the
        :class:`DataverseFileReader` / :class:`DataverseFileWriter` directly.
        Text modes are wrapped in :class:`DataverseTextIO` instead of a plain
        :class:`io.TextIOWrapper` so the Dataverse-specific surface
        (``id``, ``persistent_id``, ``metadata``) stays reachable on the handle.
        """
        if "b" in mode:
            return super().open(
                path,
                mode,
                block_size=block_size,
                cache_options=cache_options,
                compression=compression,
                metadata=metadata,
                **kwargs,
            )

        text_kwargs = {
            key: kwargs.pop(key)
            for key in ("encoding", "errors", "newline")
            if key in kwargs
        }
        binary = super().open(
            path,
            mode.replace("t", "") + "b",
            block_size=block_size,
            cache_options=cache_options,
            compression=compression,
            metadata=metadata,
            **kwargs,
        )
        return DataverseTextIO(binary, **text_kwargs)

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
    ):
        """
        Open a file. ``r``/``w`` return text streams, ``rb``/``wb`` binary.

        Args:
            path: Path to the file in the dataset
            mode: 'r'/'rb' to read (default), 'w'/'wb' to create or replace
            buffering: Accepted for compatibility (ignored)
            metadata: Optional upload metadata (write mode only)

        Returns:
            A readable or writable file-like object.

        Example:
            >>> with fs.openbin("data/file.csv") as f:
            ...     content = f.read()
            >>> with fs.openbin("data/newfile.csv", mode="wb") as f:
            ...     f.write(b"data")
        """
        if mode not in ("r", "rb", "w", "wb"):
            raise ValueError(
                f"Invalid mode '{mode}'. Supported modes: 'r', 'rb', 'w', 'wb'"
            )
        return self.open(path, mode=mode, metadata=metadata)

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
            >>> for chunk in fs.stream_tabular("data/file.csv", api_token=None):
            ...     print(chunk.columns)
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
            api_token: Optional Dataverse API token for authenticated access.
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
            >>> df = fs.open_tabular("data/file.csv", api_token=None)
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
            >>> metadata = UploadBody(description="Updated description")
            >>> fs.setinfo("data/file.csv", metadata)
        """
        file = self._find_file(path)

        if file.data_file is None or file.data_file.id is None:
            raise ValueError(f"File '{path}' has no file ID")

        self.native_api.update_datafile_metadata(file.data_file.id, metadata=info)
        self._cache.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

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

    @staticmethod
    def _file_info(name: str, file: File) -> Dict[str, Any]:
        """Build an fsspec info dict for a file entry."""
        data_file = file.data_file
        return {
            "name": name,
            "size": data_file.filesize
            if data_file is not None and data_file.filesize is not None
            else 0,
            "type": "file",
            "id": data_file.id if data_file is not None else None,
            "content_type": data_file.content_type
            if data_file is not None
            else None,
        }

    def _find_file(self, path: str) -> File:
        """Find a file by its path in the dataset."""
        dataset = self._get_dataset()
        path = self._strip_protocol(path)

        assert dataset.files is not None

        for file in dataset.files:
            if self._build_file_path(file) == path:
                if file.data_file is None:
                    raise FileNotFoundError(
                        f"File '{path}' exists but has no data_file metadata"
                    )
                return file

        raise FileNotFoundError(f"File not found: {path}")
