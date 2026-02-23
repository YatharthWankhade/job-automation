"""
Logging configuration for job application automation system.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name: str = "job_automation", 
                log_file: str = "logs/job_automation.log",
                level: str = "INFO",
                console: bool = True) -> logging.Logger:
    """
    Set up logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Whether to log to console
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler with colors
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


def log_job_scraped(logger: logging.Logger, job_title: str, company: str, platform: str):
    """Log when a job is scraped."""
    logger.info(f"📋 Scraped: {job_title} at {company} ({platform})")


def log_job_matched(logger: logging.Logger, job_title: str, company: str, score: float):
    """Log when a job is matched."""
    logger.info(f"✅ Matched ({score}%): {job_title} at {company}")


def log_application_submitted(logger: logging.Logger, job_title: str, company: str):
    """Log when an application is submitted."""
    logger.info(f"🚀 Applied: {job_title} at {company}")


def log_followup_sent(logger: logging.Logger, job_title: str, company: str, attempt: int):
    """Log when a follow-up is sent."""
    logger.info(f"📧 Follow-up #{attempt} sent: {job_title} at {company}")


def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """Log an error with context."""
    logger.error(f"❌ Error {context}: {str(error)}", exc_info=True)
