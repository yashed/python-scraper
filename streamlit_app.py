import streamlit as st
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_website(url):
    ua = UserAgent()
    headers = {'User-Agent': ua.random, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Referer': 'https://www.google.com/'}
    try:
        logger.info(f"Attempting static scrape of {url}")
        time.sleep(random.uniform(1, 3))
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)
        if len(text_content) > 100 and not any(keyword in text_content.lower() for keyword in ['captcha', 'verify you are not a bot']):
            logger.info("Successfully scraped static content")
            return text_content
    except requests.exceptions.RequestException as e:
        logger.warning(f"Static scrape failed: {str(e)}")
    try:
        logger.info(f"Attempting dynamic scrape of {url} with Selenium")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(f'user-agent={ua.random}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
        try:
            time.sleep(random.uniform(1, 3))
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
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
    except Exception as e:
        logger.error(f"Dynamic scrape failed: {str(e)}")
        return f"Failed to scrape {url}: {str(e)}"

def main():
    st.title("Web Scraper")
    st.write("Enter a URL to scrape its content.")
    url = st.text_input("Website URL", placeholder="https://example.com")
    if st.button("Scrape"):
        if not url:
            st.error("Please enter a valid URL.")
        else:
            with st.spinner("Scraping the website, please wait..."):
                result = scrape_website(url)
            st.subheader("Scraped Content")
            if result.startswith("Failed to scrape"):
                st.error(result)
            else:
                st.write("**Status:** Success")
                st.write(f"**URL Scraped:** {url}")
                st.write(f"**Word Count:** {len(result.split())}")
                st.write("**Preview:**")
                st.write(result[:500] + "..." if len(result) > 500 else result)
                with st.expander("View Full Content", expanded=False):
                    st.text_area("Full Scraped Text", result, height=300)

if __name__ == "__main__":
    main()