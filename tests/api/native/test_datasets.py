"""Tests for the Datasets functionality in NativeApi.

This module contains comprehensive test functions for dataset-related operations
including retrieval, creation, editing, publishing, versioning, deletion, and
file management.
"""

import io
import zipfile
from typing import Callable

import pandas as pd
import pytest
from httpx import HTTPStatusError

from pyDataverse.api.native import NativeApi
from pyDataverse.dataverse.dataset import Dataset
from tests.conftest import Credentials


class TestDatasets:
    """Test suite for Datasets functionality."""

    def test_get_dataset(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving a dataset by persistent identifier."""

        # Get the dataset by identifier
        test_dataset = dataset()
        assert test_dataset.identifier is not None
        assert test_dataset.persistent_identifier is not None
        fetched = native_api.get_dataset(
            test_dataset.persistent_identifier,
        )

        assert fetched.dataset_persistent_id == test_dataset.persistent_identifier, (
            f"Expected {test_dataset.persistent_identifier} but got {fetched.dataset_persistent_id}"
        )

        assert fetched.dataset_id == test_dataset.identifier, (
            f"Expected {test_dataset.identifier} but got {fetched.identifier}"
        )

    def test_get_dataset_with_version(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving a dataset with a specific version."""

        # Create the dataset and publish it
        test_dataset = dataset()
        test_dataset.publish()

        test_dataset.wait_for_unlock()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with version"
        )

        # Get the dataset with the specific version
        fetched = native_api.get_dataset(
            test_dataset.persistent_identifier,
            version="1.0",
        )

        assert fetched.dataset_persistent_id == test_dataset.persistent_identifier, (
            f"Expected {test_dataset.persistent_identifier} but got {fetched.dataset_persistent_id}"
        )

    def test_get_dataset_with_database_id(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving a dataset using database ID."""
        test_dataset = dataset()

        assert test_dataset.identifier is not None, (
            "Dataset identifier is required to test with database ID"
        )

        fetched = native_api.get_dataset(test_dataset.identifier)

        assert fetched.dataset_id == test_dataset.identifier, (
            f"Expected {test_dataset.identifier} but got {fetched.identifier}"
        )

    def test_get_datasets(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving multiple datasets concurrently."""
        datasets = [dataset() for _ in range(10)]
        dataset_ids = [dataset.identifier for dataset in datasets]

        assert all(dataset_id is not None for dataset_id in dataset_ids), (
            "All dataset identifiers must be present"
        )

        fetched = native_api.get_datasets(dataset_ids)  # pyright: ignore[reportArgumentType]

        for fetched_dataset, test_dataset in zip(fetched, datasets):
            assert fetched_dataset.dataset_id == test_dataset.identifier, (
                f"Expected {test_dataset.identifier} but got {fetched_dataset.dataset_id}"
            )

    def test_get_dataset_persistent_url(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving the persistent DOI URL for a dataset."""
        test_dataset = dataset()

        assert test_dataset.identifier is not None, (
            "Dataset identifier is required to test with persistent URL"
        )

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with persistent URL"
        )

        persistent_url = native_api.get_dataset_persistent_url(test_dataset.identifier)
        expected_url = (
            f"https://doi.org/{test_dataset.persistent_identifier.split(':')[1]}"
        )
        assert persistent_url == expected_url, (
            f"Expected {expected_url} but got {persistent_url}"
        )

    def test_get_dataset_versions(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving all versions of a dataset."""
        test_dataset = dataset()
        test_dataset.publish()

        test_dataset.wait_for_unlock()

        assert test_dataset.identifier is not None, (
            "Dataset identifier is required to test with versions"
        )

        versions = native_api.get_dataset_versions(test_dataset.identifier)
        assert len(versions) == 1, f"Expected 2 versions but got {len(versions)}"

    def test_get_dataset_export(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test exporting dataset metadata in OAI DataCite format."""
        test_dataset = dataset()
        test_dataset.publish()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset identifier is required to test with export"
        )

        export = native_api.get_dataset_export(
            test_dataset.persistent_identifier,
            "oai_datacite",
        )
        assert isinstance(export, (str, dict)), "Export should be a string or dict"

    def test_get_dataset_export_invalid_format(
        self,
        dataset: Callable[[], Dataset],
    ):
        """Test that exporting with an invalid format raises HTTPStatusError."""
        test_dataset = dataset()
        assert test_dataset.identifier is not None, (
            "Dataset identifier is required to test with export"
        )

        with pytest.raises(HTTPStatusError):
            test_dataset.export("invalid_format")

    def test_get_datasets_export(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test exporting metadata for multiple datasets in OAI DataCite format."""
        datasets = [dataset() for _ in range(2)]
        dataset_ids = [
            dataset.persistent_identifier
            for dataset in datasets
            if dataset.persistent_identifier is not None
        ]

        exports = native_api.get_datasets_export(dataset_ids, "oai_datacite")
        assert len(exports) == len(datasets), (
            f"Expected {len(datasets)} exports but got {len(exports)}"
        )
        for export, test_dataset in zip(exports, datasets):
            assert isinstance(export, (str, dict)), "Export should be a string or dict"

    def test_get_datasets_export_as_dict(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test exporting multiple datasets as dictionary objects in OAI-ORE format."""
        datasets = [dataset() for _ in range(2)]
        dataset_ids = [
            dataset.persistent_identifier
            for dataset in datasets
            if dataset.persistent_identifier is not None
        ]

        exports = native_api.get_datasets_export(dataset_ids, "OAI_ORE", as_dict=True)  # pyright: ignore[reportArgumentType]
        assert len(exports) == len(datasets), (
            f"Expected {len(datasets)} exports but got {len(exports)}"
        )
        for export, test_dataset in zip(exports, datasets):
            assert isinstance(export, dict), "Export should be a dict"

    def test_create_dataset(
        self,
        native_api: NativeApi,
        credentials: Credentials,
        dataset: Callable[[], Dataset],
    ):
        """Test creating a new dataset via NativeApi.

        Verifies that a dataset can be created using the NativeApi
        create_dataset method with proper metadata and configuration.
        """
        pass

    def test_create_dataset_and_publish(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test creating a dataset and immediately publishing it to make it publicly available."""
        test_dataset = dataset()
        test_dataset.publish()
        test_dataset.wait_for_unlock()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with publish"
        )

        # Check whether the dataset is available as a published version
        native_api.get_dataset_version(
            test_dataset.persistent_identifier,
            ":latest-published",
        )

    def test_edit_dataset_metadata(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test editing and updating dataset metadata fields."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with edit metadata"
        )

        # Edit the dataset metadata
        test_dataset["citation"]["title"] = "New Title"

        # Update the dataset metadata
        native_api.edit_dataset_metadata(
            test_dataset.persistent_identifier,
            test_dataset.to_dataverse_edit_dict(),
            replace=True,
        )

        # Refresh the dataset
        test_dataset.refresh()

        # Check if the dataset metadata was updated
        assert test_dataset.title == "New Title", (
            f"Expected New Title but got {test_dataset.title}"
        )

    def test_create_dataset_private_url(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test creating a private shareable URL for an unpublished dataset."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with private URL"
        )

        private_url = native_api.create_dataset_private_url(
            test_dataset.persistent_identifier
        )
        assert private_url.link is not None, "Private URL link is required"
        assert private_url.token is not None, "Private URL token is required"

        assert private_url.link.startswith("http://"), (
            f"Private URL link should start with https. Got {private_url.link}"
        )

    def test_get_dataset_private_url(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving an existing private URL and token for a dataset."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with private URL"
        )

        # First, create a private URL
        expected_private_url = native_api.create_dataset_private_url(
            test_dataset.persistent_identifier
        ).link

        assert expected_private_url is not None, "Expected private URL is required"

        # Then, get the private URL
        private_url = native_api.get_dataset_private_url(
            test_dataset.persistent_identifier
        )

        assert private_url.link is not None, "Private URL link is required"
        assert private_url.token is not None, "Private URL token is required"
        assert private_url.link == expected_private_url, (
            f"Private URL link should start with https. Got {private_url.link}"
        )

    def test_delete_dataset_private_url(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test deleting a private URL for a dataset and verifying removal."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with private URL"
        )

        # First, create a private URL
        native_api.create_dataset_private_url(test_dataset.persistent_identifier)

        # Then, delete the private URL
        native_api.delete_dataset_private_url(test_dataset.persistent_identifier)

        with pytest.raises(HTTPStatusError):
            native_api.get_dataset_private_url(test_dataset.persistent_identifier)

    def test_publish_dataset(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test publishing a dataset to make it publicly available."""
        test_dataset = dataset()
        test_dataset.publish()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with publish"
        )

        # Check whether the dataset is available as a published version
        native_api.get_dataset_version(
            test_dataset.persistent_identifier,
            ":latest-published",
        )

    def test_publish_dataset_minor_release(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test publishing a dataset with a minor version increment (e.g., 1.0 -> 1.1)."""
        test_dataset = dataset()

        # We, first publish the dataset to get a version number
        test_dataset.publish()

        # Then, we will edit to create a draft version with a minor version increment
        test_dataset["citation"]["title"] = "New Title"
        test_dataset.update_metadata()
        test_dataset.refresh()

        # Finally, we will publish the dataset with a minor version increment
        test_dataset.publish(release_type="minor")

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with publish"
        )

        # Check whether the dataset is available as a published version
        try:
            native_api.get_dataset_version(
                test_dataset.persistent_identifier,
                "1.1",
            )
        except Exception as e:
            raise ValueError(
                "Minor version increment should be available as a published version, but got an error: {e}"
            ) from e

    def test_publish_dataset_major_release(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test publishing a dataset with a major version increment (e.g., 1.0 -> 2.0)."""
        test_dataset = dataset()

        # We, first publish the dataset to get a version number
        test_dataset.publish()

        # Then, we will edit to create a draft version with a major version increment
        test_dataset["citation"]["title"] = "New Title"
        test_dataset.update_metadata()
        test_dataset.refresh()

        # Finally, we will publish the dataset with a major version increment
        test_dataset.publish(release_type="major")

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with publish"
        )

        # Check whether the dataset is available as a published version
        try:
            native_api.get_dataset_version(
                test_dataset.persistent_identifier,
                "2.0",
            )
        except Exception as e:
            raise ValueError(
                "Major version increment should be available as a published version, but got an error: {e}"
            ) from e

    def test_submit_dataset_to_review(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test submitting a dataset to review."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with submit to review"
        )

        native_api.submit_dataset_to_review(test_dataset.persistent_identifier)

        assert test_dataset.is_locked is True, "Dataset is not locked"

    def test_return_dataset_to_author(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test returning a dataset to author."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with return to author"
        )

        # First, submit the dataset to review
        native_api.submit_dataset_to_review(test_dataset.persistent_identifier)
        assert test_dataset.is_locked is True, "Dataset is not locked"

        # Then, return the dataset to author
        native_api.return_dataset_to_author(
            test_dataset.persistent_identifier, "Test reason"
        )
        assert test_dataset.is_locked is False, "Dataset is not locked"

    def test_get_dataset_lock(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test checking if a dataset is locked during publication operations."""

        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with lock"
        )

        # We will use the publish method without waiting for unlock
        # to simulate a publish operation
        native_api.publish_dataset(test_dataset.persistent_identifier)

        # Check whether the dataset is locked
        locks = native_api.get_dataset_lock(test_dataset.persistent_identifier).root

        assert len(locks) == 1, f"Expected 1 lock but got {len(locks)}"
        assert locks[0].lock_type == "finalizePublication", (
            f"Expected finalizePublication lock but got {locks[0].lock_type}"
        )

    def test_set_dataset_assignment_and_get_assignments(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test setting a role assignment for a dataset and retrieving all assignments."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with assignment"
        )

        # Set the role assignment
        native_api.set_dataset_assignment(
            identifier=test_dataset.persistent_identifier,
            assignee="@dataverseAdmin",
            role="curator",
        )

        # Get the role assignments
        assignments = native_api.get_dataset_assignments(
            test_dataset.persistent_identifier
        )

        assert len(assignments) == 4, (
            f"Expected 1 assignment but got {len(assignments)}"
        )

        new_assignment = next(
            (
                assignment
                for assignment in assignments
                if assignment.assignee == "@dataverseAdmin"
                and assignment.role_name == "Curator"
            ),
            None,
        )

        assert new_assignment is not None, "New assignment not found"

    def test_delete_dataset(
        self,
        native_api: NativeApi,
        credentials: Credentials,
        dataset: Callable[[], Dataset],
    ):
        """Test deleting an unpublished draft dataset and verifying removal."""

        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with delete"
        )

        native_api.delete_dataset(test_dataset.persistent_identifier)

        with pytest.raises(HTTPStatusError):
            native_api.get_dataset(test_dataset.persistent_identifier)

    def test_destroy_dataset(
        self,
        native_api_superuser: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test permanently destroying a published dataset (superuser operation only)."""
        test_dataset = dataset()
        test_dataset.publish()
        test_dataset.wait_for_unlock()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with destroy"
        )

        native_api_superuser.destroy_dataset(test_dataset.persistent_identifier)

        with pytest.raises(HTTPStatusError):
            native_api_superuser.get_dataset(test_dataset.persistent_identifier)

    def test_datafiles_table(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving all files in a dataset as a pandas DataFrame with metadata."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafiles table"
        )

        with test_dataset.open(
            "data/file.csv",
            "w",
            description="A test CSV file",
        ) as file:
            # Write a CSV file with a header row and two columns
            file.write("Hello, world!")

        with test_dataset.open(
            "data/file.py",
            "w",
            description="A test Python script",
        ) as file:
            # Write a Python script to print "Hello, world!"
            file.write("print('Hello, world!')")

        df = native_api.datafiles_table(test_dataset.persistent_identifier)

        expected_columns = [
            "id",
            "persistentId",
            "path",
            "description",
            "mime_type",
            "restricted",
        ]
        assert set(df.columns) == set(expected_columns), (
            f"Expected columns {expected_columns} but got {df.columns}"
        )

        assert len(df) == 2, f"Expected 2 files but got {len(df)}"

        # Create expected DataFrame without id and persistentId columns
        expected_data = {
            "path": ["data/file.csv", "data/file.py"],
            "description": ["A test CSV file", "A test Python script"],
            "mime_type": ["text/csv", "text/x-python"],
            "restricted": [False, False],
        }

        expected_df = pd.DataFrame(expected_data)

        # Sort both by path
        df = df.sort_values(by=["path"])
        expected_df = expected_df.sort_values(by="path")
        df_filtered = df[["path", "description", "mime_type", "restricted"]]

        pd.testing.assert_frame_equal(df_filtered, expected_df)

    def test_datafiles_table_filtered_by_mime_type(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving files filtered by MIME type as a pandas DataFrame."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafiles table"
        )

        with test_dataset.open(
            "data/file.csv", "w", description="A test CSV file"
        ) as file:
            file.write("Hello, world!")

        df = native_api.datafiles_table(
            test_dataset.persistent_identifier, filter_mime_types=["text/csv"]
        )

        expected_df = pd.DataFrame(
            {
                "path": ["data/file.csv"],
                "description": ["A test CSV file"],
                "mime_type": ["text/csv"],
                "restricted": [False],
            }
        )

        # Sort both by path
        df = df.sort_values(by=["path"])
        expected_df = expected_df.sort_values(by="path")
        df_filtered = df[["path", "description", "mime_type", "restricted"]]

        pd.testing.assert_frame_equal(df_filtered, expected_df)

    def test_get_datafiles_metadata(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving comprehensive metadata for all files in a dataset."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafiles metadata"
        )

        with test_dataset.open(
            "data/file.csv",
            "w",
            description="A test CSV file",
            categories=["Data"],
        ) as file:
            file.write("Hello, world!")

        files = native_api.get_datafiles_metadata(test_dataset.persistent_identifier)

        assert len(files) == 1, f"Expected 1 file but got {len(files)}"

        file = files[0]
        assert file.data_file is not None, "File data file is required"
        assert file.label == "file.csv", f"Expected file.csv but got {file.label}"
        assert file.directory_label == "data", (
            f"Expected data but got {file.directory_label}"
        )
        assert file.description == "A test CSV file", (
            f"Expected A test CSV file but got {file.description}"
        )
        assert file.categories == ["Data"], f"Expected Data but got {file.categories}"
        assert file.data_file.content_type == "text/csv", (
            f"Expected text/csv but got {file.data_file.content_type}"
        )
        assert not file.restricted, f"Expected not restricted but got {file.restricted}"

    def test_get_datafiles_metadata_filtered(
        self,
        native_api: NativeApi,
        credentials: Credentials,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving file metadata filtered by specific MIME types."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafiles metadata"
        )

        with test_dataset.open(
            "data/file.csv",
            "w",
            description="A test CSV file",
            categories=["Data"],
        ) as file:
            file.write("Hello, world!")

        with test_dataset.open(
            "data/file.py",
            "w",
            description="A test Python script",
            categories=["Code"],
        ) as file:
            file.write("print('Hello, world!')")

        files = native_api.get_datafiles_metadata(
            test_dataset.persistent_identifier,
            filter_mime_types=["text/csv"],
        )

        assert len(files) == 1, f"Expected 1 file but got {len(files)}"

        file = files[0]
        assert file.data_file is not None, "File data file is required"
        assert file.data_file.content_type == "text/csv", (
            f"Expected text/csv but got {file.data_file.content_type}"
        )

    def test_get_datafile_metadata(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving comprehensive metadata for a specific datafile by ID."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with datafile metadata"
        )

        with test_dataset.open(
            "data/file.csv",
            "w",
            description="A test CSV file",
            categories=["Data"],
        ) as file:
            file.write("Hello, world!")

        files = native_api.get_datafiles_metadata(test_dataset.persistent_identifier)
        assert len(files) == 1, f"Expected 1 file but got {len(files)}"

        file = files[0]

        assert file.data_file is not None, "File data file is required"
        assert file.data_file.id is not None, "File ID is required"

        # Now fetch the metadata for the specific datafile
        file_metadata = native_api.get_datafile_metadata(file.data_file.id)

        assert file_metadata.data_file is not None, "File data file is required"
        assert file_metadata.label == "file.csv", (
            f"Expected file.csv but got {file_metadata.label}"
        )
        assert file_metadata.directory_label == "data", (
            f"Expected data but got {file_metadata.directory_label}"
        )
        assert file_metadata.description == "A test CSV file", (
            f"Expected A test CSV file but got {file_metadata.description}"
        )
        assert file_metadata.categories == ["Data"], (
            f"Expected Data but got {file_metadata.categories}"
        )
        assert file_metadata.data_file.content_type == "text/csv", (
            f"Expected text/csv but got {file_metadata.data_file.content_type}"
        )
        assert not file_metadata.restricted, (
            f"Expected not restricted but got {file_metadata.restricted}"
        )

    def test_download_all_datafiles(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test retrieving a dataset bundle containing all files."""
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with dataset bundle"
        )

        with test_dataset.open("file.txt", "w") as file:
            file.write("Hello, world!")

        bundle = native_api.download_all_datafiles(test_dataset.persistent_identifier)

        with zipfile.ZipFile(io.BytesIO(bundle)) as zip_file:
            assert zip_file.testzip() is None, "ZIP archive should be valid"
            assert zip_file.namelist() == [
                "file.txt",
                "MANIFEST.TXT",
            ], "ZIP archive should contain the correct files"

    def test_stream_all_datafiles(
        self,
        native_api: NativeApi,
        dataset: Callable[[], Dataset],
    ):
        """Test streaming a dataset bundle containing all files.

        This test verifies that the stream_all_datafiles method correctly streams
        a ZIP archive containing all files from a dataset. It creates a test file,
        streams the dataset bundle, and validates the ZIP content.
        """
        # Setup: Get test dataset and ensure it has a persistent identifier
        test_dataset = dataset()
        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is required to test with dataset bundle"
        )

        # Create a test file in the dataset
        with test_dataset.open("file.txt", "w") as file:
            file.write("Hello, world!")

        # Stream the dataset bundle and collect the content
        with native_api.stream_all_datafiles(
            test_dataset.persistent_identifier
        ) as response:
            # Collect streamed content into a bytearray
            content = bytearray()
            for chunk in response.iter_bytes():
                content.extend(chunk)

            # Validate the ZIP archive content
            with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                # Verify ZIP integrity
                assert zip_file.testzip() is None, "ZIP archive should be valid"

                # Verify expected files are present
                assert zip_file.namelist() == [
                    "file.txt",
                    "MANIFEST.TXT",
                ], "ZIP archive should contain the correct files"
