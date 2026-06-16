"""Tests for the Info functionality in NativeApi.

This module contains test functions for info-related operations
including version information, server details, export formats, terms of use, and licenses.
"""

import pytest

from pyDataverse.api.native import NativeApi
from pyDataverse.models import info


class TestInfo:
    """Test suite for Info functionality.
    
    Tests cover retrieving server information, version details, available
    export formats, terms of use, and license information.
    """

    def test_get_info_version(
        self,
        native_api: NativeApi,
    ):
        """Test retrieving Dataverse server version and build information.
        
        Verifies that get_info_version() returns version information including
        the Dataverse version number and build details.
        """

        version = native_api.get_info_version()
        assert version.version is not None, "Version is required"

    def test_get_export_formats(
        self,
        native_api: NativeApi,
    ):
        """Test retrieving available export formats.
        
        Verifies that get_export_formats() returns a dictionary of available
        export formats (e.g., OAI_ORE, OAI_Datacite) with their Exporter objects.
        """
        export_formats = native_api.get_export_formats()
        assert export_formats is not None, "Export formats are required"
        assert len(export_formats) > 0, "Export formats are required"
        assert isinstance(export_formats, dict), "Export formats should be a dictionary"
        assert all(
            isinstance(export_format, info.Exporter)
            for export_format in export_formats.values()
        ), "Export formats should be a dictionary of Exporter objects"

    def test_get_info_server(
        self,
        native_api: NativeApi,
    ):
        """Test retrieving the Dataverse server name and identification.
        
        Verifies that get_info_server() returns server identification information
        including the server name and message.
        """
        server = native_api.get_info_server()
        assert server.message is not None, "Message is required"

    def test_get_info_api_terms_of_use(
        self,
        native_api: NativeApi,
    ):
        """Test retrieving the API Terms of Use URL.
        
        Verifies that get_info_api_terms_of_use() returns the URL or message
        containing the API terms of use information.
        """
        terms_of_use = native_api.get_info_api_terms_of_use()
        assert terms_of_use.message is not None, "Message is required"

    def test_get_available_licenses(
        self,
        native_api: NativeApi,
    ):
        """Test retrieving available licenses.
        
        Verifies that get_available_licenses() returns a list of License objects
        representing all licenses available on the Dataverse instance.
        """
        licenses = native_api.get_available_licenses()
        assert licenses is not None, "Licenses are required"
        assert len(licenses) > 0, "Licenses are required"
        assert isinstance(licenses, list), "Licenses should be a list"
        assert all(isinstance(license, info.License) for license in licenses), (
            "Licenses should be a list of License objects"
        )

    def test_get_license_by_id(self, native_api: NativeApi):
        """Test retrieving license information by numeric identifier.
        
        Verifies that get_license() can retrieve a License object by its numeric ID,
        returning complete license information including name and URI.
        """
        licenses = native_api.get_available_licenses()
        assert licenses is not None, "Licenses are required"
        assert len(licenses) > 0, "Licenses are required"

        # Get one of the licenses
        license = licenses[0]

        license = native_api.get_license(license.id)
        assert license is not None, "License is required"
        assert license.name is not None, "License name is required"
        assert license.uri is not None, "License URI is required"

    def test_get_license_by_name(self, native_api: NativeApi):
        """Test retrieving license information by name.
        
        Verifies that get_license() can retrieve a License object by its name string,
        enabling license lookup by human-readable name rather than numeric ID.
        """
        licenses = native_api.get_available_licenses()
        assert licenses is not None, "Licenses are required"
        assert len(licenses) > 0, "Licenses are required"

        # Get one of the licenses
        license = licenses[0]

        license = native_api.get_license(license.name)
        assert license is not None, "License is required"
        assert license.name is not None, "License name is required"
        assert license.uri == license.uri, "License URI should match"

    def test_get_license_not_found(self, native_api: NativeApi):
        """Test that retrieving a non-existent license raises ValueError.
        
        Verifies that get_license() raises ValueError when attempting to retrieve
        a license that does not exist on the Dataverse instance.
        """
        with pytest.raises(ValueError):
            native_api.get_license("Non-existent license")
