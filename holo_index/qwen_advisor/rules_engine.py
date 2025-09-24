﻿#!/usr/bin/env python3
"""
QwenAdvisor Rules Engine - Immediate Intelligence Without LLM
WSP Compliance: WSP 50, WSP 84, WSP 85, WSP 87

This provides immediate intelligent guidance using deterministic rules
while we prepare the full LLM integration. Can be deployed TODAY.
"""

import re
import os
import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Import module health auditors
try:
    from ..module_health.size_audit import SizeAuditor, FileSizeResult, RiskTier
    from ..module_health.structure_audit import StructureAuditor, StructureResult
    MODULE_HEALTH_AVAILABLE = True
except ImportError:
    MODULE_HEALTH_AVAILABLE = False
    SizeAuditor = None
    StructureAuditor = None


try:
    from ..violation_tracker import ViolationTracker, Violation
    VIOLATION_TRACKER_AVAILABLE = True
except ImportError:
    VIOLATION_TRACKER_AVAILABLE = False
    ViolationTracker = None
    Violation = None


@dataclass
class ComplianceCheckResult:
    """Result of a compliance check."""
    passed: bool
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    guidance: str
    suggested_fix: Optional[str] = None
    wsp_reference: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ComplianceRulesEngine:
    """
    Deterministic rules engine for immediate WSP compliance guidance.
    No LLM needed - can be deployed immediately for 0102 agents.
    """

    def __init__(self):
        """Initialize the rules engine with WSP checkpoints."""
        # Initialize database tables first
        self._init_database_tables()

        self.violations_history = self._load_violations_history()

        # Find the actual project root (where modules/ exists)
        cwd = Path.cwd()
        if (cwd / "modules").exists():
            self.project_root = cwd
        elif (cwd.parent / "modules").exists():
            self.project_root = cwd.parent
        else:
            self.project_root = cwd

        # Initialize module health auditors if available
        if MODULE_HEALTH_AVAILABLE:
            self.size_auditor = SizeAuditor()
            self.structure_auditor = StructureAuditor()
        else:
            self.size_auditor = None
            self.structure_auditor = None

        if VIOLATION_TRACKER_AVAILABLE:
            try:
                self.violation_tracker = ViolationTracker()
            except Exception:
                self.violation_tracker = None
        else:
            self.violation_tracker = None

    def _init_database_tables(self):
        """Initialize database tables for HoloIndex module (WSP 78)."""
        try:
            from modules.infrastructure.database.src.module_db import ModuleDB
            db = ModuleDB("holo_index")

            # Create violations table
            db.create_table("violations", """
                id TEXT PRIMARY KEY,
                timestamp DATETIME,
                wsp TEXT,
                module TEXT,
                severity TEXT,
                description TEXT,
                agent TEXT,
                remediation_status TEXT DEFAULT 'pending',
                metadata JSON
            """)

            # Create indexes for better performance
            try:
                db.db.execute_write("CREATE INDEX IF NOT EXISTS idx_holo_violations_timestamp ON modules_holo_index_violations(timestamp)")
                db.db.execute_write("CREATE INDEX IF NOT EXISTS idx_holo_violations_wsp ON modules_holo_index_violations(wsp)")
                db.db.execute_write("CREATE INDEX IF NOT EXISTS idx_holo_violations_severity ON modules_holo_index_violations(severity)")
            except Exception as e:
                # Indexes are optional, continue if they fail
                pass

        except Exception as e:
            # Database initialization failure should not break the system
            pass

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze the intent of a search query to provide targeted guidance.
        """
        query_lower = query.lower()

        intent = {
            "is_creation": any(word in query_lower for word in [
                "create", "new", "build", "implement", "add", "generate"
            ]),
            "is_modification": any(word in query_lower for word in [
                "edit", "modify", "update", "change", "fix", "enhance"
            ]),
            "is_test": "test" in query_lower,
            "is_documentation": any(word in query_lower for word in [
                "doc", "readme", "document"
            ]),
            "targets_root": not any(sep in query for sep in ['/', '\\', 'modules']),
            "has_enhanced": "enhanced" in query_lower or "_v2" in query or "_new" in query,
            "mentions_file": ".py" in query or ".md" in query or ".js" in query
        }

        # Determine primary action
        if intent["is_creation"]:
            intent["primary_action"] = "create"
        elif intent["is_modification"]:
            intent["primary_action"] = "modify"
        else:
            intent["primary_action"] = "search"

        return intent

    def check_wsp_85_root_protection(self, query: str, intent: Dict) -> Optional[ComplianceCheckResult]:
        """
        WSP 85: Root Directory Protection
        Never create test files or module code in root.
        """
        if not intent["is_creation"]:
            return None

        if intent["targets_root"] and intent["mentions_file"]:
            # Check for test files specifically
            if "test" in query.lower():
                return ComplianceCheckResult(
                    passed=False,
                    severity="CRITICAL",
                    guidance="[CRITICAL] WSP 85 VIOLATION: Never create test files in root directory!",
                    suggested_fix="Move to: modules/infrastructure/integration_tests/tests/ or appropriate module tests/",
                    wsp_reference="WSP 85: Root Directory Protection"
                )

            # Check for any .py files in root
            if ".py" in query and not any(allowed in query.lower() for allowed in ["main.py", "holo_index.py", "navigation.py"]):
                return ComplianceCheckResult(
                    passed=False,
                    severity="HIGH",
                    guidance="[WARN] WSP 85 WARNING: Root directory is for foundational files only",
                    suggested_fix="Place in appropriate module under modules/{domain}/{module}/",
                    wsp_reference="WSP 85: Root Directory Protection"
                )

        return None

    def check_wsp_84_no_duplicates(self, query: str, intent: Dict) -> Optional[ComplianceCheckResult]:
        """
        WSP 84: Code Memory - Never create enhanced_ or _v2 versions
        """
        if intent["has_enhanced"]:
            return ComplianceCheckResult(
                passed=False,
                severity="CRITICAL",
                guidance="[CRITICAL] WSP 84 VIOLATION: NEVER create enhanced_, _v2, or _improved versions!",
                suggested_fix="Edit the existing file directly. Trust git for version history.",
                wsp_reference="WSP 84: Code Memory Verification"
            )

        if intent["is_creation"] and "new" in query.lower():
            return ComplianceCheckResult(
                passed=False,
                severity="MEDIUM",
                guidance="[WARN] WSP 84 CHECK: Verify this functionality doesn't already exist",
                suggested_fix="Run HoloIndex search first to find existing implementations",
                wsp_reference="WSP 84: Code Memory Verification"
            )

        return None

    def check_wsp_87_search_first(self, query: str, intent: Dict) -> Optional[ComplianceCheckResult]:
        """
        WSP 87: Navigation Protocol - Search before creating
        """
        if intent["is_creation"]:
            # Check if HoloIndex was used recently (would need telemetry integration)
            return ComplianceCheckResult(
                passed=False,
                severity="HIGH",
                guidance="[REQUIRED] WSP 87 REQUIRED: Run HoloIndex before creating new code",
                suggested_fix="ALWAYS search for existing code before creating new:\npython holo_index.py --search \"" + query + "\"",
                wsp_reference="WSP 87: Code Navigation Protocol"
            )

        return None

    def check_wsp_22_modlog_sync(self, query: str, intent: Dict) -> Optional[ComplianceCheckResult]:
        """
        WSP 22: ModLog Protocol - Keep documentation synchronized
        """
        if intent["is_test"] and intent["is_creation"]:
            return ComplianceCheckResult(
                passed=False,
                severity="MEDIUM",
                guidance="[REMINDER] WSP 22: Update TestModLog after adding tests",
                suggested_fix="After creating test, update the module's TestModLog.md with test details",
                wsp_reference="WSP 22: ModLog and Documentation"
            )

        if intent["is_modification"]:
            return ComplianceCheckResult(
                passed=True,  # Reminder, not violation
                severity="LOW",
                guidance="[REMINDER] WSP 22: Update ModLog.md after significant changes",
                suggested_fix=None,
                wsp_reference="WSP 22: ModLog and Documentation"
            )

        return None

    def check_wsp_49_module_structure(self, query: str, intent: Dict) -> Optional[ComplianceCheckResult]:
        """
        WSP 49: Module Structure - Enforce standard structure
        """
        if "module" in query.lower() and intent["is_creation"]:
            return ComplianceCheckResult(
                passed=False,
                severity="HIGH",
                guidance="[STRUCTURE] WSP 49 REQUIRED: Follow standard module structure",
                suggested_fix="Create module scaffolding:\nREADME.md\nModLog.md\nINTERFACE.md\nsrc/\ntests/\ntests/TestModLog.md\nmemory/",
                wsp_reference="WSP 49: Module Directory Structure"
            )

        return None

    def check_module_size_health(self, search_hits: List[Dict]) -> List[ComplianceCheckResult]:
        """
        Check size health of files referenced in search hits.
        WSP 87: Monitor file sizes and line counts.
        """
        if not self.size_auditor:
            return []

        results = []
        checked_files = set()

        for hit in search_hits:
            # Try to resolve the file path from the hit
            file_path = self._resolve_file_path(hit)
            if not file_path or file_path in checked_files:
                continue

            checked_files.add(file_path)

            # Run size audit
            size_result = self.size_auditor.audit_file(file_path)
            if size_result and size_result.needs_attention:
                severity = "HIGH" if size_result.risk_tier == RiskTier.CRITICAL else "MEDIUM"
                severity_label = "[CRITICAL]" if severity == "HIGH" else "[WARN]"
                metadata = {
                    "module_path": str(file_path),
                    "line_count": size_result.line_count,
                    "byte_size": size_result.byte_size,
                    "risk_tier": size_result.risk_tier.name
                }
                results.append(ComplianceCheckResult(
                    passed=False,
                    severity=severity,
                    guidance=f"{severity_label} WSP 87: {file_path.name} - {size_result.guidance}",
                    suggested_fix=f"Consider refactoring {file_path} ({size_result.line_count} lines)",
                    wsp_reference="WSP 87: Code Navigation Protocol",
                    metadata=metadata
                ))

        return results

    def check_module_structure_health(self, search_hits: List[Dict]) -> List[ComplianceCheckResult]:
        """
        Check structure health of modules referenced in search hits.
        WSP 49: Ensure required scaffolding exists.
        """
        if not self.structure_auditor:
            return []

        results = []
        checked_modules = set()

        for hit in search_hits:
            # Try to find the module root
            file_path = self._resolve_file_path(hit)
            if not file_path:
                continue

            module_root = self.structure_auditor.find_module_root(file_path)
            if not module_root or module_root in checked_modules:
                continue

            checked_modules.add(module_root)

            # Run structure audit
            structure_result = self.structure_auditor.audit_module(module_root)
            if not structure_result.is_compliant:
                metadata = {
                    "module_path": str(module_root),
                    "missing_artifacts": structure_result.missing_artifacts
                }
                results.append(ComplianceCheckResult(
                    passed=False,
                    severity="MEDIUM",
                    guidance=f"[STRUCTURE] WSP 49: {module_root.name} - {structure_result.guidance}",
                    suggested_fix="\n".join(structure_result.todos[:3]),  # Show first 3 todos
                    wsp_reference="WSP 49: Module Directory Structure",
                    metadata=metadata
                ))

        return results

    def _resolve_file_path(self, hit: Dict) -> Optional[Path]:
        """
        Try to resolve a file path from a search hit.

        Handles various formats:
        - Direct paths: "modules/foo/bar/src/file.py"
        - Module notation: "modules.foo.bar.src.file"
        - Navigation location: "modules.foo.bar.Class.method"
        """
        location = hit.get('location', '') or hit.get('path', '') or hit.get('file', '')
        if not location:
            return None

        # Handle direct file paths
        if '.py' in location or '/' in location or '\\' in location:
            path = Path(location)
            if path.is_absolute() and path.exists():
                return path
            # Try relative to project root
            rel_path = self.project_root / path
            if rel_path.exists():
                return rel_path

        # Handle module notation (modules.foo.bar.src.file)
        if '.' in location:
            # Remove any method/class suffixes
            if '(' in location:
                location = location[:location.index('(')]

            # Convert dots to path separators
            parts = location.split('.')

            # Special handling for modules.x.y.z format
            if parts[0] == 'modules' or location.startswith('modules'):
                # Try to find where the module path ends and class/method begins
                for i in range(len(parts), 0, -1):
                    test_path = Path(*parts[:i])
                    # Try with .py extension
                    py_path = self.project_root / f"{test_path}.py"
                    if py_path.exists():
                        return py_path
                    # Try as directory with __init__.py
                    init_path = self.project_root / test_path / "__init__.py"
                    if init_path.exists():
                        return init_path
                    # Try finding specific file in that directory
                    if i < len(parts):
                        # The next part might be a filename
                        dir_path = self.project_root / test_path
                        if dir_path.is_dir():
                            file_path = dir_path / f"{parts[i]}.py"
                            if file_path.exists():
                                return file_path

        return None

    def generate_contextual_guidance(
        self,
        query: str,
        search_hits: List[Dict],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate intelligent guidance based on query and context.
        This is the main entry point for the rules engine.
        """
        # Analyze intent
        intent = self.analyze_query_intent(query)

        # Run all compliance checks
        checks = []
        violations = []
        reminders = []

        # Critical checks
        for check_func in [
            self.check_wsp_85_root_protection,
            self.check_wsp_84_no_duplicates,
            self.check_wsp_87_search_first,
            self.check_wsp_22_modlog_sync,
            self.check_wsp_49_module_structure
        ]:
            result = check_func(query, intent)
            if result:
                checks.append(result)
                if result.severity in ["CRITICAL", "HIGH"]:
                    violations.append(result)
                else:
                    reminders.append(result)

        # Analyze search results for additional context
        if search_hits:
            # Run module health checks on search results
            if MODULE_HEALTH_AVAILABLE:
                # Check file sizes
                size_checks = self.check_module_size_health(search_hits)
                for check in size_checks:
                    checks.append(check)
                    if check.severity in ["CRITICAL", "HIGH"]:
                        violations.append(check)
                    else:
                        reminders.append(check)

                # Check module structure
                structure_checks = self.check_module_structure_health(search_hits)
                for check in structure_checks:
                    checks.append(check)
                    reminders.append(check)  # Structure issues are usually reminders

            # If high-confidence matches found, emphasize using existing code
            if any(hit.get("confidence", 0) > 50 for hit in search_hits):
                reminders.append(ComplianceCheckResult(
                    passed=True,
                    severity="LOW",
                    guidance="EFound existing implementations - consider enhancing instead of creating new",
                    suggested_fix=None,
                    wsp_reference="WSP 84: Code Memory"
                ))

        # Build guidance response
        guidance = {
            "intent": intent,
            "violations": [v.__dict__ for v in violations],
            "reminders": [r.__dict__ for r in reminders],
            "all_checks": [c.__dict__ for c in checks],
            "risk_level": self._calculate_risk_level(violations),
            "primary_guidance": self._generate_primary_guidance(intent, violations, search_hits),
            "action_items": self._generate_action_items(checks)
        }

        return guidance

    def _calculate_risk_level(self, violations: List[ComplianceCheckResult]) -> str:
        """Calculate overall risk level based on violations."""
        if any(v.severity == "CRITICAL" for v in violations):
            return "CRITICAL"
        elif any(v.severity == "HIGH" for v in violations):
            return "HIGH"
        elif violations:
            return "MEDIUM"
        return "LOW"

    def _generate_primary_guidance(
        self,
        intent: Dict,
        violations: List[ComplianceCheckResult],
        search_hits: List[Dict]
    ) -> str:
        """Generate primary guidance message."""
        if violations:
            # Focus on most critical violation
            critical = next((v for v in violations if v.severity == "CRITICAL"), None)
            if critical:
                return f"ESTOP: {critical.guidance}"
            else:
                return f"EECAUTION: {violations[0].guidance}"

        elif intent["primary_action"] == "create":
            if search_hits and any(h.get("confidence", 0) > 30 for h in search_hits):
                return " TIP: Found existing code that might meet your needs. Review before creating new."
            else:
                return " VERIFY: Ensure this functionality doesn't already exist before creating."

        else:
            return "EQuery appears compliant. Remember to follow WSP protocols."

    def _generate_action_items(self, checks: List[ComplianceCheckResult]) -> List[str]:
        """Generate concrete action items from checks."""
        actions = []

        for check in checks:
            if check.suggested_fix and not check.passed:
                actions.append(check.suggested_fix)

        # Always remind about core practices
        if not any("HoloIndex" in a for a in actions):
            actions.append("Remember: Always search with HoloIndex before creating new code")

        return actions[:5]  # Limit to top 5 actions

    def _load_violations_history(self) -> List[Dict]:
        """Load violation history from ViolationTracker (WSP 78 database)."""
        try:
            from holo_index.violation_tracker import ViolationTracker

            tracker = ViolationTracker()
            violations = tracker.get_all_violations()
            tracker.close()

            # Convert Violation objects to dictionaries
            return [v.to_dict() for v in violations]

        except Exception as e:
            # logger.debug(f"Could not load violations from ViolationTracker: {e}")
            return []

    def analyze_search_patterns(self, search_history: List[Dict]) -> Dict[str, Any]:
        """
        Phase 2: Analyze search patterns for success/failure detection and context correlation.

        Args:
            search_history: List of search interaction records

        Returns:
            Pattern analysis results with improvement recommendations
        """
        if not search_history:
            return {"patterns": [], "recommendations": [], "confidence": 0.0}

        # Extract patterns from search data
        success_patterns = []
        failure_patterns = []
        context_correlations = {}

        # Analyze query types and success rates
        query_patterns = {}
        for search in search_history[-100:]:  # Analyze last 100 searches
            query = search.get('query', '').lower()
            results_found = search.get('results_found', False)
            health_issues = search.get('health_issues_count', 0)
            advisor_used = search.get('advisor_used', False)

            # Categorize query type
            query_type = self._categorize_query_type(query)

            if query_type not in query_patterns:
                query_patterns[query_type] = {'total': 0, 'successful': 0, 'with_advisor': 0}

            query_patterns[query_type]['total'] += 1
            if results_found:
                query_patterns[query_type]['successful'] += 1
            if advisor_used:
                query_patterns[query_type]['with_advisor'] += 1

        # Identify success patterns
        for query_type, stats in query_patterns.items():
            success_rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            advisor_usage = stats['with_advisor'] / stats['total'] if stats['total'] > 0 else 0

            if success_rate > 0.8 and stats['total'] >= 5:
                success_patterns.append({
                    'pattern': f"High success rate for {query_type} queries",
                    'success_rate': success_rate,
                    'sample_size': stats['total'],
                    'recommendation': f"Continue using direct search for {query_type} queries"
                })

            if success_rate < 0.3 and advisor_usage < 0.5 and stats['total'] >= 3:
                failure_patterns.append({
                    'pattern': f"Low success rate for {query_type} queries without advisor",
                    'success_rate': success_rate,
                    'sample_size': stats['total'],
                    'recommendation': f"Consider using advisor for {query_type} queries"
                })

        # Context correlation analysis
        time_patterns = self._analyze_time_patterns(search_history)
        complexity_patterns = self._analyze_complexity_patterns(search_history)

        context_correlations.update(time_patterns)
        context_correlations.update(complexity_patterns)

        return {
            'success_patterns': success_patterns,
            'failure_patterns': failure_patterns,
            'context_correlations': context_correlations,
            'overall_confidence': min(1.0, len(search_history) / 50.0),  # Confidence based on data size
            'recommendations': self._generate_pattern_recommendations(
                success_patterns, failure_patterns, context_correlations
            )
        }

    def _categorize_query_type(self, query: str) -> str:
        """Categorize query by type for pattern analysis."""
        query_lower = query.lower()

        if any(word in query_lower for word in ['class', 'method', 'function', 'def ', 'import']):
            return 'code_structure'
        elif any(word in query_lower for word in ['error', 'exception', 'bug', 'fix', 'debug']):
            return 'debugging'
        elif any(word in query_lower for word in ['test', 'pytest', 'unit', 'integration']):
            return 'testing'
        elif any(word in query_lower for word in ['wsp', 'compliance', 'protocol', 'standard']):
            return 'compliance'
        elif any(word in query_lower for word in ['module', 'domain', 'infrastructure', 'communication']):
            return 'architecture'
        else:
            return 'general'

    def _analyze_time_patterns(self, search_history: List[Dict]) -> Dict[str, Any]:
        """Analyze search patterns by time of day."""
        hour_performance = {}

        for search in search_history[-50:]:  # Last 50 searches
            timestamp = search.get('timestamp')
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp)
                    hour = dt.hour
                    success = search.get('results_found', False)

                    if hour not in hour_performance:
                        hour_performance[hour] = {'total': 0, 'successful': 0}

                    hour_performance[hour]['total'] += 1
                    if success:
                        hour_performance[hour]['successful'] += 1

                except:
                    continue

        # Find best/worst performing hours
        time_insights = {}
        for hour, stats in hour_performance.items():
            if stats['total'] >= 3:  # At least 3 searches
                success_rate = stats['successful'] / stats['total']
                if success_rate > 0.8:
                    time_insights[f"hour_{hour}"] = f"High success rate ({success_rate:.1%}) at {hour}:00"
                elif success_rate < 0.4:
                    time_insights[f"hour_{hour}_low"] = f"Low success rate ({success_rate:.1%}) at {hour}:00"

        return {'time_patterns': time_insights}

    def _analyze_complexity_patterns(self, search_history: List[Dict]) -> Dict[str, Any]:
        """Analyze how query complexity affects success rates."""
        simple_queries = []
        complex_queries = []

        for search in search_history[-100:]:
            query = search.get('query', '')
            success = search.get('results_found', False)

            # Simple heuristic: longer queries are more complex
            if len(query.split()) > 5:
                complex_queries.append(success)
            else:
                simple_queries.append(success)

        simple_success = sum(simple_queries) / len(simple_queries) if simple_queries else 0
        complex_success = sum(complex_queries) / len(complex_queries) if complex_queries else 0

        complexity_insights = {}
        if len(simple_queries) >= 10 and len(complex_queries) >= 10:
            if complex_success < simple_success * 0.7:
                complexity_insights['complex_query_issue'] = (
                    f"Complex queries have lower success rate ({complex_success:.1%} vs {simple_success:.1%} for simple)"
                )

        return {'complexity_patterns': complexity_insights}

    def _generate_pattern_recommendations(self, success_patterns: List, failure_patterns: List,
                                        context_correlations: Dict) -> List[str]:
        """Generate actionable recommendations from pattern analysis."""
        recommendations = []

        # Success pattern recommendations
        for pattern in success_patterns:
            recommendations.append(f"✅ {pattern['recommendation']}")

        # Failure pattern recommendations
        for pattern in failure_patterns:
            recommendations.append(f"🔧 {pattern['recommendation']}")

        # Context correlation recommendations
        time_patterns = context_correlations.get('time_patterns', {})
        for key, insight in time_patterns.items():
            if '_low' in key:
                recommendations.append(f"⚠️ {insight} - consider different search strategies")
            else:
                recommendations.append(f"✅ {insight} - optimal search time")

        complexity_patterns = context_correlations.get('complexity_patterns', {})
        for key, insight in complexity_patterns.items():
            recommendations.append(f"📊 {insight}")

        return recommendations[:10]  # Limit to top 10 recommendations

    def record_violation(self, violation_data: Dict[str, Any]):
        """Record a violation using structured storage (database or JSONL)."""
        try:
            from holo_index.violation_tracker import ViolationTracker, Violation

            # Use the existing violation tracker
            tracker = ViolationTracker()

            timestamp_value = violation_data.get('timestamp')
            if timestamp_value:
                try:
                    timestamp_dt = datetime.fromisoformat(timestamp_value)
                except ValueError:
                    timestamp_dt = datetime.now(timezone.utc)
                    violation_data['timestamp'] = timestamp_dt.isoformat()
            else:
                timestamp_dt = datetime.now(timezone.utc)
                violation_data['timestamp'] = timestamp_dt.isoformat()

            violation_id = violation_data.get('id') or f"v-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

            violation = Violation(
                id=violation_id,
                timestamp=timestamp_dt,
                wsp_number=violation_data.get('wsp', 'UNKNOWN'),
                module_path=violation_data.get('module', 'unknown'),
                severity=violation_data.get('severity', 'MEDIUM'),
                description=violation_data.get('description', 'Violation detected'),
                agent_id=violation_data.get('agent', '0102'),
                remediation_status=violation_data.get('remediation_status', 'pending'),
                metadata=violation_data.get('metadata')
            )

            tracker.record_violation(violation)
            tracker.close()
            return

        except Exception as exc:
            logger.debug(f"ViolationTracker unavailable: {exc}")

        # Fallback to JSONL if tracker unavailable or failed
        self._record_violation_jsonl(violation_data)

    def _record_violation_jsonl(self, violation_data: Dict[str, Any]):
        """Fallback: Record violation to JSONL file."""
        import json
        from pathlib import Path

        jsonl_file = Path("WSP_VIOLATIONS.jsonl")
        try:
            with open(jsonl_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(violation_data, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to record violation to JSONL: {e}")

    def format_guidance_for_cli(self, guidance: Dict) -> List[str]:
        """
        Format guidance dictionary into CLI-friendly output lines.
        """
        lines = []

        # Add violations first (most important)
        if guidance["violations"]:
            lines.append("[WARN] Violations Detected:")
            for v in guidance["violations"]:
                lines.append(f"  - [{v['wsp_reference']}] {v['guidance']}")
                if v['suggested_fix']:
                    lines.append(f"    FIX: {v['suggested_fix']}")

        # Add reminders
        if guidance["reminders"]:
            lines.append("[REM] Reminders:")
            for r in guidance["reminders"]:
                lines.append(f"  - {r['wsp_reference']}: {r['guidance']}")

        # Add action items
        if guidance["action_items"]:
            lines.append("[TODO] Action Items:")
            for i, action in enumerate(guidance["action_items"], 1):
                lines.append(f"  {i}. {action}")

        return lines


# Convenience function for immediate use
def analyze_query(query: str, search_hits: List[Dict] = None) -> Dict:
    """
    Quick function to analyze a query for WSP compliance.
    Can be called directly from CLI or integrated into HoloIndex.
    """
    engine = ComplianceRulesEngine()
    return engine.generate_contextual_guidance(query, search_hits or [])


if __name__ == "__main__":
    # Test the engine with example queries
    test_queries = [
        "create test_new_feature.py",
        "create enhanced_chat_sender.py",
        "implement new authentication module",
        "modify existing chat handler",
        "search for message processing"
    ]

    engine = ComplianceRulesEngine()

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        guidance = engine.generate_contextual_guidance(query, [])

        # Format for CLI
        lines = engine.format_guidance_for_cli(guidance)
        for line in lines:
            print(line)

        print(f"\nRisk Level: {guidance['risk_level']}")
        print(f"Primary Guidance: {guidance['primary_guidance']}")






