from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .cache import AdvisorCache
from .config import QwenAdvisorConfig
from .llm_engine import QwenInferenceEngine
from .pattern_coach import PatternCoach
from .wsp_master import WSPMaster
from .prompts import build_compliance_prompt
from .telemetry import record_advisor_event
from .rules_engine import ComplianceRulesEngine

logger = logging.getLogger(__name__)


@dataclass
class AdvisorContext:
    """Inputs collected from HoloIndex search results."""

    query: str
    code_hits: List[Dict[str, Any]]
    wsp_hits: List[Dict[str, Any]]


@dataclass
class AdvisorResult:
    """Structured advisor response consumed by the CLI."""

    guidance: str
    reminders: List[str]
    todos: List[str]
    metadata: Dict[str, Any]


class QwenAdvisor:
    """Qwen-backed advisor with LLM intelligence.

    Uses local Qwen 1.5B coder model for intelligent code analysis and guidance,
    with rules engine fallback for compliance checking.
    """

    def __init__(
        self,
        config: Optional[QwenAdvisorConfig] = None,
        cache: Optional[AdvisorCache] = None,
    ) -> None:
        self.config = config or QwenAdvisorConfig.from_env()
        self.cache = cache or AdvisorCache(enabled=self.config.cache_enabled)
        self.rules_engine = ComplianceRulesEngine()  # Initialize rules engine

        # Initialize LLM engine for intelligent analysis
        self.llm_engine = QwenInferenceEngine(
            model_path=self.config.model_path,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )

        # Initialize WSP Master for comprehensive protocol guidance
        self.wsp_master = WSPMaster()

        # Initialize Pattern Coach for intelligent behavioral coaching
        self.pattern_coach = PatternCoach()
        self.pattern_coach.set_wsp_master(self.wsp_master)

        # Troubleshooting pattern database
        self.troubleshooting_db = self._build_troubleshooting_db()

    def detect_file_movements_and_compliance(self, context: AdvisorContext) -> Dict[str, Any]:
        """
        NEW: Detect file movements and provide WSP compliance guidance.

        Analyzes context for signs of file movements and ensures 0102 discoverability.
        Returns guidance for proper WSP compliance after file operations.
        """
        guidance = {
            'file_movements_detected': [],
            'wsp_violations': [],
            'documentation_updates_needed': [],
            'navigation_updates_needed': [],
            '0102_discoverability_score': 1.0
        }

        # Detect file movement patterns in query
        movement_indicators = ['move', 'moved', 'refactor', 'relocate', 'organize', 'wsp']
        if any(indicator in context.query.lower() for indicator in movement_indicators):
            guidance['file_movements_detected'].append('Query indicates file movement operation')

        # Check code hits for moved files
        for hit in context.code_hits:
            path = hit.get('path', hit.get('file_path', ''))
            if path and ('moved' in path.lower() or 'refactor' in path.lower()):
                guidance['file_movements_detected'].append(f"File movement detected: {path}")

        # WSP compliance analysis
        if guidance['file_movements_detected']:
            guidance['wsp_violations'].append('WSP VIOLATION: Files moved without 0102 indexing verification')
            guidance['documentation_updates_needed'].extend([
                'Update module README.md to document moved files',
                'Verify files are indexed in navigation system',
                'Check WSP knowledge base for proper documentation'
            ])
            guidance['navigation_updates_needed'].extend([
                'Add moved files to modules/infrastructure/navigation/src/navigation.py NEED_TO dictionary',
                'Ensure 0102 agents can discover moved files through navigation system'
            ])
            guidance['0102_discoverability_score'] = 0.3  # Low score indicates potential issues

        return guidance

    def detect_integration_gaps(self, context: AdvisorContext) -> Dict[str, Any]:
        """
        HOLOINDEX IMPROVEMENT OPPORTUNITY #1: Integration Gap Detection

        Detect when Module A monitors state but Module B could act on it,
        but NO CONNECTION exists between A->B.

        Example: QuotaAwarePoller monitors quota but TokenManager.rotate() exists
        but no integration between them.
        """
        gaps = {
            'detected_gaps': [],
            'missing_connections': [],
            'recommended_integrations': [],
            'confidence_score': 1.0
        }

        # Step 1: Extract modules and their capabilities from search results
        monitoring_modules = {}
        action_modules = {}

        for hit in context.code_hits:
            path = hit.get('path', hit.get('file_path', ''))
            content = hit.get('content', hit.get('preview', ''))

            # Detect monitoring patterns (Module A - monitors state)
            if any(keyword in content.lower() for keyword in [
                'monitor', 'check', 'quota', 'usage', 'status', 'health', 'alert'
            ]):
                module_name = self._extract_module_name(path)
                if module_name not in monitoring_modules:
                    monitoring_modules[module_name] = {'path': path, 'capabilities': []}
                monitoring_modules[module_name]['capabilities'].append('monitoring')

            # Detect action patterns (Module B - can act on state)
            if any(keyword in content.lower() for keyword in [
                'rotate', 'switch', 'change', 'update', 'reset', 'refresh', 'cleanup'
            ]):
                module_name = self._extract_module_name(path)
                if module_name not in action_modules:
                    action_modules[module_name] = {'path': path, 'capabilities': []}
                action_modules[module_name]['capabilities'].append('action')

        # Step 2: Analyze for integration gaps
        for monitor_name, monitor_info in monitoring_modules.items():
            monitor_path = monitor_info['path']

            # Look for potential action partners
            for action_name, action_info in action_modules.items():
                if monitor_name == action_name:
                    continue  # Same module, not a gap

                action_path = action_info['path']

                # Check if there's any connection between modules
                connection_exists = self._check_module_connection(monitor_path, action_path, context)

                if not connection_exists:
                    # Detect specific integration gap patterns
                    gap_type = self._classify_integration_gap(monitor_path, action_path)

                    if gap_type:
                        gap = {
                            'type': gap_type,
                            'monitoring_module': monitor_name,
                            'action_module': action_name,
                            'monitor_path': monitor_path,
                            'action_path': action_path,
                            'severity': 'HIGH' if 'quota' in monitor_path.lower() else 'MEDIUM'
                        }

                        gaps['detected_gaps'].append(gap)
                        gaps['missing_connections'].append(
                            f"{monitor_name} -> {action_name} (no integration detected)"
                        )

                        # Generate specific recommendations
                        recommendation = self._generate_integration_recommendation(gap)
                        if recommendation:
                            gaps['recommended_integrations'].append(recommendation)

        # Adjust confidence based on gap detection quality
        if gaps['detected_gaps']:
            gaps['confidence_score'] = 0.8  # High confidence when gaps found
        else:
            gaps['confidence_score'] = 0.9  # High confidence when no gaps (good integration)

        return gaps

    def _extract_module_name(self, path: str) -> str:
        """Extract module name from file path."""
        parts = path.split('/')
        # Look for modules/ pattern
        if 'modules' in parts:
            modules_idx = parts.index('modules')
            if modules_idx + 2 < len(parts):
                return f"{parts[modules_idx+1]}.{parts[modules_idx+2]}"
        return path.split('/')[-2] if '/' in path else 'unknown'

    def _check_module_connection(self, monitor_path: str, action_path: str, context: AdvisorContext) -> bool:
        """Check if there's any connection between two modules in the codebase."""
        # Look for imports, function calls, or references between modules
        monitor_module = self._extract_module_name(monitor_path)
        action_module = self._extract_module_name(action_path)

        for hit in context.code_hits:
            content = hit.get('content', hit.get('preview', ''))
            # Check for cross-module references
            if monitor_module in content and action_module in content:
                return True

        return False

    def _classify_integration_gap(self, monitor_path: str, action_path: str) -> Optional[str]:
        """Classify the type of integration gap detected."""
        monitor_lower = monitor_path.lower()
        action_lower = action_path.lower()

        # Quota monitoring -> Token rotation gap
        if ('quota' in monitor_lower or 'poller' in monitor_lower) and ('token' in action_lower or 'oauth' in action_lower):
            return 'QUOTA_TOKEN_ROTATION_GAP'

        # Health monitoring -> Cleanup action gap
        if 'health' in monitor_lower and ('cleanup' in action_lower or 'reset' in action_lower):
            return 'HEALTH_MAINTENANCE_GAP'

        # Generic monitoring -> action gap
        if ('monitor' in monitor_lower or 'check' in monitor_lower) and ('rotate' in action_lower or 'switch' in action_lower):
            return 'MONITORING_ACTION_GAP'

        return None

    def _generate_integration_recommendation(self, gap: Dict[str, Any]) -> Optional[str]:
        """Generate specific integration recommendations."""
        gap_type = gap['type']

        if gap_type == 'QUOTA_TOKEN_ROTATION_GAP':
            return f"INTEGRATION: Add token rotation to {gap['monitoring_module']} when quota >95%. Pass token_manager to __init__ and call rotate() in calculate_optimal_interval()"

        elif gap_type == 'HEALTH_MAINTENANCE_GAP':
            return f"INTEGRATION: Connect {gap['monitoring_module']} health checks to {gap['action_module']} cleanup actions"

        elif gap_type == 'MONITORING_ACTION_GAP':
            return f"INTEGRATION: Connect {gap['monitoring_module']} state monitoring to {gap['action_module']} corrective actions"

        return None

    def _generate_work_context_map(self, context: AdvisorContext) -> Optional[Dict[str, Any]]:
        """
        Generate a real-time work context map showing what 0102 is currently working on.

        This analyzes multiple signals:
        - Query content (what the agent is asking about)
        - Recent code changes (what files are being modified)
        - Module relationships (what's connected to current work)
        - Task patterns (what type of work is being done)
        """
        try:
            work_map = {
                'current_task': 'Unknown',
                'active_module': 'Unknown',
                'exact_location': 'Unknown',
                'related_modules': [],
                'task_type': 'unknown',
                'confidence': 0.0
            }

            # Signal 1: Analyze query content for current task
            query_lower = context.query.lower()
            if any(kw in query_lower for kw in ['quota', 'token', 'oauth', 'rotation']):
                work_map['current_task'] = 'OAuth Token Rotation Integration'
                work_map['task_type'] = 'integration'
                work_map['active_module'] = 'communication.livechat'
                work_map['related_modules'] = ['platform_integration.utilities.oauth_management']
                work_map['confidence'] = 0.9
            elif any(kw in query_lower for kw in ['greeting', 'spam', 'session']):
                work_map['current_task'] = 'Bot Greeting Optimization'
                work_map['task_type'] = 'optimization'
                work_map['active_module'] = 'communication.livechat'
                work_map['confidence'] = 0.8
            elif any(kw in query_lower for kw in ['holo', 'index', 'search']):
                work_map['current_task'] = 'HoloIndex Enhancement'
                work_map['task_type'] = 'enhancement'
                work_map['active_module'] = 'holo_index'
                work_map['confidence'] = 0.7

            # Signal 2: Analyze code hits for active modules
            if context.code_hits:
                # Find most recently modified files
                active_files = []
                for hit in context.code_hits:
                    path = hit.get('path', hit.get('file_path', ''))
                    if path:
                        active_files.append(path)

                if active_files:
                    # Extract module from most active file
                    primary_file = active_files[0]
                    work_map['active_module'] = self._extract_module_name(primary_file)

                    # Set exact location if we can determine it
                    if len(active_files) == 1:
                        work_map['exact_location'] = f"{primary_file}"

            # Signal 3: Check breadcrumb tracer for recent activity
            try:
                from ..adaptive_learning.breadcrumb_tracer import BreadcrumbTracer
                tracer = BreadcrumbTracer()
                recent_tasks = tracer.get_recent_tasks(limit=1)
                if recent_tasks:
                    recent_task = recent_tasks[0]
                    work_map['current_task'] = recent_task.get('description', work_map['current_task'])
                    work_map['confidence'] = min(1.0, work_map['confidence'] + 0.2)
            except Exception:
                pass  # Breadcrumb tracer not available

            # Only return if we have reasonable confidence
            if work_map['confidence'] >= 0.5:
                return work_map
            else:
                return None

        except Exception as e:
            logger.warning(f"Failed to generate work context map: {e}")
            return None

    def generate_guidance(self, context: AdvisorContext) -> AdvisorResult:
        """Generate intelligent guidance using WSP Master, LLM, and Pattern Coach."""

        cache_key = self.cache.make_key(context.query, {"code": len(context.code_hits), "wsp": len(context.wsp_hits)})
        cube_tags = sorted({hit.get('cube') for hit in context.code_hits + context.wsp_hits if hit and hit.get('cube')})
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug("Advisor cache hit for query: %s", context.query)
            return AdvisorResult(**cached)

        # NEW: Step 0.5 - File Movement Detection & WSP Compliance
        file_movement_analysis = self.detect_file_movements_and_compliance(context)
        if file_movement_analysis['file_movements_detected']:
            logger.info("[CYCLE] File movement detected - initiating WSP compliance verification")

        # Initialize guidance as dict to store analysis results
        guidance = {}

        # NEW: Step 0.6 - Integration Gap Detection
        logger.info("[INTEGRATION-GAP] Starting integration gap detection analysis")
        integration_gap_analysis = self.detect_integration_gaps(context)
        logger.info(f"[INTEGRATION-GAP] Analysis complete - Found {len(integration_gap_analysis.get('detected_gaps', []))} gaps")
        if integration_gap_analysis['detected_gaps']:
            logger.info("[LINK] Integration gaps detected - Module A monitors but Module B can't act")
            for gap in integration_gap_analysis['detected_gaps']:
                logger.info(f"[GAP] {gap['type']}: {gap['monitoring_module']} -> {gap['action_module']}")
            guidance['integration_gaps'] = integration_gap_analysis

        # Step 0: Troubleshooting Pattern Recognition
        troubleshooting_patterns = self._detect_troubleshooting_patterns(context.query)
        troubleshooting_guidance = ""
        if troubleshooting_patterns:
            logger.info("[TOOL] Troubleshooting patterns detected: %s", list(troubleshooting_patterns.keys()))
            troubleshooting_guidance = self._generate_troubleshooting_guidance(troubleshooting_patterns)

        # Step 1: WSP Master Analysis - Comprehensive protocol guidance
        wsp_analysis = self.wsp_master.analyze_query(context.query, context.code_hits)

        # Check for Unicode/emojis preventive warnings (WSP 20)
        unicode_check = None
        if "code" in context.query.lower() or "implement" in context.query.lower() or "python" in context.query.lower():
            unicode_check = self.wsp_master.check_unicode_violation(context.query, "query")
            if unicode_check["preventive_warning"]:
                # Add WSP 20 reference for Unicode guidance (not a violation, just prevention)
                if "WSP_20" not in wsp_analysis.suggested_wsps:
                    wsp_analysis.suggested_wsps.append("WSP_20")
                    wsp_analysis.wsp_relevance["WSP_20"] = 0.7  # Lower priority since it's preventive

        logger.debug("WSP Master analysis completed: intent=%s, risk=%s",
                    wsp_analysis.intent_category, wsp_analysis.risk_level)

        # Step 2: LLM Analysis - Intelligent code understanding
        prompt = build_compliance_prompt(context.query, context.code_hits, context.wsp_hits)
        llm_analysis = None
        try:
            llm_analysis = self.llm_engine.analyze_code_context(
                query=context.query,
                code_snippets=[hit.get('content', '')[:500] for hit in context.code_hits[:5]],
                wsp_guidance=[hit.get('content', '')[:300] for hit in context.wsp_hits[:3]]
            )
            logger.debug("LLM analysis completed successfully")
        except Exception as e:
            logger.warning(f"LLM analysis failed, falling back to rules engine: {e}")

        # Step 3: Rules Engine Fallback - Compliance checking
        rules_guidance = self.rules_engine.generate_contextual_guidance(
            context.query,
            context.code_hits,
            {"wsp_hits": context.wsp_hits}
        )

        # Step 4: Pattern Coach - Behavioral coaching
        # Note: Pattern coach is handled at CLI level for now, but could be integrated here


        # Combine all guidance sources
        integration_gaps = guidance.get('integration_gaps')
        guidance = self._synthesize_guidance(llm_analysis, wsp_analysis, rules_guidance, troubleshooting_guidance, integration_gaps, context)
        todos = self._synthesize_todos(llm_analysis, wsp_analysis, rules_guidance)
        # Add Unicode preventive warning if detected
        if unicode_check and unicode_check["preventive_warning"]:
            unicode_todo = ("WSP 20 PREVENTION: Avoid Unicode/emojis in future code - use ASCII alternatives like [OK], [ERROR], [TARGET]")
            if unicode_todo not in todos:
                todos.insert(0, unicode_todo)
        reminders = self._synthesize_reminders(wsp_analysis, rules_guidance)

        # Add Unicode preventive warning to guidance if detected
        if unicode_check and unicode_check["preventive_warning"]:
            preventive_warning = f"\\n\\n{unicode_check['recommendation']}"
            if guidance:
                guidance += preventive_warning
            else:
                guidance = unicode_check['recommendation']

        # Add test-specific guidance
        query_lower = context.query.lower()
        if ('test' in query_lower) and "Review FMAS plan: WSP_framework/docs/testing/HOLOINDEX_QWEN_ADVISOR_FMAS_PLAN.md" not in todos:
            todos.append("Review FMAS plan: WSP_framework/docs/testing/HOLOINDEX_QWEN_ADVISOR_FMAS_PLAN.md")

        # Calculate confidence based on guidance sources
        confidence = self._calculate_confidence(llm_analysis, wsp_analysis)

        # Include violation information
        violations = []
        for violation in rules_guidance.get("violations", []):
            violations.append(f"[{violation['wsp_reference']}] {violation['guidance']}")

        # NEW: Integrate file movement guidance into main guidance
        if file_movement_analysis['file_movements_detected']:
            guidance += f"\n\n[CYCLE] FILE MOVEMENT DETECTED - WSP COMPLIANCE REQUIRED:\n"
            guidance += f"0102 Discoverability Score: {file_movement_analysis['0102_discoverability_score']:.1f}/1.0\n\n"

            if file_movement_analysis['wsp_violations']:
                guidance += "[ERROR] WSP VIOLATIONS:\n"
                for violation in file_movement_analysis['wsp_violations']:
                    guidance += f"   - {violation}\n"

            if file_movement_analysis['documentation_updates_needed']:
                guidance += "\n[DOCS] REQUIRED DOCUMENTATION UPDATES:\n"
                for update in file_movement_analysis['documentation_updates_needed']:
                    guidance += f"   - {update}\n"
                    todos.append(update)

            if file_movement_analysis['navigation_updates_needed']:
                guidance += "\n[NAV] REQUIRED NAVIGATION UPDATES:\n"
                for update in file_movement_analysis['navigation_updates_needed']:
                    guidance += f"   - {update}\n"
                    todos.append(update)

        result = AdvisorResult(
            guidance=guidance,
            reminders=reminders,
            todos=todos,
            metadata={
                "prompt": prompt,
                "model_path": str(self.config.model_path),
                "cache_key": cache_key,
                "cubes": cube_tags,
                "risk_level": wsp_analysis.risk_level,
                "violations": violations,
                "intent": {"category": wsp_analysis.intent_category, "prevention_focus": wsp_analysis.prevention_focus},
                "llm_used": llm_analysis is not None,
                "llm_confidence": confidence,
                "llm_model": llm_analysis.get("model_used") if llm_analysis else None,
                "wsp_analysis": {
                    "suggested_wsps": wsp_analysis.suggested_wsps,
                    "relevance_scores": wsp_analysis.wsp_relevance
                },
                "file_movement_analysis": file_movement_analysis,  # NEW: File movement compliance data
            },
        )

        self.cache.set(cache_key, result.__dict__)
        record_advisor_event(self.config.telemetry_path, {
            "query": context.query,
            "reminder_count": len(reminders),
            "todo_count": len(todos),
            "cubes": cube_tags,
            "llm_used": llm_analysis is not None,
            "intent": wsp_analysis.intent_category,
            "risk_level": wsp_analysis.risk_level,
        })

        return result

    def _synthesize_guidance(self, llm_analysis, wsp_analysis, rules_guidance, troubleshooting_guidance="", integration_gaps=None, context=None) -> str:
        """Synthesize guidance from all sources."""
        guidance_parts = []

        # Priority: Troubleshooting guidance (if detected)
        if troubleshooting_guidance:
            guidance_parts.append(troubleshooting_guidance)
            guidance_parts.append("")  # Add spacing

        # NEW: HIGH PRIORITY - Integration Gap Detection
        if integration_gaps and integration_gaps.get('detected_gaps'):
            guidance_parts.append("[LINK] INTEGRATION GAPS DETECTED:")
            for gap in integration_gaps['detected_gaps']:
                guidance_parts.append(f"  - {gap['type']}: {gap['monitoring_module']} -> {gap['action_module']}")
            if integration_gaps.get('recommended_integrations'):
                guidance_parts.append("  [IDEA] RECOMMENDED INTEGRATIONS:")
                for rec in integration_gaps['recommended_integrations'][:2]:  # Limit to top 2
                    guidance_parts.append(f"     {rec}")
            guidance_parts.append("")  # Add spacing

        # NEW: REAL-TIME 0102 WORK CONTEXT MAP
        logger.info("[WORK-CONTEXT] Generating 0102 work context map")
        work_context_map = self._generate_work_context_map(context)
        logger.info(f"[WORK-CONTEXT] Map generated - Confidence: {work_context_map.get('confidence', 0.0) if work_context_map else 0.0:.2f}")
        if work_context_map:
            logger.info(f"[WORK-CONTEXT] Current task: {work_context_map.get('current_task', 'Unknown')}")
            logger.info(f"[WORK-CONTEXT] Active module: {work_context_map.get('active_module', 'Unknown')}")
            guidance_parts.append("[MAP] 0102 WORK CONTEXT MAP:")
            guidance_parts.append(f"  [TARGET] Current Focus: {work_context_map.get('current_task', 'Unknown')}")
            guidance_parts.append(f"  [FOLDER] Active Module: {work_context_map.get('active_module', 'Unknown')}")
            guidance_parts.append(f"  [LOCATION] Exact Location: {work_context_map.get('exact_location', 'Unknown')}")
            if work_context_map.get('related_modules'):
                guidance_parts.append("  [LINK] Related Modules:")
                for mod in work_context_map['related_modules'][:3]:
                    guidance_parts.append(f"     - {mod}")
            guidance_parts.append("")  # Add spacing

        # Primary: LLM analysis (if available)
        if llm_analysis and llm_analysis.get("guidance"):
            guidance_parts.append(llm_analysis["guidance"])
        else:
            # Secondary: WSP Master guidance
            wsp_guidance_items = self.wsp_master.generate_comprehensive_guidance(wsp_analysis)
            if wsp_guidance_items:
                top_guidance = wsp_guidance_items[0]
                guidance_parts.append(f"{top_guidance.wsp_reference}: {top_guidance.guidance}")

        # Tertiary: Rules engine fallback
        if not guidance_parts:
            guidance_parts.append(rules_guidance.get("primary_guidance", "Query processed. Follow WSP protocols."))

        return " ".join(guidance_parts)

    def _synthesize_todos(self, llm_analysis, wsp_analysis, rules_guidance) -> List[str]:
        """Synthesize TODOs from all sources."""
        todos = []

        # From rules engine
        todos.extend(rules_guidance.get("action_items", []))

        # From LLM recommendations
        if llm_analysis and llm_analysis.get("recommendations"):
            todos.extend(llm_analysis["recommendations"])

        # From WSP Master
        wsp_guidance_items = self.wsp_master.generate_comprehensive_guidance(wsp_analysis)
        for guidance in wsp_guidance_items[:2]:  # Top 2 WSP items
            todos.extend(guidance.action_items)

        return list(set(todos))  # Remove duplicates

    def _synthesize_reminders(self, wsp_analysis, rules_guidance) -> List[str]:
        """Synthesize reminders from WSP and rules sources."""
        reminders = []

        # From rules engine
        for reminder in rules_guidance.get("reminders", []):
            reminders.append(f"{reminder['wsp_reference']}: {reminder['guidance']}")

        # From WSP Master
        wsp_guidance_items = self.wsp_master.generate_comprehensive_guidance(wsp_analysis)
        for guidance in wsp_guidance_items[:3]:  # Top 3 WSP items
            if guidance.priority in ['CRITICAL', 'HIGH']:
                reminders.append(f"{guidance.wsp_reference}: {guidance.guidance}")

        return list(set(reminders))  # Remove duplicates

    def _calculate_confidence(self, llm_analysis, wsp_analysis) -> float:
        """Calculate overall confidence in the guidance."""
        confidence = 0.3  # Base confidence

        # LLM confidence
        if llm_analysis:
            confidence += llm_analysis.get("confidence", 0.5) * 0.4

        # WSP relevance confidence
        if wsp_analysis and wsp_analysis.wsp_relevance:
            max_relevance = max(wsp_analysis.wsp_relevance.values())
            confidence += max_relevance * 0.3

        # Risk level adjustment
        risk_multiplier = {'LOW': 1.0, 'MEDIUM': 0.9, 'HIGH': 0.8, 'CRITICAL': 0.7}
        confidence *= risk_multiplier.get(wsp_analysis.risk_level, 1.0)

        return min(confidence, 1.0)

    def _detect_troubleshooting_patterns(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Detect common troubleshooting patterns in queries."""
        patterns = {}
        query_lower = query.lower()

        for pattern_name, pattern_data in self.troubleshooting_db.items():
            if any(keyword in query_lower for keyword in pattern_data['keywords']):
                # Check if any of the code hits match the expected modules
                patterns[pattern_name] = pattern_data

        return patterns

    def _build_troubleshooting_db(self) -> Dict[str, Dict[str, Any]]:
        """Build database of common troubleshooting patterns and solutions."""
        return {
            'youtube_daemon_stuck': {
                'keywords': ['youtube', 'daemon', 'stuck', 'hung', 'not responding', 'circuit breaker'],
                'description': 'YouTube daemon is stuck, likely due to circuit breaker or authentication issues',
                'solutions': [
                    'Check circuit breaker status - may need manual reset',
                    'Verify YouTube API authentication tokens',
                    'Check for NO-QUOTA mode fallback capability',
                    'Review rate limiting and CAPTCHA detection'
                ],
                'modules': ['communication/livechat', 'platform_integration/youtube_auth', 'platform_integration/stream_resolver'],
                'priority': 'HIGH'
            },
            'rate_limiting_captcha': {
                'keywords': ['rate limit', '429', 'captcha', 'blocked', 'google.com/sorry'],
                'description': 'YouTube is rate limiting requests or showing CAPTCHA pages',
                'solutions': [
                    'Increase anti-detection delays (10-18s recommended)',
                    'Implement CAPTCHA detection and automatic cooldown',
                    'Reduce retry attempts from 5 to 2',
                    'Use NO-QUOTA web scraping mode as fallback'
                ],
                'modules': ['platform_integration/stream_resolver'],
                'priority': 'HIGH'
            },
            'authentication_failure': {
                'keywords': ['auth', 'token', 'oauth', 'api client is none', 'credential'],
                'description': 'YouTube API authentication is failing',
                'solutions': [
                    'Verify .env file has correct credential paths',
                    'Check OAuth token files exist and are valid',
                    'Ensure credential sets are properly configured (1, 10)',
                    'Test token refresh functionality'
                ],
                'modules': ['platform_integration/youtube_auth'],
                'priority': 'CRITICAL'
            },
            'stream_detection_failure': {
                'keywords': ['stream', 'detection', 'not finding', 'live video', 'video id'],
                'description': 'Daemon cannot detect live streams',
                'solutions': [
                    'Verify NO-QUOTA mode is properly initialized',
                    'Check channel IDs are correct in environment variables',
                    'Test individual video verification',
                    'Review anti-detection delays and patterns'
                ],
                'modules': ['platform_integration/stream_resolver', 'communication/livechat'],
                'priority': 'HIGH'
            },
            'circuit_breaker_open': {
                'keywords': ['circuit breaker', 'open', 'blocked', 'api calls blocked'],
                'description': 'Circuit breaker is stuck open, blocking all API calls',
                'solutions': [
                    'Implement manual circuit breaker reset',
                    'Reduce circuit breaker threshold from 10 to 5 failures',
                    'Add automatic recovery after timeout period',
                    'Improve fallback to NO-QUOTA mode'
                ],
                'modules': ['platform_integration/stream_resolver'],
                'priority': 'MEDIUM'
            }
        }

    def _generate_troubleshooting_guidance(self, patterns: Dict[str, Dict[str, Any]]) -> str:
        """Generate troubleshooting guidance for detected patterns."""
        guidance_parts = ["[TOOL] TROUBLESHOOTING DETECTED:"]

        for pattern_name, pattern_data in patterns.items():
            guidance_parts.append(f"\n[ERROR] Issue: {pattern_data['description']}")
            guidance_parts.append(f"[TARGET] Priority: {pattern_data['priority']}")
            guidance_parts.append("[IDEA] Solutions:")

            for solution in pattern_data['solutions']:
                guidance_parts.append(f"   - {solution}")

            if pattern_data['modules']:
                guidance_parts.append(f"[FOLDER] Focus modules: {', '.join(pattern_data['modules'])}")

        return "\n".join(guidance_parts)

