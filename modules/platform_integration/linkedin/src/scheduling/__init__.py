"""
LinkedIn Scheduling Module
WSP Compliance: WSP 49
"""

try:
    from .linkedin_scheduler import LinkedInScheduler
except ImportError:
    LinkedInScheduler = None

__all__ = ['LinkedInScheduler'] if LinkedInScheduler else []