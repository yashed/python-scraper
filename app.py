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

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Web Scraper Service")


# Request model to validate incoming URL
class ScrapeRequest(BaseModel):
    url: str


def scrape_website(url):
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
    }

    # First attempt: Try static scraping
    try:
        logger.info(f"Attempting static scrape of {url}")
        time.sleep(random.uniform(1, 3))
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text_content = soup.get_text(separator=" ", strip=True)
        if len(text_content) > 100 and not any(
            keyword in text_content.lower()
            for keyword in ["captcha", "verify you are not a bot"]
        ):
            logger.info("Successfully scraped static content")
            return text_content
    except requests.exceptions.RequestException as e:
        logger.warning(f"Static scrape failed: {str(e)}")

    # Second attempt: Selenium
    try:
        logger.info(f"Attempting dynamic scrape of {url} with Selenium")
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument(f"user-agent={ua.random}")

        # Assign unique user-data directory
        import tempfile

        chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")

        driver = webdriver.Chrome(options=chrome_options)
        try:
            time.sleep(random.uniform(1, 3))
            driver.get(url)

            # Anti-detection technique
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            text_content = soup.get_text(separator=" ", strip=True)

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


@app.post("/scrape")
async def scrape_endpoint(request: ScrapeRequest):
    """Endpoint to scrape a website given a URL."""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")

    result = scrape_website(request.url)
    print(result)
    if result.startswith("Failed to scrape"):
        raise HTTPException(status_code=500, detail=result)

    return {
        "status": "success",
        "url": request.url,
        "word_count": len(result.split()),
        "preview": result[:500] + "..." if len(result) > 500 else result,
        "full_content": result,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
