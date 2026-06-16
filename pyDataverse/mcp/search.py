from typing import Annotated, Any, Dict, List, Literal, Optional

from fastmcp import Context
from fastmcp.dependencies import CurrentContext
from pydantic import BaseModel, Field
from toon_format import encode

from ..api.search import QueryOptions
from ..dataverse.search import SearchResult
from .utils import ensure_dataverse

# Maximum number of concurrent requests to the Dataverse API
MAX_CONCURRENT_REQUESTS = 2

# Literal for the filter_by parameter
SearchType = Literal["dataset", "collection"]


class Collection(BaseModel):
    """
    Represents a collection (dataverse) in search results.

    Attributes:
        alias: The collection's alias/identifier
        name: The collection's display name
        description: Optional description of the collection
    """

    alias: str
    name: str
    description: Optional[str] = None


class Dataset(BaseModel):
    """
    Represents a dataset in search results.

    Attributes:
        title: The dataset's title
        description: Optional description of the dataset
        authors: List of author information dictionaries
        subjects: List of subject categories/keywords
    """

    persistent_id: str
    title: str
    description: Optional[str] = None
    authors: List[Dict[str, Any]]
    subjects: List[str]


class CompactSearchResult(BaseModel):
    """
    A compact representation of search results containing datasets and collections.

    Attributes:
        datasets: List of datasets found in the search
        collections: List of collections found in the search
    """

    datasets: List[Dataset] = Field(default_factory=list)
    collections: List[Collection] = Field(default_factory=list)

    @classmethod
    def from_search_result(
        cls, search_result: SearchResult, filter_by: Optional[SearchType] = None
    ):
        """
        Create a CompactSearchResult from a SearchResult object.

        Args:
            search_result: The SearchResult object to convert
            filter_by: Optional filter to include only specific types of results
                      ("dataset" or "file"). If None, includes all types.

        Returns:
            CompactSearchResult: A new instance with filtered and formatted results
        """
        result = cls()

        if filter_by is None or filter_by == "dataset":
            for dataset in search_result.datasets:
                if dataset.persistent_identifier is None:
                    continue

                result.datasets.append(
                    Dataset(
                        persistent_id=dataset.persistent_identifier,
                        title=dataset.title,
                        description=dataset.description,
                        authors=dataset.authors,
                        subjects=dataset.subjects,
                    )
                )
        if filter_by is None or filter_by == "collection":
            for collection in search_result.collections:
                result.collections.append(
                    Collection(
                        alias=collection.alias,
                        name=collection.metadata.name,
                        description=collection.metadata.description,
                    )
                )
        return result


def search(
    query: Annotated[str, "The search query string to execute"],
    collection: Annotated[
        Optional[str],
        "Optional collection identifier to scope the search to. If provided, search will be limited to that collection.",
    ] = None,
    filter_by: Annotated[
        Optional[SearchType],
        "Optional filter to limit results to specific types: 'dataset' for datasets only, 'file' for files (treated as datasets), or None for all types",
    ] = None,
    per_page: Annotated[int, "Maximum number of results to return per page"] = 10,
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse this MCP server is connected to by default.",
    ] = None,
    ctx: Context = CurrentContext(),
):
    """
    Search for datasets and collections in Dataverse.

    This function performs a search across the Dataverse instance, optionally
    scoped to a specific collection. Results can be filtered by type and are
    returned in a compact, encoded format.

    Args:
        query: The search query string to execute
        collection: Optional collection identifier to scope the search to.
                   If provided, search will be limited to that collection.
        filter_by: Optional filter to limit results to specific types:
                  - "dataset": Only return datasets
                  - "file": Only return files (currently treated as datasets)
                  - None: Return all types (datasets and collections)
        per_page: Maximum number of results to return per page (default: 10)
        dataverse_name: Optional name of specific dataverse (for multi-dataverse setups)
        ctx: The MCP context containing the Dataverse connection

    Returns:
        str: Encoded search results as a formatted string containing datasets
             and collections that match the query, with null values excluded.

    Examples:
        >>> search("climate data")
        # Returns all datasets and collections matching "climate data"

        >>> search("temperature", collection="climate-dataverse", filter_by="dataset")
        # Returns only datasets matching "temperature" within "climate-dataverse"
    """

    dataverse = ensure_dataverse(ctx, base_url=base_url)

    if collection:
        coll = dataverse.collections[collection]
        search_result = coll.search(
            query,
            options=QueryOptions(per_page=per_page),
        )
    else:
        search_result = dataverse.search(
            query,
            options=QueryOptions(per_page=per_page),
        )

    return encode(
        CompactSearchResult.from_search_result(search_result, filter_by).model_dump(
            exclude_none=True
        )
    )
