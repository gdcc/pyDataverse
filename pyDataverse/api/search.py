import math
from typing import List, Literal, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from ..models.search import SearchResponse
from .api import Api


class QueryOptions(BaseModel):
    """Configuration options for search queries.

    This class defines all available parameters that can be used to customize
    search behavior, including filtering, sorting, pagination, and result formatting.

    Attributes:
        type: Filter results by content type (dataverse, dataset, or file).
            Pass a list to include several types.
        subtree: Limit search to a specific dataverse and its sub-dataverses.
            Pass a list to search several dataverses.
        sort: Field to sort results by ('name', 'date' or 'score'; server default 'score').
        per_page: Number of results to return per page (1-1000, default 10).
        start: Starting index for pagination (default 0).
        order: Sort order, either ascending or descending (default 'desc').
        filter_query: Advanced filter using Solr query syntax. Pass a list
            to apply several filters.
        show_entity_ids: Whether to include entity IDs in the response.
        show_relevance: Whether to include relevance scores in the response.
        show_facets: Whether to include facet information for result filtering.
        show_api_urls: Whether to include API URLs in the response.
        query_entities: Whether to query entities for additional metadata (default True).
        metadata_fields: Metadata fields to include for datasets (e.g., 'citation:author').
            Pass a list to include several fields.
        geo_point: Geographic point for spatial search (latitude,longitude format,
            e.g., '42.3,-71.1'). Must be set together with geo_radius.
        geo_radius: Radius in kilometers from geo_point (e.g., '1.5'). Must be
            set together with geo_point.
        show_type_counts: Whether to include total counts per content type.
        show_collections: Whether to include parent and linked collections for datasets.
        search_service: Name of the search service to use.
    """

    model_config = ConfigDict(populate_by_name=True)

    type: Optional[
        Union[
            Literal["dataverse", "dataset", "file"],
            List[Literal["dataverse", "dataset", "file"]],
        ]
    ] = Field(
        default=None,
        description="Filter results by content type (dataverse, dataset, or file).",
    )
    subtree: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Limit search to a specific dataverse.",
    )
    sort: Optional[Literal["name", "date", "score"]] = Field(
        default=None,
        description="Sort field (name, date, score).",
    )
    per_page: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Number of results per page (default 10, max 1000).",
    )
    start: int = Field(
        default=0,
        ge=0,
        description="Starting index for pagination (default 0).",
    )
    order: Literal["asc", "desc"] = Field(
        default="desc",
        description="Sort order (asc, desc).",
    )
    filter_query: Optional[Union[str, List[str]]] = Field(
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
    show_api_urls: bool = Field(
        default=False,
        description="Include API URLs in response.",
    )
    query_entities: bool = Field(
        default=True,
        description="Query entities for additional metadata (slower).",
    )
    metadata_fields: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Metadata fields to include (block:field or block:*).",
    )
    geo_point: Optional[str] = Field(
        default=None,
        description="Point for geographic search (latitude,longitude).",
    )
    geo_radius: Optional[str] = Field(
        default=None,
        description="Radius in kilometers for geographic search.",
    )
    show_type_counts: bool = Field(
        default=False,
        description="Include total counts per content type.",
    )
    show_collections: bool = Field(
        default=False,
        description="Include parent and linked collections for datasets.",
    )
    search_service: Optional[str] = Field(
        default=None,
        description="Name of the search service to use.",
    )

    @field_validator("geo_point")
    @classmethod
    def _validate_geo_point(cls, value: Optional[str]) -> Optional[str]:
        lat_max = 90
        lat_min = -90
        lon_max = 180
        lon_min = -180

        if value is None:
            return value
        try:
            if any(char.isspace() for char in value):
                raise ValueError
            lat, lon = (float(part) for part in value.split(","))
        except ValueError:
            msg = "geo_point must be 'latitude,longitude', e.g. '42.3,-71.1'"
            raise ValueError(
                msg
            ) from None
        if not lat_min <= lat <= lat_max:
            msg = "geo_point latitude must be between -90 and 90"
            raise ValueError(msg)
        if not lon_min <= lon <= lon_max:
            msg = "geo_point longitude must be between -180 and 180"
            raise ValueError(msg)
        return value

    @field_validator("geo_radius")
    @classmethod
    def _validate_geo_radius(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        try:
            radius = float(value)
        except ValueError:
            msg = "geo_radius must be a number of kilometers"
            raise ValueError(msg) from None
        if not (math.isfinite(radius) and radius > 0):
            msg = "geo_radius must be a positive number of kilometers"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def _validate_geo_pair(self) -> "QueryOptions":
        if (self.geo_point is None) != (self.geo_radius is None):
            msg = "geo_point and geo_radius must be set together"
            raise ValueError(msg)
        return self


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
