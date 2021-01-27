"""Find out more at https://github.com/GDCC/pyDataverse."""
import os
import pytest
from pyDataverse.api import NativeApi
from pyDataverse.utils import read_json


def test_config():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.dirname(test_dir)
    test_data_dir = os.path.join(test_dir, "data")
    json_schemas_dir = os.path.join(root_dir, "src/pyDataverse/schemas/json")
    test_data_output_dir = os.path.join(test_data_dir, "output")
    invalid_filename_strings = ["wrong", ""]
    invalid_filename_types = [(), [], 12, 12.12, set(), True, False]

    return {
        "root_dir": root_dir,
        "test_dir": test_dir,
        "test_data_dir": test_data_dir,
        "json_schemas_dir": json_schemas_dir,
        "test_data_output_dir": test_data_output_dir,
        "dataverse_upload_min_filename": os.path.join(
            test_data_dir, "dataverse_upload_min.json"
        ),
        "dataverse_upload_full_filename": os.path.join(
            test_data_dir, "dataverse_upload_full.json"
        ),
        "dataverse_upload_schema_filename": os.path.join(
            json_schemas_dir, "dataverse_upload_schema.json"
        ),
        "dataverse_json_output_filename": os.path.join(
            test_data_output_dir, "dataverse_pytest.json"
        ),
        "dataset_upload_min_filename": os.path.join(
            test_data_dir, "dataset_upload_min_default.json"
        ),
        "dataset_upload_full_filename": os.path.join(
            test_data_dir, "dataset_upload_full_default.json"
        ),
        "dataset_upload_schema_filename": os.path.join(
            json_schemas_dir, "dataset_upload_default_schema.json"
        ),
        "dataset_json_output_filename": os.path.join(
            test_data_output_dir, "dataset_pytest.json"
        ),
        "datafile_upload_min_filename": os.path.join(
            test_data_dir, "datafile_upload_min.json"
        ),
        "datafile_upload_full_filename": os.path.join(
            test_data_dir, "datafile_upload_full.json"
        ),
        "datafile_upload_schema_filename": os.path.join(
            json_schemas_dir, "datafile_upload_schema.json"
        ),
        "datafile_json_output_filename": os.path.join(
            test_data_output_dir, "datafile_pytest.json"
        ),
        "tree_filename": os.path.join(test_data_dir, "tree.json"),
        "invalid_filename_strings": ["wrong", ""],
        "invalid_filename_types": [(), [], 12, 12.12, set(), True, False],
        "invalid_validate_types": [None, "wrong", {}, []],
        "invalid_json_data_types": [[], (), 12, set(), True, False, None],
        "invalid_set_types": invalid_filename_types + ["", "wrong"],
        "invalid_json_strings": invalid_filename_strings,
        "invalid_data_format_types": invalid_filename_types,
        "invalid_data_format_strings": invalid_filename_strings,
        "base_url": os.getenv("BASE_URL"),
        "api_token": os.getenv("API_TOKEN"),
        "travis": os.getenv("TRAVIS") or False,
        "wait_time": 1,
    }


test_config = test_config()


@pytest.fixture()
def native_api(monkeypatch):
    """Fixture, so set up an Api connection.

    Returns
    -------
    Api
        Api object.

    """
    monkeypatch.setenv("BASE_URL", "https://demo.dataverse.org")
    return NativeApi(os.getenv("BASE_URL"))


def import_dataverse_min_dict():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    return {
        "alias": "test-pyDataverse",
        "name": "Test pyDataverse",
        "dataverseContacts": [{"contactEmail": "info@aussda.at"}],
    }


def import_dataset_min_dict():
    """Import dataset dict.

    Returns
    -------
    dict
        Dataset metadata.

    """
    return {
        "license": "CC0",
        "termsOfUse": "CC0 Waiver",
        "termsOfAccess": "Terms of Access",
        "citation_displayName": "Citation Metadata",
        "title": "Replication Data for: Title",
    }


def import_datafile_min_dict():
    """Import minimum Datafile dict.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    return {"pid": "doi:10.11587/EVMUHP", "filename": "tests/data/datafile.txt"}


def import_datafile_full_dict():
    """Import full Datafile dict.

    Returns
    -------
    dict
        Full Datafile metadata.

    """
    return {
        "pid": "doi:10.11587/EVMUHP",
        "filename": "tests/data/datafile.txt",
        "description": "Test datafile",
        "restrict": False,
    }
