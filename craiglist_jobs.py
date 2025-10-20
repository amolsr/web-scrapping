import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

BASE_URL = "https://delhi.craigslist.org/search/jjj#search=2~gallery~0"
CSV_FILE = "output/craigslist_jobs.csv"

# Configure headless Chrome
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(BASE_URL)
time.sleep(4)
print("✅ Craigslist Jobs page loaded")

# Scroll to ensure all lazy listings load
last_height = driver.execute_script("return document.body.scrollHeight")
for i in range(3):  # scroll 3 times (adjust for more results)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Parse with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")
results = soup.select("div.cl-search-result")

print(f"🔍 Found {len(results)} listings")

os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Link", "Location", "Date", "ImageURL"])

    for res in results:
        card = res.find("div", class_="gallery-card")
        if not card:
            continue

        # Title and link
        title_tag = card.find("a", class_="posting-title")
        if not title_tag:
            title_tag = card.find("a", class_="cl-search-anchor")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"
        link = title_tag["href"] if title_tag and title_tag.has_attr("href") else "N/A"

        # Meta info (date + location)
        meta = card.find("div", class_="meta")
        date, location = "N/A", "N/A"
        if meta:
            text = meta.get_text(" ", strip=True)
            # Example: "15/10 Delhi NCR"
            parts = text.split()
            if len(parts) >= 1:
                date = parts[0]
                location = " ".join(parts[1:]) if len(parts) > 1 else "N/A"

        # Image
        img_tag = card.find("img")
        img_url = "N/A"
        if img_tag and img_tag.has_attr("src"):
            src = img_tag["src"]
            if "empty" not in src.lower():
                img_url = src

        writer.writerow([title, link, location, date, img_url])

print(f"\n✅ Scraping complete — saved {CSV_FILE}")
driver.quit()
