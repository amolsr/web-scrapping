import requests
from bs4 import BeautifulSoup
import csv
import time
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.amazon.in/'
}

products = []

search_queries = ['laptops', 'smartphones', 'headphones']

for query in search_queries:
    print(f"\n--- Scraping for query: '{query}' ---")
    
    for page in range(1, 26): 
        print(f"Scraping page {page} for {query}...")
        
        url = f"https://www.amazon.in/s?k={query}&page={page}"
        
        response = requests.get(url, headers=headers)
        
        if "api-services-support@amazon.com" in response.text:
            print(f"Blocked by Amazon on page {page}. Moving to next query.")
            break 
            
        soup = BeautifulSoup(response.text, 'lxml')

        containers = soup.find_all('div', attrs={'data-component-type': 's-search-result'})

        if not containers:
            print(f"No more products found at page {page}. Moving to next query.")
            break 
        for container in containers:
            product_data = {}

            try:
                name_element = container.find('span', class_='a-text-normal')
                product_data['Name'] = name_element.get_text().strip()
            except AttributeError:
                product_data['Name'] = 'N/A'

            try:
                price_element = container.find('span', class_='a-price-whole')
                product_data['Price'] = f"₹{price_element.get_text().strip()}"
            except AttributeError:
                product_data['Price'] = 'N/A'

            try:
                rating_element = container.find('span', class_='a-icon-alt')
                product_data['Rating'] = rating_element.get_text().strip().split(' ')[0]
            except AttributeError:
                product_data['Rating'] = 'N/A'
            
            if product_data['Name'] != 'N/A':
                products.append(product_data)
                
        # Wait a bit between pages
        time.sleep(1.5)

if products:
    fieldnames = ['Name', 'Price', 'Rating']
    
    output_dir = 'output'
    csv_path = os.path.join(output_dir, 'Amazon.csv')
    
    os.makedirs(output_dir, exist_ok=True) 
    
    with open(csv_path, 'w', encoding="utf-8", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
        
    print(f"\nSuccessfully saved {len(products)} total products to {csv_path}")
else:
    print("\nNo products were scraped. Amazon may have changed its HTML or blocked the request.")
