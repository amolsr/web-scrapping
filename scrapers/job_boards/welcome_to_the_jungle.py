from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

# Configure Selenium options
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')  # Without GUI
options.add_argument('--log-level=3')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

csv_file = open('output/welcome_to_the_jungle.csv', 'w', encoding='utf-8')
csv_file.write('Name,Sectors,Location,url,Number of Employees,Logo URL,Number of Job Offers\n')
driver = webdriver.Chrome()

your_location = "United States of America"  # Specify your location here
# Scraping multiple pages
for page in range(1, 35):
    url = f"https://www.welcometothejungle.com/companies?page={page}&aroundQuery={your_location.replace(' ', '%20')}"
    driver.get(url)
    time.sleep(2)
    driver.refresh()
    time.sleep(2)
    # Wait for the page to fully load (modified here)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-role='companies:thumb'][data-testid='company-card']"))
        )
    except Exception as e:
        print(f"Error loading page {page}: {e}")
        continue  # Skip to the next page on error

    # Analyze the HTML with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    companies = soup.select("article[data-role='companies:thumb'][data-testid='company-card']")

    # Extract company information
    for company in companies:
        try:
            name = company.select_one("div header a span").get_text(strip=True)
            url = "https://www.welcometothejungle.com" + company.select_one("a")['href']
            details = company.select("ul li")
            sectors = details[0].get_text(strip=True) if len(details) > 0 else "N/A"
            location = details[1].get_text(strip=True) if len(details) > 1 else "N/A"
            num_employees = details[2].get_text(strip=True) if len(details) > 2 else "N/A"
            logo = company.select_one("img")['src']
            nb_jobs = company.select_one("footer a").get_text(strip=True)
            csv_file.write(f'"{name}","{sectors}","{location}","{url}","{num_employees}","{logo}","{nb_jobs}"\n')
        except Exception as e:
            print(f"Error extracting data for a company: {e}")
    
    print(f"Page {page} done.")

# Close the driver and the CSV file
driver.quit()
csv_file.close()