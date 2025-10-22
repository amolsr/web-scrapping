import requests
from bs4 import BeautifulSoup
import csv
import time

URL = 'https://www.flipkart.com/search?q=nokia+smartphones&sid=tyy%2C4io&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_0_10_na_na_pr&otracker1=AS_QueryStore_OrganicAutoSuggest_0_10_na_na_pr&as-pos=0&as-type=RECENT&suggestionId=nokia+smartphones&requestId=675612e2-512b-4d0e-8b75-6bdf91921d7c&as-backfill=on'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

products = []

containers = soup.find_all('div', class_='_2kHMtA')

if not containers:
    print("Could not find any product containers. Flipkart's HTML has likely changed again!")
else:
    print(f"Found {len(containers)} products on the page.")

for container in containers:
    product_data = {}

    try:
        product_data['Name'] = container.find('div', class_='_4rR01T').get_text().strip()
    except AttributeError:
        product_data['Name'] = None

    try:
        product_data['Price'] = container.find('div', class_='_30jeq3 _1_WHN1').get_text().strip()
    except AttributeError:
        product_data['Price'] = None

    try:
        product_data['Rating'] = container.find('div', class_='_3LWZlK').get_text().strip()
    except AttributeError:
        product_data['Rating'] = None

    try:
        spec_list = container.find('ul', class_='fMghEO')
        specs = [spec.get_text().strip() for spec in spec_list.find_all('li', class_='rgWa7D')]
        product_data['Description'] = ' | '.join(specs)
    except AttributeError:
        product_data['Description'] = None
    
    if product_data['Name']:
        products.append(product_data)

if products:
    fieldnames = ['Name', 'Price', 'Rating', 'Description']
    
    with open('flipkart_nokia.csv', 'w', encoding="utf-8", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        writer.writerows(products)
        
    print(f"Successfully saved {len(products)} products to flipkart_nokia.csv")
else:
    print("No products were scraped. Check the selectors.")
