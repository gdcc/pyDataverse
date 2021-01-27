"""Datafile data model tests."""
import json
import jsonschema
import os
import platform
import pytest

from pyDataverse.models import Datafile
from pyDataverse.utils import read_file, write_json
from ..conftest import test_config


def data_object():
    """Get Datafile object.

    Returns
    -------
    pydataverse.models.Datafile
        :class:`Datafile` object.
    """
    return Datafile()


def dict_flat_set_min():
    """Get flat dict for set() of minimum Datafile.

    Returns
    -------
    dict
        Flat dict with minimum Datafile data.

    """
    return {"pid": "doi:10.11587/RRKEA9", "filename": "10109_qu_de_v1_0.pdf"}


def dict_flat_set_full():
    """Get flat dict for set() of full Datafile.

    Returns
    -------
    dict
        Flat dict with full Datafile data.

    """
    return {
        "pid": "doi:10.11587/NVWE8Y",
        "filename": "20001_ta_de_v1_0.pdf",
        "description": "Another data file.",
        "restrict": True,
        "categories": ["Documentation"],
        "label": "Questionnaire",
        "directoryLabel": "data/subdir1",
    }


def object_data_init():
    """Get dictionary for Datafile with initial attributes.

    Returns
    -------
    dict
        Dictionary of init data attributes set.

    """
    return {
        "_Datafile_default_json_format": "dataverse_upload",
        "_Datafile_default_json_schema_filename": test_config[
            "datafile_upload_schema_filename"
        ],
        "_Datafile_allowed_json_formats": ["dataverse_upload", "dataverse_download"],
        "_Datafile_json_dataverse_upload_attr": [
            "description",
            "categories",
            "restrict",
            "label",
            "directoryLabel",
            "pid",
            "filename",
        ],
        "_internal_attributes": [],
    }


def object_data_min():
    """Get dictionary for Datafile with minimum attributes.

    Returns
    -------
    pyDataverse.Datafile
        :class:`Datafile` with minimum attributes set.

    """
    return {"pid": "doi:10.11587/RRKEA9", "filename": "10109_qu_de_v1_0.pdf"}


def object_data_full():
    """Get flat dict for :func:`get()` with initial data of Datafile.

    Returns
    -------
    pyDataverse.Datafile
        :class:`Datafile` with full attributes set.

    """
    return {
        "pid": "doi:10.11587/NVWE8Y",
        "filename": "20001_ta_de_v1_0.pdf",
        "description": "Another data file.",
        "restrict": True,
        "categories": ["Documentation"],
        "label": "Questionnaire",
        "directoryLabel": "data/subdir1",
    }


def dict_flat_get_min():
    """Get flat dict for :func:`get` with minimum data of Datafile.

    Returns
    -------
    dict
        Minimum Datafile dictionary returned by :func:`get`.

    """
    return {"pid": "doi:10.11587/RRKEA9", "filename": "10109_qu_de_v1_0.pdf"}


def dict_flat_get_full():
    """Get flat dict for :func:`get` of full data of Datafile.

    Returns
    -------
    dict
        Full Datafile dictionary returned by :func:`get`.

    """
    return {
        "pid": "doi:10.11587/NVWE8Y",
        "filename": "20001_ta_de_v1_0.pdf",
        "description": "Another data file.",
        "restrict": True,
        "categories": ["Documentation"],
        "label": "Questionnaire",
        "directoryLabel": "data/subdir1",
    }


def json_upload_min():
    """Get JSON string of minimum Datafile.

    Returns
    -------
    dict
        JSON string.

    """
    return read_file(test_config["datafile_upload_min_filename"])


def json_upload_full():
    """Get JSON string of full Datafile.

    Returns
    -------
    str
        JSON string.

    """
    return read_file(test_config["datafile_upload_full_filename"])


def json_dataverse_upload_attr():
    """List of attributes import or export in format `dataverse_upload`.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
    return [
        "description",
        "categories",
        "restrict",
        "label",
        "directoryLabel",
        "pid",
        "filename",
    ]


def json_dataverse_upload_required_attr():
    """List of attributes required for `dataverse_upload` JSON.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
    return ["pid", "filename"]


class TestDatafileGeneric(object):
    """Generic tests for Datafile()."""

    def test_datafile_set_and_get_valid(self):
        """Test Datafile.get() with valid data."""
        data = [
            ((dict_flat_set_min(), object_data_min()), dict_flat_get_min()),
            ((dict_flat_set_full(), object_data_full()), dict_flat_get_full()),
            (({}, {}), {}),
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
        for data in test_config["invalid_set_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(data)

    def test_datafile_from_json_valid(self):
        """Test Datafile.from_json() with valid data."""
        data = [
            (({json_upload_min()}, {}), object_data_min()),
            (({json_upload_full()}, {}), object_data_full()),
            (
                ({json_upload_min()}, {"data_format": "dataverse_upload"}),
                object_data_min(),
            ),
            (({json_upload_min()}, {"validate": False}), object_data_min()),
            (
                ({json_upload_min()}, {"filename_schema": "wrong", "validate": False},),
                object_data_min(),
            ),
            (
                (
                    {json_upload_min()},
                    {
                        "filename_schema": test_config[
                            "datafile_upload_schema_filename"
                        ],
                        "validate": True,
                    },
                ),
                object_data_min(),
            ),
            (({"{}"}, {"validate": False}), {}),
        ]

        for input, data_eval in data:
            pdv = data_object()
            args = input[0]
            kwargs = input[1]
            pdv.from_json(*args, **kwargs)

            for key, val in data_eval.items():
                assert getattr(pdv, key) == data_eval[key]
            assert len(pdv.__dict__) - len(object_data_init()) == len(data_eval)

    def test_datafile_from_json_invalid(self):
        """Test Datafile.from_json() with invalid data."""
        # invalid data
        for data in test_config["invalid_json_data_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(data, validate=False)

        if int(platform.python_version_tuple()[1]) >= 5:
            for json_string in test_config["invalid_json_strings"]:
                with pytest.raises(json.decoder.JSONDecodeError):
                    pdv = data_object()
                    pdv.from_json(json_string, validate=False)
        else:
            for json_string in test_config["invalid_json_strings"]:
                with pytest.raises(ValueError):
                    pdv = data_object()
                    pdv.from_json(json_string, validate=False)

        # invalid `filename_schema`
        for filename_schema in test_config["invalid_filename_strings"]:
            with pytest.raises(FileNotFoundError):
                pdv = data_object()
                pdv.from_json(json_upload_min(), filename_schema=filename_schema)

        for filename_schema in test_config["invalid_filename_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(json_upload_min(), filename_schema=filename_schema)

        # invalid `data_format`
        for data_format in (
            test_config["invalid_data_format_types"]
            + test_config["invalid_data_format_strings"]
        ):
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(
                    json_upload_min(), data_format=data_format, validate=False
                )

        # invalid `validate`
        for validate in test_config["invalid_validate_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(json_upload_min(), validate=validate)

        with pytest.raises(jsonschema.exceptions.ValidationError):
            pdv = data_object()
            pdv.from_json("{}")

        for attr in json_dataverse_upload_required_attr():
            with pytest.raises(jsonschema.exceptions.ValidationError):
                pdv = data_object()
                data = json.loads(json_upload_min())
                del data[attr]
                data = json.dumps(data)
                pdv.from_json(data, validate=True)

    def test_datafile_to_json_valid(self):
        """Test Datafile.json() with valid data."""
        data = [
            ((dict_flat_set_min(), {}), json.loads(json_upload_min())),
            ((dict_flat_set_full(), {}), json.loads(json_upload_full())),
            (
                (dict_flat_set_min(), {"data_format": "dataverse_upload"}),
                json.loads(json_upload_min()),
            ),
            (
                (dict_flat_set_min(), {"validate": False}),
                json.loads(json_upload_min()),
            ),
            (
                (dict_flat_set_min(), {"filename_schema": "wrong", "validate": False},),
                json.loads(json_upload_min()),
            ),
            (
                (
                    dict_flat_set_min(),
                    {
                        "filename_schema": test_config[
                            "datafile_upload_schema_filename"
                        ],
                        "validate": True,
                    },
                ),
                json.loads(json_upload_min()),
            ),
            (({}, {"validate": False}), {}),
        ]

        pdv = data_object()
        pdv.set(dict_flat_set_min())
        assert isinstance(pdv.json(), str)

        for input, data_eval in data:
            pdv = data_object()
            pdv.set(input[0])
            kwargs = input[1]
            data = json.loads(pdv.json(**kwargs))
            for key, val in data_eval.items():
                assert data[key] == data_eval[key]
            assert len(data) == len(data_eval)

    def test_datafile_to_json_invalid(self):
        """Test Datafile.json() with non-valid data."""
        # invalid `filename_schema`
        for filename_schema in test_config["invalid_filename_strings"]:
            with pytest.raises(FileNotFoundError):
                obj = data_object()
                obj.json(filename_schema=filename_schema)

        for filename_schema in test_config["invalid_filename_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.json(filename_schema=filename_schema)

        # invalid `data_format`
        for data_format in (
            test_config["invalid_data_format_types"]
            + test_config["invalid_data_format_strings"]
        ):
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(dict_flat_set_min())
                pdv.json(data_format=data_format, validate=False)

        # invalid `validate`
        for validate in test_config["invalid_validate_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(dict_flat_set_min())
                pdv.json(validate=validate)

        with pytest.raises(jsonschema.exceptions.ValidationError):
            pdv = data_object()
            pdv.set({})
            pdv.json()

        for attr in json_dataverse_upload_required_attr():
            with pytest.raises(jsonschema.exceptions.ValidationError):
                pdv = data_object()
                data = json.loads(json_upload_min())
                del data[attr]
                pdv.set(data)
                pdv.json(validate=True)

    def test_datafile_validate_json_valid(self):
        """Test Datafile.validate_json() with valid data."""
        data = [
            ((dict_flat_set_min(), {}), True),
            ((dict_flat_set_full(), {}), True),
            ((dict_flat_set_min(), {"data_format": "dataverse_upload"}), True),
            (
                (
                    dict_flat_set_min(),
                    {
                        "data_format": "dataverse_upload",
                        "filename_schema": test_config[
                            "datafile_upload_schema_filename"
                        ],
                    },
                ),
                True,
            ),
            (
                (
                    dict_flat_set_min(),
                    {"filename_schema": test_config["datafile_upload_schema_filename"]},
                ),
                True,
            ),
        ]

        for input, data_eval in data:
            pdv = data_object()
            pdv.set(input[0])

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
        for filename_schema in test_config["invalid_filename_strings"]:
            with pytest.raises(FileNotFoundError):
                pdv = data_object()
                pdv.set(dict_flat_set_min())
                pdv.validate_json(filename_schema=filename_schema)

        for filename_schema in test_config["invalid_filename_types"]:
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
            (Datafile(), {}),
            (Datafile(dict_flat_set_min()), object_data_min()),
            (Datafile(dict_flat_set_full()), object_data_full()),
            (Datafile({}), {}),
        ]

        for pdv, data_eval in data:
            for key, val in data_eval.items():
                assert getattr(pdv, key) == data_eval[key]
            assert len(pdv.__dict__) - len(object_data_init()) == len(data_eval)

    def test_datafile_init_invalid(self):
        """Test Datafile.init() with invalid data."""
        pdv = Datafile()

        # invalid data
        for data in ["invalid_set_types"]:
            with pytest.raises(AssertionError):
                pdv.set(data)


if not os.environ.get("TRAVIS"):

    class TestDatafileGenericTravisNot(object):
        """Generic tests for Datafile(), not running on Travis (no file-write permissions)."""

        def test_dataverse_from_json_to_json_valid(self):
            """Test Dataverse to JSON from JSON with valid data."""
            data = [
                ({json_upload_min()}, {}),
                ({json_upload_full()}, {}),
                ({json_upload_min()}, {"data_format": "dataverse_upload"}),
                ({json_upload_min()}, {"validate": False}),
                ({json_upload_min()}, {"filename_schema": "wrong", "validate": False},),
                (
                    {json_upload_min()},
                    {
                        "filename_schema": test_config[
                            "datafile_upload_schema_filename"
                        ],
                        "validate": True,
                    },
                ),
                ({"{}"}, {"validate": False}),
            ]

            for args_from, kwargs_from in data:
                pdv_start = data_object()
                args = args_from
                kwargs = kwargs_from
                pdv_start.from_json(*args, **kwargs)
                if "validate" in kwargs:
                    if not kwargs["validate"]:
                        kwargs = {"validate": False}
                write_json(
                    test_config["datafile_json_output_filename"],
                    json.loads(pdv_start.json(**kwargs)),
                )
                pdv_end = data_object()
                kwargs = kwargs_from
                pdv_end.from_json(
                    read_file(test_config["datafile_json_output_filename"]), **kwargs
                )

                for key, val in pdv_end.get().items():
                    assert getattr(pdv_start, key) == getattr(pdv_end, key)
                assert len(pdv_start.__dict__) == len(pdv_end.__dict__,)
