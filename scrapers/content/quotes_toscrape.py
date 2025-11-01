import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_all_quotes():
    """
    Scrapes all quotes, authors, and tags from all pages of quotes.toscrape.com
    and saves them to a CSV file.
    """
    base_url = 'https://quotes.toscrape.com'
    current_url = '/'
    all_quotes = []
    
    # This loop will continue as long as there is a 'Next' page button
    while current_url:
        # Construct the full URL to scrape
        scrape_url = base_url + current_url
        print(f"Scraping page: {scrape_url}")

        try:
            # Send a GET request to the URL
            response = requests.get(scrape_url)
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all the quote containers on the page
            quote_containers = soup.find_all('div', class_='quote')

            for quote in quote_containers:
                # Extract the text, author, and tags for each quote
                text = quote.find('span', class_='text').text.strip()
                author = quote.find('small', class_='author').text.strip()
                
                # The tags are a list, so we'll join them into a single string
                tags_list = [tag.text for tag in quote.find_all('a', class_='tag')]
                tags = ', '.join(tags_list)

                # Append the extracted data to our list
                all_quotes.append({
                    'Quote': text,
                    'Author': author,
                    'Tags': tags
                })
            
            # Find the 'Next' button to see if there's a next page
            next_li = soup.find('li', class_='next')
            current_url = next_li.find('a')['href'] if next_li else None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching {scrape_url}: {e}")
            break

    # Convert the list of quotes to a pandas DataFrame
    df = pd.DataFrame(all_quotes)
    
    # Define the CSV filename
    file_name = 'output/quotestoscrape.csv'
    
    # Save the DataFrame to a CSV file
    df.to_csv(file_name, index=False, encoding='utf-8')
    
    print(f"\n✅ Scraping complete! All quotes have been saved to '{file_name}'.")

if __name__ == "__main__":
    scrape_all_quotes()