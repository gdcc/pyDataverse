"""Metadata block handling and Pydantic model generation."""

from functools import lru_cache
from typing import Annotated, Any, Dict, List, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, Field, create_model
from pydantic.functional_validators import AfterValidator

from ...models import metadatablocks
from .config import BlockConfig
from .metadata import CompoundField, JSONSchemaExtra, MetadataBlockBase
from .utils import clean_name, map_field_type
from .validated_list import ValidatingList

T = TypeVar("T", bound=BaseModel)


def create_model_from_block(
    name: str,
    block: Dict[str, metadatablocks.MetadataField],
    base: Type[T] = MetadataBlockBase,
    enum_limit: Optional[int] = None,
) -> Type[T]:
    """
    Create a Pydantic model from a metadata block.

    Args:
        name: Name for the model class
        block: Dictionary of metadata fields
        base: Base class for the model (default: MetadataBlockBase)

    Returns:
        Dynamically created Pydantic model class
    """
    compounds, primitives, cv_fields = split_fields(block)
    attrs = {}

    # Add primitive fields
    for primitive in primitives:
        attr = field_to_pydantic_attr(primitive)
        if attr is not None:
            attrs[clean_name(primitive.name)] = attr

    # Add compound fields
    for compound in compounds:
        result = compound_field_to_pydantic_attr(compound)
        if result is not None:
            field_name, field_attr = result
            attrs[field_name] = field_attr

    # Add controlled vocabulary fields
    for cv_field in cv_fields:
        if (
            enum_limit is not None
            and cv_field.controlled_vocabulary_values is not None
            and len(cv_field.controlled_vocabulary_values) > enum_limit
        ):
            continue
        result = cv_field_to_pydantic_attr(cv_field)
        if result is not None:
            field_name, field_attr = result
            attrs[clean_name(field_name)] = field_attr

    # Create block configuration
    config = BlockConfig(
        block_name=name,
        compound_fields=[compound.name for compound in compounds],
        primitive_fields=[primitive.name for primitive in primitives],
        cv_fields=[cv_field.name for cv_field in cv_fields],
    )

    # Create and return the model
    return create_model(
        name,
        __base__=base,
        __cls_kwargs__={"block_config": config},
        **attrs,
    )


def split_fields(
    block: Dict[str, metadatablocks.MetadataField],
) -> Tuple[
    List[metadatablocks.MetadataField],
    List[metadatablocks.MetadataField],
    List[metadatablocks.MetadataField],
]:
    """
    Split metadata fields by type class.

    Args:
        block: Dictionary of metadata fields

    Returns:
        Tuple of (compound_fields, primitive_fields, controlled_vocabulary_fields)
    """
    compound_fields = [
        field for field in block.values() if field.type_class == "compound"
    ]
    primitive_fields = [
        field for field in block.values() if field.type_class == "primitive"
    ]
    controlled_vocabulary_fields = [
        field for field in block.values() if field.type_class == "controlledVocabulary"
    ]
    return compound_fields, primitive_fields, controlled_vocabulary_fields


def field_to_pydantic_attr(
    field: metadatablocks.MetadataField,
) -> Optional[Tuple[Type, Any]]:
    """
    Convert a metadata field to a Pydantic field attribute.

    Args:
        field: The metadata field to convert

    Returns:
        Tuple of (type, Field) for use in create_model, or None if field cannot be mapped
    """
    dtype = map_field_type(field.type)
    if dtype is None:
        return None

    params = {
        "description": field.description,
        "alias": field.name,
        "title": field.title,
        "json_schema_extra": JSONSchemaExtra.from_field(field).model_dump(
            by_alias=True
        ),
    }

    if field.multiple:
        dtype = List[dtype]
        params["default_factory"] = list
    else:
        dtype = Optional[dtype]
        params["default"] = None

    return (dtype, Field(**params))


def compound_field_to_pydantic_attr(
    field: metadatablocks.MetadataField,
) -> Optional[Tuple[str, Tuple[Any, Any]]]:
    """
    Convert a compound metadata field to a Pydantic field attribute.

    Creates a ValidatingList for multiple fields, which supports the .add() method
    for type-safe item creation using keyword arguments.

    Args:
        field: The compound metadata field to convert

    Returns:
        Tuple of (field_name, (type, Field)) for use in create_model, or None if field cannot be mapped

    Note:
        For multiple compound fields (lists), the resulting ValidatingList supports both:
        - Dictionary style: `field += [{"authorName": "John", "authorAffiliation": "MIT"}]`
        - Method style: `field.add(authorName="John", authorAffiliation="MIT")`
        - Snake case: `field.add(author_name="John", author_affiliation="MIT")`
    """
    if field.child_fields is None:
        return None

    comp_type = create_model_from_block(
        field.name,
        field.child_fields,
        base=CompoundField,
    )

    if field.multiple:
        field_type = ValidatingList[comp_type]
        factory = lambda: ValidatingList[comp_type]()  # noqa: E731
    else:
        field_type = comp_type
        factory = lambda: comp_type()  # noqa: E731

    field_attr = (
        field_type,
        Field(
            description=field.description,
            alias=field.name,
            default_factory=factory,
            json_schema_extra=JSONSchemaExtra.from_field(field).model_dump(
                by_alias=True
            ),
        ),
    )

    return (clean_name(field.name), field_attr)


def cv_field_to_pydantic_attr(
    field: metadatablocks.MetadataField,
) -> Optional[Tuple[str, Tuple[Any, Any]]]:
    """
    Convert a controlled vocabulary field to a Pydantic field attribute.

    Notes on implementation:
        We intentionally avoid generating `Enum` classes for controlled vocabulary
        values. Profiling showed Enum creation to be a major bottleneck when
        building many metadata blocks.

        Instead, we validate against the allowed values using a cached
        `AfterValidator` and keep JSON Schema output useful by injecting an
        `"enum": [...]` list into `json_schema_extra`.

    Args:
        field: The controlled vocabulary field to convert

    Returns:
        Tuple of (field_name, (type, Field)) for use in create_model, or None if field cannot be mapped
    """
    values = field.controlled_vocabulary_values
    if not values:
        return None

    cv_type = _cv_type_from_values(tuple(values), multiple=field.multiple)
    if cv_type is None:
        return None

    params = {
        "description": field.description,
        "alias": field.name,
        "json_schema_extra": (
            JSONSchemaExtra.from_field(field).model_dump(by_alias=True)
            | {"enum": list(values)}
        ),
    }

    if field.multiple:
        params["default_factory"] = list
    else:
        cv_type = Optional[cv_type]
        params["default"] = None

    return (field.name, (cv_type, Field(**params)))


@lru_cache(maxsize=4096)
def _cv_type_from_values(values: Tuple[str, ...], *, multiple: bool) -> Any:
    """
    Build a Pydantic-compatible type for controlled vocabulary validation.

    This returns an `Annotated[...]` type with an `AfterValidator` which checks
    the provided value(s) against the allowed vocabulary.

    Why not `Enum` or `Literal`?
        - `Enum` creation is expensive and dominated build time in profiling.
        - `Literal[...]` would be ideal, but Python 3.9 compatibility is tricky
          because `typing.Literal` is not reliably subscriptable via
          `Literal.__getitem__` across environments.

    Args:
        values: Allowed controlled vocabulary values.
        multiple: Whether the field is a list field.

    Returns:
        An `Annotated[str, AfterValidator(...)]` (or list variant) suitable for
        use in Pydantic model field annotations.
    """
    allowed = frozenset(values)

    if multiple:

        def _validate_list(v: List[str]) -> List[str]:
            return [item for item in v if item in allowed]

        return Annotated[List[str], AfterValidator(_validate_list)]

    def _validate_scalar(v: str) -> str:
        if v not in allowed:
            raise ValueError("Invalid controlled vocabulary value")
        return v

    return Annotated[str, AfterValidator(_validate_scalar)]
