"""
client.py — High-level Dataverse API client

This module provides a clean, modern interface for interacting with a Dataverse
installation. It wraps lower-level endpoint modules (datasets, files, search, etc.)
and exposes a unified, ergonomic API surface.

Intended to replace the monolithic NativeApi/DataAccessApi classes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .endpoints.datasets import DatasetEndpoint
from .endpoints.files import FileEndpoint
from .endpoints.info import InfoEndpoint
from .endpoints.search import SearchEndpoint
from .transport import HttpClient


@dataclass
class DataverseConfig:
    base_url: str
    api_token: str | None = None
    timeout: int = 30


class DataverseClient:
    """
    High-level Dataverse client.

    Provides:
    - Dataset operations
    - File operations
    - Search
    - Metadata/info endpoints

    Example:
        client = DataverseClient("https://demo.dataverse.org", api_token="XYZ")
        ds = client.endpoints.datasets.create("root", metadata)
        client.files.upload(ds.id, "myfile.csv")
    """

    def __init__(
        self,
        base_url: str,
        api_token: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.config = DataverseConfig(
            base_url=base_url.rstrip("/"),
            api_token=api_token,
            timeout=timeout,
        )

        # Shared HTTP transport layer
        self.http = HttpClient(
            base_url=self.config.base_url,
            api_token=self.config.api_token,
            timeout=self.config.timeout,
        )

        # Endpoint modules
        self.datasets = DatasetEndpoint(self.http)
        self.files = FileEndpoint(self.http)
        self.search = SearchEndpoint(self.http)
        self.info = InfoEndpoint(self.http)

    # ----------------------------------------------------------------------
    # High-level convenience methods
    # ----------------------------------------------------------------------

    def create_dataset(self, dataverse_alias: str, metadata: dict[str, Any]) -> dict[str, Any]:
        """
        Shortcut for: client.datasets.create(...)
        """
        return self.datasets.create(dataverse_alias, metadata)

    def upload_file(self, dataset_id: int, file_path: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Shortcut for: client.files.upload(...)
        """
        return self.files.upload(dataset_id, file_path, metadata)

    def publish_dataset(self, persistent_id: str, release_type: str = "major") -> dict[str, Any]:
        """
        Shortcut for: client.datasets.publish(...)
        """
        return self.datasets.publish(persistent_id, release_type)

    def search_datasets(self, query: str, type: str = "dataset") -> list[dict[str, Any]]:
        """
        Shortcut for: client.search.query(...)
        """
        return self.search.query(query, type=type)

    def ping(self) -> bool:
        """
        Check if the Dataverse server is reachable.
        """
        try:
            info = self.info.version()
            return "version" in info
        except Exception:
            return False

    def __repr__(self) -> str:
        return f"<DataverseClient base_url={self.config.base_url}>"
