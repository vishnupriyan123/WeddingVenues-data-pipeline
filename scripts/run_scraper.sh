#!/bin/bash

# Move into the script directory
cd "$(dirname "$0")" || exit

# Activate your virtual environment
source ../venv/bin/activate

# Log start and run the scraper
echo "[CRON START] $(date)" >> ../logs/cron_debug.log
python scraper.py >> ../logs/scraper_log.txt 2>&1
echo "[CRON END] $(date)" >> ../logs/cron_debug.log