"""
CoinGecko Cryptocurrency Scraper
Scrapes top 50 cryptocurrencies by market cap from CoinGecko.
Outputs: CSV file in output/coingecko.csv
"""

import requests
import csv
import os

# Ensure output folder exists
os.makedirs("output", exist_ok=True)

# API URL for top cryptocurrencies in USD
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1,
    "sparkline": False
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
    exit()

# Prepare CSV file
csv_file = "output/coingecko.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # Write header
    writer.writerow(["Name", "Symbol", "Current Price (USD)", "Market Cap (USD)", "24h Change (%)", "Coin URL"])
    
    # Write data
    for coin in data:
        name = coin.get("name", "N/A")
        symbol = coin.get("symbol", "N/A").upper()
        price = coin.get("current_price", "N/A")
        market_cap = coin.get("market_cap", "N/A")
        change_24h = coin.get("price_change_percentage_24h", "N/A")
        url_coin = f"https://www.coingecko.com/en/coins/{coin.get('id')}"
        writer.writerow([name, symbol, price, market_cap, change_24h, url_coin])

print(f"Successfully scraped {len(data)} cryptocurrencies. CSV saved to {csv_file}")
