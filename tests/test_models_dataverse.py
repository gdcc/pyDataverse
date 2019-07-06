# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse data model tests."""
import os
from pyDataverse.models import Dataverse

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class TestDataverse(object):
    """Tests for Dataverse()."""

    def test_dataverse_init(self):
        """Test Dataverse.__init__()."""
        dv = Dataverse()

        assert isinstance(dv, Dataverse)
        assert len(dv.__dict__.keys()) == 0

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

        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert isinstance(dv.dataverseContacts, list)
        assert len(dv.dataverseContacts) == 1
        assert dv.dataverseContacts[0]['contactEmail'] == 'info@aussda.at'
        assert len(dv.__dict__.keys()) == 3

        data = import_dataverse_full_dict
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
        assert len(dv.__dict__.keys()) == 6

    def test_dataverse_import_data_dv_up(self):
        """Test Dataverse.import_data() with format=`dv_up`."""
        dv = Dataverse()
        dv.import_data(TEST_DIR + '/data/dataverse_min.json')

        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert len(dv.dataverseContacts) == 1
        assert dv.dataverseContacts[0]['contactEmail'] == 'info@aussda.at'
        assert len(dv.__dict__.keys()) == 3

        dv = Dataverse()
        dv.import_data(TEST_DIR + '/data/dataverse_full.json')

        assert dv.alias == 'science'
        assert dv.name == 'Scientific Research'
        assert dv.affiliation == 'Scientific Research University'
        assert dv.description == 'We do all the science.'
        assert dv.dataverseType == 'LABORATORY'
        assert len(dv.dataverseContacts) == 2
        assert dv.dataverseContacts[0]['contactEmail'] == 'pi@example.edu'
        assert dv.dataverseContacts[1]['contactEmail'] == 'student@example.edu'
        assert len(dv.__dict__.keys()) == 6

    def test_dataverse_import_data_format_wrong(self):
        """Test Dataverse.import_data() with non-valid format."""
        dv = Dataverse()
        dv.import_data(TEST_DIR + '/data/dataverse_min.json', 'wrong')

        assert len(dv.__dict__.keys()) == 0

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
        attr_required = [
            'alias',
            'dataverseContacts',
            'name'
        ]
        for attr in attr_required:
            data = import_dataverse_min_dict
            dv = Dataverse()
            del data[attr]
            dv.set(data)
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
        assert len(dv.dict().keys()) == 3

        data = import_dataverse_full_dict
        dv = Dataverse()
        dv.set(data)

        assert dv.dict()
        assert isinstance(dv.dict(), dict)
        assert len(dv.dict().keys()) == 6

    def test_dataverse_dict_all_valid(self, import_dataverse_min_dict,
                                      import_dataverse_full_dict):
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

        assert len(dv.__dict__.keys()) == 3

        dv.set({
            'pid': 'doi:10.11587/EVMUHP'
        })

        assert len(dv.__dict__.keys()) == 4

        data = dv.dict('all')

        assert data
        assert isinstance(data, dict)
        assert data['pid'] == 'doi:10.11587/EVMUHP'
        assert data['alias'] == 'test-pyDataverse'
        assert data['name'] == 'Test pyDataverse'
        assert len(data['dataverseContacts']) == 1
        assert data['dataverseContacts'][0]['contactEmail'] == 'info@aussda.at'
        assert len(data.keys()) == 4

        data = import_dataverse_full_dict
        dv = Dataverse()
        dv.set(data)

        assert len(dv.__dict__.keys()) == 6

        dv.set({
            'pid': 'doi:10.11587/EVMUHP'
        })

        assert len(dv.__dict__.keys()) == 7

        data = dv.dict('all')

        assert data
        assert isinstance(data, dict)
        assert data['pid'] == 'doi:10.11587/EVMUHP'
        assert data['alias'] == 'science'
        assert data['name'] == 'Scientific Research'
        assert data['affiliation'] == 'Scientific Research University'
        assert data['description'] == 'We do all the science.'
        assert data['dataverseType'] == 'LABORATORY'
        assert len(data['dataverseContacts']) == 2
        assert data['dataverseContacts'][0]['contactEmail'] == 'pi@example.edu'
        assert data['dataverseContacts'][1]['contactEmail'] == 'student@example.edu'
        assert len(data.keys()) == len(dv.__dict__.keys())

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
        dv.pid = 'doi:10.11587/EVMUHP'
        data = dv.json('all')

        assert isinstance(data, str)
        assert len(dv.__dict__.keys()) == 4

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
        dv.pid = 'doi:10.11587/EVMUHP'
        data = dv.json('wrong')

        assert not data
