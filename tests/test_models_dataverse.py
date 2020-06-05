# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse data model tests."""
import json
import os
from pyDataverse.models import Dataverse
from pyDataverse.models import DVObject
import pytest


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


def assert_dict_full():
    data = {
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/dataverse_upload_full_schema.json',
        'attr_dv_up_values': 'LIST',
        'alias': 'science',
        'name': 'Scientific Research',
        'affiliation': 'Scientific Research University',
        'description': 'We do all the science.',
        'dataverseType': 'LABORATORY',
        'dataverseContacts': 'LIST'
    }
    return data


def assert_dict_min():
    data = {
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/dataverse_upload_full_schema.json',
        'attr_dv_up_values': 'LIST',
        'alias': 'test-pyDataverse',
        'name': 'Test pyDataverse',
        'dataverseContacts': 'LIST'
    }
    return data


def assert_dict_invalid():
    data = {
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/dataverse_upload_full_schema.json',
        'attr_dv_up_values': 'LIST',
    }
    return data


class TestDataverse(object):
    """Tests for Dataverse()."""

    def test_dataverse_init(self):
        """Test Dataverse.__init__()."""

        data = assert_dict_invalid()
        dv = Dataverse()

        assert isinstance(dv, Dataverse)
        assert isinstance(dv, DVObject)
        assert len(dv.__dict__.keys()) == len(data.keys())
        for attr in list(data.keys()):
            if data[attr] != 'LIST':
                assert getattr(dv, attr) == data[attr]

    def test_dataverse_set_valid(self):
        """Test Dataverse.set() with format=`dv_up`.

        Parameters
        ----------
        dict_flat_min : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """

        data_min = assert_dict_min()

        data = dict_flat_min()
        dv = Dataverse()
        dv.set(data)

        assert dv.dataverseContacts == [{'contactEmail': 'info@aussda.at'}]
        for attr in list(data_min.keys()):
            if data_min[attr] != 'LIST':
                assert getattr(dv, attr) == data_min[attr]
        assert len(dv.__dict__.keys()) == len(data_min.keys())

        data = dict_flat_full()
        dv = Dataverse()
        dv.set(data)

        data_full = assert_dict_full()

        assert dv.dataverseContacts == [{'contactEmail': 'pi@example.edu'},{'contactEmail': 'student@example.edu'}]
        for attr in list(data_full.keys()):
            if data_full[attr] != 'LIST':
                assert getattr(dv, attr) == data_full[attr]
        assert len(dv.__dict__.keys()) == len(data_full.keys())

    def test_dataverse_from_json_dv_up_valid(self):
        """Test Dataverse.import_data() with format=`dv_up`."""

        data_min = assert_dict_min()

        dv = Dataverse()
        dv.from_json('tests/data/dataverse_upload_min.json')

        for attr in list(data_min.keys()):
            if data_min[attr] != 'LIST':
                assert getattr(dv, attr) == data_min[attr]
        assert len(dv.__dict__.keys()) == len(data_min.keys())

        data_full = assert_dict_full()

        dv = Dataverse()
        dv.from_json('tests/data/dataverse_upload_full.json')

        assert dv.dataverseContacts == [{'contactEmail': 'pi@example.edu'},{'contactEmail': 'student@example.edu'}]
        for attr in list(data_full.keys()):
            if data_full[attr] != 'LIST':
                assert getattr(dv, attr) == data_full[attr]
        assert len(dv.__dict__.keys()) == len(data_full.keys())

    def test_dataverse_from_json_format_invalid(self):
        """Test Dataverse.import_data() with non-valid format."""
        data = assert_dict_invalid()

        dv = Dataverse()
        dv.from_json('tests/data/dataverse_upload_min.json', format='wrong')

        for attr in list(data.keys()):
            if data[attr] != 'LIST':
                assert getattr(dv, attr) == data[attr]
        assert len(dv.__dict__.keys()) == len(data.keys())

    def test_dataverse_dict_valid(self):
        """Test Dataverse.dict() with format=`all` and valid data.

        Parameters
        ----------
        object_min : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data_min = assert_dict_min()
        dv = object_min()

        for attr in list(data_min.keys()):
            if data_min[attr] != 'LIST':
                assert getattr(dv, attr) == data_min[attr]
        assert len(dv.__dict__.keys()) == len(data_min.keys())

        data = dv.dict()

        assert data
        assert isinstance(data, dict)
        for attr in list(data.keys()):
            if data[attr] != 'LIST':
                assert getattr(dv, attr) == data[attr]
        assert len(data.keys()) == len(data_min.keys()) == len(dv.__dict__.keys())

        data_full = assert_dict_full()
        dv = object_full()

        assert len(dv.__dict__.keys()) == len(data_full.keys())

        data = dv.dict()
        assert data
        assert isinstance(data, dict)
        assert data['dataverseContacts'] == [{'contactEmail': 'pi@example.edu'},{'contactEmail': 'student@example.edu'}]
        for attr in list(data.keys()):
            if data[attr] != 'LIST':
                assert getattr(dv, attr) == data[attr]
        assert len(data.keys()) == len(data_full.keys()) == len(dv.__dict__.keys())

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
        data = assert_dict_invalid()
        dv = object_min()
        with pytest.raises(TypeError):
            json_dict = json.loads(dv.to_json(format='wrong'))

    def test_dataverse_from_json_to_json(self):
        """Test Dataverse pipeline from import to export with format=`dv_up`."""
        if not os.environ.get('TRAVIS'):
            dv = Dataverse()
            dv.from_json(os.path.join(TEST_DIR + '/data/dataverse_upload_min.json'))
            json_str = dv.to_json()
            assert json.loads(json_upload_min()) == json.loads(dv.to_json())

            dv = Dataverse()
            dv.from_json(TEST_DIR + '/data/dataverse_upload_full.json')
            json_str = dv.to_json()
            assert json.loads(json_upload_full()) == json.loads(dv.to_json())
