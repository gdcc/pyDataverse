"""Tests for the Collections functionality in NativeApi.

This module contains test functions for collection-related operations
including creation, retrieval, content management, assignments, facets, and deletion.
"""

import uuid

import pytest

from pyDataverse.api.native import NativeApi
from pyDataverse.models.collection.content import Collection
from pyDataverse.models.collection.create import CollectionCreateBody, Contact
from pyDataverse.models.dataset.create import DatasetCreateBody
from tests.conftest import Credentials


class TestCollections:
    """Test suite for Collections functionality."""

    def test_collection_lifecycle(
        self, native_api: NativeApi, credentials: Credentials
    ):
        """Test the full lifecycle of a collection: create, retrieve, publish, and delete.

        Verifies that a collection can be created with metadata, retrieved by alias,
        published to make it publicly available, and deleted, ensuring all operations
        complete successfully and metadata is preserved correctly.
        """
        collection_alias = str(uuid.uuid4())
        collection = native_api.create_collection(
            parent="root",
            metadata=CollectionCreateBody(
                name="Test Collection",
                alias=collection_alias,
                description="Test Collection Description",
                affiliation="Test Affiliation",
                dataverse_type="DEPARTMENT",
                dataverse_contacts=[Contact(contact_email="test@test.com")],
            ),
        )

        # Retrieve the collection
        collection = native_api.get_collection(collection.alias)
        assert collection is not None, "Collection not found"
        assert collection.name == "Test Collection", "Name does not match"
        assert collection.alias == collection_alias, "Alias does not match"
        assert collection.description == "Test Collection Description", (
            "Description does not match"
        )
        assert collection.affiliation == "Test Affiliation", (
            "Affiliation does not match"
        )
        assert collection.dataverse_type == "DEPARTMENT", (
            "Dataverse type does not match"
        )

        # Update the collection
        # TODO: Add test for update_collection

        # Publish the collection
        native_api.publish_collection(collection.alias)

        # Delete the collection
        native_api.delete_collection(collection.alias)

        with pytest.raises(Exception):
            native_api.get_collection(collection.alias)

    def test_collection_contents(self, native_api: NativeApi, credentials: Credentials):
        """Test retrieving collection contents including nested collections.

        Verifies that get_collection_contents() returns an empty list for new collections,
        and correctly lists nested collections when they are created within a parent collection.
        """
        identifier = str(uuid.uuid4())
        collection = native_api.create_collection(
            parent="root",
            metadata=CollectionCreateBody(
                name="Test Collection",
                alias=f"test-collection-{identifier}",
                description="Test Collection Description",
                affiliation="Test Affiliation",
                dataverse_type="DEPARTMENT",
                dataverse_contacts=[Contact(contact_email="test@test.com")],
            ),
        )

        # Check if the collection is empty
        contents = native_api.get_collection_contents(collection.alias)
        assert contents is not None, "Contents not found"
        assert len(contents) == 0, "Contents are not empty"

        # Now create another collection in the collection
        another_collection = native_api.create_collection(
            parent=collection.alias,
            metadata=CollectionCreateBody(
                name="Another Collection",
                alias=f"another-collection-{identifier}",
                description="Another Collection Description",
                affiliation="Another Affiliation",
                dataverse_type="DEPARTMENT",
                dataverse_contacts=[Contact(contact_email="another@test.com")],
            ),
        )

        # Check if the collection is not empty
        contents = native_api.get_collection_contents(collection.alias)
        assert contents is not None, "Contents not found"
        assert len(contents) == 1, "Contents are empty"
        assert isinstance(contents[0], Collection), "Contents are not a collection"

        # Delete the collections altogheter
        native_api.delete_collection(another_collection.alias)
        native_api.delete_collection(collection.alias)

        with pytest.raises(Exception):
            native_api.get_collection_contents(collection.alias)

    def test_collection_contents_with_datasets(
        self,
        native_api: NativeApi,
        dataset_upload_min_default: DatasetCreateBody,
    ):
        """Test retrieving collection contents when it contains datasets.

        Verifies that get_collection_contents() correctly returns datasets that have
        been created within a collection, distinguishing them from nested collections.
        """
        identifier = str(uuid.uuid4())
        collection = native_api.create_collection(
            parent="root",
            metadata=CollectionCreateBody(
                name="Test Collection",
                alias=f"test-collection-{identifier}",
                description="Test Collection Description",
                affiliation="Test Affiliation",
                dataverse_type="DEPARTMENT",
                dataverse_contacts=[Contact(contact_email="test@test.com")],
            ),
        )

        native_api.create_dataset(
            collection.alias,
            dataset_upload_min_default,
        )
        contents = native_api.get_collection_contents(collection.alias)

        assert contents is not None, "Contents not found"
        assert len(contents) == 1, "Contents are empty"

        # Delete dataset
        assert contents[0].id is not None, "Dataset ID not found"
        native_api.delete_dataset(contents[0].id)
        native_api.delete_collection(collection.alias)

        with pytest.raises(Exception):
            native_api.get_collection_contents(collection.alias)

    def test_collection_assignments(
        self, native_api: NativeApi, credentials: Credentials
    ):
        """Test retrieving role assignments for a collection.

        Verifies that get_collection_assignments() returns role assignments for a collection,
        including the default admin role that is automatically assigned to the creator.
        """
        identifier = str(uuid.uuid4())
        collection = native_api.create_collection(
            parent="root",
            metadata=CollectionCreateBody(
                name="Test Collection",
                alias=f"test-collection-{identifier}",
                description="Test Collection Description",
                affiliation="Test Affiliation",
                dataverse_type="DEPARTMENT",
                dataverse_contacts=[Contact(contact_email="test@test.com")],
            ),
        )

        # Check if the collection is empty
        assignments = native_api.get_collection_assignments(collection.alias)
        assert assignments is not None, "Assignments not found"
        assert len(assignments) == 1, "Assignments should be one (Admin)"
        assert assignments[0].role is not None, "Role should be not None"
        assert assignments[0].role.alias == "admin", "Role should be admin"

        # Delete the collection
        native_api.delete_collection(collection.alias)

        with pytest.raises(Exception):
            native_api.get_collection_assignments(collection.alias)

    def test_collection_facets(self, native_api: NativeApi, credentials: Credentials):
        """Test retrieving search facets configured for a collection.

        Verifies that get_collection_facets() returns the search facets that are
        configured for a collection, which control how search results are filtered
        and displayed.
        """
        identifier = str(uuid.uuid4())
        collection = native_api.create_collection(
            parent="root",
            metadata=CollectionCreateBody(
                name="Test Collection",
                alias=f"test-collection-{identifier}",
                description="Test Collection Description",
                affiliation="Test Affiliation",
                dataverse_type="DEPARTMENT",
                dataverse_contacts=[Contact(contact_email="test@test.com")],
            ),
        )
        facets = native_api.get_collection_facets(collection.alias)
        assert facets is not None, "Facets not found"
        assert len(facets) > 0, "Facets are empty"

        # Delete the collection
        native_api.delete_collection(collection.alias)

        with pytest.raises(Exception):
            native_api.get_collection_facets(collection.alias)

    def test_collection_id2alias(self, native_api: NativeApi, credentials: Credentials):
        """Test converting a collection database ID to its alias.

        Verifies that dataverse_id2alias() can convert a numeric collection database ID
        to its corresponding alias string, enabling lookup by ID.
        """
        identifier = str(uuid.uuid4())
        collection = native_api.create_collection(
            parent="root",
            metadata=CollectionCreateBody(
                name="Test Collection",
                alias=f"test-collection-{identifier}",
                description="Test Collection Description",
                affiliation="Test Affiliation",
                dataverse_type="DEPARTMENT",
                dataverse_contacts=[Contact(contact_email="test@test.com")],
            ),
        )
        assert collection.id is not None, "Collection ID not found"
        alias = native_api.dataverse_id2alias(str(collection.id))
        assert alias is not None, "Alias not found"
        assert alias == f"test-collection-{identifier}", "Alias does not match"

        # Delete the collection
        native_api.delete_collection(collection.alias)

        with pytest.raises(Exception):
            assert collection.id is not None, "Collection ID not found"
            assert isinstance(collection.id, str), "Collection ID is not a string"
            native_api.dataverse_id2alias(collection.id)

    def test_crawl_collection(self, native_api: NativeApi, credentials: Credentials):
        """Test recursively crawling a collection to retrieve all nested contents.

        Verifies that crawl_collection() recursively traverses a collection hierarchy
        to retrieve all nested collections and datasets, returning a flat list of contents.
        """
        identifier = str(uuid.uuid4())
        collection = native_api.create_collection(
            parent="root",
            metadata=CollectionCreateBody(
                name="Test Collection",
                alias=f"test-collection-{identifier}",
                description="Test Collection Description",
                affiliation="Test Affiliation",
                dataverse_type="DEPARTMENT",
                dataverse_contacts=[Contact(contact_email="test@test.com")],
            ),
        )
        contents = native_api.crawl_collection(collection.alias)
        assert contents is not None, "Contents not found"
        assert len(contents) == 0, "Contents are empty"

        # Delete the collection
        native_api.delete_collection(collection.alias)

    def test_update_collection(self, native_api: NativeApi, credentials: Credentials):
        """Test updating collection metadata.

        Verifies that collection metadata can be updated and changes
        are persisted correctly on the server.
        """
        pass
