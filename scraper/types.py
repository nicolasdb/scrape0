"""Type conversion utilities for extracted data."""

import re
from typing import Any, Union


class TypeConverter:
    """Convert extracted string values to TOML-compatible types."""

    @staticmethod
    def convert_to_bool(value: str) -> Union[bool, str]:
        """
        Convert string to boolean if possible.

        Recognizes: "yes", "no", "true", "false", "1", "0" (case-insensitive).
        Returns original string if not a recognized boolean value.
        """
        if not isinstance(value, str):
            return value

        normalized = value.strip().lower()
        if normalized in ("yes", "true", "1"):
            return True
        elif normalized in ("no", "false", "0"):
            return False
        return value

    @staticmethod
    def convert_to_number(value: str) -> Union[int, float, str]:
        """
        Convert string to number if possible.

        Attempts int conversion first, then float.
        Returns original string if not numeric.
        """
        if not isinstance(value, str):
            return value

        value = value.strip()
        if not value:
            return value

        try:
            # Try integer first
            if "." not in value:
                return int(value)
            else:
                return float(value)
        except ValueError:
            return value

    @staticmethod
    def convert_to_list(value: str, separators: list = None) -> Union[list, str]:
        """
        Convert comma or semicolon-separated string to list.

        Default separators: comma, semicolon, pipe.
        Returns list of stripped strings if multiple values found.
        Returns original string if only one value or no separator matches.
        """
        if not isinstance(value, str):
            return value

        if separators is None:
            separators = [",", ";", "|"]

        value = value.strip()
        if not value:
            return value

        for sep in separators:
            if sep in value:
                parts = [part.strip() for part in value.split(sep)]
                # Only return as list if multiple non-empty parts
                non_empty = [p for p in parts if p]
                if len(non_empty) > 1:
                    return non_empty
                elif len(non_empty) == 1:
                    return non_empty[0]

        return value

    @staticmethod
    def convert_to_string(value: str) -> str:
        """Clean and return value as string."""
        if not isinstance(value, str):
            return str(value) if value is not None else ""
        return value.strip()

    @staticmethod
    def infer_and_convert(value: str) -> Any:
        """
        Attempt to infer type and convert value.

        Tries conversions in order: boolean, number, list, string.
        """
        if not isinstance(value, str) or not value.strip():
            return value

        # Try boolean
        bool_result = TypeConverter.convert_to_bool(value)
        if isinstance(bool_result, bool):
            return bool_result

        # Try number
        num_result = TypeConverter.convert_to_number(value)
        if not isinstance(num_result, str):
            return num_result

        # Try list
        list_result = TypeConverter.convert_to_list(value)
        if isinstance(list_result, list):
            return list_result

        # Return as string
        return TypeConverter.convert_to_string(value)
