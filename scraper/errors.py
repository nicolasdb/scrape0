"""Exception classes for the scraping module."""


class ScrapingError(Exception):
    """Base exception for scraping errors."""

    pass


class NetworkError(ScrapingError):
    """Raised on network-related errors."""

    pass


class NetworkTimeout(NetworkError):
    """Raised when request times out."""

    pass


class ExtractionError(ScrapingError):
    """Raised when data extraction fails."""

    pass


class ParsingError(ExtractionError):
    """Raised when HTML parsing fails."""

    pass


class TypeConversionError(ExtractionError):
    """Raised when type conversion fails."""

    pass
