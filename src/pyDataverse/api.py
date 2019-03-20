from __future__ import absolute_import

from datetime import datetime
import requests

"""
Connect and request the Dataverse API Endpoints. Save and use request results.
"""


class Api(object):
    """DEFAULT."""

    def __init__(self, host, api_token=None, use_https=True, api_version='v1'):
        """Init an Api() class.

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

        Returns
        -------
        type
            Description of returned object.

        """
        # set passed values
        self.host = host
        self.api_token = api_token
        self.use_https = use_https
        self.api_version = api_version
        # set derived values
        self.conn_started = datetime.now()
        if use_https:
            url_scheme = 'https://'
        else:
            url_scheme = 'http://'
        self.base_url = '{0}{1}'.format(url_scheme, self.host)
        self.native_base_url = '{0}/api/{1}'.format(self.base_url,
                                                    self.api_version)
        self.dataverse_version = \
            self.get_info_version('json_as_dict')['data']['version']

    def __str__(self):
        """Return naming of Api() class for users.

        Parameters
        ----------


        Returns
        -------
        string
            Naming of the Api() class.

        """
        return 'pyDataverse API class'

    def __get_request_return(self, resp, return_data_type='json_as_dict'):
        """Return the needed data type for the request made.

        Parameters
        ----------
        resp : requests.Response
            Return of the requests.request function call.
        return_data_type : string
            Wanted data type to return, 'text', 'json_as_dict', 'content'
            and 'response_object' as options.

        Returns
        -------
        dict(), response object, string or boolean
            Returns the requested data, or False if error occurs.

        All other specific options can be accessed directly via the response
        object.

        """
        if return_data_type == 'text':
            return resp.text
        elif return_data_type == 'json_as_dict':
            return resp.json()
        elif return_data_type == 'content':
            return resp.content
        elif return_data_type == 'response_object':
            return resp
        else:
            print('No valid return_data_type passed.')
            return False

    def make_post_request(self, query_str, json, auth=True):
        """Make a POST request.

        Parameters
        ----------
        query_str : string
            Description of parameter `query_str`.
        json : string
            Description of parameter `json`.
        auth : boolean
            Is authentication used (True/False).

        Returns
        -------
        requests.Response
            Response object of requerst library.

        """
        if auth:
            resp = requests.post(
                '{0}{1}'.format(self.native_base_url, query_str),
                json,
                params={'key': self.api_token}
            )
        else:
            resp = requests.post(
                query_str,
                json
            )

        return resp

    def make_get_request(self, query_str, auth=True):
        """Make a GET request.

        Parameters
        ----------
        query_str : string
            Description of parameter `query_str`.
        auth : boolean
            Is authentication used (True/False).

        Returns
        -------
        requests.Response
            Response object of request library.

        """
        if auth:
            resp = requests.get(
                '{0}{1}'.format(self.native_base_url, query_str),
                params={'key': self.api_token}
            )
        else:
            resp = requests.get(query_str)
        return resp

    def make_delete_request(self, query_str):
        """Make a DELETE request."""
        resp = requests.delete(
            '{0}{1}'.format(self.native_base_url, query_str),
            params={'key': self.api_token}
        )
        return resp

    def get_dataverse(self, identifier, return_data_type='json_as_dict'):
        """Get a dataverse.

        View data about the dataverse $identified by identifier. Identifier can
        be the id number of the dataverse, its alias, or the special
        value :root.

        GET http://$SERVER/api/dataverses/$id
        """
        query_str = '/dataverses/{0}'.format(identifier)
        resp = self.make_get_request(query_str)
        data = self.__get_request_return(resp, return_data_type)
        return data

    def create_dataverse(self, identifier, json, parent=':root',
                         return_data_type='json_as_dict'):
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
            Description of parameter `json`.
        parent : string
            Parent dataverse if existing.
        return_data_type : string
            Description of parameter `return_data_type`.

        Returns
        -------
        type
            Description of returned object.

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
        data = self.__get_request_return(resp, return_data_type)
        return data

    def delete_dataverse(self, identifier, return_data_type='json_as_dict'):
        """Delete dataverse.

        Deletes the dataverse whose ID is given:

        DELETE http://$SERVER/api/dataverses/$id?key=$apiKey

        """
        query_str = '/dataverses/{0}'.format(identifier)
        resp = self.make_delete_request(query_str)

        if resp.status_code == 404:
            print('Dataverse {0} was not found.'.format(identifier))
        elif resp.status_code == 200:
            print('{0} Dataverse has been deleted.'.format(identifier))
        else:
            print('{0} Dataverse could not be deleted.'.format(identifier))
        data = self.__get_request_return(resp, return_data_type)
        return data

    def get_dataset(self, identifier, is_doi=True,
                    return_data_type='json_as_dict'):
        """Get JSON representation of a dataset.

        With Dataverse identifier:
            GET http://$SERVER/api/datasets/$identifier
        With PID:
            GET http://$SERVER/api/datasets/:persistentId/?persistentId=$ID
            GET http://$SERVER/api/datasets/:persistentId/
            ?persistentId=doi:10.5072/FK2/J8SJZB
        """
        if is_doi:
            query_str = '/datasets/:persistentId/?persistentId={0}'.format(
                identifier)
        else:
            query_str = '/datasets/{0}'.format(identifier)
        resp = self.make_get_request(query_str)
        data = self.__get_request_return(resp, return_data_type)
        return data

    def get_dataset_export(self, export_format, identifier,
                           return_data_type='content'):
        """Get metadata of a dataset exported in different formats.

        CORS Export the metadata of the current published version of a dataset
        in various formats see Note below:

        Formats: 'ddi', 'oai_ddi', 'dcterms', 'oai_dc', 'schema.org',
            'dataverse_json'

        GET http://$SERVER/api/datasets/
        export?exporter=ddi&persistentId=$persistentId
        """
        query_str = '/datasets/export?exporter={0}&persistentId={1}'.format(
            export_format, identifier)
        resp = self.make_get_request(query_str)
        data = self.__get_request_return(resp, return_data_type)
        return data

    def get_dataset_files(self, doi, version='1',
                          return_data_type='json_as_dict'):
        # TODO: add passing of dataset and version as string
        """List files in a dataset.

        Lists all the file metadata, for the given dataset and version:

        doi = string

        http://guides.dataverse.org/en/latest/api/native-api.html#list-files-in-a-dataset
        GET http://$SERVER/api/datasets/$id/versions/$versionId/
        files?key=$apiKey

        dataset muss eine Dataset() Classe sein.
        """
        base_str = '/datasets/:persistentId/versions/'
        query_str = base_str+'{0}/files?persistentId={1}'.format(version, doi)
        resp = self.make_get_request(query_str)
        data = self.__get_request_return(resp, return_data_type)
        return data

    def get_datafile(self, identifier, format='original'):
        """Download a datafile.

        File ID
            GET /api/access/datafile/$id
        DOI
            GET http://$SERVER/api/access/datafile/
            :persistentId/?persistentId=doi:10.5072/FK2/J8SJZB
        """
        query_str = '/access/datafile/{0}'.format(identifier)
        resp = self.make_get_request(query_str)
        return resp

    def get_datafile_bundle(self, identifier):
        """Download a datafile in all its formats.

        GET /api/access/datafile/bundle/$id

        Data Access API calls can now be made using persistent identifiers (in
        addition to database ids). This is done by passing the constant
        :persistentId where the numeric id of the file is expected, and then
        passing the actual persistent id as a query parameter with the name
        persistentId.

        """
        query_str = '/access/datafile/bundle/{0}'.format(identifier)
        data = self.make_get_request(query_str)
        return data

    def get_info_version(self, return_data_type='json_as_dict'):
        """Get the Dataverse version and build number.

        The response contains the version and build numbers.

        Requires no api_token
        GET http://$SERVER/api/info/version
        """
        query_str = '/info/version'
        resp = self.make_get_request(query_str)
        data = self.__get_request_return(resp, return_data_type)
        return data

    def get_info_server(self, return_data_type='json_as_dict'):
        """Get Dataverse Server Name.

        This is useful when a Dataverse system is
        composed of multiple Java EE servers behind a load balancer.

        GET http://$SERVER/api/info/server
        """
        query_str = '/info/server'
        resp = self.make_get_request(query_str)
        data = self.__get_request_return(resp, return_data_type)
        return data

    def get_info_apiTermsOfUse(self, return_data_type='json_as_dict'):
        """Get API Terms of Use URL.

        The response contains the text value inserted as API Terms of use which
        uses the database setting :ApiTermsOfUse.

        GET http://$SERVER/api/info/apiTermsOfUse
        """
        query_str = '/info/apiTermsOfUse'
        resp = self.make_get_request(query_str)
        data = self.__get_request_return(resp, return_data_type)
        return data

    def get_metadatablocks(self, return_data_type='json_as_dict'):
        """Get info about all metadata blocks.

        Lists brief info about all metadata blocks registered in the system.

        GET http://$SERVER/api/metadatablocks
        """
        query_str = '/metadatablocks'
        resp = self.make_get_request(query_str)
        data = self.__get_request_return(resp, return_data_type)
        return data

    def get_metadatablock(self, identifier, return_data_type='json_as_dict'):
        """Get info about single metadata block.

        Returns data about the block whose identifier is passed. identifier can
        either be the block’s id, or its name.

        GET http://$SERVER/api/metadatablocks/$identifier
        """
        query_str = '/metadatablocks/{0}'.format(identifier)
        resp = self.make_get_request(query_str)
        data = self.__get_request_return(resp, return_data_type)
        return data
