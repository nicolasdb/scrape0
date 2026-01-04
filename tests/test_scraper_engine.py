"""Tests for the scraping engine."""

import pytest
from unittest.mock import patch, MagicMock
from scraper.models import ScraperConfig, SiteConfig
from scraper.scraper_engine import ScrapingEngine
from scraper.errors import NetworkTimeout, NetworkError


@pytest.fixture
def scraper_config():
    """Create a test scraper configuration."""
    site = SiteConfig(
        id="test-site",
        url_pattern="example.com",
        site_type="test",
        priority_fields={"name": "h1"},
    )
    return ScraperConfig(sites=[site], default_timeout=10, default_max_retries=3)


class TestScrapingEngine:
    """Tests for ScrapingEngine class."""

    def test_engine_initialization(self, scraper_config):
        """Test engine initializes with config."""
        engine = ScrapingEngine(scraper_config)
        assert engine._timeout == 10
        assert engine._max_retries == 3

    def test_fetch_content_returns_html(self, scraper_config):
        """Test successful HTML fetch."""
        engine = ScrapingEngine(scraper_config)
        content = engine.fetch_content("https://example.com")
        assert isinstance(content, str)
        assert len(content) > 0

    def test_fetch_content_mock_fallback(self, scraper_config):
        """Test mock fetch when scrapling unavailable."""
        engine = ScrapingEngine(scraper_config)
        content = engine.fetch_content("https://example.com")
        # Mock content should be returned
        assert "Mock Content" in content or "<html>" in content

    def test_fetch_with_custom_timeout(self, scraper_config):
        """Test custom timeout parameter."""
        engine = ScrapingEngine(scraper_config)
        # Should not raise with valid URL
        content = engine.fetch_content("https://example.com", timeout=5)
        assert isinstance(content, str)

    def test_no_retry_on_success(self, scraper_config):
        """Test that successful fetch doesn't retry."""
        engine = ScrapingEngine(scraper_config)

        with patch.object(engine, "_fetch_with_timeout") as mock_fetch:
            mock_fetch.return_value = "<html>Content</html>"
            content = engine.fetch_content("https://example.com")
            assert content == "<html>Content</html>"
            # Should be called exactly once
            assert mock_fetch.call_count == 1

    def test_retry_logic_on_transient_failure(self, scraper_config):
        """Test retry logic on transient failures."""
        engine = ScrapingEngine(scraper_config)
        call_count = 0

        def mock_fetch_impl(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise NetworkTimeout("Timeout")
            return "<html>Success</html>"

        with patch.object(engine, "_fetch_with_timeout", side_effect=mock_fetch_impl):
            content = engine.fetch_content("https://example.com")
            assert "<html>Success</html>" in content
            # Should have retried once
            assert call_count == 2

    def test_network_error_categorization(self, scraper_config):
        """Test that network errors are properly categorized."""
        engine = ScrapingEngine(scraper_config)

        with patch.object(engine, "_fetch_with_timeout") as mock_fetch:
            # Simulate network error
            mock_fetch.side_effect = NetworkError("Connection failed")
            with pytest.raises(NetworkError):
                engine.fetch_content("https://example.com")

    def test_max_retries_gives_up(self, scraper_config):
        """Test that engine gives up after max retries."""
        config = ScraperConfig(
            sites=[
                SiteConfig(
                    id="test",
                    url_pattern="test.com",
                    site_type="test",
                    priority_fields={},
                )
            ],
            default_timeout=1,
            default_max_retries=1,  # Only 1 retry
        )
        engine = ScrapingEngine(config)

        with patch.object(engine, "_fetch_with_timeout") as mock_fetch:
            mock_fetch.side_effect = NetworkTimeout("Always timeout")
            with pytest.raises(NetworkTimeout):
                engine.fetch_content("https://example.com")

            # Should have been called twice (initial + 1 retry)
            assert mock_fetch.call_count == 2
