# coding: utf-8
import os
from pyDataverse.models import Dataset
from pyDataverse.models import Dataverse

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class TestDataverse(object):
    """Test the Api() class initalization."""

    def test_dataverse_init(self):
        dv = Dataverse()

        assert isinstance(dv.datasets, list)
        assert len(dv.datasets) == 0
        assert isinstance(dv.dataverses, list)
        assert len(dv.dataverses) == 0
        assert not dv.pid
        assert not dv.name
        assert not dv.alias
        assert isinstance(dv.dataverseContacts, list)
        assert len(dv.dataverseContacts) == 0
        assert not dv.affiliation
        assert not dv.description
        assert not dv.dataverseType

    def test_dataverse_set_dv_up(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)

        assert isinstance(dv.datasets, list)
        assert not dv.datasets
        assert isinstance(dv.dataverses, list)
        assert not dv.dataverses
        assert not dv.pid
        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert len(dv.dataverseContacts) == 1
        assert dv.dataverseContacts[0]['contactEmail'] == 'info@aussda.at'

    def test_dataverse_is_valid_valid(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)

        assert dv.is_valid()

    def test_dataverse_is_valid_not(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)
        dv.name = None

        assert not dv.name
        assert not dv.is_valid()

    def test_dataverse_dict_dv_up_valid(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)

        assert dv.dict()
        assert isinstance(dv.dict(), dict)

    def test_dataverse_dict_valid_all(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)
        dv.datasets = [Dataset()]
        dv.dataverses = [Dataverse()]
        dv.pid = 'doi:10.11587/EVMUHP'
        data = dv.dict('all')

        assert data
        assert isinstance(data, dict)
        assert data['alias'] == 'test-pyDataverse'
        assert data['name'] == 'Test pyDataverse'
        assert data['dataverseContacts'][0]['contactEmail'] == 'info@aussda.at'
        assert data['pid'] == 'doi:10.11587/EVMUHP'

    def test_dataverse_dict_format_wrong(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)

        assert not dv.dict('wrong')

    def test_dataverse_dict_dv_up_valid_not(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)
        dv.name = None

        assert not dv.dict()

    def test_dataverse_json_dv_up_valid(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)

        assert dv.json()
        assert isinstance(dv.json(), str)

    def test_dataverse_json_dv_up_valid_not(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)
        dv.name = None

        assert not dv.json()

    def test_dataverse_json_valid_all(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)
        dv.datasets = [Dataset()]
        dv.dataverses = [Dataverse()]
        dv.pid = 'doi:10.11587/EVMUHP'
        data = dv.json('all')

        assert data
        assert isinstance(data, str)

    def test_dataverse_json_valid_format_wrong(self, import_dataverse_min):
        data = import_dataverse_min
        dv = Dataverse()
        dv.set(data)
        dv.datasets = [Dataset()]
        dv.dataverses = [Dataverse()]
        dv.pid = 'doi:10.11587/EVMUHP'
        data = dv.json('wrong')

        assert not data

    def test_dataverse_import_metadata_dv_up(self):
        dv = Dataverse()
        dv.import_metadata(TEST_DIR + '/data/dataverse_min.json')

        assert isinstance(dv.datasets, list)
        assert not dv.datasets
        assert isinstance(dv.dataverses, list)
        assert not dv.dataverses
        assert not dv.pid
        assert dv.alias == 'test-pyDataverse'
        assert dv.name == 'Test pyDataverse'
        assert isinstance(dv.dataverseContacts, list)
        assert len(dv.dataverseContacts) == 1
        assert dv.dataverseContacts[0]['contactEmail'] == 'info@aussda.at'

    def test_dataverse_import_metadata_format_wrong(self):
        dv = Dataverse()
        dv.import_metadata(TEST_DIR + '/data/dataverse_min.json', 'wrong_data-format')

        assert isinstance(dv.datasets, list)
        assert len(dv.datasets) == 0
        assert not dv.datasets
        assert isinstance(dv.dataverses, list)
        assert len(dv.dataverses) == 0
        assert not dv.dataverses
        assert not dv.pid
        assert not dv.name
        assert not dv.alias
        assert isinstance(dv.dataverseContacts, list)
        assert len(dv.dataverseContacts) == 0
        assert not dv.dataverseContacts
        assert not dv.affiliation
        assert not dv.description
        assert not dv.dataverseType
