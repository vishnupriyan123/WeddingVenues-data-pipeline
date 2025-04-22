from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os

# Setup Chrome options
options = Options()
options.add_argument("--headless")  # comment to see live
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

# Initialize Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Go to the wedding venues listing page
driver.get("https://www.hitched.co.uk/wedding-venues/")

# Handle cookie consent pop-up if it appears
# try:
#     cookie_accept_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='cookie']"))
#     )
#     cookie_accept_button.click()
#     print("Cookie consent accepted.")
# except Exception as e:
#     print("No cookie consent pop-up.")

# Wait for the regions to load and extract data
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".venuesCitiesList"))
)

regions = []
try:
    # Extract region elements
    region_elements = driver.find_elements(By.CSS_SELECTOR, ".venuesCitiesList__link")
    for region in region_elements:
        region_name = region.text.strip()
        region_url = region.get_attribute("href")
        if region_url:
            regions.append({
                "name": region_name,
                "url": region_url
            })
    print(f"Found {len(regions)} regions.")
except Exception as e:
    print("Error while extracting regions:", e)

# Save region data to JSON file
regions_file = "data/raw/regions.json"
with open(regions_file, "w", encoding="utf-8") as f:
    json.dump(regions, f, indent=2, ensure_ascii=False)

print(f"Regions saved to {regions_file}")

# Logging scraper activity
with open("logs/region_scraper_log.txt", "a") as log:
    log.write(f"Scraped {len(regions)} regions on {time.ctime()}\n")

driver.quit()  # Close the browser after the task