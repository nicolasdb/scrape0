# Task Breakdown: Phase 2 - Onboarding & Periodic Monitoring

## Overview

Phase 2 implements site registration, periodic scheduling, and results aggregation for the scraping system. Using minimal viable approach: Site Registry (2.1) + Scheduler (2.3) with SQLite + TOML storage, cron jobs.

**Total Tasks**: 28 subtasks across 3 sprints
**Approach**: Minimal viable (Phase 2.1 + 2.3 only)
**Storage**: Both SQLite (queryable) and TOML (human-readable)
**Scheduling**: Cron jobs (native Linux, simple)

---

## Task List

### Sprint 1: Site Registry System (1-2 weeks)

#### Task Group 1.1: Site Registry Data Model
**Dependencies**: None
**Duration**: 3-4 hours

- [x] 1.1.1 Create site registry data models
  - Create `SiteRegistry` dataclass with: id, url, site_type, description, frequency, active, created_date, last_scraped
  - Create `SiteConfig` linking to config file path
  - Create registry JSON schema
  - Add validation for required fields

- [x] 1.1.2 Implement file-based registry storage
  - Create `scraper_admin/registry_manager.py`
  - Implement `save_registry()` - write to `data/sites.json`
  - Implement `load_registry()` - read from `data/sites.json`
  - Add version field for future migrations
  - Handle file locking for concurrent access

- [x] 1.1.3 Build registry database (SQLite)
  - Create SQLite schema in `data/archive.db`
  - Table: sites (id, url, site_type, description, frequency, active, created_date, last_scraped)
  - Add indexes on: url, site_type, frequency
  - Create migration system for schema updates

- [x] 1.1.4 Implement registry CRUD operations
  - `register_site(url, site_type, description, frequency)` - add new site
  - `list_sites(filter_by_type=None, filter_active=True)` - list all sites
  - `get_site(url)` - get single site
  - `update_site(url, updates)` - modify existing
  - `deactivate_site(url)` - soft delete
  - Sync between JSON and SQLite

**Acceptance Criteria**:
- Sites can be registered and stored
- Registry loads correctly on restart
- CRUD operations work
- JSON and SQLite stay synchronized
- 10+ sites can be registered

---

#### Task Group 1.2: Configuration Template System
**Dependencies**: Task Group 1.1
**Duration**: 3-4 hours

- [x] 1.2.1 Create configuration templates
  - Create `config/templates/` directory
  - Create `template_fablab.toml` with FabLab selectors
  - Create `template_makerspace.toml` with Makerspace selectors
  - Create `template_blog.toml` with Blog selectors
  - Document selector choices in comments

- [x] 1.2.2 Implement template loader
  - Create `scraper_admin/template_loader.py`
  - `get_template(site_type)` - load template by type
  - `list_available_templates()` - show all templates
  - Handle missing templates gracefully

- [x] 1.2.3 Build config generator
  - `generate_config(url, site_type, template=None)`
  - Extract domain from URL
  - Create config/domain.toml from template
  - Add site to sites list
  - Fill in URL pattern and site type

- [x] 1.2.4 Implement config validation
  - Validate generated config is valid TOML
  - Check all required fields present
  - Test config with dry run
  - Report generation success/failure

**Acceptance Criteria**:
- Templates available for 3+ site types
- Configs can be auto-generated
- Generated configs are valid TOML
- Can be tested immediately

---

#### Task Group 1.3: Site Onboarding CLI
**Dependencies**: Task Groups 1.1, 1.2
**Duration**: 4-5 hours

- [x] 1.3.1 Build interactive onboarding script
  - Create `scripts/onboard_site.py`
  - Prompt for: URL, site type (select from list), scrape frequency
  - Show generated config
  - Ask for approval before saving
  - Provide option to refine selectors

- [x] 1.3.2 Implement config testing in onboarding
  - After generating config, run test scrape
  - Show extraction preview
  - Report: X/Y fields extracted
  - Ask: "Does this look good?"

- [x] 1.3.3 Add manual refinement option
  - If user says "no" to extraction preview
  - Show browser DevTools instructions
  - Offer to edit config manually
  - Re-test after edits

- [x] 1.3.4 Save and register site
  - Save final config to `config/domain.toml`
  - Register in site registry
  - Ask about scheduling frequency
  - Create schedule (see Sprint 2)

**Acceptance Criteria**:
- Interactive onboarding works
- Sites can be registered via CLI
- Configs are generated and tested
- User can refine if needed

---

### Sprint 2: Scheduling & Periodic Runs (1-2 weeks)

#### Task Group 2.1: Scheduler System
**Dependencies**: Task Group 1.1
**Duration**: 3-4 hours

- [x] 2.1.1 Create schedule data model
  - Create `Schedule` dataclass: site_id, frequency (daily/weekly/monthly), time_of_day, next_run
  - Create `ScheduleManager` class
  - Implement `save_schedule()` - write to `data/schedules.json`
  - Implement `load_schedule()` - read from `data/schedules.json`

- [x] 2.1.2 Implement schedule calculation
  - `get_next_run(frequency)` - calculate next execution time
  - `is_due_for_run(site_id)` - check if site should run now
  - `get_all_due_sites()` - list all sites due to run today
  - Handle timezone considerations

- [x] 2.1.3 Build schedule management
  - `schedule_site(url, frequency)` - add site to schedule
  - `unschedule_site(url)` - remove from schedule
  - `list_schedule()` - show all scheduled sites
  - `get_next_runs(days=7)` - preview upcoming runs

- [x] 2.1.4 Create cron job runner script
  - Create `scripts/run_scheduled_scrapes.sh`
  - Check which sites are due
  - Run scraper for each due site
  - Log results
  - Update next_run time

**Acceptance Criteria**:
- Sites can be scheduled
- Schedule persists across restarts
- Cron runner identifies due sites
- Can schedule for daily/weekly/monthly

---

#### Task Group 2.2: Results Storage by Date
**Dependencies**: Task Group 1.1, 2.1
**Duration**: 3-4 hours

- [x] 2.2.1 Organize TOML output by date
  - Modify output path to: `output/YYYY-MM-DD/domain_timestamp.toml`
  - Create directory if not exists
  - Use domain name (first 10 chars) + timestamp
  - No overwrites (each run unique file)

- [x] 2.2.2 Implement results archiving
  - Create `scraper_admin/result_archiver.py`
  - `archive_result(url, toml_file, metadata)` - save to database
  - Extract metadata from TOML:
    - success (true/false)
    - extraction_timestamp
    - extraction_duration_seconds
    - site_type
    - fields_status (extracted/failed/not_found counts)
  - Insert metadata into SQLite

- [x] 2.2.3 Build results database schema
  - Table: results (id, url, run_date, success, duration, site_type, extracted_count, failed_count, not_found_count)
  - Table: result_fields (result_id, field_name, status, value)
  - Add indexes on: url, run_date, site_type, success

- [x] 2.2.4 Create results query interface
  - `get_results_for_site(url, days=30)` - last 30 days
  - `get_results_by_date(date)` - all results for a date
  - `get_latest_result(url)` - most recent scrape
  - `get_success_rate(url, days=30)` - success %

**Acceptance Criteria**:
- TOML files organized by date
- No overwrites (unique filenames)
- Results metadata stored in SQLite
- Can query results by URL, date, type

---

#### Task Group 2.3: Change Detection Engine
**Dependencies**: Task Group 2.2
**Duration**: 3-4 hours

- [x] 2.3.1 Implement result comparison
  - Create `scraper_admin/change_detector.py`
  - `compare_runs(url, date1, date2)` - diff two dates
  - Extract fields from both TOML files
  - Show: added, removed, changed, unchanged

- [x] 2.3.2 Detect specific changes
  - New fields appearing (extraction improved)
  - Fields disappearing (selector broke)
  - Content changes (price, status, hours)
  - Success rate changes (selector reliability)

- [x] 2.3.3 Generate change reports
  - `generate_diff_report(url, old_toml, new_toml)`
  - Formatted output showing what changed
  - Flag important changes (extraction failures)
  - Suggest actions (update selectors, etc)

- [x] 2.3.4 Create change alerts (optional)
  - Track important fields that change
  - Flag when selector success rate drops
  - Notify if site goes from success → failure
  - Log alerts to SQLite for later review

**Acceptance Criteria**:
- Can compare two scrape results
- Shows what changed between runs
- Detects when selectors break
- Generates readable diff reports

---

### Sprint 3: Testing & Integration (1-2 weeks)

#### Task Group 3.1: Unit Tests for Phase 2
**Dependencies**: All previous tasks
**Duration**: 3-4 hours

- [ ] 3.1.1 Test registry operations
  - Test register_site()
  - Test list_sites()
  - Test update_site()
  - Test JSON and SQLite sync
  - 8-10 tests total

- [ ] 3.1.2 Test template system
  - Test load_template()
  - Test generate_config()
  - Test validation of generated configs
  - 5-6 tests total

- [ ] 3.1.3 Test scheduler
  - Test schedule_site()
  - Test is_due_for_run()
  - Test next_run calculation
  - Test cron runner logic
  - 6-8 tests total

- [ ] 3.1.4 Test change detection
  - Test compare_runs()
  - Test detect changes
  - Test report generation
  - 4-5 tests total

**Acceptance Criteria**:
- 25+ new tests for Phase 2
- All registry tests pass
- Scheduler tests pass
- Change detection tests pass

---

#### Task Group 3.2: Integration Tests
**Dependencies**: Task Group 3.1
**Duration**: 2-3 hours

- [ ] 3.2.1 End-to-end registration flow
  - Register a new site via CLI
  - Generate config
  - Test config works
  - Verify in registry
  - Complete scenario test

- [ ] 3.2.2 End-to-end schedule flow
  - Schedule a site
  - Run scheduled scrape
  - Verify results saved by date
  - Check metadata in SQLite
  - Complete scenario test

- [ ] 3.2.3 End-to-end change detection
  - Scrape site twice
  - Detect differences
  - Generate report
  - Complete scenario test

**Acceptance Criteria**:
- Full workflows tested end-to-end
- No integration issues
- All components work together

---

#### Task Group 3.3: Documentation & Deployment
**Dependencies**: Task Groups 3.1, 3.2
**Duration**: 2-3 hours

- [ ] 3.3.1 Document Phase 2 system
  - Create `PHASE_2_IMPLEMENTATION.md`
  - Document each module
  - Show API/function signatures
  - Provide usage examples

- [ ] 3.3.2 Create CLI usage guide
  - Document `onboard_site.py` usage
  - Document `run_scheduled_scrapes.sh` usage
  - Show example workflows
  - Troubleshooting tips

- [ ] 3.3.3 Set up cron job
  - Create cron entry
  - Document cron setup
  - Show log location
  - Test cron execution

- [ ] 3.3.4 Create operations guide
  - How to check registry
  - How to view results
  - How to detect changes
  - How to troubleshoot issues

**Acceptance Criteria**:
- Documentation complete
- Cron job working
- Users can follow guide to set up

---

## Implementation Plan

### Pre-Sprint: Setup

- [ ] Create directory structure:
  ```
  scraper_admin/
  ├── __init__.py
  ├── registry_manager.py
  ├── template_loader.py
  ├── config_generator.py
  ├── schedule_manager.py
  ├── result_archiver.py
  ├── change_detector.py
  └── __init__.py

  scripts/
  ├── onboard_site.py
  └── run_scheduled_scrapes.sh

  data/
  ├── sites.json (registry)
  ├── schedules.json
  └── archive.db (SQLite)

  config/templates/
  ├── template_fablab.toml
  ├── template_makerspace.toml
  └── template_blog.toml

  tests/
  └── test_phase2_*.py (5-6 test files)
  ```

- [ ] Update requirements.txt with any new dependencies

### Sprint 1 Workflow

1. Build data models (1.1)
2. Build templates (1.2)
3. Build CLI (1.3)
4. Test each component
5. Manual integration testing

### Sprint 2 Workflow

1. Build scheduler (2.1)
2. Build storage layer (2.2)
3. Build change detection (2.3)
4. Test each component
5. Verify cron works

### Sprint 3 Workflow

1. Write unit tests
2. Write integration tests
3. Write documentation
4. Set up cron job
5. Final validation

---

## File Structure After Phase 2

```
scrape0/
├── scraper/                      # Core module (unchanged)
│   └── ... (existing files)
│
├── scraper_admin/                # NEW: Phase 2 admin tools
│   ├── __init__.py
│   ├── registry_manager.py       # Site registry
│   ├── template_loader.py        # Config templates
│   ├── config_generator.py       # Generate configs
│   ├── schedule_manager.py       # Manage schedules
│   ├── result_archiver.py        # Store results
│   └── change_detector.py        # Detect changes
│
├── scripts/                       # NEW: Automation scripts
│   ├── onboard_site.py           # Interactive onboarding
│   └── run_scheduled_scrapes.sh  # Cron runner
│
├── data/                          # NEW: Data storage
│   ├── sites.json               # Site registry
│   ├── schedules.json           # Schedule info
│   └── archive.db               # SQLite database
│
├── config/
│   ├── example.toml             # (existing)
│   ├── templates/               # NEW: Config templates
│   │   ├── template_fablab.toml
│   │   ├── template_makerspace.toml
│   │   └── template_blog.toml
│   └── ... (domain-specific configs)
│
├── output/
│   ├── 2026-01-04/              # NEW: Dated directories
│   │   ├── oxylabs_20260104_123456.toml
│   │   └── example_20260104_123500.toml
│   ├── 2026-01-05/
│   └── ...
│
└── tests/
    ├── test_phase2_registry.py        # NEW
    ├── test_phase2_scheduler.py       # NEW
    ├── test_phase2_storage.py         # NEW
    ├── test_phase2_detection.py       # NEW
    ├── test_phase2_integration.py     # NEW
    └── ... (existing tests)
```

---

## Example Usage After Phase 2

### Register a New Site

```bash
python scripts/onboard_site.py

# Interactive prompts:
# URL: https://new-fablab.com
# Site type: [1] fablab [2] makerspace [3] blog → 1
# Scrape frequency: [1] daily [2] weekly [3] monthly → 2
#
# ✓ Generated config
# ✓ Testing config...
# ✓ 7/10 fields extracted
# ✓ Ready? (y/n) → y
# ✓ Site registered!
# ✓ Scheduled for weekly scraping
```

### Check Registry

```bash
python scripts/list_sites.py

# Output:
# Registered Sites:
# 1. openfab.be (fablab) - Active - Weekly
# 2. example.com (blog) - Active - Daily
# 3. new-fablab.com (fablab) - Active - Weekly
```

### View Results

```bash
python scripts/view_results.py new-fablab.com

# Output:
# Latest results for new-fablab.com:
# 2026-01-05: ✓ 7/10 fields (2.3s)
# 2026-01-04: ✓ 7/10 fields (2.1s)
# 2026-01-03: ✓ 5/10 fields (2.2s) - 2 selectors failed
```

### Detect Changes

```bash
python scripts/detect_changes.py new-fablab.com

# Output:
# Changes between 2026-01-04 and 2026-01-05:
# NEW: hours_monday
# CHANGED: contact (email address updated)
# FAILED: equipment (selector broken - fix needed)
```

### Automatic Cron Runs

```bash
# Cron job: every day at 9 AM
0 9 * * * /home/nicolas/github/scrape0/scripts/run_scheduled_scrapes.sh

# Process (automated):
# ✓ Checking due sites...
# ✓ Running: openfab.be (daily)
# ✓ Running: example.com (daily)
# ✓ Running: new-fablab.com (weekly - due today)
# ✓ 3 sites completed
# ✓ Results saved to output/2026-01-05/
# ✓ Checking for changes...
# ✓ 1 change detected (see results)
```

---

## Acceptance Criteria for Phase 2 Completion

### Functional Completeness
- [ ] Sites can be registered via CLI
- [ ] Configs auto-generated from templates
- [ ] Sites can be scheduled for regular scraping
- [ ] Cron job runs at scheduled times
- [ ] Results stored by date (no overwrites)
- [ ] Results metadata in SQLite
- [ ] Changes detected between runs
- [ ] Change reports generated

### Technical Quality
- [ ] 25+ tests for Phase 2 components
- [ ] All tests pass
- [ ] Code formatted (Black)
- [ ] Type checking passes (MyPy)
- [ ] No dead code

### Documentation
- [ ] API documented
- [ ] CLI guide provided
- [ ] Example workflows shown
- [ ] Troubleshooting guide included
- [ ] Operations guide provided

### Production Readiness
- [ ] Cron job installed and working
- [ ] Data persists across restarts
- [ ] Error handling robust
- [ ] Logs helpful for debugging
- [ ] System can handle 10+ sites

---

## References

- **Phase 1 Spec**: `/home/nicolas/github/scrape0/agent-os/specs/2026-01-04-core-scraping-modular-architecture/`
- **Phase 2 Roadmap**: `/home/nicolas/github/scrape0/PHASE_2_ROADMAP.md`
- **Current Output**: `./output/<YYYY-MM-DD>/<domain>_<timestamp>.toml`
- **Site Registry**: `./data/sites.json`
- **Results DB**: `./data/archive.db` (SQLite)
