from __future__ import annotations

import webbrowser
from functools import cached_property
from pathlib import Path
from typing import IO, TYPE_CHECKING, Dict, Iterator, List, Literal, Optional, Union

import pandas as pd
import rich
from pydantic import Field, PrivateAttr, computed_field

from pyDataverse.models.file.filemeta import UploadBody

from ..filesystem.reader import DataverseFileReader
from ..filesystem.tab import TABULAR_MIME_TYPES
from ..models.file import FileInfo, update
from .contentbase import ContentBase

if TYPE_CHECKING:
    from .dataset import Dataset


class File(ContentBase):
    """
    Represents a Dataverse file instance, including its metadata and data access methods.

    Provides convenient methods to retrieve, update, and access file contents,
    as well as utilities for tabular file operations.

    Attributes:
        identifier (int): The unique integer identifier for the Dataverse file.
        dataset (Dataset): The parent dataset this file belongs to.

    Examples:
        >>> file = dataset.files["data/file.csv"]
        >>> print(file.metadata.data_file.filesize)
        >>> df = file.open_tabular()
        >>> file.download("local_copy.csv")
    """

    identifier: int = Field(
        ...,
        description="The identifier of the file",
        frozen=True,
    )
    dataset: Dataset = Field(exclude=True, repr=False)
    _inner_df: Optional[pd.DataFrame] = PrivateAttr(default=None)
    _metadata: Optional[FileInfo] = PrivateAttr(default=None)

    @property
    def id(self) -> int:
        """
        The database ID of the file.
        """
        assert self.metadata.data_file is not None, (
            f"File '{self.path}' has no data file"
        )
        assert self.metadata.data_file.id is not None, f"File '{self.path}' has no ID"
        return self.metadata.data_file.id

    @property
    def persistent_id(self) -> str:
        """
        The persistent ID of the file.
        """
        assert self.metadata.data_file is not None, (
            f"File '{self.path}' has no data file"
        )
        assert self.metadata.data_file.persistent_id is not None, (
            f"File '{self.path}' has no persistent ID"
        )

        return self.metadata.data_file.persistent_id

    @computed_field(repr=False)
    @property
    def metadata(self) -> FileInfo:
        """
        Returns the full FileInfo metadata for this file.

        Fetched from the native Dataverse API on first access and cached
        thereafter (or pre-populated by the parent dataset listing).

        Returns:
            FileInfo: Metadata object describing this file.
        """
        if self._metadata is None:
            self._metadata = self.native_api.get_datafile_metadata(self.identifier)
        return self._metadata

    @computed_field
    @property
    def content_type(self) -> str:
        """
        The content type of the file.
        """
        assert self.metadata.data_file is not None, (
            f"File '{self.path}' has no data file"
        )
        assert self.metadata.data_file.content_type is not None, (
            f"File '{self.path}' has no content type"
        )
        return self.metadata.data_file.content_type

    @computed_field
    @property
    def size(self) -> int:
        """
        The size of the file in bytes.
        """
        assert self.metadata.data_file is not None, (
            f"File '{self.path}' has no data file"
        )

        assert self.metadata.data_file.filesize is not None, (
            f"File '{self.path}' has no size"
        )
        return self.metadata.data_file.filesize

    @computed_field
    @property
    def path(self) -> str:
        """
        The file's path within the dataset, e.g. "data/table.csv" or "myfile.txt".

        Returns:
            str: Relative file path in the dataset (including virtual directories).
        """
        return "/".join(
            filter(None, [self.metadata.directory_label, self.metadata.label])
        )

    @cached_property
    def is_tabular(self) -> bool:
        """
        Returns True if the file is a tabular file, False otherwise.
        """
        assert self.metadata.data_file is not None, (
            f"File '{self.path}' has no data file"
        )

        mime_type = self.metadata.data_file.content_type

        return mime_type in TABULAR_MIME_TYPES

    @cached_property
    def tabular_schema(self) -> Dict[str, str]:
        """
        Get the schema (column names and data types) of a tabular file.

        This property reads the first few rows of the tabular file to infer the column
        names and data types using pandas' type inference. The result is cached so
        subsequent accesses don't require additional API calls.

        Returns:
            Dict[str, str]: A dictionary mapping column names to their pandas data types
                as strings (e.g., {"name": "object", "age": "int64", "score": "float64"}).

        Raises:
            ValueError: If the file is not tabular (use `is_tabular` to check first).

        Examples:
            >>> file = dataset.files["data/results.csv"]
            >>> if file.is_tabular:
            ...     schema = file.tabular_schema
            ...     print(schema)
            {'participant_id': 'int64', 'name': 'object', 'score': 'float64'}
        """
        if not self.is_tabular:
            raise ValueError(f"File '{self.path}' is not tabular")

        # Stream first 4 rows and get dtypes and names
        header = self.open_tabular(nrows=4)

        return {k: str(v) for k, v in header.dtypes.to_dict().items()}

    @property
    def is_restricted(self) -> bool:
        """
        Returns True if the file is restricted, False otherwise.
        """

        if self.metadata.restricted is None:
            return False

        return self.metadata.restricted

    @computed_field(repr=False)
    @cached_property
    def url(self) -> str:
        """
        The URL of the file.
        """
        return self.dataset.dataverse.data_access_api.get_datafile_download_url(
            self.identifier,
        )

    def update_metadata(
        self,
        description: Optional[str] = None,
        categories: Optional[List[str]] = None,
        prov_freeform: Optional[str] = None,
        restrict: Optional[bool] = None,
    ):
        """
        Update the file's metadata in Dataverse.

        Args:
            filename (Optional[str]): New name for the file (optional).
            directory_label (Optional[str]): Directory label (for virtual paths) (optional).
            description (Optional[str]): File description (optional).
            categories (Optional[List[str]]): List of category strings (optional).
            prov_freeform (Optional[str]): Prov freeform (optional).
            restrict (Optional[bool]): Restrict the file (optional).

        Returns:
            FileInfo: Updated file metadata object.
        """

        if description is None:
            description = self.metadata.description
        if categories is None:
            categories = self.metadata.categories

        metadata = update.UpdateBody(
            description=description,
            categories=categories,
            prov_freeform=prov_freeform,
            restrict=restrict,
        )

        result = self.native_api.update_datafile_metadata(
            identifier=self.identifier,
            metadata=metadata,
        )

        self._metadata = None  # drop stale cache

        return result

    def open_in_browser(self) -> None:
        """
        Open the file in the default browser.
        """
        if isinstance(self.identifier, str):
            url = f"{self.dataset.dataverse.base_url}/file.xhtml?persistentId={self.identifier}"
        else:
            url = (
                f"{self.dataset.dataverse.base_url}/file.xhtml?fileId={self.identifier}"
            )
        webbrowser.open(url)

    def open(self, mode: Literal["r", "rb"] = "r") -> DataverseFileReader:
        """
        Open the file for binary reading with a streaming reader.

        Returns:
            DataverseFileReader: File-like object supporting .read() chunks.
        """
        return self.dataset.open(self.path, mode=mode)

    def open_tabular(
        self,
        no_header: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Open a tabular Dataverse file (e.g., CSV, TSV) and load it as a pandas DataFrame.

        Args:
            no_header (bool): If True, do not treat the first row as column names (default False).
            **kwargs: Additional arguments forwarded to pandas.read_csv.

        Returns:
            pd.DataFrame: DataFrame containing file contents.
        """
        if not self.is_tabular:
            raise ValueError(f"File '{self.path}' is not tabular")

        return self.dataset.open_tabular(
            self.path,
            no_header=no_header,
            **kwargs,
        )

    def stream_tabular(
        self,
        chunk_size: int = 10_000,
        no_header: bool = False,
        **kwargs,
    ) -> Iterator[pd.DataFrame]:
        """
        Read a tabular file as a stream of pandas DataFrames (chunks) for large files.

        Args:
            chunk_size (int): Number of rows per DataFrame chunk (default 10,000).
            no_header (bool): If True, do not treat the first row as column names.
            **kwargs: Additional keyword arguments to pandas.read_csv.

        Yields:
            Iterator[pd.DataFrame]: Yields DataFrame chunks.
        """
        if not self.is_tabular:
            raise ValueError(f"File '{self.path}' is not tabular")

        return self.dataset.stream_tabular(
            self.path,
            chunk_size=chunk_size,
            no_header=no_header,
            **kwargs,
        )

    def download(
        self,
        path: Union[str, Path],
        chunk_size: int = 8192,
    ) -> None:
        """
        Download the file from Dataverse and save it to a local file.

        Args:
            path (Union[str, Path]): Local path to save the downloaded file to.
            chunk_size (int): Number of bytes to read per chunk (default 8192).

        Returns:
            None
        """
        if isinstance(path, str):
            path = Path(path)
        with self.open(mode="rb") as reader:
            while True:
                chunk = reader.read(chunk_size)
                if not chunk:
                    break
                path.write_bytes(chunk)  # type: ignore[arg-type]

        rich.print(f"Downloaded {path.name} to {path.absolute()}")

    def replace(
        self,
        file: Union[str, Path, IO[str], IO[bytes]],
        description: Optional[str] = None,
        categories: Optional[List[str]] = None,
        restrict: Optional[bool] = None,
    ) -> None:
        """
        Replace the file with a new file.

        Args:
            file: The new file to replace the current file with.
            description: The new description for the file.
            categories: The new categories for the file.
            restrict: Whether to restrict the file.

        Returns:
            None
        """
        self.native_api.replace_datafile(
            self.identifier,
            file,
            metadata=UploadBody(
                description=description,
                categories=categories,
                restrict=restrict,
            ),
        )

        rich.print(f"Replaced {self.path} with {file}")

        self._metadata = None  # drop stale cache

    def delete(self) -> None:
        """
        Delete the file from Dataverse.
        """
        self.native_api.delete_datafile(self.identifier)
        rich.print(f"Deleted {self.path}")
