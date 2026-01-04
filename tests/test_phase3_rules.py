"""Tests for Phase 3.2: Support for Additional Scraping Rules (Task Group 3.2)."""

import pytest
from scraper.extraction import RuleParser, ExtractionEngine
from scraper.models import SiteConfig


class TestRuleParserDetection:
    """Test RuleParser detects various rule types correctly."""

    def test_css_selector_detection(self):
        """Test CSS selector rules are detected correctly."""
        rule_type, pattern = RuleParser.parse_rule("h1.name")
        assert rule_type == "css"
        assert pattern == "h1.name"

    def test_xpath_detection(self):
        """Test XPath rules are detected correctly."""
        rule_type, pattern = RuleParser.parse_rule("//h1[@class='name']")
        assert rule_type == "xpath"
        assert pattern == "//h1[@class='name']"

    def test_xpath_simple_detection(self):
        """Test XPath with simple syntax detection."""
        rule_type, pattern = RuleParser.parse_rule("//div[@id='main']/span")
        assert rule_type == "xpath"

    def test_regex_delimited_detection(self):
        """Test regex rules with delimiters are detected correctly."""
        rule_type, pattern = RuleParser.parse_rule("/[A-Z][a-z]+/")
        assert rule_type == "regex"
        assert pattern == "/[A-Z][a-z]+/"

    def test_regex_anchored_detection(self):
        """Test regex rules with anchors are detected correctly."""
        rule_type, pattern = RuleParser.parse_rule("^[0-9]{2,4}-[0-9]{2}-[0-9]{2}")
        assert rule_type == "regex"

    def test_default_css_selector(self):
        """Test rules without special syntax default to CSS selector."""
        rule_type, pattern = RuleParser.parse_rule("div.equipment li")
        assert rule_type == "css"
        assert pattern == "div.equipment li"

    def test_whitespace_handling(self):
        """Test parser handles leading/trailing whitespace."""
        rule_type, pattern = RuleParser.parse_rule("  h1.name  ")
        assert rule_type == "css"
        assert pattern == "h1.name"


class TestCSSRuleExtraction:
    """Test CSS selector extraction works correctly."""

    def test_css_selector_basic(self, sample_html):
        """Test basic CSS selector extraction."""
        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(sample_html, site_config)

        assert "name" in result.priority_fields
        assert result.priority_fields["name"] == "Example Fablab"

    def test_css_selector_class(self, sample_html):
        """Test CSS selector with class."""
        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "location": "span.location",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(sample_html, site_config)

        assert "location" in result.priority_fields
        assert "San Francisco" in result.priority_fields["location"]

    def test_css_selector_multiple_matching(self, sample_html):
        """Test CSS selector with multiple matches returns joined text."""
        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "expertise": "div.expertise",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(sample_html, site_config)

        assert "expertise" in result.priority_fields
        # Should extract the expertise content
        assert "3D printing" in result.priority_fields["expertise"]


class TestXPathRuleExtraction:
    """Test XPath rule extraction support."""

    def test_xpath_rule_detection(self):
        """Test XPath rules are detected and parsed."""
        rule_type, pattern = RuleParser.parse_rule("//h1[@class='name']")
        assert rule_type == "xpath"

    def test_xpath_extraction(self, sample_html):
        """Test XPath extraction works with HTML."""
        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "//h1[@class='name']",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(sample_html, site_config)

        # Should extract using XPath
        assert "name" in result.priority_fields


class TestRegexRuleExtraction:
    """Test regex pattern extraction support."""

    def test_regex_rule_detection(self):
        """Test regex rules are detected."""
        rule_type, pattern = RuleParser.parse_rule("/[A-Z][a-z]+/")
        assert rule_type == "regex"

    def test_regex_pattern_extraction(self, sample_html):
        """Test regex pattern extraction from HTML."""
        # Create HTML with email pattern
        html_with_email = sample_html.replace(
            "contact@example-fablab.com", "contact@example-fablab.com"
        )

        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "contact": "/[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}/",
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(html_with_email, site_config)

        # Should extract email from text content
        assert "contact" in result.priority_fields


class TestRuleTypeVariations:
    """Test extraction engine handles different rule types correctly."""

    def test_mixed_rule_types_in_config(self, sample_html):
        """Test config can use different rule types for different fields."""
        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",  # CSS selector
                "location": "//span[@class='location']",  # XPath
            },
            extra_fields={
                "operating_hours": "div.hours",  # CSS selector
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(sample_html, site_config)

        # Both CSS and XPath rules should extract successfully
        assert "name" in result.priority_fields
        assert "location" in result.priority_fields
        assert "operating_hours" in result.extra_metadata

    def test_fallback_on_rule_failure(self, sample_html):
        """Test extraction continues if one rule type fails."""
        site_config = SiteConfig(
            id="test",
            url_pattern="test.com",
            site_type="fablab",
            priority_fields={
                "name": "h1.name",  # Works
                "location": "//nonexistent",  # Invalid XPath
                "expertise": "div.expertise",  # Works
            },
        )

        engine = ExtractionEngine()
        result = engine.extract_fields(sample_html, site_config)

        # Should extract working fields
        assert "name" in result.priority_fields
        assert "expertise" in result.priority_fields
        # Failed field should be tracked
        assert (
            "location" in result.fields_status.failed
            or "location" in result.fields_status.not_found
        )


class TestRuleParserEdgeCases:
    """Test RuleParser handles edge cases gracefully."""

    def test_empty_rule_string(self):
        """Test empty rule string."""
        rule_type, pattern = RuleParser.parse_rule("")
        assert rule_type == "unknown"

    def test_none_rule(self):
        """Test None rule value."""
        rule_type, pattern = RuleParser.parse_rule(None)
        assert rule_type == "unknown"

    def test_rule_with_spaces(self):
        """Test rule with multiple spaces is normalized."""
        rule_type, pattern = RuleParser.parse_rule("  div.class  span  ")
        assert rule_type == "css"
        assert pattern == "div.class  span"
