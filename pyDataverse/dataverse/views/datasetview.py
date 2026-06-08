from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Type, Union

from ...models.collection import content as collection_content
from .contentview import ContentView

if TYPE_CHECKING:
    from ..dataset import Dataset


class DatasetView(ContentView["Dataset"]):
    """
    Provides both iterator and dictionary-style access to datasets within a Collection.

    This view supports:
      - Iteration: `for ds in view: ...` (prefetching for performance on first iteration)
      - Access by identifier: `ds = view[identifier]` (by DOI or database ID)

    Internally, the view optimizes performance by prefetching datasets concurrently on
    first iteration and maintains a cache for fast repeated access.
    """

    def _get_content_type(self) -> Type:
        """Return the model class to filter (ContentDataset)."""
        from ...models.collection.content import Dataset as ContentDataset

        return ContentDataset

    def _extract_ids(self) -> List[Union[str, int]]:
        """Extract dataset IDs/identifiers from collection._raw_content."""
        content_type = self._get_content_type()
        ids = []
        for content in self.collection._raw_content:
            if isinstance(content, content_type):
                identifier = self._resolve_identifier(content)
                ids.append(identifier)
        return ids

    def _fetch_item(self, identifier: Union[str, int]) -> "Dataset":
        """Fetch a single dataset by identifier."""
        return self.dataverse.fetch_dataset(identifier)

    def _get_cache_keys(self, dataset: "Dataset") -> List[Union[str, int]]:
        """Extract cache keys from a fetched dataset."""
        keys = []
        if hasattr(dataset, "identifier") and dataset.identifier:
            keys.append(dataset.identifier)
        # Note: We don't add dataset.id here as it's added in ContentView._prefetch
        return keys

    def _resolve_index_to_identifier(self, index: int) -> Union[str, int]:
        """Resolve an integer index to a dataset identifier."""
        if not self._ids:
            self._ids = self._extract_ids()

        # Support negative indexing (Python convention)
        if index < 0:
            index = len(self._ids) + index

        if index < 0 or index >= len(self._ids):
            raise IndexError(
                f"Index {index} out of range (collection has {len(self._ids)} datasets)"
            )

        return self._ids[index]

    def _parse_version(self, identifier: str) -> Tuple[str, str]:
        """Parse version suffix from identifier string."""
        if "@" not in identifier:
            return identifier, ":latest"

        identifier, version_str = identifier.rsplit("@", 1)
        if version_str in ("latest", "latest-published", "draft"):
            version = f":{version_str}"
        else:
            version = version_str

        return identifier, version

    def __getitem__(self, identifier: Union[str, int]) -> "Dataset":
        """
        Retrieve a dataset by its identifier (DOI string or numeric database ID) or index.

        Args:
            identifier (str or int): The dataset's global identifier (e.g., DOI)
                or local database ID, or an integer index for positional access.
                For string identifiers, version can be specified using "@version" suffix
                (e.g., "doi:10.5072/FK2/ABC123@latest" or "doi:10.5072/FK2/ABC123@1.1").
                Valid version values are:
                - "@latest" (default): draft if exists, otherwise latest published
                - "@latest-published": latest published version only
                - "@draft": draft version only
                - "@x.y": specific version (e.g., "@1.1", "@2.0")
                - "@x": major version (e.g., "@1", "@2")
                For integer identifiers:
                - Positive integers: 0-based index (e.g., 0 for first dataset)
                - Negative integers: -1 for last dataset, -2 for second-to-last, etc.

        Returns:
            Dataset: The loaded dataset object.

        Raises:
            KeyError: If the identifier does not correspond to a valid dataset.
            IndexError: If the integer index is out of range.
        """
        # Handle integer indexing (positional access)
        original_identifier = identifier
        is_index_access = isinstance(identifier, int)

        if is_index_access:
            identifier = self._resolve_index_to_identifier(identifier)

        # Parse version from string identifier if present
        if isinstance(identifier, str):
            identifier, version = self._parse_version(identifier)
        else:
            version = ":latest"

        cache_key = identifier

        # Check cache first
        if cache_key in self._cache:
            dataset = self._cache[cache_key]
            if is_index_access:
                self._cache[original_identifier] = dataset
            return dataset

        # Fetch and cache dataset
        dataset = self.dataverse.fetch_dataset(identifier, version=version)

        # Cache with all keys
        for key in self._get_cache_keys(dataset):
            self._cache[key] = dataset
        self._cache[cache_key] = dataset
        if is_index_access:
            self._cache[original_identifier] = dataset

        return dataset

    def __repr__(self) -> str:
        datasets = []
        for content in self.collection._raw_content:
            if isinstance(content, collection_content.Dataset):
                datasets.append(content.identifier)
        return f"DatasetView(datasets={len(datasets)})"
