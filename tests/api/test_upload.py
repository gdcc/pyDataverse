import json
import os
import tempfile

import httpx

from pyDataverse.api import DataAccessApi, NativeApi
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

    def test_file_upload_without_metadata(self):
        """
        Test case for uploading a file to a dataset without metadata.

        --> json_str will be set as None

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

        # Act
        response = api.upload_datafile(
            identifier=pid,
            filename="tests/data/datafile.txt",
            json_str=None,
        )

        # Assert
        assert response.status_code == 200, "File upload failed."

    def test_bulk_file_upload(self, create_mock_file):
        """
        Test case for uploading bulk files to a dataset.

        This test is meant to check the performance of the file upload feature
        and that nothing breaks when uploading multiple files in line.

        This test case performs the following steps:
        0. Create 50 mock files.
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

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create mock files
            mock_files = [
                create_mock_file(
                    filename=f"mock_file_{i}.txt",
                    dir=tmp_dir,
                    size=1024**2,  # 1MB
                )
                for i in range(50)
            ]

            for mock_file in mock_files:
                # Prepare file upload
                df = Datafile({"pid": pid, "filename": os.path.basename(mock_file)})

                # Act
                response = api.upload_datafile(
                    identifier=pid,
                    filename=mock_file,
                    json_str=df.json(),
                )

                # Assert
                assert response.status_code == 200, "File upload failed."

    def test_file_replacement_wo_metadata(self):
        """
        Test case for replacing a file in a dataset without metadata.

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
        data_api = DataAccessApi(BASE_URL, API_TOKEN)

        # Perform file upload
        df = Datafile({"pid": pid, "filename": "datafile.txt"})
        response = api.upload_datafile(
            identifier=pid,
            filename="tests/data/replace.xyz",
            json_str=df.json(),
        )

        response.raise_for_status()

        # Retrieve file ID
        file_id = response.json()["data"]["files"][0]["dataFile"]["id"]

        # Act
        with tempfile.TemporaryDirectory() as tempdir:
            original = open("tests/data/replace.xyz").read()
            mutated = "Z" + original[1::]
            mutated_path = os.path.join(tempdir, "replace.xyz")

            with open(mutated_path, "w") as f:
                f.write(mutated)

            json_data = {}

            response = api.replace_datafile(
                identifier=file_id,
                filename=mutated_path,
                json_str=json.dumps(json_data),
                is_filepid=False,
            )

            response.raise_for_status()

        # Assert
        file_id = response.json()["data"]["files"][0]["dataFile"]["id"]
        content = data_api.get_datafile(file_id, is_pid=False).text

        assert response.status_code == 200, "File replacement failed."
        assert content == mutated, "File content does not match the expected content."

    def test_file_replacement_w_metadata(self):
        """
        Test case for replacing a file in a dataset with metadata.

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
        data_api = DataAccessApi(BASE_URL, API_TOKEN)

        # Perform file upload
        df = Datafile({"pid": pid, "filename": "datafile.txt"})
        response = api.upload_datafile(
            identifier=pid,
            filename="tests/data/replace.xyz",
            json_str=df.json(),
        )

        # Retrieve file ID
        file_id = response.json()["data"]["files"][0]["dataFile"]["id"]

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
                "directoryLabel": "some/other",
            }

            response = api.replace_datafile(
                identifier=file_id,
                filename=mutated_path,
                json_str=json.dumps(json_data),
                is_filepid=False,
            )

        # Assert
        file_id = response.json()["data"]["files"][0]["dataFile"]["id"]
        data_file = api.get_dataset(pid).json()["data"]["latestVersion"]["files"][0]
        content = data_api.get_datafile(file_id, is_pid=False).text

        assert (
            data_file["description"] == "My description."
        ), "Description does not match."
        assert data_file["categories"] == ["Data"], "Categories do not match."
        assert (
            data_file["directoryLabel"] == "some/other"
        ), "Directory label does not match."
        assert response.status_code == 200, "File replacement failed."
        assert content == mutated, "File content does not match the expected content."

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
