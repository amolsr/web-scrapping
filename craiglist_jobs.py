import requests
import csv
import os

API_URL = "https://sapi.craigslist.org/web/v8/postings/search/full"
PARAMS = {
    "batch": "86-0-360-0-0",   # 86 = area (Delhi), 0-360 = range (first 360)
    "searchPath": "jjj",       # jjj = jobs
    "lang": "en",
    "cc": "us"
}

CSV_FILE = "output/craigslist_jobs.csv"
os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

print("Fetching data from API…")
resp = requests.get(API_URL, params=PARAMS, headers=headers)
resp.raise_for_status()
data = resp.json()

items = data.get("data", {}).get("items", [])
print(f"Found {len(items)} job listings")

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Company", "Description", "Link", "ImageURL"])

    for item in items:
        # Each 'item' is a list, not a dict
        title = next((x[1] for x in item if isinstance(x, list) and x[0] == 12), "N/A")
        company = next((x[1] for x in item if isinstance(x, list) and x[0] == 8), "N/A")
        desc = next((x[1] for x in item if isinstance(x, list) and x[0] == 7), "N/A")
        slug = next((x[1] for x in item if isinstance(x, list) and x[0] == 6), None)

        link = f"https://delhi.craigslist.org/{slug}" if slug else "N/A"

        # Extract image ID if present
        img_url = "N/A"
        for sub in item:
            if isinstance(sub, list) and sub[0] == 4:
                img_parts = sub[1].split("_")
                if len(img_parts) > 1:
                    img_id = img_parts[-1]
                    img_url = f"https://images.craigslist.org/{img_id}_300x300.jpg"
                break

        writer.writerow([title, company, desc, link, img_url])

print(f"\n✅ Scraping complete — saved {CSV_FILE}")
