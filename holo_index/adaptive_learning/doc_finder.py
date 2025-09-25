"""
Documentation Finder for HoloIndex
Finds and presents related documentation for search results

This module:
1. Maps search results to related docs
2. Finds README, INTERFACE, ModLog files
3. Shows implementation examples
4. Links to WSP protocols
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class DocFinder:
    """Finds related documentation for search results."""

    def __init__(self):
        self.root = Path(".")
        self.doc_patterns = [
            "README.md",
            "INTERFACE.md",
            "ModLog.md",
            "CLAUDE.md",
            "ROADMAP.md",
            "**/docs/*.md",
            "**/docs/**/*.md"
        ]

    def find_related_docs(self, search_query: str, search_results: List[Dict]) -> List[Dict]:
        """
        Find documentation related to search results.

        Args:
            search_query: Original search query
            search_results: Results from HoloIndex search

        Returns:
            List of related documentation with paths and descriptions
        """
        related_docs = []

        # Extract modules from search results
        modules = self._extract_modules(search_results)

        for module_path in modules:
            # Look for docs in module directory
            docs = self._find_module_docs(module_path)
            related_docs.extend(docs)

        # Add WSP documentation if relevant
        wsp_docs = self._find_wsp_docs(search_query, search_results)
        related_docs.extend(wsp_docs)

        # Remove duplicates
        seen_paths = set()
        unique_docs = []
        for doc in related_docs:
            if doc['path'] not in seen_paths:
                seen_paths.add(doc['path'])
                unique_docs.append(doc)

        return unique_docs

    def _extract_modules(self, search_results: List[Dict]) -> List[str]:
        """Extract unique module paths from search results."""
        modules = set()

        for result in search_results:
            # Extract module from file path
            if 'file_path' in result:
                path = Path(result['file_path'])
                # Find module root (contains README.md or __init__.py)
                module_path = self._find_module_root(path)
                if module_path:
                    modules.add(str(module_path))

            # Extract module from import statements
            if 'module' in result:
                modules.add(result['module'])

            # Extract from function references
            if 'function_path' in result:
                # Parse module.path.to.function
                parts = result['function_path'].split('.')
                if len(parts) > 2:
                    # Reconstruct module path
                    module = '.'.join(parts[:-2])
                    modules.add(module.replace('.', '/'))

        return list(modules)

    def _find_module_root(self, file_path: Path) -> Optional[Path]:
        """Find the module root directory for a file."""
        current = file_path.parent if file_path.is_file() else file_path

        # Walk up to find module root
        while current != self.root:
            # Check if this is a module root
            if (current / "README.md").exists() or (current / "__init__.py").exists():
                return current
            current = current.parent

        return None

    def _find_module_docs(self, module_path: str) -> List[Dict]:
        """Find documentation files in a module."""
        docs = []
        module_dir = Path(module_path)

        if not module_dir.exists():
            # Try to construct path from module notation
            module_dir = Path(module_path.replace('.', '/'))
            if not module_dir.exists():
                module_dir = Path("modules") / module_path.replace('.', '/')

        if not module_dir.exists():
            return docs

        # Look for standard documentation files
        doc_files = [
            ("README.md", "Module overview and purpose"),
            ("INTERFACE.md", "Public API documentation"),
            ("ModLog.md", "Module change history"),
            ("CLAUDE.md", "Module-specific 0102 instructions"),
            ("ROADMAP.md", "Development roadmap"),
        ]

        for doc_name, description in doc_files:
            doc_path = module_dir / doc_name
            if doc_path.exists():
                docs.append({
                    'path': str(doc_path),
                    'type': doc_name.replace('.md', ''),
                    'description': description,
                    'module': module_path
                })

        # Look in docs directory
        docs_dir = module_dir / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.glob("*.md"):
                docs.append({
                    'path': str(doc_file),
                    'type': 'documentation',
                    'description': f"Documentation: {doc_file.stem}",
                    'module': module_path
                })

        # Look in tests directory for test documentation
        tests_dir = module_dir / "tests"
        if tests_dir.exists():
            test_readme = tests_dir / "README.md"
            if test_readme.exists():
                docs.append({
                    'path': str(test_readme),
                    'type': 'test_documentation',
                    'description': "Test documentation and examples",
                    'module': module_path
                })

        return docs

    def _find_wsp_docs(self, query: str, results: List[Dict]) -> List[Dict]:
        """Find relevant WSP documentation."""
        wsp_docs = []

        # Check if query or results mention WSP
        query_lower = query.lower()
        mentions_wsp = 'wsp' in query_lower

        # Check results for WSP references
        if not mentions_wsp:
            for result in results:
                if 'wsp' in str(result).lower():
                    mentions_wsp = True
                    break

        if mentions_wsp:
            # Look for WSP documentation files
            wsp_files = [
                ("WSP_MASTER_INDEX.md", "Complete WSP protocol index"),
                ("WSP_CORE.md", "Core WSP protocols"),
                ("WSP_framework.md", "WSP framework documentation"),
            ]

            for wsp_file, description in wsp_files:
                wsp_path = Path(wsp_file)
                if wsp_path.exists():
                    wsp_docs.append({
                        'path': str(wsp_path),
                        'type': 'wsp_protocol',
                        'description': description,
                        'module': 'WSP Framework'
                    })

            # Check WSP_framework directory
            wsp_dir = Path("WSP_framework")
            if wsp_dir.exists():
                for wsp_doc in wsp_dir.glob("WSP_*.md"):
                    # Extract WSP number if present
                    wsp_num = self._extract_wsp_number(wsp_doc.stem)
                    if wsp_num:
                        desc = f"WSP {wsp_num} protocol documentation"
                    else:
                        desc = f"WSP documentation: {wsp_doc.stem}"

                    wsp_docs.append({
                        'path': str(wsp_doc),
                        'type': 'wsp_protocol',
                        'description': desc,
                        'module': 'WSP Framework'
                    })

        return wsp_docs

    def _extract_wsp_number(self, filename: str) -> Optional[str]:
        """Extract WSP number from filename."""
        # Pattern: WSP_XX_Name or WSP_XX
        parts = filename.split('_')
        if len(parts) >= 2 and parts[0] == 'WSP':
            try:
                # Try to parse as number
                int(parts[1])
                return parts[1]
            except ValueError:
                pass
        return None

    def format_docs_for_display(self, docs: List[Dict]) -> str:
        """Format documentation list for display."""
        if not docs:
            return "No related documentation found."

        output = []
        output.append("📚 Related Documentation:")
        output.append("")

        # Group by module
        by_module = {}
        for doc in docs:
            module = doc.get('module', 'General')
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(doc)

        for module, module_docs in by_module.items():
            output.append(f"### {module}")
            for doc in module_docs:
                doc_type = doc.get('type', 'doc').upper()
                path = doc.get('path', '')
                desc = doc.get('description', '')
                output.append(f"- [{doc_type}] {path}")
                if desc:
                    output.append(f"  {desc}")
            output.append("")

        return "\n".join(output)

    def get_implementation_examples(self, module_path: str) -> List[Tuple[str, str]]:
        """Get implementation examples from module tests."""
        examples = []

        # Construct test directory path
        module_dir = Path(module_path.replace('.', '/'))
        if not module_dir.exists():
            module_dir = Path("modules") / module_path.replace('.', '/')

        tests_dir = module_dir / "tests"
        if not tests_dir.exists():
            return examples

        # Look for test files with examples
        for test_file in tests_dir.glob("test_*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Extract docstring examples
                    if '"""' in content:
                        # Simple extraction of first docstring
                        start = content.find('"""')
                        if start != -1:
                            end = content.find('"""', start + 3)
                            if end != -1:
                                example = content[start + 3:end].strip()
                                if 'example' in example.lower() or 'usage' in example.lower():
                                    examples.append((str(test_file), example))

            except Exception as e:
                logger.debug(f"Failed to read {test_file}: {e}")
                continue

        return examples

    def find_breadcrumbs(self, module_path: str) -> Dict[str, List[str]]:
        """Find breadcrumb trails in module documentation."""
        breadcrumbs = {
            'setup': [],
            'usage': [],
            'testing': [],
            'integration': []
        }

        module_dir = Path(module_path.replace('.', '/'))
        if not module_dir.exists():
            module_dir = Path("modules") / module_path.replace('.', '/')

        if not module_dir.exists():
            return breadcrumbs

        # Check README for setup/usage breadcrumbs
        readme = module_dir / "README.md"
        if readme.exists():
            try:
                with open(readme, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                    current_section = None
                    for line in lines:
                        line_lower = line.lower()

                        # Detect sections
                        if line.startswith('#'):
                            if 'setup' in line_lower or 'install' in line_lower:
                                current_section = 'setup'
                            elif 'usage' in line_lower or 'example' in line_lower:
                                current_section = 'usage'
                            elif 'test' in line_lower:
                                current_section = 'testing'
                            elif 'integration' in line_lower:
                                current_section = 'integration'

                        # Collect numbered steps or bullet points
                        elif current_section and (line.strip().startswith(('1.', '2.', '3.', '-', '*'))):
                            breadcrumbs[current_section].append(line.strip())

            except Exception as e:
                logger.debug(f"Failed to read README: {e}")

        return breadcrumbs


# Example usage
if __name__ == "__main__":
    finder = DocFinder()

    # Example search results
    example_results = [
        {
            'file_path': 'modules/communication/livechat/src/auto_moderator_dae.py',
            'function_path': 'modules.communication.livechat.src.auto_moderator_dae.connect',
            'module': 'modules.communication.livechat'
        }
    ]

    # Find related docs
    docs = finder.find_related_docs("youtube dae connect", example_results)

    # Format for display
    formatted = finder.format_docs_for_display(docs)
    print(formatted)

    # Get examples
    module = "modules.communication.livechat"
    examples = finder.get_implementation_examples(module)
    if examples:
        print("\n📝 Implementation Examples:")
        for file_path, example in examples:
            print(f"\nFrom {file_path}:")
            print(example)

    # Get breadcrumbs
    breadcrumbs = finder.find_breadcrumbs(module)
    if any(breadcrumbs.values()):
        print("\n🍞 Breadcrumb Trail:")
        for category, crumbs in breadcrumbs.items():
            if crumbs:
                print(f"\n{category.title()}:")
                for crumb in crumbs:
                    print(f"  {crumb}")