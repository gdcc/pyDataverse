import pytest


class TestInit(object):
    pass


class TestSearch(object):
    @pytest.mark.vcr()
    @pytest.mark.parametrize("test_input,expected", [("aussda", ""), ("election", ""),])
    def test_ok(self, search_api, test_input, expected):
        resp = search_api.search(test_input)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"
