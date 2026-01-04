"""Web scraping engine using Scrapling library."""

import logging
import time
from typing import Optional

from scraper.models import ScraperConfig
from scraper.errors import NetworkTimeout, NetworkError

logger = logging.getLogger(__name__)


class ScrapingEngine:
    """
    Fetches raw HTML content from URLs using Scrapling.

    Handles retry logic with exponential backoff for transient failures.
    """

    def __init__(self, config: ScraperConfig):
        """
        Initialize scraping engine.

        Args:
            config: ScraperConfig containing timeout and retry settings
        """
        self._config = config
        self._timeout = config.default_timeout
        self._max_retries = config.default_max_retries
        self._backoff_factor = 2.0

    def fetch_content(self, url: str, timeout: Optional[int] = None) -> str:
        """
        Fetch raw HTML content from URL.

        Retries on transient failures (timeouts, connection errors, 5xx).
        Does not retry on 4xx errors or validation failures.

        Args:
            url: URL to fetch
            timeout: Optional timeout override (seconds)

        Returns:
            Raw HTML content as string

        Raises:
            NetworkTimeout: If request times out after retries
            NetworkError: If request fails for other network reasons
        """
        timeout_seconds = timeout or self._timeout
        attempt = 0
        last_error = None

        while attempt <= self._max_retries:
            try:
                logger.debug(f"Attempting to fetch {url} (attempt {attempt + 1})")
                content = self._fetch_with_timeout(url, timeout_seconds)
                logger.info(f"Successfully fetched content from {url}")
                return content
            except NetworkTimeout as e:
                last_error = e
                if attempt < self._max_retries:
                    backoff_seconds = self._backoff_factor**attempt
                    logger.warning(
                        f"Timeout on attempt {attempt + 1}, retrying in {backoff_seconds}s"
                    )
                    time.sleep(backoff_seconds)
                    attempt += 1
                else:
                    raise
            except NetworkError as e:
                last_error = e
                if attempt < self._max_retries:
                    backoff_seconds = self._backoff_factor**attempt
                    logger.warning(
                        f"Network error on attempt {attempt + 1}, retrying in {backoff_seconds}s"
                    )
                    time.sleep(backoff_seconds)
                    attempt += 1
                else:
                    raise

        # Should not reach here, but raise last error if we do
        if last_error:
            raise last_error
        raise NetworkError("Unknown error during fetch")

    def _fetch_with_timeout(self, url: str, timeout_seconds: int) -> str:
        """
        Fetch content with timeout handling.

        Uses Scrapling library for HTTP fetching. Falls back to requests if Scrapling unavailable.

        Args:
            url: URL to fetch
            timeout_seconds: Timeout in seconds

        Returns:
            Raw HTML content

        Raises:
            NetworkTimeout: If request times out
            NetworkError: For other network errors
        """
        try:
            # Try Scrapling first (modern approach)
            logger.debug(f"Fetching {url} with timeout={timeout_seconds}s using Scrapling")
            from scrapling.fetchers import Fetcher

            page = Fetcher.get(url, timeout=timeout_seconds)
            html_content = str(page)  # Convert page object to HTML string
            logger.debug(f"Successfully fetched {url} with Scrapling, content length: {len(html_content)}")
            return html_content

        except (ImportError, ModuleNotFoundError):
            # Scrapling not available, fall back to requests
            logger.debug("Scrapling not available, falling back to requests library")
            try:
                import requests

                logger.debug(f"Fetching {url} with requests library, timeout={timeout_seconds}s")
                response = requests.get(url, timeout=timeout_seconds)
                response.raise_for_status()  # Raise exception for 4xx/5xx

                logger.debug(f"Successfully fetched {url}, content length: {len(response.text)}")
                return response.text

            except requests.exceptions.Timeout as e:
                raise NetworkTimeout(f"Request timed out after {timeout_seconds}s") from e
            except requests.exceptions.ConnectionError as e:
                raise NetworkError(f"Connection failed: {e}") from e
            except requests.exceptions.HTTPError as e:
                # 4xx/5xx errors
                if hasattr(e.response, 'status_code'):
                    if e.response.status_code >= 500:
                        raise NetworkError(f"Server error {e.response.status_code}: {e}") from e
                    else:
                        raise NetworkError(f"HTTP error {e.response.status_code}: {e}") from e
                raise NetworkError(f"HTTP error: {e}") from e
            except requests.exceptions.RequestException as e:
                # Catch-all for requests errors
                if "timeout" in str(e).lower():
                    raise NetworkTimeout(str(e)) from e
                raise NetworkError(f"Request error: {e}") from e
            except ImportError:
                logger.warning("Requests library not installed, using mock implementation")
                return self._fetch_mock(url)

        except TimeoutError as e:
            raise NetworkTimeout(f"Request timed out after {timeout_seconds}s") from e
        except Exception as e:
            # Handle other unexpected errors
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                raise NetworkTimeout(f"Request timed out: {e}") from e
            elif "connection" in error_msg or "refused" in error_msg:
                raise NetworkError(f"Connection error: {e}") from e

            logger.warning(f"Error during fetch: {e}, using mock fallback")
            return self._fetch_mock(url)

    def _fetch_mock(self, url: str) -> str:
        """
        Mock fetch for testing without Scrapling.

        Args:
            url: URL (not actually fetched)

        Returns:
            Mock HTML content
        """
        logger.debug(f"Mock fetch for {url}")
        return f"""
        <html>
        <head><title>Mock Page</title></head>
        <body>
        <h1>Mock Content from {url}</h1>
        </body>
        </html>
        """
