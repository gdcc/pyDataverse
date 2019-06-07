# coding: utf-8
import pytest
from pyDataverse.models import Dataset


class TestDataset(object):
    """Test the Dataset() class initalization."""

    def test_dataset_init(self):
        pass

    def test_dataset_set_dvup(self):
        pass

    def test_dataset_set_dvup_less(self):
        pass

    def test_dataset_set_dvup_more(self):
        pass

    def test_dataset_is_valid(self):
        pass

    def test_dataset_is_valid_not(self):
        pass

    def test_dataset_import_metadata_dv_up(self):

        """Dataset"""
        assert self.license ==
        assert self.termsOfUse ==
        assert self.termsOfAccess ==

        """Citation"""
        assert self.citation_displayName ==
        assert self.title ==
        assert self.subtitle ==
        assert self.alternativeTitle ==
        assert self.alternativeURL ==
        assert self.otherId = []
        assert self.author = []
        assert self.datasetContact = []
        assert self.dsDescription = []
        assert self.subject = []
        assert self.keyword = []
        assert self.topicClassification = []
        assert self.publication = []
        assert self.notesText ==
        assert self.producer = []
        assert self.productionDate ==
        assert self.productionPlace ==
        assert self.contributor = []
        assert self.grantNumber = []
        assert self.distributor = []
        assert self.distributionDate ==
        assert self.depositor ==
        assert self.dateOfDeposit ==
        assert self.timePeriodCovered = []
        assert self.dateOfCollection = []
        assert self.kindOfData = []
        assert self.series = []
        assert self.software = []
        assert self.relatedMaterial = []
        assert self.relatedDatasets = []
        assert self.otherReferences = []
        assert self.dataSources = []
        assert self.originOfSources ==
        assert self.characteristicOfSources ==
        assert self.accessToSources ==

        """Geospatial"""
        assert self.geospatial_displayName ==
        assert self.geographicCoverage = []
        assert self.geographicUnit ==
        assert self.geographicBoundingBox = []

    def test_dataset_import_metadata_wrong(self):
        pass

    def test_dataset_dict_dv_up_valid_minimum(self):
        pass

    def test_dataset_dict_dv_up_valid_full(self):
        pass

    def test_dataset_dict_dv_up_valid_not(self):
        pass

    def test_dataset_dict_all(self):
        pass

    def test_dataset_dict_wrong(self):
        pass

    def test_dataset_json_dv_up(self):
        pass

    def test_dataset_json_all(self):
        pass

    def test_dataset_json_wrong(self):
        pass

    def test_dataset_export_metadata_dv_up(self):
        pass

    def test_dataset_export_metadata_wrong(self):
        pass
