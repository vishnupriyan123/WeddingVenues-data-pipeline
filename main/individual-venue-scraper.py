import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.driver_setup import setup_driver
from utils.helpers import (
    extract_description, extract_text, extract_faq_tags,
    extract_social_links, extract_suppliers, extract_map, extract_venue_url, extract_deals
)
from utils.file_utils import save_to_json
from utils.selectors import SELECTORS

venue_url = "https://www.hitched.co.uk/wedding-venues/the-oak-tree-of-peover_6313.htm"

driver = setup_driver()
try:
    driver.get(venue_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))

    # Build FAQ tag fields dynamically
    faq_sections = SELECTORS["venues"]["details"]["faq_sections"]
    faq_data = {
        key: extract_faq_tags(driver, section_name)
        for key, section_name in faq_sections.items()
    }

    venue_details = {
        "url": venue_url,
        "description": extract_description(driver),
        "address_full": extract_text(driver, SELECTORS["venues"]["details"]["address"]),
        "venue_url": extract_venue_url(driver, SELECTORS["venues"]["details"]["venue_url"], attr="data-href"),
        "map_url": extract_map(driver, SELECTORS["venues"]["details"]["map_url"], "href"),
        "social_links": extract_social_links(driver),
        "deals": extract_deals(driver, SELECTORS["venues"]["details"]["deals_section"]),
        "preferred_suppliers": extract_suppliers(driver, SELECTORS["venues"]["details"]["suppliers_section"]),
        **faq_data
    }

    save_to_json(venue_details, "data/raw/venue_details_sample.json")
    print("✅ Scraped and saved venue details successfully!")

except Exception as e:
    print("❌ Scraping failed:", e)
finally:
    driver.quit()
