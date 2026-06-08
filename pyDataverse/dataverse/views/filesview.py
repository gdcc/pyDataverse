from __future__ import annotations

import sys
from io import StringIO
from typing import (
    TYPE_CHECKING,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Union,
)

import pandas as pd
from bigtree.node.node import Node
from bigtree.tree.export import print_tree
from typing_extensions import TypedDict

from pyDataverse.filesystem.tab import TABULAR_MIME_TYPES
from pyDataverse.models.file import FileInfo

if TYPE_CHECKING:
    from ...models.dataset.edit_get import File as ModelFile
    from ..dataset import Dataset
    from ..file import File


class FileTableRow(TypedDict):
    identifier: Optional[int]
    path: str
    filesize: Optional[int]
    mime_type: Optional[str]
    description: Optional[str]
    is_tabular: Optional[bool]


class FilesView:
    """
    FilesView provides indexed and iterable access to files in a Dataverse Dataset.

    Features:
      - Iterable: Iterate over File objects: ``for file in files_view: ...``
      - Dictionary-style: Access File objects: ``file = files_view[path]``
      - Displays as a visual file tree in ``repr``.
      - Filtering: When ``tabular_only=True``, only tabular files (CSV, TSV, Excel) are included.

    Example:
        >>> dataset = dataverse.datasets["..."]
        >>> for file in dataset.files:
        ...     print(file.path)
        >>> file = dataset.files["data/file.csv"]
        >>> print(file.metadata.data_file.filesize)
        >>> print(dataset.files)
        >>> # Only tabular files
        >>> tabular_files = FilesView(dataset, tabular_only=True)
        >>> for file in tabular_files:
        ...     print(file.path)

    Notes:
        - File objects expose metadata and provide methods for file operations.
        - Directory-like navigation is not provided: all file paths are flat strings with "/" separators.
        - When ``tabular_only=True``, iteration, indexing, and length operations only include tabular files.
    """

    def __init__(self, dataset: "Dataset", tabular_only: bool = False):
        """
        Initialize the FilesView for a given Dataset.

        Args:
            dataset (Dataset): The Dataverse dataset.
            tabular_only (bool): If True, only include tabular files (CSV, TSV, Excel).
                When True, iteration, indexing, length, and representation only show
                tabular files. Accessing non-tabular files by path raises KeyError.
        """
        self.dataset = dataset
        self.tabular_only = tabular_only
        self._cache: Dict[str, "File"] = {}
        self._cache_by_id: Dict[int, "File"] = {}
        self._files_list: List[str] = []
        self._file_info_by_path: Dict[str, "ModelFile"] = {}
        self._file_info_list: List["ModelFile"] = []
        self._files_loaded = False

    def _load_files(self) -> None:
        """
        Load the list of file paths from the dataset's filesystem and cache it.

        This is performed lazily on first access for efficient use.
        Raises ValueError if the dataset is not properly identified.
        """
        if self._files_loaded:
            return  # Prevent redundant loads
        if self.dataset.identifier is None:
            raise ValueError("Dataset identifier is required")

        # Build a fast path->file-info index once to avoid repeated O(n) scans
        # via `dataset.fs._find_file(...)` during indexing/iteration.
        self._file_info_list = list(self._get_all_file_info())
        self._file_info_by_path.clear()
        self._files_list = []
        for file in self._file_info_list:
            path_parts = []
            if file.directory_label:
                path_parts.append(file.directory_label)
            if file.label:
                path_parts.append(file.label)
            if not path_parts:
                continue
            file_path = "/".join(path_parts)
            self._files_list.append(file_path)
            self._file_info_by_path[file_path] = file

        self._files_loaded = True

    def _iter_files(self) -> Generator["File", None, None]:
        """
        Internal generator for iterating File objects from the cache.

        Yields:
            File: File objects from the dataset.
        """
        self._load_files()
        # Yield File objects for all file paths
        for file_path in self._files_list:
            yield self[file_path]

    def __iter__(self):
        """
        Iterate over File objects in the dataset.

        Yields:
            File: File object for each file.

        Example:
            >>> for file in dataset.files:
            ...     print(file.path)
        """
        yield from self._iter_files()

    def __getitem__(self, path: Union[str, int]) -> "File":
        """
        Retrieve a File object by its path or index.

        Args:
            path (Union[str, int]): The file path (e.g., "data/file.csv") or index.

        Returns:
            File: The File object.

        Raises:
            KeyError: If the path does not refer to a file.
            IndexError: If the index is out of range.

        Example:
            >>> file = dataset.files["data/file.csv"]
            >>> print(file.metadata.data_file.filesize)
            >>> file = dataset.files[0]  # Get first file sorted by directory_label
        """
        if isinstance(path, int):
            return self._get_file_by_index(path)
        return self._get_file_by_path(path)

    def _get_file_by_path(self, path: str) -> "File":
        """
        Retrieve a File object by its path.

        Args:
            path (str): The file path (e.g., "data/file.csv").

        Returns:
            File: The File object.

        Raises:
            KeyError: If the path does not refer to a file, or if tabular_only is True
                and the file is not tabular.

        Example:
            >>> file = dataset.files._get_file_by_path("data/file.csv")
            >>> print(file.metadata.data_file.filesize)
        """
        self._load_files()
        path = path.strip("/")

        # Serve from cache if available
        if path in self._cache:
            return self._cache[path]

        file_info = self._file_info_by_path.get(path)
        if file_info is None:
            if self.tabular_only:
                try:
                    candidate = self.dataset.fs._find_file(path)
                except FileNotFoundError as e:
                    raise KeyError(f"File '{path}' not found") from e

                if candidate.data_file is None:
                    raise KeyError(f"File '{path}' has no file ID")

                mime_type = candidate.data_file.content_type
                if not mime_type or mime_type not in TABULAR_MIME_TYPES:
                    raise KeyError(f"File '{path}' is not tabular (tabular_only=True)")

            raise KeyError(f"File '{path}' not found")

        if file_info.data_file is None or file_info.data_file.id is None:
            raise KeyError(f"File '{path}' has no file ID")

        file_id = file_info.data_file.id
        file_obj = self._cache_by_id.get(file_id)
        if file_obj is None:
            from ..file import File

            file_obj = File(
                identifier=file_id,
                dataset=self.dataset,
                dataverse=self.dataset.dataverse,
            )
            file_obj._metadata = FileInfo.model_validate(file_info.model_dump())
            self._cache_by_id[file_id] = file_obj

        self._cache[path] = file_obj
        return file_obj

    def _resolve_index_to_path(self, index: int) -> str:
        """Resolve an integer index to a file path."""
        self._load_files()

        # Support negative indexing (Python convention)
        original_index = index
        if index < 0:
            index = len(self._files_list) + index

        if index < 0 or index >= len(self._files_list):
            raise IndexError(
                f"Index {original_index} out of range (dataset has {len(self._files_list)} files)"
            )

        return self._files_list[index]

    def _get_file_by_index(self, index: int) -> "File":
        """
        Get the File object at the specified index, sorted by directory_label.

        Args:
            index (int): The zero-based index of the file.

        Returns:
            File: The File object at the specified index.

        Raises:
            IndexError: If the index is out of range.
            ValueError: If the dataset identifier is not available.

        Example:
            >>> file = dataset.files._get_file_by_index(0)  # Get first file
        """
        path = self._resolve_index_to_path(index)
        return self._get_file_by_path(path)

    def __len__(self) -> int:
        """
        Return the total file count in the dataset.

        Returns:
            int: Number of files in the dataset (including nested files).

        Caching:
            File list is cached on first use.
        """
        self._load_files()
        return len(self._files_list)

    def _get_all_file_paths(self) -> List[str]:
        """
        Fetch all file paths (including in virtual directories) for tree representations.

        Returns:
            List[str]: Sorted list of full file paths, sorted by directory_label.

        Notes:
            This fetches paths from the underlying dataset object, not just the root.
            Files are sorted by directory_label (None values come first).
        """

        self._load_files()
        return self._files_list

    def _get_all_file_info(self) -> Sequence["ModelFile"]:
        # Defensive check: ensure dataset has an id
        if self.dataset.identifier is None:
            raise ValueError("Dataset identifier is required")

        # Use private method to get the underlying files data structure.
        dataset = self.dataset.fs._get_dataset()
        if dataset.files is None:
            return []

        # Filter to tabular files if tabular_only is True
        files = dataset.files

        if self.tabular_only:
            files = [
                f
                for f in files
                if f.data_file
                and f.data_file.content_type
                and f.data_file.content_type in TABULAR_MIME_TYPES
            ]

        # Sort files by directory_label (None values come first), then by label
        return sorted(
            files,
            key=lambda f: (f.directory_label or "", f.label or ""),
        )

    def __repr__(self) -> str:
        """
        Return a visual tree display of all files in the dataset.

        Returns:
            str: Text tree of the file structure. "FilesView (empty)" if no files.

        Example:
            >>> print(dataset.files)
            ZENODO.1234
            └── data
                └── myfile.csv

        Rendered using the bigtree Node tree.
        """
        # Retrieve all file paths for building the tree.
        file_paths = self._get_all_file_paths()
        if not file_paths:
            return "FilesView (empty)"

        root = Node(f"{self.dataset.identifier}")
        for file_path in file_paths:
            parts = file_path.split("/")
            current_node = root
            for part in parts:
                # Avoid duplicate nodes
                child = next(
                    (child for child in current_node.children if child.name == part),
                    None,
                )
                if child is None:
                    child = Node(part, parent=current_node)
                current_node = child

        # Capture the printed tree and return as a string
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        try:
            print_tree(root, style="rounded")
            tree_str = buffer.getvalue()
        finally:
            sys.stdout = old_stdout
        return tree_str.rstrip()

    @property
    def df(self) -> pd.DataFrame:
        """
        Return a pandas DataFrame of all files in the dataset.
        When tabular_only is True, only tabular files are included.
        """
        self._load_files()
        files = self._file_info_list

        rows = []
        for file in files:
            if file.data_file is None:
                continue

            mime_type = file.data_file.content_type
            is_tabular = mime_type in TABULAR_MIME_TYPES if mime_type else False

            rows.append(
                FileTableRow(
                    identifier=file.data_file.id,
                    path="/".join([file.directory_label or "", file.label or ""]),
                    filesize=file.data_file.filesize,
                    mime_type=mime_type,
                    description=file.data_file.description,
                    is_tabular=is_tabular,
                )
            )
        return pd.DataFrame(rows)
