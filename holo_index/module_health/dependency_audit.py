#!/usr/bin/env python3
"""
HoloIndex Dependency Audit System
Traces all Python dependencies starting from entry points with proper __init__.py import resolution.

This module fixes the key issue where __init__.py relative imports were not properly traced,
causing false positives in orphan file detection.
"""

import ast
import os
from pathlib import Path
from typing import Dict, Set, List, Tuple

class DependencyAuditor:
    """Traces all Python dependencies starting from entry points with enhanced __init__.py support."""

    def __init__(self, root_path: str = ".", scan_path: str = None):
        self.root_path = Path(root_path)
        self.scan_path = Path(scan_path) if scan_path else self.root_path
        self.dependency_graph = {}
        self.processed_files = set()
        self.imported_files = set()
        self.all_files = set()

    def audit_dependencies(self) -> Dict:
        """Audit all Python dependencies starting from entry points."""
        print(f"Starting dependency audit from: {self.scan_path}")

        # Find all Python files in scan path
        self.all_files = self._find_all_python_files()
        print(f"Found {len(self.all_files)} Python files")

        # Find all Python entry points
        entry_points = self._find_entry_points()
        print(f"Found {len(entry_points)} entry points")

        # Trace dependencies from each entry point
        for entry_point in entry_points:
            self._trace_dependencies(entry_point)

        # Calculate orphans
        orphaned_files = self.all_files - self.imported_files

        return {
            "total_files": len(self.all_files),
            "imported_files": len(self.imported_files),
            "orphaned_files": len(orphaned_files),
            "dependency_graph": self.dependency_graph,
            "orphan_list": sorted(list(orphaned_files)),
            "imported_list": sorted(list(self.imported_files))
        }

    def _find_all_python_files(self) -> Set[str]:
        """Find all Python files in the scan path."""
        python_files = set()
        for py_file in self.scan_path.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                # Convert to relative path string for consistency
                relative_path = str(py_file.relative_to(self.root_path)).replace("\\", "/")
                python_files.add(relative_path)
        return python_files

    def _find_entry_points(self) -> List[Path]:
        """Find all Python entry points (main files, __init__.py, etc.)."""
        entry_points = []

        # Look for common entry point patterns
        patterns = [
            "main.py",
            "__main__.py",
            "app.py",
            "application.py",
            "run.py",
            "holo_index.py"  # Our main entry point
        ]

        for pattern in patterns:
            for file_path in self.scan_path.rglob(pattern):
                if file_path.is_file():
                    entry_points.append(file_path)

        # Also include all __init__.py files as they may import modules
        for init_file in self.scan_path.rglob("__init__.py"):
            entry_points.append(init_file)

        return list(set(entry_points))  # Remove duplicates

    def _trace_dependencies(self, file_path: Path):
        """Trace dependencies from a single file with enhanced relative import resolution."""
        if file_path in self.processed_files:
            return

        self.processed_files.add(file_path)

        # Mark this file as imported (reachable)
        try:
            relative_path = str(file_path.relative_to(self.root_path)).replace("\\", "/")
            self.imported_files.add(relative_path)
        except ValueError:
            pass  # File outside root path

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the AST to find imports
            tree = ast.parse(content, filename=str(file_path))
            imports = self._extract_imports(tree)

            # Store dependencies
            module_name = self._file_to_module(file_path)
            self.dependency_graph[module_name] = list(imports)

            # Recursively trace imported modules
            for imported_module in imports:
                imported_file = self._module_to_file(imported_module, context_file=file_path)
                if imported_file and imported_file.exists():
                    self._trace_dependencies(imported_file)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """Extract all import statements from AST with proper relative import handling."""
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

    def _file_to_module(self, file_path: Path) -> str:
        """Convert file path to Python module name."""
        try:
            relative_path = file_path.relative_to(self.root_path)
            module_parts = []

            for part in relative_path.parts:
                if part.endswith('.py'):
                    if part == '__init__.py':
                        continue  # Skip __init__.py in module name
                    module_parts.append(part[:-3])  # Remove .py extension
                elif part != '__pycache__':
                    module_parts.append(part)

            return '.'.join(module_parts)
        except ValueError:
            return str(file_path)

    def _module_to_file(self, module_name: str, context_file: Path = None) -> Path:
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
                self.root_path / f"{module_name.replace('.', '/')}.py",
                self.root_path / module_name.replace('.', '/') / "__init__.py"
            ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def get_dependency_stats(self) -> Dict[str, int]:
        """Get statistics about the dependency graph."""
        stats = {
            'total_modules': len(self.dependency_graph),
            'total_dependencies': sum(len(deps) for deps in self.dependency_graph.values()),
            'processed_files': len(self.processed_files)
        }

        if stats['total_modules'] > 0:
            stats['avg_dependencies_per_module'] = stats['total_dependencies'] / stats['total_modules']

        return stats

    def print_dependency_graph(self):
        """Print the dependency graph in a readable format."""
        print("\nDependency Graph:")
        print("=" * 50)

        for module, deps in sorted(self.dependency_graph.items()):
            print(f"{module}:")
            for dep in sorted(deps):
                print(f"  -> {dep}")
            print()

def main():
    """Main function for command-line usage."""
    import sys

    if len(sys.argv) > 1:
        scan_path = sys.argv[1]
    else:
        scan_path = "."

    auditor = DependencyAuditor(scan_path=scan_path)
    results = auditor.audit_dependencies()

    stats = auditor.get_dependency_stats()
    print(f"\nAudit Complete:")
    print(f"  Modules analyzed: {stats['total_modules']}")
    print(f"  Total dependencies: {stats['total_dependencies']}")
    print(f"  Files processed: {stats['processed_files']}")
    print(f"  Imported files: {results['imported_files']}")
    print(f"  Orphaned files: {results['orphaned_files']}")

    if results['orphaned_files'] > 0:
        print(f"\nOrphaned files ({results['orphaned_files']}):")
        for orphan in results['orphan_list'][:10]:  # Show first 10
            print(f"  - {orphan}")
        if len(results['orphan_list']) > 10:
            print(f"  ... and {len(results['orphan_list']) - 10} more")

if __name__ == "__main__":
    main()