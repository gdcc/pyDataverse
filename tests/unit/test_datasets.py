# ----------------------------------------------------------------------
# Create
# ----------------------------------------------------------------------


def test_create_dataset(datasets, mock_http):
    mock_http.post.return_value = {"id": 123}

    metadata = {"title": "My Dataset"}
    result = datasets.create("root", metadata)

    mock_http.post.assert_called_once_with(
        "/api/dataverses/root/datasets",
        json={"datasetVersion": metadata},
    )

    assert result == {"id": 123}


# ----------------------------------------------------------------------
# Get dataset
# ----------------------------------------------------------------------


def test_get_dataset(datasets, mock_http):
    mock_http.get.return_value = {"persistentId": "doi:10.123/ABC"}

    result = datasets.get("doi:10.123/ABC")

    mock_http.get.assert_called_once_with(
        "/api/datasets/:persistentId/",
        params={"persistentId": "doi:10.123/ABC"},
    )

    assert result["persistentId"] == "doi:10.123/ABC"


# ----------------------------------------------------------------------
# Get dataset version
# ----------------------------------------------------------------------


def test_get_dataset_version(datasets, mock_http):
    mock_http.get.return_value = {"versionNumber": 1}

    result = datasets.get_version("doi:10.123/ABC", version="1")

    mock_http.get.assert_called_once_with(
        "/api/datasets/:persistentId/versions/1",
        params={"persistentId": "doi:10.123/ABC"},
    )

    assert result["versionNumber"] == 1


def test_get_dataset_version_default_latest(datasets, mock_http):
    mock_http.get.return_value = {"versionNumber": 2}

    datasets.get_version("doi:10.123/ABC")

    mock_http.get.assert_called_once_with(
        "/api/datasets/:persistentId/versions/:latest",
        params={"persistentId": "doi:10.123/ABC"},
    )


# ----------------------------------------------------------------------
# List datasets in a Dataverse
# ----------------------------------------------------------------------


def test_list_in_dataverse_filters_only_datasets(datasets, mock_http):
    mock_http.get.return_value = [
        {"type": "dataset", "id": 1},
        {"type": "file", "id": 2},
        {"type": "dataset", "id": 3},
    ]

    result = datasets.list_in_dataverse("root")

    mock_http.get.assert_called_once_with("/api/dataverses/root/contents")

    assert result == [
        {"type": "dataset", "id": 1},
        {"type": "dataset", "id": 3},
    ]


# ----------------------------------------------------------------------
# Publish
# ----------------------------------------------------------------------


def test_publish_dataset(datasets, mock_http):
    mock_http.post.return_value = {"status": "OK"}

    result = datasets.publish("doi:10.123/ABC", release_type="major")

    mock_http.post.assert_called_once_with(
        "/api/datasets/:persistentId/actions/:publish",
        params={"persistentId": "doi:10.123/ABC", "type": "major"},
    )

    assert result == {"status": "OK"}


# ----------------------------------------------------------------------
# Update metadata
# ----------------------------------------------------------------------


def test_update_metadata(datasets, mock_http):
    metadata = {"title": "Updated Title"}
    mock_http.put.return_value = {"updated": True}

    result = datasets.update_metadata("doi:10.123/ABC", metadata)

    mock_http.put.assert_called_once_with(
        "/api/datasets/:persistentId/versions/:draft",
        params={"persistentId": "doi:10.123/ABC"},
        json={"datasetVersion": metadata},
    )

    assert result == {"updated": True}


# ----------------------------------------------------------------------
# Delete
# ----------------------------------------------------------------------


def test_delete_dataset(datasets, mock_http):
    mock_http.delete.return_value = {"deleted": True}

    result = datasets.delete("doi:10.123/ABC")

    mock_http.delete.assert_called_once_with(
        "/api/datasets/:persistentId/",
        params={"persistentId": "doi:10.123/ABC"},
    )

    assert result == {"deleted": True}
