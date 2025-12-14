#!/usr/bin/env python
"""
WSP 85 Compliance: Move campaign_results to correct module location

This script moves campaign_results folders from root and src/ to the module root,
following WSP 85 (Root Directory Protection Protocol).

Per WSP 85: Module-specific data belongs in modules/{domain}/{module}/data/ or 
modules/{domain}/{module}/logs/. Campaign results are module-specific data.
"""
import shutil
from pathlib import Path

def move_campaign_results():
    """Move campaign_results to module location per WSP 85."""
    # Paths
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    root_campaign_results = project_root / "campaign_results"
    src_campaign_results = project_root / "modules" / "ai_intelligence" / "pqn_alignment" / "src" / "campaign_results"
    module_campaign_results = project_root / "modules" / "ai_intelligence" / "pqn_alignment" / "campaign_results"
    
    # Ensure module location exists
    module_campaign_results.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    skipped_count = 0
    
    # Move from root level
    if root_campaign_results.exists():
        print(f"[WSP 85] Moving campaign_results from root to module location...")
        for item in root_campaign_results.iterdir():
            if item.is_dir():
                dest = module_campaign_results / item.name
                if dest.exists():
                    print(f"  [SKIP] {item.name} already exists in module location")
                    skipped_count += 1
                else:
                    print(f"  [MOVE] {item.name} -> {dest}")
                    shutil.move(str(item), str(dest))
                    moved_count += 1
    
    # Move from src/ level
    if src_campaign_results.exists():
        print(f"\n[WSP 85] Moving campaign_results from src/ to module location...")
        for item in src_campaign_results.iterdir():
            if item.is_dir():
                dest = module_campaign_results / item.name
                if dest.exists():
                    print(f"  [SKIP] {item.name} already exists in module location")
                    skipped_count += 1
                else:
                    print(f"  [MOVE] {item.name} -> {dest}")
                    shutil.move(str(item), str(dest))
                    moved_count += 1
    
    # Clean up directories (WSP 85: Remove root violations)
    # If root campaign_results exists and all folders were skipped (duplicates), remove it
    if root_campaign_results.exists():
        remaining_items = list(root_campaign_results.iterdir())
        if not remaining_items:
            print(f"\n[WSP 85] Removing empty root campaign_results/ directory...")
            root_campaign_results.rmdir()
        else:
            print(f"\n[WSP 85] WARNING: Root campaign_results/ still contains {len(remaining_items)} folders")
            print(f"  These appear to be duplicates of module location. Safe to delete manually:")
            print(f"  Remove-Item -Recurse -Force campaign_results")
    
    if src_campaign_results.exists():
        remaining_items = list(src_campaign_results.iterdir())
        if not remaining_items:
            print(f"\n[WSP 85] Removing empty src/campaign_results/ directory...")
            src_campaign_results.rmdir()
        else:
            print(f"[WSP 85] WARNING: src/campaign_results/ still contains {len(remaining_items)} folders")
            print(f"  These appear to be duplicates. Safe to delete manually if verified.")
    
    print(f"\n[OK] WSP 85 compliance complete:")
    print(f"  - Moved: {moved_count} folders")
    print(f"  - Skipped (duplicates): {skipped_count} folders")
    print(f"  - Module location: {module_campaign_results}")

if __name__ == "__main__":
    move_campaign_results()

