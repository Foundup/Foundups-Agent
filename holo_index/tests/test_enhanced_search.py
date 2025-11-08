#!/usr/bin/env python3
"""Test enhanced HoloIndex search with path/line/snippet
WSP 3 Compliant - Located in proper holo_index test directory"""

import sys
from pathlib import Path

# WSP 3 compliant path setup
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from holo_index.core.holo_index import HoloIndex

def test_enhanced_search():
    holo = HoloIndex(quiet=True)
    results = holo.search('quiz timer', limit=2)

    print("Code results with enhanced info:")
    for hit in results.get('code', []):
        path = hit.get('path', 'unknown')
        line = hit.get('line', '?')
        snippet = hit.get('snippet', '')[:50]
        print(f"  {path}:{line} - {snippet}...")

    print("\nWSP results:")
    for hit in results.get('wsps', []):
        print(f"  {hit.get('title', 'unknown')} - {hit.get('summary', '')[:50]}...")

if __name__ == "__main__":
    test_enhanced_search()
