from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_reviews(driver, venue_url):
    """Scrape all reviews for a venue."""
    reviews = []
    
    try:
        # Modify URL to go to reviews page
        if "/wedding-venues/" in venue_url and "_":
            url_parts = venue_url.split("/wedding-venues/")
            if len(url_parts) == 2:
                venue_path = url_parts[1]
                review_url = f"https://www.hitched.co.uk/wedding-venues/reviews/{venue_path}"
                
                # Visit the review page
                driver.get(review_url)
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.storefrontReviewsTileContent"))
                )
                
                # Find all reviews
                review_elements = driver.find_elements(By.CSS_SELECTOR, "div.storefrontReviewsTileContent__description.app-reviews-tile-read-more")
                
                for element in review_elements:
                    review_text = element.text.strip()
                    if review_text:
                        reviews.append(review_text)
            else:
                print("Unexpected URL format, skipping reviews extraction.")
        else:
            print("Unexpected URL format, skipping reviews extraction.")
            
    except Exception as e:
        print(f"Error extracting reviews: {e}")
    
    return reviews