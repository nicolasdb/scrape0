"""Tests for Phase 3: Expanded Configuration Schema (Task Group 3.1)."""

import pytest
from pathlib import Path
from scraper.config import ConfigManager, ConfigurationError


class TestMultipleSitesConfiguration:
    """Test configuration with multiple sites defined in single config."""

    def test_multiple_sites_in_single_config(self, temp_dir):
        """Test loading config with multiple sites."""
        config_content = """
[scraper]
primary_library = "scrapling"
timeout_seconds = 30

[[sites]]
id = "site-1"
url_pattern = "site1.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1"
location = "span.location"

[[sites]]
id = "site-2"
url_pattern = "site2.com"
site_type = "makerspace"

[sites.fields.priority]
name = "h2"
contact = "span.contact"
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        assert len(config.sites) == 2
        assert config.sites[0].id == "site-1"
        assert config.sites[1].id == "site-2"
        assert config.sites[0].site_type == "fablab"
        assert config.sites[1].site_type == "makerspace"

    def test_lookup_different_sites_by_url(self, temp_dir):
        """Test looking up different sites by their URL patterns."""
        config_content = """
[scraper]
primary_library = "scrapling"

[[sites]]
id = "fablab-1"
url_pattern = "fablab.example.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1"

[[sites]]
id = "makerspace-1"
url_pattern = "maker.example.com"
site_type = "makerspace"

[sites.fields.priority]
name = "h2"
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)

        manager = ConfigManager()
        manager.load_config(str(config_file))

        # Different URLs should match different sites
        site1 = manager.lookup_site_config("https://fablab.example.com/")
        site2 = manager.lookup_site_config("https://maker.example.com/")

        assert site1.id == "fablab-1"
        assert site2.id == "makerspace-1"
        assert site1 is not site2


class TestExtraFieldsConfiguration:
    """Test configuration with extra fields alongside priority fields."""

    def test_extra_fields_extracted_alongside_priority(self, sample_config_toml, temp_dir):
        """Test that extra fields are extracted and stored separately."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        site = config.sites[0]

        # Priority fields should be present
        assert "name" in site.priority_fields
        assert "location" in site.priority_fields

        # Extra fields should be present
        assert "operating_hours" in site.extra_fields

    def test_extra_fields_optional(self, temp_dir):
        """Test configuration works without extra fields defined."""
        config_content = """
[scraper]
primary_library = "scrapling"

[[sites]]
id = "minimal-site"
url_pattern = "minimal.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1"
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        site = config.sites[0]
        assert len(site.extra_fields) == 0

    def test_multiple_extra_fields(self, temp_dir):
        """Test configuration with multiple extra fields."""
        config_content = """
[scraper]
primary_library = "scrapling"

[[sites]]
id = "rich-site"
url_pattern = "rich.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1"

[sites.fields.extra]
operating_hours = "div.hours"
equipment = "div.equipment"
pricing = "span.price"
website_url = "a.website"
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        site = config.sites[0]
        assert len(site.extra_fields) == 4
        assert "operating_hours" in site.extra_fields
        assert "equipment" in site.extra_fields
        assert "pricing" in site.extra_fields
        assert "website_url" in site.extra_fields


class TestSiteSpecificConfigOverrides:
    """Test site-specific timeout and retry overrides."""

    def test_site_specific_timeout_override(self, temp_dir):
        """Test site can override default timeout."""
        config_content = """
[scraper]
primary_library = "scrapling"
timeout_seconds = 30

[[sites]]
id = "fast-site"
url_pattern = "fast.com"
site_type = "fablab"
timeout_seconds = 10

[sites.fields.priority]
name = "h1"

[[sites]]
id = "slow-site"
url_pattern = "slow.com"
site_type = "fablab"
timeout_seconds = 60

[sites.fields.priority]
name = "h1"
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        fast_site = config.sites[0]
        slow_site = config.sites[1]

        assert fast_site.timeout_seconds == 10
        assert slow_site.timeout_seconds == 60
        assert config.default_timeout == 30

    def test_site_specific_retry_override(self, temp_dir):
        """Test site can override default max retries."""
        config_content = """
[scraper]
primary_library = "scrapling"
max_retries = 3

[[sites]]
id = "reliable-site"
url_pattern = "reliable.com"
site_type = "fablab"
max_retries = 1

[sites.fields.priority]
name = "h1"

[[sites]]
id = "unreliable-site"
url_pattern = "unreliable.com"
site_type = "fablab"
max_retries = 5

[sites.fields.priority]
name = "h1"
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        reliable = config.sites[0]
        unreliable = config.sites[1]

        assert reliable.max_retries == 1
        assert unreliable.max_retries == 5
        assert config.default_max_retries == 3

    def test_uses_default_when_not_overridden(self, temp_dir):
        """Test site uses default values when not overridden."""
        config_content = """
[scraper]
primary_library = "scrapling"
timeout_seconds = 30
max_retries = 3

[[sites]]
id = "default-site"
url_pattern = "default.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1"
"""
        config_file = temp_dir / "config.toml"
        config_file.write_text(config_content)

        manager = ConfigManager()
        config = manager.load_config(str(config_file))

        site = config.sites[0]
        # Should use defaults from scraper section
        assert site.timeout_seconds == 30
        assert site.max_retries == 3
