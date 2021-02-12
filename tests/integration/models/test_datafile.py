import json
import jsonschema
import os
import platform
import pytest
from pyDataverse.models import Datafile
from pyDataverse.utils import read_file, write_json
from .conftest import test_config
from ..conftest import ROOT_DIR


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
    return read_file("tests/data/api/datafiles/datafile_upload_min_1.json")


def json_upload_full():
    """Get JSON string of full Datafile.

    Returns
    -------
    str
        JSON string.

    """
    return read_file("tests/data/api/datafiles/datafile_upload_full_1.json")


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


class TestDatafileGenericTravisNot(object):
    """Generic tests for Datafile(), not running on Travis (no file-write permissions)."""

    @pytest.mark.parametrize(
        "test_input",
        [
            ({json_upload_min()}, {}),
            ({json_upload_full()}, {}),
            ({json_upload_min()}, {"data_format": "dataverse_upload"}),
            ({json_upload_min()}, {"validate": False}),
            ({json_upload_min()}, {"filename_schema": "wrong", "validate": False},),
            (
                {json_upload_min()},
                {
                    "filename_schema": os.path.join(
                        ROOT_DIR,
                        "src/pyDataverse/schemas/json/datafile_upload_schema.json",
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
        write_json(
            os.path.join(tmp_path, "datafile_integrity_test.json"),
            json.loads(pdv_start.json(**kwargs)),
        )
        pdv_end = data_object()
        pdv_end.from_json(
            read_file(os.path.join(tmp_path, "datafile_integrity_test.json")), **kwargs
        )

        for key, val in pdv_end.get().items():
            assert getattr(pdv_start, key) == getattr(pdv_end, key)
        assert len(pdv_start.__dict__) == len(pdv_end.__dict__,)
