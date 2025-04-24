from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from .selectors import SELECTORS


# collecting regions helpers

def collect_regions(driver):
    print("🌐 Navigating to Hitched venue listing page...")
    driver.get("https://www.hitched.co.uk/wedding-venues/")

    # Wait until the region links are loaded
    WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["region"]["list"]))
    )

    print("🔍 Extracting regions...")
    region_elements = driver.find_elements(By.CSS_SELECTOR, SELECTORS["region"]["link"])
    
    regions = []
    for region in region_elements:
        name = region.text.strip()
        url = region.get_attribute("href")
        if url:
            regions.append({"name": name, "url": url})

    print(f"✅ Found {len(regions)} regions.")
    return regions

# for collecting basic venues data from each region



# for collecting  individual venue datas

def click_read_more(driver):
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button.storefrontDescription__link")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)
    except:
        pass

def extract_text(driver, selector, by=By.CSS_SELECTOR):
    try:
        return driver.find_element(by, selector).text.strip()
    except:
        return None

def extract_description(driver):
    click_read_more(driver)
    return extract_text(driver, SELECTORS["description"])

def extract_faq_tags(driver, section_name):
    try:
        section = driver.find_element(By.XPATH, f"//h3[normalize-space(text())='{section_name}:']/following-sibling::div")
        tags = section.find_elements(By.CSS_SELECTOR, "div.storefrontFaqs__itemList")
        return [tag.text.strip() for tag in tags if tag.text.strip()]
    except:
        return []

def extract_social_links(driver):
    try:
        anchors = driver.find_elements(By.CSS_SELECTOR, SELECTORS["social_links"])
        return [a.get_attribute("href") for a in anchors if a.get_attribute("href")]
    except:
        return []

def extract_suppliers(driver):
    suppliers = []
    try:
        supplier_cards = driver.find_elements(By.CSS_SELECTOR, "div.storefrontEndorsedVendor__tile")
        for card in supplier_cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, "a.storefrontEndorsedVendor__tileTitle").text
                url = card.find_element(By.CSS_SELECTOR, "a.storefrontEndorsedVendor__tileTitle").get_attribute("href")
                img = card.find_element(By.CSS_SELECTOR, "picture img").get_attribute("src")
                rating_block = card.find_elements(By.CSS_SELECTOR, ".storefrontEndorsedVendor__rating span")
                rating = rating_block[0].text if rating_block else None
                reviews = rating_block[1].text if len(rating_block) > 1 else None
                category = card.text.split('\n')[-1]  # fallback for bottom text
                suppliers.append({
                    "name": name,
                    "url": url,
                    "image": img,
                    "rating": rating,
                    "reviews": reviews,
                    "category": category
                })
            except Exception as e:
                print("⚠️ Failed to parse one supplier:", e)
    except Exception as e:
        print("⚠️ Suppliers section not found:", e)
    return suppliers