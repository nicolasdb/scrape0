"""Schedule manager for periodic scraping."""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import sqlite3

from scraper_admin.models import Frequency
from scraper_admin.db import DatabaseManager

logger = logging.getLogger(__name__)


class Schedule:
    """Schedule entry for a site."""

    def __init__(
        self,
        site_id: str,
        frequency: str,
        time_of_day: str = "09:00",
        next_run: Optional[str] = None,
    ):
        """Initialize schedule.

        Args:
            site_id: Site ID to schedule.
            frequency: Scraping frequency (daily, weekly, monthly).
            time_of_day: Time to run (HH:MM format).
            next_run: ISO format timestamp of next run.
        """
        self.site_id = site_id
        self.frequency = Frequency(frequency)
        self.time_of_day = time_of_day
        self.next_run = next_run or self._calculate_next_run(frequency, time_of_day)
        self.last_run = None

    def _calculate_next_run(self, frequency: str, time_of_day: str) -> str:
        """Calculate next run time.

        Args:
            frequency: Frequency string.
            time_of_day: Time of day (HH:MM).

        Returns:
            ISO format timestamp.
        """
        now = datetime.now(timezone.utc)
        hour, minute = map(int, time_of_day.split(":"))

        # Create next run at specified time today
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # If that time has passed, schedule for next occurrence
        if next_run <= now:
            if frequency.lower() == "daily":
                next_run += timedelta(days=1)
            elif frequency.lower() == "weekly":
                next_run += timedelta(weeks=1)
            elif frequency.lower() == "monthly":
                # Move to same day next month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)

        return next_run.isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "site_id": self.site_id,
            "frequency": self.frequency.value,
            "time_of_day": self.time_of_day,
            "next_run": self.next_run,
            "last_run": self.last_run,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Schedule":
        """Create from dictionary."""
        schedule = cls(
            site_id=data["site_id"],
            frequency=data["frequency"],
            time_of_day=data.get("time_of_day", "09:00"),
            next_run=data.get("next_run"),
        )
        schedule.last_run = data.get("last_run")
        return schedule


class ScheduleManager:
    """Manages scheduling for sites."""

    def __init__(
        self,
        schedules_path: str = "data/schedules.json",
        db_path: str = "data/archive.db",
    ):
        """Initialize schedule manager.

        Args:
            schedules_path: Path to JSON schedules file.
            db_path: Path to SQLite database.
        """
        self.schedules_path = Path(schedules_path)
        self.schedules_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.init_schedules_tables()

    def save_schedules(self, schedules: List[Schedule]) -> None:
        """Save schedules to JSON file.

        Args:
            schedules: List of Schedule objects.

        Raises:
            IOError: If file cannot be written.
        """
        try:
            data = {
                "version": "1.0",
                "schedules": [s.to_dict() for s in schedules],
            }
            with open(self.schedules_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Schedules saved to {self.schedules_path}")
        except IOError as e:
            logger.error(f"Error saving schedules: {e}")
            raise

    def load_schedules(self) -> List[Schedule]:
        """Load schedules from JSON file.

        Returns:
            List of Schedule objects or empty list if file doesn't exist.
        """
        if not self.schedules_path.exists():
            logger.info(f"Schedules file not found at {self.schedules_path}")
            return []

        try:
            with open(self.schedules_path, "r") as f:
                data = json.load(f)
            schedules = [Schedule.from_dict(s) for s in data.get("schedules", [])]
            logger.info(f"Loaded {len(schedules)} schedules")
            return schedules
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading schedules: {e}")
            raise

    def schedule_site(
        self,
        site_id: str,
        frequency: str,
        time_of_day: str = "09:00",
    ) -> Schedule:
        """Schedule a site for periodic scraping.

        Args:
            site_id: Site ID to schedule.
            frequency: Scraping frequency (daily, weekly, monthly).
            time_of_day: Time to run (HH:MM format).

        Returns:
            Schedule object.

        Raises:
            ValueError: If schedule already exists or invalid inputs.
        """
        schedules = self.load_schedules()

        # Check if already scheduled
        if any(s.site_id == site_id for s in schedules):
            raise ValueError(f"Site '{site_id}' is already scheduled")

        # Create schedule
        schedule = Schedule(site_id, frequency, time_of_day)
        schedules.append(schedule)

        self.save_schedules(schedules)
        self._sync_schedule_to_db(schedule, insert=True)

        logger.info(f"Scheduled site {site_id} for {frequency} scraping at {time_of_day}")
        return schedule

    def unschedule_site(self, site_id: str) -> None:
        """Remove a site from schedule.

        Args:
            site_id: Site ID to unschedule.

        Raises:
            ValueError: If schedule not found.
        """
        schedules = self.load_schedules()
        initial_count = len(schedules)

        schedules = [s for s in schedules if s.site_id != site_id]

        if len(schedules) == initial_count:
            raise ValueError(f"Schedule for site '{site_id}' not found")

        self.save_schedules(schedules)
        self._delete_schedule_from_db(site_id)

        logger.info(f"Unscheduled site: {site_id}")

    def list_schedules(self) -> List[Schedule]:
        """Get all schedules.

        Returns:
            List of Schedule objects.
        """
        return self.load_schedules()

    def get_schedule(self, site_id: str) -> Optional[Schedule]:
        """Get schedule for a specific site.

        Args:
            site_id: Site ID.

        Returns:
            Schedule or None if not found.
        """
        schedules = self.load_schedules()
        for schedule in schedules:
            if schedule.site_id == site_id:
                return schedule
        return None

    def is_due_for_run(self, site_id: str) -> bool:
        """Check if a site is due for a scrape run.

        Args:
            site_id: Site ID to check.

        Returns:
            True if due, False otherwise.
        """
        schedule = self.get_schedule(site_id)
        if not schedule:
            return False

        next_run = datetime.fromisoformat(schedule.next_run)
        now = datetime.now(timezone.utc)

        return now >= next_run

    def get_all_due_sites(self) -> List[str]:
        """Get all sites due to run now.

        Returns:
            List of site IDs due to run.
        """
        due_sites = []
        for schedule in self.load_schedules():
            if self.is_due_for_run(schedule.site_id):
                due_sites.append(schedule.site_id)

        return due_sites

    def get_next_runs(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming runs in the next N days.

        Args:
            days: Number of days to look ahead.

        Returns:
            List of dicts with site_id, next_run, frequency.
        """
        upcoming = []
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days)

        for schedule in self.load_schedules():
            next_run = datetime.fromisoformat(schedule.next_run)
            if now <= next_run <= future:
                upcoming.append({
                    "site_id": schedule.site_id,
                    "next_run": schedule.next_run,
                    "frequency": schedule.frequency.value,
                    "due_soon": (next_run - now).total_seconds() < 3600,  # Due within 1 hour
                })

        return sorted(upcoming, key=lambda x: x["next_run"])

    def mark_run_complete(self, site_id: str) -> None:
        """Mark a site as successfully run and update next_run.

        Args:
            site_id: Site ID that was run.

        Raises:
            ValueError: If schedule not found.
        """
        schedules = self.load_schedules()
        schedule = None

        for s in schedules:
            if s.site_id == site_id:
                schedule = s
                break

        if not schedule:
            raise ValueError(f"Schedule for site '{site_id}' not found")

        # Update times
        now = datetime.now(timezone.utc)
        schedule.last_run = now.isoformat()

        # Calculate next run based on frequency
        next_run = now
        if schedule.frequency == Frequency.DAILY:
            next_run = now + timedelta(days=1)
        elif schedule.frequency == Frequency.WEEKLY:
            next_run = now + timedelta(weeks=1)
        elif schedule.frequency == Frequency.MONTHLY:
            # Move to same day next month
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1)
            else:
                next_run = next_run.replace(month=now.month + 1)

        schedule.next_run = next_run.isoformat()

        self.save_schedules(schedules)
        self._sync_schedule_to_db(schedule, insert=False)

        logger.info(f"Updated next run for {site_id}: {schedule.next_run}")

    def _sync_schedule_to_db(self, schedule: Schedule, insert: bool = True) -> None:
        """Sync a schedule to SQLite database.

        Args:
            schedule: Schedule to sync.
            insert: Whether to insert (True) or update (False).
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            if insert:
                cursor.execute("""
                    INSERT OR REPLACE INTO schedules
                    (site_id, frequency, time_of_day, next_run, last_run, active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    schedule.site_id,
                    schedule.frequency.value,
                    schedule.time_of_day,
                    schedule.next_run,
                    schedule.last_run,
                    1,
                ))
            else:
                cursor.execute("""
                    UPDATE schedules SET
                    frequency = ?, time_of_day = ?, next_run = ?, last_run = ?
                    WHERE site_id = ?
                """, (
                    schedule.frequency.value,
                    schedule.time_of_day,
                    schedule.next_run,
                    schedule.last_run,
                    schedule.site_id,
                ))

            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error syncing schedule to database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def _delete_schedule_from_db(self, site_id: str) -> None:
        """Delete a schedule from SQLite database.

        Args:
            site_id: Site ID to delete.
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM schedules WHERE site_id = ?", (site_id,))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error deleting schedule from database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
