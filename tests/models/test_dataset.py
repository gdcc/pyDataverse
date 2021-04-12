"""Dataset data model tests."""
import json
import os
import platform
import pytest
from pyDataverse.models import Dataset
from ..conftest import test_config


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
                "topicClassVocabURI": "https://topic.class/vocab/uri",
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
                "topicClassVocabURI": "https://topic.class/vocab/uri",
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
                "topicClassVocabURI": "https://topic.class/vocab/uri",
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
    return read_file(test_config["dataset_upload_min_filename"])


def json_upload_full():
    """Get JSON string of full Dataset.

    Returns
    -------
    str
        JSON string.

    """
    return read_file(test_config["dataset_upload_full_filename"])


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


class TestDatasetGeneric(object):
    """Generic tests for Dataset()."""

    def test_dataset_set_and_get_valid(self):
        """Test Dataset.get() with valid data."""
        data = [
            ((dict_flat_set_min(), object_data_min()), dict_flat_get_min()),
            ((dict_flat_set_full(), object_data_full()), dict_flat_get_full()),
            (({}, {}), {}),
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
        for data in test_config["invalid_set_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(data)

    def test_dataset_validate_json_valid(self):
        """Test Dataset.validate_json() with valid data."""
        data = [
            ((dict_flat_set_min(), {}), True),
            ((dict_flat_set_full(), {}), True),
            ((dict_flat_set_min(), {"data_format": "dataverse_upload"}), True),
            (
                (
                    dict_flat_set_min(),
                    {
                        "data_format": "dataverse_upload",
                        "filename_schema": test_config[
                            "dataset_upload_schema_filename"
                        ],
                    },
                ),
                True,
            ),
            (
                (
                    dict_flat_set_min(),
                    {"filename_schema": test_config["dataset_upload_schema_filename"]},
                ),
                True,
            ),
        ]

        for input, data_eval in data:
            pdv = data_object()
            pdv.set(input[0])

            assert pdv.validate_json() == data_eval


class TestDatasetSpecific(object):
    """Specific tests for Dataset()."""

    def test_dataset_from_json_valid(self):
        """Test Dataset.from_json() with valid data."""
        data = [
            (({json_upload_min()}, {}), object_data_min()),
            (({json_upload_full()}, {}), object_data_full()),
            (
                ({json_upload_min()}, {"data_format": "dataverse_upload"}),
                object_data_min(),
            ),
            (({json_upload_min()}, {"validate": False}), object_data_min()),
            (
                ({json_upload_min()}, {"filename_schema": "", "validate": False},),
                object_data_min(),
            ),
            (
                ({json_upload_min()}, {"filename_schema": "wrong", "validate": False},),
                object_data_min(),
            ),
            (
                (
                    {json_upload_min()},
                    {
                        "filename_schema": test_config[
                            "dataset_upload_schema_filename"
                        ],
                        "validate": True,
                    },
                ),
                object_data_min(),
            ),
        ]

        for input, data_eval in data:
            pdv = data_object()
            args = input[0]
            kwargs = input[1]
            pdv.from_json(*args, **kwargs)

            for key, val in data_eval.items():
                assert getattr(pdv, key) == data_eval[key]
            assert len(pdv.__dict__) - len(object_data_init()) == len(data_eval)

    def test_dataset_to_json_valid(self):
        """Test Dataset.json() with valid data."""
        data = [
            ((dict_flat_set_min(), {}), json.loads(json_upload_min())),
            ((dict_flat_set_full(), {}), json.loads(json_upload_full())),
            (
                (dict_flat_set_min(), {"data_format": "dataverse_upload"}),
                json.loads(json_upload_min()),
            ),
            (
                (dict_flat_set_min(), {"validate": False}),
                json.loads(json_upload_min()),
            ),
            (
                (dict_flat_set_min(), {"filename_schema": "", "validate": False},),
                json.loads(json_upload_min()),
            ),
            (
                (dict_flat_set_min(), {"filename_schema": "wrong", "validate": False},),
                json.loads(json_upload_min()),
            ),
            (
                (
                    dict_flat_set_min(),
                    {
                        "filename_schema": test_config[
                            "dataset_upload_schema_filename"
                        ],
                        "validate": True,
                    },
                ),
                json.loads(json_upload_min()),
            ),
        ]

        pdv = data_object()
        pdv.set(dict_flat_set_min())
        assert isinstance(pdv.json(), str)

        # TODO: recursevily test values of lists and dicts
        for input, data_eval in data:
            pdv = data_object()
            pdv.set(input[0])
            kwargs = input[1]
            data = json.loads(pdv.json(**kwargs))
            assert data
            assert isinstance(data, dict)
            assert len(data) == len(data_eval)
            assert len(data["datasetVersion"]["metadataBlocks"]["citation"]) == len(
                data_eval["datasetVersion"]["metadataBlocks"]["citation"]
            )
            assert len(
                data["datasetVersion"]["metadataBlocks"]["citation"]["fields"]
            ) == len(
                data_eval["datasetVersion"]["metadataBlocks"]["citation"]["fields"]
            )

    def test_dataset_init_valid(self):
        """Test Dataset.__init__() with valid data."""
        # specific
        data = [
            (Dataset(), {}),
            (Dataset(dict_flat_set_min()), object_data_min()),
            (Dataset(dict_flat_set_full()), object_data_full()),
            (Dataset({}), {}),
        ]

        for pdv, data_eval in data:
            for key, val in data_eval.items():
                assert getattr(pdv, key) == data_eval[key]
            assert len(pdv.__dict__) - len(object_data_init()) == len(data_eval)

    def test_dataset_init_invalid(self):
        """Test Dataset.init() with invalid data."""
        pdv = Dataset()

        # invalid data
        for data in test_config["invalid_set_types"]:
            with pytest.raises(AssertionError):
                pdv.set(data)

    def test_dataset_from_json_invalid(self):
        """Test Dataset.from_json() with invalid data."""
        # invalid data
        for data in test_config["invalid_json_data_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(data, validate=False)

        if int(platform.python_version_tuple()[1]) >= 5:
            for json_string in test_config["invalid_json_strings"]:
                with pytest.raises(json.decoder.JSONDecodeError):
                    pdv = data_object()
                    pdv.from_json(json_string, validate=False)
        else:
            for json_string in test_config["invalid_json_strings"]:
                with pytest.raises(ValueError):
                    pdv = data_object()
                    pdv.from_json(json_string, validate=False)

        # invalid `filename_schema`
        for filename_schema in test_config["invalid_filename_strings"]:
            with pytest.raises(FileNotFoundError):
                pdv = data_object()
                pdv.from_json(json_upload_min(), filename_schema=filename_schema)

        for filename_schema in test_config["invalid_filename_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(json_upload_min(), filename_schema=filename_schema)

        # invalid `data_format`
        for data_format in (
            test_config["invalid_data_format_types"]
            + test_config["invalid_data_format_strings"]
        ):
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(
                    json_upload_min(), data_format=data_format, validate=False
                )

        # invalid `validate`
        for validate in test_config["invalid_validate_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.from_json(json_upload_min(), validate=validate)

    def test_dataset_to_json_invalid(self):
        """Test Dataset.json() with non-valid data."""
        # invalid `filename_schema`
        for filename_schema in test_config["invalid_filename_strings"]:
            with pytest.raises(FileNotFoundError):
                obj = data_object()
                obj.json(filename_schema=filename_schema)

        for filename_schema in test_config["invalid_filename_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.json(filename_schema=filename_schema)

        # invalid `data_format`
        for data_format in (
            test_config["invalid_data_format_types"]
            + test_config["invalid_data_format_strings"]
        ):
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(dict_flat_set_min())
                pdv.json(data_format=data_format, validate=False)

        # invalid `validate`
        for validate in test_config["invalid_validate_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(dict_flat_set_min())
                pdv.json(validate=validate)

    def test_dataset_validate_json_invalid(self):
        """Test Dataset.validate_json() with non-valid data."""
        # invalid `filename_schema`
        for filename_schema in test_config["invalid_filename_strings"]:
            with pytest.raises(FileNotFoundError):
                pdv = data_object()
                pdv.set(dict_flat_set_min())
                pdv.validate_json(filename_schema=filename_schema)

        for filename_schema in test_config["invalid_filename_types"]:
            with pytest.raises(AssertionError):
                pdv = data_object()
                pdv.set(dict_flat_set_min())
                pdv.validate_json(filename_schema=filename_schema)


if not os.environ.get("TRAVIS"):

    class TestDatasetSpecificTravisNot(object):
        """Generic tests for Dataset(), not running on Travis (no file-write permissions)."""

        def test_dataset_to_json_from_json_valid(self):
            """Test Dataset to JSON from JSON with valid data."""
            data = [
                (dict_flat_set_min(), {}),
                (dict_flat_set_full(), {}),
                (dict_flat_set_min(), {"data_format": "dataverse_upload"}),
                (dict_flat_set_min(), {"validate": False}),
                (dict_flat_set_min(), {"filename_schema": "wrong", "validate": False},),
                (
                    dict_flat_set_min(),
                    {
                        "filename_schema": test_config[
                            "dataset_upload_schema_filename"
                        ],
                        "validate": True,
                    },
                ),
            ]

            for data_set, kwargs_from in data:

                kwargs = {}
                pdv_start = data_object()
                pdv_start.set(data_set)
                if "validate" in kwargs_from:
                    if not kwargs_from["validate"]:
                        kwargs = {"validate": False}
                write_json(
                    test_config["dataset_json_output_filename"],
                    json.loads(pdv_start.json(**kwargs)),
                )

                pdv_end = data_object()
                kwargs = kwargs_from
                pdv_end.from_json(
                    read_file(test_config["dataset_json_output_filename"]), **kwargs
                )

                for key, val in pdv_end.get().items():
                    assert getattr(pdv_start, key) == getattr(pdv_end, key)
                assert len(pdv_start.__dict__) == len(pdv_end.__dict__,)
