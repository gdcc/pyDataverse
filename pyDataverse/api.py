"""Dataverse API wrapper for all it's API's."""

import json
from typing import Any, Dict, Optional
import httpx
import subprocess as sp
from warnings import warn

from httpx import ConnectError, Response

from pyDataverse.auth import ApiTokenAuth
from pyDataverse.exceptions import (
    ApiAuthorizationError,
    ApiUrlError,
    DatasetNotFoundError,
    DataverseNotEmptyError,
    DataverseNotFoundError,
    OperationFailedError,
)

DEPRECATION_GUARD = object()


class Api:
    """Base class.

    Parameters
    ----------
        base_url : str
            Base URL of Dataverse instance. Without trailing `/` at the end.
            e.g. `http://demo.dataverse.org`
        api_token : str
            Authentication token for the api.

    Attributes
    ----------
    base_url
    api_token
    dataverse_version

    """

    def __init__(
        self,
        base_url: str,
        api_token: Optional[str] = None,
        api_version: str = "latest",
        *,
        auth: Optional[httpx.Auth] = None,
    ):
        """Init an Api() class.

        Scheme, host and path combined create the base-url for the api.
        See more about URL at `Wikipedia <https://en.wikipedia.org/wiki/URL>`_.

        Parameters
        ----------
        base_url : str
            Base url for Dataverse api.
        api_token : str | None
            API token for Dataverse API. If you provide an :code:`api_token`, we
            assume it is an API token as retrieved via your Dataverse instance
            user profile.
            We recommend using the :code:`auth` argument instead.
            To retain the current behaviour with the :code:`auth` argument, change

            .. code-block:: python

                Api("https://demo.dataverse.org", "my_token")

            to

            .. code-block:: python

                from pyDataverse.auth import ApiTokenAuth

                Api("https://demo.dataverse.org", auth=ApiTokenAuth("my_token"))

            If you are using an OIDC/OAuth 2.0 Bearer token, please use the :code:`auth`
            parameter with the :py:class:`.auth.BearerTokenAuth`.
        api_version : str
            The version string of the Dataverse API or :code:`latest`, e.g.,
            :code:`v1`. Defaults to :code:`latest`, which drops the version from
            the API urls.
        auth : httpx.Auth | None
            You can provide any authentication mechanism you like to connect to
            your Dataverse instance.  The most common mechanisms are implemented
            in :py:mod:`.auth`, but if one is missing, you can use your own
            `httpx.Auth`-compatible class. For more information, have a look at
            `httpx' Authentication docs
            <https://www.python-httpx.org/advanced/authentication/>`_.
        Examples
        -------
        Create an API connection::

        .. code-block::

            >>> from pyDataverse.api import Api
            >>> base_url = 'http://demo.dataverse.org'
            >>> api = Api(base_url)

        .. code-block::

            >>> from pyDataverse.api import Api
            >>> from pyDataverse.auth import ApiTokenAuth
            >>> base_url = 'http://demo.dataverse.org'
            >>> api = Api(base_url, ApiTokenAuth('my_api_token'))

        """
        if not isinstance(base_url, str):
            raise ApiUrlError("base_url {0} is not a string.".format(base_url))

        self.base_url = base_url.rstrip("/")
        self.client = None

        if not isinstance(api_version, str):
            raise ApiUrlError("api_version {0} is not a string.".format(api_version))
        self.api_version = api_version

        self.auth = auth
        self.api_token = api_token
        if api_token is not None:
            if auth is None:
                self.auth = ApiTokenAuth(api_token)
            else:
                self.api_token = None
                warn(
                    UserWarning(
                        "You provided both, an api_token and a custom auth "
                        "method. We will only use the auth method."
                    )
                )

        if self.api_version == "latest":
            self.base_url_api = "{0}/api".format(self.base_url)
        else:
            self.base_url_api = "{0}/api/{1}".format(self.base_url, self.api_version)

        self.timeout = 500

    def __str__(self):
        """Return the class name and URL of the used API class.

        Returns
        -------
        str
            Naming of the API class.

        """
        return f"{self.__class__.__name__}: {self.base_url_api}"

    def get_request(self, url, params=None, auth=DEPRECATION_GUARD):
        """Make a GET request.

        Parameters
        ----------
        url : str
            Full URL.
        params : dict
            Dictionary of parameters to be passed with the request.
            Defaults to `None`.
        auth : Any
            .. deprecated:: 0.3.4
                The auth parameter was ignored before version 0.3.4.
                Please pass your auth to the Api instance directly, as
                explained in :py:func:`Api.__init__`.
                If you need multiple auth methods, create multiple
                API instances:

                .. code-block:: python

                    api = Api("https://demo.dataverse.org", auth=ApiTokenAuth("my_api_token"))
                    api_oauth = Api("https://demo.dataverse.org", auth=BearerTokenAuth("my_bearer_token"))

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        if auth is not DEPRECATION_GUARD:
            warn(
                DeprecationWarning(
                    "The auth parameter is deprecated. Please pass your auth "
                    "arguments to the __init__ method instead."
                )
            )
        headers = {}
        headers["User-Agent"] = "pydataverse"

        if self.client is None:
            return self._sync_request(
                method=httpx.get,
                url=url,
                headers=headers,
                params=params,
            )
        else:
            return self._async_request(
                method=self.client.get,
                url=url,
                headers=headers,
                params=params,
            )

    def post_request(
        self, url, data=None, auth=DEPRECATION_GUARD, params=None, files=None
    ):
        """Make a POST request.

        params will be added as key-value pairs to the URL.

        Parameters
        ----------
        url : str
            Full URL.
        data : str
            Metadata as a json-formatted string. Defaults to `None`.
        auth : Any
            .. deprecated:: 0.3.4
                The auth parameter was ignored before version 0.3.4.
                Please pass your auth to the Api instance directly, as
                explained in :py:func:`Api.__init__`.
                If you need multiple auth methods, create multiple
                API instances:

                .. code-block:: python

                    api = Api("https://demo.dataverse.org", auth=ApiTokenAuth("my_api_token"))
                    api_oauth = Api("https://demo.dataverse.org", auth=BearerTokenAuth("my_bearer_token"))
        files : dict
            e.g. :code:`files={'file': open('sample_file.txt','rb')}`
        params : dict
            Dictionary of parameters to be passed with the request.
            Defaults to :code:`None`.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        if auth is not DEPRECATION_GUARD:
            warn(
                DeprecationWarning(
                    "The auth parameter is deprecated. Please pass your auth "
                    "arguments to the __init__ method instead."
                )
            )
        headers = {}
        headers["User-Agent"] = "pydataverse"

        if isinstance(data, str):
            data = json.loads(data)

        # Decide whether to use 'data' or 'json' args
        request_params = self._check_json_data_form(data)

        if self.client is None:
            return self._sync_request(
                method=httpx.post,
                url=url,
                headers=headers,
                params=params,
                files=files,
                **request_params,
            )
        else:
            return self._async_request(
                method=self.client.post,
                url=url,
                headers=headers,
                params=params,
                files=files,
                **request_params,
            )

    def put_request(self, url, data=None, auth=DEPRECATION_GUARD, params=None):
        """Make a PUT request.

        Parameters
        ----------
        url : str
            Full URL.
        data : str
            Metadata as a json-formatted string. Defaults to `None`.
        auth : Any
            .. deprecated:: 0.3.4
                The auth parameter was ignored before version 0.3.4.
                Please pass your auth to the Api instance directly, as
                explained in :py:func:`Api.__init__`.
                If you need multiple auth methods, create multiple
                API instances:

                .. code-block:: python

                    api = Api("https://demo.dataverse.org", auth=ApiTokenAuth("my_api_token"))
                    api_oauth = Api("https://demo.dataverse.org", auth=BearerTokenAuth("my_bearer_token"))
        params : dict
            Dictionary of parameters to be passed with the request.
            Defaults to `None`.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        if auth is not DEPRECATION_GUARD:
            warn(
                DeprecationWarning(
                    "The auth parameter is deprecated. Please pass your auth "
                    "arguments to the __init__ method instead."
                )
            )
        headers = {}
        headers["User-Agent"] = "pydataverse"

        if isinstance(data, str):
            data = json.loads(data)

        # Decide whether to use 'data' or 'json' args
        request_params = self._check_json_data_form(data)

        if self.client is None:
            return self._sync_request(
                method=httpx.put,
                url=url,
                json=data,
                headers=headers,
                params=params,
                **request_params,
            )
        else:
            return self._async_request(
                method=self.client.put,
                url=url,
                json=data,
                headers=headers,
                params=params,
                **request_params,
            )

    def delete_request(self, url, auth=DEPRECATION_GUARD, params=None):
        """Make a Delete request.

        Parameters
        ----------
        url : str
            Full URL.
        auth : Any
            .. deprecated:: 0.3.4
                The auth parameter was ignored before version 0.3.4.
                Please pass your auth to the Api instance directly, as
                explained in :py:func:`Api.__init__`.
                If you need multiple auth methods, create multiple
                API instances:

                .. code-block:: python

                    api = Api("https://demo.dataverse.org", auth=ApiTokenAuth("my_api_token"))
                    api_oauth = Api("https://demo.dataverse.org", auth=BearerTokenAuth("my_bearer_token"))
        params : dict
            Dictionary of parameters to be passed with the request.
            Defaults to `None`.

        Returns
        -------
        httpx.Response
            Response object of httpx library.

        """
        if auth is not DEPRECATION_GUARD:
            warn(
                DeprecationWarning(
                    "The auth parameter is deprecated. Please pass your auth "
                    "arguments to the __init__ method instead."
                )
            )
        headers = {}
        headers["User-Agent"] = "pydataverse"

        if self.client is None:
            return self._sync_request(
                method=httpx.delete,
                url=url,
                headers=headers,
                params=params,
            )
        else:
            return self._async_request(
                method=self.client.delete,
                url=url,
                headers=headers,
                params=params,
            )

    @staticmethod
    def _check_json_data_form(data: Optional[Dict]):
        """This method checks and distributes given payload to match Dataverse expectations.

        In the case of the form-data keyed by "jsonData", Dataverse expects
        the payload as a string in a form of a dictionary. This is not possible
        using HTTPXs json parameter, so we need to handle this case separately.
        """

        if not data:
            return {}
        elif not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")
        elif "jsonData" not in data:
            return {"json": data}

        assert list(data.keys()) == [
            "jsonData"
        ], "jsonData must be the only key in the dictionary."

        # Content of JSON data should ideally be a string
        content = data["jsonData"]
        if not isinstance(content, str):
            data["jsonData"] = json.dumps(content)

        return {"data": data}

    def _sync_request(
        self,
        method,
        **kwargs,
    ):
        """
        Sends a synchronous request to the specified URL using the specified HTTP method.

        Args:
            method (function): The HTTP method to use for the request.
            **kwargs: Additional keyword arguments to be passed to the method.

        Returns:
            httpx.Response: The response object returned by the request.

        Raises:
            ApiAuthorizationError: If the response status code is 401 (Authorization error).
            ConnectError: If a connection to the API cannot be established.
        """
        assert "url" in kwargs, "URL is required for a request."

        kwargs = self._filter_kwargs(kwargs)

        try:
            resp: httpx.Response = method(
                **kwargs, auth=self.auth, follow_redirects=True, timeout=None
            )
            if resp.status_code == 401:
                try:
                    error_msg = resp.json()["message"]
                except json.JSONDecodeError:
                    error_msg = resp.reason_phrase
                raise ApiAuthorizationError(
                    "ERROR: HTTP 401 - Authorization error {0}. MSG: {1}".format(
                        kwargs["url"], error_msg
                    )
                )

            return resp

        except ConnectError:
            raise ConnectError(
                "ERROR - Could not establish connection to api '{0}'.".format(
                    kwargs["url"]
                )
            )

    async def _async_request(
        self,
        method,
        **kwargs,
    ):
        """
        Sends an asynchronous request to the specified URL using the specified HTTP method.

        Args:
            method (callable): The HTTP method to use for the request.
            **kwargs: Additional keyword arguments to be passed to the method.

        Raises:
            ApiAuthorizationError: If the response status code is 401 (Authorization error).
            ConnectError: If a connection to the API cannot be established.

        Returns:
            The response object.

        """
        assert "url" in kwargs, "URL is required for a request."

        kwargs = self._filter_kwargs(kwargs)

        try:
            resp = await method(**kwargs, auth=self.auth)

            if resp.status_code == 401:
                error_msg = resp.json()["message"]
                raise ApiAuthorizationError(
                    "ERROR: HTTP 401 - Authorization error {0}. MSG: {1}".format(
                        kwargs["url"], error_msg
                    )
                )

            return resp

        except ConnectError:
            raise ConnectError(
                "ERROR - Could not establish connection to api '{0}'.".format(
                    kwargs["url"]
                )
            )

    @staticmethod
    def _filter_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters out any keyword arguments that are `None` from the specified dictionary.

        Args:
            kwargs (Dict[str, Any]): The dictionary to filter.

        Returns:
            Dict[str, Any]: The filtered dictionary.
        """
        return {k: v for k, v in kwargs.items() if v is not None}

    async def __aenter__(self):
        """
        Context manager method that initializes an instance of httpx.AsyncClient.

        Returns:
            httpx.AsyncClient: An instance of httpx.AsyncClient.
        """
        self.client = httpx.AsyncClient()

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Closes the client connection when exiting a context manager.

        Args:
            exc_type (type): The type of the exception raised, if any.
            exc_value (Exception): The exception raised, if any.
            traceback (traceback): The traceback object associated with the exception, if any.
        """

        await self.client.aclose()
        self.client = None


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


class MetricsApi(Api):
    """Class to access Dataverse's Metrics API.

    Attributes
    ----------
    base_url_api_metrics : type
        Description of attribute `base_url_api_metrics`.
    base_url : type
        Description of attribute `base_url`.

    """

    def __init__(self, base_url, api_token=None, api_version="latest", *, auth=None):
        """Init an MetricsApi() class."""
        super().__init__(base_url, api_token, api_version, auth=auth)
        if base_url:
            self.base_url_api_metrics = "{0}/api/info/metrics".format(self.base_url)
        else:
            self.base_url_api_metrics = None

    def total(self, data_type, date_str=None, auth=DEPRECATION_GUARD):
        """
        GET https://$SERVER/api/info/metrics/$type
        GET https://$SERVER/api/info/metrics/$type/toMonth/$YYYY-DD

        $type can be set to dataverses, datasets, files or downloads.

        """
        url = "{0}/{1}".format(self.base_url_api_metrics, data_type)
        if date_str:
            url += "/toMonth/{0}".format(date_str)
        return self.get_request(url, auth=auth)

    def past_days(self, data_type, days_str, auth=DEPRECATION_GUARD):
        """

        http://guides.dataverse.org/en/4.18.1/api/metrics.html
        GET https://$SERVER/api/info/metrics/$type/pastDays/$days

        $type can be set to dataverses, datasets, files or downloads.
        """
        # TODO: check if date-string has proper format
        url = "{0}/{1}/pastDays/{2}".format(
            self.base_url_api_metrics, data_type, days_str
        )
        return self.get_request(url, auth=auth)

    def get_dataverses_by_subject(self, auth=DEPRECATION_GUARD):
        """
        GET https://$SERVER/api/info/metrics/dataverses/bySubject

        $type can be set to dataverses, datasets, files or downloads.
        """
        # TODO: check if date-string has proper format
        url = "{0}/dataverses/bySubject".format(self.base_url_api_metrics)
        return self.get_request(url, auth=auth)

    def get_dataverses_by_category(self, auth=DEPRECATION_GUARD):
        """
        GET https://$SERVER/api/info/metrics/dataverses/byCategory

        $type can be set to dataverses, datasets, files or downloads.
        """
        # TODO: check if date-string has proper format
        url = "{0}/dataverses/byCategory".format(self.base_url_api_metrics)
        return self.get_request(url, auth=auth)

    def get_datasets_by_subject(self, date_str=None, auth=DEPRECATION_GUARD):
        """
        GET https://$SERVER/api/info/metrics/datasets/bySubject

        $type can be set to dataverses, datasets, files or downloads.
        """
        # TODO: check if date-string has proper format
        url = "{0}/datasets/bySubject".format(self.base_url_api_metrics)
        if date_str:
            url += "/toMonth/{0}".format(date_str)
        return self.get_request(url, auth=auth)

    def get_datasets_by_data_location(self, data_location, auth=DEPRECATION_GUARD):
        """
        GET https://$SERVER/api/info/metrics/datasets/?dataLocation=$location

        $type can be set to dataverses, datasets, files or downloads.
        """
        # TODO: check if date-string has proper format
        url = "{0}/datasets/?dataLocation={1}".format(
            self.base_url_api_metrics, data_location
        )
        return self.get_request(url, auth=auth)


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

    def __init__(self, base_url: str, api_token=None, api_version="v1", *, auth=None):
        """Init an Api() class.

        Scheme, host and path combined create the base-url for the api.
        See more about URL at `Wikipedia <https://en.wikipedia.org/wiki/URL>`_.

        Parameters
        ----------
        native_api_version : str
            API version of Dataverse native API. Default is `v1`.

        """
        super().__init__(base_url, api_token, api_version, auth=auth)
        self.base_url_api_native = self.base_url_api

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


class SearchApi(Api):
    """Class to access Dataverse's Search API.

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

    def __init__(self, base_url, api_token=None, api_version="latest", *, auth=None):
        """Init an SearchApi() class."""
        super().__init__(base_url, api_token, api_version, auth=auth)
        if base_url:
            self.base_url_api_search = "{0}/search?q=".format(self.base_url_api)
        else:
            self.base_url_api_search = self.base_url_api

    def search(
        self,
        q_str,
        data_type=None,
        subtree=None,
        sort=None,
        order=None,
        per_page=None,
        start=None,
        show_relevance=None,
        show_facets=None,
        filter_query=None,
        show_entity_ids=None,
        query_entities=None,
        auth=DEPRECATION_GUARD,
    ):
        """Search.

        http://guides.dataverse.org/en/4.18.1/api/search.html
        """
        url = "{0}{1}".format(self.base_url_api_search, q_str)
        if data_type:
            # TODO: pass list of types
            url += "&type={0}".format(data_type)
        if subtree:
            # TODO: pass list of subtrees
            url += "&subtree={0}".format(subtree)
        if sort:
            url += "&sort={0}".format(sort)
        if order:
            url += "&order={0}".format(order)
        if per_page:
            url += "&per_page={0}".format(per_page)
        if start:
            url += "&start={0}".format(start)
        if show_relevance:
            url += "&show_relevance={0}".format(show_relevance)
        if show_facets:
            url += "&show_facets={0}".format(show_facets)
        if filter_query:
            url += "&fq={0}".format(filter_query)
        if show_entity_ids:
            url += "&show_entity_ids={0}".format(show_entity_ids)
        if query_entities:
            url += "&query_entities={0}".format(query_entities)
        return self.get_request(url, auth=auth)


class SwordApi(Api):
    """Class to access Dataverse's SWORD API.

    Parameters
    ----------
    sword_api_version : str
        SWORD API version. Defaults to 'v1.1'.

    Attributes
    ----------
    base_url_api_sword : str
        Description of attribute `base_url_api_sword`.
    base_url : str
        Description of attribute `base_url`.
    native_api_version : str
        Description of attribute `native_api_version`.
    sword_api_version

    """

    def __init__(
        self,
        base_url,
        api_version="v1.1",
        api_token=None,
        sword_api_version="v1.1",
        *,
        auth=None,
    ):
        """Init a :class:`SwordApi <pyDataverse.api.SwordApi>` instance.

        Parameters
        ----------
        sword_api_version : str
            Api version of Dataverse SWORD API.
        api_token : str | None
            An Api token as retrieved from your Dataverse instance.
        auth : httpx.Auth
            Note that the SWORD API uses a different authentication mechanism
            than the native API, in particular it uses `HTTP Basic
            Authentication
            <https://guides.dataverse.org/en/latest/api/sword.html#sword-auth>`_.
            Thus, if you pass an api_token, it will be used as the username in
            the HTTP Basic Authentication. If you pass a custom :py:class:`httpx.Auth`, use
            :py:class:`httpx.BasicAuth` with an empty password:

            .. code-block:: python

                sword_api = Api(
                    "https://demo.dataverse.org", auth=httpx.BasicAuth(username="my_token", password="")
                )

        """
        if auth is None and api_token is not None:
            auth = httpx.BasicAuth(api_token, "")
        super().__init__(base_url, api_token, api_version, auth=auth)
        if not isinstance(sword_api_version, ("".__class__, "".__class__)):
            raise ApiUrlError(
                "sword_api_version {0} is not a string.".format(sword_api_version)
            )
        self.sword_api_version = sword_api_version

        # Test connection.
        if self.base_url and sword_api_version:
            self.base_url_api_sword = "{0}/dvn/api/data-deposit/{1}".format(
                self.base_url, self.sword_api_version
            )
        else:
            self.base_url_api_sword = base_url

    def get_service_document(self):
        url = "{0}/swordv2/service-document".format(self.base_url_api_sword)
        return self.get_request(url, auth=True)
