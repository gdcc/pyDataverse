"""Tests for the dataverse MCP tools.

All tests use the shared mcp_client to emulate a client calling tools via the
server.
"""

import re

import pytest
from mcp.types import TextContent

from tests.conftest import Credentials

pytest.importorskip("fastmcp.client")

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


class TestGetMetrics:
    """Test suite for Dataverse_Metrics tool."""

    async def test_metrics_structure(self, mcp_client: Client[FastMCPTransport]):
        """Test that metrics are returned in TOON format."""
        result = await mcp_client.call_tool(
            name="Dataverse_Metrics",
            arguments={},
        )

        assert result is not None
        assert len(result.content) > 0, "Metrics should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert re.search(
            r"collections_by_subject\[\d+\]\{subject,count\}",
            content.text,
        ), "Content should contain metrics"

    async def test_base_url_override(
        self,
        mcp_client: Client[FastMCPTransport],
        credentials: Credentials,
    ):
        """Test using base_url to target alternate Dataverse."""
        result = await mcp_client.call_tool(
            name="Dataverse_Metrics",
            arguments={"base_url": credentials.base_url},
        )

        assert result is not None
        assert len(result.content) > 0, "Metrics should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert re.search(
            r"collections_by_subject\[\d+\]\{subject,count\}",
            content.text,
        ), "Content should contain metrics"
