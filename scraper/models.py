"""Data models for the scraping module."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


@dataclass
class SiteConfig:
    """Configuration for a single site."""

    id: str  # Unique identifier for the site
    url_pattern: str  # Substring pattern to match against URLs
    site_type: str  # Type of site (e.g., "fablab", "makerspace")
    priority_fields: Dict[str, str]  # Field name -> extraction rule
    extra_fields: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 30
    max_retries: int = 3
    description: str = ""

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.id or not self.id.strip():
            raise ValueError("Site id cannot be empty")
        if not self.url_pattern or not self.url_pattern.strip():
            raise ValueError("Site url_pattern cannot be empty")
        if not self.site_type or not self.site_type.strip():
            raise ValueError("Site site_type cannot be empty")
        if not isinstance(self.priority_fields, dict):
            raise ValueError("priority_fields must be a dictionary")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be at least 1")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")


@dataclass
class ScraperConfig:
    """Root configuration for the scraper."""

    sites: List[SiteConfig]
    primary_library: str = "scrapling"
    default_timeout: int = 30
    default_max_retries: int = 3

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.primary_library or not self.primary_library.strip():
            raise ValueError("primary_library cannot be empty")
        if self.default_timeout < 1:
            raise ValueError("default_timeout must be at least 1")
        if self.default_max_retries < 0:
            raise ValueError("default_max_retries cannot be negative")


@dataclass
class ExtractionMetadata:
    """Metadata about an extraction operation."""

    success: bool
    extraction_timestamp: str  # ISO format UTC timestamp
    failure_reason: Optional[str] = None  # Category of failure if applicable
    site_type: str = "unknown"
    extraction_duration_seconds: float = 0.0

    @classmethod
    def now(cls, success: bool, site_type: str = "unknown") -> "ExtractionMetadata":
        """Create metadata with current timestamp."""
        return cls(
            success=success,
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            site_type=site_type,
        )


@dataclass
class FieldStatus:
    """Status of field extraction attempts."""

    extracted: List[str] = field(default_factory=list)  # Successfully extracted
    failed: List[str] = field(default_factory=list)  # Extraction errors
    not_found: List[str] = field(default_factory=list)  # No matches found


@dataclass
class ExtractionResult:
    """Result of a complete extraction operation."""

    success: bool
    priority_fields: Dict[str, Any] = field(default_factory=dict)
    extra_metadata: Dict[str, Any] = field(default_factory=dict)
    metadata: ExtractionMetadata = field(default_factory=lambda: ExtractionMetadata.now(False))
    fields_status: FieldStatus = field(default_factory=FieldStatus)
    error: Optional[str] = None  # Critical error that prevented extraction
