"""Results archiving and storage manager."""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
import sqlite3

from scraper_admin.db import DatabaseManager

logger = logging.getLogger(__name__)


class ResultArchiver:
    """Manages results storage and archival."""

    def __init__(
        self,
        output_dir: str = "output",
        db_path: str = "data/archive.db",
    ):
        """Initialize results archiver.

        Args:
            output_dir: Directory for TOML output files.
            db_path: Path to SQLite database.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.init_results_tables()

    def organize_output_path(self, domain: str, timestamp: Optional[str] = None) -> Path:
        """Get organized output path for a result.

        Creates: output/YYYY-MM-DD/domain_timestamp.toml

        Args:
            domain: Site domain name.
            timestamp: Optional timestamp string (ISO format).

        Returns:
            Path object for output file.
        """
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()

        # Parse timestamp
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d")

        # Create date directory
        date_dir = self.output_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Create filename: domain_timestamp.toml
        # Use first 10 chars of domain and compact timestamp
        domain_short = domain.replace(".", "").replace("-", "")[:10]
        time_compact = dt.strftime("%Y%m%d_%H%M%S")
        filename = f"{domain_short}_{time_compact}.toml"

        return date_dir / filename

    def archive_result(
        self,
        url: str,
        toml_content: str,
        result_dict: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> tuple[str, int]:
        """Archive a scrape result.

        Saves TOML file and metadata to database.

        Args:
            url: Site URL that was scraped.
            toml_content: TOML output content.
            result_dict: Result dictionary from scrape_facility.
            output_path: Optional custom output path.

        Returns:
            Tuple of (output_file_path, result_id).
        """
        from urllib.parse import urlparse

        # Extract domain
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")

        # Generate output path if not provided
        if not output_path:
            output_path = str(self.organize_output_path(domain))

        # Write TOML file
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(toml_content)
            logger.info(f"Result saved to {output_path}")
        except IOError as e:
            logger.error(f"Error writing result file: {e}")
            raise

        # Extract metadata
        metadata = result_dict.get("metadata", {})
        extraction_meta = metadata.get("extraction_metadata", {})
        fields_status = metadata.get("fields_status", {})

        success = result_dict.get("success", False)
        duration = extraction_meta.get("extraction_duration_seconds", 0)
        site_type = extraction_meta.get("site_type", "unknown")
        extracted_count = len(fields_status.get("extracted", []))
        failed_count = len(fields_status.get("failed", []))
        not_found_count = len(fields_status.get("not_found", []))

        # Archive to database
        result_id = self._archive_to_db(
            url=url,
            success=success,
            duration=duration,
            site_type=site_type,
            extracted_count=extracted_count,
            failed_count=failed_count,
            not_found_count=not_found_count,
            result_file=output_path,
            fields_status=fields_status,
        )

        logger.info(f"Result archived with ID {result_id}")
        return output_path, result_id

    def _archive_to_db(
        self,
        url: str,
        success: bool,
        duration: float,
        site_type: str,
        extracted_count: int,
        failed_count: int,
        not_found_count: int,
        result_file: str,
        fields_status: Dict[str, List[str]],
    ) -> int:
        """Archive result metadata to SQLite database.

        Args:
            url: Site URL.
            success: Whether scraping was successful.
            duration: Extraction duration in seconds.
            site_type: Type of site.
            extracted_count: Number of extracted fields.
            failed_count: Number of failed fields.
            not_found_count: Number of not found fields.
            result_file: Path to result file.
            fields_status: Dictionary with extracted, failed, not_found lists.

        Returns:
            Result ID in database.
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            # Insert result
            run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO results
                (url, run_date, success, duration, site_type, extracted_count, failed_count, not_found_count, result_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                url,
                run_date,
                1 if success else 0,
                duration,
                site_type,
                extracted_count,
                failed_count,
                not_found_count,
                result_file,
            ))

            result_id = cursor.lastrowid

            # Insert field statuses
            for field_name in fields_status.get("extracted", []):
                cursor.execute("""
                    INSERT INTO result_fields (result_id, field_name, status)
                    VALUES (?, ?, ?)
                """, (result_id, field_name, "extracted"))

            for field_name in fields_status.get("failed", []):
                cursor.execute("""
                    INSERT INTO result_fields (result_id, field_name, status)
                    VALUES (?, ?, ?)
                """, (result_id, field_name, "failed"))

            for field_name in fields_status.get("not_found", []):
                cursor.execute("""
                    INSERT INTO result_fields (result_id, field_name, status)
                    VALUES (?, ?, ?)
                """, (result_id, field_name, "not_found"))

            conn.commit()
            return result_id

        except sqlite3.Error as e:
            logger.error(f"Error archiving result to database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_results_for_site(
        self,
        url: str,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get results for a site from the last N days.

        Args:
            url: Site URL.
            days: Number of days to look back.

        Returns:
            List of result dictionaries.
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

            cursor.execute("""
                SELECT * FROM results
                WHERE url = ? AND run_date >= ?
                ORDER BY run_date DESC, id DESC
            """, (url, cutoff_date))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        finally:
            conn.close()

    def get_results_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get all results for a specific date.

        Args:
            date: Date in YYYY-MM-DD format.

        Returns:
            List of result dictionaries.
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM results
                WHERE run_date = ?
                ORDER BY url, id DESC
            """, (date,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        finally:
            conn.close()

    def get_latest_result(self, url: str) -> Optional[Dict[str, Any]]:
        """Get the most recent result for a site.

        Args:
            url: Site URL.

        Returns:
            Result dictionary or None if no results.
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM results
                WHERE url = ?
                ORDER BY run_date DESC, id DESC
                LIMIT 1
            """, (url,))

            row = cursor.fetchone()
            return dict(row) if row else None

        finally:
            conn.close()

    def get_success_rate(self, url: str, days: int = 30) -> float:
        """Get success rate for a site over N days.

        Args:
            url: Site URL.
            days: Number of days to analyze.

        Returns:
            Success rate as percentage (0-100).
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

            # Get total runs
            cursor.execute("""
                SELECT COUNT(*) as count FROM results
                WHERE url = ? AND run_date >= ?
            """, (url, cutoff_date))

            total = cursor.fetchone()["count"]

            if total == 0:
                return 0.0

            # Get successful runs
            cursor.execute("""
                SELECT COUNT(*) as count FROM results
                WHERE url = ? AND run_date >= ? AND success = 1
            """, (url, cutoff_date))

            successful = cursor.fetchone()["count"]

            return (successful / total) * 100

        finally:
            conn.close()

    def get_field_status_for_result(self, result_id: int) -> Dict[str, List[str]]:
        """Get field statuses for a specific result.

        Args:
            result_id: Result ID.

        Returns:
            Dictionary with extracted, failed, not_found lists.
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT field_name, status FROM result_fields
                WHERE result_id = ?
            """, (result_id,))

            rows = cursor.fetchall()

            fields_status = {
                "extracted": [],
                "failed": [],
                "not_found": [],
            }

            for row in rows:
                status = row["status"]
                field_name = row["field_name"]
                if status in fields_status:
                    fields_status[status].append(field_name)

            return fields_status

        finally:
            conn.close()
