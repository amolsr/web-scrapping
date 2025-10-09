# Installation required:
# pip install playwright beautifulsoup4 pandas
# playwright install chromium

import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import json
import time

class PlaywrightNaukriScraper:
    def __init__(self):
        self.browser = None
        self.page = None
        self.jobs_data = []
        
    async def setup_browser(self):
        """Setup browser with stealth settings"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with anti-detection settings
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Set to True for headless mode
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials'
            ]
        )
        
        # Create context with realistic viewport and user agent
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            color_scheme='light',
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            java_script_enabled=True
        )
        
        self.page = await context.new_page()
        
        # Add stealth scripts
        await self.page.add_init_script("""
            // Override the navigator.webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Chrome specific
            window.chrome = {
                runtime: {}
            };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
    async def intercept_api_calls(self):
        """Intercept API calls to get data directly"""
        async def handle_response(response):
            if 'jobsearchresult' in response.url or 'jobs/search' in response.url:
                try:
                    data = await response.json()
                    print(f"Intercepted API response: {response.url}")
                    # Store the intercepted data
                    self.api_data = data
                except:
                    pass
        
        self.page.on('response', handle_response)
        
    async def scrape_jobs(self, url):
        """Main scraping function"""
        print("Loading page...")
        
        # Setup API interception
        await self.intercept_api_calls()
        
        # Navigate to the page
        await self.page.goto(url, wait_until='networkidle', timeout=60000)
        
        # Wait for initial load
        await self.page.wait_for_timeout(5000)
        
        # Handle popups if any
        await self.handle_popups()
        
        # Wait for job listings
        print("Waiting for job listings...")
        try:
            await self.page.wait_for_selector('.srp-jobtuple-wrapper, .jobTuple, article[class*="job"]', 
                                             timeout=30000)
        except:
            print("Job listings not found with primary selectors, trying alternatives...")
            
        # Scroll to load all jobs
        await self.scroll_page()
        
        # Extract jobs using multiple methods
        jobs = await self.extract_jobs()
        
        return jobs
    
    async def handle_popups(self):
        """Handle any popups"""
        try:
            # Close cookie consent if present
            cookie_button = await self.page.wait_for_selector(
                'button:has-text("Accept"), button:has-text("Got it")', 
                timeout=3000
            )
            if cookie_button:
                await cookie_button.click()
                await self.page.wait_for_timeout(1000)
        except:
            pass
            
        try:
            # Close any modal dialogs
            close_button = await self.page.wait_for_selector(
                'button.close, .modal-close, [aria-label="Close"]',
                timeout=3000
            )
            if close_button:
                await close_button.click()
                await self.page.wait_for_timeout(1000)
        except:
            pass
    
    async def scroll_page(self):
        """Scroll the page to load all content"""
        print("Scrolling to load all jobs...")
        
        # Get initial scroll height
        last_height = await self.page.evaluate('document.body.scrollHeight')
        
        while True:
            # Scroll down
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            
            # Wait for new content to load
            await self.page.wait_for_timeout(2000)
            
            # Check if we've reached the bottom
            new_height = await self.page.evaluate('document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height
    
    async def extract_jobs(self):
        """Extract job data from the page"""
        print("Extracting job data...")
        
        # Method 1: Direct DOM extraction
        jobs_data = await self.page.evaluate("""
            () => {
                const jobs = [];
                
                // Try multiple selectors
                const selectors = [
                    'article.jobTuple',
                    '.srp-jobtuple-wrapper',
                    'div.jobTuple',
                    'article[class*="job"]',
                    'div[class*="job-tuple"]'
                ];
                
                let jobElements = [];
                for (const selector of selectors) {
                    jobElements = document.querySelectorAll(selector);
                    if (jobElements.length > 0) break;
                }
                
                jobElements.forEach(job => {
                    try {
                        const jobData = {};
                        
                        // Title
                        const titleElem = job.querySelector('a.title, .job-title, h2 a, .designation, .title');
                        jobData.title = titleElem ? titleElem.innerText.trim() : 'N/A';
                        jobData.url = titleElem && titleElem.href ? titleElem.href : '';
                        
                        // Company
                        const companyElem = job.querySelector('.comp-name, .company-name, .companyInfo a, a[class*="comp"]');
                        jobData.company = companyElem ? companyElem.innerText.trim() : 'N/A';
                        
                        // Experience
                        const expElem = job.querySelector('.exp, .experience, .exp-wrap, li:has(.exp-icon)');
                        jobData.experience = expElem ? expElem.innerText.trim() : 'N/A';
                        
                        // Salary
                        const salaryElem = job.querySelector('.sal, .salary, .salary-wrap, li:has(.sal-icon)');
                        jobData.salary = salaryElem ? salaryElem.innerText.trim() : 'Not Disclosed';
                        
                        // Location
                        const locationElem = job.querySelector('.loc, .location, .location-wrap, li:has(.loc-icon)');
                        jobData.location = locationElem ? locationElem.innerText.trim() : 'N/A';
                        
                        // Description
                        const descElem = job.querySelector('.job-desc, .job-description, .desc');
                        jobData.description = descElem ? descElem.innerText.trim() : 'N/A';
                        
                        // Posted date
                        const postedElem = job.querySelector('.job-post-day, .posted, span[class*="date"], .date');
                        jobData.posted = postedElem ? postedElem.innerText.trim() : 'N/A';
                        
                        // Skills
                        const skillsElem = job.querySelector('.tags, .skills, ul.tags-gt');
                        jobData.skills = skillsElem ? skillsElem.innerText.trim() : 'N/A';
                        
                        if (jobData.title !== 'N/A') {
                            jobs.push(jobData);
                        }
                    } catch (e) {
                        console.error('Error extracting job:', e);
                    }
                });
                
                return jobs;
            }
        """)
        
        return jobs_data
    
    async def save_to_csv(self, jobs_data, filename='naukri_jobs.csv'):
        """Save data to CSV"""
        if jobs_data:
            df = pd.DataFrame(jobs_data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Data saved to {filename}")
            return df
        else:
            print("No data to save")
            return None
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

# Alternative: Using API endpoints directly
async def scrape_via_api():
    """Try to access Naukri's internal API directly"""
    import aiohttp
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.naukri.com/',
        'Origin': 'https://www.naukri.com'
    }
    
    # Naukri API endpoint (might change)
    api_url = 'https://www.naukri.com/jobapi/v3/search'
    
    params = {
        'noOfResults': 20,
        'urlType': 'search_by_key_loc',
        'searchType': 'adv',
        'keyword': 'full stack developer',
        'pageNo': 1,
        'sort': 'r',
        'k': 'full stack developer'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print("Successfully accessed API!")
                    return data
                else:
                    print(f"API request failed with status: {response.status}")
                    return None
        except Exception as e:
            print(f"Error accessing API: {e}")
            return None

# Main execution
async def main():
    # Method 1: Playwright scraping
    print("Starting Playwright scraper...")
    scraper = PlaywrightNaukriScraper()
    
    try:
        await scraper.setup_browser()
        url = "https://www.naukri.com/full-stack-developer-jobs?src=popular_roles_homepage_srch"
        jobs = await scraper.scrape_jobs(url)
        
        if jobs:
            print(f"\nSuccessfully scraped {len(jobs)} jobs!")
            df = await scraper.save_to_csv(jobs)
            
            # Display sample
            for i, job in enumerate(jobs[:3], 1):
                print(f"\nJob {i}:")
                print(f"Title: {job.get('title', 'N/A')}")
                print(f"Company: {job.get('company', 'N/A')}")
                print(f"Location: {job.get('location', 'N/A')}")
        else:
            print("No jobs scraped. Trying API method...")
            
            # Method 2: Try direct API access
            api_data = await scrape_via_api()
            if api_data:
                print("API data retrieved successfully!")
                # Process API data here
    
    finally:
        await scraper.close()

# Run the scraper
if __name__ == "__main__":
    asyncio.run(main())
