# Web Scraper

A Streamlit app to scrape websites using Requests and Selenium.

## Setup

### Local (Docker)
1. Clone repo: `git clone <repo-url>`
2. Build: `docker build -t web-scraper .`
3. Run: `docker run -p 8501:8501 web-scraper`
4. Open: `http://localhost:8501`

### Local (Python)
1. Clone repo: `git clone <repo-url>`
2. Install: `pip install -r requirements.txt`
3. Install Chrome & ChromeDriver
4. Run: `streamlit run streamlit_app.py`
5. Open: `http://localhost:8501`

## Deploy on Choreo
1. Push to Git repo
2. Connect to Choreo
3. Deploy using `.choreo/component.yaml`

## Usage
- Enter URL
- Click "Scrape"
- View results