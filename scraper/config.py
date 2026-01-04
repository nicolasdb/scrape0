"""Configuration management for the scraper."""

import logging
from pathlib import Path
from typing import Dict, Optional
import tomli

from scraper.models import SiteConfig, ScraperConfig

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or cannot be loaded."""

    pass


class ConfigManager:
    """Manages scraper configuration loading and validation."""

    def __init__(self):
        """Initialize configuration manager."""
        self._config: Optional[ScraperConfig] = None
        self._config_path: Optional[Path] = None
        self._site_cache: Dict[str, SiteConfig] = {}

    def load_config(self, config_path: str) -> ScraperConfig:
        """
        Load and parse TOML configuration file.

        Args:
            config_path: Path to configuration TOML file

        Returns:
            ScraperConfig object

        Raises:
            ConfigurationError: If file not found or TOML syntax invalid
        """
        path = Path(config_path)

        if not path.exists():
            msg = f"Configuration file not found: {config_path}"
            logger.error(msg)
            raise ConfigurationError(msg)

        try:
            with open(path, "rb") as f:
                config_dict = tomli.load(f)
        except tomli.TOMLDecodeError as e:
            msg = f"Invalid TOML syntax in configuration file: {e}"
            logger.error(msg)
            raise ConfigurationError(msg)
        except IOError as e:
            msg = f"Failed to read configuration file: {e}"
            logger.error(msg)
            raise ConfigurationError(msg)

        self._config = self._parse_config(config_dict)
        self._config_path = path
        self._site_cache.clear()

        logger.info(f"Configuration loaded from {config_path}")
        return self._config

    def _parse_config(self, config_dict: dict) -> ScraperConfig:
        """
        Parse configuration dictionary into ScraperConfig object.

        Args:
            config_dict: Dictionary loaded from TOML

        Returns:
            ScraperConfig object

        Raises:
            ConfigurationError: If required fields missing or invalid
        """
        # Parse scraper section
        scraper_section = config_dict.get("scraper", {})
        primary_library = scraper_section.get("primary_library", "scrapling")
        default_timeout = scraper_section.get("timeout_seconds", 30)
        default_max_retries = scraper_section.get("max_retries", 3)

        # Parse sites
        sites_list = config_dict.get("sites", [])
        if not isinstance(sites_list, list):
            raise ConfigurationError("'sites' must be a list of site configurations")

        sites = []
        for site_dict in sites_list:
            if not isinstance(site_dict, dict):
                raise ConfigurationError("Each site must be a dictionary")

            site_id = site_dict.get("id")
            url_pattern = site_dict.get("url_pattern")
            site_type = site_dict.get("site_type")

            if not site_id or not url_pattern or not site_type:
                raise ConfigurationError(
                    "Each site must have 'id', 'url_pattern', and 'site_type' fields"
                )

            # Parse priority and extra fields
            fields_section = site_dict.get("fields", {})
            priority_fields = fields_section.get("priority", {})
            extra_fields = fields_section.get("extra", {})

            if not isinstance(priority_fields, dict):
                raise ConfigurationError(f"Site {site_id}: priority fields must be a dictionary")
            if not isinstance(extra_fields, dict):
                raise ConfigurationError(f"Site {site_id}: extra fields must be a dictionary")

            # Use site-specific or default timeouts
            timeout = site_dict.get("timeout_seconds", default_timeout)
            max_retries = site_dict.get("max_retries", default_max_retries)

            site_config = SiteConfig(
                id=site_id,
                url_pattern=url_pattern,
                site_type=site_type,
                priority_fields=priority_fields,
                extra_fields=extra_fields,
                timeout_seconds=timeout,
                max_retries=max_retries,
                description=site_dict.get("description", ""),
            )
            sites.append(site_config)

        return ScraperConfig(
            sites=sites,
            primary_library=primary_library,
            default_timeout=default_timeout,
            default_max_retries=default_max_retries,
        )

    def lookup_site_config(self, url: str) -> SiteConfig:
        """
        Find site configuration matching the given URL.

        Args:
            url: URL to match against site patterns

        Returns:
            SiteConfig matching the URL

        Raises:
            ConfigurationError: If no matching site found
        """
        if not self._config:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")

        # Check cache
        cache_key = url
        if cache_key in self._site_cache:
            return self._site_cache[cache_key]

        # Search for matching site
        for site in self._config.sites:
            if site.url_pattern in url:
                self._site_cache[cache_key] = site
                logger.debug(f"Found site config '{site.id}' for URL: {url}")
                return site

        msg = f"No site configuration found for URL: {url}"
        logger.error(msg)
        raise ConfigurationError(msg)

    @property
    def config(self) -> Optional[ScraperConfig]:
        """Get current configuration object."""
        return self._config

    @property
    def config_path(self) -> Optional[Path]:
        """Get path to loaded configuration file."""
        return self._config_path
