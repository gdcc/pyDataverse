# coding: utf-8
from __future__ import absolute_import
from datetime import datetime
import json
import requests
import subprocess as sp


"""
Connect and request the Dataverse API Endpoints. Save and use request results.
"""


class Api(object):
    """API class.

    Parameters
    ----------
        host : string
            Description of parameter `host`.
        api_token : string
            Description of parameter `api_token`.
        use_https : boolean
            Is the api https secured or not.
        api_version : string
            Dataverse API version.

    Attributes
    ----------
    conn_started : type
        Description of attribute `conn_started`.
    base_url : type
        Description of attribute `base_url`.
    native_base_url : type
        Description of attribute `native_base_url`.
    dataverse_version : type
        Description of attribute `dataverse_version`.
    get_info_version : type
        Description of attribute `get_info_version`.
    host
    api_token
    use_https
    api_version

    """

    def __init__(self, base_url, api_token=None, use_https=True,
                 api_version='v1'):
        """Init an Api() class.

        Scheme, host and path combined create the base-url for the API.
        See more about url at https://en.wikipedia.org/wiki/URL

        """
        # set mandatory variables
        self.base_url = base_url
        # set optional variables
        self.api_token = api_token
        if self.base_url.find('https', 0, 5):
            self.use_https = True
        else:
            self.use_https = False
        self.api_version = api_version
        # set derived variables
        self.conn_started = datetime.now()
        self.native_api_base_url = '{0}/api/{1}'.format(self.base_url,
                                                        self.api_version)
        self.dataverse_version = \
            self.get_info_version().json()['data']['version']

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
            Description of parameter `query_str`.
        auth : bool
            Should an api token be used for authentication? By default = False.
        params : dict
            Dictionary of parameters to be passed with the request.
            Default: None

        Returns
        -------
        requests.Response
            Response object of request library.

        """
        if auth:
            if self.api_token:
                if not params:
                    params = {}
                params['key'] = self.api_token
            else:
                print('ERROR: API token not available for GET request.')

        try:
            resp = requests.get(
                '{0}{1}'.format(self.native_api_base_url, query_str),
                params=params
            )
            return resp
        except Exception as e:
            raise e

    def make_post_request(self, query_str, data, auth=False, headers=None,
                          params=None):
        """Make a POST request.

        Parameters
        ----------
        query_str : string
            Description of parameter `query_str`.
        data : ??
            Description of parameter `data`.
        auth : bool
            Should an api token be used for authentication? By default = False.
        headers : dict()
            Description.
        params : dict
            Dictionary of parameters to be passed with the request.
            Default: None

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        if auth:
            if self.api_token:
                if not params:
                    params = {}
                params['key'] = self.api_token
            else:
                print('ERROR: API token not available for POST request.')

        try:
            resp = requests.post(
                '{0}{1}'.format(self.native_api_base_url, query_str),
                data=data,
                headers=headers,
                params=params
            )
            return resp
        except Exception as e:
            raise e

    def make_delete_request(self, query_str, auth=False, params=None):
        """Make a DELETE request.

        auth : bool
            Should an api token be used for authentication? By default = False.
        params : dict
            Dictionary of parameters to be passed with the request.
            Default: None

        """
        if auth:
            if self.api_token:
                if not params:
                    params = {}
                params['key'] = self.api_token
            else:
                print('ERROR: API token not available for DELETE request.')

        resp = requests.delete(
            '{0}{1}'.format(self.native_base_url, query_str),
            params={'key': self.api_token}
        )
        return resp

    def get_dataverse(self, identifier):
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
            Response object of requerst library.

        """
        query_str = '/dataverses/{0}'.format(identifier)
        resp = self.make_get_request(query_str)
        return resp

    def create_dataverse(self, identifier, json, parent=':root'):
        """Create a dataverse.

        Generates a new dataverse under $id. Expects a JSON content describing
        the dataverse, as in the example below. If $id is omitted, a root
        dataverse is created. $id can either be a dataverse id (long) or a
        dataverse alias (more robust).

        POST http://$SERVER/api/dataverses/$id?key=$apiKey

        Download the JSON example file and modified to create dataverses to
        suit your needs. The fields name, alias, and dataverseContacts are
        required. http://guides.dataverse.org/en/latest/
        _downloads/dataverse-complete.json

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long) or a dataverse alias (more
            robust).
        json : string
            JSON-formatted string for upload.
        parent : string
            Parent dataverse if existing. Default is `:root`.

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        if not parent:
            print('No parent dataverse passed.')

        query_str = '/dataverses/{0}'.format(parent)
        resp = self.make_post_request(query_str, json)

        if resp.status_code == 404:
            print('Dataverse {0} was not found.'.format(parent))
        elif resp.status_code == 201:
            print('{0} Dataverse has been created.'.format(identifier))
        else:
            print('{0} Dataverse could not be created.'.format(identifier))
        return resp

    def delete_dataverse(self, identifier):
        """Delete dataverse by alias or id.

        Deletes the dataverse whose ID is given:
        DELETE http://$SERVER/api/dataverses/$id?key=$apiKey

        Parameters
        ----------
        identifier : string
            Can either be a dataverse id (long) or a dataverse alias (more
            robust).

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        query_str = '/dataverses/{0}'.format(identifier)
        resp = self.make_delete_request(query_str)

        if resp.status_code == 404:
            print('Dataverse {0} was not found.'.format(identifier))
        elif resp.status_code == 200:
            print('{0} Dataverse has been deleted.'.format(identifier))
        else:
            print('{0} Dataverse could not be deleted.'.format(identifier))
        return resp

    def get_dataset(self, identifier, is_doi=True):
        """Get metadata of a dataset.

        With Dataverse identifier:
            GET http://$SERVER/api/datasets/$identifier
        With PID:
            GET http://$SERVER/api/datasets/:persistentId/?persistentId=$ID
            GET http://$SERVER/api/datasets/:persistentId/
            ?persistentId=doi:10.5072/FK2/J8SJZB

        Parameters
        ----------
        identifier : string
            Doi of the dataset.
        is_doi : bool
            Is the identifier a Doi? Defaul: True, cause so far the module only
            supports Doi's.

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        if is_doi:
            query_str = '/datasets/:persistentId/?persistentId={0}'.format(
                identifier)
        else:
            query_str = '/datasets/{0}'.format(identifier)
        resp = self.make_get_request(query_str)
        return resp

    def get_dataset_export(self, export_format, identifier):
        """Get metadata of dataset exported in different formats.

        CORS Export the metadata of the current published version of a dataset
        in various formats:
        Formats: 'ddi', 'oai_ddi', 'dcterms', 'oai_dc', 'schema.org',
            'dataverse_json'

        GET http://$SERVER/api/datasets/
        export?exporter=ddi&persistentId=$persistentId

        Parameters
        ----------
        export_format : string
            Export format as a string.
        identifier : string
            Doi of the dataset.

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        query_str = '/datasets/export?exporter={0}&persistentId={1}'.format(
            export_format, identifier)
        resp = self.make_get_request(query_str)
        return resp

    def create_dataset(self, dataverse, json):
        """Add dataset to dataverse.

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

        Parameters
        ----------
        dataverse : string
            Alias for dataverse.
        json : string
            Dataverse metadata as json-formatted string.

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        query_str = '/dataverses/{0}/datasets'.format(dataverse)
        resp = self.make_post_request(query_str, json)

        if resp.status_code == 404:
            print('Dataverse {0} was not found.'.format(dataverse))
        elif resp.status_code == 201:
            print('Dataset has been created.')
        else:
            print('Dataset could not be created.')
        return resp

    def delete_dataset(self, identifier):
        """Delete dataset.

        Delete the dataset whose id is passed:
        DELETE http://$SERVER/api/datasets/$id?key=$apiKey

        Parameters
        ----------
        identifier : string
            Dataverse id or alias.

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        query_str = '/datasets/:persistentId/?persistentId={0}'.format(
            identifier)
        resp = self.make_delete_request(query_str)
        print(resp.status_code)
        print(resp.text)

        if resp.status_code == 404:
            print('Dataset {0} was not found.'.format(identifier))
        elif resp.status_code == 200:
            print('{0} Dataset has been deleted.'.format(identifier))
        elif resp.status_code == 405:
            print(
                'Published datasets can only be deleted from the GUI. For '
                'more information, please refer to '
                'https://github.com/IQSS/dataverse/issues/778'
            )
        else:
            print('{0} Dataset could not be deleted.'.format(identifier))
        return resp

    def get_files(self, doi, version='1'):
        """List metadata of all files of a dataset.

        http://guides.dataverse.org/en/latest/api/native-api.html#list-files-in-a-dataset
        GET http://$SERVER/api/datasets/$id/versions/$versionId/
        files?key=$apiKey

        Parameters
        ----------
        doi : string
            Doi of dataset.
        version : string
            Version of dataset.

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        base_str = '/datasets/:persistentId/versions/'
        query_str = base_str+'{0}/files?persistentId={1}'.format(version, doi)
        resp = self.make_get_request(query_str)
        return resp

    def get_file(self, identifier):
        """Download a datafile.

        File ID
            GET /api/access/datafile/$id
        DOI
            GET http://$SERVER/api/access/datafile/
            :persistentId/?persistentId=doi:10.5072/FK2/J8SJZB

        Parameters
        ----------
        identifier : string
            Doi of datafile.

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        query_str = '/access/datafile/{0}'.format(identifier)
        resp = self.make_get_request(query_str)
        return resp

    def get_file_bundle(self, identifier):
        """Download a datafile in all its formats.

        GET /api/access/datafile/bundle/$id

        Data Access API calls can now be made using persistent identifiers (in
        addition to database ids). This is done by passing the constant
        :persistentId where the numeric id of the file is expected, and then
        passing the actual persistent id as a query parameter with the name
        persistentId.

        Parameters
        ----------
        identifier : string
            Doi of Datafile.

        Returns
        -------
        requests.Response
            Response object of requerst library.

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
            Doi of dataset.
        filename : string
            Full filename with path.

        Returns
        -------
        dict
            Response of CURL request, converted to dict().

        """
        query_str = self.native_api_base_url
        query_str += '/datasets/:persistentId/add?persistentId={0}'.format(
            identifier)
        shell_command = 'curl -H "X-Dataverse-key: {0}"'.format(
            self.api_token)
        shell_command += ' -X POST {0} -F file=@{2}'.format(
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
            Response object of requerst library.

        """
        query_str = '/info/version'
        resp = self.make_get_request(query_str)
        return resp

    def get_info_server(self):
        """Get Dataverse Server Name.

        This is useful when a Dataverse system is
        composed of multiple Java EE servers behind a load balancer.

        GET http://$SERVER/api/info/server

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        query_str = '/info/server'
        resp = self.make_get_request(query_str)
        return resp

    def get_info_apiTermsOfUse(self):
        """Get API Terms of Use URL.

        The response contains the text value inserted as API Terms of use which
        uses the database setting :ApiTermsOfUse.

        GET http://$SERVER/api/info/apiTermsOfUse

        Returns
        -------
        requests.Response
            Response object of requerst library.

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
            Response object of requerst library.

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
            Response object of requerst library.

        """
        query_str = '/metadatablocks/{0}'.format(identifier)
        resp = self.make_get_request(query_str)
        return resp
