#!/usr/bin/env python3
"""View scrape results for a site."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper_admin.result_archiver import ResultArchiver


def main():
    """View results for a site."""
    if len(sys.argv) < 2:
        print("Usage: python view_results.py <url> [days]")
        print("  url: Site URL or domain to view results for")
        print("  days: Number of days to look back (default: 30)")
        sys.exit(1)

    url = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    # Normalize URL
    if not url.startswith("http"):
        url = "https://" + url

    archiver = ResultArchiver()

    # Get results
    results = archiver.get_results_for_site(url, days)

    if not results:
        print(f"No results found for {url} in the last {days} days")
        return

    print("\n" + "=" * 80)
    print(f"RESULTS FOR {url}")
    print(f"Last {days} days")
    print("=" * 80)

    for result in results:
        status = "✓ Success" if result["success"] else "✗ Failed"
        print(f"\n{result['run_date']} - {status}")
        print(f"  Duration: {result['duration']:.2f}s")
        print(f"  Type: {result['site_type']}")
        print(f"  Extracted: {result['extracted_count']}, Failed: {result['failed_count']}, Not found: {result['not_found_count']}")

        # Get field status
        fields = archiver.get_field_status_for_result(result["id"])
        if fields["extracted"]:
            print(f"  Fields: {', '.join(fields['extracted'][:5])}")
            if len(fields["extracted"]) > 5:
                print(f"          ... and {len(fields['extracted']) - 5} more")

    # Summary
    success_rate = archiver.get_success_rate(url, days)
    print("\n" + "=" * 80)
    print(f"Summary: {len(results)} results, {success_rate:.1f}% success rate")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
