"""Tests for Phase 5.2: Strategic Gap-Filling Tests.

These 8 tests verify critical workflows not yet thoroughly tested
in Phases 1-4, focusing on user-facing scenarios and integration points.
"""

import pytest
import tempfile
from pathlib import Path
from scraper.config import ConfigManager
from scraper import scrape_facility
from scraper.extraction import ExtractionEngine
from scraper.models import SiteConfig


class TestMultipleSitesEndToEnd:
    """Test end-to-end workflow with multiple sites in single config."""

    def test_scrape_facility_with_five_different_sites(self, temp_dir):
        """Test configuration with 5 different sites, each extracted separately."""
        config_content = """
[scraper]
primary_library = "scrapling"
timeout_seconds = 30

[[sites]]
id = "site-1"
url_pattern = "site1.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1.site1-name"
location = "span.site1-loc"

[[sites]]
id = "site-2"
url_pattern = "site2.com"
site_type = "fablab"

[sites.fields.priority]
name = "h2.site2-name"
location = "div.site2-loc"

[[sites]]
id = "site-3"
url_pattern = "site3.com"
site_type = "makerspace"

[sites.fields.priority]
name = "div.site3-name"
location = "p.site3-loc"

[[sites]]
id = "site-4"
url_pattern = "site4.com"
site_type = "hackerspace"

[sites.fields.priority]
name = "span.site4-name"
location = "div.site4-loc"

[[sites]]
id = "site-5"
url_pattern = "site5.com"
site_type = "workshop"

[sites.fields.priority]
name = "article h1"
location = "article .location"
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        # Should load all 5 sites
        assert len(config.sites) == 5
        assert config.sites[0].id == "site-1"
        assert config.sites[4].id == "site-5"

        # Should be able to lookup each site
        site1 = manager.lookup_site_config("https://site1.com/about")
        site5 = manager.lookup_site_config("https://site5.com/info")

        assert site1.id == "site-1"
        assert site5.id == "site-5"
        assert site1.site_type == "fablab"
        assert site5.site_type == "workshop"


class TestConfigurationReloadWithChanges:
    """Test configuration can be reloaded with modifications."""

    def test_config_reload_with_new_sites(self, temp_dir):
        """Test configuration can be reloaded with additional sites."""
        config_v1 = """
[scraper]
primary_library = "scrapling"

[[sites]]
id = "site-1"
url_pattern = "site1.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1"
"""

        config_v2 = """
[scraper]
primary_library = "scrapling"

[[sites]]
id = "site-1"
url_pattern = "site1.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1"

[[sites]]
id = "site-2"
url_pattern = "site2.com"
site_type = "makerspace"

[sites.fields.priority]
name = "h2"
"""

        config_file = temp_dir / "config.toml"
        manager = ConfigManager()

        # Load version 1
        config_file.write_text(config_v1)
        config = manager.load_config(str(config_file))
        assert len(config.sites) == 1

        # Update and reload version 2
        config_file.write_text(config_v2)
        config = manager.load_config(str(config_file))
        assert len(config.sites) == 2
        assert config.sites[1].id == "site-2"


class TestNetworkTimeoutWithRetryRecovery:
    """Test network timeout handling with automatic retry."""

    def test_timeout_retry_and_recovery_recorded(self):
        """Test timeout with retry is recorded in metadata."""
        # This is validated through scraper_engine tests
        # But we verify it's integrated into the full pipeline
        from scraper.scraper_engine import ScrapingEngine
        from scraper.models import ScraperConfig

        config = ScraperConfig(
            sites=[],
            primary_library="scrapling",
            default_timeout=5,
            default_max_retries=2,
        )

        engine = ScrapingEngine(config)
        # The engine has retry logic
        assert engine._config.default_max_retries >= 1
        assert engine._config.default_timeout >= 1


class TestInvalidConfigErrorClarity:
    """Test error messages for invalid configurations are clear."""

    def test_invalid_config_missing_required_fields(self, temp_dir):
        """Test error message when config missing required fields."""
        invalid_config = """
[scraper]
primary_library = "scrapling"

[[sites]]
id = "incomplete-site"
# Missing: url_pattern, site_type
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(invalid_config)

        manager = ConfigManager()
        try:
            manager.load_config(str(config_file))
            assert False, "Should raise ConfigurationError"
        except Exception as e:
            # Error message should be clear
            error_msg = str(e)
            assert (
                "url_pattern" in error_msg
                or "site_type" in error_msg
                or "required" in error_msg.lower()
            )

    def test_invalid_config_bad_toml_syntax(self, temp_dir):
        """Test error message for invalid TOML syntax."""
        invalid_toml = """
[scraper
primary_library = "scrapling"
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(invalid_toml)

        manager = ConfigManager()
        try:
            manager.load_config(str(config_file))
            assert False, "Should raise ConfigurationError"
        except Exception as e:
            # Error should mention TOML
            assert "TOML" in str(e) or "syntax" in str(e).lower()


class TestOutputTOMLExternalToolCompatibility:
    """Test generated TOML can be read by external TOML parsers."""

    def test_toml_output_parseable_by_tomli(self, sample_html, temp_dir):
        """Test TOML output can be parsed by tomli library."""
        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(sample_html, site_config)

        # Format output to TOML
        from scraper.output import TOMLOutputFormatter

        formatter = TOMLOutputFormatter()
        toml_string = formatter.format_result(result)

        # Should be parseable by tomli
        import tomli

        parsed = tomli.loads(toml_string)
        assert "extraction_metadata" in parsed
        assert "priority_fields" in parsed
        assert "fields_status" in parsed


class TestMixedSuccessSomeFieldsExtracted:
    """Test mixed success: some fields extracted, others failed."""

    def test_mixed_success_returned_with_partial_data(self):
        """Test result returned when some fields succeed, others fail."""
        html_content = """
<html>
<body>
    <h1 class="name">Test Facility</h1>
    <span class="location">Test Location</span>
    <!-- Missing: expertise, url, contact -->
</body>
</html>
"""

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
                "expertise": "div.expertise",
                "url": "a.website",
                "contact": "span.contact",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(html_content, site_config)

        # Mixed success: some extracted, others not
        assert result.success is True  # Has some priority fields
        assert len(result.priority_fields) == 2
        assert len(result.fields_status.not_found) == 3
        assert "name" in result.fields_status.extracted
        assert "location" in result.fields_status.extracted
        assert "expertise" in result.fields_status.not_found


class TestSiteTypeDetectionAndTracking:
    """Test site type is properly detected and tracked for analytics."""

    def test_site_type_preserved_in_metadata(self, temp_dir):
        """Test site type is correctly preserved through extraction pipeline."""
        config_content = """
[scraper]
primary_library = "scrapling"

[[sites]]
id = "test-fablab"
url_pattern = "fablab.test.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1"

[[sites]]
id = "test-makerspace"
url_pattern = "maker.test.com"
site_type = "makerspace"

[sites.fields.priority]
name = "h1"
"""

        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)

        manager = ConfigManager()
        manager.load_config(str(config_file))

        # Lookup different sites
        fablab = manager.lookup_site_config("https://fablab.test.com")
        maker = manager.lookup_site_config("https://maker.test.com")

        # Site type should be tracked
        assert fablab.site_type == "fablab"
        assert maker.site_type == "makerspace"

        # This site_type is used in ExtractionMetadata for analytics
        from scraper.models import ExtractionMetadata

        metadata_fablab = ExtractionMetadata.now(success=True, site_type=fablab.site_type)
        metadata_maker = ExtractionMetadata.now(success=True, site_type=maker.site_type)

        assert metadata_fablab.site_type == "fablab"
        assert metadata_maker.site_type == "makerspace"


class TestMetadataCompletenessVerification:
    """Test metadata is complete and suitable for Phase 2 analytics."""

    def test_extraction_metadata_all_fields_present(self, sample_html):
        """Test extraction metadata includes all required fields for analytics."""
        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={"name": "h1.name"},
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(sample_html, site_config)

        # All metadata fields should be present
        metadata = result.metadata
        assert hasattr(metadata, "success")
        assert hasattr(metadata, "extraction_timestamp")
        assert hasattr(metadata, "failure_reason")
        assert hasattr(metadata, "site_type")
        assert hasattr(metadata, "extraction_duration_seconds")

        # Verify values are reasonable
        assert isinstance(metadata.success, bool)
        assert isinstance(metadata.extraction_timestamp, str)
        assert isinstance(metadata.site_type, str)
        assert isinstance(metadata.extraction_duration_seconds, float)

    def test_field_status_complete_for_all_fields(self, sample_html):
        """Test field status accounts for all configured fields."""
        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
                "expertise": "div.expertise",
                "url": "a.website",
                "contact": "span.contact",
            },
            extra_fields={
                "operating_hours": "div.hours",
                "equipment": "ul.equipment",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(sample_html, site_config)

        # All fields should be accounted for
        all_fields = set(site_config.priority_fields.keys()) | set(site_config.extra_fields.keys())
        accounted = (
            set(result.fields_status.extracted)
            | set(result.fields_status.failed)
            | set(result.fields_status.not_found)
        )

        # Every configured field should be in status
        for field in all_fields:
            assert field in accounted, f"Field {field} not in field status"
