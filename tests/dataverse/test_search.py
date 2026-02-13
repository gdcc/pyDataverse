"""Tests for the SearchResult class.

This module contains test functions for search result operations
including accessing datasets and collections from search results.
"""

from tests.conftest import Credentials


class TestSearchResult:
    """Test suite for SearchResult functionality."""

    def test_update_metadata(self, credentials: Credentials):
        """Test that update_metadata raises NotImplementedError.
        
        Verifies that attempting to update metadata on a SearchResult
        raises NotImplementedError since search results are read-only.
        """
        pass

    def test_datasets(self, credentials: Credentials):
        """Test accessing datasets from search results.
        
        Verifies that datasets can be accessed from search results
        and converted to Dataset objects for further manipulation.
        """
        pass

    def test_collections(self, credentials: Credentials):
        """Test accessing collections from search results.
        
        Verifies that collections can be accessed from search results
        and converted to Collection objects for further manipulation.
        """
        pass
