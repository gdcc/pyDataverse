"""Tests for the Search API functionality.

This module contains test functions for searching Dataverse content including
dataverses, datasets, and files with various filtering and sorting options.
"""

import uuid

from pyDataverse.api.search import QueryOptions, SearchApi
from tests.conftest import CollectionFactory, Credentials, DatasetFactory


class TestSearch:
    """Test suite for Search API functionality."""

    def test_search_basic_query(
        self,
        search_api: SearchApi,
        dataset: DatasetFactory,
    ):
        """Test basic keyword search across all content types."""
        new_title = str(uuid.uuid4())
        test_dataset = dataset()
        test_dataset["citation"]["title"] = new_title
        test_dataset.update_metadata()
        test_dataset.publish()

        results = search_api.search(new_title)

        assert results.total_count >= 1, "Total count should be at least 1"
        assert len(results.items) >= 1, "Items should be at least 1"
        assert any(item.name == new_title for item in results.items), (
            "Item name should be the new title"
        )

    def test_search_with_type_filter_dataset(
        self,
        search_api: SearchApi,
        dataset: DatasetFactory,
    ):
        """Test searching with type filter set to datasets only."""
        new_title = str(uuid.uuid4())
        test_dataset = dataset()
        test_dataset["citation"]["title"] = new_title
        test_dataset.update_metadata()
        test_dataset.publish()

        results = search_api.search(new_title, QueryOptions(type="dataset"))
        assert results.total_count >= 1, "Total count should be at least 1"
        assert len(results.items) >= 1, "Items should be at least 1"

    def test_search_with_type_filter_dataverse(
        self,
        search_api: SearchApi,
        collection: CollectionFactory,
    ):
        """Test searching with type filter set to dataverses only."""
        alias = str(uuid.uuid4())
        new_collection = collection(alias)
        results = search_api.search(new_collection.name, QueryOptions(type="dataverse"))

        assert results.total_count >= 1, "Total count should be at least 1"
        assert len(results.items) >= 1, "Items should be at least 1"
        assert any(item.name == new_collection.name for item in results.items), (
            "Item name should be the new collection name"
        )

    def test_search_with_type_filter_file(
        self,
        search_api: SearchApi,
        credentials: Credentials,
        dataset: DatasetFactory,
    ):
        """Test searching with type filter set to files only."""
        test_dataset = dataset()

        filename = f"test_{str(uuid.uuid4())}.txt"
        with test_dataset.open(filename, mode="w") as f:
            f.write("This is a test file")

        test_dataset.publish()

        results = search_api.search(filename, QueryOptions(type="file"))

        assert results.total_count >= 1, "Total count should be at least 1"
        assert len(results.items) >= 1, "Items should be at least 1"
        assert any(item.name == filename for item in results.items), (
            "Item name should be the filename"
        )
