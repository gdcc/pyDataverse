# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/AUSSDA/pyDataverse."""
import json
import os
from pyDataverse.api import Api
import pytest

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(scope='module')
def api_connection():
    """Fixture, so set up an Api connection.

    Returns
    -------
    Api
        Api object.

    """
    api_token = os.environ['API_TOKEN']
    base_url = os.environ['BASE_URL']
    return Api(base_url, api_token)


def read_json(filename):
    """Read in json file.

    Parameters
    ----------
    filename : string
        Filename with full path.

    Returns
    -------
    dict
        File content as dict.

    """
    return j2d(read_file(filename))


def read_file(filename):
    """Read in file.

    Parameters
    ----------
    filename : string
        Filename with full path.

    Returns
    -------
    string
        File content as string.

    """
    with open(filename, 'r') as f:
        data = f.read()
    return data


def write_file(filename, data):
    """Write data to file.

    Parameters
    ----------
    filename : string
        Filename with full path.
    data : string
        File content as string.

    """
    with open(filename, 'w') as f:
        f.write(data)


def write_json(filename, data):
    """Write data to json file.

    Parameters
    ----------
    filename : string
        Filename with full path.
    data : dict
        File content as dict.

    """
    write_file(filename, d2j(data))


def j2d(data):
    """Convert json to dict.

    Parameters
    ----------
    data : string
        JSON-formatted string.

    Returns
    -------
    dict
        Data as dict.

    """
    return json.loads(data)


def d2j(data):
    """Coinvert dict 2 json.

    Parameters
    ----------
    data : dict
        Data as dict.

    Returns
    -------
    string
        JSON-formatted string.

    """
    return json.dumps(data, ensure_ascii=False, indent=2)


@pytest.fixture
def import_dataverse_min_dict():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    return read_json(TEST_DIR + '/data/dataverse_min.json')


@pytest.fixture
def import_dataset_min_dict():
    """Import dataset dict.

    Returns
    -------
    dict
        Dataset metadata.

    """
    data = {
        'license': 'CC0',
        'termsOfUse': 'CC0 Waiver',
        'termsOfAccess': 'Terms of Access',
        'citation_displayName': 'Citation Metadata',
        'title': 'Replication Data for: Title'
    }
    return data


@pytest.fixture
def import_datafile_min_dict():
    """Import minimum Datafile dict.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    data = {
        'pid': 'doi:10.11587/EVMUHP',
        'filename': 'tests/data/datafile.txt'
    }
    return data


@pytest.fixture
def import_datafile_full_dict():
    """Import full Datafile dict.

    Returns
    -------
    dict
        Full Datafile metadata.

    """
    data = {
        'pid': 'doi:10.11587/EVMUHP',
        'filename': 'tests/data/datafile.txt',
        'description': 'Test datafile',
        'restrict': False
    }
    return data
