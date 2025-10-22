from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  #Importing the Beautiful Soup Library
import time					   #Importing the time library
import csv					   #Importing the csv module

#Define a random list of search queries
search_queries = ['hacking tutorials', 'python programming', 'data science', 'machine learning', 'artificial intelligence', 'open source contributions', 'how to be open source cobtributor', 'best programming languages 2024', 'web development tutorials', 'cybersecurity basics', 'cloud computing', 'blockchain technology', 'internet of things', 'devops practices', 'mobile app development', 'game development', 'software engineering principles', 'agile methodologies', 'big data analytics', 'virtual reality']
urls = []

#Generate YouTube search URLs for each query
for query in search_queries:
    urls.append(f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}')

# Set up Selenium WebDriver with headless Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# Set up WebDriverWait
wait = WebDriverWait(driver, 10)
# try a few common selectors for YouTube consent / close buttons
selectors = [ '#introAgreeButton', 'tp-yt-paper-button[aria-label="I agree"]', 'button[aria-label="Close"]','yt-icon-button[aria-label="Close"]']

final_list = []
# retrieve data from each URL and write it directly to CSV
with open('output/youtube.csv', mode='a', newline='', encoding='utf-8') as file: #open in append mode
	writer = csv.writer(file)
	for i in range(len(urls)):
		print(f'{i+1}/{len(urls)} : {urls[i]}')
		driver.get(urls[i])
		time.sleep(2)
		if i == 0: # handle consent only on first run
			for sel in selectors:
				try:
					btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
					btn.click()
					time.sleep(1)
					break
				except Exception: pass
		
		soup = BeautifulSoup(driver.page_source, 'lxml') # Parse the page source with BeautifulSoup
		all_videos_in_page = soup.find_all('ytd-video-renderer') # Find all video renderers on the page
		for video in all_videos_in_page:
			try:
				title = video.find('a', id='video-title')
				views = video.find('span', class_='inline-metadata-item style-scope ytd-video-meta-block') #
				channel = video.find('ytd-channel-name', id='channel-name')
				link = 'https://www.youtube.com' + title['href'] if title else 'N/A'
				
				final_list.append((title.get_text(strip=True) if title else 'N/A', 
							channel.get_text(strip=True) if channel else 'N/A',
							views.get_text(strip=True).replace('\xa0', ' ') if views else 'N/A',
							link if link else 'N/A',
							)) # Append the extracted data to the final list
				writer.writerow(list(final_list[-1])) # Write the latest entry to CSV
			except Exception as e:
				continue
driver.quit()