"""
System-Wide Emoji Restoration Script
Reverts WSP 90 unicode cleanup campaign that broke emoji rendering

WSP Compliance:
- WSP 90: Unicode compliance (restore emoji rendering)
- WSP 22: Document changes in ModLog
- WSP 84: Pre-action verification (HoloIndex search confirmed scope)

Usage:
    python scripts/restore_emojis_system_wide.py --dry-run  # Preview changes
    python scripts/restore_emojis_system_wide.py --execute  # Apply fixes
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# Unicode → Emoji mapping (most common)
EMOJI_MAP = {
    '[U+270A]': '✊',  # Raised fist
    '[U+270B]': '✋',  # Raised hand
    '[U+1F590]': '🖐',  # Hand with fingers splayed
    '[U+1F602]': '😂',  # Face with tears of joy
    '[U+1F923]': '🤣',  # Rolling on the floor laughing
    '[U+2764]': '❤',   # Red heart
    '[U+1F44D]': '👍',  # Thumbs up
    '[U+1F64C]': '🙌',  # Raising hands
    '[U+1F60A]': '😊',  # Smiling face with smiling eyes
    '[U+1F4AA]': '💪',  # Flexed biceps
    '[U+1F914]': '🤔',  # Thinking face
    '[U+1F3C6]': '🏆',  # Trophy
    '[U+1F441]': '👁',  # Eye
    '[U+1F331]': '🌱',  # Seedling
    '[U+1F310]': '🌐',  # Globe with meridians
    '[U+1F4E2]': '📢',  # Loudspeaker
    '[U+1F30A]': '🌊',  # Water wave
    '[U+1F31F]': '🌟',  # Glowing star
    '[U+1F35C]': '🍜',  # Steaming bowl
    '[U+1F3AD]': '🎭',  # Performing arts
    '[U+1F440]': '👀',  # Eyes
    '[U+1F44B]': '👋',  # Waving hand
    '[U+1F480]': '💀',  # Skull
    '[U+1F4AB]': '💫',  # Dizzy
    '[U+1F4AC]': '💬',  # Speech balloon
    '[U+1F525]': '🔥',  # Fire
    '[U+1F528]': '🔨',  # Hammer
    '[U+1F5FE]': '🗾',  # Map of Japan
    '[U+1F604]': '😄',  # Grinning face with smiling eyes
    '[U+1F60E]': '😎',  # Smiling face with sunglasses
    '[U+1F917]': '🤗',  # Hugging face
    '[U+1F921]': '🤡',  # Clown face
    '[U+1F92A]': '🤪',  # Zany face
    '[U+1F92F]': '🤯',  # Exploding head
    '[U+1F985]': '🦅',  # Eagle
    '[U+1F9E8]': '🧨',  # Firecracker
    '[U+2728]': '✨',  # Sparkles
    '[U+1F4AD]': '💭',  # Thought balloon
    '[U+26A0]': '⚠',   # Warning sign
}


def should_skip_file(file_path: Path) -> bool:
    """Skip files that should not be modified"""
    skip_patterns = [
        '_archive',
        'test_',
        '.git',
        '__pycache__',
        '.pyc',
        'CLAUDE.md',
        'ModLog.md',
        'README.md',
    ]

    path_str = str(file_path)
    return any(pattern in path_str for pattern in skip_patterns)


def restore_emojis_in_file(file_path: Path, dry_run: bool = True) -> Tuple[int, List[str]]:
    """
    Restore emojis in a single file

    Returns:
        (replacements_count, lines_changed)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read {file_path}: {e}")
        return 0, []

    original_content = content
    replacements = 0
    lines_changed = []

    for unicode_code, emoji in EMOJI_MAP.items():
        if unicode_code in content:
            count = content.count(unicode_code)
            replacements += count
            content = content.replace(unicode_code, emoji)
            lines_changed.append(f"{unicode_code} -> {emoji} ({count}x)")

    if replacements > 0 and not dry_run:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[FIX] {file_path}: {replacements} replacements")
        except Exception as e:
            print(f"[ERROR] Failed to write {file_path}: {e}")
            return 0, []

    return replacements, lines_changed


def scan_and_restore(root_dir: Path, dry_run: bool = True) -> Dict[str, int]:
    """
    Scan all Python files and restore emojis

    Returns:
        Statistics dictionary
    """
    stats = {
        'files_scanned': 0,
        'files_modified': 0,
        'total_replacements': 0,
        'skipped_files': 0
    }

    modified_files = []

    for py_file in root_dir.rglob('*.py'):
        stats['files_scanned'] += 1

        if should_skip_file(py_file):
            stats['skipped_files'] += 1
            continue

        replacements, changes = restore_emojis_in_file(py_file, dry_run)

        if replacements > 0:
            stats['files_modified'] += 1
            stats['total_replacements'] += replacements
            modified_files.append((py_file, replacements, changes))

            if dry_run:
                print(f"\n[DRY-RUN] {py_file}:")
                for change in changes:
                    print(f"  {change}")

    return stats, modified_files


def main():
    parser = argparse.ArgumentParser(description='Restore emojis system-wide')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--execute', action='store_true', help='Apply emoji restoration')
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("[ERROR] Must specify --dry-run or --execute")
        return

    root_dir = Path(__file__).parent.parent / 'modules'
    print(f"[START] Scanning {root_dir}")
    print(f"[MODE] {'DRY-RUN (preview)' if args.dry_run else 'EXECUTE (apply fixes)'}")

    stats, modified_files = scan_and_restore(root_dir, dry_run=args.dry_run)

    print("\n" + "="*80)
    print("[SUMMARY]")
    print(f"  Files scanned: {stats['files_scanned']}")
    print(f"  Files skipped: {stats['skipped_files']}")
    print(f"  Files modified: {stats['files_modified']}")
    print(f"  Total replacements: {stats['total_replacements']}")

    if args.dry_run:
        print("\n[NEXT] Run with --execute to apply fixes")
    else:
        print("\n[COMPLETE] Emoji restoration complete")
        print("[ACTION] Update ModLog.md to document system-wide fix")


if __name__ == '__main__':
    main()
