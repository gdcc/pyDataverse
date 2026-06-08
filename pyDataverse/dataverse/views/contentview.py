from __future__ import annotations

import itertools
from abc import abstractmethod
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Iterator, List, Optional, Type, Union

from .baseview import BaseView, T

if TYPE_CHECKING:
    from ..collection import Collection
    from ..dataverse import Dataverse


class ContentView(BaseView[T]):
    """
    Base class for collection-based views.

    Extends BaseView to add:
    - Collection interface (_raw_content access)
    - Lazy iteration with a bounded concurrent fetch window

    Subclasses must implement:
    - `_get_content_type()` - Return model class to filter
    - `_extract_ids()` - Extract IDs from collection._raw_content
    - `_fetch_item(identifier)` - Fetch single item by identifier
    - `_get_cache_keys(item)` - Extract cache keys from item
    """

    def __init__(self, collection: "Collection", dataverse: "Dataverse"):
        """
        Initialize the ContentView.

        Args:
            collection: The collection containing the content
            dataverse: The Dataverse instance for fetching items
        """
        super().__init__()
        self.collection = collection
        self.dataverse = dataverse
        self._ids: List[Union[str, int]] = []
        self.prefetch_concurrency: int = 8

    @abstractmethod
    def _get_content_type(self) -> Type:
        """
        Return the model class to filter (ContentDataset, ContentCollection).

        Returns:
            The model class to use for filtering _raw_content
        """
        pass

    @abstractmethod
    def _extract_ids(self) -> List[Union[str, int]]:
        """
        Extract IDs/identifiers from collection._raw_content.

        Returns:
            List of IDs/identifiers to fetch
        """
        pass

    def _load_items(self) -> None:
        """Populate the identifier list without fetching the items themselves."""
        if not self._items_loaded:
            self._ids = self._extract_ids()
            self._items_loaded = True

    def _safe_fetch(self, identifier: Union[str, int]) -> Optional[T]:
        """Return a cached item, fetch it, or ``None`` if the fetch fails."""
        if identifier in self._cache:
            return self._cache[identifier]
        try:
            return self._fetch_item(identifier)
        except Exception:
            return None

    def _cache_item(self, item: T, fetch_id: Union[str, int]) -> None:
        """Store an item under all of its cache keys."""
        for cache_key in self._get_cache_keys(item):
            self._cache[cache_key] = item
        self._cache[fetch_id] = item

    def _resolve_identifier(self, content) -> Union[str, int]:
        """
        Resolve the identifier to use for fetching an item.

        Handles the case where content has id=0 (placeholder) and we need to
        use the identifier mapping from the adapter (for search results).
        For dataset content items, constructs the full persistent identifier
        (DOI) from protocol, authority, separator, and identifier fields.

        Args:
            content: The content item from _raw_content

        Returns:
            The identifier to use for fetching

        Raises:
            ValueError: If the content item has no id or identifier
        """
        # Check if this is a search result adapter with identifier mapping
        if (
            hasattr(self.collection, "_collection_identifiers")
            and hasattr(content, "id")
            and content.id is not None
            and content.id == 0
        ):
            # Use identifier mapping if available
            identifier_map = getattr(self.collection, "_collection_identifiers", {})
            if content.id in identifier_map:
                return identifier_map[content.id]

        # For dataset content items, construct full persistent identifier (DOI)
        # from protocol, authority, separator, and identifier fields
        if (
            hasattr(content, "protocol")
            and hasattr(content, "authority")
            and hasattr(content, "separator")
            and hasattr(content, "identifier")
            and content.protocol
            and content.authority
            and content.separator
            and content.identifier
        ):
            return f"{content.protocol}:{content.authority}{content.separator}{content.identifier}"

        # Default: use id if available and not None, otherwise identifier
        if hasattr(content, "id") and content.id is not None:
            return content.id
        elif hasattr(content, "identifier") and content.identifier:
            return content.identifier
        else:
            raise ValueError(f"Content item {content} has no id or identifier")

    def __len__(self) -> int:
        """
        Return the number of items in the collection.

        Returns:
            int: The count of items matching the content type in the collection.
        """
        content_type = self._get_content_type()
        count = 0
        for content in self.collection._raw_content:
            if isinstance(content, content_type):
                count += 1
        return count

    def __iter__(self) -> Iterator[T]:
        """
        Yield items in order, fetching them in a bounded concurrent window.

        Up to ``prefetch_concurrency`` fetches run ahead of the consumer, so
        iterating is fast while consumers that stop early (e.g.
        ``itertools.islice(view, 50)`` or ``break``) never trigger fetches for
        the whole collection.

        Example:
            >>> for item in collection_view:
            ...     print(item.identifier)
        """
        ids = self._extract_ids()
        self._ids = ids
        if not ids:
            return

        window = max(1, self.prefetch_concurrency)
        ids_iter = iter(ids)
        sentinel = object()

        with ThreadPoolExecutor(max_workers=window) as executor:
            pending = deque(
                (i, executor.submit(self._safe_fetch, i))
                for i in itertools.islice(ids_iter, window)
            )
            while pending:
                fetch_id, future = pending.popleft()

                nxt = next(ids_iter, sentinel)
                if nxt is not sentinel:
                    pending.append((nxt, executor.submit(self._safe_fetch, nxt)))

                item = future.result()
                if item is None:
                    continue

                self._cache_item(item, fetch_id)
                yield item

    def __getitem__(self, identifier: Union[str, int]) -> T:
        """
        Retrieve an item by its identifier.

        Args:
            identifier: The item's identifier (string or int)

        Returns:
            The loaded item object.

        Raises:
            KeyError: If the identifier does not correspond to a valid item.

        Example:
            >>> item = collection_view["some-identifier"]
            >>> print(item.title)
        """
        # Check cache first
        if identifier in self._cache:
            return self._cache[identifier]

        # Not cached: fetch using Dataverse's API and add to cache
        item = self._fetch_item(identifier)

        # Store in cache for future fast access
        for cache_key in self._get_cache_keys(item):
            self._cache[cache_key] = item
        self._cache[identifier] = item
        return item
