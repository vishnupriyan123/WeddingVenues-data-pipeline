import time
from utils.driver_setup import setup_driver
from utils.file_utils import save_to_json, log_message, setup_directories
from utils.helpers import collect_regions

# Setup
dirs = setup_directories()
driver = setup_driver()
regions_file = dirs.raw_dir / "regions.json"
log_file = dirs.log_dir / "region_scraper_log.txt"

try:
    regions = collect_regions(driver)
    save_to_json(regions, regions_file)
    log_message(log_file, f"Scraped {len(regions)} regions on {time.ctime()}")
    print(f"Regions saved to {regions_file}")
except Exception as e:
    print("Failed to scrape regions:", e)
    log_message(log_file, f"Failed to scrape regions: {str(e)}")
finally:
    driver.quit()