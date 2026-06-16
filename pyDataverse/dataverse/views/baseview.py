from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Generic, Iterator, List, TypeVar, Union

if TYPE_CHECKING:
    pass

T = TypeVar("T")


class BaseView(ABC, Generic[T]):
    """
    Base class for all views with caching and iteration.

    Provides common functionality for views that need to:
    - Cache fetched items
    - Iterate over items
    - Access items by key (identifier, path, etc.)

    Subclasses must implement:
    - `_load_items()` - Load initial list of items/keys
    - `_fetch_item(key)` - Fetch a single item by key
    - `_get_cache_keys(item)` - Extract cache keys from fetched item
    """

    def __init__(self):
        """Initialize the base view with empty cache."""
        self._cache: Dict[Union[str, int], T] = {}
        self._items_loaded = False

    @abstractmethod
    def _load_items(self) -> None:
        """
        Load initial list of items/keys. Called lazily on first access.

        This method should populate any internal data structures needed
        for iteration and length calculation.
        """
        pass

    @abstractmethod
    def _fetch_item(self, key: Union[str, int]) -> T:
        """
        Fetch a single item by key. Should check cache first.

        Args:
            key: The key to fetch (identifier, path, etc.)

        Returns:
            The fetched item

        Raises:
            KeyError: If the key does not correspond to a valid item
        """
        pass

    @abstractmethod
    def _get_cache_keys(self, item: T) -> List[Union[str, int]]:
        """
        Extract all cache keys from a fetched item.

        Args:
            item: The item to extract keys from

        Returns:
            List of keys that should be used to cache this item
        """
        pass

    def __len__(self) -> int:
        """
        Return count of items. Calls `_load_items()` first if not already loaded.

        Subclasses should override this if they need custom counting logic.
        """
        if not self._items_loaded:
            self._load_items()
        # Default implementation - subclasses should override
        return len(self._cache)

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over items. Calls `_load_items()` and `_fetch_item()`.

        Subclasses should override this if they need custom iteration logic.
        """
        if not self._items_loaded:
            self._load_items()
        # Default implementation - subclasses should override
        for key in self._cache:
            yield self._cache[key]

    def __getitem__(self, key: Union[str, int]) -> T:
        """
        Get item by key with caching.

        Args:
            key: The key to look up

        Returns:
            The item corresponding to the key

        Raises:
            KeyError: If the key does not correspond to a valid item
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]

        # Fetch and cache
        item = self._fetch_item(key)
        for cache_key in self._get_cache_keys(item):
            self._cache[cache_key] = item
        return item
