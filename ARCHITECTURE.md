# Architecture: Core Scraping Module with Modular Design

## Overview

This module implements a production-ready web scraping system using a clean Input-Process-Output (IPO) architecture. The design supports modular component swapping, configuration-driven behavior, and graceful partial failure handling.

## IPO Architecture

The module is organized into three distinct layers:

### Input Layer
Responsible for accepting and validating user input, loading configuration, and retrieving raw content:

- **URL Validation**: Validates URL format, normalizes to HTTP/HTTPS
- **Configuration Loading**: Loads TOML configuration, validates structure
- **Raw Content Fetching**: Retrieves HTML/web content using Scrapling with retry logic
- **Error Boundary**: Captures and categorizes input-level errors

Key components:
- `InputLayer`: Coordinates URL and config validation
- `URLValidator`: Validates and normalizes URLs
- `ConfigManager`: Loads and manages scraper configuration
- `ScrapingEngine`: Wraps Scrapling library with retry logic

### Process Layer
Transforms raw HTML into structured, typed data with error tracking:

- **Field Extraction**: Applies configuration rules to extract fields from HTML
- **Type Conversion**: Converts raw strings to appropriate TOML-compatible types
- **Error Handling**: Captures field-level failures without halting
- **Metadata Tracking**: Records which fields succeeded, failed, or were not found
- **Site Type Detection**: Identifies site type for analytics

Key components:
- `ExtractionEngine`: Applies extraction rules and manages field-level failures
- `RuleParser` and Rule classes: Support multiple extraction rule formats (CSS, XPath, regex)
- `TypeConverter`: Converts extracted strings to appropriate types
- `ExtractionMetadata`: Tracks extraction success, failures, and diagnostics

### Output Layer
Formats and persists extraction results:

- **Type Enforcement**: Ensures all values are TOML-compatible
- **TOML Serialization**: Creates valid TOML structure
- **Metadata Attachment**: Includes extraction metadata and field status
- **File Writing**: Persists TOML output with proper error handling

Key components:
- `TOMLOutputFormatter`: Formats extraction results as TOML
- `FileOutput`: Handles file I/O and directory creation

## Component Design

### Data Flow

```
User Input
    |
    v
InputLayer (URL + Config validation)
    |
    v
ScrapingEngine (Fetch HTML)
    |
    v
ExtractionEngine (Apply rules, convert types)
    |
    v
TOMLOutputFormatter (Format output)
    |
    v
FileOutput (Write to disk)
    |
    v
Return Result
```

### Data Models

The module uses dataclasses for type safety:

```python
@dataclass
class SiteConfig:
    id: str
    url_pattern: str
    site_type: str
    priority_fields: Dict[str, str]
    extra_fields: Dict[str, str]
    timeout_seconds: int
    max_retries: int

@dataclass
class ExtractionResult:
    success: bool
    priority_fields: Dict[str, Any]
    extra_metadata: Dict[str, Any]
    metadata: ExtractionMetadata
    fields_status: FieldStatus
    error: Optional[str]
```

### Error Handling Strategy

**Fail Fast for Critical Issues**:
- Configuration file not found → Return error immediately
- URL validation fails → Return error immediately
- Network unavailable → Return error immediately

**Graceful Partial Failure**:
- Individual field extraction fails → Continue with other fields
- Type conversion fails → Log and track in fields_status
- Partial extraction → Return with success=False but include extracted data

**Error Categorization**:
- Each error is categorized (NETWORK_TIMEOUT, PARSE_ERROR, etc.)
- Failure_reason stored in metadata for analytics
- Fields_status tracks which fields succeeded vs. failed

## Configuration Evolution

The configuration schema is intentionally flexible to support discovery during implementation:

```toml
[scraper]
primary_library = "scrapling"        # Swappable library name
timeout_seconds = 30                 # Request timeout
max_retries = 3                      # Retry attempts
retry_backoff_factor = 2.0           # Exponential backoff multiplier

[[sites]]
id = "site-identifier"
url_pattern = "example.com"          # Substring match in URL
site_type = "fablab"                 # Analytics categorization
description = "Site description"

[sites.fields.priority]
# Map field names to extraction rules
name = "h1.title"                    # CSS selector
location = "span.address"
expertise = "div.skills"
url = "a.website"
contact = "span.contact"

[sites.fields.extra]
# Additional fields as discovered
operating_hours = "div.hours"
equipment = "ul.equipment li"

[output]
format = "toml"
include_metadata = true
directory = "./output"
```

Schema changes are documented in CONFIG_EVOLUTION.md as implementation proceeds.

## Library Swapping Design

The module is designed to support alternative scraping libraries:

**Current Implementation**: Scrapling (browser automation)
**Future Options**: Requests + BeautifulSoup, Selenium, Playwright, etc.

**Abstraction Point**: `ScrapingEngine` class
- Wraps library-specific code
- Provides standardized interface: `fetch_content(url) -> str`
- Returns content or structured error
- Can be swapped with alternative implementation

**Extension Points**:
- New extraction rule types (currently: CSS, XPath, regex)
- Alternative type conversion strategies
- Additional failure categorization

## Testing Strategy

Tests are organized by layer:

- **Unit Tests**: Individual components (models, validators, formatters)
- **Integration Tests**: Component interactions (config → extraction → output)
- **End-to-End Tests**: Complete pipeline from URL to TOML file

Each test group focuses on critical user workflows, not exhaustive coverage.

## Future Enhancements

### Phase 2: Analytics Integration
- Metrics collection for reliability measurement
- Field-level success rate tracking
- Site-type-specific analytics

### Phase 3: Advanced Features
- LLM-based post-processing
- Batch mode for multiple URLs
- Advanced extraction strategies

### Phase 4: Optimization
- Performance profiling and optimization
- Caching strategies
- Distributed scraping

## Design Principles

1. **Separation of Concerns**: Each layer has distinct responsibility
2. **Fail Gracefully**: Partial success preferred over total failure
3. **Track Everything**: Metadata enables future analysis
4. **Be Extensible**: Configuration and rule systems support discovery
5. **Keep It Simple**: Avoid over-engineering during prototype phase
6. **Library Agnostic**: Architecture supports swapping scraping libraries

## Known Limitations and TODOs

- Site type detection uses simple URL pattern matching (can be enhanced)
- Type conversion uses basic heuristics (can be refined with data)
- Configuration schema flexible but undocumented edge cases may exist
- Library swapping abstraction designed but not tested with alternatives

See KNOWN_ISSUES.md for complete list.
