"""Find out more at https://github.com/GDCC/pyDataverse."""

import json
import os
from typing import Callable

import pytest
from pydantic import BaseModel

from pyDataverse import Collection, Dataverse
from pyDataverse.api.data_access import DataAccessApi
from pyDataverse.api.metrics import MetricsApi
from pyDataverse.api.native import NativeApi
from pyDataverse.api.search import SearchApi
from pyDataverse.api.semantic import SemanticApi
from pyDataverse.api.sword import SwordApi
from pyDataverse.dataverse.dataset import Dataset
from pyDataverse.models.dataset.create import DatasetCreateBody

DatasetFactory = Callable[[], Dataset]
CollectionFactory = Callable[[str], Collection]


class Credentials(BaseModel):
    base_url: str
    api_token: str
    api_token_superuser: str


@pytest.fixture(scope="session")
def credentials():
    """
    Retrieves the base URL and API token from the environment variables.
    Created once per test session and reused across all tests.

    Returns:
        tuple: A tuple containing the base URL and API token.
    """
    base_url = os.environ.get("BASE_URL", None)
    api_token = os.environ.get("API_TOKEN", None)
    api_token_superuser = os.environ.get("API_TOKEN_SUPERUSER", None)

    assert base_url is not None, "BASE_URL is not set"
    assert api_token is not None, "API_TOKEN is not set"
    assert api_token_superuser is not None, "API_TOKEN_SUPERUSER is not set"

    return Credentials(
        base_url=base_url.rstrip("/"),
        api_token=api_token,
        api_token_superuser=api_token_superuser,
    )


@pytest.fixture
def metrics_api(credentials: Credentials) -> MetricsApi:
    """Fixture to provide an initialized MetricsApi instance.

    Args:
        credentials: Fixture providing base URL and API token credentials.

    Returns:
        MetricsApi: An initialized MetricsApi instance for testing.
    """
    return MetricsApi(
        base_url=credentials.base_url,
        api_token=credentials.api_token,
    )


@pytest.fixture
def semantic_api(credentials: Credentials) -> SemanticApi:
    """Fixture to provide an initialized SemanticApi instance.

    Args:
        credentials: Fixture providing base URL and API token credentials.
    """
    return SemanticApi(
        base_url=credentials.base_url,
        api_token=credentials.api_token,
    )


@pytest.fixture
def native_api(credentials: Credentials) -> NativeApi:
    """Fixture to provide an initialized NativeApi instance.

    Args:
        credentials: Fixture providing base URL and API token credentials.
    """
    return NativeApi(
        base_url=credentials.base_url,
        api_token=credentials.api_token,
    )


@pytest.fixture
def native_api_superuser(credentials: Credentials) -> NativeApi:
    """Fixture to provide an initialized NativeApi instance with superuser privileges.

    Args:
        credentials: Fixture providing base URL and API token credentials.
    """
    return NativeApi(
        base_url=credentials.base_url,
        api_token=credentials.api_token_superuser,
    )


@pytest.fixture
def search_api(credentials: Credentials) -> SearchApi:
    """Fixture to provide an initialized SearchApi instance.

    Args:
        credentials: Fixture providing base URL and API token credentials.
    """
    return SearchApi(
        base_url=credentials.base_url,
        api_token=credentials.api_token,
    )


@pytest.fixture
def data_access_api(credentials: Credentials) -> DataAccessApi:
    """Fixture to provide an initialized DataAccessApi instance.

    Args:
        credentials: Fixture providing base URL and API token credentials.
    """
    return DataAccessApi(
        base_url=credentials.base_url,
        api_token=credentials.api_token,
    )


@pytest.fixture
def sword_api(credentials: Credentials) -> SwordApi:
    """Fixture to provide an initialized SwordApi instance.

    Args:
        credentials: Fixture providing base URL and API token credentials.
    """
    return SwordApi(
        base_url=credentials.base_url,
        api_token=credentials.api_token,
    )


@pytest.fixture
def dataset_upload_min_default():
    """Fixture to provide an initialized DataverseUploadMin instance.

    Args:
        credentials: Fixture providing base URL and API token credentials.
    """
    return DatasetCreateBody.model_validate(
        json.load(open("tests/data/dataset_upload_min_default.json"))
    )


@pytest.fixture(scope="session")
def dataverse(credentials: Credentials) -> Dataverse:
    """Fixture to provide an initialized Dataverse instance.
    Created once per test session and reused across all tests to avoid
    reconnecting on every test.

    Args:
        credentials: Fixture providing base URL and API token credentials.
    """
    return Dataverse(
        base_url=credentials.base_url,
        api_token=credentials.api_token,
    )


@pytest.fixture
def dataset(minimal_dataset: Dataset) -> DatasetFactory:
    """Fixture to provide a factory function for creating test datasets.

    Returns a lambda function that creates a dataset with standard test metadata
    and uploads it to the root collection. This allows tests to control when
    the dataset is actually created, preventing ID misalignment issues.

    Args:
        dataverse: Session-scoped Dataverse instance to reuse.

    Returns:
        Callable: A lambda function that creates and returns a Dataset instance.
    """

    def create_dataset():
        dataset = minimal_dataset
        dataset.upload_to_collection("root")

        return dataset

    return create_dataset


@pytest.fixture
def minimal_dataset(dataverse: Dataverse):
    return dataverse.create_dataset(
        title="Test Dataset",
        description="This is a test dataset",
        authors=[{"name": "Test Author"}],
        contacts=[{"name": "Test Author", "email": "test@test.com"}],
        subjects=["Computer and Information Science"],
        license=dataverse.default_license,
        upload_to_collection=False,
    )


def _create_mcp_server(credentials: Credentials):
    """
    Create and configure a Dataverse MCP server using credentials.

    Used by both session-scoped and standalone fixtures. Inspired by server.py
    but uses credentials from the fixture instead of hardcoded values.

    Args:
        credentials: Credentials containing base_url and api_token.

    Returns:
        Configured FastMCP instance with Dataverse tools registered.
    """
    from fastmcp import FastMCP

    from pyDataverse.mcp import DataverseMCP

    mcp = FastMCP(name="PyDataverse MCP Test")
    dataverse = Dataverse(
        base_url=credentials.base_url,
        api_token=credentials.api_token,
        verbose=0,
    )
    DataverseMCP(dataverse=dataverse).to_mcp(mcp)
    return mcp


@pytest.fixture(scope="session")
def mcp_server(credentials: Credentials):
    """
    Session-scoped MCP server instance.

    Creates the FastMCP server once per test session and reuses it across all
    tests. Use this when tests can share the same server state.

    Args:
        credentials: Session-scoped credentials fixture.

    Returns:
        Configured FastMCP instance with Dataverse tools.
    """
    return _create_mcp_server(credentials)


@pytest.fixture
def mcp_server_fixture(credentials: Credentials):
    """
    Function-scoped MCP server instance.

    Creates a fresh server for each test. Use when the session-scoped server
    may not be suitable (e.g. tests that modify server state, need isolation,
    or require different configuration).

    Args:
        credentials: Credentials fixture.

    Returns:
        Configured FastMCP instance with Dataverse tools.
    """
    return _create_mcp_server(credentials)


@pytest.fixture
async def mcp_client(mcp_server):
    """
    MCP client connected to the shared server.

    Each test gets its own client instance; all connect to the same
    session-scoped server. Use this fixture to emulate a client calling tools
    via the server (which provides the required context).
    """
    pytest.importorskip("fastmcp.client")
    from fastmcp.client import Client

    async with Client(transport=mcp_server) as client:
        yield client


@pytest.fixture
async def mcp_client_isolated(mcp_server_fixture):
    """
    Function-scoped MCP client with isolated server.

    Use when tests need an isolated server (e.g. state-modifying tests).
    """
    pytest.importorskip("fastmcp.client")
    from fastmcp.client import Client

    async with Client(transport=mcp_server_fixture) as client:
        yield client


@pytest.fixture
def collection(dataverse: Dataverse) -> CollectionFactory:
    """Fixture to provide a factory function for creating test collections.

    Returns a lambda function that creates a collection with standard test metadata
    and uploads it to the root collection. This allows tests to control when
    the collection is actually created, preventing ID misalignment issues.

    Args:
        dataverse: Session-scoped Dataverse instance to reuse.

    Returns:
        Callable: A lambda function that creates and returns a Collection instance.
    """

    def create_collection(alias: str):
        collection = dataverse.create_collection(
            alias=alias,
            name="Test Collection",
            affiliation="Test Affiliation",
            dataverse_type="DEPARTMENT",
            dataverse_contacts=["test@test.com"],
            parent="root",
            description="This is a test collection",
        )

        return collection

    return create_collection
