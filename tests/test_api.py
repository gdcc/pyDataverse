from __future__ import unicode_literals, print_function
import configparser
from datetime import datetime
import os
import pytest
from pyDataverse.api import Api


def test_connection_to_api():
    """Test setup of Dataverse API connection.

    Parameters
    ----------


    Returns
    -------
    type
        Description of returned object.

    """
    # TODO: falschen auth-token, falschen host übergeben, falsche api version übergeben
    host = os.environ.get('HOST')
    api_auth_token = os.environ.get('API_AUTH_TOKEN')
    dataverse_api_version = os.environ.get('DATAVERSE_API_VERSION')
    dataverse_version = os.environ.get('DATAVERSE_VERSION')
    api = Api(host, api_auth_token)
    assert isinstance(api, Api)
    assert api.host == host
    assert api.api_token == api_auth_token
    assert api.api_version is not None
    assert isinstance(api.conn_started, datetime)
    assert api.base_url == 'https://'+host
    assert api.api_version == dataverse_api_version
    assert api.native_base_url == 'https://'+host+'/api/v1'
    assert api.dataverse_version == dataverse_version
    api = Api(host, api_auth_token, use_https=False)
    assert api.native_base_url == 'http://'+host+'/api/v1'
