"""Dataverse factory class for creating Dataset instances."""

from __future__ import annotations

import asyncio
import re
import threading
from functools import cached_property, lru_cache
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Type,
    Union,
)

from asyncer import asyncify
from httpx import HTTPStatusError
from pydantic import BaseModel, Field, PrivateAttr, model_validator
from typing_extensions import Self, TypedDict

from pyDataverse.api.search import QueryOptions, SearchApi
from pyDataverse.dataverse.search import SearchResult

from ..api import DataAccessApi, MetricsApi, NativeApi, SemanticApi
from ..models import collection, info
from ..models.dataset import create, edit_get
from ..models.metadatablocks import MetadatablockSpecification
from .connect import create_model_from_block
from .metrics import Metrics

if TYPE_CHECKING:
    from .collection import Collection
    from .dataset import Dataset

VERSION_PATTERN = re.compile(r"^v?(\d+)(?:\.\d+)*")
MINIMUM_MAJOR_VERSION = 6


def _extract_major_version(version_string: str) -> int:
    """
    Extract the major version from a Dataverse version string.

    Supports canonical versions (e.g., ``6.10``, ``v6.10.1``, ``6.10.1-SNAPSHOT``)
    and versions with trailing descriptors returned by some installations
    (e.g., ``6.10 bugfixes``).

    Args:
        version_string: Raw version string returned by the Dataverse API.

    Returns:
        int: Parsed major version.

    Raises:
        ValueError: If the version string does not start with a valid version number.
    """
    match = VERSION_PATTERN.match(version_string.strip())

    if match is None:
        raise ValueError(
            f"Unable to parse version string: {version_string}. "
            "Expected to start with: vX.Y.Z, X.Y, X.Y.Z-SUFFIX, or X.Y <description>"
        )

    return int(match.group(1))

# Used for autocomplete in the create_dataset method
Subject = Literal[
    "Agricultural Sciences",
    "Arts and Humanities",
    "Astronomy and Astrophysics",
    "Business and Management",
    "Chemistry",
    "Computer and Information Science",
    "Earth and Environmental Sciences",
    "Engineering",
    "Law",
    "Mathematical Sciences",
    "Medicine, Health and Life Sciences",
    "Physics",
    "Social Sciences",
    "Other",
]


# Type alias for author
class Author(TypedDict, total=False):
    name: str
    affiliation: Optional[str]
    identifier_scheme: Optional[str]
    identifier: Optional[str]


# Type alias for contact
class Contact(TypedDict, total=False):
    name: str
    email: str
    affiliation: Optional[str]


class Dataverse(BaseModel):
    """
    Factory class for creating Dataset instances with metadata blocks.

    The Dataverse class connects to a Dataverse installation and provides
    methods to create Dataset objects with properly configured metadata blocks.
    It handles the fetching of metadata block specifications and creates
    properly typed Dataset instances with all available metadata blocks.

    Attributes:
        base_url: Base URL of the Dataverse installation
        api_token: Optional API token for authentication

    Example:
        >>> # Create a Dataverse instance
        >>> dv = Dataverse(base_url="https://demo.dataverse.org")
        >>>
        >>> # Create a dataset with all available metadata blocks
        >>> dataset = dv.create_dataset()
        >>>
        >>> # Access metadata blocks
        >>> dataset.metadata_blocks["citation"].title = "My Dataset Title"
    """

    base_url: Union[str, Literal["https://demo.dataverse.org"]] = Field(
        ...,
        description="Base URL of the Dataverse installation",
    )

    api_token: Optional[str] = Field(
        default=None,
        description="Optional API token for authentication",
        repr=False,
    )

    verbose: int = Field(
        default=1,
        description="Verbose level for the Dataverse instance",
        repr=False,
    )

    _native_api: Optional[NativeApi] = PrivateAttr(default=None)
    _data_access_api: Optional[DataAccessApi] = PrivateAttr(default=None)
    _semantic_api: Optional[SemanticApi] = PrivateAttr(default=None)
    _metrics_api: Optional[MetricsApi] = PrivateAttr(default=None)
    _search_api: Optional[SearchApi] = PrivateAttr(default=None)
    _factory_lock: threading.Lock = PrivateAttr(default_factory=threading.Lock)
    _factory_initialized: bool = PrivateAttr(default=False)

    @model_validator(mode="after")
    def _setup_api(self) -> Self:
        """
        Initialize the NativeApi instance after model validation.

        This validator runs after all field validation is complete and sets up
        the internal API client using the provided base_url and api_token.
        It also pre-initializes the dataset factory to prevent race conditions
        when multiple async operations try to fetch datasets simultaneously.

        Returns:
            Self: The validated Dataverse instance
        """
        # Check compatibility with the API version
        self._check_api_version()
        # Only setup APIs if they haven't been initialized yet
        self._ensure_apis_initialized()
        # Pre-initialize the factory to prevent race conditions in async operations
        self._ensure_factory_initialized()
        return self

    def _ensure_apis_initialized(self) -> None:
        """Ensure APIs are initialized. Called internally to prevent duplicate initialization."""
        if self._native_api is None:
            self._native_api = NativeApi(
                base_url=self.base_url,  # pyright: ignore[reportCallIssue]
                api_token=self.api_token,  # pyright: ignore[reportCallIssue]
                verbose=self.verbose,  # pyright: ignore[reportCallIssue]
            )

            self._data_access_api = DataAccessApi.from_api(self._native_api)
            self._semantic_api = SemanticApi.from_api(self._native_api)
            self._metrics_api = MetricsApi.from_api(self._native_api)
            self._search_api = SearchApi.from_api(self._native_api)

    def _ensure_factory_initialized(self) -> None:
        """
        Ensure the dataset factory is initialized to prevent race conditions.

        This method uses a lock to ensure only one thread initializes the factory
        at a time, preventing concurrent async operations from competing.
        """
        if not self._factory_initialized:
            with self._factory_lock:
                # Double-check pattern: another thread might have initialized it
                if not self._factory_initialized:
                    # Pre-initialize the factory with default enum_limit
                    # This populates the cache and prevents race conditions
                    self._dataset_factory(enum_limit=None)
                    self._factory_initialized = True

    def _check_api_version(self) -> None:
        """
        Check compatibility with the API version.

        Raises:
            ValueError: If the Dataverse instance version is below the minimum required version.
        """
        version = self.native_api.get_info_version()
        major_version = _extract_major_version(version.version)

        if major_version < MINIMUM_MAJOR_VERSION:
            raise ValueError(
                f"Dataverse version {version.version} is below the minimum required "
                f"version {MINIMUM_MAJOR_VERSION}. Please upgrade your Dataverse instance."
            )

    @property
    def native_api(self) -> NativeApi:
        """
        Access the NativeApi instance.

        Provides access to the underlying NativeApi client for direct API calls
        if needed. The API client is automatically configured with the base_url
        and api_token provided during initialization.

        Returns:
            NativeApi: The configured API client instance
        """
        self._ensure_apis_initialized()
        assert self._native_api is not None, "NativeApi not initialized"
        return self._native_api

    @property
    def data_access_api(self) -> DataAccessApi:
        """
        Access the DataAccessApi instance.
        """
        self._ensure_apis_initialized()
        assert self._data_access_api is not None, "DataAccessApi not initialized"
        return self._data_access_api

    @property
    def semantic_api(self) -> SemanticApi:
        """
        Access the SemanticApi instance.
        """
        self._ensure_apis_initialized()
        assert self._semantic_api is not None, "SemanticApi not initialized"
        return self._semantic_api

    @property
    def metrics_api(self) -> MetricsApi:
        """
        Access the MetricsApi instance.
        """
        self._ensure_apis_initialized()
        assert self._metrics_api is not None, "MetricsApi not initialized"
        return self._metrics_api

    @cached_property
    def version(self) -> info.VersionResponse:
        """
        Return the version of the Dataverse instance.
        """
        return self.native_api.get_info_version()

    @cached_property
    def licenses(self) -> Sequence[info.License]:
        """
        Return the list of available licenses from the Dataverse instance.
        """
        return self.native_api.get_available_licenses()

    @cached_property
    def default_license(self) -> info.License:
        """
        Return the default license from the Dataverse instance.
        """
        try:
            return next(license for license in self.licenses if license.is_default)
        except StopIteration:
            raise ValueError("No default license found")

    @property
    def metrics(self) -> Metrics:
        """
        Access the Metrics instance for retrieving Dataverse metrics.

        Provides access to various metrics including total counts, historical data,
        and breakdowns by subject, category, and location.

        Returns:
            Metrics: The Metrics instance configured with the MetricsApi

        Example:
            >>> dv = Dataverse("https://demo.dataverse.org")
            >>> # Get collections grouped by subject
            >>> df = dv.metrics.collections_by_subject
            >>> # Get total datasets count
            >>> result = dv.metrics.total("datasets")
        """
        self._ensure_apis_initialized()
        assert self._metrics_api is not None, "MetricsApi not initialized"
        return Metrics(metrics_api=self._metrics_api)

    @property
    def collections(self):
        """
        Return collections from the root collection.
        Supports both iteration and dict-like access by identifier.

        Examples:
            >>> # Iterator access
            >>> for coll in dv.collections:
            ...     print(coll.identifier)
            >>> # Dict-like access
            >>> coll = dv.collections["harvard"]
            >>> coll = dv.collections[123]  # by database ID
        """
        from .collection import Collection
        from .views.collectionview import CollectionView

        root = Collection(dataverse=self, identifier=":root")
        return CollectionView(collection=root, dataverse=self)

    @property
    def datasets(self):
        """
        Return datasets from the root collection.
        Supports both iteration and dict-like access by identifier.

        Examples:
            >>> # Iterator access
            >>> for ds in dv.datasets:
            ...     print(ds.title)
            >>> # Dict-like access
            >>> ds = dv.datasets["doi:10.5072/FK2/ABC123"]
            >>> ds = dv.datasets[123]  # by database ID
        """
        from .collection import Collection
        from .views.datasetview import DatasetView

        root = Collection(dataverse=self, identifier=":root")
        return DatasetView(collection=root, dataverse=self)

    @cached_property
    def export_formats(self) -> Dict[str, info.Exporter]:
        """
        Return the list of available export formats.
        """
        return self.native_api.get_export_formats()

    @cached_property
    def metadatablocks(self) -> Dict[str, MetadatablockSpecification]:
        """
        Return the list of available metadata blocks.
        """

        return self.native_api.get_metadatablocks(full=True)

    @lru_cache
    def _dataset_factory(
        self,
        enum_limit: Optional[int] = None,
    ) -> Callable[[], Dataset]:
        """
        Return the dataset factory.

        This method is cached to avoid repeated API calls. The factory is
        pre-initialized during Dataverse setup to prevent race conditions
        when multiple async operations try to fetch datasets simultaneously.
        """

        from .dataset import Dataset

        # Ensure APIs are initialized before fetching metadata blocks
        self._ensure_apis_initialized()

        self.native_api.logger.info("Fetching metadata blocks...")

        metadata_blocks = asyncio.run(self._get_metadata_blocks())

        blocks = {}

        # Add each metadata block to the dataset
        for block_name in metadata_blocks:
            blocks[block_name] = create_model_from_block(
                block_name,
                metadata_blocks[block_name].fields,
                enum_limit=enum_limit,
            )

        def factory(include: Optional[List[str]] = None) -> Dataset:
            dataset = Dataset(
                identifier=None,
                license=None,
                verbose=self.verbose,
                dataverse=self,
                version=None,
            )

            for block_name, model in blocks.items():
                if include is not None and block_name not in include:
                    continue
                dataset.metadata_blocks[block_name] = model()

            return dataset

        self.native_api.logger.info("Dataset factory initialized")

        return factory

    def search(
        self,
        query: str,
        per_page: int = 10,
        type: Optional[Literal["dataset", "collection", "dataverse"]] = None,
        options: Optional[QueryOptions] = None,
    ) -> SearchResult:
        """
        Search for datasets in the Dataverse instance.
        """
        from .search import SearchResult

        assert self._search_api is not None, "SearchApi not initialized"

        if per_page is not None:
            if options is None:
                options = QueryOptions(per_page=per_page)
            else:
                options.per_page = per_page

        if type is not None:
            options.type = "dataverse" if type == "collection" else type

        return SearchResult(
            search_response=self._search_api.search(query, options),
            dataverse=self,
        )

    def create_collection(
        self,
        alias: str,
        name: str,
        description: str,
        affiliation: str,
        dataverse_type: Literal[
            "DEPARTMENT",
            "JOURNALS",
            "LABORATORY",
            "ORGANIZATIONS_INSTITUTIONS",
            "RESEARCHERS",
            "RESEARCH_GROUP",
            "RESEARCH_PROJECTS",
            "TEACHING_COURSES",
            "UNCATEGORIZED",
        ],
        dataverse_contacts: List[str],
        parent: Union[Literal["root"], str] = "root",
    ) -> Collection:
        """
        Create a new Dataverse collection (sub-dataverse) at the root level.

        This method allows you to create a new collection inside the Dataverse installation
        by specifying the required metadata fields, including name, alias, affiliation, and
        the type of dataverse. Contacts for the collection should be passed as a list of email
        addresses (`dataverse_contacts`), which will be converted to the appropriate metadata objects.

        Args:
            alias (str): The unique, non-whitespace string identifier for the new collection (sub-dataverse).
            name (str): The human-readable name for the collection.
            description (str): Description for the collection.
            affiliation (str): The affiliation of the collection.
            dataverse_type (Literal): The type/category of the collection.
            dataverse_contacts (List[str]): List of emails for collection contacts.

        Returns:
            collection.CollectionCreateResponse: The server response containing details about the newly created collection.

        Example:
            >>> response = dataverse.create_collection(
            ...     alias="astro-data",
            ...     name="Astrophysics Data",
            ...     description="A collection for astrophysical datasets.",
            ...     affiliation="Department of Astronomy",
            ...     dataverse_type="LABORATORY",
            ...     dataverse_contacts=["astro@university.edu", "info@astro.org"],
            ... )
            >>> print(response.id, response.name)

        """
        from .collection import Collection

        metadata = collection.CollectionCreateBody(
            name=name,
            alias=alias,
            description=description,
            affiliation=affiliation,
            dataverse_type=dataverse_type,
            dataverse_contacts=[
                collection.Contact(contact_email=c) for c in dataverse_contacts
            ],
        )

        response = self.native_api.create_collection(
            parent=parent,
            metadata=metadata,
        )

        return Collection(dataverse=self, identifier=response.alias)

    def create_dataset(
        self,
        title: str,
        description: str,
        authors: List[Author],
        contacts: List[Contact],
        subjects: List[Subject],
        upload_to_collection: bool = True,
        collection: Optional[Union[Literal["root"], str]] = None,
        license: Optional[Union[str, info.License]] = None,
    ) -> Dataset:
        """
        Create a new Dataset with metadata blocks, ready to be uploaded to a Dataverse collection.

        This method initializes a Dataset instance with the specified core metadata fields,
        and includes all available metadata blocks from the Dataverse installation.
        Metadata blocks are constructed dynamically from API-provided specifications at runtime.

        Args:
            title (str): The title of the dataset (required, citation metadata block).
            description (str): The dataset’s description/abstract (citation block).
            authors (List[Author]): List of dataset authors (each must be an `Author` object).
            contacts (List[Contact]): List of contact persons for the dataset.
            subjects (List[Subject]): Subjects to categorize the dataset (controlled vocabulary).
            upload_to_collection (bool, optional): If True, the dataset will also be uploaded to the collection upon creation. Defaults to True.
            collection (Optional[Union[Literal["root"], str]], optional): Alias of the collection (dataverse) to upload to. Defaults to None (root dataverse).

        Returns:
            Dataset: The created Dataset instance with metadata blocks populated.

        Raises:
            Exception: If unable to fetch metadata block specifications from the server.

        Example:
            >>> dv = Dataverse("https://demo.dataverse.org")
            >>> ds = dv.create_dataset(
            ...     title="Neural Network Results",
            ...     description="Results and code for the paper.",
            ...     authors=[Author(name="Jane Smith", affiliation="UniX")],
            ...     contacts=[Contact(email="jane.smith@unix.edu")],
            ...     subjects=["Computer Science"]
            ... )
            >>> ds.metadata_blocks["citation"].title
            'Neural Network Results'
        """

        dataset = self._internal_create_dataset(
            title=title,
            description=description,
            authors=authors,
            contacts=contacts,
            subjects=subjects,
            license=license,
            _blocks_to_include=None,
        )

        if upload_to_collection:
            assert collection is not None, (
                "Collection is required to upload to a collection"
            )
            dataset.upload_to_collection(collection)
            dataset.refresh()

        return dataset

    def _internal_create_dataset(
        self,
        title: str,
        description: str,
        authors: List[Author],
        contacts: List[Contact],
        subjects: List[Subject],
        license: Optional[Union[str, info.License]] = None,
        _blocks_to_include: Optional[List[str]] = None,
    ) -> Dataset:
        """
        Create a new Dataset instance with metadata blocks.

        Fetches all available metadata blocks from the Dataverse installation
        and creates a Dataset instance with properly configured metadata blocks.
        The metadata blocks are dynamically created as Pydantic models based on
        the specifications retrieved from the Dataverse API.

        This method is cached to avoid repeated API calls for the same Dataverse
        instance, improving performance when creating multiple datasets.

        Returns:
            Dataset: A new Dataset instance with all available metadata blocks
                configured and ready for use

        Raises:
            Exception: If there's an error fetching metadata blocks from the API

        Example:
            >>> dv = Dataverse("https://demo.dataverse.org")
            >>> ds = dv.create_dataset()
            >>>
            >>> # Access citation metadata block
            >>> ds.metadata_blocks["citation"].title = "My Research Dataset"
            >>> ds.metadata_blocks["citation"].author = [{"authorName": "John Doe"}]
        """

        dataset = self._internal_create_blank_dataset(
            _blocks_to_include=_blocks_to_include
        )

        dataset.metadata_blocks["citation"]["title"] = title
        dataset.metadata_blocks["citation"]["subject"] = subjects
        dataset.metadata_blocks["citation"]["dsDescription"] = [
            {"dsDescriptionValue": description}
        ]

        for author in authors:
            assert "name" in author, "Name is required"
            dataset.metadata_blocks["citation"]["author"].append(
                {
                    "authorName": author["name"],
                    "authorAffiliation": author.get("affiliation", None),
                    "authorIdentifierScheme": author.get("identifier_scheme", None),
                    "authorIdentifier": author.get("identifier", None),
                }
            )

        for contact in contacts:
            assert "name" in contact, "Name is required"
            assert "email" in contact, "Email is required"
            dataset.metadata_blocks["citation"]["datasetContact"].append(
                {
                    "datasetContactName": contact["name"],
                    "datasetContactEmail": contact["email"],
                    "datasetContactAffiliation": contact.get("affiliation"),
                }
            )

        if license:
            dataset.license = license

        return dataset

    def _internal_create_blank_dataset(
        self,
        enum_limit: Optional[int] = None,
        _blocks_to_include: Optional[List[str]] = None,
    ) -> Dataset:
        # Ensure factory is initialized (safety check for edge cases)
        self._ensure_factory_initialized()
        return self._dataset_factory(enum_limit=enum_limit)()

    async def _get_metadata_blocks(
        self,
    ) -> Dict[str, MetadatablockSpecification]:
        """
        Asynchronously fetch all metadata block specifications.

        This private method retrieves the list of available metadata blocks
        and then fetches the full specification for each block concurrently
        using asyncio.gather for improved performance.

        Returns:
            Dict[str, MetadatablockSpecification]: A dictionary mapping block names
                to their full specifications

        Raises:
            Exception: If there's an error during the async operations, the
                exception is re-raised after cleaning up the async client
        """
        native_api = self.native_api  # Use property to ensure initialization
        blocks = [block.name for block in native_api.get_metadatablocks(full=False)]
        try:
            native_api._setup_async_client()
            tasks = [native_api.get_metadatablock(block) for block in blocks]
            results: List[MetadatablockSpecification] = await asyncio.gather(*tasks)  # type: ignore
            return {block.name: block for block in results}
        except Exception as e:
            native_api.client = None
            raise e
        finally:
            native_api.client = None

    def fetch_dataset(
        self,
        identifier: Union[str, int],
        version: Union[
            Literal[":latest", ":latest-published", ":draft"], str
        ] = ":latest",
    ) -> Dataset:
        return self._internal_fetch_dataset(
            identifier,
            version,
            _blocks_to_include=None,
        )

    def _internal_fetch_dataset(
        self,
        identifier: Union[str, int],
        version: Union[
            Literal[":latest", ":latest-published", ":draft"], str
        ] = ":latest",
        _blocks_to_include: Optional[List[str]] = None,
    ) -> Dataset:
        """
        Load a dataset from the Dataverse instance.

        Fetches the dataset metadata and persistent URL in parallel for improved
        performance. The dataset is then converted to a Dataset instance with all
        metadata blocks properly configured.

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`)
                or numeric database ID.
            version: Version to retrieve. Options are `:latest-published` (latest published),
                `:latest` (draft if exists, otherwise latest published), `:draft` (draft only),
                `x.y` (specific version like 1.0), or `x` (major version like 1).
                Defaults to `:latest`.
            _blocks_to_include: Optional list of metadata block names to include.
                If None, all available blocks are included.

        Returns:
            Dataset: A Dataset instance with metadata blocks populated from the server.
        """
        # Fetch dataset and persistent URL in parallel
        dataset, persistent_url = asyncio.run(
            self._fetch_dataset_and_url(identifier, version)
        )

        nu_dataset = self._internal_create_blank_dataset()
        nu_dataset.version = version
        nu_dataset.persistent_url = persistent_url

        nu_dataset.identifier = dataset.dataset_id
        nu_dataset.persistent_identifier = dataset.dataset_persistent_id

        if dataset.license:
            nu_dataset.license = dataset.license.name

        return nu_dataset.from_dataverse_dict(dataset)

    async def _fetch_dataset_and_url(
        self,
        identifier: Union[str, int],
        version: Union[Literal[":latest", ":latest-published", ":draft"], str],
    ) -> tuple[edit_get.GetDatasetResponse, str]:
        """
        Fetch dataset metadata and persistent URL in parallel using asyncify.

        This internal helper method uses `asyncer.asyncify` to convert synchronous
        API calls to async functions, then executes them concurrently using
        `asyncio.gather` for improved performance.

        Args:
            identifier: Dataset identifier - either a persistent ID or numeric database ID.
            version: Version to retrieve (e.g., `:latest`, `:latest-published`, `:draft`, or specific version).

        Returns:
            tuple: A tuple containing (dataset_response, persistent_url) where:
                - dataset_response: GetDatasetResponse object with dataset metadata
                - persistent_url: Optional[str] containing the persistent URL for the dataset
        """
        fetch_dataset = asyncify(self.native_api.get_dataset)
        fetch_persistent_url = asyncify(self.native_api.get_dataset_persistent_url)

        dataset, persistent_url = await asyncio.gather(
            fetch_dataset(identifier, version),
            fetch_persistent_url(identifier),
        )

        return dataset, persistent_url

    def fetch_collection(
        self,
        identifier: Union[str, int],
    ):
        """
        Load a collection from the Dataverse instance.
        """
        from .collection import Collection

        return Collection(dataverse=self, identifier=identifier)

    def from_dataverse_dict(
        self,
        dataset: Union[edit_get.GetDatasetResponse, create.DatasetCreateBody],
    ) -> Dataset:
        """
        Create a new dataset from a dictionary of data.
        """
        nu_dataset = self._internal_create_blank_dataset()

        if isinstance(dataset, edit_get.GetDatasetResponse):
            metadata_blocks = dataset.metadata_blocks
        elif isinstance(dataset, create.DatasetCreateBody):
            metadata_blocks = dataset.dataset_version.metadata_blocks

        assert metadata_blocks is not None, "Metadata blocks are required"

        for block_name, block_data in metadata_blocks.items():
            block_class = nu_dataset.metadata_blocks[block_name]
            nu_dataset.metadata_blocks[block_name] = block_class.from_dataverse_dict(
                block_data
            )

        if isinstance(dataset, create.DatasetCreateBody):
            license_obj = dataset.dataset_version.license
            if isinstance(license_obj, create.License):
                nu_dataset.license = license_obj.name
            else:
                nu_dataset.license = license_obj
        elif isinstance(dataset, edit_get.GetDatasetResponse):
            if dataset.license:
                nu_dataset.license = dataset.license.name
            else:
                nu_dataset.license = None

        return nu_dataset

    def to_pydantic(
        self,
        enum_limit: Optional[int] = None,
    ) -> Dict[str, Type[BaseModel]]:
        """
        Return a Pydantic model for the Dataverse instance.
        """
        dataset = self._internal_create_blank_dataset(enum_limit=enum_limit)
        blocks = {}

        for block_name, block in dataset.metadata_blocks.items():
            blocks[block_name] = block.__class__

        return blocks

    def __getitem__(
        self,
        identifier: Union[str, int],
    ) -> Union["Dataset", "Collection"]:
        errors = []
        for fetcher in (self.fetch_dataset, self.fetch_collection):
            try:
                return fetcher(identifier)
            except Exception as e:
                if isinstance(e, HTTPStatusError):
                    if e.response.status_code == 400:
                        errors.append(e)
                        continue
                    else:
                        raise e
                else:
                    raise e

        error_messages = "\n".join(
            [f"{i + 1}. {type(e).__name__}: {e}" for i, e in enumerate(errors)]
        )

        raise ValueError(
            f"Invalid identifier: {identifier}\nTried both collection and dataset fetchers, got errors:\n{error_messages}"
        )

    def __repr__(self) -> str:
        """
        Return a string representation of the Dataverse instance.

        Returns:
            str: A human-readable string showing the base URL and token status
        """
        token_status = "with token" if self.api_token else "without token"
        return f"Dataverse(base_url='{self.base_url}', {token_status})"

    def __hash__(self) -> int:
        """
        Return a hash value for the Dataverse instance.

        The hash is based on the base_url and api_token, allowing Dataverse
        instances to be used in sets and as dictionary keys.

        Returns:
            int: Hash value based on base_url and api_token
        """
        return hash((self.base_url, self.api_token))

    def json_schema(self) -> Dict[str, Any]:
        """
        Return the JSON schema for the Dataverse instance.
        """
        return self._internal_create_blank_dataset().json_schema
