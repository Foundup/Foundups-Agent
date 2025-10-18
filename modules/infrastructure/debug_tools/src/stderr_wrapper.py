#!/usr/bin/env python3
"""
Debug Script: Find Which Module Wraps sys.stderr
Traces import chain to identify WSP 90 violators
"""

import sys
import io
import importlib.abc
import importlib.machinery

# Save original stderr
_original_stderr = sys.stderr
_original_stdout = sys.stdout

class StderrWatchingFinder(importlib.abc.MetaPathFinder):
    """Custom import hook to detect sys.stderr wrapping"""

    def __init__(self):
        self.imports = []
        self.wrapper_found = False

    def find_spec(self, fullname, path, target=None):
        """Called for every import"""
        # Track imports
        self.imports.append(fullname)

        # Check if stderr was wrapped after this import
        if not self.wrapper_found and sys.stderr is not _original_stderr:
            print(f"\n{'='*70}", file=_original_stderr)
            print(f"[FOUND] sys.stderr WRAPPED after importing: {fullname}", file=_original_stderr)
            print(f"{'='*70}", file=_original_stderr)
            print(f"Import chain:", file=_original_stderr)
            for i, mod in enumerate(self.imports[-10:], 1):  # Last 10 imports
                print(f"  {i}. {mod}", file=_original_stderr)
            print(f"{'='*70}\n", file=_original_stderr)
            self.wrapper_found = True

            # Try to find the exact location
            try:
                if fullname in sys.modules:
                    module = sys.modules[fullname]
                    if hasattr(module, '__file__'):
                        print(f"Module file: {module.__file__}", file=_original_stderr)
            except:
                pass

        return None  # Let default import machinery handle it

# Install the import hook
finder = StderrWatchingFinder()
sys.meta_path.insert(0, finder)

print("[DEBUG] Import tracer installed", file=_original_stderr)
print("[DEBUG] Starting main.py import...", file=_original_stderr)
print(f"[DEBUG] Original stderr: {id(_original_stderr)}", file=_original_stderr)
print("="*70 + "\n", file=_original_stderr)

try:
    # Import main.py - this will trigger the tracer
    import main

    print("\n" + "="*70, file=_original_stderr)
    print("[SUCCESS] main.py imported successfully!", file=_original_stderr)
    print("="*70, file=_original_stderr)

except Exception as e:
    print("\n" + "="*70, file=_original_stderr)
    print(f"[ERROR] Import failed: {e}", file=_original_stderr)
    print("="*70, file=_original_stderr)
    import traceback
    traceback.print_exc(file=_original_stderr)

print(f"\n[DEBUG] Total imports tracked: {len(finder.imports)}", file=_original_stderr)
print(f"[DEBUG] Wrapper found: {finder.wrapper_found}", file=_original_stderr)
print(f"[DEBUG] Current stderr: {id(sys.stderr)}", file=_original_stderr)
print(f"[DEBUG] Same as original: {sys.stderr is _original_stderr}", file=_original_stderr)
