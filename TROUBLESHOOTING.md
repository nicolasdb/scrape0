# Troubleshooting Guide: Core Scraping Module

This guide covers common issues and how to resolve them.

## Configuration Issues

### Issue: "Configuration file not found"

**Symptoms**:
```
ConfigurationError: Configuration file not found: ./config.toml
```

**Solution**:
1. Verify the config file exists: `ls -la config.toml`
2. Check the path is correct (relative or absolute)
3. Use absolute path if in different directory:
   ```python
   result = scrape_facility(
       url="https://example.com",
       config_path="/full/path/to/config.toml"
   )
   ```

### Issue: "Invalid TOML syntax"

**Symptoms**:
```
ConfigurationError: Invalid TOML syntax in configuration file: ...
```

**Solution**:
1. Check TOML syntax - common mistakes:
   - Missing closing brackets: `[section` instead of `[section]`
   - String quotes: ensure `key = "value"` (not `key = value`)
   - List format: use `[[sites]]` for array of tables, not `[sites]`
2. Validate with online TOML validator: https://www.toml-lint.com/
3. Compare against `config.toml.example`

### Issue: "No site configuration found for URL"

**Symptoms**:
```
ConfigurationError: No site configuration found for URL: https://example.com
```

**Solution**:
1. Check `url_pattern` in config matches your URL:
   ```toml
   # This matches: https://example.com/about, https://example.com/page
   # But NOT: https://other.com
   url_pattern = "example.com"
   ```
2. Use substring matching - the pattern must appear in the URL
3. Add new site if URL pattern not configured:
   ```toml
   [[sites]]
   id = "new-site"
   url_pattern = "newsite.com"
   site_type = "fablab"

   [sites.fields.priority]
   name = "h1"
   ```

### Issue: "Required fields missing in configuration"

**Symptoms**:
```
ConfigurationError: Each site must have 'id', 'url_pattern', and 'site_type' fields
```

**Solution**:
Ensure each site has all required fields:
```toml
[[sites]]
id = "unique-site-id"           # Required: unique identifier
url_pattern = "site.com"        # Required: URL pattern to match
site_type = "fablab"            # Required: site categorization

[sites.fields.priority]          # Required: at least one priority field
name = "h1.name"
```

## URL Validation Issues

### Issue: "Invalid URL format"

**Symptoms**:
```
URLValidationError: Invalid URL format: example.com
```

**Solution**:
URLs must include scheme (http:// or https://):
```python
# Wrong:
scrape_facility("example.com")

# Correct:
scrape_facility("https://example.com")
scrape_facility("http://example.com")
```

The module auto-normalizes URLs - if you forget https://, you'll get an error. Add it explicitly.

### Issue: Trailing slashes or parameters causing lookup failures

**Symptoms**:
```
# Config has:
url_pattern = "example.com"

# But URL is:
https://example.com/about/    # Extra slash
https://example.com?page=1    # Query parameter
```

**Solution**:
The module automatically handles these:
- Trailing slashes are removed
- Query parameters and fragments are preserved for matching

If lookup still fails, ensure `url_pattern` is a substring of the full URL:
```python
url = "https://example.com/about?page=1"
# Patterns that will match:
# "example.com" ✓
# "example" ✓
# "/about" ✓

# Patterns that won't match:
# "example.org" ✗
# "other.com" ✗
```

## Extraction Issues

### Issue: No fields extracted (success=False)

**Symptoms**:
```python
{
  'success': False,
  'data': {'priority_fields': {}, 'extra_metadata': {}},
  'metadata': {
    'failure_reason': 'no_fields_extracted'
  }
}
```

**Solutions**:

1. **Check HTML structure matches rules**:
   ```python
   # config.toml has:
   name = "h1.facility-name"  # CSS selector

   # But HTML is:
   <h1>Facility Name</h1>    # No class="facility-name"!
   ```

   Solution: Update config to match actual HTML:
   ```toml
   name = "h1"  # Just h1 element
   ```

2. **Verify CSS selector syntax**:
   ```toml
   # Correct CSS selectors:
   name = "h1"                    # Element
   name = ".facility-name"        # Class
   name = "#main-title"           # ID
   name = "div.container h1"      # Descendant
   name = "h1.primary.title"      # Multiple classes
   ```

3. **Test with browser developer tools**:
   - Right-click on the data in browser
   - Select "Inspect" to see the HTML structure
   - Verify your CSS selector would select that element
   - Update config.toml accordingly

4. **Enable debug logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)

   result = scrape_facility("https://example.com", "./config.toml")
   # Will print detailed extraction attempts
   ```

### Issue: "Partial extraction - some fields missing"

**Symptoms**:
```python
{
  'success': True,  # Still successful because some fields extracted
  'data': {
    'priority_fields': {'name': 'Facility Name'},
    'extra_metadata': {}
  },
  'metadata': {
    'fields_status': {
      'extracted': ['name'],
      'failed': [],
      'not_found': ['location', 'expertise', 'url', 'contact']
    }
  }
}
```

**Solution**:
This is normal graceful degradation. Fields are "not_found" because:
1. HTML doesn't contain that data
2. CSS selector doesn't match the element
3. Element is dynamically loaded (Scrapling needed)

Options:
1. **Adjust selectors** for missing fields
2. **Add fallback selectors** using extra_fields:
   ```toml
   [sites.fields.priority]
   name = "h1"
   location = "span.location"

   [sites.fields.extra]
   location_alt = "div.address"  # Fallback pattern
   ```
3. **Accept partial data** - some sites don't have all fields

### Issue: "HTML parsing error"

**Symptoms**:
```
ParsingError: Failed to parse HTML content: ...
```

**Solution**:
This is rare with BeautifulSoup. Usually indicates:
1. Empty HTML response from website
2. Extremely malformed HTML
3. Binary content returned instead of HTML

Try:
1. Test URL in browser to verify it loads
2. Check HTTP response with curl:
   ```bash
   curl -I https://example.com
   # Should show: HTTP/1.1 200 OK
   ```
3. Verify site is accessible without authentication

## Type Conversion Issues

### Issue: "Field extracted but type conversion failed"

**Symptoms**:
```python
# Config has:
expertise = "div.expertise"

# HTML contains:
<div class="expertise">3D Printing, Electronics</div>

# Result gets:
'expertise': '3D Printing, Electronics'  # String, not list
```

**Solution**:
The module auto-detects types. For comma-separated lists:
```python
# If you want this as a list:
'expertise': ['3D Printing', 'Electronics']

# The HTML needs to be structured like:
<div class="expertise">
  <span>3D Printing</span>
  <span>Electronics</span>
</div>

# Or the text needs commas:
<div class="expertise">3D Printing, Electronics</div>
# This works! Comma-separated strings become lists.
```

Type conversion rules:
- `"yes"`, `"no"`, `"true"`, `"false"`, `"1"`, `"0"` → boolean
- `"42"`, `"3.14"` → number
- `"item1, item2"` → list
- Everything else → string

## TOML Output Issues

### Issue: "Output file not created"

**Symptoms**:
```python
result = scrape_facility(
    url="https://example.com",
    config_path="./config.toml",
    output_path="./output/example.toml"
)

# File not created in ./output/
```

**Solution**:
1. Verify output directory is writable:
   ```bash
   ls -la output/
   # If output doesn't exist, the module should create it
   # If permission denied, create directory first:
   mkdir -p output
   chmod 755 output
   ```

2. Check return value `success` flag - file only written on success:
   ```python
   if result['success']:
       # File should be written
       print(f"Check: {output_path}")
   else:
       # No file written on failure
       print(f"Extraction failed: {result['metadata']['failure_reason']}")
   ```

3. If output_path not provided, no file is written:
   ```python
   # This won't create a file:
   result = scrape_facility(url)

   # This will:
   result = scrape_facility(url, output_path="./out.toml")
   ```

### Issue: "TOML output invalid"

**Symptoms**:
```
Trying to open generated TOML file:
Error: Invalid TOML syntax
```

**Solution**:
The module validates TOML before writing. This should not happen in normal use.

If it does:
1. Check for special characters in extracted data:
   ```python
   # Some characters need escaping:
   # Quotes: "text with \"quotes\""
   # Newlines: represented as \\n in TOML
   # Tab: represented as \\t
   ```

2. Verify with external tool:
   ```bash
   python -m tomli < output/example.toml
   # Should succeed if TOML is valid
   ```

3. Check string values don't have unescaped quotes or newlines

## Logging Issues

### Issue: "Not enough debug information"

**Solution**:
Enable debug logging:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

result = scrape_facility(url, config)
# Now you'll see:
# - Configuration loading
# - Site lookup
# - HTML fetching
# - Field extraction attempts
# - Type conversions
# - Output file writing
```

### Issue: "Too much logging noise"

**Solution**:
Set specific logger level:

```python
import logging

# Quiet everything except scraper
logging.basicConfig(level=logging.WARNING)
logging.getLogger('scraper').setLevel(logging.INFO)

result = scrape_facility(url, config)
```

## Performance Issues

### Issue: "Scraping is very slow"

**Symptoms**:
```python
# Takes 30+ seconds for single site
result = scrape_facility(url)
```

**Solutions**:

1. **Check timeout setting**:
   ```toml
   [scraper]
   timeout_seconds = 30  # Default

   # For faster sites:
   timeout_seconds = 5

   # For slow sites:
   timeout_seconds = 60
   ```

2. **Network issues**:
   - Test site response: `curl -w "@curl-format.txt" -o /dev/null -s https://example.com`
   - Check internet connection
   - Try different network (if available)

3. **Site-specific override**:
   ```toml
   [[sites]]
   id = "fast-site"
   url_pattern = "fast.com"
   timeout_seconds = 5

   [[sites]]
   id = "slow-site"
   url_pattern = "slow.com"
   timeout_seconds = 60
   ```

## Getting Help

If you encounter issues not covered here:

1. **Check logs** - enable DEBUG logging for detailed info
2. **Review configuration** - compare against `config.toml.example`
3. **Test HTML structure** - use browser inspector to verify CSS selectors
4. **Check specification** - see `spec.md` for design decisions
5. **Review test examples** - tests in `tests/` show expected behavior

## Reporting Bugs

If you believe you've found a bug:

1. Enable DEBUG logging
2. Record the exact error message
3. Provide the configuration (without sensitive data)
4. Note the URL or describe the HTML structure
5. Include full error traceback

This information helps diagnose and fix issues.

## FAQ

### Q: Can I scrape multiple URLs?
**A**: Not yet. Phase 1 expansion will add batch mode. Currently: one URL at a time.

### Q: Can I use authentication?
**A**: Not in Phase 0-1. Phase 2+ will support authenticated scraping.

### Q: What about JavaScript-heavy sites?
**A**: Scrapling library handles JavaScript. Just provide the URL - library loads the page in a browser.

### Q: How do I improve extraction rates?
**A**: See CONFIG_EVOLUTION.md for patterns. Adjust CSS selectors to match actual HTML structure.

### Q: Can I add new field types?
**A**: Yes! Add to `[sites.fields.extra]` in config without code changes.

## Version Information

- Module Version: 0.1.0
- Python: 3.9+
- Main Dependencies: scrapling, tomli, beautifulsoup4

See ARCHITECTURE.md for design overview and spec.md for full specification.
