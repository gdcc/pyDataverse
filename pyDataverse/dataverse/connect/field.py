"""Field metadata classes for Dataverse dataset models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Type, Union

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

from ...models import metadatablocks

# Type aliases for Pydantic field names
TypeClass = Literal["primitive", "compound", "controlledVocabulary"]


class JSONSchemaExtra(BaseModel):
    """
    Extra metadata for JSON schema generation.

    Stores type information and metadata about field structure for use in
    schema generation and field processing.
    """

    model_config: ConfigDict = ConfigDict(
        populate_by_name=True,
    )

    type_class: TypeClass = Field(alias="typeClass")
    multiple: bool = Field(alias="multiple")
    type_name: str = Field(alias="typeName")

    @classmethod
    def from_field(cls, field: metadatablocks.MetadataField) -> Self:
        """
        Create JSONSchemaExtra from a MetadataField.

        Args:
            field: The MetadataField to extract information from.

        Returns:
            A JSONSchemaExtra instance populated with field metadata.
        """
        return cls(
            typeClass=field.type_class,
            multiple=field.multiple,
            typeName=field.name,
        )


@dataclass
class FieldInfo:
    """
    Information about a field's type and structure.

    Contains metadata extracted from Pydantic model field definitions,
    including type information, parent class relationships, and schema metadata.
    """

    json_schema_extra: JSONSchemaExtra
    dtype: Type
    parent_class: Union[Type[BaseModel], Type, None]
    multiple: bool
