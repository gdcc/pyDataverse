"""Dataverse data-types data model."""

from __future__ import absolute_import

import json
import os

from pyDataverse.utils import validate_data


INTERNAL_ATTRIBUTES = [
    "_default_json_format",
    "_default_json_schema_filename",
    "_allowed_json_formats",
    "_json_dataverse_upload_attr",
    "_internal_attributes",
]


class DVObject:
    """Base class for the Dataverse data types `Dataverse`, `Dataset` and `Datafile`."""

    def __init__(self, data=None):
        """Init :class:`DVObject`.

        Parameters
        ----------
        data : dict
            Flat dictionary. All keys will be mapped to a similar
            named attribute and it's value.
        """
        if data is not None:
            self.set(data)

    def set(self, data):
        """Set class attributes by a flat dictionary.

        The flat dict is the main way to set the class attributes.
        It is the main interface between the object and the outside world.

        Parameters
        ----------
        data : dict
            Flat dictionary. All keys will be mapped to a similar
            named attribute and it's value.

        Returns
        -------
        bool
            `True` if all attributes are set, `False` if wrong data type was
            passed.

        """
        assert isinstance(data, dict)

        for key, val in data.items():
            if key in self._internal_attributes:
                print("Importing attribute {0} not allowed.".format(key))
            else:
                self.__setattr__(key, val)

    def get(self):
        """Create flat `dict` of all attributes.

        Creates :class:`dict` with all attributes in a flat structure.
        The flat :class:`dict` can then be used for further processing.

        Returns
        -------
        dict
            Data in a flat data structure.

        """
        data = {}

        for attr in list(self.__dict__.keys()):
            if attr not in INTERNAL_ATTRIBUTES:
                data[attr] = self.__getattribute__(attr)

        assert isinstance(data, dict)
        return data

    def validate_json(self, filename_schema=None):
        """Validate JSON formats.

        Check if JSON data structure is valid.

        Parameters
        ----------
        filename_schema : str
            Filename of JSON schema with full path.

        Returns
        -------
        bool
            `True` if JSON validates correctly, `False` if not.

        """
        if filename_schema is None:
            filename_schema = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                self._default_json_schema_filename,
            )
        assert isinstance(filename_schema, str)

        return validate_data(
            json.loads(self.json(validate=False)),
            filename_schema,
            file_format="json",
        )

    def from_json(
        self, json_str, data_format=None, validate=True, filename_schema=None
    ):
        """Import metadata from a JSON file.

        Parses in the metadata from different JSON formats.

        Parameters
        ----------
        json_str : str
            JSON string to be imported.
        data_format : str
            Data formats available for import. See `_allowed_json_formats`.
        validate : bool
            `True`, if imported JSON should be validated against a JSON
            schema file. `False`, if JSON string should be imported directly and
            not checked if valid.
        filename_schema : str
            Filename of JSON schema with full path.

        Returns
        -------
        bool
            `True` if JSON imported correctly, `False` if not.

        """
        assert isinstance(json_str, str)
        json_dict = json.loads(json_str)
        assert isinstance(json_dict, dict)
        assert isinstance(validate, bool)
        if data_format is None:
            data_format = self._default_json_format
        assert isinstance(data_format, str)
        assert data_format in self._allowed_json_formats
        if filename_schema is None:
            filename_schema = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                self._default_json_schema_filename,
            )
        assert isinstance(filename_schema, str)

        data = {}

        if data_format == "dataverse_upload":
            if validate:
                validate_data(json_dict, filename_schema)
            # get first level metadata and parse it automatically
            for key in json_dict.keys():
                if key in self._json_dataverse_upload_attr:
                    data[key] = json_dict[key]
                else:
                    print(
                        "INFO: Attribute {0} not valid for import (data format=`{1}`).".format(
                            key, data_format
                        )
                    )
        elif data_format == "dataverse_download":
            print("INFO: Not implemented yet.")
        elif data_format == "dspace":
            print("INFO: Not implemented yet.")
        elif data_format == "custom":
            print("INFO: Not implemented yet.")
        else:
            # TODO: add exception for wrong data format
            pass

        self.set(data)

    def json(self, data_format=None, validate=True, filename_schema=None):
        r"""Create JSON from :class:`DVObject` attributes.

        Parameters
        ----------
        data_format : str
            Data formats to be validated. See `_allowed_json_formats`.
        validate : bool
            `True`, if created JSON should be validated against a JSON schema
            file. `False`, if JSON string should be created and not checked if
            valid.
        filename_schema : str
            Filename of JSON schema with full path.

        Returns
        -------
        str
            The data as a JSON string.
        """
        assert isinstance(validate, bool)
        if data_format is None:
            data_format = self._default_json_format
        assert isinstance(data_format, str)
        assert data_format in self._allowed_json_formats
        if filename_schema is None:
            filename_schema = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                self._default_json_schema_filename,
            )
        assert isinstance(filename_schema, str)

        data = {}

        if data_format == "dataverse_upload":
            for attr in self._json_dataverse_upload_attr:
                # check if attribute exists
                if hasattr(self, attr):
                    data[attr] = self.__getattribute__(attr)
        elif data_format == "dspace":
            print("INFO: Not implemented yet.")
            return False
        elif data_format == "custom":
            print("INFO: Not implemented yet.")
            return False
        if validate:
            validate_data(data, filename_schema)

        json_str = json.dumps(data, indent=2)
        assert isinstance(json_str, str)
        return json_str


class Dataverse(DVObject):
    """Base class for the Dataverse data type `Dataverse`.

    Attributes
    ----------
    _default_json_format : str
        Default JSON data format.
    _default_json_schema_filename : str
        Default JSON schema filename.
    _allowed_json_formats : list
        List of all possible JSON data formats.
    _json_dataverse_upload_attr : list
        List of all attributes to be exported in :func:`json`.
    """

    def __init__(self, data=None):
        """Init :class:`Dataverse()`.

        Inherits attributes from parent :class:`DVObject()`

        Parameters
        ----------
        data : dict
            Flat dictionary. All keys will be mapped to a similar
            named attribute and it's value.

        Examples
        -------
        Create a Dataverse::

            >>> from pyDataverse.models import Dataverse
            >>> dv = Dataverse()
            >>> print(dv._default_json_schema_filename)
            'schemas/json/dataverse_upload_schema.json'

        """
        self._internal_attributes = [
            "_Dataverse" + attr for attr in INTERNAL_ATTRIBUTES
        ]

        super().__init__(data=data)

        self._default_json_format = "dataverse_upload"
        self._default_json_schema_filename = "schemas/json/dataverse_upload_schema.json"
        self._allowed_json_formats = ["dataverse_upload", "dataverse_download"]
        self._json_dataverse_upload_attr = [
            "affiliation",
            "alias",
            "dataverseContacts",
            "dataverseType",
            "description",
            "name",
        ]


class Dataset(DVObject):
    """Base class for the Dataverse data type `Dataset`.

    Attributes
    ----------
    _default_json_format : str
        Default JSON data format.
    _default_json_schema_filename : str
        Default JSON schema filename.
    _allowed_json_formats : list
        List of all possible JSON data formats.
    _json_dataverse_upload_attr : list
        List with all attributes to be exported in :func:`json`.
    __attr_import_dv_up_datasetVersion_values : list
        Dataverse API Upload Dataset JSON attributes inside ds[\'datasetVersion\'].
    __attr_import_dv_up_citation_fields_values : list
        Dataverse API Upload Dataset JSON attributes inside
        ds[\'datasetVersion\'][\'metadataBlocks\'][\'citation\'][\'fields\'].
    __attr_import_dv_up_citation_fields_arrays : dict
        Dataverse API Upload Dataset JSON attributes inside
        [\'datasetVersion\'][\'metadataBlocks\'][\'citation\'][\'fields\'].
    __attr_import_dv_up_geospatial_fields_values : list
        Attributes of Dataverse API Upload Dataset JSON metadata standard inside
        [\'datasetVersion\'][\'metadataBlocks\'][\'geospatial\'][\'fields\'].
    __attr_import_dv_up_geospatial_fields_arrays : dict
        Attributes of Dataverse API Upload Dataset JSON metadata standard inside
        [\'datasetVersion\'][\'metadataBlocks\'][\'geospatial\'][\'fields\'].
    __attr_import_dv_up_socialscience_fields_values : list
        Attributes of Dataverse API Upload Dataset JSON metadata standard inside
        [\'datasetVersion\'][\'metadataBlocks\'][\'socialscience\'][\'fields\'].
    __attr_import_dv_up_journal_fields_values : list
        Attributes of Dataverse API Upload Dataset JSON metadata standard inside
        [\'datasetVersion\'][\'metadataBlocks\'][\'journal\'][\'fields\'].
    __attr_import_dv_up_journal_fields_arrays : dict
        Attributes of Dataverse API Upload Dataset JSON metadata standard inside
        [\'datasetVersion\'][\'metadataBlocks\'][\'journal\'][\'fields\'].
    __attr_dict_dv_up_required :list
        Required attributes for valid `dv_up` metadata dict creation.
    __attr_dict_dv_up_type_class_primitive : list
        typeClass primitive.
    __attr_dict_dv_up_type_class_compound : list
        typeClass compound.
    __attr_dict_dv_up_type_class_controlled_vocabulary : list
        typeClass controlledVocabulary.
    __attr_dict_dv_up_single_dict : list
        This attributes are excluded from automatic parsing in ds.get() creation.
    __attr_displayNames : list
        Attributes of displayName.
    """

    __attr_import_dv_up_datasetVersion_values = [
        "license",
        "termsOfAccess",
        "fileAccessRequest",
        "protocol",
        "authority",
        "identifier",
        "termsOfUse",
    ]
    __attr_import_dv_up_citation_fields_values = [
        "accessToSources",
        "alternativeTitle",
        "alternativeURL",
        "characteristicOfSources",
        "dateOfDeposit",
        "dataSources",
        "depositor",
        "distributionDate",
        "kindOfData",
        "language",
        "notesText",
        "originOfSources",
        "otherReferences",
        "productionDate",
        "productionPlace",
        "relatedDatasets",
        "relatedMaterial",
        "subject",
        "subtitle",
        "title",
    ]
    __attr_import_dv_up_citation_fields_arrays = {
        "author": [
            "authorName",
            "authorAffiliation",
            "authorIdentifierScheme",
            "authorIdentifier",
        ],
        "contributor": ["contributorType", "contributorName"],
        "dateOfCollection": ["dateOfCollectionStart", "dateOfCollectionEnd"],
        "datasetContact": [
            "datasetContactName",
            "datasetContactAffiliation",
            "datasetContactEmail",
        ],
        "distributor": [
            "distributorName",
            "distributorAffiliation",
            "distributorAbbreviation",
            "distributorURL",
            "distributorLogoURL",
        ],
        "dsDescription": ["dsDescriptionValue", "dsDescriptionDate"],
        "grantNumber": ["grantNumberAgency", "grantNumberValue"],
        "keyword": ["keywordValue", "keywordVocabulary", "keywordVocabularyURI"],
        "producer": [
            "producerName",
            "producerAffiliation",
            "producerAbbreviation",
            "producerURL",
            "producerLogoURL",
        ],
        "otherId": ["otherIdAgency", "otherIdValue"],
        "publication": [
            "publicationCitation",
            "publicationIDType",
            "publicationIDNumber",
            "publicationURL",
        ],
        "software": ["softwareName", "softwareVersion"],
        "timePeriodCovered": ["timePeriodCoveredStart", "timePeriodCoveredEnd"],
        "topicClassification": [
            "topicClassValue",
            "topicClassVocab",
            "topicClassVocabURI",
        ],
    }
    __attr_import_dv_up_geospatial_fields_values = ["geographicUnit"]
    __attr_import_dv_up_geospatial_fields_arrays = {
        "geographicBoundingBox": [
            "westLongitude",
            "eastLongitude",
            "northLongitude",
            "southLongitude",
        ],
        "geographicCoverage": ["country", "state", "city", "otherGeographicCoverage"],
    }
    __attr_import_dv_up_socialscience_fields_values = [
        "actionsToMinimizeLoss",
        "cleaningOperations",
        "collectionMode",
        "collectorTraining",
        "controlOperations",
        "dataCollectionSituation",
        "dataCollector",
        "datasetLevelErrorNotes",
        "deviationsFromSampleDesign",
        "frequencyOfDataCollection",
        "otherDataAppraisal",
        "researchInstrument",
        "responseRate",
        "samplingErrorEstimates",
        "samplingProcedure",
        "unitOfAnalysis",
        "universe",
        "timeMethod",
        "weighting",
    ]
    __attr_import_dv_up_journal_fields_values = ["journalArticleType"]
    __attr_import_dv_up_journal_fields_arrays = {
        "journalVolumeIssue": ["journalVolume", "journalIssue", "journalPubDate"]
    }
    __attr_dict_dv_up_required = [
        "author",
        "datasetContact",
        "dsDescription",
        "subject",
        "title",
    ]
    __attr_dict_dv_up_type_class_primitive = (
        [
            "accessToSources",
            "alternativeTitle",
            "alternativeURL",
            "authorAffiliation",
            "authorIdentifier",
            "authorName",
            "characteristicOfSources",
            "city",
            "contributorName",
            "dateOfDeposit",
            "dataSources",
            "depositor",
            "distributionDate",
            "kindOfData",
            "notesText",
            "originOfSources",
            "otherGeographicCoverage",
            "otherReferences",
            "productionDate",
            "productionPlace",
            "publicationCitation",
            "publicationIDNumber",
            "publicationURL",
            "relatedDatasets",
            "relatedMaterial",
            "seriesInformation",
            "seriesName",
            "state",
            "subtitle",
            "title",
        ]
        + __attr_import_dv_up_citation_fields_arrays["dateOfCollection"]
        + __attr_import_dv_up_citation_fields_arrays["datasetContact"]
        + __attr_import_dv_up_citation_fields_arrays["distributor"]
        + __attr_import_dv_up_citation_fields_arrays["dsDescription"]
        + __attr_import_dv_up_citation_fields_arrays["grantNumber"]
        + __attr_import_dv_up_citation_fields_arrays["keyword"]
        + __attr_import_dv_up_citation_fields_arrays["producer"]
        + __attr_import_dv_up_citation_fields_arrays["otherId"]
        + __attr_import_dv_up_citation_fields_arrays["software"]
        + __attr_import_dv_up_citation_fields_arrays["timePeriodCovered"]
        + __attr_import_dv_up_citation_fields_arrays["topicClassification"]
        + __attr_import_dv_up_geospatial_fields_values
        + __attr_import_dv_up_geospatial_fields_arrays["geographicBoundingBox"]
        + __attr_import_dv_up_socialscience_fields_values
        + __attr_import_dv_up_journal_fields_arrays["journalVolumeIssue"]
        + [
            "socialScienceNotesType",
            "socialScienceNotesSubject",
            "socialScienceNotesText",
        ]
        + ["targetSampleActualSize", "targetSampleSizeFormula"]
    )
    __attr_dict_dv_up_type_class_compound = (
        list(__attr_import_dv_up_citation_fields_arrays.keys())
        + list(__attr_import_dv_up_geospatial_fields_arrays.keys())
        + list(__attr_import_dv_up_journal_fields_arrays.keys())
        + ["series", "socialScienceNotes", "targetSampleSize"]
    )
    __attr_dict_dv_up_type_class_controlled_vocabulary = [
        "authorIdentifierScheme",
        "contributorType",
        "country",
        "journalArticleType",
        "language",
        "publicationIDType",
        "subject",
    ]
    __attr_dict_dv_up_single_dict = ["series", "socialScienceNotes", "targetSampleSize"]
    __attr_displayNames = [
        "citation_displayName",
        "geospatial_displayName",
        "socialscience_displayName",
        "journal_displayName",
    ]

    def __init__(self, data=None):
        """Init a Dataset() class.

        Parameters
        ----------
        data : dict
            Flat dictionary. All keys will be mapped to a similar
            named attribute and it's value.

        Examples
        -------
        Create a Dataset::

            >>> from pyDataverse.models import Dataset
            >>> ds = Dataset()
            >>> print(ds._default_json_schema_filename)
            'schemas/json/dataset_upload_default_schema.json'

        """
        self._internal_attributes = ["_Dataset" + attr for attr in INTERNAL_ATTRIBUTES]

        super().__init__(data=data)

        self._default_json_format = "dataverse_upload"
        self._default_json_schema_filename = (
            "schemas/json/dataset_upload_default_schema.json"
        )
        self._allowed_json_formats = [
            "dataverse_upload",
            "dataverse_download",
            "dspace",
            "custom",
        ]
        self._json_dataverse_upload_attr = [
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

    def validate_json(self, filename_schema=None):
        """Validate JSON formats of Dataset.

        Check if JSON data structure is valid.

        Parameters
        ----------
        filename_schema : str
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
        if filename_schema is None:
            filename_schema = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                self._default_json_schema_filename,
            )
        assert isinstance(filename_schema, str)

        is_valid = True

        data_json = self.json(validate=False)
        if data_json:
            is_valid = validate_data(
                json.loads(data_json), filename_schema, file_format="json"
            )
            if not is_valid:
                return False
        else:
            return False

        # check if all required attributes are set
        for attr in self.__attr_dict_dv_up_required:
            if attr in list(self.__dict__.keys()):
                if not self.__getattribute__(attr):
                    is_valid = False
                    print("Attribute '{0}' is `False`.".format(attr))
            else:
                is_valid = False
                print("Attribute '{0}' missing.".format(attr))

        # check if attributes set are complete where necessary
        if "timePeriodCovered" in list(self.__dict__.keys()):
            tp_cov = self.__getattribute__("timePeriodCovered")
            if tp_cov:
                for tp in tp_cov:
                    if "timePeriodCoveredStart" in tp or "timePeriodCoveredEnd" in tp:
                        if not (
                            "timePeriodCoveredStart" in tp
                            and "timePeriodCoveredEnd" in tp
                        ):
                            is_valid = False
                            print("timePeriodCovered attribute missing.")

        if "dateOfCollection" in list(self.__dict__.keys()):
            d_coll = self.__getattribute__("dateOfCollection")
            if d_coll:
                for d in d_coll:
                    if "dateOfCollectionStart" in d or "dateOfCollectionEnd" in d:
                        if not (
                            "dateOfCollectionStart" in d and "dateOfCollectionEnd" in d
                        ):
                            is_valid = False
                            print("dateOfCollection attribute missing.")

        if "author" in list(self.__dict__.keys()):
            authors = self.__getattribute__("author")
            if authors:
                for a in authors:
                    if (
                        "authorAffiliation" in a
                        or "authorIdentifierScheme" in a
                        or "authorIdentifier" in a
                    ):
                        if "authorName" not in a:
                            is_valid = False
                            print("author attribute missing.")

        if "datasetContact" in list(self.__dict__.keys()):
            ds_contac = self.__getattribute__("datasetContact")
            if ds_contac:
                for c in ds_contac:
                    if "datasetContactAffiliation" in c or "datasetContactEmail" in c:
                        if "datasetContactName" not in c:
                            is_valid = False
                            print("datasetContact attribute missing.")

        if "producer" in list(self.__dict__.keys()):
            producer = self.__getattribute__("producer")
            if producer:
                for p in producer:
                    if (
                        "producerAffiliation" in p
                        or "producerAbbreviation" in p
                        or "producerURL" in p
                        or "producerLogoURL" in p
                    ):
                        if not p["producerName"]:
                            is_valid = False
                            print("producer attribute missing.")

        if "contributor" in list(self.__dict__.keys()):
            contributor = self.__getattribute__("contributor")
            if contributor:
                for c in contributor:
                    if "contributorType" in c:
                        if "contributorName" not in c:
                            is_valid = False
                            print("contributor attribute missing.")

        if "distributor" in list(self.__dict__.keys()):
            distributor = self.__getattribute__("distributor")
            if distributor:
                for d in distributor:
                    if (
                        "distributorAffiliation" in d
                        or "distributorAbbreviation" in d
                        or "distributorURL" in d
                        or "distributorLogoURL" in d
                    ):
                        if "distributorName" not in d:
                            is_valid = False
                            print("distributor attribute missing.")

        if "geographicBoundingBox" in list(self.__dict__.keys()):
            bbox = self.__getattribute__("geographicBoundingBox")
            if bbox:
                for b in bbox:
                    if b:
                        if not (
                            "westLongitude" in b
                            and "eastLongitude" in b
                            and "northLongitude" in b
                            and "southLongitude" in b
                        ):
                            is_valid = False
                            print("geographicBoundingBox attribute missing.")

        assert isinstance(is_valid, bool)
        return is_valid

    def from_json(
        self, json_str, data_format=None, validate=True, filename_schema=None
    ):
        """Import Dataset metadata from JSON file.

        Parses in the metadata of a Dataset from different JSON formats.

        Parameters
        ----------
        json_str : str
            JSON string to be imported.
        data_format : str
            Data formats available for import. See `_allowed_json_formats`.
        validate : bool
            `True`, if imported JSON should be validated against a JSON
            schema file. `False`, if JSON string should be imported directly and
            not checked if valid.
        filename_schema : str
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
        assert isinstance(json_str, str)
        json_dict = json.loads(json_str)
        assert isinstance(json_dict, dict)
        assert isinstance(validate, bool)
        if data_format is None:
            data_format = self._default_json_format
        assert isinstance(data_format, str)
        assert data_format in self._allowed_json_formats
        if filename_schema is None:
            filename_schema = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                self._default_json_schema_filename,
            )
        assert isinstance(filename_schema, str)

        data = {}

        if data_format == "dataverse_upload":
            if validate:
                validate_data(json_dict, filename_schema, file_format="json")
            # dataset
            # get first level metadata and parse it automatically
            for key, val in json_dict["datasetVersion"].items():
                if not key == "metadataBlocks":
                    if key in self.__attr_import_dv_up_datasetVersion_values:
                        data[key] = val
                    else:
                        print(
                            "Attribute {0} not valid for import (format={1}).".format(
                                key, data_format
                            )
                        )

            if "metadataBlocks" in json_dict["datasetVersion"]:
                # citation
                if "citation" in json_dict["datasetVersion"]["metadataBlocks"]:
                    citation = json_dict["datasetVersion"]["metadataBlocks"]["citation"]
                    if "displayName" in citation:
                        data["citation_displayName"] = citation["displayName"]

                    for field in citation["fields"]:
                        if (
                            field["typeName"]
                            in self.__attr_import_dv_up_citation_fields_values
                        ):
                            data[field["typeName"]] = field["value"]
                        elif (
                            field["typeName"]
                            in self.__attr_import_dv_up_citation_fields_arrays
                        ):
                            data[field["typeName"]] = self.__parse_field_array(
                                field["value"],
                                self.__attr_import_dv_up_citation_fields_arrays[
                                    field["typeName"]
                                ],
                            )
                        elif field["typeName"] == "series":
                            data["series"] = {}
                            if "seriesName" in field["value"]:
                                data["series"]["seriesName"] = field["value"][
                                    "seriesName"
                                ]["value"]
                            if "seriesInformation" in field["value"]:
                                data["series"]["seriesInformation"] = field["value"][
                                    "seriesInformation"
                                ]["value"]
                        else:
                            print(
                                "Attribute {0} not valid for import (dv_up).".format(
                                    field["typeName"]
                                )
                            )
                else:
                    # TODO: Exception
                    pass

                # geospatial
                if "geospatial" in json_dict["datasetVersion"]["metadataBlocks"]:
                    geospatial = json_dict["datasetVersion"]["metadataBlocks"][
                        "geospatial"
                    ]
                    if "displayName" in geospatial:
                        self.__setattr__(
                            "geospatial_displayName", geospatial["displayName"]
                        )

                    for field in geospatial["fields"]:
                        if (
                            field["typeName"]
                            in self.__attr_import_dv_up_geospatial_fields_values
                        ):
                            data[field["typeName"]] = field["value"]
                        elif (
                            field["typeName"]
                            in self.__attr_import_dv_up_geospatial_fields_arrays
                        ):
                            data[field["typeName"]] = self.__parse_field_array(
                                field["value"],
                                self.__attr_import_dv_up_geospatial_fields_arrays[
                                    field["typeName"]
                                ],
                            )
                        else:
                            print(
                                "Attribute {0} not valid for import (dv_up).".format(
                                    field["typeName"]
                                )
                            )
                else:
                    # TODO: Exception
                    pass

                # socialscience
                if "socialscience" in json_dict["datasetVersion"]["metadataBlocks"]:
                    socialscience = json_dict["datasetVersion"]["metadataBlocks"][
                        "socialscience"
                    ]

                    if "displayName" in socialscience:
                        self.__setattr__(
                            "socialscience_displayName",
                            socialscience["displayName"],
                        )

                    for field in socialscience["fields"]:
                        if (
                            field["typeName"]
                            in self.__attr_import_dv_up_socialscience_fields_values
                        ):
                            data[field["typeName"]] = field["value"]
                        elif field["typeName"] == "targetSampleSize":
                            data["targetSampleSize"] = {}
                            if "targetSampleActualSize" in field["value"]:
                                data["targetSampleSize"]["targetSampleActualSize"] = (
                                    field["value"]["targetSampleActualSize"]["value"]
                                )
                            if "targetSampleSizeFormula" in field["value"]:
                                data["targetSampleSize"]["targetSampleSizeFormula"] = (
                                    field["value"]["targetSampleSizeFormula"]["value"]
                                )
                        elif field["typeName"] == "socialScienceNotes":
                            data["socialScienceNotes"] = {}
                            if "socialScienceNotesType" in field["value"]:
                                data["socialScienceNotes"]["socialScienceNotesType"] = (
                                    field["value"]["socialScienceNotesType"]["value"]
                                )
                            if "socialScienceNotesSubject" in field["value"]:
                                data["socialScienceNotes"][
                                    "socialScienceNotesSubject"
                                ] = field["value"]["socialScienceNotesSubject"]["value"]
                            if "socialScienceNotesText" in field["value"]:
                                data["socialScienceNotes"]["socialScienceNotesText"] = (
                                    field["value"]["socialScienceNotesText"]["value"]
                                )
                        else:
                            print(
                                "Attribute {0} not valid for import (dv_up).".format(
                                    field["typeName"]
                                )
                            )
                else:
                    # TODO: Exception
                    pass

                # journal
                if "journal" in json_dict["datasetVersion"]["metadataBlocks"]:
                    journal = json_dict["datasetVersion"]["metadataBlocks"]["journal"]

                    if "displayName" in journal:
                        self.__setattr__("journal_displayName", journal["displayName"])

                    for field in journal["fields"]:
                        if (
                            field["typeName"]
                            in self.__attr_import_dv_up_journal_fields_values
                        ):
                            data[field["typeName"]] = field["value"]
                        elif (
                            field["typeName"]
                            in self.__attr_import_dv_up_journal_fields_arrays
                        ):
                            data[field["typeName"]] = self.__parse_field_array(
                                field["value"],
                                self.__attr_import_dv_up_journal_fields_arrays[
                                    field["typeName"]
                                ],
                            )
                        else:
                            print(
                                "Attribute {0} not valid for import (dv_up).".format(
                                    field["typeName"]
                                )
                            )
                else:
                    # TODO: Exception
                    pass
        elif data_format == "dataverse_download":
            print("INFO: Not implemented yet.")
        elif data_format == "dspace":
            print("INFO: Not implemented yet.")
        elif data_format == "custom":
            print("INFO: Not implemented yet.")
        self.set(data)

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
        assert isinstance(data, list)
        assert isinstance(attr_list, list)

        data_tmp = []

        for d in data:
            tmp_dict = {}
            for key, val in d.items():
                if key in attr_list:
                    tmp_dict[key] = val["value"]
                else:
                    print("Key '{0}' not in attribute list".format(key))
            data_tmp.append(tmp_dict)

        assert isinstance(data_tmp, list)
        return data_tmp

    def __generate_field_arrays(self, key, sub_keys):
        """Generate dicts for array attributes of Dataverse API metadata upload.

        Parameters
        ----------
        key : str
            Name of attribute.
        sub_keys : list
            List of keys to be created.

        Returns
        -------
        list
            List of filled :class:`dict`s of metadata for Dataverse API upload.

        """
        assert isinstance(key, str)
        assert isinstance(sub_keys, list)

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
                        type_class = None
                        if isinstance(v, list):
                            multiple = True
                        else:
                            multiple = False
                        if k in self.__attr_dict_dv_up_type_class_primitive:
                            type_class = "primitive"
                        elif k in self.__attr_dict_dv_up_type_class_compound:
                            type_class = "compound"
                        elif (
                            k in self.__attr_dict_dv_up_type_class_controlled_vocabulary
                        ):
                            type_class = "controlledVocabulary"
                        tmp_dict[k] = {}
                        tmp_dict[k]["typeName"] = k
                        tmp_dict[k]["typeClass"] = type_class
                        tmp_dict[k]["multiple"] = multiple
                        tmp_dict[k]["value"] = v
                tmp_list.append(tmp_dict)

        assert isinstance(tmp_list, list)
        return tmp_list

    def json(self, data_format=None, validate=True, filename_schema=None):
        """Create Dataset JSON from attributes.

        Parameters
        ----------
        format : str
            Data formats to be validated. See `_allowed_json_formats`.
        validate : bool
            `True`, if created JSON should be validated against a JSON schema
            file. `False`, if JSON string should be created and not checked if
            valid.
        filename_schema : str
            Filename of JSON schema with full path.

        Returns
        -------
        str
            The data as a JSON string.
        """
        assert isinstance(validate, bool)
        if data_format is None:
            data_format = self._default_json_format
        assert isinstance(data_format, str)
        assert data_format in self._allowed_json_formats
        if filename_schema is None:
            filename_schema = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                self._default_json_schema_filename,
            )
        assert isinstance(filename_schema, str)

        data = {}

        if data_format == "dataverse_upload":
            data_dict = self.get()
            data["datasetVersion"] = {}
            data["datasetVersion"]["metadataBlocks"] = {}
            citation = {}
            citation["fields"] = []

            # dataset
            # Generate first level attributes
            for attr in self.__attr_import_dv_up_datasetVersion_values:
                if attr in data_dict:
                    data["datasetVersion"][attr] = data_dict[attr]

            # citation
            if "citation_displayName" in data_dict:
                citation["displayName"] = data_dict["citation_displayName"]

            # Generate first level attributes
            for attr in self.__attr_import_dv_up_citation_fields_values:
                if attr in data_dict:
                    v = data_dict[attr]
                    if isinstance(v, list):
                        multiple = True
                    else:
                        multiple = False
                    if attr in self.__attr_dict_dv_up_type_class_primitive:
                        type_class = "primitive"
                    elif attr in self.__attr_dict_dv_up_type_class_compound:
                        type_class = "compound"
                    elif (
                        attr in self.__attr_dict_dv_up_type_class_controlled_vocabulary
                    ):
                        type_class = "controlledVocabulary"
                    citation["fields"].append(
                        {
                            "typeName": attr,
                            "multiple": multiple,
                            "typeClass": type_class,
                            "value": v,
                        }
                    )

            # Generate fields attributes
            for (
                key,
                val,
            ) in self.__attr_import_dv_up_citation_fields_arrays.items():
                if key in data_dict:
                    v = data_dict[key]
                    citation["fields"].append(
                        {
                            "typeName": key,
                            "multiple": True,
                            "typeClass": "compound",
                            "value": self.__generate_field_arrays(key, val),
                        }
                    )

            # Generate series attributes
            if "series" in data_dict:
                series = data_dict["series"]
                tmp_dict = {}
                if "seriesName" in series:
                    if series["seriesName"] is not None:
                        tmp_dict["seriesName"] = {}
                        tmp_dict["seriesName"]["typeName"] = "seriesName"
                        tmp_dict["seriesName"]["multiple"] = False
                        tmp_dict["seriesName"]["typeClass"] = "primitive"
                        tmp_dict["seriesName"]["value"] = series["seriesName"]
                if "seriesInformation" in series:
                    if series["seriesInformation"] is not None:
                        tmp_dict["seriesInformation"] = {}
                        tmp_dict["seriesInformation"]["typeName"] = "seriesInformation"
                        tmp_dict["seriesInformation"]["multiple"] = False
                        tmp_dict["seriesInformation"]["typeClass"] = "primitive"
                        tmp_dict["seriesInformation"]["value"] = series[
                            "seriesInformation"
                        ]
                citation["fields"].append(
                    {
                        "typeName": "series",
                        "multiple": False,
                        "typeClass": "compound",
                        "value": tmp_dict,
                    }
                )

            # geospatial
            for attr in (
                self.__attr_import_dv_up_geospatial_fields_values
                + list(self.__attr_import_dv_up_geospatial_fields_arrays.keys())
                + ["geospatial_displayName"]
            ):
                if attr in data_dict:
                    geospatial = {}
                    if attr != "geospatial_displayName":
                        geospatial["fields"] = []
                        break

            if "geospatial_displayName" in data_dict:
                geospatial["displayName"] = data_dict["geospatial_displayName"]

            # Generate first level attributes
            for attr in self.__attr_import_dv_up_geospatial_fields_values:
                if attr in data_dict:
                    v = data_dict[attr]
                    if isinstance(v, list):
                        multiple = True
                    else:
                        multiple = False
                    if attr in self.__attr_dict_dv_up_type_class_primitive:
                        type_class = "primitive"
                    elif attr in self.__attr_dict_dv_up_type_class_compound:
                        type_class = "compound"
                    elif (
                        attr in self.__attr_dict_dv_up_type_class_controlled_vocabulary
                    ):
                        type_class = "controlledVocabulary"
                    geospatial["fields"].append(
                        {
                            "typeName": attr,
                            "multiple": multiple,
                            "typeClass": type_class,
                            "value": v,
                        }
                    )

            # Generate fields attributes
            for (
                key,
                val,
            ) in self.__attr_import_dv_up_geospatial_fields_arrays.items():
                if key in data_dict:
                    geospatial["fields"].append(
                        {
                            "typeName": key,
                            "multiple": True,
                            "typeClass": "compound",
                            "value": self.__generate_field_arrays(key, val),
                        }
                    )

            # socialscience
            for attr in self.__attr_import_dv_up_socialscience_fields_values + [
                "socialscience_displayName"
            ]:
                if attr in data_dict:
                    socialscience = {}
                    if attr != "socialscience_displayName":
                        socialscience["fields"] = []
                        break

            if "socialscience_displayName" in data_dict:
                socialscience["displayName"] = data_dict["socialscience_displayName"]

            # Generate first level attributes
            for attr in self.__attr_import_dv_up_socialscience_fields_values:
                if attr in data_dict:
                    v = data_dict[attr]
                    if isinstance(v, list):
                        multiple = True
                    else:
                        multiple = False
                    if attr in self.__attr_dict_dv_up_type_class_primitive:
                        type_class = "primitive"
                    elif attr in self.__attr_dict_dv_up_type_class_compound:
                        type_class = "compound"
                    elif (
                        attr in self.__attr_dict_dv_up_type_class_controlled_vocabulary
                    ):
                        type_class = "controlledVocabulary"
                    socialscience["fields"].append(
                        {
                            "typeName": attr,
                            "multiple": multiple,
                            "typeClass": type_class,
                            "value": v,
                        }
                    )

            # Generate targetSampleSize attributes
            if "targetSampleSize" in data_dict:
                target_sample_size = data_dict["targetSampleSize"]
                tmp_dict = {}
                if "targetSampleActualSize" in target_sample_size:
                    if target_sample_size["targetSampleActualSize"] is not None:
                        tmp_dict["targetSampleActualSize"] = {}
                        tmp_dict["targetSampleActualSize"]["typeName"] = (
                            "targetSampleActualSize"
                        )
                        tmp_dict["targetSampleActualSize"]["multiple"] = False
                        tmp_dict["targetSampleActualSize"]["typeClass"] = "primitive"
                        tmp_dict["targetSampleActualSize"]["value"] = (
                            target_sample_size["targetSampleActualSize"]
                        )
                if "targetSampleSizeFormula" in target_sample_size:
                    if target_sample_size["targetSampleSizeFormula"] is not None:
                        tmp_dict["targetSampleSizeFormula"] = {}
                        tmp_dict["targetSampleSizeFormula"]["typeName"] = (
                            "targetSampleSizeFormula"
                        )
                        tmp_dict["targetSampleSizeFormula"]["multiple"] = False
                        tmp_dict["targetSampleSizeFormula"]["typeClass"] = "primitive"
                        tmp_dict["targetSampleSizeFormula"]["value"] = (
                            target_sample_size["targetSampleSizeFormula"]
                        )
                socialscience["fields"].append(
                    {
                        "typeName": "targetSampleSize",
                        "multiple": False,
                        "typeClass": "compound",
                        "value": tmp_dict,
                    }
                )

            # Generate socialScienceNotes attributes
            if "socialScienceNotes" in data_dict:
                social_science_notes = data_dict["socialScienceNotes"]
                tmp_dict = {}
                if "socialScienceNotesType" in social_science_notes:
                    if social_science_notes["socialScienceNotesType"] is not None:
                        tmp_dict["socialScienceNotesType"] = {}
                        tmp_dict["socialScienceNotesType"]["typeName"] = (
                            "socialScienceNotesType"
                        )
                        tmp_dict["socialScienceNotesType"]["multiple"] = False
                        tmp_dict["socialScienceNotesType"]["typeClass"] = "primitive"
                        tmp_dict["socialScienceNotesType"]["value"] = (
                            social_science_notes["socialScienceNotesType"]
                        )
                if "socialScienceNotesSubject" in social_science_notes:
                    if social_science_notes["socialScienceNotesSubject"] is not None:
                        tmp_dict["socialScienceNotesSubject"] = {}
                        tmp_dict["socialScienceNotesSubject"]["typeName"] = (
                            "socialScienceNotesSubject"
                        )
                        tmp_dict["socialScienceNotesSubject"]["multiple"] = False
                        tmp_dict["socialScienceNotesSubject"]["typeClass"] = "primitive"
                        tmp_dict["socialScienceNotesSubject"]["value"] = (
                            social_science_notes["socialScienceNotesSubject"]
                        )
                if "socialScienceNotesText" in social_science_notes:
                    if social_science_notes["socialScienceNotesText"] is not None:
                        tmp_dict["socialScienceNotesText"] = {}
                        tmp_dict["socialScienceNotesText"]["typeName"] = (
                            "socialScienceNotesText"
                        )
                        tmp_dict["socialScienceNotesText"]["multiple"] = False
                        tmp_dict["socialScienceNotesText"]["typeClass"] = "primitive"
                        tmp_dict["socialScienceNotesText"]["value"] = (
                            social_science_notes["socialScienceNotesText"]
                        )
                socialscience["fields"].append(
                    {
                        "typeName": "socialScienceNotes",
                        "multiple": False,
                        "typeClass": "compound",
                        "value": tmp_dict,
                    }
                )

            # journal
            for attr in (
                self.__attr_import_dv_up_journal_fields_values
                + list(self.__attr_import_dv_up_journal_fields_arrays.keys())
                + ["journal_displayName"]
            ):
                if attr in data_dict:
                    journal = {}
                    if attr != "journal_displayName":
                        journal["fields"] = []
                        break

            if "journal_displayName" in data_dict:
                journal["displayName"] = data_dict["journal_displayName"]

            # Generate first level attributes
            for attr in self.__attr_import_dv_up_journal_fields_values:
                if attr in data_dict:
                    v = data_dict[attr]
                    if isinstance(v, list):
                        multiple = True
                    else:
                        multiple = False
                    if attr in self.__attr_dict_dv_up_type_class_primitive:
                        type_class = "primitive"
                    elif attr in self.__attr_dict_dv_up_type_class_compound:
                        type_class = "compound"
                    elif (
                        attr in self.__attr_dict_dv_up_type_class_controlled_vocabulary
                    ):
                        type_class = "controlledVocabulary"
                    journal["fields"].append(
                        {
                            "typeName": attr,
                            "multiple": multiple,
                            "typeClass": type_class,
                            "value": v,
                        }
                    )

            # Generate fields attributes
            for (
                key,
                val,
            ) in self.__attr_import_dv_up_journal_fields_arrays.items():
                if key in data_dict:
                    journal["fields"].append(
                        {
                            "typeName": key,
                            "multiple": True,
                            "typeClass": "compound",
                            "value": self.__generate_field_arrays(key, val),
                        }
                    )

            data["datasetVersion"]["metadataBlocks"]["citation"] = citation
            if "socialscience" in locals():
                data["datasetVersion"]["metadataBlocks"]["socialscience"] = (
                    socialscience
                )
            if "geospatial" in locals():
                data["datasetVersion"]["metadataBlocks"]["geospatial"] = geospatial
            if "journal" in locals():
                data["datasetVersion"]["metadataBlocks"]["journal"] = journal
        elif data_format == "dspace":
            data = None
            print("INFO: Not implemented yet.")
        elif data_format == "custom":
            data = None
            print("INFO: Not implemented yet.")
        if validate:
            validate_data(data, filename_schema)

        json_str = json.dumps(data, indent=2)
        assert isinstance(json_str, str)
        return json_str


class Datafile(DVObject):
    """Base class for the Dataverse data type `Datafile`.

    Attributes
    ----------
    _default_json_format : str
        Default JSON data format.
    _default_json_schema_filename : str
        Default JSON schema filename.
    _allowed_json_formats : list
        List of all possible JSON data formats.
    _json_dataverse_upload_attr : list
        List of all attributes to be exported in :func:`json`.
    """

    def __init__(self, data=None):
        """Init :class:`Datafile()`.

        Inherits attributes from parent :class:`DVObject()`

        Parameters
        ----------
        data : dict
            Flat dictionary. All keys will be mapped to a similar
            named attribute and it's value.

        Examples
        -------
        Create a Datafile::

            >>> from pyDataverse.models import Datafile
            >>> df = Datafile()
            >>> print(df._default_json_schema_filename)
            'schemas/json/datafile_upload_schema.json'

        """
        self._internal_attributes = ["_Datafile" + attr for attr in INTERNAL_ATTRIBUTES]

        super().__init__(data=data)

        self._default_json_format = "dataverse_upload"
        self._default_json_schema_filename = "schemas/json/datafile_upload_schema.json"
        self._allowed_json_formats = ["dataverse_upload", "dataverse_download"]
        self._json_dataverse_upload_attr = [
            "description",
            "categories",
            "restrict",
            "label",
            "directoryLabel",
            "pid",
            "filename",
        ]
