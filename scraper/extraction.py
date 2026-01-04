"""Data extraction engine for field extraction from HTML."""

import logging
import re
from typing import Any, Dict, Optional
from bs4 import BeautifulSoup

from scraper.models import SiteConfig, ExtractionMetadata, FieldStatus, ExtractionResult
from scraper.types import TypeConverter
from scraper.errors import ParsingError, ExtractionError

logger = logging.getLogger(__name__)


class RuleParser:
    """Parses extraction rules to determine their type."""

    @staticmethod
    def parse_rule(rule: str) -> tuple[str, str]:
        """
        Determine rule type and extract the pattern.

        Args:
            rule: Rule string (CSS selector, XPath, or regex)

        Returns:
            Tuple of (rule_type, pattern)
        """
        if not rule or not isinstance(rule, str):
            return ("unknown", str(rule))

        # XPath rules start with //
        if rule.strip().startswith("//"):
            return ("xpath", rule.strip())

        # Regex rules enclosed in /.../ or start with ^
        if (rule.strip().startswith("/") and rule.strip().endswith("/")) or rule.strip().startswith(
            "^"
        ):
            return ("regex", rule.strip())

        # Default to CSS selector
        return ("css", rule.strip())


class ExtractionEngine:
    """
    Extracts field data from HTML content using configuration rules.

    Handles field-level errors gracefully without halting extraction.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize extraction engine.

        Args:
            config: Optional configuration dict (for future extensibility)
        """
        self._config = config or {}

    def extract_fields(self, html_content: str, site_config: SiteConfig) -> ExtractionResult:
        """
        Extract all fields from HTML using site configuration rules.

        Args:
            html_content: Raw HTML content
            site_config: Site configuration with extraction rules

        Returns:
            ExtractionResult with extracted data and field status

        Raises:
            ParsingError: If HTML parsing fails
        """
        # Parse HTML
        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception as e:
            logger.error(f"HTML parsing error: {e}")
            raise ParsingError(f"Failed to parse HTML content: {e}") from e

        # Initialize result structures
        priority_fields: Dict[str, Any] = {}
        extra_metadata: Dict[str, Any] = {}
        field_status = FieldStatus()
        metadata = ExtractionMetadata.now(success=False, site_type=site_config.site_type)

        # Extract priority fields
        for field_name, rule in site_config.priority_fields.items():
            try:
                value = self._extract_single_field(soup, rule)
                if value is not None and value.strip():
                    # Convert type
                    converted = TypeConverter.infer_and_convert(value)
                    priority_fields[field_name] = converted
                    field_status.extracted.append(field_name)
                    logger.debug(f"Extracted '{field_name}': {converted}")
                else:
                    field_status.not_found.append(field_name)
                    logger.debug(f"Field '{field_name}' not found in content")
            except Exception as e:
                logger.warning(f"Error extracting '{field_name}': {e}")
                field_status.failed.append(field_name)

        # Extract extra fields
        for field_name, rule in site_config.extra_fields.items():
            try:
                value = self._extract_single_field(soup, rule)
                if value is not None and value.strip():
                    converted = TypeConverter.infer_and_convert(value)
                    extra_metadata[field_name] = converted
                    field_status.extracted.append(field_name)
                    logger.debug(f"Extracted extra '{field_name}': {converted}")
                else:
                    field_status.not_found.append(field_name)
            except Exception as e:
                logger.warning(f"Error extracting extra '{field_name}': {e}")
                field_status.failed.append(field_name)

        # Determine overall success
        # Success if at least some priority fields extracted
        success = len(field_status.extracted) > 0
        metadata.success = success
        if not success:
            metadata.failure_reason = "no_fields_extracted"

        return ExtractionResult(
            success=success,
            priority_fields=priority_fields,
            extra_metadata=extra_metadata,
            metadata=metadata,
            fields_status=field_status,
            error=None,
        )

    def _extract_single_field(self, soup: BeautifulSoup, rule: str) -> Optional[str]:
        """
        Extract a single field from HTML using a rule.

        Args:
            soup: BeautifulSoup object
            rule: Extraction rule (CSS selector, XPath, or regex)

        Returns:
            Extracted value as string, or None if not found

        Raises:
            ExtractionError: If extraction fails
        """
        if not rule or not isinstance(rule, str):
            return None

        rule_type, pattern = RuleParser.parse_rule(rule)

        if rule_type == "css":
            return self._extract_css(soup, pattern)
        elif rule_type == "xpath":
            return self._extract_xpath(soup, pattern)
        elif rule_type == "regex":
            return self._extract_regex(soup, pattern)
        else:
            return None

    def _extract_css(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Extract value using CSS selector."""
        try:
            elements = soup.select(selector)
            if not elements:
                return None

            # Join text from all matching elements
            texts = [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]
            if not texts:
                return None

            # Return single value or comma-separated list
            return ", ".join(texts) if len(texts) > 1 else texts[0]
        except Exception as e:
            logger.debug(f"CSS selector error: {e}")
            raise ExtractionError(f"CSS selector error: {e}") from e

    def _extract_xpath(self, soup: BeautifulSoup, xpath: str) -> Optional[str]:
        """Extract value using XPath (basic implementation)."""
        # Note: Full XPath support requires lxml
        # For now, provide basic support
        try:
            from lxml import html as lxml_html

            tree = lxml_html.fromstring(str(soup))
            results = tree.xpath(xpath)
            if not results:
                return None

            # Extract text from results
            if isinstance(results[0], str):
                return results[0]
            elif hasattr(results[0], "text_content"):
                return results[0].text_content()
            else:
                return str(results[0])
        except ImportError:
            logger.warning("lxml not available for XPath extraction, using mock")
            return None
        except Exception as e:
            logger.debug(f"XPath extraction error: {e}")
            raise ExtractionError(f"XPath error: {e}") from e

    def _extract_regex(self, soup: BeautifulSoup, pattern: str) -> Optional[str]:
        """Extract value using regex pattern."""
        try:
            # Remove delimiters if present
            clean_pattern = pattern.strip("/") if pattern.startswith("/") else pattern.strip()
            html_text = str(soup)
            match = re.search(clean_pattern, html_text, re.IGNORECASE)
            if not match:
                return None
            return match.group(0) if match.groups() else match.group(0)
        except Exception as e:
            logger.debug(f"Regex extraction error: {e}")
            raise ExtractionError(f"Regex error: {e}") from e
