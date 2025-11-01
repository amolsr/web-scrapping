# Web Scraping Collection 🕷️

A comprehensive collection of web scraping scripts for extracting data from popular websites. This project demonstrates various web scraping techniques using Python and provides ready-to-use scripts for data extraction.
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/f2518991-a261-4c67-95e3-43e09ff421c6" />


## 🌟 Features

- **Multiple Website Support**: Scrape data from 10+ popular websites
- **CSV Output**: All scrapers export data in CSV format for easy analysis
- **Easy to Use**: Simple Python scripts with clear documentation
- **Educational**: Perfect for learning web scraping techniques
- **Open Source**: Contribute and improve the collection

## 🚀 Quick Start

### Prerequisites

```bash
pip install requests beautifulsoup4 lxml
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/amolsr/web-scrapping.git
   cd web-scrapping
   ```

2. **Run any scraper**
   ```bash
   python scrapers/ecommerce/flipkart.py
   ```

3. **Check the output**
   ```bash
   ls output/
   ```

## 📊 Sample Output

### IMDB Top Movies
```csv
Rank,Name,Year,Rating,Link,Director
1,The Shawshank Redemption,1994,9.2,https://www.imdb.com/title/tt0111161/,Frank Darabont
2,The Godfather,1972,9.2,https://www.imdb.com/title/tt0068646/,Francis Ford Coppola
```

### Flipkart Smartphones
```csv
Mobile Name,Ratings,Pricing,Description
Nokia 8.1,4.3,₹15,999,6GB RAM | 128GB Storage
Nokia 6.1 Plus,4.2,₹12,999,4GB RAM | 64GB Storage
```

## 🛠️ Usage Examples

### Basic Usage
```python
# Run a specific scraper
python scrapers/content/imdb.py

# The script will automatically:
# 1. Fetch data from the website
# 2. Parse the HTML content
# 3. Extract relevant information
# 4. Save to CSV file in the output/ directory
```

### Customization
Each script can be easily modified to:
- Change the target URL
- Extract different data fields
- Modify the output format
- Add error handling

## 📁 Project Structure

```
web-scrapping/
├── scrapers/               # All scraper scripts organized by category
│   ├── ecommerce/          # E-commerce website scrapers
│   │   ├── flipkart.py     # Flipkart smartphone scraper
│   │   ├── amazon.py       # Amazon product scraper
│   │   └── olx.py          # OLX listings scraper
│   ├── job_boards/         # Job board scrapers
│   │   ├── indeed.py       # Indeed job listings
│   │   ├── naukri_jobs.py  # Naukri job listings
│   │   ├── apnajob.py      # ApnaJob listings
│   │   ├── jobhai.py       # JobHai listings
│   │   ├── welcome_to_the_jungle.py  # Welcome to the Jungle jobs
│   │   └── craigslist_jobs.py  # Craigslist jobs
│   ├── educational/       # Educational platform scrapers
│   │   ├── udemy.py        # Udemy course scraper
│   │   ├── sanfoundry.py   # Sanfoundry educational content
│   │   ├── college_notice_scraper.py  # College notices scraper
│   │   ├── javaguide.py    # Java Guide content
│   │   └── indiabix_networking.py  # IndiaBix networking Q&A
│   ├── social_media/       # Social media and developer platforms
│   │   ├── youtube.py       # YouTube video scraper
│   │   ├── youtube_links.py # YouTube links extractor
│   │   ├── reddit.py       # Reddit posts scraper
│   │   ├── hackernews.py   # Hacker News posts
│   │   ├── stack_overflow.py  # Stack Overflow questions
│   │   └── github.py       # GitHub repository scraper
│   ├── content/            # Content and media scrapers
│   │   ├── imdb.py         # IMDB top movies scraper
│   │   ├── books_toscrape.py  # Books.toscrape.com scraper
│   │   ├── quotes_toscrape.py  # Quotes to scrape
│   │   ├── wikipedia.py    # Wikipedia table scraper
│   │   └── openlibrary_books.py  # Open Library books
│   ├── misc/               # Miscellaneous scrapers
│   │   ├── coinmarketcap.py  # Cryptocurrency market data
│   │   ├── weather.py      # Weather information scraper
│   │   ├── craigslist_housing.py  # Craigslist housing
│   │   └── syntaxminds.py  # SyntaxMinds content
│   └── utils/              # Utility functions
│       └── __init__.py     # Helper functions for scrapers
├── output/                 # Generated CSV files
│   ├── flipkart_latest_smartphones.csv
│   ├── imdb.csv
│   ├── github.csv
│   └── ...
├── main.py                 # Main entry point
└── README.md               # This file
```

## 🔧 Dependencies

- **requests**: HTTP library for making web requests
- **beautifulsoup4**: HTML/XML parsing library
- **lxml**: XML and HTML processing library
- **csv**: Built-in CSV module for data export

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a new scraper** or improve existing ones
3. **Add proper documentation** and comments
4. **Test your changes**
5. **Submit a pull request**

### Contribution Ideas
- Add new website scrapers
- Improve error handling
- Add data validation
- Create web interface
- Add support for different output formats (JSON, XML)
- Implement rate limiting and respect robots.txt

## ⚠️ Important Notes

- **Respect robots.txt**: Always check the website's robots.txt file
- **Rate Limiting**: Add delays between requests to be respectful
- **Terms of Service**: Ensure you comply with each website's terms
- **Data Usage**: Use scraped data responsibly and ethically

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Beautiful Soup for HTML parsing
- Requests library for HTTP handling
- All contributors who help improve this collection

## 📞 Support

If you have questions or need help:
- Open an issue on GitHub
- Check the code comments for implementation details
- Review the output files for expected data format

---

**Happy Scraping! 🕷️✨**

[![Stargazers over time](https://starchart.cc/amolsr/web-scrapping.svg?variant=adaptive)](https://starchart.cc/amolsr/web-scrapping)
