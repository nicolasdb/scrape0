# Tech Stack

## Core Scraping & Automation

- **Scrapling** (https://github.com/D4Vinci/Scrapling): Primary web scraping engine providing browser automation and intelligent data extraction
- **Python 3.x**: Backend language for orchestration, configuration, and data processing

## Data Format & Configuration

- **TOML**: Human-readable format for configuration files and facility profile output
- **JSON**: Internal data interchange and logging

## Frontend & User Interface

- **HTML5**: Minimal web interface for reliability measurement, search, and dashboard views
- **CSS3**: Styling for user interface
- **JavaScript (vanilla or lightweight framework)**: Client-side interactivity for search and filtering

## Data Storage & Persistence

- **File System (TOML files)**: Primary storage for facility profiles, enabling version control and human readability
- **SQLite**: Structured database for indexing, metrics, and analytics queries
- **Git/Version Control**: Track profile changes over time for audit trail and historical analysis

## Monitoring, Logging & Reliability Tracking

- **Python logging**: Application logging for scraping operations and failures
- **Structured Logging (JSON/CSV)**: Persistent storage of success/failure metrics for reliability measurement
- **Metrics Database (SQLite)**: Track success rates, failure patterns, and method performance across time
- **File-based Reports**: CSV/JSON exports of reliability metrics and scraping performance data

## Scheduling & Orchestration

- **APScheduler** or **Celery**: Task scheduling for periodic scraping runs
- **Cron Jobs**: Alternative lightweight scheduling for deployment scenarios
- **subprocess/threading**: Process management for scraping tasks

## Development & Testing

- **pytest**: Unit and integration testing framework
- **Virtual Environment (venv)**: Python dependency isolation
- **Git**: Version control for code and profile data

## Future Tech Stack (Out of Scope - Phase 3+)

- **Neo4j**: Graph database for ingestion phase, modeling relationships between facilities, expertise areas, and community connections
- **Grafiti** (or similar tools): Data ingestion and transformation framework for populating Neo4j with facility and relationship data
- **PostgreSQL**: If scaling beyond SQLite for production deployment

## Architecture Overview

```
User Interface (HTML/CSS/JS)
  ├─ Reliability Dashboard (success rates, method comparisons)
  └─ Search & Discovery Interface
        ↓
Scrape0 Backend (Python + APScheduler)
        ↓
Scrapling Engine (Browser Automation)
        ↓
Target Websites (Fablabs/Makerspaces)
        ↓
Data Processing & Validation
        ↓
Storage & Metrics Layer
  ├─ TOML Profiles (File System)
  ├─ Success/Failure Metrics (SQLite)
  ├─ Audit Trail (Git)
  └─ Performance Analytics (JSON/CSV)
```

## Data Flow

1. **Configuration**: TOML files define target websites, extraction patterns, scraping methods, and schedules
2. **Scraping**: Scrapling executes extraction on schedule, capturing priority and comprehensive data
3. **Metrics Collection**: Each scraping run tracked with success/failure status, errors, and method performance
4. **Processing**: Python backend validates, normalizes, and enriches extracted data
5. **Storage**: Profiles written as TOML files with Git version control; metrics stored in SQLite
6. **Analysis**: Reliability dashboard queries metrics database to display performance trends and method comparisons
7. **Query**: Search interface queries TOML files and facility database for discovery
8. **Future Ingestion**: Rich profile data prepared for Neo4j ingestion and relationship modeling

## Notes on Tech Stack Decisions

- **Scrapling**: Browser automation handles dynamic content and JavaScript-heavy websites better than static scrapers
- **TOML**: Chosen for human readability, making profiles editable and version-controllable without special tools
- **File-Based Storage**: Enables Git version control for audit trails and enables easy diffs of profile changes
- **SQLite for Metrics**: Lightweight database for tracking success/failure rates and enabling complex reliability queries
- **Minimal Frontend**: HTML-based interface keeps deployment simple and aligns with current single-user usage
- **Python**: Widely-supported ecosystem for web scraping, scheduling, and data processing
- **Neo4j + Grafiti (Future)**: Graph structure naturally models facility relationships, expertise networks, and community connections for semantic understanding beyond simple profile storage
- **Reliability Focus**: Reliability measurement infrastructure built into core product rather than added later, making it a primary differentiator
