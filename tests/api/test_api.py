from datetime import datetime
import json
import os
import pytest
from requests import Response
from time import sleep
from pyDataverse.api import NativeApi
from pyDataverse.exceptions import ApiResponseError
from pyDataverse.exceptions import ApiUrlError
from ..conftest import test_config, import_dataverse_min_dict, import_dataset_min_dict


class TestApiConnect(object):
    """Test the NativeApi() class initalization."""

    def test_api_connect(self, native_api):
        """Test successfull connection without api_token."""
        native_api = NativeApi(test_config["base_url"])
        sleep(test_config["wait_time"])

        assert isinstance(native_api, NativeApi)
        assert not native_api.api_token
        assert native_api.api_version == "v1"
        assert native_api.base_url == test_config["base_url"]
        assert native_api.base_url_api_native == "{0}/api/{1}".format(
            test_config["base_url"], native_api.api_version
        )

    def test_api_connect_base_url_wrong(self, native_api):
        """Test native_api connection with wrong `base_url`."""
        # None
        with pytest.raises(ApiUrlError):
            base_url = None
            native_api = NativeApi(base_url)
            sleep(test_config["wait_time"])

            assert not native_api.api_token
            assert native_api.api_version == "v1"
            assert not native_api.base_url
            assert not native_api.base_url_api_native


class TestApiRequests(object):
    """Test the native_api requests."""

    dataset_id = None

    @classmethod
    def setup_class(cls):
        """Create the native_api connection for later use."""
        cls.dataverse_id = "test-pyDataverse"
        cls.dataset_id = None

    def test_get_request(self, native_api):
        """Test successfull `.get_request()` request."""
        # TODO: test params und auth default
        query_str = test_config["base_url"] + "/api/v1/info/server"
        resp = native_api.get_request(query_str)
        sleep(test_config["wait_time"])

        assert isinstance(resp, Response)

    def test_get_dataverse(self, native_api):
        """Test successfull `.get_dataverse()` request`."""
        resp = native_api.get_dataverse(":root")
        sleep(test_config["wait_time"])

        assert isinstance(resp, Response)
