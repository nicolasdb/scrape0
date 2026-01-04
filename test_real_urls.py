#!/usr/bin/env python3
"""
Real-world URL testing script.

This script tests the scraper against actual public websites to verify
the implementation works with real HTML and network requests.

Usage:
    python test_real_urls.py
    python test_real_urls.py example.com
    python test_real_urls.py https://example.com
"""

import sys
import json
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

# Activate venv as per CLAUDE.md
from scraper.api import scrape_facility


def test_real_url(url: str, config_path: str = None, output_dir: str = None):
    """
    Test scraping a real URL.

    Args:
        url: URL to scrape
        config_path: Path to TOML config file
        output_dir: Directory to save output

    Returns:
        Result dict from scrape_facility
    """
    if config_path is None:
        config_path = "./config/real-world.toml"

    if output_dir is None:
        output_dir = "./output"

    # Generate output filename based on domain (max 10 chars)
    domain = urlparse(url).netloc.replace('www.', '')
    domain_short = domain.split('.')[0][:10]  # First part, max 10 chars
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create dated subdirectory
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = f"{output_dir}/{today}/{domain_short}_{timestamp}.toml"

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"Testing URL: {url}")
    print(f"Config: {config_path}")
    print(f"Output: {output_dir}")
    print(f"{'='*70}\n")

    try:
        result = scrape_facility(
            url=url,
            config_path=config_path,
            output_path=output_path
        )

        # Print results
        print("✓ Scraping completed!")
        print(f"  Success: {result['success']}")
        print(f"  Site Type: {result['metadata']['extraction_metadata'].get('site_type', 'unknown')}")

        if result['success']:
            print(f"\n  Extracted Fields:")
            for field, value in result['data']['priority_fields'].items():
                if value:
                    preview = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                    print(f"    - {field}: {preview}")

            if result['data'].get('extra_metadata'):
                print(f"\n  Extra Metadata:")
                for field, value in result['data']['extra_metadata'].items():
                    if value:
                        preview = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                        print(f"    - {field}: {preview}")
        else:
            reason = result['metadata']['extraction_metadata'].get('failure_reason', 'unknown')
            print(f"\n✗ Scraping failed: {reason}")

        # Print field status
        print(f"\n  Field Status:")
        fields_status = result['metadata'].get('fields_status', {})
        if fields_status.get('extracted'):
            print(f"    Extracted: {fields_status['extracted']}")
        if fields_status.get('failed'):
            print(f"    Failed: {fields_status['failed']}")
        if fields_status.get('not_found'):
            print(f"    Not Found: {fields_status['not_found']}")

        # Print output file (use the generated output_path)
        if output_path and Path(output_path).exists():
            print(f"\n  Output file saved to: {output_path}")

            # Try to read and display the TOML output
            try:
                with open(output_path, 'r') as f:
                    toml_content = f.read()
                    print(f"\n  Generated TOML (first 15 lines):")
                    for line in toml_content.split('\n')[:15]:
                        print(f"    {line}")
                    if len(toml_content.split('\n')) > 15:
                        print(f"    ... (see {output_path} for full output)")
            except Exception as e:
                print(f"  Could not read output file: {e}")
        else:
            print(f"\n  Output file: {output_path}")

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main testing function."""

    # Test URLs
    test_urls = [
        "https://example.com",                              # Simple, always available
        "https://en.wikipedia.org/wiki/Python_(programming_language)",  # Wikipedia
    ]

    # Allow passing URL as argument(s)
    # Usage: python test_real_urls.py [url] [config]
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]

    config_path = None
    if len(sys.argv) > 2:
        config_path = sys.argv[2]

    print("\n" + "="*70)
    print("REAL-WORLD URL SCRAPING TEST")
    print("="*70)
    print(f"\nTesting {len(test_urls)} real URL(s)...")

    results = []
    for url in test_urls:
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        result = test_real_url(url, config_path=config_path)
        results.append({
            'url': url,
            'success': result['success'] if result else False,
            'result': result
        })

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    successful = sum(1 for r in results if r['success'])
    print(f"\nTests passed: {successful}/{len(results)}")

    for result in results:
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"  {status}: {result['url']}")

    print(f"\nOutput files saved to: ./output/<YYYY-MM-DD>/")
    print("Structure: ./output/2026-01-04/domain_20260104_091523.toml")
    print("\nTo test additional URLs, run:")
    print("  python test_real_urls.py <url>")
    print("  python test_real_urls.py <url> <config.toml>")
    print("\nExamples:")
    print("  python test_real_urls.py https://openfab.be ./config/openfab.toml")
    print("  python test_real_urls.py example.com ./config/real-world.toml")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
