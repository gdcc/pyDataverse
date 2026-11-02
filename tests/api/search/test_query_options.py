"""Tests for QueryOptions serialization.

These tests check how QueryOptions is turned into Search API query
parameters and do not require a Dataverse instance.
"""

import httpx
import pytest
from pydantic import ValidationError

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


class TestQueryOptionsParameters:
    """Test suite for the Search API parameters exposed by QueryOptions."""

    def test_defaults(self):
        """Test the parameters sent when no options are set."""
        params = _query_params(QueryOptions())

        assert dict(params) == {
            "per_page": "10",
            "start": "0",
            "order": "desc",
            "show_entity_ids": "false",
            "show_relevance": "false",
            "show_facets": "false",
            "show_api_urls": "false",
            "query_entities": "true",
            "show_type_counts": "false",
            "show_collections": "false",
        }

    def test_boolean_options(self):
        """Test that boolean options are sent as lowercase strings."""
        options = QueryOptions(
            show_api_urls=True,
            query_entities=False,
            show_type_counts=True,
            show_collections=True,
        )
        params = _query_params(options)

        assert params["show_api_urls"] == "true"
        assert params["query_entities"] == "false"
        assert params["show_type_counts"] == "true"
        assert params["show_collections"] == "true"

    def test_string_options(self):
        """Test that string options are sent under their API names."""
        options = QueryOptions(
            metadata_fields="citation:author",
            geo_point="42.3,-71.1",
            geo_radius="1.5",
            search_service="solr",
        )
        params = _query_params(options)

        assert params["metadata_fields"] == "citation:author"
        assert params["geo_point"] == "42.3,-71.1"
        assert params["geo_radius"] == "1.5"
        assert params["search_service"] == "solr"

    def test_optional_strings_omitted_by_default(self):
        """Test that unset string options are not sent."""
        params = _query_params(QueryOptions())

        for name in ("metadata_fields", "geo_point", "geo_radius", "search_service"):
            assert name not in params


class TestQueryOptionsRepeatableParameters:
    """Test suite for parameters that the Search API allows to repeat."""

    def test_single_values(self):
        """Test that single values are sent once."""
        options = QueryOptions(
            type="dataset",
            subtree="harvard",
            filter_query="subject:Physics",
            metadata_fields="citation:*",
        )
        params = _query_params(options)

        assert params.get_list("type") == ["dataset"]
        assert params.get_list("subtree") == ["harvard"]
        assert params.get_list("fq") == ["subject:Physics"]
        assert params.get_list("metadata_fields") == ["citation:*"]

    def test_list_values_are_repeated(self):
        """Test that list values are sent as repeated parameters."""
        options = QueryOptions(
            type=["dataset", "file"],
            subtree=["harvard", "mit"],
            filter_query=["subject:Physics", "publicationDate:2020"],
            metadata_fields=["citation:author", "geospatial:*"],
        )
        params = _query_params(options)

        assert params.get_list("type") == ["dataset", "file"]
        assert params.get_list("subtree") == ["harvard", "mit"]
        assert params.get_list("fq") == ["subject:Physics", "publicationDate:2020"]
        assert params.get_list("metadata_fields") == ["citation:author", "geospatial:*"]

    def test_invalid_type_rejected(self):
        """Test that unknown content types are rejected."""
        with pytest.raises(ValidationError):
            QueryOptions(type="collection")

        with pytest.raises(ValidationError):
            QueryOptions(type=["dataset", "collection"])


class TestQueryOptionsValidation:
    """Test suite for QueryOptions value validation."""

    @pytest.mark.parametrize("sort", ["name", "date", "score"])
    def test_valid_sort(self, sort):
        """Test that the documented sort fields are accepted."""
        assert _query_params(QueryOptions(sort=sort))["sort"] == sort

    def test_invalid_sort_rejected(self):
        """Test that unknown sort fields are rejected."""
        with pytest.raises(ValidationError):
            QueryOptions(sort="relevance")

    @pytest.mark.parametrize("per_page", [1, 1000])
    def test_per_page_bounds_accepted(self, per_page):
        """Test that per_page accepts values at the documented limits."""
        assert _query_params(QueryOptions(per_page=per_page))["per_page"] == str(
            per_page
        )

    @pytest.mark.parametrize("per_page", [0, 1001])
    def test_per_page_out_of_range_rejected(self, per_page):
        """Test that per_page outside 1-1000 is rejected."""
        with pytest.raises(ValidationError):
            QueryOptions(per_page=per_page)
