import os
import json
import httpx

from pyDataverse.api import DataAccessApi, NativeApi

class TestDataAccess:

    def test_get_data_by_id(self):
        """Tests getting data file by id."""

        # Arrange
        BASE_URL = os.getenv("BASE_URL").rstrip("/")
        API_TOKEN = os.getenv("API_TOKEN")

        assert BASE_URL is not None, "BASE_URL is not set"
        assert API_TOKEN is not None, "API_TOKEN is not set"

        # Create dataset
        metadata = json.load(open("tests/data/file_upload_ds_minimum.json"))
        pid = self._create_dataset(BASE_URL, API_TOKEN, metadata)
        api = DataAccessApi(BASE_URL, API_TOKEN)

        # Upload a file
        self._upload_datafile(BASE_URL, API_TOKEN, pid)

        # Retrieve the file ID
        file_id = self._get_file_id(BASE_URL, API_TOKEN, pid)

        # Act
        response = api.get_datafile(file_id, is_pid=False)
        response.raise_for_status()
        content = response.content.decode("utf-8")

        # Assert
        expected = open("tests/data/datafile.txt").read()
        assert content == expected, "Data retrieval failed."

    def test_get_data_by_pid(self):
        """Tests getting data file by id.

        Test runs with a PID instead of a file ID from Harvard.
        No PID given if used within local containers

        TODO - Check if possible with containers
        """

        # Arrange
        BASE_URL = "https://dataverse.harvard.edu"
        pid = "doi:10.7910/DVN/26093/IGA4JD"
        api = DataAccessApi(BASE_URL)

        # Act
        response = api.get_datafile(pid, is_pid=True)
        response.raise_for_status()
        content = response.content

        # Assert
        expected = self._get_file_content(BASE_URL, pid)
        assert content == expected, "Data retrieval failed."

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
        """Retrieves a file ID for a given persistent identifier (PID) in Dataverse."""

        response = httpx.get(
            url=f"{BASE_URL}/api/datasets/:persistentId/?persistentId={pid}",
            headers={
                "X-Dataverse-key": API_TOKEN,
                "Content-Type": "application/json",
            }
        )

        response.raise_for_status()

        return response.json()["data"]["latestVersion"]["files"][0]["dataFile"]["id"]

    @staticmethod
    def _upload_datafile(
        BASE_URL: str,
        API_TOKEN: str,
        pid: str,
    ):
        """Uploads a file to Dataverse"""

        url = f"{BASE_URL}/api/datasets/:persistentId/add?persistentId={pid}"
        response = httpx.post(
            url=url,
            files={"file": open("tests/data/datafile.txt", "rb")},
            headers={
                "X-Dataverse-key": API_TOKEN,
            },
        )

        response.raise_for_status()

    @staticmethod
    def _get_file_content(
        BASE_URL: str,
        pid: str,
    ):
        """Retrieves the file content for testing purposes."""

        response = httpx.get(
            url=f"{BASE_URL}/api/access/datafile/:persistentId/?persistentId={pid}",
            follow_redirects=True,
        )

        response.raise_for_status()

        return response.content
