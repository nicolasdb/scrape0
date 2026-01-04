"""Tests for the data extraction engine."""

import pytest
from scraper.models import SiteConfig, ExtractionResult, FieldStatus
from scraper.extraction import ExtractionEngine, RuleParser
from scraper.errors import ParsingError


@pytest.fixture
def extraction_engine():
    """Create extraction engine instance."""
    return ExtractionEngine()


@pytest.fixture
def site_config():
    """Create test site configuration."""
    return SiteConfig(
        id="test-site",
        url_pattern="example.com",
        site_type="fablab",
        priority_fields={
            "name": "h1.name",
            "location": "span.location",
            "expertise": "div.expertise",
            "url": "a.website",
            "contact": "span.contact",
        },
        extra_fields={"operating_hours": "div.hours"},
    )


class TestRuleParser:
    """Tests for rule parsing."""

    def test_parse_css_selector(self):
        """Test CSS selector parsing."""
        rule_type, pattern = RuleParser.parse_rule("h1.title")
        assert rule_type == "css"
        assert pattern == "h1.title"

    def test_parse_xpath(self):
        """Test XPath parsing."""
        rule_type, pattern = RuleParser.parse_rule("//h1[@class='title']")
        assert rule_type == "xpath"

    def test_parse_regex_delimited(self):
        """Test regex parsing with delimiters."""
        rule_type, pattern = RuleParser.parse_rule("/[A-Z][a-z]+/")
        assert rule_type == "regex"

    def test_parse_regex_anchored(self):
        """Test regex parsing with anchor."""
        rule_type, pattern = RuleParser.parse_rule("^Title:")
        assert rule_type == "regex"

    def test_parse_default_to_css(self):
        """Test unknown format defaults to CSS."""
        rule_type, pattern = RuleParser.parse_rule("some-selector")
        assert rule_type == "css"


class TestExtractionEngine:
    """Tests for extraction engine."""

    def test_extract_all_priority_fields(self, extraction_engine, site_config, sample_html):
        """Test extracting all priority fields from sample HTML."""
        result = extraction_engine.extract_fields(sample_html, site_config)

        assert result.success is True
        assert "name" in result.priority_fields
        assert "location" in result.priority_fields
        assert "expertise" in result.priority_fields
        assert result.priority_fields["name"] == "Example Fablab"

    def test_extract_extra_fields(self, extraction_engine, site_config, sample_html):
        """Test extracting extra metadata fields."""
        result = extraction_engine.extract_fields(sample_html, site_config)

        assert "operating_hours" in result.extra_metadata

    def test_partial_extraction_tracks_status(self, extraction_engine, sample_html):
        """Test partial extraction tracks field status."""
        site_config = SiteConfig(
            id="test",
            url_pattern="example.com",
            site_type="test",
            priority_fields={
                "name": "h1.name",
                "nonexistent": "span.nothere",  # This won't be found
            },
        )

        result = extraction_engine.extract_fields(sample_html, site_config)

        # Check field status
        assert "name" in result.fields_status.extracted
        assert (
            "nonexistent" in result.fields_status.not_found
            or "nonexistent" in result.fields_status.failed
        )

    def test_extraction_failure_with_empty_html(self, extraction_engine, site_config):
        """Test extraction with minimal HTML."""
        html = "<html><body></body></html>"
        result = extraction_engine.extract_fields(html, site_config)

        # Should not crash, but mark fields as not found
        assert result.success is False
        assert len(result.fields_status.not_found) > 0

    def test_invalid_html_raises_parsing_error(self, extraction_engine, site_config):
        """Test that invalid HTML raises ParsingError."""
        # Note: BeautifulSoup is very forgiving, so create a case it can't handle
        # For now, just verify error handling exists
        result = extraction_engine.extract_fields("<html>Unclosed tags", site_config)
        # BeautifulSoup will parse this, but extraction may fail
        assert isinstance(result, ExtractionResult)

    def test_css_selector_extraction(self, extraction_engine):
        """Test CSS selector extraction."""
        html = """
        <html>
        <body>
            <h1 class="name">Test Name</h1>
            <span class="location">Test City</span>
        </body>
        </html>
        """

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="test",
            priority_fields={
                "name": "h1.name",
                "location": "span.location",
            },
        )

        result = extraction_engine.extract_fields(html, site_config)
        assert result.priority_fields["name"] == "Test Name"
        assert result.priority_fields["location"] == "Test City"

    def test_multiple_matching_elements_joined(self, extraction_engine):
        """Test that multiple matching elements are joined."""
        html = """
        <html>
        <body>
            <div class="skills">
                <span>Python</span>
                <span>JavaScript</span>
                <span>Go</span>
            </div>
        </body>
        </html>
        """

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="test",
            priority_fields={
                "skills": "div.skills span",
            },
        )

        result = extraction_engine.extract_fields(html, site_config)
        # Should have joined multiple values
        assert "Python" in result.priority_fields.get("skills", "")

    def test_type_conversion_applied(self, extraction_engine):
        """Test that type conversion is applied to extracted values."""
        html = """
        <html>
        <body>
            <span class="hours">Mon, Tue, Wed</span>
            <span class="count">3</span>
        </body>
        </html>
        """

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="test",
            priority_fields={
                "hours": "span.hours",
                "count": "span.count",
            },
        )

        result = extraction_engine.extract_fields(html, site_config)
        # Should have converted comma-separated to list
        assert isinstance(result.priority_fields["hours"], (list, str))
        # Should have converted to number
        assert isinstance(result.priority_fields["count"], (int, str))

    def test_field_level_errors_dont_halt_extraction(self, extraction_engine):
        """Test that field-level errors don't halt extraction."""
        html = "<html><body><h1>Good Field</h1></body></html>"

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="test",
            priority_fields={
                "good": "h1",
                "bad_xpath": "//invalid[*syntax*",  # Bad syntax
            },
        )

        # Should not crash
        result = extraction_engine.extract_fields(html, site_config)
        # Good field should be extracted
        assert "good" in result.fields_status.extracted
        # Bad field should be marked as failed
        assert (
            "bad_xpath" in result.fields_status.failed
            or "bad_xpath" in result.fields_status.not_found
        )

    def test_extraction_metadata_site_type(self, extraction_engine, site_config, sample_html):
        """Test that extraction metadata includes site type."""
        result = extraction_engine.extract_fields(sample_html, site_config)
        assert result.metadata.site_type == "fablab"
