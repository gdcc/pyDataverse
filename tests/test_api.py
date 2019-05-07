# coding: utf-8
from __future__ import unicode_literals
from __future__ import print_function
from datetime import datetime
from datetime import timedelta
from pyDataverse.api import Api
from pyDataverse.exceptions import ApiResponseError
from pyDataverse.exceptions import ApiUrlError
import pytest
from requests import Response


class TestApiInit(object):
    """Test the Api() class initalization."""

    def test_api_connect(self):
        """Test __init__ of Api()."""
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

    def test_make_get_request(self):
        """Test successfull GET request."""
        # TODO: test params und auth default
        base_url = 'http://demo.dataverse.org'
        query_str = '/info/server'
        api = Api(base_url)
        resp = api.make_get_request(query_str)
        assert api.status == 'OK'
        assert isinstance(resp, Response)
