from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)


import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.getcwd())

from holo_index.core.holo_index import HoloIndex

def verify_test_integration():
    print("--- 1. Initializing HoloIndex ---")
    holo = HoloIndex(quiet=False)
    
    print("\n--- 2. Indexing Test Registry ---")
    # This should read WSP_Test_Registry.json and populate navigation_tests
    holo.index_test_registry()
    
    print("\n--- 3. Searching for 'engagement' ---")
    # Should find test_live_engagement_full.py
    results = holo.search("engagement", limit=3, doc_type_filter="test")
    
    test_hits = results.get('test_hits', [])
    print(f"\nFound {len(test_hits)} test hits:")
    
    found_target = False
    for hit in test_hits:
        print(f" - [{hit['similarity']}] {hit['test_id']} ({hit['path']})")
        if "test_live_engagement_" in hit['test_id']:
            found_target = True
            
    if found_target:
        print("\n[SUCCESS] Verified: HoloIndex successfully indexed and retrieved the engagement test.")
    else:
        print("\n[FAILURE] Verified: Could not find 'test_live_engagement_' in search results.")

    # Also verify mixed search
    print("\n--- 4. Mixed Search (All types) ---")
    results_all = holo.search("live test", limit=5, doc_type_filter="all")
    print(f"Code hits: {len(results_all['code_hits'])}")
    print(f"WSP hits: {len(results_all['wsp_hits'])}")
    print(f"Test hits: {len(results_all['test_hits'])}")
    
if __name__ == "__main__":
    verify_test_integration()
