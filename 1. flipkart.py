import requests
from bs4 import BeautifulSoup
import csv
import time
import os  

BASE_URL = 'https://www.flipkart.com/search?q=nokia+smartphones&sid=tyy%2C4io&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_0_10_na_na_pr&otracker1=AS_QueryStore_OrganicAutoSuggest_0_10_na_na_pr&as-pos=0&as-type=RECENT&suggestionId=nokia+smartphones&requestId=675612e2-512b-4d0e-8b75-6bdf91921d7c&as-backfill=on'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

products = []

for page in range(1, 31):
    print(f"Scraping page {page}...")
    
    url = f"{BASE_URL}&page={page}"
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    containers = soup.find_all('div', class_='_75nlfW')
    if not containers:
        containers = soup.find_all('div', class_='_1AtVbE')

    if not containers:
        print(f"No more products found at page {page}. Stopping.")
        break

    for container in containers:
        product_data = {}

        try:
            product_data['Name'] = container.find('img', class_='_53KjZw').get('alt').strip()
        except AttributeError:
            try:
                 product_data['Name'] = container.find('img', class_='DByuf4').get('alt').strip()
            except AttributeError:
                 product_data['Name'] = None

        try:
            product_data['Price'] = container.find('div', class_='Nx9bqj _4b5DiR').get_text().strip()
        except AttributeError:
            product_data['Price'] = None

        try:
            product_data['Rating'] = container.find('div', class_='XQDdHH').get_text().strip()
        except AttributeError:
            product_data['Rating'] = None

        try:
            spec_list = container.find_all('li', class_='Wphh3N')
            specs = [spec.get_text().strip() for spec in spec_list]
            product_data['Description'] = ' | '.join(specs)
        except AttributeError:
            product_data['Description'] = None
        
        if product_data['Name']: 
            products.append(product_data)
            
    time.sleep(1)

if products:
    fieldnames = ['Name', 'Price', 'Rating', 'Description']
    
    output_dir = 'output'
    csv_path = os.path.join(output_dir, 'flipkart_nokia_latest.csv')
    
    os.makedirs(output_dir, exist_ok=True) 
    
    with open(csv_path, 'w', encoding="utf-8", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
        
    print(f"\nSuccessfully saved {len(products)} products to {csv_path}")
else:
    print("\nNo products were scraped. Check the selectors.")
