"""Tests for the Dataset class.

This module contains comprehensive test functions for dataset-related operations
including metadata management, file operations, publishing, versioning, locks,
export formats, and data access patterns.
"""

import asyncio
import io
import json
import tempfile
import uuid
import zipfile
from pathlib import Path

import pandas as pd
import pytest
from rdflib import Graph

from pyDataverse.dataverse.dataset import Dataset
from pyDataverse.dataverse.dataverse import Dataverse
from pyDataverse.dataverse.file import File
from pyDataverse.filesystem.dvfs import DataverseFS
from pyDataverse.models import info
from pyDataverse.models.dataset import create, edit_get
from tests.conftest import CollectionFactory, Credentials, DatasetFactory


class TestDataset:
    """Test suite for Dataset functionality.

    Tests cover dataset lifecycle operations including creation, metadata management,
    file operations, publishing, versioning, locking mechanisms, and data export.
    """

    def test_from_doi_url(self):
        """Test creating a Dataset instance from a DOI URL.

        Verifies that a Dataset can be instantiated from a DOI URL string,
        and that both the Dataverse and Dataset objects are properly created
        with the correct persistent identifier.
        """
        DOI_URL = "https://doi.org/10.18419/DARUS-5539"
        dataverse, dataset = Dataset.from_doi_url(DOI_URL)

        assert dataverse is not None, "Dataverse instance is None"
        assert dataset is not None, "Dataset instance is None"
        assert dataset.persistent_identifier == "doi:10.18419/DARUS-5539", (
            "Persistent identifier does not match"
        )

    def test_is_locked(self, dataset: DatasetFactory):
        """Test checking if dataset is locked.

        Verifies that a newly created dataset is unlocked, and that submitting
        it for review correctly sets the locked status to True.
        """

        test_dataset = dataset()

        assert test_dataset.is_locked is False, "Dataset is not locked"

        # Now, submit the dataset to review
        test_dataset.submit_to_review()

        assert test_dataset.is_locked is True, "Dataset is not locked"

    def test_is_in_review(self, dataset: DatasetFactory):
        """Test checking if dataset is in review status.

        Verifies that a newly created dataset is not in review, and that
        submitting it for review correctly sets the in_review status to True.
        """
        test_dataset = dataset()

        assert test_dataset.is_in_review is False, "Dataset is not in review"

        # Now, submit the dataset to review
        test_dataset.submit_to_review()
        assert test_dataset.is_in_review is True, "Dataset is not in review"

    def test_locks(self, dataset: DatasetFactory):
        """Test retrieving and managing dataset locks.

        Verifies that submitting a dataset for review creates an "InReview" lock,
        and that returning it to the author removes all locks.
        """
        test_dataset = dataset()

        # Submit for review
        test_dataset.submit_to_review()

        assert len(test_dataset.locks) == 1, "Dataset locks are not 1"
        assert test_dataset.locks[0].lock_type == "InReview", (
            "Dataset locks are not in review"
        )

        # Return to author
        test_dataset.return_to_author("Test reason")

        # Check that the dataset is not locked anymore
        assert len(test_dataset.locks) == 0, "Dataset locks are not 0"

    @pytest.mark.asyncio
    async def test_wait_for_unlock(self, dataset: DatasetFactory):
        """Test waiting for dataset to unlock asynchronously.

        Verifies that the wait_for_unlock method correctly waits until a dataset
        is unlocked. Tests concurrent submission/return and unlock waiting.
        """
        test_dataset = dataset()

        async def submit_and_return():
            """Submit dataset for review, wait 1 second, then return to author."""
            test_dataset.submit_to_review()
            await asyncio.sleep(1)
            test_dataset.return_to_author("Test reason")

        async def wait_for_unlock():
            """Wait for dataset to unlock."""
            await asyncio.to_thread(test_dataset.wait_for_unlock)

        # Run both tasks in parallel
        await asyncio.gather(
            submit_and_return(),
            wait_for_unlock(),
        )

        # Verify the dataset is unlocked
        assert test_dataset.is_locked is False, "Dataset should be unlocked"

    def test_refresh(self, credentials: Credentials, dataset: DatasetFactory):
        """Test refreshing dataset metadata from the server.

        Verifies that refreshing an out-of-sync dataset instance correctly
        fetches the latest metadata from the server, ensuring consistency
        across multiple dataset instances.
        """
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier is None"
        )

        # First, grab a later out-of-sync instance of the dataset
        old_instance = test_dataset.dataverse.fetch_dataset(
            test_dataset.persistent_identifier
        )

        # Now, update the original dataset instance
        test_dataset.title = "New Title"
        test_dataset.update_metadata()

        # Refresh the original dataset instance
        old_instance.refresh()

        # Verify that the original dataset instance is updated
        assert test_dataset.title == old_instance.title, "Dataset title is not updated"

    def test_url(self, dataset: DatasetFactory):
        """Test accessing the dataset URL property.

        Verifies that the dataset URL is properly constructed and points to
        the correct location on the Dataverse server.
        """
        test_dataset = dataset()
        assert test_dataset.url is not None, "Dataset URL is None"
        assert test_dataset.url.startswith(test_dataset.dataverse.base_url), (
            "Dataset URL is not a valid URL"
        )

    def test_title(self, dataset: DatasetFactory):
        """Test accessing and setting dataset title.

        Verifies that the title can be read, modified, updated on the server,
        and correctly refreshed from the server.
        """
        test_dataset = dataset()

        assert test_dataset.title is not None, "Dataset title is None"
        assert test_dataset.title == "Test Dataset", "Dataset title is not Test Dataset"

        test_dataset.title = "New Title"
        test_dataset.update_metadata()
        test_dataset.refresh()

        assert test_dataset.title == "New Title", "Dataset title is not New Title"

    def test_description(self, dataset: DatasetFactory):
        """Test accessing and setting dataset description.

        Verifies that the description can be read, modified, and updated
        on the server correctly.
        """
        test_dataset = dataset()

        assert test_dataset.description is not None, "Dataset description is None"
        assert test_dataset.description == "This is a test dataset", (
            "Dataset description is not Test Dataset Description"
        )

        test_dataset.description = "New Description"
        test_dataset.update_metadata()

        assert test_dataset.description == "New Description", (
            "Dataset description is not New Description"
        )

    def test_dict(self, dataset: DatasetFactory):
        """Test converting dataset to dictionary representation.

        Verifies that the dict() method correctly exports all dataset metadata
        including identifier, persistent identifier, license, metadata blocks,
        version, and other properties in the expected format.
        """
        test_dataset = dataset()

        # First, export the dataset to a dictionary
        dict_export = test_dataset.dict()

        # Now, create the expected dictionary
        expected_dict = {
            "identifier": test_dataset.identifier,
            "persistent_identifier": test_dataset.persistent_identifier,
            "license": "CC0 1.0",
            "metadata_blocks": {
                "citation": {
                    "title": "Test Dataset",
                    "author": [{"authorName": "Test Author"}],
                    "datasetContact": [
                        {
                            "datasetContactName": "Test Author",
                            "datasetContactEmail": "test@test.com",
                        }
                    ],
                    "dsDescription": [{"dsDescriptionValue": "This is a test dataset"}],
                    "subject": ["Computer and Information Science"],
                }
            },
            "url": test_dataset.url,
            "version": test_dataset.version,
            "title": test_dataset.title,
            "description": "This is a test dataset",
            "authors": [{"authorName": "Test Author"}],
            "subjects": ["Computer and Information Science"],
        }

        assert dict_export is not None, "Dataset dictionary is None"
        assert dict_export == expected_dict, (
            "Dataset dictionary is not a valid dictionary"
        )

    def test_export(self, dataset: DatasetFactory):
        """Test exporting dataset metadata in various formats.

        Verifies that the export method can generate dataset metadata exports
        in different formats (e.g., OAI_ORE) and returns valid export data.
        """
        test_dataset = dataset()

        assert test_dataset.export("OAI_ORE") is not None, "Dataset export is None"

    def test_graph(self, dataset: DatasetFactory):
        """Test retrieving RDF graph representation of dataset.

        Verifies that the graph() method returns a valid RDF Graph object
        (from rdflib) containing semantic metadata about the dataset.
        """

        test_dataset = dataset()
        graph = test_dataset.graph("OAI_ORE")

        assert graph is not None, "Dataset graph is None"
        assert isinstance(graph, Graph), "Dataset graph is not a Graph"

    def test_fs(self, credentials: Credentials, dataset: DatasetFactory):
        """Test accessing the file system interface.

        Verifies that the fs property returns a DataverseFS instance that
        provides file system-like access to dataset files.
        """

        test_dataset = dataset()
        fs = test_dataset.fs

        assert fs is not None, "Dataset file system is None"
        assert isinstance(fs, DataverseFS), "Dataset file system is not a DataverseFS"

    def test_dataset_files(self, credentials: Credentials, dataset: DatasetFactory):
        """Test accessing dataset files through the files view.

        Verifies that files can be written to the dataset, accessed via the
        files dictionary-like interface, and read back with correct content.
        """
        test_dataset = dataset()
        df = pd.DataFrame(
            [
                {"column1": 1, "column2": 4, "column3": 7},
                {"column1": 2, "column2": 5, "column3": 8},
                {"column1": 3, "column2": 6, "column3": 9},
            ],
        )

        with test_dataset.open("data/file.csv", "w", tab_ingest=False) as f:
            f.write(df.to_csv(index=False))

        file = test_dataset.files["data/file.csv"]
        content = file.open("r").read()

        assert file is not None, "Dataset file is None"
        assert isinstance(file, File), "Dataset file is not a File"
        assert content == df.to_csv(index=False), "Dataset file content is not correct"

    def test_dataset_tabular_files(
        self,
        dataset: DatasetFactory,
    ):
        """Test accessing tabular files through the tabular_files view.

        Verifies that CSV files uploaded to the dataset are automatically
        converted to tab-delimited format and can be accessed via the
        tabular_files interface with correct content.
        """
        test_dataset = dataset()
        df = pd.DataFrame(
            [
                {"column1": 1, "column2": 4, "column3": 7},
                {"column1": 2, "column2": 5, "column3": 8},
                {"column1": 3, "column2": 6, "column3": 9},
            ],
        )

        with test_dataset.open("data/file.csv", "w") as f:
            f.write(df.to_csv(index=False))

        file = test_dataset.tabular_files["data/file.tab"]
        content = file.open("r").read()

        assert file is not None, "Dataset file is None"
        assert isinstance(file, File), "Dataset file is not a File"
        assert content == df.to_csv(index=False, sep="\t"), (
            "Dataset file content is not correct"
        )

    def test_dataset_update_metadata(self, dataset: DatasetFactory):
        """Test updating dataset metadata on the server.

        Verifies that changes to dataset properties (title, description, and
        nested metadata fields) can be updated on the server and correctly
        persisted after refresh.
        """
        test_dataset = dataset()
        test_dataset.title = "New Title"
        test_dataset.description = "New Description"

        test_dataset["citation"]["subtitle"] = "New Subtitle"
        test_dataset.update_metadata()
        test_dataset.refresh()

        assert test_dataset.title == "New Title", "Dataset title is not New Title"
        assert test_dataset.description == "New Description", (
            "Dataset description is not New Description"
        )
        assert test_dataset["citation"]["subtitle"] == "New Subtitle", (
            "Dataset subtitle is not New Subtitle"
        )

    def test_publish(self, dataset: DatasetFactory):
        """Test publishing a dataset to make it publicly available.

        Verifies that publishing a dataset creates a published version that
        can be accessed via checkout, and that the persistent identifier
        remains consistent across versions.
        """
        test_dataset = dataset()
        test_dataset.publish()

        # Get the latest published version of the dataset
        latest_published = test_dataset.checkout(":latest-published")

        assert latest_published is not None, "Latest published version is None"
        assert (
            latest_published.persistent_identifier == test_dataset.persistent_identifier
        ), (
            "Latest published version persistent identifier is not the same as the original dataset"
        )

    def test_published_is_latest(self, dataset: DatasetFactory):
        """Test that publishing updates the dataset version correctly.

        Verifies that a draft dataset has version ":draft", and that after
        publishing, the version changes to ":latest-published".
        """
        test_dataset = dataset()

        assert test_dataset.version == ":draft", "Dataset version is not :draft"

        test_dataset.publish()

        assert test_dataset.version == ":latest-published", (
            "Dataset version is not :latest-published"
        )

    def test_upload_to_collection(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test creating and uploading a dataset to a specific collection.

        Verifies that a dataset can be created and automatically uploaded
        to a published collection using the upload_to_collection parameter.
        """

        # Create a test collection
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Create a test dataset
        dataverse.create_dataset(
            title="Test Dataset",
            description="Test Description",
            authors=[{"name": "Test Author"}],
            contacts=[{"name": "Test Author", "email": "test@test.com"}],
            subjects=["Computer and Information Science"],
            upload_to_collection=True,
            collection=col.alias,
            license=dataverse.default_license,
        )

    def test_to_dataverse_create_dict(
        self,
        minimal_dataset: Dataset,
    ):
        """Test converting dataset to Dataverse API create request format.

        Verifies that to_dataverse_create_dict() correctly converts a Dataset
        object into a DatasetCreateBody model with properly structured metadata
        fields matching the Dataverse API requirements.
        """
        create_dict = minimal_dataset.to_dataverse_create_dict()

        assert isinstance(create_dict, create.DatasetCreateBody), (
            f"Expect 'DatasetCreateBody' but got {type(create_dict)}"
        )

        assert minimal_dataset.license is not None, "Dataset license is None"

        if isinstance(minimal_dataset.license, info.License):
            license = minimal_dataset.license.name
        else:
            license = minimal_dataset.license

        expected = create.DatasetCreateBody(
            dataset_type=None,
            dataset_version=create.DatasetVersion(
                license=license,
                metadata_blocks={
                    "citation": create.MetadataBlock(
                        display_name="citation",
                        fields=[
                            create.MetadataField(
                                type_class="primitive",
                                type_name="title",
                                multiple=False,
                                value=minimal_dataset.title,
                            ),
                            create.MetadataField(
                                type_class="compound",
                                type_name="author",
                                multiple=True,
                                value=[
                                    {
                                        "authorName": create.MetadataField(
                                            type_class="primitive",
                                            type_name="authorName",
                                            multiple=False,
                                            value="Test Author",
                                        )
                                    }
                                ],
                            ),
                            create.MetadataField(
                                type_class="compound",
                                type_name="datasetContact",
                                multiple=True,
                                value=[
                                    {
                                        "datasetContactName": create.MetadataField(
                                            type_class="primitive",
                                            type_name="datasetContactName",
                                            multiple=False,
                                            value="Test Author",
                                        ),
                                        "datasetContactEmail": create.MetadataField(
                                            type_class="primitive",
                                            type_name="datasetContactEmail",
                                            multiple=False,
                                            value="test@test.com",
                                        ),
                                    }
                                ],
                            ),
                            create.MetadataField(
                                type_class="compound",
                                type_name="dsDescription",
                                multiple=True,
                                value=[
                                    {
                                        "dsDescriptionValue": create.MetadataField(
                                            type_class="primitive",
                                            type_name="dsDescriptionValue",
                                            multiple=False,
                                            value="This is a test dataset",
                                        )
                                    }
                                ],
                            ),
                            create.MetadataField(
                                type_class="controlledVocabulary",
                                type_name="subject",
                                multiple=True,
                                value=["Computer and Information Science"],
                            ),
                        ],
                    )
                },
            ),
        )

        assert create_dict == expected, (
            "DatasetCreateBody conversion differs from the expected body."
        )

    def test_to_dataverse_edit_dict(self, minimal_dataset: Dataset):
        """Test converting dataset to Dataverse API edit request format.

        Verifies that to_dataverse_edit_dict() correctly converts a Dataset
        object with modifications into an EditMetadataBody model with properly
        structured metadata fields for updating existing datasets.
        """

        minimal_dataset.title = "New Title"
        edit_dict = minimal_dataset.to_dataverse_edit_dict()

        assert isinstance(edit_dict, edit_get.EditMetadataBody), (
            f"Expect 'EditMetadataBody' but got {type(edit_dict)}"
        )

        assert minimal_dataset.license is not None, "Dataset license is None"

        if isinstance(minimal_dataset.license, info.License):
            license = minimal_dataset.license.name
        else:
            license = minimal_dataset.license

        expected = edit_get.EditMetadataBody(
            license=license,
            fields=[
                edit_get.MetadataField(
                    type_class="primitive",
                    type_name="title",
                    multiple=False,
                    value="New Title",
                ),
                edit_get.MetadataField(
                    type_class="compound",
                    type_name="author",
                    multiple=True,
                    value=[
                        {
                            "authorName": edit_get.MetadataField(
                                type_class="primitive",
                                type_name="authorName",
                                multiple=False,
                                value="Test Author",
                            )
                        }
                    ],
                ),
                edit_get.MetadataField(
                    type_class="compound",
                    type_name="datasetContact",
                    multiple=True,
                    value=[
                        {
                            "datasetContactName": edit_get.MetadataField(
                                type_class="primitive",
                                type_name="datasetContactName",
                                multiple=False,
                                value="Test Author",
                            ),
                            "datasetContactEmail": edit_get.MetadataField(
                                type_class="primitive",
                                type_name="datasetContactEmail",
                                multiple=False,
                                value="test@test.com",
                            ),
                        }
                    ],
                ),
                edit_get.MetadataField(
                    type_class="compound",
                    type_name="dsDescription",
                    multiple=True,
                    value=[
                        {
                            "dsDescriptionValue": edit_get.MetadataField(
                                type_class="primitive",
                                type_name="dsDescriptionValue",
                                multiple=False,
                                value="This is a test dataset",
                            )
                        }
                    ],
                ),
                edit_get.MetadataField(
                    type_class="controlledVocabulary",
                    type_name="subject",
                    multiple=True,
                    value=["Computer and Information Science"],
                ),
            ],
        )

        edit_dict_json = json.loads(edit_dict.model_dump_json())
        expected_json = json.loads(expected.model_dump_json())

        assert edit_dict_json == expected_json, (
            "EditMetadataBody conversion differs from the expected body."
        )

    def test_from_dataverse_dict(
        self,
        dataverse: Dataverse,
        minimal_dataset: Dataset,
    ):
        """Test creating a Dataset instance from Dataverse API dictionary format.

        Verifies that from_dataverse_dict() can reconstruct a Dataset object
        from a Dataverse API response dictionary, preserving title, description,
        and license information.
        """

        new_dataset = dataverse.from_dataverse_dict(
            minimal_dataset.to_dataverse_create_dict()
        )

        assert new_dataset.title == minimal_dataset.title, (
            "Dataset title is not the same"
        )

        assert new_dataset.description == minimal_dataset.description, (
            "Dataset description is not the same"
        )

        assert new_dataset.license == minimal_dataset.license, (
            "Dataset license is not the same"
        )

    def test_dataset_open_file(self, dataset: DatasetFactory):
        """Test opening files in the dataset using the context manager interface.

        Verifies that files can be written to and read from the dataset using
        the open() method with file-like context manager semantics, ensuring
        correct content persistence.
        """
        test_dataset = dataset()
        with test_dataset.open("data/file.txt", "w") as f:
            f.write("This is a test file.")

        with test_dataset.open("data/file.txt", "r") as f:
            assert f.read() == "This is a test file.", "File content is not the same"

    def test_upload_file(self, dataset: DatasetFactory):
        """Test uploading a local file to the dataset.

        Verifies that upload_file() can upload a file from the local filesystem
        to the dataset, and that the uploaded file is accessible via the files
        interface with correct content.
        """

        test_dataset = dataset()

        with tempfile.TemporaryDirectory() as path:
            with open(Path(path) / "test.txt", "w") as f:
                f.write("This is a test file.")

            test_dataset.upload_file(Path(path) / "test.txt")

            assert test_dataset.files["test.txt"] is not None, "File is not uploaded"
            assert (
                test_dataset.files["test.txt"].open("r").read()
                == "This is a test file."
            ), "File content is not the same"

    def test_dataset_open_tabular(
        self,
        dataset: DatasetFactory,
    ):
        """Test opening tabular files as pandas DataFrames.

        Verifies that tabular files can be opened directly as pandas DataFrames
        using open_tabular(), and that the data matches the original content
        after Dataverse's automatic tabular file processing.
        """
        test_dataset = dataset()

        df = pd.DataFrame(
            {
                "column1": [1, 2, 3],
                "column2": [4, 5, 6],
                "column3": [7, 8, 9],
            }
        )

        with test_dataset.open("data/file.tab", "w") as f:
            f.write(df.to_csv(index=False, sep="\t"))

        # Wait for unlock
        test_dataset.wait_for_unlock()

        # Now, fetch the file as a pandas DataFrame
        df = test_dataset.open_tabular("data/file.tab")
        assert df is not None, "DataFrame is None"
        assert isinstance(df, pd.DataFrame), "DataFrame is not a pandas DataFrame"
        assert df.equals(df), "DataFrame is not the same"

    def test_dataset_stream_tabular(self, dataset: DatasetFactory):
        """Test streaming tabular files in chunks for memory-efficient access.

        Verifies that stream_tabular() can read large tabular files in chunks,
        and that concatenating the chunks produces a DataFrame identical to
        the original data.
        """

        test_dataset = dataset()

        df = pd.DataFrame(
            {
                "column1": [1, 2, 3],
                "column2": [4, 5, 6],
                "column3": [7, 8, 9],
            }
        )

        with test_dataset.open("data/file.tab", "w") as f:
            f.write(df.to_csv(index=False, sep="\t"))

        # Wait for unlock
        test_dataset.wait_for_unlock()

        # Now, fetch the file as a pandas DataFrame
        series = []
        for chunk in test_dataset.stream_tabular("data/file.tab", chunk_size=1):
            series.append(chunk)

        df_streamed = pd.concat(series)

        assert df_streamed.equals(df), "DataFrame is not the same"

    def test_bundle_datafiles(self, dataset: DatasetFactory):
        """Test bundling dataset files into a ZIP archive.

        Verifies that bundle_datafiles() creates a valid ZIP archive containing
        all dataset files and a MANIFEST.TXT file, suitable for download or backup.
        """

        test_dataset = dataset()

        with test_dataset.open("file.txt", "w") as f:
            f.write("This is a test file.")

        # Wait for unlock
        test_dataset.wait_for_unlock()

        # Now, bundle the file
        bundle = test_dataset.bundle_datafiles(files="all")

        # Read into ZIP file
        with zipfile.ZipFile(io.BytesIO(bundle)) as zip_file:
            assert zip_file.testzip() is None, "ZIP archive should be valid"
            assert zip_file.namelist() == [
                "file.txt",
                "MANIFEST.TXT",
            ], "ZIP archive should contain the correct files"

    def test_bundle_datafiles_stream(self, dataset: DatasetFactory):
        """Test bundling dataset files as ZIP archive in streaming mode.

        Verifies that bundle_datafiles() with stream=True returns a streaming
        response that can be read in chunks, producing a valid ZIP archive
        identical to the non-streaming version.
        """
        test_dataset = dataset()

        with test_dataset.open("file.txt", "w") as f:
            f.write("This is a test file.")

        # Wait for unlock
        test_dataset.wait_for_unlock()

        # Now stream into a file
        content = bytearray()
        with test_dataset.bundle_datafiles(files="all", stream=True) as response:
            for chunk in response.iter_bytes():
                content.extend(chunk)

        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            assert zip_file.testzip() is None, "ZIP archive should be valid"
            assert zip_file.namelist() == [
                "file.txt",
                "MANIFEST.TXT",
            ], "ZIP archive should contain the correct files"

    def test_getitem(self, credentials: Credentials, dataset: DatasetFactory):
        """Test accessing metadata blocks via dictionary-like __getitem__ interface.

        Verifies that metadata blocks can be accessed using dictionary-style
        syntax (e.g., dataset["citation"]) for convenient metadata manipulation.
        """
        pass
