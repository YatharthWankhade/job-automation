"""
Job matcher that uses AI to match jobs with resume data.
"""

import yaml
from typing import Dict, List, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ai_helper import AIHelper
from utils.database import Database
from utils.logger import setup_logger


class JobMatcher:
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize job matcher.
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.threshold = self.config['matching']['threshold']
        self.ai_helper = AIHelper(model_name=self.config['matching']['gemini_model'])
        self.db = Database(self.config['database']['path'])
        self.logger = setup_logger(
            level=self.config['logging']['level'],
            log_file=self.config['logging']['file'],
            console=self.config['logging']['console']
        )
    
    def match_jobs(self, resume_data: Dict, dry_run: bool = False) -> List[Dict]:
        """
        Match all unprocessed jobs with resume data.
        
        Args:
            resume_data: Structured resume data
            dry_run: If True, don't save to database
        
        Returns:
            List of matched jobs with scores
        """
        # Get jobs that haven't been matched yet
        jobs = self.db.get_jobs_without_applications()
        
        if not jobs:
            self.logger.info("No new jobs to match")
            return []
        
        self.logger.info(f"Matching {len(jobs)} jobs with resume...")
        
        matched_jobs = []
        
        for job in jobs:
            try:
                # Use AI to match job with resume
                match_score, rationale, missing_skills = self.ai_helper.match_job_with_resume(
                    job, resume_data
                )
                
                job['match_score'] = match_score
                job['match_rationale'] = rationale
                job['missing_skills'] = missing_skills
                
                # Log the match
                if match_score >= self.threshold:
                    self.logger.info(
                        f"✅ Match ({match_score}%): {job['title']} at {job['company']}"
                    )
                    matched_jobs.append(job)
                    
                    if not dry_run:
                        # Determine application mode
                        app_mode = self._determine_application_mode(match_score)
                        
                        # Add to applications table
                        app_data = {
                            'job_id': job['id'],
                            'match_score': match_score,
                            'match_rationale': rationale,
                            'status': 'pending_review' if app_mode == 'review' else 'ready_to_apply',
                            'application_mode': app_mode,
                            'cover_letter': None,
                            'applied_date': None,
                            'notes': f"Missing skills: {', '.join(missing_skills)}" if missing_skills else None
                        }
                        self.db.add_application(app_data)
                else:
                    self.logger.debug(
                        f"❌ Below threshold ({match_score}%): {job['title']} at {job['company']}"
                    )
                    
                    if not dry_run:
                        # Still add to database but mark as rejected
                        app_data = {
                            'job_id': job['id'],
                            'match_score': match_score,
                            'match_rationale': rationale,
                            'status': 'rejected_low_match',
                            'application_mode': 'none',
                            'cover_letter': None,
                            'applied_date': None,
                            'notes': f"Below threshold. Missing: {', '.join(missing_skills)}"
                        }
                        self.db.add_application(app_data)
                        
            except Exception as e:
                self.logger.error(f"Error matching job {job['title']}: {e}")
                continue
        
        self.logger.info(
            f"Matched {len(matched_jobs)} jobs above {self.threshold}% threshold"
        )
        
        return matched_jobs
    
    def _determine_application_mode(self, match_score: float) -> str:
        """
        Determine whether to auto-apply or add to review queue.
        
        Args:
            match_score: Match score (0-100)
        
        Returns:
            'auto' or 'review'
        """
        app_config = self.config['application']
        mode = app_config['mode']
        
        if mode == 'auto':
            return 'auto'
        elif mode == 'review_queue':
            return 'review'
        elif mode == 'both':
            # Auto-apply if score is above auto threshold
            auto_threshold = app_config.get('auto_apply_threshold', 85)
            return 'auto' if match_score >= auto_threshold else 'review'
        else:
            return 'review'
    
    def get_match_summary(self) -> Dict:
        """
        Get summary of matching results.
        
        Returns:
            Dictionary with match statistics
        """
        stats = self.db.get_statistics()
        
        summary = {
            'total_jobs_scraped': stats['total_jobs'],
            'total_applications': stats['total_applications'],
            'applications_by_status': stats['applications_by_status'],
            'average_match_score': stats['avg_match_score'],
            'threshold': self.threshold
        }
        
        return summary
    
    def print_match_summary(self):
        """Print a formatted match summary."""
        summary = self.get_match_summary()
        
        print("\n" + "="*60)
        print("JOB MATCHING SUMMARY")
        print("="*60)
        print(f"Total Jobs Scraped: {summary['total_jobs_scraped']}")
        print(f"Total Applications: {summary['total_applications']}")
        print(f"Average Match Score: {summary['average_match_score']}%")
        print(f"Match Threshold: {summary['threshold']}%")
        print("\nApplications by Status:")
        for status, count in summary['applications_by_status'].items():
            print(f"  {status}: {count}")
        print("="*60 + "\n")


if __name__ == "__main__":
    # Test the matcher
    from resume_parser import ResumeParser
    
    parser = ResumeParser()
    resume_data = parser.load_resume_data("../resume_data.json")
    
    matcher = JobMatcher("../config.yaml")
    matched_jobs = matcher.match_jobs(resume_data, dry_run=True)
    
    print(f"\nMatched {len(matched_jobs)} jobs")
    for job in matched_jobs[:5]:  # Show top 5
        print(f"\n{job['title']} at {job['company']}")
        print(f"Match Score: {job['match_score']}%")
        print(f"Rationale: {job['match_rationale'][:200]}...")
