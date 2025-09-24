#!/usr/bin/env python3
"""
Focused test of the dependency auditor for just HoloIndex with main entry point
"""

from pathlib import Path
import sys
sys.path.insert(0, 'holo_index')
from module_health.dependency_audit import DependencyAuditor

def test_holoindex_audit():
    """Test dependency audit focused on HoloIndex only"""
    print("=== HoloIndex Dependency Audit Test ===")

    # Create auditor that scans holo_index but includes main holo_index.py as entry
    auditor = DependencyAuditor(root_path=".", scan_path="holo_index")

    # Manually add holo_index.py as an entry point since it's outside scan_path
    main_entry = Path("holo_index.py")
    if main_entry.exists():
        print(f"Adding main entry point: {main_entry}")
        auditor._trace_dependencies(main_entry)

    # Run the standard audit
    results = auditor.audit_dependencies()

    print(f"\nResults:")
    print(f"  Total Python files in holo_index/: {results['total_files']}")
    print(f"  Files traced/imported: {results['imported_files']}")
    print(f"  Orphaned files: {results['orphaned_files']}")

    # Show some key files we expect to be imported
    key_files = [
        'holo_index/cli.py',
        'holo_index/output/agentic_output_throttler.py',
        'holo_index/adaptive_learning/breadcrumb_tracer.py'
    ]

    print(f"\nKey file import status:")
    for key_file in key_files:
        status = "✓ IMPORTED" if key_file in results['imported_list'] else "✗ ORPHANED"
        print(f"  {status}: {key_file}")

    if results['orphaned_files'] > 0 and results['orphaned_files'] < 20:
        print(f"\nOrphaned files ({results['orphaned_files']}):")
        for orphan in sorted(results['orphan_list']):
            print(f"  - {orphan}")

    return results

if __name__ == "__main__":
    results = test_holoindex_audit()