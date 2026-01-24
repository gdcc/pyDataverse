import json
import os
from typing import Any
import httpx
from pyDataverse.api import NativeApi


class TestEditDatasetMetadata:
    def test_edit_dataset_metadata_replace(self):
        """
        Test case for editing a dataset's metadata.

        This test case performs the following steps:
        1. Creates a dataset using the provided metadata.
        2. Edits the dataset metadata and replaces the existing metadata.
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
                },
                {
                    "typeName": "datasetContact",
                    "value": [
                        {
                            "datasetContactEmail": {
                                "typeName": "datasetContactEmail",
                                "value": "jane@doe.com",
                            },
                            "datasetContactName": {
                                "typeName": "datasetContactName",
                                "value": "Jane Doe",
                            },
                        }
                    ],
                },
            ]
        }

        # Act
        response = api.edit_dataset_metadata(
            identifier=pid,
            metadata=edit_metadata,
            replace=True,
        )

        response.raise_for_status()

        # Assert
        dataset = api.get_dataset(pid).json()
        new_title = self._get_field_value(dataset, "citation", "title")
        new_contact = self._get_field_value(dataset, "citation", "datasetContact")[0]

        assert new_title == "New Title", "Metadata edit failed."
        assert (
            new_contact["datasetContactEmail"]["value"] == "jane@doe.com"
        ), "Metadata edit failed."
        assert (
            new_contact["datasetContactName"]["value"] == "Jane Doe"
        ), "Metadata edit failed."

    def test_edit_dataset_metadata_add(self):
        """
        Test case for editing a dataset's metadata.

        This test case performs the following steps:
        1. Creates a dataset using the provided metadata.
        2. Edits the dataset metadata and replaces the existing metadata.
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
                {"typeName": "subject", "value": ["Astronomy and Astrophysics"]},
                {"typeName": "subtitle", "value": "Subtitle"},
            ]
        }

        # Act
        response = api.edit_dataset_metadata(
            identifier=pid,
            metadata=edit_metadata,
        )

        response.raise_for_status()

        # Assert
        dataset = api.get_dataset(pid).json()
        new_subject = self._get_field_value(dataset, "citation", "subject")
        new_subtitle = self._get_field_value(dataset, "citation", "subtitle")

        assert "Astronomy and Astrophysics" in new_subject, "Metadata edit failed."
        assert new_subtitle == "Subtitle", "Metadata edit failed."

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

    @staticmethod
    def _get_field_value(data: dict, block: str, field: str) -> Any:
        """
        Get the value of a field in a metadata block.
        """

        blocks = data["data"]["latestVersion"]["metadataBlocks"]

        assert block in blocks, f"Block {block} not found in metadata blocks"

        metadata_block = blocks[block]

        try:
            filtered = next(
                filter(lambda f: f["typeName"] == field, metadata_block["fields"])
            )
            return filtered["value"]
        except StopIteration:
            raise ValueError(f"Field {field} not found in block {block}")
