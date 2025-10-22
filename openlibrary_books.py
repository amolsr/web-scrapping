"""
Outputs:
    openlibrary_books.csv

Requirements:
    pip install requests
"""

import requests
import csv
import time

BASE_URL = "https://openlibrary.org"
API_SEARCH_URL = "https://openlibrary.org/search.json"
OUTPUT_CSV = "output/openlibrary_books.csv"
USER_AGENT = "OpenLibraryScraper/1.0 (+your_email@example.com)"
CRAWL_DELAY = 1  # seconds
MAX_PAGES = 5   # Number of pages to fetch (100 results per page)


def fetch_books(page=1):
    """
    Fetch books from OpenLibrary API by page.
    """
    params = {
        "q": "the",  # generic query to get lots of books
        "page": page,
        "limit": 100
    }
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(API_SEARCH_URL, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()

def extract_book_data(doc):
    """
    Extract required fields from a book doc.
    """
    title = doc.get("title", "N/A")
    
    authors = doc.get("author_name")
    authors_str = ", ".join(authors) if authors else "N/A"
    
    subjects = doc.get("subject")
    subjects_str = ", ".join(subjects[:10]) if subjects else "N/A"  # max 10 subjects
    
    publish_year = doc.get("first_publish_year", "N/A")
    
    key = doc.get("key", "")
    link = BASE_URL + key if key else "N/A"
    
    return {
        "Title": title,
        "Author": authors_str,
        "Subjects": subjects_str,
        "PublishYear": publish_year,
        "Link": link
    }


def main():
    all_books = []
    print("[+] Starting OpenLibrary scraper...")

    for page in range(1, MAX_PAGES + 1):
        print(f"[+] Fetching page {page}...")
        try:
            data = fetch_books(page)
            docs = data.get("docs", [])
            for doc in docs:
                book = extract_book_data(doc)
                all_books.append(book)
        except Exception as e:
            print(f"  ! Failed to fetch page {page}: {e}")
        
        time.sleep(CRAWL_DELAY)  # polite delay

    if all_books:
        keys = ["Title", "Author", "Subjects", "PublishYear", "Link"]
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_books)
        print(f"[+] Saved {len(all_books)} books to {OUTPUT_CSV}")
    else:
        print("[!] No books scraped")

if __name__ == "__main__":
    main()
