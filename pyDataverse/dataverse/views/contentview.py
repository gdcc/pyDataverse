from __future__ import annotations

import asyncio
from abc import abstractmethod
from typing import TYPE_CHECKING, Awaitable, Generator, List, Type, Union

from .baseview import BaseView, T

if TYPE_CHECKING:
    from ..collection import Collection
    from ..dataverse import Dataverse


class ContentView(BaseView[T]):
    """
    Base class for collection-based views with prefetch.

    Extends BaseView to add:
    - Prefetch mechanism using async gather
    - Collection interface (_raw_content access)
    - Optimized iteration with prefetching

    Subclasses must implement:
    - `_get_content_type()` - Return model class to filter
    - `_extract_ids()` - Extract IDs from collection._raw_content
    - `_fetch_item(identifier)` - Fetch single item by identifier
    - `_fetch_item_async(identifier)` - Async fetch for prefetching
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
        self._items_list: List[T] = []
        self._prefetched = False
        self._ids: List[Union[str, int]] = []
        self.prefetch_limit: int = 25
        self.prefetch_concurrency: int = 8

    async def _prefetch_extras_async(self, items: List[T]) -> None:
        """
        Optional hook for subclasses to warm additional data concurrently.

        This runs after `_prefetch()` has populated `_items_list` and `_cache`.
        The default implementation does nothing.
        """
        return None

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

    @abstractmethod
    def _fetch_item_async(self, identifier: Union[str, int]) -> Awaitable[T]:
        """
        Async fetch for prefetching.

        Args:
            identifier: The identifier to fetch

        Returns:
            An awaitable that yields the fetched item
        """
        pass

    def _load_items(self) -> None:
        """
        Load items by filtering collection._raw_content.

        This is called lazily and triggers prefetch if not already done.
        """
        if not self._items_loaded:
            self._prefetch()
            self._items_loaded = True

    def _prefetch(self) -> None:
        """
        Prefetch all items concurrently for efficient iteration.

        Items are prefetched based on IDs extracted from collection._raw_content.
        Prefetched items are stored in cache and _items_list for iteration.
        """
        if self._prefetched:
            return

        ids = self._extract_ids()
        self._ids = ids
        if not ids:
            self._prefetched = True
            return

        prefetch_ids = ids[: self.prefetch_limit] if self.prefetch_limit > 0 else []
        if not prefetch_ids:
            self._prefetched = True
            return

        async def _fetch_all() -> None:
            semaphore = asyncio.Semaphore(self.prefetch_concurrency)

            async def _bounded_fetch(identifier: Union[str, int]):
                async with semaphore:
                    return await self._fetch_item_async(identifier)

            results = await asyncio.gather(
                *[_bounded_fetch(identifier) for identifier in prefetch_ids],
                return_exceptions=True,
            )

            items = [None if isinstance(r, Exception) else r for r in results]
            self._cache_items(items, prefetch_ids)  # type: ignore[arg-type]

            try:
                await self._prefetch_extras_async(self._items_list)
            except Exception:
                pass

        self._prefetched = True

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            try:
                asyncio.run(_fetch_all())
            except Exception:
                pass  # Fallback to lazy loading on failure
        else:
            loop.create_task(_fetch_all())

    def _cache_items(self, items: List[T], ids: List[Union[str, int]]) -> None:
        """Cache fetched items with all their keys."""
        for idx, item in enumerate(items):
            if item is None:
                continue

            self._items_list.append(item)

            # Cache by all item keys
            for cache_key in self._get_cache_keys(item):
                self._cache[cache_key] = item

            # Cache by original fetch ID
            if idx < len(ids):
                self._cache[ids[idx]] = item

    def _iter_items(self) -> Generator[T, None, None]:
        """
        Internal generator for iterating items lazily.

        Yields items one at a time by fetching them on-demand from the collection's
        raw content. Used as a fallback when prefetching is not available or fails.

        Yields:
            T: Each item in the collection, fetched on-demand.
        """
        content_type = self._get_content_type()
        for content in self.collection._raw_content:
            if isinstance(content, content_type):
                # Handle identifier mapping for search results (id=0 placeholder)
                identifier = self._resolve_identifier(content)
                yield self[identifier]

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

    def __iter__(self):
        """
        Yield items from the collection.

        Returns:
            Iterator[T]: Each item in the collection.

        Iteration will prefetch and cache all items for best performance. If prefetch
        fails or yields nothing, will fallback to lazy loading.

        Example:
            >>> for item in collection_view:
            ...     print(item.identifier)
        """
        self._prefetch()
        if self._ids:
            for identifier in self._ids:
                yield self[identifier]
        else:
            yield from self._iter_items()

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
