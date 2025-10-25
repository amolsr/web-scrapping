"""
CoinGecko scraper script
Uses CoinGecko API to fetch cryptocurrency data
Outputs CSV to output/coingecko.csv
"""

import csv
import os
import sys
import requests


def fetch_coingecko_data():
    """Fetch top 50 cryptocurrencies from CoinGecko API and save to CSV."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"Error fetching data: {err}")
        sys.exit()

    data = response.json()
    os.makedirs("output", exist_ok=True)

    csv_path = os.path.join("output", "coingecko.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Symbol", "Price (USD)", "Market Cap", "24h Change (%)"])
        for coin in data:
            writer.writerow([
                coin.get("name", "N/A"),
                coin.get("symbol", "N/A").upper(),
                coin.get("current_price", "N/A"),
                coin.get("market_cap", "N/A"),
                coin.get("price_change_percentage_24h", "N/A")
            ])

    print(f"Data saved to {csv_path}")


if __name__ == "__main__":
    fetch_coingecko_data()
