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
    extract_text,
    extract_social_links,
    extract_suppliers,
    extract_faq_tags,
    extract_deals,
    extract_venue_url,
    extract_map
)
from utils.selectors import SELECTORS

# Setup directories
data_dir = Path("data")
processed_dir = data_dir / "processed"
raw_dir = data_dir / "raw"
processed_dir.mkdir(parents=True, exist_ok=True)
raw_dir.mkdir(parents=True, exist_ok=True)

# Load venues from cleaned CSV
df = pd.read_csv(processed_dir / "cleaned_venues.csv")
all_venues = df.to_dict(orient="records")

# Start Selenium driver
driver = setup_driver()

# Final output list
venue_details_list = []

for venue in tqdm(all_venues, desc="Scraping full venue details"):
    url = venue.get("url", "")
    if not url.startswith("http"):
        print(f"⚠️ Skipping malformed URL: {url}")
        continue

    print(f"🕵️‍♂️ Visiting: {url}")
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))

        venue_no = venue.get("venue_no")  # Pick up the V1, V2, V3 etc.

        # 🧹 Extract details
        full_description = extract_description(driver)
        address_full = extract_text(driver, SELECTORS["venues"]["details"]["address"])
        venue_url = extract_venue_url(driver, SELECTORS["venues"]["details"]["venue_url"], attr="data-href")
        map_url = extract_map(driver, SELECTORS["venues"]["details"]["map_url"], "href")
        social_links = extract_social_links(driver)

        # 🧩 Extract and tag deals
        deals = extract_deals(driver, SELECTORS["venues"]["details"]["deals_section"])
        for deal in deals:
            deal["venue_no"] = venue_no

        # 🧩 Extract and tag suppliers
        suppliers = extract_suppliers(driver, SELECTORS["venues"]["details"]["suppliers_section"])
        for supplier in suppliers:
            supplier["venue_no"] = venue_no

        # 🧩 Extract FAQ tags
        faq_sections = SELECTORS["venues"]["details"]["faq_sections"]
        faq_data = {
            key: extract_faq_tags(driver, section_name)
            for key, section_name in faq_sections.items()
        }

        # 📦 Combine everything
        venue_data = {
            **venue,
            "description": full_description,
            "address_full": address_full,
            "venue_url": venue_url,
            "map_url": map_url,
            "social_links": social_links,
            "deals": deals,
            "preferred_suppliers": suppliers,
            **faq_data
        }

        venue_details_list.append(venue_data)

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        continue

# 💾 Save
save_to_json(venue_details_list, raw_dir / "venue_all_details.json")
print(f"✅ Done! Scraped {len(venue_details_list)} venues.")

# 🧹 Cleanup
driver.quit()