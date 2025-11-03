# -*- coding: utf-8 -*-
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems

import sys
import os
import io

# Store original stdout/stderr for restoration if needed
_original_stdout = sys.stdout
_original_stderr = sys.stderr

class SafeUTF8Wrapper:
    """Safe UTF-8 wrapper that doesn't interfere with redirection"""

    def __init__(self, original_stream):
        self.original_stream = original_stream
        self.encoding = 'utf-8'
        self.errors = 'replace'

    def write(self, data):
        """Write with UTF-8 encoding safety"""
        try:
            if isinstance(data, str):
                # Try to encode as UTF-8 bytes first
                encoded = data.encode('utf-8', errors='replace')
                # Write bytes to original stream
                if hasattr(self.original_stream, 'buffer'):
                    self.original_stream.buffer.write(encoded)
                else:
                    # Fallback for streams without buffer
                    self.original_stream.write(data.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
            else:
                # If it's already bytes, write directly
                self.original_stream.write(data)
        except Exception:
            # Ultimate fallback - just try to write
            try:
                self.original_stream.write(str(data))
            except Exception:
                pass  # Silent failure to avoid infinite loops

    def flush(self):
        """Flush the stream"""
        try:
            self.original_stream.flush()
        except Exception:
            pass

    def __getattr__(self, name):
        """Delegate other attributes to original stream"""
        return getattr(self.original_stream, name)

# Only apply on Windows where the problem occurs
if sys.platform.startswith('win'):
    # Use safe wrapper instead of full TextIOWrapper
    sys.stdout = SafeUTF8Wrapper(sys.stdout)
    sys.stderr = SafeUTF8Wrapper(sys.stderr)
# === END UTF-8 ENFORCEMENT ===

# WSP Orchestrator module
