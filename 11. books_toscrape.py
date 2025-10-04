# Title: Web Scraping Books Data from books.toscrape.com
# Author: Parveen Birthaliya
# Description: This script collects all book details like title, price,
# availability, rating, and link using BeautifulSoup and saves them into a CSV file.

# I tried to explain each part of the script

# importing all the required libraries
import requests                # to send HTTP requests and get web pages
from bs4 import BeautifulSoup  # to parse HTML content
import pandas as pd            # to store data in table format and save as CSV
import time, random            # for delay between requests
from urllib.parse import urljoin  # to handle relative URLs

# this is the main website from where we will scrape data
base_url = "https://books.toscrape.com/"

# creating a session helps us reuse the same connection
session = requests.Session()

# adding a fake user-agent to look like a real browser
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0"
})

# function to extract all books from a single page
def get_books_from_page(soup):
    books = []   # list to store data of all books on one page
    
    # find all <article> tags having class 'product_pod'
    all_books = soup.find_all("article", class_="product_pod")
    
    # loop through each book
    for book in all_books:
        # getting the title from the <a> tag inside <h3>
        title = book.h3.a["title"]
        
        # getting the price
        price = book.find("p", class_="price_color").text
        
        # getting the availability text (In stock / Out of stock)
        availability = book.find("p", class_="instock availability").text.strip()
        
        # getting the rating (One, Two, Three, etc.)
        rating = book.find("p", class_="star-rating")["class"][-1]
        
        # getting the full URL of the book page
        link = urljoin(base_url, book.h3.a["href"])
        
        # store all information as a dictionary
        book_info = {
            "title": title,
            "price": price,
            "availability": availability,
            "rating": rating,
            "link": link
        }
        
        # append to list
        books.append(book_info)
    
    # return all books from that page
    return books


# function to go through all pages (pagination)
def scrape_all_books():
    page_url = base_url     # starting page
    all_books = []          # store data from all pages
    
    # continue scraping until no next page found
    while page_url:
        print("Scraping page:", page_url)
        response = session.get(page_url)
        
        # parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "lxml")
        
        # extract data from this page
        books = get_books_from_page(soup)
        all_books.extend(books)
        
        # check if there is a "next" button
        next_page = soup.select_one("li.next a")
        if next_page:
            # join the relative link with base URL
            page_url = urljoin(page_url, next_page["href"])
            
            # add delay to avoid overloading the server
            time.sleep(random.uniform(1, 2))
        else:
            page_url = None   # stop the loop
    
    return all_books


# main function (starting point)
if __name__ == "__main__":
    print("Starting scraper...")
    
    # call the function to get all book data
    data = scrape_all_books()
    
    # convert list of dictionaries to DataFrame
    df = pd.DataFrame(data)
    
    # save it as a CSV file
    df.to_csv("output/books_toscrape_data.csv", index=False, encoding="utf-8")
    
    print(f"Scraping completed. Total books found: {len(df)}")
    print("Data saved to books_toscrape_data.csv")
