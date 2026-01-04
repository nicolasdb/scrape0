"""Tests for site registry system."""

import pytest
from pathlib import Path
import json
from datetime import datetime, timezone

from scraper_admin.registry_manager import RegistryManager
from scraper_admin.models import SiteRegistry, SiteType, Frequency, SiteRegistryFile


class TestSiteRegistryModels:
    """Test registry data models."""

    def test_site_registry_creation(self):
        """Test creating a SiteRegistry."""
        now = datetime.now(timezone.utc).isoformat()
        site = SiteRegistry(
            id="example",
            url="https://example.com",
            site_type=SiteType.FABLAB,
            description="Test site",
            frequency=Frequency.DAILY,
            active=True,
            created_date=now,
        )

        assert site.id == "example"
        assert site.url == "https://example.com"
        assert site.active is True

    def test_site_registry_validation(self):
        """Test SiteRegistry validation."""
        now = datetime.now(timezone.utc).isoformat()

        with pytest.raises(ValueError):
            SiteRegistry(
                id="",  # Empty ID
                url="https://example.com",
                site_type=SiteType.FABLAB,
                description="Test",
                frequency=Frequency.DAILY,
                active=True,
                created_date=now,
            )

    def test_site_registry_to_dict(self):
        """Test converting SiteRegistry to dictionary."""
        now = datetime.now(timezone.utc).isoformat()
        site = SiteRegistry(
            id="example",
            url="https://example.com",
            site_type=SiteType.FABLAB,
            description="Test site",
            frequency=Frequency.DAILY,
            active=True,
            created_date=now,
        )

        data = site.to_dict()
        assert data["id"] == "example"
        assert data["site_type"] == "fablab"
        assert data["frequency"] == "daily"

    def test_site_registry_from_dict(self):
        """Test creating SiteRegistry from dictionary."""
        data = {
            "id": "example",
            "url": "https://example.com",
            "site_type": "fablab",
            "description": "Test site",
            "frequency": "daily",
            "active": True,
            "created_date": datetime.now(timezone.utc).isoformat(),
        }

        site = SiteRegistry.from_dict(data)
        assert site.id == "example"
        assert isinstance(site.site_type, SiteType)


class TestRegistryManager:
    """Test registry manager."""

    def test_register_site(self, temp_dir):
        """Test registering a new site."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        site = registry.register_site(
            url="https://examplefablab.com",
            site_type="fablab",
            description="Example FabLab",
            frequency="daily",
        )

        assert site.id == "examplefablab"
        assert site.url == "https://examplefablab.com"
        assert site.active is True

    def test_register_duplicate_site(self, temp_dir):
        """Test that duplicate sites cannot be registered."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        registry.register_site(
            url="https://examplefablab.com",
            site_type="fablab",
            description="Example FabLab",
            frequency="daily",
        )

        with pytest.raises(ValueError):
            registry.register_site(
                url="https://examplefablab.com",  # Same domain - should fail
                site_type="fablab",
                description="Another Example",
                frequency="daily",
            )

    def test_list_sites(self, temp_dir):
        """Test listing registered sites."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        registry.register_site(
            url="https://fablab1.com",
            site_type="fablab",
            description="FabLab 1",
            frequency="daily",
        )

        registry.register_site(
            url="https://makerspace1.com",
            site_type="makerspace",
            description="Makerspace 1",
            frequency="weekly",
        )

        sites = registry.list_sites()
        assert len(sites) == 2

    def test_list_sites_filtered_by_type(self, temp_dir):
        """Test listing sites filtered by type."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        registry.register_site(
            url="https://fablab1.com",
            site_type="fablab",
            description="FabLab 1",
            frequency="daily",
        )

        registry.register_site(
            url="https://makerspace1.com",
            site_type="makerspace",
            description="Makerspace 1",
            frequency="weekly",
        )

        fablab_sites = registry.list_sites(filter_by_type="fablab")
        assert len(fablab_sites) == 1
        assert fablab_sites[0].site_type == SiteType.FABLAB

    def test_get_site(self, temp_dir):
        """Test retrieving a single site."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        registry.register_site(
            url="https://fablab1.com",
            site_type="fablab",
            description="FabLab 1",
            frequency="daily",
        )

        site = registry.get_site("fablab1")
        assert site is not None
        assert site.id == "fablab1"

    def test_get_site_not_found(self, temp_dir):
        """Test getting a non-existent site."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        site = registry.get_site("nonexistent")
        assert site is None

    def test_update_site(self, temp_dir):
        """Test updating a site."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        registry.register_site(
            url="https://fablab1.com",
            site_type="fablab",
            description="FabLab 1",
            frequency="daily",
        )

        updated = registry.update_site(
            "fablab1",
            {"description": "Updated Description", "frequency": "weekly"},
        )

        assert updated.description == "Updated Description"
        assert updated.frequency == Frequency.WEEKLY

    def test_deactivate_site(self, temp_dir):
        """Test deactivating a site."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        registry.register_site(
            url="https://fablab1.com",
            site_type="fablab",
            description="FabLab 1",
            frequency="daily",
        )

        registry.deactivate_site("fablab1")

        site = registry.get_site("fablab1")
        assert site.active is False

    def test_record_scrape(self, temp_dir):
        """Test recording a scrape."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        registry.register_site(
            url="https://fablab1.com",
            site_type="fablab",
            description="FabLab 1",
            frequency="daily",
        )

        now = datetime.now(timezone.utc).isoformat()
        registry.record_scrape("fablab1", now)

        site = registry.get_site("fablab1")
        assert site.last_scraped == now

    def test_save_and_load_registry(self, temp_dir):
        """Test saving and loading registry."""
        registry_path = temp_dir / "sites.json"
        db_path = temp_dir / "archive.db"

        registry1 = RegistryManager(
            registry_path=str(registry_path),
            db_path=str(db_path),
        )

        registry1.register_site(
            url="https://fablab1.com",
            site_type="fablab",
            description="FabLab 1",
            frequency="daily",
        )

        # Load in new manager
        registry2 = RegistryManager(
            registry_path=str(registry_path),
            db_path=str(db_path),
        )

        sites = registry2.list_sites()
        assert len(sites) == 1
        assert sites[0].id == "fablab1"

    def test_sync_to_database(self, temp_dir):
        """Test synchronizing to SQLite database."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        registry.register_site(
            url="https://fablab1.com",
            site_type="fablab",
            description="FabLab 1",
            frequency="daily",
        )

        db_sites = registry.get_sites_from_db()
        assert len(db_sites) == 1
        assert db_sites[0]["id"] == "fablab1"

    def test_get_site_by_url(self, temp_dir):
        """Test getting site by URL."""
        registry = RegistryManager(
            registry_path=str(temp_dir / "sites.json"),
            db_path=str(temp_dir / "archive.db"),
        )

        registry.register_site(
            url="https://fablab1.com",
            site_type="fablab",
            description="FabLab 1",
            frequency="daily",
        )

        site = registry.get_site_by_url("https://fablab1.com")
        assert site is not None
        assert site.id == "fablab1"
