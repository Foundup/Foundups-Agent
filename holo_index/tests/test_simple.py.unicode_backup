#!/usr/bin/env python3
"""
Simple dependency import testing for holo_index module
WSP 3 Compliant: Located in holo_index/tests/ per proper module organization
WSP 5 Compliant: Testing standards for dependency resolution
"""

import ast
from pathlib import Path
import sys
import os

# Add project root to path for testing
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def extract_imports(tree: ast.AST) -> set:
    """Extract all import statements from AST."""
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)  # Keep full module path
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                # Handle relative imports by preserving the level
                imports.add(node.module)

    return imports

def test_dependency_imports():
    """Test basic dependency import resolution for holo_index."""
    print("=== HoloIndex Simple Dependency Test ===")

    # Test importing core holo_index components
    try:
        from holo_index.module_health.dependency_audit import DependencyAuditor
        print("✅ Successfully imported DependencyAuditor")
    except ImportError as e:
        print(f"❌ Failed to import DependencyAuditor: {e}")
        return False

    # Test basic functionality
    try:
        auditor = DependencyAuditor(root_path=".", scan_path="holo_index")
        print("✅ Successfully created DependencyAuditor instance")
    except Exception as e:
        print(f"❌ Failed to create DependencyAuditor: {e}")
        return False

    print("✅ All basic dependency imports working")
    return True

def test_module_parsing():
    """Test AST parsing of holo_index modules."""
    print("\n=== Module Parsing Test ===")

    # Test parsing a holo_index file
    holo_index_path = Path(__file__).parent.parent / "module_health" / "dependency_audit.py"

    if not holo_index_path.exists():
        print(f"❌ Test file not found: {holo_index_path}")
        return False

    try:
        with open(holo_index_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        tree = ast.parse(source_code)
        imports = extract_imports(tree)

        print(f"✅ Successfully parsed {holo_index_path.name}")
        print(f"   Found {len(imports)} import statements:")
        for imp in sorted(imports)[:5]:  # Show first 5
            print(f"   - {imp}")

        return True

    except Exception as e:
        print(f"❌ Failed to parse module: {e}")
        return False

if __name__ == "__main__":
    print("Running HoloIndex Simple Tests...")
    print("WSP 3 Compliant: Located in holo_index/tests/")
    print("WSP 5 Compliant: Testing dependency resolution\n")

    success = True
    success &= test_dependency_imports()
    success &= test_module_parsing()

    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
