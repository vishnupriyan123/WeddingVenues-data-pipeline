import time
import json
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from multiprocessing import Pool, cpu_count
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

def wait_for_element(driver, by, value, timeout=10):  # Reduced timeout from 30 to 10
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

def scrape_venue_with_retry(venue):
    driver = setup_driver()  # Each process needs its own driver
    venue_no = venue.get("venue_no")
    venue_name = venue.get("name")
    base_url = venue.get("url")
    
    if not base_url:
        print(f"⚠️ Skipping venue without URL: {venue_name}")
        log_message(log_file, f"⚠️ Skipped venue (no URL): {venue_name}")
        driver.quit()
        return {
            "venue_no": venue_no,
            "venue_name": venue_name,
            "review_text": "N/A"
        }

    reviews_url = base_url.replace("wedding-venues", "wedding-venues/reviews")
    
    try:
        driver.get(reviews_url)
        # Fast check for "no reviews" message
        try:
            no_reviews_title = driver.find_element(By.CSS_SELECTOR, "div.sectionCardBig__title")
            if no_reviews_title and no_reviews_title.text.strip() == "Be the first to share your experience!":
                print(f"ℹ️ No reviews available for {venue_name}")
                log_message(log_file, f"ℹ️ No reviews available for {venue_name}")
                driver.quit()
                return {
                    "venue_no": venue_no,
                    "venue_name": venue_name,
                    "review_text": "No reviews"
                }
        except Exception:
            pass

        reviews_container = wait_for_element(
            driver,
            By.CSS_SELECTOR,
            "div.storefrontReviewsTileContent",
            timeout=5
        )

        if not reviews_container:
            print(f"ℹ️ No reviews section found for {venue_name}")
            log_message(log_file, f"ℹ️ No reviews section found for {venue_name}")
            driver.quit()
            return {
                "venue_no": venue_no,
                "venue_name": venue_name,
                "review_text": "No reviews section"
            }

        click_all_read_more_buttons(driver)
        venue_reviews = extract_reviews(driver)
        
        driver.quit()

        if venue_reviews:
            print(f"✅ Scraped {len(venue_reviews)} reviews from {venue_name}")
            log_message(log_file, f"✅ Scraped {len(venue_reviews)} reviews from {venue_name}")
            return [{
                "venue_no": venue_no,
                "venue_name": venue_name,
                "review_text": review
            } for review in venue_reviews]
        else:
            print(f"ℹ️ No reviews found for {venue_name}")
            log_message(log_file, f"ℹ️ No reviews found for {venue_name}")
            return {
                "venue_no": venue_no,
                "venue_name": venue_name,
                "review_text": "No reviews found"
            }
            
    except Exception as e:
        print(f"❌ Failed to scrape {venue_name}. Error: {str(e)}")
        log_message(log_file, f"❌ Failed to scrape {venue_name}. Error: {str(e)}")
        driver.quit()
        return {
            "venue_no": venue_no,
            "venue_name": venue_name,
            "review_text": "Error scraping"
        }

def main():
    # Load the venues
    df = pd.read_csv(processed_dir / "cleaned_venues.csv")
    all_venues = df.to_dict(orient="records")
    
    # Number of processes - use 75% of available CPUs
    num_processes = max(1, int(cpu_count() * 0.75))
    print(f"Starting scraping with {num_processes} processes...")
    
    # Create a pool of processes
    with Pool(num_processes) as pool:
        # Use imap_unordered to get results as they complete
        results = []
        for result in tqdm(pool.imap_unordered(scrape_venue_with_retry, all_venues), 
                          total=len(all_venues),
                          desc="Scraping Reviews",
                          colour="cyan"):
            if isinstance(result, list):
                results.extend(result)
            else:
                results.append(result)
            
            # Save progress every 10 venues
            if len(results) % 10 == 0:
                save_progress(results)

    # Final save
    save_progress(results)
    print(f"\n✅ Done! Scraped reviews from {len(all_venues)} venues.")
    log_message(log_file, f"✅ Finished scraping reviews across {len(all_venues)} venues.")

def save_progress(results):
    """Save current progress to CSV files"""
    reviews_df = pd.DataFrame(results)
    
    # Save latest version
    latest_reviews_file = processed_dir / "venue_reviews.csv"
    reviews_df.to_csv(latest_reviews_file, index=False)
    
    # Save timestamped backup
    today = datetime.now().strftime("%Y%m%d")
    timestamped_reviews_file = backup_dir / f"venue_reviews_{today}.csv"
    reviews_df.to_csv(timestamped_reviews_file, index=False)

if __name__ == "__main__":
    main()