import json
import os

from pyDataverse.api import NativeApi


class TestEditDatasetMetadata:
    def test_edit_dataset_metadata(self):
        """
        Test case for uploading a file to a dataset.

        This test case performs the following steps:
        1. Creates a dataset using the provided metadata.
        2. Edits the dataset metadata.
        3. Asserts that the metadata was edited successfully.

        Raises:
            AssertionError: If the file upload fails.

        """
        # Arrange
        BASE_URL = os.getenv("BASE_URL").rstrip("/")
        API_TOKEN = os.getenv("API_TOKEN")

        # Create dataset
        metadata = json.load(open("tests/data/file_upload_ds_minimum.json"))
        pid = self._create_dataset(BASE_URL, API_TOKEN, metadata)
        api = NativeApi(BASE_URL, API_TOKEN)

        # Prepare file upload
        edit_metadata = {
            "fields": [
                {
                    "typeName": "title",
                    "value": "New Title",
                }
            ]
        }

        # Act
        response = api.edit_dataset_metadata(
            identifier=pid,
            metadata=edit_metadata,
        )

        # Assert
        dataset = api.get_dataset(pid)
        assert (
            dataset.json()["data"]["metadataBlocks"]["citation"]["fields"][0]["value"]
            == "New Title"
        ), "Metadata edit failed."
        assert response.status_code == 200, "Metadata edit failed."
