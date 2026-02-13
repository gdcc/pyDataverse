"""Content base class for Dataverse dataset models."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

from pydantic import BaseModel, Field

from ..api.data_access import DataAccessApi
from ..api.native import NativeApi
from ..api.semantic import SemanticApi

if TYPE_CHECKING:
    from .dataverse import Dataverse


class ContentBase(BaseModel):
    """
    Abstract base class for Dataverse content objects.

    This class serves as the foundational base for all high-level content objects in the Dataverse API,
    such as datasets, collections (dataverses), and files. Provides common attributes, links back
    to the parent Dataverse instance, and exposes convenient accessors for the underlying API clients.

    Subclasses should implement their own `update_metadata` method.
    """

    verbose: int = Field(
        default=1,
        description="Verbosity level for content instance logging/messages. 1=normal, 0=quiet.",
        exclude=True,
        repr=False,
    )

    dataverse: "Dataverse" = Field(
        ...,
        description="Reference to the Dataverse instance this content object belongs to.",
        exclude=True,
        repr=False,
    )

    @abstractmethod
    def update_metadata(self, **kwargs):
        """
        Abstract method to update the metadata for this content object.

        Subclasses should implement this method to support updating or patching their
        own metadata, and raise an appropriate error if this operation is not allowed.

        Args:
            **kwargs: Arbitrary keyword arguments required for metadata updating.

        Raises:
            NotImplementedError: If called on the base class or an unimplemented subclass.
        """
        raise NotImplementedError(
            f"update_metadata is not implemented for {self.__class__.__name__}"
        )

    @property
    def native_api(self) -> NativeApi:
        """
        The native API client associated with this content's Dataverse instance.

        Returns:
            NativeApi: An instance of the NativeApi for making native API requests.
        """
        self._ensure_dataverse()
        return self.dataverse.native_api

    @property
    def data_access_api(self) -> DataAccessApi:
        """
        The Data Access API client associated with this content's Dataverse instance.

        Returns:
            DataAccessApi: An instance of the DataAccessApi.
        """
        self._ensure_dataverse()
        return self.dataverse.data_access_api

    @property
    def semantic_api(self) -> SemanticApi:
        """
        The Semantic API client for the content's Dataverse instance.

        Returns:
            SemanticApi: An instance of the SemanticApi.
        """
        self._ensure_dataverse()
        return self.dataverse.semantic_api

    def dict(self) -> Dict[str, Any]:
        """
        Generate a dictionary representation of this content object,
        omitting attributes with value None.

        Returns:
            Dict[str, Any]: The model as a dictionary.
        """
        return self.model_dump(exclude_none=True)

    def json(self, indent: Optional[int] = 4) -> str:
        """
        Return a JSON string representation of this content object.

        Args:
            indent (Optional[int]): The indentation level for pretty-printing. Defaults to 4.

        Returns:
            str: The model as a JSON-formatted string.
        """
        return self.model_dump_json(exclude_none=True, indent=indent)

    def _ensure_dataverse(self) -> None:
        """
        Ensure that the parent Dataverse instance is set.

        Raises:
            ValueError: If `dataverse` is not set on this content object.
        """
        if self.dataverse is None:
            raise ValueError(
                f"Dataverse is not set. Please derive {self.__class__.__name__} from a Dataverse instance."
            )
