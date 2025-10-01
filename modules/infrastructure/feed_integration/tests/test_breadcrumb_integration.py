#!/usr/bin/env python3
"""Test that breadcrumb integration didn't break HoloIndex"""

import sys
from pathlib import Path

# Add project root to path (go up four directories from tests/)
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_holo_index_works():
    """Test basic HoloIndex functionality"""
    print("Testing HoloIndex with breadcrumbs...")

    try:
        # Import and initialize HoloIndex
        from holo_index.core.holo_index import HoloIndex
        hi = HoloIndex()
        print("[OK] HoloIndex initialized")

        # Check breadcrumb tracer
        if hi.breadcrumb_tracer:
            print("[OK] Breadcrumb tracer active")
        else:
            print("[WARN] Breadcrumb tracer not active (but HoloIndex works)")

        # Perform a search
        results = hi.search("test", limit=1)
        print(f"[OK] Search completed, found {len(results.get('code', []))} code results")

        # Check if breadcrumbs were recorded
        if hi.breadcrumb_tracer:
            trail = hi.breadcrumb_tracer.get_session_trail()
            print(f"[OK] Breadcrumb trail has {len(trail)} entries")

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_breadcrumb_tracer_standalone():
    """Test BreadcrumbTracer by itself"""
    print("\nTesting BreadcrumbTracer standalone...")

    try:
        from holo_index.adaptive_learning.breadcrumb_tracer import BreadcrumbTracer
        bt = BreadcrumbTracer()
        print("[OK] BreadcrumbTracer initialized")

        # Add a test search
        bt.add_search("test query", [{"test": "result"}], ["doc1.md"])
        print("[OK] Added search to breadcrumbs")

        # Get trail
        trail = bt.get_session_trail()
        print(f"[OK] Trail has {len(trail)} entries")

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("BREADCRUMB INTEGRATION TEST")
    print("=" * 50)

    test1 = test_holo_index_works()
    test2 = test_breadcrumb_tracer_standalone()

    print("\n" + "=" * 50)
    if test1 and test2:
        print("ALL TESTS PASSED - Nothing broken!")
    else:
        print("SOME TESTS FAILED - Check errors above")
    print("=" * 50)
