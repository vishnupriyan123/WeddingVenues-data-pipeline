import json
import re
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup directories using pathlib
data_dir = Path("data")
raw_dir = data_dir / "raw"
log_dir = Path("logs")

raw_dir.mkdir(parents=True, exist_ok=True)
log_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=log_dir / "scraper_log.txt",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Load regions list
with open(raw_dir / "regions.json", "r") as f:
    regions = json.load(f)

# Setup browser
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
options.add_argument("accept-language=en-US,en;q=0.9")
temp_profile = tempfile.mkdtemp()
options.add_argument(f"--user-data-dir={temp_profile}")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(180)

results = []

for region in regions:
    print(f"Scraping region: {region['name']}")
    logging.info("Scraping region: %s", region['name'])
    base_url = region["url"] + "?page="

    try:
        driver.get(base_url + "1")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.vendorTile"))
        )

        try:
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "button.pagination__itemButton")
            page_numbers = [int(btn.text) for btn in page_buttons if btn.text.isdigit()]
            max_page = max(page_numbers) if page_numbers else 1
        except:
            max_page = 1

        for page in range(1, max_page + 1):
            url = region["url"] + f"?page={page}"
            print(f"\t➡ Page {page} of {region['name']}")
            logging.info("➡ Page %d of %s", page, region["name"])
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.vendorTile"))
            )

            venue_cards = driver.find_elements(By.CSS_SELECTOR, "li.vendorTile")
            for card in venue_cards:
                try:
                    name = card.find_element(By.CSS_SELECTOR, "div.vendorTile__content h2").text

                    try:
                        rating = card.find_element(By.CSS_SELECTOR, "span.vendorTile__rating").text
                        content_rating = card.find_element(By.CSS_SELECTOR, "div.vendorTile__contentRating").text
                        reviews = re.search(r"\(([\d,]+)\)", content_rating)
                        reviews = int(reviews.group(1).replace(",", "")) if reviews else None
                    except:
                        rating = None
                        reviews = None

                    location = card.find_element(By.CSS_SELECTOR, "span.vendorTile__location").text
                    relative_link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                    full_link = "https://www.hitched.co.uk" + relative_link

                    try:
                        price_block = card.find_element(By.CSS_SELECTOR, "div.vendorTileFooter__price")
                        price_text = price_block.text.strip()

                        try:
                            price_icon = price_block.find_element(By.TAG_NAME, "i")
                            icon_class = price_icon.get_attribute("class")

                            if "menus-price" in icon_class:
                                price_type = "meal"
                            elif "pricing" in icon_class:
                                price_type = "venue"
                            else:
                                price_type = "other"
                        except:
                            price_type = None
                    except:
                        price_text = None
                        price_type = None

                    try:
                        capacity_text = card.find_element(By.CSS_SELECTOR, "div.vendorTileFooter__capacity").text
                    except:
                        capacity_text = None

                    results.append({
                        "region": region["name"],
                        "name": name,
                        "rating": rating,
                        "no_of_reviews": reviews,
                        "location": location,
                        "price_text": price_text,
                        "price_type": price_type,
                        "capacity": capacity_text,
                        "url": full_link
                    })

                except Exception:
                    logging.warning("⚠️ Error parsing venue:\n%s", traceback.format_exc())

    except Exception:
        logging.error("Failed to scrape region %s:\n%s", region['name'], traceback.format_exc())

# Save files
today = datetime.now().strftime("%Y%m%d")

timestamped_file = raw_dir / f"all_venues_{today}.json"
latest_file = raw_dir / "all_venues.json"

with open(timestamped_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
    logging.info("Saved timestamped file: %s", timestamped_file)

with open(latest_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
    logging.info("Saved latest file: %s", latest_file)

print(f"✅ Done! Scraped {len(results)} venues across {len(regions)} regions.")
logging.info("Finished: Scraped %d venues across %d regions.", len(results), len(regions))

driver.quit()