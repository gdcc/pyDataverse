# coding: utf-8
from datetime import datetime
from datetime import timedelta
import os
from pyDataverse.api import Api
from pyDataverse.exceptions import ApiResponseError
from pyDataverse.exceptions import ApiUrlError
import pytest
from requests import Response
from time import sleep


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
SLEEP_TIME = 0.1


class TestApiConnect(object):
    """Test the Api() class initalization."""

    def test_api_connect(self):
        """Test successfull connection without api_token."""
        api = Api(os.environ['BASE_URL'])
        sleep(SLEEP_TIME)
        assert isinstance(api, Api)
        assert not api.api_token
        assert api.api_version == 'v1'
        assert isinstance(api.conn_started, datetime)
        assert api.base_url == os.environ['BASE_URL']
        assert api.native_api_base_url == '{0}/api/{1}'.format(
            os.environ['BASE_URL'], api.api_version)
        assert api.status == 'OK'

    def test_api_connect_base_url_wrong(self):
        """Test api connection with wrong `base_url`."""
        # wrong string
        with pytest.raises(ApiResponseError):
            base_url = 'http://wikipedia.org'
            api = Api(base_url)
            sleep(SLEEP_TIME)
            assert not api.api_token
            assert api.api_version == 'v1'
            assert api.base_url == 'http://wikipedia.org'
            assert api.native_api_base_url == 'http://wikipedia.org/api/v1'
            assert api.status == 'ERROR'

        # None
        with pytest.raises(ApiUrlError):
            base_url = None
            api = Api(base_url)
            sleep(SLEEP_TIME)
            assert not api.api_token
            assert api.api_version == 'v1'
            assert not api.base_url
            assert not api.native_api_base_url
            assert api.status == 'ERROR'


class TestApiRequests(object):
    """Test the api requests."""

    dataset_id = None

    @classmethod
    def setup_class(cls):
        """Create the api connection for later use."""
        cls.dataverse_id = 'test-pyDataverse'

    def test_get_request(self, api_connection):
        """Test successfull `.get_request()` request."""
        # TODO: test params und auth default
        api = api_connection
        query_str = '/info/server'
        resp = api.get_request(query_str)
        sleep(SLEEP_TIME)
        assert api.status == 'OK'
        assert isinstance(resp, Response)

    def test_get_dataverse(self, api_connection):
        """Test successfull `.get_dataverse()` request`."""
        api = api_connection
        resp = api.get_dataverse(':root')
        sleep(SLEEP_TIME)
        assert isinstance(resp, Response)
