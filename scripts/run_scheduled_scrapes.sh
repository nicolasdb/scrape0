#!/bin/bash
# Cron-friendly script to run scheduled scrapes
# Can be added to crontab: 0 9 * * * /path/to/run_scheduled_scrapes.sh

set -e

# Set working directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Set Python path
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Create logs directory if needed
mkdir -p logs

# Log file with timestamp
LOG_FILE="logs/scheduled_scrapes_$(date +%Y%m%d_%H%M%S).log"

# Run the scheduler
python3 -c "
import sys
import logging
from datetime import datetime
from scraper_admin.registry_manager import RegistryManager
from scraper_admin.schedule_manager import ScheduleManager
from scraper_admin.result_archiver import ResultArchiver
from scraper_admin.change_detector import ChangeDetector
from scraper import scrape_facility

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('$LOG_FILE'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info('=' * 60)
logger.info('Starting scheduled scrapes')
logger.info('=' * 60)

try:
    # Initialize managers
    registry = RegistryManager()
    scheduler = ScheduleManager()
    archiver = ResultArchiver()
    detector = ChangeDetector()

    # Get sites due for scraping
    due_sites = scheduler.get_all_due_sites()
    logger.info(f'Found {len(due_sites)} sites due for scraping')

    if not due_sites:
        logger.info('No sites due for scraping at this time')
        sys.exit(0)

    # Process each due site
    completed = 0
    failed = 0

    for site_id in due_sites:
        try:
            logger.info(f'Starting scrape for site: {site_id}')

            # Get site configuration
            site = registry.get_site(site_id)
            if not site:
                logger.warning(f'Site {site_id} not found in registry')
                failed += 1
                continue

            if not site.active:
                logger.info(f'Site {site_id} is not active, skipping')
                failed += 1
                continue

            if not site.config_path:
                logger.warning(f'Site {site_id} has no config path')
                failed += 1
                continue

            # Run scraper
            result = scrape_facility(site.url, site.config_path)

            if result.get('success'):
                logger.info(f'Successfully scraped {site_id}')

                # Archive result
                toml_content = str(result.get('data', {}))
                archiver.archive_result(site.url, toml_content, result)

                # Update last_scraped
                now = datetime.now().isoformat()
                registry.record_scrape(site_id, now)

                # Update scheduler
                scheduler.mark_run_complete(site_id)

                completed += 1

            else:
                logger.warning(f'Scrape for {site_id} returned success=False')
                failed += 1

        except Exception as e:
            logger.error(f'Error scraping {site_id}: {e}', exc_info=True)
            failed += 1

    logger.info('=' * 60)
    logger.info(f'Scheduled scrapes completed: {completed} successful, {failed} failed')
    logger.info('=' * 60)

except Exception as e:
    logger.error(f'Fatal error in scheduler: {e}', exc_info=True)
    sys.exit(1)
" >> "$LOG_FILE" 2>&1

exit_code=$?

echo "Scheduled scrapes completed. Log: $LOG_FILE"
exit $exit_code
