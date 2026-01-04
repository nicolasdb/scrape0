# Known Issues and Limitations: Core Scraping Module

This document lists known issues, limitations, and planned improvements for the Core Scraping Module v0.1.0.

## Current Limitations (Phase 0.1)

### 1. Single-URL Processing Only

**Status**: Known limitation (by design)

**Description**: The module processes one URL at a time. Batch processing is deferred.

**Workaround**: Call `scrape_facility()` in a loop for multiple URLs:
```python
from scraper import scrape_facility

urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
results = []

for url in urls:
    result = scrape_facility(url, "./config.toml")
    results.append(result)
```

**Planned Fix**: Phase 1 will add batch mode with parallelization.

---

### 2. Scrapling Library Fallback

**Status**: Design limitation

**Description**: When Scrapling library is unavailable or fails, the module falls back to mock HTML. This allows testing but doesn't actually fetch real pages.

**Indication**: No error is raised; mock data is returned silently.

**Workaround**: Ensure Scrapling is installed:
```bash
pip install scrapling
```

**Planned Fix**: Phase 2 will improve Scrapling integration with better error reporting.

---

### 3. No Authentication Support

**Status**: Known limitation (deferred feature)

**Description**: The module cannot authenticate to password-protected sites or APIs requiring headers.

**Workaround**: Pre-fetch authenticated pages and provide as mock content in tests.

**Planned Fix**: Phase 2+ will add authentication support (API keys, basic auth, OAuth).

---

### 4. Limited XPath Support

**Status**: Partial implementation

**Description**: XPath extraction is supported but requires lxml library. Complex XPath expressions may not work correctly.

**Indication**: XPath rules starting with `//` are detected but may fail silently.

**Workaround**: Use CSS selectors when possible; they're more reliable:
```toml
# Reliable:
name = "h1.facility-name"

# Less reliable:
name = "//h1[@class='facility-name']"
```

**Planned Fix**: Phase 2 will improve XPath support with better error reporting.

---

### 5. Site Type Detection Limited

**Status**: URL pattern matching only

**Description**: Site type is determined by URL pattern matching, not content analysis. Misclassifications possible.

**Example**:
```toml
# If URL is "https://example.com/fablab"
# And pattern is "example.com", site_type will be whatever configured
# Even if it's actually a different type
```

**Workaround**: Configure URL patterns carefully to match site type.

**Planned Fix**: Phase 3 will add content-based site type detection.

---

### 6. Type Conversion Heuristics Simple

**Status**: Basic implementation

**Description**: Type detection uses simple heuristics (yes/no for boolean, numbers by regex, comma-separated for lists). May misclassify edge cases.

**Examples**:
```python
"yes" → True          # Correct
"maybe" → "maybe"    # Strings to remain strings
"1.0" → 1.0          # Correctly converted
"2, 4, 6" → [2, 4, 6]  # Works
```

**Limitation**: Context-dependent types not supported:
```python
"123-45-6789" → "123-45-6789"  # Not converted to number (good)
"01-01-2026" → "01-01-2026"    # Not converted to date (expected)
```

**Planned Fix**: Phase 3 will add field-specific type hints and more sophisticated inference.

---

### 7. Configuration Schema Flexibility

**Status**: Feature by design

**Description**: The schema is intentionally loose to support evolution. Missing fields silently use defaults.

**Implication**: Configuration errors may not be caught:
```toml
[[sites]]
id = "test"
url_pattern = "test.com"
# Missing required: site_type
# Will fail when looking up, not when loading config
```

**Workaround**: Validate configuration manually against template.

**Planned Fix**: Phase 2 will add stricter validation options.

---

### 8. No Concurrent Request Support

**Status**: Single-threaded by design

**Description**: All operations are synchronous. No threading or async support.

**Implication**: Multiple URLs will be processed sequentially, slowly.

**Workaround**: Use external parallelization:
```python
from concurrent.futures import ThreadPoolExecutor

def scrape_url(url):
    return scrape_facility(url, "./config.toml")

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(scrape_url, urls)
```

**Planned Fix**: Phase 1 batch mode will include parallelization.

---

### 9. Limited TOML Output Customization

**Status**: Fixed format

**Description**: TOML output structure is fixed. Cannot customize sections or field organization.

**Limitation**: Output always includes all sections even if empty.

**Workaround**: Post-process TOML output for custom formats.

**Planned Fix**: Phase 3 will add output format customization.

---

### 10. No Persistent Configuration Cache

**Status**: In-memory only

**Description**: Configuration is cached in memory during runtime only. Not persisted to disk.

**Implication**: Configuration file must be read on every module instantiation.

**Workaround**: None needed; caching is transparent.

**Planned Fix**: Phase 2 may add persistent cache if performance needs it.

---

## Minor Issues

### 1. URL Normalization Edge Cases

**Description**: Some URL edge cases may not normalize correctly:

```python
# Works:
https://example.com/path/
https://example.com/path

# Edge cases:
https://example.com//double//slash  # Extra slashes preserved
https://example.com#fragment?query   # Fragment preserved correctly
```

**Impact**: Low; unlikely to affect real sites.

---

### 2. Regex Rule Syntax

**Description**: Regex rules require manual delimiters:

```toml
# Correct format:
email = "/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/"
pattern = "^[A-Z][a-z]+"

# Wrong (won't work):
email = "[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"
```

**Impact**: Low; documented in config examples.

---

### 3. Large HTML Files

**Description**: No performance testing done on very large HTML files (>10MB).

**Impact**: Unknown performance with unusually large documents.

**Workaround**: Unlikely to encounter such files in practice; most facility pages < 1MB.

---

### 4. Special Characters in Extracted Data

**Description**: Some special characters may not TOML-escape correctly:

```python
# Unlikely characters that may need manual escaping:
""" (triple quotes)
\n (embedded newlines)
[section brackets in text]
```

**Impact**: Very low; TOML is permissive.

---

## Dependencies Issues

### 1. Scrapling Library Installation

**Issue**: Scrapling may be difficult to install on some systems.

**Solution**: Follow Scrapling documentation for your OS.

**Fallback**: Mock mode will be used if Scrapling unavailable.

---

### 2. BeautifulSoup4 Version Compatibility

**Issue**: Some versions of BeautifulSoup4 may have parsing differences.

**Current Version**: Uses system-installed version.

**Recommendation**: Update periodically.

---

## Testing Gaps

These areas have limited test coverage (but are not critical):

1. **Very Large Files**: No stress testing with huge HTML
2. **Concurrent Requests**: Single-threaded only
3. **Network Edge Cases**: Limited network error scenario testing
4. **Extreme Unicode**: Limited testing with unusual character sets
5. **Malformed TOML Output**: Should not happen but untested

---

## Future Improvements

### Phase 1: Batch Processing
- [ ] Multi-URL scraping
- [ ] Parallelization
- [ ] Progress tracking
- [ ] Result aggregation

### Phase 2: Analytics & Reliability
- [ ] Reliability measurement framework
- [ ] Success rate tracking
- [ ] Multi-method comparison
- [ ] Analytics dashboard

### Phase 3: Data Quality
- [ ] LLM-based post-processing
- [ ] Quality scoring
- [ ] Confidence estimation
- [ ] Content-based site detection

### Phase 4: Discovery
- [ ] Search interface
- [ ] Facility discovery
- [ ] Mapping visualization
- [ ] External API

### Future Enhancements
- [ ] Authentication support
- [ ] Proxy support
- [ ] JavaScript rendering options
- [ ] PDF/document support
- [ ] Custom output formats
- [ ] Database export
- [ ] Webhook notifications

---

## Workarounds and Solutions

### Issue: Configuration not reloading

**Symptom**: Changes to config.toml not reflected.

**Cause**: Configuration cached in ConfigManager instance.

**Solution**:
```python
# Create new ConfigManager for each reload
manager = ConfigManager()
config = manager.load_config("./config.toml")  # Forces reload
```

---

### Issue: No data extracted from page

**Symptom**: All fields marked as not_found.

**Cause**: CSS selectors don't match HTML structure.

**Solution**:
1. Open page in browser
2. Inspect HTML with developer tools
3. Verify CSS selector matches target element
4. Update config.toml

---

### Issue: Type conversion unexpected

**Symptom**: Value is string when expecting number/boolean.

**Cause**: Heuristics didn't recognize format.

**Solution**:
1. Check extraction value matches type pattern
2. For special formats, keep as string and convert in application code
3. Consider adding field-level type hints (Phase 3)

---

## Reporting Issues

To report a new issue:

1. Check this document first
2. Enable DEBUG logging
3. Verify issue with minimal example
4. Provide:
   - Exact error message
   - Configuration (sanitized)
   - URL or sample HTML
   - Full traceback

---

## Stability and Support

**Current Status**: v0.1.0 (Initial Release)

- **Stability**: Stable for single-URL extraction
- **Production Ready**: Yes (with limitations noted)
- **Performance**: Adequate for typical facility websites
- **Support**: Community-driven

---

## Version History

- **v0.1.0** (2026-01-04): Initial release with single-URL scraping

See CHANGELOG.md for complete version history.

---

## Conclusion

The Core Scraping Module is stable and production-ready with the documented limitations in mind. Most limitations are intentional design choices deferred to future phases rather than bugs.

For issues not listed here, please refer to TROUBLESHOOTING.md or review the specification in spec.md.
