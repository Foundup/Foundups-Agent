#!/usr/bin/env python3
"""
WSP 90 Bulk Fix - UTF-8 Wrapping Deduplication

Problem:
    379 modules copy-pasted the UTF-8 wrapping pattern from WSP 90.
    Each module re-wraps stderr on import, which eventually breaks the stream
    with "lost sys.stderr" error.

Solution:
    1. main.py sets FOUNDUPS_UTF8_WRAPPED=1 BEFORE wrapping
    2. All other modules check this flag before wrapping
    3. This script updates all 379 modules to check the flag

Usage:
    python modules/development/wsp_tools/scripts/fix_wsp90_utf8_bulk.py --dry-run
    python modules/development/wsp_tools/scripts/fix_wsp90_utf8_bulk.py --apply

WSP References:
    - WSP 90: UTF-8 Encoding Enforcement Protocol (original pattern)
    - WSP 50: Pre-Action Verification (check before modify)
"""

import os
import ast
import re
import sys
import argparse
from pathlib import Path


# Pattern variations to detect and fix
PATTERNS = [
    # Full block with if sys.platform check
    (
        r"if sys\.platform\.startswith\(['\"]win['\"]\):\s*\n"
        r"(\s+)sys\.stdout = io\.TextIOWrapper\(sys\.stdout\.buffer[^\n]+\n"
        r"\s+sys\.stderr = io\.TextIOWrapper\(sys\.stderr\.buffer[^\n]+\n",

        r"# UTF-8 enforcement: check flag to prevent double-wrapping (WSP 90 fix)\n"
        r"if sys.platform.startswith('win') and not __import__('os').environ.get('FOUNDUPS_UTF8_WRAPPED'):\n"
        r"\1sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')\n"
        r"\1sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')\n"
    ),

    # Standalone lines without if block
    (
        r"(?m)^(\s*)sys\.stdout = io\.TextIOWrapper\(sys\.stdout\.buffer[^\n]+\n"
        r"\1sys\.stderr = io\.TextIOWrapper\(sys\.stderr\.buffer[^\n]+\n",

        r"\1pass  # UTF-8 wrapping handled by entrypoint (WSP 90)\n"
    ),
]


def _contains_executable_utf8_wrapper(content: str) -> bool:
    """Return True only if executable AST contains sys.stdout/sys.stderr TextIOWrapper assignments."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        fn = node.value.func
        if not (
            isinstance(fn, ast.Attribute)
            and isinstance(fn.value, ast.Name)
            and fn.value.id == "io"
            and fn.attr == "TextIOWrapper"
        ):
            continue

        for target in node.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "sys"
                and target.attr in {"stdout", "stderr"}
            ):
                return True
    return False


def _is_entrypoint_file(content: str) -> bool:
    """Detect common entrypoint guard."""
    return (
        "if __name__ == '__main__':" in content
        or "if __name__ == \"__main__\":" in content
    )


def fix_file(
    filepath: Path,
    dry_run: bool = True,
    include_entrypoints: bool = False,
) -> tuple[bool, str]:
    """
    Fix UTF-8 wrapping in a single file.

    Returns:
        (modified: bool, message: str)
    """
    try:
        content = filepath.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return False, f"SKIP (encoding error): {filepath}"

    # Skip main.py - it should keep the wrapping
    if filepath.name == 'main.py' and 'FoundUps Agent' in content:
        return False, f"SKIP (main.py): {filepath}"

    if not _contains_executable_utf8_wrapper(content):
        return False, f"SKIP (no executable wrapper): {filepath}"

    if not include_entrypoints and _is_entrypoint_file(content):
        return False, f"SKIP (entrypoint): {filepath}"

    # Already fixed?
    if "FOUNDUPS_UTF8_WRAPPED" in content:
        return False, f"SKIP (already fixed): {filepath}"

    original = content

    # Try each pattern
    for pattern, replacement in PATTERNS:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    if content == original:
        # Fallback: replace raw wrapper lines with a no-op statement.
        content = re.sub(
            r"(?m)^(\s*)sys\.stdout = io\.TextIOWrapper\(sys\.stdout\.buffer[^\n]+\n"
            r"\1sys\.stderr = io\.TextIOWrapper\(sys\.stderr\.buffer[^\n]+\n",
            r"\1pass  # UTF-8 wrapping handled by entrypoint (WSP 90)\n",
            content
        )

    if content == original:
        return False, f"SKIP (pattern not matched): {filepath}"

    if not dry_run:
        filepath.write_text(content, encoding='utf-8')
        return True, f"FIXED: {filepath}"
    else:
        return True, f"WOULD FIX: {filepath}"


def main():
    parser = argparse.ArgumentParser(description="WSP 90 Bulk Fix - UTF-8 Wrapping")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be fixed")
    parser.add_argument('--apply', action='store_true', help="Actually apply fixes")
    parser.add_argument(
        '--include-entrypoints',
        action='store_true',
        help="Also modify files with __main__ guard (default: skip entrypoints)",
    )
    parser.add_argument('--verbose', '-v', action='store_true', help="Show all files")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Usage: Specify --dry-run or --apply")
        sys.exit(1)

    dry_run = not args.apply

    repo_root = Path(__file__).resolve().parents[4]  # Go up to repo root
    modules_dir = repo_root / 'modules'

    if not modules_dir.exists():
        print(f"ERROR: modules/ not found at {modules_dir}")
        sys.exit(1)

    print(f"{'[DRY RUN] ' if dry_run else ''}WSP 90 Bulk Fix")
    print(f"Scanning: {modules_dir}")
    print(f"Mode: {'all wrappers (incl. entrypoints)' if args.include_entrypoints else 'non-entrypoint wrappers only (safe default)'}")
    print("-" * 60)

    fixed = 0
    skipped = 0
    errors = 0

    for pyfile in modules_dir.rglob('*.py'):
        # Skip .feature_clean and other backup dirs
        if '.feature_clean' in str(pyfile) or '__pycache__' in str(pyfile):
            continue

        try:
            modified, message = fix_file(
                pyfile,
                dry_run=dry_run,
                include_entrypoints=bool(args.include_entrypoints),
            )
            if modified:
                print(message)
                fixed += 1
            elif args.verbose:
                print(message)
            else:
                skipped += 1
        except Exception as e:
            print(f"ERROR: {pyfile}: {e}")
            errors += 1

    print("-" * 60)
    print(f"{'Would fix' if dry_run else 'Fixed'}: {fixed}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")

    if dry_run and fixed > 0:
        print(f"\nRun with --apply to fix {fixed} files")


if __name__ == '__main__':
    main()
