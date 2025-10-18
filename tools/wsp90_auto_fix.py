#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WSP 90 UTF-8 Enforcement Auto-Fixer
====================================

Automatically adds WSP 90 UTF-8 enforcement headers to Python files.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

import os
import re
from pathlib import Path

WSP90_HEADER = """# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems

import sys
import os
import io

# Store original stdout/stderr for restoration if needed
_original_stdout = sys.stdout
_original_stderr = sys.stderr

class SafeUTF8Wrapper:
    \"\"\"Safe UTF-8 wrapper that doesn't interfere with redirection\"\"\"

    def __init__(self, original_stream):
        self.original_stream = original_stream
        self.encoding = 'utf-8'
        self.errors = 'replace'

    def write(self, data):
        \"\"\"Write with UTF-8 encoding safety\"\"\"
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
        \"\"\"Flush the stream\"\"\"
        try:
            self.original_stream.flush()
        except Exception:
            pass

    def __getattr__(self, name):
        \"\"\"Delegate other attributes to original stream\"\"\"
        return getattr(self.original_stream, name)

# Only apply on Windows where the problem occurs
if sys.platform.startswith('win'):
    # Use safe wrapper instead of full TextIOWrapper
    sys.stdout = SafeUTF8Wrapper(sys.stdout)
    sys.stderr = SafeUTF8Wrapper(sys.stderr)
# === END UTF-8 ENFORCEMENT ===

"""

def has_wsp90_header(content: str) -> bool:
    """Check if file already has WSP 90 header"""
    return "# === UTF-8 ENFORCEMENT (WSP 90) ===" in content

def has_utf8_declaration(content: str) -> bool:
    """Check if file has UTF-8 encoding declaration"""
    return "# -*- coding: utf-8 -*-" in content or "# coding: utf-8" in content

def add_utf8_declaration(content: str) -> str:
    """Add UTF-8 encoding declaration at top of file"""
    if has_utf8_declaration(content):
        return content

    # Find the first non-comment line (after shebang if present)
    lines = content.split('\n')
    insert_index = 0

    # Skip shebang if present
    if lines and lines[0].startswith('#!'):
        insert_index = 1

    # Insert UTF-8 declaration
    lines.insert(insert_index, "# -*- coding: utf-8 -*-")
    if insert_index == 0 or (insert_index == 1 and not lines[insert_index].strip()):
        lines.insert(insert_index + 1, "")

    return '\n'.join(lines)

def find_import_section(content: str) -> tuple[int, int]:
    """Find the import section in the file"""
    lines = content.split('\n')
    start_line = -1
    end_line = -1

    for i, line in enumerate(lines):
        # Skip docstring
        if line.strip().startswith('"""') or line.strip().startswith("'''"):
            # Find end of docstring
            quote_type = line.strip()[:3]
            j = i + 1
            while j < len(lines):
                if quote_type in lines[j]:
                    i = j
                    break
                j += 1
            continue

        # Skip comments and empty lines until we find imports
        if line.strip().startswith('#') or not line.strip():
            continue

        # Found first non-comment, non-empty line - this should be imports
        if start_line == -1:
            start_line = i
            # Find end of import section
            j = i
            while j < len(lines):
                if not lines[j].strip() or lines[j].strip().startswith('#'):
                    j += 1
                    continue
                if not (lines[j].strip().startswith(('import ', 'from ')) or
                       lines[j].strip().startswith('#') or
                       not lines[j].strip()):
                    break
                j += 1
            end_line = j
            break

    return start_line, end_line

def add_wsp90_header(content: str) -> str:
    """Add WSP 90 header after imports"""
    if has_wsp90_header(content):
        return content

    lines = content.split('\n')
    start_line, end_line = find_import_section(content)

    if start_line == -1:
        # No clear import section found, add after docstring
        docstring_end = -1
        in_docstring = False
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                else:
                    docstring_end = i
                    break

        if docstring_end != -1:
            # Insert after docstring
            lines.insert(docstring_end + 1, "")
            for i, header_line in enumerate(WSP90_HEADER.strip().split('\n')):
                lines.insert(docstring_end + 1 + i, header_line)
        else:
            # Insert at beginning after any shebang
            insert_pos = 0
            if lines and lines[0].startswith('#!'):
                insert_pos = 1
            for i, header_line in enumerate(WSP90_HEADER.strip().split('\n')):
                lines.insert(insert_pos + i, header_line)
    else:
        # Insert after import section
        lines.insert(end_line, "")
        for i, header_line in enumerate(WSP90_HEADER.strip().split('\n')):
            lines.insert(end_line + i, header_line)

    return '\n'.join(lines)

def fix_file(file_path: Path) -> bool:
    """Fix a single Python file for WSP 90 compliance"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip if already compliant
        if has_wsp90_header(content):
            return True

        # Add UTF-8 declaration if missing
        content = add_utf8_declaration(content)

        # Add WSP 90 header
        content = add_wsp90_header(content)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"[ERROR] Failed to fix {file_path}: {e}")
        return False

def fix_directory(directory: Path, max_files: int = None) -> tuple[int, int]:
    """Fix all Python files in a directory"""
    if not directory.exists():
        print(f"[SKIP] Directory not found: {directory}")
        return 0, 0

    python_files = list(directory.rglob("*.py"))
    if not python_files:
        print(f"[SKIP] No Python files in {directory}")
        return 0, 0

    if max_files:
        python_files = python_files[:max_files]

    fixed = 0
    total = len(python_files)

    print(f"[INFO] Fixing {total} files in {directory}")

    for py_file in python_files:
        if fix_file(py_file):
            fixed += 1
        else:
            print(f"[FAIL] {py_file}")

    return fixed, total

if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent

    print("WSP 90 UTF-8 Enforcement Auto-Fixer")
    print("=" * 50)
    print("Phase 1: Core Infrastructure Modules")
    print()

    # Phase 1: Critical infrastructure (as per WSP 90)
    critical_dirs = [
        repo_root / "modules" / "infrastructure",
        repo_root / "modules" / "communication" / "liberty_alert",
        repo_root / "holo_index",
        repo_root / "tools",
    ]

    total_fixed = 0
    total_processed = 0

    for directory in critical_dirs:
        # Remove limit for infrastructure modules since they're critical
        if "infrastructure" in str(directory):
            fixed, processed = fix_directory(directory)  # No limit for infrastructure
        else:
            fixed, processed = fix_directory(directory, max_files=100)  # Reasonable limit for others
        total_fixed += fixed
        total_processed += processed
        print(f"[RESULT] {fixed}/{processed} files fixed in {directory}")
        print()

    print("=" * 50)
    print(f"Phase 1 Complete: {total_fixed}/{total_processed} critical files fixed")
    print("Run 'python tools/wsp90_enforcer.py' to check remaining compliance")
    print("Use --full flag to fix all files (WARNING: large operation)")
