from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re
import os
from datetime import datetime

# Make sure data/raw and logs folders exist
os.makedirs("../data/raw", exist_ok=True)
os.makedirs("../logs", exist_ok=True)


# Setup browser

# options = Options()
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")

# headless mode fix for gitactions
options = Options()
options.add_argument("--headless=new") # Comment to headless mode for local debugging
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)
options.add_argument("accept-language=en-US,en;q=0.9")

#driver = webdriver.Chrome(options=options)
# fix for gitactions
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

base_url = "https://www.hitched.co.uk/busc.php?id_grupo=1&id_region=1001&showmode=list&priceType=menu&userSearch=1&showNearByListing=0&isNearby=0&NumPage="

# Open the first page
driver.get(base_url + "1")
driver.save_screenshot("../logs/debug_screenshot.png")
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "li.vendorTile"))
)

# Detecting number of total pages
try:
    page_buttons = driver.find_elements(By.CSS_SELECTOR, "button.pagination__itemButton")
    page_numbers = [int(btn.text) for btn in page_buttons if btn.text.isdigit()]
    max_page = max(page_numbers) if page_numbers else 1
    print(f"Total pages detected: {max_page}")
except Exception as e:
    max_page = 1
    print("Couldn't detect pagination: ", e)

results = []

# Loop through all pages
for page in range(1, max_page + 1):
    page_url = base_url + str(page)
    print(f"Scraping page {page}: {page_url}")
    driver.get(page_url)

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
            print("Error parsing a venue:", e)

# Save timestamped version (for logging/auditing)
today_str = datetime.now().strftime("%Y%m%d")
timestamped_file = f"../data/raw/hitched_venues_{today_str}.json"

# Save latest version (for use in dashboard tools)
latest_file = "../data/raw/hitched_venues.json"

# Save both
with open(timestamped_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

with open(latest_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# logging
with open("../logs/scraper_log.txt", "a") as log:
    log.write(f"Scraped {len(results)} venues on {time.ctime()}\n")

print(f"Scraped {len(results)} venues across {max_page} pages and saved to hitched_venues.json")
