# Changelog: Core Scraping Module

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-01-04

### Initial Release

This is the first production-ready release of the Core Scraping Module with complete Input-Process-Output architecture.

#### Features Added

##### Phase 0: Foundation
- Project structure and dependencies setup
- Python virtual environment configuration
- Testing infrastructure (pytest, coverage)
- Code formatting (Black) and type checking (mypy)
- Version control with git

##### Phase 1: Core Architecture
- **Data Models**: SiteConfig, ScraperConfig, ExtractionResult, ExtractionMetadata, FieldStatus
- **Type System**: TypeConverter for string → bool/number/list conversion
- **Configuration Management**: ConfigManager for TOML loading and parsing
- **URL Validation**: URLValidator with normalization and HTTPs scheme enforcement
- **Input Layer**: InputLayer coordinating validation and config lookup

##### Phase 2: Single Example Site Implementation
- **Scraping Engine**: ScrapingEngine wrapper around Scrapling library
- **Retry Logic**: Exponential backoff for transient failures (1s, 2s, 4s default)
- **Extraction Engine**: Field extraction with CSS selector, XPath, and regex support
- **Rule Parser**: Automatic detection of extraction rule types
- **TOML Output**: TOMLOutputFormatter generating valid TOML with metadata
- **File I/O**: FileOutput class for writing TOML files
- **Public API**: scrape_facility() main entry point

##### Phase 3: Configuration & Extensibility
- **Multiple Sites**: Support for multiple site configurations in single TOML file
- **Extra Fields**: Extensible metadata fields beyond priority fields
- **Site-Specific Overrides**: Per-site timeout and retry configuration
- **Configuration Evolution**: Flexible schema supporting schema changes without code updates
- **Multiple Rule Types**: Full support for CSS selectors, XPath, and regex patterns

##### Phase 4: Error Handling & Robustness
- **Error Categorization**: Standardized failure_reason values (network_timeout, parse_error, etc.)
- **Exception Hierarchy**: ScrapingError base with NetworkError, ExtractionError subclasses
- **Graceful Degradation**: Extraction continues on individual field failures
- **Partial Success Tracking**: FieldStatus tracking extracted/failed/not_found
- **Logging Throughout**: Comprehensive logging at all major operations
- **Diagnostic Metadata**: Collection of duration, site_type, timestamps for analytics

##### Phase 5: Testing & Validation
- **177 Focused Tests**: Comprehensive test coverage across all features
- **Gap-Filling Tests**: 10 strategic integration tests for critical workflows
- **Test Documentation**: TESTING_PLAN.md and TEST_RESULTS.md

##### Phase 6: Documentation & Polish
- **Code Formatting**: Black formatter applied
- **Type Checking**: MyPy type validation
- **Comprehensive README**: Usage guide and quick start
- **Configuration Examples**: config.toml.example with detailed comments
- **Troubleshooting Guide**: TROUBLESHOOTING.md for common issues
- **Architecture Documentation**: ARCHITECTURE.md explaining IPO design
- **Configuration Evolution**: CONFIG_EVOLUTION.md documenting schema evolution

#### Features

##### Supported Extraction Rules
- CSS Selectors: `h1.name`, `div.container span.field`, `#main-title`
- XPath: `//h1[@class='name']`, `//div[@id='main']/span`
- Regex Patterns: `/[A-Z][a-z]+/`, `^[0-9]{2,4}-[0-9]{2}-[0-9]{2}`

##### Type Conversions
- Boolean: yes/no, true/false, 1/0 → bool
- Numbers: 42, 3.14 → int/float
- Lists: "item1, item2" → array
- Strings: passthrough with whitespace cleanup

##### Output Format
- Valid TOML with metadata sections
- Priority fields and extra metadata separation
- Field status tracking (extracted/failed/not_found)
- ISO 8601 timestamps with UTC timezone
- Extraction duration tracking

##### Configuration
- Single unified TOML configuration file
- Multiple site definitions
- Per-site field extraction rules
- Site-specific timeout and retry overrides
- Optional extra metadata fields

##### Error Handling
- Critical failures with clear error messages
- Partial success with data and failure_reason
- Field-level error recovery
- Structured exception hierarchy

#### Architecture

**Input-Process-Output Model**:
- Input Layer: URL validation, config loading, HTML fetching
- Process Layer: Field extraction, type conversion, error handling
- Output Layer: TOML formatting, file writing, metadata attachment

**Modular Design**:
- ConfigManager: Configuration management
- InputLayer: Input coordination
- ScrapingEngine: HTML fetching (Scrapling wrapper)
- ExtractionEngine: Field extraction
- TOMLOutputFormatter: Output formatting
- FileOutput: File I/O

#### Known Limitations

These features are deferred to future phases:

1. **Batch Processing**: Only single-URL scraping currently (Phase 1 expansion)
2. **Database Integration**: No database layer (Phase 2+)
3. **LLM Post-Processing**: Deferred to Phase 3+
4. **Authentication**: No auth support yet
5. **Vector Embeddings**: Deferred to Phase 3+

#### Testing

- **177 Tests**: Comprehensive coverage of all features
- **0% Failure Rate**: All tests passing
- **100% Test Pass Rate**: Complete test coverage for implemented features
- **Fast Execution**: Full suite runs in ~10 seconds

Test breakdown:
- Unit tests: 140 tests
- Integration tests: 37 tests
- Total coverage: All public APIs and critical workflows

#### Documentation

- README.md: Quick start and feature overview
- spec.md: Complete specification with design decisions
- ARCHITECTURE.md: System architecture and design patterns
- CONFIG_EVOLUTION.md: Configuration schema and evolution guide
- TROUBLESHOOTING.md: Common issues and solutions
- TESTING_PLAN.md: Test coverage and methodology
- TEST_RESULTS.md: Test execution results

#### Dependencies

Core:
- scrapling: Web scraping library with browser automation
- tomli: TOML parsing library
- beautifulsoup4: HTML parsing

Development:
- pytest: Test framework
- pytest-cov: Coverage reporting
- black: Code formatter
- mypy: Type checker

#### Requirements

- Python 3.9+
- Linux/macOS/Windows

#### Future Enhancements

##### Phase 1 Expansion
- Batch mode for multi-URL scraping
- Parallelization for speed
- Progress tracking and reporting

##### Phase 2: Analytics & Reliability
- Reliability measurement framework
- Success rate tracking by site and field
- Multi-method extraction comparison
- Analytics dashboard support

##### Phase 3: Data Quality & LLM
- LLM-based post-processing
- Data quality scoring
- Confidence estimation
- Manual review workflow

##### Phase 4: Discovery & Search
- Facility discovery interface
- Search and filtering
- Mapping and visualization
- API for external systems

#### Contributors

Initial implementation: 2026-01-04

#### License

TBD

---

## Release Checklist

- [x] All phases 0-6 complete
- [x] 177 tests passing (100%)
- [x] Code formatted with Black
- [x] Type checking with MyPy
- [x] Documentation complete
- [x] Example configuration provided
- [x] Troubleshooting guide available
- [x] Architecture documented
- [x] Public API stable

## Next Release

Version 0.2.0 will include:

- Batch mode for multi-URL scraping
- Enhanced retry strategies
- More extraction rule types
- Additional metadata collection
- Performance optimizations
