"""
datasets.py — Dataset-related endpoints for the Dataverse API

This module provides a clean, typed wrapper around Dataverse dataset operations:
- Create dataset
- Retrieve dataset metadata
- Publish dataset
- Delete dataset
- List datasets in a Dataverse
- Manage dataset versions

All HTTP transport is delegated to the shared HttpClient.
"""

from __future__ import annotations

from typing import Any

from ..transport import HttpClient


class DatasetEndpoint:
    """
    Wrapper for Dataverse dataset endpoints.

    Example:
        ds = client.datasets.create("root", metadata)
        info = client.datasets.get("doi:10.123/ABC")
        client.datasets.publish("doi:10.123/ABC")
    """

    def __init__(self, http: HttpClient) -> None:
        self.http = http

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(self, dataverse_alias: str, metadata: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new dataset inside a Dataverse.

        POST /api/dataverses/{alias}/datasets
        """
        return self.http.post(
            f"/api/dataverses/{dataverse_alias}/datasets",
            json={"datasetVersion": metadata},
        )

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def get(self, persistent_id: str) -> dict[str, Any]:
        """
        Retrieve dataset metadata by persistent ID.

        GET /api/datasets/:persistentId/?persistentId={pid}
        """
        return self.http.get(
            "/api/datasets/:persistentId/",
            params={"persistentId": persistent_id},
        )

    def get_version(self, persistent_id: str, version: str = ":latest") -> dict[str, Any]:
        """
        Retrieve a specific dataset version.

        GET /api/datasets/:persistentId/versions/{version}
        """
        return self.http.get(
            f"/api/datasets/:persistentId/versions/{version}",
            params={"persistentId": persistent_id},
        )

    # ------------------------------------------------------------------
    # List datasets in a Dataverse
    # ------------------------------------------------------------------

    def list_in_dataverse(self, dataverse_alias: str) -> list[dict[str, Any]]:
        """
        List datasets inside a Dataverse.

        GET /api/dataverses/{alias}/contents
        """
        contents = self.http.get(f"/api/dataverses/{dataverse_alias}/contents")
        return [item for item in contents if item.get("type") == "dataset"]

    # ------------------------------------------------------------------
    # Publish
    # ------------------------------------------------------------------

    def publish(self, persistent_id: str, release_type: str = "major") -> dict[str, Any]:
        """
        Publish a dataset.

        POST /api/datasets/:persistentId/actions/:publish
        """
        return self.http.post(
            "/api/datasets/:persistentId/actions/:publish",
            params={"persistentId": persistent_id, "type": release_type},
        )

    # ------------------------------------------------------------------
    # Update metadata
    # ------------------------------------------------------------------

    def update_metadata(self, persistent_id: str, metadata: dict[str, Any]) -> dict[str, Any]:
        """
        Update dataset metadata.

        PUT /api/datasets/:persistentId/versions/:draft
        """
        return self.http.put(
            "/api/datasets/:persistentId/versions/:draft",
            params={"persistentId": persistent_id},
            json={"datasetVersion": metadata},
        )

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, persistent_id: str) -> dict[str, Any]:
        """
        Delete a dataset (only allowed for admins or unpublished datasets).

        DELETE /api/datasets/:persistentId/
        """
        return self.http.delete(
            "/api/datasets/:persistentId/",
            params={"persistentId": persistent_id},
        )
