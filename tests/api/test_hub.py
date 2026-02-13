"""Tests for the Dataverse Hub API.

This module contains test functions for retrieving information about
Dataverse installations from the global Hub registry.
"""

from pyDataverse.api.hub import DataverseHub


class TestHub:
    """Test suite for the Hub API.
    
    Tests cover retrieving information about Dataverse installations
    from the global Hub registry.
    """

    def test_installations(self):
        """Test retrieving the status of all Dataverse installations.
        
        Verifies that the installations property returns a non-empty list
        of Dataverse installation information from the Hub registry.
        """
        installations = DataverseHub().installations
        assert installations is not None, "No installations found"
        assert len(installations) > 0, "No installations found"
