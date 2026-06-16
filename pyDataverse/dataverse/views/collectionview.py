from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, Union

from ...models.collection import content as collection_content
from .contentview import ContentView

if TYPE_CHECKING:
    from ..collection import Collection


class CollectionView(ContentView["Collection"]):
    """
    Provides both iterator and dictionary-style access to collections within a Collection.

    This view supports:
      - Iteration: `for coll in view: ...` (prefetching for performance on first iteration)
      - Access by identifier: `coll = view[identifier]` (by alias or database ID)

    Internally, the view optimizes performance by prefetching collections concurrently on
    first iteration and maintains a cache for fast repeated access.
    """

    def _get_content_type(self) -> Type:
        """Return the model class to filter (ContentCollection)."""
        from ...models.collection.content import Collection as ContentCollection

        return ContentCollection

    def _extract_ids(self) -> List[Union[str, int]]:
        """Extract collection IDs from collection._raw_content."""
        content_type = self._get_content_type()
        ids = []
        for content in self.collection._raw_content:
            if isinstance(content, content_type):
                identifier = self._resolve_identifier(content)
                ids.append(identifier)
        return ids

    def _fetch_item(
        self,
        identifier: Union[str, int],
    ) -> "Collection":
        """Fetch a single collection and prime its metadata.

        ``fetch_collection`` only builds a lazy handle, so the metadata request
        is issued here to make the view's concurrent fetch window do real work.
        """
        coll = self.dataverse.fetch_collection(identifier)
        coll._metadata = self.dataverse.native_api.get_collection(identifier)
        return coll

    def _get_cache_keys(
        self,
        collection: "Collection",
    ) -> List[Union[str, int]]:
        """Extract cache keys from a fetched collection."""
        keys = []

        if hasattr(collection, "identifier") and collection.identifier:
            keys.append(collection.identifier)

        return keys

    def __repr__(self) -> str:
        collections = []
        for content in self.collection._raw_content:
            if isinstance(content, collection_content.Collection):
                collections.append(content.id)
        return f"CollectionView(collections={len(collections)})"
