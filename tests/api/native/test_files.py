"""Tests for the Files functionality in NativeApi.

This module contains comprehensive test functions for file-related operations
including upload, metadata management, deletion, replacement, file type detection,
and tabular file processing.
"""

import os
from io import BytesIO
from tempfile import TemporaryDirectory

import httpx
import pandas as pd
import pytest

from pyDataverse.api.native import NativeApi
from pyDataverse.models.file import update
from pyDataverse.models.file.filemeta import UploadBody
from tests.conftest import Credentials, DatasetFactory


class TestFiles:
    """Test suite for Files functionality."""

    def test_get_datafile_metadata(
        self,
        native_api: NativeApi,
        dataset: DatasetFactory,
    ):
        """Test retrieving metadata for a specific datafile."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open(
            "data/file.csv",
            "w",
        ) as file:
            file.write("Hello, world!")

        file = native_api.get_datafile_metadata(file.id)
        assert file.data_file is not None, "File data file is required"
        assert file.data_file.id is not None, "File ID is required"
        assert file.data_file.persistent_id is not None, (
            "File persistent ID is required"
        )
        assert file.data_file.filename is not None, "File filename is required"
        assert file.data_file.content_type is not None, "File content type is required"
        assert file.data_file.filesize is not None, "File filesize is required"
        assert file.data_file.description is not None, "File description is required"
        assert file.data_file.storage_identifier is not None, (
            "File storage identifier is required"
        )
        assert file.data_file.directory_label is not None, (
            "File directory label is required"
        )
        assert file.data_file.root_data_file_id is not None, (
            "File root data file ID is required"
        )
        assert file.data_file.md5 is not None, "File MD5 is required"

    def test_upload_datafile(
        self, native_api: NativeApi, credentials: Credentials, dataset: DatasetFactory
    ):
        """Test uploading a file to a dataset."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "file.csv")
            with open(file_path, "wb") as file:
                file.write(b"Hello, world!")

            metadata = UploadBody(
                description="A test CSV file",
                directory_label="data",
                filename="file.csv",
            )

            native_api.upload_datafile(
                identifier=test_dataset.persistent_identifier,
                file=file_path,
                metadata=metadata,
            )

        # Get the file from the dataset
        file = test_dataset.files["data/file.csv"]

        assert file.metadata.data_file is not None, "File data file is required"
        assert file.metadata.data_file.id is not None, "File ID is required"
        assert file.metadata.data_file.persistent_id is not None, (
            "File persistent ID is required"
        )
        assert file.metadata.data_file.filename is not None, "File filename is required"
        assert file.metadata.data_file.content_type is not None, (
            "File content type is required"
        )
        assert file.metadata.data_file.filesize is not None, "File filesize is required"

    def test_upload_datafile_with_metadata(
        self, native_api: NativeApi, credentials: Credentials, dataset: DatasetFactory
    ):
        """Test uploading a file with comprehensive metadata.
        
        Verifies that files can be uploaded with detailed metadata including
        description, directory label, categories, and other file properties.
        """
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        metadata = UploadBody(
            description="A test file",
            directory_label="data",
            filename="file.txt",
        )

        response = native_api.upload_datafile(
            identifier=test_dataset.persistent_identifier,
            file=BytesIO(b"A test file"),
            metadata=metadata,
        )

        assert response.files is not None, "Response files are required"
        assert len(response.files) == 1, "Expected 1 file but got {len(response.files)}"
        assert response.files[0].data_file is not None, "File data file is required"
        assert response.files[0].data_file.id is not None, "File ID is required"

        # Fetch the file metadata
        file_metadata = native_api.get_datafile_metadata(response.files[0].data_file.id)
        assert file_metadata.data_file is not None, "File data file is required"
        assert file_metadata.data_file.id is not None, "File ID is required"
        assert file_metadata.data_file.persistent_id is not None, (
            "File persistent ID is required"
        )
        assert file_metadata.data_file.filename == metadata.filename, (
            "File filename does not match"
        )
        assert file_metadata.data_file.description == metadata.description, (
            "File description does not match"
        )
        assert file_metadata.data_file.directory_label == metadata.directory_label, (
            "File directory label does not match"
        )

    def test_upload_datafile_with_path(
        self,
        native_api: NativeApi,
        dataset: DatasetFactory,
    ):
        """Test uploading a file using a local file path.
        
        Verifies that files can be uploaded by providing a path to a local
        file on the filesystem, with proper file handling and metadata.
        """

        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "file.txt")
            with open(file_path, "wb") as file:
                file.write(b"Hello, world!")

            metadata = UploadBody(
                description="A test file",
                directory_label="data",
                filename="file.txt",
            )

            native_api.upload_datafile(
                identifier=test_dataset.persistent_identifier,
                file=file_path,
                metadata=metadata,
            )

    def test_upload_datafile_with_file_object(
        self, native_api: NativeApi, credentials: Credentials, dataset: DatasetFactory
    ):
        """Test uploading a file using a file-like object."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        file_like_object = BytesIO(b"Hello, world!")
        metadata = UploadBody(
            description="A test file",
            directory_label="data",
            filename="file.txt",
        )

        native_api.upload_datafile(
            identifier=test_dataset.persistent_identifier,
            file=file_like_object,
            metadata=metadata,
        )

    def test_update_datafile_metadata(
        self,
        native_api: NativeApi,
        dataset: DatasetFactory,
    ):
        """Test updating metadata for an existing datafile.
        
        Verifies that file metadata including description, categories, and
        provenance information can be updated after file upload.
        """
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open("data/file.txt", "w") as file:
            file.write("Hello, world!")

        native_api.update_datafile_metadata(
            identifier=file.id,
            metadata=update.UpdateBody(
                description="A new test file",
                categories=["Test"],
                prov_freeform="Test prov freeform",
                restrict=False,
            ),
        )

        # Fetch the file metadata
        file_metadata = native_api.get_datafile_metadata(file.id)
        assert file_metadata.data_file is not None, "File data file is required"
        assert file_metadata.data_file.id is not None, "File ID is required"

        assert file_metadata.data_file.directory_label == "data", (
            "File directory label does not match"
        )
        assert file_metadata.data_file.filename == "file.txt", (
            "File filename does not match"
        )
        assert file_metadata.data_file.description == "A new test file", (
            "File description does not match"
        )

    def test_delete_datafile(
        self,
        native_api: NativeApi,
        dataset: DatasetFactory,
    ):
        """Test deleting a datafile from a dataset."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open("data/file.txt", "w") as file:
            file.write("Hello, world!")

        native_api.delete_datafile(file.id)

        with pytest.raises(httpx.HTTPStatusError):
            native_api.get_datafile_metadata(file.id)

    def test_replace_datafile(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test replacing an existing datafile with a new file.
        
        Verifies that an existing file can be replaced with new content
        while preserving the file ID and path structure.
        """
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open("file.txt", "w") as file:
            file.write("Hello, world!")

        native_api.replace_datafile(
            identifier=file.id,
            file=BytesIO(b"Hallo, Welt!"),
            metadata=UploadBody(filename="file.txt"),
        )

        file = test_dataset.files["file.txt"]
        content = file.open().read()
        assert content == "Hallo, Welt!", "File content does not match"

    def test_redetect_file_type(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test redetecting and updating the MIME type of a datafile.
        
        Verifies that the MIME type of an uploaded file can be redetected
        and updated based on file content analysis.
        """
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open("file.txt", "w") as file:
            file.write("Hello, world!")

        native_api.redetect_file_type(file.id)

    def test_redetect_file_type_dry_run(
        self,
        native_api: NativeApi,
        dataset: DatasetFactory,
    ):
        """Test redetecting file type in dry-run mode without applying changes.
        
        Verifies that file type redetection can be performed in dry-run mode
        to preview changes without actually updating the file metadata.
        """
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open("file.txt", "w") as file:
            file.write("Hello, world!")

        native_api.redetect_file_type(file.id, dry_run=True)

    def test_reingest_datafile(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test reingesting a datafile to reprocess its content.
        
        Verifies that tabular files can be reingested to trigger reprocessing
        of their content, useful when file processing failed initially.
        """
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        # First, upload the file with tab_ingest=False to ensure it is not processed
        with test_dataset.open(
            "file.csv",
            "w",
            tab_ingest=False,
        ) as file:
            df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
            file.write(df.to_csv(index=False))

        native_api.reingest_datafile(file.id)

    def test_uningest_datafile(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test uningesting a datafile to remove processed content.
        
        Verifies that tabular file processing can be undone, removing
        processed content and returning the file to an unprocessed state.
        """
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open("file.csv", "w") as file:
            df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
            file.write(df.to_csv(index=False))

        native_api.uningest_datafile(file.id)

    def test_restrict_datafile(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test restricting access to a datafile.
        
        Verifies that file access can be restricted, making the file
        accessible only to authorized users with proper permissions.
        """
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open("file.txt", "w") as file:
            file.write("Hello, world!")

        native_api.restrict_datafile(file.id, restrict=True)

        file = test_dataset.files["file.txt"]
        assert file.is_restricted is True, "File should be restricted"

    def test_unrestrict_datafile(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test removing access restrictions from a datafile.
        
        Verifies that access restrictions can be removed from a file,
        making it publicly accessible again.
        """
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open("file.txt", "w") as file:
            file.write("Hello, world!")

        # First restrict the file
        native_api.restrict_datafile(
            file.id,
            restrict=True,
            enable_access_request=True,
            terms_of_access="Test terms of access",
        )

        file = test_dataset.files["file.txt"]
        assert file.is_restricted is True, "File should be restricted"

        # Then unrestrict the file
        native_api.restrict_datafile(file.id, restrict=False)

        file = test_dataset.files["file.txt"]
        assert file.is_restricted is False, "File should be unrestricted"
