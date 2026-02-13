from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Sequence

from pyDataverse.models import dataset

if TYPE_CHECKING:
    from pyDataverse.api.native import NativeApi


async def conc_get_datasets(
    api: NativeApi,
    identifiers: Sequence[str | int],
    batch_size: int = 50,
    max_concurrent: int = 10,
) -> Sequence[dataset.GetDatasetResponse]:
    """Fetch datasets from the API with optimized concurrency control.

    This function implements efficient batched fetching with the following optimizations:
    - Semaphore-based concurrency limiting to prevent overwhelming the server
    - Batched processing to manage memory usage for large identifier lists
    - Error handling that allows partial results even if some requests fail
    - Connection pooling through the async HTTP client for connection reuse

    Args:
        api: The API instance with an initialized async client.
        identifiers: The identifiers of the datasets to fetch. Can be persistent IDs
            (DOI/Handle) or numeric database IDs.
        batch_size: Number of datasets to fetch per batch. Controls memory usage by
            processing identifiers in chunks. Default is 50.
        max_concurrent: Maximum number of concurrent requests allowed at any time.
            This prevents overwhelming the server or hitting rate limits. Default is 10.

    Returns:
        A sequence of GetDatasetResponse objects, one for each identifier. If a request
        fails, None will be returned in that position.

    Example:
        >>> api = NativeApi(base_url="https://demo.dataverse.org", api_token="token")
        >>> api._setup_async_client()
        >>> identifiers = ["doi:10.5072/FK2/ABC123", "doi:10.5072/FK2/DEF456"]
        >>> results = await _fetch_datasets(api, identifiers, batch_size=100, max_concurrent=20)
    """
    # Create a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(
        identifier: str | int,
    ) -> dataset.GetDatasetResponse | None:
        """Fetch a single dataset with semaphore-controlled concurrency.

        This wrapper function ensures that only max_concurrent requests are active
        at any given time, preventing server overload and respecting rate limits.

        Args:
            identifier: Dataset identifier to fetch.

        Returns:
            GetDatasetResponse if successful, None if an error occurs.
        """
        async with semaphore:
            try:
                return await api.get_dataset(identifier)  # type: ignore
            except Exception as e:
                # Log the error but don't fail the entire batch
                print(f"Error fetching dataset {identifier}: {e}")
                return None

    # Process identifiers in batches to manage memory for large lists
    results = []
    for i in range(0, len(identifiers), batch_size):
        batch = identifiers[i : i + batch_size]

        # Create tasks for the current batch
        tasks = [fetch_with_semaphore(identifier) for identifier in batch]

        # Execute batch with controlled concurrency
        # gather() will respect the semaphore, so max_concurrent requests run at once
        batch_results = await asyncio.gather(*tasks, return_exceptions=False)
        results.extend(batch_results)

    return results
