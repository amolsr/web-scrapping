from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv, re, time, random

# ---------- HELPERS ---------- #
def classify_detail(text):
    t = text.strip()
    if not t:
        return None
    if re.search(r'\b(fresher|freshers)\b', t, re.I) or re.search(r'\b\d+(\+|-)?\s*(yrs?|years?)\b', t, re.I) or re.search(r'^\d+[-–]\d+\s*(yrs?|years?)', t, re.I):
        return ('experience', t)
    if re.search(r'₹|\b(lpa|lakh|lakhs|per annum|pa\b|yearly|k\/annum|k p\.a\.)', t, re.I) or re.search(r'\d+\s*(?:-|\u2013)\s*\d+\s*(lakh|lpa|k)\b', t, re.I):
        return ('salary', t)
    if len(t) <= 60:
        return ('location', t)
    return None


def extract_exp_sal_loc_from_job(job):
    selectors = ['.exp', '.experience', '.sal', '.salary', '.loc', '.location', 'li.fleft', 'span.ellipsis', 'ul li']
    exp = salary = location = None
    for sel in selectors:
        el = job.select_one(sel)
        if el:
            txt = el.get_text(strip=True)
            for p in re.split(r'\s*\|\s*|\n|,', txt):
                classified = classify_detail(p)
                if classified:
                    kind, val = classified
                    if kind == 'experience' and not exp: exp = val
                    elif kind == 'salary' and not salary: salary = val
                    elif kind == 'location' and not location: location = val
            if exp and salary and location:
                return exp, salary, location
    for tag in job.find_all(['li', 'span', 'p', 'div'], recursive=True):
        txt = tag.get_text(" ", strip=True)
        if not txt or len(txt) > 120: continue
        classified = classify_detail(txt)
        if classified:
            kind, val = classified
            if kind == 'experience' and not exp: exp = val
            elif kind == 'salary' and not salary: salary = val
            elif kind == 'location' and not location: location = val
        if exp and salary and location: break
    return exp or 'N/A', salary or 'N/A', location or 'N/A'


# ---------- MAIN SCRAPER ---------- #
def scrape_jobs_playwright(num_pages=42):
    all_jobs_data = []
    with sync_playwright() as p:
        # 🚀 Use non-headless mode + realistic user-agent
        browser = p.chromium.launch(headless=False, args=[
            "--disable-blink-features=AutomationControlled",
            "--start-maximized"
        ])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )

        page = context.new_page()

        for page_num in range(1, num_pages + 1):
            if page_num == 1:
                url = "https://www.naukri.com/full-stack-developer-jobs?src=popular_roles_homepage_srch"
            else:
                url = f"https://www.naukri.com/full-stack-developer-jobs-{page_num}?src=popular_roles_homepage_srch"

            print(f"\n🌐 Scraping Page {page_num}: {url}")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(random.uniform(3, 5))  # Wait for JS to render job cards

                html = page.content()
                soup = BeautifulSoup(html, "html.parser")

                # Try multiple selectors
                job_cards = soup.select(
                    '.srp-jobtuple-wrapper, article.jobTuple, div.jobTuple, div[class*="job-tuple"]'
                )

                if not job_cards:
                    print("⚠️ No job cards detected, retrying after scroll...")
                    page.mouse.wheel(0, 4000)
                    time.sleep(3)
                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    job_cards = soup.select(
                        '.srp-jobtuple-wrapper, article.jobTuple, div.jobTuple, div[class*="job-tuple"]'
                    )

                if not job_cards:
                    print(f"❌ Still no job cards found on page {page_num}, skipping.")
                    continue

                print(f"   ➤ Found {len(job_cards)} jobs.")

                for job in job_cards:
                    title_elem = job.select_one('a.title, .job-title, h2 a, .designation, .title')
                    title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                    company_elem = job.select_one('.comp-name, .company-name, .companyInfo a, a[class*="comp"]')
                    company = company_elem.get_text(strip=True) if company_elem else 'N/A'
                    experience, salary, location = extract_exp_sal_loc_from_job(job)
                    tags_ul = job.select_one('ul.tags-gt, .tags, .skills')
                    if tags_ul:
                        tags_list = [li.get_text(strip=True) for li in tags_ul.find_all('li')]
                        skills = ', '.join(tags_list) if tags_list else tags_ul.get_text(" ", strip=True)
                    else:
                        skills = 'N/A'
                    job_url = title_elem['href'] if title_elem and title_elem.has_attr('href') else 'N/A'

                    all_jobs_data.append({
                        'Job Title': title,
                        'Company Name': company,
                        'Experience': experience,
                        'Salary': salary,
                        'Location': location,
                        'Skills': skills,
                        'URL': job_url
                    })

                print(f"✅ Page {page_num} done with {len(job_cards)} jobs.")
                time.sleep(random.uniform(2, 4))  # Add delay to avoid detection

            except Exception as e:
                print(f"❌ Error scraping page {page_num}: {e}")
                continue

        browser.close()
        print("\n🚀 All pages processed.")
    return all_jobs_data


# ---------- SAVE TO CSV ---------- #
def save_to_csv(data, filename='naukri_jobs.csv'):
    if not data:
        print("No data to save.")
        return
    headers = ['Job Title', 'Company Name', 'Experience', 'Salary', 'Location', 'Skills', 'URL']
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    print(f"\n✅ Saved {len(data)} jobs to {filename}")
# ---------- MAIN ---------- #
if __name__ == "__main__":
    scraped_data = scrape_jobs_playwright(num_pages=42)
    save_to_csv(scraped_data)





