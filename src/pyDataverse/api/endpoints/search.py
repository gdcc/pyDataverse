"""
search.py — Search endpoints for the Dataverse API

This module provides a clean wrapper around Dataverse's search functionality:
- Full-text search
- Filtering by type (dataset, file, dataverse)
- Pagination
- Facets
- Optional entity ID expansion

All HTTP transport is delegated to the shared HttpClient.
"""

from __future__ import annotations

from typing import Any

from ..transport import HttpClient


class SearchEndpoint:
    """
    Wrapper for Dataverse search endpoints.

    Example:
        results = client.search.query("climate change")
        datasets = client.search.query("ocean", type="dataset")
    """

    def __init__(self, http: HttpClient) -> None:
        self.http = http

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def query(
        self,
        query: str,
        type: str | None = None,
        start: int = 0,
        per_page: int = 10,
        show_entity_ids: bool = False,
        sort: str | None = None,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Perform a full-text search.

        GET /api/search
        """
        params: dict[str, Any] = {
            "q": query,
            "start": start,
            "per_page": per_page,
            "show_entity_ids": str(show_entity_ids).lower(),
        }

        if type:
            params["type"] = type

        if sort:
            params["sort"] = sort

        if order:
            params["order"] = order

        result = self.http.get("/api/search", params=params)

        # Dataverse returns a dict with "items"
        return result.get("items", [])

    # ------------------------------------------------------------------
    # Facets
    # ------------------------------------------------------------------

    def facets(self, query: str) -> dict[str, Any]:
        """
        Retrieve facet information for a search query.

        GET /api/search/facets
        """
        return self.http.get("/api/search/facets", params={"q": query})

    # ------------------------------------------------------------------
    # Count
    # ------------------------------------------------------------------

    def count(self, query: str, type: str | None = None) -> int:
        """
        Return the number of search results for a query.

        GET /api/search
        """
        params = {"q": query, "per_page": 0}

        if type:
            params["type"] = type

        result = self.http.get("/api/search", params=params)
        return result.get("total_count", 0)
