from typing import Annotated, Optional

from fastmcp import Context
from fastmcp.dependencies import CurrentContext
from toon_format import encode

from .utils import ensure_dataverse


def get_metrics(
    base_url: Annotated[
        Optional[str],
        "The base URL of the dataverse to use. If not specified, the function will use the dataverse from the context.",
    ] = None,
    ctx: Context = CurrentContext(),
):
    """
    Retrieve metrics from Dataverse.

    Args:
        ctx: The MCP context containing the Dataverse connection

    Returns:
        Encoded metrics as a string
    """
    dataverse = ensure_dataverse(ctx, base_url=base_url)
    return encode(dataverse.metrics.dict())
