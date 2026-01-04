# Phase 3: Catalogue Extraction - Requirements

## Functional Requirements

### FR1: Configuration Support for List Extraction

**Requirement**: The system shall support a new `[sites.list_extraction]` section in TOML configs.

**Details**:
- New optional section in TOML for each site
- Required field: `item_selector` (CSS selector for item containers)
- Optional field: `output_field` (name for output array, defaults to "items")
- Required section: `[sites.list_extraction.fields]` with field extraction rules
- Field values use special syntax: `::text`, `::attr(name)`, `::exists`, `::text::all`

**Acceptance Criteria**:
- Config parser accepts and validates `[sites.list_extraction]` section
- Config validation fails if `item_selector` missing
- Config validation fails if `fields` section missing or empty
- `output_field` is optional and defaults to "items"

### FR2: Extract List Items Using Special Syntax

**Requirement**: The extraction engine shall extract structured list items from HTML using special syntax modifiers.

**Details**:
- `::text` - Extract text content of element
- `::attr(name)` - Extract HTML attribute (e.g., `href`, `src`, `data-id`)
- `::exists` - Check if element exists (returns true/false)
- `::text::all` - Extract all matching elements as array
- Modifiers can be chained with CSS selectors: `.selector::modifier`

**Acceptance Criteria**:
- Each modifier works independently
- Selectors can be chained with modifiers (e.g., `.tag::text`)
- Array extraction (::all) returns list instead of single value
- Existence check returns boolean value
- Non-existent elements return None/null values

### FR3: Extract Multiple Items per Page

**Requirement**: The system shall extract all items matching the item_selector from a page.

**Details**:
- Find all elements matching `item_selector`
- For each item element, extract configured fields
- Build list of dictionaries, one per item
- Handle items with missing fields gracefully

**Acceptance Criteria**:
- All matching items are extracted
- Items with no extracted fields are excluded
- Field count varies per item (some may have missing fields)
- Returns empty list if no items match selector
- Handles large lists (1000+) without performance issues

### FR4: Dynamic Output Field Naming

**Requirement**: Output array name shall be determined by configuration and site type.

**Details**:
- Priority 1: User-specified `output_field` in config
- Priority 2: Auto-detect from `site_type = "catalogue_index"` → use "items"
- Priority 3: Default to "items"

**Acceptance Criteria**:
- Custom output_field overrides defaults
- site_type auto-detection works
- Default fallback is "items"
- Output array uses correct TOML syntax: `[[array_name]]`

### FR5: Output as TOML Array of Objects

**Requirement**: List items shall be output as TOML array of tables.

**Details**:
- Use TOML `[[array_name]]` syntax for array of objects
- Each item is a separate table with its extracted fields
- Output should be valid TOML

**Acceptance Criteria**:
- Output is valid TOML format
- Can be parsed by standard TOML parsers
- Array syntax is correct: `[[items]]`, `[[members]]`, etc.
- Field values are properly typed (string, boolean, array)

## Non-Functional Requirements

### NFR1: Backward Compatibility

**Requirement**: Existing Phase 2 functionality shall not be affected.

**Details**:
- Sites without `list_extraction` config work as before
- Phase 2 test suite continues to pass
- No breaking changes to config format for existing configs
- Existing extraction logic unchanged for non-list sites

**Acceptance Criteria**:
- All Phase 2 unit tests pass (62 tests)
- Existing configs work without modification
- No regression in existing functionality

### NFR2: Performance

**Requirement**: List extraction shall perform efficiently.

**Details**:
- Handle large lists (1000+ items) without timeout
- Extraction time proportional to item count
- No memory leaks with large result sets

**Acceptance Criteria**:
- Extracting 1000+ items completes in reasonable time
- Memory usage scales linearly with item count
- No performance regression vs. Phase 2 baseline

### NFR3: Error Handling

**Requirement**: System shall handle invalid configurations gracefully.

**Details**:
- Invalid CSS selectors are caught and reported
- Missing required fields cause clear error messages
- Malformed special syntax is handled

**Acceptance Criteria**:
- Invalid config raises clear error message
- Invalid CSS selector is caught at parse time
- Extraction continues even if some items have missing fields
- Error messages guide user to fix issues

### NFR4: Code Quality

**Requirement**: Implementation shall follow project coding standards.

**Details**:
- Follow existing code patterns in scraper module
- Include docstrings for new methods
- Use type hints for function signatures
- Unit tests for extraction logic

**Acceptance Criteria**:
- Code follows project style guidelines
- New methods have complete docstrings
- Type hints present on all function signatures
- Unit tests achieve >80% coverage of new code

## Design Constraints

### Constraint 1: No Pagination in Minimal Version

**Scope**: Extract first page only
- devicemed.fr: Works perfectly (all items on one page)
- biowin.org: Gets ~20-30 items from first page only
- Future: Add pagination support in Phase 3.5

### Constraint 2: Special Syntax Only

**Scope**: Use only `::text`, `::attr`, `::exists`, `::text::all` syntax
- No XPath support
- No JavaScript execution
- No dynamic rendering
- CSS selectors only

### Constraint 3: Simple Nesting Only

**Scope**: No complex nested object extraction
- Extract flat arrays only in minimal version
- Each item is one level of fields
- No nested lists or objects within items

## Test Data Requirements

### Test Data 1: Simple List (devicemed.fr)

**Configuration**: `config/devicemed_catalogue.toml`
- Site: devicemed.fr/fournisseurs-liste
- Items: ~1200 suppliers
- Fields per item: name (text), url (href)
- No pagination
- Flat structure

### Test Data 2: Rich List (biowin.org)

**Configuration**: `config/biowin_catalogue.toml`
- Site: biowin.org/members/
- Items: 209 members (~20-30 on first page for minimal version)
- Fields per item: name, url, description, type, tags
- Has pagination (not used in minimal version)
- Complex structure with arrays (tags)

### Test Data 3: Unit Test Fixtures

**File**: `tests/test_list_extraction.py`
- Sample HTML with simple list structure
- Sample HTML with complex item structure
- Edge cases: missing fields, empty items, malformed selectors

## Success Metrics

| Metric | Target | Acceptance |
|--------|--------|-----------|
| Unit test coverage | >80% | Required |
| All Phase 2 tests pass | 62/62 | Required |
| Can extract devicemed.fr | 100+ items | Required |
| Can extract biowin.org | 10+ items | Required |
| TOML output validity | 100% | Required |
| Config validation | Clear errors | Required |
| Backward compatibility | No regressions | Required |

## Dependencies

- Phase 2 (Registry, Scheduler, Results Storage) - COMPLETED
- BeautifulSoup4 library (already in project)
- TOML parser (already in project)
- No new external dependencies

## Out of Scope (Future Phases)

- ❌ Pagination support
- ❌ Nested object extraction
- ❌ CSV/JSON output formats
- ❌ Deduplication across pages
- ❌ Incremental updates/change tracking
- ❌ JavaScript rendering
- ❌ XPath support
- ❌ Form submission/interaction
