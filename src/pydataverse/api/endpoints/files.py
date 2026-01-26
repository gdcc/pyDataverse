"""
files.py — File-related endpoints for the Dataverse API

This module provides a clean wrapper around Dataverse file operations:
- Upload file
- Retrieve file metadata
- Download file
- Delete file
- Replace file
- List files in a dataset

All HTTP transport is delegated to the shared HttpClient.
"""

from __future__ import annotations

from typing import Any

from ..transport import HttpClient


class FileEndpoint:
    """
    Wrapper for Dataverse file endpoints.

    Example:
        client.files.upload(dataset_id, "data.csv")
        info = client.files.get(123)
        client.files.delete(123)
    """

    def __init__(self, http: HttpClient) -> None:
        self.http = http

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    def upload(
        self,
        dataset_id: int,
        file_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Upload a file to a dataset.

        POST /api/datasets/{id}/add
        """
        files = {"file": open(file_path, "rb")}
        params = {}

        if metadata:
            params["jsonData"] = metadata

        try:
            return self.http.post(
                f"/api/datasets/{dataset_id}/add",
                files=files,
                data={"jsonData": metadata} if metadata else None,
            )
        finally:
            files["file"].close()

    # ------------------------------------------------------------------
    # Retrieve metadata
    # ------------------------------------------------------------------

    def get(self, file_id: int) -> dict[str, Any]:
        """
        Retrieve file metadata.

        GET /api/files/{id}
        """
        return self.http.get(f"/api/files/{file_id}")

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    def download(self, file_id: int) -> bytes:
        """
        Download a file's binary content.

        GET /api/access/datafile/{id}
        """
        # Use raw=True to bypass JSON parsing
        response = self.http.get(
            self.http._build_url(f"/api/access/datafile/{file_id}"),
            timeout=self.http.timeout,
        )

        if response.status_code != 200:
            self.http._raise_for_status(response)

        return response.content

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, file_id: int) -> dict[str, Any]:
        """
        Delete a file.

        DELETE /api/files/{id}
        """
        return self.http.delete(f"/api/files/{file_id}")

    # ------------------------------------------------------------------
    # Replace
    # ------------------------------------------------------------------

    def replace(
        self,
        file_id: int,
        file_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Replace an existing file with a new one.

        POST /api/files/{id}/replace
        """
        files = {"file": open(file_path, "rb")}

        try:
            return self.http.post(
                f"/api/files/{file_id}/replace",
                files=files,
                data={"jsonData": metadata} if metadata else None,
            )
        finally:
            files["file"].close()

    # ------------------------------------------------------------------
    # List files in a dataset
    # ------------------------------------------------------------------

    def list_in_dataset(self, persistent_id: str) -> list[dict[str, Any]]:
        """
        List files in a dataset.

        GET /api/datasets/:persistentId/versions/:latest/files
        """
        return self.http.get(
            "/api/datasets/:persistentId/versions/:latest/files",
            params={"persistentId": persistent_id},
        )
