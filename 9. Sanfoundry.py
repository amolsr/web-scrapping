import requests
from bs4 import BeautifulSoup
f = open("sanfoundry.csv","w")
url = "https://www.sanfoundry.com/java-questions-answers-data-type-enums/"
w =0 
while True:
	r = requests.get(url)
	soup = BeautifulSoup(r.content)
	g_data = soup.find_all("div",{"class":"entry-content"})
	for i in g_data:
		f.write(i.text)
	w+=1
	print(w)
	url_ = soup.find(rel='next')
	print(url)
	url = url_.get("href")
	if url == None:
		break
print("success") 
