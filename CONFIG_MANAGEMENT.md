# Configuration Management Guide

## How Config Files Are Generated

### Direct Answer: **Config files are NOT auto-generated**

The current config files were:
- ✓ **Manually created by Claude** during implementation
- ✓ Based on analyzing which websites we wanted to test
- ✓ Created to demonstrate different extraction patterns

**Current config files and their origin:**
- `config/example.toml` - Demonstration file with example-fablab.com
- `config/real-world.toml` - Multi-site test file with Wikipedia, GitHub, example.com
- `config/openfab.toml` - Real Belgian FabLab (openfab.be)

### Why Not Auto-Generated?

Config files CANNOT be auto-generated because they require **manual inspection** of target websites:

1. **CSS selectors are site-specific**
   ```html
   <!-- Site A uses: -->
   <h1 class="title">Name</h1>

   <!-- Site B uses: -->
   <div id="facility-name">Name</div>

   <!-- Site C uses: -->
   <span data-role="name">Name</span>
   ```

2. **Each site has different HTML structure** - No two websites are identical
3. **Manual inspection required** - Use browser DevTools to find selectors
4. **Domain knowledge needed** - Know what data to extract and why

## Do You Need a Config for Each URL?

### Short Answer: **NO - One config can handle many URLs**

You can have a **single config file with multiple site configurations**. The scraper uses URL pattern matching to find the right config.

### Example: Single Config File for Multiple Sites

**File: `config/fablabs.toml`**
```toml
[scraper]
primary_library = "scrapling"
timeout_seconds = 20
max_retries = 2

# Site 1: OpenFab Brussels
[[sites]]
id = "openfab-brussels"
url_pattern = "openfab.be"
site_type = "fablab"
[sites.fields.priority]
title = "h1"
intro = "p"
contact = "span.contact"

# Site 2: TechLab Vienna
[[sites]]
id = "techlab-vienna"
url_pattern = "techlab.wien"
site_type = "fablab"
[sites.fields.priority]
title = ".facility-name"
location = ".address"
contact = ".email"

# Site 3: FabLab Barcelona
[[sites]]
id = "fablab-barcelona"
url_pattern = "fablabbcn.org"
site_type = "fablab"
[sites.fields.priority]
title = "h1.page-title"
description = "div.about"
```

### How URL Matching Works

```bash
# Command:
./run.sh https://openfab.be ./config/fablabs.toml

# Process:
1. Extract domain: openfab.be
2. Look through all [[sites]] in config
3. Find: url_pattern = "openfab.be"
4. Use that configuration
5. Extract fields with those selectors
```

### When to Create Separate Configs

Even though you can use one config, create separate ones for **organization**:

```
config/
├── fablabs.toml          # All FabLab configurations
├── makerspaces.toml      # All Makerspace configurations
├── hackerspaces.toml     # All Hackerspace configurations
├── generic.toml          # Fallback generic configuration
└── real-world.toml       # Test suite multi-site example
```

**Benefits of separation:**
- Easier to maintain
- Faster to find specific site config
- Different sites of same type may have similar rules
- Can apply type-specific settings (timeouts, retry logic)

## Starting Simple: Single Config, Multiple Sites

### Phase 1: Generic Config (5 minutes)

Create `config/myconfig.toml`:
```toml
[scraper]
primary_library = "scrapling"
timeout_seconds = 20
max_retries = 2

[[sites]]
id = "generic"
url_pattern = "example.com"
site_type = "generic"

[sites.fields.priority]
title = "h1"
description = "p"
content = "body"
```

### Phase 2: Test and Inspect (10-15 minutes)

```bash
# Test the URL
./run.sh https://example.com ./config/myconfig.toml

# Check output
cat output/real-test.toml
```

Expected output structure:
```toml
[extraction_metadata]
success = true
site_type = "generic"

[priority_fields]
title = "..."
description = "..."
content = "..."

[fields_status]
extracted = ["title", "description", "content"]
not_found = []
failed = []
```

### Phase 3: Refine Selectors (20-30 minutes)

1. **Open website in browser** (Chrome/Firefox)
2. **Inspect target element**:
   - Right-click → Inspect Element
   - Find the CSS class or ID
   - Look at the HTML structure

3. **Update config with better selectors**:
```toml
[[sites]]
id = "example-refined"
url_pattern = "example.com"

[sites.fields.priority]
title = "h1.main-heading"           # More specific
description = "div.intro-paragraph" # Based on inspection
content = "div.article-content"     # More targeted
```

4. **Test again and iterate**:
```bash
./run.sh https://example.com ./config/myconfig.toml
# Check results, refine further if needed
```

### Phase 4: Add More Sites (5-10 minutes per site)

Once your first site works, add more to the same config:

```toml
[[sites]]
id = "site2"
url_pattern = "site2.com"
site_type = "fablab"

[sites.fields.priority]
title = "h1"
location = "span.loc"
# ... etc

[[sites]]
id = "site3"
url_pattern = "site3.com"
site_type = "fablab"

[sites.fields.priority]
title = ".name"
# ... etc
```

Test all with same config:
```bash
./run.sh https://site2.com ./config/myconfig.toml
./run.sh https://site3.com ./config/myconfig.toml
```

## Study and Refine: Configuration Evolution

### Starting Point: Generic Rules

```toml
# Very simple - works for many sites
[sites.fields.priority]
title = "h1"
description = "p"
```

### Observation Phase: What's Actually on the Site?

Use **browser DevTools Inspector** to understand structure:

```
Common patterns found:
- Titles: h1, h1.title, h1.heading, div.facility-name
- Descriptions: p, div.description, article, div.intro
- Contact: span.email, a[href*="mailto"], div.contact
- Location: span.address, .location, .address-block
```

### Refinement: Build a Library of Patterns

**Pattern 1: Modern websites (CSS framework)**
```toml
title = "h1.display-large"
description = "p.lead"
contact = "a[data-role='contact']"
```

**Pattern 2: Older websites (basic HTML)**
```toml
title = "h1"
description = "p"
contact = "a[href*='mailto']"
```

**Pattern 3: SPAs / Dynamic sites (class-heavy)**
```toml
title = ".hero__title"
description = ".content__description"
contact = ".footer__email"
```

### Iteration Example

**Attempt 1** (80% extracted):
```toml
title = "h1"
location = "p"
contact = "email"  # FAILED - selector doesn't exist
```

**Attempt 2** (90% extracted):
```toml
title = "h1"
location = "span.location"  # Now extracts!
contact = "a[href*='mailto']"  # Better selector
```

**Attempt 3** (95%+ extracted):
```toml
title = "h1.site-title"  # More specific
location = "span.location-text"  # Even more specific
contact = ".footer__email"  # Perfect match
```

## Simple Runners

### Option 1: Run with Default Config Detection

```bash
./run.sh https://openfab.be
# Automatically finds config/openfab.be.toml or matches url_pattern
```

### Option 2: Run with Explicit Config

```bash
./run.sh https://openfab.be ./config/openfab.toml
```

### Option 3: Run with Full Test Script

```bash
./run_tests.sh https://openfab.be ./config/openfab.toml
# Same as run.sh but with more verbose output
```

## Analytics: Current Status & Future

### ❌ NOT in Current Spec

The current implementation (Phases 0-6) focuses on:
- ✓ **Core scraping module** - Fetching and extracting data
- ✓ **Configuration system** - Defining what to extract
- ✓ **TOML output** - Structured data with metadata
- ✓ **Error handling** - Robust failure recovery
- ✓ **Testing** - 177 unit tests + real-world tests

### 📊 Analytics: Phase 2+ Feature

Analytics would be a **separate Phase 2 or later**:

```
Phase 2+ Analytics Features (PLANNED, NOT IMPLEMENTED):
├── Data Aggregation
│   ├── Collect multiple scrape results
│   ├── Track changes over time
│   └── Aggregate metrics by site type
│
├── Analytics Dashboard (Frontend)
│   ├── Web UI to view metrics
│   ├── Charts/graphs of extraction success
│   └── Site status monitoring
│
├── Metrics Tracking
│   ├── Extraction success rate by site
│   ├── Field-level extraction accuracy
│   ├── Average extraction time
│   └── Timeout/error rates
│
└── Data Storage
    ├── Database for historical data
    ├── Time-series metrics
    └── Audit logs of all scrapes
```

### Why Analytics is Separate

1. **Different concerns** - Analytics = analyzing past results
2. **Different stack** - Would need: database, API, frontend framework
3. **Not in MVP scope** - Focus on scraping first, analytics later
4. **Optional feature** - Works without analytics, analytics doesn't work without core

### Current Output Available for Analytics

The TOML output **already contains data useful for analytics**:

```toml
[extraction_metadata]
success = true                              # Success/fail tracking
extraction_timestamp = "2026-01-04T11:37:31"  # When extracted
extraction_duration_seconds = 0.5           # Performance metric
failure_reason = null                       # Error tracking
site_type = "fablab"                        # Site categorization

[fields_status]
extracted = ["title", "intro"]              # What succeeded
failed = []                                 # What failed
not_found = ["contact"]                     # What wasn't found
```

### Building Analytics Later

When Phase 2 analytics is built, it can:
1. Read all TOML files from `output/`
2. Parse metadata and extract results
3. Aggregate success rates, timing, errors
4. Display in web dashboard
5. Store in database for trends

## Best Practices Summary

| Goal | Approach |
|------|----------|
| **Quick test of one site** | `./run.sh https://site.com ./config/site.toml` |
| **Test multiple sites** | One config file with multiple `[[sites]]` sections |
| **Organize by type** | Separate configs: `fablabs.toml`, `makerspaces.toml` |
| **Iterate and refine** | Use browser DevTools, update selectors, test again |
| **Production deployment** | Version control configs, document site-specific rules |
| **Analytics** | Phase 2+ feature, store TOML files for later analysis |

## Files in This Project

- **`config/example.toml`** - Documented example (template)
- **`config/real-world.toml`** - Multi-site test configuration
- **`config/openfab.toml`** - Real FabLab configuration
- **`run.sh`** - Simple runner (auto-detects config)
- **`run_tests.sh`** - Full test runner (requires explicit config)
- **`test_real_urls.py`** - Underlying test script
- **`CONFIG_MANAGEMENT.md`** - This file (you are here)
- **`REAL_URL_TESTING.md`** - Real website testing guide
- **`QUICK_START.md`** - Updated with config explanation

## Next Steps

1. **Choose approach**:
   - ✓ Start with single generic config for all sites
   - ✓ Gradually add site-specific configurations as needed
   - ✓ Organize by type once you have many sites

2. **Create your first config** for your target websites

3. **Test and iterate**:
   ```bash
   ./run.sh <your-url> ./config/myconfig.toml
   # Check output/real-test.toml
   # Refine selectors
   # Repeat
   ```

4. **Add more sites** to the same config

5. **Consider Phase 2** analytics when ready to analyze results
