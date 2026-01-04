"""URL validation and normalization."""

import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class URLValidationError(Exception):
    """Raised when URL validation fails."""

    pass


class URLValidator:
    """Validates and normalizes URLs."""

    VALID_SCHEMES = {"http", "https"}

    @staticmethod
    def validate(url: str) -> None:
        """
        Validate that URL has valid format.

        Args:
            url: URL to validate

        Raises:
            URLValidationError: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise URLValidationError("URL must be a non-empty string")

        url = url.strip()
        if not url:
            raise URLValidationError("URL cannot be empty or whitespace only")

        # Check for scheme
        if "://" not in url:
            raise URLValidationError("URL must contain a scheme (http:// or https://)")

        parsed = urlparse(url)
        if parsed.scheme not in URLValidator.VALID_SCHEMES:
            raise URLValidationError(
                f"URL scheme '{parsed.scheme}' not supported. Use http:// or https://"
            )

        if not parsed.netloc:
            raise URLValidationError("URL must contain a domain/host")

    @staticmethod
    def normalize(url: str) -> str:
        """
        Normalize URL to standard format.

        Adds https:// if no scheme, removes trailing slashes.

        Args:
            url: URL to normalize

        Returns:
            Normalized URL

        Raises:
            URLValidationError: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise URLValidationError("URL must be a non-empty string")

        url = url.strip()

        # Add https:// if no scheme
        if "://" not in url:
            url = f"https://{url}"

        # Validate after normalization
        URLValidator.validate(url)

        # Remove trailing slashes for consistency
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        if parsed.fragment:
            normalized += f"#{parsed.fragment}"

        return normalized
