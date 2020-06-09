# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse data-types data model."""
from __future__ import absolute_import
import json
from pyDataverse.utils import read_json
from pyDataverse.utils import validate_data
from pyDataverse.utils import write_json

"""
Data-structure to work with data and metadata of Dataverses, Datasets and
Datafiles - coming from different sources.
"""


class DVObject(object):
    def __init__(self):
        self.default_validate_format = 'dataverse_upload'
        self.attr_dv_up_values = None

    def set(self, data):
        """Set class attributes with a flat :class:`dict`.

        Parameters
        ----------
        data : dict
            Flat :class:`dict` with data. All keys will be mapped to a similar
            called attribute with it's value.

        """
        for key, val in data.items():
            self.__setattr__(key, val)

    def dict(self):
        """Create different data outputs as :class:`dict`.

        Creates different data outputs - different in structure and content -
        of the objects data.

        Parameters
        ----------
        format : string
            Data format for :class:`dict` creation. Available format so far are:
            ``dataverse_upload``: Dataverse API Upload Dataverse JSON metadata standard.
            ``all``: All attributes.

        Returns
        -------
        dict
            Data as :class:`dict` with expected structure and content.

        Examples
        -------
        Get dict of Dataverse metadata::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()
            >>> data = {
            >>>     'dataverseContacts': [
            >>>         {'contactEmail': 'test@example.com'}
            >>>     ],
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

        for attr in list(self.__dict__.keys()):
            if attr in list(self.__dict__.keys()):
                if self.__getattribute__(attr) is not None:
                    data[attr] = self.__getattribute__(attr)
        return data

    def validate_json(self, format=None, filename_schema=None):
        """Short summary.

        Parameters
        ----------
        format : type
            Description of parameter `format`.
        filename_schema : type
            Description of parameter `filename_schema`.

        Returns
        -------
        type
            Description of returned object.

        """
        if not format:
            format = self.default_validate_format
        if not filename_schema:
            filename_schema = self.default_validate_schema_filename

        data_json = self.to_json(format=format)
        is_valid = validate_data(json.loads(data_json), filename_schema)
        if is_valid:
            return True
        else:
            return False

    def from_json(self, filename, format=None, validate=True,
                  filename_schema=None):
        """Import Dataverse API Upload JSON metadata from JSON file.

        Parses in data stored in the Dataverse API Dataverse JSON standard.

        Parameters
        ----------
        filename : string
            Filename with full path.
        format : string
            Data format for input data formats. Available format so far are:
            ``dv_up``: Dataverse API Upload Dataverse JSON metadata standard.
            ``all``: All attributes.

        Examples
        -------
        Import metadata coming from JSON file::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()
            >>> dv.import_data('tests/data/dataverse_full.json')
            >>> dv.name
            'Test pyDataverse'

        """
        data = {}
        allowed_formats = [
            'dataverse_upload',
            'dataverse_download',
            'dspace',
            'custom'
        ]

        if not format:
            format = self.default_validate_format
        if not filename_schema:
            filename_schema = self.default_validate_schema_filename

        if format in allowed_formats:
            if format == 'dataverse_upload':
                data_json = read_json(filename)
                if validate:
                    validate_data(data_json, filename_schema)
                # get first level metadata and parse it automatically
                for key, val in data_json.items():
                    if key in self.attr_dv_up_values:
                        data[key] = data_json[key]
                    else:
                        print('INFO: Attribute {0} not valid for import (dv_up).'.format(key))
                self.set(data)
                return True
            elif format == 'dataverse_download':
                return True
            elif format == 'dspace':
                pass
            elif format == 'custom':
                pass
        else:
            # TODO: Exception
            print('WARNING: Data-format not right.')
            return False

    def to_json(self, format=None, validate=True, filename_schema=None):
        r"""Create JSON from attributes.

        Parameters
        ----------
        format : string
            Data format of input. Available formats are: `dv_up` for Dataverse
            API upload compatible format (default) and `all` with all attributes
            named in `__attr_valid_class`.
        validate : boolean
            Should the output be validated.
        filename_schema : string
            Filename of the schema to be validated against.

        Returns
        -------
        string
            JSON formatted string of formatted data-structure.

        """
        data = {}
        allowed_formats = [
            'dataverse_upload',
            'dspace',
            'custom'
        ]

        if not format:
            format = self.default_validate_format
        if not filename_schema:
            filename_schema = self.default_validate_schema_filename

        if format in allowed_formats:
            if format == 'dataverse_upload':
                for attr in self.attr_dv_up_values:
                    # check if attribute exists
                    if attr in list(self.dict().keys()):
                        data[attr] = self.dict()[attr]
            elif format == 'dspace':
                pass
            elif format == 'custom':
                pass
            if validate:
                validate_data(data, filename_schema)
            return json.dumps(data, indent=2)
        else:
            return None


class Dataverse(DVObject):
    """Base class for Dataverse data model."""

    def __init__(self):
        """Init :class:`Dataverse()`.

        Examples
        -------
        Create a Dataverse::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()

        """
        super().__init__()
        self.default_validate_schema_filename = 'schemas/json/dataverse_upload_schema.json'

        """Attributes to be imported from `dv_up` file."""
        self.attr_dv_up_values = [
            'affiliation',
            'alias',
            'dataverseContacts',
            'dataverseType',
            'description',
            'name'
        ]

    def __str__(self):
        """Return name of class :class:`Dataverse()` for users."""
        return 'pyDataverse Dataverse() model class.'


class Dataset(DVObject):
    """Base class for the Dataset data model."""

    """
    Dataverse API Upload Dataset JSON attributes inside
    ds[\'datasetVersion\'].
    """
    __attr_import_dv_up_datasetVersion_values = [
        'license',
        'termsOfAccess',
        'termsOfUse'
    ]

    """
    Dataverse API Upload Dataset JSON attributes inside
    ds[\'datasetVersion\'][\'metadataBlocks\'][\'citation\'][\'fields\'].
    """
    __attr_import_dv_up_citation_fields_values = [
        'accessToSources',
        'alternativeTitle',
        'alternativeURL',
        'characteristicOfSources',
        'dateOfDeposit',
        'dataSources',
        'depositor',
        'distributionDate',
        'kindOfData',
        'language',
        'notesText',
        'originOfSources',
        'otherReferences',
        'productionDate',
        'productionPlace',
        'relatedDatasets',
        'relatedMaterial',
        'subject',
        'subtitle',
        'title'
    ]

    """
    Dataverse API Upload Dataset JSON attributes inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'citation\'][\'fields\'].
    """
    __attr_import_dv_up_citation_fields_arrays = {
        'author': ['authorName', 'authorAffiliation', 'authorIdentifierScheme',
                   'authorIdentifier'],
        'contributor': ['contributorType', 'contributorName'],
        'dateOfCollection': ['dateOfCollectionStart', 'dateOfCollectionEnd'],
        'datasetContact': ['datasetContactName', 'datasetContactAffiliation',
                           'datasetContactEmail'],
        'distributor': ['distributorName', 'distributorAffiliation',
                        'distributorAbbreviation', 'distributorURL',
                        'distributorLogoURL'],
        'dsDescription': ['dsDescriptionValue', 'dsDescriptionDate'],
        'grantNumber': ['grantNumberAgency', 'grantNumberValue'],
        'keyword': ['keywordValue', 'keywordVocabulary',
                    'keywordVocabularyURI'],
        'producer': ['producerName', 'producerAffiliation',
                     'producerAbbreviation', 'producerURL', 'producerLogoURL'],
        'otherId': ['otherIdAgency', 'otherIdValue'],
        'publication': ['publicationCitation', 'publicationIDType',
                        'publicationIDNumber', 'publicationURL'],
        'software': ['softwareName', 'softwareVersion'],
        'timePeriodCovered': ['timePeriodCoveredStart',
                              'timePeriodCoveredEnd'],
        'topicClassification': ['topicClassValue', 'topicClassVocab']
    }

    """
    Attributes of Dataverse API Upload Dataset JSON metadata standard inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'geospatial\'][\'fields\'].
    """
    __attr_import_dv_up_geospatial_fields_values = [
        'geographicUnit'
    ]

    """
    Attributes of Dataverse API Upload Dataset JSON metadata standard inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'geospatial\'][\'fields\'].
    """
    __attr_import_dv_up_geospatial_fields_arrays = {
        'geographicBoundingBox': ['westLongitude', 'eastLongitude',
                                  'northLongitude', 'southLongitude'],
        'geographicCoverage': ['country', 'state', 'city',
                               'otherGeographicCoverage']
    }

    """
    Attributes of Dataverse API Upload Dataset JSON metadata standard inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'socialscience\'][\'fields\'].
    """
    __attr_import_dv_up_socialscience_fields_values = [
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
        'researchInstrument',
        'responseRate',
        'samplingErrorEstimates',
        'samplingProcedure',
        'unitOfAnalysis',
        'universe',
        'timeMethod',
        'weighting'
    ]

    """
    Attributes of Dataverse API Upload Dataset JSON metadata standard inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'journal\'][\'fields\'].
    """
    __attr_import_dv_up_journal_fields_values = [
        'journalArticleType'
    ]

    """
    Attributes of Dataverse API Upload Dataset JSON metadata standard inside
    [\'datasetVersion\'][\'metadataBlocks\'][\'journal\'][\'fields\'].
    """
    __attr_import_dv_up_journal_fields_arrays = {
        'journalVolumeIssue': ['journalVolume', 'journalIssue',
                               'journalPubDate']
    }

    """Required attributes for valid `dv_up` metadata dict creation."""
    __attr_dict_dv_up_required = [
        'author',
        'datasetContact',
        'dsDescription',
        'subject',
        'title'
    ]

    """typeClass primitive."""
    __attr_dict_dv_up_typeClass_primitive = [
        'accessToSources',
        'alternativeTitle',
        'alternativeURL',
        'authorAffiliation',
        'authorIdentifier',
        'authorName',
        'characteristicOfSources',
        'city',
        'contributorName',
        'dateOfDeposit',
        'dataSources',
        'depositor',
        'distributionDate',
        'kindOfData',
        'notesText',
        'originOfSources',
        'otherGeographicCoverage',
        'otherReferences',
        'productionDate',
        'productionPlace',
        'publicationCitation',
        'publicationIDNumber',
        'publicationURL',
        'relatedDatasets',
        'relatedMaterial',
        'seriesInformation',
        'seriesName',
        'state',
        'subtitle',
        'title'
    ] + __attr_import_dv_up_citation_fields_arrays['dateOfCollection'] \
    + __attr_import_dv_up_citation_fields_arrays['datasetContact'] \
    + __attr_import_dv_up_citation_fields_arrays['distributor'] \
    + __attr_import_dv_up_citation_fields_arrays['dsDescription'] \
    + __attr_import_dv_up_citation_fields_arrays['grantNumber'] \
    + __attr_import_dv_up_citation_fields_arrays['keyword'] \
    + __attr_import_dv_up_citation_fields_arrays['producer'] \
    + __attr_import_dv_up_citation_fields_arrays['otherId'] \
    + __attr_import_dv_up_citation_fields_arrays['software'] \
    + __attr_import_dv_up_citation_fields_arrays['timePeriodCovered'] \
    + __attr_import_dv_up_citation_fields_arrays['topicClassification'] \
    + __attr_import_dv_up_geospatial_fields_values \
    + __attr_import_dv_up_geospatial_fields_arrays['geographicBoundingBox'] \
    + __attr_import_dv_up_socialscience_fields_values \
    + __attr_import_dv_up_journal_fields_arrays['journalVolumeIssue'] \
    + ['socialScienceNotesType', 'socialScienceNotesSubject', 'socialScienceNotesText'] \
    + ['targetSampleActualSize', 'targetSampleSizeFormula'] \

    """typeClass compound."""
    __attr_dict_dv_up_typeClass_compound = [
    ] + list(__attr_import_dv_up_citation_fields_arrays.keys()) \
    + list(__attr_import_dv_up_geospatial_fields_arrays.keys()) \
    + list(__attr_import_dv_up_journal_fields_arrays.keys()) \
    + ['series', 'socialScienceNotes', 'targetSampleSize']

    """typeClass controlledVocabulary."""
    __attr_dict_dv_up_typeClass_controlledVocabulary = [
        'authorIdentifierScheme',
        'contributorType',
        'country',
        'journalArticleType',
        'language',
        'publicationIDType',
        'subject',
    ]

    __attr_dict_dv_up_multiple = [
    ]

    """
    This attributes are excluded from automatic parsing in ds.dict() creation.
    """
    __attr_dict_dv_up_single_dict = [
        'series',
        'socialScienceNotes',
        'targetSampleSize'
    ]

    """Attributes of displayName."""
    __attr_displayNames = [
        'citation_displayName',
        'geospatial_displayName',
        'socialscience_displayName',
        'journal_displayName'
    ]

    def __init__(self):
        """Init a Dataset() class.

        Examples
        -------
        Create a Dataverse::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()

        """
        super().__init__()
        self.default_validate_schema_filename = 'schemas/json/dataset_upload_default_schema.json'

    def __str__(self):
        """Return name of Dataset() class for users."""
        return 'pyDataverse Dataset() model class.'

    def from_json(self, filename, format=None,
                  filename_mapping=None, validate=True,
                  filename_schema=None):
        """Import Dataset API Upload JSON metadata from JSON file.

        Parses in data stored in the Dataverse API Dataset JSON standard.

        Parameters
        ----------
        filename : string
            Filename with full path.
        format : string
            Data format of input data, coming from file. Available format so
            far are: ``dv_up`` for the Dataverse API Upload Dataset JSON
            metadata standard.

        Examples
        -------
        Set Dataverse attributes via flat :class:`dict`::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> ds.import_data('tests/data/dataset_full.json')
            >>> ds.title
            'Replication Data for: Title'

        """
        data = {}
        allowed_formats = [
            'dataverse_upload',
            'dataverse_download',
            'dspace',
            'custom'
        ]

        if not format:
            format = self.default_validate_format
        if not filename_schema:
            filename_schema = self.default_validate_schema_filename

        if format in allowed_formats:
            if format == 'dataverse_upload':
                data_json = read_json(filename)
                if validate:
                    validate_data(data_json, filename_schema)
                """dataset"""
                # get first level metadata and parse it automatically
                for key, val in data_json['datasetVersion'].items():
                    if not key == 'metadataBlocks':
                        if key in self.__attr_import_dv_up_datasetVersion_values:
                            data[key] = val
                        else:
                            print('Attribute {0} not valid for import (dv_up).'.format(key))

                if 'metadataBlocks' in data_json['datasetVersion']:

                    """citation"""
                    if 'citation' in data_json['datasetVersion']['metadataBlocks']:
                        citation = data_json['datasetVersion']['metadataBlocks']['citation']
                        if 'displayName' in citation:
                            data['citation_displayName'] = citation['displayName']

                        for field in citation['fields']:
                            if field['typeName'] in self.__attr_import_dv_up_citation_fields_values:
                                data[field['typeName']] = field['value']
                            elif field['typeName'] in self.__attr_import_dv_up_citation_fields_arrays:
                                data[field['typeName']] = self.__parse_field_array(
                                    field['value'],
                                    self.__attr_import_dv_up_citation_fields_arrays[field['typeName']])
                            elif field['typeName'] == 'series':
                                data['series'] = {}
                                if 'seriesName' in field['value']:
                                    data['series']['seriesName'] = field['value']['seriesName']['value']
                                if 'seriesInformation' in field['value']:
                                    data['series']['seriesInformation'] = field['value']['seriesInformation']['value']
                            else:
                                print('Attribute {0} not valid for import (dv_up).'.format(field['typeName']))
                    else:
                        # TODO: Exception
                        print('Citation not in JSON')

                    """geospatial"""
                    if 'geospatial' in data_json['datasetVersion']['metadataBlocks']:
                        geospatial = data_json['datasetVersion']['metadataBlocks']['geospatial']
                        if 'displayName' in geospatial:
                            self.__setattr__('geospatial_displayName',
                                             geospatial['displayName'])

                        for field in geospatial['fields']:
                            if field['typeName'] in self.__attr_import_dv_up_geospatial_fields_values:
                                data[field['typeName']] = field['value']
                            elif field['typeName'] in self.__attr_import_dv_up_geospatial_fields_arrays:
                                data[field['typeName']] = self.__parse_field_array(
                                    field['value'],
                                    self.__attr_import_dv_up_geospatial_fields_arrays[field['typeName']])
                            else:
                                print('Attribute {0} not valid for import (dv_up).'.format(field['typeName']))
                    else:
                        # TODO: Exception
                        print('geospatial not in JSON')

                    """socialscience"""
                    if 'socialscience' in data_json['datasetVersion']['metadataBlocks']:
                        socialscience = data_json['datasetVersion']['metadataBlocks']['socialscience']

                        if 'displayName' in socialscience:
                            self.__setattr__('socialscience_displayName',
                                             socialscience['displayName'])

                        for field in socialscience['fields']:
                            if field['typeName'] in self.__attr_import_dv_up_socialscience_fields_values:
                                data[field['typeName']] = field['value']
                            elif field['typeName'] == 'targetSampleSize':
                                data['targetSampleSize'] = {}
                                if 'targetSampleActualSize' in field['value']:
                                    data['targetSampleSize']['targetSampleActualSize'] = field['value']['targetSampleActualSize']['value']
                                if 'targetSampleSizeFormula' in field['value']:
                                    data['targetSampleSize']['targetSampleSizeFormula'] = field['value']['targetSampleSizeFormula']['value']
                            elif field['typeName'] == 'socialScienceNotes':
                                data['socialScienceNotes'] = {}
                                if 'socialScienceNotesType' in field['value']:
                                    data['socialScienceNotes']['socialScienceNotesType'] = field['value']['socialScienceNotesType']['value']
                                if 'socialScienceNotesSubject' in field['value']:
                                    data['socialScienceNotes']['socialScienceNotesSubject'] = field['value']['socialScienceNotesSubject']['value']
                                if 'socialScienceNotesText' in field['value']:
                                    data['socialScienceNotes']['socialScienceNotesText'] = field['value']['socialScienceNotesText']['value']
                            else:
                                print('Attribute {0} not valid for import (dv_up).'.format(field['typeName']))
                    else:
                        # TODO: Exception
                        print('socialscience not in JSON')

                    """journal"""
                    if 'journal' in data_json['datasetVersion']['metadataBlocks']:
                        journal = data_json['datasetVersion']['metadataBlocks']['journal']

                        if 'displayName' in journal:
                            self.__setattr__('journal_displayName',
                                             journal['displayName'])

                        for field in journal['fields']:
                            if field['typeName'] in self.__attr_import_dv_up_journal_fields_values:
                                data[field['typeName']] = field['value']
                            elif field['typeName'] in self.__attr_import_dv_up_journal_fields_arrays:
                                data[field['typeName']] = self.__parse_field_array(
                                    field['value'],
                                    self.__attr_import_dv_up_journal_fields_arrays[field['typeName']])
                            else:
                                print('Attribute {0} not valid for import (dv_up).'.format(field['typeName']))
                    else:
                        # TODO: Exception
                        print('journal not in JSON')
                self.set(data)
                return True
            else:
                # TODO: Exception
                print('Data-format not right')
                return False

    def __parse_field_array(self, data, attr_list):
        """Parse out Dataverse API Upload Dataset JSON arrays.

        Parameters
        ----------
        data : list
            List of dictionaries of a specific Dataverse API metadata field.
        attr_list : list
            List of attributes to be parsed.

        Returns
        -------
        list
            List of :class:`dict`s with parsed out key-value pairs.

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

    def validate_json(self):
        """Check if all attributes required for Dataverse metadata are set.

        Check if all attributes are set necessary for the Dataverse API Upload
        JSON metadata standard of a Dataset.

        Returns
        -------
        bool
            ``True``, if creation of metadata JSON is possible. `False`, if
            not.

        Examples
        -------
        Check if metadata is valid for Dataverse API upload::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> data = {
            >>>     'title': 'pyDataverse study 2019',
            >>>     'dsDescription': [
            >>>         {'dsDescriptionValue': 'New study about pyDataverse usage in 2019'}
            >>>     ]
            >>> }
            >>> ds.set(data)
            >>> ds.validate_json()
            False
            >>> ds.author = [{'authorName': 'LastAuthor1, FirstAuthor1'}]
            >>> ds.datasetContact = [{'datasetContactName': 'LastContact1, FirstContact1'}]
            >>> ds.subject = ['Engineering']
            >>> ds.validate_json()
            True

        Todo
        -------
        Test out required fields or ask Harvard.

        """
        is_valid = True

        # check if all required attributes are set
        for attr in self.__attr_dict_dv_up_required:
            if attr in list(self.__dict__.keys()):
                if not self.__getattribute__(attr):
                    is_valid = False
                    print('Attribute \'{0}\' is `False`.'.format(attr))
            else:
                is_valid = False
                print('Attribute \'{0}\' missing.'.format(attr))

        # check if attributes set are complete where necessary
        if 'timePeriodCovered' in list(self.__dict__.keys()):
            tp_cov = self.__getattribute__('timePeriodCovered')
            if tp_cov:
                for tp in tp_cov:
                    if 'timePeriodCoveredStart' in tp or 'timePeriodCoveredEnd' in tp:
                        if not ('timePeriodCoveredStart' in tp and 'timePeriodCoveredEnd' in tp):
                            is_valid = False
                            print('timePeriodCovered attribute missing.')

        if 'dateOfCollection' in list(self.__dict__.keys()):
            d_coll = self.__getattribute__('dateOfCollection')
            if d_coll:
                for d in d_coll:
                    if 'dateOfCollectionStart' in d or 'dateOfCollectionEnd' in d:
                        if not ('dateOfCollectionStart' in d and 'dateOfCollectionEnd' in d):
                            is_valid = False
                            print('dateOfCollection attribute missing.')

        if 'author' in list(self.__dict__.keys()):
            authors = self.__getattribute__('author')
            if authors:
                for a in authors:
                    if 'authorAffiliation' in a or 'authorIdentifierScheme' in a or 'authorIdentifier' in a:
                        if 'authorName' not in a:
                            is_valid = False
                            print('author attribute missing.')

        if 'datasetContact' in list(self.__dict__.keys()):
            ds_contac = self.__getattribute__('datasetContact')
            if ds_contac:
                for c in ds_contac:
                    if 'datasetContactAffiliation' in c or 'datasetContactEmail' in c:
                        if 'datasetContactName' not in c:
                            is_valid = False
                            print('datasetContact attribute missing.')

        if 'producer' in list(self.__dict__.keys()):
            producer = self.__getattribute__('producer')
            if producer:
                for p in producer:
                    if 'producerAffiliation' in p or 'producerAbbreviation' in p or 'producerURL' in p or 'producerLogoURL' in p:
                        if not p['producerName']:
                            is_valid = False
                            print('producer attribute missing.')

        if 'contributor' in list(self.__dict__.keys()):
            contributor = self.__getattribute__('contributor')
            if contributor:
                for c in contributor:
                    if 'contributorType' in c:
                        if 'contributorName' not in c:
                            is_valid = False
                            print('contributor attribute missing.')

        if 'distributor' in list(self.__dict__.keys()):
            distributor = self.__getattribute__('distributor')
            if distributor:
                for d in distributor:
                    if 'distributorAffiliation' in d or 'distributorAbbreviation' in d or 'distributorURL' in d or 'distributorLogoURL' in d:
                        if 'distributorName' not in d:
                            is_valid = False
                            print('distributor attribute missing.')

        if 'geographicBoundingBox' in list(self.__dict__.keys()):
            bbox = self.__getattribute__('geographicBoundingBox')
            if bbox:
                for b in bbox:
                    if b:
                        if not ('westLongitude' in b and 'eastLongitude' in b and 'northLongitude' in b and 'southLongitude' in b):
                            is_valid = False
                            print('geographicBoundingBox attribute missing.')

        return is_valid

    def __generate_field_arrays(self, key, sub_keys):
        """Generate dicts for array attributes of Dataverse API metadata upload.

        Parameters
        ----------
        key : string
            Name of attribute.
        sub_keys : string
            List of keys to be created.

        Returns
        -------
        list
            List of filled :class:`dict`s of metadata for Dataverse API upload.

        """
        # check if attribute exists
        tmp_list = []
        if self.__getattribute__(key):
            attr = self.__getattribute__(key)
            # loop over list of attribute dict
            for d in attr:
                tmp_dict = {}
                # iterate over key-value pairs
                for k, v in d.items():
                    # check if key is in attribute list
                    if k in sub_keys:
                        multiple = None
                        typeClass = None
                        if isinstance(v, list):
                            multiple = True
                        else:
                            multiple = False
                        if k in self.__attr_dict_dv_up_typeClass_primitive:
                            typeClass = 'primitive'
                        elif k in self.__attr_dict_dv_up_typeClass_compound:
                            typeClass = 'compound'
                        elif k in self.__attr_dict_dv_up_typeClass_controlledVocabulary:
                            typeClass = 'controlledVocabulary'
                        tmp_dict[k] = {}
                        tmp_dict[k]['typeName'] = k
                        tmp_dict[k]['typeClass'] = typeClass
                        tmp_dict[k]['multiple'] = multiple
                        tmp_dict[k]['value'] = v
                tmp_list.append(tmp_dict)

        return tmp_list

    def to_json(self, format=None, validate=True, filename_schema=None):
        data = {}
        allowed_formats = [
            'dataverse_upload',
            'dspace',
            'custom'
        ]

        if not format:
            format = self.default_validate_format
        if not filename_schema:
            filename_schema = self.default_validate_schema_filename

        if format in allowed_formats:

            if format == 'dataverse_upload':
                data['datasetVersion'] = {}
                data['datasetVersion']['metadataBlocks'] = {}
                citation = {}
                citation['fields'] = []

                data_dict = self.dict()

                """dataset"""
                # Generate first level attributes
                for attr in self.__attr_import_dv_up_datasetVersion_values:
                    if attr in list(data_dict.keys()):
                        data['datasetVersion'][attr] = data_dict[attr]

                """citation"""
                if 'citation_displayName' in list(data_dict.keys()):
                    citation['displayName'] = data_dict['citation_displayName']

                # Generate first level attributes
                for attr in self.__attr_import_dv_up_citation_fields_values:
                    if attr in list(data_dict.keys()):
                        v = data_dict[attr]
                        if isinstance(v, list):
                            multiple = True
                        else:
                            multiple = False
                        if attr in self.__attr_dict_dv_up_typeClass_primitive:
                            typeClass = 'primitive'
                        elif attr in self.__attr_dict_dv_up_typeClass_compound:
                            typeClass = 'compound'
                        elif attr in self.__attr_dict_dv_up_typeClass_controlledVocabulary:
                            typeClass = 'controlledVocabulary'
                        citation['fields'].append({
                            'typeName': attr,
                            'multiple': multiple,
                            'typeClass': typeClass,
                            'value': v
                        })

                # Generate fields attributes
                for key, val in self.__attr_import_dv_up_citation_fields_arrays.items():
                    if key in list(data_dict.keys()):
                        v = data_dict[key]
                        citation['fields'].append({
                            'typeName': key,
                            'multiple': True,
                            'typeClass': 'compound',
                            'value': self.__generate_field_arrays(key, val)
                        })

                # Generate series attributes
                if 'series' in list(data_dict.keys()):
                    series = data_dict['series']
                    tmp_dict = {}
                    if 'seriesName' in series:
                        if series['seriesName'] is not None:
                            tmp_dict['seriesName'] = {}
                            tmp_dict['seriesName']['typeName'] = 'seriesName'
                            tmp_dict['seriesName']['multiple'] = False
                            tmp_dict['seriesName']['typeClass'] = 'primitive'
                            tmp_dict['seriesName']['value'] = series['seriesName']
                    if 'seriesInformation' in series:
                        if series['seriesInformation'] is not None:
                            tmp_dict['seriesInformation'] = {}
                            tmp_dict['seriesInformation']['typeName'] = 'seriesInformation'
                            tmp_dict['seriesInformation']['multiple'] = False
                            tmp_dict['seriesInformation']['typeClass'] = 'primitive'
                            tmp_dict['seriesInformation']['value'] = series['seriesInformation']
                    citation['fields'].append({
                        'typeName': 'series',
                        'multiple': False,
                        'typeClass': 'compound',
                        'value': tmp_dict
                    })

                """geospatial"""
                for attr in self.__attr_import_dv_up_geospatial_fields_values + list(self.__attr_import_dv_up_geospatial_fields_arrays.keys()) + ['geospatial_displayName']:
                    if attr in list(data_dict.keys()):
                        geospatial = {}
                        if not attr == 'geospatial_displayName':
                            geospatial['fields'] = []

                if 'geospatial_displayName' in list(data_dict.keys()):
                    if 'geospatial' not in locals():
                        geospatial = {}
                    geospatial['displayName'] = self.geospatial_displayName

                # Generate first level attributes
                for attr in self.__attr_import_dv_up_geospatial_fields_values:
                    if attr in list(data_dict.keys()):
                        v = data_dict[attr]
                        if isinstance(v, list):
                            multiple = True
                        else:
                            multiple = False
                        if attr in self.__attr_dict_dv_up_typeClass_primitive:
                            typeClass = 'primitive'
                        elif attr in self.__attr_dict_dv_up_typeClass_compound:
                            typeClass = 'compound'
                        elif attr in self.__attr_dict_dv_up_typeClass_controlledVocabulary:
                            typeClass = 'controlledVocabulary'
                        geospatial['fields'].append({
                            'typeName': attr,
                            'multiple': multiple,
                            'typeClass': typeClass,
                            'value': v
                        })

                # Generate fields attributes
                for key, val in self.__attr_import_dv_up_geospatial_fields_arrays.items():
                    if key in list(data_dict.keys()):
                        geospatial['fields'].append({
                            'typeName': key,
                            'multiple': True,
                            'typeClass': 'compound',
                            'value': self.__generate_field_arrays(key, val)
                        })

                """socialscience"""
                for attr in self.__attr_import_dv_up_socialscience_fields_values + ['socialscience_displayName']:
                    if attr in list(data_dict.keys()):
                        socialscience = {}
                        if not attr == 'socialscience_displayName':
                            socialscience['fields'] = []

                if 'socialscience_displayName' in list(data_dict.keys()):
                    if 'socialscience' not in locals():
                        socialscience = {}
                    socialscience['displayName'] = self.socialscience_displayName

                # Generate first level attributes
                for attr in self.__attr_import_dv_up_socialscience_fields_values:
                    if attr in list(data_dict.keys()):
                        v = data_dict[attr]
                        if isinstance(v, list):
                            multiple = True
                        else:
                            multiple = False
                        if attr in self.__attr_dict_dv_up_typeClass_primitive:
                            typeClass = 'primitive'
                        elif attr in self.__attr_dict_dv_up_typeClass_compound:
                            typeClass = 'compound'
                        elif attr in self.__attr_dict_dv_up_typeClass_controlledVocabulary:
                            typeClass = 'controlledVocabulary'
                        socialscience['fields'].append({
                            'typeName': attr,
                            'multiple': multiple,
                            'typeClass': typeClass,
                            'value': v
                        })

                # Generate targetSampleSize attributes
                if 'targetSampleSize' in list(data_dict.keys()):
                    target_sample_size = data_dict['targetSampleSize']
                    tmp_dict = {}
                    if 'targetSampleActualSize' in target_sample_size:
                        if target_sample_size['targetSampleActualSize'] is not None:
                            tmp_dict['targetSampleActualSize'] = {}
                            tmp_dict['targetSampleActualSize']['typeName'] = 'targetSampleActualSize'
                            tmp_dict['targetSampleActualSize']['multiple'] = False
                            tmp_dict['targetSampleActualSize']['typeClass'] = 'primitive'
                            tmp_dict['targetSampleActualSize']['value'] = target_sample_size['targetSampleActualSize']
                    if 'targetSampleSizeFormula' in target_sample_size:
                        if target_sample_size['targetSampleSizeFormula'] is not None:
                            tmp_dict['targetSampleSizeFormula'] = {}
                            tmp_dict['targetSampleSizeFormula']['typeName'] = 'targetSampleSizeFormula'
                            tmp_dict['targetSampleSizeFormula']['multiple'] = False
                            tmp_dict['targetSampleSizeFormula']['typeClass'] = 'primitive'
                            tmp_dict['targetSampleSizeFormula']['value'] = target_sample_size['targetSampleSizeFormula']
                    socialscience['fields'].append({
                        'typeName': 'targetSampleSize',
                        'multiple': False,
                        'typeClass': 'compound',
                        'value': tmp_dict
                    })

                # Generate socialScienceNotes attributes
                if 'socialScienceNotes' in list(data_dict.keys()):
                    social_science_notes = data_dict['socialScienceNotes']
                    tmp_dict = {}
                    if 'socialScienceNotesType' in social_science_notes:
                        if social_science_notes['socialScienceNotesType'] is not None:
                            tmp_dict['socialScienceNotesType'] = {}
                            tmp_dict['socialScienceNotesType']['typeName'] = 'socialScienceNotesType'
                            tmp_dict['socialScienceNotesType']['multiple'] = False
                            tmp_dict['socialScienceNotesType']['typeClass'] = 'primitive'
                            tmp_dict['socialScienceNotesType']['value'] = social_science_notes['socialScienceNotesType']
                    if 'socialScienceNotesSubject' in social_science_notes:
                        if social_science_notes['socialScienceNotesSubject'] is not None:
                            tmp_dict['socialScienceNotesSubject'] = {}
                            tmp_dict['socialScienceNotesSubject']['typeName'] = 'socialScienceNotesSubject'
                            tmp_dict['socialScienceNotesSubject']['multiple'] = False
                            tmp_dict['socialScienceNotesSubject']['typeClass'] = 'primitive'
                            tmp_dict['socialScienceNotesSubject']['value'] = social_science_notes['socialScienceNotesSubject']
                    if 'socialScienceNotesText' in social_science_notes:
                        if social_science_notes['socialScienceNotesText'] is not None:
                            tmp_dict['socialScienceNotesText'] = {}
                            tmp_dict['socialScienceNotesText']['typeName'] = 'socialScienceNotesText'
                            tmp_dict['socialScienceNotesText']['multiple'] = False
                            tmp_dict['socialScienceNotesText']['typeClass'] = 'primitive'
                            tmp_dict['socialScienceNotesText']['value'] = social_science_notes['socialScienceNotesText']
                    socialscience['fields'].append({
                        'typeName': 'socialScienceNotes',
                        'multiple': False,
                        'typeClass': 'compound',
                        'value': tmp_dict
                    })

                """journal"""
                for attr in self.__attr_import_dv_up_journal_fields_values + list(self.__attr_import_dv_up_journal_fields_arrays.keys()) + ['journal_displayName']:
                    if attr in list(data_dict.keys()):
                        journal = {}
                        if not attr == 'journal_displayName':
                            journal['fields'] = []

                if 'journal_displayName' in list(data_dict.keys()):
                    journal['displayName'] = self.journal_displayName

                # Generate first level attributes
                for attr in self.__attr_import_dv_up_journal_fields_values:
                    if attr in list(data_dict.keys()):
                        v = data_dict[attr]
                        if isinstance(v, list):
                            multiple = True
                        else:
                            multiple = False
                        if attr in self.__attr_dict_dv_up_typeClass_primitive:
                            typeClass = 'primitive'
                        elif attr in self.__attr_dict_dv_up_typeClass_compound:
                            typeClass = 'compound'
                        elif attr in self.__attr_dict_dv_up_typeClass_controlledVocabulary:
                            typeClass = 'controlledVocabulary'
                        journal['fields'].append({
                            'typeName': attr,
                            'multiple': multiple,
                            'typeClass': typeClass,
                            'value': v
                        })

                # Generate fields attributes
                for key, val in self.__attr_import_dv_up_journal_fields_arrays.items():
                    if key in list(data_dict.keys()):
                        journal['fields'].append({
                            'typeName': key,
                            'multiple': True,
                            'typeClass': 'compound',
                            'value': self.__generate_field_arrays(key, val)
                        })

                # TODO: prüfen, ob required attributes gesetzt sind. wenn nicht = Exception!
                data['datasetVersion']['metadataBlocks']['citation'] = citation
                if 'socialscience' in locals():
                    data['datasetVersion']['metadataBlocks']['socialscience'] = socialscience
                if 'geospatial' in locals():
                    data['datasetVersion']['metadataBlocks']['geospatial'] = geospatial
                if 'journal' in locals():
                    data['datasetVersion']['metadataBlocks']['journal'] = journal

                if validate:
                    validate_data(data, filename_schema)

                return json.dumps(data, indent=2)
            elif format == 'dspace':
                pass
            else:
                print('WARNING: dict can not be created. Format is not valid.')
                return None


class Datafile(DVObject):
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
        List with valid metadata for Dataverse API upload.
    __attr_valid_class : list
        List of all attributes.
    pid
    filename

    """

    def __init__(self):
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

        super().__init__()
        self.default_validate_schema_filename = 'schemas/json/datafile_upload_schema.json'

        """Attributes to be imported from `dv_up` file."""
        self.attr_dv_up_values = [
            'description',
            'categories',
            'restrict',
            'title',
            'directoryLabel',
            'pid',
            'filename'
        ]

    def __str__(self):
        """Return name of Datafile() class for users."""
        return 'pyDataverse Datafile() model class.'
