import csv
import requests
from bs4 import BeautifulSoup

# Base URL for all pages
BASE_URL = "https://www.indiabix.com/networking/networking-basics/"
OUTPUT_FILE = 'output/indiabix_networking_data.csv'
TOTAL_PAGES = 7  # known from site pagination

def scrape_page(url):
    print(f"Fetching: {url}")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    questions = soup.find_all('div', class_='bix-div-container')
    data = []

    for q in questions:
        # Extract question text
        q_text_div = q.find('div', class_='bix-td-qtxt')
        question = q_text_div.get_text(strip=True, separator=' ') if q_text_div else ''

        # Extract options
        options_div = q.find_all('div', class_='bix-td-option-val')
        options = [opt.get_text(strip=True, separator=' ') for opt in options_div]

        # Extract correct answer from hidden input
        answer_tag = q.find('input', {'class': 'jq-hdnakq'})
        correct_answer = answer_tag['value'].strip() if answer_tag else ''

        while len(options) < 4:
            options.append('')

        data.append({
            'Question': question,
            'Option A': options[0] if len(options) > 0 else '',
            'Option B': options[1] if len(options) > 1 else '',
            'Option C': options[2] if len(options) > 2 else '',
            'Option D': options[3] if len(options) > 3 else '',
            'Correct Answer': correct_answer
        })
    return data

def scrape_all_pages(output_csv):
    all_data = []

    for i in range(1, TOTAL_PAGES + 1):
        url = BASE_URL if i == 1 else f"{BASE_URL}00100{i}"
        page_data = scrape_page(url)
        all_data.extend(page_data)

    # Write all data to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)

    print(f"✅ Scraped {len(all_data)} questions from {TOTAL_PAGES} pages into '{output_csv}'.")

if __name__ == '__main__':
    scrape_all_pages(OUTPUT_FILE)
