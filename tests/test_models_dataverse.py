# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse data model tests."""
import os
from pyDataverse.models import Dataset
from pyDataverse.models import Dataverse

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class TestDataverse(object):
    """Tests for Dataverse()."""

    def test_dataverse_init(self):
        """Test Dataverse.__init__()."""
        dv = Dataverse()

        assert not dv.datasets
        assert not dv.dataverses
        assert not dv.pid
        assert not dv.name
        assert not dv.alias
        assert not dv.contactEmail
        assert not dv.affiliation
        assert not dv.description
        assert not dv.dataverseType

    def test_dataverse_set_dv_up(self, import_dataverse_min_dict,
                                 import_dataverse_full_dict):
        """Test Dataverse.set() with format=`dv_up`.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = import_dataverse_min_dict
        dv = Dataverse()
        dv.set(data)

        assert not dv.datasets
        assert not dv.dataverses
        assert not dv.pid
        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert len(dv.contactEmail) == 1
        assert dv.contactEmail[0] == 'info@aussda.at'

        data = import_dataverse_full_dict
        dv = Dataverse()
        dv.set(data)

        assert not dv.datasets
        assert not dv.dataverses
        assert not dv.pid
        assert dv.alias == 'science'
        assert dv.name == 'Scientific Research'
        assert dv.affiliation == 'Scientific Research University'
        assert dv.description == 'We do all the science.'
        assert dv.dataverseType == 'LABORATORY'
        assert len(dv.contactEmail) == 2
        assert dv.contactEmail[0] == 'pi@example.edu'
        assert dv.contactEmail[1] == 'student@example.edu'

    def test_dataverse_import_metadata_dv_up(self):
        """Test Dataverse.import_metadata() with format=`dv_up`."""
        dv = Dataverse()
        dv.import_metadata(TEST_DIR + '/data/dataverse_min.json')

        assert not dv.datasets
        assert not dv.dataverses
        assert not dv.pid
        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert len(dv.contactEmail) == 1
        assert dv.contactEmail[0] == 'info@aussda.at'

        dv = Dataverse()
        dv.import_metadata(TEST_DIR + '/data/dataverse_full.json')

        assert not dv.datasets
        assert not dv.dataverses
        assert not dv.pid
        assert dv.alias == 'science'
        assert dv.name == 'Scientific Research'
        assert dv.affiliation == 'Scientific Research University'
        assert dv.description == 'We do all the science.'
        assert dv.dataverseType == 'LABORATORY'
        assert len(dv.contactEmail) == 2
        assert dv.contactEmail[0] == 'pi@example.edu'
        assert dv.contactEmail[1] == 'student@example.edu'

    def test_dataverse_import_metadata_format_wrong(self):
        """Test Dataverse.import_metadata() with non-valid format."""
        dv = Dataverse()
        dv.import_metadata(TEST_DIR + '/data/dataverse_min.json', 'wrong')

        assert not dv.datasets
        assert not dv.dataverses
        assert not dv.pid
        assert not dv.name
        assert not dv.alias
        assert not dv.contactEmail
        assert not dv.affiliation
        assert not dv.description
        assert not dv.dataverseType

    def test_dataverse_is_valid_valid(self, import_dataverse_min_dict,
                                      import_dataverse_full_dict):
        """Test Dataverse.is_valid() with valid data.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = import_dataverse_min_dict
        dv = Dataverse()
        dv.set(data)
        assert dv.is_valid()

        data = import_dataverse_full_dict
        dv = Dataverse()
        dv.set(data)
        assert dv.is_valid()

    def test_dataverse_is_valid_not(self, import_dataverse_min_dict):
        """Test Dataverse.is_valid() with non-valid data.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = import_dataverse_min_dict
        attr_required = [
            'alias',
            'contactEmail',
            'name'
        ]
        for attr in attr_required:
            dv = Dataverse()
            dv.set(data)
            dv.set({attr: None})
            assert not hasattr(dv, attr)
            assert not dv.is_valid()

    def test_dataverse_dict_dv_up_valid(self, import_dataverse_min_dict,
                                        import_dataverse_full_dict):
        """Test Dataverse.dict() with format=`dv_up` and valid data.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = import_dataverse_min_dict
        dv = Dataverse()
        dv.set(data)

        assert dv.dict()
        assert isinstance(dv.dict(), dict)

        data = import_dataverse_full_dict
        dv = Dataverse()
        dv.set(data)

        assert dv.dict()
        assert isinstance(dv.dict(), dict)

    def test_dataverse_dict_all_valid(self, import_dataverse_min_dict):
        """Test Dataverse.dict() with format=`all` and valid data.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """

        data = import_dataverse_min_dict
        dv = Dataverse()
        dv.set(data)
        dv.set({
            'datasets': [Dataset()],
            'dataverses': [Dataverse()],
            'pid': 'doi:10.11587/EVMUHP'
        })
        data = dv.dict('all')

        assert data
        assert isinstance(data, dict)
        assert len(data['datasets']) == 1
        assert len(data['dataverses']) == 1
        assert data['pid'] == 'doi:10.11587/EVMUHP'
        assert data['alias'] == 'test-pyDataverse'
        assert data['name'] == 'Test pyDataverse'
        assert len(data['contactEmail']) == 1
        assert data['contactEmail'][0] == 'info@aussda.at'

        assert data
        assert isinstance(data, dict)
        assert not data['datasets']
        assert not data['dataverses']
        assert not data['pid']
        assert data['alias'] == 'science'
        assert data['name'] == 'Scientific Research'
        assert data['affiliation'] == 'Scientific Research University'
        assert data['description'] == 'We do all the science.'
        assert data['dataverseType'] == 'LABORATORY'
        assert len(data['contactEmail']) == 2
        assert data['contactEmail'][0] == 'pi@example.edu'
        assert data['contactEmail'][1] == 'student@example.edu'

    def test_dataverse_dict_format_wrong(self, import_dataverse_min_dict):
        """Test Dataverse.dict() with non-valid format.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = import_dataverse_min_dict
        dv = Dataverse()
        dv.set(data)

        assert not dv.dict('wrong')

    def test_dataverse_dict_dv_up_valid_not(self, import_dataverse_min_dict):
        """Test Dataverse.dict() with format=`dv_up` and non-valid data.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = import_dataverse_min_dict
        dv = Dataverse()
        dv.set(data)
        dv.name = None

        assert not dv.dict()

    def test_dataverse_json_dv_up_valid(self, import_dataverse_min_dict):
        """Test Dataverse.json() with format=`dv_up` and valid data.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = import_dataverse_min_dict
        dv = Dataverse()
        dv.set(data)

        assert dv.json()
        assert isinstance(dv.json(), str)

    def test_dataverse_json_dv_up_valid_not(self, import_dataverse_min_dict):
        """Test Dataverse.json() with format=`dv_up` and non-valid data.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = import_dataverse_min_dict
        dv = Dataverse()
        dv.set(data)
        dv.name = None

        assert not dv.json()

    def test_dataverse_json_all_valid(self, import_dataverse_min_dict):
        """Test Dataverse.json() with format=`all` and valid data.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = import_dataverse_min_dict
        dv = Dataverse()
        dv.set(data)
        dv.datasets = [Dataset()]
        dv.dataverses = [Dataverse()]
        dv.pid = 'doi:10.11587/EVMUHP'
        data = dv.json('all')

        assert data
        assert isinstance(data, str)

    def test_dataverse_json_format_wrong_valid(self, import_dataverse_min_dict):
        """Test Dataverse.json() with non-valid format and valid data.

        Parameters
        ----------
        import_dataverse_min_dict : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        """
        data = import_dataverse_min_dict
        dv = Dataverse()
        dv.set(data)
        dv.datasets = [Dataset()]
        dv.dataverses = [Dataverse()]
        dv.pid = 'doi:10.11587/EVMUHP'
        data = dv.json('wrong')

        assert not data
