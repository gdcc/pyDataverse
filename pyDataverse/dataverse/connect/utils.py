"""Utility functions for dataset metadata processing."""

import keyword
import re
from typing import Any, Optional, Type


def clean_name(name: str) -> str:
    """
    Convert a string into a valid Python identifier for use as an attribute/enum name.

    Handles:
    - Replaces spaces, dots, and all special characters (except underscores) with underscores
    - Spells out leading digits (0-9)
    - Removes consecutive underscores
    - Ensures the result is not empty and doesn't conflict with keywords
    - Raises ValueError for empty or invalid names

    Args:
        name: The input string to clean

    Returns:
        A valid Python identifier in snake_case (lowercase)

    Raises:
        ValueError: If name is empty, whitespace-only, or contains only invalid characters

    Examples:
        >>> clean_name("Hello World")
        'hello_world'
        >>> clean_name("123 Test")
        'one_two_three_test'
        >>> clean_name("My-Field!")
        'my_field'
        >>> clean_name("9Lives")
        'nine_lives'
        >>> clean_name("file.name")
        'file_name'
    """
    digit_words = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
    }

    if not name:
        raise ValueError("Name cannot be empty")

    cleaned = str(name).strip()
    if not cleaned:
        raise ValueError("Name cannot be empty or whitespace-only")

    # Replace all non-alphanumeric characters (including dots, spaces, etc.) except underscores with underscores
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", cleaned)

    # Handle leading digits by spelling them out
    leading_digits = []
    i = 0
    while i < len(cleaned) and cleaned[i].isdigit():
        leading_digits.append(digit_words[cleaned[i]])
        i += 1

    if leading_digits:
        cleaned = "_".join(leading_digits) + (
            "_" + cleaned[i:] if i < len(cleaned) else ""
        )

    # Remove consecutive underscores and leading/trailing underscores
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")

    if not cleaned:
        raise ValueError(
            f"Name '{name}' contains only invalid characters and cannot be converted to a valid identifier"
        )

    # Handle Python keywords
    if keyword.iskeyword(cleaned):
        cleaned = cleaned + "_"

    return cleaned


def map_field_type(field_type: str) -> Optional[Type[Any]]:
    """
    Map a Dataverse field type to a Python type.

    Args:
        field_type: The Dataverse field type string

    Returns:
        The corresponding Python type, or None if no mapping exists
    """
    if field_type in {"TEXT", "TEXTBOX", "STRING", "DATE", "EMAIL", "URL"}:
        return str
    elif field_type == "FLOAT":
        return float
    elif field_type == "INT":
        return int
    elif field_type == "NONE":
        return None

    return None
