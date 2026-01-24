# ----------------------------------------------------------------------
# Query tests
# ----------------------------------------------------------------------


def test_query_basic(search, mock_http):
    mock_http.get.return_value = {"items": [{"title": "Dataset A"}]}

    result = search.query("climate")

    mock_http.get.assert_called_once_with(
        "/api/search",
        params={
            "q": "climate",
            "start": 0,
            "per_page": 10,
            "show_entity_ids": "false",
        },
    )

    assert result == [{"title": "Dataset A"}]


def test_query_with_type(search, mock_http):
    mock_http.get.return_value = {"items": []}

    search.query("ocean", type="dataset")

    mock_http.get.assert_called_once()
    params = mock_http.get.call_args.kwargs["params"]
    assert params["type"] == "dataset"


def test_query_with_pagination(search, mock_http):
    mock_http.get.return_value = {"items": []}

    search.query("fish", start=20, per_page=50)

    params = mock_http.get.call_args.kwargs["params"]
    assert params["start"] == 20
    assert params["per_page"] == 50


def test_query_with_sort_and_order(search, mock_http):
    mock_http.get.return_value = {"items": []}

    search.query("birds", sort="name", order="asc")

    params = mock_http.get.call_args.kwargs["params"]
    assert params["sort"] == "name"
    assert params["order"] == "asc"


def test_query_returns_empty_list_if_no_items(search, mock_http):
    mock_http.get.return_value = {"status": "OK"}  # no "items" key

    result = search.query("nothing")
    assert result == []


# ----------------------------------------------------------------------
# Facets tests
# ----------------------------------------------------------------------


def test_facets(search, mock_http):
    mock_http.get.return_value = {"facet_counts": {}}

    result = search.facets("climate")

    mock_http.get.assert_called_once_with(
        "/api/search/facets",
        params={"q": "climate"},
    )

    assert result == {"facet_counts": {}}


# ----------------------------------------------------------------------
# Count tests
# ----------------------------------------------------------------------


def test_count_basic(search, mock_http):
    mock_http.get.return_value = {"total_count": 42}

    result = search.count("climate")

    mock_http.get.assert_called_once_with(
        "/api/search",
        params={"q": "climate", "per_page": 0},
    )

    assert result == 42


def test_count_with_type(search, mock_http):
    mock_http.get.return_value = {"total_count": 10}

    result = search.count("ocean", type="dataset")

    params = mock_http.get.call_args.kwargs["params"]
    assert params["type"] == "dataset"
    assert result == 10


def test_count_returns_zero_if_missing(search, mock_http):
    mock_http.get.return_value = {"status": "OK"}  # no total_count

    result = search.count("unknown")
    assert result == 0
