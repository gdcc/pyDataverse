# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/AUSSDA/pyDataverse."""
from __future__ import absolute_import
from pyDataverse.utils import dict_to_json
from pyDataverse.utils import read_file_json
from pyDataverse.utils import write_file_json


"""
Data-structure to work with data and metadata of Dataverses, Datasets and
Datafiles - coming from different sources.
"""


class Dataverse(object):
    """Base class for the Dataverse model.

    * data
        * dict: dict mit key value pairs übergeben, wo key exakt das
        attributist.
        * optional: list: liste tuples (links key, rechts value) übergeben, wo
        key exakt das attribut ist.
    * does: set metadata functions: dicts mit key-value pairs übergeben. die
    keys müssen wie die metadata attribute

    """

    """Attributes required to Dataverse metadata json."""
    __attr_required = [
        'alias',
        'name',
        'dataverseContacts'
    ]
    """Attributes on first level of Dataverse metadata json."""
    __attr_valid = [
        'alias',
        'name',
        'affiliation',
        'description',
        'dataverseContacts',
        'dataverseType'
    ]
    __attr_misc = [
        # 'datasets',
        # 'dataverses',
        'pid'
    ]

    def __init__(self):
        """Init `Dataverse()` class."""
        """Misc"""
        self.datasets = []
        self.dataverses = []
        self.pid = None

        """Metadata"""
        self.name = None
        self.alias = None
        self.dataverseContacts = []
        self.affiliation = None
        self.description = None
        self.dataverseType = None

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

    def import_metadata(self, filename, format='dv_up'):
        """Import data from different sources.

        It is allowed to import incomplete Dataverses, where required
        attributes are missing.

        Simmply parse in the data. No validation needed. This will be done
        later before the export.

        format: dv_up

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
            for attr in self.__attr_valid:
                if attr in metadata:
                    data[attr] = metadata[attr]
            self.set(data)
        elif format == 'dv_down':
            metadata = read_file_json(filename)
            self.set(data)
        else:
            # TODO: Exception
            print('Data-format not right.')

    def dict(self, format='dv_up'):
        """Get Dataverse metadata as dict for Dataverse API upload.

        TODO: Validate standard

        format: all, dv_up

        if data is valid will be checked here. so it is not necessary anymore
        in json().

        """
        data = {}
        if format == 'dv_up':
            if self.is_valid():
                for attr in self.__attr_valid:
                    if self.__getattribute__(attr):
                        data[attr] = self.__getattribute__(attr)
                # TODO: prüfen, ob required attributes gesetzt sind = Exception
                return data
            else:
                print('dict can not be created. Data is not valid for format')
                return None
        elif format == 'all':
            for attr in self.__attr_misc + self.__attr_valid:
                if self.__getattribute__(attr):
                    data[attr] = self.__getattribute__(attr)
            return data
        else:
            # TODO: Exception
            print('Format not right for dict.')
            return None

    def json(self, format='dv_up'):
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
        if format == 'dv_up':
            data = self.dict('dv_up')
            if data:
                return dict_to_json(data)
            else:
                return None
        elif format == 'all':
            data = self.dict('all')
            if data:
                return dict_to_json(data)
            else:
                return None
        else:
            # TODO Exception
            print('data format not valid.')

    def export_metadata(self, filename, format='dv_up'):
        """Export data to different file-formats.

        exports only to metadata standards.

        format: `dv_up`

        """
        if format == 'dv_up':
            return write_file_json(filename, self.dict())
        else:
            # TODO: Exception
            print('Data-format not right.')


class Dataset(object):
    """Base class for the Dataset model."""

    __attr_misc = [
        'datafiles'
    ]

    """Attributes required for Dataset metadata json."""
    __attr_required = [
        'title',
        'author',
        'datasetContact',
        'dsDescription',
        'subject'
    ]

    """Attributes on first level of Dataverse metadata json inside
    [\'datasetVersion\']."""
    __attr_datasetVersion = [
        'license',
        'termsOfUse',
        'termsOfAccess'
    ]

    """Attributes on first level of Dataverse metadata json inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'citation\']."""
    __attr_citation = [
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
        'seriesName',
        'seriesInformation',
        'relatedMaterial',
        'relatedDatasets',
        'otherReferences',
        'dataSources',
        'originOfSources',
        'characteristicOfSources',
        'accessToSources',
        'kindOfData'
    ]

    """Attributes in Dataverse metadata json inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'citation\'][\'fields\']."""
    __attr_citation_fields = {
        'otherId': ['otherIdAgency', 'otherIdValue'],
        'author': ['authorName', 'authorAffiliation', 'authorIdentifierScheme',
                   'authorIdentifier'],
        'datasetContact': ['datasetContactName', 'datasetContactAffiliation',
                           'datasetContactEmail'],
        'dsDescription': ['dsDescriptionValue', 'dsDescriptionDate'],
        'keyword': ['keywordValue', 'keywordVocabulary',
                    'keywordVocabularyURI'],
        'producer': ['producerName', 'producerAffiliation',
                     'producerAbbreviation', 'producerURL', 'producerLogoURL'],
        'contributor': ['contributorType', 'contributorName'],
        'grantNumber': ['grantNumberAgency', 'grantNumberValue'],
        'topicClassification': ['topicClassValue', 'topicClassVocab'],
        'publication': ['publicationCitation', 'publicationIDType',
                        'publicationIDNumber', 'publicationURL'],
        'distributor': ['distributorName', 'distributorAffiliation',
                        'distributorAbbreviation', 'distributorURL',
                        'distributorLogoURL'],
        'timePeriodCovered': ['timePeriodCoveredStart',
                              'timePeriodCoveredEnd'],
        'dateOfCollection': ['dateOfCollectionStart', 'dateOfCollectionEnd'],
        'software': ['softwareName', 'softwareVersion']
    }

    """Attributes on first level of Dataverse metadata json inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'geospatial\']."""
    __attr_geospatial = [
        'geographicUnit'
    ]

    """Attributes in Dataverse metadata json inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'geospatial\'][\'fields\']."""
    __attr_geospatial_fields = {
        'geographicCoverage': ['country', 'state', 'city',
                               'otherGeographicCoverage'],
        'geographicBoundingBox': ['westLongitude', 'eastLongitude',
                                  'northLongitude', 'southLongitude']
    }

    """Attributes on first level of Dataverse metadata json inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'socialscience\']."""
    __attr_socialscience = [
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

    """Attributes on first level of Dataverse metadata json inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'journal\']."""
    __attr_journal = [
        'journalArticleType'
    ]

    """Attributes in Dataverse metadata json inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'journal\'][\'fields\']."""
    __attr_journal_fields = {
        'journalVolumeIssue': ['journalVolume', 'journalIssue',
                               'journalPubDate']
    }

    def __init__(self):
        """Init Dataset() class."""
        """Misc"""
        self.datafiles = []

        """Metadata: dataset"""
        self.license = None
        self.termsOfUse = None
        self.termsOfAccess = None

        """Metadata: citation"""
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
        self.seriesName = None
        self.seriesInformation = None
        self.software = []
        self.relatedMaterial = []
        self.relatedDatasets = []
        self.otherReferences = []
        self.dataSources = []
        self.originOfSources = None
        self.characteristicOfSources = None
        self.accessToSources = None

        """Metadata: geospatial"""
        self.geospatial_displayName = None
        self.geographicCoverage = []
        self.geographicUnit = None
        self.geographicBoundingBox = []

        """Metadata: socialscience"""
        self.socialscience_displayName = None
        self.unitOfAnalysis = []
        self.universe = []
        self.timeMethod = None
        self.dataCollector = None
        self.collectorTraining = None
        self.frequencyOfDataCollection = None
        self.samplingProcedure = None
        self.targetSampleActualSize = None
        self.targetSampleSizeFormula = None
        self.socialScienceNotesType = None
        self.socialScienceNotesSubject = None
        self.socialScienceNotesText = None
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

        """Metadata: journal"""
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

        # check if attribute sets are complete where necessary
        tp_cov = self.__getattribute__('timePeriodCovered')
        if tp_cov:
            for tp in tp_cov:
                if 'timePeriodCoveredStart' in tp or 'timePeriodCoveredEnd' in tp:
                    if not ('timePeriodCoveredStart' in tp and 'timePeriodCoveredEnd' in tp):
                        is_valid = False

        d_coll = self.__getattribute__('dateOfCollection')
        if d_coll:
            for d in d_coll:
                if 'dateOfCollectionStart' in d or 'dateOfCollectionEnd' in d:
                    if not ('dateOfCollectionStart' in d and 'dateOfCollectionEnd' in d):
                        is_valid = False

        authors = self.__getattribute__('author')
        if authors:
            for a in authors:
                if 'authorAffiliation' in a or 'authorIdentifierScheme' in a or 'authorIdentifier' in a:
                    if 'authorName' not in a:
                        is_valid = False

        ds_contac = self.__getattribute__('datasetContact')
        if ds_contac:
            for c in ds_contac:
                if 'datasetContactAffiliation' in c or 'datasetContactEmail' in c:
                    if 'datasetContactName' not in c:
                        is_valid = False

        producer = self.__getattribute__('producer')
        if producer:
            for p in producer:
                if 'producerAffiliation' in p or 'producerAbbreviation' in p or 'producerURL' in p or 'producerLogoURL' in p:
                    if not p['producerName']:
                        is_valid = False

        contributor = self.__getattribute__('contributor')
        if contributor:
            for c in contributor:
                if 'contributorType' in c:
                    if 'contributorName' not in c:
                        is_valid = False

        distributor = self.__getattribute__('distributor')
        if distributor:
            for d in distributor:
                if 'distributorAffiliation' in d or 'distributorAbbreviation' in d or 'distributorURL' in d or 'distributorLogoURL' in d:
                    if 'distributorName' not in d:
                        is_valid = False

        bbox = self.__getattribute__('geographicBoundingBox')
        if bbox:
            for b in bbox:
                if b:
                    if not ('westLongitude' in b and 'eastLongitude' in b and 'northLongitude' in b and 'southLongitude' in b):
                        is_valid = False

        return is_valid

    def import_metadata(self, filename, format='dv_up'):
        """Import metadata.

        format: dv_up

        """
        data = {}
        if format == 'dv_up':
            metadata = read_file_json(filename)
            """dataset"""
            # get first level metadata and parse it automatically
            for key, val in metadata['datasetVersion'].items():
                if key in self.__attr_datasetVersion:
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
                    if field['typeName'] in self.__attr_citation:
                        data[field['typeName']] = field['value']

                    if field['typeName'] in self.__attr_citation_fields:
                        data[field['typeName']] = self.__parse_dicts(
                            field['value'],
                            self.__attr_citation_fields[field['typeName']])

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
                    self.__setattr__('geospatial_displayName',
                                     geospatial['displayName'])

                for field in geospatial['fields']:
                    if field['typeName'] in self.__attr_geospatial:
                        data[field['typeName']] = field['value']

                    if field['typeName'] in self.__attr_geospatial_fields:
                        data[field['typeName']] = self.__parse_dicts(
                            field['value'],
                            self.__attr_geospatial_fields[field['typeName']])
            else:
                # TODO: Exception
                print('geospatial not in json')

            """socialscience"""
            if 'socialscience' in metadata['datasetVersion']['metadataBlocks']:
                socialscience = metadata['datasetVersion']['metadataBlocks']['socialscience']
                if 'displayName' in socialscience:
                    self.__setattr__('socialscience_displayName',
                                     socialscience['displayName'])

                for field in socialscience['fields']:
                    if field['typeName'] in self.__attr_socialscience:
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
                    self.__setattr__('journal_displayName',
                                     journal['displayName'])

                for field in journal['fields']:
                    if field['typeName'] in self.__attr_journal:
                        data[field['typeName']] = field['value']

                    if field['typeName'] in self.__attr_journal_fields:
                        data[field['typeName']] = self.__parse_dicts(
                            field['value'],
                            self.__attr_journal_fields[field['typeName']])
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

    def dict(self, format='dv_up'):
        """Get Dataset metadata as dict for Dataverse API upload.

        TODO: Validate standard

        format: dv_up, all

        """
        if format == 'dv_up':
            if self.is_valid():
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

                """dataset"""
                # Generate first level attributes
                for attr in self.__attr_datasetVersion:
                    data['datasetVersion'][attr] = self.__getattribute__(attr)

                """citation"""
                if self.citation_displayName:
                    citation['displayName'] = self.citation_displayName

                # Generate first level attributes
                for attr in self.__attr_citation:
                    citation['fields'].append({
                        'typeName': attr,
                        'value': self.__getattribute__(attr)
                    })

                # Generate fields attributes
                for key, val in self.__attr_citation_fields.items():
                    citation['fields'].append({
                        'typeName': key,
                        'value': self.__generate_dicts(key, val)
                    })

                # Generate series attributes
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
                # Generate first level attributes
                for attr in self.__attr_geospatial:
                    geospatial['fields'].append({
                        'typeName': attr,
                        'value': self.__getattribute__(attr)
                    })

                # Generate fields attributes
                for key, val in self.__attr_geospatial_fields.items():
                    # check if attribute exists
                    geospatial['fields'].append({
                        'typeName': key,
                        'value': self.__generate_dicts(key, val)
                    })

                """socialscience"""
                # Generate first level attributes
                for attr in self.__attr_socialscience:
                    socialscience['fields'].append({
                        'typeName': attr,
                        'value': self.__getattribute__(attr)
                    })

                # Generate targetSampleSize attributes
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

                # Generate socialScienceNotes attributes
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
                # Generate first level attributes
                for attr in self.__attr_journal:
                    journal['fields'].append({
                        'typeName': attr,
                        'value': self.__getattribute__(attr)
                    })

                # Generate fields attributes
                for key, val in self.__attr_journal_fields.items():
                    journal['fields'].append({
                        'typeName': key,
                        'value': self.__generate_dicts(key, val)
                    })

                # TODO: prüfen, ob required attributes gesetzt sind. wenn nicht = Exception!
                data['datasetVersion']['metadataBlocks']['citation'] = citation
                data['datasetVersion']['metadataBlocks']['socialscience'] = socialscience
                data['datasetVersion']['metadataBlocks']['geospatial'] = geospatial
                data['datasetVersion']['metadataBlocks']['journal'] = journal

                return data
            else:
                print('dict can not be created. Data is not valid for format')
                return None
        elif format == 'all':
            attr_lst = self.__attr_datasetVersion + self.__attr_citation + self.__attr_geospatial + self.__attr_socialscience + self.__attr_journal
            for key, val in self.__attr_citation_fields.update(
                self.__attr_geospatial_fields.update(
                    self.__attr_journal_fields)):
                attr_lst.append(key)
            for attr in attr_lst:
                if self.__getattribute__(attr):
                    data[attr] = self.__getattribute__(attr)
            return data

        else:
            print('dict can not be created. Format is not valid')
            return None

    def __generate_dicts(self, key, val):
        """Parse out list of dicts of metadata attributes for dict export."""
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

        return tmp_list

    def json(self, format='dv_up'):
        """Get Dataset metadata as json for Dataverse API upload.

        TODO: Validate standard
        TODO: Link to default json file

        """
        if format == 'dv_up':
            return dict_to_json(self.dict())
        elif format == 'all':
            return dict_to_json(self.dict('all'))
        else:
            # TODO Exception
            print('data format not valid.')

    def export_metadata(self, filename, format='dv_up'):
        """Export data to different file-formats.

        format: `dv_up`

        """
        if format == 'dv_up':
            return write_file_json(filename, self.dict())
        else:
            # TODO: Exception
            print('Data-format not right.')


class Datafile(object):
    """Base class for the Datafile model."""

    """Attributes required for Datafile metadata json."""
    __attr_required = [
        'filename',
        'pid'
    ]

    """Attributes on first level of Datafile metadata json."""
    __attr_valid = [
        'description',
        'categories',
        'directoryLabel',
        'restrict'
    ]
    """Attributes on first level of Datafile metadata json."""
    __attr_misc = [
        'pid',
        'filename'
    ]

    def __init__(self, filename=None, pid=None):
        """Init `Datafile()` class."""
        """Misc"""
        self.pid = pid
        self.filename = filename

        """Metadata"""
        self.description = None
        self.categories = []
        self.directoryLabel = None
        self.restrict = None

    def __str__(self):
        """Return name of Datafile() class for users."""
        return 'pyDataverse Datafile() model class.'

    def set(self, data):
        """Set attributes.

        Takes a dict with Key-Value pairs containing Datafile metadata.
        Keys: attribute name. named after dataverse up standard.
        Value: attribute value. types must be compatible for dataverse up.

        """
        for key, val in data.items():
            self.__setattr__(key, val)

    def is_valid(self):
        """Check if metadata stored in attributes is valid for dataverse api upload.

        more

        """
        is_valid = True

        for attr in self.__attr_required:
            if not self.__getattribute__(attr):
                is_valid = False
                print('attribute \'{0}\' missing.'.format(attr))

        return is_valid

    def import_metadata(self, filename, format='dv_up'):
        """Import metadata.

        format: dv_up

        """
        data = {}
        if format == 'dv_up':
            metadata = read_file_json(filename)

            for attr in self.__attr_valid:
                if attr in metadata:
                    data[attr] = metadata[attr]

            self.set(data)
        elif format == 'dv_down':
            metadata = read_file_json(filename)
            self.set(metadata)
        else:
            # TODO: Exception
            print('Data-format not right')

    def dict(self, format='dv_up'):
        """Get Dataset metadata as dict for Dataverse API upload.

        TODO: Validate standard

        """
        if format == 'dv_up':
            if self.is_valid():
                data = {}

                for attr in self.__attr_valid:
                    data[attr] = self.__getattribute__(attr)

                return data
            else:
                print('dict can not be created. Data is not valid')
                return None
        elif format == 'all':
            for attr in self.__attr_misc + self.__attr_valid:
                if self.__getattribute__(attr):
                    data[attr] = self.__getattribute__(attr)
            return data
        else:
            # TODO: Exception
            print('Format not right for dict.')
            return None

    def json(self, format='dv_up'):
        """Get Datafile metadata as json for Dataverse API upload.

        TODO: Validate standard
        TODO: Link to default json file

        """
        if format == 'dv_up':
            return dict_to_json(self.dict())
        elif format == 'all':
            return dict_to_json(self.dict('all'))
        else:
            # TODO Exception
            print('data format not valid.')

    def export_metadata(self, filename, format='dv_up'):
        """Export data to different file-formats.

        format: `dv_up`

        """
        if format == 'dv_up':
            return write_file_json(filename, self.dict)
        else:
            # TODO: Exception
            print('Data-format not right.')
