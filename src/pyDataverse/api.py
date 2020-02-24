# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse API connector."""
from datetime import datetime
import json
from pyDataverse.exceptions import ApiAuthorizationError
from pyDataverse.exceptions import ApiResponseError
from pyDataverse.exceptions import ApiUrlError
from pyDataverse.exceptions import DatasetNotFoundError
from pyDataverse.exceptions import DataverseNotEmptyError
from pyDataverse.exceptions import DataverseNotFoundError
from pyDataverse.exceptions import OperationFailedError
from requests import ConnectionError
from requests import delete
from requests import get
from requests import post
from requests import put
import subprocess as sp


class Api(object):
    """Api class.

    Parameters
    ----------
        base_url : string
            Base URL of Dataverse instance. Without trailing `/` at the end.
            e.g. `http://demo.dataverse.org`
        api_token : string
            Authenication token for the api.
        api_version : string
            Dataverse api version. Defaults to `v1`.

    Attributes
    ----------
    conn_started : datetime
        Time when `Api()` was instantiated, the connection got established.
    native_api_base_url : string
        Url of Dataverse's native Api.
    base_url
    api_token
    api_version
    dataverse_version

    """

    def __init__(self, base_url, api_token=None, api_version='v1'):
        """Init an Api() class.

        Scheme, host and path combined create the base-url for the api.
        See more about URL at `Wikipedia <https://en.wikipedia.org/wiki/URL>`_.

        Parameters
        ----------
        base_url : string
            Base url for Dataverse api.
        api_token : string
            Api token for Dataverse api.
        api_version : string
            Api version of Dataverse native api. Default is `v1`.

        Examples
        -------
        Create an Api connection::

            >>> from pyDataverse.api import Api
            >>> base_url = 'http://demo.dataverse.org'
            >>> api = Api(base_url)
            >>> api.status
            'OK'

        """
        # Check and set basic variables.
        if not isinstance(base_url, ("".__class__, u"".__class__)):
            raise ApiUrlError('base_url {0} is not a string.'.format(base_url))
        self.base_url = base_url

        if not isinstance(api_version, ("".__class__, u"".__class__)):
            raise ApiUrlError('api_version {0} is not a string.'.format(
                api_version))
        self.api_version = api_version

        if api_token:
            if not isinstance(api_token, ("".__class__, u"".__class__)):
                raise ApiAuthorizationError(
                    'Api token passed is not a string.')
        self.api_token = api_token
        self.timeout = 500
        self.conn_started = datetime.now() # TODO: Maybe set var later?

        # Test connection.
        if base_url and api_version:
            self.native_api_base_url = '{0}/api/{1}'.format(self.base_url,
                                                            self.api_version)
            path = '/info/server'
            url = '{0}{1}'.format(self.native_api_base_url, path)
            try:
                resp = get(url)
                if resp:
                    self.status = resp.json()['status']
                else:
                    self.status = 'ERROR'
                    raise ApiResponseError(
                        'No response from api request {0}.'.format(url)
                    )
            except KeyError as e:
                print('ERROR: Key not in response {0} {1}.'.format(e, url))
            except ConnectionError as e:
                self.status = 'ERROR'
                print(
                    'ERROR: Could not establish connection to url {0} {1}.'
                    ''.format(url, e))
        else:
            self.status = 'ERROR'
            self.native_api_base_url = None

        try:
            resp = self.get_info_version()
            if 'data' in resp.json().keys():
                if 'version' in resp.json()['data'].keys():
                    self.dataverse_version = resp.json()['data']['version']
                else:
                    # TODO: raise exception
                    self.dataverse_version = None
                    print('Key not in response.')
            else:
                self.dataverse_version = None
                # TODO: raise exception
                print('Key not in response.')
        except:
            self.dataverse_version = 'ERROR'
            # TODO: raise exception
            print('Dataverse build version can not be retrieved.')

    def __str__(self):
        """Return name of Api() class for users.

        Returns
        -------
        string
            Naming of the Api() class.

        """
        return 'pyDataverse API class'

    def get_request(self, path, params=None, auth=False):
        """Make a GET request.

        Parameters
        ----------
        path : string
            Query string for the request. Will be concatenated to
            `native_api_base_url`.
        params : dict
            Dictionary of parameters to be passed with the request.
            Defaults to `None`.
        auth : bool
            Should an api token be sent in the request. Defaults to `False`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        url = '{0}{1}'.format(self.native_api_base_url, path)
        if auth:
            if self.api_token:
                if not params:
                    params = {}
                params['key'] = self.api_token
            else:
                ApiAuthorizationError(
                    'ERROR: GET - Api token not passed to '
                    '`get_request` {}.'.format(url)
                )

        try:
            resp = get(
                url,
                params=params
            )
            if resp:
                if resp.status_code == 401:
                    error_msg = resp.json()['message']
                    raise ApiAuthorizationError(
                        'ERROR: GET - Authorization invalid {0}. MSG: {1}.'
                        ''.format(url, error_msg)
                    )
                elif resp.status_code >= 300:
                    error_msg = resp.json()['message']
                    raise OperationFailedError(
                        'ERROR: GET HTTP {0} - {1}. MSG: {2}'.format(
                            resp.status_code, url, error_msg)
                    )
            return resp
        except ConnectionError:
            raise ConnectionError(
                'ERROR: GET - Could not establish connection to api {}.'
                ''.format(url)
            )

    def post_request(self, path, metadata=None, auth=False,
                     params=None):
        """Make a POST request.

        Parameters
        ----------
        path : string
            Query string for the request. Will be concatenated to
            `native_api_base_url`.
        metadata : string
            Metadata as a json-formatted string. Defaults to `None`.
        auth : bool
            Should an api token be sent in the request. Defaults to `False`.
        params : dict
            Dictionary of parameters to be passed with the request.
            Defaults to `None`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        url = '{0}{1}'.format(self.native_api_base_url, path)
        if auth:
            if self.api_token:
                if not params:
                    params = {}
                params['key'] = self.api_token
            else:
                ApiAuthorizationError(
                    'ERROR: POST - Api token not passed to '
                    '`post_request` {}.'.format(url)
                )

        try:
            resp = post(
                url,
                data=metadata,
                params=params
            )
            if resp.status_code == 401:
                error_msg = resp.json()['message']
                raise ApiAuthorizationError(
                    'ERROR: POST HTTP 401 - Authorization error {0}. MSG: {1}'
                    ''.format(url, error_msg)
                )
            return resp
        except ConnectionError:
            raise ConnectionError(
                'ERROR: POST - Could not establish connection to API: {}'
                ''.format(url)
            )

    def put_request(self, path, metadata=None, auth=False,
                    params=None):
        """Make a PUT request.

        Parameters
        ----------
        path : string
            Query string for the request. Will be concatenated to
            `native_api_base_url`.
        metadata : string
            Metadata as a json-formatted string. Defaults to `None`.
        auth : bool
            Should an api token be sent in the request. Defaults to `False`.
        params : dict
            Dictionary of parameters to be passed with the request.
            Defaults to `None`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        url = '{0}{1}'.format(self.native_api_base_url, path)
        if auth:
            if self.api_token:
                if not params:
                    params = {}
                params['key'] = self.api_token
            else:
                ApiAuthorizationError(
                    'ERROR: PUT - Api token not passed to '
                    '`put_request` {}.'.format(url)
                )

        try:
            resp = put(
                url,
                data=metadata,
                params=params
            )
            if resp.status_code == 401:
                error_msg = resp.json()['message']
                raise ApiAuthorizationError(
                    'ERROR: PUT HTTP 401 - Authorization error {0}. MSG: {1}'
                    ''.format(url, error_msg)
                )
            return resp
        except ConnectionError:
            raise ConnectionError(
                'ERROR: PUT - Could not establish connection to api {}.'
                ''.format(url)
            )

    def delete_request(self, path, auth=False, params=None):
        """Make a DELETE request.

        Parameters
        ----------
        path : string
            Query string for the request. Will be concatenated to
            `native_api_base_url`.
        auth : bool
            Should an api token be sent in the request. Defaults to `False`.
        params : dict
            Dictionary of parameters to be passed with the request.
            Defaults to `None`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        url = '{0}{1}'.format(self.native_api_base_url, path)
        if auth:
            if self.api_token:
                if not params:
                    params = {}
                params['key'] = self.api_token
            else:
                ApiAuthorizationError(
                    'ERROR: DELETE - Api token not passed to '
                    '`delete_request` {}.'.format(url)
                )

        try:
            resp = delete(
                url,
                params=params
            )
            return resp
        except ConnectionError:
            raise ConnectionError(
                'ERROR: DELETE could not establish connection to api {}.'
                ''.format(url)
            )

    def get_dataverse(self, identifier, auth=False):
        """Get dataverse metadata by alias or id.

        View metadata about a dataverse.

        .. code-block:: bash

            GET http://$SERVER/api/dataverses/$id

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long), a dataverse alias (more
            robust), or the special value ``:root``.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/dataverses/{0}'.format(identifier)
        resp = self.get_request(path, auth=auth)
        return resp

    def create_dataverse(self, identifier, metadata, auth=True,
                         parent=':root'):
        """Create a dataverse.

        Generates a new dataverse under identifier. Expects a JSON content
        describing the dataverse.

        HTTP Request:

        .. code-block:: bash

            POST http://$SERVER/api/dataverses/$id

        Download the `dataverse.json <http://guides.dataverse.org/en/latest/
        _downloads/dataverse-complete.json>`_ example file and modify to create
        dataverses to suit your needs. The fields name, alias, and
        dataverseContacts are required.

        Status Codes:
            200: dataverse created
            201: dataverse created

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long) or a dataverse alias (more
            robust). If identifier is omitted, a root dataverse is created.
        metadata : string
            Metadata of the Dataverse as a json-formatted string.
        auth : bool
            True if api authorization is necessary. Defaults to ``True``.
        parent : string
            Parent dataverse, if existing, to which the Dataverse gets attached
            to. Defaults to ``:root``.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        if not parent:
            raise DataverseNotFoundError(
                'Dataverse {} not found. No parent dataverse passed to '
                '`create_dataverse()`.'.format(identifier)
            )

        path = '/dataverses/{0}'.format(parent)
        resp = self.post_request(path, metadata, auth)

        if resp.status_code == 404:
            error_msg = resp.json()['message']
            raise DataverseNotFoundError(
                'ERROR: HTTP 404 - Dataverse {0} was not found. MSG: '.format(
                    parent, error_msg))
        elif resp.status_code != 200 and resp.status_code != 201:
            error_msg = resp.json()['message']
            raise OperationFailedError(
                'ERROR: HTTP {0} - Dataverse {1} could not be created. '
                'MSG: {2}'.format(resp.status_code, identifier, error_msg)
            )
        else:
            print('Dataverse {0} created.'.format(identifier))
        return resp

    def publish_dataverse(self, identifier, auth=True):
        """Publish a dataverse.

        Publish the Dataverse pointed by identifier, which can either by the
        dataverse alias or its numerical id.

        HTTP Request:

        .. code-block:: bash

            POST http://$SERVER/api/dataverses/$identifier/actions/:publish

        Status Code:
            200: Dataverse published

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long) or a dataverse alias (more
            robust).
        auth : bool
            True if api authorization is necessary. Defaults to ``False``.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/dataverses/{0}/actions/:publish'.format(identifier)
        resp = self.post_request(path, auth=auth)

        if resp.status_code == 401:
            error_msg = resp.json()['message']
            raise ApiAuthorizationError(
                'ERROR: HTTP 401 - Publish Dataverse {0} unauthorized. '
                'MSG: {1}'.format(identifier, error_msg)
            )
        elif resp.status_code == 404:
            error_msg = resp.json()['message']
            raise DataverseNotFoundError(
                'ERROR: HTTP 404 - Dataverse {} was not found. MSG: {1}'
                ''.format(
                    identifier, error_msg)
            )
        elif resp.status_code != 200:
            error_msg = resp.json()['message']
            raise OperationFailedError(
                'ERROR: HTTP {0} - Dataverse {1} could not be published. MSG: '
                '{2}'.format(resp.status_code, identifier, error_msg)
            )
        elif resp.status_code == 200:
            print('Dataverse {} published.'.format(identifier))
        return resp

    def delete_dataverse(self, identifier, auth=True):
        """Delete dataverse by alias or id.

        HTTP Request:

        .. code-block:: bash

            DELETE http://$SERVER/api/dataverses/$id

        Status Code:
            200: Dataverse deleted

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long) or a dataverse alias (more
            robust).

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/dataverses/{0}'.format(identifier)
        resp = self.delete_request(path, auth)

        if resp.status_code == 401:
            error_msg = resp.json()['message']
            raise ApiAuthorizationError(
                'ERROR: HTTP 401 - Delete Dataverse {0} unauthorized. '
                'MSG: {1}'.format(identifier, error_msg)
            )
        elif resp.status_code == 404:
            error_msg = resp.json()['message']
            raise DataverseNotFoundError(
                'ERROR: HTTP 404 - Dataverse {0} was not found. MSG: {1}'
                ''.format(identifier, error_msg)
            )
        elif resp.status_code == 403:
            error_msg = resp.json()['message']
            raise DataverseNotEmptyError(
                'ERROR: HTTP 403 - Dataverse {0} not empty. MSG: {1}'.format(
                    identifier, error_msg)
            )
        elif resp.status_code != 200:
            error_msg = resp.json()['message']
            raise OperationFailedError(
                'ERROR: HTTP {0} - Dataverse {1} could not be deleted. MSG: '
                '{2}'.format(resp.status_code, identifier, error_msg)
            )
        elif resp.status_code == 200:
            print('Dataverse {} deleted.'.format(identifier))
        return resp

    def get_dataverse_roles(self, identifier, auth=False):
        """Get dataverse roles by alias or id.

        View roles of a dataverse.

        .. code-block:: bash

            GET http://$SERVER/api/dataverses/$id/roles

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long), a dataverse alias (more
            robust), or the special value ``:root``.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/dataverses/{0}/roles'.format(identifier)
        resp = self.get_request(path, auth=auth)
        return resp


    def get_dataverse_contents(self, identifier, auth=False):
        """Gets contents of Dataverse.

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long), a dataverse alias (more
            robust), or the special value ``:root``.
        auth : bool
            Description of parameter `auth` (the default is False).

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/dataverses/{0}/contents'.format(identifier)
        resp = self.get_request(path, auth=auth)
        return resp


    def get_dataverse_assignments(self, identifier, auth=False):
        """Get dataverse assignments by alias or id.

        View assignments of a dataverse.

        .. code-block:: bash

            GET http://$SERVER/api/dataverses/$id/assignments

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long), a dataverse alias (more
            robust), or the special value ``:root``.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/dataverses/{0}/assignments'.format(identifier)
        resp = self.get_request(path, auth=auth)
        return resp

    def get_dataverse_facets(self, identifier, auth=False):
        """Get dataverse facets by alias or id.

        View facets of a dataverse.

        .. code-block:: bash

            GET http://$SERVER/api/dataverses/$id/facets

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long), a dataverse alias (more
            robust), or the special value ``:root``.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/dataverses/{0}/facets'.format(identifier)
        resp = self.get_request(path, auth=auth)
        return resp

    def get_dataset(self, identifier, version=':latest', auth=True, is_pid=True):
        """Get metadata of a Dataset.

        With Dataverse identifier:

        .. code-block:: bash

            GET http://$SERVER/api/datasets/$identifier

        With persistent identifier:

        .. code-block:: bash

            GET http://$SERVER/api/datasets/:persistentId/?persistentId=$id
            GET http://$SERVER/api/datasets/:persistentId/
            ?persistentId=$pid

        Parameters
        ----------
        identifier : string
            Identifier of the dataset. Can be a Dataverse identifier or a
            persistent identifier (e.g. ``doi:10.11587/8H3N93``).
        is_pid : bool
            True, if identifier is a persistent identifier.
        version : string
            Version to be retrieved:
            ``:latest-published``: the latest published version
            ``:latest``: either a draft (if exists) or the latest published version.
            ``:draft``: the draft version, if any
            ``x.y``: x.y a specific version, where x is the major version number and y is the minor version number.
            ``x``: same as x.0

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        if is_pid:
            path = '/datasets/:persistentId/{0}?persistentId={1}'.format(
                version, identifier)
        else:
            path = '/datasets/{0}'.format(identifier)
            # CHECK: Its not really clear, if the version query can also be done via ID.
        resp = self.get_request(path, auth=auth)
        return resp

    def get_dataset_versions(self, identifier, auth=True, is_pid=True):
        """Get versions of a Dataset.

        With Dataverse identifier:

        .. code-block:: bash

            GET http://$SERVER/api/datasets/$identifier/versions

        With persistent identifier:

        .. code-block:: bash

            GET http://$SERVER/api/datasets/:persistentId/versions?persistentId=$id

        Parameters
        ----------
        identifier : string
            Identifier of the dataset. Can be a Dataverse identifier or a
            persistent identifier (e.g. ``doi:10.11587/8H3N93``).
        is_pid : bool
            True, if identifier is a persistent identifier.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        if is_pid:
            path = '/datasets/:persistentId/versions?persistentId={0}'.format(
                identifier)
        else:
            path = '/datasets/{0}/versions'.format(identifier)
        resp = self.get_request(path, auth=auth)
        return resp

    def get_dataset_version(self, identifier, version, auth=True, is_pid=True):
        """Get version of a Dataset.

        With Dataverse identifier:

        .. code-block:: bash

            GET http://$SERVER/api/datasets/$identifier/versions/$versionNumber

        With persistent identifier:

        .. code-block:: bash

            GET http://$SERVER/api/datasets/:persistentId/versions/$versionNumber?persistentId=$id

        Parameters
        ----------
        identifier : string
            Identifier of the dataset. Can be a Dataverse identifier or a
            persistent identifier (e.g. ``doi:10.11587/8H3N93``).
        version : string
            Version string of the Dataset.
        is_pid : bool
            True, if identifier is a persistent identifier.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        if is_pid:
            path = '/datasets/:persistentId/versions/{0}?persistentId={1}'.format(
                version, identifier)
        else:
            path = '/datasets/{0}/versions/{1}'.format(identifier, version)
        resp = self.get_request(path, auth=auth)
        return resp

    def get_dataset_export(self, pid, export_format, auth=False):
        """Get metadata of dataset exported in different formats.

        Export the metadata of the current published version of a dataset
        in various formats by its persistend identifier.

        .. code-block:: bash

            GET http://$SERVER/api/datasets/export?exporter=$exportformat&persistentId=$pid

        Parameters
        ----------
        pid : string
            Persistent identifier of the dataset. (e.g. ``doi:10.11587/8H3N93``).
        export_format : string
            Export format as a string. Formats: ``ddi``, ``oai_ddi``,
            ``dcterms``, ``oai_dc``, ``schema.org``, ``dataverse_json``.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/datasets/export?exporter={0}&persistentId={1}'.format(
            export_format, pid)
        resp = self.get_request(path, auth=auth)
        return resp

    def create_dataset(self, dataverse, metadata, auth=True):
        """Add dataset to a dataverse.

        `Dataverse Documentation
        <http://guides.dataverse.org/en/latest/api/native-api.html#create-a-dataset-in-a-dataverse>`_

        HTTP Request:

        .. code-block:: bash

            POST http://$SERVER/api/dataverses/$dataverse/datasets --upload-file FILENAME

        Add new dataset with curl:

        .. code-block:: bash

            curl -H "X-Dataverse-key: $API_TOKEN" -X POST $SERVER_URL/api/dataverses/$DV_ALIAS/datasets --upload-file tests/data/dataset_min.json

        Import dataset with existing persistend identifier with curl:

        .. code-block:: bash

            curl -H "X-Dataverse-key: $API_TOKEN" -X POST $SERVER_URL/api/dataverses/$DV_ALIAS/datasets/:import?pid=$PERSISTENT_IDENTIFIER&release=yes --upload-file tests/data/dataset_min.json

        To create a dataset, you must create a JSON file containing all the
        metadata you want such as example file: `dataset-finch1.json
        <http://guides.dataverse.org/en/latest/_downloads/dataset-finch1.json>`_.
        Then, you must decide which dataverse to create the dataset in and
        target that datavese with either the "alias" of the dataverse (e.g.
        "root" or the database id of the dataverse (e.g. "1"). The initial
        version state will be set to DRAFT:

        Status Code:
            201: dataset created

        Parameters
        ----------
        dataverse : string
            "alias" of the dataverse (e.g. ``root``) or the database id of the
            dataverse (e.g. ``1``)
        metadata : string
            Metadata of the Dataset as a json-formatted string (e. g.
            `dataset-finch1.json <http://guides.dataverse.org/en/latest/_downloads/dataset-finch1.json>`_)

        Returns
        -------
        requests.Response
            Response object of requests library.

        Todo
        -------
        Link Dataset finch1.json

        """
        path = '/dataverses/{0}/datasets'.format(dataverse)
        resp = self.post_request(path, metadata, auth)

        if resp.status_code == 404:
            error_msg = resp.json()['message']
            raise DataverseNotFoundError(
                'ERROR: HTTP 404 - Dataverse {0} was not found. MSG: {1}'
                ''.format(dataverse, error_msg))
        elif resp.status_code == 401:
            error_msg = resp.json()['message']
            raise ApiAuthorizationError(
                'ERROR: HTTP 401 - Create Dataset unauthorized. MSG: '
                ''.format(error_msg)
            )
        elif resp.status_code == 201:
            if 'data' in resp.json():
                if 'persistentId' in resp.json()['data']:
                    identifier = resp.json()['data']['persistentId']
                    print('Dataset with pid \'{}\' created.'.format(identifier))
                elif 'id' in resp.json()['data']:
                    identifier = resp.json()['data']['id']
                    print('Dataset with id \'{}\' created.'.format(identifier))
                else:
                    print('ERROR: No identifier returned for created Dataset.')
        return resp

    def create_dataset_private_url(self, identifier, is_pid=True, auth=True):
        """Create private Dataset URL.

        POST http://$SERVER/api/datasets/$id/privateUrl?key=$apiKey


        http://guides.dataverse.org/en/4.16/api/native-api.html#create-a-private-url-for-a-dataset
                'MSG: {1}'.format(pid, error_msg))

        """
        if is_pid:
            path = '/datasets/:persistentId/privateUrl/?persistentId={0}'.format(identifier)
        else:
            path = '/datasets/{0}/privateUrl'.format(identifier)

        resp = self.post_request(path, auth=auth)

        if resp.status_code == 200:
            print('Dataset private URL created: {0}'.format(resp.json()['data']['link']))
        return resp

    def get_dataset_private_url(self, identifier, is_pid=True, auth=True):
        """Get private Dataset URL.

        GET http://$SERVER/api/datasets/$id/privateUrl?key=$apiKey

        http://guides.dataverse.org/en/4.16/api/native-api.html#get-the-private-url-for-a-dataset

        """
        if is_pid:
            path = '/datasets/:persistentId/privateUrl/?persistentId={0}'.format(identifier)
        else:
            path = '/datasets/{0}/privateUrl'.format(identifier)

        resp = self.get_request(path, auth=auth)

        if resp.status_code == 200:
            print('Got Dataset private URL: {0}'.format(resp.json()['data']['link']))
        return resp

    def delete_dataset_private_url(self, identifier, is_pid=True, auth=True):
        """Get private Dataset URL.

        DELETE http://$SERVER/api/datasets/$id/privateUrl?key=$apiKey

        http://guides.dataverse.org/en/4.16/api/native-api.html#delete-the-private-url-from-a-dataset

        """
        if is_pid:
            path = '/datasets/:persistentId/privateUrl/?persistentId={0}'.format(identifier)
        else:
            path = '/datasets/{0}/privateUrl'.format(identifier)

        resp = self.delete_request(path, auth=auth)

        if resp.status_code == 200:
            print('Got Dataset private URL: {0}'.format(resp.json()['data']['link']))
        return resp

    def publish_dataset(self, pid, type='minor', auth=True):
        """Publish dataset.

        Publishes the dataset whose id is passed. If this is the first version
        of the dataset, its version number will be set to 1.0. Otherwise, the
        new dataset version number is determined by the most recent version
        number and the type parameter. Passing type=minor increases the minor
        version number (2.3 is updated to 2.4). Passing type=major increases
        the major version number (2.3 is updated to 3.0). Superusers can pass
        type=updatecurrent to update metadata without changing the version
        number.

        HTTP Request:

        .. code-block:: bash

            POST http://$SERVER/api/datasets/$id/actions/:publish?type=$type

        When there are no default workflows, a successful publication process
        will result in 200 OK response. When there are workflows, it is
        impossible for Dataverse to know how long they are going to take and
        whether they will succeed or not (recall that some stages might require
        human intervention). Thus, a 202 ACCEPTED is returned immediately. To
        know whether the publication process succeeded or not, the client code
        has to check the status of the dataset periodically, or perform some
        push request in the post-publish workflow.

        Status Code:
            200: dataset published

        Parameters
        ----------
        pid : string
            Persistent identifier of the dataset (e.g.
            ``doi:10.11587/8H3N93``).
        type : string
            Passing ``minor`` increases the minor version number (2.3 is
            updated to 2.4). Passing ``major`` increases the major version
            number (2.3 is updated to 3.0). Superusers can pass
            ``updatecurrent`` to update metadata without changing the version
            number.
        auth : bool
            ``True`` if api authorization is necessary. Defaults to ``False``.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/datasets/:persistentId/actions/:publish'
        path += '?persistentId={0}&type={1}'.format(pid, type)
        resp = self.post_request(path, auth=auth)

        if resp.status_code == 404:
            error_msg = resp.json()['message']
            raise DatasetNotFoundError(
                'ERROR: HTTP 404 - Dataset {0} was not found. MSG: {1}'
                ''.format(pid, error_msg))
        elif resp.status_code == 401:
            error_msg = resp.json()['message']
            raise ApiAuthorizationError(
                'ERROR: HTTP 401 - User not allowed to publish dataset {0}. '
                'MSG: {1}'.format(pid, error_msg))
        elif resp.status_code == 200:
            print('Dataset {} published'.format(pid))
        return resp

    def get_dataset_lock(self, pid):
        """Get if dataset is locked.

        The lock API endpoint was introduced in Dataverse 4.9.3.

        Parameters
        ----------
        pid : string
            Persistent identifier of the dataset (e.g.
            ``doi:10.11587/8H3N93``).

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/datasets/:persistentId/locks/?persistentId={0}'.format(pid)
        resp = self.get_request(path, auth=True)
        return resp

    def get_dataset_assignments(self, identifier, is_pid=True, auth=True):
        """Get Dataset assignments.

        GET http://$SERVER/api/datasets/$id/assignments?key=$apiKey


        """
        if is_pid:
            path = '/datasets/:persistentId/assignments/?persistentId={0}'.format(identifier)
        else:
            path = '/datasets/{0}/assignments'.format(identifier)

        resp = self.get_request(path, auth=auth)
        return resp

    def delete_dataset(self, identifier, is_pid=True, auth=True):
        """Delete a dataset.

        Delete the dataset whose id is passed

        HTTP Request:

        .. code-block:: bash

            DELETE http://$SERVER/api/datasets/$id

        Status Code:
            200: dataset deleted

        Parameters
        ----------
        identifier : string
            Identifier of the dataset. Can be a Dataverse identifier or a
            persistent identifier (e.g. ``doi:10.11587/8H3N93``).
        is_pid : bool
            True, if identifier is a persistent identifier.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        if is_pid:
            path = '/datasets/:persistentId/?persistentId={0}'.format(
                identifier)
        else:
            path = '/datasets/{0}'.format(identifier)
        resp = self.delete_request(path, auth=auth)

        if resp.status_code == 404:
            error_msg = resp.json()['message']
            raise DatasetNotFoundError(
                'ERROR: HTTP 404 - Dataset \'{0}\' was not found. MSG: {1}'
                ''.format(identifier, error_msg))
        elif resp.status_code == 405:
            error_msg = resp.json()['message']
            raise OperationFailedError(
                'ERROR: HTTP 405 - '
                'Published datasets can only be deleted from the GUI. For '
                'more information, please refer to '
                'https://github.com/IQSS/dataverse/issues/778'
                ' MSG: {}'.format(error_msg)
            )
        elif resp.status_code == 401:
            error_msg = resp.json()['message']
            raise ApiAuthorizationError(
                'ERROR: HTTP 401 - User not allowed to delete dataset \'{0}\'. '
                'MSG: {1}'.format(identifier, error_msg))
        elif resp.status_code == 200:
            print('Dataset \'{}\' deleted.'.format(identifier))
        return resp

    def destroy_dataset(self, identifier, is_pid=True, auth=True):
        """Destroy Dataset.

        http://guides.dataverse.org/en/4.16/api/native-api.html#delete-published-dataset

        Normally published datasets should not be deleted, but there exists a
        “destroy” API endpoint for superusers which will act on a dataset given
        a persistent ID or dataset database ID:

        curl -H "X-Dataverse-key:$API_TOKEN" -X DELETE http://$SERVER/api/datasets/:persistentId/destroy/?persistentId=doi:10.5072/FK2/AAA000

        curl -H "X-Dataverse-key:$API_TOKEN" -X DELETE http://$SERVER/api/datasets/999/destroy

        Calling the destroy endpoint is permanent and irreversible. It will
        remove the dataset and its datafiles, then re-index the parent
        dataverse in Solr. This endpoint requires the API token of a
        superuser.
        """
        if is_pid:
            path = '/datasets/:persistentId/destroy/?persistentId={0}'.format(identifier)
        else:
            path = '/datasets/{0}/destroy'.format(identifier)

        resp = self.delete_request(path, auth=auth)

        if resp.status_code == 200:
            print('Dataset {0} destroyed'.format(resp.json()))
        return resp

    def edit_dataset_metadata(self, identifier, metadata, is_pid=True,
                              is_replace=False, auth=True):
        """Edit metadata of a given dataset.

        `Offical documentation
        <http://guides.dataverse.org/en/latest/api/native-api.html#
        edit-dataset-metadata>`_.

        HTTP Request:

        .. code-block:: bash

            PUT http://$SERVER/api/datasets/editMetadata/$id --upload-file FILENAME

        Add data to dataset fields that are blank or accept multiple values with
        the following

        CURL Request:

        .. code-block:: bash

            curl -H "X-Dataverse-key: $API_TOKEN" -X PUT $SERVER_URL/api/datasets/:persistentId/editMetadata/?persistentId=$pid --upload-file dataset-add-metadata.json

        For these edits your JSON file need only include those dataset fields
        which you would like to edit. A sample JSON file may be downloaded
        here: `dataset-edit-metadata-sample.json
        <http://guides.dataverse.org/en/latest/_downloads/dataset-finch1.json>`_

        Parameters
        ----------
        identifier : string
            Identifier of the dataset. Can be a Dataverse identifier or a
            persistent identifier (e.g. ``doi:10.11587/8H3N93``).
        metadata : string
            Metadata of the Dataset as a json-formatted string.
        is_pid : bool
            ``True`` to use persistent identifier. ``False``, if not.
        is_replace : bool
            ``True`` to replace already existing metadata. ``False``, if not.
        auth : bool
            ``True``, if an api token should be sent. Defaults to ``False``.

        Returns
        -------
        requests.Response
            Response object of requests library.

        Examples
        -------
        Get dataset metadata::

            >>> data = api.get_dataset_metadata(doi, auth=True)
            >>> resp = api.edit_dataset_metadata(doi, data, is_replace=True, auth=True)
            >>> resp.status_code
            200: metadata updated

        """
        if is_pid:
            path = '/datasets/:persistentId/editMetadata/?persistentId={0}'
            ''.format(identifier)
        else:
            path = '/datasets/editMetadata/{0}'.format(identifier)
        params = {'replace': True} if is_replace else {}

        resp = self.put_request(path, metadata, auth, params)

        if resp.status_code == 401:
            error_msg = resp.json()['message']
            raise ApiAuthorizationError(
                'ERROR: HTTP 401 - Updating metadata unauthorized. MSG: '
                ''.format(error_msg)
            )
        elif resp.status_code == 400:
            if 'Error parsing' in resp.json()['message']:
                print('Wrong passed data format.')
            else:
                print('You may not add data to a field that already has data ' +
                      'and does not allow multiples. ' +
                      'Use is_replace=true to replace existing data.')
        elif resp.status_code == 200:
            print('Dataset {0} updated'.format(identifier))
        return resp

    def upload_datafile(self, identifier, filename, json_str=None, is_pid=True):
        """Add file to a dataset.

        Add a file to an existing Dataset. Description and tags are optional:

        HTTP Request:

        .. code-block:: bash

            POST http://$SERVER/api/datasets/$id/add

        The upload endpoint checks the content of the file, compares it with
        existing files and tells if already in the database (most likely via
        hashing).

        `Offical documentation
        <http://guides.dataverse.org/en/latest/api/native-api.html#adding-files>`_.

        Parameters
        ----------
        identifier : string
            Identifier of the dataset.
        filename : string
            Full filename with path.
        json_str : string
            Metadata as JSON string.
        is_pid : bool
            ``True`` to use persistent identifier. ``False``, if not.

        Returns
        -------
        dict
            The json string responded by the CURL request, converted to a
            dict().

        """
        path = self.native_api_base_url
        if is_pid:
            path += '/datasets/:persistentId/add?persistentId={0}'.format(
                identifier)
        else:
            path += '/datasets/{0}/add'.format(identifier)
        shell_command = 'curl -H "X-Dataverse-key: {0}"'.format(
            self.api_token)
        shell_command += ' -X POST {0} -F file=@{1}'.format(
            path, filename)
        if json_str:
            shell_command += " -F 'jsonData={0}'".format(json_str)
        # TODO(Shell): is shell=True necessary?
        result = sp.run(shell_command, shell=True, stdout=sp.PIPE)
        resp = json.loads(result.stdout)
        return resp

    def get_datafiles(self, pid, version='1', auth=False):
        """List metadata of all datafiles of a dataset.

        `Documentation <http://guides.dataverse.org/en/latest/api/native-api.html#list-files-in-a-dataset>`_

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/datasets/$id/versions/$versionId/files

        Parameters
        ----------
        pid : string
            Persistent identifier of the dataset. e.g. ``doi:10.11587/8H3N93``.
        version : string
            Version of dataset. Defaults to `1`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        base_str = '/datasets/:persistentId/versions/'
        path = base_str + '{0}/files?persistentId={1}'.format(
            version, pid)
        resp = self.get_request(path, auth=auth)
        return resp

    def get_datafile(self, identifier, is_pid=True, auth=False):
        """Download a datafile via the Dataverse Data Access API.

        Get by file id (HTTP Request).

        .. code-block:: bash

            GET /api/access/datafile/$id

        Get by persistent identifier (HTTP Request).

        .. code-block:: bash

            GET http://$SERVER/api/access/datafile/:persistentId/?persistentId=doi:10.5072/FK2/J8SJZB

        Parameters
        ----------
        identifier : string
            Identifier of the dataset. Can be datafile id or persistent
            identifier of the datafile (e. g. doi).
        is_pid : bool
            ``True`` to use persistent identifier. ``False``, if not.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        if is_pid:
            path = '/access/datafile/{0}'.format(identifier)
        else:
            path = '/access/datafile/:persistentId/?persistentId={0}'
            ''.format(identifier)
        resp = self.get_request(path, auth=auth)
        return resp

    def get_datafile_bundle(self, identifier, auth=False):
        """Download a datafile in all its formats.

        HTTP Request:

        .. code-block:: bash

            GET /api/access/datafile/bundle/$id

        Data Access API calls can now be made using persistent identifiers (in
        addition to database ids). This is done by passing the constant
        :persistentId where the numeric id of the file is expected, and then
        passing the actual persistent id as a query parameter with the name
        persistentId.

        This is a convenience packaging method available for tabular data
        files. It returns a zipped bundle that contains the data in the
        following formats:
        - Tab-delimited;
        - “Saved Original”, the proprietary (SPSS, Stata, R, etc.) file
        from which the tabular data was ingested;
        - Generated R Data frame (unless the “original” above was in R);
        - Data (Variable) metadata record, in DDI XML;
        - File citation, in Endnote and RIS formats.

        Parameters
        ----------
        identifier : string
            Identifier of the dataset.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/access/datafile/bundle/{0}'.format(identifier)
        data = self.get_request(path, auth=auth)
        return data

    def update_datafile_metadata(self, datafile_id, json_str, auth=True):
        """Update Datafile metadata.

        Updates the file metadata for an existing file where id is the database
        id of the file to replace or pid is the persistent id (DOI or Handle)
        of the file. Requires a jsonString expressing the new metadata. No
        metadata from the previous version of this file will be persisted, so
        if you want to update a specific field first get the json with the
        above command and alter the fields you want:

        POST -F 'jsonData={json}' http://$SERVER/api/files/{id}/metadata?key={apiKey}

        Also note that dataFileTags are not versioned and changes to these
        will update the published version of the file.

        """
        path = '/files/{}/metadata'.format(datafile_id)

        resp = self.post_request(path, auth=auth)

        shell_command = 'curl -H "X-Dataverse-key: {0}"'.format(
            self.api_token)
        shell_command += " -X POST {0} -F 'jsonData={0}'".format(json_str)
        # TODO(Shell): is shell=True necessary?
        result = sp.run(shell_command, shell=True, stdout=sp.PIPE)
        resp = json.loads(result.stdout)
        return resp

    def get_info_version(self, auth=False):
        """Get the Dataverse version and build number.

        The response contains the version and build numbers. Requires no api
        token.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/info/version

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/info/version'
        resp = self.get_request(path, auth=auth)
        return resp

    def get_info_server(self, auth=False):
        """Get dataverse server name.

        This is useful when a Dataverse system is composed of multiple Java EE
        servers behind a load balancer.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/info/server

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/info/server'
        resp = self.get_request(path, auth=auth)
        return resp

    def get_info_apiTermsOfUse(self, auth=False):
        """Get API Terms of Use url.

        The response contains the text value inserted as API Terms of use which
        uses the database setting :ApiTermsOfUse.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/info/apiTermsOfUse

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/info/apiTermsOfUse'
        resp = self.get_request(path, auth=auth)
        return resp

    def get_metadatablocks(self, auth=False):
        """Get info about all metadata blocks.

        Lists brief info about all metadata blocks registered in the system.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/metadatablocks

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/metadatablocks'
        resp = self.get_request(path, auth=auth)
        return resp

    def get_metadatablock(self, identifier, auth=False):
        """Get info about single metadata block.

        Returns data about the block whose identifier is passed. identifier can
        either be the block’s id, or its name.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/metadatablocks/$identifier

        Parameters
        ----------
        identifier : string
            Can be block's id, or it's name.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/metadatablocks/{0}'.format(identifier)
        resp = self.get_request(path, auth=auth)
        return resp

    def get_user_apitoken_expirationdate(self, auth=False):
        """Get the expiration date of an Users's API token.

        HTTP Request:

        .. code-block:: bash

            curl -H X-Dataverse-key:$API_TOKEN -X GET $SERVER_URL/api/users/token

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/users/token'
        resp = self.get_request(path, auth=auth)
        return resp

    def recreate_user_apitoken(self):
        """Recreate an Users API token.

        HTTP Request:

        .. code-block:: bash

            curl -H X-Dataverse-key:$API_TOKEN -X POST $SERVER_URL/api/users/token/recreate

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/users/token/recreate'
        resp = self.post_request(path)
        return resp

    def delete_user_apitoken(self):
        """Delete an Users API token.

        HTTP Request:

        .. code-block:: bash

            curl -H X-Dataverse-key:$API_TOKEN -X POST $SERVER_URL/api/users/token/recreate

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/users/token'
        resp = self.delete_request(path)
        return resp

    def create_dataverse_role(self, dataverse_id):
        """Create a new role in a Dataverse.

        HTTP Request:

        .. code-block:: bash

            POST http://$SERVER/api/roles?dvo=$dataverseIdtf&key=$apiKey

        Parameters
        ----------
        dataverse_id : string
            Can be alias or id of a Dataverse.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/roles?dvo={0}'.format(dataverse_id)
        resp = self.post_request(path)
        return resp

    def get_dataverse_role(self, role_id, auth=False):
        """Get role of a Dataverse.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/roles/$id

        Parameters
        ----------
        identifier : string
            Can be alias or id of a Dataverse.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/roles/{0}'.format(role_id)
        resp = self.get_request(path, auth=auth)
        return resp

    def delete_dataverse_role(self, role_id):
        """Delete role of a Dataverse.

        HTTP Request:

        .. code-block:: bash

            DELETE http://$SERVER/api/roles/$id

        Parameters
        ----------
        identifier : string
            Can be alias or id of a Dataverse.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        path = '/roles/{0}'.format(role_id)
        resp = self.delete_request(path)
        return resp

    def walker(self, dv_lst=None, ds_lst=None, dataverse=':root'):
        """Walks through all child dataverses and collects the dataverses
        and datasets.

        CORS Lists all the dataverses and datasets directly under
        a dataverse (direct children only). You must specify the
        “alias” of a dataverse or its database id. If you specify
        your API token and have access, unpublished dataverses
        and datasets will be included in the listing.

        curl -H X-Dataverse-key:$API_TOKEN $SERVER_URL/api/dataverses/$ALIAS/contents

        Parameters
        ----------
        dv_lst : type
            Description of parameter `dv_lst`.
        ds_lst : type
            Description of parameter `ds_lst`.
        dataverse : type
            Description of parameter `dataverse` (the default is ':root').

        Returns
        -------
        type
            Description of returned object.
        """
        if dv_lst is None:
            dv_lst = []
        if ds_lst is None:
            ds_lst = []
        resp = self.get_dataverse_contents(dataverse)
        if 'data' in resp.json():
            content = resp.json()['data']
            for c in content:
                if c['type'] == 'dataset':
                    ds_lst.append(c['identifier'])
                elif c['type'] == 'dataverse':
                    dv_lst.append(c['id'])
                    dv_lst, ds_lst = self.walker(dv_lst, ds_lst, c['id'])
        else:
            print('Walker: API request not working.')
        return dv_lst, ds_lst
