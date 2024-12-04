import json
from enum import Enum
from typing import Any, Dict, Optional
from warnings import warn

import httpx
from httpx import ConnectError
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ConfigDict,
    model_validator,
    computed_field,
)
from sqlalchemy.testing.plugin.plugin_base import warnings

from pyDataverse.auth import ApiTokenAuth
from pyDataverse.exceptions import (
    ApiAuthorizationError,
)

DEPRECATION_GUARD = object()


class APIVersion(Enum):
    LATEST = "latest"
    V1 = "v1"


class Api(BaseModel):
    base_url: str = Field(
        ...,
        description="Base url for Dataverse api.",
    )

    api_token: Optional[str] = Field(
        None,
        description="API token for Dataverse API",
    )

    api_version: APIVersion = Field(
        APIVersion.LATEST,
        description="The version string of the Dataverse API.",
    )

    auth: Optional[httpx.Auth] = Field(
        None,
        description="You can provide any authentication mechanism you like to connect to your Dataverse instance.",
    )

    timeout: int = Field(
        500,
        description="Timeout for the API connection.",
    )

    client: Optional[httpx.AsyncClient] = Field(
        None,
        description="An instance of httpx.AsyncClient. This will be initialized in an async context manager.",
    )

    model_config: ConfigDict = {
        "use_enum_values": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "arbitrary_types_allowed": True,
    }

    @model_validator(mode="after")
    def check_auth(self):
        if self.api_token and self.auth:
            warnings.warn(
                "You provided both, an api_token and a custom auth method. We will only use the auth method."
            )
        elif self.api_token:
            self.auth = ApiTokenAuth(self.api_token)
            self.api_token = None

        return self

    @computed_field(return_type=str)
    def base_url_api(self):
        if self.api_version == APIVersion.LATEST:
            return f"{self.base_url}/api"
        else:
            return f"{self.base_url}/api/{self.api_version.value}"

    @classmethod
    @field_validator("base_url")
    def check_base_url(cls, url):
        response = httpx.head(url)

        if response.status_code != 200:
            raise ValueError(f"Could not connect to {url}.")

        return url.rstrip("/")

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

        headers = {"User-Agent": "pydataverse"}

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
