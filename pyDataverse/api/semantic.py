import asyncio
import json
from typing import Any, Dict, Literal, Sequence, Union, overload

from pydantic import computed_field
from rdflib import Graph, URIRef

from ..models import collection
from .api import Api


class SemanticApi(Api):
    """Class to access Dataverse's Semantic/Linked Data API.

    This class provides methods to retrieve and work with dataset metadata in semantic
    formats like JSON-LD (JSON for Linking Data). The semantic API allows you to access
    structured metadata that can be used for semantic web applications, knowledge graphs,
    and linked data workflows.

    The SemanticApi extends the base Api class and provides specialized methods for:
    - Retrieving individual dataset metadata in JSON-LD format
    - Batch retrieval of multiple datasets with concurrent processing
    - Converting JSON-LD responses to RDFLib Graph objects for further processing

    Args:
        base_url: Base URL of the Dataverse instance (e.g., "https://demo.dataverse.org").
        api_token: Optional API token for authentication. Required for accessing
            private datasets or performing operations that require authentication.
        api_version: Version of the Dataverse API to use. Defaults to the latest version.

    Attributes:
        base_url_api_native: The base URL for native API endpoints.
        base_url_api: The base URL for API endpoints.

    Examples:
        Basic usage with public datasets::

            >>> api = SemanticApi(base_url="https://demo.dataverse.org")
            >>> metadata = api.get_dataset("doi:10.11587/8H3N93")
            >>> print(metadata["@context"])

        Authenticated usage::

            >>> api = SemanticApi(
            ...     base_url="https://your-dataverse.org",
            ...     api_token="your-api-token"
            ... )
            >>> metadata = api.get_dataset("doi:10.11587/8H3N93")

        Batch processing multiple datasets::

            >>> identifiers = ["doi:10.11587/8H3N93", "doi:10.11587/ABC123"]
            >>> all_metadata = api.get_datasets(identifiers, batch_size=10)
            >>> print(f"Retrieved {len(all_metadata)} datasets")
    """

    @computed_field
    @property
    def base_url_api_native(self) -> str:
        """Get the base URL for native API endpoints.

        Returns:
            str: The base URL for native API endpoints, same as base_url_api.
        """
        return self.base_url_api

    @computed_field
    @property
    def api_base_url(self) -> str:
        """Get the base URL for API endpoints.

        Returns:
            str: The base URL for API endpoints.
        """
        return self.base_url_api

    @overload
    def get_dataset(
        self,
        identifier: str | int,
        as_graph: Literal[False] = False,
    ) -> Dict[str, Any]: ...

    @overload
    def get_dataset(
        self,
        identifier: str | int,
        as_graph: Literal[True] = True,
    ) -> Graph: ...

    def get_dataset(
        self,
        identifier: str | int,
        as_graph: bool = False,
    ) -> Union[Dict[str, Any], Graph]:
        """Get dataset metadata in JSON-LD format.

        Retrieves the semantic metadata for a dataset using its persistent identifier
        or numeric ID. The response is returned in JSON-LD (JSON for Linking Data) format,
        which provides structured data that can be used for semantic web applications,
        knowledge graphs, and linked data workflows.

        JSON-LD is a lightweight syntax for encoding linked data using JSON. It allows
        data to be serialized in a way that is both human-readable and machine-processable,
        making it ideal for semantic web applications.

        HTTP Request:

        .. code-block:: bash

            # For persistent identifiers:
            GET http://$SERVER/api/datasets/:persistentId/metadata?persistentId=$PID
            Accept: application/ld+json

            # For numeric IDs:
            GET http://$SERVER/api/datasets/$ID/metadata
            Accept: application/ld+json

        Args:
            identifier: Dataset identifier. Can be either:
                - Persistent identifier (str): e.g., "doi:10.11587/8H3N93", "hdl:1902.1/21919"
                - Numeric database ID (int): e.g., 42

        Returns:
            Dict[str, Any]: A dictionary containing the dataset metadata in JSON-LD format.
            The dictionary includes standard JSON-LD fields like "@context", "@type", and
            dataset-specific metadata fields such as title, authors, description, etc.

        Raises:
            httpx.HTTPStatusError: If the API request fails (e.g., dataset not found,
                authentication required, server error).
            ValueError: If the identifier format is invalid.

        Examples:
            Get dataset metadata using a DOI::

                >>> api = SemanticApi(base_url="https://demo.dataverse.org")
                >>> metadata = api.get_dataset("doi:10.11587/8H3N93")
                >>> print(metadata["@context"])
                >>> print(metadata.get("name"))  # Dataset title

            Get dataset metadata using a numeric ID::

                >>> metadata = api.get_dataset(42)
                >>> print(metadata["@type"])

            Access specific metadata fields::

                >>> metadata = api.get_dataset("doi:10.11587/8H3N93")
                >>> authors = metadata.get("author", [])
                >>> for author in authors:
                ...     print(author.get("name"))

        Note:
            The JSON-LD format includes a "@context" field that defines the vocabulary
            and mappings used in the metadata. This context is essential for properly
            interpreting the semantic meaning of the data fields.
        """

        params = {}
        if self._is_pid(identifier):
            url = self._assemble_url("datasets/:persistentId/metadata")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"datasets/{identifier}/metadata")

        dataset = self.get_request(
            url,
            params=params,
            use_async=self.client is not None,
            headers={"Accept": "application/ld+json"},
            response_model=Dict[str, Any],
        )

        if as_graph:
            return self.response_to_graph(dataset)
        else:
            return dataset

    @overload
    def get_datasets(
        self,
        identifiers: Sequence[str | int | collection.content.Dataset],
        batch_size: int = 50,
        as_graph: Literal[False] = False,
    ) -> Sequence[Dict[str, Any]]: ...

    @overload
    def get_datasets(
        self,
        identifiers: Sequence[str | int | collection.content.Dataset],
        batch_size: int = 50,
        as_graph: Literal[True] = True,
    ) -> Graph: ...

    def get_datasets(
        self,
        identifiers: Sequence[str | int | collection.content.Dataset],
        batch_size: int = 50,
        as_graph: bool = False,
    ) -> Sequence[Dict[str, Any]] | Graph:
        """Get metadata for multiple datasets in JSON-LD format with concurrent processing.

        This method efficiently retrieves semantic metadata for multiple datasets by
        processing them in concurrent batches. It's designed for bulk operations where
        you need to collect metadata from many datasets while managing system resources
        and API rate limits.

        The method automatically handles:
        - Concurrent API requests within each batch for improved performance
        - Proper async client lifecycle management
        - Error handling and cleanup
        - Memory-efficient batch processing

        Args:
            identifiers: A sequence of dataset identifiers. Each identifier can be either:
                - Persistent identifier (str): e.g., "doi:10.11587/8H3N93"
                - Numeric database ID (int): e.g., 42
            batch_size: Number of datasets to process concurrently in each batch.
                Defaults to 50. Larger batch sizes can improve performance but may
                consume more memory and potentially hit API rate limits. Smaller
                batch sizes are more conservative and suitable for large collections.

        Returns:
            Sequence[Dict[str, Any]]: A sequence of dictionaries, each containing
            dataset metadata in JSON-LD format. The order of results corresponds
            to the order of input identifiers.

        Raises:
            httpx.HTTPStatusError: If any API request fails. The method will stop
                processing and raise the first encountered error.
            ValueError: If any identifier format is invalid.
            asyncio.TimeoutError: If requests exceed the configured timeout.

        Examples:
            Process a small list of datasets::

                >>> api = SemanticApi(base_url="https://demo.dataverse.org")
                >>> identifiers = [
                ...     "doi:10.11587/8H3N93",
                ...     "doi:10.11587/ABC123",
                ...     42
                ... ]
                >>> all_metadata = api.get_datasets(identifiers)
                >>> print(f"Retrieved {len(all_metadata)} datasets")

            Process a large collection with custom batch size::

                >>> # For processing 1000+ datasets, use smaller batch size
                >>> large_collection = [f"doi:10.11587/ID{i}" for i in range(1000)]
                >>> metadata = api.get_datasets(large_collection, batch_size=25)

            Extract specific information from all datasets::

                >>> identifiers = ["doi:10.11587/8H3N93", "doi:10.11587/ABC123"]
                >>> all_metadata = api.get_datasets(identifiers)
                >>> for metadata in all_metadata:
                ...     title = metadata.get("name", "Unknown")
                ...     authors = len(metadata.get("author", []))
                ...     print(f"Dataset: {title}, Authors: {authors}")

        Performance Notes:
            - The optimal batch_size depends on your system resources, network latency,
              and the Dataverse instance's performance characteristics
            - For most use cases, the default batch size of 50 provides a good balance
              between performance and resource usage
            - Consider using smaller batch sizes (10-25) when processing very large
              collections or when working with slower networks
        """

        identifiers = [
            identifier.identifier
            if isinstance(identifier, collection.content.Dataset)
            else identifier
            for identifier in identifiers
        ]

        datasets = asyncio.run(self._get_datasets(identifiers, batch_size))
        if as_graph:
            return self.responses_to_graph(datasets)
        else:
            return datasets

    async def _get_datasets(
        self,
        identifiers: Sequence[str | int],
        batch_size: int,
    ) -> Sequence[Dict[str, Any]]:
        """Internal async method to retrieve metadata for multiple datasets concurrently.

        This is the internal implementation that handles the actual concurrent processing
        of dataset metadata requests. It manages the async client lifecycle and processes
        identifiers in batches to optimize performance while managing system resources.

        The method works by:
        1. Setting up an async HTTP client context
        2. Dividing the identifier list into batches of the specified size
        3. Creating concurrent tasks for each identifier in a batch
        4. Using asyncio.gather to execute all tasks in a batch simultaneously
        5. Collecting and extending results from each batch
        6. Properly cleaning up the async client when done

        Args:
            identifiers: A sequence of dataset identifiers (persistent IDs or numeric IDs).
            batch_size: Number of datasets to process concurrently in each batch.

        Returns:
            Sequence[Dict[str, Any]]: A sequence of JSON-LD dictionaries containing
            the metadata for each requested dataset, in the same order as the input
            identifiers.

        Raises:
            httpx.HTTPStatusError: If any HTTP request fails during processing.
            ValueError: If any identifier is in an invalid format.
            asyncio.TimeoutError: If any request exceeds the configured timeout.

        Note:
            This method is intended for internal use by the get_datasets method.
            It requires an async context and proper client lifecycle management.
            Use get_datasets for synchronous access to this functionality.
        """

        async with self:
            results = []
            for i in range(0, len(identifiers), batch_size):
                batch = identifiers[i : i + batch_size]
                tasks = [self.get_dataset(identifier) for identifier in batch]
                batch_results = await asyncio.gather(*tasks)  # type: ignore
                results.extend(batch_results)
            return results

    def response_to_graph(
        self,
        response: Dict[str, Any],
        normalize_uris: bool = True,
    ) -> Graph:
        """Convert a JSON-LD response dictionary to an RDFLib Graph object.

        This utility method transforms JSON-LD metadata returned by the Dataverse API
        into an RDFLib Graph object, which enables advanced semantic data processing,
        querying with SPARQL, serialization to different RDF formats, and integration
        with other semantic web tools and workflows.

        RDFLib is a Python library for working with RDF (Resource Description Framework)
        data. By converting JSON-LD to an RDFLib Graph, you can:
        - Execute SPARQL queries on the metadata
        - Serialize the data to various RDF formats (Turtle, N-Triples, RDF/XML, etc.)
        - Merge multiple datasets into a single knowledge graph
        - Perform graph-based analysis and reasoning

        Args:
            response: A dictionary containing dataset metadata in JSON-LD format,
                typically obtained from get_dataset() or get_datasets() methods.
                The dictionary should contain valid JSON-LD with appropriate
                "@context" and semantic markup.
            normalize_uris: If True (default), normalize HTTP schema.org URIs to HTTPS
                to consolidate prefixes in Turtle serialization. This prevents duplicate
                prefixes like `schema:` and `schema1:` from appearing in the output.

        Returns:
            Graph: An RDFLib Graph object containing the parsed RDF triples from
            the JSON-LD input. The graph can be queried, serialized, or further
            processed using RDFLib's extensive API.

        Raises:
            ValueError: If the input dictionary is not valid JSON-LD or cannot
                be parsed by RDFLib.
            TypeError: If the response is not a dictionary.

        Examples:
            Convert dataset metadata to RDF graph::

                >>> api = SemanticApi(base_url="https://demo.dataverse.org")
                >>> metadata = api.get_dataset("doi:10.11587/8H3N93")
                >>> graph = api.response_to_graph(metadata)
                >>> print(f"Graph contains {len(graph)} triples")

            Query the graph with SPARQL::

                >>> metadata = api.get_dataset("doi:10.11587/8H3N93")
                >>> graph = api.response_to_graph(metadata)
                >>> query = '''
                ...     SELECT ?title WHERE {
                ...         ?dataset a ?type .
                ...         ?dataset <http://schema.org/name> ?title .
                ...     }
                ... '''
                >>> results = graph.query(query)
                >>> for row in results:
                ...     print(f"Title: {row.title}")

            Serialize to different RDF formats::

                >>> graph = api.response_to_graph(metadata)
                >>> turtle_data = graph.serialize(format='turtle')
                >>> print(turtle_data)

            Merge multiple datasets into one graph::

                >>> identifiers = ["doi:10.11587/8H3N93", "doi:10.11587/ABC123"]
                >>> combined_graph = Graph()
                >>> for metadata in api.get_datasets(identifiers):
                ...     dataset_graph = api.response_to_graph(metadata)
                ...     combined_graph += dataset_graph
                >>> print(f"Combined graph has {len(combined_graph)} triples")

        Note:
            The resulting Graph object preserves all the semantic relationships
            and context from the original JSON-LD, making it suitable for advanced
            semantic web applications and linked data workflows.
        """
        # Extract base URI from response to prevent local file path resolution
        # Prefer @id, then url, then use base_url as fallback
        base_uri = None
        if "@id" in response:
            base_uri = response["@id"]
        elif "url" in response:
            base_uri = response["url"]
        elif hasattr(self, "base_url") and self.base_url:
            base_uri = self.base_url

        # Parse with base URI to prevent RDFLib from resolving relative paths
        # against the current working directory
        if base_uri:
            graph = Graph().parse(
                data=json.dumps(response), format="json-ld", base=base_uri
            )
        else:
            graph = Graph().parse(data=json.dumps(response), format="json-ld")

        if normalize_uris:
            graph = self._normalize_schema_org_uris(graph)
        return graph

    def responses_to_graph(
        self, responses: Sequence[Dict[str, Any]], normalize_uris: bool = True
    ) -> Graph:
        """Convert a sequence of JSON-LD responses to an RDFLib Graph object.

        This method efficiently converts a sequence of JSON-LD responses into an RDFLib
        Graph object, which enables advanced semantic data processing, querying with
        SPARQL, serialization to different RDF formats, and integration with other
        semantic web tools and workflows.

        Args:
            responses: A sequence of JSON-LD response dictionaries.
            normalize_uris: If True (default), normalize HTTP schema.org URIs to HTTPS
                to consolidate prefixes in Turtle serialization. This prevents duplicate
                prefixes like `schema:` and `schema1:` from appearing in the output.

        Returns:
            Graph: An RDFLib Graph object containing all triples from the responses.
        """
        graphs = [
            self.response_to_graph(response, normalize_uris=normalize_uris)
            for response in responses
        ]
        graph = graphs[0]
        for g in graphs[1:]:
            graph += g
        return graph

    def _normalize_schema_org_uris(self, graph: Graph) -> Graph:
        """Normalize HTTP schema.org URIs to HTTPS to consolidate prefixes.

        Optimized single-pass implementation using string slicing and minimal allocations.
        RDFLib doesn't provide built-in URI normalization, so we create a new graph efficiently.

        This helper method replaces all occurrences of http://schema.org/ URIs
        with https://schema.org/ URIs in the graph. This is done to ensure the
        correct one is used, since there are clashes between HTTP and HTTPS versions
        of schema.org URIs in the JSON-LD data from Dataverse, which causes RDFLib
        to create separate prefixes (e.g., `schema:` and `schema1:`) in Turtle serialization.

        By normalizing to HTTPS (the commonly used and official standard for schema.org),
        all schema.org URIs are consolidated into a single prefix, resulting in cleaner
        and more consistent Turtle output.

        Args:
            graph: The RDFLib Graph to normalize.

        Returns:
            Graph: A new Graph with normalized URIs (HTTP schema.org URIs replaced
            with HTTPS equivalents), or the original graph if no normalization occurred.
        """
        # Constants for performance
        HTTP_PREFIX = "http://schema.org/"
        HTTPS_PREFIX = "https://schema.org/"
        PREFIX_LEN = 18

        # Helper function to normalize a single URIRef (reduces code duplication)
        uri_cache = {}

        def normalize_uri(uri):
            if isinstance(uri, URIRef):
                uri_str = str(uri)
                if uri_str.startswith(HTTP_PREFIX):
                    return uri_cache.setdefault(
                        uri_str, URIRef(HTTPS_PREFIX + uri_str[PREFIX_LEN:])
                    )
            return uri

        # Single-pass: normalize and build graph, track if any normalization occurred
        normalized_graph = Graph()
        needs_normalization = False

        for s, p, o in graph:
            s_norm = normalize_uri(s)
            p_norm = normalize_uri(p)
            o_norm = normalize_uri(o)

            # Track if normalization occurred (for early return optimization)
            if s_norm is not s or p_norm is not p or o_norm is not o:
                needs_normalization = True

            normalized_graph.add((s_norm, p_norm, o_norm))

        # Return original graph if no normalization occurred (zero-copy optimization)
        return graph if not needs_normalization else normalized_graph
