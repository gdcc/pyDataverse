# coding: utf-8
import os
from pyDataverse.models import Dataset

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class TestDataset(object):
    """Test the Dataset() class initalization."""

    def test_dataset_init(self):
        pass

    def test_dataset_set_dvup(self):
        pass

    def test_dataset_set_dvup_less(self):
        pass

    def test_dataset_set_dvup_more(self):
        pass

    def test_dataset_is_valid(self):
        pass

    def test_dataset_is_valid_not(self):
        pass

    def test_dataset_import_metadata_dv_up(self):
        ds = Dataset()
        ds.import_metadata(TEST_DIR + '/data/dataset_full.json')

        """dataset"""
        assert ds.license == 'CC0'
        assert ds.termsOfUse == 'CC0 Waiver'
        assert ds.termsOfAccess == 'Terms of Access'

        """citation"""
        assert ds.citation_displayName == 'Citation Metadata'
        assert ds.title == 'Replication Data for: Title'
        assert ds.subtitle == 'Subtitle'
        assert ds.alternativeTitle == 'Alternative Title'
        assert ds.alternativeURL == 'http://AlternativeURL.org'
        assert isinstance(ds.otherId, list)
        assert len(ds.otherId) == 1
        for d in ds.otherId:
            assert d['otherIdAgency'] in ['OtherIDAgency1']
            assert d['otherIdValue'] in ['OtherIDIdentifier1']
        assert isinstance(ds.author, list)
        assert len(ds.author) == 1
        for d in ds.author:
            assert d['authorName'] in ['LastAuthor1, FirstAuthor1']
            assert d['authorAffiliation'] in ['AuthorAffiliation1']
            assert d['authorIdentifierScheme'] in ['ORCID']
            assert d['authorIdentifier'] in ['AuthorIdentifier1']
        assert isinstance(ds.datasetContact, list)
        assert len(ds.datasetContact) == 1
        for d in ds.datasetContact:
            assert d['datasetContactName'] in ['LastContact1, FirstContact1']
            assert d['datasetContactAffiliation'] in ['ContactAffiliation1']
            assert d['datasetContactEmail'] in ['ContactEmail1@mailinator.com']
        assert isinstance(ds.dsDescription, list)
        assert len(ds.dsDescription) == 1
        for d in ds.dsDescription:
            assert d['dsDescriptionValue'] in ['DescriptionText2']
            assert d['dsDescriptionDate'] in ['1000-02-02']
        assert ds.subject == ['Agricultural Sciences',
                              'Business and Management', 'Engineering', 'Law']
        assert isinstance(ds.keyword, list)
        assert len(ds.keyword) == 1
        for d in ds.keyword:
            assert d['keywordValue'] in ['KeywordTerm1']
            assert d['keywordVocabulary'] in ['KeywordVocabulary1']
            assert d['keywordVocabularyURI'] in ['http://KeywordVocabularyURL1.org']
        assert isinstance(ds.topicClassification, list)
        assert len(ds.topicClassification) == 1
        for d in ds.topicClassification:
            assert d['topicClassValue'] in ['Topic Class Value1']
            assert d['topicClassVocab'] in ['Topic Classification Vocabulary']
        assert isinstance(ds.publication, list)
        assert len(ds.publication) == 1
        for d in ds.publication:
            assert d['publicationCitation'] in ['RelatedPublicationCitation1']
            assert d['publicationIDType'] in ['ark']
            assert d['publicationIDNumber'] in ['RelatedPublicationIDNumber1']
            assert d['publicationURL'] in ['http://RelatedPublicationURL1.org']
        assert ds.notesText == 'Notes1'
        assert isinstance(ds.producer, list)
        assert len(ds.producer) == 1
        for d in ds.producer:
            assert d['producerName'] in ['LastProducer1, FirstProducer1']
            assert d['producerAffiliation'] in ['ProducerAffiliation1']
            assert d['producerAbbreviation'] in ['ProducerAbbreviation1']
            assert d['producerURL'] in ['http://ProducerURL1.org']
            assert d['producerLogoURL'] in ['http://ProducerLogoURL1.org']
        assert ds.productionDate == '1003-01-01'
        assert ds.productionPlace == 'ProductionPlace'
        assert isinstance(ds.contributor, list)
        assert len(ds.contributor) == 1
        for d in ds.contributor:
            assert d['contributorType'] in ['Data Collector']
            assert d['contributorName'] in ['LastContributor1, FirstContributor1']
        assert isinstance(ds.grantNumber, list)
        assert len(ds.grantNumber) == 1
        for d in ds.grantNumber:
            assert d['grantNumberAgency'] in ['GrantInformationGrantAgency1']
            assert d['grantNumberValue'] in ['GrantInformationGrantNumber1']
        assert isinstance(ds.distributor, list)
        assert len(ds.distributor) == 1
        for d in ds.distributor:
            assert d['distributorName'] in ['LastDistributor1, FirstDistributor1']
            assert d['distributorAffiliation'] in ['DistributorAffiliation1']
            assert d['distributorAbbreviation'] in ['DistributorAbbreviation1']
            assert d['distributorURL'] in ['http://DistributorURL1.org']
            assert d['distributorLogoURL'] in ['http://DistributorLogoURL1.org']
        assert ds.distributionDate == '1004-01-01'
        assert ds.depositor == 'LastDepositor, FirstDepositor'
        assert ds.dateOfDeposit == '1002-01-01'
        assert isinstance(ds.timePeriodCovered, list)
        assert len(ds.timePeriodCovered) == 1
        for d in ds.timePeriodCovered:
            assert d['timePeriodCoveredStart'] in ['1005-01-01']
            assert d['timePeriodCoveredEnd'] in ['1005-01-02']
        assert isinstance(ds.dateOfCollection, list)
        assert len(ds.dateOfCollection) == 1
        for d in ds.dateOfCollection:
            assert d['dateOfCollectionStart'] in ['1006-01-01']
            assert d['dateOfCollectionEnd'] in ['1006-01-01']
        assert ds.kindOfData == ['KindOfData1', 'KindOfData2']
        assert ds.seriesName == 'SeriesName'
        assert ds.seriesInformation == 'SeriesInformation'
        assert isinstance(ds.software, list)
        assert len(ds.software) == 1
        for d in ds.software:
            assert d['softwareName'] in ['SoftwareName1']
            assert d['softwareVersion'] in ['SoftwareVersion1']
        assert ds.relatedMaterial == ['RelatedMaterial1', 'RelatedMaterial2']
        assert ds.relatedDatasets == ['RelatedDatasets1', 'RelatedDatasets2']
        assert ds.otherReferences == ['OtherReferences1', 'OtherReferences2']
        assert ds.dataSources == ['DataSources1', 'DataSources2']
        assert ds.originOfSources == 'OriginOfSources'
        assert ds.characteristicOfSources == 'CharacteristicOfSourcesNoted'
        assert ds.accessToSources == 'DocumentationAndAccessToSources'

        """geospatial"""
        assert ds.geospatial_displayName == 'Geospatial Metadata'
        assert isinstance(ds.geographicCoverage, list)
        assert len(ds.geographicCoverage) == 1
        for d in ds.geographicCoverage:
            assert d['country'] in ['Afghanistan']
            assert d['state'] in ['GeographicCoverageStateProvince1']
            assert d['city'] in ['GeographicCoverageCity1']
            assert d['otherGeographicCoverage'] in ['GeographicCoverageOther1']
        assert ds.geographicUnit == ['GeographicUnit1', 'GeographicUnit2']
        assert isinstance(ds.geographicBoundingBox, list)
        assert len(ds.geographicBoundingBox) == 1
        for d in ds.geographicBoundingBox:
            assert d['westLongitude'] in ['10']
            assert d['eastLongitude'] in ['20']
            assert d['northLongitude'] in ['30']
            assert d['southLongitude'] in ['40']

        """socialscience"""
        assert ds.socialscience_displayName == 'Social Science and Humanities Metadata'
        assert ds.unitOfAnalysis == ['UnitOfAnalysis1', 'UnitOfAnalysis2']
        assert ds.universe == ['Universe1', 'Universe2']
        assert ds.timeMethod == 'TimeMethod'
        assert ds.dataCollector == 'LastDataCollector1, FirstDataCollector1'
        assert ds.collectorTraining == 'CollectorTraining'
        assert ds.frequencyOfDataCollection == 'Frequency'
        assert ds.samplingProcedure == 'SamplingProcedure'
        assert ds.targetSampleActualSize == '100'
        assert ds.targetSampleSizeFormula == 'TargetSampleSizeFormula'
        assert ds.deviationsFromSampleDesign == 'MajorDeviationsForSampleDesign'
        assert ds.collectionMode == 'CollectionMode'
        assert ds.researchInstrument == 'TypeOfResearchInstrument'
        assert ds.dataCollectionSituation == 'CharacteristicsOfDataCollectionSituation'
        assert ds.actionsToMinimizeLoss == 'ActionsToMinimizeLosses'
        assert ds.controlOperations == 'ControlOperations'
        assert ds.weighting == 'Weighting'
        assert ds.cleaningOperations == 'CleaningOperations'
        assert ds.datasetLevelErrorNotes == 'StudyLevelErrorNotes'
        assert ds.responseRate == 'ResponseRate'
        assert ds.samplingErrorEstimates == 'EstimatesOfSamplingError'
        assert ds.otherDataAppraisal == 'OtherFormsOfDataAppraisal'
        assert ds.socialScienceNotesType == 'NotesType'
        assert ds.socialScienceNotesSubject == 'NotesSubject'
        assert ds.socialScienceNotesText == 'NotesText'

        """journal"""
        assert ds.journal_displayName == 'Journal Metadata'
        assert isinstance(ds.journalVolumeIssue, list)
        assert len(ds.journalVolumeIssue) == 1
        for d in ds.journalVolumeIssue:
            assert d['journalVolume'] in ['JournalVolume1']
            assert d['journalIssue'] in ['JournalIssue1']
            assert d['journalPubDate'] in ['1008-01-01']
        assert ds.journalArticleType == 'abstract'

    def test_dataset_import_metadata_wrong(self):
        pass

    def test_dataset_dict_dv_up_valid_minimum(self):
        pass

    def test_dataset_dict_dv_up_valid_full(self):
        pass

    def test_dataset_dict_dv_up_valid_not(self):
        pass

    def test_dataset_dict_all(self):
        pass

    def test_dataset_dict_wrong(self):
        pass

    def test_dataset_json_dv_up(self):
        pass

    def test_dataset_json_all(self):
        pass

    def test_dataset_json_wrong(self):
        pass

    def test_dataset_export_metadata_dv_up(self):
        pass

    def test_dataset_export_metadata_wrong(self):
        pass
