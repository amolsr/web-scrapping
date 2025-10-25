import requests
from bs4 import BeautifulSoup
import csv
import os
import time

URL = 'https://www.allrecipes.com/food-news-trends/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.allrecipes.com/',
    'Dnt': '1',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
    'Te': 'trailers'
}

print(f"Requesting data from {URL}...")
articles = []
seen_links = set() # To avoid duplicates

try:
    response = requests.get(URL, headers=headers, timeout=10)
    # Check if the request was successful
    response.raise_for_status() 
    print("Successfully fetched page.")

    soup = BeautifulSoup(response.text, 'lxml')

    # Find all the article containers (<a> tags with the specific class)
    containers = soup.find_all('a', class_='mntl-card-list-items')

    if not containers:
        print("No article containers found with class 'mntl-card-list-items'. Selectors might need updating.")
    else:
        print(f"Found {len(containers)} potential articles. Parsing...")
        for container in containers:
            article_data = {}

            # --- Extract Link ---
            # The container itself is the link tag, get its 'href'
            link = container.get('href')
            if not link or not link.startswith('https://www.allrecipes.com/'): # Basic check
                continue # Skip if no valid link

            # --- Extract Headline ---
            try:
                # Find the span with class 'card__title-text' inside the container
                headline_span = container.find('span', class_='card__title-text')
                if headline_span:
                    headline = headline_span.get_text(strip=True)
                else:
                    headline = None # Skip if no headline span found
            except AttributeError:
                headline = None

            # --- Store Data if Valid and New ---
            if link and headline:
                # Check if we've already added this link
                if link not in seen_links:
                    article_data['Headline'] = headline
                    article_data['Link'] = link
                    articles.append(article_data)
                    seen_links.add(link) # Add link to our set of seen links

except requests.exceptions.RequestException as e:
    print(f"Error during requests to {URL}: {e}")
except Exception as e:
    print(f"An error occurred during parsing: {e}")


# --- Save to CSV ---
if articles:
    fieldnames = ['Headline', 'Link']
    
    output_dir = 'output'
    csv_path = os.path.join(output_dir, 'allrecipes_scraper.csv')
    
    os.makedirs(output_dir, exist_ok=True) 
    
    try:
        with open(csv_path, 'w', encoding="utf-8", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(articles)
            
        print(f"\nSuccessfully saved {len(articles)} articles to {csv_path}")
    except IOError as e:
        print(f"\nError writing to CSV file {csv_path}: {e}")
else:
    print("\nNo articles were successfully scraped.")