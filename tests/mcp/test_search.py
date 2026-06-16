"""Tests for the search MCP tools.

All tests use the shared mcp_client to emulate a client calling tools via the
server.
"""

import uuid

import pytest
from mcp.types import TextContent

from pyDataverse.dataverse.dataset import Dataset
from tests.conftest import CollectionFactory

pytest.importorskip("fastmcp.client")

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


class TestSearch:
    """Test suite for Search_Dataverse tool."""

    async def test_basic_search(
        self,
        mcp_client: Client[FastMCPTransport],
        minimal_dataset: Dataset,
    ):
        """Test search with simple query."""

        title = str(uuid.uuid4())
        minimal_dataset.title = title
        minimal_dataset.upload_to_collection("root")
        minimal_dataset.publish()

        result = await mcp_client.call_tool(
            name="Search_Dataverse",
            arguments={"query": title},
        )
        assert result is not None
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert title in content.text, f"Title {title} not in content"

    async def test_collection_scoped(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
        minimal_dataset: Dataset,
    ):
        """Test search scoped to specific collection."""
        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        minimal_dataset.title = str(uuid.uuid4())
        minimal_dataset.upload_to_collection(collection_alias)
        minimal_dataset.publish()

        result = await mcp_client.call_tool(
            name="Search_Dataverse",
            arguments={
                "query": minimal_dataset.title,
                "collection": collection_alias,
            },
        )
        assert result is not None
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]
        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert minimal_dataset.title in content.text, (
            f"Title {minimal_dataset.title} not in content"
        )

    async def test_filter_by_dataset(
        self,
        mcp_client: Client[FastMCPTransport],
        collection: CollectionFactory,
        minimal_dataset: Dataset,
    ):
        """Test filtering results to datasets only."""

        collection_alias = str(uuid.uuid4())
        col = collection(collection_alias)
        col.publish()

        minimal_dataset.title = str(uuid.uuid4())
        minimal_dataset.upload_to_collection(collection_alias)
        minimal_dataset.publish()

        result = await mcp_client.call_tool(
            name="Search_Dataverse",
            arguments={"query": minimal_dataset.title, "filter_by": "dataset"},
        )

        assert result is not None
        assert len(result.content) > 0, "No content returned"

        content = result.content[0]
        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert minimal_dataset.title in content.text, (
            f"Title {minimal_dataset.title} not in content"
        )
