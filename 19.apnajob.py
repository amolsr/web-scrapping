from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv, re, time, random

def classify_detail(text):
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

def scrape_apna_playwright(base_url, max_pages=150, scroll_pause=2, max_scrolls=10):
    all_jobs_data = []
    seen_jobs = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled","--start-maximized","--disable-dev-shm-usage","--no-sandbox"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        print(f"\n🌐 Starting Apna.co scraper")
        print(f"📍 URL: {base_url}")
        failed_pages = 0
        empty_pages = 0
        current_page = 1
        
        try:
            page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(random.uniform(3, 5))
            
            while current_page <= max_pages:
                print(f"\n{'='*70}")
                print(f"📄 Page {current_page}/{max_pages}")
                print(f"{'='*70}")
                
                try:
                    page.wait_for_selector("body", timeout=10000)
                    time.sleep(random.uniform(2, 3))   # Scroll to load all content
                    
                    for i in range(max_scrolls):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(scroll_pause)     # Scroll to load all content
                        
                        if i % 3 == 0:
                            print(f"   ➤ Scrolling... {i+1}/{max_scrolls}")
                    
                    html = page.content()     # Get HTML and parse
                    soup = BeautifulSoup(html, "html.parser")
                    container = soup.select_one("body")     # Find job cards
                    job_cards = container.find_all(['div', 'article', 'li'],
                        class_=re.compile(r'job|card|item|listing|post', re.I))
                    
                    if len(job_cards) < 5:
                        job_cards = [
                            div for div in container.find_all('div', recursive=True)
                            if div.find(['h2', 'h3', 'a']) and (
                                '₹' in div.get_text() or 
                                re.search(r'\b(experience|fresher)\b', div.get_text(), re.I)
                            )
                        ]
                    
                    if len(job_cards) == 0:
                        empty_pages += 1
                        if empty_pages > 3:
                            break
                
                    page_jobs_count = 0      # Extract jobs from this page
                    
                    for card in job_cards:
                        try:
                            card_text = card.get_text(" ", strip=True)
                            
                            if len(card_text) < 20:
                                continue
                            
                            title, company, salary, location, experience = extract_job_details(card)
                            
                            job_key = f"{title}_{company}_{salary}_{location}_{experience}"
                            if job_key in seen_jobs:   # Create unique key
                                continue
                            seen_jobs.add(job_key)
                            
                            job_url = 'N/A'        # Find job URL
                            link_elem = card.find('a', href=True)
                            if link_elem:
                                href = link_elem['href']
                                if href.startswith('/'):
                                    job_url = f"https://apna.co{href}"
                                elif href.startswith('http'):
                                    job_url = href
                            
                            all_jobs_data.append({'Job Title': title,'Company Name': company,'Experience': experience,'Salary': salary,'Location': location,'URL': job_url,'Page Number': current_page})
                            page_jobs_count += 1
                            
                        except Exception as e:
                            continue
                    
                    print(f"✅ Extracted {page_jobs_count} new jobs")
                    print(f"📊 Total jobs: {len(all_jobs_data)} | Failed: {failed_pages} | Empty: {empty_pages}")
                
                    try:      # Click "Next" button to go to next page
                        next_button = None    # Try multiple selectors for the Next button
                        selectors = ["button:has-text('Next')","a:has-text('Next')","[aria-label='Next']",".pagination button:last-child","button[class*='next']"]
                        
                        for selector in selectors:
                            try:
                                next_button = page.locator(selector)
                                if next_button.count() > 0:
                                    print(f"   ➤ Found Next button with selector: {selector}")
                                    break
                            except:
                                continue
                        
                        if next_button and next_button.count() > 0:
                            is_disabled = next_button.is_disabled()
                            if is_disabled:
                                print("✅ Reached last page (Next button disabled)")
                                break
                            
                            next_button.scroll_into_view_if_needed()   
                            time.sleep(1)  
                            next_button.click()
                            print("   ➤ Clicked Next button")
                            
                            time.sleep(random.uniform(3, 5))
                            current_page += 1
                        else:
                            break
                            
                    except Exception as e:
                        break
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    failed_pages += 1
                    
                    if failed_pages > 5:  # Try to continue to next page
                        break
                    continue
                
        finally:
            browser.close()
        
        print(f"\n{'='*70}")
        print(f"🚀 Scraping completed!")
        print(f"📊 Total jobs collected: {len(all_jobs_data)}")
      
    return all_jobs_data

def save_to_csv(data, filename='apna_jobs.csv'):
    if not data:
        print("⚠️ No data to save")
        return
    
    headers = ['Job Title', 'Company Name', 'Experience', 'Salary', 'Location', 'URL', 'Page Number']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Data saved to {filename}")

if __name__ == "__main__":
    base_url = "https://apna.co/jobs/freshers-jobs?sourcePage=Home+Page"
    scraped_data = scrape_apna_playwright(base_url=base_url,max_pages=200,scroll_pause=1,max_scrolls=8)
    save_to_csv(scraped_data, filename='apna_freshers_jobs.csv')