import json
import os
from pyDataverse.api import Api
import pytest

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(scope='module')
def api_connection():
    api_token = os.environ['API_TOKEN']
    base_url = os.environ['BASE_URL']
    return Api(base_url, api_token)


def read_json(filename):
    return j2d(read_file(filename))


def read_file(filename):
    with open(filename, 'r') as f:
        data = f.read()
    return data


def write_file(filename, data):
    with open(filename, 'w') as f:
        f.write(data)


def write_json(filename, data):
    write_file(filename, d2j(data))


def j2d(data):
    return json.loads(data)


def d2j(data):
    return json.dumps(data, ensure_ascii=False, indent=2)


@pytest.fixture
def import_dict():
    data = {
        'license': 'CC0',
        'termsOfUse': 'CC0 Waiver',
        'termsOfAccess': 'Terms of Access',
        'citation_displayName': 'Citation Metadata',
        'title': 'Replication Data for: Title'
    }
    return data

@pytest.fixture
def import_dataset_full():
    return read_json(TEST_DIR + '/data/dataset_full.json')


@pytest.fixture
def import_dataset_min():
    return read_json(TEST_DIR + '/data/dataset_min.json')


@pytest.fixture
def import_dataverse_min():
    return read_json(TEST_DIR + '/data/dataverse_min.json')
