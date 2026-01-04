"""Tests for configuration management."""

import pytest
import tempfile
from pathlib import Path
from scraper.config import ConfigManager, ConfigurationError


class TestConfigManager:
    """Tests for ConfigManager class."""

    def test_load_valid_config(self, sample_config_toml, temp_dir):
        """Test loading valid TOML configuration."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        assert config is not None
        assert config.primary_library == "scrapling"
        assert config.default_timeout == 30
        assert len(config.sites) > 0

    def test_load_config_file_not_found(self):
        """Test loading non-existent configuration file."""
        manager = ConfigManager()
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            manager.load_config("/nonexistent/config.toml")

    def test_load_config_invalid_toml_syntax(self, temp_dir):
        """Test loading invalid TOML syntax."""
        config_file = temp_dir / "bad_config.toml"
        config_file.write_text("[invalid toml\nno closing bracket")

        manager = ConfigManager()
        with pytest.raises(ConfigurationError, match="Invalid TOML syntax"):
            manager.load_config(str(config_file))

    def test_config_with_defaults(self, temp_dir):
        """Test configuration with optional fields using defaults."""
        config_content = """
[scraper]
primary_library = "scrapling"

[[sites]]
id = "test-site"
url_pattern = "test.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1"
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        # Check defaults applied
        assert config.default_timeout == 30
        assert config.default_max_retries == 3
        assert config.sites[0].timeout_seconds == 30

    def test_lookup_site_config_by_url(self, sample_config_toml, temp_dir):
        """Test site configuration lookup by URL pattern."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        manager = ConfigManager()
        manager.load_config(str(config_file))

        # URL containing the pattern should match
        site_config = manager.lookup_site_config("https://example-fablab.com/about")
        assert site_config.id == "example-fablab"
        assert site_config.site_type == "fablab"

    def test_lookup_site_config_not_found(self, sample_config_toml, temp_dir):
        """Test site configuration lookup fails for unmatched URL."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        manager = ConfigManager()
        manager.load_config(str(config_file))

        with pytest.raises(ConfigurationError, match="No site configuration found"):
            manager.lookup_site_config("https://unknown-site.com")

    def test_config_caching(self, sample_config_toml, temp_dir):
        """Test site config caching for same URL."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        manager = ConfigManager()
        manager.load_config(str(config_file))

        url = "https://example-fablab.com"
        config1 = manager.lookup_site_config(url)
        config2 = manager.lookup_site_config(url)

        # Should be same object from cache
        assert config1 is config2

    def test_config_priority_fields_parsed(self, sample_config_toml, temp_dir):
        """Test priority fields are correctly parsed."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        site = config.sites[0]
        assert "name" in site.priority_fields
        assert "location" in site.priority_fields
        assert "expertise" in site.priority_fields

    def test_config_extra_fields_parsed(self, sample_config_toml, temp_dir):
        """Test extra fields are correctly parsed."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        site = config.sites[0]
        assert "operating_hours" in site.extra_fields
