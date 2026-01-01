"""
SKILLz Migration Script

Migrates the codebase from SKILL.md to SKILLz.md naming convention.

WSP 95 Enhancement: The 'z' suffix makes skill files immediately recognizable
as FoundUps/WRE agent instructions.

Run: python scripts/migrate_skillz_naming.py [--dry-run]
"""

import os
import re
import argparse
from pathlib import Path


def find_skill_md_files(root_dir: str) -> list:
    """Find all SKILL.md files that need renaming."""
    skill_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == "SKILL.md":
                skill_files.append(Path(dirpath) / filename)
    return skill_files


def find_references_in_file(filepath: Path, pattern: str) -> list:
    """Find all occurrences of pattern in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        matches = []
        for i, line in enumerate(content.split('\n'), 1):
            if pattern in line:
                matches.append((i, line.strip()))
        
        return matches
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return []


def replace_in_file(filepath: Path, old: str, new: str, dry_run: bool = True) -> int:
    """Replace all occurrences of old with new in file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        count = content.count(old)
        if count == 0:
            return 0
        
        if not dry_run:
            new_content = content.replace(old, new)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return count
    except Exception as e:
        print(f"  Error updating {filepath}: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Migrate SKILL.md to SKILLz.md")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be changed without making changes")
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    
    print("=" * 60)
    print("SKILLz MIGRATION SCRIPT")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    
    # Step 1: Find and rename SKILL.md files
    print("\n[1] Finding SKILL.md files to rename...")
    skill_files = find_skill_md_files(root_dir)
    print(f"    Found {len(skill_files)} SKILL.md files")
    
    for skill_file in skill_files:
        new_name = skill_file.parent / "SKILLz.md"
        print(f"    {skill_file.relative_to(root_dir)}")
        print(f"      → {new_name.relative_to(root_dir)}")
        
        if not args.dry_run:
            os.rename(skill_file, new_name)
    
    # Step 2: Update references in .md and .py files
    print("\n[2] Updating references in code and docs...")
    
    extensions = ['.md', '.py']
    exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
    
    files_to_update = []
    for ext in extensions:
        for filepath in root_dir.rglob(f"*{ext}"):
            if any(excl in str(filepath) for excl in exclude_dirs):
                continue
            files_to_update.append(filepath)
    
    total_replacements = 0
    files_changed = 0
    
    # Patterns to replace
    replacements = [
        ("SKILL.md", "SKILLz.md"),
        ("WSP_95_WRE_Skills_Wardrobe_Protocol", "WSP_95_WRE_SKILLz_Wardrobe_Protocol"),
        ("WSP_96_WRE_Skills_Wardrobe_Protocol", "WSP_95_WRE_SKILLz_Wardrobe_Protocol"),
    ]
    
    for filepath in files_to_update:
        file_changes = 0
        for old, new in replacements:
            count = replace_in_file(filepath, old, new, dry_run=args.dry_run)
            file_changes += count
        
        if file_changes > 0:
            print(f"    {filepath.relative_to(root_dir)}: {file_changes} replacements")
            files_changed += 1
            total_replacements += file_changes
    
    # Summary
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"  SKILL.md files found:    {len(skill_files)}")
    print(f"  Files with references:   {files_changed}")
    print(f"  Total replacements:      {total_replacements}")
    print()
    
    if args.dry_run:
        print("  [DRY RUN] No changes were made.")
        print("  Run without --dry-run to apply changes.")
    else:
        print("  [DONE] All changes applied.")


if __name__ == "__main__":
    main()
