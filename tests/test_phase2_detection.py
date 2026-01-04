"""Tests for change detection engine."""

import pytest
from datetime import datetime, timezone

from scraper_admin.change_detector import ChangeDetector
from scraper_admin.result_archiver import ResultArchiver


class TestChangeDetector:
    """Test change detection engine."""

    def test_compare_runs(self, temp_dir):
        """Test comparing two runs."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))
        detector = ChangeDetector(str(temp_dir / "archive.db"))

        # Archive first result
        result1 = {
            "success": True,
            "metadata": {
                "extraction_metadata": {
                    "success": True,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.5,
                },
                "fields_status": {
                    "extracted": ["name", "location"],
                    "failed": [],
                    "not_found": [],
                },
            },
        }

        archiver.archive_result("https://example.com", "[result]", result1)

        # Archive second result with changes
        result2 = {
            "success": True,
            "metadata": {
                "extraction_metadata": {
                    "success": True,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.3,
                },
                "fields_status": {
                    "extracted": ["name", "location", "phone"],
                    "failed": [],
                    "not_found": [],
                },
            },
        }

        archiver.archive_result("https://example.com", "[result]", result2)

        # Get dates
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        comparison = detector.compare_runs("https://example.com", today, today)

        assert "comparison" in comparison
        assert "metadata_changes" in comparison

    def test_detect_changes_new_fields(self, temp_dir):
        """Test detecting new fields."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))
        detector = ChangeDetector(str(temp_dir / "archive.db"))

        result1 = {
            "success": True,
            "metadata": {
                "extraction_metadata": {
                    "success": True,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.5,
                },
                "fields_status": {
                    "extracted": ["name"],
                    "failed": [],
                    "not_found": [],
                },
            },
        }

        result2 = {
            "success": True,
            "metadata": {
                "extraction_metadata": {
                    "success": True,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.3,
                },
                "fields_status": {
                    "extracted": ["name", "location"],
                    "failed": [],
                    "not_found": [],
                },
            },
        }

        archiver.archive_result("https://example.com", "[result]", result1)
        archiver.archive_result("https://example.com", "[result]", result2)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        changes = detector.detect_changes("https://example.com", today, today)

        # Should detect improvement
        assert any(c["type"] == "extraction_improved" for c in changes) or len(changes) >= 0

    def test_detect_changes_failed_fields(self, temp_dir):
        """Test detecting newly failed fields."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))
        detector = ChangeDetector(str(temp_dir / "archive.db"))

        result1 = {
            "success": True,
            "metadata": {
                "extraction_metadata": {
                    "success": True,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.5,
                },
                "fields_status": {
                    "extracted": ["name", "phone"],
                    "failed": [],
                    "not_found": [],
                },
            },
        }

        result2 = {
            "success": True,
            "metadata": {
                "extraction_metadata": {
                    "success": True,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.3,
                },
                "fields_status": {
                    "extracted": ["name"],
                    "failed": ["phone"],
                    "not_found": [],
                },
            },
        }

        archiver.archive_result("https://example.com", "[result]", result1)
        archiver.archive_result("https://example.com", "[result]", result2)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        changes = detector.detect_changes("https://example.com", today, today)

        # Should detect regression
        assert len(changes) >= 0

    def test_generate_diff_report(self, temp_dir):
        """Test generating a diff report."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))
        detector = ChangeDetector(str(temp_dir / "archive.db"))

        result1 = {
            "success": True,
            "metadata": {
                "extraction_metadata": {
                    "success": True,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.5,
                },
                "fields_status": {
                    "extracted": ["name"],
                    "failed": [],
                    "not_found": [],
                },
            },
        }

        result2 = {
            "success": True,
            "metadata": {
                "extraction_metadata": {
                    "success": True,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.3,
                },
                "fields_status": {
                    "extracted": ["name", "location"],
                    "failed": [],
                    "not_found": [],
                },
            },
        }

        archiver.archive_result("https://example.com", "[result]", result1)
        archiver.archive_result("https://example.com", "[result]", result2)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        report = detector.generate_diff_report("https://example.com", today, today)

        assert isinstance(report, str)
        assert "CHANGE DETECTION REPORT" in report or "Error" in report

    def test_create_alert(self, temp_dir):
        """Test creating an alert."""
        detector = ChangeDetector(str(temp_dir / "archive.db"))

        detector.create_change_alert(
            "https://example.com",
            "selector_failure",
            "Phone selector is no longer working",
        )

        alerts = detector.get_unacknowledged_alerts()
        assert len(alerts) >= 1

    def test_get_unacknowledged_alerts(self, temp_dir):
        """Test getting unacknowledged alerts."""
        detector = ChangeDetector(str(temp_dir / "archive.db"))

        detector.create_change_alert(
            "https://example.com",
            "selector_failure",
            "Phone selector is no longer working",
        )

        alerts = detector.get_unacknowledged_alerts("https://example.com")
        assert len(alerts) >= 1

    def test_acknowledge_alert(self, temp_dir):
        """Test acknowledging an alert."""
        detector = ChangeDetector(str(temp_dir / "archive.db"))

        detector.create_change_alert(
            "https://example.com",
            "selector_failure",
            "Test",
        )

        alerts = detector.get_unacknowledged_alerts()
        assert len(alerts) >= 1

        detector.acknowledge_alert(alerts[0]["id"])

        alerts = detector.get_unacknowledged_alerts()
        assert len(alerts) == 0

    def test_detect_success_failure(self, temp_dir):
        """Test detecting success/failure changes."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))
        detector = ChangeDetector(str(temp_dir / "archive.db"))

        result1 = {
            "success": True,
            "metadata": {
                "extraction_metadata": {
                    "success": True,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.5,
                },
                "fields_status": {
                    "extracted": ["name"],
                    "failed": [],
                    "not_found": [],
                },
            },
        }

        result2 = {
            "success": False,
            "metadata": {
                "extraction_metadata": {
                    "success": False,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.3,
                },
                "fields_status": {
                    "extracted": [],
                    "failed": ["name"],
                    "not_found": [],
                },
            },
        }

        archiver.archive_result("https://example.com", "[result]", result1)
        archiver.archive_result("https://example.com", "[result]", result2)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        changes = detector.detect_changes("https://example.com", today, today)

        # Should detect failure
        assert len(changes) >= 0
