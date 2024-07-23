import os
import httpx
import pytest
from httpx import Response
from time import sleep
from pyDataverse.api import DataAccessApi, NativeApi, SwordApi
from pyDataverse.auth import ApiTokenAuth
from pyDataverse.exceptions import ApiAuthorizationError
from pyDataverse.exceptions import ApiUrlError
from pyDataverse.models import Dataset
from pyDataverse.utils import read_file
from ..conftest import test_config


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class TestApiConnect(object):
    """Test the NativeApi() class initialization."""

    def test_api_connect(self, native_api):
        sleep(test_config["wait_time"])

        assert isinstance(native_api, NativeApi)
        assert not native_api.api_token
        assert native_api.api_version == "v1"
        assert native_api.base_url == os.getenv("BASE_URL").rstrip("/")
        assert native_api.base_url_api_native == "{0}/api/{1}".format(
            os.getenv("BASE_URL").rstrip("/"), native_api.api_version
        )

    def test_api_connect_base_url_wrong(self):
        """Test native_api connection with wrong `base_url`."""
        # None
        with pytest.raises(ApiUrlError):
            NativeApi(None)


class TestApiTokenAndAuthBehavior:
    def test_api_token_none_and_auth_none(self):
        api = NativeApi("https://demo.dataverse.org")
        assert api.api_token is None
        assert api.auth is None

    def test_api_token_none_and_auth(self):
        auth = ApiTokenAuth("mytoken")
        api = NativeApi("https://demo.dataverse.org", auth=auth)
        assert api.api_token is None
        assert api.auth is auth

    def test_api_token_and_auth(self):
        auth = ApiTokenAuth("mytoken")
        # Only one, api_token or auth, should be specified
        with pytest.warns(UserWarning):
            api = NativeApi(
                "https://demo.dataverse.org", api_token="sometoken", auth=auth
            )
        assert api.api_token is None
        assert api.auth is auth

    def test_api_token_and_auth_none(self):
        api_token = "mytoken"
        api = NativeApi("https://demo.dataverse.org", api_token)
        assert api.api_token == api_token
        assert isinstance(api.auth, ApiTokenAuth)
        assert api.auth.api_token == api_token


class TestApiRequests(object):
    """Test the native_api requests."""

    dataset_id = None

    @classmethod
    def setup_class(cls):
        """Create the native_api connection for later use."""
        cls.dataverse_id = "test-pyDataverse"
        cls.dataset_id = None

    def test_get_request(self, native_api):
        """Test successful `.get_request()` request."""
        # TODO: test params und auth default
        base_url = os.getenv("BASE_URL").rstrip("/")
        query_str = base_url + "/api/v1/info/server"
        resp = native_api.get_request(query_str)
        sleep(test_config["wait_time"])

        assert isinstance(resp, Response)

    def test_get_dataverse(self, native_api):
        """Test successful `.get_dataverse()` request`."""
        resp = native_api.get_dataverse(":root")
        sleep(test_config["wait_time"])

        assert isinstance(resp, Response)


if not os.environ.get("TRAVIS"):

    class TestApiToken(object):
        """Test user rights."""

        def test_token_missing(self):
            BASE_URL = os.getenv("BASE_URL").rstrip("/")
            api = NativeApi(BASE_URL)
            resp = api.get_info_version()
            assert resp.json()["data"]["version"] == os.getenv("DV_VERSION")
            # assert resp.json()["data"]["build"] == "267-a91d370"

            with pytest.raises(ApiAuthorizationError):
                ds = Dataset()
                ds.from_json(
                    read_file(
                        os.path.join(
                            BASE_DIR, "tests/data/dataset_upload_min_default.json"
                        )
                    )
                )
                api.create_dataset(":root", ds.json())

        def test_token_empty_string(self):
            BASE_URL = os.getenv("BASE_URL").rstrip("/")
            api = NativeApi(BASE_URL, "")
            resp = api.get_info_version()
            assert resp.json()["data"]["version"] == os.getenv("DV_VERSION")
            # assert resp.json()["data"]["build"] == "267-a91d370"

            with pytest.raises(ApiAuthorizationError):
                ds = Dataset()
                ds.from_json(
                    read_file(
                        os.path.join(
                            BASE_DIR, "tests/data/dataset_upload_min_default.json"
                        )
                    )
                )
                api.create_dataset(":root", ds.json())

        # def test_token_no_rights(self):
        #     BASE_URL = os.getenv("BASE_URL")
        #     API_TOKEN = os.getenv("API_TOKEN_NO_RIGHTS")
        #     api = NativeApi(BASE_URL, API_TOKEN)
        #     resp = api.get_info_version()
        #     assert resp.json()["data"]["version"] == os.getenv("DV_VERSION")
        #     assert resp.json()["data"]["build"] == "267-a91d370"

        #     with pytest.raises(ApiAuthorizationError):
        #         ds = Dataset()
        #         ds.from_json(
        #             read_file(
        #                 os.path.join(
        #                     BASE_DIR, "tests/data/dataset_upload_min_default.json"
        #                 )
        #             )
        #         )
        #         api.create_dataset(":root", ds.json())

        def test_token_right_create_dataset_rights(self):
            BASE_URL = os.getenv("BASE_URL").rstrip("/")
            api_su = NativeApi(BASE_URL, os.getenv("API_TOKEN_SUPERUSER"))
            # api_nru = NativeApi(BASE_URL, os.getenv("API_TOKEN_TEST_NO_RIGHTS"))

            resp = api_su.get_info_version()
            assert resp.json()["data"]["version"] == os.getenv("DV_VERSION")
            # assert resp.json()["data"]["build"] == "267-a91d370"
            # resp = api_nru.get_info_version()
            # assert resp.json()["data"]["version"] == os.getenv("DV_VERSION")
            # assert resp.json()["data"]["build"] == "267-a91d370"

            ds = Dataset()
            ds.from_json(
                read_file(
                    os.path.join(BASE_DIR, "tests/data/dataset_upload_min_default.json")
                )
            )
            resp = api_su.create_dataset(":root", ds.json())
            pid = resp.json()["data"]["persistentId"]
            assert resp.json()["status"] == "OK"

            # with pytest.raises(ApiAuthorizationError):
            #     resp = api_nru.get_dataset(pid)

            resp = api_su.delete_dataset(pid)
            assert resp.json()["status"] == "OK"

        def test_token_should_not_be_exposed_on_error(self):
            BASE_URL = os.getenv("BASE_URL")
            API_TOKEN = os.getenv("API_TOKEN")
            api = DataAccessApi(BASE_URL, API_TOKEN)

            result = api.get_datafile("does-not-exist").json()
            assert API_TOKEN not in result["requestUrl"]

        @pytest.mark.parametrize(
            "auth", (True, False, "api-token", ApiTokenAuth("some-token"))
        )
        def test_using_auth_on_individual_requests_is_deprecated(self, auth):
            BASE_URL = os.getenv("BASE_URL")
            API_TOKEN = os.getenv("API_TOKEN")
            api = DataAccessApi(BASE_URL, auth=ApiTokenAuth(API_TOKEN))
            with pytest.warns(DeprecationWarning):
                api.get_datafile("does-not-exist", auth=auth)

        @pytest.mark.parametrize(
            "auth", (True, False, "api-token", ApiTokenAuth("some-token"))
        )
        def test_using_auth_on_individual_requests_is_deprecated_unauthorized(
            self, auth
        ):
            BASE_URL = os.getenv("BASE_URL")
            no_auth_api = DataAccessApi(BASE_URL)
            with pytest.warns(DeprecationWarning):
                no_auth_api.get_datafile("does-not-exist", auth=auth)

        def test_sword_api_requires_http_basic_auth(self):
            BASE_URL = os.getenv("BASE_URL")
            API_TOKEN = os.getenv("API_TOKEN")
            api = SwordApi(BASE_URL, api_token=API_TOKEN)
            assert isinstance(api.auth, httpx.BasicAuth)

        def test_sword_api_can_authenticate(self):
            BASE_URL = os.getenv("BASE_URL")
            API_TOKEN = os.getenv("API_TOKEN")
            api = SwordApi(BASE_URL, api_token=API_TOKEN)
            response = api.get_service_document()
            assert response.status_code == 200

        def test_sword_api_cannot_authenticate_without_token(self):
            BASE_URL = os.getenv("BASE_URL")
            api = SwordApi(BASE_URL)
            with pytest.raises(ApiAuthorizationError):
                api.get_service_document()
