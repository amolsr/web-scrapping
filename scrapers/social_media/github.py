from bs4 import BeautifulSoup
import requests
import csv

data = requests.get('https://github.com/explore').text
soup = BeautifulSoup(data, 'lxml')
ind = 1
with open('github.csv', 'w') as file:
    write = csv.writer(file)
    write.writerow(['S.No',
                    'Repository Name',
                    'Repository Owner',
                    'Repository Stars',
                    'Repository details',
                    'Repository URL'])
    for i in soup.find_all('article'):
        user_info = i.find_all('div', class_='px-3')
        if user_info is None or len(user_info) < 2:
            continue
        user_info = user_info[1].find(
            'div',
            class_='d-flex flex-justify-between my-3')
        if user_info is None:
            continue
        stars = user_info.find(
            'div',
            class_='d-flex flex-items-start ml-3')
        user_info = user_info.find(
            'div',
            class_='d-flex flex-auto')
        if user_info is None or stars is None:
            continue
        user_info = user_info.h1.find_all('a')
        details = i.find('div', class_='border-bottom bg-white')
        if details is None:
            continue
        details = details.find('div', class_='px-3 pt-3')
        if details is None:
            continue
        repo_details = details.div.text
        repo_stars = stars.find(
            'a',
            class_='social-count float-none').text
        write.writerow([ind,
                        user_info[1].text.strip(),
                        user_info[0].text.strip(),
                        repo_stars,
                        repo_details,
                        f"https://github.com/{user_info[0].text.strip()}/{user_info[1].text.strip()}"])
        ind += 1
