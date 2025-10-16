import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

def get_driver():
    ua = UserAgent()
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")  # uncomment to run invisibly
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_apna_jobs():
    driver = get_driver()
    driver.get("https://apna.co/jobs")

    # Wait for the job container to load (example container selector)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='job-card']"))
    )

    jobs = []
    seen_titles = set()
    scroll_pause = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        cards = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='job-card']")
        for card in cards:
            try:
                title = card.find_element(By.TAG_NAME, "h3").text
            except:
                title = ""
            if title in seen_titles:
                continue
            seen_titles.add(title)
            try:
                company = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text
            except:
                company = ""
            try:
                location = card.find_element(By.CSS_SELECTOR, "[data-testid='job-location']").text
            except:
                location = ""
            try:
                salary = card.find_element(By.CSS_SELECTOR, "[data-testid='job-salary']").text
            except:
                salary = ""

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "salary": salary
            })

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(scroll_pause, scroll_pause+2))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.quit()

    df = pd.DataFrame(jobs)
    os.makedirs("../output", exist_ok=True)
    df.to_csv("../output/apna_jobs.csv", index=False)
    print(f"✅ Scraped {len(df)} jobs → ../output/apna_jobs.csv")

if __name__ == "__main__":
    scrape_apna_jobs()
