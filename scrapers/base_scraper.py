"""
Base scraper class for all job platform scrapers.
Provides common functionality and interface.
"""

import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import hashlib


class BaseScraper(ABC):
    """Abstract base class for job scrapers."""
    
    def __init__(self, config: Dict):
        """
        Initialize base scraper.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.rate_limit_config = config.get('rate_limiting', {})
        self.delay = self.rate_limit_config.get('delay_between_scrapes', 3)
        self.max_retries = self.rate_limit_config.get('max_retries', 3)
        self.platform_name = self.get_platform_name()
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the platform name (e.g., 'linkedin', 'indeed')."""
        pass
    
    @abstractmethod
    def search_jobs(self, keywords: List[str], locations: List[str], 
                   **kwargs) -> List[Dict]:
        """
        Search for jobs on the platform.
        
        Args:
            keywords: List of job keywords/titles
            locations: List of locations
            **kwargs: Additional platform-specific parameters
        
        Returns:
            List of job dictionaries
        """
        pass
    
    @abstractmethod
    def get_job_details(self, job_url: str) -> Dict:
        """
        Get detailed information about a specific job.
        
        Args:
            job_url: URL of the job posting
        
        Returns:
            Dictionary with job details
        """
        pass
    
    def generate_job_id(self, job_data: Dict) -> str:
        """
        Generate a unique job ID based on job data.
        
        Args:
            job_data: Job information
        
        Returns:
            Unique job ID string
        """
        # Create unique ID from platform, company, title, and URL
        unique_string = f"{self.platform_name}_{job_data.get('company', '')}_{job_data.get('title', '')}_{job_data.get('url', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def normalize_job_data(self, raw_data: Dict) -> Dict:
        """
        Normalize job data to standard format.
        
        Args:
            raw_data: Raw job data from platform
        
        Returns:
            Normalized job data
        """
        normalized = {
            'job_id': self.generate_job_id(raw_data),
            'title': raw_data.get('title', ''),
            'company': raw_data.get('company', ''),
            'location': raw_data.get('location', ''),
            'url': raw_data.get('url', ''),
            'description': raw_data.get('description', ''),
            'requirements': raw_data.get('requirements', ''),
            'salary_range': raw_data.get('salary_range'),
            'job_type': raw_data.get('job_type'),
            'platform': self.platform_name,
            'posted_date': raw_data.get('posted_date'),
        }
        return normalized
    
    def rate_limit_delay(self):
        """Add delay between requests to avoid rate limiting."""
        # Add some randomness to appear more human-like
        delay = self.delay + random.uniform(0, 1)
        time.sleep(delay)
    
    def retry_on_failure(self, func, *args, **kwargs):
        """
        Retry a function on failure.
        
        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result or None if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"All {self.max_retries} attempts failed: {e}")
                    return None
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        text = text.replace('\x00', '')
        
        return text.strip()
    
    def extract_salary(self, text: str) -> Optional[str]:
        """
        Extract salary information from text.
        
        Args:
            text: Text containing salary info
        
        Returns:
            Extracted salary range or None
        """
        import re
        
        # Common salary patterns
        patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',  # $50,000 - $70,000
            r'\$[\d,]+k?\s*-\s*\$?[\d,]+k?',  # $50k - $70k
            r'[\d,]+\s*-\s*[\d,]+\s*(?:USD|per year|annually)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def is_recent_posting(self, posted_date_str: str, max_days: int = 30) -> bool:
        """
        Check if job posting is recent.
        
        Args:
            posted_date_str: Posted date string
            max_days: Maximum age in days
        
        Returns:
            True if recent, False otherwise
        """
        # This is a simplified check - implement proper date parsing as needed
        recent_keywords = ['today', 'yesterday', 'hour', 'hours ago', 'day ago', 'days ago']
        return any(keyword in posted_date_str.lower() for keyword in recent_keywords)
