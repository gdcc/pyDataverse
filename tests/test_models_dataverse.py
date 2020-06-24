# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse data model tests."""
import json
import jsonschema
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



def dict_flat_set_min():
    """Get flat dict for set() of minimum Dataverse.

    Returns
    -------
    dict
        Flat dict with minimum Dataverse data.

    """
    data = {
        'alias': 'test-pyDataverse',
        'name': 'Test pyDataverse',
        'dataverseContacts': [
            {'contactEmail': 'info@aussda.at'}
        ]
    }
    return data


def dict_flat_set_full():
    """Get flat dict for set() of full Dataverse.

    Returns
    -------
    dict
        Flat dict with full Dataverse data.

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


def object_init():
    """Get :class:Dataverse() with initial attributes.

    Returns
    -------
    pyDataverse.Dataverse()
        :class:Dataverse() with init attributes set.

    """
    dv = Dataverse()
    return dv


def object_min():
    """Get :class:Dataverse() with attributes of minimum Dataverse.

    Returns
    -------
    pyDataverse.Dataverse()
        :class:Dataverse() with minimum attributes set.

    """
    dv = object_init()
    dv.alias = 'test-pyDataverse'
    dv.name = 'Test pyDataverse'
    dv.dataverseContacts = [{'contactEmail': 'info@aussda.at'}]
    return dv


def object_full():
    """Get :class:Dataverse() with attributes of full Dataverse.

    Returns
    -------
    pyDataverse.Dataverse()
        :class:Dataverse() with full attributes set.

    """
    dv = object_init()
    dv.alias = 'science'
    dv.name = 'Scientific Research'
    dv.dataverseContacts = [{'contactEmail': 'pi@example.edu'},{'contactEmail': 'student@example.edu'}]
    dv.affiliation = 'Scientific Research University'
    dv.description = 'We do all the science.'
    dv.dataverseType = 'LABORATORY'
    return dv


def dict_flat_dict_min():
    """Get flat dict for dict() of minimum Dataverse.

    Returns
    -------
    dict
        Flat dict with minimum Dataverse data.

    """
    data = {
        'alias': 'test-pyDataverse',
        'name': 'Test pyDataverse',
        'dataverseContacts': [
            {'contactEmail': 'info@aussda.at'}
        ],
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/dataverse_upload_schema.json',
        'attr_dv_up_values': attr_dv_up_values()
    }
    return data


def dict_flat_dict_full():
    """Get flat dict for dict() of full Dataverse.

    Returns
    -------
    dict
        Flat dict with full Dataverse data.

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
        'dataverseType': 'LABORATORY',
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/dataverse_upload_schema.json',
        'attr_dv_up_values': attr_dv_up_values()
    }
    return data


def json_upload_min():
    """Get JSON string of minimum Dataverse.

    Returns
    -------
    string
        JSON string.

    """
    data = read_file('tests/data/dataverse_upload_min.json')
    return data


def json_upload_full():
    """Get JSON string of full Dataverse.

    Returns
    -------
    string
        JSON string.

    """
    data = read_file('tests/data/dataverse_upload_full.json')
    return data


def attr_dv_up_values():
    """List of attributes import or export in format `dataverse_upload`.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
    data = [
        'affiliation',
        'alias',
        'dataverseContacts',
        'dataverseType',
        'description',
        'name'
    ]
    return data


def attr_dv_up_required():
    """List of attributes required for `dataverse_upload` JSON.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
    data = [
        'alias',
        'dataverseContacts',
        'name'
    ]
    return data


class TestDataverse(object):
    """Tests for Dataverse()."""

    def test_dataverse_init(self):
        """Test Dataverse.__init__()."""
        obj = Dataverse()
        obj_assert = object_init()
        assert obj.__dict__ == obj_assert.__dict__

    def test_dataverse_set_min_valid(self):
        """Test Dataverse.set() with minimum data."""
        obj = object_init()
        result = obj.set(dict_flat_set_min())
        obj_assert = object_min()
        assert result
        assert obj.__dict__ == obj_assert.__dict__

    def test_dataverse_set_full_valid(self):
        """Test Dataverse.set() with full data."""
        obj = object_init()
        result = obj.set(dict_flat_set_full())
        obj_assert = object_full()
        assert result
        assert obj.__dict__ == obj_assert.__dict__

    def test_dataverse_set_invalid(self):
        """Test Dataverse.set() with invalid data."""
        obj = object_init()
        obj_assert = obj
        for dtype in [list(), str(), int(), set(), tuple()]:
            result = obj.set(list())
            assert not result
            assert obj.__dict__ == obj_assert.__dict__

    def test_dataverse_get_min_valid(self):
        """Test Dataverse.get() with min data."""
        obj = object_min()
        dict_flat = obj.get()
        dict_assert = dict_flat_dict_min()
        assert dict_flat == dict_assert

    def test_dataverse_get_full_valid(self):
        """Test Dataverse.get() with full data."""
        obj = object_full()
        dict_flat = obj.get()
        dict_assert = dict_flat_dict_full()
        assert dict_flat == dict_assert

    def test_dataverse_from_json_min_valid(self):
        """Test Dataverse.from_json() with min data."""
        obj = object_init()
        result = obj.from_json('tests/data/dataverse_upload_min.json', validate=False)
        obj_assert = object_min()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

    def test_dataverse_from_json_full_valid(self):
        """Test Dataverse.from_json() with full data."""
        obj = object_init()
        result = obj.from_json('tests/data/dataverse_upload_full.json')
        obj_assert = object_full()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

        obj = object_init()
        result = obj.from_json('tests/data/dataverse_upload_full.json', validate=False)
        obj_assert = object_full()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

        obj = object_init()
        result = obj.from_json('tests/data/dataverse_upload_full.json', validate=False, filename_schema='wrong')
        obj_assert = object_full()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

    def test_dataverse_from_json_invalid(self):
        """Test Dataverse.from_json() with non-valid format."""
        # filename_schema=wrong
        with pytest.raises(FileNotFoundError):
            obj = object_init()
            obj.from_json(os.path.join(TEST_DIR, '/data/dataverse_upload_min.json'), filename_schema='wrong')

        # format=wrong
        obj = object_init()
        result = obj.from_json(os.path.join(TEST_DIR, '/data/dataverse_upload_min.json'), format='wrong')
        obj_assert = object_init()
        assert not result
        assert obj_assert.__dict__ == obj.__dict__

        # format=wrong, validate=False
        obj = object_init()
        result = obj.from_json(os.path.join(TEST_DIR, '/data/dataverse_upload_min.json'), format='wrong', validate=False)
        obj_assert = object_init()
        assert not result
        assert obj_assert.__dict__ == obj.__dict__

    def test_dataverse_to_json_min_valid(self):
        """Test Dataverse.to_json() with min data."""
        obj = object_min()
        result = obj.to_json()
        dict_assert = json.loads(json_upload_min())
        assert result
        assert isinstance(result, str)
        assert json.loads(result) == dict_assert

    def test_dataverse_to_json_full_valid(self):
        """Test Dataverse.to_json() with full data."""
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

    def test_dataverse_to_json_invalid(self):
        """Test Dataverse.to_json() with non-valid data."""
        with pytest.raises(FileNotFoundError):
            obj = object_full()
            result = obj.to_json(filename_schema='wrong')

        obj = object_full()
        result = obj.to_json(format='wrong')
        assert not result

        obj = object_full()
        result = obj.to_json(format='wrong', validate=False)
        assert not result

    def test_dataverse_validate_json_valid(self):
        """Test Dataverse.validate_json() with valid data."""
        obj = object_min()
        result = obj.validate_json()
        assert result

        obj = object_full()
        result = obj.validate_json()
        assert result

    def test_dataverse_validate_json_invalid(self):
        """Test Dataverse.validate_json() with non-valid data."""
        # init data
        with pytest.raises(jsonschema.exceptions.ValidationError):
            obj = object_init()
            obj.validate_json()

        # remove required attributes
        required_attributes = attr_dv_up_required()
        for attr in required_attributes:
            with pytest.raises(jsonschema.exceptions.ValidationError):
                obj = object_min()
                delattr(obj, attr)
                obj.validate_json()

        # file not found
        with pytest.raises(FileNotFoundError):
            obj = object_min()
            obj.validate_json(filename_schema='wrong')

        # format=wrong
        obj = object_min()
        result = obj.validate_json(format='wrong')
        assert not result

        obj = object_full()
        result = obj.validate_json(format='wrong')
        assert not result

        # format=wrong, filename_schema=wrong
        obj = object_min()
        result = obj.validate_json(format='wrong', filename_schema='wrong')
        assert not result

        obj = object_full()
        result = obj.validate_json(format='wrong', filename_schema='wrong')
        assert not result

    def test_dataverse_to_json_from_json_min(self):
        """Test Dataverse to JSON from JSON with min data."""
        if not os.environ.get('TRAVIS'):
            obj = object_min()
            data = obj.to_json(validate=False, as_dict=True)
            write_json(os.path.join(TEST_DIR + '/data/output/dataverse_upload_min.json'), data)
            obj_new = Dataverse()
            obj_new.from_json(os.path.join(TEST_DIR + '/data/output/dataverse_upload_min.json'), validate=False)
            assert obj_new.__dict__ == obj.__dict__

    def test_dataverse_to_json_from_json_full(self):
        """Test Dataverse to JSON from JSON with full data."""
        if not os.environ.get('TRAVIS'):
            obj = object_full()
            data = obj.to_json(validate=False, as_dict=True)
            write_json(os.path.join(TEST_DIR + '/data/output/dataverse_upload_full.json'), data)
            obj_new = Dataverse()
            obj_new.from_json(os.path.join(TEST_DIR + '/data/output/dataverse_upload_full.json'), validate=False)
            assert obj_new.__dict__ == obj.__dict__
