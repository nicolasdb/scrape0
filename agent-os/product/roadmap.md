# Product Roadmap

## Phase 1: Core Scraping & Profiling

1. [ ] **Scrapling Integration & Configuration** — Integrate Scrapling as the primary scraping engine and build a configuration system to define target websites, extraction patterns, and retry logic. `M`

2. [ ] **Priority Data Extraction Pipeline** — Implement automated extraction of core fields (name, location, expertise, URL, contact) from target fablabs/makerspaces with error handling and field validation. `M`

3. [ ] **TOML Profile Output** — Generate structured TOML files for each scraped facility containing priority data, timestamps, and metadata about the scraping process. `S`

4. [ ] **Basic Scheduling & Orchestration** — Implement scheduled scraping runs (daily/weekly/monthly) to keep profiles current without manual intervention. `M`

## Phase 2: Reliability Measurement & Testing

5. [ ] **Success Rate Tracking** — Add comprehensive metrics collection to track success/failure rates for each scraping target and method, enabling identification of unreliable scraping patterns. `M`

6. [ ] **Failure Detection & Logging** — Implement detection of scraping failures (timeout, parse errors, invalid output, HTTP errors) with structured logging of all failure events. `S`

7. [ ] **Multi-Method Testing Framework** — Allow definition and comparison of multiple scraping approaches per target, with metrics tracking to identify optimal extraction paths and method reliability. `L`

8. [ ] **Reliability Dashboard** — Build HTML interface displaying success rates, failure trends, method performance comparisons, and recommendations for which scraping approaches work best. `M`

## Phase 3: Data Enrichment & Preservation

9. [ ] **Comprehensive Data Capture** — Extend beyond priority fields to automatically collect all available information from facility websites (additional contact methods, services, hours, photos, descriptions). `M`

10. [ ] **Full Profile Storage & Versioning** — Build storage system for complete facility profiles with version history, enabling tracking of changes over time and preservation of rich facility data. `M`

11. [ ] **Data Validation & Quality Metrics** — Implement validation rules for extracted data (email format, URL validity, location parsing) and quality scores to indicate data confidence. `M`

## Phase 4: Search & Discovery

12. [ ] **Search Interface** — Build minimal HTML-based search interface allowing users to query profiles by name, location, expertise, and other key fields. `M`

13. [ ] **Facility Discovery Dashboard** — Create web interface showing community statistics (total facilities tracked, recent updates, and trending expertise areas). `M`

> Notes
> - Phase 1 establishes core MVP: automated scraping with priority data output
> - Phase 2 is the core differentiator: reliability measurement and testing framework
> - Phase 3 enables rich data preservation for future analysis
> - Phase 4 implements user-facing search and discovery
> - Each item represents an end-to-end, testable feature with frontend + backend components
> - Effort estimates assume single-developer workflow with vertical slice implementation
> - Phases can overlap; Phase 2 can begin once Phase 1 core is stable
> - Semantic search (vector embedding) is out of scope; focus on reliability measurement as primary value add
