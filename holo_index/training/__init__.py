"""
HoloIndex Training Module - Comprehensive System Data Training for Gemma/Qwen

This module collects ALL system data for training Gemma as Qwen's assistant:
- 012.txt (0102 operational decisions)
- ModLog files (module evolution)
- WSP violations (error -> fix patterns)
- Chat logs (interaction patterns)
- Git history (system evolution)
- Daemon logs (runtime operations)

Architecture: Gemma + Qwen -> Together become DAE for Rubik's Cube

WSP Compliance: WSP 90 (UTF-8), WSP 49 (Module Structure), WSP 22 (ModLog)
"""

from .comprehensive_training_corpus import ComprehensiveTrainingCorpus
from .export_for_colab import ColabExporter

__all__ = [
    'ComprehensiveTrainingCorpus',
    'ColabExporter'
]
