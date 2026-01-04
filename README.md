# Core Scraping Module with Modular Architecture

A production-ready web scraping module designed for extracting facility data (fablabs, makerspaces, etc.) with a clean Input-Process-Output architecture. Built with Scrapling for browser automation and structured TOML output.

## Features

- **IPO Architecture**: Clean separation of Input, Process, and Output layers
- **Configuration-Driven**: Single unified TOML configuration file for all sites
- **Graceful Degradation**: Extracts partial data when full extraction isn't possible
- **Comprehensive Metadata**: Tracks extraction success, failures, and diagnostics
- **TOML Output**: Valid TOML output with metadata sections
- **Library Swappability**: Designed to support alternative scraping libraries
- **Type Safety**: Automatic type conversion and TOML compatibility checking

## Quick Start

### Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Basic Usage

```python
from scraper import scrape_facility

result = scrape_facility(
    url="https://example-fablab.com",
    config_path="./config.toml",
    output_path="./output/example.toml"
)

if result['success']:
    print(f"Success! Extracted: {result['data']['priority_fields']['name']}")
else:
    print(f"Failed: {result['metadata']['extraction_metadata']['failure_reason']}")
    print(f"Partial data: {result['data']}")
```

## Configuration

Configuration is specified in a TOML file that defines site patterns and extraction rules:

```toml
[scraper]
primary_library = "scrapling"
timeout_seconds = 30
max_retries = 3
retry_backoff_factor = 2.0

[[sites]]
id = "example-fablab"
url_pattern = "example-fablab.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1.facility-name"
location = "span.location"
expertise = "div.expertise"
url = "a.website-link"
contact = "span.contact"

[sites.fields.extra]
operating_hours = "div.hours"

[output]
format = "toml"
include_metadata = true
directory = "./output"
```

## Output Format

The module produces valid TOML output with metadata:

```toml
[extraction_metadata]
success = true
extraction_timestamp = "2026-01-04T10:00:00Z"
extraction_duration_seconds = 2.3
failure_reason = null
site_type = "fablab"

[priority_fields]
name = "Example Fablab"
location = "San Francisco, CA"
expertise = ["3D printing", "electronics", "woodworking"]
url = "https://example.com"
contact = "contact@example.com"

[extra_metadata]
operating_hours = "Mon-Fri 9am-6pm, Sat 10am-4pm"

[fields_status]
extracted = ["name", "location", "expertise", "url", "contact", "operating_hours"]
failed = []
not_found = []
```

## Architecture

The module follows an Input-Process-Output pattern:

```
Input Layer          Process Layer          Output Layer
    |                    |                       |
    ├─ URL input         ├─ Field extraction     ├─ Type enforcement
    ├─ Config load       ├─ Type conversion      ├─ TOML serialization
    ├─ HTML fetch        ├─ Error capture        ├─ Metadata attachment
    └─ Validation        └─ Partial success      └─ File writing
```

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
pytest tests/ -v --cov=scraper  # With coverage
```

## Project Structure

```
scrape0/
├── scraper/                 # Main module
│   ├── __init__.py
│   ├── api.py              # Public interface (scrape_facility)
│   ├── models.py           # Data models
│   ├── config.py           # Configuration management
│   ├── input.py            # Input layer
│   ├── scraper_engine.py   # Scraping engine (Scrapling wrapper)
│   ├── extraction.py       # Data extraction engine
│   ├── output.py           # TOML output formatter
│   ├── types.py            # Type conversion utilities
│   └── errors.py           # Exception classes
├── tests/                  # Test suite
├── config/                 # Configuration files
├── output/                 # Generated TOML output
├── docs/                   # Implementation notes
└── requirements.txt        # Dependencies
```

## Error Handling

The module handles errors gracefully:

- **Critical Failures**: Return error field with clear message (config not found, invalid URL)
- **Partial Failures**: Return success=False with extracted data and failure_reason
- **Field-Level Failures**: Track in fields_status without halting extraction

See TROUBLESHOOTING.md for common issues and debugging.

## Version

0.1.0 - Initial implementation with single-URL scraping and basic configuration

## License

TBD
