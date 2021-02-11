"""Find out more at https://github.com/gdcc/pyDataverse."""
import hashlib
import json
import os
import pytest
from pyDataverse.api import NativeApi
from pyDataverse.api import MetricsApi
from pyDataverse.api import SwordApi
from pyDataverse.api import SearchApi
from pyDataverse.api import DataAccessApi
from pyDataverse.utils import read_csv
from pyDataverse.utils import read_file
from vcr import VCR


BASE_URL = os.getenv("BASE_URL")

vcr = VCR(
    cassette_library_dir="tests/data/vcr_cassettes/4.18.1",
    serializer="json",
    path_transformer=VCR.ensure_suffix(".json"),
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "serializer": "json",
        "record_mode": "once",
        "path_transformer": VCR.ensure_suffix(".json"),
    }


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    return os.path.join("tests/data/vcr_cassettes/4.18.1")


@pytest.fixture()
def vcr_cassette_name(request):
    """Name of the VCR cassette."""
    filename = os.path.basename(request.node.fspath)
    mod_name_lst = request.module.__name__.split(".")
    test_type = mod_name_lst[1]
    module_name = mod_name_lst[2]
    file_suffix = filename.split(".")[0].split("_")[1].lower()
    cls_name = request.cls.__name__.replace("Test", "")
    func_name = request.function.__name__.lower()
    hashval = hashlib.sha1(request.node.nodeid.encode("UTF-8")).hexdigest()[-6:]
    return os.path.join(
        test_type, module_name, file_suffix, cls_name, f"{func_name}_{hashval}"
    )


@pytest.fixture(scope="session")
def native_api():
    BASE_URL = os.getenv("BASE_URL")
    API_TOKEN = os.getenv("API_TOKEN_SUPERUSER")
    api = NativeApi(BASE_URL, API_TOKEN)
    yield api


@pytest.fixture(scope="session")
def search_api():
    BASE_URL = os.getenv("BASE_URL")
    API_TOKEN = os.getenv("API_TOKEN_SUPERUSER")
    api = SearchApi(BASE_URL, API_TOKEN)
    yield api


@pytest.fixture(scope="session")
def dataaccess_api():
    BASE_URL = os.getenv("BASE_URL")
    API_TOKEN = os.getenv("API_TOKEN_SUPERUSER")
    api = DataAccessApi(BASE_URL, API_TOKEN)
    yield api


@pytest.fixture(scope="session")
def sword_api():
    BASE_URL = os.getenv("BASE_URL")
    API_TOKEN = os.getenv("API_TOKEN_SUPERUSER")
    api = SwordApi(BASE_URL, API_TOKEN)
    yield api


@pytest.fixture(scope="session")
def metrics_api():
    BASE_URL = os.getenv("BASE_URL")
    API_TOKEN = os.getenv("API_TOKEN_SUPERUSER")
    api = MetricsApi(BASE_URL, API_TOKEN)
    yield api


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/get_info_version")
def get_info_version(native_api):
    yield native_api.get_info_version().json()["data"]["version"]


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/create_dataverse_pydataverse")
def create_dataverse_pydataverse(native_api, dataverse_upload_min_1):
    DV_ALIAS = os.getenv("DV_ALIAS")
    metadata = json.loads(dataverse_upload_min_1)
    metadata["alias"] = DV_ALIAS
    native_api.create_dataverse(":root", json.dumps(metadata))
    native_api.publish_dataverse(DV_ALIAS)
    yield
    native_api.delete_dataverse(DV_ALIAS)


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/create_dataverse_min")
def create_dataverse_min(
    native_api, create_dataverse_pydataverse, dataverse_upload_min_1
):
    DV_ALIAS = os.getenv("DV_ALIAS")
    resp = native_api.create_dataverse(DV_ALIAS, dataverse_upload_min_1)
    alias = resp.json()["data"]["alias"]
    yield resp
    native_api.delete_dataverse(alias)


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/create_dataverse_full")
def create_dataverse_full(
    native_api, create_dataverse_pydataverse, dataverse_upload_full_1
):
    DV_ALIAS = os.getenv("DV_ALIAS")
    resp = native_api.create_dataverse(DV_ALIAS, dataverse_upload_full_1)
    alias = resp.json()["data"]["alias"]
    yield resp
    native_api.delete_dataverse(alias)


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/publish_dataverse_min")
def publish_dataverse_min(native_api, create_dataverse_min):
    alias = create_dataverse_min.json()["data"]["alias"]
    resp = native_api.publish_dataverse(alias)
    yield resp


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/create_dataset_min")
def create_dataset_min(
    native_api, create_dataverse_pydataverse, dataset_upload_default_min_1
):
    DV_ALIAS = os.getenv("DV_ALIAS")
    resp = native_api.create_dataset(DV_ALIAS, dataset_upload_default_min_1)
    yield resp


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/create_dataset_full")
def create_dataset_full(
    native_api, create_dataverse_pydataverse, dataset_upload_default_full_1
):
    DV_ALIAS = os.getenv("DV_ALIAS")
    resp = native_api.create_dataset(DV_ALIAS, dataset_upload_default_full_1)
    pid = resp.json()["data"]["persistentId"]
    yield resp
    native_api.delete_dataset(pid)


@pytest.fixture(scope="session")
@vcr.use_cassette("fixtures/publish_dataset_min")
def publish_dataset_min(native_api, create_dataset_min):
    pid = create_dataset_min.json()["data"]["persistentId"]
    resp = native_api.publish_dataset(pid, release_type="major")
    yield resp
    native_api.destroy_dataset(pid)


@pytest.fixture(scope="session")
def dataverse_upload_full_1():
    yield read_file("tests/data/api/dataverses/dataverse_upload_full_1.json")


@pytest.fixture(scope="session")
def dataverse_upload_min_1():
    yield read_file("tests/data/api/dataverses/dataverse_upload_min_1.json")


@pytest.fixture(scope="session")
def dataset_upload_default_full_1():
    yield read_file("tests/data/api/datasets/dataset_upload_default_full_1.json")


@pytest.fixture(scope="session")
def dataset_upload_default_min_1():
    yield read_file("tests/data/api/datasets/dataset_upload_default_min_1.json")


@pytest.fixture(scope="session")
def dataset_upload_finch_1():
    yield read_file("tests/data/api/datasets/dataset_upload_finch_1.json")


@pytest.fixture(scope="session")
def datafile_upload_full_1():
    yield read_file("tests/data/api/datafiles/datafile_upload_full_1.json")


@pytest.fixture(scope="session")
def datafile_upload_min_1():
    yield read_file("tests/data/api/datafiles/datafile_upload_min_1.json")


@pytest.fixture(scope="session")
def datasets_csv():
    yield read_csv("tests/data/csv/datasets.csv")


@pytest.fixture(scope="session")
def datafiles_csv():
    yield read_csv("tests/data/csv/datafiles.csv")


# @pytest.fixture()
# def dataverse_min_dict():
#     """Import minimum Dataverse dict.

#     Returns
#     -------
#     dict
#         Minimum Dataverse metadata.

#     """
#     yield {
#         "alias": "test-pyDataverse",
#         "name": "Test pyDataverse",
#         "dataverseContacts": [{"contactEmail": "info@aussda.at"}],
#     }


# @pytest.fixture()
# def dataverse_full_dict():
#     """Import full Dataverse dict.

#     Returns
#     -------
#     dict
#         Minimum Dataverse metadata.

#     """
#     yield {
#         "name": "Scientific Research",
#         "alias": "science",
#         "dataverseContacts": [
#             {
#                 "contactEmail": "pi@example.edu"
#             },
#             {
#                 "contactEmail": "student@example.edu"
#             }
#         ],
#         "affiliation": "Scientific Research University",
#         "description": "We do all the science.",
#         "dataverseType": "LABORATORY",
#         }

# @pytest.fixture()
# def dataset_min_dict():
#     """Import dataset dict.

#     Returns
#     -------
#     dict
#         Dataset metadata.

#     """
#     yield {
#         "license": "CC0",
#         "termsOfUse": "CC0 Waiver",
#         "termsOfAccess": "Terms of Access",
#         "citation_displayName": "Citation Metadata",
#         "title": "Replication Data for: Title",
#     }


# @pytest.fixture()
# def datafile_min_dict():
#     """Import minimum Datafile dict.

#     Returns
#     -------
#     dict
#         Minimum Datafile metadata.

#     """
#     yield {
#         "pid": "doi:10.11587/EVMUHP",
#         "filename": "tests/data/datafile.txt"
#     }


# @pytest.fixture()
# def datafile_full_dict():
#     """Import full Datafile dict.

#     Returns
#     -------
#     dict
#         Full Datafile metadata.

#     """
#     yield {
#         "pid": "doi:10.11587/EVMUHP",
#         "filename": "tests/data/datafile.txt",
#         "description": "Test datafile",
#         "restrict": False,
#     }
