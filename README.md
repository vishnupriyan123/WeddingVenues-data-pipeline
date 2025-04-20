# 🏗️ WeddingVenues Data Pipeline

A complete automated data pipeline to extract, clean, enrich, visualize, and version-control wedding venue data

---

## 🔧 Features Implemented

### 1️⃣ Data Pipeline Engineering
- Automated scraper using **Selenium** (Hitched.co.uk, London venues)
- Handles pagination and dynamic content
- Scheduled to run daily using `cron`
- Logs scraping success and errors

### 2️⃣ Content Enrichment & Optimization
- Extracts fields: `name`, `location`, `rating`, `price`, `capacity`, `reviews`
- Parses and standardizes price formats and capacity ranges
- Outputs enriched JSON and cleaned CSV

### 3️⃣ Data Cleaning & Quality Assurance
- Uses **Pandas** to clean and format data
- Replaces missing/invalid values with `N/A`
- Visualizes null fields with heatmaps

### 4️⃣ Visualization & Analysis
- `scripts/analyzer.py`: generates static charts with Matplotlib
- `scripts/ai-data-viz.py`: AI-powered Streamlit dashboard with Together + E2B
- Allows querying the dataset in natural language and downloading generated charts

### 5️⃣ Version Control & Organization
- Proper `.gitignore` for logs, raw data, and environments
- Logs saved in `/logs/`, visualizations in `/plots/`
- Modular scripts inside `/scripts/`

---

## 📁 Project Structure

```bash
WeddingVenues-data-pipeline/
├── data/
│   ├── raw/               # Scraped JSON output
│   ├── processed/         # Cleaned CSV for analysis
│   └── plots/             # Chart PNGs from analyzer & Streamlit
├── logs/                 # Daily run logs
├── scripts/
│   ├── scraper.py         # Scrapes venue data from Hitched
│   ├── cleaner.py         # Cleans and enriches scraped data
│   ├── analyzer.py        # Generates static plots
│   └── ai-data-viz.py     # Streamlit app for AI visualization
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
	•	Python
	•	Selenium for scraping
	•	Pandas for cleaning
	•	Matplotlib / Seaborn for static visuals
	•	Together AI + E2B for AI chart generation
	•	Streamlit for interactive dashboard
	•	CRON for automation


⸻

📌 Next Up
	•	✅ Database integration (PostgreSQL/SQLite)
	•	✅ Automated git commits
	•	✅ Multi-region support & localization
	•	✅ Dashboard for vendor profile completeness