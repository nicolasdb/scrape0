# Real-World URL Testing Guide

This document describes how to test the scraper against real, live websites.

## Quick Start

### Test OpenFab.be (French Belgian FabLab)
```bash
./run_tests.sh https://openfab.be ./config/openfab.toml
```

**What's tested:**
- Real Belgian FabLab website
- French content extraction
- Headings, descriptions, links
- Output: `./output/real-test.toml`

### Test Example.com (Simple, Always Available)
```bash
./run_tests.sh https://example.com ./config/real-world.toml
```

**What's tested:**
- Simple test domain (always available)
- Basic HTML extraction
- Title, intro paragraphs
- Output: `./output/real-test.toml`

## Configuration Files

### `./config/openfab.toml`
Configuration for OpenFab Brussels FabLab
- **URL Pattern**: openfab.be
- **Site Type**: fablab
- **Extracts**: headings, descriptions, links
- **Fields**: title, main_heading, intro_text, page_content, all_links, all_headings

### `./config/real-world.toml`
Configuration for multiple real websites
- Example.com (documentation site)
- Wikipedia (Python article)
- GitHub (Scrapling repository)

## Testing Your Own URLs

### Simple Test
```bash
./run_tests.sh <url> <config.toml>
```

Example:
```bash
./run_tests.sh https://github.com ./config/real-world.toml
```

### Manual Testing
```bash
source venv/bin/activate
python test_real_urls.py <url> <config.toml>
```

## What Gets Generated

Each test run creates:
- **TOML Output File**: `./output/real-test.toml`
  - Contains extracted data with metadata
  - Includes field status (extracted, failed, not_found)
  - ISO format timestamp
  - Extraction duration

## Implementation Details

### Scraper Engine (`scraper/scraper_engine.py`)

The current implementation uses:
1. **Primary**: Scrapling library (modern `Fetcher.get()` API)
   - Handles dynamic content
   - Respects timeouts
   - Supports proxy and stealth headers

2. **Fallback**: Requests library (if Scrapling unavailable)
   - Simple HTTP GET requests
   - Standard error handling
   - Timeout support

3. **Mock Fallback**: Generic HTML (if both unavailable)
   - For testing without network access

### Error Handling

The scraper handles:
- **Network timeouts** (15-20 second default)
- **Connection errors** (retries with exponential backoff)
- **HTTP errors** (4xx/5xx responses)
- **Partial failures** (extracts what's available)

### Example Output Format

```toml
[extraction_metadata]
success = true
extraction_timestamp = "2026-01-04T11:37:31.967047+00:00"
extraction_duration_seconds = 0.5
site_type = "fablab"

[priority_fields]
title = ["Bricoler", "ça fait du bien..."]
intro_text = ["Parce que nous manquons..."]

[extra_metadata]
all_links = ["Gamelab", "Vulca"]
all_headings = ["Bricoler", "Qui sommes nous?"]

[fields_status]
extracted = ["title", "intro_text", "all_links"]
failed = []
not_found = ["main_heading"]
```

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'scrapling'`:
```bash
source venv/bin/activate
pip install scrapling requests beautifulsoup4 lxml tomli
```

### Connection Timeouts
- Default timeout is 20 seconds for OpenFab
- Increase timeout in config: `timeout_seconds = 30`
- Check your network connection
- Try example.com first (always available)

### No Fields Extracted
1. Verify selectors in config match the website HTML
2. Check if website uses JavaScript to load content (Scrapling handles this)
3. Inspect website with browser DevTools to find correct selectors
4. Update config with correct CSS selectors

### Output File Not Created
Check:
- `./output/` directory exists
- Directory has write permissions
- No errors in test output

## Success Criteria

✓ Real-world testing successful when:
- HTTP request completes without timeout
- HTML content is fetched
- CSS selectors find matching elements
- TOML output file is created and valid
- Metadata shows extraction timestamp and duration
- Fields_status accurately tracks extraction results

## Next Steps

1. Test with more real websites:
   ```bash
   ./run_tests.sh https://makerspacebuffalo.org ./config/real-world.toml
   ```

2. Customize configurations for your sites:
   - Add new sites to config files
   - Use browser DevTools to find correct CSS selectors
   - Test extraction rules before deploying

3. Monitor logs for insights:
   ```bash
   python test_real_urls.py <url> <config> 2>&1 | grep -i "fetching\|extracted\|error"
   ```

## Files

- `test_real_urls.py` - Main testing script
- `run_tests.sh` - Helper script (activates venv)
- `config/openfab.toml` - OpenFab configuration
- `config/real-world.toml` - Multi-site configurations
- `scraper/scraper_engine.py` - Network fetching logic
