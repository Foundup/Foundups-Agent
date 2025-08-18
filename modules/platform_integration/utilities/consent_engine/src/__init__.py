"""
Consent Engine Module - Meeting Consent Management

Manages participant consent collection and validation for meetings.
"""

from .consent_engine import ConsentEngine, ConsentStatus, ConsentRequest

__version__ = "0.0.1"
__all__ = ["ConsentEngine", "ConsentStatus", "ConsentRequest"] 