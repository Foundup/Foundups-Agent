#!/usr/bin/env python3
"""
Module Fingerprint Generator - WSP 86 v2 Implementation
Creates semantic fingerprints for all modules to enable instant navigation

This tool scans modules and generates fingerprints containing:
- Purpose and capabilities
- Dependencies and relationships
- Patterns and complexity metrics
- Test coverage and documentation status
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ModuleFingerprintGenerator:
    """
    Generates semantic fingerprints for Python modules per WSP 86 v2.

    Fingerprints enable:
    - Instant module understanding without reading entire files
    - Graph-based navigation of codebase relationships
    - Pattern recognition and anti-vibecoding verification
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fingerprints = {}
        self.patterns = {
            "quota_handling": r"quota|QuotaExceeded|exhausted",
            "error_recovery": r"try:|except\s+\w+|retry|fallback",
            "caching": r"cache|Cache|cached|memoize",
            "api_calls": r"request\.|\.execute\(\)|api\.|youtube_client",
            "singleton": r"instance|_instance|SingleInstance",
            "async": r"async\s+def|await\s+|asyncio",
            "logging": r"logger\.|logging\.",
            "testing": r"test_|mock|Mock|assert",
        }

    def scan_module(self, module_path: Path) -> Dict[str, Any]:
        """
        Generate fingerprint for a single module.

        Returns fingerprint with:
        - Basic metadata (name, domain, size)
        - Purpose extracted from docstrings
        - Public API (functions, classes)
        - Dependencies (imports)
        - Detected patterns
        - Complexity metrics
        """
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST for structural analysis
            try:
                tree = ast.parse(content)
            except SyntaxError:
                logger.warning(f"Syntax error in {module_path}")
                tree = None

            # Extract module components
            fingerprint = {
                "id": module_path.stem,
                "path": str(module_path.relative_to(self.project_root)),
                "domain": self._get_domain(module_path),
                "purpose": self._extract_purpose(tree, content),
                "metadata": {
                    "lines": len(content.splitlines()),
                    "size_kb": len(content) / 1024,
                    "last_modified": os.path.getmtime(module_path)
                },
                "capabilities": self._extract_capabilities(tree) if tree else [],
                "dependencies": self._extract_dependencies(tree) if tree else {},
                "patterns": self._detect_patterns(content),
                "complexity": self._calculate_complexity(tree) if tree else {},
                "wsp_compliance": self._check_wsp_compliance(content, module_path)
            }

            return fingerprint

        except Exception as e:
            logger.error(f"Error scanning {module_path}: {e}")
            return None

    def _get_domain(self, module_path: Path) -> str:
        """Extract domain from module path (e.g., platform_integration)."""
        parts = module_path.parts
        if "modules" in parts:
            idx = parts.index("modules")
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return "unknown"

    def _extract_purpose(self, tree: ast.AST, content: str) -> str:
        """Extract module purpose from docstring or comments."""
        if tree and ast.get_docstring(tree):
            docstring = ast.get_docstring(tree)
            # Take first non-empty line
            for line in docstring.split('\n'):
                line = line.strip()
                if line and not line.startswith('"""'):
                    return line[:200]  # Limit length

        # Fallback: Check first few comment lines
        for line in content.splitlines()[:10]:
            if line.strip().startswith('#') and len(line.strip()) > 10:
                return line.strip('#').strip()[:200]

        return "No description available"

    def _extract_capabilities(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Extract public functions and classes."""
        capabilities = []

        for node in ast.walk(tree):
            # Functions
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):  # Public only
                    capabilities.append({
                        "type": "function",
                        "name": node.name,
                        "params": [arg.arg for arg in node.args.args],
                        "has_docstring": ast.get_docstring(node) is not None
                    })

            # Classes
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith('_'):
                    methods = [m.name for m in node.body
                              if isinstance(m, ast.FunctionDef) and not m.name.startswith('_')]
                    capabilities.append({
                        "type": "class",
                        "name": node.name,
                        "methods": methods[:10],  # Limit to 10 methods
                        "has_docstring": ast.get_docstring(node) is not None
                    })

        return capabilities[:20]  # Limit total capabilities

    def _extract_dependencies(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Extract imports and what's imported from each."""
        dependencies = {
            "stdlib": [],
            "third_party": [],
            "local": []
        }

        stdlib_modules = {'os', 'sys', 'json', 'time', 'datetime', 'logging',
                         'pathlib', 'typing', 're', 'ast', 'asyncio'}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in stdlib_modules:
                        dependencies["stdlib"].append(module)
                    elif module.startswith('modules.'):
                        dependencies["local"].append(alias.name)
                    else:
                        dependencies["third_party"].append(module)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if module in stdlib_modules:
                        if module not in dependencies["stdlib"]:
                            dependencies["stdlib"].append(module)
                    elif node.module.startswith('modules.'):
                        dependencies["local"].append(node.module)
                    else:
                        if module not in dependencies["third_party"]:
                            dependencies["third_party"].append(module)

        # Deduplicate
        for key in dependencies:
            dependencies[key] = list(set(dependencies[key]))[:10]  # Limit each

        return dependencies

    def _detect_patterns(self, content: str) -> List[str]:
        """Detect common code patterns."""
        detected = []

        for pattern_name, pattern_regex in self.patterns.items():
            if re.search(pattern_regex, content, re.IGNORECASE):
                detected.append(pattern_name)

        return detected

    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate basic complexity metrics."""
        metrics = {
            "functions": 0,
            "classes": 0,
            "methods": 0,
            "max_depth": 0,
            "branches": 0
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        metrics["methods"] += 1
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                metrics["branches"] += 1

        return metrics

    def _check_wsp_compliance(self, content: str, module_path: Path) -> Dict[str, bool]:
        """Check basic WSP compliance indicators."""
        compliance = {
            "has_docstring": content.strip().startswith('"""') or content.strip().startswith("'''"),
            "has_modlog": (module_path.parent / "ModLog.md").exists(),
            "has_tests": (module_path.parent / "tests").exists(),
            "has_readme": (module_path.parent / "README.md").exists(),
            "mentions_wsp": bool(re.search(r'WSP\s+\d+', content))
        }
        return compliance

    def scan_project(self, output_file: str = "memory/MODULE_FINGERPRINTS.json"):
        """
        Scan entire project and generate fingerprints for all Python modules.

        Saves results to JSON file for use by navigation tools.
        """
        logger.info(f"Scanning project from {self.project_root}")

        # Find all Python files in modules directory
        modules_dir = self.project_root / "modules"
        if not modules_dir.exists():
            logger.error(f"Modules directory not found: {modules_dir}")
            return

        python_files = list(modules_dir.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files")

        # Generate fingerprints
        for py_file in python_files:
            # Skip tests and __pycache__
            if "test" in py_file.name or "__pycache__" in str(py_file):
                continue

            fingerprint = self.scan_module(py_file)
            if fingerprint:
                self.fingerprints[str(py_file)] = fingerprint
                logger.debug(f"Generated fingerprint for {py_file.name}")

        # Save to JSON
        output_path = self.project_root / output_file
        with open(output_path, 'w') as f:
            json.dump(self.fingerprints, f, indent=2, default=str)

        logger.info(f"Saved {len(self.fingerprints)} fingerprints to {output_file}")

        # Generate summary
        self._print_summary()

    def _print_summary(self):
        """Print summary statistics of scanned modules."""
        if not self.fingerprints:
            return

        print("\n" + "="*60)
        print("MODULE FINGERPRINT SUMMARY")
        print("="*60)

        # Domain distribution
        domains = {}
        for fp in self.fingerprints.values():
            domain = fp["domain"]
            domains[domain] = domains.get(domain, 0) + 1

        print("\nDomains:")
        for domain, count in sorted(domains.items()):
            print(f"  {domain}: {count} modules")

        # Pattern distribution
        all_patterns = {}
        for fp in self.fingerprints.values():
            for pattern in fp["patterns"]:
                all_patterns[pattern] = all_patterns.get(pattern, 0) + 1

        print("\nCommon Patterns:")
        for pattern, count in sorted(all_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {count} modules")

        # Complexity stats
        total_lines = sum(fp["metadata"]["lines"] for fp in self.fingerprints.values())
        total_functions = sum(fp["complexity"].get("functions", 0) for fp in self.fingerprints.values())
        total_classes = sum(fp["complexity"].get("classes", 0) for fp in self.fingerprints.values())

        print(f"\nStatistics:")
        print(f"  Total modules: {len(self.fingerprints)}")
        print(f"  Total lines: {total_lines:,}")
        print(f"  Total functions: {total_functions}")
        print(f"  Total classes: {total_classes}")

        # WSP compliance
        compliant = sum(1 for fp in self.fingerprints.values()
                       if fp["wsp_compliance"]["mentions_wsp"])
        print(f"\nWSP Compliance:")
        print(f"  Modules mentioning WSP: {compliant}/{len(self.fingerprints)}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    generator = ModuleFingerprintGenerator(".")
    generator.scan_project()

    print("\n✅ Module fingerprints generated successfully!")
    print("Next steps:")
    print("1. Review MODULE_FINGERPRINTS.json")
    print("2. Build navigation graph from relationships")
    print("3. Create semantic search index")
    print("4. Integrate with Claude Code navigation")