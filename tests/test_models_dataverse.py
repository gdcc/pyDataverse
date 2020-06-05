# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse data model tests."""
import json
import os
from pyDataverse.models import Dataverse
from pyDataverse.models import DVObject


TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def read_file(filename, mode='r'):
    """Read in a file.

    Parameters
    ----------
    filename : string
        Filename with full path.
    mode : string
        Read mode of file. Defaults to `r`. See more at
        https://docs.python.org/3.5/library/functions.html#open

    Returns
    -------
    string
        Returns data as string.

    """
    try:
        with open(filename, mode) as f:
            data = f.read()
        return data
    except IOError:
        print('An error occured trying to read the file {}.'.format(filename))
    except Exception as e:
        raise e


def read_json(filename, mode='r', encoding='utf-8'):
    """Read in a json file.

    See more about the json module at
    https://docs.python.org/3.5/library/json.html

    Parameters
    ----------
    filename : string
        Filename with full path.

    Returns
    -------
    dict
        Data as a json-formatted string.

    """
    try:
        with open(filename, mode=mode, encoding=encoding) as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise e


def write_json(filename, data, mode='w', encoding='utf-8'):
    """Write data to a json file.

    Parameters
    ----------
    filename : string
        Filename with full path.
    data : dict
        Data to be written in the json file.
    mode : string
        Write mode of file. Defaults to `w`. See more at
        https://docs.python.org/3/library/functions.html#open

    """
    try:
        with open(filename, mode, encoding=encoding) as f:
            json.dump(data, f, indent=2)
    except IOError:
        print('An error occured trying to write the file {}.'.format(filename))
    except Exception as e:
        raise e


def object_min():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = dict_flat_min()
    dv = Dataverse()
    dv.set(data)
    return dv


def object_full():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = dict_flat_full()
    dv = Dataverse()
    dv.set(data)
    return dv


def dict_flat_min():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = {
        'alias': 'test-pyDataverse',
        'name': 'Test pyDataverse',
        'dataverseContacts': [
            {'contactEmail': 'info@aussda.at'}
        ]
    }
    return data


def dict_flat_full():
    """Import full Dataverse dict.

    Returns
    -------
    dict
        Full Dataverse metadata.

    """
    data = {
        'name': 'Scientific Research',
        'alias': 'science',
        'dataverseContacts': [
            {'contactEmail': 'pi@example.edu'},
            {'contactEmail': 'student@example.edu'}
        ],
        'affiliation': 'Scientific Research University',
        'description': 'We do all the science.',
        'dataverseType': 'LABORATORY'
    }
    return data


def json_upload_min():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = read_file('tests/data/dataverse_upload_min.json')
    return data


def json_upload_full():
    """Import full Dataverse dict.

    Returns
    -------
    dict
        Full Dataverse metadata.

    """
    data = read_file('tests/data/dataverse_upload_full.json')
    return data


class TestDataverse(object):
    """Tests for Dataverse()."""

    def test_dataverse_init(self):
        """Test Dataverse.__init__()."""
        dv = Dataverse()

        assert isinstance(dv, Dataverse)
        assert isinstance(dv, DVObject)
        assert len(dv.__dict__.keys()) == 3
        assert dv.default_validate_format == 'dataverse_upload'
        assert dv.default_validate_schema_filename == 'schemas/json/dataverse_upload_full_schema.json'

    def test_dataverse_set_valid(self):
        """Test Dataverse.set() with format=`dv_up`.

        Parameters
        ----------
        dict_flat_min : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = dict_flat_min()
        dv = Dataverse()
        dv.set(data)

        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert isinstance(dv.dataverseContacts, list)
        assert len(dv.dataverseContacts) == 1
        assert dv.dataverseContacts[0]['contactEmail'] == 'info@aussda.at'
        assert dv.default_validate_format == 'dataverse_upload'
        assert dv.default_validate_schema_filename == 'schemas/json/dataverse_upload_full_schema.json'
        assert len(dv.__dict__.keys()) == 6

        data = dict_flat_full()
        dv = Dataverse()
        dv.set(data)

        assert dv.alias == 'science'
        assert dv.name == 'Scientific Research'
        assert dv.affiliation == 'Scientific Research University'
        assert dv.description == 'We do all the science.'
        assert dv.dataverseType == 'LABORATORY'
        assert isinstance(dv.dataverseContacts, list)
        assert len(dv.dataverseContacts) == 2
        assert dv.dataverseContacts[0]['contactEmail'] == 'pi@example.edu'
        assert dv.dataverseContacts[1]['contactEmail'] == 'student@example.edu'
        assert dv.default_validate_format == 'dataverse_upload'
        assert dv.default_validate_schema_filename == 'schemas/json/dataverse_upload_full_schema.json'
        assert len(dv.__dict__.keys()) == 9

    def test_dataverse_from_json_dv_up_valid(self):
        """Test Dataverse.import_data() with format=`dv_up`."""
        dv = Dataverse()
        dv.from_json('tests/data/dataverse_upload_min.json')

        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert len(dv.dataverseContacts) == 1
        assert dv.dataverseContacts[0]['contactEmail'] == 'info@aussda.at'
        assert dv.default_validate_format == 'dataverse_upload'
        assert dv.default_validate_schema_filename == 'schemas/json/dataverse_upload_full_schema.json'
        assert len(dv.__dict__.keys()) == 6

        dv = Dataverse()
        dv.from_json('tests/data/dataverse_upload_full.json')

        assert dv.alias == 'science'
        assert dv.name == 'Scientific Research'
        assert dv.affiliation == 'Scientific Research University'
        assert dv.description == 'We do all the science.'
        assert dv.dataverseType == 'LABORATORY'
        assert len(dv.dataverseContacts) == 2
        assert dv.dataverseContacts[0]['contactEmail'] == 'pi@example.edu'
        assert dv.dataverseContacts[1]['contactEmail'] == 'student@example.edu'
        assert dv.default_validate_format == 'dataverse_upload'
        assert dv.default_validate_schema_filename == 'schemas/json/dataverse_upload_full_schema.json'
        assert len(dv.__dict__.keys()) == 9

    def test_dataverse_from_json_format_invalid(self):
        """Test Dataverse.import_data() with non-valid format."""
        dv = Dataverse()
        dv.default_validate_format = 'wrong'
        dv.from_json('tests/data/dataverse_upload_min.json')

        assert dv.default_validate_format == 'wrong'
        assert dv.default_validate_schema_filename == 'schemas/json/dataverse_upload_full_schema.json'
        assert len(dv.__dict__.keys()) == 3

    def test_dataverse_dict_valid(self):
        """Test Dataverse.dict() with format=`all` and valid data.

        Parameters
        ----------
        object_min : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        dv = object_min()

        assert dv.default_validate_format == 'dataverse_upload'
        assert dv.default_validate_schema_filename == 'schemas/json/dataverse_upload_full_schema.json'
        assert len(dv.__dict__.keys()) == 6

        data = dv.dict()

        assert data
        assert isinstance(data, dict)
        assert data['alias'] == 'test-pyDataverse'
        assert data['name'] == 'Test pyDataverse'
        assert len(data['dataverseContacts']) == 1
        assert data['dataverseContacts'][0]['contactEmail'] == 'info@aussda.at'
        assert len(data.keys()) == 6

        dv = object_full()

        assert len(dv.__dict__.keys()) == 9

        data = dv.dict()

        assert data
        assert isinstance(data, dict)
        assert data['alias'] == 'science'
        assert data['name'] == 'Scientific Research'
        assert data['affiliation'] == 'Scientific Research University'
        assert data['description'] == 'We do all the science.'
        assert data['dataverseType'] == 'LABORATORY'
        assert len(data['dataverseContacts']) == 2
        assert data['dataverseContacts'][0]['contactEmail'] == 'pi@example.edu'
        assert data['dataverseContacts'][1]['contactEmail'] == 'student@example.edu'
        assert len(data.keys()) == len(dv.__dict__.keys())

    def test_dataverse_to_json_dv_up_valid(self):
        """Test Dataverse.json() with format=`dv_up` and valid data.

        Parameters
        ----------
        object_min : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        TODO: Assert content
        """
        dv = object_min()

        assert dv.to_json()
        assert isinstance(dv.to_json(), str)
        assert json.loads(dv.to_json()) == json.loads(json_upload_min())

        dv = object_full()

        assert dv.to_json()
        assert isinstance(dv.to_json(), str)
        assert json.loads(dv.to_json()) == json.loads(json_upload_full())

    # def test_dataverse_to_json_dv_up_invalid(self, object_min):
    #     """Test Dataverse.json() with format=`dv_up` and non-valid data.
    #
    #     Parameters
    #     ----------
    #     object_min : dict
    #         Fixture, which returns a flat dataset dict() coming from
    #         `tests/data/dataverse_min.json`.
    #
    #     """
    #     dv = object_min
    #     dv.name = None
    #     # TODO: check error

    def test_dataverse_to_json_format_invalid(self):
        """Test Dataverse.json() with non-valid format and valid data.

        Parameters
        ----------

        """
        dv = object_min()
        data = dv.to_json('wrong')

        assert not data

    def test_dataverse_from_json_to_json(self):
        """Test Dataverse pipeline from import to export with format=`dv_up`."""
        if not os.environ.get('TRAVIS'):
            dv = Dataverse()
            dv.from_json(os.path.join(TEST_DIR + '/data/dataverse_upload_min.json'))
            json_str = dv.to_json()
            assert json.loads(dv.to_json()) == json.loads(json_upload_min())

            dv = Dataverse()
            dv.from_json(TEST_DIR + '/data/dataverse_upload_full.json')
            json_str = dv.to_json()
            assert json.loads(dv.to_json()) == json.loads(json_upload_full())
