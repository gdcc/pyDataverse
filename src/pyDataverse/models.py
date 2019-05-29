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
        """Set attributes."""
        if isinstance(data, list):
            # TODO: prüfen, ob die struktur passt
            data = dict(data)
        elif not isinstance(data, dict):
            # TODO: Exception raisen
            print('Data was not passed in the correct data type. Dict() or '
                  'List() required.')

        for key, val in data.items():
            # TODO: prüfen, ob es sich immer um strings handelt bei den keys und values.
            if key == 'alias':
                self.alias = val
            elif key == 'name':
                self.name = val
            elif key == 'contactEmail':
                # TODO: add oder overwrite??
                if isinstance(val, list):
                    for email in val:
                        self.contactEmail.append(email)
                elif isinstance(val, str):
                    self.contactEmail.append(val)
                else:
                    # TODO: Exception
                    print('contactEmail "{}" not a list or a string. Do not'
                          ' know what to do'.format(val))
            elif key == 'affiliation':
                self.affiliation = val
            elif key == 'description':
                self.description = val
            elif key == 'dataverseType':
                self.dataverseType = val
            else:
                print('Key "{}" passed is not valid'.format(key))

    @property
    def dict(self):
        """Get Dataverse metadata as dict for Dataverse API upload.

        TODO: Validate standard

        """
        data = {}

        # prüfen, ob required attributes gesetzt sind. wenn nicht = Exception!
        if self.alias:
            data['alias'] = self.alias
        if self.name:
            data['name'] = self.name
        if self.contactEmail:
            data['dataverseContacts'] = []
            for email in self.contactEmail:
                data['dataverseContacts'].append({'contactEmail': email})
        if self.affiliation:
            data['affiliation'] = self.affiliation
        if self.description:
            data['description'] = self.description
        if self.dataverseType:
            data['dataverseType'] = self.dataverseType

        return data

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

    def import_data(self, filename, format):
        """Import data from different sources.

        does: mappen der metadaten in die interne datenstruktur -> set()

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
        return: True

        dv = Dataverse()
        dv.import_data('data/dataverse/dataverse-complete.json', 'dv_up')
        dv.contactEmail

        """
        if format == 'dv_up' or format == 'dv_down':
            data = read_file_json(filename)
            # TODO: welche der variablen sind den required? wie soll damit umgegangen werden?
            if 'name' in data:
                self.name = data['name']
            if 'alias' in data:
                self.alias = data['alias']
            if 'dataverseContacts' in data:
                for contact in data['dataverseContacts']:
                    for key, val in contact.items():
                        if key == 'contactEmail':
                            self.contactEmail.append(val)
            if 'affiliation' in data:
                self.affiliation = data['affiliation']
            if 'description' in data:
                self.description = data['description']
            if 'dataverseType' in data:
                self.dataverseType = data['dataverseType']
        else:
            # TODO: Exception
            print('Data-format not right')

    def export_data(self, filename, format):
        """Export data to different file-formats.

        format: `dv_up`

        """
        if format == 'dv_up':
            return write_file_json(filename, self.dict)
        else:
            # TODO: Exception
            print('Data-format not right')


class Dataset(object):
    """Base class for the Dataset model."""

    def __init__(self):
        """Init Dataset() class."""
        """Dataset"""
        self.license = None
        self.termsOfUse = None
        self.termsOfAccess = None

        """Citation"""
        self.citation_displayName = None
        self.title = None
        self.subtitle = None
        self.alternativeTitle = None
        self.alternativeURL = None
        self.otherId = []
        # self.otherIdAgency
        # self.otherIdValue
        self.author = []
        # self.authorName
        # self.authorAffiliation
        # self.authorIdentifierScheme
        # self.authorIdentifier
        self.datasetContact = []
        # self.datasetContactName
        # self.datasetContactAffiliation
        # self.datasetContactEmail
        self.dsDescription = []
        # self.dsDescriptionValue
        # self.dsDescriptionDate
        self.subject = []
        self.keyword = []
        # self.keywordValue
        # self.keywordVocabulary
        # self.keywordVocabularyURI
        self.topicClassification = []
        # self.topicClassValue
        # self.topicClassVocab
        self.publication = []
        # self.publicationCitation
        # self.publicationIDType
        # self.publicationIDNumber
        # self.publicationURL
        self.notesText = None
        self.producer = []
        # self.producerName
        # self.producerAffiliation
        # self.producerAbbreviation
        # self.producerURL
        # self.producerLogoURL
        self.productionDate = None
        self.productionPlace = None
        self.contributor = []
        # self.contributorType
        # self.contributorName
        self.grantNumber = []
        # self.grantNumberAgency
        # self.grantNumberValue
        self.distributor = []
        # self.distributorName
        # self.distributorAffiliation
        # self.distributorAbbreviation
        # self.distributorURL
        # self.distributorLogoURL
        self.distributionDate = None
        self.depositor = None
        self.dateOfDeposit = None
        self.timePeriodCovered = []
        # self.timePeriodCoveredStart
        # self.timePeriodCoveredEnd
        self.dateOfCollection = []
        # self.dateOfCollectionStart
        # self.dateOfCollectionEnd
        self.kindOfData = []
        self.series = []
        # self.seriesName
        # self.seriesInformation
        self.software = []
        # self.softwareName
        # self.softwareVersion
        self.relatedMaterial = []
        self.relatedDatasets = []
        self.otherReferences = []
        self.dataSources = []
        self.originOfSources = None
        self.characteristicOfSources = None
        self.accessToSources = None

        """Geospatial"""
        self.geospatial_displayName = None
        self.geographicCoverage = []
        # self.country
        # self.state
        # self.city
        # self.otherGeographicCoverage
        self.geographicUnit = None
        self.geographicBoundingBox = []
        # self.westLongitude
        # self.eastLongitude
        # self.northLongitude
        # self.southLongitude

        """SocialScience"""
        self.socialscience_displayName = None
        self.unitOfAnalysis = []
        self.universe = []
        self.timeMethod = None
        self.dataCollector = None
        self.collectorTraining = None
        self.frequencyOfDataCollection = None
        self.samplingProcedure = None
        self.targetSampleSize = []
        # self.targetSampleActualSize
        # self.targetSampleSizeFormula
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
        self.socialScienceNotesType = None
        self.socialScienceNotesSubject = None
        self.socialScienceNotesText = None

        """Journal"""
        self.journal_displayName = None
        self.journalVolumeIssue = []
        # self.journalVolume
        # self.journalIssue
        # self.journalPubDate
        self.journalArticleType = None

    def __str__(self):
        """Return name of Dataset() class for users."""
        return 'pyDataverse Dataset() model class.'

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
        socialscience = {}
        journal = {}

        # TODO: prüfen, ob required attributes gesetzt sind. wenn nicht = Exception!

        """Dataset"""
        if self.license:
            data['datasetVersion']['license'] = self.license
        if self.termsOfUse:
            data['datasetVersion']['termsOfUse'] = self.termsOfUse
        if self.termsOfAccess:
            data['datasetVersion']['termsOfAccess'] = self.termsOfAccess

        """Citation"""
        if self.citation_displayName:
            citation['displayName'] = self.citation_displayName
        if self.title:
            citation['fields'].append({'title': self.title})
        if self.subtitle:
            citation['fields'].append({'subtitle': self.subtitle})
        if self.alternativeTitle:
            citation['fields'].append({'alternativeTitle': self.alternativeTitle})
        if self.alternativeURL:
            citation['fields'].append({'alternativeURL': self.alternativeURL})
        if self.otherId:
            pass
        if self.author:
            pass
        if self.datasetContact:
            pass
        if self.dsDescription:
            pass
        if self.subject:
            citation['fields'].append({'subject': self.subject})
        if self.keyword:
            pass
        if self.topicClassification:
            pass
        if self.publication:
            pass
        if self.notesText:
            citation['fields'].append({'notesText': self.notesText})
        if self.producer:
            pass
        if self.productionDate:
            citation['fields'].append({'productionDate': self.productionDate})
        if self.productionPlace:
            citation['fields'].append({'productionPlace': self.productionPlace})
        if self.contributor:
            pass
        if self.grantNumber:
            pass
        if self.distributor:
            pass
        if self.distributionDate:
            citation['fields'].append({'distributionDate': self.distributionDate})
        if self.depositor:
            citation['fields'].append({'depositor': self.depositor})
        if self.dateOfDeposit:
            citation['fields'].append({'dateOfDeposit': self.dateOfDeposit})
        if self.timePeriodCovered:
            pass
        if self.dateOfCollection:
            pass
        if self.kindOfData:
            citation['fields'].append({'kindOfData': self.kindOfData})
        if self.series:
            pass
        if self.software:
            pass
        if self.relatedMaterial:
            citation['fields'].append({'relatedMaterial': self.relatedMaterial})
        if self.relatedDatasets:
            citation['fields'].append(
                {'relatedDatasets': self.relatedDatasets})
        if self.otherReferences:
            citation['fields'].append({'otherReferences': self.otherReferences})
        if self.dataSources:
            citation['fields'].append({'dataSources': self.dataSources})
        if self.originOfSources:
            citation['fields'].append(
                {'originOfSources': self.originOfSources})
        if self.characteristicOfSources:
            citation['fields'].append(
                {'characteristicOfSources': self.characteristicOfSources})
        if self.accessToSources:
            citation['fields'].append({'accessToSources': self.accessToSources})

        """Geospatial"""
        if self.geospatial_displayName:
            data['geospatial_displayName'] = self.geospatial_displayName
        if self.geographicCoverage:
            pass
        if self.geographicUnit:
            data['geographicUnit'] = self.geographicUnit
        if self.geographicBoundingBox:
            pass

        """SocialScience"""
        if self.socialscience_displayName:
            data['socialscience_displayName'] = self.socialscience_displayName
        if self.unitOfAnalysis:
            data['unitOfAnalysis'] = self.unitOfAnalysis
        if self.universe:
            data['universe'] = self.universe
        if self.timeMethod:
            data['timeMethod'] = self.timeMethod
        if self.dataCollector:
            data['dataCollector'] = self.dataCollector
        if self.collectorTraining:
            data['collectorTraining'] = self.collectorTraining
        if self.frequencyOfDataCollection:
            data['frequencyOfDataCollection'] = self.frequencyOfDataCollection
        if self.samplingProcedure:
            data['samplingProcedure'] = self.samplingProcedure
        if self.targetSampleSize:
            pass
        if self.deviationsFromSampleDesign:
            data['deviationsFromSampleDesign'] = self.deviationsFromSampleDesign
        if self.collectionMode:
            data['collectionMode'] = self.collectionMode
        if self.researchInstrument:
            data['researchInstrument'] = self.researchInstrument
        if self.dataCollectionSituation:
            data['dataCollectionSituation'] = self.dataCollectionSituation
        if self.actionsToMinimizeLoss:
            data['actionsToMinimizeLoss'] = self.actionsToMinimizeLoss
        if self.controlOperations:
            data['controlOperations'] = self.controlOperations
        if self.weighting:
            data['weighting'] = self.weighting
        if self.cleaningOperations:
            data['cleaningOperations'] = self.cleaningOperations
        if self.datasetLevelErrorNotes:
            data['datasetLevelErrorNotes'] = self.datasetLevelErrorNotes
        if self.responseRate:
            data['responseRate'] = self.responseRate
        if self.samplingErrorEstimates:
            data['samplingErrorEstimates'] = self.samplingErrorEstimates
        if self.otherDataAppraisal:
            data['otherDataAppraisal'] = self.otherDataAppraisal
        if self.socialScienceNotesType:
            data['socialScienceNotesType'] = self.socialScienceNotesType
        if self.socialScienceNotesSubject:
            data['socialScienceNotesSubject'] = self.socialScienceNotesSubject
        if self.socialScienceNotesText:
            data['socialScienceNotesText'] = self.socialScienceNotesText

        """Journal"""
        if self.journal_displayName:
            data['journal_displayName'] = self.journal_displayName
        if self.journalVolumeIssue:
            pass
        if self.journalArticleType:
            data['journalArticleType'] = self.journalArticleType

        data['datasetVersion']['metadataBlocks']['citation'] = citation
        data['datasetVersion']['metadataBlocks'][''] = socialscience
        data['datasetVersion']['metadataBlocks'][''] = geospatial
        data['datasetVersion']['metadataBlocks'][''] = journal

        return data

    @property
    def json(self):
        """Get Dataset metadata as json for Dataverse API upload.

        TODO: Validate standard
        TODO: Link to default json file

        """
        return dict_to_json(self.dict)
