from __future__ import annotations

import asyncio
import time
import warnings
from contextlib import _GeneratorContextManager
from functools import cached_property
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
    overload,
)

import httpx
import pandas as pd
from asyncer import asyncify
from pydantic import (
    ConfigDict,
    Field,
    PrivateAttr,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)
from rdflib import Graph
from typing_extensions import Self

from ..filesystem.dvfs import DataverseFS
from ..filesystem.reader import DataverseFileReader
from ..filesystem.writer import DataverseFileWriter
from ..models import info
from ..models.dataset import create, edit_get
from ..models.dataset.create import DatasetCreateBody, DatasetVersion
from ..models.file.filemeta import Checksum, UploadBody, UploadResponse
from .connect import MetadataBlockBase
from .contentbase import ContentBase
from .dataverse import Dataverse
from .file import File

if TYPE_CHECKING:
    from .collection import Collection

SemanticApiFormat = Literal["semantic_api"]
GraphFormat = Union[str, SemanticApiFormat, List[Union[SemanticApiFormat, str]]]

SEMANTIC_FORMATS = {"application/ld+json", "application/json"}


class Dataset(ContentBase):
    """
    A Dataverse Dataset object, representing the core container of data, metadata, and files within a Dataverse instance.

    This class provides a convenient interface for interacting with Dataverse datasets, including reading and updating metadata,
    accessing files in the dataset, and supporting read operations for tabular data using pandas.

    Attributes:
        identifier (Optional[str]): The unique identifier (such as DOI or database ID) for the dataset.
        license (Union[str, info.License, None]): The assigned license for the dataset, as a string or License object.
        metadata_blocks (Dict[str, MetadataBlockBase]): All metadata blocks associated with the dataset, keyed by block name.
        dataverse (Dataverse): The parent Dataverse object this dataset belongs to.
    """

    model_config = ConfigDict(
        validate_assignment=True,
    )

    identifier: Optional[int] = Field(
        default=None,
        description="Dataset identifier (DOI or database ID)",
    )

    persistent_identifier: Optional[str] = Field(
        default=None,
        description="Dataset persistent identifier (DOI)",
    )

    persistent_url: Optional[str] = Field(
        default=None,
        description="Dataset persistent URL",
    )

    version: Optional[str] = Field(
        default=":draft",
        description="Dataset version",
    )

    license: Union[str, info.License, None] = Field(
        default=None,
        description="The license assigned to this dataset.",
    )

    metadata_blocks: Annotated[
        Dict[str, MetadataBlockBase], Field(default_factory=dict)
    ] = Field(
        default_factory=dict,
        description="Metadata blocks of the dataset",
        repr=False,
    )

    dataverse: "Dataverse" = Field(
        ...,
        description="The Dataverse instance this dataset belongs to",
        exclude=True,
        repr=False,
    )

    _fs: Optional[DataverseFS] = PrivateAttr(default=None)

    @classmethod
    def from_doi_url(cls, doi_url: str) -> Tuple[Dataverse, Dataset]:
        """
        Create a Dataset instance from a DOI URL.

        This method follows the DOI URL to extract the base Dataverse URL and persistent identifier,
        then creates both a Dataverse instance and fetches the corresponding Dataset.

        Args:
            doi_url (str): The DOI URL pointing to a dataset (e.g., "https://doi.org/10.18419/DARUS-5539")

        Returns:
            Tuple[Dataverse, Dataset]: A tuple containing the Dataverse instance and the Dataset object

        Raises:
            ValueError: If the URL doesn't lead to a valid Dataverse instance or if the persistent
                       identifier cannot be extracted from the URL parameters
            httpx.HTTPStatusError: If the HTTP request to the DOI URL fails

        Example:
            >>> dataverse, dataset = Dataset.from_doi_url("https://doi.org/10.18419/DARUS-5539")
            >>> print(dataset.persistent_identifier)
            doi:10.18419/DARUS-5539
        """
        response = httpx.get(doi_url, follow_redirects=True)
        response.raise_for_status()

        base_url = f"{response.url.scheme}://{response.url.host}"
        params = dict(response.url.params)

        try:
            dataverse = Dataverse(base_url=base_url)
        except Exception as e:
            raise ValueError(
                "Could not create a Dataverse instance from the base URL. Maybe the dataset you are trying to access is not available or not hosted on a Dataverse instance."
            ) from e

        persistent_identifier = params.get("persistentId")

        if not persistent_identifier:
            raise ValueError(
                "Persistent identifier is required to create a dataset from a DOI URL. Maybe the dataset you are trying to access is not available or not hosted on a Dataverse instance."
            )

        dataset = dataverse.fetch_dataset(persistent_identifier)
        return dataverse, dataset

    @property
    def is_locked(self) -> bool:
        """
        Check if the dataset is locked.
        """
        return len(self.locks) > 0

    @property
    def is_in_review(self) -> bool:
        """
        Check if the dataset is in review.
        """
        return any(lock.lock_type == "InReview" for lock in self.locks)

    @property
    def locks(self) -> List[locks.Lock]:
        """
        Get the locks of the dataset.
        """
        if self.persistent_identifier is None:
            raise ValueError("Dataset identifier is required to get locks.")
        return self.dataverse.native_api.get_dataset_lock(
            self.persistent_identifier
        ).root

    def wait_for_unlock(self) -> None:
        """
        Wait for the dataset to be unlocked.
        """
        while self.is_locked:
            self.dataverse.native_api.logger.info(
                f"Dataset {self.persistent_identifier} is locked, waiting for unlock..."
            )
            time.sleep(0.5)

        self.dataverse.native_api.logger.info(
            f"Dataset {self.persistent_identifier} is unlocked"
        )

    def refresh(
        self,
        version: Union[
            Literal[":latest", ":latest-published", ":draft"], str
        ] = ":latest",
    ) -> Dataset:
        """
        Refresh the dataset from the Dataverse server.
        """
        if self.persistent_identifier is None:
            raise ValueError("Dataset identifier is required to refresh.")

        fresh_dataset = self.dataverse.fetch_dataset(
            self.persistent_identifier,
            version=version,
        )

        self.version = fresh_dataset.version
        self.persistent_identifier = fresh_dataset.persistent_identifier
        self.persistent_url = fresh_dataset.persistent_url
        self.identifier = fresh_dataset.identifier
        self.license = fresh_dataset.license
        self.metadata_blocks = fresh_dataset.metadata_blocks

        return self

    def checkout(
        self,
        version: Union[
            Literal[":latest", ":latest-published", ":draft"], str
        ] = ":latest",
    ) -> Dataset:
        """
        Checkout the dataset to the specified version.
        """
        return self.refresh(version=version)

    @computed_field
    @property
    def url(self) -> str:
        """
        Get the URL of the dataset.
        """
        from urllib.parse import urlencode, urljoin, urlparse, urlunparse

        if self.persistent_identifier is None:
            raise ValueError(
                "Dataset identifier is required to get the URL. You may need to upload the dataset first."
            )
        base_url = self.dataverse.base_url
        path = "dataset.xhtml"
        base_path = urljoin(base_url, path)
        parsed = urlparse(base_path)
        query = urlencode({"persistentId": self.persistent_identifier})

        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                query,
                parsed.fragment,
            )
        )

    def open_in_browser(self) -> None:
        """
        Open the dataset in your system's default web browser.

        This method constructs the dataset's persistent URL
        and launches it using Python's ``webbrowser`` module.

        Example:
            >>> dataset.open_in_browser()

        Raises:
            ValueError: If the dataset identifier is not set.
        """
        import webbrowser

        webbrowser.open(self.url)

    @computed_field
    @property
    def title(self) -> str:
        """
        Get the title of the dataset from the citation metadata block.

        Returns:
            str: The dataset title.

        Raises:
            AssertionError: If the citation metadata block is unavailable.
        """
        assert "citation" in self.metadata_blocks, "Citation metadata block is required"
        return self.metadata_blocks["citation"]["title"]

    @title.setter
    def title(self, value: str) -> None:
        """
        Set the title for the dataset in the citation metadata block.

        Args:
            value (str): The new title for the dataset.

        Raises:
            AssertionError: If the citation metadata block is unavailable.
        """
        assert "citation" in self.metadata_blocks, "Citation metadata block is required"
        self.metadata_blocks["citation"]["title"] = value

    @computed_field(repr=False)
    @property
    def description(self) -> str:
        """
        Retrieve the dataset's description from the citation block.

        Returns:
            str: The dataset description.

        Raises:
            AssertionError: If the citation metadata block is unavailable.
        """
        assert "citation" in self.metadata_blocks, "Citation metadata block is required"
        return self.metadata_blocks["citation"]["dsDescription"][0][
            "dsDescriptionValue"
        ]

    @description.setter
    def description(self, value: str) -> None:
        """
        Set the dataset description in the citation metadata block.

        Args:
            value (str): The new description string.

        Raises:
            AssertionError: If the citation metadata block is unavailable.
        """
        assert "citation" in self.metadata_blocks, "Citation metadata block is required"
        self.metadata_blocks["citation"]["dsDescription"] = [
            {"dsDescriptionValue": value}
        ]

    @computed_field
    @property
    def authors(self) -> List[Dict[str, Any]]:
        """
        Get the authors of the dataset from the citation metadata block.
        """
        assert "citation" in self.metadata_blocks, "Citation metadata block is required"
        return [
            author.model_dump(by_alias=True, exclude_none=True)
            for author in self.metadata_blocks["citation"]["author"]
        ]

    @computed_field
    @property
    def subjects(self) -> List[str]:
        """
        Get the subjects of the dataset from the citation metadata block.
        """
        assert "citation" in self.metadata_blocks, "Citation metadata block is required"
        return self.metadata_blocks["citation"]["subject"]

    def dict(self, include: Optional[Sequence[str]] = None) -> Dict[str, Any]:
        """
        Generate a dictionary representation of this Dataset, omitting fields that are unset.

        Args:
            include: Optional list of metadata block names to include. If not specified, all metadata blocks will be included.

        Returns:
            Dict[str, Any]: A dict containing dataset fields with non-None values.
        """

        serialized = self.model_dump(exclude_none=True)

        if include is not None:
            serialized["metadata_blocks"] = {
                k: serialized["metadata_blocks"][k]
                for k in include
                if k in serialized["metadata_blocks"]
            }

        return serialized

    @overload
    def export(
        self,
        format: Literal["semantic_api"],
    ) -> Dict[str, Any]: ...

    @overload
    def export(
        self,
        format: str,
    ) -> Union[str, Dict[str, Any]]: ...

    def export(
        self,
        format: Union[str, SemanticApiFormat],
    ) -> Union[str, Dict[str, Any]]:
        """
        Export the dataset's metadata in the specified format via the Dataverse API.

        Args:
            format (str): The export format (e.g., 'dataverse_json', 'DublinCore', etc.)

        Returns:
            Union[str, Dict[str, Any]]: The exported metadata, as a string or parsed dict.
        """
        if format == "semantic_api":
            return self.dataverse.semantic_api.get_dataset(self._ensure_identifier())

        return self.dataverse.native_api.get_dataset_export(
            self._ensure_identifier(pid=True),
            format,
            self.version,
        )

    def graph(self, format: GraphFormat) -> Graph:
        """
        Get the RDF graph of the dataset by exporting metadata in semantic formats.

        This method retrieves the dataset's metadata in one or more semantic formats
        (such as JSON-LD, RDF/XML, Turtle, etc.) and converts them into an RDF graph
        using rdflib. The method validates that the requested formats are available
        and support semantic data representation.

        Args:
            format (GraphFormat): A single format string or list of format strings
                specifying the semantic export formats to use. Valid formats are
                those available in the Dataverse instance that have semantic media types.

        Returns:
            Graph: An rdflib Graph object containing the merged RDF triples from
                all requested export formats.

        Raises:
            ValueError: If any of the requested formats are not available in the
                Dataverse instance or do not support semantic data representation.

        Examples:
            >>> # Get graph using a single format
            >>> graph = dataset.graph("OAI_ORE")

            >>> # Get graph using multiple formats
            >>> graph = dataset.graph(["OAI_ORE", "JSON-LD"])

            >>> # Query the resulting graph
            >>> for subj, pred, obj in graph:
            ...     print(f"{subj} {pred} {obj}")
        """
        if isinstance(format, str):
            format = [format]

        valid_formats = {
            name: export_format
            for name, export_format in self.dataverse.export_formats.items()
            if export_format.media_type in SEMANTIC_FORMATS
        }

        invalid_formats = [
            f for f in format if f not in valid_formats and f != "semantic_api"
        ]
        if invalid_formats:
            raise ValueError(
                f"Invalid formats: {invalid_formats} are not available in the Dataverse instance."
                f"Available formats: {list(valid_formats.keys())}"
            )

        if len(format) == 1:
            exported = [
                self._add_missing_id(cast(Dict[str, Any], self.export(format[0])))
            ]
        else:
            exported = [
                self._add_missing_id(export)
                for export in asyncio.run(self._batch_format_export(format))
                if isinstance(export, dict)
            ]

        # Suppress rdflib ConjunctiveGraph deprecation warning
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="ConjunctiveGraph is deprecated, use Dataset instead",
                category=DeprecationWarning,
                module="rdflib.plugins.parsers.jsonld",
            )
            return self.dataverse.semantic_api.responses_to_graph(exported)

    async def _batch_format_export(
        self,
        formats: List[str],
    ) -> List[Union[str, Dict[str, Any]]]:
        """
        Fetch the formats from the Dataverse instance.
        """
        fetch_format_async = asyncify(self.export)
        return await asyncio.gather(*[fetch_format_async(f) for f in formats])

    def _add_missing_id(self, exported: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add the missing ID to the exported data.
        """
        if "@id" not in exported:
            if self.persistent_url is not None:
                exported["@id"] = self.persistent_url
            else:
                exported["@id"] = self.identifier
        return exported

    @property
    def fs(self) -> DataverseFS:
        """
        Get a file system interface (DataverseFS) for this dataset to access its files.

        Returns:
            DataverseFS: The file system for file operations (openbin, open_tabular, etc.).

        Raises:
            ValueError: If the dataset has no identifier.
        """
        if self._fs is None:
            self._fs = DataverseFS(
                base_url=self.dataverse.base_url,
                identifier=self._ensure_identifier(),
                api_token=self.dataverse.api_token,
                native_api=self.dataverse.native_api,
                data_access_api=self.dataverse.data_access_api,
            )
        return self._fs

    @property
    def files(self):
        """
        Obtain a view of files in the dataset, with both iterator and dict-like access.

        Returns:
            FilesView: Provides iteration over all files and allows lookup by path.

        Examples:
            >>> for file in dataset.files:
            ...     print(file.path)
            >>> file = dataset.files["data/file.csv"]
            >>> print(file.metadata.data_file.filesize)
        """
        from .views.filesview import FilesView

        return FilesView(dataset=self)

    @property
    def tabular_files(self):
        """
        Get a view of tabular files in the dataset.
        """
        from .views.filesview import FilesView

        return FilesView(dataset=self, tabular_only=True)

    @model_validator(mode="after")
    def _post_init(self) -> Self:
        """
        Set the default license if not provided.
        """
        if isinstance(self.license, info.License):
            self.license = self.dataverse.default_license
        return self

    @field_serializer("metadata_blocks")
    def serialize_metadata_blocks(
        self, metadata_blocks: Dict[str, MetadataBlockBase]
    ) -> Dict[str, Any]:
        """
        Serialize non-empty metadata blocks for this dataset for export or storage.

        Args:
            metadata_blocks (Dict[str, MetadataBlockBase]): Map of block names to block objects.

        Returns:
            Dict[str, Any]: Dictionary mapping block names to their serializable form, excluding empty blocks.
        """
        result = {}
        for name, block in metadata_blocks.items():
            if not block.is_empty:
                result[name] = block.model_dump()
        return result

    @field_validator("license", mode="before")
    @classmethod
    def validate_license(cls, value: Union[info.License, str]) -> Optional[str]:
        """
        Converts a License object into its string name, or returns the string if already provided.

        Args:
            value (Union[info.License, str, None]): License value to validate/convert.

        Returns:
            Optional[str]: The license name as a string, or None if not set.

        Example:
            >>> dataset.license = License(name="CC0", uri="...")
            >>> dataset.license = "MIT"
        """
        if isinstance(value, info.License):
            return value.name
        return value

    def update_metadata(self):
        """
        Update the dataset metadata on the Dataverse server using the native API.
        Pushes all changes (metadata blocks and license) from this object to Dataverse.

        Raises:
            ValueError: If this dataset does not have an identifier.
        """
        payload = self.to_dataverse_edit_dict()

        import rich

        rich.print(payload)

        assert self.persistent_identifier is not None, (
            "Dataset persistent identifier is required to update metadata."
        )

        self.native_api.edit_dataset_metadata(
            self.persistent_identifier,
            payload,
            replace=True,
        )

        # We will wait for the dataset to unlock to avoid race conditions
        self.wait_for_unlock()

        # Then, we will refresh the dataset to get the latest metadata and draft state
        self.refresh()

    def publish(
        self,
        release_type: Literal["minor", "major", "updatecurrent"] = "major",
    ):
        """
        Publishes a dataset within its collection.

        Raises:
            ValueError: If the dataset has no persistent identifier.
        """

        # Await for the dataset to unlock
        self.wait_for_unlock()

        if self.persistent_identifier is None:
            raise ValueError("Dataset persistent identifier is required to publish.")

        if self.license is None:
            raise ValueError(
                "Dataset license is required to publish. Use `Dataverse.licenses` to get a list of available licenses and set the license using the `license` attribute."
            )

        self.dataverse.native_api.publish_dataset(
            self.persistent_identifier,
            release_type,
        )

        # Wait for the dataset to unlock to avoid race conditions
        self.wait_for_unlock()
        self.refresh(":latest-published")

    def submit_to_review(self):
        """
        Submit the dataset to review.
        """
        if self.persistent_identifier is None:
            raise ValueError(
                "Dataset persistent identifier is required to submit to review."
            )

        self.dataverse.native_api.submit_dataset_to_review(self.persistent_identifier)

    def return_to_author(self, reason: str):
        """
        Return the dataset to author.
        """
        if self.persistent_identifier is None:
            raise ValueError(
                "Dataset persistent identifier is required to return to author."
            )
        self.dataverse.native_api.return_dataset_to_author(
            pid=self.persistent_identifier,
            reason_for_return=reason,
        )

    def upload_to_collection(self, collection: Union[str, Collection]):
        """
        Create (upload) this dataset to a Dataverse collection using the native API.

        This method sends the current state of this Dataset object as a new dataset
        into the target Dataverse (collection). The metadata sent includes all
        metadata blocks and the license as set in this object.

        Args:
            collection (str): The dataverse alias or identifier into which this dataset
                will be created/uploaded.

        Returns:
            None

        Raises:
            httpx.HTTPStatusError: If the Dataverse API returns an error
            ValueError: If required dataset metadata is missing

        Example:
            >>> ds = Dataset(...)
            >>> ds.upload("mydataverse")
        """
        from .collection import Collection

        response = self.native_api.create_dataset(
            dataverse=collection.alias
            if isinstance(collection, Collection)
            else collection,
            metadata=self.to_dataverse_create_dict(),
        )

        self.persistent_identifier = response.persistent_id
        self.identifier = response.id
        self.version = ":draft"

    def to_dataverse_create_dict(
        self,
        dataset_type: Optional[str] = None,
        license: Optional[str] = None,
    ) -> DatasetCreateBody:
        """
        Convert this dataset instance into a Dataverse-compatible dict (for API creation/upload).

        Args:
            dataset_type (Optional[str]): The dataset type tag (e.g., "dataset").
            license (Optional[str]): License name, overrides self.license if specified.

        Returns:
            DatasetCreateBody: Pydantic model ready for Dataverse API interaction.
        """
        metadata_blocks = {}

        for name, block in self.metadata_blocks.items():
            if not block.is_empty:
                metadata_blocks[name] = block.to_metadata_block()

        if isinstance(self.license, str):
            license = self.license
        elif isinstance(self.license, info.License):
            license = self.license.name

        return DatasetCreateBody(
            dataset_type=dataset_type,
            dataset_version=DatasetVersion(
                license=license,
                metadata_blocks=metadata_blocks,
            ),
        )

    def to_dataverse_edit_dict(self) -> edit_get.EditMetadataBody:
        """
        Convert this dataset instance into a Dataverse-compatible dict (for API editing).
        """
        license = (
            self.license.name
            if isinstance(self.license, info.License)
            else self.license
        )

        fields = [
            field
            for block in self.metadata_blocks.values()
            for field in block.to_update_metadata_block()
        ]

        return edit_get.EditMetadataBody(
            license=license,
            fields=fields,
        )

    def from_dataverse_dict(
        self,
        metadata: Union[edit_get.GetDatasetResponse, create.DatasetCreateBody],
    ) -> Self:
        """
        Update in-place this Dataset's metadata_blocks from a Dataverse API metadata dict or model.

        Args:
            metadata (edit_get.GetDatasetResponse or create.DatasetCreateBody): Metadata dict/model from Dataverse.

        Returns:
            Self: Self, but with updated metadata blocks loaded from the input.

        Raises:
            AssertionError: If input lacks metadata blocks.

        Note:
            Metadata blocks from Dataverse are loaded into self.metadata_blocks using
            each block's own from_dataverse_dict method.
        """
        if isinstance(metadata, edit_get.GetDatasetResponse):
            if (
                metadata.metadata_blocks is not None
                and len(metadata.metadata_blocks) > 0
            ):
                metadata_blocks = metadata.metadata_blocks
            elif (
                metadata.latest_version is not None
                and metadata.latest_version.metadata_blocks is not None
                and len(metadata.latest_version.metadata_blocks) > 0
            ):
                metadata_blocks = metadata.latest_version.metadata_blocks
        elif isinstance(metadata, create.DatasetCreateBody):
            metadata_blocks = metadata.dataset_version.metadata_blocks

        assert metadata_blocks is not None, "Metadata blocks are required"

        for block_name, block_data in metadata_blocks.items():
            block_instance = self.metadata_blocks[block_name]
            block_instance = block_instance.from_dataverse_dict(block_data)
            self.metadata_blocks[block_name] = block_instance

        return self

    @cached_property
    def json_schema(self) -> Dict[str, Any]:
        """
        Generate a JSON schema validating all metadata blocks of the dataset.

        Returns:
            Dict[str, Any]: A JSON schema representing all fields for this dataset,
                suitable for validation and UI generation.
        """
        schema = {
            "title": "Dataverse dataset schema",
            "$schema": "http://json-schema.org/draft-07/schema",
            "type": "object",
            "properties": {},
        }

        for name, block in self.metadata_blocks.items():
            schema["properties"][name] = block.model_json_schema(mode="validation")

        return schema

    @overload
    def open(
        self,
        path: File,
        mode: Literal["r", "rb"] = "r",
    ) -> DataverseFileReader: ...

    @overload
    def open(
        self,
        path: Union[str, File],
        mode: Literal["r", "rb"],
    ) -> DataverseFileReader: ...

    @overload
    def open(
        self,
        path: Union[str, File],
        mode: Literal["w", "wb"],
        *,
        description: Optional[str] = None,
        categories: Optional[List[str]] = None,
        content_type: Optional[str] = None,
        tab_ingest: Optional[bool] = None,
    ) -> DataverseFileWriter: ...

    def open(
        self,
        path: Union[str, File],
        mode: Literal["r", "rb", "w", "wb"] = "r",
        *,
        description: Optional[str] = None,
        categories: Optional[List[str]] = None,
        content_type: Optional[str] = None,
        tab_ingest: Optional[bool] = None,
    ) -> Union[DataverseFileReader, DataverseFileWriter]:
        """
        Open a file from the dataset for reading or writing, in binary or text mode.

        Args:
            path (Union[str, File]): The file path within the dataset (e.g., "data/file.txt" or "subdir/notes.csv")
                or a File object.
            mode (Literal["r", "rb", "w", "wb"], optional): File open mode.
                - "r" or "rb": Read mode (default, "r" is text, "rb" is binary).
                - "w" or "wb": Write mode ("w" is text, "wb" is binary; creates/replaces file).
            description: Optional file description (only available in write mode "w" or "wb").
            categories: Optional list of category strings (only available in write mode "w" or "wb").
            content_type: Optional MIME type (only available in write mode "w" or "wb").

        Returns:
            DataverseFileReader or DataverseFileWriter:
                - Reader-like object if opened in read mode.
                - Writer-like object if opened in write mode.

        Raises:
            FileNotFoundError: If specified file does not exist (in read mode).
            ValueError: If mode is invalid or metadata is provided in read mode.

        Examples:
            >>> # Read a file as text
            >>> with dataset.open("data/readme.txt") as f:
            ...     text = f.read()
            >>> # Read using a File object
            >>> file = dataset.files[0]
            >>> with dataset.open(file) as f:
            ...     text = f.read()
            >>> # Write a new file as binary
            >>> with dataset.open("outputs/results.bin", mode="wb") as f:
            ...     f.write(b"result data")
            >>> # Write with metadata
            >>> with dataset.open("outputs/results.bin", mode="wb", description="My file") as f:
            ...     f.write(b"result data")
        """

        if isinstance(path, File):
            path = path.path

        # Metadata is only allowed in write mode
        has_metadata = any(
            [
                description,
                categories,
                content_type,
                tab_ingest is not None,
            ]
        )
        if has_metadata and mode in ("r", "rb"):
            raise ValueError(
                "Metadata can only be provided in write mode ('w' or 'wb'), not read mode"
            )

        # Build metadata if provided (only in write mode)
        upload_metadata = None
        if has_metadata and mode in ("w", "wb"):
            # Parse path to get directory and filename for metadata building
            directory_label, filename = self._parse_dataset_path(path)
            upload_metadata = self._build_upload_metadata(
                directory_label=directory_label,
                filename=filename,
                description=description,
                categories=categories,
                content_type=content_type,
                tab_ingest=tab_ingest,
            )

        return self.fs.openbin(
            path,
            mode=mode,
            metadata=upload_metadata,
        )

    def upload_file(
        self,
        local_file_path: Union[str, Path],
        dataset_path: Optional[str] = None,
        *,
        description: Optional[str] = None,
        categories: Optional[List[str]] = None,
        content_type: Optional[str] = None,
    ) -> UploadResponse:
        """
        Upload a local file to the dataset.

        This method uploads a file from the local filesystem to the dataset.
        It reuses the same path and metadata handling as the `open()` method
        but uploads the file directly instead of streaming writes.

        Args:
            local_file_path: Path to the local file to upload (string or Path object).
            dataset_path: Optional path where the file should be stored in the dataset
                (e.g., "data/file.txt" or "subdir/notes.csv").
                If not provided, uses the basename of the local file path.
            description: Optional file description.
            categories: Optional list of category strings.
            content_type: Optional MIME type.
            friendly_type: Optional friendly type name.
            storage_identifier: Optional storage identifier.
            md5: Optional MD5 checksum.
            checksum: Optional checksum dict with "type" and "value" keys.
            tabular_data: Optional flag indicating if file is tabular.
            file_access_request: Optional flag for file access request.
            force_replace: Optional flag to force replacement if file exists.

        Returns:
            UploadResponse: Response object with upload confirmation and file information.

        Raises:
            FileNotFoundError: If the local file does not exist.
            ValueError: If the dataset identifier is not set.

        Example:
            >>> # Upload a local file (uses basename as dataset path)
            >>> dataset.upload_file("/path/to/local/file.txt")
            >>>
            >>> # Upload to specific dataset path
            >>> dataset.upload_file("/path/to/local/file.txt", "data/file.txt")
            >>>
            >>> # Upload with custom metadata
            >>> dataset.upload_file(
            ...     "/path/to/data.csv",
            ...     "data/data.csv",
            ...     description="My data file",
            ...     categories=["Data", "Research"]
            ... )
        """
        # Ensure dataset has identifier
        if self.identifier is None:
            raise ValueError(
                "Dataset identifier is required. You may need to upload the dataset first."
            )

        # Validate and normalize local file path
        local_path = self._validate_local_file(local_file_path)

        # Use dataset_path if provided, otherwise use basename of local file
        if dataset_path is None:
            dataset_path = local_path.name

        # Parse dataset path and build metadata
        directory_label, filename = self._parse_dataset_path(dataset_path)
        upload_metadata = self._build_upload_metadata(
            directory_label=directory_label,
            filename=filename,
            description=description,
            categories=categories,
            content_type=content_type,
        )

        # Check if file exists and determine if we're replacing
        file_id = self._get_existing_file_id(dataset_path)

        # Perform upload or replacement
        with open(local_path, "rb") as local_file:
            if file_id:
                response = self._replace_file(file_id, local_file, upload_metadata)
            else:
                response = self._upload_new_file(local_file, upload_metadata)

        # Clear cache to ensure fresh data on next read
        self.fs._cache.clear()

        return response

    def _validate_local_file(self, local_file_path: Union[str, Path]) -> Path:
        """Validate that the local file exists and return Path object."""
        local_path = (
            Path(local_file_path)
            if isinstance(local_file_path, str)
            else local_file_path
        )

        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_file_path}")

        return local_path

    def _parse_dataset_path(self, dataset_path: str) -> Tuple[str, str]:
        """Parse dataset path into directory and filename components."""
        dataset_path = dataset_path.strip("/")

        if "/" in dataset_path:
            directory_label, label = dataset_path.rsplit("/", 1)
        else:
            directory_label = ""
            label = dataset_path

        return directory_label, label

    def _build_upload_metadata(
        self,
        directory_label: str,
        filename: str,
        *,
        description: Optional[str] = None,
        categories: Optional[List[str]] = None,
        content_type: Optional[str] = None,
        friendly_type: Optional[str] = None,
        storage_identifier: Optional[str] = None,
        md5: Optional[str] = None,
        checksum: Optional[Dict[str, Optional[str]]] = None,
        tabular_data: Optional[bool] = None,
        file_access_request: Optional[bool] = None,
        force_replace: Optional[bool] = None,
        tab_ingest: Optional[bool] = None,
    ) -> UploadBody:
        """Build UploadBody from path components and optional metadata parameters."""
        # Start with defaults from path
        metadata_dict: Dict[str, Any] = {
            "directory_label": directory_label if directory_label else None,
            "filename": filename,
        }

        # Add optional metadata fields if provided
        if description is not None:
            metadata_dict["description"] = description
        if categories is not None:
            metadata_dict["categories"] = categories
        if content_type is not None:
            metadata_dict["content_type"] = content_type
        if friendly_type is not None:
            metadata_dict["friendly_type"] = friendly_type
        if storage_identifier is not None:
            metadata_dict["storage_identifier"] = storage_identifier
        if md5 is not None:
            metadata_dict["md5"] = md5
        if checksum is not None:
            if isinstance(checksum, dict):
                metadata_dict["checksum"] = Checksum(
                    type=checksum.get("type"),
                    value=checksum.get("value"),
                )
            else:
                metadata_dict["checksum"] = checksum
        if tabular_data is not None:
            metadata_dict["tabular_data"] = tabular_data
        if file_access_request is not None:
            metadata_dict["file_access_request"] = file_access_request
        if force_replace is not None:
            metadata_dict["force_replace"] = force_replace
        if tab_ingest is not None:
            metadata_dict["tab_ingest"] = tab_ingest

        return UploadBody(**metadata_dict)

    def _get_existing_file_id(self, dataset_path: str) -> Optional[int]:
        """Get the file ID if a file exists at the given dataset path."""
        try:
            existing_file = self.fs._find_file(dataset_path)
            if existing_file.data_file:
                return existing_file.data_file.id
        except FileNotFoundError:
            pass
        return None

    def _upload_new_file(
        self,
        local_file: Any,
        metadata: UploadBody,
    ) -> UploadResponse:
        """Upload a new file to the dataset."""
        if self.identifier is None:
            raise ValueError("Dataset identifier is required")
        return self.fs.native_api.upload_datafile(
            identifier=self.identifier,
            file=local_file,
            metadata=metadata,
        )

    def _replace_file(
        self,
        file_id: int,
        local_file: Any,
        metadata: UploadBody,
    ) -> UploadResponse:
        """Replace an existing file in the dataset."""
        return self.fs.native_api.replace_datafile(
            identifier=file_id,
            file=local_file,
            metadata=metadata,
        )

    def open_tabular(
        self,
        path: str,
        no_header: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load an entire tabular file (CSV, TSV, etc.) from the dataset as a pandas DataFrame.

        Args:
            path (str): Path to the file in the dataset.
            sep (str, optional): Delimiter to use (default: ',').
            no_header (bool, optional): If True, use integer columns instead of header row.
            **kwargs: Additional keyword arguments for pandas.read_csv().

        Returns:
            pd.DataFrame: The loaded data.

        Examples:
            >>> df = dataset.open_tabular("data/file.csv")
            >>> df = dataset.open_tabular("data/file.csv", no_header=True)
            >>> df = dataset.open_tabular(
            ...     "data/file.csv",
            ...     usecols=["col1", "col2"],
            ...     dtype={"col1": str, "col2": int},
            ...     na_values=["N/A", "null"],
            ... )
        """
        return self.fs.open_tabular(
            path,
            no_header=no_header,
            api_token=self.dataverse.api_token,
            **kwargs,
        )

    def stream_tabular(
        self,
        path: str,
        chunk_size: int = 10_000,
        no_header: bool = False,
        sep: str = ",",
        **kwargs,
    ) -> Iterator[pd.DataFrame]:
        """
        Stream a tabular file as multiple pandas DataFrames (chunked reads).

        Args:
            path (str): File path in the dataset.
            chunk_size (int, optional): Number of rows per yielded chunk (default: 10000).
            no_header (bool, optional): If True, use integer columns.
            sep (str, optional): Field delimiter (default: ',').
            **kwargs: Passed through to pandas.read_csv().

        Yields:
            pd.DataFrame: Yields each chunk as a DataFrame.

        Examples:
            >>> for chunk in dataset.stream_tabular("data/file.csv"):
            ...     print(chunk.head())
            >>> for chunk in dataset.stream_tabular("data/file.csv", no_header=True):
            ...     print(chunk.columns)
            >>> for chunk in dataset.stream_tabular(
            ...     "data/file.csv", usecols=[0, 1, 2], dtype={"col1": str}
            ... ):
            ...     process(chunk)
        """
        return self.fs.stream_tabular(
            path,
            chunk_size=chunk_size,
            no_header=no_header,
            api_token=self.dataverse.api_token,
            sep=sep,
            **kwargs,
        )

    @overload
    def bundle_datafiles(
        self,
        files: Union[Literal["all"], List[Union[File, str, int]]],
        stream: Literal[True],
    ) -> _GeneratorContextManager[httpx.Response, None, None]: ...

    @overload
    def bundle_datafiles(
        self,
        files: Union[Literal["all"], List[Union[File, str, int]]] = "all",
        stream: Literal[False] = False,
    ) -> bytes: ...

    def bundle_datafiles(
        self,
        files: Union[Literal["all"], List[Union[File, str, int]]] = "all",
        stream: bool = False,
    ) -> Union[
        bytes,
        _GeneratorContextManager[httpx.Response, None, None],
    ]:
        """
        Bundle one or multiple datafiles in the dataset together as a ZIP file (Dataverse "datafiles-bundle" API).

        Args:
            files (Union[Literal["all"], List[Union[File, str, int]]], optional):
                Files to include in the bundle. "all" (default) bundles all files.
                You can also provide a list of File objects, file paths, or file IDs.
            stream (bool, optional): If True, return a context manager to stream the ZIP response.

        Returns:
            httpx.Response or contextlib._GeneratorContextManager[httpx.Response]:
                The HTTP response object containing the ZIP, or a stream context.

        Raises:
            ValueError: If any file reference is not recognized.

        Examples:
            >>> with dataset.bundle_datafiles(files="all", stream=True) as resp:
            ...     with open("dataset.zip", "wb") as f:
            ...         for chunk in resp.iter_bytes():
            ...             f.write(chunk)
            >>> resp = dataset.bundle_datafiles(files=["mytab1.tab", "mytab2.tab"])
            >>> with open("some.zip", "wb") as f:
            ...     f.write(resp.read())
        """

        identifier = self._ensure_identifier()

        if files == "all":
            if stream:
                return self.native_api.stream_all_datafiles(
                    identifier,
                )
            else:
                return self.native_api.download_all_datafiles(
                    identifier,
                )

        file_ids = []

        for file in files:
            if isinstance(file, File):
                file_ids.append(file.identifier)
            elif isinstance(file, str):
                file_ids.append(file)
            elif isinstance(file, int):
                file_ids.append(file)
            else:
                raise ValueError(f"Invalid file type: {type(file)}")

        if stream:
            return self.data_access_api.stream_datafiles(file_ids)
        else:
            return self.data_access_api.get_datafiles(file_ids)

    @overload
    def _ensure_identifier(self) -> int: ...

    @overload
    def _ensure_identifier(self, pid: Literal[True]) -> str: ...

    def _ensure_identifier(self, pid: bool = False) -> Union[int, str]:
        """
        Internal method to require that this dataset has an identifier.

        Returns:
            str: The dataset identifier.

        Raises:
            ValueError: If the identifier is not set on this Dataset.

        Notes:
            This is used to enforce that certain actions (like downloading or bundling files) must
            only be done after the dataset is saved/uploaded to Dataverse.
        """

        if pid:
            assert self.persistent_identifier is not None, (
                "Dataset persistent identifier is required. Seems like you are trying to bundle datafiles from a local draft dataset. Please upload the dataset first to do this operation."
            )
            return self.persistent_identifier
        else:
            assert self.identifier is not None, (
                "Dataset identifier is required. Seems like you are trying to bundle datafiles from a local draft dataset. Please upload the dataset first to do this operation."
            )
            return self.identifier

    def __getitem__(self, key: str) -> MetadataBlockBase:
        """
        Access a metadata block on this dataset by block name using indexing.

        Args:
            key (str): The name of the metadata block.

        Returns:
            MetadataBlockBase: The metadata block instance.

        Examples:
            >>> citation = dataset["citation"]
        """
        return self.metadata_blocks[key]
