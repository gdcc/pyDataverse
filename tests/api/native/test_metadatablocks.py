"""Tests for the Metadatablocks functionality in NativeApi.

This module contains test functions for metadata block operations
including retrieving metadata block information and specifications.
"""

import uuid

from pyDataverse.api.native import NativeApi
from pyDataverse.models import metadatablocks
from pyDataverse.models.collection.create import CollectionCreateBody, Contact
from tests.conftest import Credentials


class TestMetadatablocks:
    """Test suite for Metadatablocks functionality.
    
    Tests cover retrieving metadata block information, both brief summaries
    and full specifications with field definitions, for global and collection-specific blocks.
    """

    def test_get_metadatablocks(
        self,
        native_api: NativeApi,
    ):
        """Test retrieving brief metadata about all available metadata blocks.
        
        Verifies that get_metadatablocks() returns a list of MetadatablockMeta objects
        containing brief information about all metadata blocks available on the server.
        """
        blocks = native_api.get_metadatablocks()

        assert blocks is not None, "Blocks are required"
        assert len(blocks) > 0, "Blocks are required"
        assert isinstance(blocks, list), "Blocks should be a list"
        assert all(
            isinstance(block, metadatablocks.MetadatablockMeta) for block in blocks
        ), "Blocks should be a list of MetadatablockMeta objects"

    def test_get_metadatablocks_full(
        self, native_api: NativeApi, credentials: Credentials
    ):
        """Test retrieving complete metadata block specifications with field definitions.
        
        Verifies that get_metadatablocks(full=True) returns a dictionary of complete
        MetadatablockSpecification objects with full field definitions and constraints.
        """
        blocks = native_api.get_metadatablocks(full=True)
        assert blocks is not None, "Blocks are required"
        assert len(blocks) > 0, "Blocks are required"
        assert isinstance(blocks, dict), "Blocks should be a dictionary"
        assert all(
            isinstance(block, metadatablocks.MetadatablockSpecification)
            for block in blocks.values()
        ), "Blocks should be a dictionary of MetadatablockSpecification objects"

    def test_get_metadatablocks_for_collection(
        self, native_api: NativeApi, credentials: Credentials
    ):
        """Test retrieving brief metadata blocks configured for a specific collection.
        
        Verifies that get_metadatablocks(collection_alias=...) returns metadata blocks
        that are specifically enabled for a given collection, which may differ from
        the global set of available blocks.
        """
        # First, create a collection
        alias = f"test-collection-{str(uuid.uuid4())}"
        native_api.create_collection(
            parent="root",
            metadata=CollectionCreateBody(
                name="Test Collection",
                alias=alias,
                description="Test Collection Description",
                affiliation="Test Affiliation",
                dataverse_type="DEPARTMENT",
                dataverse_contacts=[Contact(contact_email="test@test.com")],
            ),
        )

        # Now retrieve the metadata blocks for the collection
        blocks = native_api.get_metadatablocks(collection_alias=alias)

        assert blocks is not None, "Blocks are required"
        assert len(blocks) > 0, "Blocks are required"
        assert isinstance(blocks, list), "Blocks should be a list"
        assert all(
            isinstance(block, metadatablocks.MetadatablockMeta) for block in blocks
        ), "Blocks should be a list of MetadatablockMeta objects"

    def test_get_metadatablocks_for_collection_full(
        self, native_api: NativeApi, credentials: Credentials
    ):
        """Test retrieving complete metadata block specifications for a specific collection.
        
        Verifies that get_metadatablocks(collection_alias=..., full=True) returns complete
        metadata block specifications with full field definitions for collection-specific blocks.
        """
        # First, create a collection
        alias = f"test-collection-{str(uuid.uuid4())}"
        native_api.create_collection(
            parent="root",
            metadata=CollectionCreateBody(
                name="Test Collection",
                alias=alias,
                description="Test Collection Description",
                affiliation="Test Affiliation",
                dataverse_type="DEPARTMENT",
                dataverse_contacts=[Contact(contact_email="test@test.com")],
            ),
        )

        # Now retrieve the metadata blocks for the collection
        blocks = native_api.get_metadatablocks(
            collection_alias=alias,
            full=True,
        )

        assert blocks is not None, "Blocks are required"
        assert len(blocks) > 0, "Blocks are required"

    def test_get_metadatablock(self, native_api: NativeApi, credentials: Credentials):
        """Test retrieving a single metadata block with full field specifications by name.
        
        Verifies that get_metadatablock() returns a complete MetadatablockSpecification
        for a specific metadata block (e.g., "citation") including all field definitions,
        types, and validation rules.
        """
        metadata_block = native_api.get_metadatablock("citation")
        assert metadata_block is not None, "Metadata block is required"
        assert metadata_block.name == "citation", "Metadata block name should match"
        assert metadata_block.display_name == "Citation Metadata", (
            "Metadata block display name should match"
        )
        assert metadata_block.display_on_create is not None, (
            "Metadata block display on create should be a boolean"
        )
        assert metadata_block.fields is not None, (
            "Metadata block fields should be a dictionary"
        )
        assert len(metadata_block.fields) > 0, (
            "Metadata block fields should be a non-empty dictionary"
        )
        assert all(
            isinstance(field, metadatablocks.MetadataField)
            for field in metadata_block.fields.values()
        ), "Metadata block fields should be a dictionary of MetadataField objects"
