import json
import os
from pyDataverse.api import Api
import pytest


@pytest.fixture(scope='module')
def api_connection():
    api_token = os.environ['API_TOKEN']
    base_url = os.environ['BASE_URL']
    return Api(base_url, api_token)


@pytest.fixture
def read_json(filename):
    j2d(read_file(filename, 'r'))


@pytest.fixture
def read_file(filename):
    with open(filename, 'r') as f:
        data = f.read()
    return data


@pytest.fixture
def write_file(filename, data):
    with open(filename, 'w') as f:
        f.write(data)


@pytest.fixture
def write_json(filename, data):
    write_file(filename, d2j(data))


@pytest.fixture
def j2d(data):
    return json.loads(data)


@pytest.fixture
def d2j(data):
    json.dumps(data, ensure_ascii=False, indent=2)
