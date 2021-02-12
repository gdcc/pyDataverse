import json
import os
import pytest
from pyDataverse.api import NativeApi
from pyDataverse.exceptions import ApiAuthorizationError
from pyDataverse.exceptions import ApiResponseError
from pyDataverse.exceptions import ApiUrlError
from pyDataverse.models import Dataset
from pyDataverse.utils import read_file
from requests import Response
from .conftest import test_config, import_dataverse_min_dict, import_dataset_min_dict
from ..conftest import BASE_URL
from ..conftest import ROOT_DIR


class TestNativeApi(object):
    class TestApiToken(object):
        """Test user rights."""

        def test_token_missing(self):
            api = NativeApi(BASE_URL)
            resp = api.get_info_version()
            assert resp.json()["data"]["version"] == "4.15.1"
            assert resp.json()["data"]["build"] == "1377-701b56b"

            with pytest.raises(ApiAuthorizationError):
                ds = Dataset()
                ds.from_json(
                    read_file(
                        os.path.join(
                            ROOT_DIR,
                            "tests/data/api/datasets/dataset_upload_default_min_1.json",
                        )
                    )
                )
                api.create_dataset(":root", ds.json())

        def test_token_empty_string(self):
            api = NativeApi(BASE_URL, "")
            resp = api.get_info_version()
            assert resp.json()["data"]["version"] == "4.15.1"
            assert resp.json()["data"]["build"] == "1377-701b56b"

            with pytest.raises(ApiAuthorizationError):
                ds = Dataset()
                ds.from_json(
                    read_file(
                        os.path.join(
                            ROOT_DIR,
                            "tests/data/api/datasets/dataset_upload_default_min_1.json",
                        )
                    )
                )
                api.create_dataset(":root", ds.json())

        def test_token_no_rights(self):
            API_TOKEN = os.getenv("API_TOKEN_NO_RIGHTS")
            api = NativeApi(BASE_URL, API_TOKEN)
            resp = api.get_info_version()
            assert resp.json()["data"]["version"] == "4.15.1"
            assert resp.json()["data"]["build"] == "1377-701b56b"

            with pytest.raises(ApiAuthorizationError):
                ds = Dataset()
                ds.from_json(
                    read_file(
                        os.path.join(
                            ROOT_DIR,
                            "tests/data/api/datasets/dataset_upload_default_min_1.json",
                        )
                    )
                )
                api.create_dataset(":root", ds.json())

        def test_token_right_create_dataset_rights(self):
            api_su = NativeApi(BASE_URL, os.getenv("API_TOKEN_SUPERUSER"))
            api_nru = NativeApi(BASE_URL, os.getenv("API_TOKEN_TEST_NO_RIGHTS"))

            resp = api_su.get_info_version()
            assert resp.json()["data"]["version"] == "4.15.1"
            assert resp.json()["data"]["build"] == "1377-701b56b"
            resp = api_nru.get_info_version()
            assert resp.json()["data"]["version"] == "4.15.1"
            assert resp.json()["data"]["build"] == "1377-701b56b"

            ds = Dataset()
            ds.from_json(
                read_file(
                    os.path.join(
                        ROOT_DIR,
                        "tests/data/api/datasets/dataset_upload_default_min_1.json",
                    )
                )
            )
            resp = api_su.create_dataset(":root", ds.json())
            pid = resp.json()["data"]["persistentId"]
            assert resp.json()["status"] == "OK"

            with pytest.raises(ApiAuthorizationError):
                resp = api_nru.get_dataset(pid)

            resp = api_su.delete_dataset(pid)
            assert resp.json()["status"] == "OK"

    class TestGetInfoVersion(object):
        @pytest.mark.parametrize(
            "test_input, expected",
            [("https://data.aussda.at", ("4.18.1", "267-a91d370"))],
        )
        def test_ok(self, test_input, expected):
            api = NativeApi(test_input)
            resp = api.get_info_version()
            assert resp.status_code == 200
            assert resp.json()["status"] == "OK"
            assert resp.json()["data"]["version"] == expected[0]
            assert resp.json()["data"]["build"] == expected[1]
