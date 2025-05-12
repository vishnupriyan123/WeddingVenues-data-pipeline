from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from .custom_selectors import SELECTORS


### collecting regions

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

### for collecting venue names and essecntial data

# inside utils/helpers.py
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .custom_selectors import SELECTORS

def get_max_page(driver):
    """Get the maximum number of pages in a region."""
    try:
        page_buttons = driver.find_elements(By.CSS_SELECTOR, "button.pagination__itemButton")
        page_numbers = [int(btn.text) for btn in page_buttons if btn.text.isdigit()]
        return max(page_numbers) if page_numbers else 1
    except:
        return 1

def scrape_venue_card(card, region_name):
    """Scrape basic details of a venue from its card."""
    try:
        name = card.find_element(By.CSS_SELECTOR, SELECTORS["venues"]["venue_name"]).text
    except:
        name = None

    try:
        rating = card.find_element(By.CSS_SELECTOR, SELECTORS["venues"]["venue_rating"]).text
        content_rating = card.find_element(By.CSS_SELECTOR, SELECTORS["venues"]["venue_rating_text"]).text
        match = re.search(r"\(([\d,]+)\)", content_rating)
        reviews = int(match.group(1).replace(",", "")) if match else None
    except:
        rating, reviews = None, None

    try:
        location = card.find_element(By.CSS_SELECTOR, SELECTORS["venues"]["venue_location"]).text
    except:
        location = None

    try:
        relative_link = card.find_element(By.CSS_SELECTOR, SELECTORS["venues"]["venue_link"]).get_attribute("href")
        full_link = relative_link if relative_link.startswith("http") else f"https://www.hitched.co.uk{relative_link}"
    except:
        full_link = None

    try:
        price_block = card.find_element(By.CSS_SELECTOR, SELECTORS["venues"]["venue_price_block"])
        price_text = price_block.text.strip()
        try:
            icon_class = price_block.find_element(By.TAG_NAME, "i").get_attribute("class")
            if "menus-price" in icon_class:
                price_type = "meal"
            elif "pricing" in icon_class:
                price_type = "venue"
            else:
                price_type = "other"
        except:
            price_type = None
    except:
        price_text, price_type = None, None

    try:
        capacity_text = card.find_element(By.CSS_SELECTOR, SELECTORS["venues"]["venue_capacity"]).text
    except:
        capacity_text = None

    return {
        "region": region_name,
        "name": name,
        "rating": rating,
        "no_of_reviews": reviews,
        "location": location,
        "price_text": price_text,
        "price_type": price_type,
        "capacity": capacity_text,
        "url": full_link
    }

def scrape_region(driver, region):
    """Scrape all venues from a region (pagination handled)."""
    venues = []
    base_url = region["url"]
    driver.get(base_url + "?page=1")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["venues"]["venue_list_item"]))
    )
    max_page = get_max_page(driver)

    for page in range(1, max_page + 1):
        page_url = f"{base_url}?page={page}"
        print(f"\t➡ Page {page} of {region['name']}")
        driver.get(page_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["venues"]["venue_list_item"]))
        )
        cards = driver.find_elements(By.CSS_SELECTOR, SELECTORS["venues"]["venue_list_item"])
        for card in cards:
            try:
                venue = scrape_venue_card(card, region["name"])
                venues.append(venue)
            except Exception as e:
                print(f"⚠️ Failed to scrape venue on {region['name']}: {e}")
    return venues

### for collecting  individual venue details

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

### scraping reviews

def click_all_read_more_buttons(driver, button_selector="button.app-read-more-link"):
    """
    Clicks all 'Read more' buttons to expand hidden content.
    """
    try:
        read_more_buttons = driver.find_elements(By.CSS_SELECTOR, button_selector)
        for btn in read_more_buttons:
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.2)  # Small pause to let content expand
            except Exception as click_e:
                print(f"⚠️ Couldn't click a 'Read more' button: {click_e}")
    except Exception as e:
        print(f"⚠️ Couldn't find 'Read more' buttons: {e}")

def extract_reviews(driver, review_block_selector="div.storefrontReviewsTileContent", review_text_selector="div.storefrontReviewsTileContent__description.app-reviews-tile-read-more"):
    """
    Extracts all reviews after expanding the read more buttons.
    """
    reviews = []
    try:
        review_blocks = driver.find_elements(By.CSS_SELECTOR, review_block_selector)
        for block in review_blocks:
            try:
                review_text = block.find_element(By.CSS_SELECTOR, review_text_selector).text.strip()
                reviews.append(review_text)
            except Exception as e:
                print(f"⚠️ Skipped a review block: {e}")
    except Exception as e:
        print(f"⚠️ Failed to find review blocks: {e}")

    return reviews