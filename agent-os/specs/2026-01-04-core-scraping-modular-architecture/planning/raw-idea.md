# Raw Idea: Core Scraping with Modular Architecture

**Feature**: Core Scraping with Modular Architecture

**Key Requirements**:
- Build with IPO (Input-Process-Output) model for clarity and modularity
- Design architecture to allow swapping scraping libraries/methods (Scrapling is primary choice but may need alternatives)
- Ensure reliability testing capabilities are built-in
- Support extracting two types of data: priority fields (name, location, expertise, URL, contact) and extra metadata
- Output data in TOML format
- Enable us to refine a schema to format the extracted data like a preference file
- Pipeline flow: URL > extract raw > filter/organize > output TOML

**Context**:
- Part of Scrape0 project for profiling fablabs and makerspaces
- Currently using Scrapling (https://github.com/D4Vinci/Scrapling) but needs flexible swapping capability
- Single-user tool (creator only)
- Data is destined for future vector embedding (out of current scope)
