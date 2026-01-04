#!/usr/bin/env python3
"""Interactive CLI for onboarding new sites."""

import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper_admin.registry_manager import RegistryManager
from scraper_admin.template_loader import TemplateLoader
from scraper_admin.config_generator import ConfigGenerator
from scraper import scrape_facility

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def prompt_url() -> str:
    """Prompt for and validate site URL.

    Returns:
        Validated URL.
    """
    while True:
        url = input("\nEnter site URL (e.g., https://example-fablab.com): ").strip()

        if not url:
            print("ERROR: URL cannot be empty")
            continue

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        return url


def prompt_site_type(templates: list) -> str:
    """Prompt for site type selection.

    Args:
        templates: Available template types.

    Returns:
        Selected site type.
    """
    while True:
        print("\nAvailable site types:")
        for i, template in enumerate(templates, 1):
            print(f"  {i}. {template}")
        print(f"  {len(templates) + 1}. other")

        try:
            choice = int(input(f"Select site type (1-{len(templates) + 1}): ").strip())
            if 1 <= choice <= len(templates):
                return templates[choice - 1]
            elif choice == len(templates) + 1:
                return "other"
            else:
                print("ERROR: Invalid choice")
        except ValueError:
            print("ERROR: Please enter a number")


def prompt_frequency() -> str:
    """Prompt for scraping frequency.

    Returns:
        Selected frequency (daily, weekly, monthly).
    """
    frequencies = ["daily", "weekly", "monthly"]
    while True:
        print("\nScraping frequency:")
        for i, freq in enumerate(frequencies, 1):
            print(f"  {i}. {freq}")

        try:
            choice = int(input(f"Select frequency (1-{len(frequencies)}): ").strip())
            if 1 <= choice <= len(frequencies):
                return frequencies[choice - 1]
            else:
                print("ERROR: Invalid choice")
        except ValueError:
            print("ERROR: Please enter a number")


def prompt_description(url: str, site_type: str) -> str:
    """Prompt for site description.

    Args:
        url: Site URL.
        site_type: Site type.

    Returns:
        Description string.
    """
    default = f"{site_type.title()} facility at {url}"
    user_input = input(f"\nEnter description [{default}]: ").strip()
    return user_input if user_input else default


def test_config(url: str, config_path: str) -> tuple[bool, dict]:
    """Test configuration with a dry run.

    Args:
        url: Site URL to test.
        config_path: Path to configuration file.

    Returns:
        Tuple of (success, result_dict).
    """
    print("\nTesting configuration...")
    try:
        result = scrape_facility(url, config_path)
        return result.get("success", False), result
    except Exception as e:
        logger.error(f"Test scrape failed: {e}")
        return False, {"error": str(e)}


def show_test_results(result: dict) -> None:
    """Show test scrape results.

    Args:
        result: Result dictionary from scrape_facility.
    """
    if result.get("error"):
        print(f"\nERROR: {result['error']}")
        return

    metadata = result.get("metadata", {})
    extraction_meta = metadata.get("extraction_metadata", {})
    fields_status = metadata.get("fields_status", {})

    extracted_count = len(fields_status.get("extracted", []))
    failed_count = len(fields_status.get("failed", []))
    not_found_count = len(fields_status.get("not_found", []))
    total_count = extracted_count + failed_count + not_found_count

    print(f"\nTest Results:")
    print(f"  Success: {extraction_meta.get('success', False)}")
    print(f"  Duration: {extraction_meta.get('extraction_duration_seconds', 0):.2f}s")
    print(f"  Extracted: {extracted_count}/{total_count} fields")

    if extracted_count > 0:
        print(f"    Extracted fields: {', '.join(fields_status.get('extracted', []))}")

    if failed_count > 0:
        print(f"    Failed fields: {', '.join(fields_status.get('failed', []))}")

    if not_found_count > 0:
        print(f"    Not found: {', '.join(fields_status.get('not_found', []))}")


def prompt_satisfied() -> bool:
    """Prompt if user is satisfied with results.

    Returns:
        True if satisfied, False otherwise.
    """
    while True:
        response = input("\nDoes this look good? (y/n): ").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        else:
            print("ERROR: Please enter 'y' or 'n'")


def prompt_refinement() -> str:
    """Prompt for config refinement options.

    Returns:
        User choice (manual, try_again, skip).
    """
    print("\nConfig Refinement Options:")
    print("  1. Manually edit config file")
    print("  2. Try again with same config")
    print("  3. Skip refinement and register")

    while True:
        try:
            choice = int(input("Select option (1-3): ").strip())
            if choice == 1:
                return "manual"
            elif choice == 2:
                return "try_again"
            elif choice == 3:
                return "skip"
            else:
                print("ERROR: Invalid choice")
        except ValueError:
            print("ERROR: Please enter a number")


def edit_config_manually(config_path: str) -> None:
    """Open config file for manual editing.

    Args:
        config_path: Path to configuration file.
    """
    import subprocess
    import os

    editor = os.environ.get("EDITOR", "nano")
    print(f"Opening {config_path} in {editor}...")
    subprocess.run([editor, config_path])


def main():
    """Main onboarding flow."""
    print("=" * 60)
    print("SITE ONBOARDING WIZARD")
    print("=" * 60)

    # Initialize managers
    registry = RegistryManager()
    template_loader = TemplateLoader()
    config_generator = ConfigGenerator()

    # Get available templates
    templates = template_loader.list_available_templates()
    if not templates:
        print("ERROR: No templates available. Please create templates first.")
        sys.exit(1)

    # Collect site information
    url = prompt_url()
    site_type = prompt_site_type(templates)
    frequency = prompt_frequency()
    description = prompt_description(url, site_type)

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  URL: {url}")
    print(f"  Type: {site_type}")
    print(f"  Frequency: {frequency}")
    print(f"  Description: {description}")
    print("=" * 60)

    # Generate configuration
    print("\nGenerating configuration...")
    try:
        config_path, config_content = config_generator.generate_config(
            url, site_type
        )
        print(f"✓ Configuration generated at {config_path}")
    except Exception as e:
        print(f"ERROR: Failed to generate configuration: {e}")
        logger.error(f"Config generation failed: {e}")
        sys.exit(1)

    # Validate configuration
    is_valid, error_msg = config_generator.validate_config(config_content)
    if not is_valid:
        print(f"ERROR: {error_msg}")
        sys.exit(1)
    print("✓ Configuration is valid TOML")

    # Test configuration
    while True:
        success, result = test_config(url, config_path)
        show_test_results(result)

        if prompt_satisfied():
            break

        # Ask for refinement
        choice = prompt_refinement()
        if choice == "manual":
            edit_config_manually(config_path)
            # Reload config for validation
            try:
                with open(config_path, "r") as f:
                    config_content = f.read()
                is_valid, error_msg = config_generator.validate_config(config_content)
                if not is_valid:
                    print(f"ERROR: {error_msg}")
                    continue
            except IOError as e:
                print(f"ERROR: Failed to read config: {e}")
                continue
        elif choice == "skip":
            break

    # Register site
    print("\nRegistering site...")
    try:
        now = datetime.now(timezone.utc).isoformat()
        site = registry.register_site(
            url=url,
            site_type=site_type,
            description=description,
            frequency=frequency,
            config_path=config_path,
        )
        print(f"✓ Site registered successfully!")
        print(f"  Site ID: {site.id}")
        print(f"  Created: {site.created_date}")
    except Exception as e:
        print(f"ERROR: Failed to register site: {e}")
        logger.error(f"Site registration failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("ONBOARDING COMPLETE!")
    print("=" * 60)
    print(f"\nNext steps:")
    print(f"  1. Review your site: scraper_admin/registry_manager.py list_sites()")
    print(f"  2. Schedule the site: python scripts/schedule_site.py {site.id}")
    print(f"  3. Test the scrape: python -c \"from scraper import scrape_facility; scrape_facility('{url}', '{config_path}')\"")


if __name__ == "__main__":
    main()
