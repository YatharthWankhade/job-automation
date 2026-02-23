"""
Indeed job scraper using requests and BeautifulSoup.
"""

import sys
import os
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapers.base_scraper import BaseScraper


class IndeedScraper(BaseScraper):
    """Scraper for Indeed job postings."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://www.indeed.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def get_platform_name(self) -> str:
        return "indeed"
    
    def search_jobs(self, keywords: List[str], locations: List[str], 
                   limit: int = 50, **kwargs) -> List[Dict]:
        """
        Search for jobs on Indeed.
        
        Args:
            keywords: List of job keywords
            locations: List of locations
            limit: Maximum number of jobs to scrape
            **kwargs: Additional parameters
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        for keyword in keywords:
            for location in locations:
                print(f"\nSearching Indeed: {keyword} in {location}")
                
                # Build search URL
                search_url = f"{self.base_url}/jobs"
                params = {
                    'q': keyword,
                    'l': location,
                    'fromage': '7',  # Last 7 days
                }
                
                try:
                    response = requests.get(search_url, params=params, headers=self.headers)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find job cards
                    job_cards = soup.find_all('div', class_='job_seen_beacon')
                    
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
                    print(f"Error searching Indeed: {e}")
                    continue
        
        return jobs
    
    def _extract_job_from_card(self, card) -> Dict:
        """Extract job data from a job card element."""
        try:
            # Title and link
            title_elem = card.find('h2', class_='jobTitle')
            title_link = title_elem.find('a') if title_elem else None
            title = title_link.get_text(strip=True) if title_link else ""
            job_key = title_link.get('data-jk', '') if title_link else ""
            url = f"{self.base_url}/viewjob?jk={job_key}" if job_key else ""
            
            # Company
            company_elem = card.find('span', {'data-testid': 'company-name'})
            company = company_elem.get_text(strip=True) if company_elem else ""
            
            # Location
            location_elem = card.find('div', {'data-testid': 'text-location'})
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Salary (if available)
            salary_elem = card.find('div', {'data-testid': 'attribute_snippet_testid'})
            salary = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Snippet/description
            snippet_elem = card.find('div', class_='job-snippet')
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'url': url,
                'description': snippet,
                'requirements': '',
                'salary_range': salary,
                'job_type': 'Full-time',
            }
        except Exception as e:
            print(f"Error extracting card data: {e}")
            return None
    
    def get_job_details(self, job_url: str) -> Dict:
        """
        Get detailed job information from job URL.
        
        Args:
            job_url: Indeed job URL
        
        Returns:
            Job details dictionary
        """
        try:
            response = requests.get(job_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1', class_='jobsearch-JobInfoHeader-title')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract company
            company_elem = soup.find('div', {'data-testid': 'inlineHeader-companyName'})
            company = company_elem.get_text(strip=True) if company_elem else ""
            
            # Extract location
            location_elem = soup.find('div', {'data-testid': 'inlineHeader-companyLocation'})
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Extract description
            desc_elem = soup.find('div', id='jobDescriptionText')
            description = desc_elem.get_text(separator='\n', strip=True) if desc_elem else ""
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'url': job_url,
                'description': self.clean_text(description),
                'requirements': '',
                'salary_range': self.extract_salary(description),
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error getting job details: {e}")
            return {}


if __name__ == "__main__":
    # Test the scraper
    import yaml
    
    with open("../config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    scraper = IndeedScraper(config)
    jobs = scraper.search_jobs(
        keywords=["python developer"],
        locations=["Remote"],
        limit=5
    )
    
    print(f"\nScraped {len(jobs)} jobs from Indeed")
    for job in jobs:
        print(f"\n{job['title']} at {job['company']}")
        print(f"Location: {job['location']}")
        print(f"URL: {job['url']}")
