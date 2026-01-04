"""Public API for the scraping module."""

import logging
import time
from typing import Any, Dict, Optional

from scraper.config import ConfigManager, ConfigurationError
from scraper.input import InputLayer
from scraper.scraper_engine import ScrapingEngine
from scraper.extraction import ExtractionEngine
from scraper.output import TOMLOutputFormatter
from scraper.file_output import FileOutput
from scraper.models import ExtractionResult, ExtractionMetadata
from scraper.validators import URLValidationError
from scraper.errors import NetworkError, NetworkTimeout, ParsingError

logger = logging.getLogger(__name__)


def scrape_facility(
    url: str,
    config_path: str = "./config.toml",
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Scrape a single facility from the given URL.

    This is the main entry point for the scraping module. It orchestrates
    the complete pipeline: configuration loading, URL validation, HTML
    fetching, field extraction, TOML formatting, and file output.

    Args:
        url: Target URL to scrape (will be normalized to https://)
        config_path: Path to scraper configuration file (default: ./config.toml)
        output_path: Optional path to write TOML output file

    Returns:
        Dictionary with keys:
        - success (bool): Whether scraping succeeded (True if any fields extracted)
        - data (dict): Extracted data with 'priority_fields' and 'extra_metadata' keys
        - metadata (dict): Extraction metadata and field status info
        - error (str or None): Critical error message if applicable (only on critical failures)

    Example:
        ```python
        result = scrape_facility(
            url="https://example-fablab.com",
            config_path="./config.toml",
            output_path="./output/example.toml"
        )

        if result['success']:
            print(f"Extracted: {result['data']['priority_fields']}")
        else:
            reason = result['metadata']['extraction_metadata'].get('failure_reason')
            print(f"Partial extraction: {reason}")
        ```

    Error Handling:
        Critical errors (config not found, invalid URL) return with error field populated.
        Partial failures (timeout, parsing errors) return success=False with extracted data.
        Field-level failures are tracked in fields_status without halting extraction.
    """
    start_time = time.time()

    # Initialize result structure
    result: Dict[str, Any] = {
        "success": False,
        "data": {"priority_fields": {}, "extra_metadata": {}},
        "metadata": {},
        "error": None,
    }

    try:
        # Phase 1: Load configuration
        logger.info(f"Loading configuration from {config_path}")
        config_manager = ConfigManager()
        scraper_config = config_manager.load_config(config_path)

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        result["error"] = str(e)
        return result

    try:
        # Phase 2: Validate and normalize URL
        logger.info(f"Validating URL: {url}")
        input_layer = InputLayer(config_manager)
        normalized_url = input_layer.validate_and_normalize_url(url)
        logger.info(f"Normalized URL: {normalized_url}")

    except URLValidationError as e:
        logger.error(f"URL validation error: {e}")
        result["error"] = str(e)
        return result

    try:
        # Phase 3: Look up site configuration
        logger.info("Looking up site configuration")
        site_config = input_layer.lookup_site_config(normalized_url)
        logger.info(f"Found config for site: {site_config.id}")

    except ConfigurationError as e:
        logger.error(f"Site configuration lookup failed: {e}")
        result["error"] = str(e)
        return result

    try:
        # Phase 4: Fetch HTML content
        logger.info(f"Fetching content from {normalized_url}")
        scraping_engine = ScrapingEngine(scraper_config)
        html_content = scraping_engine.fetch_content(normalized_url)
        logger.info("Successfully fetched HTML content")

    except NetworkTimeout as e:
        logger.error(f"Network timeout: {e}")
        result["error"] = str(e)
        return result
    except NetworkError as e:
        logger.error(f"Network error: {e}")
        result["error"] = str(e)
        return result

    try:
        # Phase 5: Extract fields from HTML
        logger.info("Extracting fields from HTML")
        extraction_engine = ExtractionEngine()
        extraction_result = extraction_engine.extract_fields(html_content, site_config)
        logger.info(
            f"Extraction complete: {len(extraction_result.fields_status.extracted)} "
            f"fields extracted"
        )

    except ParsingError as e:
        logger.error(f"HTML parsing error: {e}")
        result["error"] = str(e)
        return result
    except Exception as e:
        logger.error(f"Unexpected extraction error: {e}")
        result["error"] = str(e)
        return result

    # Phase 6: Format output
    try:
        logger.info("Formatting TOML output")
        toml_output = TOMLOutputFormatter.format_result(extraction_result)
        logger.debug(f"TOML output generated ({len(toml_output)} bytes)")

    except Exception as e:
        logger.error(f"Output formatting error: {e}")
        result["error"] = str(e)
        return result

    # Phase 7: Write file if requested
    if output_path:
        try:
            logger.info(f"Writing output to {output_path}")
            FileOutput.write_toml(toml_output, output_path)
            FileOutput.verify_file(output_path)
            logger.info(f"Output file written and verified: {output_path}")

        except IOError as e:
            logger.error(f"File output error: {e}")
            result["error"] = str(e)
            return result

    # Phase 8: Prepare response
    duration = time.time() - start_time
    extraction_result.metadata.extraction_duration_seconds = duration

    result["success"] = extraction_result.success
    result["data"] = {
        "priority_fields": extraction_result.priority_fields,
        "extra_metadata": extraction_result.extra_metadata,
    }
    result["metadata"] = {
        "extraction_metadata": {
            "success": extraction_result.metadata.success,
            "extraction_timestamp": extraction_result.metadata.extraction_timestamp,
            "extraction_duration_seconds": extraction_result.metadata.extraction_duration_seconds,
            "failure_reason": extraction_result.metadata.failure_reason,
            "site_type": extraction_result.metadata.site_type,
        },
        "fields_status": {
            "extracted": extraction_result.fields_status.extracted,
            "failed": extraction_result.fields_status.failed,
            "not_found": extraction_result.fields_status.not_found,
        },
    }

    logger.info(f"Scraping complete (success={result['success']}, duration={duration:.2f}s)")
    return result
