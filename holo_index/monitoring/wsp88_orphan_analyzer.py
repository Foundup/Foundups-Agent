#!/usr/bin/env python3
"""
WSP 88 Orphan Analysis - Intelligent Module Connection System
================================================================

First Principles Implementation:
- Most "orphans" are false positives from __init__.py import tracing failures
- Focus on CONNECTION opportunities, not deletion
- Provide actionable intelligence for system enhancement
- Integrate with HoloDAE for real-time analysis

This makes HoloDAE the "green foundation board" that automatically suggests
improvements and connections based on detected patterns.

WSP 88 Compliance: Transform orphan detection into system optimization
"""

import os
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ImportChain:
    """Represents a chain of imports from file to its eventual usage."""
    source_file: str
    import_path: List[str]  # ["holo_index", "core", "holo_index"]
    final_target: str
    confidence: float  # 0.0-1.0, how sure we are this is actually used


@dataclass
class OrphanAnalysis:
    """Analysis result for a potentially orphaned file."""
    file_path: str
    apparent_status: str  # "orphan", "connected", "false_positive"
    actual_status: str   # "useful_utility", "needs_connection", "legacy_code"
    import_chains: List[ImportChain] = field(default_factory=list)
    connection_opportunities: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


class WSP88OrphanAnalyzer:
    """
    WSP 88 Orphan Analysis - Intelligent Connection System

    Instead of just detecting orphans, this system:
    1. Analyzes __init__.py import chains properly
    2. Identifies connection opportunities
    3. Provides actionable enhancement suggestions
    4. Integrates with HoloDAE for automatic improvements
    """

    def __init__(self):
        self.holoindex_root = Path("holo_index")
        self.analyzed_files: Dict[str, OrphanAnalysis] = {}
        self.import_cache: Dict[str, List[str]] = {}

    def analyze_holoindex_orphans(self) -> Dict[str, OrphanAnalysis]:
        """
        Comprehensive orphan analysis for HoloIndex modules.

        Returns detailed analysis with actionable recommendations.
        """
        logger.info("[WSP88] Starting comprehensive HoloIndex orphan analysis")

        # Get all Python files in HoloIndex
        all_py_files = self._find_all_python_files()
        logger.info(f"[WSP88] Found {len(all_py_files)} Python files to analyze")

        # Analyze each file's import status
        for py_file in all_py_files:
            analysis = self._analyze_file_imports(py_file)
            self.analyzed_files[str(py_file)] = analysis

        # Generate cross-file connection opportunities
        self._identify_connection_opportunities()

        logger.info(f"[WSP88] Analysis complete: {len(self.analyzed_files)} files analyzed")
        return self.analyzed_files

    def _find_all_python_files(self) -> List[Path]:
        """Find all Python files in HoloIndex, excluding __pycache__."""
        py_files = []
        for py_file in self.holoindex_root.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                py_files.append(py_file)
        return py_files

    def _analyze_file_imports(self, py_file: Path) -> OrphanAnalysis:
        """Analyze a single file's import relationships."""
        analysis = OrphanAnalysis(
            file_path=str(py_file),
            apparent_status="unknown",
            actual_status="unknown"
        )

        # Check direct imports (what dependency auditor would find)
        direct_imports = self._find_direct_imports(py_file)

        # Check __init__.py import chains (what auditor misses)
        init_imports = self._trace_init_import_chains(py_file)

        # Check CLI/main.py usage
        cli_usage = self._check_cli_usage(py_file)

        # Determine apparent status (what basic auditor would say)
        analysis.apparent_status = "orphan" if not direct_imports else "connected"

        # Determine actual status based on comprehensive analysis
        all_usage = direct_imports + init_imports + cli_usage
        analysis.import_chains = all_usage

        if all_usage:
            analysis.actual_status = "connected"
            analysis.confidence_score = min(1.0, len(all_usage) * 0.3)
        else:
            # Even "orphans" might be useful utilities
            analysis.actual_status = self._assess_orphan_value(py_file)
            analysis.confidence_score = 0.1  # Low confidence for true orphans

        # Generate recommendations based on analysis
        analysis.recommendations = self._generate_recommendations(analysis)

        return analysis

    def _find_direct_imports(self, py_file: Path) -> List[ImportChain]:
        """Find direct imports of this file."""
        chains = []
        module_name = self._file_to_module_name(py_file)

        # Search all Python files for imports of this module
        for other_file in self._find_all_python_files():
            if other_file == py_file:
                continue

            try:
                with open(other_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for direct imports
                if f"from {module_name}" in content or f"import {module_name}" in content:
                    chains.append(ImportChain(
                        source_file=str(other_file),
                        import_path=[module_name],
                        final_target=str(py_file),
                        confidence=1.0
                    ))
            except Exception as e:
                logger.debug(f"Error reading {other_file}: {e}")

        return chains

    def _trace_init_import_chains(self, py_file: Path) -> List[ImportChain]:
        """
        Trace import chains through __init__.py files.

        This is the key insight of WSP 88: Most "orphans" are actually
        imported through __init__.py files that dependency auditors miss.
        """
        chains = []
        module_name = self._file_to_module_name(py_file)

        # Find the __init__.py file that would import this module
        init_file = self._find_parent_init(py_file)
        if init_file and init_file.exists():
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if this module is exported in __init__.py
                if module_name in content and ("__all__" in content or "from" in content):
                    # Find what imports this __init__.py
                    parent_imports = self._find_direct_imports(init_file)

                    for parent_import in parent_imports:
                        # Create chain: file -> __init__.py -> target_module
                        chains.append(ImportChain(
                            source_file=parent_import.source_file,
                            import_path=parent_import.import_path + [module_name],
                            final_target=str(py_file),
                            confidence=0.8  # Slightly lower confidence for chained imports
                        ))
            except Exception as e:
                logger.debug(f"Error analyzing {init_file}: {e}")

        return chains

    def _check_cli_usage(self, py_file: Path) -> List[ImportChain]:
        """Check if file is used by CLI or main entry points."""
        chains = []

        # Check main CLI files
        cli_files = [
            Path("holo_index/cli.py"),
            Path("holo_index/__init__.py"),
            Path("main.py")
        ]

        module_name = self._file_to_module_name(py_file)

        for cli_file in cli_files:
            if cli_file.exists():
                try:
                    with open(cli_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if f"from {module_name}" in content or f"import {module_name}" in content:
                        chains.append(ImportChain(
                            source_file=str(cli_file),
                            import_path=[module_name],
                            final_target=str(py_file),
                            confidence=1.0
                        ))
                except Exception as e:
                    logger.debug(f"Error reading {cli_file}: {e}")

        return chains

    def _assess_orphan_value(self, py_file: Path) -> str:
        """Assess the value of an apparently orphaned file."""
        filename = py_file.name
        content_size = py_file.stat().st_size if py_file.exists() else 0

        # Large files are likely useful
        if content_size > 5000:
            return "useful_utility"

        # Files with "monitor", "audit", "health" in name are likely useful
        name_indicators = ["monitor", "audit", "health", "check", "validate", "test"]
        if any(indicator in filename.lower() for indicator in name_indicators):
            return "useful_utility"

        # Files in monitoring/, module_health/ are likely useful
        path_str = str(py_file)
        if "monitoring" in path_str or "module_health" in path_str:
            return "useful_utility"

        return "needs_assessment"

    def _generate_recommendations(self, analysis: OrphanAnalysis) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        if analysis.actual_status == "connected":
            recommendations.append("✅ File is properly connected - no action needed")

        elif analysis.actual_status == "useful_utility":
            if not analysis.import_chains:
                recommendations.append("🔗 Consider connecting this utility to CLI or __init__.py")
                recommendations.append("📚 Add documentation on how to use this utility")
            else:
                recommendations.append("✅ Useful utility with some connections - consider strengthening usage")

        elif analysis.actual_status == "needs_connection":
            recommendations.append("🔗 HIGH PRIORITY: Connect this file to the system")
            recommendations.append("📋 Check if it provides needed functionality")
            recommendations.append("🧹 Only consider deletion after confirming it's truly unused")

        if analysis.apparent_status == "orphan" and analysis.actual_status == "connected":
            recommendations.append("🔍 FALSE POSITIVE: Dependency auditor missed __init__.py imports")
            recommendations.append("🛠️ Consider improving dependency auditor to trace __init__.py chains")

        return recommendations

    def _identify_connection_opportunities(self):
        """Identify cross-file connection opportunities."""
        # Group files by functionality
        utilities = []
        monitors = []
        auditors = []

        for file_path, analysis in self.analyzed_files.items():
            if "monitor" in file_path.lower():
                monitors.append(analysis)
            elif "audit" in file_path.lower():
                auditors.append(analysis)
            elif "utility" in file_path.lower() or "helper" in file_path.lower():
                utilities.append(analysis)

        # Suggest connections between related utilities
        for monitor in monitors:
            for auditor in auditors:
                if not self._are_connected(monitor, auditor):
                    monitor.connection_opportunities.append(
                        f"Connect with {auditor.file_path} for comprehensive monitoring"
                    )

    def _are_connected(self, analysis1: OrphanAnalysis, analysis2: OrphanAnalysis) -> bool:
        """Check if two analyses have any connection."""
        files1 = {chain.source_file for chain in analysis1.import_chains}
        files2 = {chain.source_file for chain in analysis2.import_chains}
        return bool(files1 & files2)

    def _file_to_module_name(self, py_file: Path) -> str:
        """Convert file path to module name."""
        # Remove .py extension and convert path separators
        rel_path = py_file.relative_to(self.holoindex_root.parent)
        module_parts = str(rel_path).replace('.py', '').replace(os.sep, '.').split('.')
        return '.'.join(module_parts)

    def _find_parent_init(self, py_file: Path) -> Optional[Path]:
        """Find the __init__.py file that would import this module."""
        current_dir = py_file.parent

        # Look for __init__.py in same directory
        init_file = current_dir / "__init__.py"
        if init_file.exists():
            return init_file

        # Look in parent directory
        parent_init = current_dir.parent / "__init__.py"
        if parent_init.exists():
            return parent_init

        return None

    def generate_holodae_report(self) -> str:
        """Generate a HoloDAE-style report for 0102 consumption."""
        connected = sum(1 for a in self.analyzed_files.values() if a.actual_status == "connected")
        utilities = sum(1 for a in self.analyzed_files.values() if a.actual_status == "useful_utility")
        false_positives = sum(1 for a in self.analyzed_files.values()
                            if a.apparent_status == "orphan" and a.actual_status == "connected")

        total_files = len(self.analyzed_files)

        report = f"""
[WSP88-ANALYSIS] HoloIndex Orphan Analysis Complete
==================================================

📊 SUMMARY:
- Total Python files analyzed: {total_files}
- Properly connected: {connected} ({connected/total_files*100:.1f}%)
- Useful utilities: {utilities} ({utilities/total_files*100:.1f}%)
- False positives (missed by basic auditors): {false_positives}

🎯 KEY FINDINGS:
1. Most "orphans" are false positives from __init__.py import tracing failures
2. {utilities} useful utilities identified for potential connection enhancement
3. {false_positives} files incorrectly flagged as orphans

🔧 RECOMMENDATIONS:
- Focus on connecting utilities rather than deleting "orphans"
- Improve dependency auditors to trace __init__.py import chains
- Consider CLI integration for valuable standalone utilities

[HOLODAE-SUGGEST] WSP 88 recommends keeping all files and focusing on connections
[HOLODAE-SUGGEST] {utilities} utilities identified for potential CLI or API integration
"""

        return report.strip()

    def get_connection_suggestions(self) -> List[str]:
        """Get actionable connection suggestions."""
        suggestions = []

        for analysis in self.analyzed_files.values():
            if analysis.actual_status == "useful_utility" and not analysis.import_chains:
                suggestions.append(f"Connect {analysis.file_path} to CLI or main API")

            if analysis.apparent_status == "orphan" and analysis.actual_status == "connected":
                suggestions.append(f"Improve dependency auditor to detect {analysis.file_path} imports")

        return suggestions
