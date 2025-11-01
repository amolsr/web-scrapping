from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv, re, time, random
from datetime import datetime

def classify_detail(text):   #Helpers
    """Classify text as experience, salary, or location"""
    t = text.strip()
    if not t:
        return None
    if re.search(r'₹[\d,]+', t) or re.search(r'\b(lakh|per month|monthly)\b', t, re.I):
        return ('salary', t)
    if re.search(r'\b(fresher|experience|exp)\b', t, re.I) or re.search(r'\b\d+(\+|-)?\s*(yrs?|years?|months?)\b', t, re.I):
        return ('experience', t)
    if re.search(r'\b(Bangalore|Mumbai|Delhi|Kolkata|Chennai|Hyderabad|Pune|Ahmedabad)\b', t, re.I):
        return ('location', t)
    if len(t) <= 50 and not re.search(r'₹|\d+', t):
        return ('location', t)
    return None

def extract_job_details(job_card):
    """Extract title, company, salary, location, experience from job card"""
    title = company = salary = location = experience = 'N/A'
    
    title_elem = job_card.find(['h2', 'h3', 'a'], class_=re.compile(r'title|heading|job-title', re.I))
    if not title_elem:
        title_elem = job_card.find(['h2', 'h3'])
    if title_elem:
        title = title_elem.get_text(strip=True)
    company_elem = job_card.find(['span', 'div', 'p'], class_=re.compile(r'company|employer', re.I))
    if company_elem:
        company = company_elem.get_text(strip=True)
    all_text = job_card.get_text(" ", strip=True)
    salary_match = re.search(r'₹[\d,]+(?:\s*[-–]\s*₹?[\d,]+)?(?:\s*(?:per month|monthly|lakh|LPA))?', all_text, re.I)
    if salary_match:
        salary = salary_match.group(0)
    location_match = re.search(r'\b(Bangalore|Mumbai|Delhi|Kolkata|Chennai|Hyderabad|Pune|Ahmedabad|NCR|Gurgaon|Noida)\b', all_text, re.I)
    if location_match:
        location = location_match.group(0)
    exp_match = re.search(r'(\d+(\.\d+)?(\+|-)?\s*(yrs?|years?|months?)|fresher|no experience)', all_text, re.I)
    if exp_match:
        experience = exp_match.group(0)
    
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

def generate_pagination_urls(base_pattern, start_page=1, max_pages=150):
    """Generate pagination URLs based on JobHai's pattern"""
    urls = []
    match = re.search(r'/([\w-]+)-cgy', base_pattern)   # Pattern: /driver-jobs-page-4-cgy
    if match:
        job_type = match.group(1)
        urls.append(f"https://www.jobhai.com/{job_type}-cgy")
        for page_num in range(start_page + 1, max_pages + 1):
            urls.append(f"https://www.jobhai.com/{job_type}-page-{page_num}-cgy")
    else:
        urls.append(base_pattern)
    
    return urls

def scrape_jobhai_playwright(urls_list, scroll_pause=3, max_scrolls=15):   
    all_jobs_data = []
    seen_jobs = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled", "--start-maximized","--disable-dev-shm-usage","--no-sandbox"])  
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}  )
        
        page = context.new_page()
        print(f"\n🌐 Starting JobHai scraper")
        failed_pages = 0
        empty_pages = 0
        
        for url_idx, url in enumerate(urls_list):
            print(f"\n{'='*70}")
            print(f"📄 Page {url_idx + 1}/{len(urls_list)}: {url.split('/')[-1]}")
            print(f"{'='*70}")
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(random.uniform(2, 3))
                
                try:               # Check if page loaded successfully
                    page.wait_for_selector("body", timeout=10000)
                except:
                    print("⚠️ Page load timeout - skipping")
                    failed_pages += 1
                    continue
                
                for i in range(max_scrolls):     # Quick scroll to trigger lazy loading
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(scroll_pause)
                    
                    curr_height = page.evaluate("document.body.scrollHeight")
                    
                    if curr_height < 1000:          # Stop if page is too small (likely empty or 404)
                        print(f"   ⚠️ Small page detected ({curr_height}px) - likely empty")
                        empty_pages += 1
                        break
                    
                    if i % 5 == 0:
                        print(f"   ➤ Scrolling... {i+1}/{max_scrolls}")
                
                html = page.content()          # Get HTML
                soup = BeautifulSoup(html, "html.parser")
                
                container = soup.select_one("#common") or soup.select_one("body")    # Enhanced job card detection
                
                job_cards = container.find_all(['div', 'article', 'li'],     # Multiple detection strategies
                    class_=re.compile(r'job|card|item|listing|post', re.I))
                
                if len(job_cards) < 10:
                    job_cards = [
                        div for div in container.find_all('div', recursive=True)
                        if div.find(['h2', 'h3', 'a']) and '₹' in div.get_text()]
                
                if len(job_cards) == 0:
                    empty_pages += 1
                    continue
                
                page_jobs_count = 0       # Extract jobs from this page
                
                for idx, card in enumerate(job_cards):
                    try:
                        card_text = card.get_text(" ", strip=True)
                        
                        if len(card_text) < 20 or '₹' not in card_text:
                            continue
                        
                        title, company, salary, location, experience = extract_job_details(card)
                        job_key = f"{title}_{company}_{salary}_{location}"    # Create unique key
                        if job_key in seen_jobs:
                            continue
                        seen_jobs.add(job_key)
                        job_url = 'N/A'   # Find job URL
                        link_elem = card.find('a', href=True)
                        if link_elem:
                            href = link_elem['href']
                            if href.startswith('/'):
                                job_url = f"https://www.jobhai.com{href}"
                            elif href.startswith('http'):
                                job_url = href
                        
                        all_jobs_data.append({
                            'Job Title': title,'Company Name': company,'Experience': experience,'Salary': salary,'Location': location,'URL': job_url,'Page Number': url_idx + 1 })
                        page_jobs_count += 1
                        
                    except Exception as e:
                        continue
                
                print(f"✅ Extracted {page_jobs_count} new jobs")
                print(f"📊 Total jobs: {len(all_jobs_data)} | Failed: {failed_pages} | Empty: {empty_pages}")
                if url_idx < len(urls_list) - 1:
                    delay = random.uniform(1, 2) if page_jobs_count > 0 else random.uniform(0.5, 1)
                    time.sleep(delay)
                if empty_pages > 10 and page_jobs_count == 0:    
                    print(f"\n⚠️ Stopping: {empty_pages} consecutive empty pages detected")
                    break
                
            except KeyboardInterrupt:
                print("\n⚠️ Interrupted by user. Saving data collected so far...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_pages += 1
                continue
        
        browser.close()
        print(f"🚀 Scraping completed!")
        print(f"📊 Total jobs: {len(all_jobs_data)} | Failed: {failed_pages} | Empty: {empty_pages}")
    return all_jobs_data

def save_to_csv(data, filename='jobhai_driver_jobs_100pages.csv'): # ---------- SAVE TO CSV ---------- #
    if not data:
        return
    
    headers = ['Job Title', 'Company Name', 'Experience', 'Salary', 'Location', 'URL', 'Page Number']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
if __name__ == "__main__":  
    base_url = "https://www.jobhai.com/driver-jobs-cgy"
    urls_to_scrape = generate_pagination_urls(base_url, start_page=1, max_pages=150)
    scraped_data = scrape_jobhai_playwright(urls_to_scrape, scroll_pause=1.5, max_scrolls=10)
    save_to_csv(scraped_data)