# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Datafile data model tests."""
import json
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


def object_min():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = dict_flat_min()
    df = Datafile()
    df.set(data)
    return df


def object_full():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = dict_flat_full()
    df = Datafile()
    df.set(data)
    return df


def dict_flat_min():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = {
        'pid': 'doi:10.11587/RRKEA9',
        'filename': '10109_qu_de_v1_0.pdf'
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
        'pid': 'doi:10.11587/NVWE8Y',
        'filename': '20001_ta_de_v1_0.pdf',
        'description': 'Another data file.',
        'restrict': True,
        'categories': ['Documentation'],
        'title': 'Questionnaire',
        'directoryLabel': 'data/subdir1'
    }
    return data


def json_upload_min():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = read_file('tests/data/datafile_upload_min.json')
    return data


def json_upload_full():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = read_file('tests/data/datafile_upload_full.json')
    return data


def json_upload_full():
    """Import full Dataverse dict.

    Returns
    -------
    dict
        Full Dataverse metadata.

    """
    data = read_file('tests/data/datafile_upload_full.json')
    return data


def assert_dict_full():
    data = {
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/datafile_upload_full_schema.json',
        'attr_dv_up_values': 'LIST',
        'pid': 'doi:10.11587/NVWE8Y',
        'filename': '20001_ta_de_v1_0.pdf',
        'description': 'Another data file.',
        'restrict': True,
        'categories': 'LIST',
        'title': 'Questionnaire',
        'directoryLabel': 'data/subdir1'
    }
    return data


def assert_dict_min():
    data = {
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/datafile_upload_full_schema.json',
        'attr_dv_up_values': 'LIST',
        'pid': 'doi:10.11587/RRKEA9',
        'filename': '10109_qu_de_v1_0.pdf'
    }
    return data


def assert_dict_init():
    data = {
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/datafile_upload_full_schema.json',
        'attr_dv_up_values': 'LIST'
    }
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
        data = assert_dict_init()
        df = Datafile()

        assert isinstance(df, Datafile)
        assert isinstance(df, DVObject)
        assert getattr(df, 'attr_dv_up_values') == attr_dv_up_values()
        assert len(df.__dict__.keys()) == len(data.keys())
        for attr in list(data.keys()):
            if data[attr] != 'LIST':
                assert getattr(df, attr) == data[attr]

    def test_datafile_set_valid(self):
        """Test Datafile.set() with format=`dv_up`.

        Parameters
        ----------
        import_datafile_full_dict : dict
            Fixture, which returns a flat datafile dict().

        """
        data = dict_flat_min()
        data_assert = assert_dict_min()
        df = Datafile()
        df.set(data)

        assert getattr(df, 'attr_dv_up_values') == attr_dv_up_values()
        for attr in list(data_assert.keys()):
            if data_assert[attr] != 'LIST':
                assert data_assert[attr] == getattr(df, attr)
        assert len(df.__dict__.keys()) == len(data_assert.keys())

        data = dict_flat_full()
        data_assert = assert_dict_full()
        df = Datafile()
        df.set(data)

        assert getattr(df, 'attr_dv_up_values') == attr_dv_up_values()
        assert df.categories == ['Documentation']
        for attr in list(data_assert.keys()):
            if data_assert[attr] != 'LIST':
                assert data_assert[attr] == getattr(df, attr)
        assert len(df.__dict__.keys()) == len(data_assert.keys())

    def test_datafile_from_json_dv_up_valid(self):
        """Test Dataverse.import_data() with format=`dv_up`."""
        data_assert = dict_flat_min()
        df_assert = object_min()
        df = Datafile()
        df.from_json('tests/data/datafile_upload_min.json')

        assert df_assert.__dict__ == df.__dict__
        assert getattr(df, 'attr_dv_up_values') == attr_dv_up_values()
        for attr in list(data_assert.keys()):
            if data_assert[attr] != 'LIST':
                assert data_assert[attr] == getattr(df_assert, attr)
        assert len(df.__dict__.keys()) == len(df_assert.__dict__.keys())

        data_assert = dict_flat_full()
        df_assert = object_full()
        df = Datafile()
        df.from_json('tests/data/datafile_upload_full.json')

        assert df_assert.__dict__ == df.__dict__
        assert getattr(df, 'attr_dv_up_values') == attr_dv_up_values()
        assert df.categories == ['Documentation']
        for attr in list(data_assert.keys()):
            if data_assert[attr] != 'LIST':
                assert data_assert[attr] == getattr(df_assert, attr)
        assert len(df.__dict__.keys()) == len(df_assert.__dict__.keys())

    def test_datafile_from_json_format_invalid(self):
        """Test Dataverse.import_data() with non-valid format."""
        data_assert = assert_dict_init()
        df = Datafile()
        df.from_json('tests/data/datafile_upload_min.json', format='wrong')

        assert getattr(df, 'attr_dv_up_values') == attr_dv_up_values()
        for attr in list(data_assert.keys()):
            if data_assert[attr] != 'LIST':
                assert data_assert[attr] == getattr(df, attr)
        assert len(df.__dict__.keys()) == len(data_assert.keys())

    def test_datafile_dict_valid(self):
        """Test Datafile.dict() with format=`dv_up` and valid data.

        Parameters
        ----------
        import_datafile_min_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        df = object_min()
        data_min = dict_flat_min()
        data_assert = assert_dict_min()
        data = df.dict()

        assert data
        assert isinstance(data, dict)
        assert data['attr_dv_up_values'] == attr_dv_up_values()
        for attr in list(data_assert.keys()):
            if data_assert[attr] != 'LIST':
                assert data_assert[attr] == getattr(df, attr)
        assert len(data_assert.keys()) == len(df.__dict__.keys())

        df = object_full()
        data_full = dict_flat_full()
        data_assert = assert_dict_full()
        data = df.dict()

        assert data
        assert isinstance(data, dict)
        assert getattr(df, 'attr_dv_up_values') == attr_dv_up_values()
        assert data['categories'] == ['Documentation']
        for attr in list(data_assert.keys()):
            if data_assert[attr] != 'LIST':
                assert data_assert[attr] == getattr(df, attr)
        assert len(df.__dict__.keys()) == len(data_assert.keys())

    def test_datafile_to_json_dv_up_valid(self):
        """Test Dataverse.json() with format=`dv_up` and valid data.

        Parameters
        ----------
        object_min : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        TODO: Assert content
        """
        df = object_min()

        assert df.to_json()
        assert isinstance(df.to_json(), str)
        assert json.loads(df.to_json()) == json.loads(json_upload_min())

        df = object_full()

        assert df.to_json()
        assert isinstance(df.to_json(), str)
        assert json.loads(df.to_json()) == json.loads(json_upload_full())

    def test_datafile_to_json_format_invalid(self):
        """Test Dataverse.json() with non-valid format and valid data.

        Parameters
        ----------

        """
        df = object_min()
        with pytest.raises(TypeError):
            json_dict = json.loads(df.to_json(format='wrong'))

    def test_datafile_from_json_to_json(self):
        """Test Dataverse pipeline from import to export with format=`dv_up`."""
        if not os.environ.get('TRAVIS'):
            df = Datafile()
            df.from_json(os.path.join(TEST_DIR + '/data/datafile_upload_min.json'))
            json_str = df.to_json()
            assert json.loads(df.to_json()) == json.loads(json_upload_min())

            df = Datafile()
            df.from_json(os.path.join(TEST_DIR + '/data/datafile_upload_full.json'))
            json_str = df.to_json()
            assert json.loads(df.to_json()) == json.loads(json_upload_full())
