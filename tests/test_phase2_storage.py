"""Tests for results storage and archival."""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from scraper_admin.result_archiver import ResultArchiver


class TestResultArchiver:
    """Test results archiver."""

    def test_organize_output_path(self, temp_dir):
        """Test organizing output path by date."""
        archiver = ResultArchiver(str(temp_dir / "output"))

        path = archiver.organize_output_path("example", "2026-01-04T10:30:00+00:00")

        # Should be: output/2026-01-04/example_20260104_103000.toml
        assert "2026-01-04" in str(path)
        assert path.suffix == ".toml"

    def test_archive_result(self, temp_dir):
        """Test archiving a result."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))

        result_dict = {
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

        toml_content = "[result]\nname = 'Example'\nlocation = 'Test'"
        output_path, result_id = archiver.archive_result(
            "https://example.com",
            toml_content,
            result_dict,
        )

        assert Path(output_path).exists()
        assert result_id > 0

    def test_get_results_for_site(self, temp_dir):
        """Test getting results for a site."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))

        result_dict = {
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

        archiver.archive_result(
            "https://example.com",
            "[result]\nname = 'Test'",
            result_dict,
        )

        results = archiver.get_results_for_site("https://example.com")
        assert len(results) == 1

    def test_get_latest_result(self, temp_dir):
        """Test getting the latest result for a site."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))

        result_dict = {
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

        archiver.archive_result(
            "https://example.com",
            "[result]\nname = 'Test'",
            result_dict,
        )

        result = archiver.get_latest_result("https://example.com")
        assert result is not None
        assert result["url"] == "https://example.com"

    def test_get_success_rate(self, temp_dir):
        """Test calculating success rate."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))

        # Archive successful result
        result_dict_success = {
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

        archiver.archive_result(
            "https://example.com",
            "[result]\nname = 'Test'",
            result_dict_success,
        )

        # Archive failed result
        result_dict_failed = {
            "success": False,
            "metadata": {
                "extraction_metadata": {
                    "success": False,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.5,
                },
                "fields_status": {
                    "extracted": [],
                    "failed": ["name"],
                    "not_found": [],
                },
            },
        }

        archiver.archive_result(
            "https://example.com",
            "[result]\n",
            result_dict_failed,
        )

        rate = archiver.get_success_rate("https://example.com", days=30)
        assert 0 <= rate <= 100

    def test_get_field_status_for_result(self, temp_dir):
        """Test getting field status for a result."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))

        result_dict = {
            "success": True,
            "metadata": {
                "extraction_metadata": {
                    "success": True,
                    "site_type": "fablab",
                    "extraction_duration_seconds": 2.5,
                },
                "fields_status": {
                    "extracted": ["name", "location"],
                    "failed": ["phone"],
                    "not_found": ["hours"],
                },
            },
        }

        _, result_id = archiver.archive_result(
            "https://example.com",
            "[result]\nname = 'Test'",
            result_dict,
        )

        fields = archiver.get_field_status_for_result(result_id)
        assert "name" in fields["extracted"]
        assert "phone" in fields["failed"]
        assert "hours" in fields["not_found"]

    def test_get_results_by_date(self, temp_dir):
        """Test getting results by date."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))

        result_dict = {
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

        archiver.archive_result(
            "https://example.com",
            "[result]\nname = 'Test'",
            result_dict,
        )

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        results = archiver.get_results_by_date(today)
        assert len(results) >= 1

    def test_archive_multiple_results(self, temp_dir):
        """Test archiving multiple results."""
        archiver = ResultArchiver(str(temp_dir / "output"), str(temp_dir / "archive.db"))

        result_dict = {
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

        for i in range(3):
            archiver.archive_result(
                "https://example.com",
                f"[result]\nname = 'Test{i}'",
                result_dict,
            )

        results = archiver.get_results_for_site("https://example.com", days=30)
        assert len(results) == 3
