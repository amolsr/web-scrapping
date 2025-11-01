import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract_quiz_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    quiz_data = []

    # Find all question headings
    # Questions are in <h2> tags.
    questions = soup.find_all('h2')

    for q_tag in questions:
        question_text = q_tag.get_text().strip()

        # Skip irrelevant h2 tags like "Conclusion" or "Check out..."
        if not question_text.lower().startswith(tuple(str(i) + "." for i in range(1, 31))):
            continue

        # Initialize variables for options and correct answer
        options = []
        correct_answer = ""

        # Find the next sibling elements until the next <h2> or <div> with class 'answer'
        current_element = q_tag.next_sibling
        while current_element:
            if current_element.name == 'div' and 'optioncontainer' in current_element.get('class', []):
                options.append(current_element.get_text().strip())
            elif current_element.name == 'div' and 'answer' in current_element.get('class', []):
                # This is the answer block
                answer_div = current_element
                answer_h3 = answer_div.find('h3', string='Answer:')
                if answer_h3:
                    correct_option_div = answer_h3.find_next_sibling('div', class_='optioncontainer')
                    if correct_option_div:
                        correct_answer = correct_option_div.get_text().strip()
                break # Stop processing after finding the answer block
            elif current_element.name == 'h2': # Reached the next question
                break

            current_element = current_element.next_sibling
            # Handle NavigableString (text nodes) by skipping them
            while current_element and current_element.name is None:
                current_element = current_element.next_sibling


        quiz_data.append({
            'Question': question_text,
            'Option A': options[0] if len(options) > 0 else '',
            'Option B': options[1] if len(options) > 1 else '',
            'Option C': options[2] if len(options) > 2 else '',
            'Option D': options[3] if len(options) > 3 else '',
            'Correct Answer': correct_answer
        })

    if not quiz_data:
        print("No quiz data found on the page.")
        return None

    df = pd.DataFrame(quiz_data)
    return df

# URL of the quiz page
url = "https://www.javaguides.net/2023/01/spring-boot-quiz-multiple-choice-questions.html"

# Extract data
quiz_df = extract_quiz_data(url)

if quiz_df is not None:
    # Save to CSV
    csv_filename = "output/javaguide.csv"
    quiz_df.to_csv(csv_filename, index=False)
    print(f"Successfully extracted {len(quiz_df)} questions and saved to {csv_filename}")
else:
    print("Failed to extract quiz data.")