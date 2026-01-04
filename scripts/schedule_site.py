#!/usr/bin/env python3
"""Schedule a site for periodic scraping."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper_admin.registry_manager import RegistryManager
from scraper_admin.schedule_manager import ScheduleManager


def main():
    """Schedule a site for periodic scraping."""
    if len(sys.argv) < 2:
        print("Usage: python schedule_site.py <site_id> [frequency] [time_of_day]")
        print("  frequency: daily, weekly, monthly (default: daily)")
        print("  time_of_day: HH:MM format (default: 09:00)")
        sys.exit(1)

    site_id = sys.argv[1]
    frequency = sys.argv[2] if len(sys.argv) > 2 else "daily"
    time_of_day = sys.argv[3] if len(sys.argv) > 3 else "09:00"

    # Validate site exists
    registry = RegistryManager()
    site = registry.get_site(site_id)

    if not site:
        print(f"ERROR: Site '{site_id}' not found")
        sys.exit(1)

    # Schedule site
    scheduler = ScheduleManager()

    try:
        schedule = scheduler.schedule_site(site_id, frequency, time_of_day)
        print(f"✓ Site '{site_id}' scheduled successfully")
        print(f"  Frequency: {frequency}")
        print(f"  Time of day: {time_of_day}")
        print(f"  Next run: {schedule.next_run}")
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
