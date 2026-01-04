"""Database initialization and management for the registry system."""

import sqlite3
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for site registry and results."""

    def __init__(self, db_path: str = "data/archive.db"):
        """Initialize database manager.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection.

        Returns:
            sqlite3.Connection: Database connection.
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_registry_tables(self) -> None:
        """Initialize registry tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Sites table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sites (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL UNIQUE,
                    site_type TEXT NOT NULL,
                    description TEXT,
                    frequency TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_date TEXT NOT NULL,
                    last_scraped TEXT,
                    config_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sites_url ON sites(url)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sites_type ON sites(site_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sites_frequency ON sites(frequency)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sites_active ON sites(active)
            """)

            conn.commit()
            logger.info("Registry tables initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing registry tables: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_results_tables(self) -> None:
        """Initialize results and change tracking tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Results table - no UNIQUE constraint to allow multiple results per day
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    run_date TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    duration REAL,
                    site_type TEXT,
                    extracted_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    not_found_count INTEGER DEFAULT 0,
                    result_file TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Result fields table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS result_fields (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    result_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    value TEXT,
                    FOREIGN KEY(result_id) REFERENCES results(id) ON DELETE CASCADE
                )
            """)

            # Alerts table for change detection
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT,
                    detection_date TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_results_url ON results(url)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_results_date ON results(run_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_results_success ON results(success)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_results_type ON results(site_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_result_fields_result ON result_fields(result_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_url ON alerts(url)
            """)

            conn.commit()
            logger.info("Results tables initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing results tables: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_schedules_tables(self) -> None:
        """Initialize schedule tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Schedules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    time_of_day TEXT DEFAULT '09:00',
                    next_run TEXT NOT NULL,
                    last_run TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(site_id),
                    FOREIGN KEY(site_id) REFERENCES sites(id) ON DELETE CASCADE
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_schedules_next_run ON schedules(next_run)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_schedules_frequency ON schedules(frequency)
            """)

            conn.commit()
            logger.info("Schedule tables initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing schedule tables: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_all_tables(self) -> None:
        """Initialize all tables."""
        self.init_registry_tables()
        self.init_results_tables()
        self.init_schedules_tables()
