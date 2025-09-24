"""Intelligent Subroutine Engine - WSP 87 Compliant Algorithmic Analysis

This module provides intelligent subroutines that run algorithmic analysis
only when needed, preventing unnecessary computational overhead.

WSP Compliance: WSP 87 (Size Limits), WSP 49 (Module Structure), WSP 72 (Block Independence)
"""

from __future__ import annotations
import time
from pathlib import Path
from typing import Dict, Any


class IntelligentSubroutineEngine:
    """Intelligent subroutines that run algorithmic analysis when needed."""

    def __init__(self):
        self.module_sizes = {}
        self.duplication_patterns = {}
        self.usage_patterns = {}
        self.last_health_check = None

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
        """Automatically analyze module size and structure."""
        try:
            module_path = Path("modules") / target_module
            if not module_path.exists():
                return {'error': 'Module path not found'}

            total_lines = 0
            file_count = 0
            large_files = []

            for py_file in module_path.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_count += 1

                        # WSP 62 thresholds
                        if lines > 500:  # Python threshold
                            large_files.append({
                                'file': str(py_file.relative_to(module_path)),
                                'lines': lines,
                                'threshold': 500
                            })
                except Exception as e:
                    continue

            return {
                'total_lines': total_lines,
                'file_count': file_count,
                'large_files': large_files,
                'exceeds_threshold': total_lines > 2000 or len(large_files) > 0,
                'wsp_compliance': 'VIOLATION' if len(large_files) > 0 else 'COMPLIANT'
            }
        except Exception as e:
            return {'error': str(e)}

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
