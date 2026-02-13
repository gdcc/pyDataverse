import asyncio
import json
from contextlib import contextmanager
from pathlib import Path
from typing import (
    IO,
    Annotated,
    Any,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    Sequence,
    Union,
    overload,
)

import deprecation
import httpx
import pandas as pd
from pydantic import computed_field

from pyDataverse.models.dataset import locks
from pyDataverse.models.file import update

from ..models import (
    collection,
    dataset,
    file,
    info,
    message,
    metadatablocks,
)
from ..models.admin.users.user import User
from ..models.dataset.edit_get import Dataset
from ..models.dataset.review import ReturnToAuthorBody
from ..models.file.filemeta import UploadBody, UploadResponse
from .api import Api, Payload
from .utilities import crawl_collection
from .utilities.ds_fetcher import conc_get_datasets
from .utilities.fileinput import file_input

# Type alias for version string
Version = Literal[":draft", ":latest"] | str


class NativeApi(Api):
    """Class to access Dataverse's Native API.

    Provides methods to interact with Dataverse collections, datasets, files, and metadata
    through the Native API endpoints.

    Args:
        base_url: Base URL of the Dataverse instance.
        api_token: API token for authentication.
        api_version: API version to use.
    """

    @computed_field
    @property
    def base_url_api_native(self) -> str:
        return self.base_url_api

    @computed_field
    @property
    def api_base_url(self) -> str:
        return self.base_url_api

    @deprecation.deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use 'get_collection' instead.",
    )
    def get_dataverse(self, identifier: str) -> collection.Collection:
        return self.get_collection(identifier)

    def get_collection(self, identifier: Union[str, int]) -> collection.Collection:
        """Retrieve complete metadata about a specific dataverse.

        This endpoint returns detailed information about a dataverse including its name,
        alias, description, creation date, and other metadata properties.

        HTTP: GET /api/dataverses/{identifier}

        Args:
            identifier: Dataverse ID (numeric), alias, or the special value `:root` for the root dataverse.

        Returns:
            Collection object containing complete dataverse metadata.
        """
        url = self._assemble_url(f"dataverses/{identifier}")
        return self.get_request(
            url=url,
            use_async=self.client is not None,
            response_model=collection.Collection,
        )

    @deprecation.deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use 'create_collection' instead.",
    )
    def create_dataverse(
        self,
        parent: str,
        metadata: Payload[collection.CollectionCreateBody],
    ) -> collection.CollectionCreateResponse:
        return self.create_collection(parent, metadata)

        """Create a new dataverse collection.

        This endpoint creates a new dataverse collection.

        HTTP: POST /api/dataverses/{identifier}
        """

    def create_collection(
        self,
        parent: Union[Literal["root"], str],
        metadata: Payload[collection.CollectionCreateBody],
    ) -> collection.CollectionCreateResponse:
        """Create a new dataverse collection under a specified parent.

        This endpoint generates a new dataverse as a child of the specified parent dataverse.
        The new dataverse is created in DRAFT status and requires the fields name, alias, and
        dataverseContacts to be provided in the metadata. See the example dataverse.json file
        for complete metadata structure.

        HTTP: POST /api/dataverses/{parent}
        Docs: http://guides.dataverse.org/en/latest/_downloads/dataverse-complete.json

        Args:
            parent: Parent dataverse identifier (alias or ID) where the new dataverse will be created.
            metadata: Dataverse metadata including required fields (name, alias, dataverseContacts).

        Returns:
            CollectionCreateResponse with the created dataverse information including its ID and persistent identifier.
        """
        payload = self._parse_payload(
            payload=metadata,
            model=collection.CollectionCreateBody,
        )

        url = self._assemble_url(f"dataverses/{parent}")
        response = self.post_request(
            url=url,
            data=payload.model_dump(by_alias=True),
            use_async=self.client is not None,
            response_model=collection.CollectionCreateResponse,
        )
        self.logger.info(
            f"Collection [green]{response.alias}[/green] in [blue]{parent}[/blue] created"
        )
        return response

    def update_collection(
        self,
        identifier: str,
        metadata: Payload[collection.UpdateCollection],
    ):
        """Update the metadata of a collection.

        This endpoint updates the metadata of a collection.

        HTTP: PUT /api/dataverses/{identifier}
        """
        payload = self._parse_payload(
            payload=metadata,
            model=collection.UpdateCollection,
        )

        url = self._assemble_url(f"dataverses/{identifier}")
        response = self.put_request(
            url=url,
            data=payload.model_dump(by_alias=True, exclude_none=True),
            use_async=self.client is not None,
            response_model=collection.Collection,
        )
        return response

    @deprecation.deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use 'publish_collection' instead.",
    )
    def publish_dataverse(self, identifier: str) -> collection.CollectionCreateResponse:
        """Publish a dataverse to make it publicly accessible.

        THIS METHOD IS DEPRECATED. USE publish_collection INSTEAD.

        This endpoint changes the status of a dataverse from DRAFT to PUBLISHED, making it
        visible to all users. Once published, the dataverse and its contents become discoverable
        through search and browsing.
        """
        return self.publish_collection(identifier)

    def publish_collection(
        self,
        identifier: str,
    ) -> collection.CollectionCreateResponse:
        """Publish a dataverse to make it publicly accessible.

        This endpoint changes the status of a dataverse from DRAFT to PUBLISHED, making it
        visible to all users. Once published, the dataverse and its contents become discoverable
        through search and browsing.

        HTTP: POST /api/dataverses/{identifier}/actions/:publish

        Args:
            identifier: Dataverse ID (numeric) or alias to publish.

        Returns:
            CollectionCreateResponse with the published dataverse information and status.
        """
        url = self._assemble_url(f"dataverses/{identifier}/actions/:publish")
        response = self.post_request(
            url=url,
            use_async=self.client is not None,
            response_model=collection.CollectionCreateResponse,
        )
        self.logger.info(f"Dataverse {identifier} published")
        return response

    @deprecation.deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use 'delete_collection' instead.",
    )
    def delete_dataverse(self, identifier: str) -> message.Message:
        """Delete an unpublished dataverse.

        THIS METHOD IS DEPRECATED. USE delete_collection INSTEAD.

        This endpoint permanently removes a dataverse from the system. Only unpublished
        dataverses can be deleted through the API. The dataverse must be empty (no datasets
        or child dataverses) before deletion.
        """
        return self.delete_collection(identifier)

    def delete_collection(self, identifier: str) -> message.Message:
        """Delete an unpublished collection.

        This endpoint permanently removes a dataverse from the system. Only unpublished
        dataverses can be deleted through the API. The dataverse must be empty (no datasets
        or child dataverses) before deletion.

        HTTP: DELETE /api/dataverses/{identifier}

        Args:
            identifier: Dataverse ID (numeric) or alias to delete.

        Returns:
            Message object confirming the deletion.
        """
        url = self._assemble_url(f"dataverses/{identifier}")
        response = self.delete_request(
            url,
            use_async=self.client is not None,
            response_model=message.Message,
        )

        if response.message:
            self.logger.info(f"Dataverse {identifier} deleted")

        return response

    @deprecation.deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use 'get_collection_contents' instead.",
    )
    def get_dataverse_contents(
        self,
        alias: Annotated[
            Union[Literal[":root"], str],
            "Collection alias or :root for the root collection.",
        ] = ":root",
    ) -> List[collection.content.Collection | collection.content.Dataset]:
        """Retrieve the immediate contents of a dataverse.

        THIS METHOD IS DEPRECATED. USE get_collection_contents INSTEAD.

        This endpoint returns a list of all datasets and child dataverses (sub-collections)
        directly contained within the specified dataverse. It does not recursively list
        contents of child dataverses.
        """
        return self.get_collection_contents(alias)

    def get_collection_contents(
        self,
        alias: Union[Literal[":root"], str, int] = ":root",
    ) -> List[Union[collection.content.Collection, collection.content.Dataset]]:
        """Retrieve the immediate contents of a collection.

        This endpoint returns a list of all datasets and child dataverses (sub-collections)
        directly contained within the specified collection. It does not recursively list
        contents of child dataverses.

        HTTP: GET /api/dataverses/{alias}/contents

        Args:
            alias: Collection alias.

        Returns:
            CollectionContent object containing lists of datasets and child dataverses.
        """

        url = self._assemble_url(f"dataverses/{alias}/contents")
        return self.get_request(
            url,
            use_async=self.client is not None,
            response_model=List[
                Union[
                    collection.content.Collection,
                    collection.content.Dataset,
                ]
            ],
        )

    @deprecation.deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use 'get_collection_assignments' instead.",
    )
    def get_dataverse_assignments(self, identifier: str) -> List[collection.Assignee]:
        """Retrieve all role assignments for a collection.

        THIS METHOD IS DEPRECATED. USE get_collection_assignments INSTEAD.

        This endpoint returns a list of all users and groups assigned to roles within the
        specified collection, along with their role information. Role assignments control
        who has permission to perform various actions on the collection.
        """
        return self.get_collection_assignments(identifier)

    def get_collection_assignments(self, alias: str) -> List[collection.Assignee]:
        """Retrieve all role assignments for a collection.

        This endpoint returns a list of all users and groups assigned to roles within the
        specified collection, along with their role information. Role assignments control
        who has permission to perform various actions on the collection.

        HTTP: GET /api/dataverses/{alias}/assignments

        Args:
            alias: Collection alias.

        Returns:
            List of Assignee objects containing user/group information and their assigned roles.
        """
        url = self._assemble_url(f"dataverses/{alias}/assignments")
        assignments = self.get_request(
            url,
            use_async=self.client is not None,
            response_model=List[collection.Assignee],
        )

        roles = self.get_dataverse_roles(alias)

        for assignment in assignments:
            role = next((role for role in roles if role.id == assignment.role_id), None)
            if role is not None:
                assignment.role = role

        return assignments

    @deprecation.deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use 'get_collection_facets' instead.",
    )
    def get_dataverse_facets(self, alias: str) -> List[str]:
        """Retrieve the configured facets for a collection.

        THIS METHOD IS DEPRECATED. USE get_collection_facets INSTEAD.

        This endpoint returns a list of metadata fields configured as facets for browsing
        and filtering datasets within the collection. Facets help users narrow down search
        results based on specific metadata criteria.
        """
        return self.get_collection_facets(alias)

    def get_collection_facets(self, alias: str) -> List[str]:
        """Retrieve the configured facets for a collection.

        This endpoint returns a list of metadata fields configured as facets for browsing
        and filtering datasets within the collection. Facets help users narrow down search
        results based on specific metadata criteria.

        HTTP: GET /api/dataverses/{alias}/facets

        Args:
            alias: Collection alias.

        Returns:
            List of facet field names configured for the collection.
        """
        url = self._assemble_url(f"dataverses/{alias}/facets")
        return self.get_request(
            url,
            use_async=self.client is not None,
            response_model=List[str],
        )

    def dataverse_id2alias(self, dataverse_id: str) -> str:
        """Convert a numeric dataverse ID to its alias.

        This helper method fetches the dataverse metadata using its numeric ID and extracts
        the alias string, which is often more user-friendly and stable than the numeric identifier.

        Args:
            dataverse_id: Numeric dataverse ID.

        Returns:
            The dataverse alias string.
        """
        return self.get_collection(dataverse_id).alias

    def get_dataset(
        self,
        identifier: Union[str, int],
        version: Optional[
            Union[
                Literal[":latest", ":latest-published", ":draft"],
                str,
            ]
        ] = ":latest",
    ) -> dataset.GetDatasetResponse:
        """Retrieve complete metadata for a specific dataset version.

        This endpoint returns detailed metadata including citation information, files,
        version history, and all custom metadata fields for the specified dataset version.
        It automatically detects whether the identifier is a persistent ID (DOI/Handle) or
        numeric database ID.

        If you do not specify the version, the function will return the latest version of the dataset.

        If you specify the version, the function will return the metadata for the specified version of the dataset.
        The version can be a specific version like 1.0, a major version like 1, or a draft version like :draft.
        The version can also be a published version like :latest-published, a draft version like :draft, or a specific version like 1.0.

        HTTP: GET /api/datasets/{identifier}/versions/{version}
        HTTP: GET /api/datasets/:persistentId/versions/{version}?persistentId={pid}

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`) or numeric database ID.
            version: Version to retrieve. Options are `:latest-published` (latest published),
                `:latest` (draft if exists, otherwise latest published), `:draft` (draft only),
                `x.y` (specific version like 1.0), or `x` (major version like 1). Optional, defaults to `:latest`.
            is_pid: Legacy parameter, no longer used. Identifier type is auto-detected.

        Returns:
            GetDatasetResponse object containing complete dataset metadata and version information.
        """
        params = {}

        if self._is_pid(identifier):
            # Use persistent ID endpoint for DOI/Handle identifiers
            base_path = "datasets/:persistentId"
            params["persistentId"] = identifier
        else:
            # Use numeric ID endpoint for database identifiers
            base_path = f"datasets/{identifier}"

        if version:
            # Append version path to get specific dataset version
            url = self._assemble_url(f"{base_path}/versions/{version}")
        else:
            # Use base path to get latest version
            url = self._assemble_url(base_path)

        return self.get_request(
            url,
            params=params,
            use_async=self.client is not None,
            response_model=dataset.GetDatasetResponse,
        )

    def get_datasets(
        self,
        identifiers: Sequence[str | int],
    ) -> Sequence[dataset.GetDatasetResponse]:
        """Retrieve metadata for multiple datasets concurrently.

        Makes concurrent API calls to efficiently fetch dataset metadata for multiple
        identifiers. Automatically handles both persistent IDs and numeric database IDs.

        Args:
            identifiers: Sequence of dataset identifiers (persistent IDs or numeric IDs).
            batch_size: Maximum concurrent requests (default: 50).

        Returns:
            Sequence of GetDatasetResponse objects for successfully retrieved datasets.

        Examples:
            >>> api = NativeApi(base_url="https://demo.dataverse.org")
            >>> datasets = api.get_datasets([123, 456, "doi:10.11587/8H3N93"])
        """
        self._setup_async_client()

        try:
            result = asyncio.run(conc_get_datasets(self, identifiers))
            self.client = None
            return result
        except Exception as e:
            self.client = None
            raise e

    def get_dataset_persistent_url(self, identifier: Union[str, int]) -> str:
        """Retrieve the persistent URL for a dataset.

        This endpoint returns the persistent URL for a dataset. We use a separate endpoint for
        two reasons:

        1) When fetching a specific version, the persistent URL is not available in the dataset metadata.
        2) When use the non-versioned `get_dataset` method, we essentially waste compute due to fetching the entire dataset metadata, when we only need the persistent URL.

        Hence, this endpoint this endpoint has its own JSON schema and response model.

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`) or numeric database ID.

        Returns:
            The persistent URL for the dataset.
        """
        params = {}
        if self._is_pid(identifier):
            url = self._assemble_url("datasets/:persistentId")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"datasets/{identifier}")

        return self.get_request(
            url,
            params=params,
            use_async=self.client is not None,
            response_model=dataset.GetDatasetPersistentUrlResponse,
        ).persistent_url

    def get_dataset_versions(
        self,
        identifier: Union[str, int],
    ) -> List[dataset.GetDatasetResponse]:
        """Retrieve all versions of a dataset.

        This endpoint returns a list of all published versions of a dataset, including
        version numbers, release dates, and a summary of changes. Each version contains
        complete metadata as it existed at the time of publication.

        HTTP: GET /api/datasets/{identifier}/versions
        HTTP: GET /api/datasets/:persistentId/versions?persistentId={pid}

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`) or numeric database ID.
            is_pid: Legacy parameter, no longer used. Identifier type is auto-detected.

        Returns:
            List of GetDatasetResponse objects, one for each version of the dataset.
        """
        params = {}
        if self._is_pid(identifier):
            url = self._assemble_url("datasets/:persistentId/versions")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"datasets/{identifier}/versions")

        return self.get_request(
            url,
            params=params,
            use_async=self.client is not None,
            response_model=List[dataset.GetDatasetResponse],
        )

    def get_dataset_version(
        self,
        identifier: Union[str, int],
        version: Version,
    ) -> dataset.GetDatasetResponse:
        """Retrieve a specific version of a dataset.

        This is an alias method that calls get_dataset() with the specified version parameter.
        It returns the complete metadata for the requested dataset version.

        HTTP: GET /api/datasets/{identifier}/versions/{version}
        HTTP: GET /api/datasets/:persistentId/versions/{version}?persistentId={identifier}

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`) or numeric database ID.
            version: Version string (e.g. `1.0`, `2.1`, `:draft`, `:latest`). Can be a specific version number or a version string.

        Returns:
            GetDatasetResponse object containing the dataset metadata for the specified version.
        """
        return self.get_dataset(identifier, version)

    def get_dataset_export(
        self,
        identifier: Union[str, collection.content.Dataset, Dataset],
        export_format: str,
        version: Optional[str] = None,
    ) -> Union[str, Dict[str, Any]]:
        """Export dataset metadata in various standardized formats.

        This endpoint exports the metadata of the currently published version of a dataset
        in different metadata schemas. The exported format can be used for metadata harvesting,
        citation management, or integration with other systems.

        HTTP: GET /api/datasets/export?exporter={format}&persistentId={pid}

        Args:
            identifier: Persistent identifier of the dataset (e.g. `doi:10.11587/8H3N93`).
            export_format: Metadata export format. Available formats include `ddi`, `oai_ddi`,
                `dcterms`, `oai_dc`, `schema.org`, and `dataverse_json`.
            as_dict: If True, parse the exported metadata as a dictionary. If False, return as string.

        Returns:
            String containing the exported metadata in the requested format, or dictionary if as_dict=True.
        """

        url = self._assemble_url("datasets/export")
        params = {"exporter": export_format}

        if version:
            params["version"] = version

        if isinstance(identifier, str):
            params["persistentId"] = identifier
        elif isinstance(identifier, collection.content.Dataset):
            params["persistentId"] = (
                f"{identifier.protocol}:{identifier.authority}{identifier.separator}{identifier.identifier}"
            )
        elif isinstance(identifier, Dataset):
            assert identifier.dataset_persistent_id is not None, (
                "Dataset persistent ID is required"
            )
            params["persistentId"] = str(identifier.dataset_persistent_id)

        exported = self.get_request(
            url,
            params=params,
            use_async=self.client is not None,
            response_model=str,
        )

        return exported

    @overload
    def get_datasets_export(
        self,
        identifiers: Sequence[str | collection.content.Dataset | Dataset],
        export_format: str,
        as_dict: Literal[True],
    ) -> Sequence[Dict[str, Any]]: ...

    @overload
    def get_datasets_export(
        self,
        identifiers: Sequence[str | collection.content.Dataset | Dataset],
        export_format: str,
        as_dict: bool = False,
    ) -> Sequence[str]: ...

    def get_datasets_export(
        self,
        identifiers: Sequence[str | collection.content.Dataset | Dataset],
        export_format: str,
        as_dict: bool = False,
        version: Union[
            Literal[":draft", ":latest", ":latest-published"], str
        ] = ":latest",
    ) -> Sequence[str | Dict[str, Any]]:
        """Export metadata for multiple datasets in various standardized formats.

        This method exports metadata for multiple datasets in the specified format.
        For large collections (20+ datasets), it uses asynchronous processing for better performance.

        Args:
            identifiers: Sequence of dataset identifiers - can be persistent IDs (strings),
                Dataset objects, or collection.content.Dataset objects.
            export_format: Metadata export format. Available formats include `ddi`, `oai_ddi`,
                `dcterms`, `oai_dc`, `schema.org`, and `dataverse_json`.
            as_dict: If True, parse the exported metadata as dictionaries. If False, return as strings.

        Returns:
            Sequence of exported metadata, either as strings or dictionaries depending on as_dict parameter.
        """

        exports = []

        for identifier in identifiers:
            export = self.get_dataset_export(
                identifier=identifier,
                export_format=export_format,
                version=version,
            )
            if as_dict and isinstance(export, str):
                try:
                    export = json.loads(export)
                except json.JSONDecodeError:
                    export = export
                else:
                    export = export
            else:
                export = export
            exports.append(export)

        return exports

    def download_all_datafiles(
        self,
        identifier: Union[str, int],
    ) -> bytes:
        """Download a dataset bundle containing all files.

        Downloads a ZIP archive containing all files in a dataset. This is a convenience
        method for bulk downloading all files from a dataset at once, which is more
        efficient than downloading files individually.

        HTTP: GET /api/access/dataset/{identifier}/bundle
        HTTP: GET /api/access/dataset/:persistentId/bundle?persistentId={identifier}
        Docs: https://guides.dataverse.org/en/latest/api/dataaccess.html#dataset-level-access

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`)
                or numeric database ID.

        Returns:
            bytes: The ZIP archive content containing all dataset files.
        """

        if self._is_pid(identifier):
            url = self._assemble_url("access/dataset/:persistentId")
            params = {"persistentId": identifier}
        else:
            url = self._assemble_url(f"access/dataset/{identifier}")
            params = {}

        return self.get_request(
            url,
            params=params,
            use_async=self.client is not None,
            response_model=bytes,
        )

    @contextmanager
    def stream_all_datafiles(
        self,
        identifier: Union[str, int],
    ) -> Generator[httpx.Response, Any, Any]:
        """Stream a dataset bundle containing all files.

        Downloads a ZIP archive containing all files in a dataset using streaming
        for efficient handling of large datasets. This is recommended for datasets
        with many files or large total file sizes to avoid memory issues.

        HTTP: GET /api/access/dataset/{identifier}/bundle
        HTTP: GET /api/access/dataset/:persistentId/bundle?persistentId={identifier}
        Docs: https://guides.dataverse.org/en/latest/api/dataaccess.html#dataset-level-access

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`)
                or numeric database ID.

        Returns:
            Generator yielding httpx.Response: Context manager that yields the streaming
            HTTP response for the ZIP archive.
        """
        if self._is_pid(identifier):
            url = self._assemble_url("access/dataset/:persistentId")
            params = {"persistentId": identifier}
        else:
            url = self._assemble_url(f"access/dataset/{identifier}")
            params = {}

        with self.stream_file_context(url, params=params) as response:
            yield response

    def create_dataset(
        self,
        dataverse: str,
        metadata: Payload[dataset.DatasetCreateBody],
        identifier: Optional[str | int] = None,
        publish: bool = False,
    ) -> dataset.DatasetCreateResponse:
        """Create a new dataset or import an existing dataset with a persistent identifier.

        This endpoint creates a new dataset in DRAFT status within the specified dataverse.
        Alternatively, it can import a dataset with an existing PID (DOI or Handle), optionally
        publishing it immediately. The metadata must be in Dataverse's native JSON format.

        HTTP: POST /api/dataverses/{dataverse}/datasets
        HTTP: POST /api/dataverses/{dataverse}/datasets/:import?pid={identifier}&release={yes|no}
        Docs: http://guides.dataverse.org/en/latest/api/native-api.html#create-a-dataset-in-a-dataverse
        Example: http://guides.dataverse.org/en/latest/_downloads/dataset-finch1.json

        Args:
            dataverse: Target dataverse identifier (alias like `root` or numeric ID like `1`).
            metadata: Complete dataset metadata in Dataverse native JSON format.
            identifier: Optional persistent or numeric identifier for importing an existing dataset (DOI or Handle format).
            publish: If True and a PID is provided, the dataset will be published immediately.
                Otherwise, it will remain in DRAFT status. Only applies when importing with a PID.

        Returns:
            DatasetCreateResponse containing the created dataset's ID, persistent identifier, and URL.
        """
        params = {"release": "yes" if publish else "no"}

        payload = self._parse_payload(
            payload=metadata,
            model=dataset.DatasetCreateBody,
        )

        if identifier and self._is_pid(identifier):
            url = self._assemble_url(f"dataverses/{dataverse}/datasets/:import")
            params["persistentId"] = str(identifier)
        else:
            url = self._assemble_url(f"dataverses/{dataverse}/datasets")

        response = self.post_request(
            url=url,
            params=params,
            data=payload.model_dump(by_alias=True),
            auth=self.auth,
            use_async=self.client is not None,
            response_model=dataset.DatasetCreateResponse,
        )

        self.logger.info(
            f"Dataset [green]{response.persistent_id}[/green] created at [blue]{dataverse}[/blue]"
        )
        return response

    def edit_dataset_metadata(
        self,
        identifier: Union[str, int],
        metadata: Payload[dataset.EditMetadataBody],
        replace: bool = False,
    ) -> dataset.edit_get.GetDatasetResponse:
        """Edit or update metadata fields of a draft dataset.

        This endpoint allows you to modify metadata for a dataset that is in DRAFT status.
        By default, it adds values to empty fields or appends to multi-value fields. If
        replace=True, it completely replaces existing metadata with the provided values.
        Only the fields you want to change need to be included in the metadata parameter.

        HTTP: PUT /api/datasets/{id}/editMetadata
        HTTP: PUT /api/datasets/:persistentId/editMetadata?persistentId={identifier}
        Docs: http://guides.dataverse.org/en/latest/api/native-api.html#edit-dataset-metadata

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`) or numeric database ID.
            metadata: Metadata fields to edit (only include fields you want to change).
            is_pid: If True, treat identifier as a persistent ID. If False, treat as numeric ID.
            replace: If True, completely replace existing metadata. If False, add to or append values.

        Returns:
            GetDatasetResponse containing the updated dataset metadata.
        """
        params = {}
        if self._is_pid(identifier):
            url = self._assemble_url("datasets/:persistentId/editMetadata/")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"datasets/editMetadata/{identifier}")

        params["replace"] = True if replace else False

        payload = self._parse_payload(
            payload=metadata,
            model=dataset.EditMetadataBody,
        )

        response = self.put_request(
            url=url,
            data=payload.model_dump(by_alias=True),
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=dataset.edit_get.GetDatasetResponse,
        )

        self.logger.info(
            f"Dataset [green]{response.dataset_persistent_id}[/green] updated"
        )
        return response

    def create_dataset_private_url(
        self,
        identifier: str,
    ) -> dataset.PrivateUrl:
        """Create a private URL for sharing an unpublished dataset.

        This endpoint generates a unique, anonymous URL that allows users to preview a draft
        dataset without requiring authentication. The private URL can be shared with reviewers
        or collaborators before the dataset is published.

        HTTP: POST /api/datasets/{id}/privateUrl
        HTTP: POST /api/datasets/:persistentId/privateUrl?persistentId={identifier}
        Docs: http://guides.dataverse.org/en/4.16/api/native-api.html#create-a-private-url-for-a-dataset

        Args:
            identifier: Dataset identifier - either a persistent ID or numeric database ID.

        Returns:
            PrivateUrl object containing the generated private URL and token.
        """
        params = {}

        if self._is_pid(identifier):
            url = self._assemble_url("datasets/:persistentId/privateUrl/")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"datasets/{identifier}/privateUrl")

        return self.post_request(
            url=url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=dataset.PrivateUrl,
        )

    def get_dataset_private_url(
        self,
        identifier: str,
    ) -> dataset.PrivateUrl:
        """Retrieve the existing private URL for a dataset.

        This endpoint returns the private URL information if one has been previously created
        for the dataset. Private URLs allow anonymous access to unpublished datasets for
        review purposes.

        HTTP: GET /api/datasets/{id}/privateUrl
        HTTP: GET /api/datasets/:persistentId/privateUrl?persistentId={identifier}
        Docs: http://guides.dataverse.org/en/4.16/api/native-api.html#get-the-private-url-for-a-dataset

        Args:
            identifier: Dataset identifier - either a persistent ID or numeric database ID.

        Returns:
            PrivateUrl object containing the private URL and token, if one exists.
        """
        params = {}
        if self._is_pid(identifier):
            url = self._assemble_url("datasets/:persistentId/privateUrl/")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"datasets/{identifier}/privateUrl")

        return self.get_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=dataset.PrivateUrl,
        )

    def delete_dataset_private_url(
        self,
        identifier: str,
    ) -> str:
        """Delete the private URL for a dataset.

        This endpoint permanently removes the private URL for a dataset, revoking anonymous
        access to the unpublished dataset. Any previously shared private URL will no longer
        work after deletion.

        HTTP: DELETE /api/datasets/{id}/privateUrl
        HTTP: DELETE /api/datasets/:persistentId/privateUrl?persistentId={identifier}
        Docs: http://guides.dataverse.org/en/4.16/api/native-api.html#delete-the-private-url-from-a-dataset

        Args:
            identifier: Dataset identifier - either a persistent ID or numeric database ID.

        Returns:
            Confirmation message string.
        """
        params = {}
        if self._is_pid(identifier):
            url = self._assemble_url("datasets/:persistentId/privateUrl")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"datasets/{identifier}/privateUrl")

        response = self.delete_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=message.Message,
        )

        assert response.message is not None, "Something went wrong, there is no message"
        self.logger.info(f"Dataset [green]{identifier}[/green] private URL deleted")

        return response.message

    def publish_dataset(
        self,
        pid: str,
        release_type: Literal["minor", "major", "updatecurrent"] = "major",
    ) -> dataset.DatasetPublishResponse:
        """Publish a dataset to make it publicly accessible with version control.

        This endpoint publishes a draft dataset, assigning it a version number and making it
        discoverable. For the first publication, version 1.0 is assigned. Subsequent publications
        increment the version based on the release_type: 'minor' for minor changes (2.3 → 2.4),
        'major' for significant changes (2.3 → 3.0), or 'updatecurrent' (superusers only) to
        update without changing the version. When workflows are configured, the endpoint returns
        202 ACCEPTED and publication occurs asynchronously.

        HTTP: POST /api/datasets/:persistentId/actions/:publish?type={type}&persistentId={pid}

        Args:
            pid: Persistent identifier of the dataset (e.g. `doi:10.11587/8H3N93`).
            release_type: Version increment type - `minor` (x.y → x.y+1), `major` (x.y → x+1.0),
                or `updatecurrent` (no version change, superusers only).

        Returns:
            DatasetPublishResponse containing the published dataset information and persistent URL.
        """
        params = {}

        url = f"{self.base_url_api_native}/datasets/:persistentId/actions/:publish"

        params["persistentId"] = pid
        params["type"] = release_type

        response = self.post_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=dataset.DatasetPublishResponse,
        )

        self.logger.info(
            f"Dataset [green]{pid}[/green] published: [link={response.persistent_url}]{response.persistent_url}[/link]"
        )
        return response

    def submit_dataset_to_review(
        self,
        pid: str,
    ) -> message.Message:
        """Submit a dataset to review."""
        params = {
            "persistentId": pid,
        }

        url = self._assemble_url("datasets/:persistentId/submitForReview")
        response = self.post_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=message.Message,
        )

        self.logger.info(f"Dataset [green]{pid}[/green] submitted for review")

        return response

    def return_dataset_to_author(
        self,
        pid: str,
        reason_for_return: str,
    ) -> None:
        """Return a dataset to author."""

        params = {"persistentId": pid}
        url = self._assemble_url("datasets/:persistentId/returnToAuthor")
        data = ReturnToAuthorBody(reason_for_return=reason_for_return)

        self.post_request(
            url,
            auth=self.auth,
            params=params,
            data=data.model_dump(by_alias=True),
            use_async=self.client is not None,
            response_model=message.Message,
        )

        self.logger.info(f"Dataset [green]{pid}[/green] returned to author")

    def get_dataset_lock(
        self,
        identifier: Union[str, int],
        type: Optional[
            Literal[
                "Ingest",
                "Workflow",
                "InReview",
                "finalizePublication",
                "EditInProgress",
                "FileValidationFailed",
            ]
        ] = None,
    ) -> locks.LockResponse:
        """Check if a dataset is currently locked and retrieve lock information.

        This endpoint returns information about any locks currently placed on the dataset.
        Datasets can be locked during ingest, workflow processing, or by administrators.
        The lock API was introduced in Dataverse 4.9.3.

        HTTP: GET /api/datasets/:persistentId/locks?persistentId={identifier}

        Args:
            identifier: Dataset identifier - either a persistent ID or numeric database ID.

        Returns:
            Response containing lock status and details.
        """
        params = {}

        if self._is_pid(identifier):
            url = f"{self.base_url_api_native}/datasets/:persistentId/locks/"
            params["persistentId"] = identifier
        else:
            url = f"{self.base_url_api_native}/datasets/{identifier}/locks"

        if type:
            params["type"] = type

        return self.get_request(
            url,
            auth=True,
            params=params,
            use_async=self.client is not None,
            response_model=locks.LockResponse,
        )

    def set_dataset_assignment(
        self,
        identifier: Union[str, int],
        assignee: str,
        role: str,
    ):
        """Set the role assignments for a dataset.

        This endpoint sets the role assignments for a dataset.
        """

        if self._is_pid(identifier):
            dataset = self.get_dataset(identifier)
            assert dataset.dataset_id is not None, "Dataset ID is required"
            identifier = str(dataset.dataset_id)

        url = self._assemble_url(f"datasets/{identifier}/assignments")

        return self.post_request(
            url,
            data={
                "assignee": assignee,
                "role": role,
            },
            auth=self.auth,
            use_async=self.client is not None,
            response_model=message.Message,
        )

    def get_dataset_assignments(
        self,
        identifier: Union[str, int],
    ) -> List[dataset.DatasetAssignment]:
        """Retrieve all role assignments for a dataset.

        This endpoint returns a list of all users and groups assigned to roles within the
        specified dataset, along with their permission details. Role assignments determine
        who can view, edit, or manage the dataset.

        HTTP: GET /api/datasets/{id}/assignments
        HTTP: GET /api/datasets/:persistentId/assignments?persistentId={pid}

        Args:
            identifier: Dataset identifier - either a persistent ID or numeric database ID.

        Returns:
            Response containing list of role assignments for the dataset.
        """
        params = {}
        if self._is_pid(identifier):
            url = f"{self.base_url_api_native}/datasets/:persistentId/assignments/"
            params["persistentId"] = identifier
        else:
            url = f"{self.base_url_api_native}/datasets/{identifier}/assignments"

        return self.get_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=List[dataset.DatasetAssignment],
        )

    def delete_dataset(
        self,
        identifier: Union[str, int],
    ):
        """Delete an unpublished draft dataset.

        This endpoint permanently removes a dataset that has never been published. Published
        datasets cannot be deleted through the API - they must be deleted through the GUI or
        destroyed using the destroy_dataset method (superusers only).

        HTTP: DELETE /api/datasets/{id}
        HTTP: DELETE /api/datasets/:persistentId?persistentId={identifier}

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`) or numeric database ID.

        Returns:
            Response object confirming deletion or raising an error if the dataset is published.
        """
        params = {}

        if self._is_pid(identifier):
            url = f"{self.base_url_api_native}/datasets/:persistentId/"
            params["persistentId"] = identifier
        else:
            url = f"{self.base_url_api_native}/datasets/{identifier}"

        resp = self.delete_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
        )

        if resp.status_code == 404:
            error_msg = resp.json()["message"]
            raise ValueError(
                "ERROR: HTTP 404 - Dataset '{0}' was not found. MSG: {1}".format(
                    identifier, error_msg
                )
            )
        elif resp.status_code == 405:
            error_msg = resp.json()["message"]
            raise ValueError(
                "ERROR: HTTP 405 - "
                "Published datasets can only be deleted from the GUI. For "
                "more information, please refer to "
                "https://github.com/IQSS/dataverse/issues/778"
                " MSG: {0}".format(error_msg)
            )
        elif resp.status_code == 401:
            error_msg = resp.json()["message"]
            raise ValueError(
                "ERROR: HTTP 401 - User not allowed to delete dataset '{0}'. "
                "MSG: {1}".format(identifier, error_msg)
            )
        elif resp.status_code == 200:
            print("Dataset '{0}' deleted.".format(identifier))

        return resp

    def destroy_dataset(
        self,
        identifier: Union[str, int],
    ) -> message.Message:
        """Permanently and irreversibly destroy a dataset (superusers only).

        This endpoint is a destructive operation that completely removes a dataset and all
        its datafiles from the system, even if it has been published. The dataset is deleted
        from the database and the parent dataverse is re-indexed. This operation is permanent
        and cannot be undone. Only superusers can use this endpoint.

        HTTP: DELETE /api/datasets/{id}/destroy
        HTTP: DELETE /api/datasets/:persistentId/destroy?persistentId={identifier}
        Docs: http://guides.dataverse.org/en/4.16/api/native-api.html#delete-published-dataset

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`) or numeric database ID.

        Returns:
            Response object confirming the dataset was destroyed.
        """

        params = {}

        if self._is_pid(identifier):
            url = f"{self.base_url_api_native}/datasets/:persistentId/destroy/"
            params["persistentId"] = identifier
        else:
            url = f"{self.base_url_api_native}/datasets/{identifier}/destroy"

        resp = self.delete_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=message.Message,
        )

        if resp.message:
            self.logger.info(resp.message)

        return resp

    def datafiles_table(
        self,
        identifier: Union[str, int],
        filter_mime_types: List[str] = [],
    ) -> pd.DataFrame:
        """List all files in a dataset as a structured pandas DataFrame.

        Retrieves comprehensive file metadata for all files in a dataset and returns
        it as a pandas DataFrame for easy analysis and manipulation. This is the
        recommended starting point for file discovery and analysis workflows.

        Args:
            identifier: Dataset identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93`)
                       or numeric database ID.
            filter_mime_types: Optional list of MIME types to filter files by (e.g. ['text/csv', 'application/pdf']).
                       If provided, only files matching these content types will be included.

        Returns:
            pandas.DataFrame: DataFrame with columns:
                - id: File database ID
                - persistentId: File persistent identifier
                - path: Full file path including directory structure
                - description: File description
                - mime_type: File MIME/content type
                - restricted: Boolean indicating if file access is restricted
        """
        files = self.get_datafiles_metadata(identifier)

        # Filter by MIME types if specified
        if len(filter_mime_types) > 0:
            files = [
                file
                for file in files
                if file.data_file and file.data_file.content_type in filter_mime_types
            ]

        data = []
        for file in files:  # noqa: F402
            if file.data_file is None:
                continue
            data.append(
                {
                    "id": file.data_file.id,
                    "persistentId": file.data_file.persistent_id
                    if file.data_file.persistent_id
                    else file.persistent_id,
                    "path": "/".join(filter(None, [file.directory_label, file.label])),
                    "description": file.description,
                    "mime_type": file.data_file.content_type,
                    "restricted": file.restricted,
                }
            )
        return pd.DataFrame(data)

    def get_datafiles_metadata(
        self,
        identifier: Union[str, int],
        version: Version = ":latest",
        filter_mime_types: List[str] = [],
    ) -> List[file.FileInfo]:
        """Retrieve metadata for all files in a specific dataset version.

        This endpoint returns a list of all datafiles contained in the specified version
        of a dataset, including file names, sizes, types, descriptions, and other metadata
        associated with each file.

        HTTP: GET /api/datasets/:persistentId/versions/{version}/files?persistentId={identifier}
        Docs: http://guides.dataverse.org/en/latest/api/native-api.html#list-files-in-a-dataset

        Args:
            pid: Persistent identifier of the dataset (e.g. `doi:10.11587/8H3N93`).
            version: Dataset version string (e.g. `:latest`, `:draft`, `1.0`).

        Returns:
            Response containing list of file metadata objects for all files in the dataset version.
        """
        params = {}

        if self._is_pid(identifier):
            url = self._assemble_url(f"datasets/:persistentId/versions/{version}/files")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"datasets/{identifier}/files")

        files: List[file.FileInfo] = self.get_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=List[file.FileInfo],
        )

        if len(filter_mime_types) > 0:
            files = [
                file
                for file in files
                if file.data_file and file.data_file.content_type in filter_mime_types
            ]

        return files

    def get_datafile_metadata(
        self,
        identifier: Union[str, int],
    ) -> file.FileInfo:
        """Retrieve metadata for a specific datafile.

        This endpoint returns detailed metadata for a single file, including its name, size,
        content type, description, tags, and other file-level metadata.

        HTTP: GET /api/files/{id}
        HTTP: GET /api/files/:persistentId/?persistentId={identifier}

        Args:
            identifier: File identifier - either a file ID (numeric) or file persistent ID.
            is_draft: If True, retrieve draft version metadata. If False, retrieve published metadata.
            auth: If True, send API token for authentication.

        Returns:
            Response containing file metadata object.
        """
        params = {}

        if self._is_pid(identifier):
            url = self._assemble_url("files/:persistentId")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"files/{identifier}")

        return self.get_request(
            url,
            params=params,
            use_async=self.client is not None,
            response_model=file.FileInfo,
        )

    def upload_datafile(
        self,
        identifier: Union[str, int],
        file: Union[str, Path, IO[str], IO[bytes]],
        metadata: Payload[file.UploadBody],
    ) -> file.UploadResponse:
        """Upload a file to an existing dataset.

        This endpoint adds a new file to a dataset. The upload process includes automatic
        duplicate detection by comparing file content hashes. Optionally, you can provide
        metadata such as description, tags, and directory label for the file.

        HTTP: POST /api/datasets/{id}/add
        HTTP: POST /api/datasets/:persistentId/add?persistentId={identifier}
        Docs: http://guides.dataverse.org/en/latest/api/native-api.html#adding-files

        Args:
            identifier: Dataset identifier - either a persistent ID or numeric database ID.
            filename: Full path to the file to upload.
            metadata: Optional JSON string containing file metadata (description, tags, directoryLabel, etc.).

        Returns:
            Response object with upload confirmation and file information.
        """
        params = {}
        if self._is_pid(identifier):
            url = self._assemble_url("datasets/:persistentId/add")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"datasets/{identifier}/add")

        payload = self._parse_payload(
            payload=metadata,
            model=UploadBody,
        )

        files: dict[str, Any] = file_input(file, metadata=payload)

        if payload is not None:
            # We cannot use the HTTPX json parameter here because Dataverse
            # expects the payload as a string with in a multipart/form-data request.
            files["jsonData"] = payload.model_dump_json(
                by_alias=True,
                exclude_none=True,
            )

        return self.post_request(
            url,
            files=files,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=UploadResponse,
        )

    def update_datafile_metadata(
        self,
        identifier: Union[str, int],
        metadata: Payload[update.UpdateBody],
    ):
        """Update datafile metadata.

        metadata such as description, directoryLabel (File Path) and tags are not carried over from the file being replaced:
        Updates the file metadata for an existing file where ID is the
        database id of the file to update or PERSISTENT_ID is the persistent id
        (DOI or Handle) of the file. Requires a jsonString expressing the new
        metadata. No metadata from the previous version of this file will be
        persisted, so if you want to update a specific field first get the
        json with the above command and alter the fields you want.


        Also note that dataFileTags are not versioned and changes to these will update the published version of the file.

        This functions needs CURL to work!

        HTTP Request:

        .. code-block:: bash

            POST -F 'file=@file.extension' -F 'jsonData={json}' http://$SERVER/api/files/{id}/metadata?key={apiKey}
            curl -H "X-Dataverse-key:$API_TOKEN" -X POST -F 'jsonData={"description":"My description bbb.","provFreeform":"Test prov freeform","categories":["Data"],"restrict":false}' $SERVER_URL/api/files/$ID/metadata
            curl -H "X-Dataverse-key:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -X POST -F 'jsonData={"description":"My description bbb.","provFreeform":"Test prov freeform","categories":["Data"],"restrict":false}' "https://demo.dataverse.org/api/files/:persistentId/metadata?persistentId=doi:10.5072/FK2/AAA000"

        `Docs <http://guides.dataverse.org/en/latest/api/native-api.html#updating-file-metadata>`_.

        Args:
            identifier: Identifier of the dataset.
            json_str: Metadata as JSON string.
            is_filepid: ``True`` to use persistent identifier for datafile. ``False``, if
                not.

        Returns:
            The json string responded by the CURL request, converted to a
            dict().
        """

        params = {}
        if self._is_pid(identifier):
            url = self._assemble_url("files/:persistentId/metadata")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"files/{identifier}/metadata")

        payload = self._parse_payload(
            payload=metadata,
            model=update.UpdateBody,
        )

        return self.post_request(
            url,
            files={
                "jsonData": payload.model_dump_json(by_alias=True, exclude_none=True)
            },
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=UploadResponse,
        )

    def delete_datafile(self, identifier: Union[str, int]):
        """Delete a datafile from a dataset.

        The behavior of this operation depends on whether the dataset has been published:

        - **Unpublished Dataset**: The file will be permanently deleted from the dataset.
        - **Published Dataset**: The file is removed from the draft and future versions,
          but remains accessible in previously published versions.

        HTTP: DELETE /api/files/{id}
        HTTP: DELETE /api/files/:persistentId?persistentId={identifier}

        See: https://guides.dataverse.org/en/latest/api/native-api.html#delete-files-from-a-dataset

        Args:
            identifier: File identifier - either a persistent ID (e.g. `doi:10.11587/8H3N93/ABCDEF`)
                or numeric database ID.

        Returns:
            Message object confirming deletion with a success message.

        Example:
            >>> api = NativeApi('https://demo.dataverse.org', 'API_TOKEN')
            >>> # Delete by database ID
            >>> result = api.delete_datafile(12345)
            >>> # Delete by persistent ID
            >>> result = api.delete_datafile('doi:10.11587/8H3N93/ABCDEF')
        """
        params = {}

        if self._is_pid(identifier):
            url = self._assemble_url("files/:persistentId")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"files/{identifier}")

        return self.delete_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=message.Message,
        )

    def replace_datafile(
        self,
        identifier: Union[str, int],
        file: Union[str, Path, IO[str], IO[bytes]],
        metadata: Payload[file.UploadBody],
    ):
        """Replace datafile.

        HTTP Request:

        .. code-block:: bash

            POST -F 'file=@file.extension' -F 'jsonData={json}' http://$SERVER/api/files/{id}/replace?key={apiKey}

        `replacing-files <http://guides.dataverse.org/en/latest/api/native-api.html#replacing-files>`_.

        Args:
            identifier: Identifier of the file to be replaced.
            file: Full filename with path.
            json_str: Metadata as JSON string.
            is_filepid: ``True`` if ``identifier`` is a persistent identifier for the datafile.
                ``False``, if not.

        Returns:
            The json string responded by the CURL request, converted to a
            dict().
        """
        params = {}

        if self._is_pid(identifier):
            url = self._assemble_url("files/:persistentId/replace")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"files/{identifier}/replace")

        payload = self._parse_payload(
            payload=metadata,
            model=UploadBody,
        )
        files = file_input(file, metadata=payload)

        return self.post_request(
            url,
            data=payload.model_dump(by_alias=True),
            files=files,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=UploadResponse,
        )

    def get_info_version(self) -> info.VersionResponse:
        """Get the Dataverse version and build number.

        The response contains the version and build numbers. Requires no api
        token.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/info/version

        Returns:
            Response object of httpx library.
        """
        url = f"{self.base_url_api_native}/info/version"
        return self.get_request(
            url,
            info.VersionResponse,
            auth=self.auth,
            use_async=self.client is not None,
        )

    def get_export_formats(self) -> Dict[str, info.Exporter]:
        """Get available export formats.

        Returns:
            List of available export formats.
        """
        url = self._assemble_url("info/exportFormats")
        response = self.get_request(
            url,
            use_async=self.client is not None,
            response_model=info.ExportersResponse,
        )

        assert response.root is not None, "No export formats found"

        return response.root

    def get_info_server(self) -> info.ServerResponse:
        """Get dataverse server name.

        This is useful when a Dataverse system is composed of multiple Java EE
        servers behind a load balancer.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/info/server

        Returns:
            Response object of httpx library.
        """
        url = self._assemble_url("info/server")
        return self.get_request(
            url,
            info.ServerResponse,
            auth=self.auth,
            use_async=self.client is not None,
        )

    def get_info_api_terms_of_use(self) -> info.TermsOfUseResponse:
        """Get API Terms of Use url.

        The response contains the text value inserted as API Terms of use which
        uses the database setting :ApiTermsOfUse.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/info/apiTermsOfUse

        Returns:
            Response object of httpx library.
        """
        url = self._assemble_url("info/apiTermsOfUse")
        return self.get_request(
            url,
            info.TermsOfUseResponse,
            auth=self.auth,
            use_async=self.client is not None,
        )

    @overload
    def get_metadatablocks(
        self,
        full: Literal[True] = True,
        collection_alias: Optional[Union[str, int]] = None,
    ) -> Dict[str, metadatablocks.MetadatablockSpecification]: ...

    @overload
    def get_metadatablocks(
        self,
        full: Literal[False] = False,
        collection_alias: Optional[Union[str, int]] = None,
    ) -> List[metadatablocks.MetadatablockMeta]: ...

    def get_metadatablocks(
        self,
        full: bool = False,
        collection_alias: Optional[Union[str, int]] = None,
    ) -> Union[
        List[metadatablocks.MetadatablockMeta],
        Dict[str, metadatablocks.MetadatablockSpecification],
    ]:
        """Get info about all metadata blocks.

        Lists brief info about all metadata blocks registered in the system.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/metadatablocks

        Returns:
            Response object of httpx library.
        """

        if collection_alias is not None:
            url = self._assemble_url(f"dataverses/{collection_alias}/metadatablocks")
        else:
            url = self._assemble_url("metadatablocks")

        blocks = self.get_request(
            url,
            response_model=List[metadatablocks.MetadatablockMeta],
            auth=self.auth,
            use_async=self.client is not None,
        )

        if full:
            return {block.name: self.get_metadatablock(block.name) for block in blocks}
        else:
            return blocks

    def get_metadatablock(
        self,
        identifier: str,
    ) -> metadatablocks.MetadatablockSpecification:
        """Get info about single metadata block.

        Returns data about the block whose identifier is passed. identifier can
        either be the block's id, or its name.

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/metadatablocks/$identifier

        Args:
            identifier: Can be block's id, or it's name.

        Returns:
            MetadatablockSpecification object.
        """
        url = self._assemble_url(f"metadatablocks/{identifier}")
        return self.get_request(
            url,
            auth=self.auth,
            use_async=self.client is not None,
            response_model=metadatablocks.MetadatablockSpecification,
        )

    def get_user_api_token_expiration_date(self) -> message.Message:
        """Get the expiration date of an Users's API token.

        HTTP Request:

        .. code-block:: bash

            curl -H X-Dataverse-key:$API_TOKEN -X GET $SERVER_URL/api/users/token

        Returns:
            Response object of httpx library.
        """
        url = self._assemble_url("users/token")
        response = self.get_request(
            url,
            auth=self.auth,
            use_async=self.client is not None,
            response_model=message.Message,
        )

        if response.message:
            self.logger.info(response.message)

        return response

    def recreate_user_api_token(self) -> message.Message:
        """Recreate an Users API token.

        HTTP Request:

        .. code-block:: bash

            curl -H X-Dataverse-key:$API_TOKEN -X POST $SERVER_URL/api/users/token/recreate

        Returns:
            Response object of httpx library.
        """
        url = self._assemble_url("users/token/recreate")
        response = self.post_request(
            url,
            use_async=self.client is not None,
            auth=self.auth,
            response_model=message.Message,
        )

        if response.message:
            self.logger.info(response.message)

        return response

    def delete_user_api_token(self) -> message.Message:
        """Delete an Users API token.

        HTTP Request:

        .. code-block:: bash

            curl -H X-Dataverse-key:$API_TOKEN -X POST $SERVER_URL/api/users/token/recreate

        Returns:
            Response object of httpx library.
        """
        url = self._assemble_url("users/token")
        response = self.delete_request(
            url,
            use_async=self.client is not None,
            auth=self.auth,
            response_model=message.Message,
        )

        if response.message:
            self.logger.info(response.message)

        return response

    def get_dataverse_roles(self, identifier: str) -> List[collection.Role]:
        """All the roles defined directly in the dataverse by identifier.

        `Docs <https://guides.dataverse.org/en/latest/api/native-api.html#list-roles-defined-in-a-dataverse>`_

        .. code-block:: bash

            GET http://$SERVER/api/dataverses/$id/roles

        Args:
            identifier: Can either be a dataverse id (long), a dataverse alias (more
                robust), or the special value ``:root``.

        Returns:
            Response object of httpx library.
        """
        url = self._assemble_url(f"dataverses/{identifier}/roles")
        return self.get_request(
            url,
            use_async=self.client is not None,
            auth=self.auth,
            response_model=List[collection.Role],
        )

    def create_role(
        self,
        dataverse_id: str,
        role: Payload[collection.Role],
    ) -> collection.Role:
        """Create a new role in a dataverse.

        If no dataverse_id is provided, the role will be created in the root dataverse.

        `Docs <https://guides.dataverse.org/en/latest/api/native-api.html#id2>`_

        HTTP Request:

        .. code-block:: bash

            POST http://$SERVER/api/roles?dvo=$dataverseIdtf&key=$apiKey

        Args:
            role: Role to create.
            dataverse_id: Can be alias or id of a Dataverse.

        Returns:
            Response object of httpx library.
        """
        params = {"dvo": dataverse_id}
        payload = self._parse_payload(
            payload=role,
            model=collection.Role,
        )

        url = self._assemble_url("roles")
        return self.post_request(
            url,
            use_async=self.client is not None,
            auth=self.auth,
            response_model=collection.Role,
            params=params,
            data=payload.model_dump(by_alias=True),
        )

    def show_role(self, role_id: int) -> collection.Role:
        """Show role.

        `Docs <https://guides.dataverse.org/en/latest/api/native-api.html#show-role>`_

        HTTP Request:

        .. code-block:: bash

            GET http://$SERVER/api/roles/$id

        Args:
            identifier: Can be alias or id of a Dataverse.

        Returns:
            Response object of httpx library.
        """

        url = self._assemble_url(f"roles/{role_id}")
        return self.get_request(
            url,
            auth=self.auth,
            response_model=collection.Role,
            use_async=self.client is not None,
        )

    def delete_role(self, role_id: int) -> message.Message:
        """Delete role.

        `Docs <https://guides.dataverse.org/en/latest/api/native-api.html#delete-role>`_

        Args:
            role_id: Can be alias or id of a Role.

        Returns:
            Response object of httpx library.
        """
        url = self._assemble_url(f"roles/{role_id}")
        response = self.delete_request(
            url,
            auth=self.auth,
            use_async=self.client is not None,
            response_model=message.Message,
        )

        if response.message:
            self.logger.info(response.message)

        return response

    @overload
    def crawl_collection(
        self,
        alias: Annotated[
            Union[Literal[":root"], str, int],
            'The alias of the dataverse/collection to crawl. Can be a dataverse alias (e.g., "harvard").',
        ] = ":root",
        filter_by: Literal["collections"] = "collections",
        recursive: bool = True,
    ) -> Sequence[collection.content.Collection]: ...

    @overload
    def crawl_collection(
        self,
        alias: Annotated[
            Union[Literal[":root"], str, int],
            'The alias of the dataverse/collection to crawl. Can be a dataverse alias (e.g., "harvard").',
        ] = ":root",
        filter_by: Literal["datasets"] = "datasets",
        recursive: bool = True,
    ) -> Sequence[collection.content.Dataset]: ...

    @overload
    def crawl_collection(
        self,
        alias: Annotated[
            Union[Literal[":root"], str, int],
            'The alias of the dataverse/collection to crawl. Can be a dataverse alias (e.g., "harvard").',
        ] = ":root",
        filter_by: None = None,
        recursive: bool = True,
    ) -> Sequence[Union[collection.content.Collection, collection.content.Dataset]]: ...

    def crawl_collection(
        self,
        alias: Annotated[
            Union[Literal[":root"], str, int],
            'The alias of the dataverse/collection to crawl. Can be a dataverse alias (e.g., "harvard").',
        ] = ":root",
        filter_by: Optional[Literal["collections", "datasets"]] = None,
        recursive: bool = True,
    ) -> Sequence[Union[collection.content.Collection, collection.content.Dataset]]:
        """Crawl a collection and return all datasets and dataverses within it.

        This method provides a synchronous wrapper around the asynchronous
        crawl_collection function. It recursively traverses a Dataverse collection
        hierarchy and returns a flattened list of all child items. The method can
        optionally filter the results to return only specific types of children
        (collections or datasets).

        The method automatically sets up an async client internally to perform
        concurrent API calls when recursive traversal is enabled, improving
        performance when dealing with large collection hierarchies. The async
        client is properly cleaned up after the operation completes or if an
        error occurs.

        Note:
            This method runs the asynchronous crawling operation in a new event
            loop using asyncio.run(). If you're already in an async context,
            consider using the async crawl_collection function directly instead.

        Args:
            collection_id: The identifier (alias or numeric ID) of the
                dataverse/collection to crawl. Can be a dataverse alias
                (e.g., "harvard") or numeric ID. Supports the special value
                ":root" for the root dataverse.
            filter_by: Optional filter to specify which types of children
                to return. Defaults to None.

                - "collections": Returns only collection children (sub-dataverses)
                - "datasets": Returns only dataset children
                - None: Returns all children (both collections and datasets)

            recursive: If True (default), recursively crawls all sub-collections
                within the specified collection. If False, only returns immediate
                children of the specified collection.

        Returns:
            A sequence containing the requested child items. Each item is either a
            Collection object (for dataverses) or a Dataset object (for datasets).
            The list is flattened, meaning all items from all hierarchy levels
            are returned in a single sequence when recursive=True.

        Raises:
            Exception: Any exception that occurs during the crawling operation
                is re-raised after properly cleaning up the async client. This
                could include network errors, authentication errors, or API
                response parsing errors.

        Examples:
            Get all children from a collection::

                >>> api = NativeApi(base_url="https://demo.dataverse.org")
                >>> all_children = api.crawl_collection("harvard")
                >>> print(f"Found {len(all_children)} items")

            Get only datasets from a collection::

                >>> datasets = api.crawl_collection(
                ...     "harvard", filter_by="datasets"
                ... )
                >>> for dataset in datasets:
                ...     print(dataset.title)

            Get only sub-dataverses from a collection::

                >>> collections = api.crawl_collection(
                ...     "harvard", filter_by="collections"
                ... )
                >>> for collection in collections:
                ...     print(collection.alias)

            Non-recursive crawl (immediate children only)::

                >>> immediate_children = api.crawl_collection(
                ...     "harvard", recursive=False
                ... )
                >>> print(f"Found {len(immediate_children)} immediate children")

            Crawl with numeric collection ID::

                >>> children = api.crawl_collection("42", filter_by="datasets")

        See Also:
            - :func:`pyDataverse.api.crawler.crawl_collection`: The underlying
              async function that performs the actual crawling operation.
            - :meth:`get_dataverse_contents`: For getting immediate contents
              of a single dataverse without recursion.
        """
        try:
            collection_url = self._assemble_url(f"dataverses/{alias}")
            self.logger.info(
                f"Crawling collection [link={collection_url}]{alias}[/link] filtering by [green]{filter_by}[/green]"
            )

            self._setup_async_client()
            response = asyncio.run(crawl_collection(self, alias, filter_by, recursive))

            self.client = None
            self.logger.info(
                f"Crawled collection [link={collection_url}]{alias}[/link] filtered by [green]{filter_by}[/green]"
            )
            return response
        except Exception as e:
            self.client = None
            raise e

    @deprecation.deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use crawl_collection instead.",
    )
    def get_children(self, **_):
        """Get children of a collection.

        This method is deprecated. Use crawl_collection instead.
        """
        raise DeprecationWarning(
            "This method is deprecated. Use crawl_collection instead."
        )

    def get_user(self) -> User:
        """Get details of the current authenticated user.

        Auth must be ``true`` for this to work. API endpoint is available for Dataverse >= 5.3.

        https://guides.dataverse.org/en/latest/api/native-api.html#get-user-information-in-json-format
        """
        url = self._assemble_url("users/:me")
        return self.get_request(
            url,
            auth=True,
            use_async=self.client is not None,
            response_model=User,
        )

    def redetect_file_type(
        self,
        identifier: Union[str, int],
        dry_run: bool = False,
    ) -> file.RedetectedFileType:
        """Redetect file type.

        https://guides.dataverse.org/en/latest/api/native-api.html#redetect-file-type

        Args:
            identifier: Datafile id (fileid) or file PID.
            is_pid: Is the identifier a PID, by default False.
            dry_run: [description], by default False

        Returns:
            Request Response() object.
        """
        params: dict[str, Union[str, bool, int]] = {
            "dryRun": dry_run,
        }

        if self._is_pid(identifier):
            url = self._assemble_url("files/:persistentId/redetect")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"files/{identifier}/redetect")

        return self.post_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=file.RedetectedFileType,
        )

    def reingest_datafile(
        self,
        identifier: Union[str, int],
    ) -> message.Message:
        """Reingest datafile.

        https://guides.dataverse.org/en/latest/api/native-api.html#reingest-a-file

        Args:
            identifier: Datafile id (fileid) or file PID.
            is_pid: Is the identifier a PID, by default False.

        Returns:
            Request Response() object.
        """
        params: dict[str, Union[str, bool, int]] = {}

        if self._is_pid(identifier):
            url = self._assemble_url("files/:persistentId/reingest")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"files/{identifier}/reingest")

        response = self.post_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=message.Message,
        )

        if response.message:
            self.logger.info(response.message)

        return response

    def uningest_datafile(
        self,
        identifier: Union[str, int],
    ) -> message.Message:
        """Uningest datafile.

        https://guides.dataverse.org/en/latest/api/native-api.html#uningest-a-file

        Args:
            identifier: Datafile id (fileid) or file PID.
            is_pid: Is the identifier a PID, by default False.

        Returns:
            Request Response() object.
        """
        params = {}
        if self._is_pid(identifier):
            url = self._assemble_url("files/:persistentId/uningest")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"files/{identifier}/uningest")

        response = self.post_request(
            url,
            auth=self.auth,
            params=params,
            use_async=self.client is not None,
            response_model=message.Message,
        )

        if response.message:
            self.logger.info(response.message)

        return response

    def restrict_datafile(
        self,
        identifier: Union[str, int],
        restrict: bool,
        enable_access_request: Optional[bool] = None,
        terms_of_access: Optional[str] = None,
    ) -> message.Message:
        """Restrict or unrestrict a datafile.

        https://guides.dataverse.org/en/latest/api/native-api.html#restrict-files

        Args:
            identifier: Datafile id (fileid) or file PID.
            is_pid: Is the identifier a PID, by default False.

        Returns:
            Request Response() object.
        """

        if restrict and enable_access_request is False:
            assert terms_of_access is not None, (
                "terms_of_access is required when restrict is True and enable_access_request is False"
            )

        params = {}

        if self._is_pid(identifier):
            url = self._assemble_url("files/:persistentId/restrict")
            params["persistentId"] = identifier
        else:
            url = self._assemble_url(f"files/{identifier}/restrict")

        payload = file.RestrictFileBody(
            restrict=restrict,
            enable_access_request=enable_access_request,
            terms_of_access=terms_of_access,
        )

        response = self.put_request(
            url,
            auth=self.auth,
            params=params,
            data=payload.model_dump(by_alias=True, exclude_none=True),
            response_model=message.Message,
            use_async=self.client is not None,
        )

        if response.message:
            self.logger.info(response.message)

        return response

    def get_available_licenses(self) -> List[info.License]:
        """Get available licenses.

        https://guides.dataverse.org/en/latest/api/native-api.html#get-available-licenses

        Returns:
            List of available licenses.
        """
        url = self._assemble_url("licenses")
        return self.get_request(
            url,
            auth=self.auth,
            use_async=self.client is not None,
            response_model=List[info.License],
        )

    def get_license(self, license_id: int | str) -> info.License:
        """Get license.

        https://guides.dataverse.org/en/latest/api/native-api.html#get-a-license

        Returns:
            List of available licenses.
        """

        if isinstance(license_id, str):
            licenses = self.get_available_licenses()
            try:
                return next(
                    license
                    for license in licenses
                    if license.name == license_id
                    or license.rights_identifier == license_id
                )
            except StopIteration:
                self.logger.error(f"License with id {license_id} not found")
                raise ValueError(f"License with id {license_id} not found")

        url = self._assemble_url(f"licenses/{license_id}")
        return self.get_request(
            url,
            auth=self.auth,
            use_async=self.client is not None,
            response_model=info.License,
        )
