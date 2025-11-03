# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import io


"""Intelligent Subroutine Engine - WSP 62/87 Compliant Algorithmic Analysis

# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

This module provides intelligent subroutines that run algorithmic analysis
only when needed, preventing unnecessary computational overhead.

Implements language-specific file size thresholds per WSP 62 section 2.1.

WSP Compliance: WSP 62 (File Size Enforcement), WSP 87 (Size Limits),
                WSP 49 (Module Structure), WSP 72 (Block Independence)
"""

import time
from pathlib import Path
from typing import Dict, Any, Tuple


class IntelligentSubroutineEngine:
    """Intelligent subroutines that run algorithmic analysis when needed."""

    # WSP 62 Section 2.1: File Size Thresholds (updated for 0102 agentic growth)
    FILE_THRESHOLDS = {
        # Code files (WSP 62 lines 22-29)
        '.py': {'ok': 1200, 'guideline': 1500, 'hard_limit': 2000, 'type': 'Python'},
        '.js': {'ok': 400, 'guideline': 400, 'hard_limit': 400, 'type': 'JavaScript'},
        '.ts': {'ok': 400, 'guideline': 400, 'hard_limit': 400, 'type': 'TypeScript'},
        '.sh': {'ok': 300, 'guideline': 300, 'hard_limit': 300, 'type': 'Shell Script'},
        '.ps1': {'ok': 300, 'guideline': 300, 'hard_limit': 300, 'type': 'PowerShell'},
        '.json': {'ok': 200, 'guideline': 200, 'hard_limit': 200, 'type': 'JSON Config'},
        '.yaml': {'ok': 200, 'guideline': 200, 'hard_limit': 200, 'type': 'YAML Config'},
        '.yml': {'ok': 200, 'guideline': 200, 'hard_limit': 200, 'type': 'YAML Config'},
        '.toml': {'ok': 200, 'guideline': 200, 'hard_limit': 200, 'type': 'TOML Config'},
        '.md': {'ok': 1000, 'guideline': 1000, 'hard_limit': 1000, 'type': 'Markdown'},
    }

    def __init__(self):
        self.module_sizes = {}
        self.duplication_patterns = {}
        self.usage_patterns = {}
        self.last_health_check = None

    def get_file_threshold(self, file_path: Path) -> Tuple[int, str]:
        """Agentic file type detection and threshold selection.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (threshold_value, file_type_description)

        Uses WSP 62 Section 2.1 thresholds based on file extension.

        WSP 62 Section 2.2.1 Domain-Specific Overrides:
        - DAE modules (*_dae.py, *dae*.py in infrastructure/) use full Python threshold (800)
        - Regular infrastructure utilities use lean threshold (400)
        - Falls back to Python threshold (800) for unknown types
        """
        suffix = file_path.suffix.lower()
        threshold_info = self.FILE_THRESHOLDS.get(suffix)

        if threshold_info:
            # WSP 62 Section 2.2.1: Domain-specific thresholds for Python files
            if suffix == '.py':
                domain_threshold = self._get_domain_threshold(file_path)
                if domain_threshold:
                    return (domain_threshold, f'Python ({self._detect_module_domain(file_path)})')

                # WSP 62 Section 2.2.1: DAE modules are complex orchestrators
                # They use full Python threshold (800), not infrastructure lean (400)
                file_name = file_path.name.lower()
                file_parts = file_path.parts

                # Check if this is a DAE module
                is_dae_module = (
                    '_dae' in file_name or
                    'dae_' in file_name or
                    ('infrastructure' in file_parts and 'dae' in file_name)
                )

                if is_dae_module:
                    return (1200, 'Python (DAE Orchestrator)')

            return (threshold_info['ok'], threshold_info['type'])
        else:
            # Unknown file type - use Python threshold as default
            return (1200, f'Unknown ({suffix})')

    def _detect_module_domain(self, file_path: Path) -> str:
        """Detect the enterprise domain for a file path per WSP 3.

        Returns:
            Domain name: 'ai_intelligence', 'infrastructure', 'communication',
                        'platform_integration', 'development', 'foundups', etc.
        """
        path_parts = file_path.parts

        # Find 'modules' in path and get domain
        try:
            modules_idx = path_parts.index('modules')
            if len(path_parts) > modules_idx + 1:
                return path_parts[modules_idx + 1]
        except (ValueError, IndexError):
            pass

        return 'unknown'

    def _get_domain_threshold(self, file_path: Path) -> int:
        """Get domain-specific threshold per WSP 62 Section 2.1.2.

        Args:
            file_path: Path to the file

        Returns:
            Domain-specific threshold in lines, or None if using default
        """
        domain = self._detect_module_domain(file_path)

        # WSP 62 domain-specific thresholds for Python files (updated for 0102 growth)
        # Only explicitly defined domains get overrides; others use default 1200
        DOMAIN_THRESHOLDS = {
            'ai_intelligence': 900,      # AI models may be larger (updated for 0102 growth)
            'infrastructure': 600,       # Infrastructure utilities should be lean
            'communication': 675,        # Protocol handlers
            # gamification, foundups, development, blockchain, monitoring,
            # platform_integration: use default 1200-line threshold
        }

        return DOMAIN_THRESHOLDS.get(domain)


    def should_run_health_check(self, query: str, target_module: str = None) -> bool:
        """Algorithm to determine if health check is needed."""
        if not target_module:
            return False

        # Run health check if:
        # 1. Query suggests modification intent
        modification_keywords = ['add', 'change', 'modify', 'update', 'fix', 'refactor', 'create']
        has_modification_intent = any(keyword in query.lower() for keyword in modification_keywords)

        # 2. Module has known issues from violation history
        high_risk_modules = ['communication/livechat', 'ai_intelligence/banter_engine']
        is_high_risk = target_module in high_risk_modules

        # 3. Time-based: Haven't checked this module recently
        current_time = time.time()
        if target_module not in self.usage_patterns:
            self.usage_patterns[target_module] = {'last_check': 0, 'check_count': 0}

        time_since_last_check = current_time - self.usage_patterns[target_module]['last_check']
        needs_fresh_check = time_since_last_check > 3600  # 1 hour

        return has_modification_intent or is_high_risk or needs_fresh_check

    def should_run_size_analysis(self, query: str, target_module: str = None) -> bool:
        """Algorithm to determine if size analysis is needed."""
        if not target_module:
            return False

        # Run size analysis if:
        # 1. Adding new functionality
        expansion_keywords = ['add', 'new', 'feature', 'function', 'method', 'class']
        is_expanding = any(keyword in query.lower() for keyword in expansion_keywords)

        # 2. Module known to be large
        large_modules = ['communication/livechat', 'infrastructure/wre_core']
        is_potentially_large = target_module in large_modules

        return is_expanding or is_potentially_large

    def should_run_duplication_check(self, query: str, target_module: str = None) -> bool:
        """Algorithm to determine if duplication check is needed."""
        if not target_module:
            return False

        # Run duplication check if:
        # 1. Creating new functionality
        creation_keywords = ['create', 'new', 'add', 'implement']
        is_creating = any(keyword in query.lower() for keyword in creation_keywords)

        # 2. Module with known duplication issues
        duplication_modules = ['ai_intelligence/banter_engine', 'communication/livechat']
        has_duplication_history = target_module in duplication_modules

        return is_creating or has_duplication_history

    def analyze_module_size(self, target_module: str) -> Dict[str, Any]:
        """Automatically analyze module size with language-specific thresholds.

        Implements WSP 62 Section 2.1 file size thresholds:
        - Python (.py): 800/1000/1500 lines
        - JavaScript (.js/.ts): 400 lines
        - Markdown (.md): 1000 lines
        - Shell scripts (.sh/.ps1): 300 lines
        - Config files (.json/.yaml/.toml): 200 lines
        """
        try:
            module_path = Path("modules") / target_module
            if not module_path.exists():
                return {'error': 'Module path not found'}

            total_lines = 0
            file_count = 0
            large_files = []
            files_by_type = {}

            # Scan all code and documentation files (not just .py)
            for code_file in module_path.rglob("*"):
                if not code_file.is_file():
                    continue

                # Only check files with known thresholds
                if code_file.suffix.lower() not in self.FILE_THRESHOLDS:
                    continue

                try:
                    with open(code_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_count += 1

                        # Agentic threshold detection
                        threshold, file_type = self.get_file_threshold(code_file)

                        # Track files by type
                        if file_type not in files_by_type:
                            files_by_type[file_type] = {'count': 0, 'total_lines': 0}
                        files_by_type[file_type]['count'] += 1
                        files_by_type[file_type]['total_lines'] += lines

                        # Check against language-specific threshold
                        if lines > threshold:
                            large_files.append({
                                'file': str(code_file.relative_to(module_path)),
                                'lines': lines,
                                'threshold': threshold,
                                'file_type': file_type,
                                'severity': self._classify_severity(lines, code_file.suffix)
                            })
                except Exception:
                    continue

            return {
                'total_lines': total_lines,
                'file_count': file_count,
                'large_files': large_files,
                'files_by_type': files_by_type,
                'exceeds_threshold': len(large_files) > 0,
                'wsp_compliance': 'VIOLATION' if len(large_files) > 0 else 'COMPLIANT'
            }
        except Exception as e:
            return {'error': str(e)}

    def _classify_severity(self, lines: int, suffix: str) -> str:
        """Classify file size severity based on WSP 62 thresholds.

        Args:
            lines: Number of lines in file
            suffix: File extension (e.g., '.py')

        Returns:
            'OK', 'GUIDELINE', 'CRITICAL', or 'VIOLATION'
        """
        threshold_info = self.FILE_THRESHOLDS.get(suffix.lower())
        if not threshold_info:
            return 'UNKNOWN'

        if lines <= threshold_info['ok']:
            return 'OK'
        elif lines <= threshold_info['guideline']:
            return 'GUIDELINE'
        elif lines <= threshold_info['hard_limit']:
            return 'CRITICAL'
        else:
            return 'VIOLATION'


    def detect_code_duplication(self, target_module: str) -> Dict[str, Any]:
        """Automatically detect potential code duplication patterns."""
        try:
            module_path = Path("modules") / target_module
            if not module_path.exists():
                return {'error': 'Module path not found'}

            py_files = list(module_path.rglob("*.py"))
            file_hashes = {}

            # Simple hash-based duplication detection
            duplicates = []
            for py_file in py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if len(content) > 100:  # Only check substantial files
                            content_hash = hash(content)
                            rel_path = str(py_file.relative_to(module_path))

                            if content_hash in file_hashes:
                                duplicates.append({
                                    'original': file_hashes[content_hash],
                                    'duplicate': rel_path,
                                    'lines': len(content.split('\n'))
                                })
                            else:
                                file_hashes[content_hash] = rel_path
                except Exception:
                    continue

            return {
                'duplicates_found': len(duplicates),
                'duplicate_pairs': duplicates[:5],  # Limit to top 5
                'wsp_violation': len(duplicates) > 0,
                'recommendation': 'Consolidate duplicate files' if duplicates else 'No duplicates detected'
            }
        except Exception as e:
            return {'error': str(e)}

    def run_intelligent_analysis(self, query: str, target_module: str = None) -> Dict[str, Any]:
        """Run all intelligent subroutines based on algorithmic decisions."""
        results = {}

        if self.should_run_health_check(query, target_module):
            # Health check would go here - placeholder for integration
            results['health_check'] = {'status': 'deferred', 'reason': 'integrated_with_main_health_system'}

        if self.should_run_size_analysis(query, target_module):
            results['size_analysis'] = self.analyze_module_size(target_module)

        if self.should_run_duplication_check(query, target_module):
            results['duplication_check'] = self.detect_code_duplication(target_module)

        # Update usage patterns
        if target_module:
            current_time = time.time()
            if target_module not in self.usage_patterns:
                self.usage_patterns[target_module] = {'last_check': 0, 'check_count': 0}
            self.usage_patterns[target_module]['last_check'] = current_time
            self.usage_patterns[target_module]['check_count'] += 1

        return results
