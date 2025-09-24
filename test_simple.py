#!/usr/bin/env python3
"""
Simple test to verify the dependency auditor __init__.py import resolution
"""

import ast
from pathlib import Path

# Copy the key methods from our enhanced dependency auditor
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
                if node.level > 0:
                    # Construct the full relative import with proper dots
                    relative_import = '.' * node.level + node.module
                    imports.add(relative_import)
                else:
                    imports.add(node.module)
            elif node.level > 0:
                # Relative import without module (like: from . import something)
                imports.add('.' * node.level)

    return imports

def module_to_file(module_name: str, context_file: Path = None, root_path: Path = Path(".")) -> Path:
    """Convert Python module name to file path, handling relative imports."""
    if module_name.startswith('.'):
        # Handle relative imports
        if context_file is None:
            return None

        # Get the directory containing the context file
        context_dir = context_file.parent

        # Count the number of dots to determine how many levels to go up
        dots = len(module_name) - len(module_name.lstrip('.'))
        remaining_module = module_name.lstrip('.')

        # Go up the required number of levels
        target_dir = context_dir
        for _ in range(dots - 1):
            target_dir = target_dir.parent
            if target_dir == target_dir.parent:  # Reached filesystem root
                return None

        if remaining_module:
            # There's a module name after the dots
            possible_paths = [
                target_dir / f"{remaining_module.replace('.', '/')}.py",
                target_dir / remaining_module.replace('.', '/') / "__init__.py"
            ]
        else:
            # Just dots, referring to the package itself
            possible_paths = [target_dir / "__init__.py"]
    else:
        # Absolute import
        possible_paths = [
            root_path / f"{module_name.replace('.', '/')}.py",
            root_path / module_name.replace('.', '/') / "__init__.py"
        ]

    for path in possible_paths:
        if path.exists():
            return path

    return None

def test_dependency_resolution():
    """Test that our enhanced resolution logic works"""
    print("Testing enhanced dependency auditor __init__.py import resolution...")

    # Test cases for relative import resolution
    test_cases = [
        # (module_name, context_file, expected_result_pattern)
        (".agentic_output_throttler", Path("holo_index/output/__init__.py"), "agentic_output_throttler.py"),
        ("agentic_output_throttler", Path("holo_index/output/__init__.py"), "agentic_output_throttler.py"),
        (".breadcrumb_tracer", Path("holo_index/adaptive_learning/__init__.py"), "breadcrumb_tracer.py"),
    ]

    print("\n=== Testing relative import resolution ===")
    for module_name, context_file, expected_pattern in test_cases:
        resolved_file = module_to_file(module_name, context_file)
        status = "✓" if resolved_file else "✗"
        print(f"  {status} '{module_name}' from {context_file.name} -> {resolved_file}")

        if resolved_file and expected_pattern in str(resolved_file):
            print(f"    ✓ Contains expected pattern: {expected_pattern}")
        elif resolved_file:
            print(f"    ? Pattern '{expected_pattern}' not found but file exists")

    print("\n=== Testing import extraction from actual __init__.py files ===")

    # Test import extraction from output/__init__.py
    init_files_to_test = [
        Path("holo_index/output/__init__.py"),
        Path("holo_index/adaptive_learning/__init__.py"),
    ]

    for init_file in init_files_to_test:
        if init_file.exists():
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                imports = extract_imports(tree)
                print(f"  {init_file}: {imports}")

                # Test resolving each import
                for imp in imports:
                    resolved = module_to_file(imp, context_file=init_file)
                    status = "✓" if resolved else "✗"
                    print(f"    {status} {imp} -> {resolved}")

            except Exception as e:
                print(f"  Error reading {init_file}: {e}")
        else:
            print(f"  ✗ {init_file} does not exist")

    print("\nTest completed!")

if __name__ == "__main__":
    test_dependency_resolution()