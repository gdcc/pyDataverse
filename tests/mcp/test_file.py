"""Tests for the file MCP tools.

All tests use the shared mcp_client to emulate a client calling tools via the
server. Requires a dataset with files for tests that need real data.
"""

import io
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from fastmcp.exceptions import ToolError
from mcp.types import ImageContent, TextContent
from PIL import Image
from toon_format import encode

from pyDataverse.mcp.file import MAX_FILE_SIZE
from tests.conftest import DatasetFactory

pytest.importorskip("fastmcp.client")

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport

PDF_PATH = Path("tests/data/mcp/document.pdf")
IPYNB_PATH = Path("tests/data/mcp/notebook.ipynb")


def _create_tabular_file() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob"],
            "age": [25, 30],
        },
    )


class TestReadFile:
    """Test suite for Read_File_Content tool."""

    async def test_read_image(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test reading image file returns ImageContent."""
        ds = dataset()

        # Generate a random 100x100 RGB image
        random_data = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        image = Image.fromarray(random_data)

        # Save to bytes buffer
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="JPEG")
        img_bytes = img_buffer.getvalue()

        with ds.open("image.jpg", "wb") as file:
            file.write(img_bytes)

        ds.publish()

        result = await mcp_client.call_tool(
            name="Read_File_Content",
            arguments={
                "identifier": ds.persistent_identifier,
                "path": "image.jpg",
                "base_url": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Content should be returned"

        content = result.content[0]

        assert isinstance(content, ImageContent), "Content is not a ImageContent"
        assert content.mimeType == "image/jpeg", "Content should be a JPEG image"
        assert content.data is not None, "Content should contain data"
        assert len(content.data) > 0, "Content should contain data"

    async def test_read_pdf(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test reading PDF returns text per page."""
        ds = dataset()

        with ds.open("document.pdf", "wb") as file:
            file.write(PDF_PATH.read_bytes())

        ds.publish()

        result = await mcp_client.call_tool(
            name="Read_File_Content",
            arguments={
                "identifier": ds.persistent_identifier,
                "path": "document.pdf",
                "base_url": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Content should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert "Dummy PDF file" in content.text, "Content should contain PDF content"

    async def test_read_ipynb(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test reading Jupyter notebook returns converted script."""
        ds = dataset()

        with ds.open("notebook.ipynb", "wb") as file:
            file.write(IPYNB_PATH.read_bytes())

        ds.publish()

        result = await mcp_client.call_tool(
            name="Read_File_Content",
            arguments={
                "identifier": ds.persistent_identifier,
                "path": "notebook.ipynb",
                "base_url": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Content should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert 'print("Hello, world!")' in content.text, (
            "Content should contain IPython notebook content"
        )

    async def test_file_size_limit_exceeded(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test RuntimeError when file exceeds MAX_FILE_SIZE."""

        ds = dataset()
        fn = "file.txt"

        with ds.open(fn, "wb") as file:
            file.write(b"a" * 2 * MAX_FILE_SIZE)

        ds.publish()

        with pytest.raises(ToolError):
            await mcp_client.call_tool(
                name="Read_File_Content",
                arguments={
                    "identifier": ds.persistent_identifier,
                    "path": fn,
                    "base_url": None,
                },
            )

        # Clean up the large file
        ds.files[fn].delete()

    async def test_non_existent_path(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test KeyError when file path does not exist."""
        ds = dataset()
        fn = "file.txt"

        with pytest.raises(ToolError):
            await mcp_client.call_tool(
                name="Read_File_Content",
                arguments={
                    "identifier": ds.persistent_identifier,
                    "path": fn,
                    "base_url": None,
                },
            )


class TestReadTabular:
    """Test suite for Read_Tabular_File tool."""

    async def test_read_with_n_rows(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test reading first N rows."""
        ds = dataset()
        fn = "file.tab"
        df = _create_tabular_file()

        with ds.open(fn, "w") as file:
            file.write(df.to_csv(index=False, sep="\t"))

        ds.publish()

        result = await mcp_client.call_tool(
            name="Read_Tabular_File",
            arguments={
                "identifier": ds.persistent_identifier,
                "path": fn,
                "base_url": None,
                "n_rows": 1,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Content should be returned"

        content = result.content[0]
        expected = encode([df.to_dict(orient="records")[0]])

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert content.text == expected, "Content should be the first row of the file"

    async def test_read_full_file(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test reading entire file."""
        ds = dataset()
        fn = "file.txt"
        expected = "Hello, world!"

        with ds.open(fn, "w") as file:
            file.write(expected)

        ds.publish()

        result = await mcp_client.call_tool(
            name="Read_File_Content",
            arguments={
                "identifier": ds.persistent_identifier,
                "path": fn,
                "base_url": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Content should be returned"

        content = result.content[0]

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert content.text == expected, f"Content should be {expected}"

    async def test_summarize_mode(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test summarize=True returns describe() stats."""
        ds = dataset()
        fn = "file.tab"
        df = _create_tabular_file()

        with ds.open(fn, "w") as file:
            file.write(df.to_csv(index=False, sep="\t"))

        ds.publish()

        result = await mcp_client.call_tool(
            name="Read_Tabular_File",
            arguments={
                "identifier": ds.persistent_identifier,
                "path": fn,
                "base_url": None,
                "summarize": True,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Content should be returned"

        content = result.content[0]
        expected = encode(df.describe().to_dict(orient="records"))

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert content.text == expected, f"Content should be {expected}"

    async def test_non_tabular_file(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test error when file is not tabular."""
        ds = dataset()
        fn = "file.txt"
        with ds.open(fn, "w") as file:
            file.write("Hello, world!")

        ds.publish()

        with pytest.raises(ToolError):
            await mcp_client.call_tool(
                name="Read_Tabular_File",
                arguments={
                    "identifier": ds.persistent_identifier,
                    "path": fn,
                    "base_url": None,
                },
            )


class TestTabularSchema:
    """Test suite for Get_Tabular_File_Schema tool."""

    async def test_valid_schema(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test schema for valid tabular file."""
        ds = dataset()
        fn = "file.tab"
        df = _create_tabular_file()

        with ds.open(fn, "w") as file:
            file.write(df.to_csv(index=False, sep="\t"))

        ds.publish()

        result = await mcp_client.call_tool(
            name="Get_Tabular_File_Schema",
            arguments={
                "identifier": ds.persistent_identifier,
                "path": fn,
                "base_url": None,
            },
        )

        assert result is not None
        assert len(result.content) > 0, "Content should be returned"

        content = result.content[0]
        expected = encode({"name": "object", "age": "int64"})

        assert isinstance(content, TextContent), "Content is not a TextContent"
        assert content.text == expected, f"Content should be {expected}"

    async def test_non_tabular_file(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test error when file is not tabular."""
        ds = dataset()
        fn = "file.txt"
        with ds.open(fn, "w") as file:
            file.write("Hello, world!")

        ds.publish()

        with pytest.raises(ToolError):
            await mcp_client.call_tool(
                name="Get_Tabular_File_Schema",
                arguments={
                    "identifier": ds.persistent_identifier,
                    "path": fn,
                    "base_url": None,
                },
            )

    async def test_missing_file(
        self,
        mcp_client: Client[FastMCPTransport],
        dataset: DatasetFactory,
    ):
        """Test KeyError when file path does not exist."""
        ds = dataset()
        fn = "file.txt"
        with pytest.raises(ToolError):
            await mcp_client.call_tool(
                name="Get_Tabular_File_Schema",
                arguments={
                    "identifier": ds.persistent_identifier,
                    "path": fn,
                    "base_url": None,
                },
            )
