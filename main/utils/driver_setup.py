from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    
    # Add memory management options
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    
    # Set memory limits
    options.add_argument("--memory-pressure-off")
    options.add_argument("--js-flags=--max-old-space-size=512")
    
    # Add performance options
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # Increase page load timeout to 60 seconds
        driver.set_page_load_timeout(60)
        # Set implicit wait to 30 seconds
        driver.implicitly_wait(30)
        return driver
    except WebDriverException as e:
        print(f"Failed to initialize WebDriver: {str(e)}")
        raise