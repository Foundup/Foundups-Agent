"""
YouTube Shorts AI Generator Module

Autonomous AI-powered YouTube Shorts creation using Google Veo 3.
Standalone module with read-only integration to existing youtube_auth.

WSP Compliance: WSP 3, 49, 80, 54
"""

from .shorts_orchestrator import ShortsOrchestrator
from .veo3_generator import Veo3Generator
from .youtube_uploader import YouTubeShortsUploader
from .shorts_dae import ShortsDAE

__all__ = [
    'ShortsOrchestrator',
    'Veo3Generator',
    'YouTubeShortsUploader',
    'ShortsDAE'
]

__version__ = '0.1.0'
__status__ = 'POC'
