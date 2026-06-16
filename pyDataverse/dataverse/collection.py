from __future__ import annotations

import asyncio
from collections import defaultdict
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Literal,
    Optional,
    TypeAlias,
    Union,
)

import pandas as pd
from asyncer import asyncify
from pydantic import Field, PrivateAttr
from rdflib import BNode, Graph
from rich.progress import Progress
from typing_extensions import TypedDict

from pyDataverse.dataverse.dataset import GraphFormat
from pyDataverse.models import info

from ..api.search import QueryOptions
from ..models import collection
from ..models.metadatablocks.metadatablock import MetadatablockSpecification
from .contentbase import ContentBase
from .dataverse import Author, Contact, Subject
from .metrics import Metrics
from .search import SearchResult

if TYPE_CHECKING:
    from .dataset import Dataset


# Type alias for the raw content types
RawContentTypes: TypeAlias = List[
    Union[collection.content.Collection, collection.content.Dataset]
]

# Type alias for the parsed content types
ParsedContentTypes: TypeAlias = List[
    Union[
        "Dataset",
        "Collection",
    ]
]


# Type alias for the content type
class Content(TypedDict):
    identifier: str
    content_type: Literal["collection", "dataset"]
    title: Optional[str]


def _deduplicate_blank_nodes(graph: Graph) -> Graph:
    """Merge blank nodes with identical properties into a single canonical node.

    When merging RDF graphs from multiple sources, blank nodes from different
    graphs are treated as distinct entities even if they have identical properties.
    This function identifies blank nodes with the same property signatures
    (excluding self-referential properties) and merges them into a single node.

    Args:
        graph: The RDF graph to deduplicate. Must be a valid rdflib Graph instance.

    Returns:
        A new Graph with deduplicated blank nodes. If no duplicates are found,
        returns the original graph unchanged.

    Note:
        Self-referential properties (e.g., a blank node pointing to itself via
        `generatedBy`) are excluded from the signature calculation to ensure
        nodes with identical external properties are properly merged.
    """
    if not graph:
        return graph

    # Collect all blank nodes appearing as subjects or objects
    blank_nodes = {s for s, _, _ in graph if isinstance(s, BNode)}
    blank_nodes.update({o for _, _, o in graph if isinstance(o, BNode)})

    if not blank_nodes:
        return graph

    # Group blank nodes by their property signature (excluding self-references)
    signatures: defaultdict[frozenset[tuple], list[BNode]] = defaultdict(list)  # type: ignore[type-arg]
    for bnode in blank_nodes:
        # Get all triples where bnode is subject, excluding self-referential ones
        props = frozenset(
            (p, o) for _, p, o in graph.triples((bnode, None, None)) if o != bnode
        )
        signatures[props].append(bnode)

    # Create mapping: duplicate blank node -> canonical blank node
    mapping: dict[BNode, BNode] = {
        dup: nodes[0]
        for nodes in signatures.values()
        if len(nodes) > 1
        for dup in nodes[1:]
    }

    if not mapping:
        return graph

    # Rebuild graph with deduplicated nodes
    deduplicated = Graph()
    for s, p, o in graph:
        # Replace subject if it's a duplicate blank node
        new_s = mapping.get(s, s) if isinstance(s, BNode) else s
        # Replace object if it's a duplicate blank node
        new_o = mapping.get(o, o) if isinstance(o, BNode) else o
        deduplicated.add((new_s, p, new_o))

    return deduplicated


class Collection(ContentBase):
    """
    Represents a Dataverse collection and provides methods to manage its metadata, fetch its sub-collections and datasets,
    and interact with its child and related content.

    This class encapsulates the core operations for working with a Dataverse collection, including:
      - Reading and updating collection metadata.
      - Accessing enabled metadatablocks.
      - Retrieving lists/views of datasets or sub-collections (with dict-like and iterator access).
      - Creating new datasets within the collection.

    Attributes:
        identifier (Union[Literal[":root"], str, int]): Alias, handle, or DB ID of the collection.

    Example:
        >>> coll = dataverse["sample-collection"]
        >>> print(coll.metadata.name)
        >>> for ds in coll.datasets:
        ...     print(ds.title)
    """

    identifier: Union[Literal[":root"], str, int] = Field(
        description="The identifier of the collection."
    )

    _metadata: Optional[collection.Collection] = PrivateAttr(default=None)

    @property
    def metrics(self) -> Metrics:
        return Metrics(
            metrics_api=self.dataverse.metrics_api,
            parent_alias=self.alias,
        )

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def metadata(self) -> collection.Collection:
        """
        Metadata about this collection from the Dataverse native API.

        Fetched on first access and cached thereafter.

        Returns:
            collection.Collection: Complete metadata object for this collection.
        """
        if self._metadata is None:
            self._metadata = self.native_api.get_collection(self.identifier)
        return self._metadata

    @property
    def alias(self) -> str:
        return self.metadata.alias

    def update_metadata(
        self,
        name: Optional[str] = None,
        alias: Optional[str] = None,
        affiliation: Optional[str] = None,
        description: Optional[str] = None,
        dataverse_type: Optional[str] = None,
        dataverse_contacts: Optional[List[str]] = None,
    ):
        """
        Update collection metadata/properties through the native API.

        Args:
            name (Optional[str]): Display name of the collection.
            alias (Optional[str]): Short name/alias for the collection.
            affiliation (Optional[str]): Affiliation text.
            description (Optional[str]): Detailed collection description.
            dataverse_type (Optional[str]): Collection type.
            dataverse_contacts (Optional[List[str]]): List of contact email addresses.

        Updates the remote collection and updates the local `identifier` if alias is changed.
        """
        dataverse_contacts_ = (
            [collection.DataverseContact(contact_email=c) for c in dataverse_contacts]
            if dataverse_contacts
            else None
        )

        metadata = collection.UpdateCollection(
            name=name,
            alias=alias,
            affiliation=affiliation,
            description=description,
            dataverse_type=dataverse_type,
            dataverse_contacts=dataverse_contacts_,
        )

        # Update the metadata of the collection
        self.native_api.update_collection(self.alias, metadata)
        self._metadata = None

        if alias is not None:
            self.identifier = alias

    @cached_property
    def _raw_content(self) -> RawContentTypes:
        """
        Get the raw content listing for this collection, as provided by the API.
        Returns a list of native collection and dataset descriptors.

        Returns:
            RawContentTypes: List of native content objects.
        """
        return self.native_api.get_collection_contents(self.identifier)

    @cached_property
    def overview(self) -> pd.DataFrame:
        """
        Get a structured list of all content (datasets and collections) in this collection.

        Returns:
            List[Content]: List of dictionaries containing content information.
                Each dictionary has:
                - identifier (str): The dataset identifier or collection alias
                - content_type (Literal["collection", "dataset"]): Type of content
                - title (Optional[str]): Display title/name of the content

        Example:
            >>> content = collection.overview
            >>> for item in content:
            ...     print(f"{item['content_type']}: {item['title']}")
            dataset: My Research Data
            collection: Child Collection
        """
        collection_content = []

        for dataset in self.datasets:
            collection_content.append(
                {
                    "content_type": "dataset",
                    "persistent_identifier": dataset.persistent_identifier,
                    "title": dataset.title,
                }
            )
        for coll in self.collections:
            collection_content.append(
                {
                    "content_type": "collection",
                    "identifier": coll.alias,
                    "title": coll.metadata.name,
                }
            )
        return pd.DataFrame(collection_content)

    async def _fetch_all_content(self):
        """
        Asynchronously fetch full metadata for all child collections and datasets in this collection.

        Returns:
            list: List of objects: collection.Collection and Dataset, corresponding to all child content.

        Example:
            >>> results = await collection._fetch_all_content()
        """
        fetch_collection = asyncify(self.native_api.get_collection)
        fetch_dataset = asyncify(self.dataverse.fetch_dataset)

        tasks = []

        for content in self._raw_content:
            if isinstance(content, collection.content.Collection):
                tasks.append(fetch_collection(content.id))
            elif isinstance(content, collection.content.Dataset):
                tasks.append(fetch_dataset(content.id))  # type: ignore[arg-type]

        return await asyncio.gather(*tasks, return_exceptions=True)

    @cached_property
    def metadatablocks(self) -> Dict[str, MetadatablockSpecification]:
        """
        Get specifications for all enabled and available metadatablocks for this collection.

        Returns:
            Dict[str, MetadatablockSpecification]: Map of block name to block specification.
        """
        return self.native_api.get_metadatablocks(
            collection_alias=self.identifier,
            full=True,
        )

    @cached_property
    def _enabled_metadatablocks(self) -> List[str]:
        """
        Get a list of enabled metadatablock names for this collection.

        Returns:
            List[str]: Names of enabled metadatablocks.
        """
        return list(self.metadatablocks.keys())

    @property
    def collections(self):
        """
        Return a view of all subcollections within this collection, with both iterator and dict-like access.

        Returns:
            CollectionView: View object for iterating or accessing child collections.

        Examples:
            >>> # Iterator access
            >>> for coll in collection.collections:
            ...     print(coll.identifier)
            >>> # Dict-like access
            >>> coll = collection.collections["harvard"]
            >>> coll = collection.collections[123]  # by database ID
        """
        from .views.collectionview import CollectionView

        return CollectionView(collection=self, dataverse=self.dataverse)

    @property
    def datasets(self):
        """
        Return a view of all datasets within this collection, with both iterator and dict-like access.

        Returns:
            DatasetView: View object for iterating or accessing datasets.

        Examples:
            >>> # Iterator access
            >>> for ds in collection.datasets:
            ...     print(ds.title)
            >>> # Dict-like access
            >>> ds = collection.datasets["doi:10.5072/FK2/ABC123"]
            >>> ds = collection.datasets[123]  # by database ID
        """
        from .views.datasetview import DatasetView

        return DatasetView(collection=self, dataverse=self.dataverse)

    def create_dataset(
        self,
        title: str,
        description: str,
        authors: List[Author],
        contacts: List[Contact],
        subjects: List[Subject],
        upload_to_collection: bool = False,
        license: Optional[Union[str, info.License]] = None,
    ) -> Dataset:
        """
        Create a new dataset within this collection.

        Args:
            title (str): Title of the new dataset.
            description (str): Dataset description/abstract.
            authors (List[Author]): List of dataset author objects.
            contacts (List[Contact]): List of dataset contacts.
            subjects (List[Subject]): List of controlled vocabulary subjects.

        Returns:
            Dataset: The created dataset object (not yet persisted on server until uploaded).
        """
        self.dataverse._ensure_factory_initialized()

        dataset = self.dataverse._internal_create_dataset(
            title=title,
            description=description,
            authors=authors,
            contacts=contacts,
            subjects=subjects,
            license=license,
            _blocks_to_include=self._enabled_metadatablocks,
        )

        if upload_to_collection:
            if isinstance(self.identifier, int):
                alias = self.metadata.alias
            else:
                alias = self.identifier

            dataset.upload_to_collection(alias)

        return dataset

    def search(
        self,
        query: str,
        per_page: int = 10,
        type: Optional[
            Literal[
                "dataset",
                "collection",
                "dataverse",
            ]
        ] = None,
        options: Optional[QueryOptions] = None,
    ) -> SearchResult:
        """
        Search for content within this collection and its sub-collections.

        This method performs a search scoped to the current collection, automatically
        setting the subtree parameter to limit results to this collection and any
        nested sub-collections. It provides a convenient way to search within a
        specific collection without having to manually configure the search scope.

        Args:
            query (str): The search query string. Can include keywords, phrases in quotes,
                boolean operators (AND, OR, NOT), wildcards (* and ?), and field-specific
                searches (e.g., "title:climate").
            options (Optional[QueryOptions]): Optional search configuration including
                filtering, sorting, pagination, and result formatting. If provided,
                the subtree parameter will be automatically set to this collection's alias.
                If None, default options with subtree set to this collection will be used.

        Returns:
            SearchResult: Object containing search results, metadata, and facet information
            scoped to this collection and its sub-collections.

        Examples:
            Basic search within collection:
            >>> results = collection.search("climate change")

            Search with custom options:
            >>> options = QueryOptions(type="dataset", per_page=20, sort="date")
            >>> results = collection.search("temperature", options)

            Boolean search:
            >>> results = collection.search("climate AND temperature")

            Field-specific search:
            >>> results = collection.search("title:climate")

        Note:
            The search will automatically be scoped to this collection by setting
            the subtree parameter, regardless of whether options are provided or not.
        """
        if options is None:
            options = QueryOptions(subtree=self.alias)
        else:
            options.subtree = self.alias

        return self.dataverse.search(
            query=query,
            per_page=per_page,
            type=type,
            options=options,
        )

    def publish(self):
        """
        Publish this collection to make it publicly accessible.
        """
        self.native_api.publish_collection(self.alias)
        self._metadata = None

    def create_collection(
        self,
        alias: str,
        name: str,
        description: str,
        affiliation: str,
        dataverse_contacts: List[str],
        dataverse_type: Literal[
            "DEPARTMENT",
            "JOURNALS",
            "LABORATORY",
            "ORGANIZATIONS_INSTITUTIONS",
            "RESEARCHERS",
            "RESEARCH_GROUP",
            "RESEARCH_PROJECTS",
            "TEACHING_COURSES",
            "UNCATEGORIZED",
        ],
    ) -> Collection:
        """
        Create a new (sub-)Dataverse collection within this collection.

        Creates and returns a new sub-collection (child Dataverse) under the current collection,
        using the provided metadata. The parent for the new collection is this collection's alias.

        Note:
            This method only creates the collection metadata. The new collection must still be
            populated with datasets or further subcollections as needed.

        Args:
            alias (str):
                Unique, non-whitespace string identifier for the new collection.
            name (str):
                Human-readable display name for the collection.
            description (str):
                Brief description of the collection's contents or purpose.
            affiliation (str):
                Affiliation or institution related to the collection.
            dataverse_type (Literal):
                Category/type of the collection (see Dataverse documentation for allowed values).
            dataverse_contacts (List[str]):
                List of contact email addresses for this collection.

        Returns:
            Collection:
                The created collection as a local Collection object (the server-side alias is used).

        Example:
            >>> new_coll = collection.create_collection(
            ...     alias="astro-data",
            ...     name="Astrophysics Data",
            ...     description="A collection for astrophysical datasets.",
            ...     affiliation="Department of Astronomy",
            ...     dataverse_type="LABORATORY",
            ...     dataverse_contacts=["astro@university.edu", "info@astro.org"],
            ... )
            >>> print(new_coll.identifier)
        """
        metadata = collection.CollectionCreateBody(
            name=name,
            alias=alias,
            description=description,
            affiliation=affiliation,
            dataverse_type=dataverse_type,
            dataverse_contacts=[
                collection.Contact(contact_email=c) for c in dataverse_contacts
            ],
        )

        if isinstance(self.identifier, int):
            parent = self.metadata.alias
        else:
            parent = self.identifier

        response = self.native_api.create_collection(
            parent=parent,
            metadata=metadata,
        )
        return Collection(dataverse=self.dataverse, identifier=response.alias)

    def graph(
        self,
        format: GraphFormat,
        depth: int = 2,
        max_workers: int = 10,
    ) -> Graph:
        """
        Get the RDF graph of this collection by combining graphs from all child content.

        This method recursively retrieves RDF graphs from all datasets and subcollections
        within this collection and combines them into a single unified graph. It provides
        a comprehensive semantic view of all the metadata contained within the collection
        hierarchy.

        The method works by:
        1. Iterating through all child collections and retrieving their graphs recursively
        2. Iterating through all datasets in this collection and retrieving their graphs
        3. Combining all individual graphs into a single merged RDF graph

        Args:
            format (GraphFormat): A single format string or list of format strings
                specifying the semantic export formats to use for datasets. Valid formats
                are those available in the Dataverse instance that have semantic media types.
                This format is passed down to all child datasets when generating their graphs.
            depth (int): The depth of the graph to retrieve. 1 means only the current collection, 2 means the current collection and all child collections, 3 means the current collection and all child collections and all child datasets, etc.
            max_workers (int): Maximum number of concurrent graph retrieval operations.
                Controls parallelization when fetching graphs from multiple datasets and
                subcollections. Defaults to 10. Higher values increase parallelism but
                may overwhelm the server or consume more resources. Lower values provide
                more conservative resource usage.
        Returns:
            Graph: An rdflib Graph object containing the merged RDF triples from
                all datasets and subcollections within this collection.

        Raises:
            ValueError: If the specified format is not available in the Dataverse instance
                or does not support semantic data representation.
            IndexError: If the collection contains no child content (empty collection).

        Examples:
            Get a comprehensive graph of all content in a collection::

                >>> collection = dataverse.get_collection("my-collection")
                >>> graph = collection.graph("OAI_ORE")
                >>> print(f"Collection graph contains {len(graph)} triples")

            Use multiple formats for richer metadata::

                >>> graph = collection.graph(["OAI_ORE", "JSON-LD"])
                >>> # Query across all datasets in the collection
                >>> query = '''
                ...     SELECT ?dataset ?title WHERE {
                ...         ?dataset a <http://schema.org/Dataset> .
                ...         ?dataset <http://schema.org/name> ?title .
                ...     }
                ... '''
                >>> results = graph.query(query)
                >>> for row in results:
                ...     print(f"Dataset: {row.title}")

            Control parallelization for large collections::

                >>> # Use more workers for faster processing
                >>> graph = collection.graph("OAI_ORE", max_workers=20)
                >>> # Use fewer workers for conservative resource usage
                >>> graph = collection.graph("OAI_ORE", max_workers=5)

        Note:
            This method can be resource-intensive for large collections with many
            datasets, as it fetches and processes metadata for all child content.
            Consider the size of your collection when using this method. The method
            uses async/await internally with a semaphore to control concurrency,
            allowing efficient parallel processing while preventing resource exhaustion.
        """
        return asyncio.run(
            self._graph_async(
                format=format,
                depth=depth,
                max_workers=max_workers,
            )
        )

    async def _graph_async(
        self,
        format: GraphFormat,
        depth: int,
        max_workers: int,
        semaphore: Optional[asyncio.Semaphore] = None,
    ) -> Graph:
        """Internal async implementation with semaphore-based concurrency control."""
        # Base case: if depth is 0 or negative, return empty graph
        if depth <= 0:
            return Graph()

        # Initialize semaphore for concurrency control if not provided
        if semaphore is None:
            semaphore = asyncio.Semaphore(max_workers)

        # Convert synchronous dataset.graph() method to async for concurrent execution
        get_dataset_graph = asyncify(lambda ds: ds.graph(format))

        async def fetch_collection(coll):
            """Fetch graph from a child collection with semaphore protection."""
            async with semaphore:
                return await coll._graph_async(
                    format=format,
                    depth=depth - 1,  # Reduce depth for recursive call
                    max_workers=max_workers,
                    semaphore=semaphore,
                )

        async def fetch_dataset(ds):
            """Fetch graph from a dataset with semaphore protection."""
            async with semaphore:
                return await get_dataset_graph(ds)

        # Build list of tasks for concurrent execution
        tasks = []

        # Add collection tasks only if depth > 1 (to allow recursion)
        if depth > 1:
            tasks.extend(fetch_collection(coll) for coll in self.collections)

        # Always add dataset tasks at current level
        tasks.extend(fetch_dataset(ds) for ds in self.datasets)

        # Return empty graph if no content to process
        if not tasks:
            return Graph()

        # Execute all tasks concurrently and wait for completion
        with Progress(disable=True) as progress:
            task_id = progress.add_task("[cyan]Processing graphs...", total=len(tasks))
            graphs = []
            for coro in asyncio.as_completed(tasks):
                graphs.append(await coro)
                progress.update(task_id, advance=1)

        # Merge all retrieved graphs into a single result
        result = Graph()
        for graph in graphs:
            if graph:  # Only merge non-empty graphs
                result += graph

        # Deduplicate blank nodes with identical properties
        result = _deduplicate_blank_nodes(result)

        return result

    def __len__(self):
        """
        Get the number of direct child contents (datasets and collections) in this collection.

        Returns:
            int: The number of children in this collection.
        """
        return len(self._raw_content)
