# -*- coding: utf-8 -*-
import sys
import io


"""
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

Output Composer for HoloDAE Query Results
WSP Compliance: WSP 3 (Module Organization), WSP 48 (Recursive Learning)

Composes structured, priority-based output with alert deduplication.
Part of Intent-Driven Orchestration Enhancement (2025-10-07).

Design Doc: docs/agentic_journals/HOLODAE_INTENT_ORCHESTRATION_DESIGN.md
"""

import re
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from holo_index.intent_classifier import IntentType, IntentClassification

logger = logging.getLogger(__name__)


@dataclass
class ComposedOutput:
    """Structured output with priority sections"""
    intent_section: str
    findings_section: str
    mcp_section: Optional[str]
    alerts_section: Optional[str]
    full_output: str

    def __str__(self) -> str:
        return self.full_output


class OutputComposer:
    """
    Composes priority-based structured output for HoloDAE queries.

    Reduces noise by:
    - Organizing output into clear sections (INTENT, FINDINGS, MCP, ALERTS)
    - Deduplicating repeated warnings (87 lines -> 1 line)
    - Intent-aware formatting (different output styles per intent)

    Token Budget: ~300 tokens per composition (vs 10,000 unstructured)
    """

    def __init__(self):
        """Initialize output composer"""
        logger.info("[OUTPUT-COMPOSER] Initialized")

    def compose(
        self,
        intent_classification: Optional[IntentClassification] = None,
        intent: Optional[IntentType] = None,
        findings: str = "",
        mcp_results: Optional[str] = None,
        alerts: Optional[List[str]] = None,
        query: str = "",
        search_results: Optional[Dict[str, Any]] = None
    ) -> ComposedOutput:
        """
        Compose structured output with context-aware priority sections.

        Args:
            intent_classification: IntentClassification with output formatting rules.
            intent: Backward-compatible alias for callers that pass IntentType directly.
            findings: Raw findings from component execution
            mcp_results: Optional MCP research results
            alerts: Optional list of alert/warning strings
            query: Original user query
            search_results: Optional HoloIndex search results (for CODE_LOCATION)

        Returns:
            ComposedOutput with structured sections prioritized by intent

        Token Budget: ~300 tokens (context-aware formatting)
        """
        # Backward compatibility: support legacy compose(intent=IntentType, ...)
        if intent_classification is None:
            if intent is None:
                raise ValueError("compose requires intent_classification or intent")
            intent_classification = IntentClassification(
                intent=intent,
                confidence=1.0,
                patterns_matched=[],
                raw_query=query or "",
            )

        # Get intent and output formatting rules
        intent = intent_classification.intent
        output_rules = intent_classification.output_rules
        self._current_output_rules = output_rules

        sections = []
        section_order = output_rules.priority_sections

        # Build sections based on priority order
        for section_name in section_order:
            if section_name == 'results':
                # Section: Findings (primary content)
                findings_section = self._build_findings_section(findings, intent, search_results)
                sections.append(findings_section)
                sections.append("")

            elif section_name == 'guidance':
                # Section: WSP Guidance (for DOC_LOOKUP)
                if intent == IntentType.DOC_LOOKUP:
                    guidance_section = self._build_guidance_section(findings)
                    if guidance_section:
                        sections.append(guidance_section)
                        sections.append("")

            elif section_name == 'orchestrator':
                # Section: Orchestrator details (for detailed analysis)
                orchestrator_section = self._build_orchestrator_section(findings)
                if orchestrator_section:
                    sections.append(orchestrator_section)
                    sections.append("")

            elif section_name == 'mcp':
                # Section: MCP Research (only for RESEARCH intent)
                mcp_section = None
                if mcp_results and intent == IntentType.RESEARCH:
                    mcp_section = self._build_mcp_section(mcp_results)
                    sections.append(mcp_section)
                    sections.append("")

            elif section_name == 'alerts':
                # Section: Alerts (deduplicated warnings)
                alerts_section = None
                if alerts and len(alerts) > 0 and 'alerts' not in output_rules.suppress_sections:
                    alerts_section = self._build_alerts_section(alerts, intent)
                    sections.append(alerts_section)
                    sections.append("")

            elif section_name == 'compliance':
                # Section: Compliance info (for DOC_LOOKUP)
                if intent == IntentType.DOC_LOOKUP:
                    compliance_section = self._build_compliance_section(findings)
                    if compliance_section:
                        sections.append(compliance_section)
                        sections.append("")

            elif section_name == 'health':
                # Section: Health checks (for MODULE_HEALTH)
                if intent == IntentType.MODULE_HEALTH:
                    health_section = self._build_health_section(findings)
                    if health_section:
                        sections.append(health_section)
                        sections.append("")

            elif section_name == 'context':
                # Section: Implementation context (for CODE_LOCATION)
                if intent == IntentType.CODE_LOCATION and search_results:
                    context_section = self._build_context_section(search_results)
                    if context_section:
                        sections.append(context_section)
                        sections.append("")

        # Always include intent section first (unless suppressed)
        intent_section = self._build_intent_section(intent, query)
        if 'intent' not in output_rules.suppress_sections:
            intent_section = self._build_intent_section(intent, query)
            sections.insert(0, intent_section)
            sections.insert(1, "")

        full_output = "\n".join(sections)

        logger.debug(
            "[OUTPUT-COMPOSER] Composed %d sections for %s intent using context-aware rules",
            len(sections) // 2,  # Divide by 2 because we add empty lines
            intent.value
        )

        # Extract the sections we built for the ComposedOutput
        final_findings_section = ""
        final_mcp_section = None
        final_alerts_section = None

        # Find the sections we built
        for section_name in section_order:
            if section_name == 'results':
                final_findings_section = self._build_findings_section(findings, intent, search_results)
            elif section_name == 'mcp' and mcp_results and intent == IntentType.RESEARCH:
                final_mcp_section = self._build_mcp_section(mcp_results)
            elif section_name == 'alerts' and alerts and len(alerts) > 0 and 'alerts' not in output_rules.suppress_sections:
                final_alerts_section = self._build_alerts_section(alerts, intent)

        return ComposedOutput(
            intent_section=intent_section,
            findings_section=final_findings_section,
            mcp_section=final_mcp_section,
            alerts_section=final_alerts_section,
            full_output=full_output
        )

    def _build_guidance_section(self, findings: str) -> Optional[str]:
        """Build WSP guidance section for DOC_LOOKUP intent"""
        guidance_lines = []
        for line in findings.split('\n'):
            if any(keyword in line.upper() for keyword in ['WSP', 'GUIDANCE', 'PROTOCOL']):
                guidance_lines.append(line.strip())

        if guidance_lines:
            return "[GUIDANCE]\n" + "\n".join(guidance_lines[:5])  # Limit to 5 lines
        return None

    def _build_orchestrator_section(self, findings: str) -> Optional[str]:
        """Build orchestrator execution details section"""
        orchestrator_lines = []
        for line in findings.split('\n'):
            if any(keyword in line.upper() for keyword in ['EXECUTED', 'COMPONENT', 'ROUTING', 'PERFORMANCE']):
                orchestrator_lines.append(line.strip())

        if orchestrator_lines:
            return "[ORCHESTRATION]\n" + "\n".join(orchestrator_lines[:3])  # Limit to 3 lines
        return None

    def _build_compliance_section(self, findings: str) -> Optional[str]:
        """Build compliance information section"""
        compliance_lines = []
        for line in findings.split('\n'):
            if any(keyword in line.upper() for keyword in ['COMPLIANCE', 'VIOLATION', 'WSP']):
                compliance_lines.append(line.strip())

        if compliance_lines:
            return "[COMPLIANCE]\n" + "\n".join(compliance_lines[:3])  # Limit to 3 lines
        return None

    def _build_health_section(self, findings: str) -> Optional[str]:
        """Build system health section for MODULE_HEALTH intent"""
        health_lines = []
        for line in findings.split('\n'):
            if any(keyword in line.upper() for keyword in ['HEALTH', 'STATUS', 'OK', 'VIOLATION']):
                health_lines.append(line.strip())

        if health_lines:
            return "[SYSTEM HEALTH]\n" + "\n".join(health_lines[:5])  # Limit to 5 lines
        return None

    def _build_context_section(self, search_results: Dict[str, Any]) -> Optional[str]:
        """Build implementation context section for CODE_LOCATION intent"""
        if not search_results or 'results' not in search_results:
            return None

        context_lines = []
        results = search_results.get('results', [])
        if results:
            context_lines.append(f"Found {len(results)} relevant files")
            # Add module breakdown
            modules = {}
            for result in results[:10]:  # Limit processing
                file_path = result.get('file', '')
                if '/' in file_path:
                    module = file_path.split('/')[1] if len(file_path.split('/')) > 1 else 'root'
                    modules[module] = modules.get(module, 0) + 1

            for module, count in sorted(modules.items()):
                context_lines.append(f"  {module}: {count} files")

        if context_lines:
            return "[IMPLEMENTATION CONTEXT]\n" + "\n".join(context_lines)
        return None

    def _build_intent_section(self, intent: IntentType, query: str) -> str:
        """
        Build [INTENT] section showing classification.

        Args:
            intent: Classified intent
            query: Original query

        Returns:
            Formatted intent section
        """
        intent_descriptions = {
            IntentType.DOC_LOOKUP: "Documentation lookup - Finding specific docs/WSPs",
            IntentType.CODE_LOCATION: "Code location - Finding files/functions",
            IntentType.MODULE_HEALTH: "Module health - Checking compliance/issues",
            IntentType.RESEARCH: "Research - Learning concepts/patterns",
            IntentType.GENERAL: "General search - Exploring codebase"
        }

        description = intent_descriptions.get(intent, "Query processing")

        return f"[INTENT: {intent.value.upper()}]\n{description}"

    def _build_findings_section(self, findings: str, intent: IntentType, search_results: Optional[Dict[str, Any]] = None) -> str:
        """
        Build [FINDINGS] section with intent-aware formatting.

        Args:
            findings: Raw findings from components
            intent: Query intent for formatting
            search_results: Optional HoloIndex search results

        Returns:
            Formatted findings section
        """
        verbosity_level = "standard"
        if getattr(self, "_current_output_rules", None):
            verbosity_level = self._current_output_rules.verbosity_level

        # Extract key findings based on intent
        if intent == IntentType.DOC_LOOKUP:
            # Focus on documentation content, skip noise
            filtered = self._extract_documentation_content(findings)
        elif intent == IntentType.CODE_LOCATION:
            # For CODE_LOCATION, show actual file paths from search results
            if search_results:
                code_limit, doc_limit, line_limit = self._get_limits_for_verbosity(verbosity_level)
                filtered = self._extract_search_file_paths(search_results, code_limit=code_limit, doc_limit=doc_limit)
            else:
                filtered = self._extract_file_locations(findings)
        elif intent == IntentType.MODULE_HEALTH:
            # Show all health/compliance findings
            filtered = self._extract_health_findings(findings)
        elif intent == IntentType.RESEARCH:
            # Show pattern explanations and context
            filtered = self._extract_pattern_explanations(findings)
        else:  # GENERAL
            # Show structured summary
            filtered = self._extract_general_summary(findings)

        _, _, line_limit = self._get_limits_for_verbosity(verbosity_level)
        trimmed = self._limit_lines(filtered, line_limit)
        return f"[FINDINGS]\n{trimmed}"

    def _build_mcp_section(self, mcp_results: str) -> str:
        """
        Build [MCP RESEARCH] section for external research.

        Args:
            mcp_results: MCP tool results

        Returns:
            Formatted MCP section
        """
        return f"[MCP RESEARCH]\nExternal research results:\n{mcp_results}"

    def _build_alerts_section(self, alerts: List[str], intent: IntentType) -> str:
        """
        Build [ALERTS] section with deduplication.

        Args:
            alerts: List of alert/warning strings
            intent: Query intent (some intents suppress alerts)

        Returns:
            Formatted deduplicated alerts section
        """
        # Suppress alerts for focused intents
        if intent in [IntentType.DOC_LOOKUP, IntentType.CODE_LOCATION]:
            # Only show critical alerts, suppress noise
            critical_alerts = [a for a in alerts if 'VIOLATION' in a or 'ERROR' in a]
            if not critical_alerts:
                return "[ALERTS]\n[OK] No critical issues"
            alerts = critical_alerts

        # Deduplicate alerts
        deduplicated = self._deduplicate_alerts(alerts)

        return f"[ALERTS]\n{deduplicated}"

    def _deduplicate_alerts(self, alerts: List[str]) -> str:
        """
        Deduplicate repeated alerts into summary lines.

        Example:
            Input: ["ModLog outdated: module1", "ModLog outdated: module2", ...] x87
            Output: "[U+26A0] 87 modules have outdated ModLog entries"

        Args:
            alerts: List of alert strings

        Returns:
            Deduplicated alert summary

        Token Savings: ~85 lines eliminated for 87 identical warnings
        """
        # Group alerts by type
        alert_groups = defaultdict(list)

        for alert in alerts:
            alert_type = self._extract_alert_type(alert)
            alert_groups[alert_type].append(alert)

        # Format deduplicated alerts
        deduped_lines = []

        for alert_type, instances in sorted(alert_groups.items()):
            count = len(instances)

            if count > 3:
                # Collapse many instances into summary
                deduped_lines.append(f"[U+26A0] {count} instances: {alert_type}")
            elif count > 1:
                # Show count for 2-3 instances
                deduped_lines.append(f"[U+26A0] {count}x {alert_type}")
            else:
                # Show single instance as-is
                deduped_lines.append(f"[U+26A0] {instances[0]}")

        return "\n".join(deduped_lines) if deduped_lines else "[OK] No alerts"

    def _extract_alert_type(self, alert: str) -> str:
        """
        Extract alert type from alert string for grouping.

        Args:
            alert: Alert string

        Returns:
            Alert type identifier
        """
        # Common patterns to extract
        patterns = [
            (r'ModLog\.md older than document', 'ModLog outdated'),
            (r'missing ([\w\.]+)', 'Missing documentation'),
            (r'([\w/\\]+) missing ([\w\.]+)', 'Missing documentation'),
            (r'Large .* file ([\w/\\]+\.py)', 'Large file'),
            (r'Large implementation file detected:\s*[\w/\\]+\.py', 'Large file'),
            (r'[\w/\\]+ lacks matching tests', 'Orphan scripts lack tests'),
            (r'STALE-WARNING.*not updated in (\d+) days', r'Stale docs (\1 days)'),
            (r'coverage (\d+)%', r'Low coverage (\1%)'),
        ]

        for pattern, replacement in patterns:
            match = re.search(pattern, alert, re.IGNORECASE)
            if match:
                if isinstance(replacement, str) and '\\' in replacement:
                    return match.expand(replacement)
                return replacement

        # Default: truncate long alerts
        if len(alert) > 80:
            return alert[:77] + "..."

        return alert

    def _extract_documentation_content(self, findings: str) -> str:
        """Extract documentation content, skip health noise"""
        lines = findings.split('\n')
        doc_lines = []

        for line in lines:
            # Skip noise
            if any(skip in line for skip in [
                '[HOLODAE-', '[SEMANTIC]', '[HEALTH][OK]',
                '[SIZE][WARNING]', '[MODULE][FOUND]'
            ]):
                continue

            # Keep documentation content
            if any(keep in line for keep in [
                'WSP', 'README', 'INTERFACE', 'ModLog',
                'documentation', 'Protocol'
            ]):
                doc_lines.append(line)

        return "\n".join(doc_lines) if doc_lines else findings[:500]

    def _extract_search_file_paths(self, search_results: Dict[str, Any], code_limit: int = 10, doc_limit: int = 5) -> str:
        """
        Extract file paths directly from HoloIndex search results.

        Args:
            search_results: HoloIndex search results dictionary
                Format: {'code': [...], 'wsps': [...]}
                Code result: {'need': str, 'location': str, 'similarity': str, ...}
                WSP result: {'wsp': str, 'title': str, 'path': str, 'similarity': str, ...}

        Returns:
            Formatted list of file paths with relevance info
        """
        file_lines = []

        # Extract code results (use 'location' key)
        if 'code' in search_results:
            code_results = search_results['code']
            if code_results:
                file_lines.append("[U+1F4C1] Code locations:")
                for i, result in enumerate(code_results[:max(1, code_limit)], 1):
                    # Code results use 'location' not 'path'
                    location = result.get('location', 'Unknown')
                    need = result.get('need', '')
                    similarity = result.get('similarity', 'N/A')  # Already formatted as "85.3%"

                    # Format: "1. modules/path/file.py - Description (relevance: 85%)"
                    if need:
                        file_lines.append(f"  {i}. {location}")
                        file_lines.append(f"     {need} (relevance: {similarity})")
                    else:
                        file_lines.append(f"  {i}. {location} (relevance: {similarity})")

        # Extract documentation results (use 'path' key)
        if 'wsps' in search_results:
            wsp_results = search_results['wsps']
            if wsp_results:
                if file_lines:  # Add spacing if code results exist
                    file_lines.append("")
                file_lines.append("[BOOKS] Documentation:")
                for i, result in enumerate(wsp_results[:max(1, doc_limit)], 1):
                    path = result.get('path', 'Unknown')
                    title = result.get('title', '')
                    wsp = result.get('wsp', '')
                    similarity = result.get('similarity', 'N/A')

                    # Format: "1. WSP 35: Title - path (relevance: 85%)"
                    if wsp and title:
                        file_lines.append(f"  {i}. WSP {wsp}: {title}")
                        file_lines.append(f"     {path} (relevance: {similarity})")
                    else:
                        file_lines.append(f"  {i}. {path} (relevance: {similarity})")

        return "\n".join(file_lines) if file_lines else "No files found in search results"

    def _extract_file_locations(self, findings: str) -> str:
        """Extract file locations from component analysis (fallback)"""
        lines = findings.split('\n')
        location_lines = []

        for line in lines:
            # Keep file paths and module info
            if any(keep in line for keep in [
                'modules/', 'holo_index/', '.py',
                '[MODULE]', 'contains', 'files'
            ]):
                # Skip noise markers
                if '[HOLODAE-' not in line and '[SEMANTIC]' not in line:
                    location_lines.append(line)

        return "\n".join(location_lines[:20]) if location_lines else "No files found"

    def _extract_health_findings(self, findings: str) -> str:
        """Extract health/compliance findings"""
        lines = findings.split('\n')
        health_lines = []

        for line in lines:
            # Keep health and compliance info
            if any(keep in line for keep in [
                '[HEALTH]', '[PATTERN]', '[ORPHAN]',
                'VIOLATION', 'coverage', 'missing'
            ]):
                health_lines.append(line)

        return "\n".join(health_lines) if health_lines else "[OK] No health issues detected"

    def _extract_pattern_explanations(self, findings: str) -> str:
        """Extract pattern explanations for research"""
        lines = findings.split('\n')
        pattern_lines = []

        for line in lines:
            # Keep pattern coach and explanation content
            if any(keep in line for keep in [
                'Pattern', 'architecture', 'design',
                'how', 'why', 'principle'
            ]):
                pattern_lines.append(line)

        return "\n".join(pattern_lines) if pattern_lines else findings[:1000]

    def _extract_general_summary(self, findings: str) -> str:
        """Extract general summary, keep first N lines of each category"""
        lines = findings.split('\n')
        summary_lines = []

        # Keep section headers and first few entries
        current_section = None
        section_count = 0

        for line in lines:
            # Detect section headers
            if line.startswith('[') and ']' in line:
                current_section = line
                summary_lines.append(line)
                section_count = 0
            elif current_section and section_count < 3:
                # Keep first 3 items per section
                summary_lines.append(line)
                section_count += 1

        return "\n".join(summary_lines) if summary_lines else findings[:1000]

    def _get_limits_for_verbosity(self, verbosity_level: str) -> Tuple[int, int, int]:
        """Return (code_limit, doc_limit, line_limit) based on verbosity."""
        levels = {
            "minimal": (3, 2, 6),
            "balanced": (5, 3, 10),
            "standard": (5, 3, 10),
            "detailed": (7, 4, 14),
            "comprehensive": (10, 5, 18),
        }
        return levels.get(verbosity_level, levels["standard"])

    def _limit_lines(self, content: str, max_lines: int) -> str:
        """Trim content to a maximum number of lines."""
        if max_lines <= 0:
            return ""
        lines = content.splitlines()
        if len(lines) <= max_lines:
            return content
        trimmed = lines[:max_lines]
        return "\n".join(trimmed)


# Singleton instance
_composer_instance: Optional[OutputComposer] = None


def get_composer() -> OutputComposer:
    """
    Get singleton OutputComposer instance.

    Returns:
        Global OutputComposer instance
    """
    global _composer_instance

    if _composer_instance is None:
        _composer_instance = OutputComposer()

    return _composer_instance
