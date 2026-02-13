"""Tests for the File class.

This module contains test functions for file-related operations
including metadata access, file operations, and tabular data handling.
"""

import tempfile
from io import BytesIO
from pathlib import Path

import pandas as pd

from pyDataverse.api.native import NativeApi
from pyDataverse.models.file.filemeta import UploadBody
from tests.conftest import Credentials, DatasetFactory


class TestFile:
    """Test suite for File functionality."""

    def test_id_property(
        self,
        dataset: DatasetFactory,
        native_api: NativeApi,
    ):
        """Test accessing the file ID property."""

        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        # Use NativeAPI to upload a file. This will yield a file ID.
        response = native_api.upload_datafile(
            identifier=test_dataset.persistent_identifier,
            file=BytesIO(b"This is a test file."),
            metadata=UploadBody(
                description="This is a test file.",
                filename="file.txt",
            ),
        )

        assert response.files is not None, "Response files are required"
        assert len(response.files) == 1, "Expected 1 file but got {len(response.files)}"
        assert response.files[0].data_file is not None, "File data file is required"

        # Now, get the file via the dataset.files property.
        test_file = test_dataset.files["file.txt"]
        assert test_file.id is not None, "File ID is not set"
        assert test_file.id == response.files[0].data_file.id, "File ID does not match"

    def test_metadata(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test retrieving file metadata."""

        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        # Use NativeAPI to upload a file. This will yield a file ID.
        response = native_api.upload_datafile(
            identifier=test_dataset.persistent_identifier,
            file=BytesIO(b"This is a test file."),
            metadata=UploadBody(
                description="This is a test file.",
                filename="file.txt",
                categories=["Test"],
                directory_label="data",
            ),
        )

        assert response.files is not None, "Response files are required"
        assert len(response.files) == 1, "Expected 1 file but got {len(response.files)}"
        assert response.files[0].data_file is not None, "File data file is required"

        # Now, get the file via the dataset.files property.
        test_file = test_dataset.files["data/file.txt"]

        assert test_file.id is not None, "File ID is not set"
        assert test_file.id == response.files[0].data_file.id, "File ID does not match"
        assert test_file.metadata.description == "This is a test file.", (
            "File description does not match"
        )
        assert test_file.metadata.categories == ["Test"], "File categories do not match"
        assert test_file.metadata.directory_label == "data", (
            "File directory label does not match"
        )

    def test_content_type(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test accessing the file content type."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        content = b"This is a test file."
        native_api.upload_datafile(
            identifier=test_dataset.persistent_identifier,
            file=BytesIO(content),
            metadata=UploadBody(filename="file.txt"),
        )

        test_file = test_dataset.files["file.txt"]
        assert test_file.content_type is not None, "File content type is required"
        assert test_file.content_type == "text/plain", (
            "File content type does not match"
        )

    def test_size(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test accessing the file size."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        content = b"This is a test file."
        native_api.upload_datafile(
            identifier=test_dataset.persistent_identifier,
            file=BytesIO(content),
            metadata=UploadBody(filename="file.txt"),
        )

        test_file = test_dataset.files["file.txt"]
        assert test_file.size is not None, "File size is required"
        assert test_file.size == len(content), "File size does not match"

    def test_path(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test accessing the file path."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        content = b"This is a test file."
        native_api.upload_datafile(
            identifier=test_dataset.persistent_identifier,
            file=BytesIO(content),
            metadata=UploadBody(filename="file.txt", directory_label="data"),
        )

        test_file = test_dataset.files["data/file.txt"]
        assert test_file.path is not None, "File path is required"
        assert test_file.path == "data/file.txt", "File path does not match"

    def test_is_tabular(self, credentials: Credentials, dataset: DatasetFactory):
        """Test checking if file is tabular."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open("data/file.tab", "w") as file:
            # Create a tabular file.
            df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
            file.write(df.to_csv(index=False, sep="\t"))

        test_file = test_dataset.files["data/file.tab"]
        assert test_file.is_tabular is True, "File should be tabular"

    def test_tabular_schema(self, credentials: Credentials, dataset: DatasetFactory):
        """Test retrieving tabular file schema."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open("data/file.tab", "w") as file:
            # Create a tabular file.
            df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
            file.write(df.to_csv(index=False, sep="\t"))

        test_file = test_dataset.files["data/file.tab"]
        assert test_file.tabular_schema is not None, "Tabular schema is required"
        assert test_file.tabular_schema == {"name": "object", "age": "int64"}, (
            "Tabular schema does not match"
        )

    def test_file_is_restricted(self, native_api: NativeApi, dataset: DatasetFactory):
        """Test checking if file is restricted."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        content = b"This is a test file."
        native_api.upload_datafile(
            identifier=test_dataset.persistent_identifier,
            file=BytesIO(content),
            metadata=UploadBody(filename="file.txt", restrict=True),
        )

        test_file = test_dataset.files["file.txt"]
        assert test_file.is_restricted is True, "File should be restricted"

    def test_file_url(self, credentials: Credentials, dataset: DatasetFactory):
        """Test accessing the file URL."""
        test_dataset = dataset()

        with test_dataset.open("data/file.txt", "w") as file:
            file.write("This is a test file.")

        test_file = test_dataset.files["data/file.txt"]
        assert test_file.url is not None, "File URL is required"
        assert test_file.url.startswith(credentials.base_url), (
            "File URL does not start with base URL"
        )

    def test_update_file_metadata(self, dataset: DatasetFactory):
        """Test updating file metadata."""
        test_dataset = dataset()

        with test_dataset.open("data/file.txt", "w") as file:
            file.write("This is a test file.")

        # First, make sure the file description is None.
        assert file.metadata.description is None, (
            "Initial file description should be None"
        )

        # Now, update the file metadata.
        test_file = test_dataset.files["data/file.txt"]
        test_file.update_metadata(
            description="This is a new test file.",
        )

        # Now, make sure the file description is updated.
        assert test_file.metadata.description == "This is a new test file.", (
            "File description does not match"
        )

    def test_open(self, dataset: DatasetFactory):
        """Test opening file for reading."""
        test_dataset = dataset()
        with test_dataset.open("data/file.txt", "w") as file:
            file.write("This is a test file.")

        test_file = test_dataset.files["data/file.txt"]
        with test_file.open() as f:
            assert f.read() == "This is a test file.", "File content does not match"

    def test_open_tabular(self, dataset: DatasetFactory):
        """Test opening tabular file as DataFrame."""
        test_dataset = dataset()
        with test_dataset.open("data/file.tab", "w") as file:
            df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
            file.write(df.to_csv(index=False, sep="\t"))

        test_file = test_dataset.files["data/file.tab"]
        assert test_file.is_tabular is True, "File should be tabular"
        df = test_file.open_tabular()
        assert df.equals(df), "DataFrame does not match"

    def test_stream_tabular_file(self, dataset: DatasetFactory):
        """Test streaming tabular file as chunks."""
        test_dataset = dataset()
        with test_dataset.open("data/file.tab", "w") as file:
            df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
            file.write(df.to_csv(index=False, sep="\t"))

        test_file = test_dataset.files["data/file.tab"]
        assert test_file.is_tabular is True, "File should be tabular"

        df_streamed = pd.concat(list(test_file.stream_tabular()))
        assert df_streamed.equals(df), "DataFrame does not match"

    def test_file_download(
        self,
        dataset: DatasetFactory,
    ):
        """Test downloading file to local path.

        Verifies that files can be downloaded from the dataset to a
        specified local file path with correct content preservation.
        """
        test_dataset = dataset()

        with test_dataset.open("file.txt", "w") as file:
            file.write("This is a test file.")

        with tempfile.TemporaryDirectory() as tmp_path:
            download_path = Path(tmp_path) / "local_copy.txt"
            test_file = test_dataset.files["file.txt"]
            test_file.download(download_path)
            assert download_path.read_text() == "This is a test file.", (
                "File content does not match"
            )
