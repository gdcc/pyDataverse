from typing import Any, Generic, Iterable, TypeVar

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

T = TypeVar("T")


class ValidatingList(list, Generic[T]):
    """
    A list subclass that validates and coerces items to a specific type.

    This class extends the built-in list to provide automatic validation
    and type coercion for all items added to the list. It integrates with
    Pydantic's validation system and supports both Pydantic models and
    plain Python types.

    Attributes:
        __item_type__: The type that all items in the list must conform to.
    """

    __item_type__: type

    def __class_getitem__(cls, item_type):
        """
        Create a specialized ValidatingList class for a specific item type.

        This method is called when using bracket notation like ValidatingList[Item].
        It creates a new class with the item type bound to __item_type__.

        Args:
            item_type: The type that items in this list should conform to.

        Returns:
            A new ValidatingList class specialized for the given item type.
        """
        return type(
            f"ValidatingList[{getattr(item_type, '__name__', str(item_type))}]",
            (cls,),
            {"__item_type__": item_type},
        )

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler: GetCoreSchemaHandler):
        """
        Generate Pydantic core schema for validation.

        This method integrates the ValidatingList with Pydantic's validation
        system, ensuring that field assignments are properly validated.

        Args:
            source: The source type being validated.
            handler: Pydantic's core schema handler.

        Returns:
            A Pydantic core schema for validating this list type.
        """
        item_schema = handler.generate_schema(getattr(cls, "__item_type__", Any))
        base = core_schema.list_schema(item_schema)

        def to_self(value):
            """Convert validated value to ValidatingList instance."""
            return cls(value)

        return core_schema.no_info_after_validator_function(to_self, base)

    def __init__(self, iterable: Iterable[Any] = ()):
        """
        Initialize a ValidatingList with optional initial items.

        All items in the iterable will be validated and coerced to the
        appropriate type during initialization.

        Args:
            iterable: An iterable of items to initialize the list with.
        """
        super().__init__()
        for v in iterable:
            self.append(v)

    def _coerce(self, v):
        """
        Coerce a value to the list's item type.

        This method handles type coercion for different scenarios:
        - If the value is already the correct type, return as-is
        - If the target type is a Pydantic model, use model_validate
        - Otherwise, use the type constructor as a fallback

        Args:
            v: The value to coerce.

        Returns:
            The coerced value of the correct type.
        """
        t = self.__item_type__
        if isinstance(v, t):
            return v
        if hasattr(t, "model_validate"):  # Pydantic model
            return t.model_validate(v)
        return t(v)  # fallback for plain types

    def append(self, v):
        """
        Append a validated item to the end of the list.

        Args:
            v: The item to append, which will be validated and coerced.
        """
        super().append(self._coerce(v))

    def insert(self, i, v):
        """
        Insert a validated item at the specified index.

        Args:
            i: The index at which to insert the item.
            v: The item to insert, which will be validated and coerced.
        """
        super().insert(i, self._coerce(v))

    def extend(self, it):
        """
        Extend the list with validated items from an iterable.

        Args:
            it: An iterable of items to add, each will be validated and coerced.
        """
        super().extend(self._coerce(x) for x in it)

    def __setitem__(self, i, v):
        """
        Set item(s) at the specified index or slice with validation.

        Args:
            i: The index or slice to set.
            v: The value(s) to set, which will be validated and coerced.
        """
        if isinstance(i, slice):
            v = [self._coerce(x) for x in v]
        else:
            v = self._coerce(v)
        super().__setitem__(i, v)

    def __iadd__(self, other):
        """
        Implement in-place addition (+=) with validation.

        Args:
            other: An iterable of items to add to this list.

        Returns:
            This list instance after extending with validated items.
        """
        self.extend(other)
        return self

    def add(self, **kwargs) -> T:
        """
        Add a new item to the list using keyword arguments.

        This method provides a more discoverable and type-safe way to add items,
        especially for compound fields. Instead of passing a dictionary, you can
        use keyword arguments that match the field names.

        Args:
            **kwargs: Field names and values for the new item. These will be
                validated against the item type's schema.

        Returns:
            The newly created and appended item.

        Raises:
            ValidationError: If the provided kwargs don't match the item schema.

        Example:
            >>> # Instead of: author_list += [{"authorName": "John", "authorAffiliation": "MIT"}]
            >>> author_list.add(authorName="John", authorAffiliation="MIT")
            >>> # or using pythonic names (with underscores):
            >>> author_list.add(author_name="John", author_affiliation="MIT")
        """
        # Convert snake_case kwargs to camelCase if needed
        converted_kwargs = self._convert_kwargs(kwargs)
        item = self._coerce(converted_kwargs)
        self.append(item)
        return item

    def _convert_kwargs(self, kwargs: dict) -> dict:
        """
        Convert snake_case kwargs to match field names (which may be camelCase).

        This allows users to use Pythonic naming (author_name) while the actual
        field might be named "authorName". If a Pydantic model has aliases defined,
        those will be respected during validation.

        Args:
            kwargs: Dictionary of keyword arguments, potentially with snake_case keys.

        Returns:
            Dictionary with keys potentially converted to match field aliases.
        """
        # For Pydantic models, we can rely on populate_by_name and aliases
        # Just return kwargs as-is since Pydantic handles the conversion
        return kwargs
