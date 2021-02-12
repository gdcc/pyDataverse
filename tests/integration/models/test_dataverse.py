"""Dataverse data model tests."""
import json
import jsonschema
import os
import platform
import pytest
from pyDataverse.models import Dataverse
from .conftest import test_config
from ..conftest import ROOT_DIR


def read_file(filename, mode="r"):
    """Read in a file.

    Parameters
    ----------
    filename : str
        Filename with full path.
    mode : str
        Read mode of file. Defaults to `r`. See more at
        https://docs.python.org/3.5/library/functions.html#open

    Returns
    -------
    str
        Returns data as string.

    """
    with open(filename, mode) as f:
        return f.read()


def write_json(filename, data, mode="w", encoding="utf-8"):
    """Write data to a json file.

    Parameters
    ----------
    filename : str
        Filename with full path.
    data : dict
        Data to be written in the json file.
    mode : str
        Write mode of file. Defaults to `w`. See more at
        https://docs.python.org/3/library/functions.html#open

    """
    with open(filename, mode, encoding=encoding) as f:
        json.dump(data, f, indent=2)


def data_object():
    """Get Dataverse object.

    Returns
    -------
    pydataverse.models.Dataverse
        :class:`Dataverse` object.
    """
    return Dataverse()


def dict_flat_set_min():
    """Get flat dict for set() of minimum Dataverse.

    Returns
    -------
    dict
        Flat dict with minimum Dataverse data.
    """
    return {
        "alias": "test-pyDataverse",
        "name": "Test pyDataverse",
        "dataverseContacts": [{"contactEmail": "info@aussda.at"}],
    }


def dict_flat_set_full():
    """Get flat dict for set() of full Dataverse.

    Returns
    -------
    dict
        Flat dict with full Dataverse data.

    """
    return {
        "name": "Scientific Research",
        "alias": "science",
        "dataverseContacts": [
            {"contactEmail": "pi@example.edu"},
            {"contactEmail": "student@example.edu"},
        ],
        "affiliation": "Scientific Research University",
        "description": "We do all the science.",
        "dataverseType": "LABORATORY",
    }


def object_data_init():
    """Get dictionary for Dataverse with initial attributes.

    Returns
    -------
    dict
        Dictionary of init data attributes set.

    """
    return {
        "_Dataverse_default_json_format": "dataverse_upload",
        "_Dataverse_default_json_schema_filename": test_config[
            "dataverse_upload_schema_filename"
        ],
        "_Dataverse_allowed_json_formats": ["dataverse_upload", "dataverse_download"],
        "_Dataverse_json_dataverse_upload_attr": [
            "affiliation",
            "alias",
            "dataverseContacts",
            "dataverseType",
            "description",
            "name",
        ],
        "_internal_attributes": [],
    }


def object_data_min():
    """Get dictionary for Dataverse with minimum attributes.

    Returns
    -------
    pyDataverse.Dataverse
        :class:`Dataverse` with minimum attributes set.

    """
    return {
        "alias": "test-pyDataverse",
        "name": "Test pyDataverse",
        "dataverseContacts": [{"contactEmail": "info@aussda.at"}],
    }


def object_data_full():
    """Get dictionary for Dataverse with full attributes.

    Returns
    -------
    pyDataverse.Dataverse
        :class:`Dataverse` with full attributes set.

    """
    return {
        "alias": "science",
        "name": "Scientific Research",
        "dataverseContacts": [
            {"contactEmail": "pi@example.edu"},
            {"contactEmail": "student@example.edu"},
        ],
        "affiliation": "Scientific Research University",
        "description": "We do all the science.",
        "dataverseType": "LABORATORY",
    }


def dict_flat_get_min():
    """Get flat dict for :func:`get` with minimum data of Dataverse.

    Returns
    -------
    dict
        Minimum Dataverse dictionary returned by :func:`get`.

    """
    return {
        "alias": "test-pyDataverse",
        "name": "Test pyDataverse",
        "dataverseContacts": [{"contactEmail": "info@aussda.at"}],
    }


def dict_flat_get_full():
    """Get flat dict for :func:`get` of full data of Dataverse.

    Returns
    -------
    dict
        Full Datafile dictionary returned by :func:`get`.

    """
    return {
        "name": "Scientific Research",
        "alias": "science",
        "dataverseContacts": [
            {"contactEmail": "pi@example.edu"},
            {"contactEmail": "student@example.edu"},
        ],
        "affiliation": "Scientific Research University",
        "description": "We do all the science.",
        "dataverseType": "LABORATORY",
    }


def json_upload_min():
    """Get JSON string of minimum Dataverse.

    Returns
    -------
    str
        JSON string.

    """
    return read_file("tests/data/api/dataverses/dataverse_upload_min_1.json")


def json_upload_full():
    """Get JSON string of full Dataverse.

    Returns
    -------
    str
        JSON string.

    """
    return read_file("tests/data/api/dataverses/dataverse_upload_full_1.json")


def json_dataverse_upload_attr():
    """List of attributes import or export in format `dataverse_upload`.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
    return [
        "affiliation",
        "alias",
        "dataverseContacts",
        "dataverseType",
        "description",
        "name",
    ]


def json_dataverse_upload_required_attr():
    """List of attributes required for `dataverse_upload` JSON.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
    return ["alias", "dataverseContacts", "name"]


class TestDataverseGenericTravisNot(object):
    """Generic tests for Dataverse(), not running on Travis (no file-write permissions)."""

    @pytest.mark.parametrize(
        "test_input",
        [
            ({json_upload_min()}, {}),
            ({json_upload_full()}, {}),
            ({json_upload_min()}, {"data_format": "dataverse_upload"}),
            ({json_upload_min()}, {"validate": False}),
            ({json_upload_min()}, {"filename_schema": "", "validate": False},),
            ({json_upload_min()}, {"filename_schema": "wrong", "validate": False},),
            (
                {json_upload_min()},
                {
                    "filename_schema": os.path.join(
                        ROOT_DIR,
                        "src/pyDataverse/schemas/json/dataverse_upload_schema.json",
                    ),
                    "validate": True,
                },
            ),
            ({"{}"}, {"validate": False}),
        ],
    )
    def test_dataverse_from_json_to_json_valid(self, tmp_path, test_input):
        """Test Dataverse to JSON from JSON with valid data."""
        pdv_start = data_object()
        args = test_input[0]
        kwargs = test_input[1]
        pdv_start.from_json(*args, **kwargs)
        if "validate" in kwargs:
            if not kwargs["validate"]:
                kwargs = {"validate": False}
        data_out = json.loads(pdv_start.json(**kwargs))
        write_json(os.path.join(tmp_path, "dataverse_integrity_test.json"), data_out)
        data_in = read_file(os.path.join(tmp_path, "dataverse_integrity_test.json"))
        pdv_end = data_object()
        pdv_end.from_json(data_in, **kwargs)

        for key, val in pdv_end.get().items():
            assert getattr(pdv_start, key) == getattr(pdv_end, key)
        assert len(pdv_start.__dict__) == len(pdv_end.__dict__,)
