# Spec Requirements: Core Scraping with Modular Architecture

## Initial Description

Build a core scraping module with modular, swappable architecture designed for profiling fablabs and makerspaces. The system should extract priority fields (name, location, expertise, URL, contact) and extra metadata, output to TOML format, and enable future reliability testing and schema refinement.

**Project Context**: Scrape0 - greenfield prototype for testing scraping reliability. Single-URL focus initially; batch mode deferred. Using Scrapling as primary library with designed swappability for alternatives.

---

## Requirements Discussion

### First Round Questions

**Q1: Configuration Approach**
**Question Asked**: I'm assuming you'll want a single unified configuration file that can be iterated on and evolved as you discover more about scraping patterns. Should we build the config structure dynamically (adapting to patterns we encounter) rather than requiring it all upfront?

**Answer**: Yes, single unified config file with iteration based on structure encountered. Don't require all patterns upfront - allow the system to adapt and learn.

---

**Q2: Schema Metadata Structure**
**Question Asked**: For organizing extracted data and making it schema-ready, are you thinking of building out a complete metadata schema from the start, or is this something you want to prototype and refine during implementation?

**Answer**: Schema metadata structure is TBD - this is a prototype goal. Don't lock in schema design before implementation begins.

---

**Q3: Library Swapping Mechanism**
**Question Asked**: For the library swapping capability, are you thinking of building a complete abstraction layer now, or should we design the structure to allow swapping while prototyping with Scrapling first?

**Answer**: Library swapping approach is TBD - prototype goal. Design for swappability but focus on Scrapling for now. Don't over-engineer abstraction layers prematurely.

---

**Q4: Type Handling and Conversion**
**Question Asked**: For type handling, I'm proposing: input as raw strings → basic type conversion during processing → TOML format enforcement in output. Does that flow make sense?

**Answer**: Agreed. Raw strings as input → basic conversion in process → TOML enforcement in output. This conversion strategy is confirmed.

---

**Q5: Site Type Detection and Analytics**
**Question Asked**: Should the system track which site types were successfully extracted (for understanding patterns and reliability) to inform the multi-URL expansion in Phase 1?

**Answer**: Yes, site type detection/tracking for analytics. This relates to multi-URL expansion and will help measure reliability in Phase 2.

---

**Q6: Failure Handling Strategy**
**Question Asked**: For extraction failures, should we collect failure metadata (which fields failed, why) rather than halting the entire process?

**Answer**: Graceful failure with metadata. Return: success=false, failure_reason, fields_extracted, fields_failed. Don't halt on partial failures.

---

**Q7: Vision Document Scope**
**Question Asked**: Should I reference the larger vision/strategy document for context, or stay focused narrowly on this scraping module scope?

**Answer**: Don't review larger vision doc - stay focused on scraping scope only. Keep this spec narrowly scoped to the core scraping module.

---

**Q8: Post-Processing and LLM Enhancement**
**Question Asked**: Post-processing with LLM agents (for data quality/refinement) - is this part of this module or deferred?

**Answer**: LLM agents for post-processing noted as Phase 3+ enhancement, not core scraping. Keep out of scope for this module.

---

### Existing Code to Reference

**Similar Features Identified**: None explicitly identified by user.

The spec-writer should investigate:
- Any existing TOML configuration handling in the codebase
- Existing error handling patterns for data extraction failures
- Analytics/tracking patterns used elsewhere in the project

---

## Visual Assets

**Files Provided**: No visual assets were provided.

The spec-writer may want to create diagrams during specification writing to illustrate:
- IPO model flow (Input → Process → Output)
- Configuration file structure and evolution
- Type conversion pipeline
- Failure handling and metadata tracking
- Multi-layer module architecture for library swapping

---

## Requirements Summary

### Functional Requirements

#### Core Extraction
- Extract priority fields: name, location, expertise, URL, contact info
- Extract additional metadata fields (variable/extensible)
- Support single-URL input initially (batch mode in Phase 1)
- Process raw HTML/web content into structured data

#### Configuration Management
- Single unified configuration file (TOML or similar)
- Configuration structure should evolve based on patterns encountered
- Support iteration and refinement during implementation
- No requirement for complete schema upfront

#### Type Handling
- Accept raw string input from web scraping
- Perform basic type conversion during processing layer
- Enforce TOML-compatible types in output
- Handle conversion errors gracefully

#### Data Extraction Strategy
- Distinguish between priority fields (required/important) and extra metadata
- Support graceful partial extraction (don't fail entirely if some fields missing)
- Track which fields succeeded and which failed
- Return metadata about extraction success/failure

#### Error Handling & Failure Modes
- Graceful failure mode: return partial results with metadata
- Include in failure response: success flag, failure_reason, fields_extracted, fields_failed
- Support site type detection and tracking for analytics
- Don't halt pipeline on partial extraction failures

#### Output Format
- TOML format for all extracted data
- Include metadata fields: success, failure_reason, fields_extracted, fields_failed, site_type
- Structure for future vector embedding compatibility
- Schema designed to be refined during implementation

#### Analytics & Observability
- Track site type detection (for multi-URL expansion patterns)
- Record extraction success rates per field type
- Collect failure metadata for reliability measurement in Phase 2
- Enable analysis of scraping patterns and site variations

### Architecture Pattern: IPO Model

The system follows Input-Process-Output separation:

- **Input Layer**: URL intake, configuration loading, raw content retrieval
- **Process Layer**: Data extraction, type conversion, field mapping, validation
- **Output Layer**: TOML serialization, metadata attachment, file writing

Each layer should be independently testable and replaceable.

### Library Swapping & Modularity

- Design architecture to allow alternative scraping libraries
- Scrapling is primary choice but abstraction should support swapping
- Don't over-engineer abstraction layer during prototyping
- Library swapping approach is TBD - to be defined during implementation
- Modular design should make it easy to substitute extraction logic

### Configuration Schema (Flexible/TBD)

Current understanding (to be refined during implementation):
- Single unified config file (TOML format assumed)
- Maps site-specific extraction rules to fields
- Adapts based on patterns encountered
- No complete schema required upfront
- Schema metadata structure is TBD

**Example structure (draft, to be evolved)**:
```
[scraper]
primary_library = "scrapling"  # Swappable

[[sites]]
name = "example-fablab"
url_pattern = "example.com"
fields.name = "selector or rule"
fields.location = "selector or rule"
# ...additional field mappings

[output]
format = "toml"
include_metadata = true
```

### Data Extraction Strategy

**Priority Fields** (high confidence/important):
- name
- location
- expertise
- URL
- contact info

**Extra Metadata** (variable/extensible):
- Operating hours
- Equipment list
- Pricing info
- Website features
- Other site-specific attributes

**Extraction behavior**:
- Extract what's available
- Return success/failure metadata for each field group
- Allow partial extraction (e.g., get name but fail on contact)
- Track which fields were successfully extracted vs. which failed

### Output Schema & Metadata

**TOML Output Structure (draft)**:
```toml
[extraction_metadata]
success = true
extraction_timestamp = "2026-01-04T10:00:00Z"
failure_reason = null  # "no_response", "parsing_error", etc.
site_type = "fablab"  # For analytics tracking

[priority_fields]
name = "Example Fablab"
location = "San Francisco, CA"
expertise = ["3D printing", "electronics"]
url = "https://example.com"
contact = "contact@example.com"

[extra_metadata]
operating_hours = "Mon-Fri 9am-6pm"
equipment = ["CNC", "Laser cutter"]
# ... additional fields extracted

[fields_status]
extracted = ["name", "location", "expertise", "url", "contact"]
failed = ["operating_hours"]
not_found = []
```

### Scope Boundaries

**In Scope**:
- Single-URL scraping with Scrapling
- Priority field extraction (5 core fields)
- Extra metadata collection (extensible)
- Type conversion (strings → basic types → TOML)
- Graceful failure with metadata
- TOML output format
- Site type detection for analytics
- Modular architecture (IPO model)
- Configuration file management (single unified file)
- Error handling and metadata tracking

**Out of Scope** (deferred to later phases):
- Batch mode / multi-URL processing (Phase 1 item #4)
- LLM agents for post-processing (Phase 3+)
- Complete schema metadata design (TBD during implementation)
- Library abstraction layer over-engineering
- Vector embedding preparation (future use, not built now)
- Reliability testing framework (Phase 2 focus)

**Future Enhancements** (mentioned):
- Reliability measurement and metrics (Phase 2)
- Batch/multi-URL mode expansion (Phase 1)
- LLM-based post-processing for quality refinement (Phase 3+)
- Complete schema design finalization

### Known Unknowns / TBD Decisions

1. **Schema Metadata Structure**: Exact format for storing schema information is TBD. Will be defined during implementation based on actual scraping patterns encountered.

2. **Library Swapping Abstraction**: The specific abstraction mechanism for swapping scraping libraries is TBD. Design should support it, but over-engineering avoided during prototype phase.

3. **Configuration Schema Details**: Complete structure of the unified config file is TBD. Will evolve based on site patterns discovered during implementation.

4. **Batch Mode Implementation**: How multi-URL expansion will work is deferred to Phase 1. Current focus is single-URL reliability.

5. **Failure Metadata Format**: Exact schema for `failure_reason` values and error categorization to be defined during development.

### Technical Considerations

#### Type System
- Input: Raw strings from HTML scraping
- Processing: Basic type inference/conversion (strings, numbers, lists, booleans)
- Output: TOML-compatible types only
- No complex type coercion; keep conversion logic simple

#### Configuration Management
- Single TOML file (assumed, can be JSON or YAML)
- Human-readable and version-controllable
- Support comments for documentation
- Allow incremental enhancement without full redesign

#### Error Handling Philosophy
- Fail gracefully: partial success is acceptable
- Collect comprehensive metadata about failures
- Don't interrupt pipeline for individual field failures
- Track success/failure per field and site type

#### Integration Points
- Scrapling library (primary scraping engine)
- TOML library (output serialization)
- File system (config file loading, output writing)
- Future: vector embedding pipeline (data destination)
- Future: Phase 2 reliability measurement system

#### Extensibility
- Configuration should support discovering new site patterns
- Field definitions should be addable without code changes
- Extra metadata collection should be flexible/dynamic
- Library swapping should require minimal code changes

### Dependencies

**External Libraries**:
- Scrapling (primary scraping library, swappable)
- TOML library (output formatting)

**Internal Dependencies**:
- Configuration management system
- Type conversion utilities
- File I/O operations
- Error/exception handling patterns

### Analytics Readiness

The system is being designed with Phase 2 reliability measurement in mind:

- **Site Type Tracking**: Categorize extracted sites (e.g., "fablab", "makerspace") for pattern analysis
- **Field-Level Metrics**: Track success/failure per field to identify problematic extractions
- **Failure Reasons**: Collect structured failure metadata for root cause analysis
- **Extraction Completeness**: Measure what % of priority fields successfully extracted
- **Partial Success Handling**: Enable analysis of partial vs. complete extractions

This metadata foundation will support:
- Reliability reporting in Phase 2
- Identifying scraping library improvements needed
- Refining configuration rules for better extraction rates
- Understanding site-type-specific challenges

---

## Summary for Spec Writer

This greenfield prototype should be built with:

1. **Clear separation** of Input → Process → Output layers
2. **Flexible configuration** that evolves during implementation (not locked upfront)
3. **Graceful failure handling** that collects metadata for both success and failure cases
4. **Type pipeline** that moves from raw strings → basic types → TOML
5. **Analytics hooks** built-in for Phase 2 reliability measurement
6. **Library swappability** designed in, but not over-engineered during prototyping
7. **Schema flexibility** to accommodate variations in scraped content

Keep the scope tightly focused on the core scraping module. Defer batch mode, LLM post-processing, and advanced schema design to future phases while building the foundation for these enhancements.
