# coding: utf-8
from __future__ import unicode_literals, print_function
from datetime import datetime
import os
from pyDataverse.api import Api


def test_connection_to_api():
    """Test setup of Dataverse API connection."""
    base_url = 'https://'+os.environ.get('HOST')
    api_token = os.environ.get('API_AUTH_TOKEN')
    dataverse_api_version = os.environ.get('DATAVERSE_API_VERSION')
    dataverse_version = os.environ.get('DATAVERSE_VERSION')
    api = Api(base_url, api_token)
    assert isinstance(api, Api)
    assert api.api_token == api_token
    assert api.api_version is not None
    assert isinstance(api.conn_started, datetime)
    assert api.base_url == 'https://'+os.environ.get('HOST')
    assert api.api_version == dataverse_api_version
    assert api.native_api_base_url == api.base_url+'/api/v1'
    assert api.dataverse_version == dataverse_version
