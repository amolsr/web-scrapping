from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv, re, time, random

# ---------- HELPERS ---------- #
def classify_detail(text):
    """Classify text as experience, salary, or location"""
    t = text.strip()
    if not t:
        return None
    
    # Salary patterns (₹ symbol, lakh, etc.)
    if re.search(r'₹[\d,]+', t) or re.search(r'\b(lakh|per month|monthly)\b', t, re.I):
        return ('salary', t)
    
    # Experience patterns
    if re.search(r'\b(fresher|experience|exp)\b', t, re.I) or re.search(r'\b\d+(\+|-)?\s*(yrs?|years?|months?)\b', t, re.I):
        return ('experience', t)
    
    # Location patterns
    if re.search(r'\b(Bangalore|Mumbai|Delhi|Kolkata|Chennai|Hyderabad|Pune|Ahmedabad)\b', t, re.I):
        return ('location', t)
    
    # Short text likely location
    if len(t) <= 50 and not re.search(r'₹|\d+', t):
        return ('location', t)
    
    return None


def extract_job_details(job_card):
    """Extract title, company, salary, location, experience from job card"""
    title = company = salary = location = experience = 'N/A'
    
    # Extract job title
    title_elem = job_card.find(['h2', 'h3', 'a'], class_=re.compile(r'title|heading|job-title', re.I))
    if not title_elem:
        title_elem = job_card.find(['h2', 'h3'])
    if title_elem:
        title = title_elem.get_text(strip=True)
    
    # Extract company name
    company_elem = job_card.find(['span', 'div', 'p'], class_=re.compile(r'company|employer', re.I))
    if company_elem:
        company = company_elem.get_text(strip=True)
    
    # Extract salary, location, experience from all text
    all_text = job_card.get_text(" ", strip=True)
    
    # Salary extraction
    salary_match = re.search(r'₹[\d,]+(?:\s*[-–]\s*₹?[\d,]+)?(?:\s*(?:per month|monthly|lakh|LPA))?', all_text, re.I)
    if salary_match:
        salary = salary_match.group(0)
    
    # Location extraction
    location_match = re.search(r'\b(Bangalore|Mumbai|Delhi|Kolkata|Chennai|Hyderabad|Pune|Ahmedabad|NCR|Gurgaon|Noida)\b', all_text, re.I)
    if location_match:
        location = location_match.group(0)
    
    # Experience extraction
    exp_match = re.search(r'(\d+(\.\d+)?(\+|-)?\s*(yrs?|years?|months?)|fresher|no experience)', all_text, re.I)
    if exp_match:
        experience = exp_match.group(0)
    
    # Try extracting from structured elements
    for elem in job_card.find_all(['li', 'span', 'div', 'p'], recursive=True):
        txt = elem.get_text(" ", strip=True)
        if not txt or len(txt) > 150:
            continue
        
        classified = classify_detail(txt)
        if classified:
            kind, val = classified
            if kind == 'salary' and salary == 'N/A':
                salary = val
            elif kind == 'location' and location == 'N/A':
                location = val
            elif kind == 'experience' and experience == 'N/A':
                experience = val
    
    return title, company, salary, location, experience


# ---------- MAIN SCRAPER ---------- #
def scrape_jobhai_playwright(url, scroll_pause=3, max_scrolls=15):
    """Scrape JobHai driver jobs with Playwright"""
    all_jobs_data = []
    
    with sync_playwright() as p:
        # Launch browser with anti-detection measures
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        
        page = context.new_page()
        
        print(f"\n🌐 Scraping JobHai: {url}")
        
        try:
            # Navigate to the page
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(random.uniform(4, 6))
            
            # Wait for main content container
            try:
                page.wait_for_selector("#common, [class*='job'], [class*='card']", timeout=20000)
                print("✅ Page loaded successfully")
            except:
                print("⚠️ Timeout waiting for job cards")
            
            # Scroll to load all jobs
            print(f"📜 Scrolling to load all jobs...")
            prev_height = 0
            for i in range(max_scrolls):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(scroll_pause)
                
                curr_height = page.evaluate("document.body.scrollHeight")
                if curr_height == prev_height:
                    print(f"   ➤ Reached page end at scroll {i+1}")
                    break
                prev_height = curr_height
                print(f"   ➤ Scrolled {i+1}/{max_scrolls}")
            
            # Get page HTML
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            # Find job cards using multiple selectors
            container = soup.select_one("#common")
            if not container:
                container = soup.select_one("body")
            
            # Try multiple patterns to find job cards
            job_cards = container.find_all(['div', 'article'], 
                class_=re.compile(r'job|card|item|listing', re.I))
            
            if not job_cards:
                # Fallback: find divs containing job-related keywords
                job_cards = [
                    div for div in container.find_all('div', recursive=True)
                    if '₹' in div.get_text() and 
                    any(word in div.get_text().lower() for word in ['driver', 'cab', 'truck', 'delivery'])
                ]
            
            print(f"   ➤ Found {len(job_cards)} potential job cards")
            
            # Extract job details
            seen_jobs = set()  # Avoid duplicates
            
            for idx, card in enumerate(job_cards):
                try:
                    card_text = card.get_text(" ", strip=True)
                    
                    # Filter: must contain salary and job-related keywords
                    if '₹' not in card_text:
                        continue
                    
                    if not any(kw in card_text.lower() for kw in ['driver', 'cab', 'truck', 'delivery', 'transport']):
                        continue
                    
                    # Skip if too short (likely not a full job card)
                    if len(card_text) < 30:
                        continue
                    
                    # Extract details
                    title, company, salary, location, experience = extract_job_details(card)
                    
                    # Create unique key to avoid duplicates
                    job_key = f"{title}_{company}_{location}"
                    if job_key in seen_jobs:
                        continue
                    seen_jobs.add(job_key)
                    
                    # Try to find job URL
                    job_url = 'N/A'
                    link_elem = card.find('a', href=True)
                    if link_elem:
                        href = link_elem['href']
                        if href.startswith('/'):
                            job_url = f"https://www.jobhai.com{href}"
                        elif href.startswith('http'):
                            job_url = href
                    
                    all_jobs_data.append({
                        'Job Title': title,
                        'Company Name': company,
                        'Experience': experience,
                        'Salary': salary,
                        'Location': location,
                        'URL': job_url
                    })
                    
                except Exception as e:
                    print(f"   ⚠️ Error parsing job card {idx}: {e}")
                    continue
            
            print(f"✅ Extracted {len(all_jobs_data)} jobs successfully")
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
        
        finally:
            browser.close()
            print("\n🚀 Scraping completed.")
    
    return all_jobs_data


# ---------- SAVE TO CSV ---------- #
def save_to_csv(data, filename='jobhai_driver_jobs.csv'):
    """Save scraped data to CSV file"""
    if not data:
        print("⚠️ No data to save.")
        return
    
    headers = ['Job Title', 'Company Name', 'Experience', 'Salary', 'Location', 'URL']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Saved {len(data)} jobs to {filename}")


# ---------- MAIN ---------- #
if __name__ == "__main__":
    target_url = "https://www.jobhai.com/driver-jobs-cgy"
    scraped_data = scrape_jobhai_playwright(target_url)
    save_to_csv(scraped_data)