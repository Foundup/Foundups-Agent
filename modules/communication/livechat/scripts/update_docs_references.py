#!/usr/bin/env python3
"""
Update all documentation references from old filenames to new ones
Per WSP 84 - updating references after renaming
"""

import os
import re
from pathlib import Path

def update_file(filepath, replacements):
    """Update a single file with the replacements"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    # Define the replacements
    replacements = {
        'grok_greeting_generator.py': 'greeting_generator.py',
        'grok_integration.py': 'llm_integration.py',
        'grok_greeting_generator': 'greeting_generator',
        'grok_integration': 'llm_integration'
    }
    
    # Base directory
    base_dir = Path(__file__).parent.parent
    
    # Files to update (already identified)
    files_to_update = [
        'CLEANUP_CHECKLIST.md',
        'docs/BOT_FLOW_COT.md',
        'docs/DELETION_JUSTIFICATION.md',
        'docs/MIGRATION_PLAN.md',
        'docs/WSP_AUDIT_REPORT.md',
        'docs/WSP_COMPLIANCE_AUDIT.md',
        'docs/WSP_COMPLIANCE_FINAL_REPORT.md',
        'INTEGRATION_PLAN.md',
        'MODULE_USAGE_ANALYSIS.md',
        'ORCHESTRATION_ARCHITECTURE.md',
        'README_0102_DAE.md',
        'YOUTUBE_DAE_CUBE.md',
        'YT_DAE_ARCHITECTURE_ANALYSIS.md'
    ]
    
    updated_files = []
    for file_path in files_to_update:
        full_path = base_dir / file_path
        if full_path.exists():
            if update_file(full_path, replacements):
                updated_files.append(file_path)
                print(f"[UPDATED] {file_path}")
            else:
                print(f"[SKIPPED] No changes needed: {file_path}")
        else:
            print(f"[ERROR] File not found: {file_path}")
    
    print(f"\n[SUMMARY] Updated {len(updated_files)} files")
    if updated_files:
        print("Files updated:")
        for f in updated_files:
            print(f"  - {f}")

if __name__ == "__main__":
    main()