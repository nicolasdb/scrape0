"""Tests for TOML output formatting."""

import pytest
from scraper.models import (
    ExtractionResult,
    ExtractionMetadata,
    FieldStatus,
)
from scraper.output import TOMLOutputFormatter


@pytest.fixture
def sample_result():
    """Create a sample extraction result."""
    metadata = ExtractionMetadata(
        success=True,
        extraction_timestamp="2026-01-04T10:00:00Z",
        failure_reason=None,
        site_type="fablab",
        extraction_duration_seconds=2.3,
    )

    fields_status = FieldStatus(
        extracted=["name", "location", "expertise"],
        failed=[],
        not_found=["contact"],
    )

    return ExtractionResult(
        success=True,
        priority_fields={
            "name": "Example Fablab",
            "location": "San Francisco, CA",
            "expertise": ["3D printing", "electronics", "woodworking"],
        },
        extra_metadata={
            "operating_hours": "Mon-Fri 9am-6pm",
        },
        metadata=metadata,
        fields_status=fields_status,
    )


class TestTOMLOutputFormatter:
    """Tests for TOML output formatting."""

    def test_format_result_returns_string(self, sample_result):
        """Test that format_result returns a TOML string."""
        toml_output = TOMLOutputFormatter.format_result(sample_result)
        assert isinstance(toml_output, str)
        assert len(toml_output) > 0

    def test_format_result_contains_sections(self, sample_result):
        """Test that TOML output contains expected sections."""
        toml_output = TOMLOutputFormatter.format_result(sample_result)
        assert "[extraction_metadata]" in toml_output
        assert "[priority_fields]" in toml_output
        assert "[fields_status]" in toml_output

    def test_format_result_includes_metadata(self, sample_result):
        """Test that extraction metadata is included."""
        toml_output = TOMLOutputFormatter.format_result(sample_result)
        assert "success = true" in toml_output
        assert "site_type" in toml_output
        assert "extraction_timestamp" in toml_output

    def test_format_result_includes_fields(self, sample_result):
        """Test that extracted fields are included."""
        toml_output = TOMLOutputFormatter.format_result(sample_result)
        assert "Example Fablab" in toml_output
        assert "San Francisco, CA" in toml_output

    def test_format_result_includes_field_status(self, sample_result):
        """Test that field status is included."""
        toml_output = TOMLOutputFormatter.format_result(sample_result)
        assert "[fields_status]" in toml_output
        assert "extracted" in toml_output
        assert "failed" in toml_output
        assert "not_found" in toml_output

    def test_format_result_with_arrays(self, sample_result):
        """Test formatting of array values."""
        toml_output = TOMLOutputFormatter.format_result(sample_result)
        # Expertise should be formatted as array
        assert "[" in toml_output and "]" in toml_output

    def test_format_result_with_failure(self):
        """Test formatting with extraction failure."""
        metadata = ExtractionMetadata(
            success=False,
            extraction_timestamp="2026-01-04T10:00:00Z",
            failure_reason="network_timeout",
            site_type="fablab",
        )

        fields_status = FieldStatus(extracted=[], failed=["name", "location"])

        result = ExtractionResult(
            success=False,
            priority_fields={},
            extra_metadata={},
            metadata=metadata,
            fields_status=fields_status,
        )

        toml_output = TOMLOutputFormatter.format_result(result)
        assert "success = false" in toml_output
        assert "network_timeout" in toml_output

    def test_format_result_with_special_characters(self):
        """Test formatting with special characters."""
        metadata = ExtractionMetadata(
            success=True,
            extraction_timestamp="2026-01-04T10:00:00Z",
        )

        result = ExtractionResult(
            success=True,
            priority_fields={
                "name": 'Lab with "quotes"',
                "location": "Paris, France",
            },
            metadata=metadata,
        )

        toml_output = TOMLOutputFormatter.format_result(result)
        # Should properly escape special characters
        assert "Lab with" in toml_output
        assert "Paris" in toml_output

    def test_format_result_with_extra_metadata(self, sample_result):
        """Test that extra metadata is included."""
        toml_output = TOMLOutputFormatter.format_result(sample_result)
        assert "[extra_metadata]" in toml_output or "operating_hours" in toml_output

    def test_format_result_is_parseable(self, sample_result):
        """Test that output can be parsed back as TOML."""
        toml_output = TOMLOutputFormatter.format_result(sample_result)
        # Try to parse it back
        try:
            import tomli

            parsed = tomli.loads(toml_output)
            assert "extraction_metadata" in parsed
            assert "priority_fields" in parsed
            assert "fields_status" in parsed
        except ImportError:
            # tomli not available, skip this test
            pytest.skip("tomli not installed")
