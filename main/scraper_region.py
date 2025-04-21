import json
import os
import re
import time
import tempfile
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load region list
with open("data/raw/regions.json", "r") as f:
    regions = json.load(f)

# Make sure folders exist
os.makedirs("data/raw", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Set up browser
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

                except Exception as e:
                    print("\t\t⚠️ Error parsing venue:", e)

    except Exception as e:
        print(f"\tFailed to scrape region {region['name']}: {e}")

# Save files
today = datetime.now().strftime("%Y%m%d")
with open(f"data/raw/all_venues_{today}.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

with open("data/raw/all_venues.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

with open("logs/scraper_log.txt", "a") as log:
    log.write(f"Scraped {len(results)} venues across {len(regions)} regions on {time.ctime()}\n")

print(f"✅ Done! Scraped {len(results)} venues across {len(regions)} regions.")
driver.quit()