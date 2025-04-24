import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.driver_setup import setup_driver
from utils.helpers import (
    extract_description, extract_text, extract_faq_tags,
    extract_social_links, extract_suppliers
)
from utils.file_utils import save_to_json
from utils.selectors import SELECTORS

venue_url = "https://www.hitched.co.uk/wedding-venues/the-oak-tree-of-peover_6313.htm"

driver = setup_driver()
try:
    driver.get(venue_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))

    venue_details = {
        "url": venue_url,
        "description": extract_description(driver),
        "address_full": extract_text(driver, SELECTORS["address"]),
        "map_embed_url": driver.find_element(By.CSS_SELECTOR, SELECTORS["map_img"]).get_attribute("src"),
        "photo_count": int(re.search(r"\d+", extract_text(driver, SELECTORS["photo_button"], by=By.XPATH) or "0").group()),
        "venue_type_tags": extract_faq_tags(driver, "Venue type"),
        "dining_options": extract_faq_tags(driver, "Dining options"),
        "ceremony_options": extract_faq_tags(driver, "Ceremony options"),
        "entertainment_options": extract_faq_tags(driver, "Evening entertainment"),
        "social_links": extract_social_links(driver),
        "preferred_suppliers": extract_suppliers(driver)
    }

    save_to_json(venue_details, "data/raw/venue_details_sample.json")
    print("✅ Scraped and saved venue details successfully!")

except Exception as e:
    print("❌ Scraping failed:", e)
finally:
    driver.quit()