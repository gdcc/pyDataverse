import httpx

from pyDataverse.api.api import Api
from pyDataverse.exceptions import ApiUrlError


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
