#!/usr/bin/env python3
"""
Main orchestration script for job application automation.

Usage:
    python main.py scrape [--limit N] [--dry-run]
    python main.py match [--dry-run]
    python main.py apply [--limit N] [--dry-run] [--mode auto|review]
    python main.py followup [--dry-run]
    python main.py stats
    python main.py review
    python main.py run-all [--limit N] [--dry-run]
"""

import argparse
import yaml
import os
import sys
from datetime import datetime

from utils.database import Database
from utils.logger import setup_logger
from utils.ai_helper import AIHelper
from matcher.resume_parser import ResumeParser
from matcher.job_matcher import JobMatcher
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.indeed_scraper import IndeedScraper
from applicator.base_applicator import SimpleApplicator
from followup.scheduler import FollowupScheduler


class JobAutomation:
    """Main orchestration class for job application automation."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize job automation system."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.db = Database(self.config['database']['path'])
        self.logger = setup_logger(
            level=self.config['logging']['level'],
            log_file=self.config['logging']['file'],
            console=self.config['logging']['console']
        )
        self.ai_helper = AIHelper(model_name=self.config['matching']['gemini_model'])
        
        # Load resume data
        self.resume_parser = ResumeParser()
        self.resume_data = self._load_resume_data()
    
    def _load_resume_data(self):
        """Load resume data from configured source."""
        resume_config = self.config.get('resume', {})
        data_file = resume_config.get('data_file', 'resume_data.json')
        
        if os.path.exists(data_file):
            return self.resume_parser.load_resume_data(data_file)
        else:
            self.logger.warning(f"Resume data file not found: {data_file}")
            return {}
    
    def scrape_jobs(self, limit: int = 50, dry_run: bool = False):
        """
        Scrape jobs from configured platforms.
        
        Args:
            limit: Maximum number of jobs to scrape per platform
            dry_run: If True, don't save to database
        """
        self.logger.info("Starting job scraping...")
        
        search_config = self.config.get('search', {})
        keywords = search_config.get('keywords', [])
        locations = search_config.get('locations', [])
        platforms = self.config.get('platforms', {}).get('enabled', [])
        
        total_scraped = 0
        
        for platform in platforms:
            try:
                if platform == 'linkedin':
                    scraper = LinkedInScraper(self.config)
                elif platform == 'indeed':
                    scraper = IndeedScraper(self.config)
                else:
                    self.logger.warning(f"Unknown platform: {platform}")
                    continue
                
                self.logger.info(f"Scraping {platform}...")
                jobs = scraper.search_jobs(keywords, locations, limit=limit)
                
                if not dry_run:
                    # Save to database
                    for job in jobs:
                        job_id = self.db.add_job(job)
                        if job_id:
                            total_scraped += 1
                        else:
                            self.logger.debug(f"Duplicate job skipped: {job['title']}")
                else:
                    total_scraped += len(jobs)
                
            except Exception as e:
                self.logger.error(f"Error scraping {platform}: {e}")
        
        self.logger.info(f"Scraped {total_scraped} new jobs")
        return total_scraped
    
    def match_jobs(self, dry_run: bool = False):
        """
        Match scraped jobs with resume.
        
        Args:
            dry_run: If True, don't save to database
        """
        self.logger.info("Starting job matching...")
        
        matcher = JobMatcher(config_path="config.yaml")
        matched_jobs = matcher.match_jobs(self.resume_data, dry_run=dry_run)
        
        self.logger.info(f"Matched {len(matched_jobs)} jobs")
        return matched_jobs
    
    def apply_to_jobs(self, limit: int = None, dry_run: bool = True, mode: str = None):
        """
        Apply to matched jobs.
        
        Args:
            limit: Maximum number of applications to submit
            dry_run: If True, don't actually submit applications
            mode: Override application mode (auto/review)
        """
        self.logger.info("Starting job applications...")
        
        # Get applications ready to apply
        if mode == 'auto' or not mode:
            # Get auto-apply applications
            applications = self.db.get_pending_applications()
        else:
            applications = []
        
        if limit:
            applications = applications[:limit]
        
        applicator = SimpleApplicator(self.config)
        followup_scheduler = FollowupScheduler("config.yaml")
        
        applied_count = 0
        
        for app in applications:
            try:
                job = self.db.get_job(app['job_id'])
                
                # Generate cover letter
                cover_letter = self.ai_helper.generate_cover_letter(
                    job_data=job,
                    resume_data=self.resume_data,
                    match_rationale=app.get('match_rationale', '')
                )
                
                # Apply to job
                success = applicator.apply_to_job(
                    job_data=job,
                    resume_data=self.resume_data,
                    cover_letter=cover_letter,
                    dry_run=dry_run
                )
                
                if success:
                    if not dry_run:
                        # Update application status
                        self.db.update_application_status(
                            app['id'],
                            status='applied',
                            notes=f"Applied on {datetime.now().isoformat()}"
                        )
                        
                        # Schedule follow-ups
                        followup_scheduler.schedule_followups_for_application(
                            app['id'],
                            self.resume_data
                        )
                    
                    applied_count += 1
                    self.logger.info(f"✅ Applied to {job['title']} at {job['company']}")
                
            except Exception as e:
                self.logger.error(f"Error applying to job: {e}")
        
        self.logger.info(f"Applied to {applied_count} jobs")
        return applied_count
    
    def send_followups(self, dry_run: bool = True):
        """
        Send pending follow-up emails.
        
        Args:
            dry_run: If True, don't actually send emails
        """
        self.logger.info("Sending follow-up emails...")
        
        scheduler = FollowupScheduler("config.yaml")
        count = scheduler.send_pending_followups(dry_run=dry_run)
        
        self.logger.info(f"Sent {count} follow-ups")
        return count
    
    def show_statistics(self):
        """Display statistics about the automation."""
        stats = self.db.get_statistics()
        
        print("\n" + "="*60)
        print("JOB APPLICATION AUTOMATION STATISTICS")
        print("="*60)
        print(f"Total Jobs Scraped: {stats['total_jobs']}")
        print(f"Total Applications: {stats['total_applications']}")
        print(f"Average Match Score: {stats['avg_match_score']}%")
        print(f"Pending Follow-ups: {stats['pending_followups']}")
        print("\nApplications by Status:")
        for status, count in stats.get('applications_by_status', {}).items():
            print(f"  {status}: {count}")
        print("="*60 + "\n")
    
    def review_queue(self):
        """Show applications in review queue."""
        applications = self.db.get_pending_applications()
        
        if not applications:
            print("\n✓ No applications in review queue\n")
            return
        
        print(f"\n{'='*60}")
        print(f"REVIEW QUEUE ({len(applications)} applications)")
        print(f"{'='*60}\n")
        
        for i, app in enumerate(applications, 1):
            print(f"{i}. {app['title']} at {app['company']}")
            print(f"   Match Score: {app['match_score']}%")
            print(f"   URL: {app['url']}")
            print(f"   Rationale: {app['match_rationale'][:100]}...")
            print()
        
        print(f"{'='*60}\n")
        print("To approve applications, use: python main.py apply --mode review")
    
    def run_full_pipeline(self, limit: int = 10, dry_run: bool = True):
        """
        Run the complete automation pipeline.
        
        Args:
            limit: Limit for scraping and applying
            dry_run: If True, don't actually submit or send
        """
        self.logger.info("Running full automation pipeline...")
        
        # Step 1: Scrape jobs
        self.scrape_jobs(limit=limit, dry_run=dry_run)
        
        # Step 2: Match jobs
        self.match_jobs(dry_run=dry_run)
        
        # Step 3: Apply to jobs (auto-apply only)
        self.apply_to_jobs(limit=limit, dry_run=dry_run, mode='auto')
        
        # Step 4: Send follow-ups
        self.send_followups(dry_run=dry_run)
        
        # Step 5: Show statistics
        self.show_statistics()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Job Application Automation")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape job postings')
    scrape_parser.add_argument('--limit', type=int, default=50, help='Max jobs to scrape')
    scrape_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    # Match command
    match_parser = subparsers.add_parser('match', help='Match jobs with resume')
    match_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    # Apply command
    apply_parser = subparsers.add_parser('apply', help='Apply to jobs')
    apply_parser.add_argument('--limit', type=int, help='Max applications to submit')
    apply_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    apply_parser.add_argument('--mode', choices=['auto', 'review'], help='Application mode')
    
    # Follow-up command
    followup_parser = subparsers.add_parser('followup', help='Send follow-up emails')
    followup_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    # Review command
    subparsers.add_parser('review', help='Show review queue')
    
    # Run-all command
    runall_parser = subparsers.add_parser('run-all', help='Run full pipeline')
    runall_parser.add_argument('--limit', type=int, default=10, help='Limit per step')
    runall_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize automation
    automation = JobAutomation()
    
    # Execute command
    if args.command == 'scrape':
        automation.scrape_jobs(limit=args.limit, dry_run=args.dry_run)
    elif args.command == 'match':
        automation.match_jobs(dry_run=args.dry_run)
    elif args.command == 'apply':
        automation.apply_to_jobs(limit=args.limit, dry_run=args.dry_run, mode=args.mode)
    elif args.command == 'followup':
        automation.send_followups(dry_run=args.dry_run)
    elif args.command == 'stats':
        automation.show_statistics()
    elif args.command == 'review':
        automation.review_queue()
    elif args.command == 'run-all':
        automation.run_full_pipeline(limit=args.limit, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
