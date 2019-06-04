# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/AUSSDA/pyDataverse."""
from __future__ import absolute_import
from pyDataverse.utils import dict_to_json
from pyDataverse.utils import json_to_dict
from pyDataverse.utils import read_file_json
from pyDataverse.utils import write_file_json


"""
Data-structure to work with data and metadata of Dataverses, Datasets and
Datafiles - coming from different sources.
"""


class Dataverse(object):
    """Base class for the Dataverse model.

    * data
        * dict: dict mit key value pairs übergeben, wo key exakt das attributist.
        * optional: list: liste tuples (links key, rechts value) übergeben, wo key exakt das attribut ist.
    * does: set metadata functions: dicts mit key-value pairs übergeben. die keys müssen wie die metadata attribute

    """

    __attr_required = [
        'alias',
        'name',
        'contactEmail'
    ]
    __attr_flat = [
        'alias',
        'name',
        'affiliation',
        'description',
        'dataverseType'
    ]

    def __init__(self):
        """Init `Dataverse()` class."""
        self.name = None
        self.alias = None
        self.contactEmail = []
        self.affiliation = None
        self.description = None
        self.dataverseType = None
        self.datasets = []
        self.dataverses = []

    def __str__(self):
        """Return name of Dataverse() class for users."""
        return 'pyDataverse Dataverse() model class.'

    def set(self, data):
        """Set attributes.

        Takes a dict with Key-Value pairs containing dataverse metadata.
        Keys: attribute name. named after dataverse up standard.
        Value: attribute value. types must be compatible for dataverse up.

        """
        for key, val in data.items():
            self.__setattr__(key, val)

    def is_valid(self):
        """Check if metadata stored in attributes is valid for dataverse api upload.

        name, alias and dataverseContact are required fields. dataverseContact
        is stored as list of emails in contactEmail, so contactEmail can not be
        none.
        """
        is_valid = True
        for attr in self.__attr_required:
            if not self.__getattribute__(attr):
                is_valid = False
                print('attribute \'{0}\' missing.'.format(attr))
        return is_valid

    def import_metadata(self, filename, format):
        """Import data from different sources.

        It is allowed to import incomplete Dataverses, where required
        attributes are missing.

        Simmply parse in the data. No validation needed. This will be done
        later before the export.

        Example: Default dataverse metadata json:
        {
          "name": "Scientific Research",
          "alias": "science",
          "dataverseContacts": [
            {
              "contactEmail": "pi@example.edu"
            },
            {
              "contactEmail": "student@example.edu"
            }
          ],
          "affiliation": "Scientific Research University",
          "description": "We do all the science.",
          "dataverseType": "LABORATORY"
        }

        filename: string
        format: `dv_up`, `dv_down`

        """
        data = {}
        if format == 'dv_up':
            metadata = read_file_json(filename)
            # get first level metadata and parse it automatically
            for attr in self.__attr_flat:
                data[attr] = metadata[attr]

            # get nested metadata and parse it manually
            if 'dataverseContacts' in metadata:
                data['contactEmail'] = []
                for contact in metadata['dataverseContacts']:
                    for key, val in contact.items():
                        if key == 'contactEmail':
                            data['contactEmail'].append(val)
            self.set(data)
        elif format == 'dv_down':
            metadata = read_file_json(filename)
            self.set(data)
        else:
            # TODO: Exception
            print('Data-format not right')

    @property
    def dict(self):
        """Get Dataverse metadata as dict for Dataverse API upload.

        TODO: Validate standard

        """
        if self.is_valid():
            data = {}
            """
            dv_attr_list contains all metadata related attributes, which are
            mapped on the first level of the dataverse up metadata structure.
            This should help to shorten code
            """
            for attr in self.__attr_flat:
                if self.__getattribute__(attr):
                    data[attr] = self.__getattribute__(attr)
                else:
                    print('attr {0} not in data model.'.format(attr))

            # prüfen, ob required attributes gesetzt sind. wenn nicht = Exception!
            if self.contactEmail:
                data['dataverseContacts'] = []
                for email in self.contactEmail:
                    data['dataverseContacts'].append({'contactEmail': email})
            else:
                print('Key contactEmail not in data model.')

            return data
        else:
            print('dict can not be created. Data is not valid')
            return None

    @property
    def json(self):
        """Get Dataverse metadata as json for Dataverse API upload.

        TODO: Validate standard

        Example: Default dataverse metadata json:
        {
          "name": "Scientific Research",
          "alias": "science",
          "dataverseContacts": [
            {
              "contactEmail": "pi@example.edu"
            },
            {
              "contactEmail": "student@example.edu"
            }
          ],
          "affiliation": "Scientific Research University",
          "description": "We do all the science.",
          "dataverseType": "LABORATORY"
        }

        """
        return dict_to_json(self.dict)

    def export_metadata(self, filename, format):
        """Export data to different file-formats.

        format: `dv_up`

        """
        if format == 'dv_up':
            return write_file_json(filename, self.dict)
        else:
            # TODO: Exception
            print('Data-format not right.')


class Dataset(object):
    """Base class for the Dataset model."""

    __attr_required = [
        'displayName',
        'title',
        'author',
        'datasetContact',
        'dsDescription',
        'subject'
    ]

    __attr_flat = [
        'license',
        'termsOfUse',
        'termsOfAccess'
    ]
    __attr_citation_flat = [
        'title',
        'subtitle',
        'alternativeTitle',
        'alternativeURL',
        'subject',
        'notesText',
        'productionDate',
        'productionPlace',
        'distributionDate',
        'depositor',
        'dateOfDeposit',
        'kindOfData',
        'relatedMaterial',
        'relatedDatasets',
        'otherReferences',
        'dataSources',
        'originOfSources',
        'characteristicOfSources',
        'accessToSources',
        'kindOfData'
    ]

    __attr_citation_arrays = {
        'otherId': ['otherIdAgency', 'otherIdValue'],
        'author': ['authorName', 'authorAffiliation', 'authorIdentifierScheme', 'authorIdentifier'],
        'datasetContact': ['datasetContactName', 'datasetContactAffiliation', 'datasetContactEmail'],
        'dsDescription': ['dsDescriptionValue', 'dsDescriptionDate'],
        'keyword': ['keywordValue', 'keywordVocabulary', 'keywordVocabularyURI'],
        'producer': ['producerName', 'producerAffiliation', 'producerAbbreviation', 'producerURL', 'producerLogoURL'],
        'contributor': ['contributorType', 'contributorName'],
        'grantNumber': ['grantNumberAgency', 'grantNumberValue'],
        'topicClassification': ['topicClassValue', 'topicClassVocab'],
        'publication': ['publicationCitation', 'publicationIDType', 'publicationIDNumber', 'publicationURL'],
        'distributor': ['distributorName', 'distributorAffiliation', 'distributorAbbreviation', 'distributorURL', 'distributorLogoURL'],
        'timePeriodCovered': ['timePeriodCoveredStart', 'timePeriodCoveredEnd'],
        'dateOfCollection': ['dateOfCollectionStart', 'dateOfCollectionEnd'],
        'software': ['softwareName', 'softwareVersion']
    }

    __attr_geospatial_flat = [
        'geographicUnit'
    ]

    __attr_geospatial_arrays = {
        'geographicCoverage': ['country', 'state', 'city', 'otherGeographicCoverage'],
        'geographicBoundingBox': ['westLongitude', 'eastLongitude', 'northLongitude', 'southLongitude']
    }

    __attr_socialscience_flat = [
        'unitOfAnalysis',
        'universe',
        'timeMethod',
        'dataCollector',
        'collectorTraining',
        'frequencyOfDataCollection',
        'samplingProcedure',
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
    ]

    __attr_journal_flat = [
        'journalArticleType'
    ]

    __attr_journal_arrays = {
        'journalVolumeIssue': ['journalVolume', 'journalIssue', 'journalPubDate']
    }

    def __init__(self):
        """Init Dataset() class."""
        """dataset"""
        self.license = None
        self.termsOfUse = None
        self.termsOfAccess = None

        """citation"""
        self.citation_displayName = None
        self.title = None
        self.subtitle = None
        self.alternativeTitle = None
        self.alternativeURL = None
        self.otherId = []
        self.author = []
        self.datasetContact = []
        self.dsDescription = []
        self.subject = []
        self.keyword = []
        self.topicClassification = []
        self.publication = []
        self.notesText = None
        self.producer = []
        self.productionDate = None
        self.productionPlace = None
        self.contributor = []
        self.grantNumber = []
        self.distributor = []
        self.distributionDate = None
        self.depositor = None
        self.dateOfDeposit = None
        self.timePeriodCovered = []
        self.dateOfCollection = []
        self.kindOfData = []
        self.series = []
        self.software = []
        self.relatedMaterial = []
        self.relatedDatasets = []
        self.otherReferences = []
        self.dataSources = []
        self.originOfSources = None
        self.characteristicOfSources = None
        self.accessToSources = None

        """geospatial"""
        self.geospatial_displayName = None
        self.geographicCoverage = []
        self.geographicUnit = None
        self.geographicBoundingBox = []

        """socialscience"""
        self.socialscience_displayName = None
        self.unitOfAnalysis = []
        self.universe = []
        self.timeMethod = None
        self.dataCollector = None
        self.collectorTraining = None
        self.frequencyOfDataCollection = None
        self.samplingProcedure = None
        self.targetSampleSize = []
        self.socialScienceNotes = []
        self.deviationsFromSampleDesign = None
        self.collectionMode = None
        self.researchInstrument = None
        self.dataCollectionSituation = None
        self.actionsToMinimizeLoss = None
        self.controlOperations = None
        self.weighting = None
        self.cleaningOperations = None
        self.datasetLevelErrorNotes = None
        self.responseRate = None
        self.samplingErrorEstimates = None
        self.otherDataAppraisal = None

        """journal"""
        self.journal_displayName = None
        self.journalVolumeIssue = []
        self.journalArticleType = None

    def __str__(self):
        """Return name of Dataset() class for users."""
        return 'pyDataverse Dataset() model class.'

    def set(self, data):
        """Set attributes.

        Takes a dict with Key-Value pairs containing dataverse metadata.
        Keys: attribute name. named after dataverse up standard.
        Value: attribute value. types must be compatible for dataverse up.

        """
        for key, val in data.items():
            self.__setattr__(key, val)

    def is_valid(self):
        """Check if metadata stored in attributes is valid for dataverse api upload.

        required: ??
        TODO: Test out required fields or ask Harvard.

        """
        is_valid = True
        # check if all required attributes are set
        for attr in self.__attr_required:
            if not self.__getattribute__(attr):
                is_valid = False
                print('attribute \'{0}\' missing.'.format(attr))

        return is_valid

    def import_metadata(self, filename, format):
        """Import metadata."""
        data = {}
        if format == 'dv_up':
            metadata = read_file_json(filename)
            """dataset"""
            # get first level metadata and parse it automatically
            for key, val in metadata['datasetVersion'].items():
                if key in self.__attr_flat:
                    data[key] = val

            # get nested metadata and parse it manually
            if 'dataverseContacts' in metadata:
                data['contactEmail'] = []
                for contact in metadata['dataverseContacts']:
                    for key, val in contact.items():
                        if key == 'contactEmail':
                            data['contactEmail'].append(val)

            """citation"""
            if 'citation' in metadata['datasetVersion']['metadataBlocks']:
                citation = metadata['datasetVersion']['metadataBlocks']['citation']
                if 'displayName' in citation:
                    data['citation_displayName'] = citation['displayName']

                for field in citation['fields']:
                    if field['typeName'] in self.__attr_citation_flat:
                        data[field['typeName']] = field['value']

                    if field['typeName'] in self.__attr_citation_arrays:
                        data[field['typeName']] = self.__parse_dicts(
                            field['value'],
                            self.__attr_citation_arrays[field['typeName']])

                    if field['typeName'] == 'series':
                        if 'seriesName' in field['value']:
                            data['seriesName'] = field['value']['seriesName']['value']
                        if 'seriesInformation' in field['value']:
                            data['seriesInformation'] = field['value']['seriesInformation']['value']
            else:
                # TODO: Exception
                print('citation not in json')

            """geospatial"""
            if 'geospatial' in metadata['datasetVersion']['metadataBlocks']:
                geospatial = metadata['datasetVersion']['metadataBlocks']['geospatial']
                if 'displayName' in geospatial:
                    self.__setattr__('geospatial_displayName', geospatial['displayName'])

                for field in geospatial['fields']:
                    if field['typeName'] in self.__attr_geospatial_flat:
                        data[field['typeName']] = field['value']

                    if field['typeName'] in self.__attr_geospatial_arrays:
                        data[field['typeName']] = self.__parse_dicts(
                            field['value'],
                            self.__attr_geospatial_arrays[field['typeName']])
            else:
                # TODO: Exception
                print('geospatial not in json')

            """socialscience"""
            if 'socialscience' in metadata['datasetVersion']['metadataBlocks']:
                socialscience = metadata['datasetVersion']['metadataBlocks']['socialscience']
                if 'displayName' in socialscience:
                    self.__setattr__('socialscience_displayName', socialscience['displayName'])

                for field in socialscience['fields']:
                    if field['typeName'] in self.__attr_socialscience_flat:
                        data[field['typeName']] = field['value']

                    if field['typeName'] == 'targetSampleSize':
                        if 'targetSampleActualSize' in field['value']:
                            data['targetSampleActualSize'] = field['value']['targetSampleActualSize']['value']
                        if 'targetSampleSizeFormula' in field['value']:
                            data['targetSampleSizeFormula'] = field['value']['targetSampleSizeFormula']['value']

                    if field['typeName'] == 'socialScienceNotes':
                        if 'socialScienceNotesType' in field['value']:
                            data['socialScienceNotesType'] = field['value']['socialScienceNotesType']['value']
                        if 'socialScienceNotesSubject' in field['value']:
                            data['socialScienceNotesSubject'] = field['value']['socialScienceNotesSubject']['value']
                        if 'socialScienceNotesText' in field['value']:
                            data['socialScienceNotesText'] = field['value']['socialScienceNotesText']['value']
            else:
                # TODO: Exception
                print('socialscience not in json')

            """journal"""
            if 'journal' in metadata['datasetVersion']['metadataBlocks']:
                journal = metadata['datasetVersion']['metadataBlocks']['journal']
                if 'displayName' in journal:
                    self.__setattr__('journal_displayName', journal['displayName'])

                for field in journal['fields']:
                    if field['typeName'] in self.__attr_journal_flat:
                        data[field['typeName']] = field['value']

                    if field['typeName'] in self.__attr_journal_arrays:
                        data[field['typeName']] = self.__parse_dicts(
                            field['value'],
                            self.__attr_journal_arrays[field['typeName']])
            else:
                # TODO: Exception
                print('journal not in json')

            self.set(data)
        elif format == 'dv_down':
            metadata = read_file_json(filename)
            self.set(data)
        else:
            # TODO: Exception
            print('Data-format not right')

    def __parse_dicts(self, data, attr_list):
        """Parse out list of dicts.

        data: list of dicts
        attr_list: list of attributes to be parsed out.

        return: list of dicts

        """
        data_tmp = []

        for d in data:
            tmp_dict = {}
            for key, val in d.items():
                if key in attr_list:
                    tmp_dict[key] = val['value']
                else:
                    print('Key \'{0}\' not in attribute list'.format(key))
            data_tmp.append(tmp_dict)

        return data_tmp

    @property
    def dict(self):
        """Get Dataset metadata as dict for Dataverse API upload.

        TODO: Validate standard

        """
        data = {}
        data['datasetVersion'] = {}
        data['datasetVersion']['metadataBlocks'] = {}
        citation = {}
        citation['fields'] = []
        geospatial = {}
        geospatial['fields'] = []
        socialscience = {}
        socialscience['fields'] = []
        journal = {}
        journal['fields'] = []
        tmp_list = []

        """dataset"""
        for attr in self.__attr_flat:
            data['datasetVersion'][attr] = self.__getattribute__(attr)

        """citation"""
        if self.citation_displayName:
            citation['displayName'] = self.citation_displayName

        for attr in self.__attr_citation_flat:
            citation['fields'].append({
                'typeName': attr,
                'value': self.__getattribute__(attr)
                })

        for key, val in self.__attr_citation_arrays.items():
            # check if attribute exists
            tmp_list = []
            if self.__getattribute__(key):
                # loop over list of attribute dicts()
                for d in self.__getattribute__(key):
                    tmp_dict = {}
                    # iterate over key-value pairs
                    for k, v in d.items():
                        # check if key is in attribute list
                        if k in val:
                            tmp_dict[k] = {}
                            tmp_dict[k]['typeName'] = k
                            tmp_dict[k]['value'] = v
                    tmp_list.append(tmp_dict)
            citation['fields'].append({
                'typeName': key,
                'value': tmp_list
                })

        if self.__getattribute__('series'):
            tmp_dict = {}
            tmp_dict['value'] = {}
            if 'seriesName' in self.__getattribute__('series'):
                tmp_dict['value']['seriesName'] = {}
                tmp_dict['value']['seriesName']['typeName'] = 'seriesName'
                tmp_dict['value']['seriesName']['value'] = self.__getattribute__('seriesName')
            if 'seriesInformation' in self.__getattribute__('series'):
                tmp_dict['value']['seriesInformation'] = {}
                tmp_dict['value']['seriesInformation']['typeName'] = 'seriesInformation'
                tmp_dict['value']['seriesInformation']['value'] = self.__getattribute__('seriesInformation')
            citation['fields'].append({
                'typeName': 'series',
                'value': tmp_dict
                })

        """geospatial"""
        for attr in self.__attr_geospatial_flat:
            geospatial['fields'].append({
                'typeName': attr,
                'value': self.__getattribute__(attr)
                })

        for key, val in self.__attr_geospatial_arrays.items():
            # check if attribute exists
            tmp_list = []
            if self.__getattribute__(key):
                # loop over list of attribute dicts()
                for d in self.__getattribute__(key):
                    tmp_dict = {}
                    # iterate over key-value pairs
                    for k, v in d.items():
                        # check if key is in attribute list
                        if k in val:
                            tmp_dict[k] = {}
                            tmp_dict[k]['typeName'] = k
                            tmp_dict[k]['value'] = v
                    tmp_list.append(tmp_dict)
            geospatial['fields'].append({
                'typeName': key,
                'value': tmp_list
                })

        """socialscience"""

        for attr in self.__attr_socialscience_flat:
            socialscience['fields'].append({
                'typeName': attr,
                'value': self.__getattribute__(attr)
                })

        if self.__getattribute__('targetSampleSize'):
            tmp_dict = {}
            tmp_dict['value'] = {}
            if 'targetSampleActualSize' in self.__getattribute__('targetSampleSize'):
                tmp_dict['value']['targetSampleActualSize'] = {}
                tmp_dict['value']['targetSampleActualSize']['typeName'] = 'targetSampleActualSize'
                tmp_dict['value']['targetSampleActualSize']['value'] = self.__getattribute__('targetSampleActualSize')
            if 'targetSampleSizeFormula' in self.__getattribute__('targetSampleSize'):
                tmp_dict['value']['targetSampleSizeFormula'] = {}
                tmp_dict['value']['targetSampleSizeFormula']['typeName'] = 'targetSampleSizeFormula'
                tmp_dict['value']['targetSampleSizeFormula']['value'] = self.__getattribute__('targetSampleSizeFormula')
            socialscience['fields'].append({
                'typeName': 'series',
                'value': tmp_dict
                })

        if self.__getattribute__('socialScienceNotes'):
            tmp_dict = {}
            tmp_dict['value'] = {}
            if 'socialScienceNotesType' in self.__getattribute__('socialScienceNotes'):
                tmp_dict['value']['socialScienceNotesType'] = {}
                tmp_dict['value']['socialScienceNotesType']['typeName'] = 'socialScienceNotesType'
                tmp_dict['value']['socialScienceNotesType']['value'] = self.__getattribute__('socialScienceNotesType')
            if 'socialScienceNotesSubject' in self.__getattribute__('socialScienceNotes'):
                tmp_dict['value']['socialScienceNotesSubject'] = {}
                tmp_dict['value']['socialScienceNotesSubject']['typeName'] = 'socialScienceNotesSubject'
                tmp_dict['value']['socialScienceNotesSubject']['value'] = self.__getattribute__('socialScienceNotesSubject')
            if 'socialScienceNotesText' in self.__getattribute__('socialScienceNotes'):
                tmp_dict['value']['socialScienceNotesText'] = {}
                tmp_dict['value']['socialScienceNotesText']['typeName'] = 'socialScienceNotesText'
                tmp_dict['value']['socialScienceNotesText']['value'] = self.__getattribute__('socialScienceNotesText')
            socialscience['fields'].append({
                'typeName': 'series',
                'value': tmp_dict
                })

        """journal"""
        for attr in self.__attr_journal_flat:
            journal['fields'].append({
                'typeName': attr,
                'value': self.__getattribute__(attr)
                })

        for key, val in self.__attr_journal_arrays.items():
            # check if attribute exists
            tmp_list = []
            if self.__getattribute__(key):
                # loop over list of attribute dicts()
                for d in self.__getattribute__(key):
                    tmp_dict = {}
                    # iterate over key-value pairs
                    for k, v in d.items():
                        # check if key is in attribute list
                        if k in val:
                            tmp_dict[k] = {}
                            tmp_dict[k]['typeName'] = k
                            tmp_dict[k]['value'] = v
                    tmp_list.append(tmp_dict)
            journal['fields'].append({
                'typeName': key,
                'value': tmp_list
                })

        # TODO: prüfen, ob required attributes gesetzt sind. wenn nicht = Exception!

        data['datasetVersion']['metadataBlocks']['citation'] = citation
        data['datasetVersion']['metadataBlocks']['socialscience'] = socialscience
        data['datasetVersion']['metadataBlocks']['geospatial'] = geospatial
        data['datasetVersion']['metadataBlocks']['journal'] = journal

        return data

    @property
    def json(self):
        """Get Dataset metadata as json for Dataverse API upload.

        TODO: Validate standard
        TODO: Link to default json file

        """
        return dict_to_json(self.dict)

    def export_metadata(self, filename, format):
        """Export data to different file-formats.

        format: `dv_up`

        """
        if format == 'dv_up':
            return write_file_json(filename, self.dict)
        else:
            # TODO: Exception
            print('Data-format not right.')
