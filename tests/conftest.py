from unittest.mock import MagicMock, patch

import pytest

from pyDataverse.api.client import DataverseClient
from pyDataverse.api.endpoints.datasets import DatasetEndpoint
from pyDataverse.api.endpoints.files import FileEndpoint
from pyDataverse.api.endpoints.info import InfoEndpoint
from pyDataverse.api.endpoints.search import SearchEndpoint
from pyDataverse.api.transport import HttpClient


@pytest.fixture
def mock_http():
    mock = MagicMock(spec=HttpClient)
    mock.timeout = 30
    mock.session = MagicMock()
    return mock


@pytest.fixture
def client(mock_http):
    """
    Creates a DataverseClient instance whose internal HttpClient
    is replaced with a mock. This ensures all endpoint modules
    receive the same mocked transport layer.
    """
    with patch("pyDataverse.api.client.HttpClient", return_value=mock_http):
        client = DataverseClient("https://demo.dataverse.org", api_token="XYZ")
    return client


@pytest.fixture
def files(mock_http):
    """Create a FileEndpoint with a mocked HttpClient."""
    return FileEndpoint(mock_http)


@pytest.fixture
def datasets(mock_http):
    """Create a FileEndpoint with a mocked HttpClient."""
    return DatasetEndpoint(mock_http)


@pytest.fixture
def info(mock_http):
    """Create a FileEndpoint with a mocked HttpClient."""
    return InfoEndpoint(mock_http)


@pytest.fixture
def search(mock_http):
    """Create a FileEndpoint with a mocked HttpClient."""
    return SearchEndpoint(mock_http)
