# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Datafile data model tests."""
import json
import jsonschema
import os
from pyDataverse.models import Datafile
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


def dict_flat_set_min():
    """Import minimum Datafile dict.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    data = {
        'pid': 'doi:10.11587/RRKEA9',
        'filename': '10109_qu_de_v1_0.pdf'
    }
    return data


def dict_flat_set_full():
    """Import full Datafile dict.

    Returns
    -------
    dict
        Full Datafile metadata.

    """
    data = {
        'pid': 'doi:10.11587/NVWE8Y',
        'filename': '20001_ta_de_v1_0.pdf',
        'description': 'Another data file.',
        'restrict': True,
        'categories': ['Documentation'],
        'title': 'Questionnaire',
        'directoryLabel': 'data/subdir1'
    }
    return data


def object_init():
    """Import minimum Datafile dict.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    df = Datafile()
    return df


def object_min():
    """Import minimum Datafile dict.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    df = object_init()
    df.pid = 'doi:10.11587/RRKEA9'
    df.filename = '10109_qu_de_v1_0.pdf'
    return df


def object_full():
    """Import minimum Datafile dict.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    df = object_init()
    df.pid = 'doi:10.11587/NVWE8Y'
    df.filename = '20001_ta_de_v1_0.pdf'
    df.description = 'Another data file.'
    df.restrict = True
    df.categories = ['Documentation']
    df.title = 'Questionnaire'
    df.directoryLabel = 'data/subdir1'
    return df


def dict_flat_dict_min():
    """Import minimum Datafile dict.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    data = {
        'pid': 'doi:10.11587/RRKEA9',
        'filename': '10109_qu_de_v1_0.pdf',
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/datafile_upload_schema.json',
        'attr_dv_up_values': attr_dv_up_values()
    }
    return data


def dict_flat_dict_full():
    """Import full Datafile dict.

    Returns
    -------
    dict
        Full Datafile metadata.

    """
    data = {
        'pid': 'doi:10.11587/NVWE8Y',
        'filename': '20001_ta_de_v1_0.pdf',
        'description': 'Another data file.',
        'restrict': True,
        'categories': ['Documentation'],
        'title': 'Questionnaire',
        'directoryLabel': 'data/subdir1',
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/datafile_upload_schema.json',
        'attr_dv_up_values': attr_dv_up_values()
    }
    return data


def json_upload_min():
    """Import minimum Datafile dict.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    data = read_file('tests/data/datafile_upload_min.json')
    return data


def json_upload_full():
    """Import minimum Datafile dict.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    data = read_file('tests/data/datafile_upload_full.json')
    return data


def attr_dv_up_values():
    data = [
        'description',
        'categories',
        'restrict',
        'title',
        'directoryLabel',
        'pid',
        'filename'
    ]
    return data


class TestDatafile(object):
    """Tests for Datafile()."""

    def test_datafile_init(self):
        """Test Datafile.__init__()."""
        obj = Datafile()
        obj_assert = object_init()
        assert obj.__dict__ == obj_assert.__dict__
        assert str(obj) == 'pyDataverse Datafile() model class.'

    def test_datafile_set_min_valid(self):
        """Test Datafile.set() with minimum data."""
        obj = object_init()
        result = obj.set(dict_flat_set_min())
        obj_assert = object_min()
        assert result
        assert obj.__dict__ == obj_assert.__dict__

    def test_datafile_set_full_valid(self):
        """Test Datafile.set() with full data."""
        obj = object_init()
        result = obj.set(dict_flat_set_full())
        obj_assert = object_full()
        assert result
        assert obj.__dict__ == obj_assert.__dict__

    def test_datafile_set_invalid(self):
        """Test Datafile.set() with invalid data."""
        obj = object_init()
        obj_assert = obj
        for dtype in [list(), str(), int(), set(), tuple()]:
            result = obj.set(list())
            assert not result
            assert obj.__dict__ == obj_assert.__dict__

    def test_datafile_dict_min_valid(self):
        """Test Datafile.dict() with min data."""
        obj = object_min()
        dict_flat = obj.dict()
        dict_assert = dict_flat_dict_min()
        assert dict_flat == dict_assert

    def test_datafile_dict_full_valid(self):
        """Test Datafile.dict() with full data."""
        obj = object_full()
        dict_flat = obj.dict()
        dict_assert = dict_flat_dict_full()
        assert dict_flat == dict_assert

    def test_datafile_from_json_min_valid(self):
        """Test Datafile.from_json() with min data."""
        obj = object_init()
        result = obj.from_json('tests/data/datafile_upload_min.json', validate=False)
        obj_assert = object_min()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

    def test_datafile_from_json_full_valid(self):
        """Test Datafile.from_json() with full data."""
        obj = object_init()
        result = obj.from_json('tests/data/datafile_upload_full.json')
        obj_assert = object_full()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

        obj = object_init()
        result = obj.from_json('tests/data/datafile_upload_full.json', validate=False)
        obj_assert = object_full()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

        obj = object_init()
        result = obj.from_json('tests/data/datafile_upload_full.json', validate=False, filename_schema='wrong')
        obj_assert = object_full()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

    def test_datafile_from_json_invalid(self):
        """Test Datafile.from_json() with non-valid format."""
        # filename_schema=wrong
        with pytest.raises(FileNotFoundError):
            obj = object_init()
            obj.from_json(os.path.join(TEST_DIR, '/data/datafile_upload_min.json'), filename_schema='wrong')

        # format=wrong
        obj = object_init()
        result = obj.from_json(os.path.join(TEST_DIR, '/data/datafile_upload_min.json'), format='wrong')
        obj_assert = object_init()
        assert not result
        assert obj_assert.__dict__ == obj.__dict__

        # format=wrong, validate=False
        obj = object_init()
        result = obj.from_json(os.path.join(TEST_DIR, '/data/datafile_upload_min.json'), format='wrong', validate=False)
        obj_assert = object_init()
        assert not result
        assert obj_assert.__dict__ == obj.__dict__

    def test_datafile_to_json_min_valid(self):
        """Test Datafile.to_json() with min data."""
        obj = object_min()
        result = obj.to_json()
        dict_assert = json.loads(json_upload_min())
        assert result
        assert isinstance(result, str)
        assert json.loads(result) == dict_assert

    def test_datafile_to_json_full_valid(self):
        """Test Datafile.to_json() with full data."""
        obj = object_full()
        result = obj.to_json()
        dict_assert = json.loads(json_upload_full())
        assert result
        assert isinstance(result, str)
        assert json.loads(result) == dict_assert

        obj = object_full()
        result = obj.to_json(validate=False)
        dict_assert = json.loads(json_upload_full())
        assert result
        assert isinstance(result, str)
        assert json.loads(result) == dict_assert

        dict_assert = json.loads(json_upload_full())
        assert result
        assert isinstance(result, str)
        assert json.loads(result) == dict_assert

        obj = object_full()
        result = obj.to_json()
        dict_assert = json.loads(json_upload_full())
        assert result
        assert isinstance(result, str)
        assert json.loads(result) == dict_assert

    def test_datafile_to_json_invalid(self):
        """Test Datafile.to_json() with non-valid data."""
        with pytest.raises(FileNotFoundError):
            obj = object_full()
            result = obj.to_json(filename_schema='wrong')

        obj = object_full()
        result = obj.to_json(format='wrong')
        assert not result

        obj = object_full()
        result = obj.to_json(format='wrong', validate=False)
        assert not result

    def test_datafile_validate_json_valid(self):
        """Test Datafile.validate_json() with valid data."""
        obj = object_min()
        result = obj.validate_json()
        assert result

        obj = object_full()
        result = obj.validate_json()
        assert result

    def test_datafile_validate_json_invalid(self):
        """Test Datafile.validate_json() with non-valid data."""
        with pytest.raises(jsonschema.exceptions.ValidationError):
            obj = object_init()
            obj.validate_json()

        with pytest.raises(FileNotFoundError):
            obj = object_min()
            obj.validate_json(filename_schema='wrong')

        obj = object_min()
        result = obj.validate_json(format='wrong')
        assert not result

        obj = object_min()
        result = obj.validate_json(format='wrong', filename_schema='wrong')
        assert not result

        with pytest.raises(FileNotFoundError):
            obj = object_full()
            obj.validate_json(filename_schema='wrong')

        obj = object_full()
        result = obj.validate_json(format='wrong')
        assert not result

        obj = object_full()
        result = obj.validate_json(format='wrong', filename_schema='wrong')
        assert not result

    def test_datafile_from_json_to_json_min(self):
        """Test Datafile from JSON to JSON with min data."""
        if not os.environ.get('TRAVIS'):
            obj = object_init()
            obj.from_json(os.path.join(TEST_DIR + '/data/datafile_upload_min.json'), validate=False)
            json_str = obj.to_json(validate=False)
            dict_assert = json.loads(json_upload_min())
            assert json.loads(json_str) == dict_assert

    def test_datafile_from_json_to_json_full(self):
        """Test Datafile from JSON to JSON with full data."""
        if not os.environ.get('TRAVIS'):
            obj = object_init()
            obj.from_json(os.path.join(TEST_DIR + '/data/datafile_upload_full.json'), validate=False)
            json_str = obj.to_json(validate=False)
            dict_assert = json.loads(json_upload_full())
            assert json.loads(json_str) == dict_assert
