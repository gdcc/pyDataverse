from typing import Literal, Optional

from pydantic import BaseModel, Field, computed_field

from ..models.search import SearchResponse
from .api import Api


class QueryOptions(BaseModel):
    """Configuration options for search queries.

    This class defines all available parameters that can be used to customize
    search behavior, including filtering, sorting, pagination, and result formatting.

    Attributes:
        type: Filter results by content type (dataverse, dataset, or file).
        subtree: Limit search to a specific dataverse and its sub-dataverses.
        sort: Field to sort results by (e.g., 'name', 'date').
        per_page: Number of results to return per page (1-1000, default 10).
        start: Starting index for pagination (default 0).
        order: Sort order, either ascending or descending (default 'desc').
        filter_query: Advanced filter using Solr query syntax.
        show_entity_ids: Whether to include entity IDs in the response.
        show_relevance: Whether to include relevance scores in the response.
        show_facets: Whether to include facet information for result filtering.
        geo_point: Geographic point for spatial search (latitude,longitude format).
        geo_radius: Radius for geographic search (e.g., '10km', '5mi').
    """

    type: Optional[Literal["dataverse", "dataset", "file"]] = Field(
        default=None,
        description="Filter results by content type (dataverse, dataset, or file).",
    )
    subtree: Optional[str] = Field(
        default=None,
        description="Limit search to a specific dataverse.",
    )
    sort: Optional[str] = Field(
        default=None,
        description="Sort field (name, date).",
    )
    per_page: int = Field(
        default=10,
        description="Number of results per page (default 10, max 1000).",
    )
    start: int = Field(
        default=0,
        description="Starting index for pagination (default 0).",
    )
    order: Literal["asc", "desc"] = Field(
        default="desc",
        description="Sort order (asc, desc).",
    )
    filter_query: Optional[str] = Field(
        default=None,
        alias="fq",
        description="Filter query using Solr syntax.",
    )
    show_entity_ids: bool = Field(
        default=False,
        description="Include entity IDs in response.",
    )
    show_relevance: bool = Field(
        default=False,
        description="Include relevance scores.",
    )
    show_facets: bool = Field(
        default=False,
        description="Include facet information.",
    )
    geo_radius: Optional[str] = Field(
        default=None,
        description="Radius for geographic search.",
    )


class SearchApi(Api):
    """Class to access Dataverse's Search API.

    This class provides methods to search through Dataverse content including
    dataverses, datasets, and files. It supports advanced search features like
    filtering, sorting, pagination, and geographic search.

    The Search API uses Solr under the hood, allowing for powerful query capabilities
    including faceted search, relevance scoring, and complex filtering.

    Attributes:
        api_base_url: The base URL for search API endpoints.

    Examples:
        Basic search:
        >>> search_api = SearchApi.from_api(native_api)
        >>> results = search_api.search("climate change")

        Advanced search with options:
        >>> options = QueryOptions(
        ...     type="dataset",
        ...     per_page=20,
        ...     sort="date",
        ...     order="desc"
        ... )
        >>> results = search_api.search("climate", options)
    """

    @computed_field(return_type=str)
    def api_base_url(self):
        """Construct the base URL for search API endpoints.

        Returns:
            The complete URL path for search API requests.
        """
        return f"{self.base_url_api}/search"

    def search(
        self,
        query: str,
        options: Optional[QueryOptions] = None,
    ) -> SearchResponse:
        """Search through Dataverse content.

        Performs a search across dataverses, datasets, and files using the provided
        query string. Supports advanced filtering, sorting, and pagination options.

        The search uses Solr's full-text search capabilities, allowing for:
        - Simple keyword searches
        - Phrase searches (using quotes)
        - Boolean operators (AND, OR, NOT)
        - Wildcard searches (* and ?)
        - Field-specific searches

        HTTP: GET /api/search

        Args:
            query: The search query string. Can include keywords, phrases in quotes,
                boolean operators, and field-specific searches.
            options: Optional configuration for search behavior including filtering,
                sorting, pagination, and result formatting options.

        Returns:
            SearchResponse object containing search results, metadata, and facet
            information if requested.

        Examples:
            Simple keyword search:
            >>> results = search_api.search("climate change")

            Phrase search:
            >>> results = search_api.search('"global warming"')

            Boolean search:
            >>> results = search_api.search("climate AND temperature")

            Field-specific search:
            >>> results = search_api.search("title:climate")

            Search with options:
            >>> options = QueryOptions(type="dataset", per_page=50)
            >>> results = search_api.search("climate", options)

        Raises:
            ApiRequestError: If the search request fails or returns an error.
        """
        params = {"q": query}
        if options:
            params.update(
                options.model_dump(
                    by_alias=True,
                    exclude_none=True,
                )
            )
        return self.get_request(
            url=self.api_base_url,
            params=params,
            response_model=SearchResponse,
        )
