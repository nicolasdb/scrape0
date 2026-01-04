"""Tests for data models."""

import pytest
from datetime import datetime
from scraper.models import (
    SiteConfig,
    ScraperConfig,
    ExtractionMetadata,
    FieldStatus,
    ExtractionResult,
)


class TestSiteConfig:
    """Tests for SiteConfig model."""

    def test_site_config_creation_with_required_fields(self):
        """Test SiteConfig creation with required fields."""
        config = SiteConfig(
            id="test-site",
            url_pattern="example.com",
            site_type="fablab",
            priority_fields={"name": "h1.title", "location": "span.addr"},
        )
        assert config.id == "test-site"
        assert config.url_pattern == "example.com"
        assert config.site_type == "fablab"
        assert "name" in config.priority_fields

    def test_site_config_with_defaults(self):
        """Test SiteConfig uses correct defaults."""
        config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={},
        )
        assert config.timeout_seconds == 30
        assert config.max_retries == 3
        assert config.extra_fields == {}

    def test_site_config_validation_empty_id(self):
        """Test SiteConfig rejects empty id."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            SiteConfig(id="", url_pattern="test.com", site_type="fab", priority_fields={})

    def test_site_config_validation_invalid_timeout(self):
        """Test SiteConfig rejects invalid timeout."""
        with pytest.raises(ValueError, match="timeout_seconds must be at least 1"):
            SiteConfig(
                id="test",
                url_pattern="test.com",
                site_type="fab",
                priority_fields={},
                timeout_seconds=0,
            )


class TestExtractionMetadata:
    """Tests for ExtractionMetadata model."""

    def test_extraction_metadata_creation(self):
        """Test ExtractionMetadata creation."""
        metadata = ExtractionMetadata(
            success=True,
            extraction_timestamp="2026-01-04T10:00:00Z",
            site_type="fablab",
        )
        assert metadata.success is True
        assert metadata.site_type == "fablab"
        assert "2026-01-04" in metadata.extraction_timestamp

    def test_extraction_metadata_now(self):
        """Test ExtractionMetadata.now() creates with current timestamp."""
        metadata = ExtractionMetadata.now(success=True, site_type="fablab")
        assert metadata.success is True
        assert metadata.site_type == "fablab"
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(metadata.extraction_timestamp)

    def test_extraction_metadata_failure_reason(self):
        """Test ExtractionMetadata tracks failure reasons."""
        metadata = ExtractionMetadata(
            success=False,
            extraction_timestamp="2026-01-04T10:00:00Z",
            failure_reason="network_timeout",
            site_type="fablab",
        )
        assert metadata.failure_reason == "network_timeout"


class TestFieldStatus:
    """Tests for FieldStatus model."""

    def test_field_status_creation(self):
        """Test FieldStatus creation."""
        status = FieldStatus(
            extracted=["name", "location"],
            failed=["expertise"],
            not_found=[],
        )
        assert status.extracted == ["name", "location"]
        assert status.failed == ["expertise"]
        assert status.not_found == []

    def test_field_status_defaults(self):
        """Test FieldStatus defaults to empty lists."""
        status = FieldStatus()
        assert status.extracted == []
        assert status.failed == []
        assert status.not_found == []


class TestExtractionResult:
    """Tests for ExtractionResult model."""

    def test_extraction_result_creation(self):
        """Test ExtractionResult creation."""
        metadata = ExtractionMetadata.now(success=True)
        result = ExtractionResult(
            success=True,
            priority_fields={"name": "Example"},
            metadata=metadata,
        )
        assert result.success is True
        assert result.priority_fields["name"] == "Example"
        assert result.error is None

    def test_extraction_result_with_partial_data(self):
        """Test ExtractionResult tracks partial success."""
        metadata = ExtractionMetadata(
            success=False,
            extraction_timestamp="2026-01-04T10:00:00Z",
            failure_reason="timeout",
        )
        status = FieldStatus(extracted=["name"], failed=["location"])
        result = ExtractionResult(
            success=False,
            priority_fields={"name": "Example"},
            metadata=metadata,
            fields_status=status,
        )
        assert result.success is False
        assert "name" in result.priority_fields
        assert "location" in result.fields_status.failed
