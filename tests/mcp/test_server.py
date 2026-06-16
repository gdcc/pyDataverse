"""Tests for the DataverseMCP server configuration.

All tests use the shared mcp_client to verify the server is correctly configured.
Server setup (middleware, tool registration) is tested implicitly via tool calls.
"""

import pytest

pytest.importorskip("fastmcp.client")

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport

EXPECTED_TOOLS = {
    "Dataverse_Metrics",
    "Get_Dataset_Metadata",
    "List_Files_in_Dataset",
    "Read_Tabular_File",
    "Read_File_Content",
    "Get_Tabular_File_Schema",
    "Get_Collection_Metadata",
    "List_Content_of_Collection",
    "Knowledge_Graph_Summary",
    "Query_Knowledge_Graph",
    "Search_Dataverse",
    "Search_DataCite",
}


class TestServerConfiguration:
    """Test suite for server tool registration."""

    async def test_all_expected_tools_registered(self, mcp_client: Client[FastMCPTransport]):
        """Test that all expected tools are registered."""
        tools = await mcp_client.list_tools()
        tool_names = {t.name for t in tools}
        assert EXPECTED_TOOLS.issubset(tool_names), (
            f"Missing tools: {EXPECTED_TOOLS - tool_names}"
        )
