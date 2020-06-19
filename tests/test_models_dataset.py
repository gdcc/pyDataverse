# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataset data model tests."""
import json
import jsonschema
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
        'subject': ['Agricultural Sciences','Business and Management','Engineering','Law'],
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


def object_init():
    """Import minimum Dataset dict.

    Returns
    -------
    dict
        Minimum Dataset metadata.

    """
    ds = Dataset()
    return ds


def object_min():
    """Import minimum Dataset dict.

    Returns
    -------
    dict
        Minimum Dataset metadata.

    """
    ds = object_init()

    ds.title = 'Darwin\'s Finches'
    ds.author = [{'authorName': 'Finch, Fiona','authorAffiliation': 'Birds Inc.'}]
    ds.datasetContact = [{'datasetContactEmail': 'finch@mailinator.com','datasetContactName': 'Finch, Fiona'}]
    ds.dsDescription = [{'dsDescriptionValue': 'Darwin\'s finches (also known as the Galápagos finches) are a group of about fifteen species of passerine birds.'}]
    ds.subject = ['Medicine, Health and Life Sciences']
    ds.citation_displayName = 'Citation Metadata'
    return ds


def object_full():
    """Import minimum Dataset dict.

    Returns
    -------
    dict
        Minimum Dataset metadata.

    """
    ds = object_init()

    """citation"""
    ds.license = 'CC0'
    ds.termsOfUse = 'CC0 Waiver'
    ds.termsOfAccess = 'Terms of Access'
    ds.fileAccessRequest = True
    ds.protocol = 'doi'
    ds.authority = '10.11587'
    ds.identifier = '6AQBYW'
    ds.citation_displayName = 'Citation Metadata'
    ds.title = 'Replication Data for: Title'
    ds.subtitle = 'Subtitle'
    ds.alternativeTitle = 'Alternative Title'
    ds.alternativeURL = 'http://AlternativeURL.org'
    ds.otherId = [{'otherIdAgency': 'OtherIDAgency1', 'otherIdValue': 'OtherIDIdentifier1'}]
    ds.author = [{'authorName': 'LastAuthor1, FirstAuthor1', 'authorAffiliation': 'AuthorAffiliation1', 'authorIdentifierScheme': 'ORCID', 'authorIdentifier': 'AuthorIdentifier1'}]
    ds.datasetContact = [{'datasetContactName': 'LastContact1, FirstContact1', 'datasetContactAffiliation': 'ContactAffiliation1', 'datasetContactEmail': 'ContactEmail1@mailinator.com'}]
    ds.dsDescription = [{'dsDescriptionValue': 'DescriptionText2', 'dsDescriptionDate': '1000-02-02'}]
    ds.subject = ['Agricultural Sciences','Business and Management','Engineering','Law']
    ds.keyword = [{'keywordValue': 'KeywordTerm1', 'keywordVocabulary': 'KeywordVocabulary1', 'keywordVocabularyURI': 'http://KeywordVocabularyURL1.org'}]
    ds.topicClassification = [{'topicClassValue': 'Topic Class Value1', 'topicClassVocab': 'Topic Classification Vocabulary'}]
    ds.publication = [{'publicationCitation': 'RelatedPublicationCitation1', 'publicationIDType': 'ark', 'publicationIDNumber': 'RelatedPublicationIDNumber1', 'publicationURL': 'http://RelatedPublicationURL1.org'}]
    ds.notesText = 'Notes1'
    ds.producer = [{'producerName': 'LastProducer1, FirstProducer1', 'producerAffiliation': 'ProducerAffiliation1', 'producerAbbreviation': 'ProducerAbbreviation1', 'producerURL': 'http://ProducerURL1.org', 'producerLogoURL': 'http://ProducerLogoURL1.org'}]
    ds.productionDate = '1003-01-01'
    ds.productionPlace = 'ProductionPlace'
    ds.contributor = [{'contributorType': 'Data Collector', 'contributorName': 'LastContributor1, FirstContributor1'}]
    ds.grantNumber = [{'grantNumberAgency': 'GrantInformationGrantAgency1', 'grantNumberValue': 'GrantInformationGrantNumber1'}]
    ds.distributor = [{'distributorName': 'LastDistributor1, FirstDistributor1', 'distributorAffiliation': 'DistributorAffiliation1', 'distributorAbbreviation': 'DistributorAbbreviation1', 'distributorURL': 'http://DistributorURL1.org', 'distributorLogoURL': 'http://DistributorLogoURL1.org'}]
    ds.distributionDate = '1004-01-01'
    ds.depositor = 'LastDepositor, FirstDepositor'
    ds.dateOfDeposit = '1002-01-01'
    ds.timePeriodCovered = [{'timePeriodCoveredStart': '1005-01-01', 'timePeriodCoveredEnd': '1005-01-02'}]
    ds.dateOfCollection = [{'dateOfCollectionStart': '1006-01-01', 'dateOfCollectionEnd': '1006-01-01'}]
    ds.kindOfData = ['KindOfData1', 'KindOfData2']
    ds.language = ['German']
    ds.series = {'seriesName': 'SeriesName', 'seriesInformation': 'SeriesInformation'}
    ds.software = [{'softwareName': 'SoftwareName1', 'softwareVersion': 'SoftwareVersion1'}]
    ds.relatedMaterial = ['RelatedMaterial1', 'RelatedMaterial2']
    ds.relatedDatasets = ['RelatedDatasets1', 'RelatedDatasets2']
    ds.otherReferences = ['OtherReferences1', 'OtherReferences2']
    ds.dataSources = ['DataSources1', 'DataSources2']
    ds.originOfSources = 'OriginOfSources'
    ds.characteristicOfSources = 'CharacteristicOfSourcesNoted'
    ds.accessToSources = 'DocumentationAndAccessToSources'

    """geospatial"""
    ds.geospatial_displayName = 'Geospatial Metadata'
    ds.geographicCoverage = [{'country': 'Afghanistan', 'state': 'GeographicCoverageStateProvince1', 'city': 'GeographicCoverageCity1', 'otherGeographicCoverage': 'GeographicCoverageOther1'}]
    ds.geographicUnit = ['GeographicUnit1', 'GeographicUnit2']
    ds.geographicBoundingBox = [{'westLongitude': '10', 'eastLongitude': '20', 'northLongitude': '30', 'southLongitude': '40'}]

    """socialscience"""
    ds.socialscience_displayName = 'Social Science and Humanities Metadata'
    ds.unitOfAnalysis = ['UnitOfAnalysis1', 'UnitOfAnalysis2']
    ds.universe = ['Universe1', 'Universe2']
    ds.timeMethod = 'TimeMethod'
    ds.dataCollector = 'LastDataCollector1, FirstDataCollector1'
    ds.collectorTraining = 'CollectorTraining'
    ds.frequencyOfDataCollection = 'Frequency'
    ds.samplingProcedure = 'SamplingProcedure'
    ds.targetSampleSize = {'targetSampleActualSize': '100', 'targetSampleSizeFormula': 'TargetSampleSizeFormula'}
    ds.deviationsFromSampleDesign = 'MajorDeviationsForSampleDesign'
    ds.collectionMode = 'CollectionMode'
    ds.researchInstrument = 'TypeOfResearchInstrument'
    ds.dataCollectionSituation = 'CharacteristicsOfDataCollectionSituation'
    ds.actionsToMinimizeLoss = 'ActionsToMinimizeLosses'
    ds.controlOperations = 'ControlOperations'
    ds.weighting = 'Weighting'
    ds.cleaningOperations = 'CleaningOperations'
    ds.datasetLevelErrorNotes = 'StudyLevelErrorNotes'
    ds.responseRate = 'ResponseRate'
    ds.samplingErrorEstimates = 'EstimatesOfSamplingError'
    ds.otherDataAppraisal = 'OtherFormsOfDataAppraisal'
    ds.socialScienceNotes = {'socialScienceNotesType': 'NotesType', 'socialScienceNotesSubject': 'NotesSubject', 'socialScienceNotesText': 'NotesText'}

    """journal"""
    ds.journal_displayName = 'Journal Metadata'
    ds.journalVolumeIssue = [{'journalVolume': 'JournalVolume1', 'journalIssue': 'JournalIssue1', 'journalPubDate': '1008-01-01'}]
    ds.journalArticleType = 'abstract'

    return ds


def dict_flat_dict_min():
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
        'citation_displayName': 'Citation Metadata',
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/dataset_upload_default_schema.json',
        'attr_dv_up_values': None
    }
    return data


def dict_flat_dict_full():
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
        'subject': ['Agricultural Sciences','Business and Management','Engineering','Law'],
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
        'citation_displayName': 'Citation Metadata',
        'default_validate_format': 'dataverse_upload',
        'default_validate_schema_filename': 'schemas/json/dataset_upload_default_schema.json',
        'attr_dv_up_values': None
    }
    return data


def json_upload_min():
    """Import minimum Dataset dict.

    Returns
    -------
    dict
        Minimum Dataset metadata.

    """
    data = read_file('tests/data/dataset_upload_min_default.json')
    return data


def json_upload_full():
    """Import full Dataset dict.

    Returns
    -------
    dict
        Full Dataset metadata.

    """
    data = read_file('tests/data/dataset_upload_full_default.json')
    return data


def attr_dv_up_values():
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


def attr_dv_up_required():
    """List of attributes required for `dataverse_upload` JSON.

    Returns
    -------
    list
        List of attributes, which will be used upload check.

    """
    data = [
        'title',
        'author',
        'datasetContact',
        'dsDescription',
        'subject'
    ]
    return data


class TestDataset(object):
    """Tests for Dataset()."""

    def test_dataset_init(self):
        """Test Dataset.__init__()."""
        obj = Dataset()
        obj_assert = object_init()
        assert obj.__dict__ == obj_assert.__dict__
        assert str(obj) == 'pyDataverse Dataset() model class.'

    def test_dataset_set_min_valid(self):
        """Test Dataset.set() with minimum data."""
        obj = object_init()
        result = obj.set(dict_flat_set_min())
        obj_assert = object_min()
        assert result
        assert obj.__dict__ == obj_assert.__dict__

    def test_dataset_set_full_valid(self):
        """Test Dataset.set() with full data."""
        obj = object_init()
        result = obj.set(dict_flat_set_full())
        obj_assert = object_full()
        assert result
        assert obj.__dict__ == obj_assert.__dict__

    def test_dataset_set_invalid(self):
        """Test Dataset.set() with invalid data."""
        obj = object_init()
        obj_assert = obj
        for dtype in [list(), str(), int(), set(), tuple()]:
            result = obj.set(list())
            assert not result
            assert obj.__dict__ == obj_assert.__dict__

    def test_dataset_dict_min_valid(self):
        """Test Dataset.dict() with min data."""
        obj = object_min()
        dict_flat = obj.dict()
        dict_assert = dict_flat_dict_min()
        assert dict_flat == dict_assert

    def test_dataset_dict_full_valid(self):
        """Test Dataset.dict() with full data."""
        obj = object_full()
        dict_flat = obj.dict()
        dict_assert = dict_flat_dict_full()
        assert dict_flat == dict_assert

    def test_dataset_from_json_min_valid(self):
        """Test Dataset.from_json() with min data."""
        obj = object_init()
        result = obj.from_json('tests/data/dataset_upload_min_default.json', validate=False)
        obj_assert = object_min()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

    def test_dataset_from_json_full_valid(self):
        """Test Dataset.from_json() with full data."""
        obj = object_init()
        result = obj.from_json('tests/data/dataset_upload_full_default.json')
        obj_assert = object_full()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

        obj = object_init()
        result = obj.from_json('tests/data/dataset_upload_full_default.json', validate=False)
        obj_assert = object_full()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

        obj = object_init()
        result = obj.from_json('tests/data/dataset_upload_full_default.json', validate=False, filename_schema='wrong')
        obj_assert = object_full()
        assert result
        assert obj_assert.__dict__ == obj.__dict__

    def test_dataset_from_json_invalid(self):
        """Test Dataset.from_json() with non-valid format."""
        # filename_schema=wrong
        with pytest.raises(FileNotFoundError):
            obj = object_init()
            obj.from_json(os.path.join(TEST_DIR, '/data/dataset_upload_min_default.json'), filename_schema='wrong')

        # format=wrong
        obj = object_init()
        result = obj.from_json(os.path.join(TEST_DIR, '/data/dataset_upload_min_default.json'), format='wrong')
        obj_assert = object_init()
        assert not result
        assert obj_assert.__dict__ == obj.__dict__

        # format=wrong, validate=False
        obj = object_init()
        result = obj.from_json(os.path.join(TEST_DIR, '/data/dataset_upload_min_default.json'), format='wrong', validate=False)
        obj_assert = object_init()
        assert not result
        assert obj_assert.__dict__ == obj.__dict__

    def test_dataset_to_json_min_valid(self):
        """Test Dataset.to_json() with min data."""
        obj = object_min()
        result = obj.to_json()
        dict_assert = json.loads(json_upload_min())
        assert result
        assert isinstance(result, str)
        assert json.loads(result)

    def test_dataset_to_json_full_valid(self):
        """Test Dataset.to_json() with full data."""
        obj = object_full()
        result = obj.to_json()
        dict_assert = json.loads(json_upload_full())
        assert result
        assert isinstance(result, str)
        assert json.loads(result)

        obj = object_full()
        result = obj.to_json(validate=False)
        dict_assert = json.loads(json_upload_full())
        assert result
        assert isinstance(result, str)
        assert json.loads(result)

        dict_assert = json.loads(json_upload_full())
        assert result
        assert isinstance(result, str)
        assert json.loads(result)

        obj = object_full()
        result = obj.to_json()
        dict_assert = json.loads(json_upload_full())
        assert result
        assert isinstance(result, str)
        assert json.loads(result)

    def test_dataset_to_json_invalid(self):
        """Test Dataset.to_json() with non-valid data."""
        with pytest.raises(FileNotFoundError):
            obj = object_full()
            result = obj.to_json(filename_schema='wrong')

        obj = object_full()
        result = obj.to_json(format='wrong')
        assert not result

        obj = object_full()
        result = obj.to_json(format='wrong', validate=False)
        assert not result

    def test_dataset_validate_json_valid(self):
        """Test Dataset.validate_json() with valid data."""
        obj = object_min()
        result = obj.validate_json()
        assert result

        obj = object_full()
        result = obj.validate_json()
        assert result

    def test_dataset_validate_json_invalid(self):
        """Test Dataset.validate_json() with non-valid data."""
        # TODO
        # init data
        # with pytest.raises(jsonschema.exceptions.SchemaError):
        # obj = object_init()
        # result = obj.validate_json()
        # assert result

        # remove required attributes
        required_attributes = attr_dv_up_required()
        for attr in required_attributes:
            obj = object_min()
            delattr(obj, attr)
            assert not obj.validate_json()

        # file not found
        with pytest.raises(FileNotFoundError):
            obj = object_min()
            obj.validate_json(filename_schema='wrong')

        # format=wrong
        obj = object_min()
        result = obj.validate_json(format='wrong')
        assert not result

        obj = object_full()
        result = obj.validate_json(format='wrong')
        assert not result

        # format=wrong, filename_schema=wrong
        obj = object_min()
        result = obj.validate_json(format='wrong', filename_schema='wrong')
        assert not result

        obj = object_full()
        result = obj.validate_json(format='wrong', filename_schema='wrong')
        assert not result

    def test_dataset_to_json_from_json_min(self):
        """Test Dataset from JSON to JSON with min data."""
        if not os.environ.get('TRAVIS'):
            obj = object_min()
            data = obj.to_json(validate=False, as_dict=True)
            write_json(os.path.join(TEST_DIR + '/data/output/dataset_upload_min_default.json'), data)
            obj_new = Dataset()
            obj_new.from_json(os.path.join(TEST_DIR + '/data/output/dataset_upload_min_default.json'), validate=False)
            assert obj_new.__dict__ == obj.__dict__

    def test_dataset_to_json_from_json_full(self):
        """Test Dataset from JSON to JSON with min data."""
        if not os.environ.get('TRAVIS'):
            obj = object_full()
            data = obj.to_json(validate=False, as_dict=True)
            write_json(os.path.join(TEST_DIR + '/data/output/dataset_upload_full_default.json'), data)
            obj_new = Dataset()
            obj_new.from_json(os.path.join(TEST_DIR + '/data/output/dataset_upload_full_default.json'), validate=False)
            assert obj_new.__dict__ == obj.__dict__
