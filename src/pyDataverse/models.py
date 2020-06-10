# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse data-types data model."""
from __future__ import absolute_import
import json
from pyDataverse.utils import read_json
from pyDataverse.utils import validate_data
from pyDataverse.utils import write_json

"""
Classes to work with data and metadata of Dataverses, Datasets and Datafiles.
"""


class DVObject(object):
    """Base class for the Dataverse data types `Dataverse`, `Dataset` and
    `Datafile`.

    Attributes
    ----------
    default_validate_format : string
        Default format to be validated against in :func:`from_json()` and
        :func:`to_json()`.

    """

    def __init__(self):
        """Init :class:`DVObject()`."""
        self.default_validate_format = 'dataverse_upload'
        self.attr_dv_up_values = None

    def __str__(self):
        """Return name of class :class:`DVObject()` for users."""
        return 'pyDataverse DVObject() model class.'

    def set(self, data):
        """Set class attributes by a flat :class:`dict`.

        The flat dict is the main way to set the class attributes.
        It is the main interface between the object and the outside world.

        Parameters
        ----------
        data : dict
            Flat :class:`dict`. All keys will be mapped to a similar
            named attribute and it's value.

        Returns
        -------
        bool
            `True` if all attributes are set, `False` if wrong data type was
            passed.

        """
        if isinstance(data, dict):
            for key, val in data.items():
                self.__setattr__(key, val)
            return True
        else:
            return False

    def dict(self):
        """Create flat :class:`dict` of all attributes.

        Creates :class:`dict` with all attributes in a flat structure.
        The flat :class:`dict` can then be used for further processing.

        Returns
        -------
        dict
            Data in a flat data structure.

        """
        data = {}

        for attr in list(self.__dict__.keys()):
            data[attr] = self.__getattribute__(attr)
        return data

    def validate_json(self, format=None, filename_schema=None):
        """Validate JSON formats.

        Check if JSON data structure is valid.

        Parameters
        ----------
        format : string
            Data formats to be validated. See `allowed_formats`.
        filename_schema : string
            Filename of JSON schema with full path.

        Returns
        -------
        bool
            `True` if JSON validate correctly, `False` if not.

        """

        """List of allowed JSON formats to be validated."""
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

        data_json = self.to_json(format=format, validate=False)
        if data_json:
            is_valid = validate_data(json.loads(data_json), filename_schema, format='json')
            if is_valid:
                return True
            else:
                return False
        else:
            return False

    def from_json(self, filename, format=None, validate=True,
                  filename_schema=None):
        """Import metadata from JSON file.

        Parses in the metadata from different JSON formats.

        Parameters
        ----------
        filename : string
            Filename of JSON file with full path.
        format : string
            Data formats available for import. See `allowed_formats`.
        validate : bool
            `True`, if imported JSON should be validated against a JSON
            schema file. `False`, if JSON string should be imported directly and
            not checked if valid.
        filename_schema : string
            Filename of JSON schema with full path.

        Returns
        -------
        bool
            `True` if JSON imported correctly, `False` if not.

        """
        data = {}

        """List of allowed JSON data formats to be imported."""
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
                        print('INFO: Attribute {0} not valid for import (format=`{1}`).'.format(key, format))
                self.set(data)
                return True
            elif format == 'dataverse_download':
                print('INFO: Not implemented yet.')
                return True
            elif format == 'dspace':
                print('INFO: Not implemented yet.')
                return True
            elif format == 'custom':
                print('INFO: Not implemented yet.')
                return True
        else:
            # TODO: Exception
            print('WARNING: Data-format not right.')
            return False

    def to_json(self, format=None, validate=True, filename_schema=None,
                as_dict=False):
        r"""Create JSON from attributes.

        Parameters
        ----------
        format : string
            Data formats to be validated. See `allowed_formats`.
        validate : bool
            `True`, if created JSON should be validated against a JSON schema
            file. `False`, if JSON string should be created and not checked if
            valid.
        filename_schema : string
            Filename of JSON schema with full path.
        as_dict : bool
            `True`, if the data should be returned as dict, `False` if as a JSON
            string.

        Returns
        -------
        dict
            The data as a JSON string. If as_dict=True, the data will be
            converted into a dict.

        """
        data = {}

        """List of allowed JSON formats to be exported."""
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
                data = None
                print('INFO: Not implemented yet.')
            elif format == 'custom':
                data = None
                print('INFO: Not implemented yet.')
            if validate:
                validate_data(data, filename_schema)
            if as_dict:
                return data
            else:
                return json.dumps(data, indent=2)
        else:
            return None


class Dataverse(DVObject):
    """Base class for the Dataverse data type `Dataverse`."""

    def __init__(self):
        """Init :class:`Dataverse()`.

        Inherits attributes from parent :class:`DVObject()`

        Examples
        -------
        Create a Dataverse::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()
            >>> print(dv.default_validate_schema_filename)
            'schemas/json/dataverse_upload_schema.json'

        """
        super().__init__()
        self.default_validate_schema_filename = 'schemas/json/dataverse_upload_schema.json'

        """List of attributes to be imported or exported for `dataverse_upload`
        JSON format."""
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
    """Base class for the Dataverse data type `Dataset`."""

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
        Create a Dataset::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> print(ds.default_validate_schema_filename)
            'schemas/json/dataset_upload_default_schema.json'

        """
        super().__init__()
        self.default_validate_schema_filename = 'schemas/json/dataset_upload_default_schema.json'

    def __str__(self):
        """Return name of Dataset() class for users."""
        return 'pyDataverse Dataset() model class.'

    def from_json(self, filename, format=None, validate=True,
                  filename_schema=None):
        """Import Dataset metadata from JSON file.

        Parses in the metadata of a Dataset from different JSON formats.

        Parameters
        ----------
        filename : string
            Filename of JSON file with full path.
        format : string
            Data formats available for import. See `allowed_formats`.
        validate : bool
            `True`, if imported JSON should be validated against a JSON
            schema file. `False`, if JSON string should be imported directly and
            not checked if valid.
        filename_schema : string
            Filename of JSON schema with full path.

        Examples
        -------
        Set Dataverse attributes via flat :class:`dict`::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> ds.from_json('tests/data/dataset_upload_min_default.json')
            >>> ds.title
            'Darwin's Finches'

        """
        data = {}
        """List of allowed JSON data formats to be imported."""
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
                dict_json = read_json(filename)
                if validate:
                    validate_data(dict_json, filename_schema, format='json')
                """dataset"""
                # get first level metadata and parse it automatically
                for key, val in dict_json['datasetVersion'].items():
                    if not key == 'metadataBlocks':
                        if key in self.__attr_import_dv_up_datasetVersion_values:
                            data[key] = val
                        else:
                            print('Attribute {0} not valid for import (dv_up).'.format(key))

                if 'metadataBlocks' in dict_json['datasetVersion']:

                    """citation"""
                    if 'citation' in dict_json['datasetVersion']['metadataBlocks']:
                        citation = dict_json['datasetVersion']['metadataBlocks']['citation']
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
                    if 'geospatial' in dict_json['datasetVersion']['metadataBlocks']:
                        geospatial = dict_json['datasetVersion']['metadataBlocks']['geospatial']
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
                    if 'socialscience' in dict_json['datasetVersion']['metadataBlocks']:
                        socialscience = dict_json['datasetVersion']['metadataBlocks']['socialscience']

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
                    if 'journal' in dict_json['datasetVersion']['metadataBlocks']:
                        journal = dict_json['datasetVersion']['metadataBlocks']['journal']

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
            elif format == 'dataverse_download':
                print('INFO: Not implemented yet.')
                return True
            elif format == 'dspace':
                print('INFO: Not implemented yet.')
                return True
            elif format == 'custom':
                print('INFO: Not implemented yet.')
                return True
        else:
            # TODO: Exception
            print('WARNING: Data-format not right.')
            return False

    def __parse_field_array(self, data, attr_list):
        """Parse arrays of Dataset upload format.

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

    def validate_json(self, format=None, filename_schema=None):
        """Validate JSON formats of Dataset.

        Check if JSON data structure is valid.

        Parameters
        ----------
        format : string
            Data formats to be validated. See `allowed_formats`.
        filename_schema : string
            Filename of JSON schema with full path.

        Returns
        -------
        bool
            `True` if JSON validate correctly, `False` if not.

        Examples
        -------
        Check if JSON is valid for Dataverse API upload::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> data = {
            >>>     'title': 'pyDataverse study 2019',
            >>>     'dsDescription': [
            >>>         {'dsDescriptionValue': 'New study about pyDataverse usage in 2019'}
            >>>     ]
            >>> }
            >>> ds.set(data)
            >>> print(ds.validate_json())
            False
            >>> ds.author = [{'authorName': 'LastAuthor1, FirstAuthor1'}]
            >>> ds.datasetContact = [{'datasetContactName': 'LastContact1, FirstContact1'}]
            >>> ds.subject = ['Engineering']
            >>> print(ds.validate_json())
            True

        """
        is_valid = True
        if not format:
            format = self.default_validate_format
        if not filename_schema:
            filename_schema = self.default_validate_schema_filename

        data_json = self.to_json(format=format, validate=False)
        if data_json:
            is_valid = validate_data(json.loads(data_json), filename_schema, format='json')
            if not is_valid:
                return False
        else:
            return False

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

    def to_json(self, format=None, validate=True, filename_schema=None,
                as_dict=False):
        """Create Dataset JSON from attributes.

        Parameters
        ----------
        format : string
            Data formats to be validated. See `allowed_formats`.
        validate : bool
            `True`, if created JSON should be validated against a JSON schema
            file. `False`, if JSON string should be created and not checked if
            valid.
        filename_schema : string
            Filename of JSON schema with full path.
        as_dict : bool
            `True`, if the data should be returned as dict, `False` if as a JSON
            string.

        Returns
        -------
        dict
            The data as a JSON string. If as_dict=True, the data will be
            converted into a dict.

        """
        data = {}
        """List of allowed JSON formats to be exported."""
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
                            break

                if 'geospatial_displayName' in list(data_dict.keys()):
                    geospatial['displayName'] = data_dict['geospatial_displayName']

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
                            break

                if 'socialscience_displayName' in list(data_dict.keys()):
                    socialscience['displayName'] = data_dict['socialscience_displayName']

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
                            break

                if 'journal_displayName' in list(data_dict.keys()):
                    journal['displayName'] = data_dict['journal_displayName']

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

                data['datasetVersion']['metadataBlocks']['citation'] = citation
                if 'socialscience' in locals():
                    data['datasetVersion']['metadataBlocks']['socialscience'] = socialscience
                if 'geospatial' in locals():
                    data['datasetVersion']['metadataBlocks']['geospatial'] = geospatial
                if 'journal' in locals():
                    data['datasetVersion']['metadataBlocks']['journal'] = journal
            elif format == 'dspace':
                data = None
                print('INFO: Not implemented yet.')
            elif format == 'custom':
                data = None
                print('INFO: Not implemented yet.')
            if validate:
                validate_data(data, filename_schema)
            if as_dict:
                return data
            else:
                return json.dumps(data, indent=2)
        else:
            return None


class Datafile(DVObject):
    """Base class for the Dataverse data type `Datafile`."""

    def __init__(self):
        """Init :class:`Datafile()`.

        Inherits attributes from parent :class:`DVObject()`

        Examples
        -------
        Create a Datafile::

            >>> from pyDataverse.models import Datafile
            >>> df = Datafile()
            >>> print(df.default_validate_schema_filename)
            'schemas/json/datafile_upload_schema.json'

        """

        super().__init__()
        self.default_validate_schema_filename = 'schemas/json/datafile_upload_schema.json'

        """List of attributes to be imported or exported for `dataverse_upload`
        JSON format."""
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
