"""Tests for the Semantic API functionality.

This module contains test functions for retrieving dataset metadata in semantic
formats like JSON-LD and converting to RDF graphs.
"""

from rdflib import Graph

from pyDataverse.api.semantic import SemanticApi
from pyDataverse.dataverse.dataset import Dataset
from tests.conftest import Credentials, DatasetFactory


class TestSemantic:
    """Test suite for Semantic API functionality."""

    def _create_datasets(
        self, factory: DatasetFactory, n_datasets: int
    ) -> list[Dataset]:
        return [factory() for _ in range(n_datasets)]

    def test_get_dataset_by_persistent_id(
        self,
        semantic_api: SemanticApi,
        dataset: DatasetFactory,
    ):
        """Test retrieving dataset metadata in JSON-LD format using persistent identifier."""

        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset should have a persistent identifier"
        )

        # Fetch the dataset metadata
        metadata = semantic_api.get_dataset(test_dataset.persistent_identifier)

        assert metadata is not None, "Dataset metadata should not be None"
        assert isinstance(metadata, dict), "Dataset metadata should be a dictionary"

    def test_get_dataset_by_id(
        self,
        semantic_api: SemanticApi,
        dataset: DatasetFactory,
    ):
        """Test retrieving dataset metadata in JSON-LD format using numeric ID."""
        test_dataset = dataset()

        assert test_dataset.identifier is not None, (
            "Dataset should have a numeric identifier"
        )

        # Fetch the dataset metadata
        metadata = semantic_api.get_dataset(test_dataset.identifier)

        assert metadata is not None, "Dataset metadata should not be None"
        assert isinstance(metadata, dict), "Dataset metadata should be a dictionary"

    def test_get_dataset_as_graph(
        self,
        semantic_api: SemanticApi,
        dataset: DatasetFactory,
    ):
        """Test retrieving dataset metadata as RDFLib Graph object."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset should have a persistent identifier"
        )

        # Fetch the dataset metadata
        metadata = semantic_api.get_dataset(
            test_dataset.persistent_identifier,
            as_graph=True,
        )

        assert metadata is not None, "Dataset metadata should not be None"
        assert isinstance(metadata, Graph), "Dataset metadata should be a Graph"

    def test_get_datasets_single(
        self,
        semantic_api: SemanticApi,
        credentials: Credentials,
        dataset: DatasetFactory,
    ):
        """Test retrieving metadata for a single dataset using get_datasets."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset should have a persistent identifier"
        )

        metadata = semantic_api.get_dataset(test_dataset.persistent_identifier)

        assert metadata is not None, "Dataset metadata should not be None"
        assert isinstance(metadata, dict), "Dataset metadata should be a dictionary"

    def test_get_datasets_multiple(
        self,
        semantic_api: SemanticApi,
        dataset: DatasetFactory,
    ):
        """Test retrieving metadata for multiple datasets concurrently."""
        datasets = self._create_datasets(dataset, 2)

        metadata = semantic_api.get_datasets(
            [
                dataset.persistent_identifier
                for dataset in datasets
                if dataset.persistent_identifier is not None
            ],
        )

        assert len(metadata) == len(datasets), (
            f"There should be {len(datasets)} datasets in the metadata"
        )
        assert all(isinstance(m, dict) for m in metadata), (
            "All metadata should be dictionaries"
        )

    def test_get_datasets_with_batch_size(
        self,
        semantic_api: SemanticApi,
        dataset: DatasetFactory,
    ):
        """Test retrieving multiple datasets with custom batch size."""
        datasets = self._create_datasets(dataset, 20)

        metadata = semantic_api.get_datasets(
            [
                dataset.persistent_identifier
                for dataset in datasets
                if dataset.persistent_identifier is not None
            ],
            batch_size=10,
        )
        assert len(metadata) == len(datasets), (
            f"There should be {len(datasets)} datasets in the metadata"
        )

    def test_get_datasets_as_dicts(
        self,
        semantic_api: SemanticApi,
        credentials: Credentials,
        dataset: DatasetFactory,
    ):
        """Test retrieving multiple datasets as dictionary sequence."""
        datasets = self._create_datasets(dataset, 2)
        metadata = semantic_api.get_datasets(
            [
                dataset.persistent_identifier
                for dataset in datasets
                if dataset.persistent_identifier is not None
            ],
        )
        assert len(metadata) == len(datasets), (
            f"There should be {len(datasets)} datasets in the metadata"
        )
        assert all(isinstance(m, dict) for m in metadata), (
            "All metadata should be dictionaries"
        )

    def test_get_datasets_as_graph(
        self,
        semantic_api: SemanticApi,
        dataset: DatasetFactory,
    ):
        """Test retrieving multiple datasets as combined RDFLib Graph."""
        datasets = self._create_datasets(dataset, 2)
        graph = semantic_api.get_datasets(
            [
                dataset.persistent_identifier
                for dataset in datasets
                if dataset.persistent_identifier is not None
            ],
            as_graph=True,
        )

        assert isinstance(graph, Graph), "Graph should be a Graph"

    def test_get_datasets_mixed_identifiers(
        self,
        semantic_api: SemanticApi,
        dataset: DatasetFactory,
    ):
        """Test retrieving datasets with mixed identifier types (persistent IDs and numeric IDs)."""
        datasets = self._create_datasets(dataset, 4)
        metadata = semantic_api.get_datasets(
            [
                dataset.persistent_identifier if i % 2 == 0 else dataset.identifier
                for i, dataset in enumerate(datasets)
                if dataset.persistent_identifier is not None
                and dataset.identifier is not None
            ],
        )

        assert len(metadata) == len(datasets), (
            f"There should be {len(datasets)} datasets in the metadata"
        )
        assert all(isinstance(m, dict) for m in metadata), (
            "All metadata should be dictionaries"
        )

    def test_response_to_graph(
        self,
        semantic_api: SemanticApi,
        dataset: DatasetFactory,
    ):
        """Test converting a JSON-LD response dictionary to RDFLib Graph."""
        test_dataset = dataset()

        assert test_dataset.persistent_identifier is not None, (
            "Dataset should have a persistent identifier"
        )

        metadata = semantic_api.get_dataset(test_dataset.persistent_identifier)

        assert metadata is not None, "Dataset metadata should not be None"
        assert isinstance(metadata, dict), "Dataset metadata should be a dictionary"

        graph = semantic_api.response_to_graph(metadata)
        assert isinstance(graph, Graph), "Graph should be a Graph"

    def test_responses_to_graph(
        self,
        semantic_api: SemanticApi,
        credentials: Credentials,
        dataset: DatasetFactory,
    ):
        """Test converting multiple JSON-LD responses to a single RDFLib Graph."""
        datasets = self._create_datasets(dataset, 2)
        metadata = semantic_api.get_datasets(
            [
                dataset.persistent_identifier
                for dataset in datasets
                if dataset.persistent_identifier is not None
            ],
        )

        graph = semantic_api.responses_to_graph(metadata)

        assert isinstance(graph, Graph), "Graph should be a Graph"
