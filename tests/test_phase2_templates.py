"""Tests for configuration template system."""

import pytest
from pathlib import Path

from scraper_admin.template_loader import TemplateLoader
from scraper_admin.config_generator import ConfigGenerator


class TestTemplateLoader:
    """Test template loader."""

    def test_get_template(self, temp_dir):
        """Test loading a template."""
        # Create template file
        template_dir = temp_dir / "templates"
        template_dir.mkdir()
        template_file = template_dir / "template_fablab.toml"
        template_file.write_text("[scraper]\nprimary_library = 'scrapling'")

        loader = TemplateLoader(str(template_dir))
        content = loader.get_template("fablab")

        assert content is not None
        assert "scrapling" in content

    def test_get_template_not_found(self, temp_dir):
        """Test getting non-existent template."""
        loader = TemplateLoader(str(temp_dir / "templates"))
        content = loader.get_template("nonexistent")

        assert content is None

    def test_list_available_templates(self, temp_dir):
        """Test listing available templates."""
        # Create template files
        template_dir = temp_dir / "templates"
        template_dir.mkdir()

        (template_dir / "template_fablab.toml").write_text("[test]")
        (template_dir / "template_makerspace.toml").write_text("[test]")
        (template_dir / "template_blog.toml").write_text("[test]")

        loader = TemplateLoader(str(template_dir))
        templates = loader.list_available_templates()

        assert len(templates) == 3
        assert "fablab" in templates
        assert "makerspace" in templates
        assert "blog" in templates

    def test_template_exists(self, temp_dir):
        """Test checking if template exists."""
        template_dir = temp_dir / "templates"
        template_dir.mkdir()
        (template_dir / "template_fablab.toml").write_text("[test]")

        loader = TemplateLoader(str(template_dir))

        assert loader.template_exists("fablab") is True
        assert loader.template_exists("nonexistent") is False

    def test_validate_template(self, temp_dir):
        """Test validating template TOML."""
        template_dir = temp_dir / "templates"
        template_dir.mkdir()

        # Valid TOML
        (template_dir / "template_fablab.toml").write_text(
            "[scraper]\nprimary_library = 'scrapling'"
        )

        loader = TemplateLoader(str(template_dir))
        assert loader.validate_template("fablab") is True

    def test_validate_invalid_template(self, temp_dir):
        """Test validating invalid TOML."""
        template_dir = temp_dir / "templates"
        template_dir.mkdir()

        # Invalid TOML
        (template_dir / "template_fablab.toml").write_text("[scraper\ninvalid")

        loader = TemplateLoader(str(template_dir))
        assert loader.validate_template("fablab") is False


class TestConfigGenerator:
    """Test configuration generator."""

    def test_generate_config(self, temp_dir):
        """Test generating a configuration."""
        config_dir = temp_dir / "config"
        template_dir = temp_dir / "templates"
        config_dir.mkdir()
        template_dir.mkdir()

        # Create template
        template_content = """[scraper]
primary_library = "scrapling"

[[sites]]
id = "${domain}"
url_pattern = "${domain}"
site_type = "${site_type}"

[sites.fields.priority]
name = "h1"
"""
        (template_dir / "template_fablab.toml").write_text(template_content)

        generator = ConfigGenerator(str(config_dir), str(template_dir))
        config_path, content = generator.generate_config(
            "https://example-fablab.com",
            "fablab",
        )

        assert Path(config_path).exists()
        assert "example" in content
        assert "fablab" in content

    def test_validate_config(self, temp_dir):
        """Test validating generated config."""
        config_dir = temp_dir / "config"
        config_dir.mkdir()

        generator = ConfigGenerator(str(config_dir))

        # Valid config
        valid_content = "[scraper]\nprimary_library = 'scrapling'"
        is_valid, error = generator.validate_config(valid_content)
        assert is_valid is True
        assert error is None

    def test_validate_invalid_config(self, temp_dir):
        """Test validating invalid config."""
        config_dir = temp_dir / "config"
        config_dir.mkdir()

        generator = ConfigGenerator(str(config_dir))

        # Invalid config
        invalid_content = "[scraper\ninvalid"
        is_valid, error = generator.validate_config(invalid_content)
        assert is_valid is False
        assert error is not None

    def test_generate_config_invalid_url(self, temp_dir):
        """Test generating config with invalid URL."""
        config_dir = temp_dir / "config"
        template_dir = temp_dir / "templates"
        config_dir.mkdir()
        template_dir.mkdir()

        generator = ConfigGenerator(str(config_dir), str(template_dir))

        with pytest.raises(ValueError):
            generator.generate_config("not-a-valid-url", "fablab")

    def test_generate_config_missing_template(self, temp_dir):
        """Test generating config with missing template."""
        config_dir = temp_dir / "config"
        template_dir = temp_dir / "templates"
        config_dir.mkdir()
        template_dir.mkdir()

        generator = ConfigGenerator(str(config_dir), str(template_dir))

        with pytest.raises(ValueError):
            generator.generate_config(
                "https://example.com",
                "nonexistent",
            )

    def test_generate_config_custom_template(self, temp_dir):
        """Test generating config with custom template."""
        config_dir = temp_dir / "config"
        config_dir.mkdir()

        generator = ConfigGenerator(str(config_dir))

        custom_template = "[test]\nvalue = 1"
        config_path, content = generator.generate_config(
            "https://example.com",
            "custom",
            template=custom_template,
        )

        assert "value = 1" in content
