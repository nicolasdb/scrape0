# Phase 3: Catalogue Extraction - Task List

## Task Group 1: Update Data Models

- [ ] Modify `scraper/models.py` - Add `list_extraction` field to `SiteConfig`
  - [ ] Add `list_extraction: Optional[Dict[str, Any]] = None` field
  - [ ] Ensure field is documented with comment explaining purpose

- [ ] Modify `scraper/models.py` - Add list item fields to `ExtractionResult`
  - [ ] Add `list_items: Optional[List[Dict[str, Any]]] = None` field
  - [ ] Add `list_items_name: Optional[str] = None` field
  - [ ] Document both fields with comments

## Task Group 2: Enhance Extraction Engine

- [ ] Modify `scraper/extraction.py` - Add `extract_list_items()` method
  - [ ] Takes `soup: BeautifulSoup` and `list_config: dict` as parameters
  - [ ] Uses `item_selector` to find all item containers
  - [ ] Extracts fields from each item using `_extract_from_element()`
  - [ ] Returns `list[dict]` with all items
  - [ ] Only includes items that have at least one field extracted

- [ ] Modify `scraper/extraction.py` - Add `_extract_from_element()` helper
  - [ ] Parses special syntax: `::text`, `::attr(name)`, `::exists`, `::text::all`
  - [ ] Handles selector + modifier chains (e.g., `.tag::text`)
  - [ ] Supports single value extraction and array extraction modes
  - [ ] Returns extracted value(s) or None

- [ ] Modify `scraper/extraction.py` - Integrate list extraction
  - [ ] Update main `extract_fields()` or result building to call `extract_list_items()`
  - [ ] Pass `list_extraction` config from site config if present
  - [ ] Store results in `ExtractionResult.list_items` and `ExtractionResult.list_items_name`

## Task Group 3: Update Config Parser

- [ ] Modify `scraper/config.py` - Parse list extraction config
  - [ ] Extract `[sites.list_extraction]` section from TOML
  - [ ] Validate required fields: `item_selector` must be present
  - [ ] Validate optional field: `output_field` if specified
  - [ ] Validate `[sites.list_extraction.fields]` section exists and has entries
  - [ ] Pass parsed config to `SiteConfig` object

## Task Group 4: Update Output Generation

- [ ] Modify `scraper/output.py` - Add list items to TOML output
  - [ ] Check if `ExtractionResult.list_items` has data
  - [ ] Determine output field name:
    - [ ] Use `list_items_name` if set (from config `output_field`)
    - [ ] Fall back to "items" as default name
  - [ ] Add list items as TOML array (`[[array_name]]` syntax)
  - [ ] Ensure output is valid TOML format

## Task Group 5: Create Test Configurations

- [ ] Create `config/devicemed_catalogue.toml`
  - [ ] Configure for devicemed.fr/fournisseurs-liste
  - [ ] Simple list with name + URL per supplier
  - [ ] No pagination (single page)
  - [ ] Site type: "catalogue_index"

- [ ] Create `config/biowin_catalogue.toml`
  - [ ] Configure for biowin.org/members/
  - [ ] Rich list with name, URL, description, type, tags
  - [ ] Custom output field name: "members"
  - [ ] Site type: "catalogue_index"

## Task Group 6: Testing & Validation

- [ ] Create `tests/test_list_extraction.py` with unit tests
  - [ ] Test `_extract_from_element()` with all syntax variants:
    - [ ] `::text` modifier
    - [ ] `::attr(href)` modifier
    - [ ] `::exists` modifier
    - [ ] `::text::all` for array extraction
    - [ ] Chained selectors (e.g., `.tag::text`)

  - [ ] Test `extract_list_items()` method:
    - [ ] Extract items from sample HTML
    - [ ] Handle items with missing fields
    - [ ] Filter out empty items
    - [ ] Respect field configuration

- [ ] Integration test: Verify TOML output structure
  - [ ] List items appear in output
  - [ ] Array syntax is correct (`[[items]]` or `[[members]]`)
  - [ ] Field names match configuration
  - [ ] Output is valid TOML

- [ ] Manual test: devicemed.fr suppliers (if possible)
  - [ ] Verify extraction works on real website
  - [ ] Verify large number of items (1200+) handled
  - [ ] Check output file size and format

- [ ] Manual test: biowin.org members (if possible)
  - [ ] Verify extraction of rich item data
  - [ ] Verify custom output field name ("members")
  - [ ] Verify array of objects in TOML format

- [ ] Backward compatibility test
  - [ ] Existing Phase 2 configs still work
  - [ ] Sites without list_extraction behave as before
  - [ ] Phase 2 test suite still passes (62 tests)

## Summary

**Total Tasks**: 25+ subtasks across 6 task groups

**Estimated Effort**:
- Task Group 1 (Models): 30 minutes
- Task Group 2 (Extraction): 1.5 hours
- Task Group 3 (Config): 30 minutes
- Task Group 4 (Output): 30 minutes
- Task Group 5 (Configs): 30 minutes
- Task Group 6 (Testing): 1 hour

**Total: 4-5 hours**

**Dependencies**: All groups should be completed in order.

**Success Definition**: All tasks marked complete AND all tests passing AND backward compatibility verified.
