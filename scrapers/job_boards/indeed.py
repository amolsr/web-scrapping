"""
Indeed Job Scraper

NOTE: Requires Selenium to be installed:
    pip install selenium

Also requires ChromeDriver to be available in your system PATH.
Download from: https://chromedriver.chromium.org/
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def scrape_indeed_jobs():
    """
    Scrapes job listings from Indeed.com using Selenium.

    Indeed blocks standard HTTP requests, so this uses Selenium with
    a headless Chrome browser to bypass the blocking.
    """
    # Configuration
    query = 'python developer'
    location = 'Remote'
    num_jobs = 15

    # Configure Chrome to run headless (no browser window)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    # Build Indeed search URL
    search_url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&l={location.replace(' ', '+')}"

    all_jobs = []

    try:
        print(f"Searching Indeed for: {query} in {location}")
        driver.get(search_url)

        # Wait for job cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
        )

        # Find all job cards on the page
        job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")

        # Limit to requested number of jobs
        job_cards = job_cards[:num_jobs]

        print(f"Found {len(job_cards)} job listings")

        for idx, card in enumerate(job_cards, 1):
            try:
                # Extract job title
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span").text
                except:
                    title = "N/A"

                # Extract company name
                try:
                    company = card.find_element(By.CSS_SELECTOR, "span[data-testid='company-name']").text
                except:
                    company = "N/A"

                # Extract location
                try:
                    job_location = card.find_element(By.CSS_SELECTOR, "div[data-testid='text-location']").text
                except:
                    job_location = "N/A"

                # Extract salary (optional field)
                try:
                    salary = card.find_element(By.CSS_SELECTOR, "div.metadata.salary-snippet-container").text
                except:
                    salary = "Not Listed"

                # Extract job description snippet
                try:
                    description = card.find_element(By.CSS_SELECTOR, "div.job-snippet").text
                except:
                    description = "N/A"

                # Extract job link
                try:
                    link_element = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
                    job_link = link_element.get_attribute("href")
                except:
                    job_link = "N/A"

                all_jobs.append({
                    'Job Title': title,
                    'Company': company,
                    'Location': job_location,
                    'Salary': salary,
                    'Description': description,
                    'Job Link': job_link
                })

                print(f"  [{idx}/{len(job_cards)}] Scraped: {title} at {company}")

            except Exception as e:
                print(f"  Error scraping job {idx}: {e}")
                continue

    except Exception as e:
        print(f"Error during scraping: {e}")

    finally:
        # Always close the browser
        driver.quit()

    if not all_jobs:
        print("No jobs scraped. Check your search query or location.")
        return None

    # Convert to DataFrame and save
    df = pd.DataFrame(all_jobs)
    output_file = 'output/indeed.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"\n✅ Successfully scraped {len(all_jobs)} jobs!")
    print(f"📁 Saved to: {output_file}")
    print(f"\nPreview:")
    print(df.head())

    return df

if __name__ == "__main__":
    scrape_indeed_jobs()
