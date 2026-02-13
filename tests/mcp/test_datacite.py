"""Tests for the DataCite MCP tools.

All tests use the shared mcp_client to emulate a client calling tools via the
server.
"""

import re

import httpx
import pytest
from mcp.types import TextContent

from tests.conftest import Credentials, DatasetFactory

pytest.importorskip("fastmcp.client")

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport

from pyDataverse.mcp.datacite import Attributes, DataCite, DataItem, Title


class TestDataCiteModels:
    """Tests for the underlying DataCite classes (no MCP client)."""

    def test_data_item_title_from_attributes(
        self,
        credentials: Credentials,
        dataset: DatasetFactory,
    ):
        """DataItem extracts title from attributes.titles."""

        ds = dataset()
        ds.publish()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        item = DataItem(
            attributes=Attributes(
                url=f"{credentials.base_url.rstrip('/')}/dataset?persistentId={ds.persistent_identifier}",
                titles=[Title(title=ds.title)],
            )
        )

        assert item.title == ds.title

    def test_data_item_title_empty(self, credentials: Credentials):
        """DataItem returns None when no titles."""
        item = DataItem(attributes=Attributes(url="https://example.com", titles=None))
        assert item.title is None

    def test_data_item_base_url(
        self,
        credentials: Credentials,
        dataset: DatasetFactory,
    ):
        """DataItem extracts base URL from attributes.url."""
        ds = dataset()
        ds.publish()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        item = DataItem(
            attributes=Attributes(
                url=f"{credentials.base_url.rstrip('/')}/dataset?persistentId={ds.persistent_identifier}",
            )
        )
        assert item.base_url == credentials.base_url

    def test_data_item_base_url_none(self):
        """DataItem returns None when url is None."""
        item = DataItem(attributes=Attributes(url=None))
        assert item.base_url is None

    def test_data_item_persistent_identifier(
        self,
        credentials: Credentials,
        dataset: DatasetFactory,
    ):
        """DataItem extracts persistentId from URL query."""
        ds = dataset()
        ds.publish()

        assert ds.persistent_identifier is not None, (
            "Dataset persistent identifier not initialized"
        )

        item = DataItem(
            attributes=Attributes(
                url=f"{credentials.base_url.rstrip('/')}/dataset?persistentId={ds.persistent_identifier}",
            )
        )
        assert item.persistent_identifier == ds.persistent_identifier

    def test_data_item_persistent_identifier_none(self):
        """DataItem returns None when url has no persistentId."""
        item = DataItem(attributes=Attributes(url="https://example.com/dataset"))
        assert item.persistent_identifier is None

    def test_datacite_filter_none_urls(
        self,
        credentials: Credentials,
        dataset: DatasetFactory,
    ):
        """DataCite filter_none_urls validator removes items without URL."""
        ds = dataset()
        ds.publish()

        assert ds.persistent_identifier is not None

        expected_url = f"{credentials.base_url.rstrip('/')}/dataset?persistentId={ds.persistent_identifier}"
        data_cite = DataCite(
            data=[
                DataItem(attributes=Attributes(url=expected_url)),
                DataItem(attributes=Attributes(url=None)),
            ]
        )

        assert len(data_cite.data) == 1
        assert data_cite.data[0].attributes.url == expected_url

    @pytest.mark.asyncio
    async def test_is_dataverse_async_true(self, credentials: Credentials):
        """_is_dataverse_async returns True for valid Dataverse response."""

        async with httpx.AsyncClient() as client:
            assert await DataCite._is_dataverse_async(client, credentials.base_url), (
                "Dataverse instance should be detected"
            )

    @pytest.mark.asyncio
    async def test_is_dataverse_async_false_not_ok(self):
        """_is_dataverse_async returns False when status is not OK."""

        async with httpx.AsyncClient() as client:
            assert (
                await DataCite._is_dataverse_async(
                    client, "https://example.com/dataset"
                )
                is False
            ), "Dataverse instance should not be detected"

    @pytest.mark.asyncio
    async def test_filter_dataverse_urls_empty(self):
        """filter_dataverse_urls returns empty when no URLs to check."""
        data_cite = DataCite(data=[])
        result = await data_cite.filter_dataverse_urls()
        assert len(result.data) == 0, "DataCite should be empty"


class TestSearchDataCite:
    """Test suite for Search_DataCite tool."""

    async def test_search_valid_query(self, mcp_client: Client[FastMCPTransport]):
        """Test search with valid query returns results."""
        result = await mcp_client.call_tool(
            name="Search_DataCite",
            arguments={"query": "cephalexin neural ode"},
        )

        assert result is not None
        assert len(result.content) > 0, "DataCite should have results"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert re.search(
            r"data\[\d+\]\{title,base_url,persistent_identifier\}", content.text
        ), "Content should contain data items"

    async def test_search_empty_results(self, mcp_client: Client[FastMCPTransport]):
        """Test search with query that returns no results."""
        result = await mcp_client.call_tool(
            name="Search_DataCite",
            arguments={"query": "somegibberishthatdoesnotexist"},
        )
        assert result is not None
        assert len(result.content) > 0, "DataCite should have results"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "data[0]:" in content.text, "Content should contain data items"

    async def test_search_pagination(self, mcp_client: Client[FastMCPTransport]):
        """Test pagination with pages parameter."""
        result = await mcp_client.call_tool(
            name="Search_DataCite",
            arguments={"query": "cephalexin neural ode", "pages": 8},
        )
        assert result is not None
        assert len(result.content) > 0, "DataCite should have results"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert re.search(
            r"data\[\d+\]\{title,base_url,persistent_identifier\}", content.text
        ), "Content should contain data items"
