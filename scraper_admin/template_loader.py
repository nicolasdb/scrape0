"""Template loader for configuration templates."""

import logging
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class TemplateLoader:
    """Loads and manages configuration templates."""

    def __init__(self, template_dir: str = "config/templates"):
        """Initialize template loader.

        Args:
            template_dir: Directory where templates are stored.
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def get_template(self, site_type: str) -> Optional[str]:
        """Load a template by site type.

        Args:
            site_type: Type of site (fablab, makerspace, blog).

        Returns:
            Template content as string, or None if not found.
        """
        template_file = self.template_dir / f"template_{site_type}.toml"

        if not template_file.exists():
            logger.warning(f"Template not found for site type: {site_type}")
            return None

        try:
            with open(template_file, "r") as f:
                content = f.read()
            logger.info(f"Loaded template for: {site_type}")
            return content
        except IOError as e:
            logger.error(f"Error loading template: {e}")
            return None

    def list_available_templates(self) -> List[str]:
        """List all available templates.

        Returns:
            List of site types with available templates.
        """
        templates = []
        for template_file in self.template_dir.glob("template_*.toml"):
            # Extract type from filename (template_TYPE.toml)
            site_type = template_file.stem.replace("template_", "")
            templates.append(site_type)

        logger.info(f"Found {len(templates)} available templates: {templates}")
        return sorted(templates)

    def template_exists(self, site_type: str) -> bool:
        """Check if a template exists for a site type.

        Args:
            site_type: Type of site.

        Returns:
            True if template exists.
        """
        return (self.template_dir / f"template_{site_type}.toml").exists()

    def validate_template(self, site_type: str) -> bool:
        """Validate that a template is valid TOML.

        Args:
            site_type: Type of site.

        Returns:
            True if template is valid TOML.
        """
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        content = self.get_template(site_type)
        if not content:
            return False

        try:
            tomllib.loads(content)
            logger.info(f"Template validated for: {site_type}")
            return True
        except Exception as e:
            logger.error(f"Template validation failed for {site_type}: {e}")
            return False
