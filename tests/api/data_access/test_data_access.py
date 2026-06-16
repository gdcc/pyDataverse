"""Tests for the Data Access API functionality.

This module contains test functions for datafile download, streaming, access management,
and bundle operations.
"""

import io
import zipfile

import httpx
import pandas as pd
import pytest

from pyDataverse.api.data_access import DataAccessApi
from pyDataverse.api.native import NativeApi
from tests.conftest import Credentials, DatasetFactory


class TestDataAccess:
    """Test suite for Data Access API functionality."""

    def test_get_datafile_by_id(
        self,
        data_access_api: DataAccessApi,
        dataset: DatasetFactory,
    ):
        """Test downloading a datafile using its database ID."""
        test_dataset = dataset()

        with test_dataset.open("test_datafile.csv", "w") as f:
            f.write("Hello, world!")

        content = data_access_api.get_datafile(f.id)

        assert content == b"Hello, world!", "File should contain the correct content"

    def test_get_datafile_download_url(
        self,
        data_access_api: DataAccessApi,
        credentials: Credentials,
        dataset: DatasetFactory,
    ):
        """Test getting the direct download URL for a datafile."""
        test_dataset = dataset()

        with test_dataset.open("test_datafile.csv", "w") as f:
            f.write("Hello, world!")

        url = data_access_api.get_datafile_download_url(f.id)

        assert url is not None, "Download URL should be returned"
        assert url.startswith("http://"), "Download URL should start with http://"

        # Use the URL to download the file
        response = httpx.get(
            url,
            follow_redirects=True,
            headers={
                "X-Dataverse-key": credentials.api_token,
            },
        )

        assert response.status_code == 200, "File should be downloaded successfully"
        assert response.text == "Hello, world!", (
            "File should contain the correct content"
        )

    def test_stream_datafile(
        self,
        data_access_api: DataAccessApi,
        dataset: DatasetFactory,
    ):
        """Test streaming a datafile for efficient handling of large files."""
        test_dataset = dataset()

        with test_dataset.open("test_datafile.csv", "w") as f:
            f.write("Hello, world!")

        with data_access_api.stream_datafile(f.id) as response:
            content = b""
            for chunk in response.iter_bytes():
                content += chunk

        assert content == b"Hello, world!", "File should contain the correct content"

    def test_stream_datafile_with_range(
        self,
        data_access_api: DataAccessApi,
        dataset: DatasetFactory,
    ):
        """Test streaming a datafile with byte range request."""
        test_dataset = dataset()

        with test_dataset.open("test_datafile.csv", "w") as f:
            f.write("Hello, world!")

        with data_access_api.stream_datafile(
            f.id, range_start=0, range_end=4
        ) as response:
            content = b""
            for chunk in response.iter_bytes():
                content += chunk

        assert content == b"Hello", "File should contain the correct content"

    def test_get_datafiles_multiple(
        self,
        data_access_api: DataAccessApi,
        dataset: DatasetFactory,
    ):
        """Test downloading multiple datafiles as a ZIP archive."""
        test_dataset = dataset()

        with test_dataset.open("test_datafile.csv", "w") as f:
            f.write("Hello, world!")

        with test_dataset.open("test_datafile2.csv", "w") as f2:
            f2.write("Hello, world2!")

        content = data_access_api.get_datafiles([f.id, f2.id])

        # Read the ZIP archive
        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            assert zip_file.testzip() is None, "ZIP archive should be valid"
            assert zip_file.namelist() == [
                "test_datafile.csv",
                "test_datafile2.csv",
                "MANIFEST.TXT",
            ], "ZIP archive should contain the correct files"

    def test_stream_datafiles_multiple(
        self,
        data_access_api: DataAccessApi,
        credentials: Credentials,
        dataset: DatasetFactory,
    ):
        """Test streaming multiple datafiles as a ZIP archive."""
        test_dataset = dataset()

        with test_dataset.open("test_datafile.csv", "w") as f:
            f.write("Hello, world!")

        with test_dataset.open("test_datafile2.csv", "w") as f2:
            f2.write("Hello, world2!")

        with data_access_api.stream_datafiles([f.id, f2.id]) as response:
            content = bytearray()
            for chunk in response.iter_bytes():
                content.extend(chunk)

        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            assert zip_file.testzip() is None, "ZIP archive should be valid"
            assert zip_file.namelist() == [
                "test_datafile.csv",
                "test_datafile2.csv",
                "MANIFEST.TXT",
            ], "ZIP archive should contain the correct files"

    def test_get_datafile_bundle(
        self,
        data_access_api: DataAccessApi,
        dataset: DatasetFactory,
    ):
        """Test downloading a datafile bundle with all formats."""
        test_dataset = dataset()

        with test_dataset.open("test_datafile.csv", "w") as f:
            df = pd.DataFrame({"Hello": ["world"]})
            f.write(df.to_csv(index=False))

        content = data_access_api.get_datafile_bundle(f.id)

        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            assert zip_file.testzip() is None, "ZIP archive should be valid"
            assert zip_file.namelist() == [
                "test_datafile.tab",
                "test_datafile.csv",
                "test_datafile-ddi.xml",
                "test_datafilecitation-endnote.xml",
                "test_datafilecitation-ris.ris",
                "test_datafilecitation-bib.bib",
            ], "ZIP archive should contain the correct files"

    def test_stream_datafile_bundle(
        self,
        data_access_api: DataAccessApi,
        dataset: DatasetFactory,
    ):
        """Test streaming a datafile bundle for efficient handling of large bundles."""
        test_dataset = dataset()

        with test_dataset.open("test_datafile.csv", "w") as f:
            df = pd.DataFrame({"Hello": ["world"]})
            f.write(df.to_csv(index=False))

        with data_access_api.stream_datafiles_bundle(f.id) as response:
            content = bytearray()
            for chunk in response.iter_bytes():
                content.extend(chunk)

        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            assert zip_file.testzip() is None, "ZIP archive should be valid"
            assert zip_file.namelist() == [
                "test_datafile.tab",
                "test_datafile.csv",
                "test_datafile-ddi.xml",
                "test_datafilecitation-endnote.xml",
                "test_datafilecitation-ris.ris",
                "test_datafilecitation-bib.bib",
            ], "ZIP archive should contain the correct files"

    def test_request_access_to_restricted_file(
        self,
        data_access_api: DataAccessApi,
        native_api: NativeApi,
        dataset: DatasetFactory,
    ):
        """Test requesting access to a restricted datafile."""
        test_dataset = dataset()

        with test_dataset.open("test_datafile.csv", "w") as f:
            f.write("Hello, world!")

        # Now restrict the file
        native_api.restrict_datafile(
            f.id,
            restrict=True,
            enable_access_request=True,
            terms_of_access="Test terms of access",
        )

        test_dataset.publish()

        with pytest.raises(
            httpx.HTTPStatusError,
            match="ERROR: HTTP 400 - You may not request access to this file. It may already be available to you.",
        ):
            # We check for the explicit error, since we have created this file
            # and we are trying to request access to it, which Dataverse does not allow.
            # However, this validates that the function works.
            data_access_api.request_access(f.id)
