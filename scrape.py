import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from fake_useragent import UserAgent
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_website(url):
    """
    Comprehensive web scraping function that handles static and dynamic pages
    with bot detection mitigation.
    
    Parameters:
    url (str): The URL of the website to scrape
    
    Returns:
    str: Text content of the webpage or error message if failed
    """
    # User agents for rotation to avoid bot detection
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/'
    }
    
    # First attempt: Try static scraping with Requests
    try:
        logger.info(f"Attempting static scrape of {url}")
        
        # Add random delay to mimic human behavior
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Check if page is static or requires JS rendering
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Basic check if content is meaningful (not just a bot trap)
        if len(text_content) > 100 and not any(keyword in text_content.lower() 
            for keyword in ['captcha', 'verify you are not a bot']):
            logger.info("Successfully scraped static content")
            return text_content
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Static scrape failed: {str(e)}")
    
    # Second attempt: Use Selenium for dynamic/JS-rendered pages
    try:
        logger.info(f"Attempting dynamic scrape of {url} with Selenium")
        
        # Configure headless Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(f'user-agent={ua.random}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize driver (assumes ChromeDriver is in PATH)
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Add random delay and load page
            time.sleep(random.uniform(1, 3))
            driver.get(url)
            
            # Wait for page to load (up to 10 seconds)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            # Scroll to load dynamic content (mimics human behavior)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))
            
            # Get page source and extract text
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Check if content is valid
            if len(text_content) > 100:
                logger.info("Successfully scraped dynamic content")
                return text_content
            else:
                raise Exception("Content too short, possible bot detection")
                
        finally:
            driver.quit()
            
    except Exception as e:
        logger.error(f"Dynamic scrape failed: {str(e)}")
        return f"Failed to scrape {url}: {str(e)}"

def main():
    # Example usage
    test_urls = [
        "https://www.linkedin.com/in/visal-vitharana-953845296/"
    ]
    
    for url in test_urls:
        print(f"\nScraping {url}")
        print("-" * 50)
        result = scrape_website(url)
        print("Content preview: ",result)
        print("-" * 50)

if __name__ == "__main__":
    main()