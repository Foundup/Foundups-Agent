#!/usr/bin/env python3
"""
DEPRECATED - Backwards compatibility wrapper

This file has been moved to: modules/infrastructure/metrics_appender/src/metrics_appender.py

Please update your imports to:
    from modules.infrastructure.metrics_appender.src.metrics_appender import MetricsAppender

WSP Compliance Fix: WSP 3 (Module Organization), WSP 49 (Module Structure)
Date: 2025-10-20
"""

import warnings

# Show deprecation warning
warnings.warn(
    "Importing from modules.infrastructure.wre_core.skillz.metrics_append is deprecated. "
    "Please use: from modules.infrastructure.metrics_appender.src.metrics_appender import MetricsAppender",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location for backwards compatibility
from modules.infrastructure.metrics_appender.src.metrics_appender import MetricsAppender

__all__ = ['MetricsAppender']
