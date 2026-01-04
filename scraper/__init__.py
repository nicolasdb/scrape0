"""Core scraping module with modular architecture."""

__version__ = "0.1.0"


# Lazy import to avoid circular dependencies
def __getattr__(name):
    if name == "scrape_facility":
        from scraper.api import scrape_facility

        return scrape_facility
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
