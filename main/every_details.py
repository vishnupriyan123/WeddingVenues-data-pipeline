import pandas as pd
from pathlib import Path
from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from utils.driver_setup import setup_driver
from utils.file_utils import save_to_json
from utils.helpers import (
    extract_description,
    extract_social_links,
    extract_suppliers,
    extract_faq_tags,
)
from utils.selectors import SELECTORS

# 📁 Setup directories
data_dir = Path("data")
processed_dir = data_dir / "processed"
raw_dir = data_dir / "raw"
processed_dir.mkdir(parents=True, exist_ok=True)
raw_dir.mkdir(parents=True, exist_ok=True)

# 📄 Load venues from cleaned CSV
df = pd.read_csv(processed_dir / "cleaned_venues.csv")
all_venues = df.to_dict(orient="records")

# 🚗 Start Selenium driver
driver = setup_driver()

# 📦 Collect full venue data
venue_details_list = []

for venue in tqdm(all_venues, desc="Scraping full venue details"):
    url = venue.get("url", "")
    if not url.startswith("http"):
        print(f"⛔ Skipping malformed URL: {url}")
        continue

    print(f"🕵️‍♂️ Visiting: {url}")
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))

        # 🎯 Extract all details using modular functions
        full_description = extract_description(driver)
        social_links = extract_social_links(driver)
        suppliers = extract_suppliers(driver, SELECTORS["venues"]["details"]["suppliers_section"])

        venue_type_tags = extract_faq_tags(driver, "Venue type")
        dining_options = extract_faq_tags(driver, "Dining options")
        ceremony_options = extract_faq_tags(driver, "Ceremony options")
        entertainment_options = extract_faq_tags(driver, "Evening entertainment")

        # 🧩 Combine scraped data with existing venue info
        venue_data = {
            **venue,
            "description": full_description,
            "venue_type_tags": venue_type_tags,
            "dining_options": dining_options,
            "ceremony_options": ceremony_options,
            "entertainment_options": entertainment_options,
            "social_links": social_links,
            "preferred_suppliers": suppliers,
        }

        venue_details_list.append(venue_data)

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        continue

# 💾 Save to JSON
save_to_json(venue_details_list, "data/raw/venue_all_details.json")
print(f"✅ Done! Scraped {len(venue_details_list)} venues.")

# 🧹 Cleanup
driver.quit()