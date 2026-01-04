"""End-to-end tests for the public scraping API."""

import pytest
from pathlib import Path
from scraper.api import scrape_facility


class TestScrapeFacility:
    """End-to-end tests for scrape_facility() function."""

    def test_scrape_facility_returns_dict(self, sample_config_toml, temp_dir):
        """Test that scrape_facility returns correct dictionary structure."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        result = scrape_facility(
            url="https://example-fablab.com/about",
            config_path=str(config_file),
        )

        assert isinstance(result, dict)
        assert "success" in result
        assert "data" in result
        assert "metadata" in result
        assert "error" in result

    def test_scrape_facility_with_valid_url(self, sample_config_toml, temp_dir):
        """Test scraping with valid URL."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        result = scrape_facility(
            url="example-fablab.com",  # Will be normalized
            config_path=str(config_file),
        )

        # Should have executed without critical error
        assert result["error"] is None
        assert isinstance(result["success"], bool)

    def test_scrape_facility_with_output_file(self, sample_config_toml, temp_dir):
        """Test scraping with output file creation."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)
        output_file = temp_dir / "output.toml"

        result = scrape_facility(
            url="https://example-fablab.com",
            config_path=str(config_file),
            output_path=str(output_file),
        )

        # Output file should be created
        assert output_file.exists() if result["error"] is None else True

    def test_scrape_facility_missing_config(self, temp_dir):
        """Test scraping fails gracefully with missing config."""
        result = scrape_facility(
            url="https://example.com",
            config_path="/nonexistent/config.toml",
        )

        assert result["error"] is not None
        assert "not found" in result["error"].lower() or "configuration" in result["error"].lower()

    def test_scrape_facility_invalid_url(self, sample_config_toml, temp_dir):
        """Test scraping fails gracefully with invalid URL."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        result = scrape_facility(
            url="not a valid url",
            config_path=str(config_file),
        )

        assert result["error"] is not None

    def test_scrape_facility_unknown_site(self, sample_config_toml, temp_dir):
        """Test scraping fails for URL not in config."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        result = scrape_facility(
            url="https://unknown-site.com",
            config_path=str(config_file),
        )

        assert result["error"] is not None

    def test_scrape_facility_return_structure(self, sample_config_toml, temp_dir):
        """Test return value structure."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        result = scrape_facility(
            url="https://example-fablab.com",
            config_path=str(config_file),
        )

        # Verify data structure
        assert "priority_fields" in result["data"]
        assert "extra_metadata" in result["data"]
        assert "extraction_metadata" in result["metadata"]
        assert "fields_status" in result["metadata"]

    def test_scrape_facility_metadata_complete(self, sample_config_toml, temp_dir):
        """Test that metadata is complete."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        result = scrape_facility(
            url="https://example-fablab.com",
            config_path=str(config_file),
        )

        # Should have full metadata if success
        if result["error"] is None:
            metadata = result["metadata"]["extraction_metadata"]
            assert "success" in metadata
            assert "extraction_timestamp" in metadata
            assert "site_type" in metadata

            fields_status = result["metadata"]["fields_status"]
            assert "extracted" in fields_status
            assert "failed" in fields_status
            assert "not_found" in fields_status

    def test_scrape_facility_without_output_file(self, sample_config_toml, temp_dir):
        """Test scraping without output file parameter."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        result = scrape_facility(
            url="https://example-fablab.com",
            config_path=str(config_file),
            output_path=None,  # No output file
        )

        # Should complete successfully without file
        assert isinstance(result, dict)
        assert "error" in result
