from __future__ import annotations

import abc
import json
from contextlib import contextmanager
from enum import Enum
from types import UnionType
from typing import (
    Any,
    Coroutine,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    overload,
)
from urllib.parse import urljoin
from warnings import warn

import httpx
from httpx import ConnectError, HTTPStatusError
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    computed_field,
    field_validator,
    model_validator,
)
from typing_extensions import Self, TypeAlias

from ..auth import ApiTokenAuth
from .response import APIResponse, Status
from .utilities.logger import ApiLogger

DEPRECATION_GUARD = object()

# Type variable for generic Pydantic model types, constrained to BaseModel subclasses
T = TypeVar("T", bound=BaseModel)

# Type variable for generic Any types, constrained to Any
A = TypeVar("A", bound=Any)

# Union type representing the various response model types that can be used
# to validate and parse API responses. Includes single models, lists of models,
# and generic Any types for flexible response handling.
ResponseModels = Union[
    Type[BaseModel],
    Type[List[BaseModel]],
    Type[A],
    Type[List[A]],
]

# Union type representing all possible return types from API request methods.
# This includes raw HTTP responses, parsed Pydantic models (single or lists),
# sequences of models for compatibility, and coroutines for async operations
# that return HTTP responses.
RequestResponse = Union[
    httpx.Response,
    BaseModel,
    List[BaseModel],
    Sequence[BaseModel],
    Coroutine[Any, Any, httpx.Response],
]

# Type alias for payloads that can be either a Pydantic model or a dictionary
Payload: TypeAlias = Union[T, Dict[str, Any] | str]


class APIVersion(Enum):
    """Enumeration of supported Dataverse API versions.

    Attributes:
        LATEST: The latest version of the Dataverse API.
        V1: Version 1 of the Dataverse API.
    """

    LATEST = "v1"
    V1 = "v1"


class DataverseBase(BaseModel):
    logger: ApiLogger = Field(
        default_factory=lambda: ApiLogger(__name__),
        exclude=True,
        description="A logger for the API.",
    )

    model_config: ConfigDict = ConfigDict(
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
    )


class AbstractApi(abc.ABC):
    """Abstract base class for all API implementations.

    Every API should implement an "api_base_url" property.
    """

    @property
    @abc.abstractmethod
    def api_base_url(self) -> str:
        """Return the base URL for this API."""
        pass


class Api(DataverseBase, AbstractApi):
    """A class to handle API interactions with Dataverse.

    This class provides a unified interface for making HTTP requests to Dataverse APIs
    with support for both synchronous and asynchronous operations. It leverages Python's
    function overloading feature to provide type-safe request methods that can return
    either raw HTTP responses or parsed Pydantic models based on the provided arguments.

    The overload system works as follows:
    1. When no response_model is provided, the method returns a raw httpx.Response
    2. When a response_model is provided, the response is parsed and validated into
       the specified Pydantic model(s)
    3. The use_async parameter determines whether to return a coroutine or execute
       synchronously
    4. Type checkers can infer the correct return type based on the arguments provided

    This design ensures compile-time type safety while maintaining runtime flexibility,
    allowing developers to work with either raw responses or strongly-typed data models
    as needed.

    Attributes:
        base_url (str): Base url for Dataverse api.
        api_token (Optional[str]): API token for Dataverse API.
        api_version (APIVersion): The version string of the Dataverse API.
        auth (Optional[httpx.Auth]): Authentication mechanism for Dataverse instance.
        timeout (int): Timeout for the API connection.
        client (Optional[httpx.AsyncClient]): Instance of httpx.AsyncClient for async context.
    """

    base_url: str = Field(
        ...,
        description="Base url for Dataverse api.",
    )

    api_token: Optional[str] = Field(
        default=None,
        description="API token for Dataverse API",
        exclude=True,
    )

    api_version: APIVersion = Field(
        default=APIVersion.LATEST,
        description="The version string of the Dataverse API.",
    )

    auth: Optional[httpx.Auth] = Field(
        default=None,
        description="You can provide any authentication mechanism you like to connect to your Dataverse instance.",
    )

    timeout: int = Field(
        default=500,
        description="Timeout for the API connection.",
    )

    max_connections: int = Field(
        default=10,
        description="Maximum number of concurrent connections to the Dataverse API.",
    )

    max_keepalive_connections: int = Field(
        default=5,
        description="Maximum number of keepalive connections to the Dataverse API.",
    )

    client: Optional[httpx.AsyncClient] = Field(
        default=None,
        description="An instance of httpx.AsyncClient. This will be initialized in an async context manager.",
    )

    verbose: int = Field(
        default=1,
        description="Whether to log verbose information.",
    )

    @model_validator(mode="after")
    def check_auth(self):
        self.logger.set_verbose(self.verbose)

        # Check connection
        try:
            httpx.head(self.base_url)
            if self.verbose >= 1:
                self.logger.info(
                    f"[bold blue]{self.__class__.__name__}[/bold blue]: Connected to {self.base_url}"
                )
        except ConnectError as e:
            self.logger.error(
                f"Could not connect to [link={self.base_url}]{self.base_url}[/link]"
            )
            raise e
        if self.api_token and self.auth:
            warn(
                "You provided both, an api_token and a custom auth method. We will only use the auth method."
            )
            self.auth = ApiTokenAuth(self.api_token)
            self.api_token = None
        elif self.api_token:
            self.auth = ApiTokenAuth(self.api_token)
            self.api_token = None

        return self

    @computed_field
    @property
    def base_url_api(self) -> str:
        if self.api_version == APIVersion.LATEST:
            return urljoin(self.base_url, "api/")
        else:
            return urljoin(self.base_url, f"api/{self.api_version}/")

    @classmethod
    @field_validator("base_url")
    def check_base_url(cls, url):
        response = httpx.head(url)

        if response.status_code != 200:
            raise ValueError(f"Could not connect to {url}.")

        if not url.endswith("/"):
            url += "/"

        return url

    def __str__(self):
        """Returns the class name and URL of the used API class.

        Returns:
            str: String representation in format "ClassName: base_url_api"
        """
        return f"{self.__class__.__name__}: {self.base_url_api}"

    @classmethod
    def from_api(cls, api: "Api") -> Self:
        """Create a new Sub-API instance from an existing Api instance.

        Args:
            api: The Api instance to create a new instance from.
        """
        instance = cls.model_construct(
            base_url=api.base_url,
            api_token=api.api_token,
            auth=api.auth,
            verbose=api.verbose,
            api_version=api.api_version,
            timeout=api.timeout,
            max_connections=api.max_connections,
            max_keepalive_connections=api.max_keepalive_connections,
            logger=ApiLogger(__name__),
        )

        instance.logger.set_verbose(api.verbose)
        return instance

    @overload
    def get_request(
        self,
        url,
        response_model: None = None,
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> httpx.Response:
        """Synchronous GET request returning raw HTTP response.

        This overload is used when no response_model is provided and use_async=False.
        The method will execute synchronously and return the raw httpx.Response object.

        Args:
            url: Full URL for the request
            response_model: Must be None for this overload
            params: Optional query parameters
            auth: Deprecated authentication parameter
            use_async: Must be False for this overload

        Returns:
            httpx.Response: Raw HTTP response object
        """
        ...

    @overload
    def get_request(
        self,
        url,
        response_model: None = None,
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = True,
        follow_redirects: bool = True,
    ) -> Coroutine[Any, Any, httpx.Response]:
        """Asynchronous GET request returning coroutine of raw HTTP response.

        This overload is used when no response_model is provided and use_async=True.
        The method will return a coroutine that yields the raw httpx.Response object.

        Args:
            url: Full URL for the request
            response_model: Must be None for this overload
            params: Optional query parameters
            auth: Deprecated authentication parameter
            use_async: Must be True for this overload

        Returns:
            Coroutine[Any, Any, httpx.Response]: Coroutine yielding raw HTTP response
        """
        ...

    @overload
    def get_request(
        self,
        url,
        response_model: Type[T],
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> T:
        """Synchronous GET request returning parsed Pydantic model.

        This overload is used when a specific Pydantic model type is provided.
        The method will execute synchronously, parse the response, and return
        a validated instance of the specified model.

        Args:
            url: Full URL for the request
            response_model: Pydantic model class to parse response into
            params: Optional query parameters
            auth: Deprecated authentication parameter
            use_async: Whether to execute asynchronously

        Returns:
            T: Validated instance of the specified Pydantic model
        """
        ...

    @overload
    def get_request(
        self,
        url,
        response_model: Type[List[T]],
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> List[T]:
        """Synchronous GET request returning list of parsed Pydantic models.

        This overload is used when a List[Model] type is provided.
        The method will execute synchronously, parse the response as a collection,
        and return a list of validated model instances.

        Args:
            url: Full URL for the request
            response_model: List type annotation containing Pydantic model class
            params: Optional query parameters
            auth: Deprecated authentication parameter
            use_async: Whether to execute asynchronously

        Returns:
            List[T]: List of validated Pydantic model instances
        """
        ...

    @overload
    def get_request(
        self,
        url,
        response_model: Type[A],
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> A:
        """Synchronous GET request returning parsed Pydantic model.

        This overload is used when a specific Pydantic model type is provided.
        The method will execute synchronously, parse the response, and return
        a validated instance of the specified model.

        Args:
            url: Full URL for the request
            response_model: List type annotation containing Pydantic model class
            params: Optional query parameters
            auth: Deprecated authentication parameter
            use_async: Whether to execute asynchronously

        Returns:
            A: Validated instance of the specified Pydantic model
        """
        ...

    @overload
    def get_request(
        self,
        url,
        response_model: Type[List[A]],
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> List[A]:
        """Synchronous GET request returning list of parsed Pydantic models.

        This overload is used when a List[Model] type is provided.
        The method will execute synchronously, parse the response as a collection,
        and return a list of validated model instances.

        Args:
            url: Full URL for the request
            response_model: List type annotation containing Pydantic model class
            params: Optional query parameters
            auth: Deprecated authentication parameter
            use_async: Whether to execute asynchronously

        Returns:
            List[A]: List of validated Pydantic model instances
        """
        ...

    def get_request(
        self,
        url,
        response_model: Optional[ResponseModels] = None,
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> RequestResponse:
        """Makes a GET request.

        Args:
            url (str): Full URL.
            params (dict, optional): Dictionary of parameters for the request.
            auth (Any, optional): Deprecated. Use Api instance auth instead.

        Returns:
            httpx.Response: Response from the request.

        Deprecated:
            0.3.4: The auth parameter was ignored before version 0.3.4.
            Please pass your auth to the Api instance directly.
        """

        if headers:
            headers.update({"User-Agent": "pydataverse"})
        else:
            headers = {"User-Agent": "pydataverse"}

        if not use_async:
            return self._sync_request(
                method=httpx.get,
                url=url,
                headers=headers,
                params=params,
                response_model=response_model,
                follow_redirects=follow_redirects,
            )
        else:  # use_async is True
            if self.client is None:
                raise ValueError("Async client is not initialized.")

            return self._async_request(
                method=self.client.get,
                url=url,
                headers=headers,
                params=params,
                response_model=response_model,
                follow_redirects=follow_redirects,
            )

    @contextmanager
    def stream_file_context(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Generator[httpx.Response, Any, Any]:
        """Context manager for streaming HTTP responses.

        This method provides a context manager for streaming large files or responses
        from the Dataverse API without loading the entire content into memory. It's
        particularly useful for downloading large datasets or files.

        Args:
            url (str): The full URL to stream from.
            params (Optional[Dict[str, Any]]): Optional query parameters to include
                in the request.
            headers (Optional[Dict[str, str]]): Optional HTTP headers to include
                in the request. If provided, the User-Agent header will be added
                automatically.

        Yields:
            httpx.Response: A streaming HTTP response object that can be used to
                read the response content in chunks.

        Example:
            >>> api = Api(base_url="https://demo.dataverse.org")
            >>> with api.stream_file_context("https://example.com/largefile.zip") as response:
            ...     for chunk in response.iter_bytes():
            ...         # Process chunk
            ...         pass

        Note:
            The response should be consumed within the context manager. The connection
            will be closed automatically when exiting the context.
        """
        if headers:
            headers.update({"User-Agent": "pydataverse"})
        else:
            headers = {"User-Agent": "pydataverse"}

        with httpx.stream(
            "GET",
            url,
            headers=headers,
            params=params,
            auth=self.auth,
            follow_redirects=True,
        ) as response:
            yield response

    @overload
    def post_request(
        self,
        url: str,
        response_model: None = None,
        data: Optional[Dict[str, Any] | str] = None,
        auth=DEPRECATION_GUARD,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> httpx.Response:
        """Synchronous POST request returning raw HTTP response.

        This overload is used when no response_model is provided and use_async=False.
        The method will execute synchronously and return the raw httpx.Response object.

        Args:
            url: Full URL for the request
            response_model: Must be None for this overload
            data: Optional request body data
            auth: Deprecated authentication parameter
            params: Optional query parameters
            files: Optional files to upload
            use_async: Must be False for this overload

        Returns:
            httpx.Response: Raw HTTP response object
        """
        ...

    @overload
    def post_request(
        self,
        url: str,
        response_model: None = None,
        data: Optional[Dict[str, Any] | str] = None,
        auth=DEPRECATION_GUARD,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = True,
        follow_redirects: bool = True,
    ) -> Coroutine[Any, Any, httpx.Response]:
        """Asynchronous POST request returning coroutine of raw HTTP response.

        This overload is used when no response_model is provided and use_async=True.
        The method will return a coroutine that yields the raw httpx.Response object.

        Args:
            url: Full URL for the request
            response_model: Must be None for this overload
            data: Optional request body data
            auth: Deprecated authentication parameter
            params: Optional query parameters
            files: Optional files to upload
            use_async: Must be True for this overload

        Returns:
            Coroutine[Any, Any, httpx.Response]: Coroutine yielding raw HTTP response
        """
        ...

    @overload
    def post_request(
        self,
        url: str,
        response_model: Type[T],
        data: Optional[Dict[str, Any] | str] = None,
        auth=DEPRECATION_GUARD,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> T:
        """Synchronous POST request returning parsed Pydantic model.

        This overload is used when a specific Pydantic model type is provided.
        The method will execute synchronously, parse the response, and return
        a validated instance of the specified model.

        Args:
            url: Full URL for the request
            response_model: Pydantic model class to parse response into
            data: Optional request body data
            auth: Deprecated authentication parameter
            params: Optional query parameters
            files: Optional files to upload
            use_async: Whether to execute asynchronously

        Returns:
            T: Validated instance of the specified Pydantic model
        """
        ...

    @overload
    def post_request(
        self,
        url: str,
        response_model: Type[List[T]],
        data: Optional[Dict[str, Any] | str] = None,
        auth=DEPRECATION_GUARD,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> List[T]:
        """Synchronous POST request returning list of parsed Pydantic models.

        This overload is used when a List[Model] type is provided.
        The method will execute synchronously, parse the response as a collection,
        and return a list of validated model instances.

        Args:
            url: Full URL for the request
            response_model: List type annotation containing Pydantic model class
            data: Optional request body data
            auth: Deprecated authentication parameter
            params: Optional query parameters
            files: Optional files to upload
            use_async: Whether to execute asynchronously

        Returns:
            List[T]: List of validated Pydantic model instances
        """
        ...

    def post_request(
        self,
        url,
        response_model: Optional[Type[BaseModel] | Type[List[BaseModel]]] = None,
        data: Optional[Dict[str, Any] | str] = None,
        auth=DEPRECATION_GUARD,
        params: Optional[Dict[str, Any]] = None,
        files=None,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> RequestResponse:
        """Makes a POST request.

        Args:
            url (str): Full URL.
            data (str, optional): Metadata as a json-formatted string.
            auth (Any, optional): Deprecated. Use Api instance auth instead.
            files (dict, optional): Files to upload, e.g. {'file': open('sample_file.txt','rb')}
            params (dict, optional): Dictionary of parameters for the request.
            response_model (Type[BaseModel], optional): Pydantic model to parse the response into.

        Returns:
            httpx.Response: Response from the request.

        Deprecated:
            0.3.4: The auth parameter was ignored before version 0.3.4.
            Please pass your auth to the Api instance directly.
        """

        if isinstance(data, str):
            data = json.loads(data)

        # Decide whether to use 'data' or 'json' args
        request_params = self._check_json_data_form(data)  # type: ignore

        if headers:
            headers.update({"User-Agent": "pydataverse"})
        else:
            headers = {"User-Agent": "pydataverse"}

        if not use_async and self.client is None:
            return self._sync_request(
                method=httpx.post,
                url=url,
                headers=headers,
                params=params,
                files=files,
                response_model=response_model,
                **request_params,
                follow_redirects=follow_redirects,
            )
        else:
            if self.client is None:
                raise ValueError("Async client is not initialized.")

            return self._async_request(
                method=self.client.post,
                url=url,
                headers=headers,
                params=params,
                files=files,
                response_model=response_model,
                follow_redirects=follow_redirects,
                **request_params,
            )

    @overload
    def put_request(
        self,
        url: str,
        response_model: None = None,
        data: Optional[Dict[str, Any] | str | bool] = None,
        auth=DEPRECATION_GUARD,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> httpx.Response:
        """Synchronous PUT request returning raw HTTP response.

        This overload is used when no response_model is provided and use_async=False.
        The method will execute synchronously and return the raw httpx.Response object.

        Args:
            url: Full URL for the request
            response_model: Must be None for this overload
            data: Optional request body data
            auth: Deprecated authentication parameter
            params: Optional query parameters
            use_async: Must be False for this overload

        Returns:
            httpx.Response: Raw HTTP response object
        """
        ...

    @overload
    def put_request(
        self,
        url: str,
        response_model: None = None,
        data: Optional[Dict[str, Any] | str] = None,
        auth=DEPRECATION_GUARD,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = True,
        follow_redirects: bool = True,
    ) -> Coroutine[Any, Any, httpx.Response]:
        """Asynchronous PUT request returning coroutine of raw HTTP response.

        This overload is used when no response_model is provided and use_async=True.
        The method will return a coroutine that yields the raw httpx.Response object.

        Args:
            url: Full URL for the request
            response_model: Must be None for this overload
            data: Optional request body data
            auth: Deprecated authentication parameter
            params: Optional query parameters
            use_async: Must be True for this overload

        Returns:
            Coroutine[Any, Any, httpx.Response]: Coroutine yielding raw HTTP response
        """
        ...

    @overload
    def put_request(
        self,
        url: str,
        response_model: Type[T],
        data: Optional[Dict[str, Any] | str] = None,
        auth=DEPRECATION_GUARD,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> T:
        """Synchronous PUT request returning parsed Pydantic model.

        This overload is used when a specific Pydantic model type is provided.
        The method will execute synchronously, parse the response, and return
        a validated instance of the specified model.

        Args:
            url: Full URL for the request
            response_model: Pydantic model class to parse response into
            data: Optional request body data
            auth: Deprecated authentication parameter
            params: Optional query parameters
            use_async: Whether to execute asynchronously

        Returns:
            T: Validated instance of the specified Pydantic model
        """
        ...

    @overload
    def put_request(
        self,
        url: str,
        response_model: Type[List[T]],
        data: Optional[Dict[str, Any] | str] = None,
        auth=DEPRECATION_GUARD,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> List[T]:
        """Synchronous PUT request returning list of parsed Pydantic models.

        This overload is used when a List[Model] type is provided.
        The method will execute synchronously, parse the response as a collection,
        and return a list of validated model instances.

        Args:
            url: Full URL for the request
            response_model: List type annotation containing Pydantic model class
            data: Optional request body data
            auth: Deprecated authentication parameter
            params: Optional query parameters
            use_async: Whether to execute asynchronously

        Returns:
            List[T]: List of validated Pydantic model instances
        """
        ...

    def put_request(
        self,
        url,
        response_model: Optional[Type[BaseModel] | Type[List[BaseModel]]] = None,
        data: Optional[Dict[str, Any] | str | bool] = None,
        auth=DEPRECATION_GUARD,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> RequestResponse:
        """Makes a PUT request.

        Args:
            url (str): Full URL.
            data (str, optional): Metadata as a json-formatted string.
            auth (Any, optional): Deprecated. Use Api instance auth instead.
            params (dict, optional): Dictionary of parameters for the request.
            response_model (Type[BaseModel], optional): Pydantic model to parse the response into.
        Returns:
            httpx.Response: Response from the request.

        Deprecated:
            0.3.4: The auth parameter was ignored before version 0.3.4.
            Please pass your auth to the Api instance directly.
        """

        if isinstance(data, str):
            data = json.loads(data)

        # Decide whether to use 'data' or 'json' args
        request_params = self._check_json_data_form(data)  # type: ignore

        if headers:
            headers.update({"User-Agent": "pydataverse"})
        else:
            headers = {"User-Agent": "pydataverse"}

        if not use_async and self.client is None:
            return self._sync_request(
                method=httpx.put,
                url=url,
                headers=headers,
                params=params,
                response_model=response_model,
                follow_redirects=follow_redirects,
                **request_params,
            )
        else:  # use_async is True
            if self.client is None:
                raise ValueError("Async client is not initialized.")

            return self._async_request(
                method=self.client.put,
                url=url,
                headers=headers,
                params=params,
                response_model=response_model,
                follow_redirects=follow_redirects,
                **request_params,
            )

    @overload
    def delete_request(
        self,
        url,
        response_model: None = None,
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> httpx.Response:
        """Synchronous GET request returning raw HTTP response.

        This overload is used when no response_model is provided and use_async=False.
        The method will execute synchronously and return the raw httpx.Response object.

        Args:
            url: Full URL for the request
            response_model: Must be None for this overload
            params: Optional query parameters
            auth: Deprecated authentication parameter
            use_async: Must be False for this overload

        Returns:
            httpx.Response: Raw HTTP response object
        """
        ...

    @overload
    def delete_request(
        self,
        url,
        response_model: None = None,
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = True,
        follow_redirects: bool = True,
    ) -> Coroutine[Any, Any, httpx.Response]:
        """Asynchronous GET request returning coroutine of raw HTTP response.

        This overload is used when no response_model is provided and use_async=True.
        The method will return a coroutine that yields the raw httpx.Response object.

        Args:
            url: Full URL for the request
            response_model: Must be None for this overload
            params: Optional query parameters
            auth: Deprecated authentication parameter
            use_async: Must be True for this overload

        Returns:
            Coroutine[Any, Any, httpx.Response]: Coroutine yielding raw HTTP response
        """
        ...

    @overload
    def delete_request(
        self,
        url,
        response_model: Type[T],
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> T:
        """Synchronous GET request returning parsed Pydantic model.

        This overload is used when a specific Pydantic model type is provided.
        The method will execute synchronously, parse the response, and return
        a validated instance of the specified model.

        Args:
            url: Full URL for the request
            response_model: Pydantic model class to parse response into
            params: Optional query parameters
            auth: Deprecated authentication parameter
            use_async: Whether to execute asynchronously

        Returns:
            T: Validated instance of the specified Pydantic model
        """
        ...

    @overload
    def delete_request(
        self,
        url,
        response_model: Type[List[T]],
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> List[T]:
        """Synchronous GET request returning list of parsed Pydantic models.

        This overload is used when a List[Model] type is provided.
        The method will execute synchronously, parse the response as a collection,
        and return a list of validated model instances.

        Args:
            url: Full URL for the request
            response_model: List type annotation containing Pydantic model class
            params: Optional query parameters
            auth: Deprecated authentication parameter
            use_async: Whether to execute asynchronously

        Returns:
            List[T]: List of validated Pydantic model instances
        """
        ...

    def delete_request(
        self,
        url,
        response_model: Optional[Type[BaseModel] | Type[List[BaseModel]]] = None,
        params=None,
        auth=DEPRECATION_GUARD,
        headers: Optional[Dict[str, str]] = None,
        use_async: bool = False,
        follow_redirects: bool = True,
    ) -> RequestResponse:
        """Makes a DELETE request.

        Args:
            url (str): Full URL.
            auth (Any, optional): Deprecated. Use Api instance auth instead.
            params (dict, optional): Dictionary of parameters for the request.
            response_model (Type[BaseModel], optional): Pydantic model to parse the response into.
        Returns:
            httpx.Response: Response from the request.

        Deprecated:
            0.3.4: The auth parameter was ignored before version 0.3.4.
            Please pass your auth to the Api instance directly.
        """

        if headers:
            headers.update({"User-Agent": "pydataverse"})
        else:
            headers = {"User-Agent": "pydataverse"}

        if not use_async and self.client is None:
            return self._sync_request(
                method=httpx.delete,
                url=url,
                headers=headers,
                params=params,
                response_model=response_model,
                follow_redirects=follow_redirects,
            )
        else:
            if self.client is None:
                raise ValueError("Async client is not initialized.")

            return self._async_request(
                method=self.client.delete,
                url=url,
                headers=headers,
                params=params,
                response_model=response_model,
                follow_redirects=follow_redirects,
            )

    @staticmethod
    def _check_json_data_form(data: Optional[Dict]):
        """Checks and distributes given payload to match Dataverse expectations.

        In the case of form-data keyed by "jsonData", Dataverse expects the payload
        as a string in form of a dictionary. This is not possible using HTTPXs json
        parameter, so we need to handle this case separately.

        Args:
            data (Optional[Dict]): The data payload to check.

        Returns:
            dict: Processed data in correct format.

        Raises:
            ValueError: If data is not a dictionary.
        """

        if data is None:
            return {}
        elif not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")
        elif "jsonData" not in data:
            return {"json": data}

        assert list(data.keys()) == ["jsonData"], (
            "jsonData must be the only key in the dictionary."
        )

        # Content of JSON data should ideally be a string
        content = data["jsonData"]
        if not isinstance(content, str):
            data["jsonData"] = json.dumps(content)

        return {"data": data}

    @overload
    def _sync_request(
        self,
        method,
        response_model: Type[BaseModel],
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> BaseModel:
        """Synchronous request returning parsed Pydantic model.

        This overload is used when a response_model is provided. The method will
        parse the response and return a validated Pydantic model instance or
        list of instances.

        Args:
            method: HTTP method function to use
            response_model: Pydantic model class or List type to parse response into
            **kwargs: Additional request parameters

        Returns:
            BaseModel: Validated Pydantic model instance or list of instances
        """
        ...

    @overload
    def _sync_request(
        self,
        method,
        response_model: Type[List[BaseModel]],
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> List[BaseModel]:
        """Synchronous request returning parsed Pydantic model.

        This overload is used when a response_model is provided. The method will
        parse the response and return a validated Pydantic model instance or
        list of instances.

        Args:
            method: HTTP method function to use
            response_model: Pydantic model class or List type to parse response into
            **kwargs: Additional request parameters

        Returns:
            BaseModel: Validated Pydantic model instance or list of instances
        """
        ...

    @overload
    def _sync_request(
        self,
        method,
        response_model: None = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> httpx.Response:
        """Synchronous request returning raw HTTP response.

        This overload is used when no response_model is provided. The method will
        return the raw httpx.Response object without parsing.

        Args:
            method: HTTP method function to use
            response_model: Must be None for this overload
            **kwargs: Additional request parameters

        Returns:
            httpx.Response: Raw HTTP response object
        """
        ...

    @overload
    def _sync_request(
        self,
        method,
        response_model: Type[A],
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> A:
        """Synchronous request returning Any type.

        This overload is used when Any is provided as response_model. The method will
        return the raw httpx.Response object without parsing.

        Args:
            method: HTTP method function to use
            response_model: Must be None for this overload
            **kwargs: Additional request parameters

        Returns:
            httpx.Response: Raw HTTP response object
        """
        ...

    @overload
    def _sync_request(
        self,
        method,
        response_model: Type[List[A]],
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> List[A]:
        """Synchronous request returning Any type.

        This overload is used when Any is provided as response_model. The method will
        return the raw httpx.Response object without parsing.

        Args:
            method: HTTP method function to use
            response_model: Must be None for this overload
            **kwargs: Additional request parameters

        Returns:
            httpx.Response: Raw HTTP response object
        """
        ...

    def _sync_request(
        self,
        method,
        response_model: Optional[ResponseModels] = None,
        headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
        **kwargs,
    ):
        """
        Sends a synchronous request to the specified URL using the specified HTTP method.

        Args:
            method (function): The HTTP method to use for the request.
            response_model (Optional[Type[BaseModel] | Type[List[BaseModel]]]):
                Optional Pydantic model class or List of model classes to validate
                and parse the response data. If provided, returns a validated model
                instance or list of instances. If None, returns the raw httpx.Response.
            **kwargs: Additional keyword arguments to be passed to the method.
                Must include 'url' parameter.

        Returns:
            Union[BaseModel, List[BaseModel], httpx.Response]:
                If response_model is provided, returns a validated Pydantic model
                instance or list of instances. Otherwise, returns the raw
                httpx.Response object.

        Raises:
            ApiAuthorizationError: If the response status code is 401 (Authorization error).
            ConnectError: If a connection to the API cannot be established.
            AssertionError: If 'url' is not provided in kwargs.
        """
        assert "url" in kwargs, "URL is required for a request."

        kwargs = self._filter_kwargs(kwargs)
        model, is_collection = self._extract_model(response_model)
        headers = self._add_default_headers(headers)

        try:
            response: httpx.Response = method(
                **kwargs,
                auth=self.auth,
                follow_redirects=follow_redirects,
                timeout=self.timeout,
                headers=headers,
            )

            if not follow_redirects:
                # Do not process response if follow_redirects is False
                # This is mostly used to extract the redirect URL for
                # DataFile downloads.
                return response

            return self._handle_response(response, model, is_collection)

        except ConnectError:
            raise ConnectError(
                "ERROR - Could not establish connection to api '{0}'.".format(
                    kwargs["url"]
                )
            )

    @overload
    def _async_request(
        self,
        method,
        response_model: Type[BaseModel] | Type[List[BaseModel]],
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Coroutine[Any, Any, BaseModel]:
        """Asynchronous request returning coroutine of parsed Pydantic model.

        This overload is used when a response_model is provided. The method will
        return a coroutine that yields a validated Pydantic model instance or
        list of instances.

        Args:
            method: Async HTTP method function to use
            response_model: Pydantic model class or List type to parse response into
            **kwargs: Additional request parameters

        Returns:
            Coroutine[Any, Any, BaseModel]: Coroutine yielding validated model instance(s)
        """
        ...

    @overload
    def _async_request(
        self,
        method,
        response_model: Optional[Type[BaseModel] | Type[List[BaseModel]]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Coroutine[Any, Any, httpx.Response]:
        """Asynchronous request returning coroutine of raw HTTP response.

        This overload is used when no response_model is provided. The method will
        return a coroutine that yields the raw httpx.Response object.

        Args:
            method: Async HTTP method function to use
            response_model: Must be None for this overload
            **kwargs: Additional request parameters

        Returns:
            Coroutine[Any, Any, httpx.Response]: Coroutine yielding raw HTTP response
        """
        ...

    async def _async_request(  # type: ignore
        self,
        method,
        response_model: Optional[Type[BaseModel] | Type[List[BaseModel]]] = None,
        headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
        **kwargs,
    ):
        """
        Sends an asynchronous request to the specified URL using the specified HTTP method.

        Args:
            method (callable): The HTTP method to use for the request (async callable).
            response_model (Optional[Type[BaseModel] | Type[List[BaseModel]]]):
                Optional Pydantic model class or List of model classes to validate
                and parse the response data. If provided, returns a validated model
                instance or list of instances. If None, returns the raw httpx.Response.
            **kwargs: Additional keyword arguments to be passed to the method.
                Must include 'url' parameter.

        Returns:
            Union[BaseModel, List[BaseModel], httpx.Response]:
                If response_model is provided, returns a validated Pydantic model
                instance or list of instances. Otherwise, returns the raw
                httpx.Response object.

        Raises:
            ApiAuthorizationError: If the response status code is 401 (Authorization error).
            ConnectError: If a connection to the API cannot be established.
            AssertionError: If 'url' is not provided in kwargs.
        """
        assert "url" in kwargs, "URL is required for a request."

        kwargs = self._filter_kwargs(kwargs)
        model, is_collection = self._extract_model(response_model)
        headers = self._add_default_headers(headers)

        try:
            response: httpx.Response = await method(
                **kwargs,
                auth=self.auth,
                follow_redirects=follow_redirects,
                timeout=self.timeout,
            )

            if not follow_redirects:
                # Do not process response if follow_redirects is False
                # This is mostly used to extract the redirect URL for
                # DataFile downloads.
                return response

            return self._handle_response(response, model, is_collection)

        except ConnectError:
            raise ConnectError(
                "ERROR - Could not establish connection to api '{0}'.".format(
                    kwargs["url"]
                )
            )

    def _add_default_headers(
        self,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        if headers:
            headers.update({"User-Agent": "pydataverse"})
        else:
            headers = {"User-Agent": "pydataverse"}
        return headers

    def _handle_response(
        self,
        resp: httpx.Response,
        model: Optional[Type[BaseModel] | Type[List[A]] | Type[bytes] | Type[str]],
        is_collection: bool,
    ):
        """
        Handles and processes HTTP response based on the provided model configuration.

        Args:
            resp: The HTTP response object to process.
            model: The Pydantic model class to use for validation and parsing.
                If None, returns the raw response.
            is_collection: Whether the response should be treated as a
                collection/list of model instances.

        Returns:
            If model is provided and is_collection is True, returns a list of
            validated model instances. If model is provided and is_collection
            is False, returns a single validated model instance. If model is
            None, returns the raw httpx.Response.

        Raises:
            HTTPStatusError: If the response indicates an error status.
        """

        try:
            body = resp.json()
            text = None
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {}
            if model is bytes:
                text = resp.content
            else:
                text = resp.text

        # Raise for status if not 200 and no error message present
        if resp.is_error and "message" not in body:
            self.logger.error(f"ERROR: HTTP {resp.status_code} - {resp.text}")
            resp.raise_for_status()

        if text is not None:
            return text

        # Parse response into APIResponse format
        try:
            content = APIResponse.model_validate(body)
        except ValidationError:
            content = APIResponse.from_out_of_format(
                data=body,
                status_code=resp.status_code,
            )

        # Check API-level status
        if content.status != Status.OK:
            self.logger.error(f"ERROR: HTTP {resp.status_code} - {content.message}")
            raise HTTPStatusError(
                request=resp.request,
                response=resp,
                message=f"ERROR: HTTP {resp.status_code} - {content.message}",
            )

        if self.verbose:
            self.logger.success(
                f"{self.__class__.__name__} - HTTP {resp.status_code} - {resp.request.url}"
            )

        # Return raw response if no model specified
        if model is None:
            return resp

        # Process data based on model type
        data = content.data

        if is_collection:
            # Handle Union types using TypeAdapter
            if model is not None and self._is_union(model):
                # Use TypeAdapter to validate each item against the Union
                adapter = TypeAdapter(model)
                return [adapter.validate_python(item) for item in data]
            elif model is not None and issubclass(model, BaseModel):
                return [model.model_validate(item) for item in data]
            else:
                return data
        else:
            # Handle Union types for single items
            if model is not None and self._is_union(model):
                adapter = TypeAdapter(model)
                return adapter.validate_python(data)
            elif model is not None and issubclass(model, BaseModel):
                return model.model_validate(data)
            else:
                return data

    def _is_union(self, model) -> bool:
        return get_origin(model) is Union or get_origin(model) is UnionType

    @staticmethod
    def _extract_model(
        response_model: Optional[ResponseModels],
    ) -> tuple[Optional[Type[BaseModel]], bool]:
        """
        Extracts and analyzes the response model to determine processing strategy.

        Args:
            response_model (Optional[Type[BaseModel] | Type[List[BaseModel]]]):
                The response model type annotation, which can be a single
                BaseModel class, a List of BaseModel classes, or None.

        Returns:
            tuple[Optional[Type[BaseModel]], bool]: A tuple containing:
                - model: The extracted BaseModel class or None
                - is_collection: Boolean indicating if the response should be
                  treated as a collection/list
        """

        is_collection = get_origin(response_model) is list
        args = get_args(response_model)

        if response_model:
            if args:
                return args[0], is_collection
            else:
                return response_model, is_collection  # type: ignore
        else:
            return response_model, is_collection  # type: ignore

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

    @overload
    def _parse_payload(
        self,
        payload: Dict[str, Any] | str | BaseModel,
        model: Type[T],
    ) -> T:
        """Parse payload with a specific BaseModel type.

        Args:
            payload: Raw payload data as string or dictionary
            model: BaseModel class to validate against

        Returns:
            Validated BaseModel instance
        """
        ...

    @overload
    def _parse_payload(
        self,
        payload: Dict[str, Any] | str | BaseModel,
        model: None,
    ) -> Dict[str, Any]:
        """Parse payload without model validation.

        Args:
            payload: Raw payload data as string or dictionary
            model: Must be None for this overload

        Returns:
            Dictionary representation of the payload
        """
        ...

    def _parse_payload(
        self,
        payload: Dict[str, Any] | str | BaseModel,
        model: Optional[Type[BaseModel]],
    ) -> Union[BaseModel, Dict[str, Any]]:
        """Parse and optionally validate payload data.

        Processes raw payload data (string, dictionary, or BaseModel) and either
        returns it as a dictionary or validates it against a specified BaseModel.

        Args:
            payload: The raw payload data. Can be:
                - JSON string: Will be parsed to dictionary or validated
                - Dictionary: Will be returned as-is or validated
                - BaseModel: Currently not supported, raises ValueError
            model: Optional BaseModel class for validation. If None, returns
                raw dictionary without validation.

        Returns:
            Either a validated BaseModel instance (if model provided) or
            a dictionary representation of the payload (if model is None).

        Raises:
            ValueError: If payload type is not supported or if BaseModel
                instance is passed as payload.
        """
        if model is None:
            if isinstance(payload, str):
                return json.loads(payload)
            elif isinstance(payload, dict):
                return payload
            else:
                raise ValueError(
                    "Payload must be a string or dictionary when no model is specified."
                )
        else:
            if isinstance(payload, BaseModel):
                return payload
            elif isinstance(payload, str):
                return model.model_validate_json(payload)
            elif isinstance(payload, dict):
                return model.model_validate(payload)
            else:
                raise ValueError(
                    "Payload must be a string or dictionary for model validation."
                )

    def _assemble_url(self, path: str) -> str:
        """Assemble a complete URL by joining the API base URL with a given path.

        Args:
            path: The path to append to the API base URL.

        Returns:
            str: The complete URL formed by joining the base URL and path.
        """
        return urljoin(self.api_base_url, path)

    def _is_pid(self, identifier: str | int) -> bool:
        """Check if the identifier is a persistent identifier.

        Args:
            identifier: The identifier to check.

        Returns:
            bool: True if the identifier is a persistent identifier, False otherwise.
        """
        try:
            int(identifier)
            return False
        except ValueError:
            return True

    def _setup_async_client(self):
        self.client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=self.timeout,
            limits=httpx.Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_keepalive_connections,
            ),
        )

    async def __aenter__(self):
        """
        Context manager method that initializes an instance of httpx.AsyncClient.

        Returns:
            httpx.AsyncClient: An instance of httpx.AsyncClient.
        """
        if not self.client:
            self._setup_async_client()

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Closes the client connection when exiting a context manager.

        Args:
            exc_type (type): The type of the exception raised, if any.
            exc_value (Exception): The exception raised, if any.
            traceback (traceback): The traceback object associated with the exception, if any.
        """

        if self.client:
            await self.client.aclose()
            self.client = None
