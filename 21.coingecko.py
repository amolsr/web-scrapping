"""
CoinGecko scraper script
Uses CoinGecko API to fetch cryptocurrency data
Outputs CSV to output/21.coingecko.csv
"""

import csv
import os
import sys
import requests


def fetch_coingecko_data():
    """Fetch top 750 cryptocurrencies from CoinGecko API and save to CSV."""
    base_url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,  # Max per page is 250
        "sparkline": False
    }
    
    all_data = []
    for page in range(1, 4):  # Fetch 3 pages (750 coins total)
        params["page"] = page
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            all_data.extend(data)
        except requests.exceptions.RequestException as err:
            print(f"Error fetching data on page {page}: {err}")
            sys.exit()
    
    if not all_data:
        print("No data fetched.")
        sys.exit()
    
    os.makedirs("output", exist_ok=True)
    
    csv_path = os.path.join("output", "21.coingecko.csv")  # Updated filename to match validation
    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Symbol", "Price (USD)", "Market Cap", "24h Change (%)"])
        for coin in all_data:
            writer.writerow([
                coin.get("name", "N/A"),
                coin.get("symbol", "N/A").upper(),
                coin.get("current_price", "N/A"),
                coin.get("market_cap", "N/A"),
                coin.get("price_change_percentage_24h", "N/A")
            ])
    
    print(f"Data saved to {csv_path} ({len(all_data)} coins)")


if __name__ == "__main__":
    fetch_coingecko_data()
