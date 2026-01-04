# Task Breakdown: Core Scraping Module with Modular Architecture

## Overview

This task breakdown implements a modular, production-ready scraping module using an Input-Process-Output architecture. The implementation follows a vertical slice approach: build one complete, working example end-to-end first, then expand with additional sites and features incrementally.

**Total Tasks**: 45 subtasks across 6 phases
**Estimated Duration**: 2-3 weeks for full implementation
**Key Constraint**: Each task should take 1-3 hours of focused work

---

## Task List

### Phase 0: Setup & Foundation

#### Task Group 0.1: Project Structure and Dependencies
**Dependencies**: None
**Duration**: 2-3 hours

- [ ] 0.1.1 Create project directory structure
  - Create `/scraper/` directory with `__init__.py`
  - Create `/tests/` directory with test fixtures
  - Create `/config/` directory for configuration files
  - Create `/output/` directory for TOML output files
  - Create `/docs/` directory for implementation notes
  - Verify all directories have proper Python packages initialized

- [ ] 0.1.2 Initialize Python environment and virtual environment
  - Create `requirements.txt` with core dependencies
  - Include: scrapling, tomli (or toml), pytest, pytest-cov, black, mypy
  - Create `requirements-dev.txt` for development tools
  - Document Python version requirement (3.9+)
  - Activate venv as per CLAUDE.md guidelines

- [ ] 0.1.3 Set up version control and initial commit
  - Create `.gitignore` for Python artifacts, venv, output files, test caches
  - Create initial `README.md` describing module purpose
  - Create `ARCHITECTURE.md` documenting IPO model
  - Make initial commit with project structure

- [ ] 0.1.4 Configure testing infrastructure
  - Create `pytest.ini` with test discovery patterns
  - Create `conftest.py` for shared fixtures
  - Set up code formatting with Black (style.toml or .black)
  - Set up mypy configuration for type checking
  - Run initial tests to verify pytest works

**Acceptance Criteria**:
- Project directory structure created and properly organized
- Virtual environment functional and activated
- All dependencies installed successfully
- First test runs without errors
- Code can be formatted with Black

---

### Phase 1: Core Architecture & IPO Layers - Foundation

#### Task Group 1.1: Data Models and Type System
**Dependencies**: Phase 0
**Duration**: 2.5 hours

- [ ] 1.1.1 Write 4-6 focused tests for data models
  - Test SiteConfig creation with required fields
  - Test ExtractionResult construction and validation
  - Test ExtractionMetadata timestamp generation
  - Test FieldStatus tracking (extracted/failed/not_found lists)
  - Skip exhaustive edge case testing; focus on happy path only

- [ ] 1.1.2 Define configuration data models
  - Create `SiteConfig` dataclass (id, url_pattern, site_type, priority_fields dict, extra_fields dict, timeout_seconds, max_retries)
  - Create `ScraperConfig` dataclass (sites list, primary_library, default_timeout, default_max_retries)
  - Add basic field validation in __post_init__ methods
  - Document fields with purpose comments

- [ ] 1.1.3 Define extraction result data models
  - Create `ExtractionMetadata` dataclass (success, extraction_timestamp, failure_reason, site_type, extraction_duration_seconds)
  - Create `FieldStatus` dataclass (extracted list, failed list, not_found list)
  - Create `ExtractionResult` dataclass (success, priority_fields dict, extra_metadata dict, metadata, fields_status, error)
  - Add timestamp generation utility in ISO format

- [ ] 1.1.4 Create type conversion utilities
  - Create `TypeConverter` class with static methods for converting strings to basic types
  - Implement `convert_to_bool()` (yes/no, true/false, 1/0)
  - Implement `convert_to_number()` (detect int vs float)
  - Implement `convert_to_list()` (comma-separated, semicolon-separated)
  - Implement `convert_to_string()` (passthrough with cleanup)
  - Add validation that outputs are TOML-compatible types

- [ ] 1.1.5 Run tests for data models
  - Execute only the 4-6 tests written in 1.1.1
  - Verify all models instantiate correctly
  - Confirm type conversion produces expected outputs
  - Do NOT run full test suite

**Acceptance Criteria**:
- 4-6 focused tests pass
- All data models have clear field definitions
- Type conversion handles basic cases (strings, numbers, lists, booleans)
- Models are TOML-serializable
- Timestamp generation works in ISO format

---

#### Task Group 1.2: Configuration Management System
**Dependencies**: Task Group 1.1
**Duration**: 2.5 hours

- [ ] 1.2.1 Write 4-6 focused tests for configuration loading
  - Test valid TOML file loads successfully
  - Test invalid TOML syntax produces specific error
  - Test missing optional fields use defaults
  - Test URL pattern matching for site lookup
  - Skip comprehensive schema validation tests; focus on critical path

- [ ] 1.2.2 Create configuration file parser
  - Create `ConfigManager` class
  - Implement `load_config(config_path)` method using tomli
  - Handle file not found with clear error message
  - Handle TOML syntax errors with clear error message
  - Return `ScraperConfig` object on success

- [ ] 1.2.3 Implement configuration validation
  - Validate required fields in scraper section (primary_library)
  - Validate site entries have id, url_pattern, site_type
  - Provide default values for optional fields (timeout_seconds=30, max_retries=3)
  - Allow configuration to evolve: don't require all fields upfront
  - Document validation rules in code comments

- [ ] 1.2.4 Implement site lookup by URL
  - Create `lookup_site_config(url)` method
  - Match URL against site url_pattern values
  - Support simple string matching (url_pattern is substring of URL)
  - Return matching `SiteConfig` or raise clear error
  - Cache lookups if same URL checked multiple times

- [ ] 1.2.5 Run tests for configuration management
  - Execute only the 4-6 tests written in 1.2.1
  - Verify configuration loads and validates correctly
  - Confirm site lookup finds correct sites by URL
  - Do NOT run full test suite

**Acceptance Criteria**:
- 4-6 focused tests pass
- Configuration loads from TOML file successfully
- Invalid configurations produce clear error messages
- Site lookup by URL works correctly
- Default values applied for missing optional fields

---

#### Task Group 1.3: URL Validation and Input Layer
**Dependencies**: Task Group 1.2
**Duration**: 2 hours

- [ ] 1.3.1 Write 3-5 focused tests for URL validation
  - Test valid HTTP/HTTPS URLs accepted
  - Test invalid URLs (no scheme, malformed) rejected
  - Test URL normalization (www variants, trailing slashes)
  - Skip comprehensive URL validation; focus on basic cases

- [ ] 1.3.2 Create URL validator
  - Create `URLValidator` class
  - Implement `validate(url)` method checking for http/https scheme
  - Implement `normalize(url)` method (add https if no scheme, strip trailing slashes)
  - Raise `URLValidationError` for invalid URLs with clear message
  - Return normalized URL on success

- [ ] 1.3.3 Implement input layer interface
  - Create `InputLayer` class
  - Implement `__init__(config_manager: ConfigManager)` to store config reference
  - Implement `validate_and_normalize_url(url)` using URLValidator
  - Implement `lookup_site_config(url)` delegating to ConfigManager
  - Document that this layer focuses on validation, not fetching

- [ ] 1.3.4 Run tests for URL validation
  - Execute only the 3-5 tests written in 1.3.1
  - Verify valid URLs pass validation
  - Verify invalid URLs are rejected
  - Confirm normalization works correctly

**Acceptance Criteria**:
- 3-5 focused tests pass
- Valid HTTP/HTTPS URLs accepted
- Invalid URLs rejected with clear messages
- URL normalization handles common cases
- Site configuration lookup works after validation

---

### Phase 2: Single Example Site (Vertical Slice) - End-to-End Working Example

#### Task Group 2.1: Mock Scraping Engine
**Dependencies**: Task Group 1.3
**Duration**: 2.5 hours

- [ ] 2.1.1 Write 4-6 focused tests for scraping engine
  - Test successful HTML fetch from URL
  - Test retry logic on transient failures
  - Test timeout handling
  - Test connection error handling
  - Skip exhaustive retry scenarios; test happy path and one failure case

- [ ] 2.1.2 Create Scrapling engine wrapper
  - Create `ScrapingEngine` class
  - Implement `__init__(config: ScraperConfig)` storing timeout and retry settings
  - Implement `fetch_content(url)` method using Scrapling library
  - Return raw HTML content string on success
  - Document that this class abstracts Scrapling for future library swapping

- [ ] 2.1.3 Implement retry logic with exponential backoff
  - Add retry loop to `fetch_content()`
  - Retry on: connection errors, timeouts, 5xx HTTP errors
  - Do NOT retry on: 4xx errors, validation failures
  - Implement exponential backoff (default: 2.0x multiplier)
  - Log each retry attempt with timestamp

- [ ] 2.1.4 Add timeout and connection error handling
  - Set timeout for each request (from config)
  - Capture specific error types: `TimeoutError`, `ConnectionError`, `HTTPError`
  - Return structured error object with error_type and message
  - Preserve HTTP status codes for diagnostics

- [ ] 2.1.5 Run tests for scraping engine
  - Execute only the 4-6 tests written in 2.1.1
  - Verify content fetching works
  - Test retry logic executes on transient failures
  - Confirm timeout is enforced
  - Do NOT run full test suite

**Acceptance Criteria**:
- 4-6 focused tests pass
- HTML content successfully fetched from working URLs
- Retry logic works with exponential backoff
- Timeouts enforced correctly
- Error information captured for diagnostics

---

#### Task Group 2.2: Data Extraction Engine - Single Example Site
**Dependencies**: Task Group 2.1
**Duration**: 3 hours

- [ ] 2.2.1 Write 4-6 focused tests for field extraction
  - Test extraction of all 5 priority fields from example site
  - Test partial extraction (some fields found, others missing)
  - Test missing field tracking in FieldStatus
  - Test field extraction with different selector styles
  - Focus on single site happy path; skip multi-site complexity

- [ ] 2.2.2 Create extraction rule executor
  - Create `ExtractionEngine` class
  - Implement `__init__(config: ScraperConfig)` storing config reference
  - Create `apply_extraction_rules(html_content, site_config)` method
  - Support CSS selector rules (primary format for example site)
  - Return dict of field_name -> extracted_value

- [ ] 2.2.3 Implement field-level error handling
  - Wrap each field extraction in try-except
  - Track successes in `FieldStatus.extracted`
  - Track failures in `FieldStatus.failed` with error messages
  - Track not_found (rules matched but returned empty)
  - Continue processing remaining fields on individual failures

- [ ] 2.2.4 Integrate type conversion
  - After successful extraction, apply `TypeConverter` to each value
  - Store original extracted value and converted value
  - Log conversion attempts and failures
  - Keep raw values available for debugging if needed

- [ ] 2.2.5 Implement site type detection
  - Detect site type by matching URL against site config patterns
  - Store detected site_type in metadata
  - Support fallback to "unknown" if no match found
  - Enable site type tracking for analytics

- [ ] 2.2.6 Run tests for extraction engine
  - Execute only the 4-6 tests written in 2.2.1
  - Verify all priority fields extracted from example site
  - Test partial extraction scenarios
  - Confirm field status tracking accurate
  - Do NOT run full test suite

**Acceptance Criteria**:
- 4-6 focused tests pass
- All 5 priority fields successfully extracted from example site
- Partial extraction tracked with FieldStatus
- Type conversion applied to extracted values
- Site type detection works
- Field-level errors don't halt pipeline

---

#### Task Group 2.3: TOML Output Formatter - Single Example Site
**Dependencies**: Task Group 2.2
**Duration**: 2.5 hours

- [ ] 2.3.1 Write 3-5 focused tests for TOML serialization
  - Test valid TOML output from extraction result
  - Test metadata section included correctly
  - Test fields_status section accurate
  - Test TOML can be parsed back and matches input
  - Skip complex TOML structures; focus on basic output

- [ ] 2.3.2 Create TOML output formatter
  - Create `TOMLOutputFormatter` class
  - Implement `format_result(extraction_result)` method
  - Organize output into sections: [extraction_metadata], [priority_fields], [extra_metadata], [fields_status]
  - Ensure all values are TOML-compatible types
  - Return TOML string

- [ ] 2.3.3 Build metadata section in TOML
  - Include success (bool)
  - Include extraction_timestamp (ISO format)
  - Include extraction_duration_seconds (float)
  - Include failure_reason (string or null)
  - Include site_type (string)
  - Document what each field means

- [ ] 2.3.4 Build data sections and status section
  - Serialize priority_fields dict as [priority_fields] section
  - Serialize extra_metadata dict as [extra_metadata] section (if present)
  - Serialize fields_status with extracted, failed, not_found lists
  - Handle arrays in TOML correctly
  - Preserve field names from configuration

- [ ] 2.3.5 Run tests for TOML formatter
  - Execute only the 3-5 tests written in 2.3.1
  - Verify TOML output is valid and parseable
  - Confirm metadata included correctly
  - Test field status section accurate
  - Do NOT run full test suite

**Acceptance Criteria**:
- 3-5 focused tests pass
- TOML output is valid and parseable
- All sections included (metadata, priority_fields, extra_metadata, fields_status)
- TOML structure matches specification format
- Values are TOML-compatible types

---

#### Task Group 2.4: File Output and I/O
**Dependencies**: Task Group 2.3
**Duration**: 1.5 hours

- [ ] 2.4.1 Write 2-3 focused tests for file output
  - Test TOML file written to specified path
  - Test output directory created if missing
  - Test file overwrite behavior
  - Skip complex I/O error scenarios

- [ ] 2.4.2 Implement file output functionality
  - Create `FileOutput` class
  - Implement `write_toml(toml_string, output_path)` method
  - Create output directory if it doesn't exist
  - Write TOML string to file
  - Handle file I/O errors with clear messages
  - Return path to written file

- [ ] 2.4.3 Add file management helpers
  - Implement method to construct default output filename from site name and timestamp
  - Support relative and absolute paths
  - Add method to verify file was written correctly (read back and validate)
  - Log file operations for debugging

- [ ] 2.4.4 Run tests for file output
  - Execute only the 2-3 tests written in 2.4.1
  - Verify TOML files written successfully
  - Confirm directory creation works
  - Do NOT run full test suite

**Acceptance Criteria**:
- 2-3 focused tests pass
- TOML files written to correct paths
- Output directories created when needed
- File I/O errors handled gracefully
- Written files are valid TOML

---

#### Task Group 2.5: Public API - scrape_facility() Function
**Dependencies**: Task Group 2.4
**Duration**: 2 hours

- [ ] 2.5.1 Write 5-7 focused end-to-end tests
  - Test complete scraping pipeline from URL to TOML output
  - Test success case with full data extraction
  - Test partial failure case with some fields extracted
  - Test critical failure (bad config, invalid URL)
  - Test return value structure matches specification
  - Focus on single example site; skip multi-site testing

- [ ] 2.5.2 Implement scrape_facility() main function
  - Create function signature: `scrape_facility(url, config_path, output_path=None)`
  - Initialize all layers (Config, Input, Scraping, Extraction, Output)
  - Call each layer in sequence: validate URL -> fetch HTML -> extract fields -> format TOML -> write file
  - Measure extraction_duration_seconds
  - Return dict with success, data, metadata, error

- [ ] 2.5.3 Implement error handling in main function
  - Catch config loading errors -> return error
  - Catch URL validation errors -> return error
  - Catch critical network errors -> return error with fields that were extracted
  - Allow partial successes to return success=False with data
  - Ensure all error paths populate error field in response

- [ ] 2.5.4 Implement execution flow documentation
  - Add docstring explaining parameter meanings
  - Document return value structure and each field
  - Add usage example in docstring
  - Add code comments for each major step
  - Link to specification for detailed behavior

- [ ] 2.5.5 Run end-to-end tests
  - Execute only the 5-7 tests written in 2.5.1
  - Test full pipeline with example site
  - Verify return value structure correct
  - Confirm TOML output file created
  - Do NOT run full test suite

**Acceptance Criteria**:
- 5-7 focused end-to-end tests pass
- Complete scraping pipeline works from URL to file output
- Return value matches specification format
- Error handling covers critical failure modes
- Single example site fully functional

---

### Phase 3: Configuration & Extensibility

#### Task Group 3.1: Expanded Configuration Schema
**Dependencies**: Task Group 2.5
**Duration**: 2 hours

- [ ] 3.1.1 Write 3-4 focused tests for advanced configuration
  - Test multiple sites defined in single config
  - Test extra_fields extraction alongside priority fields
  - Test site-specific timeout and retry overrides
  - Skip comprehensive config variation testing

- [ ] 3.1.2 Expand configuration schema documentation
  - Create detailed `config.toml.example` file with all supported options
  - Document each field and its purpose
  - Include examples for priority_fields and extra_fields
  - Document optional fields and their defaults
  - Add comments about configuration evolution

- [ ] 3.1.3 Extend ConfigManager for extra fields
  - Update `SiteConfig` to properly parse extra_fields
  - Update extraction engine to extract extra_fields alongside priority fields
  - Store extra fields in ExtractionResult.extra_metadata
  - Ensure extra fields appear in output TOML

- [ ] 3.1.4 Run advanced configuration tests
  - Execute only the 3-4 tests written in 3.1.1
  - Verify multiple sites can be configured
  - Test extra_fields extraction
  - Do NOT run full test suite

**Acceptance Criteria**:
- 3-4 focused tests pass
- Multiple sites can be configured and looked up
- Extra fields extracted alongside priority fields
- Configuration schema documented with examples

---

#### Task Group 3.2: Support for Additional Scraping Rules
**Dependencies**: Task Group 3.1
**Duration**: 2.5 hours

- [ ] 3.2.1 Write 3-4 focused tests for rule variations
  - Test CSS selector extraction (primary)
  - Test XPath extraction (alternative)
  - Test regex pattern extraction
  - Skip Scrapling-specific rules; focus on common extraction methods

- [ ] 3.2.2 Create rule parser and dispatcher
  - Create `RuleParser` class
  - Implement `parse_rule(rule_string)` to detect rule type (css_selector, xpath, regex)
  - Create `Rule` base class with subclasses: `CSSRule`, `XPathRule`, `RegexRule`
  - Each rule type has `extract(html_content)` method

- [ ] 3.2.3 Implement CSS selector rules
  - Use BeautifulSoup or Scrapling's CSS selector support
  - Extract matching element text content
  - Handle multiple matches (return as list if multiple)
  - Return empty string if no matches

- [ ] 3.2.4 Implement alternative extraction rules
  - Implement `XPathRule` using lxml or Scrapling's XPath support
  - Implement `RegexRule` using Python regex
  - Each returns extracted value or empty string
  - Update extraction engine to use rule dispatcher

- [ ] 3.2.5 Run tests for rule variations
  - Execute only the 3-4 tests written in 3.2.1
  - Verify CSS selectors work
  - Test alternative rule types
  - Do NOT run full test suite

**Acceptance Criteria**:
- 3-4 focused tests pass
- CSS selector rules work as primary method
- Alternative rule types (XPath, regex) supported
- Rules integrated into extraction engine

---

### Phase 4: Error Handling & Robustness

#### Task Group 4.1: Comprehensive Error Categorization
**Dependencies**: Task Group 3.2
**Duration**: 2 hours

- [ ] 4.1.1 Write 3-4 focused tests for error categorization
  - Test network timeout -> failure_reason=network_timeout
  - Test parse error -> failure_reason=parse_error
  - Test missing config -> failure_reason=config_error
  - Test extraction rule error -> failure_reason=extraction_rule_error

- [ ] 4.1.2 Create error categorization system
  - Create `ErrorCategory` enum: NETWORK_TIMEOUT, NETWORK_ERROR, PARSE_ERROR, NO_CONTENT, VALIDATION_ERROR, EXTRACTION_RULE_ERROR, CONFIG_ERROR, UNKNOWN
  - Create `FailureReason` class mapping exceptions to error categories
  - Implement `categorize_error(exception)` method
  - Store failure_reason string (standardized names) in metadata

- [ ] 4.1.3 Enhance exception hierarchy
  - Create base `ScrapingError` exception class
  - Create specific exception types: `URLValidationError`, `ConfigurationError`, `NetworkError`, `ExtractionError`, `ParsingError`, `TypeConversionError`
  - Use meaningful exception messages for debugging
  - Ensure exceptions include error category information

- [ ] 4.1.4 Run error categorization tests
  - Execute only the 3-4 tests written in 4.1.1
  - Verify errors categorized correctly
  - Test failure_reason populated accurately
  - Do NOT run full test suite

**Acceptance Criteria**:
- 3-4 focused tests pass
- Error categories standardized
- All error types map to failure_reason values
- Exceptions include category information

---

#### Task Group 4.2: Graceful Degradation and Partial Success
**Dependencies**: Task Group 4.1
**Duration**: 2 hours

- [ ] 4.2.1 Write 3-4 focused tests for partial failures
  - Test extraction with some fields found, others missing
  - Test field extraction failure doesn't halt pipeline
  - Test partial result returned with success=False
  - Test fields_status accurate for mixed success/failure

- [ ] 4.2.2 Implement graceful partial extraction
  - Update ExtractionEngine to track field-level successes and failures
  - Continue extraction loop even when individual fields fail
  - Populate FieldStatus.failed with field names that errored
  - Populate FieldStatus.not_found with fields that had no matches

- [ ] 4.2.3 Create partial success detection logic
  - Determine success vs failure based on: did ANY critical fields extract?
  - If priority_fields has at least some values -> success=True
  - If NO priority fields extracted -> success=False
  - Document success criteria in code comments

- [ ] 4.2.4 Run partial failure tests
  - Execute only the 3-4 tests written in 4.2.1
  - Verify pipeline continues on field errors
  - Test partial results returned correctly
  - Confirm fields_status accurate
  - Do NOT run full test suite

**Acceptance Criteria**:
- 3-4 focused tests pass
- Individual field failures don't halt extraction
- Partial success scenarios handled gracefully
- Fields_status accurately tracks field-level outcomes

---

#### Task Group 4.3: Logging and Diagnostics
**Dependencies**: Task Group 4.2
**Duration**: 1.5 hours

- [ ] 4.3.1 Write 2-3 focused tests for logging
  - Test that errors logged with appropriate severity
  - Test that extraction steps logged for debugging
  - Test that sensitive information not logged (URLs can be logged)

- [ ] 4.3.2 Implement logging throughout pipeline
  - Add logger to each major class (ConfigManager, ScrapingEngine, ExtractionEngine, etc.)
  - Log configuration loading and validation
  - Log scraping attempts and retries
  - Log field extraction attempts and outcomes
  - Log output file writing

- [ ] 4.3.3 Add diagnostic information collection
  - Log HTTP status codes when fetching
  - Log extraction duration for performance tracking
  - Log retry counts and backoff timing
  - Log field-level extraction attempts and errors
  - Include timestamps in log messages

- [ ] 4.3.4 Run logging tests
  - Execute only the 2-3 tests written in 4.3.1
  - Verify logs written at appropriate levels
  - Confirm sensitive data not exposed
  - Do NOT run full test suite

**Acceptance Criteria**:
- 2-3 focused tests pass
- All major operations logged
- Log messages include timestamps and context
- Diagnostic information available for troubleshooting

---

### Phase 5: Testing & Validation

#### Task Group 5.1: Feature-Specific Test Review and Gap Analysis
**Dependencies**: Task Groups 1.1-4.3
**Duration**: 2 hours

- [ ] 5.1.1 Review all tests from Phases 1-4
  - Review 4-6 tests from Task Group 1.1 (data models)
  - Review 4-6 tests from Task Group 1.2 (config management)
  - Review 3-5 tests from Task Group 1.3 (URL validation)
  - Review 4-6 tests from Task Group 2.1 (scraping engine)
  - Review 4-6 tests from Task Group 2.2 (extraction engine)
  - Review 3-5 tests from Task Group 2.3 (TOML formatter)
  - Review 2-3 tests from Task Group 2.4 (file output)
  - Review 5-7 tests from Task Group 2.5 (public API end-to-end)
  - Review 3-4 tests from Task Group 3.1 (config schema)
  - Review 3-4 tests from Task Group 3.2 (rule variations)
  - Review 3-4 tests from Task Group 4.1 (error categorization)
  - Review 3-4 tests from Task Group 4.2 (partial failures)
  - Review 2-3 tests from Task Group 4.3 (logging)
  - **Total existing tests**: Approximately 50-65 tests

- [ ] 5.1.2 Analyze test coverage gaps for THIS feature only
  - Identify critical user workflows not tested:
    - End-to-end: URL -> config lookup -> scraping -> extraction -> TOML output file
    - Configuration evolution: adding new field to config and extracting it
    - Multiple sites in single config: lookup and extract from different sites
    - Error recovery: retries on transient failures, graceful degradation
  - Assess whether critical workflows have integration-level test coverage
  - Focus ONLY on gaps related to this spec's feature requirements
  - Do NOT assess entire application test coverage
  - Prioritize end-to-end workflows over unit test gaps

- [ ] 5.1.3 Identify maximum 8-10 strategic additional tests
  - Test workflow: Full end-to-end with multiple sites in config (if not covered)
  - Test workflow: Configuration update and re-extraction (if not covered)
  - Test workflow: Network retry and recovery (if not covered)
  - Test error scenario: Invalid config file with helpful error message
  - Test error scenario: Unreachable URL with helpful error message
  - Test scenario: Mixed success (some fields extracted, others failed)
  - Test scenario: Site type detection for analytics tracking
  - Test scenario: Output file contains valid TOML readable by external tools
  - Limit to maximum 10 new tests; skip edge cases unless business-critical

- [ ] 5.1.4 Document gaps and testing plan
  - Create `TESTING_PLAN.md` documenting all tests written in Phases 1-4
  - List critical workflows covered
  - List gaps identified and how 5.1.3 tests address them
  - Note which edge cases intentionally skipped

**Acceptance Criteria**:
- All 50-65 existing tests reviewed
- Critical workflows identified and assessed
- Maximum 10 additional tests planned
- Testing plan documented

---

#### Task Group 5.2: Write Strategic Gap-Filling Tests (Maximum 10)
**Dependencies**: Task Group 5.1
**Duration**: 2-3 hours

- [ ] 5.2.1 Implement up to 10 strategic integration tests
  - Write exactly the tests identified in 5.1.3
  - Focus on integration points and end-to-end workflows
  - Each test should verify a critical user scenario
  - Add setup/teardown for test isolation
  - Use fixtures from conftest.py for common test data

- [ ] 5.2.2 Add test fixtures and helpers
  - Create test TOML config files for different site types
  - Create mock HTML content for extraction testing
  - Create helper functions for result validation
  - Document test fixtures in conftest.py

- [ ] 5.2.3 Verify all new tests pass
  - Run only the 10 new tests (not full suite)
  - Verify each test passes individually
  - Check test isolation (no cross-test pollution)
  - Document any test dependencies

**Acceptance Criteria**:
- Up to 10 new strategic tests written
- All new tests pass
- Tests cover critical workflows and gaps
- Test isolation verified

---

#### Task Group 5.3: Run Full Feature-Specific Test Suite
**Dependencies**: Task Group 5.2
**Duration**: 1.5 hours

- [ ] 5.3.1 Run all feature-specific tests together
  - Execute all tests from Phases 1-4 (50-65 tests)
  - Execute all new tests from Phase 5 (up to 10 tests)
  - Expected total: 60-75 tests maximum
  - Verify test discovery finds all tests
  - Run with: `pytest tests/ -v --tb=short`

- [ ] 5.3.2 Analyze test results
  - Verify all tests pass
  - Note any test failures and debug if needed
  - Check for skipped or xfailed tests
  - Generate coverage report: `pytest --cov=scraper tests/`

- [ ] 5.3.3 Document test execution
  - Create `TEST_RESULTS.md` with summary
  - Note total tests run, pass rate, coverage
  - Document any warnings or edge cases
  - List critical workflows verified by tests

**Acceptance Criteria**:
- All 60-75 feature-specific tests pass
- No critical workflow gaps identified
- Coverage report generated
- Test results documented

---

#### Task Group 5.4: Validation and Integration Verification
**Dependencies**: Task Group 5.3
**Duration**: 1.5 hours

- [ ] 5.4.1 Manual end-to-end validation
  - Create real test site configuration (or use documented example site)
  - Run `scrape_facility()` manually with test URL
  - Verify output TOML file created with correct structure
  - Read output file and validate all sections present
  - Compare against specification format

- [ ] 5.4.2 Verify output compatibility
  - Read generated TOML file with external TOML parser
  - Verify all values are TOML-compatible types
  - Confirm timestamps in ISO format
  - Validate fields_status section complete

- [ ] 5.4.3 Integration check
  - Verify configuration file parsing works
  - Verify site lookup by URL works
  - Verify error messages are user-friendly
  - Confirm logging output is helpful for debugging

**Acceptance Criteria**:
- Manual end-to-end execution successful
- Output TOML valid and matches specification
- All components integrate correctly
- Error messages helpful and clear

---

### Phase 6: Documentation & Polish

#### Task Group 6.1: Code Documentation and Comments
**Dependencies**: Task Group 5.4
**Duration**: 1.5 hours

- [ ] 6.1.1 Add comprehensive docstrings
  - Add module-level docstrings to all files
  - Add class docstrings explaining purpose and usage
  - Add method docstrings with Args, Returns, Raises
  - Follow project style guide for docstring format
  - Document all public API methods thoroughly

- [ ] 6.1.2 Add implementation notes and comments
  - Add comments explaining complex logic
  - Document design decisions (e.g., why Scrapling is abstracted)
  - Add TODOs for future enhancements
  - Comment sections explaining the IPO architecture
  - Reference specification in complex areas

- [ ] 6.1.3 Document configuration schema evolution
  - Create `CONFIG_EVOLUTION.md` documenting schema changes during implementation
  - Note fields that were added/removed as patterns discovered
  - Explain rationale for each schema decision
  - Provide guidance for future config extensions

**Acceptance Criteria**:
- All public API methods have clear docstrings
- Complex logic has explanatory comments
- Configuration evolution documented
- Documentation follows project style guide

---

#### Task Group 6.2: README and Usage Documentation
**Dependencies**: Task Group 6.1
**Duration**: 1.5 hours

- [ ] 6.2.1 Create comprehensive README.md
  - Explain module purpose and design (IPO architecture)
  - Provide quick start example with sample config
  - Document how to use `scrape_facility()` function
  - Explain configuration file format
  - Document expected output structure

- [ ] 6.2.2 Create usage examples
  - Provide example configuration file with comments
  - Provide example Python usage code
  - Provide example output TOML file
  - Document how to extend configuration for new sites
  - Include example of error handling in usage code

- [ ] 6.2.3 Create troubleshooting guide
  - Document common errors and solutions
  - Explain how to read error messages
  - Provide debugging tips (enable logging, check config)
  - Link to relevant sections of specification
  - Document how to add new extraction rules

**Acceptance Criteria**:
- README.md comprehensive and user-friendly
- Usage examples clear and functional
- Troubleshooting guide covers common issues
- Configuration examples documented

---

#### Task Group 6.3: Code Formatting and Quality Check
**Dependencies**: Task Group 6.2
**Duration**: 1 hour

- [ ] 6.3.1 Apply code formatting standards
  - Run Black formatter on all Python files: `black scraper/ tests/`
  - Run mypy type checker: `mypy scraper/`
  - Fix any formatting or type issues
  - Ensure consistent style across all files

- [ ] 6.3.2 Perform code review checklist
  - Verify no dead code or unused imports
  - Check for DRY violations (repeated code)
  - Confirm function sizes are reasonable (<25 lines preferred)
  - Verify error handling follows project standards
  - Check resource cleanup (file handles, connections)

- [ ] 6.3.3 Final validation
  - Run full test suite one final time: `pytest tests/`
  - Verify coverage report: `pytest --cov=scraper tests/`
  - Check for any deprecation warnings
  - Verify all tests pass

**Acceptance Criteria**:
- All code formatted with Black
- No type checking errors from mypy
- No dead code or unused imports
- All tests passing
- Coverage acceptable for feature scope

---

#### Task Group 6.4: Final Integration and Release Preparation
**Dependencies**: Task Group 6.3
**Duration**: 1 hour

- [ ] 6.4.1 Create release documentation
  - Create `CHANGELOG.md` documenting features implemented
  - Create `KNOWN_ISSUES.md` if any limitations exist
  - Create `FUTURE_ENHANCEMENTS.md` with Phase 2+ items
  - Document any TBD items from specification

- [ ] 6.4.2 Verify specification alignment
  - Review specification requirements against implementation
  - Create `SPEC_COMPLIANCE.md` confirming all requirements met
  - Note any deviations or clarifications made
  - Document any TBD decisions that were resolved

- [ ] 6.4.3 Prepare for next phase
  - Document assumptions made during implementation
  - List configuration fields that may evolve
  - Note architecture extension points
  - Create roadmap for Phase 2 analytics integration

**Acceptance Criteria**:
- Release documentation complete
- Specification compliance verified
- All requirements from spec implemented
- Architecture ready for Phase 2 work

---

## Execution Order and Dependencies

### Recommended Implementation Sequence:

1. **Phase 0** (Setup & Foundation) - 2-3 hours
2. **Phase 1** (Core Architecture) - 9-12 hours total
   - Task 1.1 → 1.2 → 1.3 (sequential; each depends on previous)
3. **Phase 2** (Vertical Slice End-to-End) - 12-15 hours total
   - Task 2.1 → 2.2 → 2.3 → 2.4 → 2.5 (sequential; each depends on previous)
   - This produces a complete working example
4. **Phase 3** (Extensibility) - 4-5 hours total
   - Task 3.1 → 3.2 (sequential; independent of other phases)
5. **Phase 4** (Error Handling) - 5-6 hours total
   - Task 4.1 → 4.2 → 4.3 (sequential; enhances Phases 2-3)
6. **Phase 5** (Testing & Validation) - 7-10 hours total
   - Task 5.1 → 5.2 → 5.3 → 5.4 (sequential; covers all phases)
7. **Phase 6** (Documentation) - 5-6 hours total
   - Task 6.1 → 6.2 → 6.3 → 6.4 (sequential; final polish)

**Total Estimated Duration**: 45-57 hours across all phases

### Critical Path:
Phase 0 → Phase 1 (all) → Phase 2 (all) is the critical path for achieving a working vertical slice. Phases 3-6 add features and polish but don't block earlier phases.

### Parallel Opportunities:
- Phase 3 and Phase 4 can run in parallel after Phase 2 is complete
- Phase 5 can begin once Phase 4 is substantially complete
- Phase 6 can begin once Phase 5 is complete

---

## Testing Strategy Summary

### Tests Written During Implementation:
- **Phase 1**: 14-20 tests (data models, config, URL validation)
- **Phase 2**: 21-28 tests (scraping, extraction, output, public API)
- **Phase 3**: 6-8 tests (advanced config, rule variations)
- **Phase 4**: 8-11 tests (error handling, logging)
- **Subtotal from Phases 1-4**: 49-67 tests

### Gap-Filling Tests:
- **Phase 5**: Maximum 10 additional tests (strategic gaps only)

### Total Feature-Specific Tests:
- **Grand Total**: 59-77 tests covering this feature specification

### Important Constraints:
- Each task group writes 2-8 focused tests (never exhaustive)
- Tests focus on critical behaviors and happy paths
- Edge cases and exhaustive coverage skipped unless business-critical
- Test verification runs ONLY the newly written tests, not full suite
- Phase 5 adds maximum 10 additional tests (not hundreds)

---

## Acceptance Criteria for Completion

### Definition of Done for Core Scraping Module:

- [ ] All tasks in Phases 0-6 marked complete
- [ ] Public API (`scrape_facility`) fully functional
- [ ] Single example site scraping end-to-end working
- [ ] 60-75 focused feature-specific tests pass
- [ ] Configuration system working with extensible schema
- [ ] Error handling graceful with proper categorization
- [ ] TOML output valid and matches specification
- [ ] Code formatted, documented, and follows project standards
- [ ] README and usage examples clear and functional
- [ ] Specification compliance verified
- [ ] Architecture supports Phase 2 reliability measurement
- [ ] Ready for Phase 2 expansion to multiple sites and analytics

---

## Known Implementation Notes

### Configuration Evolution Expected:
The configuration schema will evolve as implementation proceeds. Document changes in `CONFIG_EVOLUTION.md` for future reference.

### Library Swapping Approach (TBD):
The architecture abstracts Scrapling behind `ScrapingEngine` for future library swapping. Specific abstraction pattern (interface, plugin, adapter) to be determined during implementation.

### Type Conversion Heuristics (TBD):
Rules for type detection and conversion will be refined based on actual extracted data patterns encountered.

### Site Type Detection (TBD):
Method for automatic site type detection will be finalized during implementation (URL pattern matching, content analysis, or hybrid).

---

## References

- **Specification**: `/home/nicolas/github/scrape0/agent-os/specs/2026-01-04-core-scraping-modular-architecture/spec.md`
- **Requirements**: `/home/nicolas/github/scrape0/agent-os/specs/2026-01-04-core-scraping-modular-architecture/planning/requirements.md`
- **Project Style Guide**: Referenced via project conventions (global-coding-style skill)
- **Error Handling Standard**: Referenced via project conventions (global-error-handling skill)
