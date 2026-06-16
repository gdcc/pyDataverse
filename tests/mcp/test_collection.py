"""Tests for the collection MCP tools.

All tests use the shared mcp_client to emulate a client calling tools via the
server. The server provides the required context via middleware.
"""

import uuid

import pytest
from fastmcp.exceptions import ToolError
from mcp.types import TextContent

from pyDataverse.dataverse.dataset import Dataset
from tests.conftest import CollectionFactory, Credentials

pytest.importorskip("fastmcp.client")

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


class TestGetCollectionMetadata:
    """Test suite for Get_Collection_Metadata tool."""

    async def test_root_collection(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
    ):
        """Test retrieving metadata for root collection."""
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        result = await mcp_client.call_tool(
            name="Get_Collection_Metadata",
            arguments={"collection": collection_alias, "base_url": None},
        )
        assert result is not None, "No result returned"
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert collection_alias in content.text, "Collection alias not in content"

    async def test_non_existent_collection(self, mcp_client: Client[FastMCPTransport]):
        """Test behaviour when collection does not exist."""

        with pytest.raises(ToolError):
            await mcp_client.call_tool(
                name="Get_Collection_Metadata",
                arguments={"collection": "non-existent-collection", "base_url": None},
            )

    async def test_base_url_override(
        self,
        mcp_client: Client[FastMCPTransport],
        credentials: Credentials,
    ):
        """Test using base_url to target alternate Dataverse."""
        result = await mcp_client.call_tool(
            name="Get_Collection_Metadata",
            arguments={"collection": "root", "base_url": credentials.base_url},
        )
        assert result is not None, "No result returned"
        assert len(result.content) > 0, "No content returned"


class TestListContent:
    """Test suite for List_Content_of_Collection tool."""

    async def test_filter_by_dataset(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
        minimal_dataset: Dataset,
    ):
        """Test filtering content to datasets only."""
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        minimal_dataset.upload_to_collection(collection_alias)
        minimal_dataset.publish()

        assert minimal_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="List_Content_of_Collection",
            arguments={
                "collection": collection_alias,
                "filter_by": "dataset",
                "base_url": None,
            },
        )
        assert result is not None, "No result returned"
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert minimal_dataset.title in content.text, "Dataset title not in content"
        assert minimal_dataset.persistent_identifier in content.text, (
            "Dataset persistent identifier not in content"
        )

    async def test_filter_collection_by_collection(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
    ):
        """Test filtering content to collections only."""
        # Create a collection
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        # Then, create a subcollection
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

        result = await mcp_client.call_tool(
            name="List_Content_of_Collection",
            arguments={
                "collection": collection_alias,
                "filter_by": "collection",
                "base_url": None,
            },
        )

        assert result is not None, "No result returned"
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]
        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert subcollection_alias in content.text, "Subcollection alias not in content"
        assert subcollection.name in content.text, "Subcollection name not in content"

    async def test_empty_collection(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
    ):
        """Test listing content of empty collection."""
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        result = await mcp_client.call_tool(
            name="List_Content_of_Collection",
            arguments={
                "collection": collection_alias,
                "filter_by": None,
                "base_url": None,
            },
        )

        assert result is not None, "No result returned"
        assert len(result.content) > 0, "Content should not be empty"

        content = result.content[0]
        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert content.text == "[0]:", "Content should be empty"


class TestGetGraphSummary:
    """Test suite for Knowledge_Graph_Summary tool."""

    async def test_oai_ore_format(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
        minimal_dataset: Dataset,
    ):
        """Test graph summary with croissant format."""
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        minimal_dataset.upload_to_collection(collection_alias)
        minimal_dataset.publish()

        assert minimal_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="Knowledge_Graph_Summary",
            arguments={
                "collection": collection_alias,
                "format": "OAI_ORE",
                "base_url": None,
            },
        )

        assert result is not None, "No result returned"
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert minimal_dataset.title in content.text, "Dataset title not in content"

    async def test_depth_levels(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
        minimal_dataset: Dataset,
    ):
        """Test different depth values affect graph scope."""
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        minimal_dataset.upload_to_collection(collection_alias)
        minimal_dataset.publish()

        assert minimal_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="Knowledge_Graph_Summary",
            arguments={
                "collection": collection_alias,
                "format": "semantic_api",
                "base_url": None,
                "depth": 1,
            },
        )

        assert result is not None, "No result returned"
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert minimal_dataset.title in content.text, "Dataset title not in content"

    async def test_empty_collection_graph(self, mcp_client: Client[FastMCPTransport]):
        """Test graph summary for collection with no data."""
        pass


class TestQuerySparql:
    """Test suite for Query_Knowledge_Graph tool."""

    async def test_single_query(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
        minimal_dataset: Dataset,
    ):
        """Test executing a single SPARQL query."""
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        minimal_dataset.upload_to_collection(collection_alias)
        minimal_dataset.publish()

        assert minimal_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="Query_Knowledge_Graph",
            arguments={
                "collection": collection_alias,
                "format": "semantic_api",
                "queries": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 1",
                "base_url": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]
        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "[1]{s,p,o}:" in content.text, "Content should contain a result"

    async def test_batch_queries(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
        minimal_dataset: Dataset,
    ):
        """Test executing multiple named SPARQL queries."""
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        minimal_dataset.upload_to_collection(collection_alias)
        minimal_dataset.publish()

        assert minimal_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="Query_Knowledge_Graph",
            arguments={
                "collection": collection_alias,
                "format": "semantic_api",
                "base_url": None,
                "queries": {
                    "datasets": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 1",
                    "count": "SELECT (COUNT(?s) AS ?c) WHERE { ?s ?p ?o }",
                },
            },
        )

        assert result is not None
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]
        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "datasets" in content.text, "Datasets not in content"
        assert "count" in content.text, "Count not in content"
        assert "[1]{s,p,o}:" in content.text, "Content should contain a result"
        assert "[1]{c}:" in content.text, "Content should contain a result"

    async def test_invalid_sparql(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
        minimal_dataset: Dataset,
    ):
        """Test error handling for malformed SPARQL."""
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        minimal_dataset.upload_to_collection(collection_alias)
        minimal_dataset.publish()

        assert minimal_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="Query_Knowledge_Graph",
            arguments={
                "collection": collection_alias,
                "format": "semantic_api",
                "base_url": None,
                "queries": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 1 INVALID",
            },
        )

        assert result is not None
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "error" in content.text, "Error not in content"

    async def test_empty_results(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
        minimal_dataset: Dataset,
    ):
        """Test handling of query returning no results."""

        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        minimal_dataset.upload_to_collection(collection_alias)
        minimal_dataset.publish()

        assert minimal_dataset.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="Query_Knowledge_Graph",
            arguments={
                "collection": collection_alias,
                "format": "semantic_api",
                "base_url": None,
                "queries": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 0",
            },
        )

        assert result is not None
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]
        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "[0]:" in content.text, "Content should contain a result"
