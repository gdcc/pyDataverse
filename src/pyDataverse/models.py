# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse data-types data model."""
from __future__ import absolute_import
from pyDataverse.utils import dict_to_json
from pyDataverse.utils import read_file_json
from pyDataverse.utils import write_file_json


"""
Data-structure to work with data and metadata of Dataverses, Datasets and
Datafiles - coming from different sources.
"""


class Dataverse(object):
    """Base class for Dataverse data model."""

    """Attributes required for Dataverse metadata json."""
    __attr_required_metadata = [
        'alias',
        'name',
        'dataverseContacts'
    ]
    """Attributes valid for Dataverse metadata json."""
    __attr_valid_metadata = [
        'alias',
        'name',
        'affiliation',
        'description',
        'dataverseContacts',
        'dataverseType'
    ]
    """Attributes valid for Dataverse class."""
    __attr_valid_class = [
        # 'datasets',
        # 'dataverses',
        'pid'
    ] + __attr_valid_metadata

    def __init__(self):
        """Init a Dataverse() class.

        Examples
        -------
        Create a Dataverse::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()

        """
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
        """Set class attributes with a flat dict.

        Parameters
        ----------
        data : dict
            Flat dict with data. Key's must be name the same as the class
            attribute, the data should be mapped to.

        Examples
        -------
        Set Dataverse attributes via flat dict::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()
            >>> data = {
            >>>     'dataverseContacts': [{'contactEmail': 'test@example.com'}],
            >>>     'name': 'Test pyDataverse',
            >>>     'alias': 'test-pyDataverse'
            >>> }
            >>> dv.set(data)
            >>> dv.name
            'Test pyDataverse'

        """
        for key, val in data.items():
            if key in self.__attr_valid_class:
                self.__setattr__(key, val)
            else:
                # TODO: Raise Exception
                print('Key {0} not valid.'.format(key))

    def import_metadata(self, filename, format='dv_up'):
        """Import Dataverse metadata from file.

        This simply parses in data with valid attribute naming as keys.
        Data must not be complete, and also attributes required for the
        metadata json export can be missing.

        Parameters
        ----------
        filename : string
            Filename with full path.
        format : string
            Data format of input. Available formats are: `dv_up` for Dataverse
            Api upload compatible format.

        Examples
        -------
        Import metadata coming from json file::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()
            >>> dv.import_metadata('tests/data/dataverse_min.json')
            >>> dv.name
            'Test pyDataverse'

        """
        data = {}
        if format == 'dv_up':
            metadata = read_file_json(filename)
            # get first level metadata and parse it automatically
            for attr in self.__attr_valid_metadata:
                if attr in metadata:
                    data[attr] = metadata[attr]
            self.set(data)
        elif format == 'dv_down':
            metadata = read_file_json(filename)
            self.set(data)
        else:
            # TODO: Exception
            print('Data-format not right.')

    def is_valid(self):
        """Check if set attributes are valid for Dataverse api metadata creation.

        The attributes required are listed in `__attr_required_metadata`.

        Returns
        -------
        bool
            True, if creation of metadata json is possible. False, if not.

        Examples
        -------
        Check if metadata is valid for Dataverse api upload::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()
            >>> data = {
            >>>     'dataverseContacts': [{'contactEmail': 'test@example.com'}],
            >>>     'name': 'Test pyDataverse',
            >>>     'alias': 'test-pyDataverse'
            >>> }
            >>> dv.set(data)
            >>> dv.is_valid
            True
            >>> dv.name = None
            >>> dv.is_valid
            False

        """
        is_valid = True
        for attr in self.__attr_required_metadata:
            if not self.__getattribute__(attr):
                is_valid = False
                print('attribute \'{0}\' missing.'.format(attr))
        return is_valid

    def dict(self, format='dv_up'):
        """Create dicts in different data formats.

        `dv_up`: Checks if data is valid for the different dict formats.

        Parameters
        ----------
        format : string
            Data format for dict creation. Available formats are: `dv_up` with
            all metadata for Dataverse api upload, and `all` with all attributes
            set.

        Returns
        -------
        dict
            Data as dict.

        Examples
        -------
        Get dict of Dataverse metadata::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()
            >>> data = {
            >>>     'dataverseContacts': [{'contactEmail': 'test@example.com'}],
            >>>     'name': 'Test pyDataverse',
            >>>     'alias': 'test-pyDataverse'
            >>> }
            >>> dv.set(data)
            >>> data = dv.dict()
            >>> data['name']
            'Test pyDataverse'

        Todo
        -------
        Validate standards.

        """
        data = {}
        if format == 'dv_up':
            if self.is_valid():
                for attr in self.__attr_valid_metadata:
                    if self.__getattribute__(attr) is not None:
                        data[attr] = self.__getattribute__(attr)
                # TODO: prüfen, ob required attributes gesetzt sind = Exception
                return data
            else:
                print('dict can not be created. Data is not valid for format')
                return None
        elif format == 'all':
            for attr in self.__attr_valid_class:
                if self.__getattribute__(attr) is not None:
                    data[attr] = self.__getattribute__(attr)
            return data
        else:
            # TODO: Exception
            print('Format not right for dict.')
            return None

    def json(self, format='dv_up'):
        r"""Create json from attributes.

        Parameters
        ----------
        format : string
            Data format of input. Available formats are: `dv_up` for Dataverse
            Api upload compatible format and `all` with all attributes named in
            `__attr_valid_class`.

        Returns
        -------
        string
            json-formatted string of Dataverse metadata for api upload.

        Examples
        -------
        Get dict of Dataverse metadata::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()
            >>> data = {
            >>>     'dataverseContacts': [{'contactEmail': 'test@example.com'}],
            >>>     'name': 'Test pyDataverse',
            >>>     'alias': 'test-pyDataverse'
            >>> }
            >>> dv.set(data)
            >>> data = dv.json()
            >>> data
            '{\n  "name": "Test pyDataverse",\n  "dataverseContacts": [\n    {\n      "contactEmail": "test@example.com"\n    }\n  ],\n  "alias": "test-pyDataverse"\n}'

        Todo
        -------
        Validate standards.

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
        """Export Dataverse metadata to Dataverse api upload json.

        Parameters
        ----------
        filename : string
            Filename with full path.
        format : string
            Data format for export. Available format is: `dv_up` with all
            metadata for Dataverse api upload.

        Examples
        -------
        Export Dataverse metadata::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()
            >>> data = {
            >>>     'dataverseContacts': [{'contactEmail': 'test@example.com'}],
            >>>     'name': 'Test pyDataverse',
            >>>     'alias': 'test-pyDataverse'
            >>> }
            >>> dv.set(data)
            >>> dv.export_metadata('tests/data/dataverse_export.json')

        """
        if format == 'dv_up':
            return write_file_json(filename, self.dict())
        else:
            # TODO: Exception
            print('Data-format not right.')


class Dataset(object):
    """Base class for the Dataset data model."""

    """Attributes required for Dataset metadata json."""
    __attr_required_metadata = [
        'title',
        'author',
        'datasetContact',
        'dsDescription',
        'subject'
    ]

    """
    Dataset metadata attributes of Dataverse api upload inside
    [\'datasetVersion\'].
    """
    __attr_valid_metadata_datasetVersion = [
        'license',
        'termsOfUse',
        'termsOfAccess'
    ]

    """
    Dataset metadata attributes of Dataverse api upload inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'citation\'].
    """
    __attr_valid_metadata_citation_dicts = [
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

    """
    Dataset metadata attributes of Dataverse api upload inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'citation\'][\'fields\'].
    """
    __attr_valid_metadata_citation_arrays = {
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

    """
    Dataset metadata attributes of Dataverse api upload inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'geospatial\'].
    """
    __attr_valid_metadata_geospatial_dicts = [
        'geographicUnit'
    ]

    """
    Dataset metadata attributes of Dataverse api upload inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'geospatial\'][\'fields\'].
    """
    __attr_valid_metadata_geospatial_arrays = {
        'geographicCoverage': ['country', 'state', 'city',
                               'otherGeographicCoverage'],
        'geographicBoundingBox': ['westLongitude', 'eastLongitude',
                                  'northLongitude', 'southLongitude']
    }

    """
    Dataset metadata attributes of Dataverse api upload inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'socialscience\'].
    """
    __attr_valid_metadata_socialscience_dicts = [
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

    """
    Dataset metadata attributes of Dataverse api upload inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'journal\'].
    """
    __attr_valid_metadata_journal_dicts = [
        'journalArticleType'
    ]

    """
    Dataset metadata attributes of Dataverse api upload inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'journal\'][\'fields\'].
    """
    __attr_valid_metadata_journal_arrays = {
        'journalVolumeIssue': ['journalVolume', 'journalIssue',
                               'journalPubDate']
    }

    """Attributes valid for Dataset class."""
    __attr_valid_class = [
        'datafiles'
    ] + __attr_valid_metadata_datasetVersion \
        + __attr_valid_metadata_citation_dicts \
        + list(__attr_valid_metadata_citation_arrays.keys()) \
        + __attr_valid_metadata_geospatial_dicts \
        + list(__attr_valid_metadata_geospatial_arrays.keys()) \
        + __attr_valid_metadata_socialscience_dicts \
        + __attr_valid_metadata_journal_dicts \
        + list(__attr_valid_metadata_journal_arrays.keys()) \

    def __init__(self):
        """Init a Dataset() class.

        Examples
        -------
        Create a Dataverse::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()

        """
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
        """Set class attributes with a flat dict as input.

        Parameters
        ----------
        data : dict
            Flat dict with data. Key's must be name the same as the class
            attribute, the data should be mapped to.

        Examples
        -------
        Set Dataverse attributes via flat dict::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> data = {
            >>>     'title': 'pyDataverse study 2019',
            >>>     'dsDescription': 'New study about pyDataverse usage in 2019'
            >>> }
            >>> ds.set(data)
            >>> ds.title
            'pyDataverse study 2019'

        """
        for key, val in data.items():
            if key in self.__attr_valid_class or key == 'citation_displayName' or key == 'geospatial_displayName' or key == 'socialscience_displayName' or key == 'journal_displayName' or key == 'targetSampleActualSize' or key == 'targetSampleSizeFormula' or key == 'socialScienceNotesType' or key == 'socialScienceNotesText' or key == 'socialScienceNotesSubject':
                self.__setattr__(key, val)
            else:
                # TODO: Raise Exception
                print('Key {0} not valid.'.format(key))

    def import_metadata(self, filename, format='dv_up'):
        """Import Dataset metadata from file.

        Parameters
        ----------
        filename : string
            Filename with full path.
        format : string
            Data format of input. Available formats are: `dv_up` for Dataverse
            api upload compatible format.

        Examples
        -------
        Set Dataverse attributes via flat dict::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> ds.import_metadata('tests/data/dataset_full.json')
            >>> ds.title
            'Replication Data for: Title'

        """
        data = {}
        if format == 'dv_up':
            metadata = read_file_json(filename)
            """dataset"""
            # get first level metadata and parse it automatically
            for key, val in metadata['datasetVersion'].items():
                if key in self.__attr_valid_metadata_datasetVersion:
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
                    if field['typeName'] in self.__attr_valid_metadata_citation_dicts:
                        data[field['typeName']] = field['value']

                    if field['typeName'] in self.__attr_valid_metadata_citation_arrays:
                        data[field['typeName']] = self.__parse_dicts(
                            field['value'],
                            self.__attr_valid_metadata_citation_arrays[field['typeName']])

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
                    if field['typeName'] in self.__attr_valid_metadata_geospatial_dicts:
                        data[field['typeName']] = field['value']

                    if field['typeName'] in self.__attr_valid_metadata_geospatial_arrays:
                        data[field['typeName']] = self.__parse_dicts(
                            field['value'],
                            self.__attr_valid_metadata_geospatial_arrays[field['typeName']])
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
                    if field['typeName'] in self.__attr_valid_metadata_socialscience_dicts:
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
                    if field['typeName'] in self.__attr_valid_metadata_journal_dicts:
                        data[field['typeName']] = field['value']

                    if field['typeName'] in self.__attr_valid_metadata_journal_arrays:
                        data[field['typeName']] = self.__parse_dicts(
                            field['value'],
                            self.__attr_valid_metadata_journal_arrays[field['typeName']])
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
        """Parse out Dataverse api metadata dicts.

        Parameters
        ----------
        data : list
            List of Dataverse api metadata fields.
        attr_list : list
            List of attributes to be parsed.

        Returns
        -------
        list
            List of dicts with parsed out key-value pairs.

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

    def is_valid(self):
        """Check if attributes available are valid for Dataverse api metadata creation.

        The attributes required are listed in `__attr_required_metadata`.

        Returns
        -------
        bool
            True, if creation of metadata json is possible. False, if not.

        Examples
        -------
        Check if metadata is valid for Dataverse api upload::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> data = {
            >>>     'title': 'pyDataverse study 2019',
            >>>     'dsDescription': 'New study about pyDataverse usage in 2019'
            >>> }
            >>> ds.set(data)
            >>> ds.is_valid()
            False
            >>> ds.author = [{'authorName': 'LastAuthor1, FirstAuthor1'}]
            >>> ds.datasetContact = [{'datasetContactName': 'LastContact1, FirstContact1'}]
            >>> ds.subject = ['Engineering']
            >>> ds.is_valid()
            True

        Todo
        -------
        Test out required fields or ask Harvard.

        """
        is_valid = True

        # check if all required attributes are set
        for attr in self.__attr_required_metadata:
            if not self.__getattribute__(attr):
                is_valid = False
                print('Metadata not valid: attribute \'{0}\' missing.'.format(attr))

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

    def dict(self, format='dv_up'):
        """Create dicts in different data formats.

        Parameters
        ----------
        format : string
            Data format for dict creation. Available formats are: `dv_up` with
            all metadata for Dataverse api upload, and `all` with all attributes
            set.

        Returns
        -------
        dict
            Data as dict.

        Examples
        -------
        Get dict of Dataverse metadata::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> data = {
            >>>     'title': 'pyDataverse study 2019',
            >>>     'dsDescription': 'New study about pyDataverse usage in 2019'
            >>> }
            >>> ds.set(data)
            >>> data = dv.dict()
            >>> data['title']
            'pyDataverse study 2019'

        Todo
        -------
        Validate standard

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
                for attr in self.__attr_valid_metadata_datasetVersion:
                    if self.__getattribute__(attr) is not None:
                        data['datasetVersion'][attr] = self.__getattribute__(attr)

                """citation"""
                if self.citation_displayName:
                    citation['displayName'] = self.citation_displayName

                # Generate first level attributes
                for attr in self.__attr_valid_metadata_citation_dicts:
                    if self.__getattribute__(attr) is not None:
                        citation['fields'].append({
                            'typeName': attr,
                            'value': self.__getattribute__(attr)
                        })

                # Generate fields attributes
                for key, val in self.__attr_valid_metadata_citation_arrays.items():
                    if self.__getattribute__(key) is not None:
                        citation['fields'].append({
                            'typeName': key,
                            'value': self.__generate_dicts(key, val)
                        })

                # Generate series attributes
                if self.__getattribute__('series') is not None:
                    tmp_dict = {}
                    tmp_dict['value'] = {}
                    if 'seriesName' in self.__getattribute__('series'):
                        if self.__getattribute__('seriesName') is not None:
                            tmp_dict['value']['seriesName'] = {}
                            tmp_dict['value']['seriesName']['typeName'] = 'seriesName'
                            tmp_dict['value']['seriesName']['value'] = self.__getattribute__('seriesName')
                    if 'seriesInformation' in self.__getattribute__('series'):
                        if self.__getattribute__('seriesInformation') is not None:
                            tmp_dict['value']['seriesInformation'] = {}
                            tmp_dict['value']['seriesInformation']['typeName'] = 'seriesInformation'
                            tmp_dict['value']['seriesInformation']['value'] = self.__getattribute__('seriesInformation')
                    citation['fields'].append({
                        'typeName': 'series',
                        'value': tmp_dict
                    })

                """geospatial"""
                # Generate first level attributes
                for attr in self.__attr_valid_metadata_geospatial_dicts:
                    if self.__getattribute__(attr) is not None:
                        geospatial['fields'].append({
                            'typeName': attr,
                            'value': self.__getattribute__(attr)
                        })

                # Generate fields attributes
                for key, val in self.__attr_valid_metadata_geospatial_arrays.items():
                    # check if attribute exists
                    if self.__getattribute__(key) is not None:
                        geospatial['fields'].append({
                            'typeName': key,
                            'value': self.__generate_dicts(key, val)
                        })

                """socialscience"""
                # Generate first level attributes
                for attr in self.__attr_valid_metadata_socialscience_dicts:
                    if self.__getattribute__(attr) is not None:
                        socialscience['fields'].append({
                            'typeName': attr,
                            'value': self.__getattribute__(attr)
                        })

                # Generate targetSampleSize attributes
                if self.__getattribute__('targetSampleSize') is not None:
                    tmp_dict = {}
                    tmp_dict['value'] = {}
                    if 'targetSampleActualSize' in self.__getattribute__('targetSampleSize'):
                        if self.__getattribute__('targetSampleActualSize') is not None:
                            tmp_dict['value']['targetSampleActualSize'] = {}
                            tmp_dict['value']['targetSampleActualSize']['typeName'] = 'targetSampleActualSize'
                            tmp_dict['value']['targetSampleActualSize']['value'] = self.__getattribute__('targetSampleActualSize')
                    if 'targetSampleSizeFormula' in self.__getattribute__('targetSampleSize'):
                        if self.__getattribute__('targetSampleSizeFormula') is not None:
                            tmp_dict['value']['targetSampleSizeFormula'] = {}
                            tmp_dict['value']['targetSampleSizeFormula']['typeName'] = 'targetSampleSizeFormula'
                            tmp_dict['value']['targetSampleSizeFormula']['value'] = self.__getattribute__('targetSampleSizeFormula')
                    socialscience['fields'].append({
                        'typeName': 'series',
                        'value': tmp_dict
                    })

                # Generate socialScienceNotes attributes
                if self.__getattribute__('socialScienceNotes') is not None:
                    tmp_dict = {}
                    tmp_dict['value'] = {}
                    if 'socialScienceNotesType' in self.__getattribute__('socialScienceNotes'):
                        if self.__getattribute__('socialScienceNotesType') is not None:
                            tmp_dict['value']['socialScienceNotesType'] = {}
                            tmp_dict['value']['socialScienceNotesType']['typeName'] = 'socialScienceNotesType'
                            tmp_dict['value']['socialScienceNotesType']['value'] = self.__getattribute__('socialScienceNotesType')
                    if 'socialScienceNotesSubject' in self.__getattribute__('socialScienceNotes'):
                        if self.__getattribute__('socialScienceNotesSubject') is not None:
                            tmp_dict['value']['socialScienceNotesSubject'] = {}
                            tmp_dict['value']['socialScienceNotesSubject']['typeName'] = 'socialScienceNotesSubject'
                            tmp_dict['value']['socialScienceNotesSubject']['value'] = self.__getattribute__('socialScienceNotesSubject')
                    if 'socialScienceNotesText' in self.__getattribute__('socialScienceNotes'):
                        if self.__getattribute__('socialScienceNotesText') is not None:
                            tmp_dict['value']['socialScienceNotesText'] = {}
                            tmp_dict['value']['socialScienceNotesText']['typeName'] = 'socialScienceNotesText'
                            tmp_dict['value']['socialScienceNotesText']['value'] = self.__getattribute__('socialScienceNotesText')
                    socialscience['fields'].append({
                        'typeName': 'series',
                        'value': tmp_dict
                    })

                """journal"""
                # Generate first level attributes
                for attr in self.__attr_valid_metadata_journal_dicts:
                    if self.__getattribute__(attr) is not None:
                        journal['fields'].append({
                            'typeName': attr,
                            'value': self.__getattribute__(attr)
                        })

                # Generate fields attributes
                for key, val in self.__attr_valid_metadata_journal_arrays.items():
                    if self.__getattribute__(key) is not None:
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
            for attr in self.__attr_valid_class:
                if self.__getattribute__(attr) is not None:
                    data[attr] = self.__getattribute__(attr)
            return data

        else:
            print('dict can not be created. Format is not valid')
            return None

    def __generate_dicts(self, key, val):
        """Generate dicts for array attributes of Dataverse api metadata upload.

        Parameters
        ----------
        key : string
            Name of attribute
        val : string
            Value of attribute.

        Returns
        -------
        list
            List of filled dicts of metadata for Dataverse api upload.

        """
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
        """Create Dataset json from attributes.

        Parameters
        ----------
        format : string
            Data format of input. Available formats are: `dv_up` for Dataverse
            Api upload compatible format and `all` with all attributes named in
            `__attr_valid_class`.

        Returns
        -------
        string
            json-formatted string of Dataverse metadata for api upload.

        Examples
        -------
        Get json of Dataverse api upload::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> data = {
            >>>     'title': 'pyDataverse study 2019',
            >>>     'dsDescription': 'New study about pyDataverse usage in 2019'
            >>>     'author': [{'authorName': 'LastAuthor1, FirstAuthor1'}],
            >>>     'datasetContact': [{'datasetContactName': 'LastContact1, FirstContact1'}],
            >>>     'subject': ['Engineering'],
            >>> }
            >>> ds.set(data)
            >>> data = ds.json()

        Todo
        -------
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
        """Export Dataset metadata to Dataverse api upload json.

        Parameters
        ----------
        filename : string
            Filename with full path.
        format : string
            Data format for export. Available format is: `dv_up` with all
            metadata for Dataverse api upload.

        Examples
        -------
        Export metadata to json file::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> data = {
            >>>     'title': 'pyDataverse study 2019',
            >>>     'dsDescription': 'New study about pyDataverse usage in 2019'
            >>>     'author': [{'authorName': 'LastAuthor1, FirstAuthor1'}],
            >>>     'datasetContact': [{'datasetContactName': 'LastContact1, FirstContact1'}],
            >>>     'subject': ['Engineering'],
            >>> }
            >>> ds.export_metadata('tests/data/export_dataset.json')

        """
        if format == 'dv_up':
            return write_file_json(filename, self.dict())
        else:
            # TODO: Exception
            print('Data-format not right.')


class Datafile(object):
    """Base class for the Datafile model.

    Parameters
    ----------
    filename : string
        Filename with full path.
    pid : type
        Description of parameter `pid` (the default is None).

    Attributes
    ----------
    description : string
        Description of datafile
    restrict : bool
        Unknown
    __attr_required_metadata : list
        List with required metadata.
    __attr_valid_metadata : list
        List with valid metadata for Dataverse api upload.
    __attr_valid_class : list
        List of all attributes.
    pid
    filename

    """

    """Attributes required for Datafile metadata json."""
    __attr_required_metadata = [
        'filename',
        'pid'
    ]

    """Attributes on first level of Datafile metadata json."""
    __attr_valid_metadata = [
        'description',
        'pid',
        'restrict'
    ]
    """Attributes on first level of Datafile metadata json."""
    __attr_valid_class = [
        'filename'
    ] + __attr_valid_metadata

    def __init__(self, filename=None, pid=None):
        """Init a Datafile() class.

        Parameters
        ----------
        filename : string
            Filename with full path.
        pid : string
            Persistend identifier, e.g. DOI.

        Examples
        -------
        Create a Datafile::

            >>> from pyDataverse.models import Datafile
            >>> df = Datafile()
            >>> df
            <pyDataverse.models.Datafile at 0x7f4dfc0466a0>

        """
        """Misc"""
        self.pid = pid
        self.filename = filename

        """Metadata"""
        self.description = None
        self.restrict = None

    def __str__(self):
        """Return name of Datafile() class for users."""
        return 'pyDataverse Datafile() model class.'

    def set(self, data):
        """Set class attributes with a flat dict.

        Parameters
        ----------
        data : dict
            Flat dict with data. Key's must be name the same as the class
            attribute, the data should be mapped to.

        Examples
        -------
        Set Datafile attributes via flat dict::

            >>> from pyDataverse.models import Datafile
            >>> df = Datafile()
            >>> data = {
            >>>     'pid': 'doi:10.11587/EVMUHP',
            >>>     'description': 'Test file',
            >>>     'filename': 'tests/data/datafile.txt'
            >>> }
            >>> df.set(data)
            >>> df.pid
            'doi:10.11587/EVMUHP',

        """
        for key, val in data.items():
            if key in self.__attr_valid_class:
                self.__setattr__(key, val)
            else:
                # TODO: Raise Exception
                print('Key {0} not valid.'.format(key))

    def is_valid(self):
        """Check if set attributes are valid for Dataverse api metadata creation.

        Returns
        -------
        bool
            True, if creation of metadata json is possible. False, if not.

        Examples
        -------
        Check if metadata is valid for Dataverse api upload::

            >>> from pyDataverse.models import Datafile
            >>> df = Datafile()
            >>> data = {
            >>>     'pid': 'doi:10.11587/EVMUHP',
            >>>     'description': 'Test file',
            >>>     'filename': 'tests/data/datafile.txt'
            >>> }
            >>> df.set(data)
            >>> df.is_valid
            True
            >>> df.filename = None
            >>> df.is_valid
            False

        """
        is_valid = True

        for attr in self.__attr_required_metadata:
            if self.__getattribute__(attr) is None:
                is_valid = False
                print('attribute \'{0}\' missing.'.format(attr))

        return is_valid

    def dict(self, format='dv_up'):
        """Create dict in different data formats.

        Parameters
        ----------
        format : string
            Data format for dict creation. Available formats are: `dv_up` with
            all metadata for Dataverse api upload, and `all` with all attributes
            set.

        Returns
        -------
        dict
            Data as dict.

        Examples
        -------
        Check if metadata is valid for Dataverse api upload::

            >>> from pyDataverse.models import Datafile
            >>> df = Datafile()
            >>> data = {
            >>>     'pid': 'doi:10.11587/EVMUHP',
            >>>     'description': 'Test file',
            >>>     'filename': 'tests/data/datafile.txt'
            >>> }
            >>> df.set(data)
            >>> data = df.dict()
            >>> data['description']
            'Test file'

        Todo
        -------
        Validate standards.

        """
        data = {}
        if format == 'dv_up':
            if self.is_valid():
                for attr in self.__attr_valid_metadata:
                    if self.__getattribute__(attr) is not None:
                        data[attr] = self.__getattribute__(attr)

                return data
            else:
                print('dict can not be created. Data is not valid')
                return None
        elif format == 'all':
            for attr in self.__attr_valid_class:
                if self.__getattribute__(attr) is not None:
                    data[attr] = self.__getattribute__(attr)
            return data
        else:
            # TODO: Exception
            print('Format not right for dict.')
            return None

    def json(self, format='dv_up'):
        r"""Create json from attributes.

        Parameters
        ----------
        format : string
            Data format of input. Available formats are: `dv_up` for Dataverse
            Api upload compatible format and `all` with all attributes named in
            `__attr_valid_class`.

        Returns
        -------
        string
            json-formatted string of Dataverse metadata for api upload.

        Examples
        -------
        Get dict of Dataverse metadata::

            >>> from pyDataverse.models import Datafile
            >>> df = Datafile()
            >>> data = {
            >>>     'pid': 'doi:10.11587/EVMUHP',
            >>>     'description': 'Test file',
            >>>     'filename': 'tests/data/datafile.txt'
            >>> }
            >>> df.set(data)
            >>> df.dict()
            {'description': 'Test file',
             'directoryLabel': None,
             'restrict': None}

        Todo
        -------
        Validate standards.
        Link to default json file

        """
        if format == 'dv_up':
            data = self.dict('dv_up')
            if data:
                return dict_to_json(data)
            else:
                print('Dict can not be created')
                return None
        elif format == 'all':
            data = self.dict('all')
            if data:
                return dict_to_json(data)
            else:
                print('Dict can not be created')
                return None
        else:
            # TODO Exception
            print('data format not valid.')
            return None
