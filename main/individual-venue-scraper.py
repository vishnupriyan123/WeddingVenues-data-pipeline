import re
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 🎯 Target venue URL
venue_url = "https://www.hitched.co.uk/wedding-venues/the-oak-tree-of-peover_6313.htm"

# 🧠 Set up headless browser
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 🧩 Updated helper for FAQ extraction
def get_faq_tags_by_title(driver, section_name):
    try:
        section = driver.find_element(By.XPATH, f"//h3[normalize-space(text())='{section_name}:']/following-sibling::div")
        tags = section.find_elements(By.CSS_SELECTOR, "div.storefrontFaqs__itemList")
        return [tag.text.strip() for tag in tags if tag.text.strip()]
    except Exception as e:
        print(f"⚠️ Couldn't extract tags for {section_name}: {e}")
        return []

try:
    driver.get(venue_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
    )

    # ✅ Click "Read more" button if it exists
    try:
        read_more = driver.find_element(By.CSS_SELECTOR, "button.storefrontDescription__link")
        driver.execute_script("arguments[0].click();", read_more)
        time.sleep(1)
    except:
        pass

    # 📝 Full Description
    try:
        section = driver.find_element(By.CSS_SELECTOR, "section.storefrontDescription.app-section-highlighter-item")
        paragraphs = section.find_elements(By.TAG_NAME, "p")
        full_description = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
    except Exception as e:
        full_description = None
        print("⚠️ Full description extraction failed:", e)

    # 📍 Full Address
    try:
        address_full = driver.find_element(By.CSS_SELECTOR, "div.storefrontAddresses__header").text.strip()
    except:
        address_full = None

    # 🗺️ Map URL
    try:
        map_img = driver.find_element(By.CSS_SELECTOR, "img.app-static-map")
        map_embed_url = map_img.get_attribute("data-src") or map_img.get_attribute("src")
    except:
        map_embed_url = None

    # 💷 Starting Price
    try:
        price_text = driver.find_element(By.CSS_SELECTOR, "p.vendorHeader__priceText").text
        starting_price = re.search(r"[\£\d,]+", price_text).group(0)
    except:
        starting_price = None

    # 📸 Media Count
    try:
        media_button = driver.find_element(By.XPATH, "//button[contains(text(), 'View photos')]")
        media_text = media_button.text
        photo_count = int(re.search(r"\d+", media_text).group()) if media_text else 0
    except:
        photo_count = 0

    # 🎬 Video Count
    try:
        video_count = len(driver.find_elements(By.CSS_SELECTOR, "div.vendorVideoCarousel__container iframe"))
    except:
        video_count = 0

    # 🏷️ Tags from FAQs
    venue_type_tags = get_faq_tags_by_title(driver, "Venue type")
    dining_options = get_faq_tags_by_title(driver, "Dining options")
    ceremony_options = get_faq_tags_by_title(driver, "Ceremony options")
    entertainment_options = get_faq_tags_by_title(driver, "Evening entertainment")

    # 💰 Deals
    has_deals = False
    deal_details = []
    try:
        deals_button = driver.find_element(By.XPATH, "//a[contains(@href, '/deals')]")
        if deals_button:
            has_deals = True
            driver.get(deals_button.get_attribute("href"))
            time.sleep(3)
            deals = driver.find_elements(By.CSS_SELECTOR, "li.vendorDeals__deal")
            deal_details = [deal.text.strip() for deal in deals]
    except:
        has_deals = False

    # 💍 Real Weddings
    try:
        real_wedding_tab = driver.find_element(By.XPATH, "//a[contains(@href, '/real-weddings')]")
        if real_wedding_tab:
            driver.get(real_wedding_tab.get_attribute("href"))
            time.sleep(3)
            weddings = driver.find_elements(By.CSS_SELECTOR, "li.realWeddingTile")
            num_real_weddings = len(weddings)
        else:
            num_real_weddings = 0
    except:
        num_real_weddings = 0

    # 🎁 Combine Everything
    venue_details = {
        "url": venue_url,
        "description": full_description,
        "address_full": address_full,
        "starting_price": starting_price,
        "photo_count": photo_count,
        "video_count": video_count,
        "venue_type_tags": venue_type_tags,
        "dining_options": dining_options,
        "ceremony_options": ceremony_options,
        "entertainment_options": entertainment_options,
        "has_deals": has_deals,
        "deal_details": deal_details,
        "num_real_weddings": num_real_weddings,
        "map_embed_url": map_embed_url,
    }

    # 💾 Save to JSON
    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/venue_details_sample.json", "w", encoding="utf-8") as f:
        json.dump(venue_details, f, indent=2, ensure_ascii=False)

    print("✅ Scraped and saved venue details successfully!")

except Exception as e:
    print("❌ Scraping failed:", e)

finally:
    driver.quit()