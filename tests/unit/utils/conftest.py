import os
from ..conftest import ROOT_DIR


def test_config():
    root_dir = ROOT_DIR
    test_dir = os.path.join(root_dir, "tests")
    test_data_dir = os.path.join(test_dir, "data")

    return {
        "test_data_dir": test_data_dir,
        "tree_filename": os.path.join(test_data_dir, "api/tree_1.json"),
    }


test_config = test_config()
