#!/usr/bin/env python3
"""
Fix anti_detection_poster.py by replacing print statements with logger calls
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


import re

def fix_logging(file_path):
    """Replace print statements with logger calls"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count original prints
    original_count = content.count('print(')

    # Replace print statements with logger calls
    # Handle different log levels based on content
    replacements = [
        # Errors
        (r'print\(f?"?\[ERROR\]([^"]*)"?\)', r'logger.error("\[ERROR\]\1")'),
        (r'print\(f"?\[ERROR\]([^"]*)"?\)', r'logger.error("\[ERROR\]\1")'),

        # Warnings
        (r'print\(f?"?\[WARNING\]([^"]*)"?\)', r'logger.warning("\[WARNING\]\1")'),
        (r'print\(f"?\[WARN\]([^"]*)"?\)', r'logger.warning("\[WARN\]\1")'),

        # Debug
        (r'print\(f?"?\[DEBUG\]([^"]*)"?\)', r'logger.debug("\[DEBUG\]\1")'),

        # Info (default for everything else)
        (r'print\((.*?)\)', r'logger.info(\1)'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Fix any double-replacement issues
    content = content.replace('logger.info(logger.', 'logger.')

    # Count final prints (should be 0 or very few)
    final_count = content.count('print(')

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed {original_count - final_count} print statements")
    print(f"Remaining print statements: {final_count}")

    return original_count - final_count

if __name__ == "__main__":
    import os
    import sys

    target_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'src',
        'anti_detection_poster.py'
    )

    if not os.path.exists(target_file):
        print(f"Error: File not found: {target_file}")
        sys.exit(1)

    # Backup original
    backup_file = target_file + '.backup_print'
    with open(target_file, 'r', encoding="utf-8") as src:
        with open(backup_file, 'w', encoding="utf-8") as dst:
            dst.write(src.read())
    print(f"Created backup: {backup_file}")

    # Fix logging
    fixed = fix_logging(target_file)
    print(f"Successfully fixed {fixed} print statements in {target_file}")