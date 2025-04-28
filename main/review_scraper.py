import time
import json
import pandas as pd
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.driver_setup import setup_driver
from utils.file_utils import save_to_json

# Setup directories
data_dir = Path("data")
processed_dir = data_dir / "processed"
raw_dir = data_dir / "raw"
processed_dir.mkdir(parents=True, exist_ok=True)
raw_dir.mkdir(parents=True, exist_ok=True)

# Load the venues
df = pd.read_csv(processed_dir / "cleaned_venues.csv")
all_venues = df.to_dict(orient="records")

# Start Selenium driver
driver = setup_driver()

# Final output
all_reviews = []

for venue in all_venues:
    venue_no = venue.get("venue_no")
    venue_name = venue.get("name")
    base_url = venue.get("url")
    
    if not base_url:
        continue

    reviews_url = base_url.replace("wedding-venues", "wedding-venues/reviews")
    
    print(f"🕵️‍♂️ Visiting reviews page for: {venue_name}")

    try:
        driver.get(reviews_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.storefrontReviewsTileContent"))
        )
        
        time.sleep(2)  # Optional wait to fully load

        # 🛠 Auto-click all 'Read more' buttons if present
        try:
            read_more_buttons = driver.find_elements(By.CSS_SELECTOR, "button.app-read-more-link")
            for btn in read_more_buttons:
                try:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.2)  # small pause to let it expand
                except Exception as click_e:
                    print(f"Couldn't click a 'Read more' button: {click_e}")
        except Exception as e:
            print(f"Couldn't find 'Read more' buttons: {e}")

        # 🎯 Now scrape all fully expanded reviews
        review_blocks = driver.find_elements(By.CSS_SELECTOR, "div.storefrontReviewsTileContent")

        for block in review_blocks:
            try:
                review_text = block.find_element(
                    By.CSS_SELECTOR, 
                    "div.storefrontReviewsTileContent__description.app-reviews-tile-read-more"
                ).text.strip()
                
                all_reviews.append({
                    "venue_no": venue_no,
                    "venue_name": venue_name,
                    "review_text": review_text
                })

            except Exception as e:
                print(f"⚠️ Skipped a review block: {e}")

    except Exception as e:
        print(f"Failed to scrape reviews for {venue_name}: {e}")

# Save reviews
reviews_df = pd.DataFrame(all_reviews)
reviews_df.to_csv(processed_dir / "venue_reviews.csv", index=False)

print(f"✅ Done! Scraped {len(all_reviews)} reviews from {len(all_venues)} venues.")

# Close driver
driver.quit()