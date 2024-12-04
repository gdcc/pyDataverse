import json
import subprocess as sp

from httpx import Response
from pydantic import computed_field

from pyDataverse.api.api import Api, DEPRECATION_GUARD
from pyDataverse.exceptions import (
    DataverseNotFoundError,
    OperationFailedError,
    ApiAuthorizationError,
    DataverseNotEmptyError,
    DatasetNotFoundError,
)


class NativeApi(Api):
    """Class to access Dataverse's Native API.

    Parameters
    ----------
    base_url : type
        Description of parameter `base_url`.
    api_token : type
        Description of parameter `api_token`.
    api_version : type
        Description of parameter `api_version`.

    Attributes
    ----------
    base_url_api_native : type
        Description of attribute `base_url_api_native`.
    base_url_api : type
        Description of attribute `base_url_api`.

    """

    @computed_field(return_type=str)
    def base_url_api_native(self):
        return self.base_url_api

    def get_dataverse(self, identifier, auth=DEPRECATION_GUARD):
        """Get dataverse metadata by alias or id.

        View metadata about a dataverse.

        .. code-block:: bash

            GET http://$SERVER/api/dataverses/$id

        Parameters
        ----------
        identifier : str
            Can either be a dataverse id (long), a dataverse alias (more
            robust), or the special value ``:root``.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/dataverses/{1}".format(self.base_url_api_native, identifier)
        return self.get_request(url, auth=auth)

    def create_dataverse(
        self, parent: str, metadata: str, auth: bool = True
    ) -> Response:
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
        parent : str
            Parent dataverse, to which the Dataverse gets attached to.
        metadata : str
            Metadata of the Dataverse.
        auth : bool
            True if api authorization is necessary. Defaults to ``True``.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        metadata_dict = json.loads(metadata)
        identifier = metadata_dict["alias"]
        url = "{0}/dataverses/{1}".format(self.base_url_api_native, parent)
        resp = self.post_request(url, metadata, auth)

        if resp.status_code == 404:
            error_msg = resp.json()["message"]
            raise DataverseNotFoundError(
                "ERROR: HTTP 404 - Dataverse {0} was not found. MSG: {1}".format(
                    parent, error_msg
                )
            )
        elif resp.status_code != 200 and resp.status_code != 201:
            error_msg = resp.json()["message"]
            raise OperationFailedError(
                "ERROR: HTTP {0} - Dataverse {1} could not be created. MSG: {2}".format(
                    resp.status_code, identifier, error_msg
                )
            )
        else:
            print("Dataverse {0} created.".format(identifier))
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
        identifier : str
            Can either be a dataverse id (long) or a dataverse alias (more
            robust).
        auth : bool
            True if api authorization is necessary. Defaults to ``False``.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/dataverses/{1}/actions/:publish".format(
            self.base_url_api_native, identifier
        )
        resp = self.post_request(url, auth=auth)

        if resp.status_code == 401:
            error_msg = resp.json()["message"]
            raise ApiAuthorizationError(
                "ERROR: HTTP 401 - Publish Dataverse {0} unauthorized. MSG: {1}".format(
                    identifier, error_msg
                )
            )
        elif resp.status_code == 404:
            error_msg = resp.json()["message"]
            raise DataverseNotFoundError(
                "ERROR: HTTP 404 - Dataverse {0} was not found. MSG: {1}".format(
                    identifier, error_msg
                )
            )
        elif resp.status_code != 200:
            error_msg = resp.json()["message"]
            raise OperationFailedError(
                "ERROR: HTTP {0} - Dataverse {1} could not be published. MSG: {2}".format(
                    resp.status_code, identifier, error_msg
                )
            )
        elif resp.status_code == 200:
            print("Dataverse {0} published.".format(identifier))
        return resp

    def delete_dataverse(self, identifier, auth=True):
        """Delete dataverse by alias or id.

        Status Code:
            200: Dataverse deleted

        Parameters
        ----------
        identifier : str
            Can either be a dataverse id (long) or a dataverse alias (more
            robust).

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/dataverses/{1}".format(self.base_url_api_native, identifier)
        resp = self.delete_request(url, auth)

        if resp.status_code == 401:
            error_msg = resp.json()["message"]
            raise ApiAuthorizationError(
                "ERROR: HTTP 401 - Delete Dataverse {0} unauthorized. MSG: {1}".format(
                    identifier, error_msg
                )
            )
        elif resp.status_code == 404:
            error_msg = resp.json()["message"]
            raise DataverseNotFoundError(
                "ERROR: HTTP 404 - Dataverse {0} was not found. MSG: {1}".format(
                    identifier, error_msg
                )
            )
        elif resp.status_code == 403:
            error_msg = resp.json()["message"]
            raise DataverseNotEmptyError(
                "ERROR: HTTP 403 - Dataverse {0} not empty. MSG: {1}".format(
                    identifier, error_msg
                )
            )
        elif resp.status_code != 200:
            error_msg = resp.json()["message"]
            raise OperationFailedError(
                "ERROR: HTTP {0} - Dataverse {1} could not be deleted. MSG: {2}".format(
                    resp.status_code, identifier, error_msg
                )
            )
        elif resp.status_code == 200:
            print("Dataverse {0} deleted.".format(identifier))
        return resp

    def get_dataverse_roles(self, identifier: str, auth: bool = False) -> Response:
        """All the roles defined directly in the dataverse by identifier.

        `Docs <https://guides.dataverse.org/en/latest/api/native-api.html#list-roles-defined-in-a-dataverse>`_

        .. code-block:: bash

            GET http://$SERVER/api/dataverses/$id/roles

        Parameters
        ----------
        identifier : str
            Can either be a dataverse id (long), a dataverse alias (more
            robust), or the special value ``:root``.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/dataverses/{1}/roles".format(self.base_url_api_native, identifier)
        return self.get_request(url, auth=auth)

    def get_dataverse_contents(self, identifier, auth=True):
        """Gets contents of Dataverse.

        Parameters
        ----------
        identifier : str
            Can either be a dataverse id (long), a dataverse alias (more
            robust), or the special value ``:root``.
        auth : bool
            Description of parameter `auth` (the default is False).

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/dataverses/{1}/contents".format(self.base_url_api_native, identifier)
        return self.get_request(url, auth=auth)

    def get_dataverse_assignments(self, identifier, auth=DEPRECATION_GUARD):
        """Get dataverse assignments by alias or id.

        View assignments of a dataverse.

        .. code-block:: bash

            GET http://$SERVER/api/dataverses/$id/assignments

        Parameters
        ----------
        identifier : str
            Can either be a dataverse id (long), a dataverse alias (more
            robust), or the special value ``:root``.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/dataverses/{1}/assignments".format(
            self.base_url_api_native, identifier
        )
        return self.get_request(url, auth=auth)

    def get_dataverse_facets(self, identifier, auth=DEPRECATION_GUARD):
        """Get dataverse facets by alias or id.

        View facets of a dataverse.

        .. code-block:: bash

            GET http://$SERVER/api/dataverses/$id/facets

        Parameters
        ----------
        identifier : str
            Can either be a dataverse id (long), a dataverse alias (more
            robust), or the special value ``:root``.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/dataverses/{1}/facets".format(self.base_url_api_native, identifier)
        return self.get_request(url, auth=auth)

    def dataverse_id2alias(self, dataverse_id, auth=DEPRECATION_GUARD):
        """Converts a Dataverse ID to an alias.

        Parameters
        ----------
        dataverse_id : str
            Dataverse ID.

        Returns
        -------
        str
            Dataverse alias

        """
        resp = self.get_dataverse(dataverse_id, auth=auth)
        if "data" in resp.json():
            if "alias" in resp.json()["data"]:
                return resp.json()["data"]["alias"]
        print("ERROR: Can not resolve Dataverse ID to alias.")
        return False

    def get_dataset(self, identifier, version=":latest", auth=True, is_pid=True):
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
        identifier : str
            Identifier of the dataset. Can be a Dataverse identifier or a
            persistent identifier (e.g. ``doi:10.11587/8H3N93``).
        is_pid : bool
            True, if identifier is a persistent identifier.
        version : str
            Version to be retrieved:
            ``:latest-published``: the latest published version
            ``:latest``: either a draft (if exists) or the latest published version.
            ``:draft``: the draft version, if any
            ``x.y``: x.y a specific version, where x is the major version number and y is the minor version number.
            ``x``: same as x.0

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        if is_pid:
            # TODO: Add version to query http://guides.dataverse.org/en/4.18.1/api/native-api.html#get-json-representation-of-a-dataset
            url = "{0}/datasets/:persistentId/?persistentId={1}".format(
                self.base_url_api_native, identifier
            )
        else:
            url = "{0}/datasets/{1}".format(self.base_url_api_native, identifier)
            # CHECK: Its not really clear, if the version query can also be done via ID.
        return self.get_request(url, auth=auth)

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
        identifier : str
            Identifier of the dataset. Can be a Dataverse identifier or a
            persistent identifier (e.g. ``doi:10.11587/8H3N93``).
        is_pid : bool
            True, if identifier is a persistent identifier.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        if is_pid:
            url = "{0}/datasets/:persistentId/versions?persistentId={1}".format(
                self.base_url_api_native, identifier
            )
        else:
            url = "{0}/datasets/{1}/versions".format(
                self.base_url_api_native, identifier
            )
        return self.get_request(url, auth=auth)

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
        identifier : str
            Identifier of the dataset. Can be a Dataverse identifier or a
            persistent identifier (e.g. ``doi:10.11587/8H3N93``).
        version : str
            Version string of the Dataset.
        is_pid : bool
            True, if identifier is a persistent identifier.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        if is_pid:
            url = "{0}/datasets/:persistentId/versions/{1}?persistentId={2}".format(
                self.base_url_api_native, version, identifier
            )
        else:
            url = "{0}/datasets/{1}/versions/{2}".format(
                self.base_url_api_native, identifier, version
            )
        return self.get_request(url, auth=auth)

    def get_dataset_export(self, pid, export_format, auth=DEPRECATION_GUARD):
        """Get metadata of dataset exported in different formats.

        Export the metadata of the current published version of a dataset
        in various formats by its persistend identifier.

        .. code-block:: bash

            GET http://$SERVER/api/datasets/export?exporter=$exportformat&persistentId=$pid

        Parameters
        ----------
        pid : str
            Persistent identifier of the dataset. (e.g. ``doi:10.11587/8H3N93``).
        export_format : str
            Export format as a string. Formats: ``ddi``, ``oai_ddi``,
            ``dcterms``, ``oai_dc``, ``schema.org``, ``dataverse_json``.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/datasets/export?exporter={1}&persistentId={2}".format(
            self.base_url_api_native, export_format, pid
        )
        return self.get_request(url, auth=auth)

    def create_dataset(self, dataverse, metadata, pid=None, publish=False, auth=True):
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
        "root") or the database id of the dataverse (e.g. "1"). The initial
        version state will be set to "DRAFT":

        Status Code:
            201: dataset created

        Import Dataset with existing PID:
        `<http://guides.dataverse.org/en/latest/api/native-api.html#import-a-dataset-into-a-dataverse>`_
        To import a dataset with an existing persistent identifier (PID), the
        dataset’s metadata should be prepared in Dataverse’s native JSON format. The
        PID is provided as a parameter at the URL. The following line imports a
        dataset with the PID PERSISTENT_IDENTIFIER to Dataverse, and then releases it:

        The pid parameter holds a persistent identifier (such as a DOI or Handle). The import will fail if no PID is provided, or if the provided PID fails validation.

        The optional release parameter tells Dataverse to immediately publish the
        dataset. If the parameter is changed to no, the imported dataset will
        remain in DRAFT status.

        Parameters
        ----------
        dataverse : str
            "alias" of the dataverse (e.g. ``root``) or the database id of the
            dataverse (e.g. ``1``)
        pid : str
            PID of existing Dataset.
        publish : bool
            Publish only works when a Dataset with an existing PID is created. If it
            is ``True``, Dataset should be instantly published, ``False``
            if a Draft should be created.
        metadata : str
            Metadata of the Dataset as a json-formatted string (e. g.
            `dataset-finch1.json <http://guides.dataverse.org/en/latest/_downloads/dataset-finch1.json>`_)

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        if pid:
            assert isinstance(pid, str)
            url = "{0}/dataverses/{1}/datasets/:import?pid={2}".format(
                self.base_url_api_native, dataverse, pid
            )
            if publish:
                url += "&release=yes"
            else:
                url += "&release=no"
        else:
            url = "{0}/dataverses/{1}/datasets".format(
                self.base_url_api_native, dataverse
            )
        resp = self.post_request(url, metadata, auth)

        if resp.status_code == 404:
            error_msg = resp.json()["message"]
            raise DataverseNotFoundError(
                "ERROR: HTTP 404 - Dataverse {0} was not found. MSG: {1}".format(
                    dataverse, error_msg
                )
            )
        elif resp.status_code == 401:
            error_msg = resp.json()["message"]
            raise ApiAuthorizationError(
                "ERROR: HTTP 401 - Create Dataset unauthorized. MSG: {0}".format(
                    error_msg
                )
            )
        elif resp.status_code == 201:
            if "data" in resp.json():
                if "persistentId" in resp.json()["data"]:
                    identifier = resp.json()["data"]["persistentId"]
                    print("Dataset with pid '{0}' created.".format(identifier))
                elif "id" in resp.json()["data"]:
                    identifier = resp.json()["data"]["id"]
                    print("Dataset with id '{0}' created.".format(identifier))
                else:
                    print("ERROR: No identifier returned for created Dataset.")
        return resp

    def edit_dataset_metadata(
        self, identifier, metadata, is_pid=True, replace=False, auth=True
    ):
        """Edit metadata of a given dataset.

        `edit-dataset-metadata <http://guides.dataverse.org/en/latest/api/native-api.html#edit-dataset-metadata>`_.

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
        identifier : str
            Identifier of the dataset. Can be a Dataverse identifier or a
            persistent identifier (e.g. ``doi:10.11587/8H3N93``).
        metadata : str
            Metadata of the Dataset as a json-formatted string.
        is_pid : bool
            ``True`` to use persistent identifier. ``False``, if not.
        replace : bool
            ``True`` to replace already existing metadata. ``False``, if not.
        auth : bool
            ``True``, if an api token should be sent. Defaults to ``False``.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        Examples
        -------
        Get dataset metadata::

            >>> data = api.get_dataset(doi).json()["data"]["latestVersion"]["metadataBlocks"]["citation"]
            >>> resp = api.edit_dataset_metadata(doi, data, is_replace=True, auth=True)
            >>> resp.status_code
            200: metadata updated

        """
        if is_pid:
            url = "{0}/datasets/:persistentId/editMetadata/?persistentId={1}".format(
                self.base_url_api_native, identifier
            )
        else:
            url = "{0}/datasets/editMetadata/{1}".format(
                self.base_url_api_native, identifier
            )
        params = {"replace": True} if replace else {}
        resp = self.put_request(url, metadata, auth, params)

        if resp.status_code == 401:
            error_msg = resp.json()["message"]
            raise ApiAuthorizationError(
                "ERROR: HTTP 401 - Updating metadata unauthorized. MSG: {0}".format(
                    error_msg
                )
            )
        elif resp.status_code == 400:
            if "Error parsing" in resp.json()["message"]:
                print("Wrong passed data format.")
            else:
                print(
                    "You may not add data to a field that already has data and does not"
                    " allow multiples. Use is_replace=true to replace existing data."
                )
        elif resp.status_code == 200:
            print("Dataset '{0}' updated".format(identifier))
        return resp

    def create_dataset_private_url(self, identifier, is_pid=True, auth=True):
        """Create private Dataset URL.

        POST http://$SERVER/api/datasets/$id/privateUrl?key=$apiKey


        http://guides.dataverse.org/en/4.16/api/native-api.html#create-a-private-url-for-a-dataset
                'MSG: {1}'.format(pid, error_msg))

        """
        if is_pid:
            url = "{0}/datasets/:persistentId/privateUrl/?persistentId={1}".format(
                self.base_url_api_native, identifier
            )
        else:
            url = "{0}/datasets/{1}/privateUrl".format(
                self.base_url_api_native, identifier
            )

        resp = self.post_request(url, auth=auth)

        if resp.status_code == 200:
            print(
                "Dataset private URL created: {0}".format(resp.json()["data"]["link"])
            )
        return resp

    def get_dataset_private_url(self, identifier, is_pid=True, auth=True):
        """Get private Dataset URL.

        GET http://$SERVER/api/datasets/$id/privateUrl?key=$apiKey

        http://guides.dataverse.org/en/4.16/api/native-api.html#get-the-private-url-for-a-dataset

        """
        if is_pid:
            url = "{0}/datasets/:persistentId/privateUrl/?persistentId={1}".format(
                self.base_url_api_native, identifier
            )
        else:
            url = "{0}/datasets/{1}/privateUrl".format(
                self.base_url_api_native, identifier
            )

        resp = self.get_request(url, auth=auth)

        if resp.status_code == 200:
            print("Got Dataset private URL: {0}".format(resp.json()["data"]["link"]))
        return resp

    def delete_dataset_private_url(self, identifier, is_pid=True, auth=True):
        """Get private Dataset URL.

        DELETE http://$SERVER/api/datasets/$id/privateUrl?key=$apiKey

        http://guides.dataverse.org/en/4.16/api/native-api.html#delete-the-private-url-from-a-dataset

        """
        if is_pid:
            url = "{0}/datasets/:persistentId/privateUrl/?persistentId={1}".format(
                self.base_url_api_native, identifier
            )
        else:
            url = "{0}/datasets/{1}/privateUrl".format(
                self.base_url_api_native, identifier
            )

        resp = self.delete_request(url, auth=auth)

        if resp.status_code == 200:
            print("Got Dataset private URL: {0}".format(resp.json()["data"]["link"]))
        return resp

    def publish_dataset(self, pid, release_type="minor", auth=True):
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
        pid : str
            Persistent identifier of the dataset (e.g.
            ``doi:10.11587/8H3N93``).
        release_type : str
            Passing ``minor`` increases the minor version number (2.3 is
            updated to 2.4). Passing ``major`` increases the major version
            number (2.3 is updated to 3.0). Superusers can pass
            ``updatecurrent`` to update metadata without changing the version
            number.
        auth : bool
            ``True`` if api authorization is necessary. Defaults to ``False``.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/datasets/:persistentId/actions/:publish".format(
            self.base_url_api_native
        )
        url += "?persistentId={0}&type={1}".format(pid, release_type)
        resp = self.post_request(url, auth=auth)

        if resp.status_code == 404:
            error_msg = resp.json()["message"]
            raise DatasetNotFoundError(
                "ERROR: HTTP 404 - Dataset {0} was not found. MSG: {1}".format(
                    pid, error_msg
                )
            )
        elif resp.status_code == 401:
            error_msg = resp.json()["message"]
            raise ApiAuthorizationError(
                "ERROR: HTTP 401 - User not allowed to publish dataset {0}. "
                "MSG: {1}".format(pid, error_msg)
            )
        elif resp.status_code == 200:
            print("Dataset {0} published".format(pid))
        return resp

    def get_dataset_lock(self, pid):
        """Get if dataset is locked.

        The lock API endpoint was introduced in Dataverse 4.9.3.

        Parameters
        ----------
        pid : str
            Persistent identifier of the Dataset (e.g.
            ``doi:10.11587/8H3N93``).

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/datasets/:persistentId/locks/?persistentId={1}".format(
            self.base_url_api_native, pid
        )
        return self.get_request(url, auth=True)

    def get_dataset_assignments(self, identifier, is_pid=True, auth=True):
        """Get Dataset assignments.

        GET http://$SERVER/api/datasets/$id/assignments?key=$apiKey


        """
        if is_pid:
            url = "{0}/datasets/:persistentId/assignments/?persistentId={1}".format(
                self.base_url_api_native, identifier
            )
        else:
            url = "{0}/datasets/{1}/assignments".format(
                self.base_url_api_native, identifier
            )
        return self.get_request(url, auth=auth)

    def delete_dataset(self, identifier, is_pid=True, auth=True):
        """Delete a dataset.

        Delete the dataset whose id is passed

        Status Code:
            200: dataset deleted

        Parameters
        ----------
        identifier : str
            Identifier of the dataset. Can be a Dataverse identifier or a
            persistent identifier (e.g. ``doi:10.11587/8H3N93``).
        is_pid : bool
            True, if identifier is a persistent identifier.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        if is_pid:
            url = "{0}/datasets/:persistentId/?persistentId={1}".format(
                self.base_url_api_native, identifier
            )
        else:
            url = "{0}/datasets/{1}".format(self.base_url_api_native, identifier)
        resp = self.delete_request(url, auth=auth)

        if resp.status_code == 404:
            error_msg = resp.json()["message"]
            raise DatasetNotFoundError(
                "ERROR: HTTP 404 - Dataset '{0}' was not found. MSG: {1}".format(
                    identifier, error_msg
                )
            )
        elif resp.status_code == 405:
            error_msg = resp.json()["message"]
            raise OperationFailedError(
                "ERROR: HTTP 405 - "
                "Published datasets can only be deleted from the GUI. For "
                "more information, please refer to "
                "https://github.com/IQSS/dataverse/issues/778"
                " MSG: {0}".format(error_msg)
            )
        elif resp.status_code == 401:
            error_msg = resp.json()["message"]
            raise ApiAuthorizationError(
                "ERROR: HTTP 401 - User not allowed to delete dataset '{0}'. "
                "MSG: {1}".format(identifier, error_msg)
            )
        elif resp.status_code == 200:
            print("Dataset '{0}' deleted.".format(identifier))
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
            url = "{0}/datasets/:persistentId/destroy/?persistentId={1}".format(
                self.base_url_api_native, identifier
            )
        else:
            url = "{0}/datasets/{1}/destroy".format(
                self.base_url_api_native, identifier
            )

        resp = self.delete_request(url, auth=auth)

        if resp.status_code == 200:
            print("Dataset {0} destroyed".format(resp.json()))
        return resp

    def get_datafiles_metadata(self, pid, version=":latest", auth=True):
        """List metadata of all datafiles of a dataset.

        `Documentation <http://guides.dataverse.org/en/latest/api/native-api.html#list-files-in-a-dataset>`_

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/datasets/$id/versions/$versionId/files

        Parameters
        ----------
        pid : str
            Persistent identifier of the dataset. e.g. ``doi:10.11587/8H3N93``.
        version : str
            Version of dataset. Defaults to `1`.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        base_str = "{0}/datasets/:persistentId/versions/".format(
            self.base_url_api_native
        )
        url = base_str + "{0}/files?persistentId={1}".format(version, pid)
        return self.get_request(url, auth=auth)

    def get_datafile_metadata(
        self, identifier, is_filepid=False, is_draft=False, auth=True
    ):
        """
        GET http://$SERVER/api/files/{id}/metadata

        curl $SERVER_URL/api/files/$ID/metadata
        curl "$SERVER_URL/api/files/:persistentId/metadata?persistentId=$PERSISTENT_ID"
        curl "https://demo.dataverse.org/api/files/:persistentId/metadata?persistentId=doi:10.5072/FK2/AAA000"
        curl -H "X-Dataverse-key:$API_TOKEN" $SERVER_URL/api/files/$ID/metadata/draft

        """
        if is_filepid:
            url = "{0}/files/:persistentId/metadata".format(self.base_url_api_native)
            if is_draft:
                url += "/draft"
            url += "?persistentId={0}".format(identifier)
        else:
            url = "{0}/files/{1}/metadata".format(self.base_url_api_native, identifier)
            if is_draft:
                url += "/draft"
            # CHECK: Its not really clear, if the version query can also be done via ID.
        return self.get_request(url, auth=auth)

    def upload_datafile(self, identifier, filename, json_str=None, is_pid=True):
        """Add file to a dataset.

        Add a file to an existing Dataset. Description and tags are optional:

        HTTP Request:

        .. code-block:: bash

            POST http://$SERVER/api/datasets/$id/add

        The upload endpoint checks the content of the file, compares it with
        existing files and tells if already in the database (most likely via
        hashing).

        `adding-files <http://guides.dataverse.org/en/latest/api/native-api.html#adding-files>`_.

        Parameters
        ----------
        identifier : str
            Identifier of the dataset.
        filename : str
            Full filename with path.
        json_str : str
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
            url += "/datasets/:persistentId/add?persistentId={0}".format(identifier)
        else:
            url += "/datasets/{0}/add".format(identifier)

        files = {"file": open(filename, "rb")}
        metadata = {}
        if json_str is not None:
            metadata["jsonData"] = json_str
        return self.post_request(url, data=metadata, files=files, auth=True)

    def update_datafile_metadata(self, identifier, json_str=None, is_filepid=False):
        """Update datafile metadata.

        metadata such as description, directoryLabel (File Path) and tags are not carried over from the file being replaced:
        Updates the file metadata for an existing file where ID is the
        database id of the file to update or PERSISTENT_ID is the persistent id
        (DOI or Handle) of the file. Requires a jsonString expressing the new
        metadata. No metadata from the previous version of this file will be
        persisted, so if you want to update a specific field first get the
        json with the above command and alter the fields you want.


        Also note that dataFileTags are not versioned and changes to these will update the published version of the file.

        This functions needs CURL to work!

        HTTP Request:

        .. code-block:: bash

            POST -F 'file=@file.extension' -F 'jsonData={json}' http://$SERVER/api/files/{id}/metadata?key={apiKey}
            curl -H "X-Dataverse-key:$API_TOKEN" -X POST -F 'jsonData={"description":"My description bbb.","provFreeform":"Test prov freeform","categories":["Data"],"restrict":false}' $SERVER_URL/api/files/$ID/metadata
            curl -H "X-Dataverse-key:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -X POST -F 'jsonData={"description":"My description bbb.","provFreeform":"Test prov freeform","categories":["Data"],"restrict":false}' "https://demo.dataverse.org/api/files/:persistentId/metadata?persistentId=doi:10.5072/FK2/AAA000"

        `Docs <http://guides.dataverse.org/en/latest/api/native-api.html#updating-file-metadata>`_.

        Parameters
        ----------
        identifier : str
            Identifier of the dataset.
        json_str : str
            Metadata as JSON string.
        is_filepid : bool
            ``True`` to use persistent identifier for datafile. ``False``, if
            not.

        Returns
        -------
        dict
            The json string responded by the CURL request, converted to a
            dict().

        """
        # if is_filepid:
        #     url = '{0}/files/:persistentId/metadata?persistentId={1}'.format(
        #         self.base_url_api_native, identifier)
        # else:
        #     url = '{0}/files/{1}/metadata'.format(self.base_url_api_native, identifier)
        #
        # data = {'jsonData': json_str}
        # resp = self.post_request(
        #     url,
        #     data=data,
        #     auth=True
        #     )
        query_str = self.base_url_api_native
        if is_filepid:
            query_str = "{0}/files/:persistentId/metadata?persistentId={1}".format(
                self.base_url_api_native, identifier
            )
        else:
            query_str = "{0}/files/{1}/metadata".format(
                self.base_url_api_native, identifier
            )
        shell_command = 'curl -H "X-Dataverse-key: {0}"'.format(self.api_token)
        shell_command += " -X POST -F 'jsonData={0}' {1}".format(json_str, query_str)
        # TODO(Shell): is shell=True necessary?
        return sp.run(shell_command, shell=True, stdout=sp.PIPE)

    def replace_datafile(self, identifier, filename, json_str, is_filepid=True):
        """Replace datafile.

        HTTP Request:

        .. code-block:: bash

            POST -F 'file=@file.extension' -F 'jsonData={json}' http://$SERVER/api/files/{id}/replace?key={apiKey}

        `replacing-files <http://guides.dataverse.org/en/latest/api/native-api.html#replacing-files>`_.

        Parameters
        ----------
        identifier : str
            Identifier of the file to be replaced.
        filename : str
            Full filename with path.
        json_str : str
            Metadata as JSON string.
        is_filepid : bool
            ``True`` if ``identifier`` is a persistent identifier for the datafile.
            ``False``, if not.

        Returns
        -------
        dict
            The json string responded by the CURL request, converted to a
            dict().

        """
        url = self.base_url_api_native
        files = {"file": open(filename, "rb")}
        data = {"jsonData": json_str}

        if is_filepid:
            url += "/files/:persistentId/replace?persistentId={0}".format(identifier)
        else:
            url += "/files/{0}/replace".format(identifier)
        return self.post_request(url, data=data, files=files, auth=True)

    def get_info_version(self, auth=DEPRECATION_GUARD):
        """Get the Dataverse version and build number.

        The response contains the version and build numbers. Requires no api
        token.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/info/version

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/info/version".format(self.base_url_api_native)
        return self.get_request(url, auth=auth)

    def get_info_server(self, auth=DEPRECATION_GUARD):
        """Get dataverse server name.

        This is useful when a Dataverse system is composed of multiple Java EE
        servers behind a load balancer.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/info/server

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/info/server".format(self.base_url_api_native)
        return self.get_request(url, auth=auth)

    def get_info_api_terms_of_use(self, auth=DEPRECATION_GUARD):
        """Get API Terms of Use url.

        The response contains the text value inserted as API Terms of use which
        uses the database setting :ApiTermsOfUse.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/info/apiTermsOfUse

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/info/apiTermsOfUse".format(self.base_url_api_native)
        return self.get_request(url, auth=auth)

    def get_metadatablocks(self, auth=DEPRECATION_GUARD):
        """Get info about all metadata blocks.

        Lists brief info about all metadata blocks registered in the system.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/metadatablocks

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/metadatablocks".format(self.base_url_api_native)
        return self.get_request(url, auth=auth)

    def get_metadatablock(self, identifier, auth=DEPRECATION_GUARD):
        """Get info about single metadata block.

        Returns data about the block whose identifier is passed. identifier can
        either be the block’s id, or its name.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/metadatablocks/$identifier

        Parameters
        ----------
        identifier : str
            Can be block's id, or it's name.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/metadatablocks/{1}".format(self.base_url_api_native, identifier)
        return self.get_request(url, auth=auth)

    def get_user_api_token_expiration_date(self, auth=DEPRECATION_GUARD):
        """Get the expiration date of an Users's API token.

        HTTP Request:

        .. code-block:: bash

            curl -H X-Dataverse-key:$API_TOKEN -X GET $SERVER_URL/api/users/token

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/users/token".format(self.base_url_api_native)
        return self.get_request(url, auth=auth)

    def recreate_user_api_token(self):
        """Recreate an Users API token.

        HTTP Request:

        .. code-block:: bash

            curl -H X-Dataverse-key:$API_TOKEN -X POST $SERVER_URL/api/users/token/recreate

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/users/token/recreate".format(self.base_url_api_native)
        return self.post_request(url)

    def delete_user_api_token(self):
        """Delete an Users API token.

        HTTP Request:

        .. code-block:: bash

            curl -H X-Dataverse-key:$API_TOKEN -X POST $SERVER_URL/api/users/token/recreate

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/users/token".format(self.base_url_api_native)
        return self.delete_request(url)

    def create_role(self, dataverse_id):
        """Create a new role.

        `Docs <https://guides.dataverse.org/en/latest/api/native-api.html#id2>`_

        HTTP Request:

        .. code-block:: bash

            POST http://$SERVER/api/roles?dvo=$dataverseIdtf&key=$apiKey

        Parameters
        ----------
        dataverse_id : str
            Can be alias or id of a Dataverse.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/roles?dvo={1}".format(self.base_url_api_native, dataverse_id)
        return self.post_request(url)

    def show_role(self, role_id, auth=DEPRECATION_GUARD):
        """Show role.

        `Docs <https://guides.dataverse.org/en/latest/api/native-api.html#show-role>`_

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/roles/$id

        Parameters
        ----------
        identifier : str
            Can be alias or id of a Dataverse.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/roles/{1}".format(self.base_url_api_native, role_id)
        return self.get_request(url, auth=auth)

    def delete_role(self, role_id):
        """Delete role.

        `Docs <https://guides.dataverse.org/en/latest/api/native-api.html#delete-role>`_

        Parameters
        ----------
        identifier : str
            Can be alias or id of a Dataverse.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/roles/{1}".format(self.base_url_api_native, role_id)
        return self.delete_request(url)

    def get_children(
        self, parent=":root", parent_type="dataverse", children_types=None, auth=True
    ):
        """Walk through children of parent element in Dataverse tree.

        Default: gets all child dataverses if parent = dataverse or all

        Example Dataverse Tree:

        .. code-block:: bash

            data = {
                'type': 'dataverse',
                'dataverse_id': 1,
                'dataverse_alias': ':root',
                'children': [
                    {
                        'type': 'datasets',
                        'dataset_id': 231,
                        'pid': 'doi:10.11587/LYFDYC',
                        'children': [
                            {
                                'type': 'datafile'
                                'datafile_id': 532,
                                'pid': 'doi:10.11587/LYFDYC/C2WTRN',
                                'filename': '10082_curation.pdf '
                            }
                        ]
                    }
                ]
            }

        Parameters
        ----------
        parent : str
            Description of parameter `parent`.
        parent_type : str
            Description of parameter `parent_type`.
        children_types : list
            Types of children to be collected. 'dataverses', 'datasets' and 'datafiles' are valid list items.
        auth : bool
            Authentication needed

        Returns
        -------
        list
            List of Dataverse data type dictionaries. Different ones for
            Dataverses, Datasets and Datafiles.

        # TODO
        - differentiate between published and unpublished data types
        - util function to read out all dataverses into a list
        - util function to read out all datasets into a list
        - util function to read out all datafiles into a list
        - Unify tree and models

        """
        children = []

        if children_types is None:
            children_types = []

        if len(children_types) == 0:
            if parent_type == "dataverse":
                children_types = ["dataverses"]
            elif parent_type == "dataset":
                children_types = ["datafiles"]

        if (
            "dataverses" in children_types
            and "datafiles" in children_types
            and "datasets" not in children_types
        ):
            print(
                "ERROR: Wrong children_types passed: 'dataverses' and 'datafiles'"
                " passed, 'datasets' missing."
            )
            return False

        if parent_type == "dataverse":
            # check for dataverses and datasets as children and get their ID
            parent_alias = parent
            resp = self.get_dataverse_contents(parent_alias, auth=auth)
            if "data" in resp.json():
                contents = resp.json()["data"]
                for content in contents:
                    if (
                        content["type"] == "dataverse"
                        and "dataverses" in children_types
                    ):
                        dataverse_id = content["id"]
                        child_alias = self.dataverse_id2alias(dataverse_id, auth=auth)
                        children.append(
                            {
                                "dataverse_id": dataverse_id,
                                "title": content["title"],
                                "dataverse_alias": child_alias,
                                "type": "dataverse",
                                "children": self.get_children(
                                    parent=child_alias,
                                    parent_type="dataverse",
                                    children_types=children_types,
                                    auth=auth,
                                ),
                            }
                        )
                    elif content["type"] == "dataset" and "datasets" in children_types:
                        pid = (
                            content["protocol"]
                            + ":"
                            + content["authority"]
                            + "/"
                            + content["identifier"]
                        )
                        children.append(
                            {
                                "dataset_id": content["id"],
                                "pid": pid,
                                "type": "dataset",
                                "children": self.get_children(
                                    parent=pid,
                                    parent_type="dataset",
                                    children_types=children_types,
                                    auth=auth,
                                ),
                            }
                        )
            else:
                print("ERROR: 'get_dataverse_contents()' API request not working.")
        elif parent_type == "dataset" and "datafiles" in children_types:
            # check for datafiles as children and get their ID
            pid = parent
            resp = self.get_datafiles_metadata(parent, version=":latest")
            if "data" in resp.json():
                for datafile in resp.json()["data"]:
                    children.append(
                        {
                            "datafile_id": datafile["dataFile"]["id"],
                            "filename": datafile["dataFile"]["filename"],
                            "label": datafile["label"],
                            "pid": datafile["dataFile"]["persistentId"],
                            "type": "datafile",
                        }
                    )
            else:
                print("ERROR: 'get_datafiles()' API request not working.")
        return children

    def get_user(self):
        """Get details of the current authenticated user.

        Auth must be ``true`` for this to work. API endpoint is available for Dataverse >= 5.3.

        https://guides.dataverse.org/en/latest/api/native-api.html#get-user-information-in-json-format
        """
        url = f"{self.base_url}/users/:me"
        return self.get_request(url, auth=True)

    def redetect_file_type(
        self, identifier: str, is_pid: bool = False, dry_run: bool = False
    ) -> Response:
        """Redetect file type.

        https://guides.dataverse.org/en/latest/api/native-api.html#redetect-file-type

        Parameters
        ----------
        identifier : str
            Datafile id (fileid) or file PID.
        is_pid : bool
            Is the identifier a PID, by default False.
        dry_run : bool, optional
            [description], by default False

        Returns
        -------
        Response
            Request Response() object.
        """
        if dry_run is True:
            dry_run_str = "true"
        elif dry_run is False:
            dry_run_str = "false"
        if is_pid:
            url = f"{self.base_url_api_native}/files/:persistentId/redetect?persistentId={identifier}&dryRun={dry_run_str}"
        else:
            url = f"{self.base_url_api_native}/files/{identifier}/redetect?dryRun={dry_run_str}"
        return self.post_request(url, auth=True)

    def reingest_datafile(self, identifier: str, is_pid: bool = False) -> Response:
        """Reingest datafile.

        https://guides.dataverse.org/en/latest/api/native-api.html#reingest-a-file

        Parameters
        ----------
        identifier : str
            Datafile id (fileid) or file PID.
        is_pid : bool
            Is the identifier a PID, by default False.

        Returns
        -------
        Response
            Request Response() object.
        """
        if is_pid:
            url = f"{self.base_url_api_native}/files/:persistentId/reingest?persistentId={identifier}"
        else:
            url = f"{self.base_url_api_native}/files/{identifier}/reingest"
        return self.post_request(url, auth=True)

    def uningest_datafile(self, identifier: str, is_pid: bool = False) -> Response:
        """Uningest datafile.

        https://guides.dataverse.org/en/latest/api/native-api.html#uningest-a-file

        Parameters
        ----------
        identifier : str
            Datafile id (fileid) or file PID.
        is_pid : bool
            Is the identifier a PID, by default False.

        Returns
        -------
        Response
            Request Response() object.
        """
        if is_pid:
            url = f"{self.base_url_api_native}/files/:persistentId/uningest?persistentId={identifier}"
        else:
            url = f"{self.base_url_api_native}/files/{identifier}/uningest"
        return self.post_request(url, auth=True)

    def restrict_datafile(self, identifier: str, is_pid: bool = False) -> Response:
        """Uningest datafile.

        https://guides.dataverse.org/en/latest/api/native-api.html#restrict-files

        Parameters
        ----------
        identifier : str
            Datafile id (fileid) or file PID.
        is_pid : bool
            Is the identifier a PID, by default False.

        Returns
        -------
        Response
            Request Response() object.
        """
        if is_pid:
            url = f"{self.base_url_api_native}/files/:persistentId/restrict?persistentId={identifier}"
        else:
            url = f"{self.base_url_api_native}/files/{identifier}/restrict"
        return self.put_request(url, auth=True)
