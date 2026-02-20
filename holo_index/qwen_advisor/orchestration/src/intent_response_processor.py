#!/usr/bin/env python3
"""
Intent Response Processor - Extracted from QwenOrchestrator

Handles intent-aware response processing, orchestration decisions,
and output filtering for HoloIndex queries.

WSP 62 Refactoring: Extracted to comply with file size thresholds.
"""

from typing import Any, Dict, List
from holo_index.intent_classifier import IntentType


class IntentResponseProcessor:
    """
    Processes intent-aware responses and orchestration decisions.
    
    Extracted from QwenOrchestrator for WSP 62 compliance.
    """

    def __init__(self, logger, breadcrumb_tracer, output_composer):
        """
        Initialize Intent Response Processor.
        
        Args:
            logger: Logging instance
            breadcrumb_tracer: Breadcrumb event tracer
            output_composer: Output composition engine
        """
        self.logger = logger
        self.breadcrumb_tracer = breadcrumb_tracer
        self.output_composer = output_composer
        self.chain_of_thought_log: List[Dict[str, Any]] = []

    def _log_chain_of_thought(self, step_type: str, message: str) -> None:
        """Log orchestration chain-of-thought (mirrors QwenOrchestrator pattern)."""
        from datetime import datetime
        self.chain_of_thought_log.append({
            'timestamp': datetime.now(),
            'type': step_type,
            'message': message,
        })
        self.logger.info(f"[QWEN-{step_type}] {message}")

    def _extract_component_results_from_report(self, analysis_report: str) -> Dict[str, Any]:
        """
        FIRST PRINCIPLES: Extract structured component results from verbose analysis report

        Parses the massive analysis_report string and extracts actionable data
        for each component to feed into the 0102 summary generator.

        Args:
            analysis_report: The full verbose analysis report string

        Returns:
            Dict mapping component names to their structured results

        Token Budget: ~300 tokens per extraction
        """
        results = {}
        lines = analysis_report.split('\n')

        current_component = None
        component_data = []

        # FIRST PRINCIPLES: Parse report by component sections
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect component section headers
            if '[HEALTH]' in line.upper() or 'health & wsp compliance' in line.lower():
                current_component = 'health_analysis'
                component_data = []
            elif '[SIZE]' in line.upper() or 'file size monitor' in line.lower():
                current_component = 'file_size_monitor'
                component_data = []
            elif '[MODULE]' in line.upper() or 'module analysis' in line.lower():
                current_component = 'module_analysis'
                component_data = []
            elif '[VIBECODING' in line.upper() or 'vibecoding analysis' in line.lower():
                current_component = 'vibecoding_analysis'
                component_data = []
            elif '[ORPHAN' in line.upper() or 'orphan analysis' in line.lower():
                current_component = 'orphan_analysis'
                component_data = []

            # Collect data for current component
            if current_component:
                component_data.append(line)

        # FIRST PRINCIPLES: Structure extracted data
        for component_name in ['health_analysis', 'file_size_monitor', 'module_analysis', 'vibecoding_analysis', 'orphan_analysis']:
            if component_name in locals() and component_name == 'current_component':
                component_lines = component_data
            else:
                component_lines = []

            # Extract actionable insights from component data
            if component_name == 'health_analysis':
                violations = [line for line in component_lines if 'violation' in line.lower() or 'missing' in line.lower()]
                results[component_name] = {'violations': violations[:5]}  # Max 5 violations

            elif component_name == 'file_size_monitor':
                large_files = [line for line in component_lines if 'large file' in line.lower() or 'exceeds' in line.lower()]
                results[component_name] = {'large_files': large_files[:3]}  # Max 3 files

            elif component_name == 'module_analysis':
                incomplete = [line for line in component_lines if 'missing' in line.lower() or 'incomplete' in line.lower()]
                results[component_name] = {'incomplete_modules': incomplete[:3]}  # Max 3 modules

            elif component_name == 'vibecoding_analysis':
                patterns = [line for line in component_lines if 'pattern' in line.lower()]
                results[component_name] = {'patterns': patterns[:2]}  # Max 2 patterns

            elif component_name == 'orphan_analysis':
                orphans = [line for line in component_lines if 'orphan' in line.lower() or 'lack' in line.lower()]
                results[component_name] = {'orphans': orphans[:3]}  # Max 3 orphans

        return results


    def _get_output_filter_for_intent(self, intent: str) -> Dict[str, bool]:
        """
        NEW: QWEN-controlled output filtering based on query intent.

        Reduces noise by only showing relevant information for each intent type.
        """
        filters = {
            "fix_error": {
                "show_init_logs": False,        # Don't show processing details
                "show_decision_logs": False,   # Don't show orchestration decisions
                "show_performance_logs": False, # Don't show effectiveness metrics
                "show_health_checks": False,   # Don't show health analysis
                "show_module_metrics": False,  # Don't show module health
                "show_detailed_analysis": False, # Focus on error solution only
                "show_file_details": True,     # Show file locations for fixes
                "compact_format": True         # Use compact output format
            },
            "locate_code": {
                "show_init_logs": False,        # Minimal processing details
                "show_decision_logs": False,   # No orchestration noise
                "show_performance_logs": False, # No metrics
                "show_health_checks": False,   # No health analysis
                "show_module_metrics": False,  # No module details
                "show_detailed_analysis": False, # Just location info
                "show_file_details": True,     # Show exact file locations
                "compact_format": True         # Clean, focused output
            },
            "explore": {
                "show_init_logs": True,         # Show exploration context
                "show_decision_logs": True,    # Show analysis decisions
                "show_performance_logs": True, # Show effectiveness
                "show_health_checks": True,    # Show health analysis
                "show_module_metrics": True,   # Show module details
                "show_detailed_analysis": True, # Full analysis
                "show_file_details": True,     # Show file details
                "compact_format": False        # Full detailed format
            },
            "wsp_manage": {
                "show_init_logs": False,        # Surgical - no processing noise
                "show_decision_logs": False,   # Focus on WSP status only
                "show_performance_logs": False, # No performance metrics
                "show_health_checks": False,   # No general health - WSP specific
                "show_module_metrics": False,  # No module noise - WSP compliance only
                "show_detailed_analysis": True, # Show WSP compliance details
                "show_file_details": True,     # Show WSP file locations
                "compact_format": True         # Clean, focused WSP format
            },
            "standard": {
                "show_init_logs": False,        # Minimal init logs
                "show_decision_logs": True,    # Show key decisions
                "show_performance_logs": False, # No performance noise
                "show_health_checks": False,   # No health unless requested
                "show_module_metrics": False,  # No module noise
                "show_detailed_analysis": True, # Show analysis
                "show_file_details": True,     # Show files
                "compact_format": False        # Standard format
            }
        }

        return filters.get(intent, filters["standard"])


    def _format_intent_aware_response(self, intent: str, analysis_report: str) -> str:
        """
        NEW: Format response based on query intent for optimal 0102 consumption.

        Different intents get different output formats optimized for their use case.
        """
        if intent == "fix_error":
            # Ultra-compact format for error fixing - just the essentials
            lines = analysis_report.split('\n')
            essential_lines = []

            for line in lines:
                # Keep only critical information
                if any(keyword in line.lower() for keyword in [
                    'error', 'fix', 'solution', 'line', 'file:', 'function',
                    'traceback', 'exception', 'bug', 'issue'
                ]):
                    essential_lines.append(line)

            if essential_lines:
                return "[TOOL] ERROR SOLUTION:\n" + '\n'.join(essential_lines[:5])  # Limit to 5 lines
            else:
                return "[TOOL] ERROR FIXING MODE: Focus on error resolution"

        elif intent == "locate_code":
            # Location-focused format
            lines = analysis_report.split('\n')
            location_lines = []

            for line in lines:
                # Keep location and file information
                if any(keyword in line.lower() for keyword in [
                    'file:', 'line', 'function', 'class', 'def ', 'path:',
                    'location', 'module', 'in file'
                ]):
                    location_lines.append(line)

            if location_lines:
                return "[PIN] CODE LOCATION:\n" + '\n'.join(location_lines[:3])  # Limit to 3 lines
            else:
                return "[PIN] CODE LOCATION MODE: Focus on file and function locations"

        elif intent == "explore":
            # Full analysis for exploration
            return "[SEARCH] EXPLORATION ANALYSIS:\n" + analysis_report

        elif intent == "wsp_manage":
            # Surgical WSP documentation management - focus on compliance
            lines = analysis_report.split('\n')
            wsp_lines = []

            for line in lines:
                # Keep only WSP-related compliance information
                if any(keyword in line.lower() for keyword in [
                    'wsp-guardian', 'compliance', 'documentation', 'readme', 'modlog',
                    'ascii', 'stale', 'outdated', 'violation', 'status'
                ]):
                    wsp_lines.append(line)

            if wsp_lines:
                return "[BOOKS] WSP DOCUMENTATION STATUS:\n" + '\n'.join(wsp_lines[:5])  # Limit to 5 lines
            else:
                return "[BOOKS] WSP MANAGEMENT MODE: Focus on documentation compliance and updates"

        else:
            # Standard format with some filtering
            lines = analysis_report.split('\n')

            # Remove excessive technical details
            filtered_lines = []
            skip_patterns = [
                'holodae-health', 'holodae-analyze', 'holodae-telemetry',
                'effectiveness:', 'processing', 'orchestration'
            ]

            for line in lines:
                if not any(pattern in line.lower() for pattern in skip_patterns):
                    filtered_lines.append(line)

            return '\n'.join(filtered_lines) if filtered_lines else analysis_report


    def _get_orchestration_decisions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get orchestration decisions from performance orchestrator"""
        available_components = {
            "health_analysis": {
                "purpose": "Check system integrity and WSP compliance",
                "triggers": ["query_contains_health", "has_modules"],
                "cost": "medium",
                "value": "high",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when locating code
            },
            "vibecoding_analysis": {
                "purpose": "Detect behavioral vibecoding patterns",
                "triggers": ["query_contains_vibecoding", "has_files"],
                "cost": "low",
                "value": "high",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when locating code
            },
            "file_size_monitor": {
                "purpose": "Monitor for architectural bloat",
                "triggers": ["query_contains_module", "has_files"],
                "cost": "low",
                "value": "medium",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when fixing errors or locating code
            },
            "module_analysis": {
                "purpose": "Validate module structure and dependencies",
                "triggers": ["has_modules", "query_contains_module"],
                "cost": "medium",
                "value": "high",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when locating code
            },
            "pattern_coach": {
                "purpose": "Prevent behavioral vibecoding through coaching",
                "triggers": ["has_files", "query_contains_vibecoding"],
                "cost": "low",
                "value": "medium",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when locating code
            },
            "orphan_analysis": {
                "purpose": "Find dead code and connection opportunities",
                "triggers": ["query_contains_health", "has_modules"],
                "cost": "high",
                "value": "medium",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when locating code
            },
            "wsp_documentation_guardian": {
                "purpose": "Monitor WSP documentation compliance and freshness",
                "triggers": ["has_files", "query_contains_wsp"],
                "cost": "medium",
                "value": "high",
                "skip_for_intents": [],  # Always run for WSP-related queries
            },
        }

        decisions: List[Dict[str, Any]] = []
        for component_name, component_info in available_components.items():
            # Skip components based on intent
            if "skip_for_intents" in component_info:
                if context.get("query_intent") in component_info["skip_for_intents"]:
                    continue  # Skip this component entirely

            should_execute = False
            confidence = 0.5
            reasoning: List[str] = []
            for trigger in component_info["triggers"]:
                if context.get(trigger, False):
                    should_execute = True
                    confidence += 0.2
                    reasoning.append(f"triggered by {trigger}")
            # Skip expensive operations for error fixing
            if context.get("query_intent") == "fix_error" and component_info["cost"] == "high":
                confidence -= 0.3  # Strongly discourage expensive ops when fixing errors
            elif component_info["cost"] == "high" and not context.get("query_contains_health"):
                confidence -= 0.1
            display_name = self._format_component_display(component_name)
            if should_execute and confidence >= 0.6:
                decisions.append(
                    {
                        "component_name": component_name,
                        "decision_type": "execute",
                        "confidence_score": confidence,
                        "reasoning_chain": reasoning,
                        "purpose": component_info["purpose"],
                    }
                )
                self._log_chain_of_thought(
                    "DECISION",
                    f"EXECUTE {display_name} (confidence: {confidence:.2f}) - {', '.join(reasoning)}",
                )
            else:
                self._log_chain_of_thought(
                    "DECISION",
                    f"SKIP {display_name} (confidence: {confidence:.2f}) - insufficient trigger strength",
                )
        return decisions

    @staticmethod
    def _format_component_display(component_name: str) -> str:
        """Format component name for display (snake_case -> Title Case)."""
        return component_name.replace("_", " ").title()

