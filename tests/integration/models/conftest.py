import os
import pytest
from pyDataverse.api import NativeApi
from pyDataverse.utils import read_json
from ..conftest import BASE_URL


def test_config():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.dirname(test_dir)
    test_data_dir = os.path.join(test_dir, "data")
    json_schemas_dir = os.path.join(root_dir, "src/pyDataverse/schemas/json")
    invalid_filename_strings = ["wrong", ""]
    invalid_filename_types = [(), [], 12, 12.12, set(), True, False]

    return {
        "root_dir": root_dir,
        "test_dir": test_dir,
        "test_data_dir": test_data_dir,
        "json_schemas_dir": json_schemas_dir,
        "dataverse_upload_min_filename": os.path.join(
            test_data_dir, "tests/data/api/dataverses/dataverse_upload_min_1.json"
        ),
        "dataverse_upload_full_filename": os.path.join(
            test_data_dir, "tests/data/api/dataverses/dataverse_upload_full_1.json"
        ),
        "dataverse_upload_schema_filename": os.path.join(
            json_schemas_dir, "dataverse_upload_schema.json"
        ),
        "dataset_upload_min_filename": os.path.join(
            test_data_dir, "tests/data/api/datasets/dataset_upload_default_min_1.json"
        ),
        "dataset_upload_full_filename": os.path.join(
            test_data_dir, "tests/data/api/datasets/dataset_upload_default_full_1.json"
        ),
        "dataset_upload_schema_filename": os.path.join(
            json_schemas_dir, "dataset_upload_default_schema.json"
        ),
        "datafile_upload_min_filename": os.path.join(
            test_data_dir, "tests/data/api/datafiles/datafile_upload_min_1.json"
        ),
        "datafile_upload_full_filename": os.path.join(
            test_data_dir, "tests/data/api/datafiles/datafile_upload_full_1.json"
        ),
        "datafile_upload_schema_filename": os.path.join(
            json_schemas_dir, "datafile_upload_schema.json"
        ),
        "tree_filename": os.path.join(test_data_dir, "api/tree.json"),
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
