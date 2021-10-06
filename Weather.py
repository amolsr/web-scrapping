from bs4 import BeautifulSoup as bs
import requests
from time import sleep

# sending request to the website

city = input('Enter the city:\n')
url = f"https://www.google.com/search?q=weather+{city}"
content = requests.get(url).text

soup = bs(content, 'html.parser')

loc = soup.find('span',class_="BNeawe tAd8D AP7Wnd") 
print(f"Showing results for : {loc.get_text().strip()} ....") # the location in better format
sleep(2)

tem = soup.find('div', attrs={'class':"BNeawe iBp4i AP7Wnd"}).get_text() # the temperature
print(f"Temperature : {tem.strip()}")

sky = soup.find('div',attrs={'class':"BNeawe tAd8D AP7Wnd"}).get_text().strip() # it will contain the sky's report
sky = sky.split('\n')

print(f"Date and time : {sky[0]}\nSky : {sky[1]}") # printing the sky and time by indexing into the list
