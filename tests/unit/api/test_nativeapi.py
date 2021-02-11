import pytest
from pyDataverse.api import NativeApi
from pyDataverse.exceptions import ApiUrlError
from pyDataverse.exceptions import OperationFailedError


class TestInit(object):
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (
                "https://data.aussda.at",
                ("https://data.aussda.at", "v1", "https://data.aussda.at/api/v1"),
            ),
            (
                "https://demo.dataverse.org",
                (
                    "https://demo.dataverse.org",
                    "v1",
                    "https://demo.dataverse.org/api/v1",
                ),
            ),
        ],
    )
    def test_base_url_ok(self, test_input, expected):
        api = NativeApi(test_input)
        assert api.api_token is None
        assert api.timeout == 500
        assert api.base_url == expected[0]
        assert api.api_version == expected[1]
        assert api.base_url_api_native == expected[2]

    def test_base_url_invalid(self):
        """Test native_api connection with wrong `base_url`."""
        # None
        with pytest.raises(ApiUrlError):
            NativeApi(None)


class TestGetDataverse(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataverse_full):
        alias = create_dataverse_full.json()["data"]["alias"]
        resp = native_api.get_dataverse(alias)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    @pytest.mark.vcr()
    def test_min_published_ok(self, native_api, publish_dataverse_min):
        alias = publish_dataverse_min.json()["data"]["alias"]
        resp = native_api.get_dataverse(alias)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestCreateDataverse(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataverse_full):
        resp = create_dataverse_full
        assert resp.status_code == 201
        assert resp.json()["status"] == "OK"


class TestPublishDataverse(object):
    @pytest.mark.vcr()
    def test_min_ok(self, native_api, publish_dataverse_min):
        resp = publish_dataverse_min
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetDataverseRoles(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataverse_full):
        alias = create_dataverse_full.json()["data"]["alias"]
        resp = native_api.get_dataverse_roles(alias)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    @pytest.mark.vcr()
    def test_min_published_ok(self, native_api, publish_dataverse_min):
        alias = publish_dataverse_min.json()["data"]["alias"]
        resp = native_api.get_dataverse_roles(alias)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetDataverseContents(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataverse_full):
        alias = create_dataverse_full.json()["data"]["alias"]
        resp = native_api.get_dataverse_contents(alias)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    @pytest.mark.vcr()
    def test_min_published_ok(self, native_api, publish_dataverse_min):
        alias = publish_dataverse_min.json()["data"]["alias"]
        resp = native_api.get_dataverse_contents(alias)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetDataverseAssignments(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataverse_full):
        alias = create_dataverse_full.json()["data"]["alias"]
        resp = native_api.get_dataverse_assignments(alias)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    @pytest.mark.vcr()
    def test_min_published_ok(self, native_api, publish_dataverse_min):
        alias = publish_dataverse_min.json()["data"]["alias"]
        resp = native_api.get_dataverse_assignments(alias)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetDataverseFacets(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataverse_full):
        alias = create_dataverse_full.json()["data"]["alias"]
        resp = native_api.get_dataverse_facets(alias)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    @pytest.mark.vcr()
    def test_min_published_ok(self, native_api, publish_dataverse_min):
        alias = publish_dataverse_min.json()["data"]["alias"]
        resp = native_api.get_dataverse_facets(alias)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestDataverseIdToAlias(object):
    # native_api.dataverse_id2alias()
    pass


class TestGetDataset(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataset_full):
        pid = create_dataset_full.json()["data"]["persistentId"]
        resp = native_api.get_dataset(pid)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    @pytest.mark.vcr()
    def test_min_published_ok(self, native_api, publish_dataset_min):
        pid = f"doi:{publish_dataset_min.json()['data']['authority']}/{publish_dataset_min.json()['data']['identifier']}"
        resp = native_api.get_dataset(pid)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetDatasetVersions(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataset_full):
        pid = create_dataset_full.json()["data"]["persistentId"]
        resp = native_api.get_dataset_versions(pid)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    @pytest.mark.vcr()
    def test_min_published_ok(self, native_api, publish_dataset_min):
        pid = f"doi:{publish_dataset_min.json()['data']['authority']}/{publish_dataset_min.json()['data']['identifier']}"
        resp = native_api.get_dataset_versions(pid)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetDatasetVersion(object):
    @pytest.mark.vcr()
    @pytest.mark.parametrize("test_input,expected", [(":draft", ""), (":latest", ""),])
    def test_full_unpublished_ok(
        self, native_api, create_dataset_full, test_input, expected
    ):
        pid = create_dataset_full.json()["data"]["persistentId"]
        resp = native_api.get_dataset_version(pid, test_input)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    @pytest.mark.vcr()
    @pytest.mark.parametrize(
        "test_input,expected",
        [(":latest", ""), (":latest-published", ""), ("1.0", ""), ("1", ""),],
    )
    def test_min_published_ok(
        self, native_api, publish_dataset_min, test_input, expected
    ):
        pid = f"doi:{publish_dataset_min.json()['data']['authority']}/{publish_dataset_min.json()['data']['identifier']}"
        resp = native_api.get_dataset_version(pid, test_input)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestCreateDataset(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataset_full):
        resp = create_dataset_full
        assert resp.status_code == 201
        assert resp.json()["status"] == "OK"


class TestEditDatasetMetadata(object):
    # native_api.edit_dataset_metadata(pid)
    pass


class TestCreateDatasetPrivateUrl(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataset_full):
        pid = create_dataset_full.json()["data"]["persistentId"]
        resp = native_api.create_dataset_private_url(pid)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetDatasetPrivateUrl(object):
    # native_api.get_dataset_private_url(pid)
    pass


class TestDeleteDatasetPrivateUrl(object):
    # native_api.delete_dataset_private_url(pid)
    pass


class TestGetDatasetExport(object):
    @pytest.mark.vcr()
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("ddi", ""),
            ("oai_ddi", ""),
            ("dcterms", ""),
            ("oai_dc", ""),
            ("schema.org", ""),
            ("dataverse_json", ""),
        ],
    )
    def test_min_published_ok(
        self, native_api, publish_dataset_min, test_input, expected
    ):
        pid = f"doi:{publish_dataset_min.json()['data']['authority']}/{publish_dataset_min.json()['data']['identifier']}"
        resp = native_api.get_dataset_export(pid, test_input)
        assert resp.status_code == 200
        assert resp.content != ""

    @pytest.mark.vcr()
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("ddi", OperationFailedError),
            ("oai_ddi", OperationFailedError),
            ("dcterms", OperationFailedError),
            ("oai_dc", OperationFailedError),
            ("schema.org", OperationFailedError),
            ("dataverse_json", OperationFailedError),
        ],
    )
    def test_full_unpublished_error(
        self, native_api, create_dataset_full, test_input, expected
    ):
        pid = create_dataset_full.json()["data"]["persistentId"]
        with pytest.raises(expected):
            native_api.get_dataset_export(pid, test_input)


class TestPublishDataset(object):
    @pytest.mark.vcr()
    def test_min_ok(self, native_api, publish_dataset_min):
        resp = publish_dataset_min
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestDatasetLock(object):
    pass


class TestGetDatasetAssignments(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataset_full):
        pid = create_dataset_full.json()["data"]["persistentId"]
        resp = native_api.get_dataset_assignments(pid)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    @pytest.mark.vcr()
    def test_min_published_ok(self, native_api, publish_dataset_min):
        pid = f"doi:{publish_dataset_min.json()['data']['authority']}/{publish_dataset_min.json()['data']['identifier']}"
        resp = native_api.get_dataset_assignments(pid)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestDeleteDataset(object):
    pass


class TestDestroyDataset(object):
    pass


class TestGetDatafilesMetadata(object):
    @pytest.mark.vcr()
    def test_full_unpublished_ok(self, native_api, create_dataset_full):
        pid = create_dataset_full.json()["data"]["persistentId"]
        resp = native_api.get_datafiles_metadata(pid)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"

    @pytest.mark.vcr()
    def test_min_published_ok(self, native_api, publish_dataset_min):
        pid = f"doi:{publish_dataset_min.json()['data']['authority']}/{publish_dataset_min.json()['data']['identifier']}"
        resp = native_api.get_datafiles_metadata(pid)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetDatafileMetadata(object):
    pass


class TestUploadDatafile(object):
    pass


class TestUpdateDatafileMetadata(object):
    pass


class TestReplaceDatafile(object):
    pass


class TestGetInfoVersion(object):
    @pytest.mark.vcr()
    def test_ok(self, native_api):
        resp = native_api.get_info_version()
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetInfoServer(object):
    @pytest.mark.vcr()
    def test_ok(self, native_api):
        resp = native_api.get_info_server()
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetApiTermsOfUse(object):
    @pytest.mark.vcr()
    def test_ok(self, native_api):
        resp = native_api.get_info_api_terms_of_use()
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetMetadatablocks(object):
    @pytest.mark.vcr()
    def test_ok(self, native_api):
        resp = native_api.get_metadatablocks()
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetMetadatablock(object):
    @pytest.mark.vcr()
    @pytest.mark.parametrize(
        "test_input, expected",
        [("citation", ""), ("geospatial", ""), ("socialscience", ""), ("journal", "")],
    )
    def test_ok(self, native_api, test_input, expected):
        resp = native_api.get_metadatablock(test_input)
        assert resp.status_code == 200
        assert resp.json()["status"] == "OK"


class TestGetUserApiTokenExpirationTokenDate(object):
    pass


class TestRecreateApiToken(object):
    pass


class TestDeleteApiToken(object):
    pass


class TestCreateRole(object):
    pass


class TestShowRole(object):
    pass


class TestDeleteRole(object):
    pass


class TestGetChildren(object):
    pass


class TestGetUser(object):
    pass


class TestRedetectFileType(object):
    pass


class TestReingestDatafile(object):
    pass


class TestUningestDatafile(object):
    pass


class TestRestrictDatafile(object):
    pass
