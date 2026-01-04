#!/usr/bin/env python3
"""List registered sites."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper_admin.registry_manager import RegistryManager
from scraper_admin.schedule_manager import ScheduleManager


def main():
    """List all registered sites."""
    registry = RegistryManager()
    scheduler = ScheduleManager()

    sites = registry.list_sites()

    if not sites:
        print("No sites registered yet.")
        return

    print("\n" + "=" * 80)
    print("REGISTERED SITES")
    print("=" * 80)

    for i, site in enumerate(sites, 1):
        status = "Active" if site.active else "Inactive"
        schedule = scheduler.get_schedule(site.id)
        frequency = schedule.frequency.value if schedule else "Not scheduled"

        print(f"\n{i}. {site.id.upper()}")
        print(f"   URL: {site.url}")
        print(f"   Type: {site.site_type.value}")
        print(f"   Description: {site.description}")
        print(f"   Status: {status}")
        print(f"   Frequency: {frequency}")
        print(f"   Created: {site.created_date}")
        if site.last_scraped:
            print(f"   Last Scraped: {site.last_scraped}")

    print("\n" + "=" * 80)
    print(f"Total: {len(sites)} site(s)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
