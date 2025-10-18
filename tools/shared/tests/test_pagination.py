#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Test script for pagination system with placeholder modules
"""

from pathlib import Path
from tools.shared.module_scoring_engine import WSP37ScoringEngine

def test_pagination():
    """Test the pagination system with placeholder modules."""
    print("[U+1F9EA] Testing Pagination System with Placeholder Modules...")
    
    # Initialize scoring engine
    scoring_engine = WSP37ScoringEngine()
    
    # Get all modules sorted by priority
    all_modules = scoring_engine.get_all_modules_sorted()
    
    print(f"[DATA] Total modules: {len(all_modules)}")
    print(f"[U+1F4C4] Pages needed: {(len(all_modules) + 3) // 4} (4 modules per page)")
    print()
    
    # Test pagination display
    modules_per_page = 4
    total_pages = (len(all_modules) + modules_per_page - 1) // modules_per_page
    
    for page in range(1, total_pages + 1):
        start_idx = (page - 1) * modules_per_page
        end_idx = min(start_idx + modules_per_page, len(all_modules))
        
        print(f"[U+1F4C4] Page {page} of {total_pages}:")
        print("-" * 50)
        
        for i, module in enumerate(all_modules[start_idx:end_idx], start_idx + 1):
            influence = module.rider_influence if hasattr(module, 'rider_influence') else 0
            print(f"{i:2d}. {module.name} - Score: {module.mps_score} (Rider: {influence}/5)")
            print(f"     Domain: {module.domain} | Status: {module.status}")
            if "placeholder" in module.name:
                print(f"     [U+1F9EA] PLACEHOLDER - {module.summary}")
            print()
        
        if page < total_pages:
            print("   -> Next page available")
        if page > 1:
            print("   <- Previous page available")
        print()
    
    # Test P0 modules specifically
    p0_modules = scoring_engine.get_priority_modules("P0")
    print(f"[U+1F525] P0 (Critical) modules: {len(p0_modules)}")
    for i, module in enumerate(p0_modules, 1):
        influence = module.rider_influence if hasattr(module, 'rider_influence') else 0
        print(f"  {i}. {module.name} - Score: {module.mps_score} (Rider: {influence}/5)")
    
    print("\n[OK] Pagination test completed!")

if __name__ == "__main__":
    test_pagination() 