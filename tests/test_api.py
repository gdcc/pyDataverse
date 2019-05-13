# coding: utf-8
from __future__ import unicode_literals
from __future__ import print_function
from datetime import datetime
from datetime import timedelta
import os
from pyDataverse.api import Api
from pyDataverse.exceptions import ApiResponseError
from pyDataverse.exceptions import ApiUrlError
from pyDataverse.utils import read_file_json
from pyDataverse.utils import dict_to_json
from pyDataverse.utils import json_to_dict
import pytest
from requests import Response


TEST_DIR = os.path.dirname(os.path.realpath(__file__))


# @pytest.fixture(scope="function")
# def read_json(filename):
#     """Read in json file.
#
#     Parameters
#     ----------
#     filename : string
#         Filename with full path.
#
#     Returns
#     -------
#     dict
#         Data represented as a dict().
#
#     """
#     # do something here?
#     return read_file_json(filename)


class TestApiConnect(object):
    """Test the Api() class initalization."""

    def test_api_connect(self):
        """Test successfull connection without api_token."""
        # TODO: add api_token
        # api_token = os.environ.get('API_AUTH_TOKEN')
        base_url = 'http://demo.dataverse.org'
        api = Api(base_url)
        time_window_start = datetime.now() - timedelta(seconds=10)
        assert isinstance(api, Api)
        assert not api.api_token
        assert api.api_version == 'v1'
        assert api.conn_started > time_window_start
        assert isinstance(api.conn_started, datetime)
        assert api.base_url == 'http://demo.dataverse.org'
        assert api.native_api_base_url == 'http://demo.dataverse.org/api/v1'
        assert api.status == 'OK'

    def test_api_connect_base_url_wrong(self):
        """Test api connection with wrong `base_url`."""
        # wrong string
        with pytest.raises(ApiResponseError):
            base_url = 'http://wikipedia.org'
            api = Api(base_url)
            time_window_start = datetime.now() - timedelta(seconds=10)
            assert not api.api_token
            assert api.api_version == 'v1'
            assert api.conn_started > time_window_start
            assert api.base_url == 'http://wikipedia.org'
            assert api.native_api_base_url == 'http://wikipedia.org/api/v1'
            assert api.status == 'ERROR'

        # None
        with pytest.raises(ApiUrlError):
            base_url = None
            api = Api(base_url)
            time_window_start = datetime.now() - timedelta(seconds=10)
            assert not api.api_token
            assert api.api_version == 'v1'
            assert api.conn_started > time_window_start
            assert not api.base_url
            assert not api.native_api_base_url
            assert api.status == 'ERROR'


class TestApiRequests(object):
    """Test the api requests."""

    @classmethod
    def setup_class(cls):
        """Create the api connection for later use."""
        # cls.base_url = 'http://demo.dataverse.org'
        cls.base_url =
        cls.api_token =
        cls.api = Api(cls.base_url, cls.api_token)
        cls.dataverse_id = 'test-pyDataverse'
        assert cls.api

    def test_make_get_request(self):
        """Test successfull `.make_get_request()` request."""
        # TODO: test params und auth default
        query_str = '/info/server'
        resp = self.api.make_get_request(query_str)
        assert self.api.status == 'OK'
        assert isinstance(resp, Response)

    def test_create_dataverse(self):
        """Test successfull `.create_dataverse()` request`."""
        filename = TEST_DIR+'/data/create_dataverse.json'
        metadata = read_file_json(filename)
        query_str = '/dataverses/{0}'.format(self.dataverse_id)
        resp = self.api.create_dataverse(query_str, dict_to_json(metadata))
        assert isinstance(resp, Response)
        assert self.api.get_dataverse(self.dataverse_id).json()

    def test_get_dataverse(self):
        """Test successfull `.get_dataverse()` request`."""
        query_str = '/dataverses/{0}'.format(self.dataverse_id)
        resp = self.api.get_dataverse(query_str)
        assert isinstance(resp, Response)

    def test_get_dataset(self):
        """Test successfull `.get_dataset()` request`."""
        identifier = 'doi:10.5072/FK2/U6AEZM'
        query_str = '/datasets/:persistentId/?persistentId={0}'.format(
            identifier)
        resp = self.api.get_dataset(query_str)
        assert self.api.status == 'OK'
        assert isinstance(resp, Response)

    def test_delete_dataverse(self):
        """Test successfull `.delete_dataverse()` request`."""
        resp = self.api.delete_dataverse(self.dataverse_id)
        assert isinstance(resp, Response)
