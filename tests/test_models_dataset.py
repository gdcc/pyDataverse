# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataset data model tests."""
import json
import os

import jsonschema

import pytest
from pyDataverse.models import Dataset, DVObject

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
FILENAME_DATA_MIN = 'tests/data/dataset_upload_min_default.json'
FILENAME_DATA_FULL = 'tests/data/dataset_upload_full_default.json'
FILENAME_SCHEMA = 'schemas/json/dataset_upload_default_schema.json'
INVALID_SCHEMA_FILENAMES = [[], 12, set(), tuple(), True, False]
INVALID_JSON_FILENAMES = INVALID_SCHEMA_FILENAMES + [None]
INVALID_DATA_FORMATS = [[], 12, set(), tuple(), True, False]
INVALID_VALIDATE = [None, 'wrong', {}, []]
INVALID_JSON_DATA = [[], 12, set(), tuple(), True, False]
INVALID_SET_DATA = [[], 'wrong', 12, set(), tuple(), True, False, None]
FILENAME_JSON_OUTPUT = os.path.join(TEST_DIR + '/data/output/dataset_pytest.json')


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
    """Get Dataset object.

    Returns
    -------
    pydataverse.models.Dataset
        Dataset object.
    """
    return Dataset()


def dict_flat_set_min():
    """Import minimum Dataset dict.

    Returns
    -------
    dict
        Minimum Dataset metadata.

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


def dict_flat_set_full():
    """Import full Dataset dict.

    Returns
    -------
    dict
        Full Dataset metadata.

    """
    data = {
        'license': 'CC0',
        'termsOfUse': 'CC0 Waiver',
        'termsOfAccess': 'Terms of Access',
        'fileAccessRequest': True,
        'protocol': 'doi',
        'authority': '10.11587',
        'identifier': '6AQBYW',
        'citation_displayName': 'Citation Metadata',
        'title': 'Replication Data for: Title',
        'subtitle': 'Subtitle',
        'alternativeTitle': 'Alternative Title',
        'alternativeURL': 'http://AlternativeURL.org',
        'otherId': [{'otherIdAgency': 'OtherIDAgency1', 'otherIdValue': 'OtherIDIdentifier1'}],
        'author': [{'authorName': 'LastAuthor1, FirstAuthor1', 'authorAffiliation': 'AuthorAffiliation1', 'authorIdentifierScheme': 'ORCID', 'authorIdentifier': 'AuthorIdentifier1'}],
        'datasetContact': [{'datasetContactName': 'LastContact1, FirstContact1', 'datasetContactAffiliation': 'ContactAffiliation1', 'datasetContactEmail': 'ContactEmail1@mailinator.com'}],
        'dsDescription': [{'dsDescriptionValue': 'DescriptionText2', 'dsDescriptionDate': '1000-02-02'}],
        'subject': ['Agricultural Sciences', 'Business and Management', 'Engineering', 'Law'],
        'keyword': [{'keywordValue': 'KeywordTerm1', 'keywordVocabulary': 'KeywordVocabulary1', 'keywordVocabularyURI': 'http://KeywordVocabularyURL1.org'}],
        'topicClassification': [{'topicClassValue': 'Topic Class Value1', 'topicClassVocab': 'Topic Classification Vocabulary'}],
        'publication': [{'publicationCitation': 'RelatedPublicationCitation1', 'publicationIDType': 'ark', 'publicationIDNumber': 'RelatedPublicationIDNumber1', 'publicationURL': 'http://RelatedPublicationURL1.org'}],
        'notesText': 'Notes1',
        'producer': [{'producerName': 'LastProducer1, FirstProducer1', 'producerAffiliation': 'ProducerAffiliation1', 'producerAbbreviation': 'ProducerAbbreviation1', 'producerURL': 'http://ProducerURL1.org', 'producerLogoURL': 'http://ProducerLogoURL1.org'}],
        'productionDate': '1003-01-01',
        'productionPlace': 'ProductionPlace',
        'contributor': [{'contributorType': 'Data Collector', 'contributorName': 'LastContributor1, FirstContributor1'}],
        'grantNumber': [{'grantNumberAgency': 'GrantInformationGrantAgency1', 'grantNumberValue': 'GrantInformationGrantNumber1'}],
        'distributor': [{'distributorName': 'LastDistributor1, FirstDistributor1', 'distributorAffiliation': 'DistributorAffiliation1', 'distributorAbbreviation': 'DistributorAbbreviation1', 'distributorURL': 'http://DistributorURL1.org', 'distributorLogoURL': 'http://DistributorLogoURL1.org'}],
        'distributionDate': '1004-01-01',
        'depositor': 'LastDepositor, FirstDepositor',
        'dateOfDeposit': '1002-01-01',
        'timePeriodCovered': [{'timePeriodCoveredStart': '1005-01-01', 'timePeriodCoveredEnd': '1005-01-02'}],
        'dateOfCollection': [{'dateOfCollectionStart': '1006-01-01', 'dateOfCollectionEnd': '1006-01-01'}],
        'kindOfData': ['KindOfData1', 'KindOfData2'],
        'language': ['German'],
        'series': {'seriesName': 'SeriesName', 'seriesInformation': 'SeriesInformation'},
        'software': [{'softwareName': 'SoftwareName1', 'softwareVersion': 'SoftwareVersion1'}],
        'relatedMaterial': ['RelatedMaterial1', 'RelatedMaterial2'],
        'relatedDatasets': ['RelatedDatasets1', 'RelatedDatasets2'],
        'otherReferences': ['OtherReferences1', 'OtherReferences2'],
        'dataSources': ['DataSources1', 'DataSources2'],
        'originOfSources': 'OriginOfSources',
        'characteristicOfSources': 'CharacteristicOfSourcesNoted',
        'accessToSources': 'DocumentationAndAccessToSources',
        'geospatial_displayName': 'Geospatial Metadata',
        'geographicCoverage': [{'country': 'Afghanistan', 'state': 'GeographicCoverageStateProvince1', 'city': 'GeographicCoverageCity1', 'otherGeographicCoverage': 'GeographicCoverageOther1'}],
        'geographicUnit': ['GeographicUnit1', 'GeographicUnit2'],
        'geographicBoundingBox': [{'westLongitude': '10', 'eastLongitude': '20', 'northLongitude': '30', 'southLongitude': '40'}],
        'socialscience_displayName': 'Social Science and Humanities Metadata',
        'unitOfAnalysis': ['UnitOfAnalysis1', 'UnitOfAnalysis2'],
        'universe': ['Universe1', 'Universe2'],
        'timeMethod': 'TimeMethod',
        'dataCollector': 'LastDataCollector1, FirstDataCollector1',
        'collectorTraining': 'CollectorTraining',
        'frequencyOfDataCollection': 'Frequency',
        'samplingProcedure': 'SamplingProcedure',
        'targetSampleSize': {'targetSampleActualSize': '100', 'targetSampleSizeFormula': 'TargetSampleSizeFormula'},
        'deviationsFromSampleDesign': 'MajorDeviationsForSampleDesign',
        'collectionMode': 'CollectionMode',
        'researchInstrument': 'TypeOfResearchInstrument',
        'dataCollectionSituation': 'CharacteristicsOfDataCollectionSituation',
        'actionsToMinimizeLoss': 'ActionsToMinimizeLosses',
        'controlOperations': 'ControlOperations',
        'weighting': 'Weighting',
        'cleaningOperations': 'CleaningOperations',
        'datasetLevelErrorNotes': 'StudyLevelErrorNotes',
        'responseRate': 'ResponseRate',
        'samplingErrorEstimates': 'EstimatesOfSamplingError',
        'otherDataAppraisal': 'OtherFormsOfDataAppraisal',
        'socialScienceNotes': {'socialScienceNotesType': 'NotesType', 'socialScienceNotesSubject': 'NotesSubject', 'socialScienceNotesText': 'NotesText'},
        'journal_displayName': 'Journal Metadata',
        'journalVolumeIssue': [{'journalVolume': 'JournalVolume1', 'journalIssue': 'JournalIssue1', 'journalPubDate': '1008-01-01'}],
        'journalArticleType': 'abstract'
    }
    return data


def object_data_init():
    """Get dictionary for Dataset with initial attributes.

    Returns
    -------
    dict
        Dictionary of init data attributes set.

    """
    data = {
        'default_json_format': 'dataverse_upload',
        'default_json_schema_filename': FILENAME_SCHEMA,
        'allowed_json_formats': ['dataverse_upload', 'dataverse_download', 'dspace', 'custom'],
        'json_dataverse_upload_attr': json_dataverse_upload_attr()
    }
    return data


def object_data_min():
    """Get dictionary for Dataset with minimum attributes.

    Returns
    -------
    dict
        Dictionary of minimum data attributes set.

    """

    data = {
        'title': 'Darwin\'s Finches',
        'author': [{'authorName': 'Finch, Fiona', 'authorAffiliation': 'Birds Inc.'}],
        'datasetContact': [{'datasetContactEmail': 'finch@mailinator.com', 'datasetContactName': 'Finch, Fiona'}],
        'dsDescription': [{'dsDescriptionValue': 'Darwin\'s finches (also known as the Galápagos finches) are a group of about fifteen species of passerine birds.'}],
        'subject': ['Medicine, Health and Life Sciences'],
        'citation_displayName': 'Citation Metadata'
    }
    data.update(object_data_init())
    return data


def object_data_full():
    """Get dictionary for Dataset with full attributes.

    Returns
    -------
    dict
        Dictionary of full data attributes set.

    """
    data = {
        'license': 'CC0',
        'termsOfUse': 'CC0 Waiver',
        'termsOfAccess': 'Terms of Access',
        'fileAccessRequest': True,
        'protocol': 'doi',
        'authority': '10.11587',
        'identifier': '6AQBYW',
        'citation_displayName': 'Citation Metadata',
        'title': 'Replication Data for: Title',
        'subtitle': 'Subtitle',
        'alternativeTitle': 'Alternative Title',
        'alternativeURL': 'http://AlternativeURL.org',
        'otherId': [{'otherIdAgency': 'OtherIDAgency1', 'otherIdValue': 'OtherIDIdentifier1'}],
        'author': [{'authorName': 'LastAuthor1, FirstAuthor1', 'authorAffiliation': 'AuthorAffiliation1', 'authorIdentifierScheme': 'ORCID', 'authorIdentifier': 'AuthorIdentifier1'}],
        'datasetContact': [{'datasetContactName': 'LastContact1, FirstContact1', 'datasetContactAffiliation': 'ContactAffiliation1', 'datasetContactEmail': 'ContactEmail1@mailinator.com'}],
        'dsDescription': [{'dsDescriptionValue': 'DescriptionText2', 'dsDescriptionDate': '1000-02-02'}],
        'subject': ['Agricultural Sciences', 'Business and Management', 'Engineering', 'Law'],
        'keyword': [{'keywordValue': 'KeywordTerm1', 'keywordVocabulary': 'KeywordVocabulary1', 'keywordVocabularyURI': 'http://KeywordVocabularyURL1.org'}],
        'topicClassification': [{'topicClassValue': 'Topic Class Value1', 'topicClassVocab': 'Topic Classification Vocabulary'}],
        'publication': [{'publicationCitation': 'RelatedPublicationCitation1', 'publicationIDType': 'ark', 'publicationIDNumber': 'RelatedPublicationIDNumber1', 'publicationURL': 'http://RelatedPublicationURL1.org'}],
        'notesText': 'Notes1',
        'producer': [{'producerName': 'LastProducer1, FirstProducer1', 'producerAffiliation': 'ProducerAffiliation1', 'producerAbbreviation': 'ProducerAbbreviation1', 'producerURL': 'http://ProducerURL1.org', 'producerLogoURL': 'http://ProducerLogoURL1.org'}],
        'productionDate': '1003-01-01',
        'productionPlace': 'ProductionPlace',
        'contributor': [{'contributorType': 'Data Collector',         'contributorName': 'LastContributor1, FirstContributor1'}],
        'grantNumber': [{'grantNumberAgency': 'GrantInformationGrantAgency1', 'grantNumberValue': 'GrantInformationGrantNumber1'}],
        'distributor': [{'distributorName': 'LastDistributor1, FirstDistributor1', 'distributorAffiliation': 'DistributorAffiliation1', 'distributorAbbreviation': 'DistributorAbbreviation1', 'distributorURL': 'http://DistributorURL1.org', 'distributorLogoURL': 'http://DistributorLogoURL1.org'}],
        'distributionDate': '1004-01-01',
        'depositor': 'LastDepositor, FirstDepositor',
        'dateOfDeposit': '1002-01-01',
        'timePeriodCovered': [{'timePeriodCoveredStart': '1005-01-01', 'timePeriodCoveredEnd': '1005-01-02'}],
        'dateOfCollection': [{'dateOfCollectionStart': '1006-01-01', 'dateOfCollectionEnd': '1006-01-01'}],
        'kindOfData': ['KindOfData1', 'KindOfData2'],
        'language': ['German'],
        'series': {'seriesName': 'SeriesName', 'seriesInformation': 'SeriesInformation'},
        'software': [{'softwareName': 'SoftwareName1', 'softwareVersion': 'SoftwareVersion1'}],
        'relatedMaterial': ['RelatedMaterial1', 'RelatedMaterial2'],
        'relatedDatasets': ['RelatedDatasets1', 'RelatedDatasets2'],
        'otherReferences': ['OtherReferences1', 'OtherReferences2'],
        'dataSources': ['DataSources1', 'DataSources2'],
        'originOfSources': 'OriginOfSources',
        'characteristicOfSources': 'CharacteristicOfSourcesNoted',
        'accessToSources': 'DocumentationAndAccessToSources',
        'geospatial_displayName': 'Geospatial Metadata',
        'geographicCoverage': [{'country': 'Afghanistan', 'state': 'GeographicCoverageStateProvince1', 'city': 'GeographicCoverageCity1', 'otherGeographicCoverage': 'GeographicCoverageOther1'}],
        'geographicUnit': ['GeographicUnit1', 'GeographicUnit2'],
        'geographicBoundingBox': [{'westLongitude': '10', 'eastLongitude': '20', 'northLongitude': '30', 'southLongitude': '40'}],
        'socialscience_displayName': 'Social Science and Humanities Metadata',
        'unitOfAnalysis': ['UnitOfAnalysis1', 'UnitOfAnalysis2'],
        'universe': ['Universe1', 'Universe2'],
        'timeMethod': 'TimeMethod',
        'dataCollector': 'LastDataCollector1, FirstDataCollector1',
        'collectorTraining': 'CollectorTraining',
        'frequencyOfDataCollection': 'Frequency',
        'samplingProcedure': 'SamplingProcedure',
        'targetSampleSize': {'targetSampleActualSize': '100', 'targetSampleSizeFormula': 'TargetSampleSizeFormula'},
        'deviationsFromSampleDesign': 'MajorDeviationsForSampleDesign',
        'collectionMode': 'CollectionMode',
        'researchInstrument': 'TypeOfResearchInstrument',
        'dataCollectionSituation': 'CharacteristicsOfDataCollectionSituation',
        'actionsToMinimizeLoss': 'ActionsToMinimizeLosses',
        'controlOperations': 'ControlOperations',
        'weighting': 'Weighting',
        'cleaningOperations': 'CleaningOperations',
        'datasetLevelErrorNotes': 'StudyLevelErrorNotes',
        'responseRate': 'ResponseRate',
        'samplingErrorEstimates': 'EstimatesOfSamplingError',
        'otherDataAppraisal': 'OtherFormsOfDataAppraisal',
        'socialScienceNotes': {'socialScienceNotesType': 'NotesType', 'socialScienceNotesSubject': 'NotesSubject', 'socialScienceNotesText': 'NotesText'},
        'journal_displayName': 'Journal Metadata',
        'journalVolumeIssue': [{'journalVolume': 'JournalVolume1', 'journalIssue': 'JournalIssue1', 'journalPubDate': '1008-01-01'}],
        'journalArticleType': 'abstract'
    }
    data.update(object_data_init())
    return data


def dict_flat_get_init():
    """Get flat dict for :func:`get()` with init data of Dataset.

    Returns
    -------
    dict
        Initial Datafile dictionary returned by :func:`get().

    """
    data = {
        'default_json_format': 'dataverse_upload',
        'default_json_schema_filename': FILENAME_SCHEMA,
        'allowed_json_formats': ['dataverse_upload', 'dataverse_download', 'dspace', 'custom'],
        'json_dataverse_upload_attr': json_dataverse_upload_attr()
    }
    return data


def dict_flat_get_min():
    """Import minimum Dataset dict.

    Returns
    -------
    dict
        Minimum Dataset metadata.

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
                'dsDescriptionValue': 'Darwin\'s finches (also known as the Galápagos finches) are a group of about fifteen species of passerine birds.'},
        ],
        'subject': [
            'Medicine, Health and Life Sciences'
        ],
        'citation_displayName': 'Citation Metadata'
    }
    data.update(dict_flat_get_init())
    return data


def dict_flat_get_full():
    """Import minimum Dataset dict.

    Returns
    -------
    dict
        Minimum Dataset metadata.

    """
    data = {
        'license': 'CC0',
        'termsOfUse': 'CC0 Waiver',
        'termsOfAccess': 'Terms of Access',
        'fileAccessRequest': True,
        'protocol': 'doi',
        'authority': '10.11587',
        'identifier': '6AQBYW',
        'citation_displayName': 'Citation Metadat',
        'title': 'Replication Data for: Title',
        'subtitle': 'Subtitle',
        'alternativeTitle': 'Alternative Title',
        'alternativeURL': 'http://AlternativeURL.org',
        'otherId': [{'otherIdAgency': 'OtherIDAgency1', 'otherIdValue': 'OtherIDIdentifier1'}],
        'author': [{'authorName': 'LastAuthor1, FirstAuthor1', 'authorAffiliation': 'AuthorAffiliation1', 'authorIdentifierScheme': 'ORCID', 'authorIdentifier': 'AuthorIdentifier1'}],
        'datasetContact': [{'datasetContactName': 'LastContact1, FirstContact1', 'datasetContactAffiliation': 'ContactAffiliation1', 'datasetContactEmail': 'ContactEmail1@mailinator.com'}],
        'dsDescription': [{'dsDescriptionValue': 'DescriptionText2', 'dsDescriptionDate': '1000-02-02'}],
        'subject': ['Agricultural Sciences', 'Business and Management', 'Engineering', 'Law'],
        'keyword': [{'keywordValue': 'KeywordTerm1', 'keywordVocabulary': 'KeywordVocabulary1', 'keywordVocabularyURI': 'http://KeywordVocabularyURL1.org'}],
        'topicClassification': [{'topicClassValue': 'Topic Class Value1', 'topicClassVocab': 'Topic Classification Vocabulary'}],
        'publication': [{'publicationCitation': 'RelatedPublicationCitation1', 'publicationIDType': 'ark', 'publicationIDNumber': 'RelatedPublicationIDNumber1', 'publicationURL': 'http://RelatedPublicationURL1.org'}],
        'notesText': 'Notes1',
        'producer': [{'producerName': 'LastProducer1, FirstProducer1', 'producerAffiliation': 'ProducerAffiliation1', 'producerAbbreviation': 'ProducerAbbreviation1', 'producerURL': 'http://ProducerURL1.org', 'producerLogoURL': 'http://ProducerLogoURL1.org'}],
        'productionDate': '1003-01-01',
        'productionPlace': 'ProductionPlace',
        'contributor': [{'contributorType': 'Data Collector', 'contributorName': 'LastContributor1, FirstContributor1'}],
        'grantNumber': [{'grantNumberAgency': 'GrantInformationGrantAgency1', 'grantNumberValue': 'GrantInformationGrantNumber1'}],
        'distributor': [{'distributorName': 'LastDistributor1, FirstDistributor1', 'distributorAffiliation': 'DistributorAffiliation1', 'distributorAbbreviation': 'DistributorAbbreviation1', 'distributorURL': 'http://DistributorURL1.org', 'distributorLogoURL': 'http://DistributorLogoURL1.org'}],
        'distributionDate': '1004-01-01',
        'depositor': 'LastDepositor, FirstDepositor',
        'dateOfDeposit': '1002-01-01',
        'timePeriodCovered': [{'timePeriodCoveredStart': '1005-01-01', 'timePeriodCoveredEnd': '1005-01-02'}],
        'dateOfCollection': [{'dateOfCollectionStart': '1006-01-01', 'dateOfCollectionEnd': '1006-01-01'}],
        'kindOfData': ['KindOfData1', 'KindOfData2'],
        'language': ['German'],
        'series': {'seriesName': 'SeriesName', 'seriesInformation': 'SeriesInformation'},
        'software': [{'softwareName': 'SoftwareName1', 'softwareVersion': 'SoftwareVersion1'}],
        'relatedMaterial': ['RelatedMaterial1', 'RelatedMaterial2'],
        'relatedDatasets': ['RelatedDatasets1', 'RelatedDatasets2'],
        'otherReferences': ['OtherReferences1', 'OtherReferences2'],
        'dataSources': ['DataSources1', 'DataSources2'],
        'originOfSources': 'OriginOfSources',
        'characteristicOfSources': 'CharacteristicOfSourcesNoted',
        'accessToSources': 'DocumentationAndAccessToSources',
        'geospatial_displayName': 'Geospatial Metadata',
        'geographicCoverage': [{'country': 'Afghanistan', 'state': 'GeographicCoverageStateProvince1', 'city': 'GeographicCoverageCity1', 'otherGeographicCoverage': 'GeographicCoverageOther1'}],
        'geographicUnit': ['GeographicUnit1', 'GeographicUnit2'],
        'geographicBoundingBox': [{'westLongitude': '10', 'eastLongitude': '20', 'northLongitude': '30', 'southLongitude': '40'}],
        'socialscience_displayName': 'Social Science and Humanities Metadata',
        'unitOfAnalysis': ['UnitOfAnalysis1', 'UnitOfAnalysis2'],
        'universe': ['Universe1', 'Universe2'],
        'timeMethod': 'TimeMethod',
        'dataCollector': 'LastDataCollector1, FirstDataCollector1',
        'collectorTraining': 'CollectorTraining',
        'frequencyOfDataCollection': 'Frequency',
        'samplingProcedure': 'SamplingProcedure',
        'targetSampleSize': {'targetSampleActualSize': '100', 'targetSampleSizeFormula': 'TargetSampleSizeFormula'},
        'deviationsFromSampleDesign': 'MajorDeviationsForSampleDesign',
        'collectionMode': 'CollectionMode',
        'researchInstrument': 'TypeOfResearchInstrument',
        'dataCollectionSituation': 'CharacteristicsOfDataCollectionSituation',
        'actionsToMinimizeLoss': 'ActionsToMinimizeLosses',
        'controlOperations': 'ControlOperations',
        'weighting': 'Weighting',
        'cleaningOperations': 'CleaningOperations',
        'datasetLevelErrorNotes': 'StudyLevelErrorNotes',
        'responseRate': 'ResponseRate',
        'samplingErrorEstimates': 'EstimatesOfSamplingError',
        'otherDataAppraisal': 'OtherFormsOfDataAppraisal',
        'socialScienceNotes': {'socialScienceNotesType': 'NotesType', 'socialScienceNotesSubject': 'NotesSubject', 'socialScienceNotesText': 'NotesText'},
        'journal_displayName': 'Journal Metadata',
        'journalVolumeIssue': [{'journalVolume': 'JournalVolume1', 'journalIssue': 'JournalIssue1', 'journalPubDate': '1008-01-01'}],
        'journalArticleType': 'abstract',
        'citation_displayName': 'Citation Metadata'
    }
    data.update(dict_flat_get_init())
    return data


def json_upload_min():
    """Get JSON string of minimum Dataset.

    Returns
    -------
    str
        JSON string.

    """
    return read_file(FILENAME_DATA_MIN)


def json_upload_full():
    """Get JSON string of full Dataset.

    Returns
    -------
    str
        JSON string.

    """
    return read_file(FILENAME_DATA_FULL)


def json_dataverse_upload_attr():
    """List of attributes import or export in format `dataverse_upload`.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
    data = [
        'license',
        'termsOfUse',
        'termsOfAccess',
        'fileAccessRequest',
        'protocol',
        'authority',
        'identifier',
        'citation_displayName',
        'title',
        'subtitle',
        'alternativeTitle',
        'alternativeURL',
        'otherId',
        'author',
        'datasetContact',
        'dsDescription',
        'subject',
        'keyword',
        'topicClassification',
        'publication',
        'notesText',
        'producer',
        'productionDate',
        'productionPlace',
        'contributor',
        'grantNumber',
        'distributor',
        'distributionDate',
        'depositor',
        'dateOfDeposit',
        'timePeriodCovered',
        'dateOfCollection',
        'kindOfData',
        'language',
        'series',
        'software',
        'relatedMaterial',
        'relatedDatasets',
        'otherReferences',
        'dataSources',
        'originOfSources',
        'characteristicOfSources',
        'accessToSources',
        'geospatial_displayName',
        'geographicCoverage',
        'geographicUnit',
        'geographicBoundingBox',
        'socialscience_displayName',
        'unitOfAnalysis',
        'universe',
        'timeMethod',
        'dataCollector',
        'collectorTraining',
        'frequencyOfDataCollection',
        'samplingProcedure',
        'targetSampleSize',
        'deviationsFromSampleDesign',
        'collectionMode',
        'researchInstrument',
        'dataCollectionSituation',
        'actionsToMinimizeLoss',
        'controlOperations',
        'weighting',
        'cleaningOperations',
        'datasetLevelErrorNotes',
        'responseRate',
        'samplingErrorEstimates',
        'otherDataAppraisal',
        'socialScienceNotes',
        'journal_displayName',
        'journalVolumeIssue',
        'journalArticleType'
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
        'title',
        'author',
        'datasetContact',
        'dsDescription',
        'subject'
    ]
    return data


class TestDatasetGeneric(object):
    """Generic tests for Dataset()."""

    def test_dataset_set_and_get_valid(self):
        """Test Dataset.get() with valid data."""
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


    def test_dataset_set_invalid(self):
        """Test Dataset.set() with invalid data."""

        # invalid data
        for data in INVALID_SET_DATA:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(data)


    def test_dataset_validate_json_valid(self):
        """Test Dataset.validate_json() with valid data."""
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


class TestDatasetSpecific(object):
    """Specific tests for Dataset()."""

    def test_dataset_from_json_valid(self):
        """Test Dataset.from_json() with valid data."""
        data = [
            (({json_upload_min()}, {}), object_data_min()),
            (({json_upload_full()}, {}), object_data_full()),
            (({json_upload_min()}, {'data_format': 'dataverse_upload'}), object_data_min()),
            (({json_upload_min()}, {'validate': False}), object_data_min()),
            (({json_upload_min()}, {'filename_schema': 'wrong', 'validate': False}), object_data_min()),
            (({json_upload_min()}, {'filename_schema': FILENAME_SCHEMA, 'validate': True}), object_data_min())
        ]

        for input, data_eval in data:
            pdv = data_object()
            args = input[0]
            kwargs = input[1]
            pdv.from_json(*args, **kwargs)

            for key, val in data_eval.items():
                assert getattr(pdv, key) == data_eval[key]
            assert len(pdv.__dict__) == len(data_eval)


    def test_dataset_to_json_valid(self):
        """Test Dataset.to_json() with valid data."""
        data = [
            ((dict_flat_set_min(), {}), json.loads(json_upload_min())),
            ((dict_flat_set_full(), {}), json.loads(json_upload_full())),
            ((dict_flat_set_min(), {'data_format': 'dataverse_upload'}), json.loads(json_upload_min())),
            ((dict_flat_set_min(), {'validate': False}), json.loads(json_upload_min())),
            ((dict_flat_set_min(), {'filename_schema': 'wrong', 'validate': False}), json.loads(json_upload_min())),
            ((dict_flat_set_min(), {'filename_schema': FILENAME_SCHEMA, 'validate': True}), json.loads(json_upload_min()))
        ]

        pdv = data_object()
        pdv.set(dict_flat_set_min())
        assert isinstance(pdv.to_json(), str)

        # TODO: recursevily test values of lists and dicts
        for input, data_eval in data:
            pdv = data_object()
            pdv.set(input[0])
            kwargs = input[1]
            data = json.loads(pdv.to_json(**kwargs))
            assert data
            assert isinstance(data, dict)
            assert len(data) == len(data_eval)
            assert len(data['datasetVersion']['metadataBlocks']['citation']) == len(data_eval['datasetVersion']['metadataBlocks']['citation'])
            assert len(data['datasetVersion']['metadataBlocks']['citation']['fields']) == len(data_eval['datasetVersion']['metadataBlocks']['citation']['fields'])

    def test_dataset_init_valid(self):
        """Test Dataset.__init__() with valid data."""
        # specific
        data = [
            (Dataset(), object_data_init()),
            (Dataset(dict_flat_set_min()), object_data_min()),
            (Dataset(dict_flat_set_full()), object_data_full()),
            (Dataset({}), object_data_init())
        ]

        for pdv, data_eval in data:
            for key, val in data_eval.items():
                assert getattr(pdv, key) == data_eval[key]
            assert len(pdv.__dict__) == len(data_eval)


    def test_dataset_init_invalid(self):
        """Test Dataset.init() with invalid data."""
        pdv = Dataset()

        # invalid data
        for data in INVALID_DATA_FORMATS:
            with pytest.raises(AssertionError):
                pdv.set(data)


    def test_dataset_from_json_invalid(self):
        """Test Dataset.from_json() with invalid data."""
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


    def test_dataset_to_json_invalid(self):
        """Test Dataset.to_json() with non-valid data."""
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


    def test_dataset_validate_json_invalid(self):
        """Test Dataset.validate_json() with non-valid data."""
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


if not os.environ.get('TRAVIS'):
    class TestDatasetSpecificTravisNot(object):
        """Generic tests for Dataset(), not running on Travis (no file-write permissions)."""

        def test_dataset_to_json_from_json_valid(self):
            """Test Dataset to JSON from JSON with valid data."""
            data = [
                (dict_flat_set_min(), {}),
                (dict_flat_set_full(), {}),
                (dict_flat_set_min(), {'data_format': 'dataverse_upload'}),
                (dict_flat_set_min(), {'validate': False}),
                (dict_flat_set_min(), {'filename_schema': 'wrong', 'validate': False}),
                (dict_flat_set_min(), {'filename_schema': FILENAME_SCHEMA, 'validate': True})
            ]

            for data_set, kwargs_from in data:

                kwargs = {}
                pdv_start = data_object()
                pdv_start.set(data_set)
                if 'validate' in kwargs_from:
                    if kwargs_from['validate'] == False:
                        kwargs = {'validate': False}
                write_json(FILENAME_JSON_OUTPUT, json.loads(pdv_start.to_json(**kwargs)))

                pdv_end = data_object()
                kwargs = kwargs_from
                pdv_end.from_json(read_file(FILENAME_JSON_OUTPUT), **kwargs)

                for key, val in pdv_end.get().items():
                    assert getattr(pdv_start, key) == getattr(pdv_end, key)
                assert len(pdv_start.__dict__) == len(pdv_end.__dict__,)
