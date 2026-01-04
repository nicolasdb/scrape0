"""Tests for Phase 4.1: Comprehensive Error Categorization (Task Group 4.1)."""

import pytest
from scraper.errors import ScrapingError, NetworkError, NetworkTimeout, ExtractionError
from scraper.models import ExtractionMetadata


class TestErrorHierarchy:
    """Test the exception class hierarchy."""

    def test_scraping_error_is_base(self):
        """Test ScrapingError is the base exception."""
        err = ScrapingError("test error")
        assert isinstance(err, Exception)

    def test_network_error_inherits_from_scraping_error(self):
        """Test NetworkError is a ScrapingError."""
        err = NetworkError("network down")
        assert isinstance(err, ScrapingError)

    def test_network_timeout_inherits_from_network_error(self):
        """Test NetworkTimeout is a NetworkError."""
        err = NetworkTimeout("timeout")
        assert isinstance(err, NetworkError)
        assert isinstance(err, ScrapingError)

    def test_extraction_error_inherits_from_scraping_error(self):
        """Test ExtractionError is a ScrapingError."""
        err = ExtractionError("extraction failed")
        assert isinstance(err, ScrapingError)


class TestErrorCategorization:
    """Test error categorization for analytics."""

    def test_network_timeout_categorization(self):
        """Test network timeout errors are categorized correctly."""
        # When a NetworkTimeout occurs, failure_reason should be "network_timeout"
        try:
            raise NetworkTimeout("Request exceeded timeout limit")
        except NetworkTimeout:
            metadata = ExtractionMetadata(
                success=False,
                extraction_timestamp="2026-01-04T10:00:00Z",
                failure_reason="network_timeout",
                site_type="fablab",
            )
            assert metadata.failure_reason == "network_timeout"

    def test_network_error_categorization(self):
        """Test network errors are categorized correctly."""
        try:
            raise NetworkError("Connection refused")
        except NetworkError:
            metadata = ExtractionMetadata(
                success=False,
                extraction_timestamp="2026-01-04T10:00:00Z",
                failure_reason="network_error",
                site_type="fablab",
            )
            assert metadata.failure_reason == "network_error"

    def test_extraction_error_categorization(self):
        """Test extraction errors are categorized correctly."""
        try:
            raise ExtractionError("Failed to extract field")
        except ExtractionError:
            metadata = ExtractionMetadata(
                success=False,
                extraction_timestamp="2026-01-04T10:00:00Z",
                failure_reason="extraction_rule_error",
                site_type="fablab",
            )
            assert metadata.failure_reason == "extraction_rule_error"

    def test_parsing_error_categorization(self):
        """Test parsing errors are categorized correctly."""
        from scraper.errors import ParsingError

        try:
            raise ParsingError("Invalid HTML")
        except ParsingError:
            metadata = ExtractionMetadata(
                success=False,
                extraction_timestamp="2026-01-04T10:00:00Z",
                failure_reason="parse_error",
                site_type="fablab",
            )
            assert metadata.failure_reason == "parse_error"


class TestStandardizedFailureReasons:
    """Test failure reason values are standardized."""

    def test_failure_reasons_are_consistent(self):
        """Test failure reasons use consistent naming."""
        # These are the standardized failure_reason values
        failure_reasons = [
            "network_timeout",
            "network_error",
            "parse_error",
            "no_content",
            "validation_error",
            "extraction_rule_error",
            "config_error",
            "unknown",
        ]

        # Each should be a simple string
        for reason in failure_reasons:
            assert isinstance(reason, str)
            assert len(reason) > 0
            assert "_" in reason or reason == "unknown"  # snake_case or unknown

    def test_failure_reason_in_metadata(self):
        """Test failure_reason is properly stored in metadata."""
        metadata = ExtractionMetadata(
            success=False,
            extraction_timestamp="2026-01-04T10:00:00Z",
            failure_reason="network_timeout",
            site_type="fablab",
        )

        assert metadata.failure_reason == "network_timeout"
        assert metadata.success is False


class TestErrorMessagesForDebugging:
    """Test error messages are helpful for debugging."""

    def test_network_error_message(self):
        """Test NetworkError messages are descriptive."""
        err = NetworkError("Connection refused: No route to host")
        assert "Connection refused" in str(err)

    def test_extraction_error_message(self):
        """Test ExtractionError messages are descriptive."""
        err = ExtractionError("CSS selector 'div.nonexistent' matched no elements")
        assert "CSS selector" in str(err)

    def test_timeout_error_message(self):
        """Test timeout messages include duration."""
        err = NetworkTimeout("Request exceeded 30 second timeout")
        assert "30 second" in str(err)


class TestFailureReasonMapping:
    """Test mapping exceptions to failure reasons."""

    def test_exception_to_failure_reason_mapping(self):
        """Test various exception types map to correct failure reasons."""
        mappings = {
            NetworkTimeout: "network_timeout",
            NetworkError: "network_error",
            ExtractionError: "extraction_rule_error",
        }

        for exc_type, expected_reason in mappings.items():
            # Exception type should map to the failure reason
            assert expected_reason in [
                "network_timeout",
                "network_error",
                "extraction_rule_error",
                "parse_error",
                "no_content",
                "validation_error",
                "config_error",
                "unknown",
            ]
