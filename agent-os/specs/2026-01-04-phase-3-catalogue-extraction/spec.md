# Phase 3: Catalogue/List Extraction Feature - Specification

## Overview

Add support for extracting structured lists/catalogues of items where each item has multiple fields. This enables scraping supplier directories, member listings, product catalogues, and similar list-based content.

## Problem Statement

The current extraction engine (Phase 1-2) extracts flat key-value fields from pages:
- Extracts a single title, location, description, etc.
- When multiple elements match, joins them into comma-separated strings
- Cannot extract structured arrays of objects

**Current Limitation**: Cannot extract like this:
```toml
[[items]]
name = "Item 1"
url = "https://example.com"

[[items]]
name = "Item 2"
url = "https://example.org"
```

## Use Cases

### Use Case 1: devicemed.fr/fournisseurs-liste
- **Structure**: Simple list of 1200+ suppliers
- **Per-item data**: Name (text) + URL (href)
- **Pagination**: None (all on one page with alphabetical filtering)
- **Data format**: Lightweight - just name and link

### Use Case 2: biowin.org/members/
- **Structure**: Rich member cards with 209 members
- **Per-item data**: Name, URL, Description, Type badge, Category tags
- **Pagination**: Multiple pages (10+ pages, no pagination in minimal version)
- **Data format**: Rich - multiple fields per member

## Solution Architecture

### Configuration-Driven Approach

Add a new optional `[sites.list_extraction]` section to TOML configs:

```toml
[[sites]]
id = "devicemed-suppliers"
url_pattern = "devicemed.fr/fournisseurs"
site_type = "catalogue_index"

# Standard page-level fields
[sites.fields.priority]
page_title = "h1"

# NEW: List extraction configuration
[sites.list_extraction]
item_selector = "a.supplier-link"      # CSS selector for item containers

[sites.list_extraction.fields]
name = "::text"                         # Extract text content
url = "::attr(href)"                    # Extract href attribute
is_partner = "img[alt*='partner']::exists"  # Check if element exists
```

### Special Extraction Syntax

The extraction rules support special modifiers:

| Syntax | Example | Description |
|--------|---------|-------------|
| `::text` | `"::text"` | Extract text content of element |
| `::attr(name)` | `"::attr(href)"` | Extract HTML attribute value |
| `::exists` | `"img::exists"` | Check if element exists (returns True/False) |
| `::text::all` | `".tag::text::all"` | Extract all matching elements as array |
| `.selector::text` | `".member-name::text"` | Chain selectors with modifiers |

### Dynamic Output Field Naming

The output array name is determined by:
1. **User override** via `output_field = "members"` in config
2. **Site type detection**: `site_type = "catalogue_index"` → auto-use `[[items]]`
3. **Default fallback**: `[[items]]`

Example outputs:
```toml
# devicemed.fr (auto-detected "items")
[[items]]
name = "3M France"
url = "https://example.com"

# biowin.org with output_field = "members"
[[members]]
name = "Argenx"
url = "https://example.com"
```

## Implementation Details

### Data Model Changes

**File: `scraper/models.py`**

Add to `SiteConfig` dataclass:
```python
list_extraction: Optional[Dict[str, Any]] = None
```

Add to `ExtractionResult` dataclass:
```python
list_items: Optional[List[Dict[str, Any]]] = None
list_items_name: Optional[str] = None
```

### Extraction Engine Changes

**File: `scraper/extraction.py`**

Add new methods to `ExtractionEngine` class:

1. **`extract_list_items(soup, list_config)`**
   - Finds all item containers using item_selector
   - Extracts fields from each item using special syntax
   - Returns list of dictionaries

2. **`_extract_from_element(element, rule)`**
   - Parses special syntax (::text, ::attr, etc.)
   - Handles single vs. array extraction modes
   - Supports nested selectors

### Config Parser Changes

**File: `scraper/config.py`**

Update `_parse_site_config()`:
- Extract `[sites.list_extraction]` section from TOML
- Validate required fields: `item_selector` and `fields`
- Pass to `SiteConfig` object

### Output Generation Changes

**File: `scraper/output.py`**

Update `_build_toml_dict()`:
- If extraction result has `list_items`:
  - Determine output field name (use `list_items_name` or default)
  - Add as array to TOML output using `[[array_name]]` syntax

## Example Outputs

### Simple Catalogue (devicemed.fr)

```toml
[extraction_metadata]
success = true
extraction_timestamp = "2026-01-04T14:30:00"
site_type = "catalogue_index"

[priority_fields]
page_title = "Fournisseurs"

# Auto-detected as "items" from site_type
[[items]]
name = "3M France"
url = "https://www.devicemed.fr/fournisseur/3m-france"

[[items]]
name = "Abbott"
url = "https://www.devicemed.fr/fournisseur/abbott"
```

### Rich Catalogue (biowin.org)

```toml
[extraction_metadata]
success = true
site_type = "catalogue_index"

[priority_fields]
page_title = "Members"

# Custom field name from config: output_field = "members"
[[members]]
name = "Argenx"
url = "https://www.biowin.org/member/argenx"
description = "Biotechnology company..."
company_type = "Company"
tags = ["Biopharmaceutical", "Antibodies"]

[[members]]
name = "UCB Pharma"
url = "https://www.biowin.org/member/ucb"
description = "Global biopharmaceutical company..."
company_type = "Company"
tags = ["Neurology", "Immunology"]
```

## Design Decisions

### ❌ Pagination: NOT included in minimal version

- Extract first page only
- **devicemed.fr**: Works perfectly (all on one page)
- **biowin.org**: Gets ~20-30 members from first page only
- **Future**: Add pagination support in Phase 3.5

### ✅ Output field naming: Auto-detect from site_type

- Default behavior: `[[items]]`
- User can override with `output_field` in config
- Enables sensible naming (suppliers, members, products, etc.)

### ✅ Attribute extraction: `::attr(name)` syntax

- Consistent with `::text` and `::exists`
- Clear, readable, chainable with selectors
- Examples:
  - `"a::attr(href)"` - extract href from anchor tag
  - `"img::attr(src)"` - extract src from image
  - `".product::attr(data-id)"` - extract custom attribute

## Success Criteria

- ✅ Can extract simple lists (devicemed.fr suppliers)
- ✅ Can extract rich lists with multiple fields (biowin.org members)
- ✅ Output valid TOML with `[[array_name]]` syntax
- ✅ Special syntax working: `::text`, `::attr(href)`, `::exists`, `::all`
- ✅ Compatible with Phase 2 scheduling system
- ✅ Backward compatible (existing configs still work)

## Files to Modify

1. `scraper/models.py` - Add list_extraction fields
2. `scraper/extraction.py` - Core extraction logic
3. `scraper/config.py` - Parse new config section
4. `scraper/output.py` - Output list items to TOML

## Files to Create

1. `config/devicemed_catalogue.toml` - Test config for simple list
2. `config/biowin_catalogue.toml` - Test config for rich list
3. `tests/test_list_extraction.py` - Unit and integration tests

## Future Enhancements (Phase 3.5+)

- Pagination support: Auto-follow "next page" links
- Nested fields: Support `tags.name`, `tags.url` for complex objects
- Alternative formats: CSV/JSON output for large catalogues
- Deduplication: Handle duplicate entries across pages
- Incremental updates: Track new/removed items between scrapes
