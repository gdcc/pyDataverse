"""Dataset data model tests."""
import json
import os
import platform
import pytest
from pyDataverse.models import Dataset
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
    """Get Dataset object.

    Returns
    -------
    pydataverse.models.Dataset
        :class:`Dataset` object.
    """
    return Dataset()


def dict_flat_set_min():
    """Get flat dict for set() of minimum Dataset.

    Returns
    -------
    dict
        Flat dict with minimum Dataset data.

    """
    return {
        "title": "Darwin's Finches",
        "author": [{"authorName": "Finch, Fiona", "authorAffiliation": "Birds Inc."}],
        "datasetContact": [
            {
                "datasetContactEmail": "finch@mailinator.com",
                "datasetContactName": "Finch, Fiona",
            }
        ],
        "dsDescription": [
            {
                "dsDescriptionValue": "Darwin's finches (also known as the Galápagos finches) are a group of about fifteen species of passerine birds."
            }
        ],
        "subject": ["Medicine, Health and Life Sciences"],
        "citation_displayName": "Citation Metadata",
    }


def dict_flat_set_full():
    """Get flat dict for set() of full Dataset.

    Returns
    -------
    dict
        Flat dict with full Dataset data.

    """
    return {
        "license": "CC0",
        "termsOfUse": "CC0 Waiver",
        "termsOfAccess": "Terms of Access",
        "fileAccessRequest": True,
        "protocol": "doi",
        "authority": "10.11587",
        "identifier": "6AQBYW",
        "citation_displayName": "Citation Metadata",
        "title": "Replication Data for: Title",
        "subtitle": "Subtitle",
        "alternativeTitle": "Alternative Title",
        "alternativeURL": "http://AlternativeURL.org",
        "otherId": [
            {"otherIdAgency": "OtherIDAgency1", "otherIdValue": "OtherIDIdentifier1"}
        ],
        "author": [
            {
                "authorName": "LastAuthor1, FirstAuthor1",
                "authorAffiliation": "AuthorAffiliation1",
                "authorIdentifierScheme": "ORCID",
                "authorIdentifier": "AuthorIdentifier1",
            }
        ],
        "datasetContact": [
            {
                "datasetContactName": "LastContact1, FirstContact1",
                "datasetContactAffiliation": "ContactAffiliation1",
                "datasetContactEmail": "ContactEmail1@mailinator.com",
            }
        ],
        "dsDescription": [
            {
                "dsDescriptionValue": "DescriptionText2",
                "dsDescriptionDate": "1000-02-02",
            }
        ],
        "subject": [
            "Agricultural Sciences",
            "Business and Management",
            "Engineering",
            "Law",
        ],
        "keyword": [
            {
                "keywordValue": "KeywordTerm1",
                "keywordVocabulary": "KeywordVocabulary1",
                "keywordVocabularyURI": "http://KeywordVocabularyURL1.org",
            }
        ],
        "topicClassification": [
            {
                "topicClassValue": "Topic Class Value1",
                "topicClassVocab": "Topic Classification Vocabulary",
            }
        ],
        "publication": [
            {
                "publicationCitation": "RelatedPublicationCitation1",
                "publicationIDType": "ark",
                "publicationIDNumber": "RelatedPublicationIDNumber1",
                "publicationURL": "http://RelatedPublicationURL1.org",
            }
        ],
        "notesText": "Notes1",
        "producer": [
            {
                "producerName": "LastProducer1, FirstProducer1",
                "producerAffiliation": "ProducerAffiliation1",
                "producerAbbreviation": "ProducerAbbreviation1",
                "producerURL": "http://ProducerURL1.org",
                "producerLogoURL": "http://ProducerLogoURL1.org",
            }
        ],
        "productionDate": "1003-01-01",
        "productionPlace": "ProductionPlace",
        "contributor": [
            {
                "contributorType": "Data Collector",
                "contributorName": "LastContributor1, FirstContributor1",
            }
        ],
        "grantNumber": [
            {
                "grantNumberAgency": "GrantInformationGrantAgency1",
                "grantNumberValue": "GrantInformationGrantNumber1",
            }
        ],
        "distributor": [
            {
                "distributorName": "LastDistributor1, FirstDistributor1",
                "distributorAffiliation": "DistributorAffiliation1",
                "distributorAbbreviation": "DistributorAbbreviation1",
                "distributorURL": "http://DistributorURL1.org",
                "distributorLogoURL": "http://DistributorLogoURL1.org",
            }
        ],
        "distributionDate": "1004-01-01",
        "depositor": "LastDepositor, FirstDepositor",
        "dateOfDeposit": "1002-01-01",
        "timePeriodCovered": [
            {
                "timePeriodCoveredStart": "1005-01-01",
                "timePeriodCoveredEnd": "1005-01-02",
            }
        ],
        "dateOfCollection": [
            {"dateOfCollectionStart": "1006-01-01", "dateOfCollectionEnd": "1006-01-01"}
        ],
        "kindOfData": ["KindOfData1", "KindOfData2"],
        "language": ["German"],
        "series": {
            "seriesName": "SeriesName",
            "seriesInformation": "SeriesInformation",
        },
        "software": [
            {"softwareName": "SoftwareName1", "softwareVersion": "SoftwareVersion1"}
        ],
        "relatedMaterial": ["RelatedMaterial1", "RelatedMaterial2"],
        "relatedDatasets": ["RelatedDatasets1", "RelatedDatasets2"],
        "otherReferences": ["OtherReferences1", "OtherReferences2"],
        "dataSources": ["DataSources1", "DataSources2"],
        "originOfSources": "OriginOfSources",
        "characteristicOfSources": "CharacteristicOfSourcesNoted",
        "accessToSources": "DocumentationAndAccessToSources",
        "geospatial_displayName": "Geospatial Metadata",
        "geographicCoverage": [
            {
                "country": "Afghanistan",
                "state": "GeographicCoverageStateProvince1",
                "city": "GeographicCoverageCity1",
                "otherGeographicCoverage": "GeographicCoverageOther1",
            }
        ],
        "geographicUnit": ["GeographicUnit1", "GeographicUnit2"],
        "geographicBoundingBox": [
            {
                "westLongitude": "10",
                "eastLongitude": "20",
                "northLongitude": "30",
                "southLongitude": "40",
            }
        ],
        "socialscience_displayName": "Social Science and Humanities Metadata",
        "unitOfAnalysis": ["UnitOfAnalysis1", "UnitOfAnalysis2"],
        "universe": ["Universe1", "Universe2"],
        "timeMethod": "TimeMethod",
        "dataCollector": "LastDataCollector1, FirstDataCollector1",
        "collectorTraining": "CollectorTraining",
        "frequencyOfDataCollection": "Frequency",
        "samplingProcedure": "SamplingProcedure",
        "targetSampleSize": {
            "targetSampleActualSize": "100",
            "targetSampleSizeFormula": "TargetSampleSizeFormula",
        },
        "deviationsFromSampleDesign": "MajorDeviationsForSampleDesign",
        "collectionMode": "CollectionMode",
        "researchInstrument": "TypeOfResearchInstrument",
        "dataCollectionSituation": "CharacteristicsOfDataCollectionSituation",
        "actionsToMinimizeLoss": "ActionsToMinimizeLosses",
        "controlOperations": "ControlOperations",
        "weighting": "Weighting",
        "cleaningOperations": "CleaningOperations",
        "datasetLevelErrorNotes": "StudyLevelErrorNotes",
        "responseRate": "ResponseRate",
        "samplingErrorEstimates": "EstimatesOfSamplingError",
        "otherDataAppraisal": "OtherFormsOfDataAppraisal",
        "socialScienceNotes": {
            "socialScienceNotesType": "NotesType",
            "socialScienceNotesSubject": "NotesSubject",
            "socialScienceNotesText": "NotesText",
        },
        "journal_displayName": "Journal Metadata",
        "journalVolumeIssue": [
            {
                "journalVolume": "JournalVolume1",
                "journalIssue": "JournalIssue1",
                "journalPubDate": "1008-01-01",
            }
        ],
        "journalArticleType": "abstract",
    }


def object_data_init():
    """Get dictionary for Dataset with initial attributes.

    Returns
    -------
    dict
        Dictionary of init data attributes set.

    """
    return {
        "_Dataset_default_json_format": "dataverse_upload",
        "_Dataset_default_json_schema_filename": test_config[
            "dataset_upload_schema_filename"
        ],
        "_Dataset_allowed_json_formats": [
            "dataverse_upload",
            "dataverse_download",
            "dspace",
            "custom",
        ],
        "_Dataset_json_dataverse_upload_attr": json_dataverse_upload_attr(),
        "_internal_attributes": [],
    }


def object_data_min():
    """Get dictionary for Dataset with minimum attributes.

    Returns
    -------
    pyDataverse.Dataset
        :class:`Dataset` with minimum attributes set.

    """

    return {
        "title": "Darwin's Finches",
        "author": [{"authorName": "Finch, Fiona", "authorAffiliation": "Birds Inc."}],
        "datasetContact": [
            {
                "datasetContactEmail": "finch@mailinator.com",
                "datasetContactName": "Finch, Fiona",
            }
        ],
        "dsDescription": [
            {
                "dsDescriptionValue": "Darwin's finches (also known as the Galápagos finches) are a group of about fifteen species of passerine birds."
            }
        ],
        "subject": ["Medicine, Health and Life Sciences"],
        "citation_displayName": "Citation Metadata",
    }


def object_data_full():
    """Get dictionary for Dataset with full attributes.

    Returns
    -------
    pyDataverse.Dataset
        :class:`Dataset` with full attributes set.

    """
    return {
        "license": "CC0",
        "termsOfUse": "CC0 Waiver",
        "termsOfAccess": "Terms of Access",
        "fileAccessRequest": True,
        "protocol": "doi",
        "authority": "10.11587",
        "identifier": "6AQBYW",
        "citation_displayName": "Citation Metadata",
        "title": "Replication Data for: Title",
        "subtitle": "Subtitle",
        "alternativeTitle": "Alternative Title",
        "alternativeURL": "http://AlternativeURL.org",
        "otherId": [
            {"otherIdAgency": "OtherIDAgency1", "otherIdValue": "OtherIDIdentifier1"}
        ],
        "author": [
            {
                "authorName": "LastAuthor1, FirstAuthor1",
                "authorAffiliation": "AuthorAffiliation1",
                "authorIdentifierScheme": "ORCID",
                "authorIdentifier": "AuthorIdentifier1",
            }
        ],
        "datasetContact": [
            {
                "datasetContactName": "LastContact1, FirstContact1",
                "datasetContactAffiliation": "ContactAffiliation1",
                "datasetContactEmail": "ContactEmail1@mailinator.com",
            }
        ],
        "dsDescription": [
            {
                "dsDescriptionValue": "DescriptionText2",
                "dsDescriptionDate": "1000-02-02",
            }
        ],
        "subject": [
            "Agricultural Sciences",
            "Business and Management",
            "Engineering",
            "Law",
        ],
        "keyword": [
            {
                "keywordValue": "KeywordTerm1",
                "keywordVocabulary": "KeywordVocabulary1",
                "keywordVocabularyURI": "http://KeywordVocabularyURL1.org",
            }
        ],
        "topicClassification": [
            {
                "topicClassValue": "Topic Class Value1",
                "topicClassVocab": "Topic Classification Vocabulary",
            }
        ],
        "publication": [
            {
                "publicationCitation": "RelatedPublicationCitation1",
                "publicationIDType": "ark",
                "publicationIDNumber": "RelatedPublicationIDNumber1",
                "publicationURL": "http://RelatedPublicationURL1.org",
            }
        ],
        "notesText": "Notes1",
        "producer": [
            {
                "producerName": "LastProducer1, FirstProducer1",
                "producerAffiliation": "ProducerAffiliation1",
                "producerAbbreviation": "ProducerAbbreviation1",
                "producerURL": "http://ProducerURL1.org",
                "producerLogoURL": "http://ProducerLogoURL1.org",
            }
        ],
        "productionDate": "1003-01-01",
        "productionPlace": "ProductionPlace",
        "contributor": [
            {
                "contributorType": "Data Collector",
                "contributorName": "LastContributor1, FirstContributor1",
            }
        ],
        "grantNumber": [
            {
                "grantNumberAgency": "GrantInformationGrantAgency1",
                "grantNumberValue": "GrantInformationGrantNumber1",
            }
        ],
        "distributor": [
            {
                "distributorName": "LastDistributor1, FirstDistributor1",
                "distributorAffiliation": "DistributorAffiliation1",
                "distributorAbbreviation": "DistributorAbbreviation1",
                "distributorURL": "http://DistributorURL1.org",
                "distributorLogoURL": "http://DistributorLogoURL1.org",
            }
        ],
        "distributionDate": "1004-01-01",
        "depositor": "LastDepositor, FirstDepositor",
        "dateOfDeposit": "1002-01-01",
        "timePeriodCovered": [
            {
                "timePeriodCoveredStart": "1005-01-01",
                "timePeriodCoveredEnd": "1005-01-02",
            }
        ],
        "dateOfCollection": [
            {"dateOfCollectionStart": "1006-01-01", "dateOfCollectionEnd": "1006-01-01"}
        ],
        "kindOfData": ["KindOfData1", "KindOfData2"],
        "language": ["German"],
        "series": {
            "seriesName": "SeriesName",
            "seriesInformation": "SeriesInformation",
        },
        "software": [
            {"softwareName": "SoftwareName1", "softwareVersion": "SoftwareVersion1"}
        ],
        "relatedMaterial": ["RelatedMaterial1", "RelatedMaterial2"],
        "relatedDatasets": ["RelatedDatasets1", "RelatedDatasets2"],
        "otherReferences": ["OtherReferences1", "OtherReferences2"],
        "dataSources": ["DataSources1", "DataSources2"],
        "originOfSources": "OriginOfSources",
        "characteristicOfSources": "CharacteristicOfSourcesNoted",
        "accessToSources": "DocumentationAndAccessToSources",
        "geospatial_displayName": "Geospatial Metadata",
        "geographicCoverage": [
            {
                "country": "Afghanistan",
                "state": "GeographicCoverageStateProvince1",
                "city": "GeographicCoverageCity1",
                "otherGeographicCoverage": "GeographicCoverageOther1",
            }
        ],
        "geographicUnit": ["GeographicUnit1", "GeographicUnit2"],
        "geographicBoundingBox": [
            {
                "westLongitude": "10",
                "eastLongitude": "20",
                "northLongitude": "30",
                "southLongitude": "40",
            }
        ],
        "socialscience_displayName": "Social Science and Humanities Metadata",
        "unitOfAnalysis": ["UnitOfAnalysis1", "UnitOfAnalysis2"],
        "universe": ["Universe1", "Universe2"],
        "timeMethod": "TimeMethod",
        "dataCollector": "LastDataCollector1, FirstDataCollector1",
        "collectorTraining": "CollectorTraining",
        "frequencyOfDataCollection": "Frequency",
        "samplingProcedure": "SamplingProcedure",
        "targetSampleSize": {
            "targetSampleActualSize": "100",
            "targetSampleSizeFormula": "TargetSampleSizeFormula",
        },
        "deviationsFromSampleDesign": "MajorDeviationsForSampleDesign",
        "collectionMode": "CollectionMode",
        "researchInstrument": "TypeOfResearchInstrument",
        "dataCollectionSituation": "CharacteristicsOfDataCollectionSituation",
        "actionsToMinimizeLoss": "ActionsToMinimizeLosses",
        "controlOperations": "ControlOperations",
        "weighting": "Weighting",
        "cleaningOperations": "CleaningOperations",
        "datasetLevelErrorNotes": "StudyLevelErrorNotes",
        "responseRate": "ResponseRate",
        "samplingErrorEstimates": "EstimatesOfSamplingError",
        "otherDataAppraisal": "OtherFormsOfDataAppraisal",
        "socialScienceNotes": {
            "socialScienceNotesType": "NotesType",
            "socialScienceNotesSubject": "NotesSubject",
            "socialScienceNotesText": "NotesText",
        },
        "journal_displayName": "Journal Metadata",
        "journalVolumeIssue": [
            {
                "journalVolume": "JournalVolume1",
                "journalIssue": "JournalIssue1",
                "journalPubDate": "1008-01-01",
            }
        ],
        "journalArticleType": "abstract",
    }


def dict_flat_get_min():
    """Get flat dict for :func:`get` with minimum data of Dataset.

    Returns
    -------
    dict
        Minimum Dataset dictionary returned by :func:`get`.

    """
    return {
        "title": "Darwin's Finches",
        "author": [{"authorName": "Finch, Fiona", "authorAffiliation": "Birds Inc."}],
        "datasetContact": [
            {
                "datasetContactEmail": "finch@mailinator.com",
                "datasetContactName": "Finch, Fiona",
            }
        ],
        "dsDescription": [
            {
                "dsDescriptionValue": "Darwin's finches (also known as the Galápagos finches) are a group of about fifteen species of passerine birds."
            },
        ],
        "subject": ["Medicine, Health and Life Sciences"],
        "citation_displayName": "Citation Metadata",
    }


def dict_flat_get_full():
    """Get flat dict for :func:`get` of full data of Dataset.

    Returns
    -------
    dict
        Full Datafile dictionary returned by :func:`get`.

    """
    return {
        "license": "CC0",
        "termsOfUse": "CC0 Waiver",
        "termsOfAccess": "Terms of Access",
        "fileAccessRequest": True,
        "protocol": "doi",
        "authority": "10.11587",
        "identifier": "6AQBYW",
        "title": "Replication Data for: Title",
        "subtitle": "Subtitle",
        "alternativeTitle": "Alternative Title",
        "alternativeURL": "http://AlternativeURL.org",
        "otherId": [
            {"otherIdAgency": "OtherIDAgency1", "otherIdValue": "OtherIDIdentifier1"}
        ],
        "author": [
            {
                "authorName": "LastAuthor1, FirstAuthor1",
                "authorAffiliation": "AuthorAffiliation1",
                "authorIdentifierScheme": "ORCID",
                "authorIdentifier": "AuthorIdentifier1",
            }
        ],
        "datasetContact": [
            {
                "datasetContactName": "LastContact1, FirstContact1",
                "datasetContactAffiliation": "ContactAffiliation1",
                "datasetContactEmail": "ContactEmail1@mailinator.com",
            }
        ],
        "dsDescription": [
            {
                "dsDescriptionValue": "DescriptionText2",
                "dsDescriptionDate": "1000-02-02",
            }
        ],
        "subject": [
            "Agricultural Sciences",
            "Business and Management",
            "Engineering",
            "Law",
        ],
        "keyword": [
            {
                "keywordValue": "KeywordTerm1",
                "keywordVocabulary": "KeywordVocabulary1",
                "keywordVocabularyURI": "http://KeywordVocabularyURL1.org",
            }
        ],
        "topicClassification": [
            {
                "topicClassValue": "Topic Class Value1",
                "topicClassVocab": "Topic Classification Vocabulary",
            }
        ],
        "publication": [
            {
                "publicationCitation": "RelatedPublicationCitation1",
                "publicationIDType": "ark",
                "publicationIDNumber": "RelatedPublicationIDNumber1",
                "publicationURL": "http://RelatedPublicationURL1.org",
            }
        ],
        "notesText": "Notes1",
        "producer": [
            {
                "producerName": "LastProducer1, FirstProducer1",
                "producerAffiliation": "ProducerAffiliation1",
                "producerAbbreviation": "ProducerAbbreviation1",
                "producerURL": "http://ProducerURL1.org",
                "producerLogoURL": "http://ProducerLogoURL1.org",
            }
        ],
        "productionDate": "1003-01-01",
        "productionPlace": "ProductionPlace",
        "contributor": [
            {
                "contributorType": "Data Collector",
                "contributorName": "LastContributor1, FirstContributor1",
            }
        ],
        "grantNumber": [
            {
                "grantNumberAgency": "GrantInformationGrantAgency1",
                "grantNumberValue": "GrantInformationGrantNumber1",
            }
        ],
        "distributor": [
            {
                "distributorName": "LastDistributor1, FirstDistributor1",
                "distributorAffiliation": "DistributorAffiliation1",
                "distributorAbbreviation": "DistributorAbbreviation1",
                "distributorURL": "http://DistributorURL1.org",
                "distributorLogoURL": "http://DistributorLogoURL1.org",
            }
        ],
        "distributionDate": "1004-01-01",
        "depositor": "LastDepositor, FirstDepositor",
        "dateOfDeposit": "1002-01-01",
        "timePeriodCovered": [
            {
                "timePeriodCoveredStart": "1005-01-01",
                "timePeriodCoveredEnd": "1005-01-02",
            }
        ],
        "dateOfCollection": [
            {"dateOfCollectionStart": "1006-01-01", "dateOfCollectionEnd": "1006-01-01"}
        ],
        "kindOfData": ["KindOfData1", "KindOfData2"],
        "language": ["German"],
        "series": {
            "seriesName": "SeriesName",
            "seriesInformation": "SeriesInformation",
        },
        "software": [
            {"softwareName": "SoftwareName1", "softwareVersion": "SoftwareVersion1"}
        ],
        "relatedMaterial": ["RelatedMaterial1", "RelatedMaterial2"],
        "relatedDatasets": ["RelatedDatasets1", "RelatedDatasets2"],
        "otherReferences": ["OtherReferences1", "OtherReferences2"],
        "dataSources": ["DataSources1", "DataSources2"],
        "originOfSources": "OriginOfSources",
        "characteristicOfSources": "CharacteristicOfSourcesNoted",
        "accessToSources": "DocumentationAndAccessToSources",
        "geospatial_displayName": "Geospatial Metadata",
        "geographicCoverage": [
            {
                "country": "Afghanistan",
                "state": "GeographicCoverageStateProvince1",
                "city": "GeographicCoverageCity1",
                "otherGeographicCoverage": "GeographicCoverageOther1",
            }
        ],
        "geographicUnit": ["GeographicUnit1", "GeographicUnit2"],
        "geographicBoundingBox": [
            {
                "westLongitude": "10",
                "eastLongitude": "20",
                "northLongitude": "30",
                "southLongitude": "40",
            }
        ],
        "socialscience_displayName": "Social Science and Humanities Metadata",
        "unitOfAnalysis": ["UnitOfAnalysis1", "UnitOfAnalysis2"],
        "universe": ["Universe1", "Universe2"],
        "timeMethod": "TimeMethod",
        "dataCollector": "LastDataCollector1, FirstDataCollector1",
        "collectorTraining": "CollectorTraining",
        "frequencyOfDataCollection": "Frequency",
        "samplingProcedure": "SamplingProcedure",
        "targetSampleSize": {
            "targetSampleActualSize": "100",
            "targetSampleSizeFormula": "TargetSampleSizeFormula",
        },
        "deviationsFromSampleDesign": "MajorDeviationsForSampleDesign",
        "collectionMode": "CollectionMode",
        "researchInstrument": "TypeOfResearchInstrument",
        "dataCollectionSituation": "CharacteristicsOfDataCollectionSituation",
        "actionsToMinimizeLoss": "ActionsToMinimizeLosses",
        "controlOperations": "ControlOperations",
        "weighting": "Weighting",
        "cleaningOperations": "CleaningOperations",
        "datasetLevelErrorNotes": "StudyLevelErrorNotes",
        "responseRate": "ResponseRate",
        "samplingErrorEstimates": "EstimatesOfSamplingError",
        "otherDataAppraisal": "OtherFormsOfDataAppraisal",
        "socialScienceNotes": {
            "socialScienceNotesType": "NotesType",
            "socialScienceNotesSubject": "NotesSubject",
            "socialScienceNotesText": "NotesText",
        },
        "journal_displayName": "Journal Metadata",
        "journalVolumeIssue": [
            {
                "journalVolume": "JournalVolume1",
                "journalIssue": "JournalIssue1",
                "journalPubDate": "1008-01-01",
            }
        ],
        "journalArticleType": "abstract",
        "citation_displayName": "Citation Metadata",
    }


def json_upload_min():
    """Get JSON string of minimum Dataset.

    Returns
    -------
    str
        JSON string.

    """
    return read_file("tests/data/api/datasets/dataset_upload_default_min_1.json")


def json_upload_full():
    """Get JSON string of full Dataset.

    Returns
    -------
    str
        JSON string.

    """
    return read_file("tests/data/api/datasets/dataset_upload_default_full_1.json")


def json_dataverse_upload_attr():
    """List of attributes import or export in format `dataverse_upload`.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
    return [
        "license",
        "termsOfUse",
        "termsOfAccess",
        "fileAccessRequest",
        "protocol",
        "authority",
        "identifier",
        "citation_displayName",
        "title",
        "subtitle",
        "alternativeTitle",
        "alternativeURL",
        "otherId",
        "author",
        "datasetContact",
        "dsDescription",
        "subject",
        "keyword",
        "topicClassification",
        "publication",
        "notesText",
        "producer",
        "productionDate",
        "productionPlace",
        "contributor",
        "grantNumber",
        "distributor",
        "distributionDate",
        "depositor",
        "dateOfDeposit",
        "timePeriodCovered",
        "dateOfCollection",
        "kindOfData",
        "language",
        "series",
        "software",
        "relatedMaterial",
        "relatedDatasets",
        "otherReferences",
        "dataSources",
        "originOfSources",
        "characteristicOfSources",
        "accessToSources",
        "geospatial_displayName",
        "geographicCoverage",
        "geographicUnit",
        "geographicBoundingBox",
        "socialscience_displayName",
        "unitOfAnalysis",
        "universe",
        "timeMethod",
        "dataCollector",
        "collectorTraining",
        "frequencyOfDataCollection",
        "samplingProcedure",
        "targetSampleSize",
        "deviationsFromSampleDesign",
        "collectionMode",
        "researchInstrument",
        "dataCollectionSituation",
        "actionsToMinimizeLoss",
        "controlOperations",
        "weighting",
        "cleaningOperations",
        "datasetLevelErrorNotes",
        "responseRate",
        "samplingErrorEstimates",
        "otherDataAppraisal",
        "socialScienceNotes",
        "journal_displayName",
        "journalVolumeIssue",
        "journalArticleType",
    ]


def json_dataverse_upload_required_attr():
    """List of attributes required for `dataverse_upload` JSON.

    Returns
    -------
    list
        List of attributes, which will be used for import and export.

    """
    return ["title", "author", "datasetContact", "dsDescription", "subject"]


class TestDatasetSpecificTravisNot(object):
    """Generic tests for Dataset(), not running on Travis (no file-write permissions)."""

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
                        "src/pyDataverse/schemas/json/dataset_upload_default_schema.json",
                    ),
                    "validate": True,
                },
            ),
        ],
    )
    def test_dataset_to_json_from_json_valid(self, tmp_path, test_input):
        """Test Dataset to JSON from JSON with valid data."""

        pdv_start = data_object()
        args = test_input[0]
        kwargs = test_input[1]
        pdv_start.from_json(*args, **kwargs)
        if "validate" in kwargs:
            if not kwargs["validate"]:
                kwargs = {"validate": False}
        write_json(
            os.path.join(tmp_path, "dataset_integrity_test.json"),
            json.loads(pdv_start.json(**kwargs)),
        )

        pdv_end = data_object()
        pdv_end.from_json(
            read_file(os.path.join(tmp_path, "dataset_integrity_test.json")), **kwargs
        )

        for key, val in pdv_end.get().items():
            assert getattr(pdv_start, key) == getattr(pdv_end, key)
        assert len(pdv_start.__dict__) == len(pdv_end.__dict__,)
