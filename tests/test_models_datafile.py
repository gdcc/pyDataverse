# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Datafile data model tests."""
import json
import os

import jsonschema

import pytest
from pyDataverse.models import Datafile, DVObject

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
FILENAME_DATA_FULL = 'tests/data/datafile_upload_full.json'
FILENAME_DATA_MIN = 'tests/data/datafile_upload_min.json'
FILENAME_SCHEMA = 'schemas/json/datafile_upload_schema.json'
INVALID_SCHEMA_FILENAMES = [[], 12, set(), tuple(), True, False]
INVALID_JSON_FILENAMES = INVALID_SCHEMA_FILENAMES + [None]
INVALID_DATA_FORMATS = [[], 12, set(), tuple(), True, False]
INVALID_VALIDATE = [None, 'wrong', {}, []]
INVALID_JSON_DATA = [[], 12, set(), tuple(), True, False]
INVALID_SET_DATA = [[], 'wrong', 12, set(), tuple(), True, False, None]
FILENAME_JSON_OUTPUT = os.path.join(TEST_DIR + '/data/output/datafile_pytest.json')


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
    with open(filename, mode) as f:
        data = f.read()
    return data


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
    with open(filename, mode, encoding=encoding) as f:
        json.dump(data, f, indent=2)


def data_object():
    """Get Datafile object.

    Returns
    -------
    pydataverse.models.Datafile
        Datafile object.
    """
    return Datafile()


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


def object_data_init():
    """Get dictionary for Datafile with initial attributes.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    data = {
        'default_json_format': 'dataverse_upload',
        'default_json_schema_filename': FILENAME_SCHEMA,
        'allowed_json_formats': ['dataverse_upload', 'dataverse_download'],
        'json_dataverse_upload_attr': [
            'description',
            'categories',
            'restrict',
            'title',
            'directoryLabel',
            'pid',
            'filename'
        ]
    }
    return data


def object_data_min():
    """Get dictionary for Datafile with minimum attributes.

    Returns
    -------
    dict
        Minimum Datafile metadata.

    """
    data = {
        'pid': 'doi:10.11587/RRKEA9',
        'filename': '10109_qu_de_v1_0.pdf'
    }
    data.update(object_data_init())
    return data


def object_data_full():
    """Get flat dict for :func:`get()` with initial data of Datafile.

    Returns
    -------
    dict
        Minimum Datafile metadata.

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
    data.update(object_data_init())
    return data


def dict_flat_get_init():
    """Get flat dict for :func:`get()` with init data of Datafile.

    Returns
    -------
    dict
        Initial Datafile dictionary returned by :func:`get().

    """
    data = {
        'default_json_format': 'dataverse_upload',
        'default_json_schema_filename': FILENAME_SCHEMA,
        'allowed_json_formats': ['dataverse_upload', 'dataverse_download'],
        'json_dataverse_upload_attr': json_dataverse_upload_attr()
    }
    return data


def dict_flat_get_min():
    """Get flat dict for :func:`get()` with minimum data of Datafile.

    Returns
    -------
    dict
        Minimum Datafile dictionary returned by :func:`get().

    """
    data = {
        'pid': 'doi:10.11587/RRKEA9',
        'filename': '10109_qu_de_v1_0.pdf'
    }
    data.update(dict_flat_get_init())
    return data


def dict_flat_get_full():
    """Get flat dict for :func:`get()` with full data of Datafile.

    Returns
    -------
    dict
        Full Datafile dictionary returned by :func:`get().

    """
    data = {
        'pid': 'doi:10.11587/NVWE8Y',
        'filename': '20001_ta_de_v1_0.pdf',
        'description': 'Another data file.',
        'restrict': True,
        'categories': ['Documentation'],
        'title': 'Questionnaire',
        'directoryLabel': 'data/subdir1',
    }
    data.update(dict_flat_get_init())
    return data


def json_upload_min():
    """Get JSON string of minimum Datafile.

    Returns
    -------
    dict
        JSON string.

    """
    data = read_file(FILENAME_DATA_MIN)
    return data


def json_upload_full():
    """Get JSON string of full Datafile.

    Returns
    -------
    str
        JSON string.

    """
    data = read_file(FILENAME_DATA_FULL)
    return data


def json_dataverse_upload_attr():
    """List of attributes import or export in format `dataverse_upload`.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
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


def json_dataverse_upload_required_attr():
    """List of attributes required for `dataverse_upload` JSON.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
    data = [
        'pid',
        'filename'
    ]
    return data


class TestDatafileGeneric(object):
    """Generic tests for Datafile()."""

    def test_datafile_set_and_get_valid(self):
        """Test Datafile.get() with valid data."""
        data = [
            ((dict_flat_set_min(), object_data_min()), dict_flat_get_min()),
            ((dict_flat_set_full(), object_data_full()), dict_flat_get_full()),
            (({}, object_data_init()), dict_flat_get_init())
        ]

        pdv = data_object()
        pdv.set(dict_flat_set_min())
        assert isinstance(pdv.get(), dict)

        for input, data_eval in data:
            pdv = data_object()
            pdv.set(input[0])
            data = pdv.get()
            for key, val in data_eval.items():
                assert data[key] == input[1][key] == data_eval[key]
            assert len(data) == len(input[1]) == len(data_eval)


    def test_datafile_set_invalid(self):
        """Test Datafile.set() with invalid data."""

        # invalid data
        for data in INVALID_SET_DATA:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(data)


    def test_datafile_from_json_valid(self):
        """Test Datafile.from_json() with valid data."""
        data = [
            (({json_upload_min()}, {}), object_data_min()),
            (({json_upload_full()}, {}), object_data_full()),
            (({json_upload_min()}, {'data_format': 'dataverse_upload'}), object_data_min()),
            (({json_upload_min()}, {'validate': False}), object_data_min()),
            (({json_upload_min()}, {'filename_schema': 'wrong', 'validate': False}), object_data_min()),
            (({json_upload_min()}, {'filename_schema': FILENAME_SCHEMA, 'validate': True}), object_data_min()),
            (({'{}'}, {'validate': False}), object_data_init())
        ]

        for input, data_eval in data:
            pdv = data_object()
            args = input[0]
            kwargs = input[1]
            pdv.from_json(*args, **kwargs)

            for key, val in data_eval.items():
                assert getattr(pdv, key) == data_eval[key]
            assert len(pdv.__dict__) == len(data_eval)


    def test_datafile_from_json_invalid(self):
        """Test Datafile.from_json() with invalid data."""
        # invalid data
        for data in INVALID_JSON_DATA:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(data, validate=False)

        with pytest.raises(json.decoder.JSONDecodeError):
            pdv = data_object()
            pdv.from_json('wrong', validate=False)

        # invalid `filename_schema`
        with pytest.raises(FileNotFoundError):
            pdv = data_object()
            pdv.from_json(json_upload_min(), filename_schema='wrong')

        for filename_schema in INVALID_SCHEMA_FILENAMES:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(json_upload_min(), filename_schema=filename_schema)

        # invalid `data_format`
        for data_format in INVALID_DATA_FORMATS + ['wrong']:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(json_upload_min(), data_format=data_format, validate=False)

        # invalid `validate`
        for validate in INVALID_VALIDATE:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(json_upload_min(), validate=validate)

        with pytest.raises(jsonschema.exceptions.ValidationError):
            pdv = data_object()
            pdv.from_json('{}')

        for attr in json_dataverse_upload_required_attr():
            with pytest.raises(jsonschema.exceptions.ValidationError):
                pdv = data_object()
                data = json.loads(json_upload_min())
                del data[attr]
                data = json.dumps(data)
                pdv.from_json(data, validate=True)


    def test_datafile_to_json_valid(self):
        """Test Datafile.to_json() with valid data."""
        data = [
            ((dict_flat_set_min(), {}), json.loads(json_upload_min())),
            ((dict_flat_set_full(), {}), json.loads(json_upload_full())),
            ((dict_flat_set_min(), {'data_format': 'dataverse_upload'}), json.loads(json_upload_min())),
            ((dict_flat_set_min(), {'validate': False}), json.loads(json_upload_min())),
            ((dict_flat_set_min(), {'filename_schema': 'wrong', 'validate': False}), json.loads(json_upload_min())),
            ((dict_flat_set_min(), {'filename_schema': FILENAME_SCHEMA, 'validate': True}), json.loads(json_upload_min())),
            (({}, {'validate': False}), {})
        ]

        pdv = data_object()
        pdv.set(dict_flat_set_min())
        assert isinstance(pdv.to_json(), str)

        for input, data_eval in data:
            pdv = data_object()
            pdv.set(input[0])
            kwargs = input[1]
            data = json.loads(pdv.to_json(**kwargs))
            for key, val in data_eval.items():
                assert data[key] == data_eval[key]
            assert len(data) == len(data_eval)


    def test_datafile_to_json_invalid(self):
        """Test Datafile.to_json() with non-valid data."""
        # invalid `filename_schema`
        with pytest.raises(FileNotFoundError):
            obj = data_object()
            result = obj.to_json(filename_schema='wrong')

        for filename_schema in INVALID_SCHEMA_FILENAMES:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.to_json(filename_schema=filename_schema)

        # invalid `data_format`
        for data_format in INVALID_DATA_FORMATS + ['wrong']:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(dict_flat_set_min())
                pdv.to_json(data_format=data_format, validate=False)

        # invalid `validate`
        for validate in INVALID_VALIDATE:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(dict_flat_set_min())
                pdv.to_json(validate=validate)

        with pytest.raises(jsonschema.exceptions.ValidationError):
            pdv = data_object()
            pdv.set({})
            pdv.to_json()

        for attr in json_dataverse_upload_required_attr():
            with pytest.raises(jsonschema.exceptions.ValidationError):
                pdv = data_object()
                data = json.loads(json_upload_min())
                del data[attr]
                pdv.set(data)
                pdv.to_json(validate=True)


    def test_datafile_validate_json_valid(self):
        """Test Datafile.validate_json() with valid data."""
        data = [
            ((dict_flat_set_min(), {}), True),
            ((dict_flat_set_full(), {}), True),
            ((dict_flat_set_min(), {'data_format': 'dataverse_upload'}), True),
            ((dict_flat_set_min(), {'data_format': 'dataverse_upload', 'filename_schema': FILENAME_SCHEMA}), True),
            ((dict_flat_set_min(), {'filename_schema': FILENAME_SCHEMA}), True)
        ]

        for input, data_eval in data:
            pdv = data_object()
            pdv.set(input[0])
            kwargs = input[1]

            assert pdv.validate_json() == data_eval


    def test_datafile_validate_json_invalid(self):
        """Test Datafile.validate_json() with non-valid data."""
        # invalid data
        for attr in json_dataverse_upload_required_attr():
            with pytest.raises(jsonschema.exceptions.ValidationError):
                for data in [dict_flat_set_min(), dict_flat_set_full()]:
                    pdv = data_object()
                    pdv.set(data)
                    delattr(pdv, attr)
                    pdv.validate_json()

        # invalid `filename_schema`
        with pytest.raises(FileNotFoundError):
            pdv = data_object()
            pdv.set(dict_flat_set_min())
            pdv.validate_json(filename_schema='wrong')

        for filename_schema in INVALID_SCHEMA_FILENAMES:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(dict_flat_set_min())
                pdv.validate_json(filename_schema=filename_schema)



class TestDatafileSpecific(object):
    """Specific tests for Datafile()."""

    def test_datafile_init_valid(self):
        """Test Datafile.__init__() with valid data."""
        # specific
        data = [
            (Datafile(), object_data_init()),
            (Datafile(dict_flat_set_min()), object_data_min()),
            (Datafile(dict_flat_set_full()), object_data_full()),
            (Datafile({}), object_data_init())
        ]

        for pdv, data_eval in data:
            for key, val in data_eval.items():
                assert getattr(pdv, key) == data_eval[key]
            assert len(pdv.__dict__) == len(data_eval)


    def test_datafile_init_invalid(self):
        """Test Datafile.init() with invalid data."""
        pdv = Datafile()

        # invalid data
        for data in INVALID_DATA_FORMATS:
            with pytest.raises(AssertionError):
                pdv.set(data)


if not os.environ.get('TRAVIS'):
    class TestDatafileGenericTravisNot(object):
        """Generic tests for Datafile(), not running on Travis (no file-write permissions)."""

        def test_dataverse_from_json_to_json_valid(self):
            """Test Dataverse to JSON from JSON with valid data."""
            data = [
                ({json_upload_min()}, {}),
                ({json_upload_full()}, {}),
                ({json_upload_min()}, {'data_format': 'dataverse_upload'}),
                ({json_upload_min()}, {'validate': False}),
                ({json_upload_min()}, {'filename_schema': 'wrong', 'validate': False}),
                ({json_upload_min()}, {'filename_schema': FILENAME_SCHEMA, 'validate': True}),
                ({'{}'}, {'validate': False})
            ]

            for args_from, kwargs_from in data:
                pdv_start = data_object()
                args = args_from
                kwargs = kwargs_from
                pdv_start.from_json(*args, **kwargs)
                if 'validate' in kwargs:
                    if kwargs['validate'] == False:
                        kwargs = {'validate': False}
                write_json(FILENAME_JSON_OUTPUT, json.loads(pdv_start.to_json(**kwargs)))
                pdv_end = data_object()
                kwargs = kwargs_from
                pdv_end.from_json(read_file(FILENAME_JSON_OUTPUT), **kwargs)

                for key, val in pdv_end.get().items():
                    assert getattr(pdv_start, key) == getattr(pdv_end, key)
                assert len(pdv_start.__dict__) == len(pdv_end.__dict__,)
