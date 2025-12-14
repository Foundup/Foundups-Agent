#!/usr/bin/env python3
"""
QwenOrchestrator - Primary orchestrator for HoloDAE intelligence system

This is the Qwen LLM orchestration layer that coordinates all HoloIndex components.
Qwen acts as the "circulatory system" - continuously analyzing and orchestrating operations,
then presenting findings to 0102 for arbitration.

ENHANCEMENT (2025-10-07): Intent-driven component routing with breadcrumb event tracking
Design Doc: docs/agentic_journals/HOLODAE_INTENT_ORCHESTRATION_DESIGN.md

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration), WSP 48 (Recursive Learning)
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Intent Classification Integration
from holo_index.intent_classifier import get_classifier, IntentType

# Breadcrumb Tracer for event tracking
from holo_index.adaptive_learning.breadcrumb_tracer import get_tracer

# PHASE 3: Output Composition Integration
from holo_index.output_composer import get_composer

# PHASE 4: Feedback Learning Integration
from holo_index.feedback_learner import get_learner

from ..qwen_health_monitor import CodeIndexCirculationEngine
from ..architect_mode import ArchitectDecisionEngine

# MCP Integration imports
try:
    from modules.ai_intelligence.ric_dae.src.mcp_tools import ResearchIngestionMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    ResearchIngestionMCP = None


COMPONENT_META = {
    'health_analysis': ('[PILL][OK]', 'Health & WSP Compliance'),
    'vibecoding_analysis': ('[AI]', 'Vibecoding Analysis'),
    'file_size_monitor': ('[RULER]', 'File Size Monitor'),
    'module_analysis': ('[BOX]', 'Module Analysis'),
    'pattern_coach': ('[AI]', 'Pattern Coach'),
    'orphan_analysis': ('[GHOST]', 'Orphan Analysis'),
    'wsp_documentation_guardian': ('[BOOKS]', 'WSP Documentation Guardian'),
}

# Intent-to-Component Routing Map (ENHANCEMENT 2025-10-07)
# Maps IntentType to relevant components for smart routing
INTENT_COMPONENT_MAP = {
    IntentType.DOC_LOOKUP: [
        'wsp_documentation_guardian',  # Primary - WSP/README/INTERFACE docs
        'module_analysis'              # Secondary - module context
    ],
    IntentType.CODE_LOCATION: [
        'module_analysis',             # Primary - find files/modules
        'orphan_analysis',             # Secondary - check if orphaned
        'file_size_monitor'            # Secondary - large file warnings
    ],
    IntentType.MODULE_HEALTH: [
        'health_analysis',             # Primary - WSP compliance
        'vibecoding_analysis',         # Secondary - pattern violations
        'orphan_analysis',             # Secondary - orphaned files
        'file_size_monitor'            # Secondary - size issues
    ],
    IntentType.RESEARCH: [
        'pattern_coach',               # Primary - explain patterns
        'wsp_documentation_guardian',  # Secondary - WSP context
        # MCP tools called separately for RESEARCH intent
    ],
    IntentType.GENERAL: [
        # FIRST PRINCIPLES: Smart component selection based on query content
        # Instead of running ALL components, select 2-3 most relevant based on keywords
        # This is handled by _select_general_components() method below
    ]
}

# WSP Documentation Guardian Configuration
WSP_DOC_CONFIG = {
    'doc_only_modules': {
        'holo_index/docs',
        'WSP_framework/docs',
        'WSP_framework/historic_assets',
        'WSP_framework/reports/legacy',
    },
    'expected_update_intervals_days': {
        'README.md': 90,  # Quarterly updates
        'ModLog.md': 30,  # Monthly updates (tracking changes)
        'requirements.txt': 30,  # Monthly dependency updates
        'INTERFACE.md': 60,  # Bi-monthly API changes
        'ROADMAP.md': 30,  # Monthly planning updates
    },
    'auto_remediate_ascii': False,  # Default to read-only mode - remediation opt-in
    'remediation_log_path': 'WSP_framework/docs/WSP_ASCII_REMEDIATION_LOG.md',
    'backup_temp_dir': 'temp/wsp_backups',  # Store backups in temp directory
}

class QwenOrchestrator:
    """Primary orchestrator for HoloDAE - Qwen's decision-making and coordination layer"""

    def __init__(self, coordinator=None) -> None:
        """Initialize the Qwen orchestrator"""
        self._ensure_utf8_console()
        self.logger = logging.getLogger('holodae_activity')
        self.chain_of_thought_log: List[Dict[str, Any]] = []
        self.performance_history: List[float] = []
        self._last_files: List[str] = []
        self._last_modules: List[str] = []
        self._last_executed_components: List[str] = []
        self.repo_root = Path(__file__).resolve().parents[3]
        self.coordinator = coordinator  # Reference to HoloDAECoordinator for MCP logging

        # Initialize QWEN filtering attributes
        self._intent_filters = {}
        self._intent_keywords = {}
        self._max_suggestions = 10
        self._deduplicate_alerts = False

        # ENHANCEMENT (2025-10-07): Intent classifier for smart routing
        self.intent_classifier = get_classifier()
        self._log_chain_of_thought("INTENT-INIT", "[TARGET] Intent classifier initialized")

        # ENHANCEMENT (2025-10-07): Breadcrumb tracer for event tracking
        self.breadcrumb_tracer = get_tracer()
        # Initialize Services
        self.mission_coordinator = MissionCoordinator(agent_type="qwen" if self._is_qwen_agent() else "0102")
        self.component_router = ComponentRouter()
        self.mcp_handler = MCPHandler(mcp_client=getattr(self, 'mcp_client', None), logger=self._log_chain_of_thought)

        # Initialize core components
        self.intent_classifier = IntentClassifier()
        self.feedback_learner = FeedbackLearner()
        self.output_composer = OutputComposer()
        self.breadcrumb_tracer = BreadcrumbTracer()
        
        # Performance tracking
        self.performance_history = []
        self._last_module_snapshots = {}

        # WSP 93: CodeIndex circulation + architect decision helpers
        self.codeindex_engine = CodeIndexCirculationEngine()
        self.architect_engine = ArchitectDecisionEngine()
        self._last_module_snapshots: Dict[str, Dict[str, Any]] = {}
        self._last_codeindex_reports: List[Dict[str, Any]] = []

        # Initialize MCP client if available
        if MCP_AVAILABLE and ResearchIngestionMCP:
            try:
                self.mcp_client = ResearchIngestionMCP()
                # Update handler with client
                self.mcp_handler.mcp_client = self.mcp_client
            except Exception as e:
                print(f"[WARN] Failed to initialize MCP client: {e}")
                self.mcp_client = None
        if any(word in query_lower for word in ['orphan', 'missing', 'test', 'connection']):
            component_scores['orphan_analysis'] += 3

        if any(word in query_lower for word in ['doc', 'readme', 'interface', 'modlog', 'documentation']):
            component_scores['wsp_documentation_guardian'] += 3

        # Score based on file/module context (FIRST PRINCIPLES: Context awareness)
        if len(files) > 10:
            component_scores['file_size_monitor'] += 2  # Large result sets suggest size monitoring
        if len(modules) > 3:
            component_scores['module_analysis'] += 2    # Multiple modules suggest module analysis

        # FIRST PRINCIPLES: Select top 2-3 components with highest relevance
        # Never select more than 3 to prevent output overload
        sorted_components = sorted(component_scores.items(), key=lambda x: x[1], reverse=True)
        selected = [comp for comp, score in sorted_components if score > 0][:3]

        # FIRST PRINCIPLES: Ensure at least basic analysis if no strong matches
        if not selected:
            selected = ['module_analysis', 'health_analysis']  # Minimal useful analysis

        self._log_chain_of_thought(
            "SMART-SELECTION",
            f"[TARGET] GENERAL query '{query[:30]}...' -> Selected {len(selected)} components: {', '.join(selected)}"
        )

        return selected

    def orchestrate_monitoring(self, work_context):
        """Handle monitoring orchestration for autonomous HoloDAE"""
        # Create a monitoring result object with expected attributes for self-improvement
        class MonitoringResult:
            def __init__(self, active_files=0, task_pattern='monitoring'):
                self.violations_found = []
                self.optimization_suggestions = []
                self.pattern_alerts = []
                self.active_files_count = active_files
                self.task_pattern = task_pattern
                self.timestamp = datetime.now().isoformat()
                self.status = 'monitoring_complete'

        active_files = len(work_context.active_files) if hasattr(work_context, 'active_files') else 0
        task_pattern = getattr(work_context, 'task_pattern', 'monitoring')

        return MonitoringResult(active_files, task_pattern)

    def orchestrate_holoindex_request(self, query: str, search_results: Dict[str, Any]) -> str:
        """
        Handle incoming HoloIndex request with intent-driven orchestration
        """
        involved_files = self._extract_files_from_results(search_results)
        involved_modules = self._extract_modules_from_files(involved_files)

        # Persist context for coordinator integration
        self._last_files = involved_files.copy()
        self._last_modules = involved_modules.copy()

        # Log the orchestration initiation
        self._log_chain_of_thought("INIT", f"Processing HoloIndex query: '{query}'")
        self._log_chain_of_thought(
            "CONTEXT",
            f"Found {len(involved_files)} files across {len(involved_modules)} modules",
        )

        if not involved_files:
            self._log_chain_of_thought("DECISION", "No files to analyze - returning early")
            return "[HOLODAE-ANALYZE] No files found to analyze"

        # FIRST PRINCIPLES: Check for mission coordination FIRST (MCP adoption, then orphans)
        
        # Check MCP adoption status first (higher priority)
        mcp_coordination = self.mission_coordinator.coordinate_mcp_adoption_mission(query)
        if mcp_coordination is not None:
            self._log_chain_of_thought(
                "COORDINATION",
                f"[U+1F3D7]️ MCP adoption mission detected - HoloIndex providing Rubik status"
            )
            return mcp_coordination

        # Check orphan archaeology coordination
        orphan_coordination = self.mission_coordinator.coordinate_orphan_archaeology_mission(query)
        if orphan_coordination is not None:
            self._log_chain_of_thought(
                "COORDINATION",
                f"[U+1F3DB]️ Orphan archaeology mission detected - HoloIndex coordinating Qwen/Gemma analysis"
            )
            return orphan_coordination

        # ENHANCEMENT: Classify intent using new intent classifier
        intent_classification = self.intent_classifier.classify(query)
        intent = intent_classification.intent

        # BREADCRUMB EVENT: Intent classification
        self.breadcrumb_tracer.add_action(
            'intent_classification',
            intent.value,
            f"Query classified as {intent.value} (confidence: {intent_classification.confidence:.2f})",
            query
        )

        self._log_chain_of_thought(
            "INTENT",
            f"[TARGET] Classified as {intent.value.upper()} (confidence: {intent_classification.confidence:.2f}, patterns: {len(intent_classification.patterns_matched)})"
        )

        context = self._build_orchestration_context(query, involved_files, involved_modules, intent)

        # Legacy intent mapping for backward compatibility with output filters
        legacy_intent = self._map_intent_to_legacy(intent)
        output_filter = self._get_output_filter_for_intent(legacy_intent)

        # PHASE 5: MCP Integration Separation (Intent-Gated)
        mcp_insights = []
        if intent == IntentType.RESEARCH:
            self._log_chain_of_thought("MCP-GATE", "[U+1F52C] RESEARCH intent detected - calling MCP tools")
            mcp_insights = self.mcp_handler.call_research_mcp_tools(query, context)
            if mcp_insights:
                self._log_chain_of_thought("MCP-RESEARCH", f"[SEARCH] Retrieved {len(mcp_insights)} research insights")
                self.mcp_handler.learn_from_mcp_usage(query, mcp_insights, context)
        else:
            self._log_chain_of_thought("MCP-SKIP", f"⏭️ Intent {intent.value} - skipping MCP research tools")

        # Log detected intent
        if intent == "fix_error":
            self._log_chain_of_thought("INTENT", "[TOOL] Error fixing mode - minimizing health checks")
        elif intent == "locate_code":
            self._log_chain_of_thought("INTENT", "[PIN] Code location mode - focused output")
        elif intent == "explore":
            self._log_chain_of_thought("INTENT", "[SEARCH] Exploration mode - full analysis")

        # ENHANCEMENT: Get intent-based component routing
        base_components = self.component_router.select_components(intent.value, query, involved_files, involved_modules)

        # PHASE 4: Apply feedback learning to filter components
        components_to_execute = self.feedback_learner.get_filtered_components(
            intent=intent,
            available_components=base_components,
            threshold=0.3  # Filter components with weight < 0.3
        )

        # BREADCRUMB EVENT: Component routing decision
        all_components = list(COMPONENT_META.keys())
        components_filtered = [c for c in all_components if c not in components_to_execute]

        self.breadcrumb_tracer.add_discovery(
            'component_routing',
            f"routed_{intent.value}",
            f"Selected {len(components_to_execute)} relevant, filtered {len(components_filtered)} noisy"
        )

        self._log_chain_of_thought(
            "ROUTING",
            f"[PIN] Intent {intent.value} -> {len(components_to_execute)} components selected (filtered {len(components_filtered)})"
        )

        # Get orchestration decisions for selected components only
        raw_decisions = self._get_orchestration_decisions_for_components(
            context, components_to_execute
        )
        orchestration_decisions = self._filter_orchestration_decisions(raw_decisions, output_filter)

        # Execute analysis with filtered output
        import time
        start_time = time.time()

        analysis_report = self._execute_orchestrated_analysis_filtered(
            query, involved_files, involved_modules, orchestration_decisions, output_filter
        )

        should_codeindex, trigger_reason = self._should_trigger_codeindex(
            query=query,
            intent_classification=intent_classification,
            module_snapshots=self._last_module_snapshots,
        )
        if should_codeindex:
            codeindex_section = self._generate_codeindex_section(self._last_module_snapshots)
            if codeindex_section:
                analysis_report = f"{analysis_report}\n{codeindex_section}"
                self._log_chain_of_thought("CODEINDEX", f"🩺 CodeIndex triggered: {trigger_reason}")
                self.breadcrumb_tracer.add_action(
                    'codeindex_activation',
                    'codeindex_surgical',
                    trigger_reason,
                    query
                )

        duration_ms = int((time.time() - start_time) * 1000)

        # BREADCRUMB EVENT: Orchestration execution
        self.breadcrumb_tracer.add_action(
            'orchestration_execution',
            f"executed_{len(orchestration_decisions)}_components",
            f"Executed {len(orchestration_decisions)} components in {duration_ms}ms",
            query
        )

        # Calculate effectiveness (filtered logging)
        effectiveness = self._calculate_analysis_effectiveness(analysis_report)
        self.performance_history.append(effectiveness)
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]

        if output_filter["show_performance_logs"]:
            self._log_chain_of_thought("EFFECTIVENESS", f"Analysis effectiveness: {effectiveness:.2f}")

        # PHASE 3: Output Composition - Structure and deduplicate output
        # Collect alerts from analysis_report
        collected_alerts = []
        for line in analysis_report.split('\n'):
            if any(keyword in line.upper() for keyword in ['WARNING', 'VIOLATION', 'STALE', 'ALERT', 'ERROR']):
                collected_alerts.append(line.strip())

        # Format MCP insights if available
        mcp_section = None
        if mcp_insights:
            mcp_lines = []
            for insight in mcp_insights[:3]:  # Limit to top 3 insights
                tool_name = insight.get('tool_name', 'Unknown')
                result = insight.get('result', 'No result')
                mcp_lines.append(f"  - [{tool_name}] {result[:200]}...")  # Truncate long results
            mcp_section = '\n'.join(mcp_lines)

        # Compose structured output with context-aware formatting
        composed = self.output_composer.compose(
            intent_classification=intent_classification,
            findings=analysis_report,
            mcp_results=mcp_section,
            alerts=collected_alerts if collected_alerts else None,
            query=query,
            search_results=search_results  # Pass search results for CODE_LOCATION
        )

        # BREADCRUMB EVENT: Output composition
        self.breadcrumb_tracer.add_action(
            'output_composition',
            f"composed_{intent.value}",
            f"Composed {len(composed.full_output)} chars with {len(collected_alerts)} alerts",
            query
        )

        # FIRST PRINCIPLES: For GENERAL queries, use intelligent 0102 summary instead of massive output
        if intent == IntentType.GENERAL:
            # Import throttler here to avoid circular imports
            from holo_index.output.agentic_output_throttler import AgenticOutputThrottler

            throttler = AgenticOutputThrottler()
            throttler.set_query_context(query, search_results)

            # Extract component results from analysis_report for summary generation
            component_results = self._extract_component_results_from_report(analysis_report)

            concise_summary = throttler.generate_0102_summary(component_results, query)

            # Log the efficiency gain
            original_length = len(composed.full_output.split())
            summary_length = len(concise_summary.split())
            compression_ratio = original_length / max(summary_length, 1)

            self._log_chain_of_thought(
                "0102-OPTIMIZATION",
                f"[TARGET] GENERAL query optimized: {compression_ratio:.1f}x compression ({original_length} -> {summary_length} tokens)"
            )

            return concise_summary

        # Return composed output for other intents (replaces legacy format_intent_aware_response)
        return composed.full_output

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

    def _filter_orchestration_decisions(self, decisions: List[Dict[str, Any]], output_filter: Dict[str, bool]) -> List[Dict[str, Any]]:
        """
        NEW: Filter orchestration decisions based on QWEN output filter
        """
        if not output_filter:
            return decisions

        # Filter out components based on intent
        filtered_decisions = []
        for decision in decisions:
            component = decision.get('component', '')

            # Skip health checks for error/locator intents
            if not output_filter.get("show_health_checks", True):
                if 'health' in component.lower():
                    continue

            # Skip module analysis for simple queries
            if not output_filter.get("show_module_metrics", True):
                if 'module' in component.lower():
                    continue

            filtered_decisions.append(decision)

        return filtered_decisions

    def _execute_orchestrated_analysis_filtered(self, query: str, files: List[str], modules: List[str],
                                               orchestration_decisions: List[Dict[str, Any]],
                                               output_filter: Dict[str, bool] = None) -> str:
        """
        Enhanced with QWEN output filtering during execution
        """
        # Use existing method
        report = self._execute_orchestrated_analysis(query, files, modules, orchestration_decisions)

        if output_filter and output_filter.get("compact_format", False):
            # Apply compact formatting
            lines = report.split('\n')
            compact_lines = []

            # Keep headers and essential info, skip noise
            for line in lines:
                # Skip noisy technical details
                if any(noise in line.lower() for noise in [
                    'holodae-', 'orchestration', 'processing', 'telemetry',
                    'effectiveness', 'chain-of-thought'
                ]):
                    continue

                # Keep important information
                if line.strip() and len(line.strip()) > 10:  # Meaningful content
                    compact_lines.append(line)

            return '\n'.join(compact_lines[:10]) if compact_lines else report  # Limit output

        return report

    def _should_trigger_codeindex(
        self,
        query: str,
        intent_classification,
        module_snapshots: Dict[str, Dict[str, Any]],
    ) -> Tuple[bool, str]:
        """Decide if CodeIndex surgical analysis should augment the response."""
        if not module_snapshots:
            return False, ""

        query_lower = query.lower()
        reasons: List[str] = []

        keyword_map = {
            "keyword 'codeindex'": ["codeindex", "surgical"],
            "refactor keyword": ["refactor", "split function", "break apart", "too long"],
            "optimization keyword": ["optimize", "performance", "efficiency"],
        }
        for label, keywords in keyword_map.items():
            if any(keyword in query_lower for keyword in keywords):
                reasons.append(label)
                break

        large_modules = [
            module for module, snapshot in module_snapshots.items()
            if snapshot.get("large_python_files")
        ]
        if large_modules:
            reasons.append(f"large modules detected ({len(large_modules)})")

        coverage_gaps = [
            module for module, snapshot in module_snapshots.items()
            if snapshot.get("py_file_count", 0) >= 3 and snapshot.get("test_count", 0) == 0
        ]
        if coverage_gaps and intent_classification.intent in {
            IntentType.CODE_LOCATION,
            IntentType.MODULE_HEALTH,
            IntentType.GENERAL,
        }:
            reasons.append("module coverage gap identified")

        if intent_classification.intent == IntentType.MODULE_HEALTH:
            reasons.append("module health review")

        # Encourage pattern-based triggers only when module set is manageable
        if len(module_snapshots) > 6 and not reasons:
            return False, ""

        if not reasons:
            return False, ""

        return True, "; ".join(reasons[:3])

    def _generate_codeindex_section(self, module_snapshots: Dict[str, Dict[str, Any]]) -> str:
        """Produce textual summary of CodeIndex reports for selected modules."""
        if not module_snapshots:
            return ""

        module_candidates: List[Tuple[int, str, Path]] = []
        for module, snapshot in module_snapshots.items():
            path = snapshot.get("path")
            if not path or not snapshot.get("exists"):
                continue
            score = 0
            large_files = snapshot.get("large_python_files", [])
            if large_files:
                score += min(6, len(large_files) * 2)
                max_lines = max((info[1] for info in large_files), default=0)
                score += min(6, max_lines // 200)
            if snapshot.get("py_file_count", 0) and snapshot.get("test_count", 0) == 0:
                score += 2
            module_candidates.append((score, module, path))

        module_candidates.sort(key=lambda item: item[0], reverse=True)
        selected_paths = [
            path for score, module, path in module_candidates if score > 0
        ][:2]
        if not selected_paths and module_candidates:
            selected_paths = [module_candidates[0][2]]
        if not selected_paths:
            return ""

        reports = self.codeindex_engine.evaluate_modules(selected_paths)
        if not reports:
            return ""

        self._last_codeindex_reports = [report.to_summary() for report in reports]

        lines: List[str] = ["[CODEINDEX][WSP 93] Surgical intelligence summary:"]
        for report in reports:
            lines.append(f"  - Module {report.module_name}: {report.critical_fix_count()} critical fixes")
            for fix in report.surgical_fixes[:2]:
                lines.append(
                    f"    - {fix.function} ({fix.line_range}) -> {fix.estimated_effort}min (complexity {fix.complexity})"
                )
            architect_lines = self.architect_engine.summarize(report).splitlines()
            for architect_line in architect_lines[:4]:
                lines.append(f"    {architect_line}")
            if report.assumption_alerts:
                assumption_lines = [
                    line.strip() for line in report.assumption_alerts.splitlines()
                    if line.strip() and not line.startswith("[ASSUMPTIONS]")
                ][:2]
                for assumption_line in assumption_lines:
                    lines.append(f"    [ASSUMPTION] {assumption_line}")
        return "\n".join(lines)

    def get_recent_analysis_context(self) -> Dict[str, List[str]]:
        """Return the most recent file/module context analyzed by Qwen"""
        return {'files': self._last_files.copy(), 'modules': self._last_modules.copy()}

    def get_recent_execution_summary(self) -> Dict[str, Any]:
        """Return latest executed component list for downstream consumers"""
        return {'executed_components': self._last_executed_components.copy()}

    def record_feedback(self, query: str, intent: IntentType, components: List[str], rating: str, notes: str = "") -> Optional[str]:
        """
        PHASE 4: Record user feedback for recursive learning

        Args:
            query: The original query
            intent: Classified intent type
            components: Components that were executed
            rating: "good", "noisy", or "missing"
            notes: Optional notes about the feedback

        Returns:
            Feedback ID if recorded, None if error
        """
        from holo_index.feedback_learner import FeedbackRating, FeedbackDimensions

        # Map string rating to enum
        rating_map = {
            "good": FeedbackRating.GOOD,
            "noisy": FeedbackRating.NOISY,
            "missing": FeedbackRating.MISSING
        }

        feedback_rating = rating_map.get(rating.lower())
        if not feedback_rating:
            self._log_chain_of_thought("FEEDBACK-ERROR", f"Invalid rating: {rating}")
            return None

        # For advanced ratings, parse dimensions from notes
        dimensions = None
        if "relevance:" in notes.lower():
            # Parse dimension scores from notes (format: "relevance:0.8 noise:0.2 ...")
            dimensions = self._parse_feedback_dimensions(notes)

        # Record feedback
        feedback_id = self.feedback_learner.record_feedback(
            query=query,
            intent=intent,
            components_executed=components,
            rating=feedback_rating,
            dimensions=dimensions,
            notes=notes
        )

        if feedback_id:
            self._log_chain_of_thought("FEEDBACK-RECORDED", f"[OK] Feedback recorded: {feedback_id}")

            # BREADCRUMB EVENT: Feedback learning
            self.breadcrumb_tracer.add_action(
                'feedback_learning',
                f"feedback_{rating}",
                f"Recorded {rating} feedback for {len(components)} components",
                query
            )

        return feedback_id

    def _parse_feedback_dimensions(self, notes: str) -> Optional[object]:
        """Parse FeedbackDimensions from notes string"""
        from holo_index.feedback_learner import FeedbackDimensions
        import re

        try:
            # Extract dimension scores (format: "relevance:0.8 noise:0.2 completeness:0.9 efficiency:0.7")
            relevance = float(re.search(r'relevance:(\d+\.?\d*)', notes, re.I).group(1)) if re.search(r'relevance:', notes, re.I) else 0.5
            noise_level = float(re.search(r'noise:(\d+\.?\d*)', notes, re.I).group(1)) if re.search(r'noise:', notes, re.I) else 0.5
            completeness = float(re.search(r'completeness:(\d+\.?\d*)', notes, re.I).group(1)) if re.search(r'completeness:', notes, re.I) else 0.5
            token_efficiency = float(re.search(r'efficiency:(\d+\.?\d*)', notes, re.I).group(1)) if re.search(r'efficiency:', notes, re.I) else 0.5

            return FeedbackDimensions(
                relevance=relevance,
                noise_level=noise_level,
                completeness=completeness,
                token_efficiency=token_efficiency
            )
        except Exception as e:
            self._log_chain_of_thought("FEEDBACK-PARSE-ERROR", f"Failed to parse dimensions: {e}")
            return None

    def _extract_files_from_results(self, search_results: Dict[str, Any]) -> List[str]:
        """Extract file paths from HoloIndex search results"""
        files: List[str] = []
        for category in ('code', 'wsps'):
            hits = search_results.get(category) or []
            for hit in hits:
                file_path: Optional[str] = None
                if category == 'code':
                    file_path = hit.get('location')
                else:
                    file_path = hit.get('path')
                if file_path and file_path not in files:
                    files.append(file_path)
        return files

    def _extract_modules_from_files(self, files: List[str]) -> List[str]:
        """Extract module names from file paths"""
        modules: set[str] = set()
        for file_path in files:
            module = self._extract_module_from_path(file_path)
            if module:
                modules.add(module)
        return list(modules)

    def _extract_module_from_path(self, file_path: str) -> Optional[str]:
        """Extract module name from file path"""
        path_parts = Path(file_path).parts
        if 'modules' in path_parts:
            try:
                idx = path_parts.index('modules')
                if idx + 2 < len(path_parts):
                    return f"modules/{path_parts[idx + 1]}/{path_parts[idx + 2]}"
            except ValueError:
                pass
        if 'holo_index' in path_parts:
            try:
                idx = path_parts.index('holo_index')
                if idx + 1 < len(path_parts):
                    return f"holo_index/{path_parts[idx + 1]}"
            except ValueError:
                pass
        return None

    def _detect_query_intent(self, query: str) -> str:
        """Detect the primary intent of the query for smarter output"""
        lower_query = query.lower()

        # Error fixing takes priority - no health checks needed
        error_keywords = ['error', 'exception', 'traceback', 'fix', 'bug', 'crash',
                         'nonetype', 'attribute', 'failed', 'broken']
        if any(kw in lower_query for kw in error_keywords):
            return "fix_error"

        # WSP documentation management takes precedence - surgical WSP compliance checking
        wsp_keywords = ['wsp', 'windsurf', 'protocol', 'compliance', 'documentation', 'readme', 'modlog']
        if any(kw in lower_query for kw in wsp_keywords):
            return "wsp_manage"

        # Code location request - minimal output
        locate_keywords = ['where', 'find', 'location', 'which file', 'line']
        if any(kw in lower_query for kw in locate_keywords):
            return "locate_code"

        # Regex patterns indicate code search - treat as locate_code for surgical output
        if '.*' in query or '|' in query or '\\' in query or '[' in query:
            return "locate_code"

        # Module exploration - show health
        explore_keywords = ['module', 'structure', 'architecture', 'health', 'status']
        if any(kw in lower_query for kw in explore_keywords):
            return "explore"

        # Default to standard
        return "standard"

    def _build_orchestration_context(
        self,
        query: str,
        files: List[str],
        modules: List[str],
        intent: IntentType = None
    ) -> Dict[str, Any]:
        """
        Build context dictionary for orchestration decisions

        ENHANCEMENT (2025-10-07): Added intent parameter for new classification system
        """
        lower_query = query.lower()

        # Use new intent if provided, otherwise fall back to legacy detection
        if intent is None:
            legacy_intent = self._detect_query_intent(query)
        else:
            legacy_intent = self._map_intent_to_legacy(intent)

        # Only check health if intent is MODULE_HEALTH or GENERAL
        should_check_health = (
            intent in [IntentType.MODULE_HEALTH, IntentType.GENERAL] if intent
            else (legacy_intent == "explore" or 'health' in lower_query)
        )

        return {
            "query": query,
            "query_intent": legacy_intent,  # Legacy field for backward compat
            "intent_type": intent,  # New field for intent-based routing
            "files_count": len(files),
            "modules_count": len(modules),
            "query_keywords": lower_query.split(),
            "is_search_request": True,
            "has_files": bool(files),
            "has_modules": bool(modules),
            "query_contains_health": should_check_health,
            "query_contains_vibecoding": any(kw in lower_query for kw in ['vibe', 'pattern', 'behavior', 'coach']),
            "query_contains_module": any(kw in lower_query for kw in ['module', 'create', 'refactor']),
            "query_contains_error": any(kw in lower_query for kw in ['error', 'fix', 'debug', 'issue']),
            "query_contains_wsp": any(kw in lower_query for kw in ['wsp', 'windsurf', 'protocol', 'compliance', 'documentation']),
        }

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

    def _get_orchestration_decisions_for_components(
        self,
        context: Dict[str, Any],
        allowed_components: List[str]
    ) -> List[Dict[str, Any]]:
        """
        ENHANCEMENT (2025-10-07): Get orchestration decisions for specific components only

        This method filters component execution based on intent-driven routing.
        Only components in allowed_components list are considered.

        Args:
            context: Orchestration context dictionary
            allowed_components: List of component names to consider

        Returns:
            List of orchestration decisions for allowed components only
        """
        # Get all decisions
        all_decisions = self._get_orchestration_decisions(context)

        # Filter to only allowed components
        filtered_decisions = [
            decision for decision in all_decisions
            if decision['component_name'] in allowed_components
        ]

        return filtered_decisions

    def _map_intent_to_legacy(self, intent: IntentType) -> str:
        """
        ENHANCEMENT (2025-10-07): Map new IntentType to legacy intent strings

        For backward compatibility with existing output filter system.

        Args:
            intent: New IntentType enum

        Returns:
            Legacy intent string
        """
        intent_mapping = {
            IntentType.DOC_LOOKUP: "wsp_manage",
            IntentType.CODE_LOCATION: "locate_code",
            IntentType.MODULE_HEALTH: "explore",
            IntentType.RESEARCH: "explore",
            IntentType.GENERAL: "standard"
        }

        return intent_mapping.get(intent, "standard")

    def _execute_orchestrated_analysis(
        self,
        query: str,
        files: List[str],
        modules: List[str],
        decisions: List[Dict[str, Any]],
    ) -> str:
        """Execute the orchestrated analysis components."""
        report_lines: List[str] = [f"[HOLODAE-INTELLIGENCE] Data-driven analysis for query: '{query}'"]
        unique_modules = sorted({module for module in modules if module})
        module_snapshots = {module: self._build_module_snapshot(module) for module in unique_modules}
        self._last_module_snapshots = module_snapshots
        report_lines.append(
            f"[SEMANTIC] {len(files)} files across {len(unique_modules)} modules"
        )

        if not unique_modules:
            report_lines.append("[HOLODAE-CONTEXT] No module directories resolved from search results")

        executed_components: List[str] = []
        for decision in decisions:
            component_name = decision["component_name"]
            display_name = self._format_component_display(component_name)
            results = self._execute_component_stub(
                component_name, query, files, unique_modules, module_snapshots
            )
            if results:
                executed_components.append(display_name)
                report_lines.extend(results)
                self._log_chain_of_thought("PERFORMANCE", f"{display_name} executed with results")

        self._last_executed_components = executed_components
        if executed_components:
            report_lines.append(
                f"[HOLODAE-ORCHESTRATION] Executed components: {', '.join(executed_components)}"
            )
        else:
            report_lines.append(
                "[HOLODAE-ORCHESTRATION] No components produced actionable output"
            )
        return '\n'.join(report_lines)

    def _execute_component_stub(
        self,
        component_name: str,
        query: str,
        files: List[str],
        modules: List[str],
        module_snapshots: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        """Execute a named analysis component using lightweight heuristics."""
        if component_name == "health_analysis":
            return self._run_health_analysis(module_snapshots)
        if component_name == "vibecoding_analysis":
            return self._run_vibecoding_analysis(module_snapshots)
        if component_name == "file_size_monitor":
            return self._run_file_size_monitor(files, module_snapshots)
        if component_name == "module_analysis":
            return self._run_module_analysis(module_snapshots)
        if component_name == "pattern_coach":
            return self._run_pattern_coach(module_snapshots)
        if component_name == "orphan_analysis":
            return self._run_orphan_analysis(module_snapshots)
        if component_name == "wsp_documentation_guardian":
            return self._run_wsp_documentation_guardian(query, files, modules, module_snapshots)
        return []

    def _run_health_analysis(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        if not module_snapshots:
            return ["[HEALTH][OK] No modules to audit in current query"]
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                lines.append(f"[HEALTH][WARNING] FOUND missing module on disk: {module}")
                continue
            missing_docs = snapshot['missing_docs']
            if missing_docs:
                lines.append(
                    f"[HEALTH][VIOLATION] {module} missing {', '.join(missing_docs)} (WSP 22)"
                )
            else:
                lines.append(f"[HEALTH][OK] {module} documentation complete")
        return lines

    def _run_vibecoding_analysis(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                continue
            py_count = snapshot['py_file_count']
            tests = snapshot['test_count']
            if py_count == 0:
                continue
            coverage = tests / py_count
            if tests == 0 and py_count >= 3:
                lines.append(
                    f"[PATTERN] Found {py_count} implementation files with 0 tests in {module} (coverage 0%)"
                )
            elif coverage < 0.2 and py_count >= 5:
                lines.append(
                    f"[PATTERN] Low coverage {coverage:.0%} in {module} ({tests} tests across {py_count} files)"
                )
        if not lines:
            lines.append("[VIBECODING-PATTERN] No high-risk vibecoding patterns detected")
        return lines

    def _run_file_size_monitor(
        self,
        files: List[str],
        module_snapshots: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        lines: List[str] = []
        flagged: set[str] = set()
        for snapshot in module_snapshots.values():
            if not snapshot['exists']:
                continue
            for py_file, line_count, size_kb in snapshot['large_python_files']:
                rel = self._relative_path(py_file)
                if rel in flagged:
                    continue
                lines.append(
                    f"[SIZE][WARNING] FOUND large file {rel} ({line_count} lines, {size_kb} KB)"
                )
                flagged.add(rel)
        for file_path in files:
            resolved = self._resolve_file_path(file_path)
            if not resolved or not resolved.exists():
                continue
            rel = self._relative_path(resolved)
            if rel in flagged:
                continue
            size_kb = max(1, resolved.stat().st_size // 1024)
            if resolved.suffix == '.py':
                line_count = self._count_file_lines(resolved)
                if line_count > 400 or size_kb > 120:
                    lines.append(
                        f"[SIZE][WARNING] FOUND large file {rel} ({line_count} lines, {size_kb} KB)"
                    )
                    flagged.add(rel)
            elif size_kb > 256:
                lines.append(
                    f"[SIZE][NOTICE] FOUND large artifact {rel} ({size_kb} KB)"
                )
                flagged.add(rel)
        if not lines:
            lines.append("[HOLODAE-SIZE][OK] No file size anomalies detected")
        return lines

    def _run_module_analysis(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                continue
            py_count = snapshot['py_file_count']
            tests = snapshot['test_count']
            lines.append(
                f"[MODULE][FOUND] {module} contains {py_count} python files with {tests} tests"
            )
            if snapshot['missing_docs']:
                lines.append(
                    f"[MODULE][WARNING] {module} missing {', '.join(snapshot['missing_docs'])}"
                )
            if snapshot['large_python_files']:
                rel = self._relative_path(snapshot['large_python_files'][0][0])
                lines.append(
                    f"[MODULE][WARNING] Large implementation file detected: {rel}"
                )
        if not lines:
            lines.append("[HOLODAE-MODULE][OK] Modules within healthy structural bounds")
        return lines

    def _run_pattern_coach(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                continue
            if snapshot['missing_docs']:
                lines.append(
                    f"[PATTERN] Found documentation gap in {module}: {', '.join(snapshot['missing_docs'])}"
                )
            if snapshot['script_orphans']:
                samples = ', '.join(
                    self._relative_path(path) for path in snapshot['script_orphans'][:2]
                )
                lines.append(
                    f"[PATTERN] Found {len(snapshot['script_orphans'])} scripts lacking tests in {module}: {samples}"
                )
        if not lines:
            lines.append("[PATTERN-COACH] Patterns stable - no interventions required")
        return lines

    def _run_orphan_analysis(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                continue
            orphans = snapshot['script_orphans']
            for orphan in orphans[:3]:
                rel = self._relative_path(orphan)
                lines.append(f"[ORPHAN-FOUND] {rel} lacks matching tests - investigate connection")
            if len(orphans) > 3:
                lines.append(
                    f"[ORPHAN-SUMMARY] {len(orphans)} potential orphan scripts detected in {module}"
                )
        if not lines:
            lines.append("[ORPHAN-ANALYSIS][OK] No orphaned scripts identified")
        return lines

    def _run_wsp_documentation_guardian(
        self,
        query: str,
        files: List[str],
        modules: List[str],
        module_snapshots: Dict[str, Dict[str, Any]],
        remediation_mode: bool = False
    ) -> List[str]:
        """
        WSP Documentation Guardian - Enhanced First Principles Implementation

        QWEN FIRST PRINCIPLES APPLIED:
        1. Understand Context - Detect WSP-related queries vs code queries
        2. Surgical Filtering - Show only relevant WSP compliance info
        3. Remove Corruption - Auto-sanitize ASCII violations (WSP 20)
        4. Focus on Essence - Show current compliance status and missing docs
        5. Continuous Learning - Log all WSP compliance checks and improvements

        ENHANCED FEATURES:
        - Doc-only exemption map integration
        - Config-driven update intervals
        - Automatic ASCII remediation
        - ModLog remediation tracking
        """
        lines: List[str] = []
        wsp_related_files = []
        wsp_framework_docs = []
        remediation_actions = []

        # Load WSP configuration
        config = WSP_DOC_CONFIG

        # Index WSP documentation from framework and modules
        for file_path in files:
            if 'wsp' in file_path.lower() or 'WSP' in file_path:
                wsp_related_files.append(file_path)

        # Check WSP framework documentation with smart exemptions
        wsp_framework_path = self.repo_root / "WSP_framework"
        if wsp_framework_path.exists():
            for md_file in wsp_framework_path.rglob("*.md"):
                file_path_str = str(md_file)
                wsp_framework_docs.append(file_path_str)

                # Skip doc-only modules for freshness checks
                rel_path = self._relative_path(md_file)
                is_doc_only = self._is_doc_only_path(rel_path, config['doc_only_modules'])

                if not is_doc_only:
                    # Check modification date with config-driven intervals
                    file_name = md_file.name
                    expected_interval = config['expected_update_intervals_days'].get(file_name, 90)  # Default quarterly

                    modlog_path = md_file.parent / "ModLog.md"
                    doc_mtime = md_file.stat().st_mtime
                    days_since_update = (datetime.now().timestamp() - doc_mtime) / 86400

                    if days_since_update > expected_interval:
                        lines.append(f"[WSP-GUARDIAN][STALE-WARNING] {rel_path} not updated in {days_since_update:.0f} days (expected: {expected_interval}d)")
                        # Note: Stale docs are warnings only - not added to remediation_actions
                        # Remediation_actions are reserved for actual file modifications
                    elif modlog_path.exists():
                        modlog_mtime = modlog_path.stat().st_mtime
                        if modlog_mtime < doc_mtime:
                            lines.append(f"[WSP-GUARDIAN][OUTDATED] {self._relative_path(modlog_path)} older than document")

        # Check module WSP compliance
        wsp_compliant_modules = 0
        total_modules = 0

        for module in modules:
            if module and module_snapshots.get(module, {}).get('exists'):
                total_modules += 1
                snapshot = module_snapshots[module]
                missing_docs = snapshot.get('missing_docs', [])

                # Check for required WSP documentation
                required_wsp_docs = ['README.md', 'ModLog.md']
                missing_wsp_docs = [doc for doc in missing_docs if doc in required_wsp_docs]

                if not missing_wsp_docs:
                    wsp_compliant_modules += 1
                else:
                    lines.append(f"[WSP-GUARDIAN][VIOLATION] {module} missing WSP docs: {', '.join(missing_wsp_docs)}")

        if total_modules > 0:
            compliance_rate = wsp_compliant_modules / total_modules
            lines.append(f"[WSP-GUARDIAN][STATUS] WSP compliance: {wsp_compliant_modules}/{total_modules} modules ({compliance_rate:.1%})")

        # ASCII compliance check with conditional remediation
        ascii_violations = []
        ascii_remediated = []

        for file_path in wsp_related_files + wsp_framework_docs:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if any(ord(c) > 127 for c in content):
                    rel_path = self._relative_path(file_path)
                    ascii_violations.append(rel_path)

                    # Conditionally remediate based on mode
                    if remediation_mode:
                        sanitized_content = self._sanitize_ascii_content(content)
                        if sanitized_content != content:
                            # Create backup in temp directory
                            backup_dir = self.repo_root / config['backup_temp_dir']
                            backup_dir.mkdir(parents=True, exist_ok=True)
                            backup_filename = Path(file_path).name + '.backup'
                            backup_path = backup_dir / backup_filename

                            # Only backup if we haven't already
                            if not backup_path.exists():
                                with open(backup_path, 'w', encoding='utf-8') as f:
                                    f.write(content)

                            # Write sanitized version
                            with open(file_path, 'w', encoding='ascii', errors='replace') as f:
                                f.write(sanitized_content)

                            ascii_remediated.append(rel_path)
                            remediation_actions.append(f"Auto-sanitized ASCII violations in {rel_path}")
                            self.logger.info(f"[WSP-GUARDIAN] Auto-sanitized ASCII in {rel_path}")

            except Exception as e:
                self.logger.warning(f"[WSP-GUARDIAN] Error checking ASCII in {file_path}: {e}")
                continue

        # Report ASCII status (always show violations, only show fixes if in remediation mode)
        if ascii_violations:
            violation_count = len(ascii_violations)
            if remediation_mode:
                remediated_count = len(ascii_remediated)
                lines.append(f"[WSP-GUARDIAN][ASCII] {violation_count} files had violations, {remediated_count} auto-remediated")
            else:
                lines.append(f"[WSP-GUARDIAN][ASCII-WARNING] {violation_count} files have non-ASCII characters (use --fix-ascii to remediate)")
                lines.append(f"[WSP-GUARDIAN][ASCII-VIOLATION] Non-ASCII chars in: {', '.join(ascii_violations[:3])}")

        # Execute remediation pipeline only if we actually made changes
        if remediation_actions and remediation_mode:
            self._execute_wsp_remediation_pipeline(remediation_actions, config)

        # Log all WSP compliance checks for continuous learning
        self.logger.info(f"[WSP-GUARDIAN] Checked {len(wsp_related_files)} WSP files, {len(wsp_framework_docs)} framework docs")
        self.logger.info(f"[WSP-GUARDIAN] Compliance rate: {wsp_compliant_modules}/{total_modules}")
        if ascii_violations:
            self.logger.warning(f"[WSP-GUARDIAN] ASCII violations found: {len(ascii_violations)}, remediated: {len(ascii_remediated)}")

        return lines if lines else ["[WSP-GUARDIAN][OK] All WSP documentation compliant and up-to-date"]

    def _is_doc_only_path(self, rel_path: str, doc_only_modules: set) -> bool:
        """Check if path is in doc-only exemption map to prevent false stale alerts."""
        path_parts = Path(rel_path).parts

        # Check if any parent directory is doc-only
        for i in range(len(path_parts)):
            check_path = '/'.join(path_parts[:i+1])
            if check_path in doc_only_modules:
                return True

        return False

    def _sanitize_ascii_content(self, content: str) -> str:
        """
        Sanitize content to ASCII-only, replacing non-ASCII characters with safe alternatives.
        WSP 20 Compliance: Remove corruption while preserving readability.
        """
        sanitized = []
        for char in content:
            if ord(char) <= 127:
                sanitized.append(char)
            else:
                # Replace common Unicode chars with ASCII equivalents
                if char in ['—', '–', '―']:  # Various dashes
                    sanitized.append('-')
                elif char in ['"', '"', '"', '"']:  # Various quotes
                    sanitized.append('"')
                elif char in ["'", "'", '′', '″']:  # Various apostrophes
                    sanitized.append("'")
                elif char in ['…', '...']:  # Ellipsis
                    sanitized.append('...')
                elif char in ['•', '·', '[U+22C5]']:  # Various bullets
                    sanitized.append('*')
                elif char in ['->', '->', '[U+279C]']:  # Arrows
                    sanitized.append('->')
                elif char in ['[OK]', '[U+2714]', '[U+2611]']:  # Checkmarks
                    sanitized.append('[OK]')
                elif char in ['[FAIL]', '[U+2718]', '[CHECKED]']:  # X marks
                    sanitized.append('[X]')
                elif char in ['[U+26A0]', '[U+25B2]', '[U+26A0]️']:  # Warnings
                    sanitized.append('[WARNING]')
                elif char in ['[AI]', '[BOT]', '[IDEA]']:  # Brains/AI
                    sanitized.append('[AI]')
                elif char in ['[BOOKS]', '[U+1F4D6]', '[U+1F4C4]']:  # Books/docs
                    sanitized.append('[DOC]')
                elif char in ['[TOOL]', '[U+2699]', '[U+1F6E0]']:  # Tools
                    sanitized.append('[TOOL]')
                elif ord(char) > 127:
                    # Replace with [U+XXXX] notation for traceability
                    sanitized.append(f'[U+{ord(char):04X}]')
                else:
                    sanitized.append(char)  # Keep as-is if we can't map it

        return ''.join(sanitized)

    def _execute_wsp_remediation_pipeline(self, remediation_actions: List[str], config: Dict[str, Any]) -> None:
        """
        Execute WSP remediation pipeline with ModLog tracking.
        Creates remediation log and updates relevant ModLogs.
        """
        if not remediation_actions:
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        remediation_log_path = self.repo_root / config['remediation_log_path']

        # Ensure log directory exists
        remediation_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing log or create new one
        existing_content = ""
        if remediation_log_path.exists():
            try:
                with open(remediation_log_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            except Exception:
                existing_content = ""

        # Create remediation entry
        remediation_entry = f"""## ASCII Remediation Session - {timestamp}

**Session Summary:**
- Total remediation actions: {len(remediation_actions)}
- Auto-remediation enabled: {config['auto_remediate_ascii']}

**Actions Taken:**
""" + '\n'.join(f"- {action}" for action in remediation_actions) + "\n\n---\n"

        # Write updated log
        new_content = remediation_entry + existing_content
        with open(remediation_log_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # Update main ModLog if it exists (with deduplication)
        modlog_path = self.repo_root / "WSP_framework" / "ModLog.md"
        if modlog_path.exists():
            try:
                with open(modlog_path, 'r', encoding='utf-8') as f:
                    modlog_content = f.read()

                # Check for recent duplicate entries to prevent spam
                recent_entry_pattern = f"WSP Documentation Guardian performed ASCII remediation on \\d+ files"
                if re.search(recent_entry_pattern, modlog_content):
                    # Skip adding duplicate entry
                    self.logger.info(f"[WSP-GUARDIAN] Skipping duplicate ModLog entry (already logged recent remediation)")
                else:
                    # Add remediation entry to ModLog
                    remediation_note = f"""- **{timestamp}**: WSP Documentation Guardian performed ASCII remediation on {len(remediation_actions)} files
"""

                    # Insert after the most recent entry
                    if "## Recent Changes" in modlog_content:
                        modlog_content = modlog_content.replace("## Recent Changes", f"## Recent Changes\n{remediation_note}", 1)
                    else:
                        modlog_content = remediation_note + modlog_content

                    with open(modlog_path, 'w', encoding='utf-8') as f:
                        f.write(modlog_content)

            except Exception as e:
                self.logger.warning(f"[WSP-GUARDIAN] Failed to update ModLog: {e}")

        self.logger.info(f"[WSP-GUARDIAN] Remediation pipeline completed - {len(remediation_actions)} actions logged")

    def rollback_ascii_changes(self, filename: str) -> str:
        """
        Rollback ASCII changes for a specific file from backup.

        Returns status message.
        """
        config = WSP_DOC_CONFIG
        backup_dir = self.repo_root / config['backup_temp_dir']

        # Find backup file
        backup_filename = filename + '.backup'
        backup_path = backup_dir / backup_filename

        if not backup_path.exists():
            return f"[ERROR] No backup found for {filename} in {backup_dir}"

        # Find target file
        target_file = None
        for ext in ['.md', '.txt', '']:
            candidate = self.repo_root / filename
            if ext and not filename.endswith(ext):
                candidate = candidate.with_suffix(ext)
            if candidate.exists():
                target_file = candidate
                break

        if not target_file:
            return f"[ERROR] Target file {filename} not found"

        try:
            # Restore from backup
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()

            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(backup_content)

            # Log the rollback
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logger.info(f"[WSP-GUARDIAN] Rolled back ASCII changes for {filename}")

            # Update remediation log
            self._log_rollback_to_remediation_log(filename, timestamp)

            return f"[SUCCESS] Rolled back ASCII changes for {filename}"

        except Exception as e:
            return f"[ERROR] Failed to rollback {filename}: {e}"

    def _log_rollback_to_remediation_log(self, filename: str, timestamp: str) -> None:
        """Log rollback action to remediation log."""
        config = WSP_DOC_CONFIG
        remediation_log_path = self.repo_root / config['remediation_log_path']

        try:
            existing_content = ""
            if remediation_log_path.exists():
                with open(remediation_log_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()

            rollback_entry = f"""## ASCII Rollback Session - {timestamp}

**Rollback Action:**
- Rolled back ASCII changes for: {filename}

---\n"""

            new_content = rollback_entry + existing_content
            with open(remediation_log_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        except Exception as e:
            self.logger.warning(f"[WSP-GUARDIAN] Failed to log rollback: {e}")

    def _build_module_snapshot(self, module: str) -> Dict[str, Any]:
        path = self._resolve_module_path(module)
        snapshot: Dict[str, Any] = {
            'module': module,
            'path': path,
            'exists': bool(path and path.exists()),
            'missing_docs': [],
            'test_count': 0,
            'py_file_count': 0,
            'script_orphans': [],
            'large_python_files': [],
        }
        if not snapshot['exists']:
            return snapshot

        py_files = list(path.rglob('*.py'))
        snapshot['py_file_count'] = len(py_files)

        tests_dir = path / 'tests'
        test_files = list(tests_dir.rglob('test_*.py')) if tests_dir.exists() else []
        snapshot['test_count'] = len(test_files)

        docs = ('README.md', 'INTERFACE.md', 'ModLog.md', 'tests/TestModLog.md')
        snapshot['missing_docs'] = [doc for doc in docs if not (path / doc).exists()]

        large_files: List[tuple[Path, int, int]] = []
        for py_file in py_files:
            line_count = self._count_file_lines(py_file)
            size_kb = max(1, py_file.stat().st_size // 1024)
            if line_count > 400 or size_kb > 120:
                large_files.append((py_file, line_count, size_kb))
        snapshot['large_python_files'] = large_files

        scripts_dir = path / 'scripts'
        script_orphans: List[Path] = []
        if scripts_dir.exists():
            test_names = {test.name for test in test_files}
            for script in scripts_dir.glob('*.py'):
                if script.name.startswith('__init__'):
                    continue
                expected = f"test_{script.stem}.py"
                if expected not in test_names:
                    script_orphans.append(script)
        snapshot['script_orphans'] = script_orphans

        return snapshot

    def _resolve_module_path(self, module: str) -> Optional[Path]:
        if not module:
            return None
        candidate = (self.repo_root / module).resolve()
        if candidate.exists():
            return candidate
        return None

    def _resolve_file_path(self, file_path: str) -> Optional[Path]:
        if not file_path:
            return None
        candidate = Path(file_path)
        if candidate.is_absolute() and candidate.exists():
            return candidate
        candidate = (self.repo_root / file_path).resolve()
        return candidate if candidate.exists() else None

    def _relative_path(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self.repo_root))
        except Exception:
            return str(path)

    def _count_file_lines(self, path: Path) -> int:
        try:
            with path.open('r', encoding='utf-8', errors='ignore') as handle:
                return sum(1 for _ in handle)
        except OSError:
            return 0

    def _calculate_analysis_effectiveness(self, report: str) -> float:
        lines = report.split('\n')
        result_lines = [
            line
            for line in lines
            if any(keyword in line.upper() for keyword in ['FOUND', 'DETECTED', 'VIOLATION', 'PATTERN', 'OK', 'HEALTH'])
        ]
        return min(1.0, len(result_lines) / max(1, len(lines) * 0.3))

    def _log_chain_of_thought(self, step_type: str, message: str) -> None:
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [BOT][AI] [QWEN-{step_type}] {message}"
        self.chain_of_thought_log.append({
            'timestamp': datetime.now(),
            'type': step_type,
            'message': message,
        })
        self.logger.info(log_entry)
        try:
            print(log_entry)
        except UnicodeEncodeError:
            sys.stdout.buffer.write((log_entry + '\n').encode('utf-8', errors='replace'))

    def get_analysis_context(self) -> Dict[str, Any]:
        return {
            'files': self._last_files.copy(),
            'modules': self._last_modules.copy(),
            'executed_components': self._last_executed_components.copy(),
        }

    def get_chain_of_thought_summary(self) -> Dict[str, Any]:
        return {
            'total_steps': len(self.chain_of_thought_log),
            'step_types': list({entry['type'] for entry in self.chain_of_thought_log[-20:]}),
            'recent_activity': [entry['message'] for entry in self.chain_of_thought_log[-5:]],
            'avg_effectiveness': sum(self.performance_history[-10:]) / max(1, len(self.performance_history[-10:])),
        }
