# -*- coding: utf-8 -*-
import sys
import io


"""shared_utilities implementation package"""

# Import all utility modules
from ..session_utils import SessionUtils, load_session_cache, save_session_cache, try_cached_stream
from ..validation_utils import ValidationUtils, mask_sensitive_id, validate_api_client
from ..delay_utils import DelayUtils, calculate_enhanced_delay

# Public API exports - update when implementation is complete
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

__all__ = [
    # Session utilities
    "SessionUtils",
    "load_session_cache",
    "save_session_cache",
    "try_cached_stream",
    # Validation utilities
    "ValidationUtils",
    "mask_sensitive_id",
    "validate_api_client",
    # Delay utilities
    "DelayUtils",
    "calculate_enhanced_delay"
]
