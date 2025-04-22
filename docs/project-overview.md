# Wedding Venue Data Pipeline – Project Overview

This project is a modular, automated data pipeline built to collect, process, enrich, and analyze wedding venue listings from publicly available online directories. It showcases best practices in data engineering, web scraping, scheduling, logging, and AI-assisted data exploration.

---

## Contents

- [Overview](#overview)
- [Methodology](#methodology)
- [Sprint Summary](#sprint-summary)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Planned Enhancements](#planned-enhancements)
- [Author](#author)

---

## Overview

The project consists of multiple components that work together to:

- Scrape structured venue listing data across regions
- Clean and normalize messy data fields
- Enrich listings with derived attributes for better filtering and ranking
- Schedule recurring updates via GitHub Actions
- Provide interactive dashboards powered by both static visualizations and AI language models

This pipeline is designed to be extensible, version-controlled, and production-aware.

---

## Methodology

This project follows a sprint-based workflow, loosely modeled after Agile principles and the Software Development Life Cycle (SDLC):

| Phase | Description |
|-------|-------------|
| Requirements | Identified real-world use case: multi-region venue aggregation |
| Planning     | Divided the project into modular sprints |
| Development  | Implemented scraping, cleaning, enrichment, and visualization logic |
| Testing      | Manual runs with data validation, pagination, and logging checks |
| Deployment   | Automated execution via GitHub Actions |
| Documentation| Maintained in Markdown for clarity and reuse |

---

## Sprint Summary

### ✅ Sprint 1: Core MVP (Automated ETL Pipeline)

**Branch:** `main`

**Features:**

- Scrape venue data from one location (London) using Selenium
- Parse ratings, review counts, prices, and capacity data
- Clean and standardize the dataset using Pandas
- Log all activity (row counts, timestamps, and errors)
- Schedule via GitHub Actions (runs daily at 04:30 UTC)
- Upload processed CSV and logs as workflow artifacts
- Provide basic data visualizations using `analyzer.py`
- Build an AI-powered Streamlit dashboard for querying with natural language

---

### 🚧 Sprint 2: Multi-Region Support & Data Enrichment

**Branch:** `enrichment-sprint`

**Multi-Region:**

- Load regional URLs from `regions.json`
- Scrape listings for multiple cities and combine into one dataset
- Save timestamped JSON output and centralized logs

**Enrichment Fields:**

- `price_bucket` → low / mid / premium (based on parsed price)
- `capacity_type` → intimate / medium / large (based on guest size)
- `score_10` → composite score using rating × review count

---

### 🧪 Sprint 3: Sentiment Analysis (Planned)

**Branch:** `review-sentiment` *(to be created)*

**Planned Capabilities:**

- Scrape venue review pages and extract user feedback
- Perform sentiment analysis using VADER, TextBlob, or HuggingFace models
- Enrich dataset with average sentiment score and top keywords
- Generate visual insights like most-loved venues and keyword clouds

---

## Tech Stack

| Component       | Technology            |
|----------------|------------------------|
| Scraping        | Python, Selenium       |
| Data Cleaning   | Pandas                 |
| Scheduling      | GitHub Actions (CRON)  |
| Visualization   | Matplotlib, Seaborn    |
| AI Dashboards   | Streamlit + LLM (Together AI) |
| Storage         | CSV, JSON              |
| Version Control | Git + GitHub           |

---

## Folder Structure

```bash
WeddingVenues-data-pipeline/
├── main/
│   ├── scraper.py
│   ├── cleaner.py
│   ├── analyzer.py
│   ├── ai-data-viz.py
│   ├── scraper_region.py
│   ├── collect_regions.py
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── logs/
│   └── plots/
├── regions.json
├── .github/workflows/scrape-clean.yml
├── README.md
└── docs/
    └── project-overview.md

```

⸻

**Planned Enhancements**
- Add Google Big Query support
- Integrate a retry mechanism for failed scrapes
- Add Docker container for reproducible deployments
- Build frontend for searchable/filterable listings
- Send email or Slack alerts on new listings

⸻

Author

Developed and maintained by @vishnupriyan123

Assisted by Cord Lord! custom GPT prompt engineered by @vishnupriyan123
https://chatgpt.com/g/g-680143e6e87c81919c7db6ede04df663-code-lord

This project demonstrates modern data pipeline engineering with modular architecture, automation, and exploratory analysis capabilities.