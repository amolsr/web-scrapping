import requests
from bs4 import BeautifulSoup
import time
import os
import argparse
from output_manager import OutputManager

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape Flipkart for smartphone data.')
    parser.add_argument('--format', type=str, default='csv', help='Output format: csv, json, or xml')
    args = parser.parse_args()

    if products:
        output_manager = OutputManager()
        output_manager.save(products, 'flipkart_latest_smartphone', args.format)
    else:
        print("\nNo products were scraped. The selectors may need updating again.")
