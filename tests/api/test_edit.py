import json
import os
import httpx
from pyDataverse.api import NativeApi


class TestEditDatasetMetadata:
    def test_edit_dataset_metadata(self):
        """
        Test case for editing a dataset's metadata.

        This test case performs the following steps:
        1. Creates a dataset using the provided metadata.
        2. Edits the dataset metadata.
        3. Asserts that the metadata was edited successfully.

        Raises:
            AssertionError: If the metadata edit fails.

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
            dataset.json()["data"]["latestVersion"]["metadataBlocks"]["citation"][
                "fields"
            ][0]["value"]
            == "New Title"
        ), "Metadata edit failed."
        assert response.status_code == 200, "Metadata edit failed."

    @staticmethod
    def _create_dataset(
        BASE_URL: str,
        API_TOKEN: str,
        metadata: dict,
    ):
        """
        Create a dataset in the Dataverse.

        Args:
            BASE_URL (str): The base URL of the Dataverse instance.
            API_TOKEN (str): The API token for authentication.
            metadata (dict): The metadata for the dataset.

        Returns:
            str: The persistent identifier (PID) of the created dataset.
        """
        url = f"{BASE_URL}/api/dataverses/root/datasets"
        response = httpx.post(
            url=url,
            json=metadata,
            headers={
                "X-Dataverse-key": API_TOKEN,
                "Content-Type": "application/json",
            },
        )

        response.raise_for_status()

        return response.json()["data"]["persistentId"]
