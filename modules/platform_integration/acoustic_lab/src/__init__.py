#!/usr/bin/env python3
"""
Acoustic Lab Source Code

Contains the core implementation for:
- Audio fingerprinting using MFCC
- Acoustic triangulation algorithms
- Synthetic audio library management
- Flask web application
"""

from .acoustic_processor import AcousticProcessor
from .audio_library import AudioLibrary
from .triangulation_engine import TriangulationEngine
from .web_app import create_app

__all__ = [
    'AcousticProcessor',
    'AudioLibrary',
    'TriangulationEngine',
    'create_app'
]
