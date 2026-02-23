"""
Base applicator class for automated job applications.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BaseApplicator(ABC):
    """Abstract base class for job application automation."""
    
    def __init__(self, config: Dict):
        """
        Initialize base applicator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.browser_config = config.get('browser', {})
    
    @abstractmethod
    def apply_to_job(self, job_data: Dict, resume_data: Dict, 
                    cover_letter: str) -> bool:
        """
        Apply to a job posting.
        
        Args:
            job_data: Job information
            resume_data: Resume information
            cover_letter: Generated cover letter
        
        Returns:
            True if application successful, False otherwise
        """
        pass
    
    def fill_text_field(self, page, selector: str, value: str):
        """
        Fill a text field on the page.
        
        Args:
            page: Playwright page object
            selector: CSS selector for the field
            value: Value to fill
        """
        try:
            page.fill(selector, value)
        except Exception as e:
            print(f"Error filling field {selector}: {e}")
    
    def upload_resume(self, page, file_input_selector: str, resume_path: str):
        """
        Upload resume file.
        
        Args:
            page: Playwright page object
            file_input_selector: CSS selector for file input
            resume_path: Path to resume file
        """
        try:
            page.set_input_files(file_input_selector, resume_path)
        except Exception as e:
            print(f"Error uploading resume: {e}")
    
    def click_button(self, page, selector: str):
        """
        Click a button on the page.
        
        Args:
            page: Playwright page object
            selector: CSS selector for the button
        """
        try:
            page.click(selector)
        except Exception as e:
            print(f"Error clicking button {selector}: {e}")


class SimpleApplicator(BaseApplicator):
    """
    Simple applicator that demonstrates the application process.
    
    This is a demonstration version that shows what would happen
    but doesn't actually submit applications.
    """
    
    def apply_to_job(self, job_data: Dict, resume_data: Dict, 
                    cover_letter: str, dry_run: bool = True) -> bool:
        """
        Demonstrate job application process.
        
        Args:
            job_data: Job information
            resume_data: Resume information
            cover_letter: Generated cover letter
            dry_run: If True, don't actually submit
        
        Returns:
            True if successful (or would be successful)
        """
        print(f"\n{'='*60}")
        print(f"APPLICATION {'(DRY RUN)' if dry_run else ''}")
        print(f"{'='*60}")
        print(f"Job: {job_data['title']}")
        print(f"Company: {job_data['company']}")
        print(f"Location: {job_data['location']}")
        print(f"URL: {job_data['url']}")
        print(f"\nApplicant: {resume_data.get('personal_info', {}).get('name', 'N/A')}")
        print(f"Email: {resume_data.get('personal_info', {}).get('email', 'N/A')}")
        print(f"\nCover Letter Preview:")
        print(f"{cover_letter[:300]}...")
        print(f"{'='*60}\n")
        
        if dry_run:
            print("✓ Application prepared (not submitted - dry run mode)")
            return True
        else:
            # In production, this would use browser automation to:
            # 1. Navigate to job URL
            # 2. Click "Apply" button
            # 3. Fill out application form
            # 4. Upload resume
            # 5. Submit application
            print("⚠ Actual submission not implemented yet")
            return False


if __name__ == "__main__":
    # Test the applicator
    import yaml
    
    with open("../config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    applicator = SimpleApplicator(config)
    
    job_data = {
        'title': 'Software Engineer',
        'company': 'Example Corp',
        'location': 'Remote',
        'url': 'https://example.com/jobs/123'
    }
    
    resume_data = {
        'personal_info': {
            'name': 'John Doe',
            'email': 'john@example.com'
        }
    }
    
    cover_letter = "Dear Hiring Manager,\n\nI am excited to apply..."
    
    success = applicator.apply_to_job(job_data, resume_data, cover_letter, dry_run=True)
    print(f"Application result: {success}")
