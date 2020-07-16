# !/usr/bin/env python
# -*- coding: utf-8 -*-
# from datetime import datetime
# import json
# import os
# from pyDataverse.api import NativeApi
# from pyDataverse.exceptions import ApiResponseError
# from pyDataverse.exceptions import ApiUrlError
# import pytest
# from requests import Response
# from time import sleep
#
#
# TEST_DIR = os.path.dirname(os.path.realpath(__file__))
#
# def native_api_connection():
#     """Fixture, so set up an Api connection.
#
#     Returns
#     -------
#     Api
#         Api object.
#
#     """
#     return NativeApi(BASE_URL, API_TOKEN)
#
#
# class TestApiConnect(object):
#     """Test the Api() class initalization."""
#
#     params = {
#         "test_NAME": [dict(a=1, b=2), dict(a=3, b=3)],
#         "test_NAME": [dict(a=1, b=0)],
#     }
#
#     def test_api_connect(self):
#         """Test successfull connection without api_token."""
#         api = NativeApi('http://localhost:8085')
#         sleep(WAIT_TIME)
#
#         assert isinstance(api, NativeApi)
#         assert not api.api_token
#         assert api.api_version == 'v1'
#         assert api.base_url == BASE_URL
#         assert api.base_url_api_native == '{0}/api/{1}'.format(
#             BASE_URL, api.api_version)
#
#     def test_api_connect_base_url_wrong(self):
#         """Test api connection with wrong `base_url`."""
#         # wrong string as base_url
#         api = NativeApi('http://wikipedia.org')
#         sleep(WAIT_TIME)
#
#         assert not api.api_token
#         assert api.api_version == 'v1'
#         assert api.base_url == 'http://wikipedia.org'
#         assert api.base_url_api_native == 'http://wikipedia.org/api/v1'
#
#         # None as base_url
#         with pytest.raises(ApiUrlError):
#             base_url = None
#             api = NativeApi(base_url)
#             sleep(WAIT_TIME)
#
#             assert not api.api_token
#             assert api.api_version == 'v1'
#             assert not api.base_url
#             assert not api.base_url_api_native
#
#
# class TestApiRequests(object):
#     """Test the api requests."""
#
#     dataset_id = None
#
#     @classmethod
#     def setup_class(cls):
#         """Create the api connection for later use."""
#         cls.parent = DV_PARENT
#         cls.alias = DV_ALIAS
#         cls.dataset_id = None
#
#     def test_create_dataverse(self, import_dataverse_upload_min, native_api_connection):
#         """Test successfull `.create_dataverse()` request`."""
#         if not os.environ.get('TRAVIS'):
#             api = native_api_connection
#             data = import_dataverse_upload_min
#             resp = api.create_dataverse(
#                 self.alias, json.dumps(data), parent=self.parent)
#             sleep(WAIT_TIME)
#
#             assert isinstance(resp, Response)
#             assert api.get_dataverse(self.dataverse_id).json()
#
#     def test_create_dataset(self, import_dataset_min_default, native_api_connection):
#         """Test successfull `.create_dataset()` request`."""
#         if not os.environ.get('TRAVIS'):
#             api = native_api_connection
#             data = import_dataset_min_default
#             resp = api.create_dataset(':root', json.dumps(data))
#             sleep(WAIT_TIME)
#             TestApiRequests.dataset_id = resp.json()['data']['persistentId']
#
#             assert isinstance(resp, Response)
#
#     def test_get_dataset(self, native_api_connection):
#         """Test successfull `.get_dataset()` request`."""
#         if not os.environ.get('TRAVIS'):
#             api = native_api_connection
#             resp = api.get_dataset(TestApiRequests.dataset_id)
#             sleep(WAIT_TIME)
#
#             assert isinstance(resp, Response)
#
#     def test_delete_dataset(self, native_api_connection):
#         """Test successfull `.delete_dataset()` request`."""
#         if not os.environ.get('TRAVIS'):
#             api = native_api_connection
#             resp = api.delete_dataset(TestApiRequests.dataset_id)
#             sleep(WAIT_TIME)
#             assert isinstance(resp, Response)
#
#     def test_delete_dataverse(self, native_api_connection):
#         """Test successfull `.delete_dataverse()` request`."""
#         if not os.environ.get('TRAVIS'):
#             api = native_api_connection
#             resp = api.delete_dataverse(self.dataverse_id)
#             sleep(WAIT_TIME)
#
#             assert isinstance(resp, Response)
#
#     def test_get_request(self, native_api_connection):
#         """Test successfull `.get_request()` request."""
#         # TODO: test params und auth default
#         api = native_api_connection
#         query_str = '/info/server'
#         resp = api.get_request(query_str)
#         sleep(WAIT_TIME)
#
#         assert isinstance(resp, Response)
#
#     def test_get_dataverse(self, native_api_connection):
#         """Test successfull `.get_dataverse()` request`."""
#         api = native_api_connection
#         resp = api.get_dataverse(':root')
#         sleep(WAIT_TIME)
#
#         assert isinstance(resp, Response)
