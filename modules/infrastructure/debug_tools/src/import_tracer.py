#!/usr/bin/env python3
"""
Enhanced Import Tracer - Find which import is blocking main.py
Logs every import with timestamps to identify slow/hanging modules
"""

import sys
import importlib.abc
import importlib.machinery
from datetime import datetime

class ImportTimer(importlib.abc.MetaPathFinder):
    """Track import timing to find blockers"""

    def __init__(self):
        self.imports = []
        self.current_import = None
        self.start_time = None

    def find_spec(self, fullname, path, target=None):
        """Called before every import"""
        now = datetime.now()

        # Log completion of previous import
        if self.current_import:
            elapsed = (now - self.start_time).total_seconds()
            status = "OK" if elapsed < 1.0 else "SLOW" if elapsed < 5.0 else "BLOCKING"
            print(f"[{status}] {self.current_import} ({elapsed:.2f}s)", flush=True)

        # Start timing new import
        self.current_import = fullname
        self.start_time = now
        print(f"[IMPORT] {fullname}...", end=" ", flush=True)

        return None  # Let default import mechanism handle it

print("="*70)
print("[IMPORT TRACER] Starting main.py with import timing")
print("="*70)
print()

# Install the import hook
tracer = ImportTimer()
sys.meta_path.insert(0, tracer)

# Now import main.py - this will trigger detailed logging
print("[IMPORTING] main module...")
print()

try:
    import main
    print()
    print("="*70)
    print("[SUCCESS] main.py imported successfully!")
    print("="*70)
except Exception as e:
    print()
    print("="*70)
    print(f"[ERROR] Import failed: {e}")
    print("="*70)
    import traceback
    traceback.print_exc()
