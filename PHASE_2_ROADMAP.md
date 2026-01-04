# Phase 2: Onboarding & Periodic Monitoring Roadmap

## What You've Discovered (Phase 1 Complete ✓)

### The Workflow Pattern
```
1. NEW URL arrives
   ↓
2. Test with standard/default config
   ↓
3. See what extracts vs what doesn't
   ↓
4. Create CUSTOM config for that domain
   ↓
5. Refine selectors using browser DevTools
   ↓
6. Test again (iterative improvement)
   ↓
7. Save as permanent config
   ↓
8. Future runs auto-detect custom config
   ↓
9. Run periodically (daily, weekly, etc)
   ↓
10. Collect results in TOML files
```

### Current State (Phase 0-1: COMPLETE ✓)
- ✓ Core scraping works
- ✓ Real-world testing works
- ✓ Configuration system flexible
- ✓ Custom config creation works
- ✓ Auto-detection works

### Missing: Phase 2 - ONBOARDING WORKFLOW
What we DON'T have yet:
- ❌ Systematic onboarding process for new sites
- ❌ Site discovery and registration system
- ❌ Configuration best practices guide
- ❌ Periodic scheduling (cron jobs, etc)
- ❌ Results aggregation and analytics
- ❌ Configuration templates by industry
- ❌ Validation and quality checks

---

## Phase 2: Onboarding & Periodic Monitoring

### Phase 2.1: Site Onboarding System

**Goal**: Structured process for adding new sites

#### 2.1.1: Site Registration
```
When someone has a new URL to scrape:

1. Register the site
   - URL
   - Industry/Type (fablab, makerspace, hackerspace, etc)
   - What data matters
   - Scrape frequency (daily, weekly, monthly)

2. Auto-generate initial config
   - Create config/{domain}.toml
   - Add generic selectors
   - Set appropriate timeouts

3. Test and validate
   - Run scraper
   - Show extraction results
   - Get feedback on what worked/didn't

4. Refine selectors
   - User inspects website
   - Updates CSS selectors
   - Re-tests

5. Save and activate
   - Store permanent config
   - Add to auto-detection
   - Schedule periodic runs
```

#### 2.1.2: Tools Needed
```python
# New tool: site_registry.py
class SiteRegistry:
    def register_site(url, site_type, data_needs):
        """Register new site for monitoring"""
        # Create config file
        # Add to registry
        # Schedule if requested

    def list_sites(site_type=None):
        """List all registered sites"""

    def get_site_config(url):
        """Get config for URL"""

    def update_site_config(url, updates):
        """Update existing config"""
```

#### 2.1.3: Web UI for Onboarding (Optional Phase 2.5)
```
Simple form:
- URL input
- Select industry (FabLab, Makerspace, etc)
- What data to extract
- Frequency (daily, weekly)

→ Auto-generates config
→ Shows extraction preview
→ Let user refine
```

### Phase 2.2: Configuration Templates by Type

**Goal**: Pre-built selectors for common site types

#### Common Site Types
```toml
# template/fablab.toml
# Common FabLab selectors (works for many)
[sites.fields.priority]
title = "h1"              # Most fablabs use h1
location = ".location"    # Common class name
contact = "a[href*='mailto']"
hours = ".hours"

# template/makerspace.toml
# Common Makerspace selectors
[sites.fields.priority]
title = ".facility-name"
location = ".address"
equipment = ".equipment-list"

# template/blog.toml
# Common blog selectors
[sites.fields.priority]
title = "h1"
author = ".author"
publish_date = ".date"
content = "article"
```

#### Tools Needed
```python
# New tool: config_templates.py
class ConfigTemplate:
    def get_template(site_type):
        """Get pre-built selectors for type"""

    def generate_config(url, site_type):
        """Generate config from template"""

    def refine_template(site_type, url, improvements):
        """Update template based on learnings"""
```

**Learning Loop**: Every time we refine a config that works well, we share back to template for next site of same type.

### Phase 2.3: Periodic Monitoring & Scheduling

**Goal**: Automatically scrape sites on schedule

#### 2.3.1: Scheduler
```python
# New tool: scheduler.py
class ScrapeScheduler:
    def schedule_site(url, frequency):
        """
        frequency: 'daily', 'weekly', 'monthly', or cron expression
        """
        # Save schedule
        # Create cron job or use APScheduler

    def run_all_scheduled():
        """Run all due scrapes"""

    def get_schedule():
        """List all scheduled sites"""
```

#### 2.3.2: Cron Jobs or Background Task Queue
```bash
# Option A: Simple cron
0 9 * * * /home/nicolas/github/scrape0/scripts/run_scheduled_scrapes.sh

# Option B: APScheduler (Python)
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(scrape_all_sites, 'cron', hour=9)
scheduler.start()

# Option C: Celery (advanced)
# Distributed task queue
```

#### 2.3.3: Results Storage
```
output/
├── 2026-01-04/
│   ├── openfab.be.toml
│   ├── example.com.toml
│   └── oxylabs.io.toml
├── 2026-01-05/
│   ├── openfab.be.toml
│   ├── example.com.toml
│   └── oxylabs.io.toml
└── archive.db (SQLite for analysis)
```

### Phase 2.4: Results Aggregation & Analytics

**Goal**: Understand what changed and trends over time

#### 2.4.1: Comparison Engine
```python
# New tool: comparison.py
class ResultComparison:
    def compare_runs(url, date1, date2):
        """What changed between two scrapes?"""
        # Extract same fields
        # Show diffs

    def detect_changes(url, results):
        """Flag what's new/different"""
        # Price changes
        # New equipment
        # Hours changes

    def generate_diff_report(url, old_toml, new_toml):
        """Detailed change report"""
```

#### 2.4.2: Analytics Dashboard (Phase 2.5+)
```
Dashboard would show:
- Sites monitored
- Last scrape time
- Success rate
- Changes detected
- Extraction accuracy
- Selector reliability
```

### Phase 2.5: Configuration Quality & Validation

**Goal**: Know when selectors break or need updating

#### 2.5.1: Validation Checks
```python
# New tool: validators.py
class ConfigValidator:
    def validate_config(url, config):
        """Check if config works"""
        # Run scrape
        # Check success rate
        # Flag broken selectors

    def quality_score(config):
        """Rate config quality (0-100)"""
        # Success rate
        # Fields extracted
        # Error rate

    def suggest_improvements(config, results):
        """Suggest better selectors based on results"""
```

#### 2.5.2: Selector Reliability Tracking
```toml
# In each config, track selector health
[sites.fields.priority]
title = "h1"  # High confidence (99% success)
location = ".location"  # Medium (75% success)
contact = "a[href*='mailto']"  # Low (40% - might need fixing)

[selector_health]
title = 0.99
location = 0.75
contact = 0.40
```

---

## Phase 2 Implementation Plan

### Sprint 1: Core Onboarding (1-2 weeks)
```
1. SiteRegistry class
   - register_site()
   - list_sites()
   - get_site_config()

2. Auto-config generation
   - config_templates.py
   - Generic selectors for common types
   - Test with new sites

3. Tests
   - Unit tests for registry
   - Integration tests with real sites
```

### Sprint 2: Scheduling & Results (1-2 weeks)
```
1. ScrapeScheduler class
   - schedule_site()
   - run_all_scheduled()

2. Results storage
   - Organize by date
   - Archive old results
   - DB for analysis

3. Comparison engine
   - Detect changes
   - Generate reports

4. Tests
   - Scheduler tests
   - Storage tests
```

### Sprint 3: Quality & Analytics (1-2 weeks)
```
1. ConfigValidator
   - Validate configs
   - Quality scoring
   - Suggest improvements

2. Dashboard (optional)
   - Simple web UI
   - Show metrics
   - Monitor sites

3. Tests
   - Validation tests
   - Analytics tests
```

---

## File Structure After Phase 2

```
scraper/                           # Core module (existing)
├── api.py
├── models.py
├── ... (existing files)

scraper_admin/                     # NEW: Admin/management tools
├── __init__.py
├── site_registry.py              # Site management
├── config_templates.py           # Config generation
├── scheduler.py                  # Periodic runs
├── comparison.py                 # Change detection
├── validators.py                 # Quality checking
└── __init__.py

scripts/                           # NEW: Automation scripts
├── run_scheduled_scrapes.sh      # Cron-friendly script
├── onboard_site.py               # CLI for adding sites
├── validate_configs.py           # Check all configs
└── generate_analytics.py         # Create reports

data/                              # NEW: Storage
├── sites.json                    # Site registry
├── schedules.json                # Scraping schedules
├── archive.db                    # Historical data
└── templates/                    # Config templates
    ├── fablab.toml
    ├── makerspace.toml
    └── blog.toml

tests/
├── test_phase2_registry.py       # Registry tests
├── test_phase2_scheduler.py      # Scheduler tests
└── test_phase2_analytics.py      # Analytics tests
```

---

## Example: Phase 2 Usage

### Adding a New Site (Complete Workflow)

```bash
# 1. Start onboarding
python scripts/onboard_site.py https://new-fablab.com

# Interactive:
# What type? (fablab, makerspace, hackerspace) → fablab
# Scrape frequency? (daily, weekly, monthly) → weekly
# Auto-extracting with template...
# ✓ Config created: config/new-fablab.com.toml
# ✓ Running test scrape...
# Results: 5/8 fields extracted
# What needs improvement? (optional)

# 2. Test the config
./run.sh https://new-fablab.com ./config/new-fablab.com.toml

# 3. Refine if needed (use browser DevTools)
# (edit config/new-fablab.com.toml with better selectors)

# 4. Validate config quality
python scripts/validate_configs.py

# 5. Schedule for regular scraping
python scripts/onboard_site.py https://new-fablab.com --schedule weekly

# 6. Future runs happen automatically
# → Cron job runs daily
# → Scrapes all weekly sites
# → Stores results by date
# → Detects changes automatically

# 7. View analytics
python scripts/generate_analytics.py
# ✓ 12 sites monitored
# ✓ 324 successful scrapes
# ✓ 98% success rate
# ✓ 15 changes detected this week
```

### Periodic Monitoring (Automated)

```bash
# Every day at 9 AM:
$ /home/nicolas/github/scrape0/scripts/run_scheduled_scrapes.sh

# Process:
# 1. Load all scheduled sites
# 2. Check which are due today
# 3. Run scrapers
# 4. Store results
# 5. Detect changes
# 6. Send alerts if configured
# 7. Update analytics
```

---

## Phase 2 vs Phase 3 vs Future

### Phase 2: Onboarding & Monitoring (NEXT)
- Site registration
- Configuration templates
- Periodic scheduling
- Results comparison
- Quality validation

### Phase 3: Analytics Dashboard (Later)
- Web UI to view metrics
- Charts and graphs
- Trend analysis
- Export capabilities

### Phase 4: Advanced Features (Future)
- ML-based selector improvement
- Automatic site structure detection
- Smart retry strategies
- Market intelligence features
- Integration with external APIs

---

## Decision Points for Phase 2

### Should We Build Phase 2?

**YES** because:
- ✓ Phase 1 core scraping is complete and working
- ✓ Phase 2 enables actual production use
- ✓ Without scheduling, it's just a manual tool
- ✓ Without registry, we can't track multiple sites
- ✓ Without analytics, we can't see what changed
- ✓ Without templates, every site is manual work

**What Phase 2 Does**:
- Turns "manual scraper" → "automated monitoring system"
- Enables periodic data collection
- Tracks changes over time
- Provides site management interface
- Makes it production-ready

### Implementation Approach

**Option A: Full Phase 2 (Complete)**
- All 5 subsystems
- Estimated: 3-4 weeks
- Result: Production-ready system

**Option B: Phase 2.1 + 2.3 Only (Minimum Viable)**
- Site registry + scheduling only
- Estimated: 1-2 weeks
- Result: Can add sites and schedule runs
- Add analytics later

**Option C: Phase 2.1 Only (Lightest)**
- Just site registry
- Estimated: 1 week
- Result: Can manage site configs
- Scheduling can be done manually

---

## Recommendation

**START WITH PHASE 2.1 + 2.3** (Option B):

### Phase 2.1: Site Registry
- Register sites
- Auto-generate configs from templates
- Manage site collection

### Phase 2.3: Scheduling
- Run sites on schedule
- Store results by date
- Detect basic changes

**Then Later Add**:
- 2.2: Better templates
- 2.4: Advanced analytics
- 2.5: Quality validation

This gives you a **working production system in 2 weeks** instead of 4 weeks, and you can enhance it with analytics later.

---

## Your Immediate Decision

Before I start Phase 2, please clarify:

1. **Which approach?**
   - Option A: Full Phase 2 (all features)
   - Option B: Phase 2.1 + 2.3 (registry + scheduling)
   - Option C: Phase 2.1 only (registry only)

2. **Scheduling preference?**
   - Cron jobs (simple, Linux-native)
   - APScheduler (Python, cross-platform)
   - Celery (advanced, distributed)

3. **Storage preference?**
   - TOML files by date (simple)
   - SQLite database (queryable)
   - Both (TOML + DB)

4. **Timeline?**
   - Start immediately
   - Plan first, start later

---

## Summary

✓ **Phase 1 (Current)**: Scraping engine - COMPLETE and working
→ **Phase 2 (Next)**: Onboarding & monitoring - Ready to plan
→ Phase 3: Analytics dashboard - Can come later

You've identified the exact gap: we need a systematic way to onboard new sites and keep monitoring them periodically. Phase 2 is the logical next step.

**Should I start Phase 2 planning?** Which approach appeals to you?
