"""Data models for the site registry system."""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum


class SiteType(str, Enum):
    """Supported site types."""
    FABLAB = "fablab"
    MAKERSPACE = "makerspace"
    BLOG = "blog"
    OTHER = "other"


class Frequency(str, Enum):
    """Supported scraping frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class SiteRegistry:
    """Registry entry for a single site."""

    id: str  # Unique identifier (domain-based)
    url: str  # Full URL
    site_type: SiteType  # Type of site
    description: str  # Human-readable description
    frequency: Frequency  # Scraping frequency
    active: bool  # Whether this site is active
    created_date: str  # ISO format UTC timestamp
    last_scraped: Optional[str] = None  # Last successful scrape timestamp
    config_path: Optional[str] = None  # Path to site-specific config file

    def __post_init__(self) -> None:
        """Validate registry entry after initialization."""
        if not self.id or not self.id.strip():
            raise ValueError("Site id cannot be empty")
        if not self.url or not self.url.strip():
            raise ValueError("Site url cannot be empty")
        if not isinstance(self.site_type, (SiteType, str)):
            raise ValueError("site_type must be a valid SiteType")
        if not isinstance(self.frequency, (Frequency, str)):
            raise ValueError("frequency must be a valid Frequency")

    @classmethod
    def from_dict(cls, data: dict) -> "SiteRegistry":
        """Create a SiteRegistry from a dictionary."""
        # Convert string enums if needed
        if isinstance(data.get("site_type"), str):
            data["site_type"] = SiteType(data["site_type"])
        if isinstance(data.get("frequency"), str):
            data["frequency"] = Frequency(data["frequency"])

        return cls(**data)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "url": self.url,
            "site_type": self.site_type.value if isinstance(self.site_type, SiteType) else self.site_type,
            "description": self.description,
            "frequency": self.frequency.value if isinstance(self.frequency, Frequency) else self.frequency,
            "active": self.active,
            "created_date": self.created_date,
            "last_scraped": self.last_scraped,
            "config_path": self.config_path,
        }


@dataclass
class SiteRegistryFile:
    """Container for the entire registry file."""

    version: str = "1.0"  # Schema version for migrations
    sites: List[SiteRegistry] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "sites": [site.to_dict() for site in self.sites],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SiteRegistryFile":
        """Create from dictionary."""
        registry = cls(version=data.get("version", "1.0"))
        for site_data in data.get("sites", []):
            registry.sites.append(SiteRegistry.from_dict(site_data))
        return registry
