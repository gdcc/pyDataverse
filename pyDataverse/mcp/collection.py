from functools import lru_cache
from typing import Annotated, Dict, List, Literal, Optional, Union

from fastmcp import Context
from fastmcp.dependencies import CurrentContext
from rdflib import Graph
from toon_format import encode

from ..dataverse import Dataverse
from .utils import ensure_dataverse


def get_collection_metadata(
    collection: Annotated[
        Union[str, Literal["root"]],
        "The identifier/alias of the collection, which can be a persistent identifier or the special value 'root' for the root collection.",
    ],
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse from the context.",
    ],
    ctx: Context = CurrentContext(),
) -> str:
    """
    Get the metadata of a collection.
    """
    dataverse = ensure_dataverse(ctx, base_url=base_url)
    return encode(dataverse.collections[collection].metadata.model_dump())


def list_content(
    collection: Annotated[
        Union[str, Literal["root"]],
        "The identifier/alias of the collection, which can be a persistent identifier or the special value 'root' for the root collection.",
    ],
    filter_by: Annotated[
        Optional[Literal["dataset", "collection"]],
        "Filter the content by type.",
    ],
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse from the context.",
    ],
    ctx: Context = CurrentContext(),
) -> str:
    """
    List the content of a collection.

    Returns a list of all datasets and sub-collections within the specified collection.
    The results can be optionally filtered by content type (dataset or collection).

    Args:
        collection: The identifier/alias of the collection, which can be a persistent
            identifier or the special value 'root' for the root collection.
        filter_by: Optional filter to limit results to either "dataset" or "collection".
            If None, returns all content types.
        ctx: FastMCP context (automatically injected).

    Returns:
        A TOON-encoded string containing a list of dictionaries, each with:
        - identifier: The dataset identifier or collection alias
        - content_type: Type of content ("dataset" or "collection")
        - title: Display title/name of the content
    """
    dataverse = ensure_dataverse(ctx, base_url=base_url)
    overview = dataverse.collections[collection].overview

    if filter_by and "content_type" in overview.columns:
        overview = overview[overview["content_type"] == filter_by]

    return encode(overview.to_dict(orient="records"))  # type: ignore[arg-type]


def get_graph_summary(
    collection: Annotated[
        Union[str, Literal["root"]],
        "The identifier/alias of the collection, which can be a persistent identifier or the special value 'root' for the root collection.",
    ],
    format: Literal["croissant", "OAI_ORE", "semantic_api"] = "semantic_api",
    depth: int = 3,
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse from the context.",
    ] = None,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Get a comprehensive summary of the RDF graph of a collection.

    Analyzes the RDF graph representation of a collection and returns detailed
    information about classes, predicates, and overall graph statistics.

    Args:
        collection: The identifier/alias of the collection, which can be a persistent
            identifier or the special value 'root' for the root collection.
        format: The RDF graph format to use. Either "croissant" or "OAI_ORE".
            Defaults to "croissant".
        ctx: FastMCP context (automatically injected).

    Returns:
        A TOON-encoded string containing a dictionary with:
        - classes: List of all RDF classes with their instance counts
        - predicates: List of all predicates with usage counts, sample values,
            and blank node detection
        - statistics: Dictionary with total_triples, total_subjects, class_count,
            and predicate_count
    """
    dataverse = ensure_dataverse(ctx, base_url=base_url)
    return _get_graph_summary_cached(
        dataverse=dataverse,
        collection=collection,
        format=format,
        depth=depth,
    )


def query_sparql(
    collection: Annotated[
        Union[str, Literal["root"]],
        "The identifier/alias of the collection, which can be a persistent identifier or the special value 'root' for the root collection.",
    ],
    queries: Annotated[
        Union[str, Dict[str, str]],
        "Either a single SPARQL query string, or a dictionary mapping query names to SPARQL strings for batch execution.",
    ],
    format: Literal["croissant", "OAI_ORE", "semantic_api"] = "semantic_api",
    depth: Annotated[
        int,
        "The depth of the graph to retrieve. 1 means only the current collection, 2 means the current collection and all child collections, 3 means the current collection and all child collections and all child datasets, etc.",
    ] = 3,
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse from the context.",
    ] = None,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Execute one or more SPARQL queries against a collection's RDF graph.

    Single query example:
        query_sparql(collection="simtech", queries="SELECT ?s WHERE { ?s a schema:Dataset }")

    Batch query example:
        query_sparql(
            collection="simtech",
            queries={
                "datasets": "SELECT ?title WHERE { ?d a schema:Dataset ; schema:name ?title }",
                "authors": "SELECT DISTINCT ?name WHERE { ?p schema:familyName ?name }"
            }
        )

    Returns:
        - Single query: List of result rows
        - Batch queries: Dictionary mapping query names to {data, count, error?}
    """
    dataverse = ensure_dataverse(ctx, base_url=base_url)
    graph = _get_graph_cached(
        dataverse=dataverse,
        collection=collection,
        format=format,
        depth=depth,
    )

    if isinstance(queries, str):
        return _execute_single_query(graph, queries)

    return _execute_batch_queries(graph, queries)


@lru_cache(maxsize=128)
def _get_graph_cached(
    dataverse: Dataverse,
    collection: str,
    format: str,
    depth: int,
) -> Graph:
    """
    Cached helper to fetch the RDF graph of a collection.

    Creates a Dataverse instance and retrieves the RDF graph representation
    of the specified collection. Results are cached using LRU cache.

    Args:
        base_url: The base URL of the Dataverse instance.
        collection: The identifier/alias of the collection.
        format: The RDF graph format to use ("croissant" or "OAI_ORE").

    Returns:
        An RDF Graph object representing the collection's metadata.
    """
    return dataverse.collections[collection].graph(
        format=format,
        depth=depth,
    )


@lru_cache(maxsize=128)
def _get_graph_summary_cached(
    dataverse: Dataverse,
    collection: str,
    format: str,
    depth: int,
) -> str:
    """
    Build comprehensive graph summary with classes, predicates, and statistics.

    Queries the RDF graph to extract class information, predicate usage, and
    overall statistics, then formats the results as a TOON-encoded string.
    Results are cached using LRU cache.

    Args:
        dataverse: The Dataverse instance.
        collection: The identifier/alias of the collection.
        format: The RDF graph format to use ("croissant" or "OAI_ORE").

    Returns:
        A TOON-encoded string containing the graph summary with classes,
        predicates, and statistics.
    """
    graph = _get_graph_cached(
        dataverse=dataverse,
        collection=collection,
        format=format,
        depth=depth,
    )

    classes = _query_classes_with_counts(graph)
    predicates = _query_predicates_with_samples(graph)
    statistics = _query_graph_statistics(graph, len(classes), len(predicates))

    return encode(
        {
            "classes": classes,
            "predicates": predicates,
            "statistics": statistics,
        }
    )


def _query_classes_with_counts(graph: Graph) -> List[Dict]:
    """
    Get all RDF classes with their instance counts.

    Executes a SPARQL query to find all RDF classes used in the graph and
    counts how many instances of each class exist.

    Args:
        graph: The RDF Graph to query.

    Returns:
        A list of dictionaries, each containing:
        - uri: The full URI of the RDF class
        - short_name: The local name extracted from the URI
        - count: The number of instances of this class in the graph
    """
    query = """
    SELECT ?class (COUNT(?s) AS ?count)
    WHERE { ?s a ?class }
    GROUP BY ?class
    ORDER BY DESC(?count)
    """
    return [
        {
            "uri": str(row[0]),  # type: ignore[index]
            "short_name": _extract_short_name(str(row[0])),  # type: ignore[index]
            "count": int(row[1]),  # type: ignore[index]
        }
        for row in graph.query(query)
    ]


def _query_predicates_with_samples(graph: Graph) -> List[Dict]:
    """
    Get all predicates with usage counts and sample values.

    Executes a SPARQL query to find all predicates used in the graph, counts
    their usage frequency, and extracts sample values. Also detects blank nodes.

    Args:
        graph: The RDF Graph to query.

    Returns:
        A list of dictionaries, each containing:
        - uri: The full URI of the predicate
        - short_name: The local name extracted from the URI
        - usage_count: The number of times this predicate is used
        - sample_value: A sample object value (None if blank node)
        - has_blank_nodes: Boolean indicating if blank nodes are present
    """
    query = """
    SELECT ?predicate (COUNT(*) AS ?count) (SAMPLE(?o) AS ?sample)
    WHERE { ?s ?predicate ?o }
    GROUP BY ?predicate
    ORDER BY DESC(?count)
    """

    predicates = []
    for row in graph.query(query):
        uri = str(row[0])  # type: ignore[index]
        sample = str(row[2]) if row[2] is not None else None  # type: ignore[index]
        is_blank = _is_blank_node_id(sample)

        predicates.append(
            {
                "uri": uri,
                "short_name": _extract_short_name(uri),
                "usage_count": int(row[1]),  # type: ignore[index]
                "sample_value": None if is_blank else sample,
                "has_blank_nodes": is_blank,
            }
        )

    return predicates


def _query_graph_statistics(
    graph: Graph,
    class_count: int,
    predicate_count: int,
) -> Dict:
    """
    Get overall graph statistics.

    Executes a SPARQL query to count total triples and unique subjects in
    the graph, and combines this with pre-computed class and predicate counts.

    Args:
        graph: The RDF Graph to query.
        class_count: The number of unique classes in the graph.
        predicate_count: The number of unique predicates in the graph.

    Returns:
        A dictionary containing:
        - total_triples: Total number of RDF triples in the graph
        - total_subjects: Number of unique subjects in the graph
        - class_count: Number of unique classes
        - predicate_count: Number of unique predicates
    """
    query = """
    SELECT (COUNT(*) AS ?triples) (COUNT(DISTINCT ?s) AS ?subjects)
    WHERE { ?s ?p ?o }
    """
    results = list(graph.query(query))

    if results:
        return {
            "total_triples": int(results[0][0]),  # type: ignore[index]
            "total_subjects": int(results[0][1]),  # type: ignore[index]
            "class_count": class_count,
            "predicate_count": predicate_count,
        }

    return {
        "total_triples": 0,
        "total_subjects": 0,
        "class_count": class_count,
        "predicate_count": predicate_count,
    }


def _execute_single_query(graph: Graph, query: str) -> str:
    """
    Execute a single SPARQL query and return results.

    Runs a SPARQL query against the RDF graph and converts the results
    to a list of dictionaries, handling errors gracefully.

    Args:
        graph: The RDF Graph to query.
        query: The SPARQL query string to execute.

    Returns:
        A TOON-encoded string containing either:
        - A list of result dictionaries (on success)
        - An error dictionary with an "error" key (on failure)
    """
    try:
        results = graph.query(query)
        rows = _sparql_results_to_dicts(results)
        return encode(rows)
    except Exception as e:
        return encode({"error": str(e)})


def _execute_batch_queries(graph: Graph, queries: Dict[str, str]) -> str:
    """
    Execute multiple SPARQL queries and return named results.

    Runs multiple SPARQL queries against the RDF graph and returns results
    organized by query name. Each query is executed independently, and errors
    are captured per query without stopping execution of others.

    Args:
        graph: The RDF Graph to query.
        queries: A dictionary mapping query names to SPARQL query strings.

    Returns:
        A TOON-encoded string containing a dictionary mapping query names to
        result dictionaries. Each result dictionary contains:
        - data: List of result rows (empty list on error)
        - count: Number of result rows
        - error: Error message string (only present if query failed)
    """
    results = {}

    for name, query in queries.items():
        try:
            query_results = graph.query(query)
            rows = _sparql_results_to_dicts(query_results)
            results[name] = {"data": rows, "count": len(rows)}
        except Exception as e:
            results[name] = {"data": [], "count": 0, "error": str(e)}

    return encode(results)


def _sparql_results_to_dicts(results) -> List[Dict]:
    """
    Convert SPARQL query results to a list of dictionaries.

    Transforms SPARQL query result objects into a list of dictionaries,
    handling different result types (SELECT queries with variables, boolean
    results, etc.).

    Args:
        results: The SPARQL query result object from rdflib.

    Returns:
        A list of dictionaries representing the query results. For SELECT
        queries, each dictionary maps variable names to their values. For
        other query types, returns dictionaries with a "result" key.
    """
    results_list = list(results)

    if not results_list:
        return []

    # SELECT query with variable bindings
    if hasattr(results, "vars") and results.vars:
        return [
            {
                str(var): _format_value(row[idx])
                for idx, var in enumerate(results.vars)
                if idx < len(row)
            }
            for row in results_list
        ]

    # Boolean or other result types
    if len(results_list) == 1 and len(results_list[0]) == 1:
        return [{"result": _format_value(results_list[0][0])}]

    return [{"result": _format_value(r)} for r in results_list]


def _extract_short_name(uri: str) -> str:
    """
    Extract the local name from a URI.

    Extracts the last segment of a URI, handling both slash-separated
    and hash-separated URIs.

    Args:
        uri: The full URI string.

    Returns:
        The local name (last segment) of the URI after splitting by "/"
        and "#".

    Example:
        >>> _extract_short_name("http://example.org/ns#ClassName")
        "ClassName"
        >>> _extract_short_name("http://example.org/path/Item")
        "Item"
    """
    return uri.split("/")[-1].split("#")[-1]


def _is_blank_node_id(value: Optional[str]) -> bool:
    """
    Check if a value looks like a blank node identifier.

    Detects common blank node identifier patterns used in RDF graphs.
    Blank nodes are anonymous resources that don't have a URI.

    Args:
        value: The string value to check. Can be None.

    Returns:
        True if the value appears to be a blank node identifier, False otherwise.
        Returns False if value is None.

    Note:
        Detects patterns:
        - Values starting with "_:" (standard blank node prefix)
        - Values of length 33 starting with an uppercase letter followed by alphanumeric characters
    """
    if value is None:
        return False

    if value.startswith("_:"):
        return True
    if len(value) == 33 and value[0].isupper() and value[1:].isalnum():
        return True
    return False


def _format_value(value) -> Optional[str]:
    """
    Format a SPARQL result value to string, handling None.

    Converts SPARQL query result values to strings, safely handling None
    values by returning None instead of the string "None".

    Args:
        value: The value to format. Can be any type, including None.

    Returns:
        The string representation of the value, or None if the input was None.
    """
    return str(value) if value is not None else None
