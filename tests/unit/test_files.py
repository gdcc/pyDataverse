from unittest.mock import MagicMock, mock_open, patch

import pytest

# ----------------------------------------------------------------------
# Upload
# ----------------------------------------------------------------------


def test_upload_file(files, mock_http):
    mock_http.post.return_value = {"status": "OK"}

    fake_file = mock_open(read_data=b"data")

    with patch("builtins.open", fake_file):
        result = files.upload(42, "data.csv")

    # Ensure file was opened
    fake_file.assert_called_once_with("data.csv", "rb")

    # Ensure HTTP call was made
    mock_http.post.assert_called_once()
    call_args = mock_http.post.call_args

    assert call_args.args[0] == "/api/datasets/42/add"
    assert result == {"status": "OK"}


def test_upload_file_with_metadata(files, mock_http):
    mock_http.post.return_value = {"status": "OK"}

    metadata = {"description": "Test file"}
    fake_file = mock_open(read_data=b"data")

    with patch("builtins.open", fake_file):
        files.upload(42, "data.csv", metadata=metadata)

    call_args = mock_http.post.call_args.kwargs
    assert call_args["data"] == {"jsonData": metadata}


# ----------------------------------------------------------------------
# Get file metadata
# ----------------------------------------------------------------------


def test_get_file(files, mock_http):
    mock_http.get.return_value = {"id": 123}

    result = files.get(123)

    mock_http.get.assert_called_once_with("/api/files/123")
    assert result == {"id": 123}


# ----------------------------------------------------------------------
# Download
# ----------------------------------------------------------------------


def test_download_file(files, mock_http):
    # Mock the underlying session.get call
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"binarydata"

    mock_http.get.return_value = mock_response

    print(files)
    result = files.download(55)

    mock_http.get.assert_called_once()
    assert result == b"binarydata"


def test_download_file_error(files, mock_http):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    mock_http.get.return_value = mock_response

    # Force _raise_for_status to be called
    mock_http._raise_for_status.side_effect = Exception("Not Found")

    with pytest.raises(Exception):
        files.download(55)


# ----------------------------------------------------------------------
# Delete
# ----------------------------------------------------------------------


def test_delete_file(files, mock_http):
    mock_http.delete.return_value = {"deleted": True}

    result = files.delete(123)

    mock_http.delete.assert_called_once_with("/api/files/123")
    assert result == {"deleted": True}


# ----------------------------------------------------------------------
# Replace
# ----------------------------------------------------------------------


def test_replace_file(files, mock_http):
    mock_http.post.return_value = {"replaced": True}

    fake_file = mock_open(read_data=b"newdata")

    with patch("builtins.open", fake_file):
        result = files.replace(123, "new.csv")

    fake_file.assert_called_once_with("new.csv", "rb")

    mock_http.post.assert_called_once()
    assert result == {"replaced": True}


def test_replace_file_with_metadata(files, mock_http):
    mock_http.post.return_value = {"replaced": True}

    metadata = {"description": "Updated file"}
    fake_file = mock_open(read_data=b"newdata")

    with patch("builtins.open", fake_file):
        files.replace(123, "new.csv", metadata=metadata)

    call_args = mock_http.post.call_args.kwargs
    assert call_args["data"] == {"jsonData": metadata}


# ----------------------------------------------------------------------
# List files in dataset
# ----------------------------------------------------------------------


def test_list_in_dataset(files, mock_http):
    mock_http.get.return_value = [{"id": 1}, {"id": 2}]

    result = files.list_in_dataset("doi:10.123/ABC")

    mock_http.get.assert_called_once_with(
        "/api/datasets/:persistentId/versions/:latest/files",
        params={"persistentId": "doi:10.123/ABC"},
    )

    assert result == [{"id": 1}, {"id": 2}]
