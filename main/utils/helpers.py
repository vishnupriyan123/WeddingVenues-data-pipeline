from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from .selectors import SELECTORS


# collecting regions

def collect_regions(driver):
    print("Navigating to Hitched venue listing page...")
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

    print(f"Found {len(regions)} regions.")
    return regions

# for collecting basic venues data from each region

# def get_max_page(driver):
#     try:
#         page_buttons = driver.find_elements(By.CSS_SELECTOR, "button.pagination__itemButton")
#         page_numbers = [int(btn.text) for btn in page_buttons if btn.text.isdigit()]
#         return max(page_numbers) if page_numbers else 1
#     except:
#         return 1
    
# def scrape_venue_card(card):
#     try:
#         name = card.find_element(By.CSS_SELECTOR, "div.vendorTile__content h2").text
#     except:
#         name = None

#     try:
#         rating = card.find_element(By.CSS_SELECTOR, "span.vendorTile__rating").text
#         content_rating = card.find_element(By.CSS_SELECTOR, "div.vendorTile__contentRating").text
#         match = re.search(r"\(([\d,]+)\)", content_rating)
#         reviews = int(match.group(1).replace(",", "")) if match else None
#     except:
#         rating, reviews = None, None

#     try:
#         location = card.find_element(By.CSS_SELECTOR, "span.vendorTile__location").text
#     except:
#         location = None

#     try:
#         relative_link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
#         full_link = f"https://www.hitched.co.uk{relative_link}"
#     except:
#         full_link = None

#     try:
#         price_block = card.find_element(By.CSS_SELECTOR, "div.vendorTileFooter__price")
#         price_text = price_block.text.strip()
#         try:
#             icon_class = price_block.find_element(By.TAG_NAME, "i").get_attribute("class")
#             price_type = (
#                 "meal" if "menus-price" in icon_class else
#                 "venue" if "pricing" in icon_class else
#                 "other"
#             )
#         except:
#             price_type = None
#     except:
#         price_text, price_type = None, None

#     try:
#         capacity_text = card.find_element(By.CSS_SELECTOR, "div.vendorTileFooter__capacity").text
#     except:
#         capacity_text = None

#     return {
#         "name": name,
#         "rating": rating,
#         "no_of_reviews": reviews,
#         "location": location,
#         "price_text": price_text,
#         "price_type": price_type,
#         "capacity": capacity_text,
#         "url": full_link,
#     }

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
    return extract_text(driver, SELECTORS["venues"]["details"]["description"])

def extract_venue_url(driver, selector, attr="href", by=By.CSS_SELECTOR):
    try: 
        return driver.find_element(by, selector).get_attribute(attr)
    except:
        return None
    
def extract_faq_tags(driver, section_name):
    try:
        section = driver.find_element(By.XPATH, f"//h3[normalize-space(text())='{section_name}:']/following-sibling::div")
        tags = section.find_elements(By.CSS_SELECTOR, "div.storefrontFaqs__itemList")
        return [tag.text.strip() for tag in tags if tag.text.strip()]
    except:
        return []

def extract_map(driver, selector, attr="href", by=By.CSS_SELECTOR):
    try:
        return driver.find_element(by, selector).get_attribute(attr)
    except:
        return None


def extract_social_links(driver):
    try:
        anchors = driver.find_elements(By.CSS_SELECTOR, SELECTORS["venues"]["details"]["social_links"])
        return [a.get_attribute("href") for a in anchors if a.get_attribute("href")]
    except:
        return []

def extract_deals(driver, selectors):
    deals = []
    try:
        deal_tiles = driver.find_elements(By.CSS_SELECTOR, selectors["tile"])
        for tile in deal_tiles:
            try:
                deal_type = tile.find_element(By.CSS_SELECTOR, selectors["type"]).text.strip()
                title = tile.find_element(By.CSS_SELECTOR, selectors["title"]).text.strip()
                expiry = tile.find_element(By.CSS_SELECTOR, selectors["expires_on"]).text.strip()

                deals.append({
                    "type": deal_type,
                    "title": title,
                    "expires_on": expiry
                })
            except Exception as inner_e:
                print("⚠️ Skipping a deal due to missing info:", inner_e)
    except Exception as e:
        print("❌ Failed to extract deals section:", e)

    return deals


def extract_suppliers(driver, selectors):
    preferred_suppliers = []
    try:
        supplier_tiles = driver.find_elements(By.CSS_SELECTOR, selectors["tile"])
        # print(f"Found {len(supplier_tiles)} supplier cards")
        for tile in supplier_tiles:
            try:
                vendor_link = tile.find_element(By.CSS_SELECTOR, selectors["link"])
                vendor_name = vendor_link.text.strip()
                vendor_url = vendor_link.get_attribute("href")
            except:
                vendor_name = None
                vendor_url = None

            try:
                vendor_image = tile.find_element(By.CSS_SELECTOR, selectors["image"]).get_attribute("src")
            except:
                vendor_image = None

            try:
                rating_element = tile.find_element(By.CSS_SELECTOR, selectors["rating"])
                rating_text = rating_element.text.strip()
            except:
                rating_text = None

            try:
                info_div = tile.find_element(By.CSS_SELECTOR, selectors["info"])
                info_text = info_div.text.strip()
                category = info_text.split("·")[-1].strip() if "·" in info_text else None
            except:
                category = None

            preferred_suppliers.append({
                "vendor_name": vendor_name,
                "vendor_url": vendor_url,
                "vendor_image": vendor_image,
                "rating_text": rating_text,
                "category": category,
            })
    except Exception as e:
        print(f"❌ Failed to load supplier tiles: {e}")
    
    return preferred_suppliers