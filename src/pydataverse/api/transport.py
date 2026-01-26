"""
transport.py — Shared HTTP transport layer for Dataverse API

This module provides:
- A reusable HttpClient with a persistent requests.Session
- Centralized error handling and exception mapping
- JSON parsing with consistent return types
- Optional retry logic (simple, built-in)
"""

from __future__ import annotations

import json
import time
from typing import Any

import requests
from requests import Response

from .exceptions import (
    AuthenticationError,
    DataverseError,
    NotFoundError,
    ServerError,
    ValidationError,
)


class HttpClient:
    """
    A lightweight HTTP client wrapper around requests.Session.

    Responsibilities:
    - Build full URLs
    - Attach authentication headers
    - Handle retries
    - Parse JSON responses
    - Map HTTP errors to structured exceptions
    """

    def __init__(
        self,
        base_url: str,
        api_token: str | None = None,
        timeout: int = 30,
        max_retries: int = 2,
        backoff_factor: float = 0.5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        self.session = requests.Session()
        if api_token:
            self.session.headers.update({"X-Dataverse-key": api_token})

        # Dataverse always expects JSON unless uploading files
        self.session.headers.update({"Accept": "application/json"})

    # ------------------------------------------------------------------
    # Public HTTP methods
    # ------------------------------------------------------------------

    def get(self, path: str, **kwargs: Any) -> Any:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Any:
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self._request("DELETE", path, **kwargs)

    # ------------------------------------------------------------------
    # Core request logic
    # ------------------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = self._build_url(path)

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    **kwargs,
                )
                return self._handle_response(response)

            except (requests.ConnectionError, requests.Timeout):
                if attempt >= self.max_retries:
                    raise DataverseError(f"Network error contacting {url}")

                sleep_time = self.backoff_factor * (2**attempt)
                time.sleep(sleep_time)

        raise DataverseError("Unexpected retry loop termination")

    # ------------------------------------------------------------------
    # URL handling
    # ------------------------------------------------------------------

    def _build_url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    # ------------------------------------------------------------------
    # Response handling
    # ------------------------------------------------------------------

    def _handle_response(self, response: Response) -> Any:
        """
        Parse JSON, map errors, and return the Dataverse API payload.
        """
        if 200 <= response.status_code < 300:
            return self._parse_json(response)

        self._raise_for_status(response)

    def _parse_json(self, response: Response) -> Any:
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise DataverseError("Invalid JSON response from Dataverse")

        # Dataverse wraps responses in {"status": "...", "data": ...}
        if isinstance(data, dict) and "data" in data:
            return data["data"]

        return data

    # ------------------------------------------------------------------
    # Error mapping
    # ------------------------------------------------------------------

    def _raise_for_status(self, response: Response) -> None:
        status = response.status_code
        text = response.text

        if status in {401, 403}:
            raise AuthenticationError("Invalid API token or insufficient permissions")

        if status == 404:
            raise NotFoundError("Requested resource not found")

        if status == 400:
            raise ValidationError(f"Bad request: {text}")

        if 500 <= status < 600:
            raise ServerError(f"Dataverse server error ({status}): {text}")

        raise DataverseError(f"Unexpected HTTP {status}: {text}")
