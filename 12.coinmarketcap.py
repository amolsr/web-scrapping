import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_and_save_crypto_data():
    """
    Scrapes the top cryptocurrencies' data from CoinMarketCap
    and saves it to a CSV file.
    """
    url = 'https://coinmarketcap.com/'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        crypto_data = []
        tbody = soup.find('tbody')
        
        if not tbody:
            print("Could not find the data table. The website structure may have changed.")
            return

        rows = tbody.find_all('tr', limit=15)

        for row in rows:
            cols = row.find_all('td')
            
            if len(cols) > 9:
                try:
                    rank = cols[1].find('p').text.strip()
                    name = cols[2].find('p', class_='coin-item-name').text.strip()
                    symbol = cols[2].find('p', class_='coin-item-symbol').text.strip()
                    price = cols[3].find('span').text.strip()
                    change_1h = cols[4].find('span').text.strip()
                    change_24h = cols[5].find('span').text.strip()
                    change_7d = cols[6].find('span').text.strip()
                    market_cap_span = cols[7].find('span', {'data-nosnippet': 'true'})
                    market_cap = market_cap_span.text.strip() if market_cap_span else cols[7].text.strip()
                    volume_24h = cols[8].find('p').text.strip()
                    circulating_supply = cols[9].find('div', class_='circulating-supply-value').text.strip()

                    crypto_data.append({
                        'Rank': rank,
                        'Name': f"{name} ({symbol})",
                        'Price': price,
                        '1h %': change_1h,
                        '24h %': change_24h,
                        '7d %': change_7d,
                        'Market Cap': market_cap,
                        'Volume (24h)': volume_24h,
                        'Circulating Supply': circulating_supply
                    })
                except AttributeError:
                    continue

        df = pd.DataFrame(crypto_data)
        
        # --- CHANGE IS HERE ---
        # Define the CSV filename
        file_name = 'output/coinmarketcap.csv'
        
        # Save the DataFrame to a CSV file
        df.to_csv(file_name, index=False, encoding='utf-8')
        
        print(f"✅ Data successfully scraped and saved to '{file_name}'!")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")

if __name__ == "__main__":
    scrape_and_save_crypto_data()