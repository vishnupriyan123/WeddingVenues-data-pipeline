# 🏗️ Wedding Venues Data Pipeline

[![Status: In Progress](https://img.shields.io/badge/status-in--progress-yellow)]()
[![Built with Python](https://img.shields.io/badge/built%20with-python-blue)]()


A fully automated, cloud-based data platform for scraping, cleaning, enriching, and analyzing wedding venue data — powered by **PySpark**, **BigQuery**, **GCS**, **Streamlit**, and **LLMs** for intelligent insights.

---

## 🚀 Overview

### 💡 Key Highlights

- Scrapes venue listings daily from **Hitched.co.uk**
- Cleans and transforms data using **PySpark**
- Stores processed data in **Google Cloud Storage (GCS)** and **BigQuery** via **Cloud Data Fusion**
- Runs an **LLM-powered sentiment agent** to analyze venue reviews
- Offers a beautiful **Streamlit app** with:
  - Region & location-wise venue explorer
  - Integrated **Tableau dashboard**
  - **AI-based natural language visualizer** using **Together AI + E2B sandbox**

---


## 🧰 Features

### 🔁 1. Automated Scraping + Scheduling
- Selenium-powered scraper for venue data
- Runs daily at **4:30 AM UTC / 10:00 AM IST** via **GitHub Actions**
- Raw data pushed to **Google Cloud Storage**

### ⚙️ 2. Distributed Cleaning with PySpark
- Data transformation & validation using **PySpark**
- Handles missing fields, standardizes prices, capacity, and reviews
- Cleaned data pushed to **BigQuery** via **Cloud Data Fusion**

### 🧠 3. Sentiment Analysis with LLMs
- Aspect-based sentiment analysis using **Together AI**
- Highlights what users love or dislike about each venue (food, decor, staff, etc.)
- Results are shown per venue in the UI

### 🧑‍💻 4. Streamlit App
- Explore venues by region, location, and sentiment score
- Two main tabs:
  - **Data Explorer** – View listings, filters, sentiment results
  - **Insights** – Embedded Tableau dashboard + AI Chart Agent

### 🎨 5. AI-Powered Data Viz Agent
- Ask questions in plain English:
  - _“Which venue has the highest rating in London?”_
  - _“Show booking trends over time”_
- Visuals generated using **Together AI** LLMs + **E2B sandbox**
- Charts downloadable in PNG format

---

## 📁 Project Structure

```bash
WeddingVenues-data-pipeline/
├── main/
│   ├── data/
│   │   ├── raw/              # Scraped JSON
│   │   └── processed/        # Cleaned CSV
│   ├── logs/                 # Run logs (scraper/cleaner)
│   ├── plots/                # Static PNG charts
│   ├── venues_scraper.py     # Web scraper (Selenium)
│   ├── venues_cleaner.py     # Pandas cleaner
│   ├── analyzer.py           # Static chart generator
│   └── ai-data-viz.py        # AI-powered Streamlit UI
├── .github/workflows/
│   └── pipeline.yml          # GitHub Actions daily workflow
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ✨ AI Features

- Ask questions in plain English (e.g., _“What’s the average meal price by location?”_)
- AI suggests chart type, titles, and formatting automatically
- Multiple LLMs supported:
  - Meta-LLaMA 3.1 405B / 3.3 70B
  - DeepSeek V3
  - Qwen 2.5 7B
- Download any chart as a PNG in one click

---

## 🔁 GitHub Actions: Daily Automation

- Scheduled to run daily at **4:30 AM UTC / 10:00 AM IST**
- Executes:
  - `main/venues_scraper.py` → Scrapes latest venue listings
  - `main/venues_cleaner.py` → Cleans and enriches raw data
- Automatically uploads artifacts:
  - `hitched_venues.json`, `hitched_venues_YYYYMMDD.json`
  - `cleaned_venues.csv`, `cleaned_venues_YYYYMMDD.csv`
  - `scraper_log.txt`, `cleaner_log.txt`
- Commits latest `cleaned_venues.csv` to GitHub repo
  - Timestamped files are **excluded via `.gitignore`**

---

## 🛡️ GDPR & Legal Compliance

✅ This project is **GDPR-compliant**:
- Scrapes only **public business listings** (no personal or user-generated data)
- Does **not collect** cookies, session info, or user-identifiable metadata
- Logging and snapshots are stored only for internal use and testing

---

---

## ✨ Tech Stack

| Layer         | Tools Used                                                                 |
|---------------|----------------------------------------------------------------------------|
| ✂️ Scraping   | Selenium                                                   	     |
| 🧹 Cleaning   | Pandas, PySpark                                                   	     |
| 📊 Storage    | Google BigQuery, GCS                                                       |
| 🤖 AI         | Together AI (LLMs), E2B sandbox                                             |
| 💻 Frontend   | Streamlit, Tableau (embedded)                                              |
| 🕹️ Automation | GitHub Actions (CRON @ 10:00 AM IST)                                       |

---


## ✅ Roadmap & Next Steps

- [x] Identifying and Scraping datasets
- [x] Cleaning and modelling the data
- [x] Building a RDBMS
- [x] Daily automation & GCS pipeline
- [x] Streamlit + Tableau dashboard
- [x] LLM-based sentiment agent
- [ ] Time series bookings trend
- [ ] Price anomaly detector
- [ ] Region-based vendor scoring
- [ ] Deploy to GCP App Engine

---
