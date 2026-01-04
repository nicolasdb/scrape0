"""Change detection engine for scrape result comparison."""

import logging
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from datetime import datetime, timezone
import sqlite3

from scraper_admin.result_archiver import ResultArchiver
from scraper_admin.db import DatabaseManager

logger = logging.getLogger(__name__)


class ChangeDetector:
    """Detects and reports changes between scrape results."""

    def __init__(self, db_path: str = "data/archive.db"):
        """Initialize change detector.

        Args:
            db_path: Path to SQLite database.
        """
        self.archiver = ResultArchiver(db_path=db_path)
        self.db_manager = DatabaseManager(db_path)

    def compare_runs(
        self,
        url: str,
        date1: str,
        date2: str,
    ) -> Dict[str, Any]:
        """Compare scrape results between two dates.

        Args:
            url: Site URL.
            date1: Earlier date (YYYY-MM-DD).
            date2: Later date (YYYY-MM-DD).

        Returns:
            Dictionary with comparison results.
        """
        # Get results for both dates
        results1 = self.archiver.get_results_by_date(date1)
        results2 = self.archiver.get_results_by_date(date2)

        # Find matching results for this URL
        result1 = None
        result2 = None

        for r in results1:
            if r["url"] == url:
                result1 = r
                break

        for r in results2:
            if r["url"] == url:
                result2 = r
                break

        if not result1:
            return {"error": f"No result found for {url} on {date1}"}
        if not result2:
            return {"error": f"No result found for {url} on {date2}"}

        # Get field statuses
        fields1 = self.archiver.get_field_status_for_result(result1["id"])
        fields2 = self.archiver.get_field_status_for_result(result2["id"])

        # Perform comparison
        return {
            "url": url,
            "date1": date1,
            "date2": date2,
            "result1_id": result1["id"],
            "result2_id": result2["id"],
            "comparison": self._compare_field_sets(fields1, fields2),
            "metadata_changes": self._compare_metadata(result1, result2),
        }

    def _compare_field_sets(
        self,
        fields1: Dict[str, List[str]],
        fields2: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Compare field sets between two results.

        Args:
            fields1: Earlier field status.
            fields2: Later field status.

        Returns:
            Dictionary with changes.
        """
        extracted1 = set(fields1.get("extracted", []))
        extracted2 = set(fields2.get("extracted", []))
        failed1 = set(fields1.get("failed", []))
        failed2 = set(fields2.get("failed", []))

        return {
            "new_fields": list(extracted2 - extracted1),  # Now extracted
            "lost_fields": list(extracted1 - extracted2),  # No longer extracted
            "newly_failed": list(failed2 - failed1),  # Now failing
            "newly_working": list(failed1 - failed2),  # Now working
            "unchanged": list(extracted1 & extracted2),  # Always extracted
        }

    def _compare_metadata(
        self,
        result1: Dict[str, Any],
        result2: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compare metadata between two results.

        Args:
            result1: Earlier result.
            result2: Later result.

        Returns:
            Dictionary with metadata changes.
        """
        return {
            "success_changed": (result1["success"] != result2["success"]),
            "success_before": bool(result1["success"]),
            "success_after": bool(result2["success"]),
            "duration_before": result1["duration"],
            "duration_after": result2["duration"],
            "extracted_count_before": result1["extracted_count"],
            "extracted_count_after": result2["extracted_count"],
            "failed_count_before": result1["failed_count"],
            "failed_count_after": result2["failed_count"],
        }

    def detect_changes(
        self,
        url: str,
        date1: str,
        date2: str,
    ) -> List[Dict[str, str]]:
        """Detect specific changes between two dates.

        Args:
            url: Site URL.
            date1: Earlier date (YYYY-MM-DD).
            date2: Later date (YYYY-MM-DD).

        Returns:
            List of change dictionaries with type and description.
        """
        comparison = self.compare_runs(url, date1, date2)

        if "error" in comparison:
            return [comparison]

        changes = []
        comp = comparison["comparison"]
        meta = comparison["metadata_changes"]

        # Field extraction improvements
        if comp["new_fields"]:
            changes.append({
                "type": "extraction_improved",
                "severity": "info",
                "description": f"New fields extracted: {', '.join(comp['new_fields'])}",
            })

        # Field extraction regressions
        if comp["lost_fields"]:
            changes.append({
                "type": "extraction_regression",
                "severity": "warning",
                "description": f"Fields no longer extracted: {', '.join(comp['lost_fields'])}",
            })

        # Selectors failing
        if comp["newly_failed"]:
            changes.append({
                "type": "selector_failure",
                "severity": "error",
                "description": f"Selectors now failing: {', '.join(comp['newly_failed'])}",
            })

        # Selectors recovering
        if comp["newly_working"]:
            changes.append({
                "type": "selector_recovery",
                "severity": "info",
                "description": f"Previously failing selectors now working: {', '.join(comp['newly_working'])}",
            })

        # Success rate changes
        if meta["success_changed"]:
            if meta["success_after"] and not meta["success_before"]:
                changes.append({
                    "type": "success_recovered",
                    "severity": "info",
                    "description": "Scraping went from failed to successful",
                })
            elif not meta["success_after"] and meta["success_before"]:
                changes.append({
                    "type": "success_failure",
                    "severity": "error",
                    "description": "Scraping went from successful to failed",
                })

        # Extraction count significant changes
        count_change = meta["extracted_count_after"] - meta["extracted_count_before"]
        if abs(count_change) > 0:
            if count_change > 0:
                changes.append({
                    "type": "extraction_increase",
                    "severity": "info",
                    "description": f"Extracted field count increased by {count_change}",
                })
            else:
                changes.append({
                    "type": "extraction_decrease",
                    "severity": "warning",
                    "description": f"Extracted field count decreased by {abs(count_change)}",
                })

        return changes if changes else [{
            "type": "no_changes",
            "severity": "info",
            "description": "No significant changes detected",
        }]

    def generate_diff_report(
        self,
        url: str,
        date1: str,
        date2: str,
    ) -> str:
        """Generate a human-readable diff report.

        Args:
            url: Site URL.
            date1: Earlier date (YYYY-MM-DD).
            date2: Later date (YYYY-MM-DD).

        Returns:
            Formatted report as string.
        """
        changes = self.detect_changes(url, date1, date2)
        comparison = self.compare_runs(url, date1, date2)

        if "error" in comparison:
            return f"Error: {comparison['error']}"

        report = []
        report.append("=" * 70)
        report.append(f"CHANGE DETECTION REPORT")
        report.append("=" * 70)
        report.append("")
        report.append(f"Site: {url}")
        report.append(f"Period: {date1} -> {date2}")
        report.append("")

        # Summary of changes
        report.append("DETECTED CHANGES:")
        report.append("-" * 70)

        if len(changes) == 1 and changes[0]["type"] == "no_changes":
            report.append("  No significant changes detected")
        else:
            for change in changes:
                severity_mark = {
                    "info": "ℹ",
                    "warning": "⚠",
                    "error": "✗",
                }.get(change.get("severity", "info"), "-")

                report.append(f"  {severity_mark} [{change['type']}] {change['description']}")

        report.append("")
        report.append("FIELD COMPARISON:")
        report.append("-" * 70)

        comp = comparison["comparison"]

        if comp["new_fields"]:
            report.append(f"  NEW (now extracted): {', '.join(comp['new_fields'])}")
        if comp["lost_fields"]:
            report.append(f"  LOST (no longer extracted): {', '.join(comp['lost_fields'])}")
        if comp["newly_failed"]:
            report.append(f"  FAILED: {', '.join(comp['newly_failed'])}")
        if comp["newly_working"]:
            report.append(f"  RECOVERED: {', '.join(comp['newly_working'])}")

        if not any([comp["new_fields"], comp["lost_fields"], comp["newly_failed"], comp["newly_working"]]):
            report.append("  No field-level changes")

        report.append("")
        report.append("METADATA COMPARISON:")
        report.append("-" * 70)

        meta = comparison["metadata_changes"]
        report.append(f"  Success: {meta['success_before']} -> {meta['success_after']}")
        report.append(f"  Extracted count: {meta['extracted_count_before']} -> {meta['extracted_count_after']}")
        report.append(f"  Failed count: {meta['failed_count_before']} -> {meta['failed_count_after']}")
        report.append(f"  Duration: {meta['duration_before']:.2f}s -> {meta['duration_after']:.2f}s")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)

    def create_change_alert(
        self,
        url: str,
        alert_type: str,
        message: str,
    ) -> None:
        """Create an alert for important changes.

        Args:
            url: Site URL.
            alert_type: Type of alert (extraction_failure, selector_broken, etc.).
            message: Alert message.
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO alerts (url, alert_type, message, detection_date)
                VALUES (?, ?, ?, ?)
            """, (url, alert_type, message, now))

            conn.commit()
            logger.info(f"Created alert: {alert_type} for {url}")

        except sqlite3.Error as e:
            logger.error(f"Error creating alert: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_unacknowledged_alerts(self, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get unacknowledged alerts.

        Args:
            url: Optional URL to filter by.

        Returns:
            List of alert dictionaries.
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            if url:
                cursor.execute("""
                    SELECT * FROM alerts
                    WHERE url = ? AND acknowledged = 0
                    ORDER BY detection_date DESC
                """, (url,))
            else:
                cursor.execute("""
                    SELECT * FROM alerts
                    WHERE acknowledged = 0
                    ORDER BY detection_date DESC
                """)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        finally:
            conn.close()

    def acknowledge_alert(self, alert_id: int) -> None:
        """Mark an alert as acknowledged.

        Args:
            alert_id: Alert ID.
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE alerts SET acknowledged = 1 WHERE id = ?
            """, (alert_id,))

            conn.commit()
            logger.info(f"Acknowledged alert {alert_id}")

        except sqlite3.Error as e:
            logger.error(f"Error acknowledging alert: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
