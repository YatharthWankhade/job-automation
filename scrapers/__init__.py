"""
__init__.py for scrapers package
"""

from .base_scraper import BaseScraper
from .linkedin_scraper import LinkedInScraper
from .indeed_scraper import IndeedScraper

__all__ = ['BaseScraper', 'LinkedInScraper', 'IndeedScraper']
