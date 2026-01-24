# ----------------------------------------------------------------------
# Version
# ----------------------------------------------------------------------


def test_version(info, mock_http):
    mock_http.get.return_value = {"version": "5.13"}

    result = info.version()

    mock_http.get.assert_called_once_with("/api/info/version")
    assert result == {"version": "5.13"}


# ----------------------------------------------------------------------
# Server info
# ----------------------------------------------------------------------


def test_server(info, mock_http):
    mock_http.get.return_value = {"status": "OK"}

    result = info.server()

    mock_http.get.assert_called_once_with("/api/info/server")
    assert result == {"status": "OK"}


# ----------------------------------------------------------------------
# Metrics
# ----------------------------------------------------------------------


def test_metrics(info, mock_http):
    mock_http.get.return_value = {"datasets": 100}

    result = info.metrics()

    mock_http.get.assert_called_once_with("/api/info/metrics")
    assert result == {"datasets": 100}


# ----------------------------------------------------------------------
# Metadata blocks
# ----------------------------------------------------------------------


def test_list_metadata_blocks(info, mock_http):
    mock_http.get.return_value = [{"name": "citation"}]

    result = info.list_metadata_blocks()

    mock_http.get.assert_called_once_with("/api/metadata")
    assert result == [{"name": "citation"}]


def test_get_metadata_block(info, mock_http):
    mock_http.get.return_value = {"name": "citation"}

    result = info.get_metadata_block("citation")

    mock_http.get.assert_called_once_with("/api/metadata/citation")
    assert result == {"name": "citation"}
