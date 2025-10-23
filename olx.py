import requests
import csv
import time
import os
import random
from datetime import datetime

OUTPUT_DIR = "output"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "olx_listings.csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SESSION = requests.Session()

BASE_API = "https://www.olx.in/api/relevance/v4/search"

CATEGORIES = {
    "bikes": "153",
    "mobile-phones": "179",     
}

LIMIT = 40                      
DESIRED_ROWS = 180 * 10        
DELAY_BETWEEN_REQUESTS = (1.0, 2.5)
REQUEST_TIMEOUT = 25

HEADERS = {
    "User-Agent": "OLX-Android-App/14.2.1 (Android 13)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.olx.in/",
}

def fetch_batch(category_id, offset, retries=3):
    """Fetch a batch (limit items) from OLX API with retries."""
    params = {
        "category": category_id,
        "limit": LIMIT,
        "offset": offset,
    }

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

def extract_items_from_json(j):
    """Normalize the JSON structure into a list of dicts for CSV."""
    out = []
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

        url = ad.get("url") or ad.get("slug") or ad.get("external_url") or ""
        if url and not url.startswith("http"):
            url = "https://www.olx.in/item/" + url if url else url

        city = ad.get("locations_resolved", {}).get("ADMIN_LEVEL_3_name") \
               or ad.get("locations_resolved", {}).get("CITY_name") \
               or ad.get("city") or ""

        country = ad.get("locations_resolved", {}).get("COUNTRY_name") or ""
        created = ad.get("created_at") or ad.get("posted") or ""

        images = []
        imgs = ad.get("images") or ad.get("images_urls") or ad.get("photos") or []
        if isinstance(imgs, list):
            for im in imgs:
                if isinstance(im, dict):
                    urlimg = im.get("url") or im.get("s3_url") or ""
                    if urlimg:
                        images.append(urlimg)
                elif isinstance(im, str):
                    images.append(im)

        out.append({
            "Title": title,
            "Price": price,
            "City": city,
            "Country": country,
            "Date": created,
            "URL": url,
            "ImageURLs": " | ".join(images) if images else ""
        })
    return out

def save_csv(rows):
    if not rows:
        print("No rows to save.")
        return
    keys = list(rows[0].keys())
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n✅ Saved {len(rows)} listings to {OUTPUT_CSV} at {datetime.now().isoformat()}")

def main():
    print("🔎 Starting OLX bikes, mobiles, and laptops scraper...")
    all_rows = []

    for category_name, cat_id in CATEGORIES.items():
        print(f"\n🚀 Scraping category: {category_name} (cat_id={cat_id})")
        batch_idx = 0
        while len(all_rows) < DESIRED_ROWS:
            offset = batch_idx * LIMIT
            print(f"→ Fetching offset {offset} ...")
            j = fetch_batch(cat_id, offset)
            if not j:
                print("   (skipped batch due to fetch failures)")
                time.sleep(2 + random.uniform(0.5, 1.5))
                batch_idx += 1
                continue

            items = extract_items_from_json(j)
            if not items:
                print("   No items returned — stopping this category.")
                break

            all_rows.extend(items)
            print(f"   Got {len(items)} items; total so far: {len(all_rows)}")

            if len(all_rows) >= DESIRED_ROWS:
                print(f"   Reached {DESIRED_ROWS} items; stopping.")
                break

            batch_idx += 1
            time.sleep(random.uniform(*DELAY_BETWEEN_REQUESTS))

        if len(all_rows) >= DESIRED_ROWS:
            break

    save_csv(all_rows[:DESIRED_ROWS])

if __name__ == "__main__":
    main()
