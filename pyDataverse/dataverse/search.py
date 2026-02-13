from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Dict, List, Union, cast

from ..models.collection.content import Collection as ContentCollection
from ..models.collection.content import Dataset as ContentDataset
from .views.collectionview import CollectionView
from .views.datasetview import DatasetView

if TYPE_CHECKING:
    from ..models.search import SearchResponse
    from .collection import Collection
    from .dataverse import Dataverse


class _SearchCollectionAdapter:
    """Adapter to make SearchResult compatible with DatasetView and CollectionView."""

    def __init__(
        self,
        raw_content: List[Union["ContentDataset", "ContentCollection"]],
        dataverse: "Dataverse",
        collection_identifiers: Dict[int, str] | None = None,
    ):
        """
        Initialize the adapter.

        Args:
            raw_content: List of ContentDataset or ContentCollection objects.
            dataverse: The Dataverse instance.
            collection_identifiers: Optional mapping of placeholder IDs to actual
                collection identifiers. Used for search results where collections
                have placeholder id=0.
        """
        self._raw_content: List[Union["ContentDataset", "ContentCollection"]] = (
            raw_content
        )
        self.dataverse: "Dataverse" = dataverse
        # Maps placeholder id (0) to actual identifier for collections
        self._collection_identifiers: Dict[int, str] = collection_identifiers or {}


class SearchResult:
    """
    A search result from the Dataverse search API.
    """

    def __init__(
        self,
        search_response: SearchResponse,
        dataverse: "Dataverse",
        **kwargs,
    ):
        """
        Initialize SearchResult from a SearchResponse.

        Args:
            search_response: The SearchResponse object containing search results.
            dataverse: The Dataverse instance.
            **kwargs: Additional arguments passed to ContentBase.
        """
        self._search_response: SearchResponse = search_response
        self.dataverse: "Dataverse" = dataverse

    def update_metadata(self, **kwargs) -> None:
        """
        Update metadata for the search result.

        This method is not implemented because SearchResult objects are read-only
        representations of search results from the Dataverse API. To update metadata,
        access the underlying dataset or collection objects and update them directly.

        Raises:
            NotImplementedError: Always raised, as this operation is not supported
                for search results.
        """
        raise NotImplementedError("update_metadata is not implemented for SearchResult")

    @cached_property
    def datasets(self) -> DatasetView:
        """
        Return a view of all datasets in the search results.

        Returns:
            DatasetView: View object for iterating or accessing datasets.

        Examples:
            >>> for ds in search_result.datasets:
            ...     print(ds.title)
            >>> ds = search_result.datasets["doi:10.5072/FK2/ABC123"]
        """
        dataset_items = self._build_dataset_items()
        adapter = _SearchCollectionAdapter(
            cast("List[Union[ContentDataset, ContentCollection]]", dataset_items),
            self.dataverse,
        )
        return DatasetView(
            collection=cast("Collection", adapter),
            dataverse=self.dataverse,
        )

    @cached_property
    def collections(self) -> CollectionView:
        """
        Return a view of all collections (dataverses) in the search results.

        Returns:
            CollectionView: View object for iterating or accessing collections.

        Examples:
            >>> for coll in search_result.collections:
            ...     print(coll.metadata.name)
            >>> coll = search_result.collections["harvard"]
        """
        collection_items, collection_identifiers = self._build_collection_items()
        adapter = _SearchCollectionAdapter(
            cast("List[Union[ContentDataset, ContentCollection]]", collection_items),
            self.dataverse,
            collection_identifiers,
        )
        return CollectionView(
            collection=cast("Collection", adapter),
            dataverse=self.dataverse,
        )

    def _build_dataset_items(self) -> List[ContentDataset]:
        """
        Build ContentDataset objects from search response items.

        Filters search response items to only include datasets (type="dataset")
        that have a global_id, and converts them to ContentDataset model objects.

        Returns:
            List[ContentDataset]: List of ContentDataset objects created from
                search result items. Returns empty list if no dataset items found.
        """
        items = self._search_response.items or []
        return [
            ContentDataset(
                id=None,  # Search results don't have database IDs
                identifier=item.global_id,
                persistent_url=item.global_id or "",
                protocol="doi",
                authority="",
                separator="/",
                publisher=item.publisher or "",
                storage_identifier=item.storage_identifier or "",
                type="dataset",
            )
            for item in items
            if item.type == "dataset" and item.global_id
        ]

    def _build_collection_items(
        self,
    ) -> tuple[List[ContentCollection], Dict[int, str]]:
        """
        Build ContentCollection objects and identifier mapping from search response items.

        Filters search response items to only include dataverses (type="dataverse")
        that have an identifier, and converts them to ContentCollection model objects.
        Uses placeholder IDs (starting from 0) for collections since search results
        don't include database IDs.

        Returns:
            tuple[List[ContentCollection], Dict[int, str]]: A tuple containing:
                - List of ContentCollection objects created from search result items
                - Dictionary mapping placeholder IDs to actual collection identifiers
                Both return empty if no collection items found.
        """
        items = self._search_response.items or []
        collection_items: List[ContentCollection] = []
        collection_identifiers: Dict[int, str] = {}
        placeholder_id = 0

        for item in items:
            if item.type != "dataverse":
                continue

            identifier = item.identifier_of_dataverse or item.identifier
            if not identifier:
                continue

            collection_items.append(
                ContentCollection(
                    id=placeholder_id,
                    title=item.name or "",
                    type="dataverse",
                )
            )
            collection_identifiers[placeholder_id] = identifier
            placeholder_id += 1

        return collection_items, collection_identifiers
