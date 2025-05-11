import time
import json
import pandas as pd
from utils.driver_setup import setup_driver
from utils.file_utils import save_to_json, log_message, setup_directories
from utils.helpers import collect_regions
from datetime import datetime

# Setup
dirs = setup_directories()
driver = setup_driver()
regions_file = dirs.raw_dir / "regions.json"
log_file = dirs.log_dir / "region_scraper_log.txt"
cleaned_file = dirs.processed_dir / "cleaned_regions.csv"
timestamp = datetime.now().strftime("%Y%m%d")
backup_file = dirs.backup_dir / f"cleaned_regions{timestamp}.csv"

try:
    # Scrape data
    regions = collect_regions(driver)

    # Save raw JSON
    save_to_json(regions, regions_file)
    print(f"✅ Regions saved to {regions_file}")

    log_message(log_file, f"Scraped {len(regions)} regions on {time.ctime()}")

    # Convert to DataFrame and clean
    df = pd.DataFrame(regions)
    df.insert(0, "region_id", ["R" + str(i) for i in range(1, len(df) + 1)])
    df["name"] = df["name"].str.strip()
    df["url"] = df["url"].str.strip()
    df = df.fillna("N/A")

    # Save latest cleaned CSV to processed/
    df.to_csv(cleaned_file, index=False)
    print(f"✅ Cleaned regions saved to {cleaned_file}")

    # Save timestamped backup CSV to backups/
    cleaned_backup = dirs.backup_dir / f"cleaned_regions_{timestamp}.csv"
    df.to_csv(cleaned_backup, index=False)
    print(f"Cleaned backup saved to {cleaned_backup}")

except Exception as e:
    print("❌ Failed to scrape or clean regions:", e)
    log_message(log_file, f"Error: {str(e)}")

finally:
    driver.quit()
