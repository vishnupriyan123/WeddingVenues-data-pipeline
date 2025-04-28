import time
import json
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.driver_setup import setup_driver
from utils.file_utils import save_to_json, log_message, setup_directories
from utils.helpers import click_all_read_more_buttons, extract_reviews

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
log_file = log_dir / "review_scraper_log.txt"

# Load the venues
df = pd.read_csv(processed_dir / "cleaned_venues.csv")
all_venues = df.to_dict(orient="records")

# Start Selenium driver
driver = setup_driver()

# Final output
all_reviews = []

# Progress bar for all venues
for venue in tqdm(all_venues, desc="Scraping Reviews", colour="cyan"):
    venue_no = venue.get("venue_no")
    venue_name = venue.get("name")
    base_url = venue.get("url")

    if not base_url:
        print(f"⚠️ Skipping venue without URL: {venue_name}")
        log_message(log_file, f"⚠️ Skipped venue (no URL): {venue_name}")
        continue

    reviews_url = base_url.replace("wedding-venues", "wedding-venues/reviews")

    try:
        driver.get(reviews_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.storefrontReviewsTileContent"))
        )

        click_all_read_more_buttons(driver)
        venue_reviews = extract_reviews(driver)

        if venue_reviews:
            for review_text in venue_reviews:
                all_reviews.append({
                    "venue_no": venue_no,
                    "venue_name": venue_name,
                    "review_text": review_text
                })
            print(f"✅ Scraped {len(venue_reviews)} reviews from {venue_name}")
            log_message(log_file, f"✅ Scraped {len(venue_reviews)} reviews from {venue_name}")
        else:
            all_reviews.append({
                "venue_no": venue_no,
                "venue_name": venue_name,
                "review_text": "N/A"
            })
            print(f"⚠️ No reviews found for {venue_name}, added N/A")
            log_message(log_file, f"⚠️ No reviews found for {venue_name}, added N/A")

    except Exception as e:
        all_reviews.append({
            "venue_no": venue_no,
            "venue_name": venue_name,
            "review_text": "N/A"
        })
        print(f"❌ Failed to scrape {venue_name}, added N/A. Error: {e}")
        log_message(log_file, f"❌ Failed to scrape {venue_name}, added N/A. Error: {e}")
        continue

# Save all reviews
reviews_df = pd.DataFrame(all_reviews)

# Save latest version
latest_reviews_file = processed_dir / "venue_reviews.csv"
reviews_df.to_csv(latest_reviews_file, index=False)

# Save timestamped backup
today = datetime.now().strftime("%Y%m%d")
timestamped_reviews_file = backup_dir / f"venue_reviews_{today}.csv"
reviews_df.to_csv(timestamped_reviews_file, index=False)

print(f"\n✅ Done! Scraped {len(all_reviews)} reviews from {len(all_venues)} venues.")
log_message(log_file, f"✅ Finished scraping {len(all_reviews)} reviews across {len(all_venues)} venues.")

# Close driver
driver.quit()