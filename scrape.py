import requests
from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class A16zJobsScraper:
    def __init__(self):
        """Initialize the scraper with Chrome options for headless browsing"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.base_url = "https://jobs.a16z.com"
        self.all_jobs = []
        
    def get_companies(self):
        """Get all companies from the main companies page"""
        print("Fetching companies list...")
        self.driver.get(f"{self.base_url}/companies")
        
        # Wait for the page to load
        time.sleep(3)
        
        try:
            # Wait for company elements to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get company links - adjust selectors based on actual page structure
            company_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/']")
            companies = []
            
            for element in company_elements:
                href = element.get_attribute('href')
                if href and '/jobs/' in href:
                    company_name = href.split('/jobs/')[-1]
                    if company_name and company_name not in companies:
                        companies.append(company_name)
            
            print(f"Found {len(companies)} companies")
            return companies
            
        except Exception as e:
            print(f"Error getting companies: {e}")
            return []
    
    def scrape_company_jobs(self, company_name):
        """Scrape all jobs for a specific company"""
        print(f"\nScraping jobs for {company_name}...")
        url = f"{self.base_url}/jobs/{company_name}"
        
        try:
            self.driver.get(url)
            time.sleep(3)
            
            # Wait for job listings to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Try multiple possible selectors for job listings
            job_elements = (
                soup.find_all('div', class_=lambda x: x and 'job' in x.lower()) or
                soup.find_all('a', class_=lambda x: x and 'job' in x.lower()) or
                soup.find_all('li', class_=lambda x: x and 'job' in x.lower())
            )
            
            jobs = []
            for job_element in job_elements:
                try:
                    # Extract job information - adjust based on actual HTML structure
                    job_title = job_element.find(['h2', 'h3', 'h4', 'a'])
                    job_location = job_element.find(class_=lambda x: x and ('location' in str(x).lower() or 'city' in str(x).lower()))
                    job_link = job_element.find('a')
                    
                    # Filter for SDE/Software Engineering roles
                    if job_title:
                        title_text = job_title.get_text(strip=True)
                        
                        # Keywords for software engineering roles
                        sde_keywords = [
                            'software', 'engineer', 'developer', 'sde', 'backend', 
                            'frontend', 'full stack', 'fullstack', 'full-stack'
                        ]
                        
                        if any(keyword in title_text.lower() for keyword in sde_keywords):
                            job_data = {
                                'company': company_name,
                                'title': title_text,
                                'location': job_location.get_text(strip=True) if job_location else 'Not specified',
                                'url': job_link.get('href') if job_link else url,
                                'scraped_from': url
                            }
                            
                            # Make URL absolute if it's relative
                            if job_data['url'] and not job_data['url'].startswith('http'):
                                job_data['url'] = f"{self.base_url}{job_data['url']}"
                            
                            jobs.append(job_data)
                            print(f"  Found: {title_text}")
                
                except Exception as e:
                    print(f"  Error parsing job element: {e}")
                    continue
            
            print(f"Found {len(jobs)} SDE jobs at {company_name}")
            return jobs
            
        except Exception as e:
            print(f"Error scraping {company_name}: {e}")
            return []
    
    def scrape_all_jobs(self):
        """Scrape all SDE jobs from all companies"""
        companies = self.get_companies()
        
        if not companies:
            print("No companies found. The page structure might have changed.")
            return []
        
        for company in companies:
            jobs = self.scrape_company_jobs(company)
            self.all_jobs.extend(jobs)
            time.sleep(2)  # Be respectful with rate limiting
        
        return self.all_jobs
    
    def save_to_json(self, filename='a16z_sde_jobs.json'):
        """Save scraped jobs to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_jobs, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(self.all_jobs)} jobs to {filename}")
    
    def save_to_csv(self, filename='a16z_sde_jobs.csv'):
        """Save scraped jobs to CSV file"""
        import csv
        
        if not self.all_jobs:
            print("No jobs to save")
            return
        
        keys = self.all_jobs[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.all_jobs)
        print(f"Saved {len(self.all_jobs)} jobs to {filename}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()


# Usage
if __name__ == "__main__":
    scraper = A16zJobsScraper()
    
    try:
        # Scrape all jobs
        jobs = scraper.scrape_all_jobs()
        
        # Display summary
        print(f"\n{'='*60}")
        print(f"SUMMARY: Found {len(jobs)} total SDE jobs")
        print(f"{'='*60}")
        
        # Group by company
        from collections import defaultdict
        jobs_by_company = defaultdict(int)
        for job in jobs:
            jobs_by_company[job['company']] += 1
        
        print("\nJobs by company:")
        for company, count in sorted(jobs_by_company.items(), key=lambda x: x[1], reverse=True):
            print(f"  {company}: {count} jobs")
        
        # Save results
        scraper.save_to_json()
        scraper.save_to_csv()
        
        # Print first few jobs as example
        print("\nExample jobs:")
        for job in jobs[:5]:
            print(f"\n  Company: {job['company']}")
            print(f"  Title: {job['title']}")
            print(f"  Location: {job['location']}")
            print(f"  URL: {job['url']}")
        
    finally:
        scraper.close()
