"""
Scheduler for managing follow-up emails.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import Database
from utils.ai_helper import AIHelper
from utils.logger import setup_logger
from followup.email_manager import EmailManager


class FollowupScheduler:
    """Manages scheduling and sending of follow-up emails."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize follow-up scheduler.
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.followup_config = self.config.get('followup', {})
        self.db = Database(self.config['database']['path'])
        self.ai_helper = AIHelper()
        self.email_manager = EmailManager(self.config)
        self.logger = setup_logger(
            level=self.config['logging']['level'],
            log_file=self.config['logging']['file'],
            console=self.config['logging']['console']
        )
    
    def schedule_followups_for_application(self, application_id: int, 
                                          resume_data: Dict):
        """
        Schedule follow-up emails for a new application.
        
        Args:
            application_id: Application database ID
            resume_data: Resume data for personalization
        """
        if not self.followup_config.get('enabled', True):
            return
        
        application = self.db.get_application(application_id)
        if not application or not application.get('applied_date'):
            return
        
        job = self.db.get_job(application['job_id'])
        if not job:
            return
        
        # Get follow-up schedule from config
        schedule = self.followup_config.get('schedule', [])
        max_followups = self.followup_config.get('max_followups_per_application', 3)
        
        applied_date = datetime.fromisoformat(application['applied_date'])
        
        for i, schedule_item in enumerate(schedule[:max_followups], 1):
            days = schedule_item.get('days', i * 2)  # Default: 2, 4, 6 days
            scheduled_date = applied_date + timedelta(days=days)
            
            # Generate follow-up email
            subject, body = self.ai_helper.generate_followup_email(
                job_data=job,
                resume_data=resume_data,
                application_date=application['applied_date'],
                attempt_number=i
            )
            
            # Add to database
            followup_data = {
                'application_id': application_id,
                'scheduled_date': scheduled_date.isoformat(),
                'status': 'pending',
                'email_subject': subject,
                'email_body': body,
                'attempt_number': i
            }
            
            self.db.add_followup(followup_data)
            self.logger.info(
                f"Scheduled follow-up #{i} for {job['title']} at {job['company']} "
                f"on {scheduled_date.strftime('%Y-%m-%d')}"
            )
    
    def send_pending_followups(self, dry_run: bool = False) -> int:
        """
        Send all pending follow-ups that are due.
        
        Args:
            dry_run: If True, don't actually send emails
        
        Returns:
            Number of follow-ups sent
        """
        current_date = datetime.now().isoformat()
        pending_followups = self.db.get_pending_followups(current_date)
        
        if not pending_followups:
            self.logger.info("No pending follow-ups to send")
            return 0
        
        self.logger.info(f"Found {len(pending_followups)} pending follow-ups")
        
        sent_count = 0
        
        for followup in pending_followups:
            try:
                job = self.db.get_job(followup['job_id'])
                
                # Generate recruiter email (in production, get actual email)
                to_email = self.email_manager.generate_recruiter_email(
                    job['company'], 
                    job['title']
                )
                
                if dry_run:
                    self.logger.info(
                        f"[DRY RUN] Would send follow-up #{followup['attempt_number']} "
                        f"for {job['title']} at {job['company']}"
                    )
                    success = True
                else:
                    # Send the email
                    success = self.email_manager.send_followup_email(
                        to_email=to_email,
                        subject=followup['email_subject'],
                        body=followup['email_body'],
                        job_title=job['title'],
                        company=job['company']
                    )
                
                if success:
                    # Update followup status
                    self.db.update_followup_status(
                        followup['id'],
                        status='sent',
                        sent_date=datetime.now().isoformat()
                    )
                    sent_count += 1
                    self.logger.info(
                        f"✅ Sent follow-up #{followup['attempt_number']} "
                        f"for {job['title']} at {job['company']}"
                    )
                else:
                    # Mark as failed
                    self.db.update_followup_status(
                        followup['id'],
                        status='failed',
                        error_message="Failed to send email"
                    )
                    
            except Exception as e:
                self.logger.error(f"Error sending follow-up {followup['id']}: {e}")
                self.db.update_followup_status(
                    followup['id'],
                    status='failed',
                    error_message=str(e)
                )
        
        return sent_count


if __name__ == "__main__":
    # Test the scheduler
    scheduler = FollowupScheduler("../config.yaml")
    
    # Send pending follow-ups (dry run)
    count = scheduler.send_pending_followups(dry_run=True)
    print(f"\nSent {count} follow-ups")
