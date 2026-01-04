"""Tests for type conversion utilities."""

import pytest
from scraper.types import TypeConverter


class TestTypeConverter:
    """Tests for TypeConverter class."""

    def test_convert_to_bool_yes_no(self):
        """Test boolean conversion recognizes yes/no."""
        assert TypeConverter.convert_to_bool("yes") is True
        assert TypeConverter.convert_to_bool("no") is False
        assert TypeConverter.convert_to_bool("YES") is True
        assert TypeConverter.convert_to_bool("NO") is False

    def test_convert_to_bool_true_false(self):
        """Test boolean conversion recognizes true/false."""
        assert TypeConverter.convert_to_bool("true") is True
        assert TypeConverter.convert_to_bool("false") is False
        assert TypeConverter.convert_to_bool("TRUE") is True
        assert TypeConverter.convert_to_bool("FALSE") is False

    def test_convert_to_bool_numeric(self):
        """Test boolean conversion recognizes 1/0."""
        assert TypeConverter.convert_to_bool("1") is True
        assert TypeConverter.convert_to_bool("0") is False

    def test_convert_to_bool_invalid_returns_string(self):
        """Test non-boolean strings returned unchanged."""
        assert TypeConverter.convert_to_bool("maybe") == "maybe"
        assert TypeConverter.convert_to_bool("123") == "123"

    def test_convert_to_number_integer(self):
        """Test number conversion recognizes integers."""
        assert TypeConverter.convert_to_number("123") == 123
        assert TypeConverter.convert_to_number("-45") == -45
        assert isinstance(TypeConverter.convert_to_number("0"), int)

    def test_convert_to_number_float(self):
        """Test number conversion recognizes floats."""
        assert TypeConverter.convert_to_number("3.14") == 3.14
        assert TypeConverter.convert_to_number("-2.5") == -2.5
        assert isinstance(TypeConverter.convert_to_number("1.0"), float)

    def test_convert_to_number_invalid_returns_string(self):
        """Test non-numeric strings returned unchanged."""
        assert TypeConverter.convert_to_number("not-a-number") == "not-a-number"
        assert TypeConverter.convert_to_number("12.34.56") == "12.34.56"

    def test_convert_to_list_comma_separated(self):
        """Test list conversion with comma separators."""
        result = TypeConverter.convert_to_list("item1, item2, item3")
        assert result == ["item1", "item2", "item3"]

    def test_convert_to_list_semicolon_separated(self):
        """Test list conversion with semicolon separators."""
        result = TypeConverter.convert_to_list("skill1; skill2; skill3")
        assert result == ["skill1", "skill2", "skill3"]

    def test_convert_to_list_single_item(self):
        """Test list with single item returns string."""
        result = TypeConverter.convert_to_list("single")
        assert result == "single"
        assert not isinstance(result, list)

    def test_convert_to_list_strips_whitespace(self):
        """Test list conversion strips whitespace."""
        result = TypeConverter.convert_to_list("  item1  ,  item2  ")
        assert result == ["item1", "item2"]

    def test_convert_to_string(self):
        """Test string conversion."""
        assert TypeConverter.convert_to_string("  hello  ") == "hello"
        assert TypeConverter.convert_to_string("test") == "test"

    def test_infer_and_convert_boolean(self):
        """Test type inference converts booleans."""
        assert TypeConverter.infer_and_convert("true") is True
        assert TypeConverter.infer_and_convert("no") is False

    def test_infer_and_convert_number(self):
        """Test type inference converts numbers."""
        assert TypeConverter.infer_and_convert("42") == 42
        assert TypeConverter.infer_and_convert("3.14") == 3.14

    def test_infer_and_convert_list(self):
        """Test type inference converts lists."""
        result = TypeConverter.infer_and_convert("a, b, c")
        assert result == ["a", "b", "c"]

    def test_infer_and_convert_string(self):
        """Test type inference returns strings when no match."""
        assert TypeConverter.infer_and_convert("just a string") == "just a string"
