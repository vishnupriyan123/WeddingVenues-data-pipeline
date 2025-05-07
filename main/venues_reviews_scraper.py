import time
import json
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException

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

# Final output
all_reviews = []

def wait_for_element(driver, by, value, timeout=30):
    """Wait for an element to be present and visible"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        # Additional wait for element to be visible
        WebDriverWait(driver, timeout).until(
            EC.visibility_of(element)
        )
        return element
    except (TimeoutException, StaleElementReferenceException):
        return None

def scrape_venue_with_retry(driver, venue, max_retries=2):
    venue_no = venue.get("venue_no")
    venue_name = venue.get("name")
    base_url = venue.get("url")
    if not base_url:
        print(f"⚠️ Skipping venue without URL: {venue_name}")
        log_message(log_file, f"⚠️ Skipped venue (no URL): {venue_name}")
        return None

    reviews_url = base_url.replace("wedding-venues", "wedding-venues/reviews")

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(2)
            driver.get(reviews_url)

            # Fast check for "no reviews" message
            try:
                no_reviews_title = driver.find_element(By.CSS_SELECTOR, "div.sectionCardBig__title")
                if no_reviews_title and no_reviews_title.text.strip() == "Be the first to share your experience!":
                    print(f"ℹ️ No reviews available for {venue_name}")
                    log_message(log_file, f"ℹ️ No reviews available for {venue_name}")
                    return []
            except Exception:
                pass

            # Shorter wait for reviews container
            reviews_container = wait_for_element(
                driver,
                By.CSS_SELECTOR,
                "div.storefrontReviewsTileContent",
                timeout=10  # Reduced timeout
            )

            if not reviews_container:
                if attempt < max_retries - 1:
                    print(f"⚠️ Reviews container not found for {venue_name}, retrying...")
                    continue
                else:
                    print(f"ℹ️ No reviews section found for {venue_name}")
                    log_message(log_file, f"ℹ️ No reviews section found for {venue_name}")
                    return []

            click_all_read_more_buttons(driver)
            venue_reviews = extract_reviews(driver)

            if venue_reviews:
                print(f"✅ Scraped {len(venue_reviews)} reviews from {venue_name}")
                log_message(log_file, f"✅ Scraped {len(venue_reviews)} reviews from {venue_name}")
                return venue_reviews
            else:
                print(f"ℹ️ No reviews found for {venue_name}")
                log_message(log_file, f"ℹ️ No reviews found for {venue_name}")
                return []
        except (TimeoutException, WebDriverException) as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Attempt {attempt + 1} failed for {venue_name}, retrying... Error: {str(e)}")
                try:
                    driver.quit()
                except:
                    pass
                driver = setup_driver()
            else:
                print(f"❌ Failed to scrape {venue_name} after {max_retries} attempts. Error: {str(e)}")
                log_message(log_file, f"❌ Failed to scrape {venue_name} after {max_retries} attempts. Error: {str(e)}")
                return None
    return None

# Start Selenium driver
driver = setup_driver()

# Progress bar for all venues
for venue in tqdm(all_venues, desc="Scraping Reviews", colour="cyan"):
    venue_reviews = scrape_venue_with_retry(driver, venue)
    
    if venue_reviews is not None:
        for review_text in venue_reviews:
            all_reviews.append({
                "venue_no": venue.get("venue_no"),
                "venue_name": venue.get("name"),
                "review_text": review_text
            })
    else:
        all_reviews.append({
            "venue_no": venue.get("venue_no"),
            "venue_name": venue.get("name"),
            "review_text": "N/A"
        })

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
try:
    driver.quit()
except:
    pass