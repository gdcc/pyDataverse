"""Tests for the Collection class.

This module contains test functions for collection-related operations
including metadata management, content access, and dataset creation.
"""

import uuid

import pandas as pd
from rdflib import Graph

from pyDataverse.dataverse.collection import Collection
from pyDataverse.dataverse.dataset import Dataset
from pyDataverse.dataverse.dataverse import Dataverse
from pyDataverse.dataverse.metrics import Metrics
from pyDataverse.models.metadatablocks.metadatablock import MetadatablockSpecification
from tests.conftest import CollectionFactory, Credentials


class TestCollection:
    """Test suite for Collection functionality.

    Tests cover collection properties, metadata management, content access,
    dataset creation, subcollection management, and RDF graph export.
    """

    def test_metrics(
        self,
        collection: CollectionFactory,
    ):
        """Test accessing collection metrics.

        Verifies that the metrics property returns a Metrics instance that
        provides access to collection statistics and usage data.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        assert col.metrics is not None, "Metrics not initialized"
        assert isinstance(col.metrics, Metrics), "Metrics not a Metrics instance"

    def test_name(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test accessing collection name.

        Verifies that the name property correctly returns the collection name
        and matches the name retrieved from the server.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Fetch the collection
        fetched_collection = dataverse.fetch_collection(collection_alias)

        assert col.name is not None, "Name not initialized"
        assert col.name == fetched_collection.name, "Name does not match"

    def test_metadata(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test retrieving collection metadata.

        Verifies that the metadata property returns complete collection metadata
        that matches the metadata retrieved from the server.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Fetch the collection
        fetched_collection = dataverse.fetch_collection(collection_alias)

        assert col.metadata is not None, "Metadata not initialized"
        assert col.metadata == fetched_collection.metadata, "Metadata does not match"

    def test_alias(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test accessing collection alias.

        Verifies that the alias property correctly returns the collection alias
        and matches the alias retrieved from the server.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Fetch the collection
        fetched_collection = dataverse.fetch_collection(collection_alias)

        assert col.alias is not None, "Alias not initialized"
        assert col.alias == fetched_collection.alias, "Alias does not match"

    def test_update_metadata(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test updating collection metadata.

        Verifies that update_metadata() can modify collection properties like name
        and that changes are persisted correctly on the server.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.update_metadata(name="Updated Collection Name")

        # Fetch the collection
        fetched_collection = dataverse.fetch_collection(collection_alias)

        assert fetched_collection.name == "Updated Collection Name", (
            "Fetched collection name does not match"
        )

    def test_collection_overview(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
        minimal_dataset: Dataset,
    ):
        """Test retrieving collection overview.

        Verifies that the overview property returns a pandas DataFrame containing
        a summary of the collection's contents and structure.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Create a subcollection
        subcollection_alias = str(uuid.uuid4())
        subcollection = col.create_collection(
            alias=subcollection_alias,
            name="Subcollection Name",
            description="Subcollection Description",
            affiliation="Subcollection Affiliation",
            dataverse_contacts=["subcollection@test.com"],
            dataverse_type="DEPARTMENT",
        )
        subcollection.publish()

        # Add a dataset to the collection
        minimal_dataset.upload_to_collection(collection_alias)
        minimal_dataset.publish()

        # Fetch the collection
        fetched_collection = dataverse.fetch_collection(collection_alias)

        assert fetched_collection.overview is not None, "Overview not initialized"
        assert isinstance(fetched_collection.overview, pd.DataFrame), (
            "Overview is not a DataFrame"
        )

        overview = fetched_collection.overview

        assert len(overview) == 2, "Overview should have 2 rows"
        assert len(overview[overview["content_type"] == "dataset"]) == 1, (
            "Overview should have 1 row for datasets"
        )
        assert len(overview[overview["content_type"] == "collection"]) == 1, (
            "Overview should have 1 row for collections"
        )

    def test_metadatablocks(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test retrieving enabled metadata blocks.

        Verifies that the metadatablocks property returns a dictionary of
        MetadatablockSpecification objects for all metadata blocks enabled
        for the collection.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Fetch the collection
        fetched_collection = dataverse.fetch_collection(collection_alias)

        assert fetched_collection.metadatablocks is not None, (
            "Metadata blocks not initialized"
        )
        assert isinstance(fetched_collection.metadatablocks, dict), (
            "Metadata blocks is not a dictionary"
        )
        assert len(fetched_collection.metadatablocks) > 0, (
            "Metadata blocks is not empty"
        )
        assert all(
            isinstance(block, MetadatablockSpecification)
            for block in fetched_collection.metadatablocks.values()
        ), "Metadata blocks is not a dictionary of MetadatablockSpecification objects"

    def test_collections(self, credentials: Credentials, collection: CollectionFactory):
        """Test accessing subcollections.

        Verifies that subcollections can be created within a collection and
        accessed via the collections dictionary-like interface.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Create a subcollection
        subcollection_alias = str(uuid.uuid4())
        col.create_collection(
            alias=subcollection_alias,
            name="Subcollection Name",
            dataverse_contacts=["subcollection@test.com"],
            description="Subcollection Description",
            affiliation="Subcollection Affiliation",
            dataverse_type="DEPARTMENT",
        )

        # Fetch the collection
        fetched_collection = col.collections[subcollection_alias]

        assert fetched_collection.collections is not None, "Collections not initialized"
        assert isinstance(fetched_collection, Collection), (
            "Collections is not a Collection instance"
        )
        assert fetched_collection.alias == subcollection_alias, (
            "Fetched collection alias does not match"
        )

    def test_datasets(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test accessing datasets in collection.

        Verifies that datasets created within a collection can be accessed
        via the datasets dictionary-like interface using persistent identifiers.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Create a dataset
        dataset = col.create_dataset(
            title="Dataset Title",
            description="Dataset Description",
            authors=[{"name": "Dataset Author", "affiliation": "Dataset Affiliation"}],
            contacts=[{"name": "Dataset Contact", "email": "dataset@test.com"}],
            subjects=["Chemistry"],
            upload_to_collection=True,
            license=dataverse.default_license,
        )
        dataset.publish()

        # Fetch the dataset
        assert dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )
        fetched_dataset = col.datasets[dataset.persistent_identifier]

        assert fetched_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )
        assert isinstance(fetched_dataset, Dataset), (
            "Fetched dataset is not a Dataset instance"
        )

    def test_create_dataset(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test creating a dataset in the collection.

        Verifies that create_dataset() can create a new dataset within the collection
        with proper metadata and that the dataset is accessible after creation.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Create a dataset
        dataset = col.create_dataset(
            title="Dataset Title",
            description="Dataset Description",
            authors=[{"name": "Dataset Author", "affiliation": "Dataset Affiliation"}],
            contacts=[{"name": "Dataset Contact", "email": "dataset@test.com"}],
            subjects=["Chemistry"],
            upload_to_collection=True,
            license=dataverse.default_license,
        )

        dataset.publish()

        assert dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        fetched_dataset = col.datasets[dataset.persistent_identifier]

        assert fetched_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )
        assert isinstance(fetched_dataset, Dataset), (
            "Fetched dataset is not a Dataset instance"
        )

    def test_search(
        self,
        dataverse: Dataverse,
        collection: CollectionFactory,
    ):
        """Test searching within the collection.

        Verifies that the search() method can search for datasets and collections
        within the current collection scope, returning relevant results.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Create a dataset
        dataset = col.create_dataset(
            title="Dataset Title",
            description="Dataset Description",
            authors=[{"name": "Dataset Author", "affiliation": "Dataset Affiliation"}],
            contacts=[{"name": "Dataset Contact", "email": "dataset@test.com"}],
            subjects=["Chemistry"],
            upload_to_collection=True,
            license=dataverse.default_license,
        )

        dataset.publish()

        # Search for the dataset
        results = col.search(dataset.title)

        assert any(dataset.title == dataset.title for dataset in results.datasets), (
            "Dataset title not found in search results"
        )

    def test_create_collection(self, collection: CollectionFactory):
        """Test creating a subcollection.

        Verifies that create_collection() can create a nested subcollection within
        the current collection with proper metadata and hierarchy.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Create a subcollection
        subcollection_alias = str(uuid.uuid4())
        subcollection = col.create_collection(
            alias=subcollection_alias,
            name="Subcollection Name",
            description="Subcollection Description",
            affiliation="Subcollection Affiliation",
            dataverse_contacts=["subcollection@test.com"],
            dataverse_type="DEPARTMENT",
        )
        subcollection.publish()

        # Fetch the subcollection
        fetched_subcollection = col.collections[subcollection_alias]

        assert fetched_subcollection.alias == subcollection_alias, (
            "Fetched subcollection alias does not match"
        )

        assert isinstance(fetched_subcollection, Collection), (
            "Fetched subcollection is not a Collection instance"
        )

    def test_graph(self, credentials: Credentials, collection: CollectionFactory):
        """Test retrieving RDF graph of collection.

        Verifies that the graph() method returns an RDFLib Graph object containing
        semantic metadata about the collection in the specified format (e.g., OAI_ORE).
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Retrieve the RDF graph
        graph = col.graph("OAI_ORE")

        assert graph is not None, "RDF graph not initialized"
        assert isinstance(graph, Graph), "RDF graph is not a Graph instance"

    def test_len(self, dataverse: Dataverse, collection: CollectionFactory):
        """Test getting the number of child contents.

        Verifies that len() returns the correct count of child items (datasets
        and subcollections) within the collection.
        """
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Add a dataset to the collection
        dataset = col.create_dataset(
            title="Dataset Title",
            description="Dataset Description",
            authors=[{"name": "Dataset Author", "affiliation": "Dataset Affiliation"}],
            contacts=[{"name": "Dataset Contact", "email": "dataset@test.com"}],
            subjects=["Chemistry"],
            upload_to_collection=True,
            license=dataverse.default_license,
        )
        dataset.publish()

        # Get the number of child contents
        num_contents = len(col)

        assert num_contents is not None, "Number of child contents not initialized"
        assert isinstance(num_contents, int), (
            "Number of child contents is not an integer"
        )
        assert num_contents == 1, "Number of child contents is not greater than 0"
