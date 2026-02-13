from __future__ import annotations

import asyncio
from typing import Annotated, List, Optional
from urllib.parse import parse_qs, urlparse

import httpx
from pydantic import BaseModel, Field, computed_field, field_validator
from toon_format import encode
from typing_extensions import Self

MAXIMUM_PAGE_SIZE = 50
RESOURCE_TYPE_ID = "dataset"


class DataCite(BaseModel):
    """DataCite API client for searching and filtering datasets.

    This class provides methods to search the DataCite API for datasets and
    automatically filter results to only include those hosted on Dataverse instances.
    The filtering works by checking each URL against the Dataverse info/version endpoint
    to verify it's a valid Dataverse instance.

    Attributes:
        data: List of DataItem objects representing the search results.
    """

    data: List[DataItem] = Field(default_factory=list)

    @field_validator("data")
    @classmethod
    def filter_none_urls(cls, data: List[DataItem]) -> List[DataItem]:
        """Filter out items without URLs.

        This validator ensures that only items with valid URLs are included
        in the results, as URLs are required for Dataverse filtering.

        Args:
            data: List of DataItem objects to filter.

        Returns:
            Filtered list containing only items with URLs.
        """
        return [item for item in data if item.attributes.url is not None]

    @staticmethod
    async def _is_dataverse_async(client: httpx.AsyncClient, url: str) -> bool:
        """Check if a URL points to a Dataverse instance.

        This method verifies that a URL points to a Dataverse instance by
        checking the info/version endpoint. A valid Dataverse instance will
        return a JSON response with status "OK".

        Args:
            client: The HTTP client to use for the request.
            url: The URL to check.

        Returns:
            True if the URL points to a Dataverse instance, False otherwise.
        """
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            version_url = f"{base_url}/api/info/version"

            response = await client.get(version_url, timeout=10.0)
            response.raise_for_status()
            json_data = response.json()

            return json_data.get("status") == "OK"

        except Exception:
            return False

    @classmethod
    async def search(
        cls,
        query: Annotated[str, "The search query string to execute"],
        pages: Annotated[int, "Number of pages to search"] = 4,
    ) -> str:
        """Search DataCite for datasets matching the query.

        This method searches the DataCite API and optionally filters results to
        only include Dataverse instances. The search and filtering are performed
        asynchronously for better performance.

        Args:
            query: The search query string.
            page: Page number for pagination (1-indexed). Defaults to 1.
            page_size: Number of results per page (max 50). Defaults to 50.
            filter_dataverse: If True, automatically filter results to only Dataverse
                            instances. If False, return all results without filtering.
                            Defaults to True.

        Returns:
            A DataCite instance with search results.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
            ValueError: If filter_dataverse is True but no Dataverse URLs are found.
        """

        async with httpx.AsyncClient() as client:
            results = cls(data=[])
            for page in range(1, pages + 1):
                response = await client.get(
                    "https://api.datacite.org/dois",
                    params={
                        "query": query,
                        "resource-type-id": RESOURCE_TYPE_ID,
                        "page[number]": page,
                        "page[size]": MAXIMUM_PAGE_SIZE,
                    },
                )
                response.raise_for_status()
                data_cite = cls(**response.json())
                dv_only = await data_cite.filter_dataverse_urls()
                results.data.extend(dv_only.data)

        return encode(results.model_dump(exclude_none=True))

    async def filter_dataverse_urls(self) -> Self:
        """Filter data items to only include those pointing to Dataverse instances.

        This method checks all URLs in the data items in parallel to determine
        which ones point to Dataverse instances. Only items with valid Dataverse
        URLs are kept in the result.

        Returns:
            A new DataCite instance with only Dataverse URLs.

        Raises:
            ValueError: If no URLs are found to check, or if no Dataverse URLs
                       are found after filtering.
        """
        data_cite = self.model_copy(deep=True)
        urls_to_check = [
            (item, item.attributes.url)
            for item in data_cite.data
            if item.attributes.url is not None
        ]

        if not urls_to_check:
            data_cite.data = []
            return data_cite

        async with httpx.AsyncClient() as client:
            # Check all URLs in parallel
            results = await asyncio.gather(
                *[
                    DataCite._is_dataverse_async(client, url)
                    for _, url in urls_to_check
                ],
                return_exceptions=True,
            )

        data_cite.data = [
            item
            for (item, _), result in zip(urls_to_check, results)
            if result is True and not isinstance(result, Exception)
        ]

        return data_cite


class Title(BaseModel):
    """Title information from DataCite.

    Represents a title associated with a dataset in the DataCite API.

    Attributes:
        title: The title string.
    """

    title: str


class Attributes(BaseModel):
    """Attributes of a DataCite data item.

    Contains the core attributes of a dataset item returned from the DataCite API,
    including the URL and associated titles.

    Attributes:
        url: Optional URL pointing to the dataset.
        titles: Optional list of Title objects associated with the dataset.
    """

    url: Optional[str] = None
    titles: Optional[List[Title]] = None


class DataItem(BaseModel):
    """A single data item from DataCite search results.

    Represents a single dataset result from a DataCite search. Provides computed
    properties for easy access to common information like title, base URL, and
    persistent identifier.

    Attributes:
        attributes: The raw attributes from DataCite (excluded from repr).
    """

    attributes: Attributes = Field(alias="attributes", exclude=True, repr=False)

    @computed_field
    @property
    def title(self) -> Optional[str]:
        """Extract the first title from attributes.

        Returns:
            The first title string if available, None otherwise.
        """
        if self.attributes.titles is None or len(self.attributes.titles) == 0:
            return None
        return self.attributes.titles[0].title

    @computed_field
    @property
    def base_url(self) -> Optional[str]:
        """Extract the base URL (scheme + netloc) from the item URL.

        Returns:
            The base URL (e.g., "https://dataverse.example.com") if available,
            None otherwise.
        """
        if self.attributes.url is None:
            return None
        parsed = urlparse(self.attributes.url)
        return f"{parsed.scheme}://{parsed.netloc}"

    @computed_field
    @property
    def persistent_identifier(self) -> Optional[str]:
        """Extract the persistent identifier from the URL query parameters.

        Extracts the persistentId parameter from the URL query string, which
        typically contains the DOI or handle identifier.

        Returns:
            The persistent identifier string if available, None otherwise.
        """
        if self.attributes.url is None:
            return None

        parsed = urlparse(self.attributes.url)
        query_params = parse_qs(parsed.query)
        return query_params.get("persistentId", [None])[0]
