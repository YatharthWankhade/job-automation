"""
LinkedIn job scraper using Playwright for browser automation.
"""

import sys
import os
from typing import List, Dict
from playwright.sync_api import sync_playwright, Page, Browser
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapers.base_scraper import BaseScraper


class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn job postings."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.browser_config = config.get('browser', {})
        self.playwright = None
        self.browser = None
        self.page = None
    
    def get_platform_name(self) -> str:
        return "linkedin"
    
    def init_browser(self):
        """Initialize Playwright browser."""
        if not self.playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.browser_config.get('headless', False)
            )
            
            # Use persistent context to maintain login session
            user_data_dir = self.browser_config.get('user_data_dir', 'browser_data/linkedin')
            os.makedirs(user_data_dir, exist_ok=True)
            
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            self.page = self.context.new_page()
    
    def close_browser(self):
        """Close browser and cleanup."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def login_if_needed(self):
        """Check if login is needed and wait for manual login."""
        self.page.goto("https://www.linkedin.com/jobs/")
        time.sleep(2)
        
        # Check if we're on login page
        if "login" in self.page.url or "authwall" in self.page.url:
            print("\n" + "="*60)
            print("LINKEDIN LOGIN REQUIRED")
            print("="*60)
            print("Please log in to LinkedIn in the browser window.")
            print("The script will continue automatically after login.")
            print("="*60 + "\n")
            
            # Wait for successful login (URL changes away from login page)
            self.page.wait_for_url(lambda url: "login" not in url and "authwall" not in url, 
                                  timeout=300000)  # 5 minutes
            print("✅ Login successful!")
            time.sleep(2)
    
    def search_jobs(self, keywords: List[str], locations: List[str], 
                   limit: int = 50, **kwargs) -> List[Dict]:
        """
        Search for jobs on LinkedIn.
        
        Args:
            keywords: List of job keywords
            locations: List of locations
            limit: Maximum number of jobs to scrape
            **kwargs: Additional parameters
        
        Returns:
            List of job dictionaries
        """
        self.init_browser()
        self.login_if_needed()
        
        jobs = []
        
        for keyword in keywords:
            for location in locations:
                print(f"\nSearching LinkedIn: {keyword} in {location}")
                
                # Build search URL
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
                
                try:
                    self.page.goto(search_url)
                    time.sleep(3)
                    
                    # Scroll to load more jobs
                    for _ in range(3):
                        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(2)
                    
                    # Find job cards
                    job_cards = self.page.query_selector_all('.job-search-card')
                    
                    for card in job_cards[:limit]:
                        if len(jobs) >= limit:
                            break
                        
                        try:
                            job_data = self._extract_job_from_card(card)
                            if job_data:
                                jobs.append(self.normalize_job_data(job_data))
                                print(f"  ✓ {job_data['title']} at {job_data['company']}")
                        except Exception as e:
                            print(f"  ✗ Error extracting job: {e}")
                            continue
                        
                        self.rate_limit_delay()
                
                except Exception as e:
                    print(f"Error searching LinkedIn: {e}")
                    continue
        
        self.close_browser()
        return jobs
    
    def _extract_job_from_card(self, card) -> Dict:
        """Extract job data from a job card element."""
        try:
            title_elem = card.query_selector('.base-search-card__title')
            company_elem = card.query_selector('.base-search-card__subtitle')
            location_elem = card.query_selector('.job-search-card__location')
            link_elem = card.query_selector('a.base-card__full-link')
            
            title = title_elem.inner_text().strip() if title_elem else ""
            company = company_elem.inner_text().strip() if company_elem else ""
            location = location_elem.inner_text().strip() if location_elem else ""
            url = link_elem.get_attribute('href') if link_elem else ""
            
            # Clean URL (remove tracking parameters)
            if '?' in url:
                url = url.split('?')[0]
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'url': url,
                'description': '',  # Will be filled by get_job_details if needed
                'requirements': '',
                'job_type': 'Full-time',  # Default
            }
        except Exception as e:
            print(f"Error extracting card data: {e}")
            return None
    
    def get_job_details(self, job_url: str) -> Dict:
        """
        Get detailed job information from job URL.
        
        Args:
            job_url: LinkedIn job URL
        
        Returns:
            Job details dictionary
        """
        self.init_browser()
        
        try:
            self.page.goto(job_url)
            time.sleep(3)
            
            # Extract description
            desc_elem = self.page.query_selector('.show-more-less-html__markup')
            description = desc_elem.inner_text() if desc_elem else ""
            
            # Extract other details
            title_elem = self.page.query_selector('h1.top-card-layout__title')
            company_elem = self.page.query_selector('.topcard__org-name-link')
            location_elem = self.page.query_selector('.topcard__flavor--bullet')
            
            job_data = {
                'title': title_elem.inner_text().strip() if title_elem else "",
                'company': company_elem.inner_text().strip() if company_elem else "",
                'location': location_elem.inner_text().strip() if location_elem else "",
                'url': job_url,
                'description': self.clean_text(description),
                'requirements': '',  # LinkedIn doesn't separate requirements
                'salary_range': self.extract_salary(description),
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error getting job details: {e}")
            return {}
        finally:
            self.close_browser()


if __name__ == "__main__":
    # Test the scraper
    import yaml
    
    with open("../config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    scraper = LinkedInScraper(config)
    jobs = scraper.search_jobs(
        keywords=["software engineer"],
        locations=["Remote"],
        limit=5
    )
    
    print(f"\nScraped {len(jobs)} jobs from LinkedIn")
    for job in jobs:
        print(f"\n{job['title']} at {job['company']}")
        print(f"Location: {job['location']}")
        print(f"URL: {job['url']}")
