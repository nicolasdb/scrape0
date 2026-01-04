# Core Scraping Module - File Index & Navigation Guide

## Quick Navigation

### Getting Started
- **[QUICK_START.md](./QUICK_START.md)** - Installation, basic usage, configuration guide
- **[README.md](./README.md)** - Project overview, features, and usage examples
- **[COMPLETION_SUMMARY.md](./COMPLETION_SUMMARY.md)** - What's been implemented and test results

### Understanding the System
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design, IPO architecture, component interactions
- **[IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)** - Detailed feature list and progress

### Configuration & Examples
- **[config/example.toml](./config/example.toml)** - Example configuration with all options documented

---

## Project Structure

### Core Module Files
Located in `/scraper/` - production code implementing the scraping system:

| File | Purpose | Lines |
|------|---------|-------|
| **api.py** | Public `scrape_facility()` function - main entry point | 195 |
| **models.py** | Data classes (SiteConfig, ExtractionResult, etc.) | 127 |
| **config.py** | ConfigManager for loading and parsing TOML files | 160 |
| **validators.py** | URLValidator for URL validation and normalization | 73 |
| **input.py** | InputLayer coordinating validation and config lookup | 45 |
| **scraper_engine.py** | ScrapingEngine with retry logic and timeout handling | 150 |
| **extraction.py** | ExtractionEngine for field extraction with multiple rule types | 207 |
| **output.py** | TOMLOutputFormatter for creating valid TOML output | 134 |
| **file_output.py** | FileOutput for writing and managing output files | 78 |
| **types.py** | TypeConverter for converting extracted strings to basic types | 108 |
| **errors.py** | Custom exception classes | 30 |
| **__init__.py** | Package initialization with lazy imports | 11 |

### Test Files
Located in `/tests/` - comprehensive test suite with 106 tests:

| File | Purpose | Tests |
|------|---------|-------|
| **test_api.py** | End-to-end API tests | 9 |
| **test_config.py** | Configuration management tests | 9 |
| **test_extraction.py** | Field extraction engine tests | 15 |
| **test_file_output.py** | File I/O operation tests | 11 |
| **test_models.py** | Data model tests | 11 |
| **test_output.py** | TOML formatter tests | 10 |
| **test_scraper_engine.py** | Scraping engine tests | 8 |
| **test_types.py** | Type conversion tests | 16 |
| **test_url_validation.py** | URL validation tests | 15 |
| **test_setup.py** | Setup verification tests | 2 |
| **conftest.py** | Shared fixtures and test configuration | - |

### Configuration Files

| File | Purpose |
|------|---------|
| **pyproject.toml** | Black formatter and mypy type checker configuration |
| **pytest.ini** | Pytest test runner configuration |
| **.gitignore** | Git ignore patterns for Python projects |
| **requirements.txt** | Core dependencies (scrapling, tomli, beautifulsoup4, lxml) |
| **requirements-dev.txt** | Development dependencies (pytest, black, mypy) |

### Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** | Project overview and features | Everyone |
| **ARCHITECTURE.md** | System design and component interactions | Developers |
| **QUICK_START.md** | Installation and basic usage | Getting started |
| **COMPLETION_SUMMARY.md** | What's implemented and test results | Project managers |
| **IMPLEMENTATION_STATUS.md** | Detailed feature checklist | Developers |
| **INDEX.md** | This file - file navigation guide | Everyone |

### Configuration Examples

| File | Purpose |
|------|---------|
| **config/example.toml** | Fully documented example configuration with all options |

### Output Directory

| Directory | Purpose |
|-----------|---------|
| **output/** | Where scraped TOML files are written (created at runtime) |

---

## Usage Flows

### For Configuration
1. Start with [QUICK_START.md](./QUICK_START.md) for basic setup
2. Copy and modify [config/example.toml](./config/example.toml) for your sites
3. Refer to [README.md](./README.md) for configuration details

### For Understanding the System
1. Read [README.md](./README.md) for overview
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) for design
3. Look at [scraper/api.py](./scraper/api.py) for entry point
4. Trace through [scraper/](./scraper/) files following imports

### For Development
1. Check [QUICK_START.md](./QUICK_START.md) for setup
2. Look at tests in [tests/](./tests/) for usage patterns
3. Review relevant module documentation
4. Write tests before making changes
5. Run full test suite: `pytest tests/ -v`

### For Testing
1. Install dev dependencies: `pip install -r requirements-dev.txt`
2. Run tests: `pytest tests/ -v`
3. Check coverage: `pytest tests/ --cov=scraper`
4. Review specific test file: `pytest tests/test_api.py -v`

---

## Key Concepts

### Input-Process-Output Architecture
The system is organized into three layers:
- **Input Layer**: URL validation, configuration loading ([input.py](./scraper/input.py), [validators.py](./scraper/validators.py))
- **Process Layer**: HTML fetching, field extraction, type conversion ([scraper_engine.py](./scraper/scraper_engine.py), [extraction.py](./scraper/extraction.py), [types.py](./scraper/types.py))
- **Output Layer**: TOML formatting, file I/O ([output.py](./scraper/output.py), [file_output.py](./scraper/file_output.py))

### Data Flow
```
URL + Config → Validate → Fetch HTML → Extract Fields → Convert Types → Format TOML → Write File
```

### Configuration-Driven Design
Extraction rules are specified in TOML configuration, not hardcoded:
- Site identification (id, url_pattern, site_type)
- Priority fields (name, location, expertise, url, contact)
- Extra metadata fields (custom per site)
- Extraction rules (CSS selectors, XPath, regex)

---

## Code Statistics

| Metric | Value |
|--------|-------|
| Production code | ~1,200 lines across 12 files |
| Test code | ~1,600 lines across 10 files |
| Total tests | 106 tests |
| Test pass rate | 100% |
| Test-to-code ratio | 1.3:1 |
| Documentation | 4 markdown files |

---

## Implementation Status

### Completed Phases
- **Phase 0**: Setup & Foundation ✓
- **Phase 1**: Core Architecture & IPO Layers ✓
- **Phase 2**: Single Example Site (Vertical Slice) ✓

### Not Yet Implemented
- **Phase 3**: Configuration & Extensibility (deferred)
- **Phase 4**: Error Handling & Robustness (deferred)
- **Phase 5**: Testing & Validation (deferred)
- **Phase 6**: Documentation & Polish (deferred)

See [COMPLETION_SUMMARY.md](./COMPLETION_SUMMARY.md) for details on what's implemented.

---

## Common Tasks

### Run Tests
```bash
source venv/bin/activate
pytest tests/ -v
```

### Create Configuration
1. Copy [config/example.toml](./config/example.toml)
2. Edit with your site patterns
3. Save as `config.toml`

### Use the Scraper
```python
from scraper import scrape_facility

result = scrape_facility(
    url="https://example.com",
    config_path="./config.toml",
    output_path="./output/example.toml"
)
```

### Check Code Quality
```bash
black scraper/ tests/
mypy scraper/
```

---

## File Access Quick Links

### Most Important Files
1. [scraper/api.py](./scraper/api.py) - Main entry point
2. [README.md](./README.md) - Project overview
3. [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
4. [config/example.toml](./config/example.toml) - Example config
5. [tests/test_api.py](./tests/test_api.py) - Usage examples

### For Developers
1. [QUICK_START.md](./QUICK_START.md) - Setup guide
2. [scraper/models.py](./scraper/models.py) - Data structures
3. [scraper/config.py](./scraper/config.py) - Configuration loading
4. [scraper/extraction.py](./scraper/extraction.py) - Field extraction
5. [tests/](./tests/) - Test examples

### For Configuration
1. [config/example.toml](./config/example.toml) - Full example
2. [README.md](./README.md#configuration) - Configuration section
3. [QUICK_START.md](./QUICK_START.md#configuration-format) - Quick reference

---

## Testing

### All Tests
```bash
pytest tests/ -v
```

### By Category
```bash
pytest tests/test_api.py -v          # End-to-end
pytest tests/test_config.py -v       # Configuration
pytest tests/test_extraction.py -v   # Extraction
pytest tests/test_models.py -v       # Data models
```

### With Coverage
```bash
pytest tests/ --cov=scraper --cov-report=html
```

---

## Next Steps

1. **Read** [README.md](./README.md) for overview
2. **Setup** using [QUICK_START.md](./QUICK_START.md)
3. **Configure** using [config/example.toml](./config/example.toml)
4. **Run** `pytest tests/ -v` to verify
5. **Integrate** `scrape_facility()` into your application
6. **Review** [ARCHITECTURE.md](./ARCHITECTURE.md) for details

---

**Last Updated**: 2026-01-04
**Status**: Phase 0-2 Complete (106/106 tests passing)
**Version**: 0.1.0
