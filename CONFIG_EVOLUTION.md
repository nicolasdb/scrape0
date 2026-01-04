# Configuration Schema Evolution

This document tracks how the configuration schema has evolved during implementation of the Core Scraping Module, explaining the rationale for each design decision and how to extend the schema for future discoveries.

## Overview

The configuration schema is intentionally flexible to support discovery and evolution during implementation. Rather than requiring a complete schema upfront, the system was designed to adapt as scraping patterns emerged from actual site variations.

## Phase 2 (Initial Implementation)

### Schema Introduced

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

[sites.fields.priority]
name = "h1.name"
location = "span.location"
expertise = "div.expertise"
url = "a.website"
contact = "span.contact"

[sites.fields.extra]
operating_hours = "div.hours"
```

### Rationale

1. **Single TOML file**: Reduces complexity vs. per-site configs and supports version control
2. **Nested sites**: Allows multiple sites in one configuration while keeping related rules together
3. **Priority vs. Extra fields**: Distinguishes between 5 core fields (name, location, expertise, url, contact) and extensible optional fields
4. **Extraction rules as strings**: Simple format supporting CSS selectors, XPath, and regex patterns without complex data structures
5. **Site-level metadata**: id, url_pattern, site_type enable site lookup and analytics tracking

### Key Decisions

- **URL pattern matching**: Simple substring matching rather than regex, for ease of manual configuration
- **No validation on rule syntax**: Extraction fails gracefully at runtime if rule is invalid
- **Flat field structure**: Rules are strings mapping field names directly to extraction patterns
- **Defaults at two levels**: Global defaults in [scraper], with optional site-level overrides

## Phase 3 (Configuration & Extensibility)

### Schema Extensions

#### Multiple Sites Per Config
No schema change needed - already supported by multiple `[[sites]]` blocks in Phase 2

#### Extra Fields Support
No schema change needed - already supported by `[sites.fields.extra]` in Phase 2

#### Site-Specific Overrides
Added optional fields at site level:
- `timeout_seconds`: Override global default for specific site
- `max_retries`: Override global default for specific site
- `description`: Human-readable site description (optional, for documentation)

Rationale:
- Some sites are known to be slow (need higher timeout)
- Some sites are unreliable (benefit from more retries)
- Description helps with site identification and debugging

### Evolution Patterns

The configuration demonstrated the following patterns during Phase 3:

1. **Additive evolution**: New sites added without modifying existing configurations
2. **Field expansion**: New extra fields discovered and added per-site without code changes
3. **Pattern variation**: Different sites use different CSS selectors for same semantic field
   - Name field: "h1.name" vs. ".facility-title" vs. "#main h1"
   - Location: "span.location" vs. ".location-text" vs. "[data-field='location']"

## Future Enhancements (Phase 4+)

### Potential Schema Extensions

#### Field-Level Configuration
Possible future addition (not yet needed):
```toml
[sites.fields.priority.name]
selector = "h1.name"
fallback_selector = "h2"  # Try this if primary fails
required = true  # Mark fields as critical vs. optional
```

Rationale: Allow field-specific retry logic and fallback rules. Currently not needed since extraction is field-level graceful already.

#### Extraction Rule Library
Possible future enhancement:
```toml
[rule_templates]
# Reusable extraction patterns
email_pattern = "/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/"
equipment_separator = "comma"  # Hint for list parsing
```

Rationale: Reduce duplication when same pattern used across sites. Currently not needed for small initial site set.

#### Analytics Configuration
Possible future addition:
```toml
[analytics]
track_extraction_duration = true
track_http_status = true
sample_rate = 1.0  # 0.0-1.0, sample fraction of requests
```

Rationale: Configure what metadata to collect for Phase 2 analytics. Currently metadata is always collected.

#### Multi-Method Testing
Possible Phase 2 enhancement:
```toml
[[sites.extraction_methods]]
method_name = "css_selectors"
rules = { name = "h1.name", ... }
priority = 1

[[sites.extraction_methods]]
method_name = "xpath"
rules = { name = "//h1[@class='name']", ... }
priority = 2
```

Rationale: Support testing multiple extraction approaches on same site for reliability comparison. Currently single method per site.

## Adding New Fields During Implementation

### Recommended Process

1. **Discover field** while examining a new site's HTML
2. **Add as extra field** first (low risk, doesn't affect success determination)
   - Modify config: add entry under `[sites.fields.extra]`
   - No code changes required
   - Test extraction by running scraper on that site
3. **If successful**, evaluate importance:
   - If site-specific: keep as extra field
   - If widely applicable: consider promoting to priority field
4. **Promotion process** (if needed):
   - Add to all applicable site configs under `[sites.fields.priority]`
   - Update success determination logic if needed
   - Ensure all priority fields present in ExtractionResult

### Example: Adding Equipment Information

Stage 1 - Discovery (config change only):
```toml
[sites.fields.extra]
operating_hours = "div.hours"
equipment = "ul.equipment li"  # <- New discovery
```

Stage 2 - Testing:
- Run scraper on site with new field
- Verify extraction works and field appears in TOML output

Stage 3 - Promotion (if widely needed):
```toml
[sites.fields.priority]
name = "h1.name"
location = "span.location"
expertise = "div.expertise"
equipment = "ul.equipment li"  # <- Promoted
url = "a.website"
contact = "span.contact"
```

## Configuration Validation

The configuration system validates:

1. **Required fields**: `id`, `url_pattern`, `site_type`, `primary_library`
2. **Type correctness**: sites must be list, fields must be dicts
3. **Value constraints**: timeout_seconds > 0, max_retries >= 0
4. **No schema constraints**: Missing optional fields silently use defaults

This permissive validation enables schema to evolve - new optional fields can be added without updating validation logic.

## Best Practices for Configuration

### Naming Conventions
- Site id: lowercase with hyphens (e.g., "example-fablab", "tech-makerspace")
- Field names: lowercase with underscores (e.g., "operating_hours", "membership_cost")
- Site type: lowercase single word (e.g., "fablab", "makerspace", "hackerspace")

### Rule Writing
- Start with CSS selectors (simplest, most common)
- Use class selectors when available (".class-name")
- Use element selectors for unique elements ("h1", "h2")
- Fall back to XPath (//) for complex hierarchies
- Use regex (/) only for pattern extraction within text

### Organization
- Keep related fields together (priority first, then extra)
- Group multiple sites logically in file
- Use `description` field liberally for documentation
- Comment unusual or fragile selectors

## Testing Configuration Changes

### Adding a New Site

1. Create config entry with site rules
2. Write extraction test with sample HTML for that site
3. Verify all priority fields extract correctly
4. Run: `pytest tests/test_extraction.py -v`

### Modifying Extraction Rules

1. Update selector/pattern in config
2. Update corresponding test fixture if needed
3. Run extraction tests to verify
4. Check TOML output for correct field values

### Checking Multi-Site Lookup

1. Verify url_pattern doesn't conflict with existing sites
2. Confirm URL matching works: `test_lookup_different_sites_by_url`
3. Ensure cache works correctly if same URL accessed twice

## Summary

The configuration schema was designed with evolution in mind:

- **Flexible structure**: New fields added without code changes
- **Layered defaults**: Global settings with site-level overrides
- **Graceful extraction**: Missing fields don't halt processing
- **Simple rule format**: Strings enable manual editing without schema knowledge
- **Extensible design**: Extra fields enable experimentation before committing to schema changes

As new sites are added and patterns emerge, the configuration adapts by:
1. Adding new sites to [[sites]] blocks
2. Adding new extraction rules under fields.extra
3. Configuring site-specific timeouts/retries as needed
4. Using comments to document unusual patterns

For future phases, the schema can be extended with field-level config, rule libraries, analytics settings, and multi-method testing - all without breaking existing configurations.
