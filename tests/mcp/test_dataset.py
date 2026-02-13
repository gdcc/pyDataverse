"""Tests for the dataset MCP tools.

All tests use the shared mcp_client to emulate a client calling tools via the
server. Requires a known dataset identifier for tests that need real data.
"""

import pandas as pd
import pytest
from fastmcp.exceptions import ToolError
from mcp.types import TextContent

from tests.conftest import DatasetFactory

pytest.importorskip("fastmcp.client")

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


class TestGetDataset:
    """Test suite for Get_Dataset_Metadata tool."""

    async def test_dataset_full_metadata(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test retrieving full dataset metadata."""
        ds = dataset()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="Get_Dataset_Metadata",
            arguments={
                "identifier": ds.persistent_identifier,
                "full": True,
                "base_url": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Dataset metadata should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert ds.title in content.text, "Dataset title not in content"
        assert ds.persistent_identifier in content.text, (
            "Dataset persistent identifier not in content"
        )

    async def test_summary_metadata(
        self, mcp_client: Client[FastMCPTransport], dataset
    ):
        """Test retrieving summary metadata."""
        ds = dataset()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="Get_Dataset_Metadata",
            arguments={
                "identifier": ds.persistent_identifier,
                "full": False,
                "base_url": None,
            },
        )
        assert result is not None
        assert len(result.content) > 0, "Dataset metadata should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert ds.title in content.text, "Dataset title not in content"
        assert ds.persistent_identifier in content.text, (
            "Dataset persistent identifier not in content"
        )

    async def test_persistent_identifier(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test with persistent identifier (DOI)."""
        ds = dataset()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="Get_Dataset_Metadata",
            arguments={
                "identifier": ds.persistent_identifier,
                "full": False,
                "base_url": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Dataset metadata should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert ds.title in content.text, "Dataset title not in content"
        assert ds.persistent_identifier in content.text, (
            "Dataset persistent identifier not in content"
        )

    async def test_numeric_identifier(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test with numeric Dataverse ID."""
        ds = dataset()

        assert ds.identifier is not None, "Dataset identifier not initialized"

        result = await mcp_client.call_tool(
            name="Get_Dataset_Metadata",
            arguments={
                "identifier": ds.identifier,
                "full": False,
                "base_url": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Dataset metadata should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert ds.title in content.text, "Dataset title not in content"
        assert str(ds.identifier) in content.text, "Dataset identifier not in content"

    async def test_non_existent_dataset(self, mcp_client: Client[FastMCPTransport]):
        """Test behaviour when dataset does not exist."""

        with pytest.raises(ToolError):
            await mcp_client.call_tool(
                name="Get_Dataset_Metadata",
                arguments={
                    "identifier": "nonexistent",
                    "full": False,
                    "base_url": None,
                },
            )

    async def test_available_metadatablocks_in_summary(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test that summary includes available_metadatablocks."""
        ds = dataset()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        result = await mcp_client.call_tool(
            name="Get_Dataset_Metadata",
            arguments={
                "identifier": ds.persistent_identifier,
                "full": False,
                "base_url": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Dataset metadata should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "available_metadatablocks" in content.text, (
            "Available metadata blocks not in content"
        )
        assert "citation" in content.text, "Citation not in content"


class TestListFiles:
    """Test suite for List_Files_in_Dataset tool."""

    async def test_all_files(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test listing all files in dataset."""
        ds = dataset()

        with ds.open("file.txt", "w") as file:
            file.write("This is a test file.")

        with ds.open("data/file.txt", "w") as file:
            file.write("This is a test file.")

        ds.publish()

        result = await mcp_client.call_tool(
            name="List_Files_in_Dataset",
            arguments={
                "identifier": ds.persistent_identifier,
                "only_tabular": False,
                "base_url": None,
                "filter_mime_types": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Dataset files should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "file.txt" in content.text, "File not in content"
        assert "data/file.txt" in content.text, "File not in content"
        assert "text/plain" in content.text, "File MIME type not in content"

    async def test_only_tabular(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test filtering to tabular files only."""
        ds = dataset()

        with ds.open("data/file.tab", "w") as file:
            df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
            file.write(df.to_csv(index=False, sep="\t"))

        ds.publish()

        result = await mcp_client.call_tool(
            name="List_Files_in_Dataset",
            arguments={
                "identifier": ds.persistent_identifier,
                "only_tabular": True,
                "base_url": None,
                "filter_mime_types": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Dataset files should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "file.tab" in content.text, "File not in content"
        assert "text/tab-separated-values" in content.text, (
            "File MIME type not in content"
        )

    async def test_filter_mime_types(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test filtering by MIME type list."""
        ds = dataset()

        with ds.open("some_script.py", "w") as file:
            file.write("print('Hello, world!')")

        ds.publish()

        result = await mcp_client.call_tool(
            name="List_Files_in_Dataset",
            arguments={
                "identifier": ds.persistent_identifier,
                "only_tabular": False,
                "base_url": None,
                "filter_mime_types": ["text/x-python"],
            },
        )

        assert result is not None, "No result returned"
        assert len(result.content) > 0, "Dataset files should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "some_script.py" in content.text, "File not in content"
        assert "text/x-python" in content.text, "File MIME type not in content"

    async def test_empty_dataset(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test listing files in empty dataset."""
        ds = dataset()
        ds.publish()

        result = await mcp_client.call_tool(
            name="List_Files_in_Dataset",
            arguments={
                "identifier": ds.persistent_identifier,
                "only_tabular": False,
                "base_url": None,
                "filter_mime_types": None,
            },
        )

        assert result is not None, "No result returned"
        assert len(result.content) > 0, "Dataset files should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "[0]:" in content.text, "Content should contain a result"

    async def test_non_existent_dataset(self, mcp_client: Client[FastMCPTransport]):
        """Test behaviour when dataset does not exist."""
        with pytest.raises(ToolError):
            await mcp_client.call_tool(
                name="List_Files_in_Dataset",
                arguments={
                    "identifier": "nonexistent",
                    "only_tabular": False,
                    "base_url": None,
                    "filter_mime_types": None,
                },
            )
