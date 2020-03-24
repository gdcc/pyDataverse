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

    Attributes
    ----------
    base_url
    api_token
    dataverse_version

    """

    def __init__(self, base_url, api_token=None, api_version='latest'):
        """Init an Api() class.

        Scheme, host and path combined create the base-url for the api.
        See more about URL at `Wikipedia <https://en.wikipedia.org/wiki/URL>`_.

        Parameters
        ----------
        base_url : string
            Base url for Dataverse api.
        api_token : string
            Api token for Dataverse api.

        Examples
        -------
        Create an Api connection::

            >>> from pyDataverse.api import Api
            >>> base_url = 'http://demo.dataverse.org'
            >>> api = Api(base_url)
            >>> api.status
            'OK'

        """

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

        if self.base_url:
            if self.api_version == 'latest':
                self.base_url_api = '{0}/api'.format(self.base_url)
            else:
                self.base_url_api = '{0}/api/{1}'.format(self.base_url, self.api_version)
        else:
            self.base_url_api = None

        # try:
        #     resp = self.get_info_version()
        #     if 'data' in resp.json().keys():
        #         if 'version' in resp.json()['data'].keys():
        #             self.dataverse_version = resp.json()['data']['version']
        #         else:
        #             # TODO: raise exception
        #             self.dataverse_version = None
        #             print('Key not in response.')
        #     else:
        #         self.dataverse_version = None
        #         # TODO: raise exception
        #         print('Key not in response.')
        # except:
        #     self.dataverse_version = None
        #     # TODO: raise exception
        #     print('Dataverse build version can not be retrieved.')

        self.timeout = 500

    def __str__(self):
        """Return name of Api() class for users.

        Returns
        -------
        string
            Naming of the API class.

        """
        return 'pyDataverse API class'

    def get_request(self, url, params=None, auth=False):
        """Make a GET request.

        Parameters
        ----------
        url : string
            Full URL.
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

    def post_request(self, url, metadata=None, auth=False,
                     params=None):
        """Make a POST request.

        Parameters
        ----------
        url : string
            Full URL.
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

    def put_request(self, url, metadata=None, auth=False,
                    params=None):
        """Make a PUT request.

        Parameters
        ----------
        url : string
            Full URL.
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

    def delete_request(self, url, auth=False, params=None):
        """Make a DELETE request.

        Parameters
        ----------
        url : string
            Full URL.
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


class DataAccessApi(Api):
    """Short summary.

    Examples
    -------
    Examples should be written in doctest format, and
    should illustrate how to use the function/class.
    >>>

    Attributes
    ----------
    base_url_api_data_access : type
        Description of attribute `base_url_api_data_access`.
    base_url : type
        Description of attribute `base_url`.

    """

    def __init__(self, base_url, api_token=None):
        """Init an DataAccessApi() class.
        """
        super().__init__(base_url, api_token, api_version)
        if base_url:
            self.base_url_api_data_access = '{0}/access'.format(self.base_url_api)
        else:
            self.base_url_api_data_access = self.base_url_api

    def __str__(self):
        """Return name of DataAccessApi() class for users.

        Returns
        -------
        string
            Naming of the DataAccess API class.

        """
        return 'pyDataverse Data-Access-API class'

    def get_datafile(self, identifier, format=None, noVarHeader=None,
                     imageThumb=None, is_pid=True, auth=False):
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
        is_first_param = True
        if is_pid:
            url = '{0}/datafile/{1}'.format(self.base_url_api_data_access, identifier)
            if format or noVarHeader or imageThumb:
                url += '?'
        else:
            url = '{0}/datafile/:persistentId/?persistentId={1}'
            ''.format(self.base_url_api_data_access, identifier)
        if format:
            url += 'format={0}'.format(format)
            is_first_param = False
        if noVarHeader:
            if not is_first_param:
                url += '&'
            url += 'noVarHeader={0}'.format(noVarHeader)
            is_first_param = False
        if imageThumb:
            if not is_first_param:
                url += '&'
            url += 'imageThumb={0}'.format(imageThumb)
        resp = self.get_request(url, auth=auth)
        return resp

    def get_datafiles(self, identifier, format=None, auth=False):
        """Download a datafile via the Dataverse Data Access API.

        Get by file id (HTTP Request).

        .. code-block:: bash

            GET /api/access/datafiles/$id1,$id2,...$idN

        Get by persistent identifier (HTTP Request).

        Parameters
        ----------
        identifier : string
            Identifier of the dataset. Can be datafile id or persistent
            identifier of the datafile (e. g. doi).

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        url = '{0}/datafiles/{1}'.format(self.base_url_api_data_access, identifier)
        if format:
            url += '?format={0}'.format(format)
        resp = self.get_request(url, auth=auth)
        return resp

    def get_datafile_bundle(self, identifier, fileMetadataId=None, auth=False):
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
        url = '{0}/datafile/bundle/{1}'.format(self.base_url_api_data_access, identifier)
        if fileMetadataId:
            url += '?fileMetadataId={0}'.format(fileMetadataId)
        resp = self.get_request(url, auth=auth)
        return resp


    def request_access(self, identifier):
        """
        curl -H "X-Dataverse-key:$API_TOKEN" -X PUT http://$SERVER/api/access/datafile/{id}/requestAccess
        """
        url = '{0}/datafile/{1}/requestAccess'.format(self.base_url_api_data_access, identifier)
        resp = self.get_request(url, auth=auth)
        return resp


    def grant_file_access(self, identifier, user):
        """
        curl -H "X-Dataverse-key:$API_TOKEN" -X PUT http://$SERVER/api/access/datafile/{id}/grantAccess/{@userIdentifier}
        """
        url = '{0}/datafile/{1}/grantAccess/{2}'.format(
            self.base_url_api_data_access, identifier, user)
        resp = self.get_request(url, auth=auth)
        return resp


    def list_file_access_requests(self, identifier):
        """
        curl -H "X-Dataverse-key:$API_TOKEN" -X GET http://$SERVER/api/access/datafile/{id}/listRequests
        """
        url = '{0}/datafile/{1}/listRequests'.format(
            self.base_url_api_data_access, identifier)
        resp = self.get_request(url, auth=auth)
        return resp


class MetricsApi(Api):
    """Short summary.

    Examples
    -------
    Examples should be written in doctest format, and
    should illustrate how to use the function/class.
    >>>

    Attributes
    ----------
    base_url_api_metrics : type
        Description of attribute `base_url_api_metrics`.
    base_url : type
        Description of attribute `base_url`.

    """

    def __init__(self, base_url, api_version='latest', api_token=None):
        """Init an MetricsApi() class.
        """
        if base_url:
            self.base_url_api_metrics = '{0}/api/info/metrics'.format(self.base_url)
        else:
            self.base_url_api_metrics = None


    def __str__(self):
        """Return name of MetricsApi() class for users.

        Returns
        -------
        string
            Naming of the MetricsApi() class.

        """
        return 'pyDataverse Metrics-API class'


class NativeApi(Api):

    def __init__(self, base_url, api_token=None, api_version='v1'):
        """Init an Api() class.

        Scheme, host and path combined create the base-url for the api.
        See more about URL at `Wikipedia <https://en.wikipedia.org/wiki/URL>`_.

        Parameters
        ----------
        native_api_version : string
            Api version of Dataverse native api. Default is `v1`.

        """
        super().__init__(base_url, api_token, api_version)
        self.base_url_api_native = self.base_url_api

    def __str__(self):
        """Return name of NativeApi() class for users.

        Returns
        -------
        string
            Naming of the NativeApi() class.

        """
        return 'pyDataverse Native-API class'

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
        url = '{0}/dataverses/{1}'.format(self.base_url_api_native, identifier)
        resp = self.get_request(url, auth=auth)
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

        url = '{0}/dataverses/{1}'.format(self.base_url_api_native, parent)
        resp = self.post_request(url, metadata, auth)

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
        url = '{0}/dataverses/{1}/actions/:publish'.format(self.base_url_api_native, identifier)
        resp = self.post_request(url, auth=auth)

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
        url = '{0}/dataverses/{1}'.format(self.base_url_api_native, identifier)
        resp = self.delete_request(url, auth)

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
        url = '{0}/dataverses/{1}/roles'.format(self.base_url_api_native, identifier)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/dataverses/{1}/contents'.format(self.base_url_api_native, identifier)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/dataverses/{1}/assignments'.format(self.base_url_api_native, identifier)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/dataverses/{1}/facets'.format(self.base_url_api_native, identifier)
        resp = self.get_request(url, auth=auth)
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
            # TODO: Add version to query http://guides.dataverse.org/en/4.18.1/api/native-api.html#get-json-representation-of-a-dataset
            url = '{0}/datasets/:persistentId/?persistentId={1}'.format(
                self.base_url_api_native, identifier)
        else:
            url = '{0}/datasets/{1}'.format(self.base_url_api_native, identifier)
            # CHECK: Its not really clear, if the version query can also be done via ID.
        resp = self.get_request(url, auth=auth)
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
            url = '{0}/datasets/:persistentId/versions?persistentId={1}'.format(
                self.base_url_api_native, identifier)
        else:
            url = '{0}/datasets/{1}/versions'.format(self.base_url_api_native, identifier)
        resp = self.get_request(url, auth=auth)
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
            url = '{0}/datasets/:persistentId/versions/{1}?persistentId={2}'.format(
                self.base_url_api_native, version, identifier)
        else:
            url = '{0}/datasets/{1}/versions/{2}'.format(self.base_url_api_native, identifier, version)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/datasets/export?exporter={1}&persistentId={2}'.format(
            self.base_url_api_native, export_format, pid)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/dataverses/{1}/datasets'.format(self.base_url_api_native, dataverse)
        resp = self.post_request(url, metadata, auth)

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
            url = '{0}/datasets/:persistentId/privateUrl/?persistentId={1}'.format(self.base_url_api_native, identifier)
        else:
            url = '{0}/datasets/{1}/privateUrl'.format(self.base_url_api_native, identifier)

        resp = self.post_request(url, auth=auth)

        if resp.status_code == 200:
            print('Dataset private URL created: {0}'.format(resp.json()['data']['link']))
        return resp

    def get_dataset_private_url(self, identifier, is_pid=True, auth=True):
        """Get private Dataset URL.

        GET http://$SERVER/api/datasets/$id/privateUrl?key=$apiKey

        http://guides.dataverse.org/en/4.16/api/native-api.html#get-the-private-url-for-a-dataset

        """
        if is_pid:
            url = '{0}/datasets/:persistentId/privateUrl/?persistentId={1}'.format(self.base_url_api_native, identifier)
        else:
            url = '{0}/datasets/{1}/privateUrl'.format(self.base_url_api_native, identifier)

        resp = self.get_request(url, auth=auth)

        if resp.status_code == 200:
            print('Got Dataset private URL: {0}'.format(resp.json()['data']['link']))
        return resp

    def delete_dataset_private_url(self, identifier, is_pid=True, auth=True):
        """Get private Dataset URL.

        DELETE http://$SERVER/api/datasets/$id/privateUrl?key=$apiKey

        http://guides.dataverse.org/en/4.16/api/native-api.html#delete-the-private-url-from-a-dataset

        """
        if is_pid:
            url = '{0}/datasets/:persistentId/privateUrl/?persistentId={1}'.format(self.base_url_api_native, identifier)
        else:
            url = '{0}/datasets/{1}/privateUrl'.format(self.base_url_api_native, identifier)

        resp = self.delete_request(url, auth=auth)

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
        url = '{0}/datasets/:persistentId/actions/:publish'.format(self.base_url_api_native)
        url += '?persistentId={0}&type={1}'.format(pid, type)
        resp = self.post_request(url, auth=auth)

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
        url = '{0}/datasets/:persistentId/locks/?persistentId={1}'.format(self.base_url_api_native, pid)
        resp = self.get_request(url, auth=True)
        return resp

    def get_dataset_assignments(self, identifier, is_pid=True, auth=True):
        """Get Dataset assignments.

        GET http://$SERVER/api/datasets/$id/assignments?key=$apiKey


        """
        if is_pid:
            url = '{0}/datasets/:persistentId/assignments/?persistentId={0}'.format(self.base_url_api_native, identifier)
        else:
            url = '{0}/datasets/{0}/assignments'.format(self.base_url_api_native, identifier)

        resp = self.get_request(url, auth=auth)
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
            url = '{0}/datasets/:persistentId/?persistentId={1}'.format(
                self.base_url_api_native, identifier)
        else:
            url = '{0}/datasets/{1}'.format(self.base_url_api_native, identifier)
        resp = self.delete_request(url, auth=auth)

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
            url = '{0}/datasets/:persistentId/destroy/?persistentId={1}'.format(self.base_url_api_native, identifier)
        else:
            url = '{0}/datasets/{1}/destroy'.format(self.base_url_api_native, identifier)

        resp = self.delete_request(url, auth=auth)

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
            url = '{0}/datasets/:persistentId/editMetadata/?persistentId={1}'
            ''.format(self.base_url_api_native, identifier)
        else:
            url = '{0}/datasets/editMetadata/{0}'.format(self.base_url_api_native, identifier)
        params = {'replace': True} if is_replace else {}

        resp = self.put_request(url, metadata, auth, params)

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
            Full filename with url.
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
        url = self.base_url_api_native
        if is_pid:
            url += '/datasets/:persistentId/add?persistentId={0}'.format(identifier)
        else:
            url += '/datasets/{0}/add'.format(identifier)
        shell_command = 'curl -H "X-Dataverse-key: {0}"'.format(
            self.api_token)
        shell_command += ' -X POST {0} -F file=@{1}'.format(
            url, filename)
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
        base_str = '{0}/datasets/:persistentId/versions/'.format(self.base_url_api_native)
        url = base_str + '{0}/files?persistentId={1}'.format(
            version, pid)
        resp = self.get_request(url, auth=auth)
        return resp

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
        url = '{0}/files/{}/metadata'.format(self.base_url_api_native, datafile_id)

        resp = self.post_request(url, auth=auth)

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
        url = '{0}/info/version'.format(self.base_url_api_native)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/info/server'.format(self.base_url_api_native)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/info/apiTermsOfUse'.format(self.base_url_api_native)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/metadatablocks'.format(self.base_url_api_native)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/metadatablocks/{1}'.format(self.base_url_api_native, identifier)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/users/token'.format(self.base_url_api_native)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/users/token/recreate'.format(self.base_url_api_native)
        resp = self.post_request(url)
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
        url = '{0}/users/token'.format(self.base_url_api_native)
        resp = self.delete_request(url)
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
        url = '{0}/roles?dvo={1}'.format(self.base_url_api_native, dataverse_id)
        resp = self.post_request(url)
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
        url = '{0}/roles/{1}'.format(self.base_url_api_native, role_id)
        resp = self.get_request(url, auth=auth)
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
        url = '{0}/roles/{1}'.format(self.base_url_api_native, role_id)
        resp = self.delete_request(url)
        return resp

    def walker(self, dv_alias_lst=None, ds_pid_lst=None, dataverse=':root'):
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
        dv_id_lst : list
            List with Dataverse ID's.
        ds_pid_lst : list
            List of Dataset PID's.
        dataverse : type
            Parent dataverse to start from.

        Returns
        -------
        type
            Description of returned object.
        """
        if dv_alias_lst is None:
            dv_alias_lst = []
        if ds_pid_lst is None:
            ds_pid_lst = []
        resp = self.get_dataverse_contents(dataverse)
        if 'data' in resp.json():
            content = resp.json()['data']
            for c in content:
                if c['type'] == 'dataset':
                    ds_pid_lst.append(c['identifier'])
                elif c['type'] == 'dataverse':
                    resp = self.get_dataverse(c['id'])
                    if 'data' in resp.json():
                        alias = resp.json()['data']['alias']
                        dv_alias_lst.append(alias)
                        dv_alias_lst, ds_pid_lst = self.walker(dv_alias_lst, ds_pid_lst, alias)
                    else:
                        print('ERROR: Can not resolve Dataverse ID to alias.')
        else:
            print('Walker: API request not working.')
        return dv_alias_lst, ds_pid_lst


class SearchApi(Api):
    """Short summary.

    Examples
    -------
    Examples should be written in doctest format, and
    should illustrate how to use the function/class.
    >>>

    Attributes
    ----------
    base_url_api_search : type
        Description of attribute `base_url_api_search`.
    base_url : type
        Description of attribute `base_url`.

    """

    def __init__(self, base_url, api_token=None, api_version='latest'):
        """Init an SearchApi() class.
        """
        super().__init__(base_url, api_token, api_version)
        if base_url:
            self.base_url_api_search = '{0}/search?q='.format(self.base_url_api)
        else:
            self.base_url_api_search = self.base_url_api


    def __str__(self):
        """Return name of SearchApi() class for users.

        Returns
        -------
        string
            Naming of the Search API class.

        """
        return 'pyDataverse Search-API class'

    def get(self, q, type=None, subtree=None, sort=None, order=None,
            per_page=None, start=None, show_relevance=None, show_facets=None,
            fq=None, show_entity_ids=None, query_entities=None):
        """

        http://guides.dataverse.org/en/4.18.1/api/search.html
        """
        url = '{0}{1}'.format(self.base_url_api_search, q)
        if type:
            # TODO: pass list of types
            url += '&type={0}'.format(type)
        if subtree:
            # TODO: pass list of subtrees
            url += '&subtree={0}'.format(subtree)
        if sort:
            url += '&sort={0}'.format(sort)
        if order:
            url += '&order={0}'.format(order)
        if per_page:
            url += '&per_page={0}'.format(per_page)
        if start:
            url += '&start={0}'.format(start)
        if show_relevance:
            url += '&show_relevance={0}'.format(show_relevance)
        if show_facets:
            url += '&show_facets={0}'.format(show_facets)
        if fq:
            url += '&fq={0}'.format(fq)
        if show_entity_ids:
            url += '&show_entity_ids={0}'.format(show_entity_ids)
        if query_entities:
            url += '&query_entities={0}'.format(query_entities)
        resp = self.get_request(url, auth=auth)
        return resp


class SwordApi(Api):
    """Short summary.

    Parameters
    ----------
    sword_api_version : type
        Description of parameter `sword_api_version` (the default is 'v1.1').

    Examples
    -------
    Examples should be written in doctest format, and
    should illustrate how to use the function/class.
    >>>

    Attributes
    ----------
    base_url_api_sword : type
        Description of attribute `base_url_api_sword`.
    base_url : type
        Description of attribute `base_url`.
    native_api_version : type
        Description of attribute `native_api_version`.
    sword_api_version

    """

    def __init__(self, base_url, api_version='latest', api_token=None, sword_api_version='v1.1'):
        """Init an SwordApi() class.

        Parameters
        ----------
        sword_api_version : string
            Api version of Dataverse SWORD API.

        """
        if not isinstance(sword_api_version, ("".__class__, u"".__class__)):
            raise ApiUrlError('sword_api_version {0} is not a string.'.format(
                sword_api_version))
        self.sword_api_version = sword_api_version

        # Test connection.
        if base_url and sword_api_version:
            self.base_url_api_sword = '{0}/dvn/api/data-deposit/v1.1{1}'.format(self.base_url,
                                                            self.native_api_version)
        else:
            self.base_url_api_sword = None

    def __str__(self):
        """Return name of Api() class for users.

        Returns
        -------
        string
            Naming of the SWORD API class.

        """
        return 'pyDataverse SWORD-API class'
