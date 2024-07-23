"""This module contains authentication handlers compatible with :class:`httpx.Auth`"""

from typing import Generator

from httpx import Auth, Request, Response

from pyDataverse.exceptions import ApiAuthorizationError


class ApiTokenAuth(Auth):
    """An authentication handler to add an API token as the X-Dataverse-key
    header.

    For more information on how to retrieve an API token and how it is used,
    please refer to https://guides.dataverse.org/en/latest/api/auth.html.
    """

    def __init__(self, api_token: str):
        """Initializes the auth handler with an API token.

        Parameters
        ----------
        api_token : str
            The API token retrieved from your Dataverse instance user profile.

        Examples
        --------

            >>> import os
            >>> from pyDataverse.api import DataAccessApi
            >>> base_url = 'https://demo.dataverse.org'
            >>> api_token_auth = ApiTokenAuth(os.getenv('API_TOKEN'))
            >>> api = DataAccessApi(base_url, api_token_auth)

        """
        if not isinstance(api_token, str):
            raise ApiAuthorizationError("API token passed is not a string.")
        self.api_token = api_token

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        """Adds the X-Dataverse-key header with the API token and yields the
        original :class:`httpx.Request`.

        Parameters
        ----------
        request : httpx.Request
            The request object which requires authentication headers

        Yields
        ------
        httpx.Request
            The original request with modified headers
        """
        request.headers["X-Dataverse-key"] = self.api_token
        yield request


class BearerTokenAuth(Auth):
    """An authentication handler to add a Bearer token as defined in `RFC 6750
    <https://datatracker.ietf.org/doc/html/rfc6750>`_ to the request.

    A bearer token could be obtained from an OIDC provider, for example,
    Keycloak.
    """

    def __init__(self, bearer_token: str):
        """Initializes the auth handler with a bearer token.

        Parameters
        ----------
        bearer_token : str
            The bearer token retrieved from your OIDC provider.

        Examples
        --------

            >>> import os
            >>> from pyDataverse.api import DataAccessApi
            >>> base_url = 'https://demo.dataverse.org'
            >>> bearer_token_auth = OAuthBearerTokenAuth(os.getenv('OAUTH_TOKEN'))
            >>> api = DataAccessApi(base_url, bearer_token_auth)

        """
        if not isinstance(bearer_token, str):
            raise ApiAuthorizationError("API token passed is not a string.")
        self.bearer_token = bearer_token

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        """Adds the X-Dataverse-key header with the API token and yields the
        original :class:`httpx.Request`.

        Parameters
        ----------
        request : httpx.Request
            The request object which requires authentication headers

        Yields
        ------
        httpx.Request
            The original request with modified headers
        """
        request.headers["Authorization"] = f"Bearer {self.bearer_token}"
        yield request
