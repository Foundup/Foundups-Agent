# -*- coding: utf-8 -*-
"""
Transcript Ask SKILLz

Extract full transcripts from YouTube videos using the "Ask" Gemini feature.
"""
from .executor import TranscriptAskExecutor, execute_skill, TranscriptResult

__all__ = [
    "TranscriptAskExecutor",
    "execute_skill",
    "TranscriptResult",
]
