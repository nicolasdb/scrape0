"""Input layer for URL validation and configuration lookup."""

import logging
from scraper.validators import URLValidator, URLValidationError
from scraper.config import ConfigManager, ConfigurationError
from scraper.models import SiteConfig

logger = logging.getLogger(__name__)


class InputLayer:
    """Coordinates URL validation and configuration lookup."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize input layer.

        Args:
            config_manager: ConfigManager instance for configuration lookups
        """
        self._config_manager = config_manager
        self._validator = URLValidator()

    def validate_and_normalize_url(self, url: str) -> str:
        """
        Validate and normalize the input URL.

        Args:
            url: URL to validate

        Returns:
            Normalized URL

        Raises:
            URLValidationError: If URL is invalid
        """
        try:
            return self._validator.normalize(url)
        except URLValidationError as e:
            logger.error(f"URL validation failed: {e}")
            raise

    def lookup_site_config(self, url: str) -> SiteConfig:
        """
        Look up site configuration for the given URL.

        Args:
            url: URL to match against site patterns

        Returns:
            SiteConfig for the matching site

        Raises:
            ConfigurationError: If no matching site found
        """
        try:
            return self._config_manager.lookup_site_config(url)
        except ConfigurationError as e:
            logger.error(f"Site configuration lookup failed: {e}")
            raise
