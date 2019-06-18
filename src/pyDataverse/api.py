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
    """API class.

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
        self.conn_started = datetime.now()

        # Test connection.
        query_str = '/info/server'
        if base_url and api_version:
            self.native_api_base_url = '{0}/api/{1}'.format(self.base_url,
                                                            self.api_version)
            url = '{0}{1}'.format(self.native_api_base_url, query_str)
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

    def __str__(self):
        """Return name of Api() class for users.

        Returns
        -------
        string
            Naming of the Api() class.

        """
        return 'pyDataverse API class'

    def get_request(self, query_str, params=None, auth=False):
        """Make a GET request.

        Parameters
        ----------
        query_str : string
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
        url = '{0}{1}'.format(self.native_api_base_url, query_str)
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

    def post_request(self, query_str, metadata=None, auth=False,
                     params=None):
        """Make a POST request.

        Parameters
        ----------
        query_str : string
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
        url = '{0}{1}'.format(self.native_api_base_url, query_str)
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
                'ERROR: POST - Could not establish connection to api {}.'
                ''.format(url)
            )

    def put_request(self, query_str, metadata=None, auth=False,
                    params=None):
        """Make a PUT request.

        Parameters
        ----------
        query_str : string
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
        url = '{0}{1}'.format(self.native_api_base_url, query_str)
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

    def delete_request(self, query_str, auth=False, params=None):
        """Make a DELETE request.

        Parameters
        ----------
        query_str : string
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
        url = '{0}{1}'.format(self.native_api_base_url, query_str)
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
        query_str = '/dataverses/{0}'.format(identifier)
        resp = self.get_request(query_str, auth=auth)
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

        query_str = '/dataverses/{0}'.format(parent)
        resp = self.post_request(query_str, metadata, auth)

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
        query_str = '/dataverses/{0}/actions/:publish'.format(identifier)
        resp = self.post_request(query_str, auth=auth)

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
        query_str = '/dataverses/{0}'.format(identifier)
        resp = self.delete_request(query_str, auth)

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

    def get_dataset(self, identifier, auth=True, is_pid=True):
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

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        if is_pid:
            query_str = '/datasets/:persistentId/?persistentId={0}'.format(
                identifier)
        else:
            query_str = '/datasets/{0}'.format(identifier)
        resp = self.get_request(query_str, auth=auth)
        return resp

    def get_dataset_export(self, pid, export_format):
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
        query_str = '/datasets/export?exporter={0}&persistentId={1}'.format(
            export_format, pid)
        resp = self.get_request(query_str)
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
        query_str = '/dataverses/{0}/datasets'.format(dataverse)
        resp = self.post_request(query_str, metadata, auth)

        if resp.status_code == 404:
            error_msg = resp.json()['message']
            raise DataverseNotFoundError(
                'ERROR: HTTP 404 - Dataverse {0} was not found. MSG: {1}'
                ''.format(dataverse, error_msg))
        elif resp.status_code == 401:
            error_msg = resp.json()['message']
            raise ApiAuthorizationError(
                'ERROR: HTTP 401 - Delete Dataset unauthorized. MSG: '
                ''.format(error_msg)
            )
        elif resp.status_code == 201:
            identifier = resp.json()['data']['persistentId']
            print('Dataset {} created.'.format(identifier))
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
        query_str = '/datasets/:persistentId/actions/:publish'
        query_str += '?persistentId={0}&type={1}'.format(identifier, type)
        resp = self.post_request(query_str, auth=auth)

        if resp.status_code == 404:
            error_msg = resp.json()['message']
            raise DatasetNotFoundError(
                'ERROR: HTTP 404 - Dataset {0} was not found. MSG: {1}'
                ''.format(identifier, error_msg))
        elif resp.status_code == 401:
            error_msg = resp.json()['message']
            raise ApiAuthorizationError(
                'ERROR: HTTP 401 - User not allowed to publish dataset {0}. '
                'MSG: {1}'.format(identifier, error_msg))
        elif resp.status_code == 200:
            print('Dataset {} published'.format(identifier))
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
            query_str = '/datasets/:persistentId/?persistentId={0}'.format(
                identifier)
        else:
            query_str = '/datasets/{0}'.format(identifier)
        resp = self.delete_request(query_str, auth=auth)

        if resp.status_code == 404:
            error_msg = resp.json()['message']
            raise DatasetNotFoundError(
                'ERROR: HTTP 404 - Dataset {0} was not found. MSG: {1}'
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
                'ERROR: HTTP 401 - User not allowed to delete dataset {0}. '
                'MSG: {1}'.format(identifier, error_msg))
        elif resp.status_code == 200:
            print('Dataset {} deleted'.format(identifier))
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
            query_str = '/datasets/:persistentId/editMetadata/?persistentId={0}'
            ''.format(identifier)
        else:
            query_str = '/datasets/editMetadata/{0}'.format(identifier)
        params = {'replace': True} if is_replace else {}

        resp = self.put_request(query_str, metadata, auth, params)

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

    def get_datafiles(self, pid, version='1'):
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
        query_str = base_str + '{0}/files?persistentId={1}'.format(
            version, pid)
        resp = self.get_request(query_str)
        return resp

    def get_datafile(self, identifier, is_pid=True):
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
            query_str = '/access/datafile/{0}'.format(identifier)
        else:
            query_str = '/access/datafile/:persistentId/?persistentId={0}'
            ''.format(identifier)
        resp = self.get_request(query_str)
        return resp

    def get_datafile_bundle(self, identifier):
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
        query_str = '/access/datafile/bundle/{0}'.format(identifier)
        data = self.get_request(query_str)
        return data

    def upload_file(self, identifier, filename, is_pid=True):
        """Add file to a dataset.

        Add a file to an existing Dataset. Description and tags are optional:

        HTTP Request:

        .. code-block:: bash

            POST http://$SERVER/api/datasets/$id/add

        The upload endpoint checks the content of the file, compares it with
        existing files and tells if already in the database (most likely via
        hashing).

        Parameters
        ----------
        identifier : string
            Identifier of the dataset.
        filename : string
            Full filename with path.
        is_pid : bool
            ``True`` to use persistent identifier. ``False``, if not.

        Returns
        -------
        dict
            The json string responded by the CURL request, converted to a
            dict().

        """
        query_str = self.native_api_base_url
        if is_pid:
            query_str += '/datasets/:persistentId/add?persistentId={0}'.format(
                identifier)
        else:
            query_str += '/datasets/{0}/add'.format(identifier)
        shell_command = 'curl -H "X-Dataverse-key: {0}"'.format(
            self.api_token)
        shell_command += ' -X POST {0} -F file=@{1}'.format(
            query_str, filename)
        # TODO(Shell): is shell=True necessary?
        result = sp.run(shell_command, shell=True, stdout=sp.PIPE)
        resp = json.loads(result.stdout)
        return resp

    def get_info_version(self):
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
        query_str = '/info/version'
        resp = self.get_request(query_str)
        return resp

    def get_info_server(self):
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
        query_str = '/info/server'
        resp = self.get_request(query_str)
        return resp

    def get_info_apiTermsOfUse(self):
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
        query_str = '/info/apiTermsOfUse'
        resp = self.get_request(query_str)
        return resp

    def get_metadatablocks(self):
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
        query_str = '/metadatablocks'
        resp = self.get_request(query_str)
        return resp

    def get_metadatablock(self, identifier):
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
        query_str = '/metadatablocks/{0}'.format(identifier)
        resp = self.get_request(query_str)
        return resp
