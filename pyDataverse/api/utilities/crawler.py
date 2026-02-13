from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Literal, Optional, Sequence, Union

from pyDataverse.models import collection

if TYPE_CHECKING:
    from pyDataverse.api.native import NativeApi


async def crawl_collection(
    native_api: NativeApi,
    alias: Union[Literal[":root"], str, int],
    filter_by: Optional[Literal["collections", "datasets"]] = None,
    recursive: bool = True,
) -> Sequence[Union[collection.content.Collection, collection.content.Dataset]]:
    """Crawl a collection and return all datasets and dataverses within it.

    This function recursively traverses a Dataverse collection hierarchy and
    returns a flattened list of all child items. It can optionally filter the
    results to return only specific types of children (collections or datasets).

    The function performs asynchronous crawling, making concurrent API calls
    when recursive traversal is enabled to improve performance when dealing
    with large collection hierarchies.

    Args:
        native_api: An instance of NativeApi used to make API calls to the
            Dataverse instance.
        alias: The alias of the dataverse/collection
        filter_by: Optional filter to specify which types of children to return.
            - "collections": Returns only collection children (sub-dataverses)
            - "datasets": Returns only dataset children
            - None: Returns all children (both collections and datasets)
        recursive: If True, recursively crawls all sub-collections within the
            specified collection. If False, only returns immediate children.

    Returns:
        A sequence containing the requested child items. Each item is either a
        Collection object (for dataverses) or a Dataset object (for datasets).
        The list is flattened, meaning all items from all hierarchy levels
        are returned in a single sequence.

    Examples:
        Get all children from a collection::

            >>> api = NativeApi(base_url="https://demo.dataverse.org")
            >>> all_children = await crawl_collection(api, "harvard")
            >>> print(f"Found {len(all_children)} items")

        Get only datasets from a collection::

            >>> datasets = await crawl_collection(
            ...     api, "harvard", filter_by="datasets"
            ... )
            >>> for dataset in datasets:
            ...     print(dataset.title)

        Get only sub-dataverses from a collection::

            >>> collections = await crawl_collection(
            ...     api, "harvard", filter_by="collections"
            ... )
            >>> for collection in collections:
            ...     print(collection.alias)

        Non-recursive crawl (immediate children only)::

            >>> immediate_children = await crawl_collection(
            ...     api, "harvard", recursive=False
            ... )
    """

    parent_content = await native_api.get_collection_contents(alias)  # type: ignore
    flattened_contents = []
    recursive_tasks = []

    # Process each content item and collect recursive tasks if needed
    for content in parent_content:
        flattened_contents.append(content)

        if isinstance(content, collection.content.Collection) and recursive:
            coll_alias = (await native_api.get_collection(str(content.id))).alias  # type: ignore
            task = crawl_collection(
                native_api=native_api,
                alias=coll_alias,
                recursive=recursive,
                filter_by=filter_by,
            )
            recursive_tasks.append(task)

    # Execute recursive tasks and merge results
    if recursive_tasks:
        results = await asyncio.gather(*recursive_tasks)
        for result in results:
            flattened_contents.extend(result)

    # Filter results based on children_types
    type_filters = {
        "collections": collection.content.Collection,
        "datasets": collection.content.Dataset,
    }

    if filter_by in type_filters:
        return [
            content
            for content in flattened_contents
            if isinstance(content, type_filters[filter_by])
        ]
    else:
        return flattened_contents
