"""TOML output formatting for extraction results."""

import logging
from typing import Any, Dict

try:
    import tomli_w as toml_writer
except ImportError:
    try:
        import toml as toml_writer
    except ImportError:
        toml_writer = None

from scraper.models import ExtractionResult

logger = logging.getLogger(__name__)


class TOMLOutputFormatter:
    """Formats extraction results as valid TOML output."""

    @staticmethod
    def format_result(result: ExtractionResult) -> str:
        """
        Format extraction result as TOML string.

        Args:
            result: ExtractionResult object

        Returns:
            TOML-formatted string

        Raises:
            ValueError: If result contains non-TOML-compatible types
        """
        toml_dict = TOMLOutputFormatter._build_toml_dict(result)

        # Try to use tomli_w first (recommended)
        if toml_writer and hasattr(toml_writer, "dumps"):
            try:
                return toml_writer.dumps(toml_dict)
            except Exception as e:
                logger.warning(f"Failed to use toml_writer: {e}, falling back to manual format")

        # Fallback to manual TOML formatting
        return TOMLOutputFormatter._format_manual(toml_dict)

    @staticmethod
    def _build_toml_dict(result: ExtractionResult) -> Dict[str, Any]:
        """Build dictionary structure for TOML serialization."""
        return {
            "extraction_metadata": {
                "success": result.metadata.success,
                "extraction_timestamp": result.metadata.extraction_timestamp,
                "extraction_duration_seconds": result.metadata.extraction_duration_seconds,
                "failure_reason": result.metadata.failure_reason,
                "site_type": result.metadata.site_type,
            },
            "priority_fields": result.priority_fields,
            "extra_metadata": result.extra_metadata,
            "fields_status": {
                "extracted": result.fields_status.extracted,
                "failed": result.fields_status.failed,
                "not_found": result.fields_status.not_found,
            },
        }

    @staticmethod
    def _format_manual(data: Dict[str, Any]) -> str:
        """Manual TOML formatting as fallback."""
        lines = []

        # Extraction metadata section
        lines.append("[extraction_metadata]")
        metadata = data.get("extraction_metadata", {})
        for key, value in metadata.items():
            lines.append(TOMLOutputFormatter._format_value(key, value))
        lines.append("")

        # Priority fields section
        if data.get("priority_fields"):
            lines.append("[priority_fields]")
            for key, value in data["priority_fields"].items():
                lines.append(TOMLOutputFormatter._format_value(key, value))
            lines.append("")

        # Extra metadata section
        if data.get("extra_metadata"):
            lines.append("[extra_metadata]")
            for key, value in data["extra_metadata"].items():
                lines.append(TOMLOutputFormatter._format_value(key, value))
            lines.append("")

        # Fields status section
        if data.get("fields_status"):
            lines.append("[fields_status]")
            status = data["fields_status"]
            lines.append(
                f"extracted = {TOMLOutputFormatter._format_array(status.get('extracted', []))}"
            )
            lines.append(f"failed = {TOMLOutputFormatter._format_array(status.get('failed', []))}")
            lines.append(
                f"not_found = {TOMLOutputFormatter._format_array(status.get('not_found', []))}"
            )

        return "\n".join(lines)

    @staticmethod
    def _format_value(key: str, value: Any) -> str:
        """Format a single key-value pair for TOML."""
        if value is None:
            return f"{key} = null"
        elif isinstance(value, bool):
            return f'{key} = {"true" if value else "false"}'
        elif isinstance(value, (int, float)):
            return f"{key} = {value}"
        elif isinstance(value, list):
            return f"{key} = {TOMLOutputFormatter._format_array(value)}"
        elif isinstance(value, str):
            # Escape quotes in strings
            escaped = value.replace('"', '\\"')
            return f'{key} = "{escaped}"'
        else:
            # Fallback for unknown types
            return f'{key} = "{str(value)}"'

    @staticmethod
    def _format_array(items: list) -> str:
        """Format a list as TOML array."""
        if not items:
            return "[]"

        # Format each item
        formatted_items = []
        for item in items:
            if isinstance(item, str):
                escaped = item.replace('"', '\\"')
                formatted_items.append(f'"{escaped}"')
            elif isinstance(item, bool):
                formatted_items.append("true" if item else "false")
            elif isinstance(item, (int, float)):
                formatted_items.append(str(item))
            else:
                formatted_items.append(f'"{str(item)}"')

        return "[" + ", ".join(formatted_items) + "]"
