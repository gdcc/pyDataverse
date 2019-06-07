# coding: utf-8
import pytest
from pyDataverse.models import Dataverse


class TestDataverse(object):
    """Test the Api() class initalization."""

    def test_dataverse_init(self):
        dv = Dataverse()

        assert isinstance(dv.datasets, list)
        assert not dv.datasets
        assert isinstance(dv.dataverses, list)
        assert not dv.dataverses
        assert not dv.pid
        assert not dv.name
        assert not dv.alias
        assert isinstance(dv.contactEmail, list)
        assert not dv.contactEmail
        assert not dv.affiliation
        assert not dv.description
        assert not dv.dataverseType

    def test_dataverse_set_dv_up(self, read_json):
        data = read_json('data/dataverse_minimum_1.json')
        dv = Dataverse()
        dv.set(data)

        assert isinstance(dv.datasets, list)
        assert not dv.datasets
        assert isinstance(dv.dataverses, list)
        assert not dv.dataverses
        assert not dv.pid
        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert isinstance(dv.dataverseContacts, list)
        assert len(dv.dataverseContacts) == 1
        assert dv.dataverseContact[0]['contactEmail'] == 'info@aussda.at'


    def test_dataverse_is_valid(self):
        data = read_json('data/dataverse_minimum_1.json')
        dv = Dataverse()
        dv.set(data)

        assert isinstance(dv.datasets, list)
        assert not dv.datasets
        assert isinstance(dv.dataverses, list)
        assert not dv.dataverses
        assert not dv.pid
        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert isinstance(dv.dataverseContacts, list)
        assert len(dv.dataverseContacts) == 1
        assert dv.dataverseContact[0]['contactEmail'] == 'info@aussda.at'
        assert dv.is_valid()

    def test_dataverse_is_valid_not(self):
        data = read_json('data/dataverse_minimum_1.json')
        dv = Dataverse()
        dv.set(data)
        dv.name = None

        assert not dv.is_valid()
        assert isinstance(dv.datasets, list)
        assert not dv.datasets
        assert isinstance(dv.dataverses, list)
        assert not dv.dataverses
        assert not dv.pid
        assert dv.alias == 'test-pyDataverse'
        assert not dv.name
        assert isinstance(dv.dataverseContacts, list)
        assert len(dv.dataverseContacts) == 1
        assert dv.dataverseContact[0]['contactEmail'] == 'info@aussda.at'

    def test_dataverse_import_metadata_dv_up(self):
        dv = Dataverse()
        dv.import_metadata('data/dataverse_minimum_1.json')

        assert isinstance(dv.datasets, list)
        assert not dv.datasets
        assert isinstance(dv.dataverses, list)
        assert not dv.dataverses
        assert not dv.pid
        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert isinstance(dv.dataverseContacts, list)
        assert len(dv.dataverseContacts) == 1
        assert dv.dataverseContact[0]['contactEmail'] == 'info@aussda.at'

    def test_dataverse_import_metadata_wrong(self):
        dv = Dataverse()
        dv.import_metadata('data/dataverse_minimum_1.json', 'wrong_data-format')
        
        assert isinstance(dv.datasets, list)
        assert not dv.datasets
        assert isinstance(dv.dataverses, list)
        assert not dv.dataverses
        assert not dv.pid
        assert not dv.name
        assert not dv.alias
        assert isinstance(dv.contactEmail, list)
        assert not dv.contactEmail
        assert not dv.affiliation
        assert not dv.description
        assert not dv.dataverseType

    def test_dataverse_dict_dv_up_valid_minimum(self):
        pass

    def test_dataverse_dict_dv_up_valid_full(self):
        pass

    def test_dataverse_dict_dv_up_valid_not(self):
        pass

    def test_dataverse_dict_all(self):
        pass

    def test_dataverse_dict_wrong(self):
        pass

    def test_dataverse_json_dv_up(self):
        pass

    def test_dataverse_json_all(self):
        pass

    def test_dataverse_json_wrong(self):
        pass

    def test_dataverse_export_metadata_dv_up(self):
        pass

    def test_dataverse_export_metadata_wrong(self):
        pass
