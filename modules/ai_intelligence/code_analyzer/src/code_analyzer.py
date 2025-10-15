"""
Code Analyzer - WSP/WRE AI Intelligence Module

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive code analysis and testing capabilities
- WSP 54 (Agent Duties): AI-powered code analysis for autonomous development
- WSP 22 (ModLog): Change tracking and analysis history
- WSP 50 (Pre-Action Verification): Enhanced verification before code analysis

Provides AI-powered code analysis capabilities for autonomous development operations.
Enables 0102 pArtifacts to analyze code quality, complexity, and compliance.
"""

import ast
import os
import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CodeAnalysisResult:
    """Result of code analysis operation."""
    file_path: str
    complexity_score: float
    quality_score: float
    compliance_score: float
    issues: List[str]
    recommendations: List[str]
    wsp_compliance: Dict[str, bool]


@dataclass
class ExecutionGraphResult:
    """Result of execution graph tracing (snake & ladders pattern)."""
    entry_point: str
    total_modules: int
    execution_graph: Dict[str, List[str]]  # module -> list of imported modules
    module_list: List[str]  # All unique modules in execution order
    depth_map: Dict[str, int]  # module -> depth from entry point
    orphaned_modules: List[Dict[str, str]] = field(default_factory=list)  # modules in folder but not in graph
    mermaid_flowchart: str = ""  # Mermaid visualization


class CodeAnalyzer:
    """
    AI-powered code analyzer for autonomous development operations.
    
    Provides comprehensive code analysis including:
    - Complexity analysis
    - Quality assessment
    - WSP compliance checking
    - Issue identification
    - Improvement recommendations
    """
    
    def __init__(self):
        """Initialize the code analyzer with WSP compliance standards."""
        self.wsp_standards = {
            'modlog_present': False,
            'readme_present': False,
            'interface_documented': False,
            'tests_present': False,
            'proper_structure': False
        }
        
    def analyze_file(self, file_path: str) -> CodeAnalysisResult:
        """
        Analyze a single file for code quality and WSP compliance.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            CodeAnalysisResult with analysis findings
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST for complexity analysis
            tree = ast.parse(content)
            
            # Calculate complexity metrics
            complexity_score = self._calculate_complexity(tree)
            quality_score = self._assess_quality(content, tree)
            compliance_score = self._check_wsp_compliance(file_path, content)
            
            # Identify issues and recommendations
            issues = self._identify_issues(content, tree)
            recommendations = self._generate_recommendations(issues, compliance_score)
            
            return CodeAnalysisResult(
                file_path=file_path,
                complexity_score=complexity_score,
                quality_score=quality_score,
                compliance_score=compliance_score,
                issues=issues,
                recommendations=recommendations,
                wsp_compliance=self.wsp_standards.copy()
            )
            
        except Exception as e:
            return CodeAnalysisResult(
                file_path=file_path,
                complexity_score=0.0,
                quality_score=0.0,
                compliance_score=0.0,
                issues=[f"Analysis failed: {str(e)}"],
                recommendations=["Fix file access or syntax issues"],
                wsp_compliance=self.wsp_standards.copy()
            )
    
    def analyze_directory(self, directory_path: str) -> List[CodeAnalysisResult]:
        """
        Analyze all Python files in a directory.
        
        Args:
            directory_path: Path to directory to analyze
            
        Returns:
            List of CodeAnalysisResult objects
        """
        results = []
        directory = Path(directory_path)
        
        for python_file in directory.rglob("*.py"):
            if python_file.is_file():
                result = self.analyze_file(str(python_file))
                results.append(result)
                
        return results
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity of the code."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
                
        return complexity
    
    def _assess_quality(self, content: str, tree: ast.AST) -> float:
        """Assess code quality based on various metrics."""
        quality_score = 100.0
        
        # Check for docstrings
        if not self._has_docstrings(tree):
            quality_score -= 20
            
        # Check for long functions
        if self._has_long_functions(tree):
            quality_score -= 15
            
        # Check for proper naming conventions
        if not self._follows_naming_conventions(tree):
            quality_score -= 10
            
        # Check for comments
        if not self._has_adequate_comments(content):
            quality_score -= 10
            
        return max(0.0, quality_score)
    
    def _check_wsp_compliance(self, file_path: str, content: str) -> float:
        """Check WSP compliance of the file and its module structure."""
        compliance_score = 100.0
        file_path_obj = Path(file_path)
        module_dir = file_path_obj.parent.parent
        
        # Check for ModLog.md
        modlog_path = module_dir / "ModLog.md"
        self.wsp_standards['modlog_present'] = modlog_path.exists()
        if not self.wsp_standards['modlog_present']:
            compliance_score -= 25
            
        # Check for README.md
        readme_path = module_dir / "README.md"
        self.wsp_standards['readme_present'] = readme_path.exists()
        if not self.wsp_standards['readme_present']:
            compliance_score -= 20
            
        # Check for INTERFACE.md
        interface_path = module_dir / "INTERFACE.md"
        self.wsp_standards['interface_documented'] = interface_path.exists()
        if not self.wsp_standards['interface_documented']:
            compliance_score -= 15
            
        # Check for tests
        tests_dir = module_dir / "tests"
        self.wsp_standards['tests_present'] = tests_dir.exists() and any(tests_dir.rglob("*.py"))
        if not self.wsp_standards['tests_present']:
            compliance_score -= 20
            
        # Check for proper structure
        src_dir = module_dir / "src"
        self.wsp_standards['proper_structure'] = src_dir.exists()
        if not self.wsp_standards['proper_structure']:
            compliance_score -= 20
            
        return max(0.0, compliance_score)
    
    def _identify_issues(self, content: str, tree: ast.AST) -> List[str]:
        """Identify specific issues in the code."""
        issues = []
        
        # Check for missing docstrings
        if not self._has_docstrings(tree):
            issues.append("Missing module or function docstrings")
            
        # Check for long functions
        if self._has_long_functions(tree):
            issues.append("Functions exceed recommended length")
            
        # Check for naming violations
        if not self._follows_naming_conventions(tree):
            issues.append("Naming conventions not followed")
            
        # Check for WSP compliance issues
        if not all(self.wsp_standards.values()):
            missing_items = [k for k, v in self.wsp_standards.items() if not v]
            issues.append(f"Missing WSP compliance items: {', '.join(missing_items)}")
            
        return issues
    
    def _generate_recommendations(self, issues: List[str], compliance_score: float) -> List[str]:
        """Generate improvement recommendations based on issues."""
        recommendations = []
        
        for issue in issues:
            if "docstrings" in issue:
                recommendations.append("Add comprehensive docstrings to all modules and functions")
            elif "length" in issue:
                recommendations.append("Refactor long functions into smaller, focused functions")
            elif "naming" in issue:
                recommendations.append("Follow PEP 8 naming conventions")
            elif "WSP compliance" in issue:
                recommendations.append("Create missing WSP compliance files (ModLog.md, README.md, etc.)")
                
        if compliance_score < 50:
            recommendations.append("Priority: Address WSP compliance violations immediately")
        elif compliance_score < 80:
            recommendations.append("Improve WSP compliance for better integration")
            
        return recommendations
    
    def _has_docstrings(self, tree: ast.AST) -> bool:
        """Check if the code has adequate docstrings."""
        has_module_docstring = False
        has_function_docstrings = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Module) and ast.get_docstring(node):
                has_module_docstring = True
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if ast.get_docstring(node):
                    has_function_docstrings = True
                    break
                    
        return has_module_docstring and has_function_docstrings
    
    def _has_long_functions(self, tree: ast.AST) -> bool:
        """Check for functions that exceed recommended length."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.body) > 20:  # More than 20 lines
                    return True
        return False
    
    def _follows_naming_conventions(self, tree: ast.AST) -> bool:
        """Check if naming conventions are followed."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    return False
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    return False
        return True
    
    def _has_adequate_comments(self, content: str) -> bool:
        """Check if the code has adequate comments."""
        lines = content.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        comment_lines = [line for line in lines if line.strip().startswith('#')]

        if not code_lines:
            return True

        comment_ratio = len(comment_lines) / len(code_lines)
        return comment_ratio >= 0.1  # At least 10% comments

    # ========== EXECUTION GRAPH TRACING (Snake & Ladders Pattern) ==========

    def trace_execution_graph(
        self,
        entry_point: str,
        max_depth: int = 10,
        modules_root: Optional[str] = None
    ) -> ExecutionGraphResult:
        """
        Trace execution graph from entry point following ALL imports (snake & ladders).

        This implements the "CodeIndex" pattern: trace every import recursively to map
        complete execution flow from a given entry point (e.g., main.py::monitor_youtube).

        Args:
            entry_point: Starting file path (e.g., "main.py" or "main.py::monitor_youtube")
            max_depth: Maximum import depth to trace (default: 10)
            modules_root: Root directory containing modules/ folder (default: auto-detect)

        Returns:
            ExecutionGraphResult with complete execution graph, orphan detection, and visualization

        Example:
            >>> analyzer = CodeAnalyzer()
            >>> result = analyzer.trace_execution_graph("main.py", max_depth=10)
            >>> print(f"Total modules: {result.total_modules}")
            >>> print(f"Orphaned: {len(result.orphaned_modules)}")
        """
        # Parse entry point (support "file.py::function" format)
        if "::" in entry_point:
            entry_file, entry_function = entry_point.split("::", 1)
        else:
            entry_file = entry_point
            entry_function = None

        # Auto-detect modules root if not provided
        if modules_root is None:
            modules_root = self._find_modules_root(entry_file)

        # Initialize traversal state
        visited: Set[str] = set()
        execution_graph: Dict[str, List[str]] = {}
        depth_map: Dict[str, int] = {}
        queue: List[Tuple[str, int]] = [(entry_file, 0)]

        # BFS traversal (snake & ladders pattern)
        while queue:
            current_file, current_depth = queue.pop(0)

            # Skip if already visited or exceeds max depth
            if current_file in visited or current_depth > max_depth:
                continue

            visited.add(current_file)
            depth_map[current_file] = current_depth

            # Parse imports from current file
            imports = self._parse_imports(current_file, modules_root)
            execution_graph[current_file] = imports

            # Add imports to queue (follow the ladder)
            for imported_module in imports:
                if imported_module not in visited:
                    queue.append((imported_module, current_depth + 1))

        # Detect orphaned modules (in folder but not in execution graph)
        orphaned_modules = self._find_orphaned_modules(modules_root, visited)

        # Generate Mermaid flowchart visualization
        mermaid_flowchart = self._generate_mermaid_flowchart(execution_graph, depth_map)

        return ExecutionGraphResult(
            entry_point=entry_point,
            total_modules=len(visited),
            execution_graph=execution_graph,
            module_list=sorted(visited, key=lambda x: depth_map.get(x, 999)),
            depth_map=depth_map,
            orphaned_modules=orphaned_modules,
            mermaid_flowchart=mermaid_flowchart
        )

    def _parse_imports(self, file_path: str, modules_root: str) -> List[str]:
        """
        Parse all imports from a Python file using AST.

        Returns list of resolved module file paths that were imported.
        """
        imports = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content, filename=file_path)
        except Exception as e:
            # Can't parse file - return empty list
            return []

        # Extract import statements
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        # Resolve import names to actual file paths
        resolved_imports = []
        for import_name in imports:
            resolved_path = self._resolve_import_path(import_name, file_path, modules_root)
            if resolved_path:
                resolved_imports.append(resolved_path)

        return resolved_imports

    def _resolve_import_path(
        self,
        import_name: str,
        from_file: str,
        modules_root: str
    ) -> Optional[str]:
        """
        Resolve import name to actual file path following WSP 3 module structure.

        Examples:
            "modules.communication.livechat.src.livechat_core"
            -> "O:/Foundups-Agent/modules/communication/livechat/src/livechat_core.py"

            ".livechat_core" (relative import)
            -> Resolve based on from_file location
        """
        # Skip stdlib imports
        stdlib_modules = {
            'os', 'sys', 'ast', 're', 'json', 'time', 'datetime', 'pathlib',
            'typing', 'dataclasses', 'collections', 'itertools', 'functools',
            'asyncio', 'logging', 'unittest', 'tempfile', 'shutil'
        }
        first_part = import_name.split('.')[0]
        if first_part in stdlib_modules:
            return None

        # Handle relative imports (e.g., ".livechat_core")
        if import_name.startswith('.'):
            base_dir = Path(from_file).parent
            relative_parts = import_name.lstrip('.').split('.')
            for part in relative_parts:
                candidate = base_dir / f"{part}.py"
                if candidate.exists():
                    return str(candidate)
            return None

        # Handle absolute imports (e.g., "modules.communication.livechat.src.livechat_core")
        parts = import_name.split('.')

        # Try converting dots to slashes and appending .py
        for i in range(len(parts), 0, -1):
            potential_path = Path(modules_root) / '/'.join(parts[:i])

            # Try as direct file
            if potential_path.with_suffix('.py').exists():
                return str(potential_path.with_suffix('.py'))

            # Try as package __init__.py
            if (potential_path / '__init__.py').exists():
                return str(potential_path / '__init__.py')

        return None

    def _find_modules_root(self, entry_file: str) -> str:
        """
        Find the root directory containing the modules/ folder.
        Walks up from entry_file until finding modules/ directory.
        """
        current_dir = Path(entry_file).parent.absolute()

        # Walk up directory tree
        for _ in range(10):  # Max 10 levels up
            modules_dir = current_dir / "modules"
            if modules_dir.exists() and modules_dir.is_dir():
                return str(current_dir)
            current_dir = current_dir.parent

        # Fallback to current directory
        return str(Path(entry_file).parent)

    def _find_orphaned_modules(
        self,
        modules_root: str,
        visited: Set[str]
    ) -> List[Dict[str, str]]:
        """
        Find modules in modules/ folder that are NOT in execution graph.
        Returns list of orphaned modules with metadata.
        """
        orphans = []
        modules_dir = Path(modules_root) / "modules"

        if not modules_dir.exists():
            return orphans

        # Scan all .py files in modules/
        for py_file in modules_dir.rglob("*.py"):
            file_path = str(py_file)

            # Skip if in execution graph
            if file_path in visited:
                continue

            # Skip __init__.py files (not orphans)
            if py_file.name == "__init__.py":
                continue

            # Skip test files (separate concern)
            if "/tests/" in file_path or "\\tests\\" in file_path:
                continue

            # This is an orphan
            orphans.append({
                "path": file_path,
                "reason": "Not imported by any module in execution graph",
                "module": str(py_file.relative_to(modules_dir)),
                "suggested_action": "Investigate why module exists or archive if unused"
            })

        return orphans

    def _generate_mermaid_flowchart(
        self,
        execution_graph: Dict[str, List[str]],
        depth_map: Dict[str, int]
    ) -> str:
        """
        Generate Mermaid flowchart for execution graph visualization.

        Output format:
        ```mermaid
        flowchart TD
            N0[main.py] --> N1[auto_moderator_dae.py]
            N1 --> N2[stream_resolver.py]
            N1 --> N3[livechat_core.py]
        ```
        """
        mermaid = "flowchart TD\n"

        # Generate node IDs and labels
        node_ids = {}
        for i, module in enumerate(sorted(execution_graph.keys(), key=lambda x: depth_map.get(x, 999))):
            node_ids[module] = f"N{i}"
            # Shorten module name for display (just filename)
            display_name = Path(module).stem
            mermaid += f"    {node_ids[module]}[{display_name}]\n"

        # Generate edges
        for module, imports in execution_graph.items():
            if module not in node_ids:
                continue
            for imported in imports:
                if imported in node_ids:
                    mermaid += f"    {node_ids[module]} --> {node_ids[imported]}\n"

        return mermaid


def analyze_code(file_path: str) -> CodeAnalysisResult:
    """
    Convenience function to analyze a single file.
    
    Args:
        file_path: Path to the file to analyze
        
    Returns:
        CodeAnalysisResult with analysis findings
    """
    analyzer = CodeAnalyzer()
    return analyzer.analyze_file(file_path)


def analyze_module(module_path: str) -> List[CodeAnalysisResult]:
    """
    Convenience function to analyze an entire module.
    
    Args:
        module_path: Path to the module to analyze
        
    Returns:
        List of CodeAnalysisResult objects
    """
    analyzer = CodeAnalyzer()
    return analyzer.analyze_directory(module_path)


if __name__ == "__main__":
    """Test the code analyzer with a sample file."""
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        result = analyze_code(file_path)
        print(f"Analysis of {file_path}:")
        print(f"Complexity Score: {result.complexity_score}")
        print(f"Quality Score: {result.quality_score}")
        print(f"Compliance Score: {result.compliance_score}")
        print(f"Issues: {result.issues}")
        print(f"Recommendations: {result.recommendations}")
    else:
        print("Usage: python code_analyzer.py <file_path>") 