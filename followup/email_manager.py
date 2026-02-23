"""
Email manager for sending follow-up emails using Gmail API.
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EmailManager:
    """
    Manages follow-up emails using Gmail API.
    
    Note: For production use, you'll need to:
    1. Enable Gmail API in Google Cloud Console
    2. Download credentials.json
    3. Authenticate and get token.json
    """
    
    def __init__(self, config: Dict):
        """
        Initialize email manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.email_config = config.get('email', {})
        self.from_email = self.email_config.get('from_email', '')
        self.from_name = self.email_config.get('from_name', '')
        self.signature = self.email_config.get('signature', '')
        
        # For now, we'll use a simple SMTP approach
        # In production, integrate with Gmail API
        self.use_gmail_api = False
    
    def send_followup_email(self, to_email: str, subject: str, body: str, 
                           job_title: str = "", company: str = "") -> bool:
        """
        Send a follow-up email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            job_title: Job title (for logging)
            company: Company name (for logging)
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Add signature to body
            full_body = f"{body}\n\n{self.signature}"
            
            print(f"\n{'='*60}")
            print(f"FOLLOW-UP EMAIL (DRY RUN)")
            print(f"{'='*60}")
            print(f"To: {to_email}")
            print(f"From: {self.from_name} <{self.from_email}>")
            print(f"Subject: {subject}")
            print(f"\n{full_body}")
            print(f"{'='*60}\n")
            
            # In production, actually send the email here
            # For now, just simulate success
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def _send_via_gmail_api(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email via Gmail API.
        
        This is a placeholder for Gmail API integration.
        To implement:
        1. pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
        2. Set up OAuth 2.0 credentials
        3. Use Gmail API to send email
        """
        # TODO: Implement Gmail API integration
        pass
    
    def _send_via_smtp(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email via SMTP.
        
        This is a fallback option using SMTP.
        """
        import smtplib
        
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # For Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            # You'll need to use an app password, not your regular password
            password = os.getenv('GMAIL_APP_PASSWORD')
            if not password:
                print("Warning: GMAIL_APP_PASSWORD not set in environment")
                return False
            
            server.login(self.from_email, password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"SMTP error: {e}")
            return False
    
    def generate_recruiter_email(self, company: str, job_title: str) -> str:
        """
        Generate a generic recruiter email address.
        
        Args:
            company: Company name
            job_title: Job title
        
        Returns:
            Email address (may not be valid)
        """
        # This is a best-guess approach
        # In production, you'd want to find the actual recruiter email
        company_domain = company.lower().replace(' ', '').replace(',', '')
        
        # Common patterns
        patterns = [
            f"careers@{company_domain}.com",
            f"recruiting@{company_domain}.com",
            f"jobs@{company_domain}.com",
            f"hr@{company_domain}.com",
        ]
        
        return patterns[0]  # Return first pattern as default


if __name__ == "__main__":
    # Test the email manager
    import yaml
    
    with open("../config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    manager = EmailManager(config)
    
    # Test sending a follow-up
    success = manager.send_followup_email(
        to_email="recruiting@example.com",
        subject="Following up on Software Engineer Application",
        body="Dear Hiring Manager,\n\nI wanted to follow up on my application for the Software Engineer position...",
        job_title="Software Engineer",
        company="Example Corp"
    )
    
    print(f"Email sent: {success}")
