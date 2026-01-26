from unittest.mock import MagicMock, patch

import pytest

from pydataverse.api.client import DataverseClient
from pydataverse.api.endpoints.datasets import DatasetEndpoint
from pydataverse.api.endpoints.files import FileEndpoint
from pydataverse.api.endpoints.info import InfoEndpoint
from pydataverse.api.endpoints.search import SearchEndpoint
from pydataverse.api.transport import HttpClient


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
    with patch("pydataverse.api.client.HttpClient", return_value=mock_http):
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
