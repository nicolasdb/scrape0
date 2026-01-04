#!/usr/bin/env python3
"""Detect changes between scrape results."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper_admin.change_detector import ChangeDetector
from scraper_admin.result_archiver import ResultArchiver


def main():
    """Detect changes between results."""
    if len(sys.argv) < 2:
        print("Usage: python detect_changes.py <url> [date1] [date2]")
        print("  url: Site URL or domain")
        print("  date1: Earlier date (YYYY-MM-DD, default: 7 days ago)")
        print("  date2: Later date (YYYY-MM-DD, default: today)")
        sys.exit(1)

    url = sys.argv[1]

    # Normalize URL
    if not url.startswith("http"):
        url = "https://" + url

    # Get dates
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    date1 = sys.argv[2] if len(sys.argv) > 2 else week_ago
    date2 = sys.argv[3] if len(sys.argv) > 3 else today

    # Detect changes
    detector = ChangeDetector()

    # Print report
    report = detector.generate_diff_report(url, date1, date2)
    print("\n" + report + "\n")

    # Create alerts for significant changes
    changes = detector.detect_changes(url, date1, date2)

    for change in changes:
        if change["severity"] == "error":
            detector.create_change_alert(
                url,
                change["type"],
                change["description"]
            )


if __name__ == "__main__":
    main()
