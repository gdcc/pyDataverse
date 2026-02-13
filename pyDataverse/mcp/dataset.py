from typing import (
    Annotated,
    Optional,
    Sequence,
    Union,
    cast,
)

import pandas as pd
from fastmcp import Context
from fastmcp.dependencies import CurrentContext
from toon_format import encode
from typing_extensions import TypedDict

from .utils import ensure_dataverse


class FileMeta(TypedDict):
    """
    Metadata information for a file in a dataset.

    Attributes:
        path: The file path within the dataset
        description: Optional description of the file
        mime_type: The MIME type of the file
        restricted: Whether the file has access restrictions
    """

    path: str
    description: Optional[str]
    mime_type: Optional[str]
    restricted: Optional[bool]


def get_dataset(
    identifier: Annotated[
        Union[str, int],
        "The identifier of the dataset, which can be a persistent identifier or a dataverse identifier (int).",
    ],
    full: Annotated[
        bool,
        "Whether to return the full dataset metadata and files. This function is token-heavy, so you should only use it if you need to access the full dataset metadata and files.",
    ],
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse from the context.",
    ],
    ctx: Context = CurrentContext(),
):
    """
    Retrieve dataset information from Dataverse.

    This function fetches dataset metadata from a Dataverse instance. It can return
    either a summary view with basic information or a full view with complete metadata
    including all metadata blocks.

    Args:
        identifier: The dataset identifier (persistent ID like DOI or numeric ID)
        full: If True, returns complete metadata; if False, returns summary info
        metadatablocks: Specific metadata blocks to include (only when full=True)
        ctx: The MCP context containing the Dataverse connection

    Returns:
        Encoded dataset metadata as a string

    Raises:
        RuntimeError: If no Dataverse connection is available in context
    """
    dataverse = ensure_dataverse(ctx, base_url=base_url)
    dataset = dataverse.fetch_dataset(identifier=identifier)

    if full:
        dataset.metadata_blocks = {
            name: metadata_block
            for name, metadata_block in dataset.metadata_blocks.items()
            if not metadata_block.is_empty
        }

        serialized = dataset.model_dump()
    else:
        serialized = dataset.model_dump(
            include={
                "identifier",
                "persistent_identifier",
                "version",
                "title",
                "description",
                "authors",
                "subjects",
                "url",
            }
        )

        # We supply the available metadata blocks to the client so they can re-fetch
        # the dataset with the metadata blocks they want to see
        serialized["available_metadatablocks"] = ", ".join(
            [
                name
                for name, metadata_block in dataset.metadata_blocks.items()
                if not metadata_block.is_empty
            ]
        )

    return encode(serialized)


def list_files(
    identifier: Annotated[
        Union[str, int],
        "The identifier of the dataset, which can be a persistent identifier or a dataverse identifier (int).",
    ],
    only_tabular: Annotated[
        bool,
        "Whether to return only tabular files. If True, the function will return only tabular files. If False, the function will return all files.",
    ],
    filter_mime_types: Annotated[
        Optional[Sequence[str]],
        "The MIME types to filter the files by. If not specified, the function will return all files.",
    ],
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse from the context.",
    ],
    ctx: Context = CurrentContext(),
):
    """
    List all files in a dataset with optional MIME type filtering.

    This function retrieves information about all files in a dataset, including
    their paths, descriptions, MIME types, and access restrictions. Files can
    be filtered by MIME type if desired.

    Args:
        identifier: The dataset identifier (persistent ID like DOI or numeric ID)
        filter_mime_types: Optional list of MIME types to filter by
        ctx: The MCP context containing the Dataverse connection

    Returns:
        Encoded list of file metadata as a string

    Raises:
        RuntimeError: If no Dataverse connection is available in context
    """
    dataverse = ensure_dataverse(ctx, base_url=base_url)
    dataset = dataverse.fetch_dataset(identifier=identifier)

    df = dataset.files.df
    if only_tabular:
        df = cast(pd.DataFrame, df[df["is_tabular"]])

    if filter_mime_types:
        df = cast(
            pd.DataFrame,
            df[df["mime_type"].isin(filter_mime_types)],
        )

    return encode(df.to_dict(orient="records"))
