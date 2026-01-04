"""Registry manager for site management."""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import sqlite3

from scraper_admin.models import SiteRegistry, SiteRegistryFile, SiteType, Frequency
from scraper_admin.db import DatabaseManager

logger = logging.getLogger(__name__)


class RegistryManager:
    """Manages site registry with both JSON and SQLite storage."""

    def __init__(
        self,
        registry_path: str = "data/sites.json",
        db_path: str = "data/archive.db",
    ):
        """Initialize registry manager.

        Args:
            registry_path: Path to JSON registry file.
            db_path: Path to SQLite database file.
        """
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.init_registry_tables()

    def save_registry(self, registry: SiteRegistryFile) -> None:
        """Save registry to JSON file.

        Args:
            registry: SiteRegistryFile to save.

        Raises:
            IOError: If file cannot be written.
        """
        try:
            with open(self.registry_path, "w") as f:
                json.dump(registry.to_dict(), f, indent=2)
            logger.info(f"Registry saved to {self.registry_path}")
        except IOError as e:
            logger.error(f"Error saving registry: {e}")
            raise

    def load_registry(self) -> SiteRegistryFile:
        """Load registry from JSON file.

        Returns:
            SiteRegistryFile: Loaded registry or empty if file doesn't exist.
        """
        if not self.registry_path.exists():
            logger.info(f"Registry file not found at {self.registry_path}, creating new")
            return SiteRegistryFile()

        try:
            with open(self.registry_path, "r") as f:
                data = json.load(f)
            registry = SiteRegistryFile.from_dict(data)
            logger.info(f"Loaded {len(registry.sites)} sites from registry")
            return registry
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading registry: {e}")
            raise

    def register_site(
        self,
        url: str,
        site_type: str,
        description: str,
        frequency: str,
        config_path: Optional[str] = None,
    ) -> SiteRegistry:
        """Register a new site.

        Args:
            url: Site URL.
            site_type: Type of site (fablab, makerspace, blog).
            description: Human-readable description.
            frequency: Scraping frequency (daily, weekly, monthly).
            config_path: Optional path to site config file.

        Returns:
            SiteRegistry: The registered site.

        Raises:
            ValueError: If site already exists or invalid parameters.
        """
        # Validate inputs
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        # Create site ID from domain
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "").split("/")[0]
        site_id = domain.split(".")[0].lower()  # First part of domain

        # Check if site already exists
        registry = self.load_registry()
        if any(s.id == site_id for s in registry.sites):
            raise ValueError(f"Site with ID '{site_id}' already exists")

        # Create site entry
        now = datetime.now(timezone.utc).isoformat()
        site = SiteRegistry(
            id=site_id,
            url=url,
            site_type=SiteType(site_type),
            description=description,
            frequency=Frequency(frequency),
            active=True,
            created_date=now,
            config_path=config_path,
        )

        # Add to registry
        registry.sites.append(site)
        self.save_registry(registry)

        # Sync to SQLite
        self._sync_site_to_db(site, insert=True)

        logger.info(f"Registered site: {site_id} ({url})")
        return site

    def list_sites(
        self,
        filter_by_type: Optional[str] = None,
        filter_active: bool = True,
    ) -> List[SiteRegistry]:
        """List all sites with optional filtering.

        Args:
            filter_by_type: Optional site type to filter by.
            filter_active: Whether to only show active sites.

        Returns:
            List of SiteRegistry objects.
        """
        registry = self.load_registry()
        sites = registry.sites

        if filter_active:
            sites = [s for s in sites if s.active]

        if filter_by_type:
            sites = [s for s in sites if s.site_type.value == filter_by_type]

        return sites

    def get_site(self, site_id: str) -> Optional[SiteRegistry]:
        """Get a single site by ID.

        Args:
            site_id: Site ID to retrieve.

        Returns:
            SiteRegistry or None if not found.
        """
        registry = self.load_registry()
        for site in registry.sites:
            if site.id == site_id:
                return site
        return None

    def get_site_by_url(self, url: str) -> Optional[SiteRegistry]:
        """Get a single site by URL.

        Args:
            url: Site URL to retrieve.

        Returns:
            SiteRegistry or None if not found.
        """
        registry = self.load_registry()
        for site in registry.sites:
            if site.url == url:
                return site
        return None

    def update_site(self, site_id: str, updates: Dict[str, Any]) -> SiteRegistry:
        """Update a site's information.

        Args:
            site_id: Site ID to update.
            updates: Dictionary of fields to update.

        Returns:
            Updated SiteRegistry.

        Raises:
            ValueError: If site not found.
        """
        registry = self.load_registry()
        site = None
        for i, s in enumerate(registry.sites):
            if s.id == site_id:
                site = s
                break

        if not site:
            raise ValueError(f"Site '{site_id}' not found")

        # Update fields
        for key, value in updates.items():
            if hasattr(site, key):
                if key == "site_type" and isinstance(value, str):
                    value = SiteType(value)
                elif key == "frequency" and isinstance(value, str):
                    value = Frequency(value)
                setattr(site, key, value)

        self.save_registry(registry)
        self._sync_site_to_db(site, insert=False)

        logger.info(f"Updated site: {site_id}")
        return site

    def deactivate_site(self, site_id: str) -> None:
        """Deactivate a site (soft delete).

        Args:
            site_id: Site ID to deactivate.

        Raises:
            ValueError: If site not found.
        """
        self.update_site(site_id, {"active": False})
        logger.info(f"Deactivated site: {site_id}")

    def record_scrape(self, site_id: str, timestamp: str) -> None:
        """Record that a site was successfully scraped.

        Args:
            site_id: Site ID that was scraped.
            timestamp: ISO format timestamp of scrape.

        Raises:
            ValueError: If site not found.
        """
        self.update_site(site_id, {"last_scraped": timestamp})
        logger.info(f"Recorded scrape for site: {site_id}")

    def _sync_site_to_db(self, site: SiteRegistry, insert: bool = True) -> None:
        """Sync a site to SQLite database.

        Args:
            site: SiteRegistry to sync.
            insert: Whether to insert (True) or update (False).
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            if insert:
                cursor.execute("""
                    INSERT OR REPLACE INTO sites
                    (id, url, site_type, description, frequency, active, created_date, last_scraped, config_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    site.id,
                    site.url,
                    site.site_type.value if isinstance(site.site_type, SiteType) else site.site_type,
                    site.description,
                    site.frequency.value if isinstance(site.frequency, Frequency) else site.frequency,
                    1 if site.active else 0,
                    site.created_date,
                    site.last_scraped,
                    site.config_path,
                ))
            else:
                cursor.execute("""
                    UPDATE sites SET
                    site_type = ?, description = ?, frequency = ?, active = ?, last_scraped = ?, config_path = ?
                    WHERE id = ?
                """, (
                    site.site_type.value if isinstance(site.site_type, SiteType) else site.site_type,
                    site.description,
                    site.frequency.value if isinstance(site.frequency, Frequency) else site.frequency,
                    1 if site.active else 0,
                    site.last_scraped,
                    site.config_path,
                    site.id,
                ))

            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error syncing site to database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def sync_all_to_db(self) -> None:
        """Sync entire registry to SQLite database."""
        registry = self.load_registry()
        for site in registry.sites:
            self._sync_site_to_db(site, insert=True)
        logger.info("Synced entire registry to database")

    def get_sites_from_db(
        self,
        filter_by_type: Optional[str] = None,
        filter_active: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get sites from SQLite database.

        Args:
            filter_by_type: Optional site type to filter by.
            filter_active: Whether to only show active sites.

        Returns:
            List of site dictionaries.
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM sites WHERE 1=1"
            params = []

            if filter_active:
                query += " AND active = 1"

            if filter_by_type:
                query += " AND site_type = ?"
                params.append(filter_by_type)

            query += " ORDER BY created_date DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        finally:
            conn.close()
