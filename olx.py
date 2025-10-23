import requests
import csv
import time
import os
import random
from datetime import datetime

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "olx_listings.csv")

SESSION = requests.Session()
BASE_API = "https://www.olx.in/api/relevance/v4/search"

CATEGORIES = {
    "bikes": "378",
    "mobile_phones": "1457"
}

LIMIT = 40
MAX_BATCHES = 25
DELAY_BETWEEN_REQUESTS = (1.0, 2.5)
REQUEST_TIMEOUT = 25
MAX_TOTAL_ROWS = 1000

HEADERS = {
    "User-Agent": "OLX-Android-App/14.2.1 (Android 13)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.olx.in/",
}

def fetch_batch(category_id, offset, retries=3):
    params = {"category": category_id, "limit": LIMIT, "offset": offset}
    backoff = 1.0
    for attempt in range(1, retries + 1):
        try:
            resp = SESSION.get(BASE_API, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"  ⚠️ Attempt {attempt} failed for offset {offset}: {e}")
            if attempt == retries:
                print("    → giving up on this batch.")
                return None
            time.sleep(backoff + random.random() * 0.5)
            backoff *= 2.0
    return None

def extract_items(j, category_name):
    items = []
    data = j.get("data", []) if isinstance(j, dict) else []
    for entry in data:
        ad = entry.get("ad") or entry.get("attributes") or entry
        if not ad:
            continue

        title = ad.get("title") or ad.get("name") or ""
        price = ""
        if isinstance(ad.get("price"), dict):
            price = ad.get("price", {}).get("value", {}).get("display") or ad.get("price", {}).get("formatted")
        else:
            price = ad.get("price") or ""

        url = ad.get("url") or ad.get("slug") or ""
        if url and not url.startswith("http"):
            url = "https://www.olx.in/item/" + url

        city = ad.get("locations_resolved", {}).get("CITY_name") or ad.get("city") or ""
        created = ad.get("created_at") or ad.get("posted") or ""
        images = []

        imgs = ad.get("images") or []
        if isinstance(imgs, list):
            for im in imgs:
                if isinstance(im, dict) and im.get("url"):
                    images.append(im["url"])

        items.append({
            "Category": category_name,
            "Title": title,
            "Price": price,
            "City": city,
            "Date": created,
            "URL": url,
            "ImageURLs": " | ".join(images)
        })
    return items

def save_csv(rows):
    if not rows:
        print(" No data to save.")
        return
    keys = list(rows[0].keys())
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n Saved {len(rows)} listings to {OUTPUT_CSV} at {datetime.now().isoformat()}")

def scrape_all_categories():
    all_rows = []
    for name, cat_id in CATEGORIES.items():
        print(f"\n Scraping {name.upper()} (category {cat_id})")
        for batch_idx in range(MAX_BATCHES):
            offset = batch_idx * LIMIT
            print(f"→ Fetching offset {offset} (batch {batch_idx+1}/{MAX_BATCHES}) ...")
            j = fetch_batch(cat_id, offset)
            if not j:
                time.sleep(3 + random.uniform(0.5, 1.5))
                continue

            items = extract_items(j, name)
            if not items:
                print(" No items returned — stopping early for this category.")
                break

            all_rows.extend(items)
            print(f"   Got {len(items)} items; total so far: {len(all_rows)}")

            if len(all_rows) >= MAX_TOTAL_ROWS:
                print("   Reached total 1000 listings; stopping scraping.")
                return all_rows

            time.sleep(random.uniform(*DELAY_BETWEEN_REQUESTS))
    return all_rows

def main():
    print("Starting OLX multi-category scraper (max 1000 rows, single CSV)...")
    rows = scrape_all_categories()
    save_csv(rows)
    print("Scraping complete!")

if __name__ == "__main__":
    main()
