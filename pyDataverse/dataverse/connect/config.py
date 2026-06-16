"""Configuration and metaclass for Dataverse dataset models."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, Field
from pydantic._internal._model_construction import ModelMetaclass


class BlockConfig(BaseModel):
    """
    Configuration for a metadata block class.

    Stores metadata about field types and block structure for use in
    model generation and serialization.
    """

    block_name: str
    compound_fields: List[str] = Field(default_factory=list)
    primitive_fields: List[str] = Field(default_factory=list)
    cv_fields: List[str] = Field(default_factory=list)


class DataverseMetaclass(ModelMetaclass):
    """
    Metaclass that tracks block configuration for dynamically created models.

    Attaches block configuration metadata to classes during creation,
    enabling runtime access to field type information and block structure.
    """

    def __new__(
        mcs,
        name: str,
        bases: Tuple[Type, ...],
        namespace: Dict[str, Any],
        block_config: Optional[BlockConfig] = None,
        **kwargs,
    ):
        """
        Create a new class with optional block configuration.

        Args:
            name: The name of the class being created.
            bases: Base classes for the new class.
            namespace: The namespace dictionary containing class attributes.
            block_config: Optional block configuration to attach to the class.
            **kwargs: Additional keyword arguments passed to parent metaclass.

        Returns:
            The newly created class with block config attached if provided.
        """
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if block_config is not None:
            cls._block_config = block_config
        return cls

