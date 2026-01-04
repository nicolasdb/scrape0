# Specification: Core Scraping with Modular Architecture

## Goal

Build a modular, production-ready scraping module using an Input-Process-Output architecture that extracts priority facility data (name, location, expertise, URL, contact) from single URLs with graceful failure handling, comprehensive metadata tracking, and TOML serialization. This foundation enables reliable data extraction while supporting future library swapping and Phase 2 reliability measurement.

## User Stories

- As a developer, I want to configure extraction rules for new sites without modifying core scraping code so that I can add new facilities independently and quickly.
- As a reliability analyst, I want to understand why extraction failed (which fields, what errors) so that I can improve scraping patterns and debug reliability issues.
- As a future system integrator, I want to swap Scrapling for alternative scraping libraries with minimal code changes so that we can test and compare different extraction approaches.

## Specific Requirements

### Input Layer

**Configuration Loading & Validation**
- Load a single unified TOML configuration file at startup containing site-specific extraction rules
- Validate configuration structure and provide clear error messages for invalid files
- Support graceful degradation if optional configuration fields are missing
- Allow configuration to evolve during implementation without requiring complete schema upfront
- Configuration file location: configurable via environment variable or CLI argument with sensible default

**URL Input Handling**
- Accept single URL as input parameter (string format)
- Validate URL format before attempting scraping (basic HTTP/HTTPS validation)
- Normalize URLs to handle common variants (trailing slashes, www prefix variations)
- Fail explicitly with clear message if URL is invalid before attempting scraping operation

**Raw Content Acquisition**
- Retrieve raw HTML/web content from target URL using Scrapling library
- Implement basic retry logic for transient failures (network timeouts, temporary 5xx errors)
- Set reasonable timeouts to prevent hanging on unresponsive sites
- Capture HTTP status codes and response headers for diagnostics

### Process Layer

**Field Extraction & Mapping**
- Extract priority fields: name, location, expertise, URL, contact info
- Support extraction of additional metadata fields defined in configuration (extensible)
- Apply site-specific extraction rules (CSS selectors, patterns, or Scrapling-specific extraction logic) from configuration
- Return structured data mapping field names to extracted values

**Type Conversion Pipeline**
- Accept raw string input from HTML extraction
- Implement basic type inference (detect strings, numbers, lists, booleans)
- Convert extracted strings to appropriate TOML-compatible types during processing
- Handle common patterns: comma-separated lists → arrays, "yes/no" strings → booleans, numeric strings → numbers
- Log conversion attempts and failures for debugging

**Graceful Partial Extraction**
- Continue processing even when individual field extraction fails
- Track which fields succeeded and which failed separately
- Collect metadata about each field's extraction status
- Do not halt pipeline for partial failures; return best-effort results

**Error Management & Failure Metadata**
- Capture structured error information for each failure (field name, error type, error message)
- Categorize failures: network errors, parsing errors, validation errors, timeout, missing data
- Store failure_reason at module level (site-wide extraction failure vs. field-level failures)
- Enable root cause analysis without exposing technical stack details in output

**Site Type Detection**
- Infer or detect site type based on URL pattern, content analysis, or configuration matching
- Store site_type in metadata for analytics tracking and pattern analysis
- Support custom site type definitions in configuration
- Enable future Phase 2 reliability measurement by site type

### Output Layer

**TOML Serialization**
- Generate valid TOML output structure for all extracted data
- Enforce TOML-compatible data types in final output
- Structure output for human readability and ease of manual editing if needed
- Include timestamp in UTC ISO format (extraction_timestamp field)

**Metadata Attachment**
- Include extraction metadata section with: success flag, extraction_timestamp, failure_reason, site_type
- Include fields_status section tracking: extracted (list), failed (list), not_found (list)
- Organize extracted data into logical sections: priority_fields, extra_metadata
- Preserve original field names and hierarchical structure from configuration

**File Output**
- Write TOML output to specified file path (default: TOML files in output directory)
- Handle file I/O errors gracefully with user-friendly messages
- Create output directory if it doesn't exist
- Support overwriting existing files with configurable behavior

**Analytics Hook Integration**
- Ensure metadata structure supports Phase 2 analytics queries
- Track success/failure at both module and field level
- Collect sufficient context for reliability dashboards (success rates, failure patterns)
- Enable analysis of extraction completeness and partial success scenarios

## Architecture

### IPO Model Overview

```
Input Layer          Process Layer          Output Layer
    |                    |                       |
    ├─ URL input         ├─ Field extraction     ├─ Type enforcement
    ├─ Config load       ├─ Type conversion      ├─ TOML serialization
    ├─ HTML fetch        ├─ Error capture        ├─ Metadata attachment
    └─ Validation        └─ Partial success      └─ File writing
```

### Component Interactions

**Configuration Manager**
- Responsible for loading, parsing, and validating TOML configuration file
- Exposes site-specific extraction rules to extraction engine
- Maintains configuration state for session lifetime
- Provides fallback defaults for missing optional fields

**Scraping Engine**
- Wraps Scrapling library with standardized interface
- Responsible for fetching raw HTML/content from target URL
- Implements retry logic and timeout management
- Returns raw content or structured error information
- Designed to allow library swapping by abstracting Scrapling behind interface

**Data Extraction Engine**
- Applies configuration rules to raw HTML content
- Executes field extraction with error handling per field
- Performs type conversion on extracted values
- Returns structured extraction result with success/failure metadata
- Tracks which fields succeeded, failed, and were not found

**TOML Output Formatter**
- Receives extraction results and metadata
- Ensures all values are TOML-compatible types
- Constructs hierarchical TOML structure (sections, subsections, arrays)
- Handles special cases (timestamps, arrays, nested structures)

**Module Interface (Public API)**
- Single entry point: scrape_facility(url: str, config_path: str) -> dict
- Returns dictionary with keys: success (bool), data (dict), metadata (dict), error (str or null)
- Data dict contains extracted fields organized by priority
- Metadata dict contains extraction_metadata, fields_status, timestamps
- Error field populated only on critical failures (config not found, network unavailable)

### Design Decisions

**Single Unified Configuration**
- Single TOML file reduces complexity vs. per-site configs
- Allows evolution during implementation without major refactoring
- Human-readable format supports version control and manual review
- Configuration structure intentionally flexible to accommodate discoveries

**Scrapling as Primary Library**
- Provides browser automation for JavaScript-heavy sites
- Superior to static scrapers for modern web applications
- Architecture designed to abstract Scrapling behind interface for future swapping
- Focus on Scrapling now; don't over-engineer abstraction prematurely

**Graceful Partial Failure**
- Aligns with real-world scraping where some fields may be unavailable
- Supports analytics measurement of extraction completeness
- Returns maximum useful data even when full extraction fails
- Metadata tracking enables diagnosis without breaking pipeline

**Type Conversion in Process Layer**
- Separates concerns: raw strings in, TOML-safe types out
- Keeps Input layer focused on HTML retrieval, Output layer on serialization
- Enables type conversion logic to be tested independently
- Supports future refinement of type detection heuristics

## Configuration Schema

### Structure (Draft, to be refined during implementation)

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
description = "Example Fablab site for testing"

[sites.fields.priority]
name = "selector or rule"
location = "selector or rule"
expertise = "selector or rule"
url = "selector or rule"
contact = "selector or rule"

[sites.fields.extra]
operating_hours = "selector or rule"
equipment = "selector or rule"

[output]
format = "toml"
include_metadata = true
directory = "./output"
```

### Configuration Flexibility

- Schema is intentionally loose; specific field extraction rules TBD during implementation
- Support for CSS selectors, XPath, regex patterns, or Scrapling-specific rules
- Configuration entries for field-level retry logic and validation rules to be added as needed
- No requirement to define all possible fields upfront; add them as discovered

### Configuration Evolution

- Capture and document extraction patterns discovered during implementation
- Refactor configuration structure iteratively based on actual site variations
- Update schema documentation as new site types are encountered
- Support version comments in configuration for tracking changes

## Data Models

### Input Configuration Model

```python
@dataclass
class SiteConfig:
    id: str
    url_pattern: str
    site_type: str
    priority_fields: Dict[str, str]  # field_name -> extraction_rule
    extra_fields: Dict[str, str]
    timeout_seconds: int
    max_retries: int

@dataclass
class ScraperConfig:
    sites: List[SiteConfig]
    primary_library: str
    default_timeout: int
    default_max_retries: int
```

### Extraction Result Model

```python
@dataclass
class ExtractionMetadata:
    success: bool
    extraction_timestamp: str  # ISO format
    failure_reason: Optional[str]  # "network_error", "timeout", "parse_error", etc.
    site_type: str
    extraction_duration_seconds: float

@dataclass
class FieldStatus:
    extracted: List[str]  # successfully extracted field names
    failed: List[str]     # fields that failed extraction
    not_found: List[str]  # fields defined in config but not present in content

@dataclass
class ExtractionResult:
    success: bool
    priority_fields: Dict[str, Any]
    extra_metadata: Dict[str, Any]
    metadata: ExtractionMetadata
    fields_status: FieldStatus
    error: Optional[str]  # Critical errors that prevented processing
```

### TOML Output Model

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
equipment = ["CNC router", "Laser cutter", "3D printer"]

[fields_status]
extracted = ["name", "location", "expertise", "url", "contact", "operating_hours"]
failed = ["equipment"]
not_found = []
```

## API/Interface

### Public Module Interface

```python
def scrape_facility(
    url: str,
    config_path: str = "./config.toml",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Scrape a single facility from the given URL.

    Args:
        url: Target URL to scrape
        config_path: Path to scraper configuration file
        output_path: Optional path to write TOML output file

    Returns:
        Dictionary with keys:
        - success (bool): Whether scraping succeeded
        - data (dict): Extracted data (priority_fields, extra_metadata)
        - metadata (dict): Extraction metadata and field status
        - error (str or None): Critical error message if applicable
    """
```

### Usage Example

```python
from scrape0.scraper import scrape_facility

result = scrape_facility(
    url="https://example-fablab.com",
    config_path="./scraper_config.toml",
    output_path="./output/example-fablab.toml"
)

if result['success']:
    print(f"Extracted: {result['data']['priority_fields']['name']}")
else:
    print(f"Extraction failed: {result['metadata']['failure_reason']}")
    print(f"Partially extracted: {result['metadata']['fields_status']['extracted']}")
```

### Return Value Format

```python
{
    'success': True,
    'data': {
        'priority_fields': {
            'name': 'Example Fablab',
            'location': 'San Francisco, CA',
            'expertise': ['3D printing', 'electronics'],
            'url': 'https://example.com',
            'contact': 'contact@example.com'
        },
        'extra_metadata': {
            'operating_hours': 'Mon-Fri 9am-6pm',
            'equipment': ['CNC', 'Laser cutter']
        }
    },
    'metadata': {
        'extraction_metadata': {
            'success': True,
            'extraction_timestamp': '2026-01-04T10:00:00Z',
            'failure_reason': None,
            'site_type': 'fablab',
            'extraction_duration_seconds': 2.3
        },
        'fields_status': {
            'extracted': ['name', 'location', 'expertise', 'url', 'contact'],
            'failed': ['equipment'],
            'not_found': []
        }
    },
    'error': None
}
```

## Error Handling

### Failure Modes & Graceful Degradation

**Critical Failures (Module Returns Error)**
- Configuration file not found or invalid TOML syntax
- Target URL validation failed (invalid format)
- Network unavailable or DNS resolution failed
- Module initialization error

**Partial Failures (Module Returns Success=False with Data)**
- Network timeout during scraping (after retries exhausted)
- HTML parsing error for specific fields
- Type conversion error for extracted values
- Extraction rule produced no results

**Field-Level Failures (Tracked in fields_status)**
- Individual field extraction rule failed
- Extracted value failed validation
- Required field missing from HTML content
- Type conversion failed for specific field

### Failure Reason Categorization

```python
# Standardized failure_reason values for analytics
FAILURE_REASONS = {
    'network_timeout': 'Request exceeded timeout limit',
    'network_error': 'Network connectivity issue',
    'parse_error': 'HTML parsing failed',
    'no_content': 'Empty or no content returned',
    'validation_error': 'Extracted data failed validation',
    'extraction_rule_error': 'Configuration rule produced invalid results',
    'unknown': 'Unexpected error during extraction'
}
```

### Retry Strategy

- Implement exponential backoff for transient network failures
- Retry on: timeouts, 5xx HTTP errors, connection resets
- Do not retry on: 4xx errors, validation failures, parsing errors
- Maximum retry count configurable (default: 3)
- Backoff multiplier configurable (default: 2.0, yielding waits of 1s, 2s, 4s)

### Resource Cleanup

- Close browser/connection contexts after scraping completes or fails
- Release file handles after TOML writing
- Implement context managers or equivalent cleanup mechanisms
- Log resource cleanup failures without breaking main pipeline

## Testing Strategy

### Unit Tests

**Configuration Loading**
- Valid TOML file loads correctly
- Invalid TOML syntax produces specific error
- Missing required fields handled gracefully
- Configuration evolution scenario (adding new fields) works

**Field Extraction**
- Each field extraction rule tested independently
- Extraction success cases with various HTML structures
- Extraction failures on missing data
- Type conversion scenarios (strings, arrays, booleans, numbers)

**TOML Output**
- Valid TOML produced from extraction result
- Metadata fields included correctly
- Field status tracking accurate
- TOML files parse back correctly

**Error Handling**
- Network timeout produces correct failure metadata
- Parsing error captured and categorized
- Partial extraction tracked accurately
- Graceful degradation on missing optional fields

### Integration Tests

**End-to-End Scraping**
- Single-URL scraping produces valid TOML output
- Configuration file correctly applies extraction rules
- Metadata and field status match actual results
- Output file written to correct path

**Configuration-Driven Extraction**
- Different site configurations produce correct field mappings
- Site type detection works as expected
- Extra metadata fields extracted when defined

**Error Scenarios**
- Invalid URL rejected before scraping attempt
- Network timeout handled with retries
- Missing configuration file produces clear error
- Partial failures return partial data with metadata

### Test Data & Fixtures

- Create mock HTML files for test sites
- Provide sample configuration files for testing
- Create test URLs (local or mock server) for network testing
- Document test site patterns used for different field types

## Scope Boundaries

### In Scope

- Single-URL scraping with Scrapling library
- Priority field extraction (name, location, expertise, URL, contact)
- Extra metadata collection (extensible via configuration)
- Type conversion pipeline (strings → basic types → TOML)
- Graceful partial extraction with metadata tracking
- TOML output format with metadata sections
- Site type detection and tracking
- Modular IPO architecture
- Configuration file management (single unified file)
- Error handling with structured failure metadata
- Retry logic for transient network failures
- Basic validation (URL format, TOML syntax)

### Out of Scope

- Batch mode / multi-URL processing (deferred to Phase 1 expansion)
- LLM agents for post-processing or data refinement (Phase 3+)
- Complete schema metadata design upfront (prototype goal; to be refined during implementation)
- Library abstraction layer over-engineering (design for swappability, but focus on Scrapling)
- Vector embedding preparation (future capability; not implemented now)
- Reliability testing framework (Phase 2 focus)
- Data quality scoring (Phase 3)
- Search and discovery interface (Phase 4)
- Scheduling and orchestration (separate Phase 1 component)

## Known Unknowns

### Schema Metadata Structure (TBD)

The exact structure for storing schema information (field types, constraints, patterns) will be determined during implementation as actual scraping patterns emerge. Current model is placeholder; expect evolution.

### Configuration Extraction Rules Format (TBD)

Specific syntax for extraction rules (CSS selectors vs. XPath vs. Scrapling-specific format vs. regex patterns) will be finalized based on what works best with Scrapling in practice. Configuration schema intentionally loose to allow exploration.

### Library Swapping Abstraction (TBD)

The specific abstraction mechanism for swapping scraping libraries (interface definition, plugin pattern, adapter pattern, factory) will be designed during implementation. Current architecture assumes Scrapling; abstraction points TBD.

### Failure Reason Categorization (TBD)

Complete taxonomy of failure_reason values and error codes will be refined as edge cases discovered. Initial set provided; expect expansion and refinement.

### Type Conversion Heuristics (TBD)

Rules for detecting and converting types (when to convert string to number, when to split string into array, etc.) will be refined based on actual extracted data patterns. Current proposal: strings, numbers, lists, booleans; refinement expected.

### Site Type Detection Method (TBD)

Mechanism for automatically detecting site type (URL pattern matching, content analysis, configuration lookup) will be finalized during implementation. May use multiple strategies.

## Dependencies

### External Libraries

- **Scrapling** (primary scraping engine, swappable)
- **tomli / toml** (TOML parsing and serialization for Python)
- **requests** or **httpx** (HTTP client, likely pulled in by Scrapling)

### Internal Dependencies

- Configuration management system (to be built)
- Type conversion utilities (to be built)
- Error/exception handling following project standards
- Python logging (per tech stack standard)

### Development Dependencies

- pytest (unit/integration testing)
- pytest-cov (test coverage)
- Black or similar (code formatting per coding-style.md)
- mypy (optional; type checking)

## Phase 2 Readiness

### Analytics Foundation

The core scraping module is designed to support Phase 2 reliability measurement:

**Metadata Collection**
- extraction_timestamp: enables tracking of scraping time and frequency
- success flag: binary signal for success/failure rates per site and field
- failure_reason: enables categorization of failure types for root cause analysis
- site_type: enables grouping and comparison across facility categories
- extraction_duration_seconds: enables performance tracking

**Field-Level Tracking**
- fields_status structure tracks extracted/failed/not_found for each field
- Enables calculation of field-specific success rates
- Supports measurement of extraction completeness
- Fields missing from config can be added to extra_metadata for analytics

**Partial Success Handling**
- Graceful partial extraction enables measurement of partial success scenarios
- Allows analysis of which field combinations frequently fail together
- Supports identification of site-type-specific challenges

### Metrics Ready Structure

TOML output structure is designed to support Phase 2 metrics queries:
- Success flag accessible at top level for aggregation
- Site type accessible at top level for filtering and grouping
- Field status provides granularity for field-level metrics
- Timestamp enables time-series analysis

### Configuration for Reliability Testing

Configuration structure supports future multi-method testing (Phase 2, item #7):
- Site definitions can be extended with multiple extraction approaches
- Scraper library field makes library swapping straightforward
- Extra metadata fields enable testing alternative extraction patterns

## Implementation Notes

### Prototyping Mindset

This specification is written with the expectation of iteration and discovery:
- Configuration schema will evolve as site patterns are encountered
- Type conversion rules will be refined based on actual data
- Error categorization may be expanded with new failure modes
- Library swapping approach will be defined through prototyping

### Vertical Slice Approach

Implementation should follow a vertical slice pattern per project conventions:
- Build end-to-end scraping for one example site first
- Get configuration → scraping → extraction → TOML output working
- Then add more sites and fields incrementally
- Test each addition before moving to next complexity

### Quality Standards

Adhere to project coding standards:
- Follow coding-style.md for naming, formatting, function size
- Follow error-handling.md for exception handling and resource cleanup
- Follow validation.md for input validation strategy
- Use meaningful names and small, focused functions
- Remove dead code and maintain DRY principle

