from unittest.mock import MagicMock

# ----------------------------------------------------------------------
# Initialization tests
# ----------------------------------------------------------------------


def test_client_initializes_transport_layer(client, mock_http):
    assert client.http is mock_http
    assert client.config.base_url == "https://demo.dataverse.org"
    assert client.config.api_token == "XYZ"


def test_client_initializes_endpoints(client):
    assert hasattr(client, "datasets")
    assert hasattr(client, "files")
    assert hasattr(client, "search")
    assert hasattr(client, "info")


# ----------------------------------------------------------------------
# Convenience method tests
# ----------------------------------------------------------------------


def test_create_dataset_calls_dataset_endpoint(client):
    client.datasets.create = MagicMock(return_value={"id": 123})

    result = client.create_dataset("root", {"title": "My Dataset"})

    client.datasets.create.assert_called_once_with("root", {"title": "My Dataset"})
    assert result == {"id": 123}


def test_upload_file_calls_file_endpoint(client):
    client.files.upload = MagicMock(return_value={"status": "OK"})

    result = client.upload_file(42, "data.csv")

    client.files.upload.assert_called_once_with(42, "data.csv", None)
    assert result == {"status": "OK"}


def test_publish_dataset_calls_dataset_endpoint(client):
    client.datasets.publish = MagicMock(return_value={"published": True})

    result = client.publish_dataset("doi:10.123/ABC")

    client.datasets.publish.assert_called_once_with("doi:10.123/ABC", "major")
    assert result == {"published": True}


def test_search_datasets_calls_search_endpoint(client):
    client.search.query = MagicMock(return_value=[{"title": "Test"}])

    result = client.search_datasets("climate")

    client.search.query.assert_called_once_with("climate", type="dataset")
    assert result == [{"title": "Test"}]


# ----------------------------------------------------------------------
# Ping tests
# ----------------------------------------------------------------------


def test_ping_returns_true_when_version_available(client):
    client.info.version = MagicMock(return_value={"version": "5.13"})

    assert client.ping() is True


def test_ping_returns_false_on_exception(client):
    client.info.version = MagicMock(side_effect=Exception("Server down"))

    assert client.ping() is False


# ----------------------------------------------------------------------
# Representation
# ----------------------------------------------------------------------


def test_repr(client):
    text = repr(client)
    assert "DataverseClient" in text
    assert "https://demo.dataverse.org" in text
