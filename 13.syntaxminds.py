import requests
from bs4 import BeautifulSoup
import csv

url = "https://syntaxminds.com/spring-boot-mcq-questions/"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
questions_data = []

# --- ORIGINAL LOGIC (LIMITED to Q1–6 ONLY) ---
question_counter = 0
for span in soup.find_all('span', class_='ez-toc-section'):
    if question_counter >= 6:
        break  # Stop after capturing 6 questions (Q1–6)

    h4 = span.find_parent('h4')
    if not h4 or not h4.find('strong'):
        continue
    question_text = h4.find('strong').get_text(strip=True)

    li_parent = h4.find_parent('li')
    option_list = []
    if li_parent:
        next_ol = li_parent.find_next_sibling('ol')
        if next_ol:
            option_list = [li.get_text(strip=True) for li in next_ol.find_all('li')]
        else:
            for sibling in li_parent.find_next_siblings('li', limit=4):
                option_list.append(sibling.get_text(strip=True))

    while len(option_list) < 4:
        option_list.append("")

    # Extract answer
    answer_tag = li_parent.find_next('p', string=lambda s: s and "Answer:" in s)
    answer = ""
    if answer_tag and answer_tag.find('strong'):
        answer = answer_tag.find('strong').get_text(strip=True).replace("Answer:", "").strip()

    questions_data.append({
        "question": question_text,
        "option_A": option_list[0],
        "option_B": option_list[1],
        "option_C": option_list[2],
        "option_D": option_list[3],
        "answer": answer
    })

    question_counter += 1

# --- PATCHED LOGIC for Q7 to Q25 ---
alt_ol = soup.find('ol', start='7')

while alt_ol:
    questions = alt_ol.find_all('li', recursive=False)
    if len(questions) >= 5:
        try:
            q_text = questions[0].get_text(strip=True)
            option_list = [li.get_text(strip=True) for li in questions[1:5]]

            answer_tag = alt_ol.find_next('p', string=lambda s: s and "Answer:" in s)
            answer = ""
            if answer_tag and answer_tag.find('strong'):
                answer = answer_tag.find('strong').get_text(strip=True).replace("Answer:", "").strip()

            questions_data.append({
                "question": q_text,
                "option_A": option_list[0],
                "option_B": option_list[1],
                "option_C": option_list[2],
                "option_D": option_list[3],
                "answer": answer
            })

        except Exception as e:
            print(f"Error processing alternate question: {e}")
    alt_ol = alt_ol.find_next('ol')

# --- CSV Writing ---
with open('output/syntaxminds.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["question", "option_A", "option_B", "option_C", "option_D", "answer"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(questions_data)

print("✅ Scraping complete.")
