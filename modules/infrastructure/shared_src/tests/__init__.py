# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        pass  # UTF-8 wrapping handled by entrypoint (WSP 90)
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===
# -*- coding: utf-8 -*-
import sys
import io


"""shared_src test package"""

# Test package initialization
