"""
LinkedIn Proxy Module
WSP Compliance: WSP 49
"""

try:
    from .linkedin_proxy import LinkedInProxy
except ImportError:
    LinkedInProxy = None

__all__ = ['LinkedInProxy'] if LinkedInProxy else []