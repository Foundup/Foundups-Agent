#!/usr/bin/env python3
"""
Test script to verify the dependency auditor can now handle __init__.py imports
"""

# Import the DependencyAuditor directly to avoid corrupted import chain
import sys
sys.path.insert(0, 'holo_index')
from module_health.dependency_audit import DependencyAuditor

def test_dependency_resolution():
    """Test that the dependency auditor can resolve __init__.py imports"""
    print("Testing enhanced dependency auditor with __init__.py import resolution...")

    # Create auditor focused on holo_index only
    auditor = DependencyAuditor(root_path=".", scan_path="holo_index")

    # Test the new _module_to_file method directly
    from pathlib import Path

    # Test cases for relative import resolution
    test_cases = [
        # (module_name, context_file, expected_result_pattern)
        (".agentic_output_throttler", Path("holo_index/output/__init__.py"), "agentic_output_throttler.py"),
        ("holo_index.output.agentic_output_throttler", None, "agentic_output_throttler.py"),
        (".breadcrumb_tracer", Path("holo_index/adaptive_learning/__init__.py"), "breadcrumb_tracer.py"),
    ]

    print("\nTesting relative import resolution:")
    for module_name, context_file, expected_pattern in test_cases:
        resolved_file = auditor._module_to_file(module_name, context_file)
        if resolved_file:
            print(f"  ✓ {module_name} -> {resolved_file}")
            if expected_pattern in str(resolved_file):
                print(f"    ✓ Contains expected pattern: {expected_pattern}")
            else:
                print(f"    ✗ Expected pattern '{expected_pattern}' not found")
        else:
            print(f"  ✗ {module_name} -> NOT RESOLVED")

    print("\nTesting import extraction from actual files:")

    # Test import extraction from output/__init__.py
    output_init = Path("holo_index/output/__init__.py")
    if output_init.exists():
        try:
            import ast
            with open(output_init, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            imports = auditor._extract_imports(tree)
            print(f"  {output_init}: {imports}")
        except Exception as e:
            print(f"  Error reading {output_init}: {e}")

    print("\nDone!")

if __name__ == "__main__":
    test_dependency_resolution()