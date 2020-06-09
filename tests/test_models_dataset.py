# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataset data model tests."""
import json
import os
from pyDataverse.models import Dataset
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


def object_init():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    ds = Dataset()
    ds.default_validate_format = 'dataverse_upload'
    ds.default_validate_schema_filename = 'schemas/json/dataset_upload_default_schema.json'
    return ds

def object_min():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    ds = object_init()
    ds.title = 'Darwin\'s Finches'
    ds.author = [{'authorName': 'Finch, Fiona','authorAffiliation': 'Birds Inc.'}]
    ds.datasetContact = [{'datasetContactEmail': 'finch@mailinator.com','datasetContactName': 'Finch, Fiona'}]
    ds.dsDescription = [{'dsDescriptionValue': 'Darwin\'s finches (also known as the Galápagos finches) are a group of about fifteen species of passerine birds.'}]
    ds.subject = ['Medicine, Health and Life Sciences']
    ds.citation_displayName = 'Citation Metadata'
    return ds


# def object_full():
#     """Import minimum Dataverse dict.
#
#     Returns
#     -------
#     dict
#         Minimum Dataverse metadata.
#
#     """
    # ds = object_init()
    # assert ds.license == 'CC0'
    # assert ds.termsOfUse == 'CC0 Waiver'
    # assert ds.termsOfAccess == 'Terms of Access'
    # assert ds.citation_displayName == 'Citation Metadata'
    # assert ds.title == 'Replication Data for: Title'
    # assert ds.subtitle == 'Subtitle'
    # assert ds.alternativeTitle == 'Alternative Title'
    # assert ds.alternativeURL == 'http://AlternativeURL.org'
    # assert ds.otherId =
    # ds.author
    #     assert d['authorName'] in ['LastAuthor1, FirstAuthor1']
    #     assert d['authorAffiliation'] in ['AuthorAffiliation1']
    #     assert d['authorIdentifierScheme'] in ['ORCID']
    #     assert d['authorIdentifier'] in ['AuthorIdentifier1']
    # for d in ds.datasetContact:
    #     assert d['datasetContactName'] in ['LastContact1, FirstContact1']
    #     assert d['datasetContactAffiliation'] in ['ContactAffiliation1']
    #     assert d['datasetContactEmail'] in ['ContactEmail1@mailinator.com']
    # for d in ds.dsDescription:
    #     assert d['dsDescriptionValue'] in ['DescriptionText2']
    #     assert d['dsDescriptionDate'] in ['1000-02-02']
    # assert ds.subject == ['Agricultural Sciences',
    #                       'Business and Management', 'Engineering', 'Law']
    # for d in ds.keyword:
    #     assert d['keywordValue'] in ['KeywordTerm1']
    #     assert d['keywordVocabulary'] in ['KeywordVocabulary1']
    #     assert d['keywordVocabularyURI'] in ['http://KeywordVocabularyURL1.org']
    # assert isinstance(ds.topicClassification, list)
    # assert len(ds.topicClassification) == 1
    # for d in ds.topicClassification:
    #     assert d['topicClassValue'] in ['Topic Class Value1']
    #     assert d['topicClassVocab'] in ['Topic Classification Vocabulary']
    # assert isinstance(ds.publication, list)
    # for d in ds.publication:
    #     assert d['publicationCitation'] in ['RelatedPublicationCitation1']
    #     assert d['publicationIDType'] in ['ark']
    #     assert d['publicationIDNumber'] in ['RelatedPublicationIDNumber1']
    #     assert d['publicationURL'] in ['http://RelatedPublicationURL1.org']
    # assert ds.notesText == 'Notes1'
    # assert isinstance(ds.producer, list)
    # for d in ds.producer:
    #     assert d['producerName'] in ['LastProducer1, FirstProducer1']
    #     assert d['producerAffiliation'] in ['ProducerAffiliation1']
    #     assert d['producerAbbreviation'] in ['ProducerAbbreviation1']
    #     assert d['producerURL'] in ['http://ProducerURL1.org']
    #     assert d['producerLogoURL'] in ['http://ProducerLogoURL1.org']
    # assert ds.productionDate == '1003-01-01'
    # assert ds.productionPlace == 'ProductionPlace'
    # for d in ds.contributor:
    #     assert d['contributorType'] in ['Data Collector']
    #     assert d['contributorName'] in ['LastContributor1, FirstContributor1']
    # for d in ds.grantNumber:
    #     assert d['grantNumberAgency'] in ['GrantInformationGrantAgency1']
    #     assert d['grantNumberValue'] in ['GrantInformationGrantNumber1']
    #     assert len(d.keys()) == 2
    # for d in ds.distributor:
    #     assert d['distributorName'] in ['LastDistributor1, FirstDistributor1']
    #     assert d['distributorAffiliation'] in ['DistributorAffiliation1']
    #     assert d['distributorAbbreviation'] in ['DistributorAbbreviation1']
    #     assert d['distributorURL'] in ['http://DistributorURL1.org']
    #     assert d['distributorLogoURL'] in ['http://DistributorLogoURL1.org']
    # assert ds.distributionDate == '1004-01-01'
    # assert ds.depositor == 'LastDepositor, FirstDepositor'
    # assert ds.dateOfDeposit == '1002-01-01'
    # for d in ds.timePeriodCovered:
    #     assert d['timePeriodCoveredStart'] in ['1005-01-01']
    #     assert d['timePeriodCoveredEnd'] in ['1005-01-02']
    # assert isinstance(ds.dateOfCollection, list)
    # for d in ds.dateOfCollection:
    #     assert d['dateOfCollectionStart'] in ['1006-01-01']
    #     assert d['dateOfCollectionEnd'] in ['1006-01-01']
    # assert ds.kindOfData == ['KindOfData1', 'KindOfData2']
    # assert ds.series['seriesName'] == 'SeriesName'
    # assert ds.series['seriesInformation'] == 'SeriesInformation'
    # for d in ds.software:
    #     assert d['softwareName'] in ['SoftwareName1']
    #     assert d['softwareVersion'] in ['SoftwareVersion1']
    # assert ds.relatedMaterial == ['RelatedMaterial1', 'RelatedMaterial2']
    # assert ds.relatedDatasets == ['RelatedDatasets1', 'RelatedDatasets2']
    # assert ds.otherReferences == ['OtherReferences1', 'OtherReferences2']
    # assert ds.dataSources == ['DataSources1', 'DataSources2']
    # assert ds.originOfSources == 'OriginOfSources'
    # assert ds.characteristicOfSources == 'CharacteristicOfSourcesNoted'
    # assert ds.accessToSources == 'DocumentationAndAccessToSources'
    #
    # """geospatial"""
    # assert ds.geospatial_displayName == 'Geospatial Metadata'
    # for d in ds.geographicCoverage:
    #     assert d['country'] in ['Afghanistan']
    #     assert d['state'] in ['GeographicCoverageStateProvince1']
    #     assert d['city'] in ['GeographicCoverageCity1']
    #     assert d['otherGeographicCoverage'] in ['GeographicCoverageOther1']
    # assert ds.geographicUnit == ['GeographicUnit1', 'GeographicUnit2']
    # for d in ds.geographicBoundingBox:
    #     assert d['westLongitude'] in ['10']
    #     assert d['eastLongitude'] in ['20']
    #     assert d['northLongitude'] in ['30']
    #     assert d['southLongitude'] in ['40']
    #
    # """socialscience"""
    # assert ds.socialscience_displayName == 'Social Science and Humanities Metadata'
    # assert ds.unitOfAnalysis == ['UnitOfAnalysis1', 'UnitOfAnalysis2']
    # assert ds.universe == ['Universe1', 'Universe2']
    # assert ds.timeMethod == 'TimeMethod'
    # assert ds.dataCollector == 'LastDataCollector1, FirstDataCollector1'
    # assert ds.collectorTraining == 'CollectorTraining'
    # assert ds.frequencyOfDataCollection == 'Frequency'
    # assert ds.samplingProcedure == 'SamplingProcedure'
    # assert ds.targetSampleSize['targetSampleActualSize'] == '100'
    # assert ds.targetSampleSize['targetSampleSizeFormula'] == 'TargetSampleSizeFormula'
    # assert ds.deviationsFromSampleDesign == 'MajorDeviationsForSampleDesign'
    # assert ds.collectionMode == 'CollectionMode'
    # assert ds.researchInstrument == 'TypeOfResearchInstrument'
    # assert ds.dataCollectionSituation == 'CharacteristicsOfDataCollectionSituation'
    # assert ds.actionsToMinimizeLoss == 'ActionsToMinimizeLosses'
    # assert ds.controlOperations == 'ControlOperations'
    # assert ds.weighting == 'Weighting'
    # assert ds.cleaningOperations == 'CleaningOperations'
    # assert ds.datasetLevelErrorNotes == 'StudyLevelErrorNotes'
    # assert ds.responseRate == 'ResponseRate'
    # assert ds.samplingErrorEstimates == 'EstimatesOfSamplingError'
    # assert ds.otherDataAppraisal == 'OtherFormsOfDataAppraisal'
    # assert ds.socialScienceNotes['socialScienceNotesType'] == 'NotesType'
    # assert ds.socialScienceNotes['socialScienceNotesSubject'] == 'NotesSubject'
    # assert ds.socialScienceNotes['socialScienceNotesText'] == 'NotesText'
    #
    # """journal"""
    # assert ds.journal_displayName == 'Journal Metadata'
    # for d in ds.journalVolumeIssue:
    #     assert d['journalVolume'] in ['JournalVolume1']
    #     assert d['journalIssue'] in ['JournalIssue1']
    #     assert d['journalPubDate'] in ['1008-01-01']
    # assert ds.journalArticleType == 'abstract'
#     return ds


def dict_flat_set_min():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = {
        'title': 'Darwin\'s Finches',
        'author': [
            {
                'authorName': 'Finch, Fiona',
                'authorAffiliation': 'Birds Inc.'
            }
        ],
        'datasetContact': [
            {
                'datasetContactEmail': 'finch@mailinator.com',
                'datasetContactName': 'Finch, Fiona'
            }
        ],
        'dsDescription': [
            {
                'dsDescriptionValue': 'Darwin\'s finches (also known as the Galápagos finches) are a group of about fifteen species of passerine birds.'
            }
        ],
        'subject': [
            'Medicine, Health and Life Sciences'
        ],
        'citation_displayName': 'Citation Metadata'
    }
    return data


# def dict_flat_set_full():
#     """Import full Dataverse dict.
#
#     Returns
#     -------
#     dict
#         Full Dataverse metadata.
#
#     """
#     data = {
#         '': '',
#         'citation_displayName': 'Citation Metadata'
#     }
#     return data


def dict_flat_dict_min():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = {
        'title': 'Darwin\'s Finches',
        'author': [
            {
                'authorName': 'Finch, Fiona',
                'authorAffiliation': 'Birds Inc.'
            }
        ],
        'datasetContact': [
            {
                'datasetContactEmail': 'finch@mailinator.com',
                'datasetContactName': 'Finch, Fiona'
            }
        ],
        'dsDescription': [
            {
                'dsDescriptionValue': 'Darwin\'s finches (also known as the Galápagos finches) are a group of about fifteen species of passerine birds.'
            }
        ],
        'subject': [
            'Medicine, Health and Life Sciences'
        ],
        'citation_displayName': 'Citation Metadata',
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/dataset_upload_default_schema.json'
    }
    return data


def json_upload_min():
    """Import minimum Dataverse dict.

    Returns
    -------
    dict
        Minimum Dataverse metadata.

    """
    data = read_file('tests/data/dataset_upload_min_default.json')
    return data


def json_upload_full():
    """Import full Dataverse dict.

    Returns
    -------
    dict
        Full Dataverse metadata.

    """
    data = read_file('tests/data/dataset_upload_full_default.json')
    return data


def attr_dv_up_values():
    data = [
        'org.dataset_id',
        'org.dataverse_id',
        'org.doi',
        'org.privateurl',
        'org.to_upload',
        'org.is_uploaded',
        'org.to_publish',
        'org.is_published',
        'org.to_delete',
        'org.is_deleted',
        'org.to_update',
        'org.is_updated',
        'root'
        'license',
        'termsOfAccess',
        'termsOfUse',
        'otherId',
        'title',
        'subtitle',
        'alternativeTitle',
        'series',
        'notesText',
        'author',
        'dsDescription',
        'subject',
        'keyword',
        'topicClassification',
        'language',
        'grantNumber',
        'dateOfCollection',
        'kindOfData',
        'dataSources',
        'accessToSources',
        'alternativeURL',
        'characteristicOfSources',
        'dateOfDeposit',
        'depositor',
        'distributionDate',
        'otherReferences',
        'productionDate',
        'productionPlace',
        'contributor',
        'relatedDatasets',
        'relatedMaterial',
        'datasetContact',
        'distributor',
        'producer',
        'publication',
        'software',
        'timePeriodCovered',
        'geographicUnit',
        'geographicBoundingBox',
        'geographicCoverage',
        'actionsToMinimizeLoss',
        'cleaningOperations',
        'collectionMode',
        'collectorTraining',
        'controlOperations',
        'dataCollectionSituation',
        'dataCollector',
        'datasetLevelErrorNotes',
        'deviationsFromSampleDesign',
        'frequencyOfDataCollection',
        'otherDataAppraisal',
        'socialScienceNotes',
        'researchInstrument',
        'responseRate',
        'samplingErrorEstimates',
        'samplingProcedure',
        'unitOfAnalysis',
        'universe',
        'timeMethod',
        'weighting'
    ]
    return data


class TestDataset(object):
    """Tests for Dataset()."""

    def test_dataset_init(self):
        """Test Dataset.__init__()."""
        obj_assert = object_init()
        obj = Dataset()

        assert obj.__dict__ == obj_assert.__dict__

    def test_dataset_set_valid(self):
        """Test Dataset.set() with format=`dv_up`.

        Parameters
        ----------
        import_dataset_min_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        obj_assert = object_min()
        obj = Dataset()
        obj.set(dict_flat_set_min())

        assert obj.__dict__ == obj_assert.__dict__

        # ds_assert = object_full()
        # ds = Dataset()
        # ds.set(dict_flat_set_full())
        #
        # assert ds.__dict__ == ds_assert.__dict__

    def test_dataset_dict_valid(self):
        """Test Datafile.dict() with format=`dv_up` and valid data.

        Parameters
        ----------
        import_datafile_min_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        dict_assert = dict_flat_dict_min()
        obj = object_min()
        dict_flat = obj.dict()

        assert dict_flat == dict_assert

        # dict_assert = dict_flat_dict_full()
        # obj = object_full()
        # dict_flat = obj.dict()
        #
        # assert dict_flat == dict_assert

    def test_dataset_from_json_dv_up_valid(self):
        """Test Dataset.import_data() with format=`dv_up`."""
        obj_assert = object_min()
        obj = Dataset()
        obj.from_json('tests/data/dataset_upload_min_default.json', validate=False)

        assert obj_assert.__dict__ == obj.__dict__

        # ds_assert = object_full()
        # ds = Dataset()
        # ds.from_json('tests/data/dataset_upload_min_default.json', validate=False)
        #
        # assert ds_assert.__dict__ == ds.__dict__

    def test_dataset_from_json_format_invalid(self):
        """Test Dataverse.import_data() with non-valid format."""
        obj_assert = object_init()
        obj = Dataset()
        obj.from_json('tests/data/dataset_upload_full_default.json', format='wrong', validate=False)

        assert obj
        assert obj.__dict__
        assert obj_assert.__dict__ is not obj.__dict__
        assert len(obj.__dict__.keys()) == len(obj_assert.__dict__.keys())

    def test_dataset_to_json_dv_up_valid(self):
        """Test Dataverse.json() with format=`dv_up` and valid data.

        Parameters
        ----------
        object_min : dict
            Fixture, which returns a flat dataset dict() coming from
            `tests/data/dataverse_min.json`.

        TODO: Assert content
        """
        dict_assert = json.loads(json_upload_min())
        obj = object_min()

        assert isinstance(obj.to_json(validate=False), str)
        # assert json.loads(ds.to_json(validate=False)) == dict_assert

        # dict_assert = json.loads(json_upload_full())
        # ds = object_full()
        #
        # assert isinstance(ds.to_json(validate=False), str)
        # assert json.loads(ds.to_json(validate=False)) == dict_assert

    # def test_dataset_to_json_dv_up_invalid(self):
    #     """Test Dataverse.json() with format=`dv_up` and valid data.
    #
    #     Parameters
    #     ----------
    #     object_min : dict
    #         Fixture, which returns a flat dataset dict() coming from
    #         `tests/data/dataverse_min.json`.
    #
    #     TODO: Assert content
    #     """
    #
    #     ds = object_min()
    #
    #     dv_up_keys = ds.__attr_import_dv_up_datasetVersion_values + ['citation_displayName'] + ds.__attr_import_dv_up_citation_fields_values + ds.__attr_import_dv_up_citation_fields_arrays.keys() + ['series'] + ds.__attr_import_dv_up_geospatial_fields_values + list(ds.__attr_import_dv_up_geospatial_fields_arrays.keys()) + ['geospatial_displayName'] + ds.__attr_import_dv_up_socialscience_fields_values + ['socialscience_displayName'] + ['socialscience_displayName'] + ['targetSampleSize'] + ['socialScienceNotes'] + ds.__attr_import_dv_up_journal_fields_values + list(ds.__attr_import_dv_up_journal_fields_arrays.keys()) + ['journal_displayName']
    #     for attr in dv_up_keys:
    #         delattr(ds, attr)

    # def test_dataset_to_json_format_invalid(self):
    #     """Test Dataverse.json() with non-valid format and valid data.
    #
    #     Parameters
    #     ----------
    #
    #     """
    #     ds = object_min()
    #     with pytest.raises(TypeError):
    #         json_dict = json.loads(ds.to_json(format='wrong', validate=False))
    #
    # def test_validate(self):
    #     ds = object_init()
    #     assert ds.from_json(os.path.join(TEST_DIR + '/data/dataset_upload_min_default.json'))
    #
    #     ds = object_init()
    #     assert ds.from_json(os.path.join(TEST_DIR + '/data/dataset_upload_min_default.json'), validate=True)
    #
    #     ds = object_init()
    #     assert ds.from_json(os.path.join(TEST_DIR + '/data/dataset_upload_min_default.json'), validate=True, filename_schema='schemas/json/dataset_upload_default_schema.json')
    #
    #     ds = object_init()
    #     assert ds.from_json(os.path.join(TEST_DIR + '/data/dataset_upload_min_default.json'), filename_schema='schemas/json/dataset_upload_default_schema.json')
    #
    #     # wrong
    #     with pytest.raises(jsonschema.exceptions.ValidationError):
    #         ds = object_init()
    #         ds.to_json()
    #     assert not ds.to_json(format='wrong')
    #     with pytest.raises(jsonschema.exceptions.ValidationError):
    #         assert ds.to_json(filename_schema='schemas/json/dataverse_upload_schema.json')
    #     with pytest.raises(jsonschema.exceptions.ValidationError):
    #         assert ds.validate_json()
    #     with pytest.raises(TypeError):
    #         assert ds.validate_json(format='wrong')
    #     with pytest.raises(jsonschema.exceptions.ValidationError):
    #         assert ds.validate_json(filename_schema='schemas/json/dataverse_upload_schema.json')

    def test_dataset_json_dataset(self):
        """Test Dataverse pipeline from import to export with format=`dv_up`."""
        if not os.environ.get('TRAVIS'):
            dict_assert = json.loads(json_upload_min())
            obj = object_init()
            obj.from_json('tests/data/dataset_upload_min_default.json', validate=False)
            json_out = obj.to_json(validate=False)
            write_json('tests/data/output/dataset_upload_min_default.json', json.loads(json_out))
            obj_new = Dataset()
            obj_new.from_json(os.path.join(TEST_DIR + '/data/output/dataset_upload_min_default.json'), validate=False)
            assert obj.__dict__ == obj_new.__dict__
