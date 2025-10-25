from requests_html import AsyncHTMLSession
import csv
import nest_asyncio

nest_asyncio.apply()  

URL = "https://www.interviewbit.com/web-technology-mcq/"
OUTPUT_FILE = "web_technology_mcq.csv"

async def scrape_mcqs():
    session = AsyncHTMLSession()
    print(f"📡 Fetching and rendering: {URL}")
    r = await session.get(URL)
    await r.html.arender(timeout=40, sleep=2)  

    
    question_sections = r.html.find("section.ibpage-mcq-problems__item")
    print(f" Found {len(question_sections)} questions")

    all_rows = []

    for q in question_sections:
        # Question text
        question_tag = q.find(".ibpage-mcq-problems__header p", first=True)
        question_text = question_tag.text.strip() if question_tag else ""

        # Options
        option_tags = q.find(".ibpage-mcq-problems__options.ibpage-mcq-problems__options--v2")
        options = []
        correct_answer = ""

        for opt in option_tags:
            # Each option text is inside div.ibpage-mcq-problems__checkbox-content > p
            p_tag = opt.find(".ibpage-mcq-problems__checkbox-content p", first=True)
            text = p_tag.text.strip() if p_tag else ""
            options.append(text)

            if opt.attrs.get("data-correct") == "true":
                correct_answer = text

        # Ensure exactly 4 options
        while len(options) < 4:
            options.append("")

        all_rows.append({
            "Question": question_text,
            "Option A": options[0],
            "Option B": options[1],
            "Option C": options[2],
            "Option D": options[3],
            "Correct Answer": correct_answer
        })

    # Save to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f" Saved {len(all_rows)} questions to '{OUTPUT_FILE}'")

# Run scraper
asession = AsyncHTMLSession()
asession.run(scrape_mcqs)
