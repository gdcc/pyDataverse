"""
info.py — Dataverse Info & Metadata Endpoints

This module provides lightweight wrappers around Dataverse's informational
endpoints, such as version, server status, and metadata block listings.

These endpoints do not modify data and are safe to call frequently.
"""

from __future__ import annotations

from typing import Any

from ..transport import HttpClient


class InfoEndpoint:
    """
    Wrapper for Dataverse informational endpoints.

    Example:
        info = InfoEndpoint(http)
        version = info.version()
    """

    def __init__(self, http: HttpClient) -> None:
        self.http = http

    # ------------------------------------------------------------------
    # Basic server info
    # ------------------------------------------------------------------

    def version(self) -> dict[str, Any]:
        """
        Returns Dataverse version information.

        GET /api/info/version
        """
        return self.http.get("/api/info/version")

    def server(self) -> dict[str, Any]:
        """
        Returns general server information.

        GET /api/info/server
        """
        return self.http.get("/api/info/server")

    def metrics(self) -> dict[str, Any]:
        """
        Returns Dataverse metrics (datasets, files, downloads, etc.)

        GET /api/info/metrics
        """
        return self.http.get("/api/info/metrics")

    # ------------------------------------------------------------------
    # Metadata blocks
    # ------------------------------------------------------------------

    def list_metadata_blocks(self) -> list[dict[str, Any]]:
        """
        Returns a list of metadata blocks available on the server.

        GET /api/metadata
        """
        return self.http.get("/api/metadata")

    def get_metadata_block(self, block_name: str) -> dict[str, Any]:
        """
        Returns details for a specific metadata block.

        GET /api/metadata/{block_name}
        """
        return self.http.get(f"/api/metadata/{block_name}")
