"""Configuration generator for sites."""

import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from scraper_admin.template_loader import TemplateLoader

logger = logging.getLogger(__name__)


class ConfigGenerator:
    """Generates site configurations from templates."""

    def __init__(self, config_dir: str = "config", template_dir: str = "config/templates"):
        """Initialize config generator.

        Args:
            config_dir: Directory where configs are stored.
            template_dir: Directory where templates are stored.
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.template_loader = TemplateLoader(template_dir)

    def generate_config(
        self,
        url: str,
        site_type: str,
        template: Optional[str] = None,
    ) -> tuple[str, str]:
        """Generate a site configuration from template.

        Args:
            url: Site URL.
            site_type: Type of site (fablab, makerspace, blog).
            template: Optional custom template content.

        Returns:
            Tuple of (config_file_path, config_content).

        Raises:
            ValueError: If template not found or URL invalid.
        """
        # Extract domain from URL
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "").split("/")[0]
            domain_name = domain.split(".")[0]
        except Exception as e:
            raise ValueError(f"Invalid URL: {e}")

        # Load template if not provided
        if not template:
            template = self.template_loader.get_template(site_type)
            if not template:
                raise ValueError(f"No template found for site type: {site_type}")

        # Customize template with site-specific values
        config_content = self._customize_template(template, url, site_type, domain)

        # Save config file
        config_path = self.config_dir / f"{domain_name}.toml"
        try:
            with open(config_path, "w") as f:
                f.write(config_content)
            logger.info(f"Generated config for {domain_name} at {config_path}")
        except IOError as e:
            logger.error(f"Error writing config file: {e}")
            raise

        return str(config_path), config_content

    def validate_config(self, config_content: str) -> tuple[bool, Optional[str]]:
        """Validate that a config is valid TOML.

        Args:
            config_content: Configuration content to validate.

        Returns:
            Tuple of (is_valid, error_message).
        """
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        try:
            tomllib.loads(config_content)
            logger.info("Config validation successful")
            return True, None
        except Exception as e:
            error_msg = f"Config validation failed: {e}"
            logger.error(error_msg)
            return False, error_msg

    def _customize_template(
        self,
        template: str,
        url: str,
        site_type: str,
        domain: str,
    ) -> str:
        """Customize template with site-specific values.

        Args:
            template: Template content.
            url: Site URL.
            site_type: Site type.
            domain: Domain name.

        Returns:
            Customized template.
        """
        # Replace placeholder values
        config = template.replace("${url}", url)
        config = config.replace("${site_type}", site_type)
        config = config.replace("${domain}", domain)

        return config
