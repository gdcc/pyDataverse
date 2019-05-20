# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/AUSSDA/pyDataverse."""
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
import subprocess as sp


"""
Connect and request the Dataverse API Endpoints. Save and use request results.
"""


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

    Example
    ----------
    Create an Api connection::

        >>> base_url = 'http://demo.dataverse.org'
        >>> api = Api(base_url)
        >>> api.status
        'OK'

    """

    def __init__(self, base_url, api_token=None, api_version='v1'):
        """Init an `Api()` class.

        Scheme, host and path combined create the base-url for the api.
        See more about url at https://en.wikipedia.org/wiki/URL

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

    def make_get_request(self, query_str, params=None, auth=False):
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
                    '`make_get_request` {}.'.format(url)
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

    def make_post_request(self, query_str, metadata=None, auth=False,
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
                    '`make_post_request` {}.'.format(url)
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

    def make_delete_request(self, query_str, auth=False, params=None):
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
                    '`make_delete_request` {}.'.format(url)
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

        View data about the dataverse $identified by identifier. Identifier can
        be the id number of the dataverse, its alias, or the special
        value :root.

        GET http://$SERVER/api/dataverses/$id

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
        resp = self.make_get_request(query_str, auth=auth)
        return resp

    def create_dataverse(self, identifier, metadata, auth=True,
                         parent=':root'):
        """Create a dataverse.

        Generates a new dataverse under identifier. Expects a JSON content
        describing the dataverse, as in the example below. If identifier is
        omitted, a root dataverse is created. $id can either be a dataverse id
        (long) or a dataverse alias (more robust).

        POST http://$SERVER/api/dataverses/$id?key=$apiKey

        Download the JSON example file and modified to create dataverses to
        suit your needs. The fields name, alias, and dataverseContacts are
        required. http://guides.dataverse.org/en/latest/
        _downloads/dataverse-complete.json

        resp.status_code:
            200: dataverse created
            201: dataverse created

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long) or a dataverse alias (more
            robust).
        metadata : string
            Metadata of the Dataverse as a json-formatted string.
        auth : bool
            True if api authorization is necessary. Defaults to `True`.
        parent : string
            Parent dataverse, if existing, to which the Dataverse gets attached
            to. Defaults to `:root`.

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
        resp = self.make_post_request(query_str, metadata, auth)

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

        POST http://$SERVER/api/dataverses/$identifier/actions/:publish

        resp.status_code:
            200: dataverse published

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long) or a dataverse alias (more
            robust).
        auth : bool
            True if api authorization is necessary. Defaults to `False`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/dataverses/{0}/actions/:publish'.format(identifier)
        resp = self.make_post_request(query_str, auth=auth)

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

        Deletes the dataverse whose ID is given:
        DELETE http://$SERVER/api/dataverses/$id?key=$apiKey

        resp.status_code:
            200: dataverse deleted

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
        resp = self.make_delete_request(query_str, auth)

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

    def get_dataset(self, identifier, auth=True, is_doi=True):
        """Get metadata of dataset.

        With Dataverse identifier:
            GET http://$SERVER/api/datasets/$identifier
        With PID:
            GET http://$SERVER/api/datasets/:persistentId/?persistentId=$ID
            GET http://$SERVER/api/datasets/:persistentId/
            ?persistentId=doi:10.5072/FK2/J8SJZB

        Parameters
        ----------
        identifier : string
            Doi of the dataset. e.g. `doi:10.11587/8H3N93`.
        is_doi : bool
            Is the identifier a Doi? Defauls to `True`. So far, the module only
            supports Doi's as PID's.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        if is_doi:
            query_str = '/datasets/:persistentId/?persistentId={0}'.format(
                identifier)
        else:
            query_str = '/datasets/{0}'.format(identifier)
        resp = self.make_get_request(query_str, auth=auth)
        return resp

    def get_dataset_export(self, identifier, export_format):
        """Get metadata of dataset exported in different formats.

        CORS Export the metadata of the current published version of a dataset
        in various formats:

        GET http://$SERVER/api/datasets/
        export?exporter=ddi&persistentId=$persistentId

        Parameters
        ----------
        identifier : string
            Doi of the dataset. e.g. `doi:10.11587/8H3N93`.
        export_format : string
            Export format as a string. Formats: 'ddi', 'oai_ddi', 'dcterms',
            'oai_dc', 'schema.org', 'dataverse_json'.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/datasets/export?exporter={0}&persistentId={1}'.format(
            export_format, identifier)
        resp = self.make_get_request(query_str)
        return resp

    def create_dataset(self, dataverse, metadata, auth=True):
        """Add dataset to a dataverse.

        http://guides.dataverse.org/en/latest/api/native-api.html#create-a-dataset-in-a-dataverse

        POST http://$SERVER/api/dataverses/$dataverse/datasets --upload-file
         FILENAME

        curl -H "X-Dataverse-key: $API_TOKEN" -X POST $SERVER_URL/api/
        dataverses/$DV_ALIAS/datasets/:import?pid=$PERSISTENT_IDENTIFIER&
        release=yes --upload-file dataset.json
        curl -H "X-Dataverse-key: $API_TOKEN" -X POST $SERVER_URL/api/
        dataverses/$DV_ALIAS/datasets --upload-file dataset-finch1.json

        To create a dataset, you must create a JSON file containing all the
        metadata you want such as in this example file: dataset-finch1.json.
        Then, you must decide which dataverse to create the dataset in and
        target that datavese with either the "alias" of the dataverse (e.g.
        "root" or the database id of the dataverse (e.g. "1"). The initial
        version state will be set to DRAFT:
        http://guides.dataverse.org/en/latest/_downloads/dataset-finch1.json

        resp.status_code:
            201: dataset created

        Parameters
        ----------
        dataverse : string
            Alias of dataverse to which the dataset should be added to.
        metadata : string
            Metadata of the Dataset as a json-formatted string.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/dataverses/{0}/datasets'.format(dataverse)
        resp = self.make_post_request(query_str, metadata, auth)

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

    def publish_dataset(self, identifier, type='minor', auth=True):
        """Publish dataset.

        Publishes the dataset whose id is passed. If this is the first version
        of the dataset, its version number will be set to 1.0. Otherwise, the
        new dataset version number is determined by the most recent version
        number and the type parameter. Passing type=minor increases the minor
        version number (2.3 is updated to 2.4). Passing type=major increases
        the major version number (2.3 is updated to 3.0). Superusers can pass
        type=updatecurrent to update metadata without changing the version
        number.

        POST http://$SERVER/api/datasets/$id/actions/:publish?type=$type

        When there are no default workflows, a successful publication process
        will result in 200 OK response. When there are workflows, it is
        impossible for Dataverse to know how long they are going to take and
        whether they will succeed or not (recall that some stages might require
        human intervention). Thus, a 202 ACCEPTED is returned immediately. To
        know whether the publication process succeeded or not, the client code
        has to check the status of the dataset periodically, or perform some
        push request in the post-publish workflow.

        resp.status_code:
            200: dataset published

        Parameters
        ----------
        identifier : string
            Doi of the dataset. e.g. `doi:10.11587/8H3N93`.
        type : string
            Passing `minor` increases the minor version number (2.3 is
            updated to 2.4).
            Passing `major` increases the major version number (2.3 is
            updated to 3.0). Superusers can pass `updatecurrent` to update
            metadata without changing the version number:
        auth : bool
            True if api authorization is necessary. Defaults to `False`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/datasets/:persistentId/actions/:publish'
        query_str += '?persistentId={0}&type={1}'.format(identifier, type)
        resp = self.make_post_request(query_str, auth=auth)

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

    def delete_dataset(self, identifier, auth=True):
        """Delete a dataset.

        Delete the dataset whose id is passed:
        DELETE http://$SERVER/api/datasets/$id?key=$apiKey

        resp.status_code:
            200: dataset deleted

        Parameters
        ----------
        identifier : string
            Doi of the dataset. e.g. `doi:10.11587/8H3N93`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/datasets/:persistentId/?persistentId={0}'.format(
            identifier)
        resp = self.make_delete_request(query_str, auth=auth)

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

    def get_datafiles(self, doi, version='1'):
        """List metadata of all datafiles of a dataset.

        http://guides.dataverse.org/en/latest/api/native-api.html#list-files-in-a-dataset
        GET http://$SERVER/api/datasets/$id/versions/$versionId/
        files?key=$apiKey

        Parameters
        ----------
        doi : string
            Doi of the dataset. e.g. `doi:10.11587/8H3N93`.
        version : string
            Version of dataset. Defaults to `1`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        base_str = '/datasets/:persistentId/versions/'
        query_str = base_str+'{0}/files?persistentId={1}'.format(version, doi)
        resp = self.make_get_request(query_str)
        return resp

    def get_datafile(self, identifier):
        """Download a datafile via the Dataverse Data Access API.

        File ID
            GET /api/access/datafile/$id
        DOI
            GET http://$SERVER/api/access/datafile/
            :persistentId/?persistentId=doi:10.5072/FK2/J8SJZB

        Parameters
        ----------
        identifier : string
            Doi of the dataset. e.g. `doi:10.11587/8H3N93`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/access/datafile/{0}'.format(identifier)
        resp = self.make_get_request(query_str)
        return resp

    def get_datafile_bundle(self, identifier):
        """Download a datafile in all its formats via the Dataverse Data Access API.

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
            Doi of the dataset. e.g. `doi:10.11587/8H3N93`.

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/access/datafile/bundle/{0}'.format(identifier)
        data = self.make_get_request(query_str)
        return data

    def upload_file(self, identifier, filename):
        """Add file to a dataset.

        Add a file to an existing Dataset. Description and tags are optional:
        POST http://$SERVER/api/datasets/$id/add?key=$apiKey

        The upload endpoint checks the content of the file, compares it with
        existing files and tells if already in the database (most likely via
        hashing)

        Parameters
        ----------
        identifier : string
            Doi of the dataset. e.g. `doi:10.11587/8H3N93`.
        filename : string
            Full filename with path.

        Returns
        -------
        dict
            The json string responded by the CURL request, converted to a
            dict().

        """
        query_str = self.native_api_base_url
        query_str += '/datasets/:persistentId/add?persistentId={0}'.format(
            identifier)
        shell_command = 'curl -H "X-Dataverse-key: {0}"'.format(
            self.api_token)
        shell_command += ' -X POST {0} -F file=@{1}'.format(
            query_str, filename)
        # TODO: is shell=True necessary?
        result = sp.run(shell_command, shell=True, stdout=sp.PIPE)
        resp = json.loads(result.stdout)
        return resp

    def get_info_version(self):
        """Get the Dataverse version and build number.

        The response contains the version and build numbers.

        Requires no api_token
        GET http://$SERVER/api/info/version

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/info/version'
        resp = self.make_get_request(query_str)
        return resp

    def get_info_server(self):
        """Get dataverse server name.

        This is useful when a Dataverse system is
        composed of multiple Java EE servers behind a load balancer.

        GET http://$SERVER/api/info/server

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/info/server'
        resp = self.make_get_request(query_str)
        return resp

    def get_info_apiTermsOfUse(self):
        """Get API Terms of Use url.

        The response contains the text value inserted as API Terms of use which
        uses the database setting :ApiTermsOfUse.

        GET http://$SERVER/api/info/apiTermsOfUse

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/info/apiTermsOfUse'
        resp = self.make_get_request(query_str)
        return resp

    def get_metadatablocks(self):
        """Get info about all metadata blocks.

        Lists brief info about all metadata blocks registered in the system.

        GET http://$SERVER/api/metadatablocks

        Returns
        -------
        requests.Response
            Response object of requests library.

        """
        query_str = '/metadatablocks'
        resp = self.make_get_request(query_str)
        return resp

    def get_metadatablock(self, identifier):
        """Get info about single metadata block.

        Returns data about the block whose identifier is passed. identifier can
        either be the block’s id, or its name.

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
        resp = self.make_get_request(query_str)
        return resp
