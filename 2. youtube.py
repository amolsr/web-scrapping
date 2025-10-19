from bs4 import BeautifulSoup  #Importing the Beautiful Soup Library
import requests				   #Importing the requests library
import time					   #Importing the time library
import csv					   #Importing the csv module

# Extracting data from YouTube
response = requests.get('https://www.youtube.com/results?search_query=vicky+kaushal')
soup = BeautifulSoup(response.text, 'lxml')
name = soup.find_all('a')[44:-60]
description = soup.find_all('div')[108:-70]
desc = []
for i in description:
	if i.get_text():
		try:
			if i.get_text().strip().split('views')[1]:
				desc.append(i.get_text().strip().split('views')[1])
		except IndexError:
			pass

final_list = []
for i in desc:
	if i not in final_list:
		final_list.append(i)

for i in final_list:
	print(i)

# Write results to CSV
output_path = 'output/youtub.csv'
try:
	with open(output_path, mode='w', encoding='utf-8', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['description'])
		for row in final_list:
			writer.writerow([row])
	print(f"Saved {len(final_list)} rows to {output_path}")
except Exception as e:
	print(f"Failed to write CSV: {e}")
