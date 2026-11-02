"""Tests for QueryOptions serialization.

These tests check how QueryOptions is turned into Search API query
parameters and do not require a Dataverse instance.
"""

import httpx

from pyDataverse.api.search import QueryOptions


def _query_params(options: QueryOptions) -> httpx.QueryParams:
    """Build the query parameters httpx would send for the given options."""
    params = options.model_dump(by_alias=True, exclude_none=True)
    return httpx.Request(
        "GET", "https://example.org/api/search", params=params
    ).url.params


class TestQueryOptionsFilterQuery:
    """Test suite for the filter_query option."""

    def test_filter_query_by_field_name(self):
        """Test that filter_query is accepted by its field name."""
        options = QueryOptions(filter_query="publicationDate:2020")

        assert options.filter_query == "publicationDate:2020"
        assert _query_params(options)["fq"] == "publicationDate:2020"

    def test_filter_query_by_alias(self):
        """Test that filter_query is accepted by its fq alias."""
        options = QueryOptions(fq="publicationDate:2020")

        assert options.filter_query == "publicationDate:2020"
        assert _query_params(options)["fq"] == "publicationDate:2020"

    def test_filter_query_omitted_by_default(self):
        """Test that fq is not sent when filter_query is not set."""
        assert "fq" not in _query_params(QueryOptions())
