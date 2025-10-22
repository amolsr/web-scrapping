import requests
from bs4 import BeautifulSoup
import csv
import time
import os

BASE_URL = 'https://www.flipkart.com/search?q=smartphones'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

products = []

for page in range(1, 42): 
    print(f"Scraping page {page}...")
    
    url = f"{BASE_URL}&page={page}"
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    containers = soup.find_all('div', class_='cPHDOP') 

    if not containers:
        print(f"No more products found at page {page} (or selectors are broken). Stopping.")
        break

    for container in containers:
        product_data = {}

        try:
            product_data['Name'] = container.find('div', class_='KzDlHZ').get_text().strip()
        except AttributeError:
            product_data['Name'] = None

        try:
            product_data['Price'] = container.find('div', class_='hl05eU').find('div').get_text().strip()
        except AttributeError:
            product_data['Price'] = None

        try:
            product_data['Rating'] = container.find('div', class_='XQDdHH').get_text().strip()
        except AttributeError:
            product_data['Rating'] = None

        try:
            spec_list_container = container.find('ul', class_='G4BRas')
            specs = [spec.get_text().strip() for spec in spec_list_container.find_all('li', class_='_6NESgJ')]
            product_data['Description'] = ' | '.join(specs)
        except AttributeError:
            product_data['Description'] = None
        
        if product_data['Name']: 
            products.append(product_data)
            
    time.sleep(1)

if products:
    fieldnames = ['Name', 'Price', 'Rating', 'Description']
    
    output_dir = 'output'
    csv_path = os.path.join(output_dir, 'flipkart_latest_smartphone.csv')
    
    os.makedirs(output_dir, exist_ok=True) 
    
    with open(csv_path, 'w', encoding="utf-8", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
        
    print(f"\nSuccessfully saved {len(products)} products to {csv_path}")
else:
    print("\nNo products were scraped. The selectors may need updating again.")
