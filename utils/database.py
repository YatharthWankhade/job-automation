"""
Database utilities for job application automation system.
Handles all database operations for jobs, applications, and follow-ups.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
from contextlib import contextmanager


class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    url TEXT NOT NULL,
                    description TEXT,
                    requirements TEXT,
                    salary_range TEXT,
                    job_type TEXT,
                    platform TEXT NOT NULL,
                    posted_date TEXT,
                    scraped_date TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Applications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    match_score REAL NOT NULL,
                    match_rationale TEXT,
                    status TEXT NOT NULL,
                    application_mode TEXT,
                    cover_letter TEXT,
                    applied_date TEXT,
                    response_received BOOLEAN DEFAULT 0,
                    response_date TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES jobs (id)
                )
            """)
            
            # Follow-ups table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS followups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER NOT NULL,
                    scheduled_date TEXT NOT NULL,
                    sent_date TEXT,
                    status TEXT NOT NULL,
                    email_subject TEXT,
                    email_body TEXT,
                    attempt_number INTEGER DEFAULT 1,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (application_id) REFERENCES applications (id)
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_platform ON jobs(platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_followups_status ON followups(status)")
    
    # ===== JOB OPERATIONS =====
    
    def add_job(self, job_data: Dict) -> Optional[int]:
        """Add a new job to the database. Returns job ID or None if duplicate."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO jobs (job_id, title, company, location, url, description, 
                                     requirements, salary_range, job_type, platform, 
                                     posted_date, scraped_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_data['job_id'],
                    job_data['title'],
                    job_data['company'],
                    job_data.get('location'),
                    job_data['url'],
                    job_data.get('description'),
                    job_data.get('requirements'),
                    job_data.get('salary_range'),
                    job_data.get('job_type'),
                    job_data['platform'],
                    job_data.get('posted_date'),
                    datetime.now().isoformat()
                ))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Job already exists
                return None
    
    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get job by database ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def job_exists(self, job_id: str) -> bool:
        """Check if job already exists in database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
            return cursor.fetchone() is not None
    
    def get_jobs_without_applications(self) -> List[Dict]:
        """Get all jobs that haven't been applied to yet."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT j.* FROM jobs j
                LEFT JOIN applications a ON j.id = a.job_id
                WHERE a.id IS NULL AND j.is_active = 1
                ORDER BY j.scraped_date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== APPLICATION OPERATIONS =====
    
    def add_application(self, app_data: Dict) -> int:
        """Add a new application record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO applications (job_id, match_score, match_rationale, status,
                                         application_mode, cover_letter, applied_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                app_data['job_id'],
                app_data['match_score'],
                app_data.get('match_rationale'),
                app_data['status'],
                app_data.get('application_mode'),
                app_data.get('cover_letter'),
                app_data.get('applied_date'),
                app_data.get('notes')
            ))
            return cursor.lastrowid
    
    def update_application_status(self, app_id: int, status: str, notes: str = None):
        """Update application status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE applications 
                SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, notes, app_id))
    
    def get_application(self, app_id: int) -> Optional[Dict]:
        """Get application by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_pending_applications(self) -> List[Dict]:
        """Get applications in review queue."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, j.title, j.company, j.url 
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                WHERE a.status = 'pending_review'
                ORDER BY a.match_score DESC, a.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_applied_applications(self) -> List[Dict]:
        """Get all successfully applied applications."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, j.title, j.company, j.url 
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                WHERE a.status = 'applied'
                ORDER BY a.applied_date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== FOLLOW-UP OPERATIONS =====
    
    def add_followup(self, followup_data: Dict) -> int:
        """Add a follow-up record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO followups (application_id, scheduled_date, status,
                                      email_subject, email_body, attempt_number)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                followup_data['application_id'],
                followup_data['scheduled_date'],
                followup_data['status'],
                followup_data.get('email_subject'),
                followup_data.get('email_body'),
                followup_data.get('attempt_number', 1)
            ))
            return cursor.lastrowid
    
    def get_pending_followups(self, current_date: str) -> List[Dict]:
        """Get follow-ups that are due to be sent."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.*, a.job_id, j.title, j.company, j.url
                FROM followups f
                JOIN applications a ON f.application_id = a.id
                JOIN jobs j ON a.job_id = j.id
                WHERE f.status = 'pending' 
                AND f.scheduled_date <= ?
                ORDER BY f.scheduled_date ASC
            """, (current_date,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_followup_status(self, followup_id: int, status: str, 
                              sent_date: str = None, error_message: str = None):
        """Update follow-up status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE followups 
                SET status = ?, sent_date = ?, error_message = ?
                WHERE id = ?
            """, (status, sent_date, error_message, followup_id))
    
    # ===== STATISTICS =====
    
    def get_statistics(self) -> Dict:
        """Get overall statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total jobs scraped
            cursor.execute("SELECT COUNT(*) as count FROM jobs")
            stats['total_jobs'] = cursor.fetchone()['count']
            
            # Total applications
            cursor.execute("SELECT COUNT(*) as count FROM applications")
            stats['total_applications'] = cursor.fetchone()['count']
            
            # Applications by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM applications 
                GROUP BY status
            """)
            stats['applications_by_status'] = {row['status']: row['count'] 
                                              for row in cursor.fetchall()}
            
            # Pending follow-ups
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM followups 
                WHERE status = 'pending'
            """)
            stats['pending_followups'] = cursor.fetchone()['count']
            
            # Average match score
            cursor.execute("SELECT AVG(match_score) as avg FROM applications")
            stats['avg_match_score'] = round(cursor.fetchone()['avg'] or 0, 2)
            
            return stats
