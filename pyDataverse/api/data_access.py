from pyDataverse.api.api import Api, DEPRECATION_GUARD


class DataAccessApi(Api):
    """Class to access Dataverse's Data Access API.

    Attributes
    ----------
    base_url_api_data_access : type
        Description of attribute `base_url_api_data_access`.
    base_url : type
        Description of attribute `base_url`.

    """

    def __init__(self, base_url, api_token=None, *, auth=None):
        """Init an DataAccessApi() class."""
        super().__init__(base_url, api_token, auth=auth)
        if base_url:
            self.base_url_api_data_access = "{0}/access".format(self.base_url_api)
        else:
            self.base_url_api_data_access = self.base_url_api

    def get_datafile(
        self,
        identifier,
        data_format=None,
        no_var_header=None,
        image_thumb=None,
        is_pid=True,
        auth=DEPRECATION_GUARD,
    ):
        """Download a datafile via the Dataverse Data Access API.

        Get by file id (HTTP Request).

        .. code-block:: bash

            GET /api/access/datafile/$id

        Get by persistent identifier (HTTP Request).

        .. code-block:: bash

            GET http://$SERVER/api/access/datafile/:persistentId/?persistentId=doi:10.5072/FK2/J8SJZB

        Parameters
        ----------
        identifier : str
            Identifier of the datafile. Can be datafile id or persistent
            identifier of the datafile (e. g. doi).
        is_pid : bool
            ``True`` to use persistent identifier. ``False``, if not.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        is_first_param = True
        if is_pid:
            url = "{0}/datafile/:persistentId/?persistentId={1}".format(
                self.base_url_api_data_access, identifier
            )
        else:
            url = "{0}/datafile/{1}".format(self.base_url_api_data_access, identifier)
            if data_format or no_var_header or image_thumb:
                url += "?"
        if data_format:
            url += "format={0}".format(data_format)
            is_first_param = False
        if no_var_header:
            if not is_first_param:
                url += "&"
            url += "noVarHeader={0}".format(no_var_header)
            is_first_param = False
        if image_thumb:
            if not is_first_param:
                url += "&"
            url += "imageThumb={0}".format(image_thumb)
        return self.get_request(url, auth=auth)

    def get_datafiles(self, identifier, data_format=None, auth=DEPRECATION_GUARD):
        """Download a datafile via the Dataverse Data Access API.

        Get by file id (HTTP Request).

        .. code-block:: bash

            GET /api/access/datafiles/$id1,$id2,...$idN

        Get by persistent identifier (HTTP Request).

        Parameters
        ----------
        identifier : str
            Identifier of the dataset. Can be datafile id or persistent
            identifier of the datafile (e. g. doi).

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/datafiles/{1}".format(self.base_url_api_data_access, identifier)
        if data_format:
            url += "?format={0}".format(data_format)
        return self.get_request(url, auth=auth)

    def get_datafile_bundle(
        self, identifier, file_metadata_id=None, auth=DEPRECATION_GUARD
    ):
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
        identifier : str
            Identifier of the dataset.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        url = "{0}/datafile/bundle/{1}".format(
            self.base_url_api_data_access, identifier
        )
        if file_metadata_id:
            url += "?fileMetadataId={0}".format(file_metadata_id)
        return self.get_request(url, auth=auth)

    def request_access(self, identifier, auth=DEPRECATION_GUARD, is_filepid=False):
        """Request datafile access.

        This method requests access to the datafile whose id is passed on the behalf of an authenticated user whose key is passed. Note that not all datasets allow access requests to restricted files.

        https://guides.dataverse.org/en/4.18.1/api/dataaccess.html#request-access

        /api/access/datafile/$id/requestAccess

        curl -H "X-Dataverse-key:$API_TOKEN" -X PUT http://$SERVER/api/access/datafile/{id}/requestAccess
        """
        if is_filepid:
            url = "{0}/datafile/:persistentId/requestAccess?persistentId={1}".format(
                self.base_url_api_data_access, identifier
            )
        else:
            url = "{0}/datafile/{1}/requestAccess".format(
                self.base_url_api_data_access, identifier
            )
        return self.put_request(url, auth=auth)

    def allow_access_request(
        self, identifier, do_allow=True, auth=DEPRECATION_GUARD, is_pid=True
    ):
        """Allow access request for datafiles.

        https://guides.dataverse.org/en/latest/api/dataaccess.html#allow-access-requests

        curl -H "X-Dataverse-key:$API_TOKEN" -X PUT -d true http://$SERVER/api/access/{id}/allowAccessRequest
        curl -H "X-Dataverse-key:$API_TOKEN" -X PUT -d true http://$SERVER/api/access/:persistentId/allowAccessRequest?persistentId={pid}
        """
        if is_pid:
            url = "{0}/:persistentId/allowAccessRequest?persistentId={1}".format(
                self.base_url_api_data_access, identifier
            )
        else:
            url = "{0}/{1}/allowAccessRequest".format(
                self.base_url_api_data_access, identifier
            )

        if do_allow:
            data = "true"
        else:
            data = "false"
        return self.put_request(url, data=data, auth=auth)

    def grant_file_access(self, identifier, user, auth=DEPRECATION_GUARD):
        """Grant datafile access.

        https://guides.dataverse.org/en/4.18.1/api/dataaccess.html#grant-file-access

        curl -H "X-Dataverse-key:$API_TOKEN" -X PUT http://$SERVER/api/access/datafile/{id}/grantAccess/{@userIdentifier}
        """
        url = "{0}/datafile/{1}/grantAccess/{2}".format(
            self.base_url_api_data_access, identifier, user
        )
        return self.put_request(url, auth=auth)

    def list_file_access_requests(self, identifier, auth=DEPRECATION_GUARD):
        """Liste datafile access requests.

        https://guides.dataverse.org/en/4.18.1/api/dataaccess.html#list-file-access-requests

        curl -H "X-Dataverse-key:$API_TOKEN" -X GET http://$SERVER/api/access/datafile/{id}/listRequests
        """
        url = "{0}/datafile/{1}/listRequests".format(
            self.base_url_api_data_access, identifier
        )
        return self.get_request(url, auth=auth)
