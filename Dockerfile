FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    wget unzip curl libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libxrender1 libxtst6 libxi6 \
    && rm -rf /var/lib/apt/lists/*
RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i /tmp/chrome.deb || apt-get install -f -y \
    && rm /tmp/chrome.deb
RUN CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+") \
    && wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION})/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080  # Changed to 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]