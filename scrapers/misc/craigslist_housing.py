import requests
import csv
import os
from pathlib import Path

API_URL = "https://sapi.craigslist.org/web/v8/postings/search/batch"
PARAMS = {
    "batch": "86-0-1080-1-1-1760780280-1760959623",
    "cacheId": "MToBDeGGMTJ3MGzbCaP0H7MvKyA59mxIYWMQPNdNPlU27pV0NtMYHupOXbJaGCt7jJ3pMG7Bbwt6Nd_psa-6nffO1gOZro27g86O1aHI_ebzLbvTxdN5Osw0LtUb29ggKsYcNNo79OPAHvkv4Kt1hBx8g3myaA",
    "lang": "en",
    "cc": "us",
}

# Get project root (go up from scrapers/misc/)
project_root = Path(__file__).parent.parent.parent
CSV_FILE = str(project_root / "output" / "craigslist_housing.csv")
Path(CSV_FILE).parent.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

print("📡 Fetching Craigslist housing data from API…")
resp = requests.get(API_URL, params=PARAMS, headers=HEADERS)
resp.raise_for_status()
json_data = resp.json()

items = json_data.get("data", {}).get("batch", [])
print(f"🏠 Found {len(items)} housing listings")

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "Title", "Price", "Slug", "Link", "ImageURLs"])

    for item in items:
        # Basic fields
        post_id = item[0] if len(item) > 0 else "N/A"
        title = item[1] if len(item) > 1 else "N/A"

        # Slug & link
        slug = None
        for entry in item:
            if isinstance(entry, list) and len(entry) >= 2 and entry[0] == 6:
                slug = entry[1]
                break
        link = f"https://delhi.craigslist.org/{slug}" if slug else "N/A"

        # Price
        price = None
        for entry in item:
            if isinstance(entry, list) and len(entry) >= 2 and entry[0] == 10:
                price = entry[1]
                break

        # Images — safer
        image_urls = []
        if len(item) > 2 and isinstance(item[2], list):
            for img_code in item[2]:
                if isinstance(img_code, str):
                    parts = img_code.split("_")
                    img_id = parts[-1]
                    image_urls.append(f"https://images.craigslist.org/{img_id}_300x300.jpg")
        image_urls_str = ", ".join(image_urls)

        writer.writerow([post_id, title, price or "N/A", slug or "N/A", link, image_urls_str])

print(f"✅ Done — saved {CSV_FILE}")
