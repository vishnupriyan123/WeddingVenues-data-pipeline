import json
import traceback
from datetime import datetime
import logging
from tqdm import tqdm

from utils.driver_setup import setup_driver
from utils.helpers import scrape_region
from utils.file_utils import save_to_json, log_message, setup_directories

# Setup directories
dirs = setup_directories()
data_dir, processed_dir, raw_dir, log_dir, backup_dir = (
    dirs.data_dir,
    dirs.processed_dir,
    dirs.raw_dir,
    dirs.log_dir,
    dirs.backup_dir
)

# Setup log file
log_file = log_dir / "scraper_log.txt"

logging.basicConfig(
    filename=log_file,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Load regions
with open(raw_dir / "regions.json", "r", encoding="utf-8") as f:
    regions = json.load(f)

# Start Selenium driver
driver = setup_driver()

results = []

# tqdm progress bar around regions
for region in tqdm(regions, desc="Scraping Regions", ncols=100):
    region_name = region["name"]
    print(f"Scraping region: {region_name}")
    logging.info("Scraping region: %s", region_name)

    try:
        venues = scrape_region(driver, region)
        results.extend(venues)
    except Exception as e:
        print(f"❌ Failed to scrape region {region_name}: {e}")
        logging.error("Failed region %s: %s", region_name, traceback.format_exc())

# Save final results
today = datetime.now().strftime("%Y%m%d")

# Save with timestamp for backup
timestamped_file = backup_dir / f"all_venues_{today}.json"
save_to_json(results, timestamped_file)
log_message(log_file, f"✅ Saved timestamped venues file: {timestamped_file}")

# Save latest version
latest_file = raw_dir / "all_venues.json"
save_to_json(results, latest_file)
log_message(log_file, f"✅ Updated latest venues file: {latest_file}")

print(f"✅ Done! Scraped {len(results)} venues across {len(regions)} regions.")
logging.info("Finished: Scraped %d venues across %d regions.", len(results), len(regions))

driver.quit()