import inspect
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Union,
    get_args,
    get_origin,
)

from cachetools import TTLCache
from fastmcp import Context

from ..dataverse import Dataverse


def ensure_dataverse(
    ctx: Context,
    base_url: Optional[str] = None,
) -> Dataverse:
    """Get a Dataverse instance from the MCP context.

    Args:
        ctx: The MCP context containing application state
        dataverse_name: Optional name of specific dataverse (for multi-dataverse setups)

    Returns:
        The configured Dataverse instance

    Raises:
        RuntimeError: If no Dataverse instance is found or invalid configuration
    """

    if base_url is None:
        dataverse = ctx.get_state("dataverse")
        if isinstance(dataverse, Dataverse):
            return dataverse
        raise RuntimeError("Dataverse is not set in the context.")

    dataverses: TTLCache[str, Dataverse] = ctx.get_state("dataverses")
    base_url = base_url.rstrip("/")

    if base_url in dataverses:
        return dataverses[base_url]

    try:
        dataverse = Dataverse(base_url=base_url, verbose=0)
        dataverses[base_url] = dataverse
        return dataverse
    except Exception as e:
        raise RuntimeError(
            f"Failed to create Dataverse instance for base URL: {base_url}"
        ) from e


def mutate_signature(
    fun: Callable,
    **kwargs,
) -> Callable:
    """Modify the type annotations of a function's parameters or remove parameters.

    This utility function allows runtime modification of function signatures,
    specifically changing the type annotations of parameters or removing them
    entirely. This is useful for dynamically adapting function signatures in MCP tools.

    Args:
        fun: The function whose signature should be modified
        **kwargs: Mapping of parameter names to new type annotations or None.
                  - If a value is None, the parameter is removed from the signature.
                  - If a value is a type annotation, the parameter's annotation is updated.
                  - If the function has **kwargs in its signature, any kwargs not in the
                    signature will be added as new parameters, and the **kwargs parameter
                    itself will be removed from the signature.

    Returns:
        The same function with modified signature annotations

    Example:
        >>> def example_func(x: int, y: str, z: bool, **kwargs) -> None:
        ...     pass
        >>> modified_func = mutate_signature(example_func, x=float, z=None, new_param=str)
        >>> # Now x has annotation 'float', z is removed, new_param is added,
        >>> # and **kwargs is removed from the signature
    """
    signature = inspect.signature(fun)
    existing_param_names = set(signature.parameters.keys())
    has_var_keyword = _has_var_keyword(signature)

    # Create new parameters from kwargs (only if function has **kwargs)
    params_to_add = []
    if has_var_keyword:
        params_to_add = _create_new_parameters(kwargs, existing_param_names)

    # Build modified parameter list
    new_params = _build_modified_parameters(signature, kwargs, params_to_add)

    # Update function signature
    fun.__signature__ = signature.replace(parameters=new_params)

    # Update function annotations to match
    _update_function_annotations(
        fun, signature, kwargs, existing_param_names, has_var_keyword
    )

    return fun


def _is_optional(annotation) -> bool:
    """Check if a type annotation is Optional (Union with None).

    Args:
        annotation: The type annotation to check

    Returns:
        True if the annotation is Optional, False otherwise
    """
    origin = get_origin(annotation)
    if origin is not Union:
        return False
    args = get_args(annotation)
    return type(None) in args


def _has_var_keyword(signature: inspect.Signature) -> bool:
    """Check if a function signature has **kwargs (VAR_KEYWORD parameter).

    Args:
        signature: The function signature to check

    Returns:
        True if the signature contains **kwargs, False otherwise
    """
    return any(
        param.kind == inspect.Parameter.VAR_KEYWORD
        for param in signature.parameters.values()
    )


def _find_var_keyword_name(signature: inspect.Signature) -> Optional[str]:
    """Find the name of the VAR_KEYWORD parameter (**kwargs) if it exists.

    Args:
        signature: The function signature to search

    Returns:
        The name of the **kwargs parameter, or None if not found
    """
    for name, param in signature.parameters.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return name
    return None


def _create_new_parameters(
    kwargs: Dict[str, Optional[type]],
    existing_param_names: set,
) -> List[inspect.Parameter]:
    """Create new Parameter objects for parameters not in the existing signature.

    Args:
        kwargs: Mapping of parameter names to type annotations
        existing_param_names: Set of existing parameter names

    Returns:
        List of new Parameter objects to add to the signature
    """
    new_params = []
    for name, annotation in kwargs.items():
        if name not in existing_param_names:
            default = None if _is_optional(annotation) else inspect.Parameter.empty
            new_params.append(
                inspect.Parameter(
                    name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation=annotation,
                    default=default,
                )
            )
    return new_params


def _build_modified_parameters(
    signature: inspect.Signature,
    kwargs: Dict[str, Optional[type]],
    params_to_add: List[inspect.Parameter],
) -> List[inspect.Parameter]:
    """Build a new parameter list with modifications applied.

    Args:
        signature: The original function signature
        kwargs: Mapping of parameter names to new annotations (None to remove)
        params_to_add: New parameters to insert where **kwargs was

    Returns:
        List of modified Parameter objects
    """
    new_params = []
    params_added = False

    for name, param in signature.parameters.items():
        # Replace **kwargs with explicit parameters
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            new_params.extend(params_to_add)
            params_added = True
            continue

        # Handle parameter modifications
        if name in kwargs:
            replacement = kwargs[name]
            if replacement is None:
                # Remove this parameter
                continue
            # Update annotation
            param = param.replace(annotation=replacement)

        new_params.append(param)

    # Safety check: add params if VAR_KEYWORD wasn't found (shouldn't happen)
    if params_to_add and not params_added:
        new_params.extend(params_to_add)

    return new_params


def _update_function_annotations(
    func: Callable,
    signature: inspect.Signature,
    kwargs: Dict[str, Optional[type]],
    existing_param_names: set,
    has_var_keyword: bool,
) -> None:
    """Update the function's __annotations__ dict to match the new signature.

    Args:
        func: The function to update
        signature: The original function signature
        kwargs: Mapping of parameter names to new annotations
        existing_param_names: Set of existing parameter names
        has_var_keyword: Whether the original signature had **kwargs
    """
    annotations = getattr(func, "__annotations__", {}).copy()

    # Remove annotations for parameters being removed
    for name, replacement in kwargs.items():
        if replacement is None:
            annotations.pop(name, None)
        elif name in existing_param_names:
            annotations[name] = replacement

    # Add annotations for new parameters (from **kwargs expansion)
    if has_var_keyword:
        for name, annotation in kwargs.items():
            if name not in existing_param_names:
                annotations[name] = annotation

    # Remove **kwargs parameter from annotations if it existed
    var_keyword_name = _find_var_keyword_name(signature)
    if var_keyword_name:
        annotations.pop(var_keyword_name, None)

    func.__annotations__ = annotations
