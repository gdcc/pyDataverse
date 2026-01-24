from unittest.mock import MagicMock, patch

import pytest
from requests import Response

from pyDataverse.api.exceptions import (
    AuthenticationError,
    DataverseError,
    NotFoundError,
    ServerError,
    ValidationError,
)
from pyDataverse.api.transport import HttpClient

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def make_response(status=200, json_data=None, text=""):
    """Create a fake Response object."""
    resp = MagicMock(spec=Response)
    resp.status_code = status
    resp.text = text

    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = ValueError("Invalid JSON")

    return resp


# ----------------------------------------------------------------------
# URL building
# ----------------------------------------------------------------------


def test_build_url():
    client = HttpClient("https://demo.dataverse.org")
    assert client._build_url("/api/info/version") == "https://demo.dataverse.org/api/info/version"


# ----------------------------------------------------------------------
# Successful JSON parsing
# ----------------------------------------------------------------------


def test_parse_json_success():
    client = HttpClient("https://demo.dataverse.org")

    response = make_response(status=200, json_data={"status": "OK", "data": {"version": "5.13"}})

    result = client._handle_response(response)
    assert result == {"version": "5.13"}


def test_parse_json_without_data_wrapper():
    client = HttpClient("https://demo.dataverse.org")

    response = make_response(status=200, json_data={"hello": "world"})

    result = client._handle_response(response)
    assert result == {"hello": "world"}


# ----------------------------------------------------------------------
# Error mapping
# ----------------------------------------------------------------------


def test_401_raises_authentication_error():
    client = HttpClient("https://demo.dataverse.org")
    response = make_response(status=401, text="Unauthorized")

    with pytest.raises(AuthenticationError):
        client._raise_for_status(response)


def test_403_raises_authentication_error():
    client = HttpClient("https://demo.dataverse.org")
    response = make_response(status=403, text="Forbidden")

    with pytest.raises(AuthenticationError):
        client._raise_for_status(response)


def test_404_raises_not_found():
    client = HttpClient("https://demo.dataverse.org")
    response = make_response(status=404, text="Not Found")

    with pytest.raises(NotFoundError):
        client._raise_for_status(response)


def test_400_raises_validation_error():
    client = HttpClient("https://demo.dataverse.org")
    response = make_response(status=400, text="Bad Request")

    with pytest.raises(ValidationError):
        client._raise_for_status(response)


def test_500_raises_server_error():
    client = HttpClient("https://demo.dataverse.org")
    response = make_response(status=500, text="Server Error")

    with pytest.raises(ServerError):
        client._raise_for_status(response)


def test_unexpected_status_raises_dataverse_error():
    client = HttpClient("https://demo.dataverse.org")
    response = make_response(status=418, text="I'm a teapot")

    with pytest.raises(DataverseError):
        client._raise_for_status(response)


# ----------------------------------------------------------------------
# Raw GET for downloads
# ----------------------------------------------------------------------


def test_download_raw_response_handling():
    client = HttpClient("https://demo.dataverse.org")

    with patch.object(client.session, "get") as mock_get:
        mock_get.return_value = make_response(status=200, text="", json_data=None)
        mock_get.return_value.content = b"binarydata"

        result = client.session.get("url").content
        assert result == b"binarydata"
