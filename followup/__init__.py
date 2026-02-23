"""
__init__.py for followup package
"""

from .email_manager import EmailManager
from .scheduler import FollowupScheduler

__all__ = ['EmailManager', 'FollowupScheduler']
