import pytest
from requests import get
from ..conftest import BASE_URL


class TestInit(object):
    pass


class TestUrls(object):
    @pytest.mark.vcr()
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (f"{BASE_URL}/api/", ("ERROR", 404)),
            (f"{BASE_URL}/api/v1/", ("ERROR", 404)),
            (f"{BASE_URL}/api/info", ("ERROR", 404)),
            (f"{BASE_URL}/api/v1/info", ("ERROR", 404)),
            (f"{BASE_URL}/api/info/metrics", ("ERROR", 404)),
            (f"{BASE_URL}/api/v1/info/metrics", ("ERROR", 404)),
            (f"{BASE_URL}/api/search", ("ERROR", 400)),
            (f"{BASE_URL}/api/v1/search", ("ERROR", 400)),
            (f"{BASE_URL}/api/access", ("ERROR", 404)),
            (f"{BASE_URL}/api/v1/access", ("ERROR", 404)),
        ],
    )
    def test_api_base_urls_ok(self, request, test_input, expected):
        resp = get(test_input)
        assert resp.json()["status"] == expected[0]
        assert resp.status_code == expected[1]


class TestGetRequest(object):
    pass


class TestPostRequest(object):
    pass


class TestPutRequest(object):
    pass


class TestDeleteRequest(object):
    pass
