import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

BASE_URL = "https://delhi.craigslist.org"
CSV_FILE = "output/craigslist_housing.csv"

# Configure Selenium headless Chrome
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
print("✅ Chrome WebDriver initialized")

# Step 1: Visit main page
driver.get(BASE_URL)
time.sleep(5)
soup = BeautifulSoup(driver.page_source, "html.parser")

# Step 2: Extract all housing category links
housing_section = soup.find("div", id="hhh")
links = []
if housing_section:
    for a in housing_section.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/search/"):
            full_url = BASE_URL + href
            links.append((a.text.strip(), full_url))

print(f"🏠 Found {len(links)} housing categories:")
for name, link in links:
    print(f"   - {name}: {link}")

# Step 3: Prepare CSV file - Ensure output directory exists
os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Category", "Title", "Link", "Price", "Location", "Date", "Bedrooms", "SqFt", "ImageURL"])

    # Step 4: Visit each category and scrape
    for category, link in links:
        print(f"\n🔍 Scraping category: {category}")
        driver.get(link)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        listings = soup.find_all("div", class_="gallery-card")
        print(f"   → Found {len(listings)} listings")

        for item in listings:
            # Title & Link
            title_tag = item.find("a", class_="posting-title")
            title = title_tag.get_text(strip=True) if title_tag else "N/A"
            post_link = BASE_URL + title_tag["href"] if title_tag and title_tag.has_attr("href") else "N/A"

            # Price
            price_tag = item.find("span", class_="priceinfo")
            price = price_tag.get_text(strip=True) if price_tag else "N/A"

            # Meta info (date, location) - Fixed parsing
            meta = item.find("div", class_="meta")
            date = location = "N/A"
            if meta:
                # Extract date from span with title attribute (common in Craigslist)
                date_elem = meta.find("span", attrs={"title": True})
                if not date_elem:
                    # Fallback to time element or first text that looks like a date
                    date_elem = meta.find("time")
                date = date_elem.get_text(strip=True) if date_elem else "N/A"

                # Extract location from result-hood span (common in Craigslist)
                hood_elem = meta.find("span", class_="result-hood")
                if hood_elem:
                    location_text = hood_elem.get_text(strip=True)
                    # Remove parentheses if present
                    location = location_text.strip(" ()")
                else:
                    # Fallback: get text with spaces, remove bedrooms/sqft, take rest as location
                    text = meta.get_text(separator=" ", strip=True)
                    # Remove extracted bedrooms and sqft text
                    if 'bedrooms' in locals() and bedrooms != "N/A":
                        text = text.replace(bedrooms, "")
                    if 'sqft' in locals() and sqft != "N/A":
                        text = text.replace(sqft.replace("sqft", "ft2"), "")
                    parts = [p for p in text.split() if p]
                    if len(parts) > 1 and ("/" in parts[0] or len(parts[0]) <= 5):
                        # Assume first is date (already set), rest location
                        location = " ".join(parts[1:])
                    elif len(parts) > 0:
                        location = " ".join(parts)

            # Bedrooms & SqFt - extract after meta to use in fallback
            bedrooms_tag = item.find("span", class_="post-bedrooms")
            bedrooms = bedrooms_tag.get_text(strip=True) if bedrooms_tag else "N/A"

            sqft_tag = item.find("span", class_="post-sqft")
            sqft = sqft_tag.get_text(strip=True).replace("ft2", "sqft") if sqft_tag else "N/A"

            # Image
            img_tag = item.find("img")
            img_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else "N/A"

            # Write to CSV
            writer.writerow([category, title, post_link, price, location, date, bedrooms, sqft, img_url])

print(f"\n✅ Done scraping all categories. Data saved in {CSV_FILE}")
driver.quit()