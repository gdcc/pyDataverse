"""Metadata block base classes for Dataverse dataset models."""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Type,
    Union,
    cast,
    get_args,
    get_origin,
)

import rich
from pydantic import (
    BaseModel,
    ConfigDict,
    model_serializer,
)
from typing_extensions import Self

from ...models.dataset import create, edit_get
from .config import BlockConfig, DataverseMetaclass
from .field import FieldInfo, JSONSchemaExtra
from .validated_list import ValidatingList


class MetadataBlockBase(
    BaseModel,
    metaclass=DataverseMetaclass,
):
    """Base class for all metadata block models."""

    model_config: ConfigDict = ConfigDict(
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_assignment=True,
        populate_by_name=True,
    )

    @model_serializer
    def _serialize_model(self) -> Dict[str, Any]:
        """
        Custom serializer for metadata blocks.

        Ensures that all fields are properly serialized including nested CompoundFields
        and ValidatingList instances. Empty fields are excluded from the output.
        """
        result = {}
        for field_name, field_value in self:
            if not self._is_value_empty(field_value):
                result[field_name] = self._serialize_value(field_value)
        return result

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """
        Recursively serialize a field value, excluding None values.

        Args:
            value: The value to serialize

        Returns:
            The serialized value with None values excluded
        """
        # Check for CompoundField by class name to avoid forward reference issues
        # CompoundField is defined later in this same module
        if (
            isinstance(value, BaseModel)
            and hasattr(value, "__class__")
            and value.__class__.__name__ == "CompoundField"
        ):
            return {
                k: MetadataBlockBase._serialize_value(v)
                for k, v in value
                if v is not None
            }
        elif isinstance(value, (list, ValidatingList)):
            return [MetadataBlockBase._serialize_value(item) for item in value]
        elif isinstance(value, BaseModel):
            return value.model_dump(exclude_none=True)
        else:
            return value

    @property
    def block_config(cls) -> Optional[BlockConfig]:
        """
        Get the block configuration for this class.

        Returns:
            The BlockConfig instance if available, None otherwise.
        """
        return getattr(cls, "_block_config", None)

    @property
    def is_empty(self) -> bool:
        """
        Check if the metadata block is empty.
        """
        for _, value in self:
            if not self._is_value_empty(value):
                return False
        return True

    def __repr__(self) -> str:
        """
        Return a string representation of the instance.

        Uses rich printing for formatted output and returns an empty string
        to maintain compatibility with standard repr expectations.
        """
        rich.print(self)
        return ""

    def __getitem__(self, key: str) -> Any:
        """
        Get a field value by name using dictionary-like access.

        Args:
            key: The name of the field to retrieve.

        Returns:
            The value of the field, which may be a primitive type, CompoundField,
            or a list of these types. Due to the dynamic nature of metadata blocks,
            the exact type depends on the schema and cannot be statically determined.
        """
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a field value by name using dictionary-like access.

        Args:
            key: The name of the field to set.
            value: The value to assign to the field.
        """
        setattr(self, key, value)

    def to_metadata_block(self) -> create.MetadataBlock:
        """
        Convert this metadata block instance to a MetadataBlock object.

        Returns:
            A MetadataBlock containing all non-empty fields from this instance.

        Raises:
            ValueError: If block configuration is not found.
        """
        if self.block_config is None:
            raise ValueError("Block config not found")

        display_name = self.block_config.block_name
        block = create.MetadataBlock(display_name=display_name, fields=[])

        for name, value in self:
            if self._is_value_empty(value):
                continue

            field_info = self._extract_info(name)
            processed_value = self._process_field_value(value, field_info)
            field = self._create_metadata_field(field_info, processed_value)
            block.fields.append(field)

        return block

    def to_update_metadata_block(self) -> List[edit_get.MetadataField]:
        if self.block_config is None:
            raise ValueError("Block config not found")

        fields = []

        for name, value in self:
            print(name, value)
            if self._is_value_empty(value):
                continue
            field_info = self._extract_info(name)
            processed_value = self._process_field_value(value, field_info)
            field = cast(
                edit_get.MetadataField,
                self._create_metadata_field(field_info, processed_value),
            )
            fields.append(field)
        return fields

    @staticmethod
    def _is_multiple_type(dtype: Any) -> bool:
        """
        Check if a type represents a multiple/collection type.

        Args:
            dtype: The type to check.

        Returns:
            True if the type is a list or ValidatingList, False otherwise.
        """
        # Check for standard list type
        if get_origin(dtype) is list:
            return True
        # Check for ValidatingList subclass
        if isinstance(dtype, type) and issubclass(dtype, ValidatingList):
            return True
        return False

    @staticmethod
    def _extract_inner_type(dtype: Any) -> Any:
        """
        Extract the inner type from a collection type.

        Args:
            dtype: The collection type (list or ValidatingList).

        Returns:
            The inner type of the collection.
        """
        # For standard list types
        if get_origin(dtype) is list:
            return get_args(dtype)[0]
        # For ValidatingList subclasses
        if isinstance(dtype, type) and issubclass(dtype, ValidatingList):
            if hasattr(dtype, "__item_type__"):
                return dtype.__item_type__
        return dtype

    @staticmethod
    def _unwrap_optional(dtype: Any) -> Any:
        """
        Unwrap an Optional type to get the actual type.

        Args:
            dtype: The type that might be Optional (Union with None).

        Returns:
            The unwrapped type, or the original type if not Optional.
        """
        if get_origin(dtype) is Union:
            return next(
                (arg for arg in get_args(dtype) if arg is not type(None)), dtype
            )
        return dtype

    @classmethod
    def _extract_info(cls, name: str) -> FieldInfo:
        """
        Extract field information from model field definition.

        Args:
            name: The name of the field to extract information for.

        Returns:
            FieldInfo containing type information, parent class, and metadata.
        """
        field_info = cls.model_fields[name]
        dtype = field_info.annotation

        # Check if field is multiple and extract inner type
        multiple = cls._is_multiple_type(dtype)
        if multiple:
            dtype = cls._extract_inner_type(dtype)

        # Unwrap Optional types
        dtype = cls._unwrap_optional(dtype)

        return FieldInfo(
            dtype=dtype,  # type: ignore
            parent_class=cls._get_parent_class(dtype),
            multiple=multiple,
            json_schema_extra=JSONSchemaExtra.model_validate(
                field_info.json_schema_extra
            ),
        )

    def _process_field_value(
        self,
        value: Any,
        field_info: FieldInfo,
    ) -> Union[
        Any, Dict[str, create.MetadataField], List[Dict[str, create.MetadataField]]
    ]:
        """
        Process a field value, converting CompoundField instances to their metadata representation.

        Args:
            value: The raw field value to process.
            field_info: Information about the field type and structure.

        Returns:
            The processed value, with CompoundField instances converted to dictionaries.
        """
        # Check by class name since CompoundField is defined later in this module

        if issubclass(field_info.dtype, CompoundField):
            if field_info.multiple and isinstance(value, list):
                return [field.to_metadata_fields() for field in value]
            return value.to_metadata_fields()

        return value

    def _create_metadata_field(
        self, field_info: FieldInfo, value: Any
    ) -> create.MetadataField:
        """
        Create a MetadataField object from field information and processed value.

        Args:
            field_info: Information about the field type and structure.
            value: The processed field value.

        Returns:
            A MetadataField instance configured with the field information.
        """

        return create.MetadataField(
            type_class=field_info.json_schema_extra.type_class,
            type_name=field_info.json_schema_extra.type_name,
            multiple=field_info.json_schema_extra.multiple,
            value=value,
        )

    @staticmethod
    def _get_parent_class(dtype) -> Union[Type[BaseModel], Type, None]:
        """
        Get the parent class of a given type.

        Args:
            dtype: The type to inspect for parent classes.

        Returns:
            The first parent class if available, None otherwise.
        """
        if hasattr(dtype, "__bases__"):
            return dtype.__bases__[0]

        return None

    @staticmethod
    def _is_value_empty(value: Any) -> bool:
        """
        Check if a value is considered empty.

        Handles CompoundField instances, lists, and None values with comprehensive
        empty state checking.

        Args:
            value: The value to check for emptiness.

        Returns:
            True if the value is empty, False otherwise.
        """
        if value is None:
            return True

        # Check for CompoundField by class name (defined later in this module)
        if isinstance(value, BaseModel) and hasattr(value, "__class__"):
            # Safe access to is_empty attribute (CompoundField has this method)
            return getattr(value, "is_empty", False)

        if isinstance(value, list):
            if len(value) == 0:
                return True
            # Check if all items in list are empty (handles nested CompoundFields)
            return all(
                isinstance(item, BaseModel)
                and hasattr(item, "__class__")
                and item.__class__.__name__ == "CompoundField"
                and getattr(item, "is_empty", False)
                for item in value
            )

        return False

    @classmethod
    def from_dataverse_dict(
        cls,
        block: Union[edit_get.MetadataBlock, create.MetadataBlock],
    ) -> Self:
        """
        Create a new instance from a dictionary of data.
        """
        data = {}

        for field in block.fields:
            assert field.type_name is not None, "Field type name is required"
            field_info = cls._extract_info(field.type_name)
            data[field.type_name] = cls._process_field(field, field_info)

        return cls(**data)

    @classmethod
    def _process_field(cls, field, field_info):
        """Process a single field based on its type class."""
        if field.type_class == "primitive":
            return field.value

        if field.type_class == "compound":
            return cls._process_compound_field(field, field_info)

        if field.type_class == "controlledVocabulary":
            return field.value

        raise ValueError(f"Invalid field type: {field.type_class}")

    @classmethod
    def _process_compound_field(cls, field, field_info):
        """Process a compound field value."""
        # Get CompoundField from module globals (defined later in this module)
        CompoundField = globals().get("CompoundField")
        if CompoundField is None:
            # Fallback: import if not yet defined (shouldn't happen)
            import sys

            module = sys.modules[__name__]
            CompoundField = getattr(module, "CompoundField", None)

        if CompoundField is not None and isinstance(field.value, dict):
            return CompoundField.from_dataverse_dict(field.value)

        if isinstance(field.value, list):
            return [
                field_info.dtype.from_dataverse_dict(item)
                for item in field.value
                if isinstance(item, dict)
            ]

        raise ValueError(f"Invalid compound field value type: {type(field.value)}")


class CompoundField(
    MetadataBlockBase,
    metaclass=DataverseMetaclass,
):
    """Base class for compound fields in metadata blocks."""

    model_config: ConfigDict = ConfigDict(
        populate_by_name=True,
    )

    @model_serializer
    def _serialize_model(self) -> Dict[str, Any]:
        """
        Custom serializer for compound fields.

        Ensures that all nested fields are properly serialized.
        Empty fields are excluded from the output.
        """
        result = {}
        for field_name, field_value in self:
            if not self._is_value_empty(field_value):
                result[field_name] = self._serialize_value(field_value)
        return result

    @property
    def is_empty(self) -> bool:
        """
        Check if all fields in the compound field are empty.

        Recursively checks nested CompoundField instances and lists to determine
        if the entire compound field structure contains no meaningful data.

        Returns:
            True if all fields are empty or None, False otherwise.
        """
        for value in self.model_dump().values():
            if value is None:
                continue

            if isinstance(value, (list, ValidatingList)) and len(value) == 0:
                continue

            if isinstance(value, CompoundField) and value.is_empty:
                continue

            if isinstance(value, (list, ValidatingList)) and all(
                isinstance(v, CompoundField) and v.is_empty for v in value
            ):
                continue

            return False

        return True

    def __getitem__(self, key: str) -> Any:
        """
        Get a field value by name using dictionary-like access.

        Args:
            key: The name of the field to retrieve.

        Returns:
            The value of the field, which may be a primitive type or CompoundField.
            Due to the dynamic nature of metadata blocks, the exact type depends on
            the schema and cannot be statically determined.
        """
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a field value by name using dictionary-like access.

        Args:
            key: The name of the field to set.
            value: The value to assign to the field.
        """
        setattr(self, key, value)

    def to_metadata_fields(
        self,
    ) -> Dict[
        str,
        Union[
            create.MetadataField,
            Dict[str, create.MetadataField],
            List[Dict[str, create.MetadataField]],
        ],
    ]:
        """
        Convert this compound field instance to a dictionary of metadata fields.

        Returns:
            A dictionary mapping field names to their MetadataField representations
            or nested dictionaries for compound fields.
        """
        fields = {}
        for name, value in self:
            if self._is_value_empty(value):
                continue

            field_info = self._extract_info(name)
            processed_value = self._process_field_value(value, field_info)

            if field_info.parent_class is CompoundField:
                fields[name] = processed_value
            else:
                field = self._create_metadata_field(field_info, processed_value)
                fields[name] = field

        return fields

    @classmethod
    def from_dataverse_dict(
        cls,
        compound_field: Mapping[
            str,
            Union[edit_get.MetadataField, create.MetadataField],
        ],
    ) -> Self:
        """
        Create a new instance from a dictionary of data.
        """
        data = {}
        for name, field in compound_field.items():
            data[name] = field.value

        return cls(**data)
