import json
import os
import tempfile

import httpx

from pyDataverse.api import NativeApi
from pyDataverse.models import Datafile


class TestFileUpload:

    def test_file_upload(self):
        """
        Test case for uploading a file to a dataset.

        This test case performs the following steps:
        1. Creates a dataset using the provided metadata.
        2. Prepares a file for upload.
        3. Uploads the file to the dataset.
        4. Asserts that the file upload was successful.

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
        df = Datafile({"pid": pid, "filename": "datafile.txt"})

        # Act
        response = api.upload_datafile(
            identifier=pid,
            filename="tests/data/datafile.txt",
            json_str=df.json(),
        )

        # Assert
        assert response.status_code == 200, "File upload failed."

    def test_file_replacement(self):
        """
        Test case for replacing a file in a dataset.

        Steps:
        1. Create a dataset using the provided metadata.
        2. Upload a datafile to the dataset.
        3. Replace the uploaded datafile with a mutated version.
        4. Verify that the file replacement was successful and the content matches the expected content.
        """
        
        # Arrange
        BASE_URL = os.getenv("BASE_URL").rstrip("/")
        API_TOKEN = os.getenv("API_TOKEN")

        # Create dataset
        metadata = json.load(open("tests/data/file_upload_ds_minimum.json"))
        pid = self._create_dataset(BASE_URL, API_TOKEN, metadata)
        api = NativeApi(BASE_URL, API_TOKEN)

        # Perform file upload
        df = Datafile({"pid": pid, "filename": "datafile.txt"})
        response = api.upload_datafile(
            identifier=pid,
            filename="tests/data/replace.xyz",
            json_str=df.json(),
        )

        # Retrieve file ID
        file_id = self._get_file_id(BASE_URL, API_TOKEN, pid)

        # Act
        with tempfile.TemporaryDirectory() as tempdir:

            original = open("tests/data/replace.xyz").read()
            mutated = "Z" + original[1::]
            mutated_path = os.path.join(tempdir, "replace.xyz")

            with open(mutated_path, "w") as f:
                f.write(mutated)

            json_data = {
                "description": "My description.",
                "categories": ["Data"],
                "forceReplace": False,
            }

            response = api.replace_datafile(
                identifier=file_id,
                filename=mutated_path,
                json_str=json.dumps(json_data),
                is_filepid=False,
            )

        # Assert
        replaced_id = self._get_file_id(BASE_URL, API_TOKEN, pid)
        replaced_content = self._fetch_datafile_content(
            BASE_URL,
            API_TOKEN,
            replaced_id,
        )

        assert response.status_code == 200, "File replacement failed."
        assert (
            replaced_content == mutated
        ), "File content does not match the expected content."

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
    def _get_file_id(
        BASE_URL: str,
        API_TOKEN: str,
        pid: str,
    ):
        """
        Retrieves the file ID for a given persistent identifier (PID) in Dataverse.

        Args:
            BASE_URL (str): The base URL of the Dataverse instance.
            API_TOKEN (str): The API token for authentication.
            pid (str): The persistent identifier (PID) of the dataset.

        Returns:
            str: The file ID of the latest version of the dataset.

        Raises:
            HTTPError: If the HTTP request to retrieve the file ID fails.
        """
        response = httpx.get(
            url=f"{BASE_URL}/api/datasets/:persistentId/?persistentId={pid}",
            headers={"X-Dataverse-key": API_TOKEN},
        )

        response.raise_for_status()

        return response.json()["data"]["latestVersion"]["files"][0]["dataFile"]["id"]

    @staticmethod
    def _fetch_datafile_content(
        BASE_URL: str,
        API_TOKEN: str,
        id: str,
    ):
        """
        Fetches the content of a datafile from the specified BASE_URL using the provided API_TOKEN.

        Args:
            BASE_URL (str): The base URL of the Dataverse instance.
            API_TOKEN (str): The API token for authentication.
            id (str): The ID of the datafile.

        Returns:
            str: The content of the datafile as a decoded UTF-8 string.
        """
        url = f"{BASE_URL}/api/access/datafile/{id}"
        headers = {"X-Dataverse-key": API_TOKEN}
        response = httpx.get(url, headers=headers)
        response.raise_for_status()

        return response.content.decode("utf-8")
