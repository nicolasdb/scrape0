# Quick Start Guide

## Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Test (Real Websites)

```bash
# Test any URL with a config file
./run.sh https://openfab.be

# Or with explicit config
./run_tests.sh https://openfab.be ./config/openfab.toml

# Test example.com (simple, always available)
./run.sh https://example.com
```

**Output**: Generated TOML file in `./output/real-test.toml` with extracted data

## Running Unit Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_api.py -v

# With coverage report
pytest tests/ --cov=scraper --cov-report=html
```

## Configuration Files

### Understanding Config Files

**Config files are NOT auto-generated.** They're manually created TOML files that define:
- **Which URLs** to scrape (via `url_pattern` matching)
- **What data** to extract from each site (via CSS selectors)
- **How to extract** (timeout, retries, etc.)

### Start Simple: Single Config for Multiple Sites

You can have **one config file** with multiple site configurations:

```toml
[scraper]
primary_library = "scrapling"
timeout_seconds = 20
max_retries = 2

# Site 1: OpenFab
[[sites]]
id = "openfab"
url_pattern = "openfab.be"
site_type = "fablab"

[sites.fields.priority]
title = "h1"
intro = "p"

# Site 2: Example.com
[[sites]]
id = "example"
url_pattern = "example.com"
site_type = "example"

[sites.fields.priority]
title = "h1"
intro = "p"
```

Then scrape both URLs with the **same config file**:
```bash
./run_tests.sh https://openfab.be ./config/myconfig.toml
./run_tests.sh https://example.com ./config/myconfig.toml
```

### When to Create a New Config

Create a new config file when:
1. **Different extraction rules needed** - Site structure is very different
2. **Different timeouts** - Some sites are slow
3. **Different retry strategies** - Some sites have strict rate limits
4. **Organization** - Easier to manage (e.g., `config/fablabs.toml`, `config/hackerspaces.toml`)

### How Configs Are Matched to URLs

When you run:
```bash
./run_tests.sh https://openfab.be ./config/myconfig.toml
```

The scraper looks through all sites in the config and finds one where:
```python
if "openfab.be" in "https://openfab.be":  # url_pattern matches
    use this configuration
```

So `url_pattern = "openfab.be"` matches:
- ✓ `https://openfab.be`
- ✓ `https://openfab.be/about`
- ✓ `https://www.openfab.be`
- ✗ `https://example.com` (doesn't contain "openfab.be")

### Study and Refine Approach

1. **Start with a generic config**:
```toml
[[sites]]
id = "generic"
url_pattern = "domain.com"
[sites.fields.priority]
title = "h1"
description = "p"
content = "body"
```

2. **Test and inspect output**:
```bash
./run_tests.sh https://example.com ./config/generic.toml
# Check output: ./output/real-test.toml
```

3. **Use browser DevTools to find better selectors**:
   - Open the website in Chrome/Firefox
   - Right-click on element → Inspect
   - Find the CSS class or ID
   - Update config

4. **Refine iteratively**:
```toml
[[sites]]
id = "example-refined"
url_pattern = "example.com"
[sites.fields.priority]
title = "h1.page-title"      # More specific
description = "div.intro"    # Better targeting
```

## Basic Usage

### 1. Create a Configuration File

Create `config.toml`:
```toml
[scraper]
primary_library = "scrapling"
timeout_seconds = 30
max_retries = 3

[[sites]]
id = "example-site"
url_pattern = "example.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1.title"
location = "span.location"
expertise = "div.skills"
url = "a.website"
contact = "span.email"

[sites.fields.extra]
hours = "div.hours"
```

### 2. Scrape a Facility

```python
from scraper import scrape_facility

result = scrape_facility(
    url="https://example.com",
    config_path="./config.toml",
    output_path="./output/example.toml"
)

# Check results
if result['success']:
    print("Success!")
    print(result['data']['priority_fields']['name'])
else:
    print(f"Failed: {result['metadata']['extraction_metadata']['failure_reason']}")
```

## Project Structure

```
scraper/              # Main module
├── api.py            # scrape_facility() entry point
├── models.py         # Data classes
├── config.py         # Configuration loading
├── validators.py     # URL validation
├── input.py          # Input layer
├── scraper_engine.py # Web scraping
├── extraction.py     # Field extraction
├── output.py         # TOML formatting
├── file_output.py    # File I/O
├── types.py          # Type conversion
└── errors.py         # Exception classes

tests/               # Test suite (106 tests)
├── conftest.py      # Shared fixtures
├── test_api.py      # End-to-end tests
├── test_config.py   # Configuration tests
├── test_extraction.py # Extraction tests
└── ...              # Other test files

config/
└── example.toml     # Example configuration

output/              # Generated TOML files go here
```

## Configuration Format

### Minimal Configuration
```toml
[scraper]
primary_library = "scrapling"

[[sites]]
id = "mysite"
url_pattern = "mysite.com"
site_type = "fablab"

[sites.fields.priority]
name = "h1"
location = "span.location"
```

### Full Configuration Options
```toml
[scraper]
primary_library = "scrapling"       # Scraping library to use
timeout_seconds = 30                # Request timeout
max_retries = 3                      # Retry attempts
retry_backoff_factor = 2.0           # Exponential backoff multiplier

[[sites]]
id = "site-id"                       # Unique identifier
url_pattern = "site-pattern.com"     # URL substring to match
site_type = "fablab"                 # Site category
description = "Optional description"

# Site-specific overrides
timeout_seconds = 45
max_retries = 5

# Extraction rules
[sites.fields.priority]              # Priority fields
field1 = "css-selector"              # CSS selector rule
field2 = "//xpath"                   # XPath rule
field3 = "/regex-pattern/"           # Regex rule

[sites.fields.extra]                 # Extra metadata fields
field4 = "another-selector"
```

## Extraction Rule Types

### CSS Selectors (Default)
```toml
name = "h1.title"
location = ".location"
skills = "div.skill"
```

### XPath
```toml
name = "//h1[@class='title']"
location = "//span[@id='location']"
```

### Regex
```toml
email = "([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
phone = "/\d{3}-\d{3}-\d{4}/"
```

## Return Value Structure

```python
{
    'success': True/False,  # Overall success flag
    'data': {
        'priority_fields': {
            'name': 'Example',
            'location': 'City, State',
            # ... other fields
        },
        'extra_metadata': {
            'hours': 'Mon-Fri 9am-5pm',
            # ... other extra fields
        }
    },
    'metadata': {
        'extraction_metadata': {
            'success': True/False,
            'extraction_timestamp': '2026-01-04T10:00:00Z',
            'extraction_duration_seconds': 2.3,
            'failure_reason': None,  # or "network_timeout", etc.
            'site_type': 'fablab'
        },
        'fields_status': {
            'extracted': ['name', 'location'],
            'failed': [],
            'not_found': ['expertise']
        }
    },
    'error': None  # or error message for critical failures
}
```

## Error Handling

### Critical Errors (error field populated)
- Configuration file not found
- Invalid URL format
- Network unavailable
- Site configuration not found

### Partial Failures (success=False with data)
- Request timeout
- Network errors
- HTML parsing errors
- Some fields extracted, others failed

## Logging

Enable logging to see detailed execution:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
result = scrape_facility(...)
```

## Common Issues

### "Configuration file not found"
Make sure `config_path` points to valid TOML file:
```python
# Absolute path recommended
result = scrape_facility(
    url="https://example.com",
    config_path="/absolute/path/to/config.toml"
)
```

### "No site configuration found"
URL pattern in config doesn't match the URL being scraped:
```toml
# Config has:
url_pattern = "example.com"

# But you're scraping:
url = "https://different.com"  # Won't match!
```

### "Mock Content" in output
Scrapling library may not be available. Check installation:
```bash
pip install scrapling
```

## Performance Tips

1. **Adjust Timeouts**: Increase `timeout_seconds` for slow sites
2. **Configure Retries**: Reduce `max_retries` for faster failures
3. **CSS Selectors**: Prefer CSS selectors for faster extraction than XPath
4. **Caching**: ConfigManager caches site configs automatically

## Testing

### Run Specific Tests
```bash
# Test just the API
pytest tests/test_api.py -v

# Test configuration
pytest tests/test_config.py -v

# Test extraction
pytest tests/test_extraction.py -v
```

### Test-Driven Development
Add your test first, then implement:
```python
# tests/test_myfeature.py
def test_my_feature():
    result = scrape_facility(...)
    assert result['success']

# Then implement in scraper/
```

## Development Workflow

1. **Make changes** to `/scraper/` files
2. **Write tests** in `/tests/` for new functionality
3. **Run tests**: `pytest tests/ -v`
4. **Format code**: `black scraper/ tests/`
5. **Check types**: `mypy scraper/`

## Documentation Files

- **README.md** - Project overview
- **ARCHITECTURE.md** - System design
- **COMPLETION_SUMMARY.md** - Implementation status
- **IMPLEMENTATION_STATUS.md** - Detailed feature list
- **config/example.toml** - Example configuration
- **QUICK_START.md** - This file

## Getting Help

1. Check **ARCHITECTURE.md** for design questions
2. Review **config/example.toml** for configuration help
3. Look at **tests/** for usage examples
4. Check docstrings in **scraper/*.py** for API details

## Next Steps

1. Create your `config.toml` with your site patterns
2. Run `scrape_facility()` with your URL
3. Check output TOML file
4. Add custom extraction rules as needed
5. Extend configuration for additional sites

Enjoy scraping!
