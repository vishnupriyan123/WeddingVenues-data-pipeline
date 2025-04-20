# 🏗️ WeddingVenues Data Pipeline

A complete automated data pipeline to extract, clean, enrich, visualize, and version-control wedding venue data.

---

## 🔧 Features Implemented

### 1️⃣ Data Pipeline Engineering
- Automated scraper using **Selenium** (Hitched.co.uk – London venues)
- Handles pagination and dynamic content with browser automation
- Runs daily using `cron` or **GitHub Actions**
- Logs scraping success and saves daily raw + cleaned data locally (or via GitHub if configured)

### 2️⃣ Content Enrichment & Optimization
- Extracts: `name`, `location`, `rating`, `price`, `capacity`, `reviews`
- Standardizes price format and parses capacity intelligently
- Cleans missing or broken data, ensures consistency

### 3️⃣ Data Cleaning & Quality Assurance
- Uses **Pandas** to clean and transform data
- Handles nulls, inconsistent entries, and broken URLs
- Visual heatmaps for detecting missing data

### 4️⃣ Visualization & Analysis
- `scripts/analyzer.py`: Generates static Matplotlib charts
- `scripts/ai-data-viz.py`: Interactive **Streamlit** dashboard with **AI-powered chart generation**
- Natural language querying of your dataset
- Chart download support in PNG format

### 5️⃣ Version Control & Logging
- `.gitignore` excludes volatile outputs (logs, raw data, environments)
- Logs each run to `logs/`
- Snapshots daily data to timestamped files
- Modular scripts inside `/scripts/`

---

## 📁 Project Structure

```bash
WeddingVenues-data-pipeline/
├── data/
│   ├── raw/               # Scraped JSON output (daily + latest)
│   ├── processed/         # Cleaned CSV files (daily + latest)
│   └── plots/             # Visualizations (saved PNGs)
├── logs/                  # Scraper and cleaner logs
├── scripts/
│   ├── scraper.py         # Web scraper
│   ├── cleaner.py         # Cleans and enriches raw data
│   ├── analyzer.py        # Static chart generator
│   └── ai-data-viz.py     # AI-powered Streamlit dashboard
├── .github/workflows/
│   └── pipeline.yml       # GitHub Actions workflow (daily automation)
├── .gitignore
├── README.md
└── requirements.txt


🚀 How to Run

1. Clone and Install

git clone https://github.com/vishnupriyan123/WeddingVenues-data-pipeline.git
cd WeddingVenues-data-pipeline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

2. Scrape and Clean Data

python scripts/scraper.py
python scripts/cleaner.py

3. Analyze or Visualize

📊 Static Charts (matplotlib/seaborn)

python scripts/analyzer.py

🤖 AI-Powered Visualization (Streamlit App)

This project includes an AI-powered Streamlit application (scripts/ai-data-viz.py) that allows you to analyze and visualize your data through natural language.

🔐 Requirements
	•	Get a Together AI API Key
	•	Get an E2B API Key

▶️ Run the app:

streamlit run scripts/ai-data-viz.py

💡 AI Features:
	•	Ask questions about your dataset in plain English
	•	AI interprets your query and generates visualizations
	•	Automatic chart type selection and styling
	•	Supports multiple LLMs:
	•	Meta-Llama 3.1 405B
	•	DeepSeek V3
	•	Qwen 2.5 7B
	•	Meta-Llama 3.3 70B
	•	Download any chart as PNG with one click

⸻

🧠 Tech Stack
	•	Python 3.10
	•	Selenium (ChromeDriver)
	•	Pandas
	•	Matplotlib / Seaborn
	•	Streamlit
	•	Together AI + E2B (LLMs)
	•	GitHub Actions & CRON (Automation)


⸻

📌 Next Up
	•	✅ Database integration (PostgreSQL/SQLite)
	•	✅ Automated git commits
	•	✅ Multi-region support & localization
	•	✅ Dashboard for vendor profile completeness