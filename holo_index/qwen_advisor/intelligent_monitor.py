#!/usr/bin/env python3
"""
Intelligent Monitoring System for HoloIndex DAE

Context-aware subroutines that run automatically based on algorithmic triggers,
not timers or manual commands. The DAE intelligently decides when to run health
checks, detect duplicates, or monitor patterns.

WSP Compliance: WSP 87, WSP 49, WSP 84, WSP 50
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
import json
from .models.monitoring_types import MonitoringResult, HealthViolation, HealthStatus, PatternAlert


@dataclass
class MonitoringContext:
    """Context that triggers monitoring subroutines"""
    query: str
    search_results: List[Dict]
    file_paths: List[str] = field(default_factory=list)
    modules_touched: List[str] = field(default_factory=list)
    patterns_detected: List[str] = field(default_factory=list)
    agent_actions: List[str] = field(default_factory=list)




class IntelligentMonitor:
    """
    Context-aware monitoring that runs subroutines based on algorithmic triggers.
    No timers, no manual commands - pure intelligent decision making.
    """

    def __init__(self):
        # Trigger thresholds (algorithmic, not time-based)
        self.triggers = {
            'size_check': self._should_check_size,
            'duplicate_check': self._should_check_duplicates,
            'structure_check': self._should_check_structure,
            'pattern_analysis': self._should_analyze_patterns,
            'agent_behavior': self._should_monitor_agent,
            'reindex_trigger': self._should_trigger_reindex,
            'file_movement_check': self._should_check_file_movements,  # NEW: WSP compliance
            'documentation_indexing': self._should_verify_documentation  # NEW: 0102 discoverability
        }

        # Cache to avoid redundant checks
        self.check_cache = {}
        self.module_fingerprints = {}

        # Agent behavior tracking
        self.agent_behavior = defaultdict(list)

    def monitor(self, context: MonitoringContext) -> MonitoringResult:
        """
        Main monitoring function - intelligently decides what to check
        based on context, not time or manual triggers.
        """
        legacy_data = {
            'health_warnings': [],
            'duplicates_found': [],
            'size_issues': [],
            'structure_violations': [],
            'optimization_suggestions': []
        }

        # Extract relevant paths from search results
        self._extract_context_paths(context)

        # Run subroutines based on algorithmic triggers
        for check_name, should_check in self.triggers.items():
            if should_check(context):
                self._run_subroutine(check_name, context, legacy_data)

        # NEW: Always run file movement and documentation checks after other monitoring
        # These are proactive checks that should run regardless of triggers
        self._run_file_movement_check(context, legacy_data)
        self._run_documentation_verification(context, legacy_data)

        # Add intelligent insights based on combined results
        self._add_intelligent_insights(context, legacy_data)

        return self._build_monitoring_result(context, legacy_data)

    def _should_check_size(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Check size when working with specific files or
        when search touches modules with many results.
        """
        # Check if query mentions files or modules
        if any(word in context.query.lower() for word in ['file', 'module', 'refactor', 'large', 'size']):
            return True

        # Check if search results concentrate in few files (potential large files)
        if context.file_paths:
            file_counts = defaultdict(int)
            for path in context.file_paths:
                file_counts[path] += 1

            # If any file appears > 3 times in results, it's likely large
            if any(count > 3 for count in file_counts.values()):
                return True

        return False

    def _should_check_duplicates(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Check duplicates when creating new code or
        when search reveals similar function names.
        """
        # Keywords that suggest potential duplication
        duplicate_indicators = ['create', 'new', 'add', 'implement', 'copy', 'similar', 'like']
        if any(word in context.query.lower() for word in duplicate_indicators):
            return True

        # Check if search results have similar function names
        if context.search_results:
            functions = [r.get('function', '') for r in context.search_results if r.get('function')]
            if len(functions) > len(set(functions)):  # Duplicate function names
                return True

        return False

    def _should_check_structure(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Check structure when working with new modules or
        when query suggests module-level operations.
        """
        structure_keywords = ['module', 'structure', 'scaffold', 'create', 'organize', 'wsp 49']
        if any(word in context.query.lower() for word in structure_keywords):
            return True

        # Check if touching modules without proper structure
        for module in context.modules_touched:
            if not self._is_module_cached(module):
                return True

        return False

    def _should_trigger_reindex(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Trigger HoloIndex re-indexing when new modules are detected
        or when module documentation changes are detected.
        """
        reindex_keywords = ['new module', 'module created', 'acoustic lab', 'module added', 'reindex', 'index']
        if any(word in context.query.lower() for word in reindex_keywords):
            return True

        # Check for module creation patterns in agent actions
        module_creation_patterns = ['module_create', 'new_module', 'scaffold_module']
        if any(pattern in ' '.join(context.agent_actions).lower() for pattern in module_creation_patterns):
            return True

        # Check if new modules exist that aren't in the index
        try:
            from pathlib import Path
            modules_dir = Path("../modules") if Path.cwd().name == 'holo_index' else Path("modules")
            if modules_dir.exists():
                for module_dir in modules_dir.rglob("*"):
                    if module_dir.is_dir() and (module_dir / "README.md").exists():
                        module_name = module_dir.name
                        # Check if this module is in our cache
                        if not self._is_module_cached(module_name):
                            return True
        except Exception:
            pass  # Don't break if module checking fails

        return False

    def _trigger_reindex(self, context: MonitoringContext, legacy_data: Dict[str, Any]):
        """Trigger HoloIndex re-indexing recommendation"""
        # Add reindexing suggestion to health warnings
        legacy_data['health_warnings'].append(
            "[HOLO] New modules detected - recommend running: python holo_index/cli.py --index-wsp"
        )

        # Add optimization suggestion
        legacy_data['optimization_suggestions'].append({
            'type': 'reindex',
            'priority': 'HIGH',
            'action': 'Run HoloIndex re-indexing to discover new Acoustic Lab module documentation',
            'command': 'python holo_index/cli.py --index-wsp',
            'benefit': 'Enable discovery of new module documentation for better search results'
        })

    def _should_analyze_patterns(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Analyze patterns when multiple similar operations detected
        or when working with pattern-heavy code.
        """
        # Check for pattern keywords
        if any(word in context.query.lower() for word in ['pattern', 'template', 'reuse', 'common']):
            return True

        # Check if agent is repeating actions (pattern forming)
        if len(context.agent_actions) > 5:
            action_types = [a.split(':')[0] for a in context.agent_actions if ':' in a]
            if len(action_types) > len(set(action_types)) * 1.5:  # Repetition detected
                return True

        return False

    def _should_monitor_agent(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Monitor agent behavior when vibecoding patterns detected
        or when agent deviates from WSP compliance.
        """
        # Always monitor if agent actions present
        if context.agent_actions:
            # Check for vibecoding patterns
            vibecode_patterns = ['file_create:new', 'skip_search', 'no_holoindex', 'direct_write']
            if any(pattern in ' '.join(context.agent_actions).lower() for pattern in vibecode_patterns):
                return True

        return len(context.agent_actions) > 0  # Always light monitoring

    def _run_subroutine(self, check_name: str, context: MonitoringContext, legacy_data: Dict[str, Any]):
        """Run specific monitoring subroutine"""

        if check_name == 'size_check':
            self._check_file_sizes(context, legacy_data)
        elif check_name == 'duplicate_check':
            self._check_duplicates(context, legacy_data)
        elif check_name == 'structure_check':
            self._check_module_structure(context, legacy_data)
        elif check_name == 'pattern_analysis':
            self._analyze_patterns(context, legacy_data)
        elif check_name == 'agent_behavior':
            self._monitor_agent_behavior(context, legacy_data)
        elif check_name == 'reindex_trigger':
            self._trigger_reindex(context, legacy_data)

    def _check_file_sizes(self, context: MonitoringContext, legacy_data: Dict[str, Any]):
        """Intelligent file size checking"""
        for file_path in context.file_paths[:10]:  # Check top 10 files
            if not os.path.exists(file_path):
                continue

            try:
                # Use subprocess for fast line counting
                line_count = int(subprocess.check_output(
                    ['wc', '-l', file_path],
                    universal_newlines=True,
                    stderr=subprocess.DEVNULL
                ).split()[0])

                if line_count > 800:
                    severity = 'CRITICAL' if line_count > 1000 else 'WARNING'
                    legacy_data['size_issues'].append({
                        'file': file_path,
                        'lines': line_count,
                        'severity': severity,
                        'action': f"Refactor {Path(file_path).name} ({line_count} lines)"
                    })

                    # Add to health warnings for display
                    legacy_data['health_warnings'].append(
                        f"[WSP 87] {severity}: {Path(file_path).name} has {line_count} lines"
                    )

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to Python line counting
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        line_count = sum(1 for _ in f)
                        if line_count > 800:
                            legacy_data['size_issues'].append({
                                'file': file_path,
                                'lines': line_count,
                                'severity': 'WARNING'
                            })
                except:
                    pass

    def _check_duplicates(self, context: MonitoringContext, legacy_data: Dict[str, Any]):
        """Intelligent duplicate detection using fingerprinting"""

        # Build function fingerprints from search results
        function_fingerprints = defaultdict(list)

        for hit in context.search_results:
            if hit.get('function') and hit.get('content'):
                # Create fingerprint from function signature
                content = hit['content'][:200]  # First 200 chars
                fingerprint = hashlib.md5(
                    re.sub(r'\s+', '', content).encode()
                ).hexdigest()[:8]

                function_fingerprints[fingerprint].append({
                    'function': hit['function'],
                    'file': hit.get('file', 'unknown'),
                    'module': hit.get('module', 'unknown')
                })

        # Detect duplicates
        for fingerprint, functions in function_fingerprints.items():
            if len(functions) > 1:
                legacy_data['duplicates_found'].append({
                    'fingerprint': fingerprint,
                    'instances': functions,
                    'severity': 'HIGH' if len(functions) > 2 else 'MEDIUM'
                })

                # Add warning
                func_names = [f['function'] for f in functions]
                legacy_data['health_warnings'].append(
                    f"[WSP 84] Duplicate pattern detected: {', '.join(func_names[:3])}"
                )

    def _check_module_structure(self, context: MonitoringContext, legacy_data: Dict[str, Any]):
        """Check WSP 49 compliance for touched modules"""

        required_structure = ['README.md', 'INTERFACE.md', 'ModLog.md', 'tests/', 'src/']

        for module_path in context.modules_touched[:5]:  # Check top 5 modules
            if not os.path.exists(module_path):
                continue

            missing = []
            for required in required_structure:
                full_path = os.path.join(module_path, required)
                if not os.path.exists(full_path):
                    missing.append(required)

            if missing:
                legacy_data['structure_violations'].append(
                    f"{Path(module_path).name}: Missing {', '.join(missing)}"
                )
                legacy_data['health_warnings'].append(
                    f"[WSP 49] {Path(module_path).name} missing: {', '.join(missing[:2])}"
                )

    def _analyze_patterns(self, context: MonitoringContext, legacy_data: Dict[str, Any]):
        """Detect and suggest patterns for extraction"""

        # Analyze search result patterns
        pattern_candidates = defaultdict(int)

        for hit in context.search_results:
            # Look for pattern indicators in content
            content = hit.get('content', '')
            if 'pattern' in content.lower() or 'template' in content.lower():
                pattern_candidates['explicit_pattern'] += 1

            # Check for repeated code structures
            if 'def ' in content and content.count('def ') > 1:
                pattern_candidates['multi_function'] += 1

            if 'class ' in content:
                pattern_candidates['class_pattern'] += 1

        # Generate suggestions
        if pattern_candidates:
            top_pattern = max(pattern_candidates, key=pattern_candidates.get)
            legacy_data['optimization_suggestions'].append(
                f"Pattern opportunity: {top_pattern} detected {pattern_candidates[top_pattern]} times"
            )

    def _monitor_agent_behavior(self, context: MonitoringContext, legacy_data: Dict[str, Any]):
        """Monitor agent for vibecoding and WSP compliance"""

        if not context.agent_actions:
            return

        # Analyze action sequence
        action_sequence = ' '.join(context.agent_actions)

        # Vibecoding detection
        if 'file_create' in action_sequence and 'search' not in action_sequence:
            legacy_data['health_warnings'].append(
                "[WSP 50] Vibecoding risk: Creating files without searching first"
            )
            legacy_data.setdefault('metadata', {})['vibecode_risk'] = 'HIGH'

        # Pattern detection
        action_types = [a.split(':')[0] for a in context.agent_actions if ':' in a]
        if action_types:
            most_common = max(set(action_types), key=action_types.count)
            if action_types.count(most_common) > 3:
                legacy_data['optimization_suggestions'].append(
                    f"Agent pattern detected: {most_common} repeated {action_types.count(most_common)} times"
                )

        # WSP compliance check
        if 'wsp_violation' in action_sequence.lower():
            legacy_data['health_warnings'].append(
                "[WSP 64] WSP violation detected in agent behavior"
            )

    def _extract_context_paths(self, context: MonitoringContext):
        """Extract file paths and modules from search results"""

        for hit in context.search_results:
            # Extract file paths
            if 'file' in hit:
                context.file_paths.append(hit['file'])

                # Extract module path
                module_path = self._get_module_path(hit['file'])
                if module_path and module_path not in context.modules_touched:
                    context.modules_touched.append(module_path)

    def _get_module_path(self, file_path: str) -> Optional[str]:
        """Extract module root path from file path"""
        path_parts = Path(file_path).parts

        # Look for module indicators
        for i, part in enumerate(path_parts):
            if part == 'modules' and i + 2 < len(path_parts):
                # modules/domain/module_name
                return str(Path(*path_parts[:i+3]))
            elif part == 'src' or part == 'tests':
                # Back up to module root
                return str(Path(*path_parts[:i]))

        return None

    def _is_module_cached(self, module_path: str) -> bool:
        """Check if module structure is already cached"""
        return module_path in self.check_cache

    def _add_intelligent_insights(self, context: MonitoringContext, legacy_data: Dict[str, Any]):
        """Add intelligent insights based on combined monitoring results"""

        # Combine insights
        if legacy_data['size_issues'] and legacy_data['duplicates_found']:
            legacy_data['optimization_suggestions'].append(
                "Consider refactoring large files and consolidating duplicates together"
            )

        if legacy_data['structure_violations'] and 'create' in context.query.lower():
            legacy_data['optimization_suggestions'].append(
                "Ensure new code follows WSP 49 structure from the start"
            )

        # Risk assessment
        risk_score = 0
        risk_score += len(legacy_data['size_issues']) * 2
        risk_score += len(legacy_data['duplicates_found']) * 3
        risk_score += len(legacy_data['structure_violations'])

        if risk_score > 5:
            legacy_data.setdefault('metadata', {})['overall_risk'] = 'HIGH'
            legacy_data['health_warnings'].insert(0,
                f"[HEALTH] High risk score ({risk_score}): Review warnings before proceeding"
            )
        elif risk_score > 2:
            legacy_data.setdefault('metadata', {})['overall_risk'] = 'MEDIUM'

        # Success tracking
        if not legacy_data['health_warnings']:
            legacy_data.setdefault('metadata', {})['health_status'] = 'EXCELLENT'


    def _build_monitoring_result(self, context: MonitoringContext, legacy_data: Dict[str, Any]) -> MonitoringResult:
        """Convert legacy monitoring data into the shared MonitoringResult model"""
        result = MonitoringResult()

        # Translate size issues into health violations
        for issue in legacy_data['size_issues']:
            file_path = issue.get('file', 'unknown')
            line_count = issue.get('lines', 0)
            severity_label = issue.get('severity', 'WARNING')
            severity = HealthStatus.CRITICAL if severity_label.upper() == 'CRITICAL' else HealthStatus.WARNING
            description = f"[SIZE] {file_path} is {line_count} lines"
            result.violations_found.append(
                HealthViolation(
                    violation_type='size_issue',
                    severity=severity,
                    description=description,
                    affected_path=file_path
                )
            )

        # Translate duplicate findings into pattern alerts
        for duplicate in legacy_data['duplicates_found']:
            name = duplicate.get('name', 'symbol')
            occurrences = duplicate.get('occurrences', 0)
            files = duplicate.get('files', [])
            confidence = min(1.0, 0.6 + 0.05 * max(occurrences, 1))
            result.pattern_alerts.append(
                PatternAlert(
                    pattern_type='duplicate_symbol',
                    confidence=confidence,
                    description=f"Duplicate symbol {name} detected ({occurrences} occurrences)",
                    affected_files=files,
                    suggested_action='Refactor duplicate implementations'
                )
            )

        # Structure violations and direct warnings become health violations
        for violation in legacy_data['structure_violations']:
            result.violations_found.append(
                HealthViolation(
                    violation_type='structure_violation',
                    severity=HealthStatus.WARNING,
                    description=violation,
                    affected_path=context.modules_touched[0] if context.modules_touched else 'context'
                )
            )

        for warning in legacy_data['health_warnings']:
            result.violations_found.append(
                HealthViolation(
                    violation_type='intelligent_monitor_warning',
                    severity=HealthStatus.WARNING,
                    description=warning,
                    affected_path=context.modules_touched[0] if context.modules_touched else 'context'
                )
            )

        # Optimization suggestions are exposed directly
        result.optimization_suggestions.extend(legacy_data['optimization_suggestions'])

        # Preserve legacy payload for backwards compatibility consumers
        legacy_payload = {
            'health_warnings': legacy_data['health_warnings'],
            'duplicates_found': legacy_data['duplicates_found'],
            'size_issues': legacy_data['size_issues'],
            'structure_violations': legacy_data['structure_violations'],
            'optimization_suggestions': legacy_data['optimization_suggestions']
        }

        metadata = legacy_data.get('metadata', {})
        metadata['legacy_monitoring_payload'] = legacy_payload
        result.metadata.update(metadata)

        return result

    def _should_check_file_movements(self, context: MonitoringContext) -> bool:
        """
        NEW: Algorithmic trigger for file movement detection and WSP compliance.

        Triggers when:
        - Query contains file movement keywords
        - Context shows file operations
        - Agent actions indicate refactoring
        """
        # Trigger on file movement keywords
        movement_keywords = ['move', 'moved', 'refactor', 'relocate', 'organize', 'wsp']
        if any(keyword in context.query.lower() for keyword in movement_keywords):
            return True

        # Trigger on agent actions that involve file operations
        file_actions = ['file_move', 'refactor', 'organize', 'wsp_compliance']
        if any(action in (context.agent_actions or []) for action in file_actions):
            return True

        return False

    def _should_verify_documentation(self, context: MonitoringContext) -> bool:
        """
        NEW: Algorithmic trigger for documentation indexing verification.

        Triggers when:
        - File movements detected
        - WSP compliance queries
        - Agent mentions documentation or indexing
        """
        # Always trigger after file movements
        if self._should_check_file_movements(context):
            return True

        # Trigger on documentation keywords
        doc_keywords = ['readme', 'documentation', 'index', 'discover', '0102']
        if any(keyword in context.query.lower() for keyword in doc_keywords):
            return True

        return False

    def _run_file_movement_check(self, context: MonitoringContext, legacy_data: Dict):
        """
        NEW: Check for WSP compliance violations in file movements.

        Verifies that moved files are properly indexed for 0102 discoverability.
        """
        # Detect recent file movements by checking for moved files in context
        moved_files = []
        for result in context.search_results:
            path = result.get('path', result.get('file_path', ''))
            if path and ('moved' in path.lower() or 'refactor' in path.lower()):
                moved_files.append(path)

        if moved_files:
            legacy_data['structure_violations'].append(
                f"WSP VIOLATION: {len(moved_files)} files moved but may not be indexed for 0102 discoverability"
            )

            # Suggest documentation updates
            legacy_data['optimization_suggestions'].append(
                "After file movements, update module README.md and navigation.py to ensure 0102 discoverability"
            )

    def _run_documentation_verification(self, context: MonitoringContext, legacy_data: Dict):
        """
        NEW: Verify that files are properly indexed in documentation.

        Checks README.md and navigation.py for moved files.
        """
        # Check if moved files are documented
        files_needing_docs = []

        # Look for files that should be in documentation but might not be
        for result in context.search_results:
            path = result.get('path', result.get('file_path', ''))
            if path and path.startswith('modules/'):
                # Check if this file is mentioned in navigation
                if 'navigation' not in path.lower() and 'readme' not in path.lower():
                    files_needing_docs.append(path)

        if files_needing_docs:
            legacy_data['health_warnings'].append(
                f"0102 DISCOVERABILITY: {len(files_needing_docs)} files may not be indexed in navigation system"
            )

            legacy_data['optimization_suggestions'].append(
                "Add moved files to modules/infrastructure/navigation/src/navigation.py NEED_TO dictionary"
            )


# Integration with HoloIndex search flow
def monitor_search_context(query: str, search_results: List[Dict],
                          agent_actions: Optional[List[str]] = None) -> MonitoringResult:
    """
    Main entry point for intelligent monitoring.
    Called automatically by HoloIndex during search operations.
    """
    monitor = IntelligentMonitor()

    context = MonitoringContext(
        query=query,
        search_results=search_results,
        agent_actions=agent_actions or []
    )

    return monitor.monitor(context)


if __name__ == "__main__":
    # Test the intelligent monitor

    # Simulate a search context
    test_context = MonitoringContext(
        query="create new authentication module for large system",
        search_results=[
            {'function': 'authenticate', 'file': 'modules/auth/src/auth.py', 'content': 'def authenticate()...'},
            {'function': 'authenticate', 'file': 'modules/user/src/login.py', 'content': 'def authenticate()...'},
            {'function': 'validate', 'file': 'modules/auth/src/auth.py', 'content': 'def validate()...'},
        ],
        agent_actions=['search:auth', 'file_create:new', 'search:auth', 'file_create:new']
    )

    monitor = IntelligentMonitor()
    result = monitor.monitor(test_context)

    print("Intelligent Monitoring Results:")
    print(f"Health Violations: {len(result.violations_found)}")
    for violation in result.violations_found:
        print(f"  - {violation.get_summary()}")

    print(f"\nPattern Alerts: {len(result.pattern_alerts)}")
    for alert in result.pattern_alerts:
        print(f"  - {alert.get_summary()}")

    print(f"\nOptimization Suggestions:")
    for suggestion in result.optimization_suggestions:
        print(f"  - {suggestion}")

    print(f"\nMetadata: {result.metadata}")

