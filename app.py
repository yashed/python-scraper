from fastapi import FastAPI, HTTPException
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
from pydantic import BaseModel
import tempfile
import os

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Web Scraper Service")

# Request model to validate incoming URL
class ScrapeRequest(BaseModel):
    url: str

def scrape_website(url: str) -> str:
    """Scrape website content using Requests or Selenium."""
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/'
    }
    
    # First attempt: Static scraping with Requests
    try:
        logger.info(f"Attempting static scrape of {url}")
        time.sleep(random.uniform(1, 3))
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)
        if len(text_content) > 100 and not any(keyword in text_content.lower() 
            for keyword in ['captcha', 'verify you are not a bot']):
            logger.info("Successfully scraped static content")
            return text_content
    except requests.exceptions.RequestException as e:
        logger.warning(f"Static scrape failed: {str(e)}")
    
    # Second attempt: Dynamic scraping with Selenium
    try:
        logger.info(f"Attempting dynamic scrape of {url} with Selenium")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(f'user-agent={ua.random}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # Use a temporary directory for user data
        temp_dir = tempfile.mkdtemp(prefix='chrome-data-')
        chrome_options.add_argument(f'--user-data-dir={temp_dir}')
        driver = webdriver.Chrome(options=chrome_options)
        try:
            time.sleep(random.uniform(1, 3))
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)
            if len(text_content) > 100:
                logger.info("Successfully scraped dynamic content")
                return text_content
            else:
                raise Exception("Content too short, possible bot detection")
        finally:
            driver.quit()
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        logger.error(f"Dynamic scrape failed: {str(e)}")
        return f"Failed to scrape {url}: {str(e)}"

@app.post("/scrape")
async def scrape_endpoint(request: ScrapeRequest):
    """Endpoint to scrape a website given a URL."""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    result = scrape_website(request.url)
    if result.startswith("Failed to scrape"):
        raise HTTPException(status_code=500, detail=result)
    
    return {
        "status": "success",
        "url": request.url,
        "word_count": len(result.split()),
        "preview": result[:500] + "..." if len(result) > 500 else result,
        "full_content": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)