"""Tests for the Dataverse class.

This module contains test functions for Dataverse factory operations
including API initialization, dataset creation, collection management, and search.
"""

import uuid

from pyDataverse.dataverse.collection import Collection
from pyDataverse.dataverse.dataset import Dataset
from pyDataverse.dataverse.dataverse import Dataverse
from pyDataverse.dataverse.metrics import Metrics
from pyDataverse.models import info
from pyDataverse.models.metadatablocks.metadatablock import MetadatablockSpecification
from tests.conftest import CollectionFactory, DatasetFactory


class TestDataverse:
    """Test suite for Dataverse functionality.
    
    Tests cover Dataverse factory operations including API access, server information,
    collection and dataset management, search functionality, and content creation.
    """

    def test_native_api_property(self, dataverse: Dataverse):
        """Test accessing the native_api property.
        
        Verifies that the native_api property returns an initialized NativeApi
        instance for low-level API operations.
        """
        assert dataverse.native_api is not None, "NativeApi not initialized"

    def test_data_access_api_property(self, dataverse: Dataverse):
        """Test accessing the data_access_api property.
        
        Verifies that the data_access_api property returns an initialized DataAccessApi
        instance for file download and data access operations.
        """
        assert dataverse.data_access_api is not None, "DataAccessApi not initialized"

    def test_semantic_api_property(self, dataverse: Dataverse):
        """Test accessing the semantic_api property.
        
        Verifies that the semantic_api property returns an initialized SemanticApi
        instance for retrieving metadata in semantic formats like JSON-LD and RDF.
        """
        assert dataverse.semantic_api is not None, "SemanticApi not initialized"

    def test_metrics_api_property(self, dataverse: Dataverse):
        """Test accessing the metrics_api property.
        
        Verifies that the metrics_api property returns an initialized MetricsApi
        instance for retrieving usage statistics and metrics.
        """
        assert dataverse.metrics_api is not None, "MetricsApi not initialized"

    def test_version(self, dataverse: Dataverse):
        """Test retrieving the Dataverse instance version.
        
        Verifies that the version property returns the Dataverse server version
        information including version number and build details.
        """
        assert dataverse.version is not None, "Version not initialized"

    def test_licenses(self, dataverse: Dataverse):
        """Test retrieving available licenses.
        
        Verifies that the licenses property returns a list of all available
        License objects that can be used for datasets.
        """
        assert dataverse.licenses is not None, "Licenses not initialized"
        assert len(dataverse.licenses) > 0, "No licenses found"

    def test_default_license(self, dataverse: Dataverse):
        """Test retrieving the default license.
        
        Verifies that the default_license property returns the License object
        marked as the default license for the Dataverse instance.
        """
        expected_default_license = next(
            (license for license in dataverse.licenses if license.is_default),
            None,
        )
        assert expected_default_license is not None, "Default license not found"
        assert dataverse.default_license is not None, "Default license not initialized"
        assert dataverse.default_license == expected_default_license, (
            "Default license not initialized"
        )

    def test_metrics(self, dataverse: Dataverse):
        """Test accessing the Metrics instance.
        
        Verifies that the metrics property returns a Metrics instance that
        provides access to server-wide usage statistics and metrics.
        """

        assert dataverse.metrics is not None, "Metrics not initialized"
        assert isinstance(dataverse.metrics, Metrics), "Metrics not a Metrics instance"

    def test_collections(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test accessing collections from root.
        
        Verifies that collections can be accessed from the root Dataverse instance
        via the collections property and fetch_collection() method.
        """
        collection_alias = str(uuid.uuid4())
        test_collection = collection(collection_alias)

        fetched_collection = dataverse.fetch_collection(collection_alias)

        assert dataverse.collections is not None, "Collections not initialized"
        assert isinstance(fetched_collection, Collection), (
            "Collections not a Collection instance"
        )
        assert fetched_collection.alias == test_collection.alias, (
            "Fetched collection alias does not match"
        )

    def test_datasets(self, dataverse: Dataverse, dataset: DatasetFactory):
        """Test accessing datasets from root.
        
        Verifies that datasets can be accessed from the root Dataverse instance
        via the datasets property and fetch_dataset() method using persistent identifiers.
        """

        ds = dataset()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        fetched_dataset = dataverse.fetch_dataset(ds.persistent_identifier)

        assert dataverse.datasets is not None, "Datasets not initialized"
        assert isinstance(fetched_dataset, Dataset), "Datasets not a Dataset instance"
        assert fetched_dataset.persistent_identifier == ds.persistent_identifier, (
            "Fetched dataset persistent identifier does not match"
        )

    def test_export_formats(self, dataverse: Dataverse):
        """Test retrieving available export formats.
        
        Verifies that the export_formats property returns a dictionary of available
        export formats (e.g., OAI_ORE, OAI_Datacite) with their Exporter objects.
        """

        assert dataverse.export_formats is not None, "Export formats not initialized"
        assert len(dataverse.export_formats) > 0, "No export formats found"
        assert all(
            isinstance(format, info.Exporter)
            for format in dataverse.export_formats.values()
        ), "Export formats not a dictionary of Exporter instances"

    def test_metadatablocks(self, dataverse: Dataverse):
        """Test retrieving available metadata blocks.
        
        Verifies that the metadatablocks property returns a dictionary of all
        available MetadatablockSpecification objects on the server.
        """

        assert dataverse.metadatablocks is not None, "Metadata blocks not initialized"
        assert len(dataverse.metadatablocks) > 0, "No metadata blocks found"
        assert all(
            isinstance(block, MetadatablockSpecification)
            for block in dataverse.metadatablocks.values()
        ), "Metadata blocks not a dictionary of MetadatablockSpecification objects"

    def test_search(
        self,
        dataverse: Dataverse,
        dataset: DatasetFactory,
    ):
        """Test searching for datasets and collections.
        
        Verifies that the search() method can search across all datasets and collections
        in the Dataverse instance, returning relevant results based on query terms.
        """
        dataset_title = str(uuid.uuid4())

        # Create a dataset
        ds = dataset()
        ds["citation"]["title"] = dataset_title
        ds.update_metadata()
        ds.publish()

        # Now search for the dataset
        results = dataverse.search(dataset_title)

        assert any(dataset.title == dataset_title for dataset in results.datasets), (
            "Dataset title not found in search results"
        )

    def test_create_collection(self, dataverse: Dataverse):
        """Test creating a new collection.
        
        Verifies that create_collection() can create a new collection with metadata
        and that the created collection can be retrieved and matches the provided metadata.
        """

        # Create a collection
        collection_alias = str(uuid.uuid4())
        dataverse.create_collection(
            alias=collection_alias,
            name="Test Collection",
            description="Test Collection Description",
            affiliation="Test Affiliation",
            dataverse_type="DEPARTMENT",
            dataverse_contacts=["test@test.com"],
        )

        # Now fetch the collection
        fetched_collection = dataverse.fetch_collection(collection_alias)
        assert fetched_collection.alias == collection_alias, (
            "Fetched collection alias does not match"
        )
        assert fetched_collection.name == "Test Collection", (
            "Fetched collection name does not match"
        )
        assert (
            fetched_collection.metadata.description == "Test Collection Description"
        ), "Fetched collection description does not match"
        assert fetched_collection.metadata.affiliation == "Test Affiliation", (
            "Fetched collection affiliation does not match"
        )
        assert fetched_collection.metadata.dataverse_type == "DEPARTMENT", (
            "Fetched collection dataverse type does not match"
        )

    def test_create_dataset(self, dataverse: Dataverse):
        """Test creating a new dataset.
        
        Verifies that create_dataset() can create a new dataset with metadata including
        title, description, authors, contacts, and subjects, and that the dataset
        is properly initialized and accessible.
        """
        dataset = dataverse.create_dataset(
            title="Test Dataset",
            description="Test Dataset Description",
            authors=[{"name": "Test Author"}],
            contacts=[{"name": "Test Author", "email": "test@test.com"}],
            subjects=["Computer and Information Science"],
            collection="root",
            upload_to_collection=True,
            license=dataverse.default_license,
        )

        assert dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        # Fetch the dataset
        fetched_dataset = dataverse.fetch_dataset(dataset.persistent_identifier)
        assert fetched_dataset.persistent_identifier == dataset.persistent_identifier, (
            "Fetched dataset persistent identifier does not match"
        )
        assert fetched_dataset.title == "Test Dataset", (
            "Fetched dataset title does not match"
        )
        assert fetched_dataset.description == "Test Dataset Description", (
            "Fetched dataset description does not match"
        )
        assert fetched_dataset.authors == [{"authorName": "Test Author"}], (
            "Fetched dataset authors do not match"
        )

    def test_fetch_dataset(
        self,
        dataverse: Dataverse,
        dataset: DatasetFactory,
    ):
        """Test fetching a dataset by identifier.
        
        Verifies that fetch_dataset() can retrieve a Dataset object by its persistent
        identifier, returning a properly initialized Dataset instance.
        """
        ds = dataset()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        # Now fetch the dataset
        fetched_dataset = dataverse.fetch_dataset(ds.persistent_identifier)
        assert fetched_dataset.persistent_identifier == ds.persistent_identifier, (
            "Fetched dataset persistent identifier does not match"
        )

    def test_fetch_collection(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test fetching a collection by identifier.
        
        Verifies that fetch_collection() can retrieve a Collection object by its alias,
        returning a properly initialized Collection instance.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Now fetch the collection
        fetched_collection = dataverse.fetch_collection(collection_alias)
        assert fetched_collection.alias == col.alias, (
            "Fetched collection alias does not match"
        )

    def test_getitem_collection(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test accessing collections via __getitem__.
        
        Verifies that collections can be accessed using dictionary-style syntax
        (e.g., dataverse[alias]) which automatically determines whether the identifier
        refers to a collection or dataset.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Now fetch the collection
        fetched_collection = dataverse[collection_alias]
        assert isinstance(fetched_collection, Collection), (
            "Fetched collection is not a Collection instance"
        )
        assert fetched_collection.alias == collection_alias, (
            "Fetched collection alias does not match"
        )

    def test_getitem_dataset(
        self,
        dataverse: Dataverse,
        dataset: DatasetFactory,
    ):
        """Test accessing datasets via __getitem__.
        
        Verifies that datasets can be accessed using dictionary-style syntax
        (e.g., dataverse[persistent_id]) which automatically determines whether
        the identifier refers to a collection or dataset.
        """
        ds = dataset()
        ds.publish()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        # Now fetch the dataset
        fetched_dataset = dataverse[ds.persistent_identifier]
        assert isinstance(fetched_dataset, Dataset), (
            "Fetched dataset is not a Dataset instance"
        )
        assert fetched_dataset.persistent_identifier == ds.persistent_identifier, (
            "Fetched dataset persistent identifier does not match"
        )

    def test_view_getitem_collection(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test accessing collections via view's __getitem__.
        
        Verifies that collections can be accessed via the collections view
        using dictionary-style syntax (e.g., dataverse.collections[alias]).
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Now fetch the collection
        fetched_collection = dataverse.collections[collection_alias]
        assert isinstance(fetched_collection, Collection), (
            "Fetched collection is not a Collection instance"
        )
        assert fetched_collection.alias == collection_alias, (
            "Fetched collection alias does not match"
        )

    def test_view_getitem_dataset(
        self,
        dataverse: Dataverse,
        dataset: DatasetFactory,
    ):
        """Test accessing datasets via view's __getitem__.
        
        Verifies that datasets can be accessed via the datasets view using
        dictionary-style syntax (e.g., dataverse.datasets[persistent_id]).
        """
        ds = dataset()
        ds.publish()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        # Now fetch the dataset
        fetched_dataset = dataverse.datasets[ds.persistent_identifier]
        assert isinstance(fetched_dataset, Dataset), (
            "Fetched dataset is not a Dataset instance"
        )
