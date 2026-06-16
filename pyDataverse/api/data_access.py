from contextlib import contextmanager
from typing import (
    Any,
    Generator,
    List,
    Literal,
    Optional,
    Sequence,
    Union,
    overload,
)
from urllib.parse import urljoin

import httpx
from pydantic import computed_field

from ..models import message
from ..models.file import access
from .api import Api


class DataAccessApi(Api):
    """Class to access Dataverse's Data Access API.

    This class provides methods to download datafiles, request access to restricted files,
    and manage file access permissions through the Dataverse Data Access API.

    Attributes:
        base_url_api_data_access: Description of attribute `base_url_api_data_access`.
        base_url: Description of attribute `base_url`.
    """

    @computed_field(return_type=str)
    def api_base_url(self):
        return urljoin(self.base_url, "api/access/")

    def get_datafile(
        self,
        identifier: Union[str, int],
        data_format: Optional[str] = None,
        no_var_header: Optional[bool] = None,
        image_thumb: Optional[bool] = None,
    ) -> bytes:
        """
        Download a datafile via the Dataverse Data Access API.

        This method retrieves a datafile using either its database identifier or a persistent
        identifier (PID). If a PID (such as a DOI) is provided, the API handles constructing
        the correct endpoint and query parameters.

        Args:
            identifier (Union[str, int]): The identifier for the datafile. Can be the numeric
                datafile database ID or a persistent identifier (such as a DOI).
            data_format (Optional[str], default=None): Format conversion for the downloaded data
                (e.g., 'original', 'bundle', 'tabular', etc.), if supported by the Dataverse API.
            no_var_header (Optional[bool], default=None): Whether to exclude variable header in
                tabular data format. Pass True to remove the variable header.
            image_thumb (Optional[bool], default=None): Whether to request an image thumbnail
                instead of the full image. Pass True for thumbnail.

        Returns:
            httpx.Response: The HTTP response object containing the datafile content.

        Raises:
            httpx.HTTPError: If the request fails for network or HTTP reasons.

        Example:
            >>> api = DataAccessApi(base_url="https://demo.dataverse.org/")
            >>> response = api.get_datafile(1234567)
            >>> with open("out.dat", "wb") as f:
            ...     f.write(response.content)
        """
        return self._get_datafile_core(
            identifier,
            data_format=data_format,
            no_var_header=no_var_header,
            image_thumb=image_thumb,
            follow_redirects=True,
        )

    def get_datafile_download_url(
        self,
        identifier: Union[str, int],
        data_format: Optional[str] = None,
        no_var_header: Optional[bool] = None,
        image_thumb: Optional[bool] = None,
    ) -> str:
        """
        Get the direct download URL for a datafile, with redirects disabled.

        This method returns the direct download URL as provided in the HTTP Location header
        after requesting the datafile from the Dataverse Data Access API. This is useful for
        workflows that need to follow or manage redirects manually (for example, in federated
        storage setups).

        Args:
            identifier (Union[str, int]): The identifier for the datafile. Can be the numeric
                datafile database ID or a persistent identifier (such as a DOI).
            data_format (Optional[str], default=None): Format conversion for the downloaded data,
                if supported by Dataverse for this type of file.
            no_var_header (Optional[bool], default=None): Whether to exclude variable header in
                tabular data format. Pass True to remove the variable header.
            image_thumb (Optional[bool], default=None): Whether to request an image thumbnail
                instead of the full image. Pass True for thumbnail.

        Returns:
            str: The direct download URL from the Location response header.

        Raises:
            AssertionError: If the Location header is not found in the response.
            httpx.HTTPError: If the request fails for network or HTTP reasons.

        Example:
            >>> api = DataAccessApi(base_url="https://demo.dataverse.org/")
            >>> download_url = api.get_datafile_download_url(1234567)
        """
        response = self._get_datafile_core(
            identifier,
            data_format=data_format,
            no_var_header=no_var_header,
            image_thumb=image_thumb,
            follow_redirects=False,
        )

        if not response.has_redirect_location:
            if self._is_pid(identifier):
                return self._assemble_url(
                    f"datafile/:persistentId?persistentId={identifier}"
                )
            else:
                return self._assemble_url(f"datafile/{identifier}")
        elif response.next_request is not None:
            return str(response.next_request.url)
        else:
            raise ValueError(
                "No redirect found in response for file download URL. This should actually never happen. Please open an issue on GitHub with the following information: {response.__dict__}"
            )

    @overload
    def _get_datafile_core(
        self,
        identifier: Union[str, int],
        follow_redirects: Literal[False],
        data_format: Optional[str] = None,
        no_var_header: Optional[bool] = None,
        image_thumb: Optional[bool] = None,
    ) -> httpx.Response:
        """
        Internal helper to issue a datafile download request to the Data Access API.
        """
        pass

    @overload
    def _get_datafile_core(
        self,
        identifier: Union[str, int],
        follow_redirects: Literal[True],
        data_format: Optional[str] = None,
        no_var_header: Optional[bool] = None,
        image_thumb: Optional[bool] = None,
    ) -> bytes:
        """
        Internal helper to issue a datafile download request to the Data Access API.
        """
        pass

    def _get_datafile_core(
        self,
        identifier: Union[str, int],
        follow_redirects: bool = True,
        data_format: Optional[str] = None,
        no_var_header: Optional[bool] = None,
        image_thumb: Optional[bool] = None,
    ) -> Union[bytes, httpx.Response]:
        """
        Internal helper to issue a datafile download request to the Data Access API.

        Constructs the proper API endpoint and request parameters for downloading a file
        by either database ID or persistent identifier, applying optional dataverse features.

        Args:
            identifier (Union[str, int]): The identifier for the datafile. Can be a database
                file ID (int) or persistent identifier (str, e.g. a DOI).
            data_format (Optional[str], default=None): Optional format for the downloaded data.
            no_var_header (Optional[bool], default=None): Option to exclude variable header for tabular files.
            image_thumb (Optional[bool], default=None): Option to download an image thumbnail if applicable.
            follow_redirects (bool, default=True): Whether to follow HTTP redirects automatically.

        Returns:
            httpx.Response: The HTTP response containing the datafile or redirect.

        Raises:
            httpx.HTTPError: For underlying transport or protocol errors.
        """
        if self._is_pid(identifier):
            url = self._assemble_url("datafile/:persistentId")
            params = {"persistentId": identifier}
        else:
            url = self._assemble_url(f"datafile/{identifier}")
            params = {}

        # Add optional parameters if provided
        if data_format:
            params["format"] = data_format
        if no_var_header:
            params["noVarHeader"] = no_var_header
        if image_thumb:
            params["imageThumb"] = image_thumb

        return self.get_request(
            url,
            params=params,
            use_async=self.client is not None,
            follow_redirects=follow_redirects,
            response_model=bytes if follow_redirects else None,
        )

    @contextmanager
    def stream_datafile(
        self,
        identifier: Union[str, int],
        data_format: Optional[str] = None,
        no_var_header: Optional[bool] = None,
        image_thumb: Optional[bool] = None,
        range_start: Optional[int] = None,
        range_end: Optional[int] = None,
    ) -> Generator[httpx.Response, Any, Any]:
        """Download a datafile via streaming using the Dataverse Data Access API.

        This method returns a context manager for streaming large files efficiently.
        Supports both database IDs and persistent identifiers (PIDs) for file access.

        Args:
            identifier: Identifier of the datafile. Can be datafile id or persistent
                identifier of the datafile (e. g. doi).
            data_format: Optional data format parameter for format conversion.
            no_var_header: Optional parameter to exclude variable header from tabular data.
            image_thumb: Optional parameter to request image thumbnail instead of full image.
            range_start: Optional start byte position for Range request (inclusive).
            range_end: Optional end byte position for Range request (inclusive).
                If range_start is provided but range_end is None, reads from range_start to end.

        Returns:
            Context manager that yields the streaming HTTP response.
        """
        if self._is_pid(identifier):
            url = self._assemble_url("datafile/:persistentId/")
            params = {"persistentId": identifier}
        else:
            url = self._assemble_url(f"datafile/{identifier}")
            params = {}

        # Add optional parameters if provided
        if data_format:
            params["format"] = data_format
        if no_var_header:
            params["noVarHeader"] = no_var_header
        if image_thumb:
            params["imageThumb"] = image_thumb

        # Build Range header if range parameters are provided
        headers = None
        if range_start is not None:
            if range_end is not None:
                range_header = f"bytes={range_start}-{range_end}"
            else:
                range_header = f"bytes={range_start}-"
            headers = {"Range": range_header}

        with self.stream_file_context(url, params=params, headers=headers) as response:
            yield response

    def get_datafiles(
        self,
        identifiers: Sequence[Union[str, int]],
    ) -> bytes:
        """Download multiple datafiles via the Dataverse Data Access API.

        Downloads multiple files as a single ZIP archive. This is useful for
        batch downloading when you need several files from the same dataset.
        Note that this endpoint only supports database IDs, not persistent identifiers.

        Get by file id (HTTP Request).

        .. code-block:: bash

            GET /api/access/datafiles/$id1,$id2,...$idN

        Args:
            identifiers: Sequence of datafile identifiers. Can be datafile ids or persistent
                identifiers of the datafiles (e. g. doi).

        Returns:
            bytes: The ZIP archive content.
        """
        id_string = ",".join(str(identifier) for identifier in identifiers)
        url = self._assemble_url(f"datafiles/{id_string}")
        return self.get_request(
            url,
            use_async=self.client is not None,
            response_model=bytes,
        )

    @contextmanager
    def stream_datafiles(
        self,
        identifiers: Sequence[Union[str, int]],
    ) -> Generator[httpx.Response, Any, Any]:
        """Download multiple datafiles via streaming using the Dataverse Data Access API.

        Downloads multiple files as a single ZIP archive using streaming for efficient
        handling of large archives. This is useful for batch downloading when you need
        several files from the same dataset. Note that this endpoint only supports
        database IDs, not persistent identifiers.

        Args:
            identifiers: Sequence of datafile identifiers. Can be datafile ids or persistent
                identifiers of the datafiles (e. g. doi).

        Returns:
            Context manager that yields the streaming HTTP response.
        """
        id_string = ",".join(str(identifier) for identifier in identifiers)
        url = self._assemble_url(f"datafiles/{id_string}")

        with self.stream_file_context(url) as response:
            yield response

    def get_datafile_bundle(
        self,
        identifier: Union[str, int],
        file_metadata_id: Optional[int] = None,
    ) -> bytes:
        """Download a datafile in all its formats.

        This is a convenience packaging method available for tabular data files.
        It returns a zipped bundle containing the data in multiple formats, which is
        particularly useful for researchers who need the data in different formats
        for various analysis tools.

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
        - "Saved Original", the proprietary (SPSS, Stata, R, etc.) file
        from which the tabular data was ingested;
        - Generated R Data frame (unless the "original" above was in R);
        - Data (Variable) metadata record, in DDI XML;
        - File citation, in Endnote and RIS formats.

        Args:
            identifier: Identifier of the datafile. Can be datafile id or persistent
                identifier of the datafile (e. g. doi).
            file_metadata_id: Optional file metadata ID parameter for specific versions.

        Returns:
            Response object of httpx library containing the ZIP bundle.
        """

        if self._is_pid(identifier):
            url = self._assemble_url("datafile/bundle/:persistentId/")
            params = {"persistentId": identifier}
        else:
            url = self._assemble_url(f"datafile/bundle/{identifier}")
            params = {}

        if file_metadata_id:
            params["fileMetadataId"] = file_metadata_id

        return self.get_request(
            url,
            params=params,
            use_async=self.client is not None,
            response_model=bytes,
        )

    @contextmanager
    def stream_datafiles_bundle(
        self,
        identifier: Union[str, int],
        file_metadata_id: Optional[int] = None,
    ) -> Generator[httpx.Response, Any, Any]:
        """Download a datafile in all its formats via streaming.

        This is a convenience packaging method available for tabular data files.
        It returns a zipped bundle containing the data in multiple formats using
        streaming for efficient handling of large bundles.

        The bundle contains the data in the following formats:
        - Tab-delimited;
        - "Saved Original", the proprietary (SPSS, Stata, R, etc.) file
        from which the tabular data was ingested;
        - Generated R Data frame (unless the "original" above was in R);
        - Data (Variable) metadata record, in DDI XML;
        - File citation, in Endnote and RIS formats.

        Args:
            identifier: Identifier of the datafile. Can be datafile id or persistent
                identifier of the datafile (e. g. doi).
            file_metadata_id: Optional file metadata ID parameter for specific versions.

        Returns:
            Context manager that yields the streaming HTTP response.
        """

        if self._is_pid(identifier):
            url = self._assemble_url("datafile/bundle/:persistentId/")
            params = {"persistentId": identifier}
        else:
            url = self._assemble_url(f"datafile/bundle/{identifier}")
            params = {}

        if file_metadata_id:
            params["fileMetadataId"] = file_metadata_id

        with self.stream_file_context(url, params=params) as response:
            yield response

    def request_access(
        self,
        identifier: Union[str, int],
    ) -> message.Message:
        """Request datafile access.

        Submits an access request for a restricted datafile on behalf of the authenticated user.
        This is typically used when files are restricted and require permission from the dataset
        owner or administrator. Note that not all datasets allow access requests to restricted files.

        This method requests access to the datafile whose id is passed on the behalf of an authenticated user whose key is passed. Note that not all datasets allow access requests to restricted files.

        https://guides.dataverse.org/en/4.18.1/api/dataaccess.html#request-access

        /api/access/datafile/$id/requestAccess

        curl -H "X-Dataverse-key:$API_TOKEN" -X PUT http://$SERVER/api/access/datafile/{id}/requestAccess

        Args:
            identifier: Identifier of the datafile. Can be datafile id or persistent
                identifier of the datafile (e. g. doi).

        Returns:
            Message object containing the response status and details.
        """
        if self._is_pid(identifier):
            url = self._assemble_url("datafile/:persistentId/requestAccess")
            params = {"persistentId": identifier}
        else:
            url = self._assemble_url(f"datafile/{identifier}/requestAccess")
            params = {}

        return self.put_request(
            url,
            params=params,
            use_async=self.client is not None,
            response_model=message.Message,
        )

    def allow_access_request(
        self,
        identifier: Union[str, int],
        do_allow: bool = True,
    ) -> message.Message:
        """Allow or deny access requests for datafiles.

        Enables or disables the ability for users to request access to restricted files.
        This is an administrative function that controls whether the "Request Access"
        button appears for restricted files in the dataset.

        https://guides.dataverse.org/en/latest/api/dataaccess.html#allow-access-requests

        curl -H "X-Dataverse-key:$API_TOKEN" -X PUT -d true http://$SERVER/api/access/{id}/allowAccessRequest
        curl -H "X-Dataverse-key:$API_TOKEN" -X PUT -d true http://$SERVER/api/access/:persistentId/allowAccessRequest?persistentId={pid}

        Args:
            identifier: Identifier of the datafile. Can be datafile id or persistent
                identifier of the datafile (e. g. doi).
            do_allow: Whether to allow access requests (True) or disable them (False).

        Returns:
            Message object containing the response status and details.
        """
        if self._is_pid(identifier):
            url = self._assemble_url("datafile/:persistentId/allowAccessRequest")
            params = {"persistentId": identifier}
        else:
            url = self._assemble_url(f"datafile/{identifier}/allowAccessRequest")
            params = {}

        return self.put_request(
            url,
            data=str(do_allow).lower(),
            params=params,
            response_model=message.Message,
            use_async=self.client is not None,
        )

    def grant_file_access(
        self,
        identifier: Union[str, int],
        user: Union[str, int],
    ) -> message.Message:
        """Grant datafile access to a specific user.

        Grants access to a restricted datafile for a specific user. This is typically
        used by dataset administrators to approve access requests or proactively grant
        access to specific users.

        https://guides.dataverse.org/en/4.18.1/api/dataaccess.html#grant-file-access

        curl -H "X-Dataverse-key:$API_TOKEN" -X PUT http://$SERVER/api/access/datafile/{id}/grantAccess/{@userIdentifier}

        Args:
            identifier: Identifier of the datafile. Can be datafile id or persistent
                identifier of the datafile (e. g. doi).
            user: User identifier to grant access to (username or user ID).

        Returns:
            Message object containing the response status and details.
        """
        if self._is_pid(identifier):
            url = self._assemble_url("datafile/:persistentId/grantAccess/:persistentId")
            params = {"persistentId": identifier, "user": user}
        else:
            url = self._assemble_url(f"datafile/{identifier}/grantAccess/{user}")
            params = {}

        return self.put_request(
            url,
            params=params,
            response_model=message.Message,
            use_async=self.client is not None,
        )

    def list_file_access_requests(
        self,
        identifier: Union[str, int],
    ) -> List[access.AccessRequest]:
        """List datafile access requests.

        Retrieves a list of all pending access requests for a specific datafile.
        This is useful for dataset administrators to review and manage access requests.
        Each request includes user information and timestamps.

        https://guides.dataverse.org/en/4.18.1/api/dataaccess.html#list-file-access-requests

        curl -H "X-Dataverse-key:$API_TOKEN" -X GET http://$SERVER/api/access/datafile/{id}/listRequests

        Args:
            identifier: Identifier of the datafile. Can be datafile id or persistent
                identifier of the datafile (e. g. doi).

        Returns:
            List of AccessRequest objects containing user details and request information.
        """

        if self._is_pid(identifier):
            url = self._assemble_url("datafile/:persistentId/listRequests")
            params = {"persistentId": identifier}
        else:
            url = self._assemble_url(f"datafile/{identifier}/listRequests")
            params = {}

        return self.get_request(
            url,
            params=params,
            use_async=self.client is not None,
            response_model=List[access.AccessRequest],
        )
