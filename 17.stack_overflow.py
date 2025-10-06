import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Fetches and parses HTML content from a URL
def get_soup(url):
    time.sleep(1.5)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers, timeout=10)
    return BeautifulSoup(response.text, "html.parser")

# Gets question links from BeautifulSoup object
def extract_question_links(soup):
    links = []
    for link in soup.find_all("a", class_="s-link", href=True):
        href = link.get('href', '')
        if href.startswith('/questions/'):
            full_url = f"https://stackoverflow.com{href}"
            if '?' not in full_url:
                full_url += "?answertab=votes#tab-top"
            if full_url not in links:
                links.append(full_url)
    return links

# Extracts question text from BeautifulSoup object
def extract_question(soup):
    question_div = soup.find("div", class_="s-prose js-post-body")
    if question_div:
        paras = question_div.find_all(['p', 'pre'])
        return ' '.join([p.get_text(strip=True) for p in paras])
    return None

# Extracts answers from BeautifulSoup object
def extract_answers(soup):
    answers = []
    answer_divs = soup.find_all("div", class_="answer")
    for answer_div in answer_divs[:1]:
        answer_body = answer_div.find("div", class_="s-prose js-post-body")
        if answer_body:
            paras = answer_body.find_all(['p', 'pre'])
            answer_text = ' '.join([p.get_text(strip=True) for p in paras])
            if answer_text:
                answers.append(answer_text)
    return answers

# Main scraping function
def scrape_stackoverflow(tag, st_page, end_page):
    all_questions = []
    all_answers = []
    question_urls = []
    for page in range(st_page, end_page + 1):
        url = f"https://stackoverflow.com/questions/tagged/{tag}?tab=votes&page={page}&pagesize=15"
        soup = get_soup(url)
        links = extract_question_links(soup)
        question_urls.extend(links)
        
    for q_url in question_urls:
        soup = get_soup(q_url)
        question = extract_question(soup)
        answers = extract_answers(soup)    
        if question:
            all_questions.append(question)
            all_answers.append(answers[0] if answers else None)
    
    return all_questions, all_answers

def save_to_csv(questions, answers, filename):
    df = pd.DataFrame({'Question': questions, 'Answer': answers})
    df.to_csv(filename, index=False, encoding='utf-8')
    return df

questions, answers = scrape_stackoverflow(tag="cpp", st_page=1, end_page=3)
df = save_to_csv(questions, answers, "stackoverflow_cpp.csv")