import requests
from bs4 import BeautifulSoup
import csv
import os
import re

def scrape_wikipedia_table(url, output_filename):
    """
    Scrapes the first wikitable from a Wikipedia URL, correctly handling
    multi-row headers, irregular cells, and saves to a clean CSV file.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"Fetching data from {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'wikitable'})
        if not table:
            print("❌ Error: No table with class 'wikitable' found on the page.")
            return

        header_rows = table.find_all('tr')[:2]
        final_headers = []

        # First header row
        for th in header_rows[0].find_all('th'):
            if th.get('rowspan'):
                clean_text = re.sub(r'\[.*?\]', '', th.get_text(strip=True))
                final_headers.append(clean_text)

        # Second header row
        for th in header_rows[1].find_all('th'):
            clean_text = re.sub(r'\(.*?\)', '', th.get_text(strip=True))  # remove units like (USD millions)
            clean_text = re.sub(r'\[.*?\]', '', clean_text)
            final_headers.append(clean_text.strip())

        # --- DATA EXTRACTION ---
        data_rows = table.find_all('tr')[2:]
        table_data = []

        for row in data_rows:
            cells = row.find_all(['th', 'td'])
            if not cells:
                continue

            # Clean each cell’s text and strip footnotes
            cleaned_cells = [re.sub(r'\[.*?\]', '', c.get_text(strip=True)) for c in cells]

            # If there are fewer cells than headers, pad with empty strings
            while len(cleaned_cells) < len(final_headers):
                cleaned_cells.append('')

            # If there are extra cells, truncate
            cleaned_cells = cleaned_cells[:len(final_headers)]

            row_data = {final_headers[i]: cleaned_cells[i] for i in range(len(final_headers))}
            table_data.append(row_data)

        # --- WRITE TO CSV ---
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=final_headers)
            writer.writeheader()
            writer.writerows(table_data)

        print(f"✅ Scraping complete. Structured data saved to {output_filename}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


if __name__ == '__main__':
    WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue"
    OUTPUT_FILE = "output/wikipedia.csv"
    scrape_wikipedia_table(WIKIPEDIA_URL, OUTPUT_FILE)
