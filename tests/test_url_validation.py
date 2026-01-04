"""Tests for URL validation and input layer."""

import pytest
from scraper.validators import URLValidator, URLValidationError
from scraper.input import InputLayer
from scraper.config import ConfigManager


class TestURLValidator:
    """Tests for URLValidator class."""

    def test_valid_https_url(self, valid_url):
        """Test valid HTTPS URL passes validation."""
        URLValidator.validate(valid_url)
        # Should not raise

    def test_valid_http_url(self):
        """Test valid HTTP URL passes validation."""
        URLValidator.validate("http://example.com")
        # Should not raise

    def test_invalid_url_no_scheme(self):
        """Test URL without scheme rejected."""
        with pytest.raises(URLValidationError, match="must contain a scheme"):
            URLValidator.validate("example.com")

    def test_invalid_url_bad_scheme(self):
        """Test URL with invalid scheme rejected."""
        with pytest.raises(URLValidationError, match="scheme"):
            URLValidator.validate("ftp://example.com")

    def test_invalid_url_empty(self):
        """Test empty URL rejected."""
        with pytest.raises(URLValidationError, match="non-empty string"):
            URLValidator.validate("")

    def test_invalid_url_whitespace_only(self):
        """Test whitespace-only URL rejected."""
        with pytest.raises(URLValidationError, match="cannot be empty"):
            URLValidator.validate("   ")

    def test_invalid_url_malformed(self):
        """Test malformed URL rejected."""
        with pytest.raises(URLValidationError, match="must contain"):
            URLValidator.validate("http://")

    def test_normalize_adds_https_scheme(self):
        """Test normalization adds https:// if missing."""
        normalized = URLValidator.normalize("example.com")
        assert normalized.startswith("https://")
        assert "example.com" in normalized

    def test_normalize_preserves_existing_scheme(self):
        """Test normalization preserves existing http/https."""
        http_url = URLValidator.normalize("http://example.com")
        assert http_url.startswith("http://")

        https_url = URLValidator.normalize("https://example.com")
        assert https_url.startswith("https://")

    def test_normalize_removes_trailing_slashes(self):
        """Test normalization removes trailing slashes."""
        normalized = URLValidator.normalize("https://example.com/path/")
        assert not normalized.endswith("/")
        assert "/path" in normalized

    def test_normalize_with_query_params(self):
        """Test normalization preserves query parameters."""
        normalized = URLValidator.normalize("example.com/page?id=123&sort=asc")
        assert "?id=123" in normalized
        assert "sort=asc" in normalized

    def test_normalize_with_fragment(self):
        """Test normalization preserves fragments."""
        normalized = URLValidator.normalize("example.com/page#section")
        assert "#section" in normalized


class TestInputLayer:
    """Tests for InputLayer class."""

    def test_input_layer_validates_url(self, sample_config_toml, temp_dir):
        """Test input layer validates URLs."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        manager = ConfigManager()
        manager.load_config(str(config_file))
        input_layer = InputLayer(manager)

        # Valid URL should work
        normalized = input_layer.validate_and_normalize_url("example-fablab.com")
        assert "https://" in normalized

    def test_input_layer_rejects_empty_url(self, sample_config_toml, temp_dir):
        """Test input layer rejects empty URLs."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        manager = ConfigManager()
        manager.load_config(str(config_file))
        input_layer = InputLayer(manager)

        with pytest.raises(URLValidationError):
            input_layer.validate_and_normalize_url("")

    def test_input_layer_lookup_site_config(self, sample_config_toml, temp_dir):
        """Test input layer looks up site configuration."""
        config_file = temp_dir / "config.toml"
        config_file.write_text(sample_config_toml)

        manager = ConfigManager()
        manager.load_config(str(config_file))
        input_layer = InputLayer(manager)

        site_config = input_layer.lookup_site_config("https://example-fablab.com")
        assert site_config.id == "example-fablab"
        assert site_config.site_type == "fablab"
