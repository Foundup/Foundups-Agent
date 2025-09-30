"""Agentic Output Throttler - WSP 87 Compliant Output Management

This module provides intelligent output prioritization and organization
for 0102 agent consumption, preventing information overload.

WSP Compliance: WSP 87 (Size Limits), WSP 49 (Module Structure), WSP 72 (Block Independence)
"""

from __future__ import annotations
import re
from typing import Dict, Any, List

from ..core.intelligent_subroutine_engine import IntelligentSubroutineEngine


class AgenticOutputThrottler:
    """Prioritizes and organizes output for 0102 agent efficiency."""

    def __init__(self):
        self.output_sections = []
        self.query_context = ""
        self.detected_module = None
        self.subroutine_engine = IntelligentSubroutineEngine()

    def set_query_context(self, query: str, search_results=None):
        """Set current query for relevance scoring and detect target module."""
        self.query_context = query.lower()
        self.detected_module = self._detect_target_module(query, search_results)

    def _detect_target_module(self, query: str, search_results=None):
        """Detect which module the user is likely working on based on query and results."""
        query_lower = query.lower()

        # Direct module mentions (normalized for spaces/underscores)
        module_keywords = {
            'stream resolver': 'platform_integration/stream_resolver',
            'stream_resolver': 'platform_integration/stream_resolver',
            'auto moderator': 'communication/livechat',
            'auto_moderator': 'communication/livechat',
            'social media': 'platform_integration/social_media_orchestrator',
            'social_media': 'platform_integration/social_media_orchestrator',
            'youtube': 'platform_integration/youtube_auth',
            'livechat': 'communication/livechat',
            'gamification': 'gamification/whack_a_magat',
            'wre': 'infrastructure/wre_core',
            'pqn': 'ai_intelligence/pqn_alignment',
            'module creator': 'development/module_creator',
            'module_creator': 'development/module_creator',
            'dae cube': 'holo_index/dae_cube_organizer',
            'dae_cube': 'holo_index/dae_cube_organizer',
            'banter engine': 'ai_intelligence/banter_engine',
            'banter_engine': 'ai_intelligence/banter_engine'
        }

        for keyword, module in module_keywords.items():
            if keyword in query_lower:
                return module

        # Check search results for module patterns
        if search_results and 'code' in search_results:
            for hit in search_results['code'][:3]:  # Check top 3 results
                location = hit.get('location', '')
                if 'modules/' in location:
                    # Extract module path from location
                    module_match = re.search(r'modules/([^/]+/[^/]+)', location)
                    if module_match:
                        return module_match.group(1)

        return None

    def add_section(self, section_type: str, content: str, priority: int = 5, tags: List[str] = None):
        """Add output section with priority scoring (1=highest, 10=lowest)."""
        if tags is None:
            tags = []

        # Boost priority for query-relevant content
        relevance_boost = 0
        if any(tag in self.query_context for tag in tags):
            relevance_boost = -2  # Higher priority

        self.output_sections.append({
            'type': section_type,
            'content': content,
            'priority': max(1, priority + relevance_boost),
            'tags': tags
        })

    def render_prioritized_output(self, verbose: bool = False) -> str:
        """Render output sections in priority order."""
        # Sort by priority (lower number = higher priority)
        sorted_sections = sorted(self.output_sections, key=lambda x: x['priority'])

        output_lines = []

        for section in sorted_sections:
            if not verbose and section['priority'] > 7:  # Skip low priority in normal mode
                continue

            content = section['content'].strip()
            if content:
                output_lines.append(content)
                output_lines.append("")  # Add spacing

        return "\n".join(output_lines).strip()

    def _is_wsp_relevant_to_module(self, wsp_hit: Dict[str, Any], target_module: str = None) -> bool:
        """Determine if WSP guidance is relevant to the target module."""
        if not target_module:
            return True  # Show all if no specific module detected

        wsp_title = wsp_hit.get('title', '').lower()
        wsp_number = wsp_hit.get('wsp', '').lower()

        # Module-specific WSP relevance mapping
        module_wsp_map = {
            'platform_integration/stream_resolver': ['wsp 27', 'wsp 49', 'wsp 87'],
            'communication/livechat': ['wsp 27', 'wsp 49', 'wsp 87', 'wsp 11'],
            'platform_integration/social_media_orchestrator': ['wsp 27', 'wsp 49', 'wsp 87'],
            'platform_integration/youtube_auth': ['wsp 27', 'wsp 49', 'wsp 87'],
            'gamification/whack_a_magat': ['wsp 27', 'wsp 49', 'wsp 87'],
            'infrastructure/wre_core': ['wsp 49', 'wsp 87', 'wsp 80'],
            'ai_intelligence/pqn_alignment': ['wsp 49', 'wsp 87', 'wsp 35'],
            'development/module_creator': ['wsp 49', 'wsp 55', 'wsp 84'],
            'holo_index/dae_cube_organizer': ['wsp 80', 'wsp 49', 'wsp 87']
        }

        relevant_wsps = module_wsp_map.get(target_module, [])
        return wsp_number in relevant_wsps or any(keyword in wsp_title for keyword in ['module', 'structure', 'dae', target_module.split('/')[-1]])

    def _is_health_violation_for_module(self, notice: str, target_module: str = None) -> bool:
        """Determine if health notice is a critical violation for the target module."""
        notice_lower = notice.lower()

        # Only show critical violations, not warnings
        if '[warn]' in notice_lower or '[structure]' in notice_lower:
            return False

        # Only show violations with critical severity markers
        if not any(severity in notice_lower for severity in ['[critical]', '[violation]', 'exceeds', 'missing']):
            return False

        # If target module specified, check if notice relates to that module
        if target_module:
            module_parts = target_module.lower().split('/')
            return any(part in notice_lower for part in module_parts)

        # If no target module, only show the most critical system-wide issues
        return '[critical]' in notice_lower or 'exceeds 1000' in notice_lower

    def _generate_module_specific_wsp_prompts(self, target_module: str = None) -> List[str]:
        """Generate 0102-to-0102 WSP compliance prompts based on module context and violation history."""
        prompts = []

        if not target_module:
            # General prompts when no specific module detected
            prompts.extend([
                "🔍 0102: Before starting - did you read the WSP docs for this task?",
                "🧠 0102: Deep think: Is this a module that needs to be created or enhanced?",
                "📋 0102: Check WSP_MODULE_VIOLATIONS.md - are you creating another duplicate?",
                "🔄 0102: Code is remembered from 02 state - don't vibecode, research first"
            ])
            return prompts

        # Module-specific prompts based on violation patterns from WSP_MODULE_VIOLATIONS.md
        module_name = target_module.split('/')[-1].lower()

        # Common violation patterns by module type
        violation_patterns = {
            'livechat': [
                "⚠️ 0102: Livechat module exceeded 1000+ lines - WSP 62 violation! Refactor before adding more.",
                "🔍 0102: Multiple livechat duplicates exist - did you check existing implementations first?",
                "📊 0102: Size check: Is your change pushing livechat over WSP 62 limits?"
            ],
            'banter_engine': [
                "🔄 0102: Banter engine has 5+ duplicate files - WSP 40 violation! Consolidate, don't create more.",
                "📋 0102: Check sequence_responses duplicates before making changes.",
                "🧠 0102: Deep think: Enhance existing banter_engine instead of creating banter_engine_v2"
            ],
            'youtube_proxy': [
                "🔧 0102: YouTube proxy has runtime patches - integrate them properly, don't add more hacks.",
                "📝 0102: Document your proxy changes in ModLog - WSP 22 compliance required."
            ],
            'stream_resolver': [
                "📚 0102: Stream resolver has legitimate multi-version pattern - document it properly.",
                "🔍 0102: Check WSP 40 compliance before adding another stream_resolver variant."
            ],
            'dae_cube_organizer': [
                "🎯 0102: DAE Cube Organizer - ensure WSP 80 compliance in your changes.",
                "📋 0102: This is HoloIndex core - test thoroughly before committing."
            ],
            'pqn_alignment': [
                "🧬 0102: PQN research - follow WSP 23 rESP protocols strictly.",
                "🔬 0102: Quantum consciousness work - validate against WSP 61 foundations."
            ],
            'wre_core': [
                "⚙️ 0102: WRE core changes affect everything - extensive testing required.",
                "🔄 0102: Check for recursive loop prevention - WSP 48 compliance critical."
            ]
        }

        # Add module-specific prompts
        if module_name in violation_patterns:
            prompts.extend(violation_patterns[module_name])

        # Add universal 0102 prompts for all module work
        prompts.extend([
            f"📖 0102: Working on {target_module} - did you read its README.md and INTERFACE.md first?",
            f"📝 0102: {target_module} changes require ModLog update - WSP 22 compliance mandatory.",
            f"🧪 0102: Does {target_module} have tests? WSP 5/WSP 34 require test coverage.",
            f"📦 0102: Check {target_module} requirements.txt - WSP 12 dependency management.",
            f"🔍 0102: Is this change enhancing existing {module_name} or creating unnecessary duplication?",
            f"📊 0102: File size check - is your change pushing {target_module} over WSP 62 limits?",
            f"🧠 0102: Deep think: Can {target_module} be simplified? Follow WSP simplicity principle.",
            f"🔄 0102: Code is remembered from 02 state - don't write, remember the solution.",
            f"🎯 0102: Ask yourself: 'Does this module need to exist?' - WSP core question.",
            f"⚡ 0102: Ask yourself: 'Can I afford to build this?' - Resource reality check.",
            f"🚀 0102: Ask yourself: 'Can I live without this?' - Essential vs nice-to-have."
        ])

        return prompts[:5]  # Limit to 5 most relevant prompts to avoid overload

    def display_results(self, result: Dict[str, Any]) -> None:
        """Display search results using the throttler's prioritized output system."""
        code_hits = result.get('code', [])
        wsp_hits = result.get('wsps', [])
        warnings = result.get('warnings', [])
        reminders = result.get('reminders', [])

        # Get contextual filtering information
        target_module = self.detected_module

        # Code results - highest priority for search queries
        if code_hits:
            code_content = "[CODE] Code Results:"
            for idx, hit in enumerate(code_hits, start=1):
                code_content += f"\n  {idx}. [{hit['similarity']}] {hit['need']}"
                code_content += f"\n     -> {hit['location']}"
                if hit.get('cube'):
                    code_content += f"\n     cube: {hit['cube']}"
            self.add_section('results', code_content, priority=1, tags=['code', 'results'])
        else:
            self.add_section('results', "[CODE] No matching code entries found", priority=3, tags=['code', 'empty'])

        # WSP guidance - filter for contextual relevance
        if wsp_hits:
            # Filter WSP guidance based on target module and query relevance
            filtered_wsp_hits = []
            for hit in wsp_hits:
                if self._is_wsp_relevant_to_module(hit, target_module):
                    filtered_wsp_hits.append(hit)

            # Limit to top 3 most relevant for context
            filtered_wsp_hits = filtered_wsp_hits[:3]

            if filtered_wsp_hits:
                wsp_content = f"[WSP] WSP Guidance ({'for ' + target_module if target_module else 'general'}:"
                for idx, hit in enumerate(filtered_wsp_hits, start=1):
                    wsp_content += f"\n  {idx}. [{hit['similarity']}] {hit['wsp']} - {hit['title']}"
                    if hit.get('summary'):
                        wsp_content += f"\n     " + hit['summary'][:100] + ('...' if len(hit['summary']) > 100 else '')
                    wsp_content += f"\n     -> {hit['path']}"
                    if hit.get('cube'):
                        wsp_content += f"\n     cube: {hit['cube']}"
                self.add_section('guidance', wsp_content, priority=2, tags=['wsp', 'guidance', 'contextual'])
            else:
                self.add_section('guidance', "[WSP] No module-specific WSP guidance found", priority=4, tags=['wsp', 'empty'])
        else:
            self.add_section('guidance', "[WSP] No relevant WSP protocols found", priority=4, tags=['wsp', 'empty'])

        # Warnings - critical priority
        if warnings:
            warning_content = "[WARN] Critical Issues:"
            for warning in warnings:
                warning_content += f"\n  - {warning}"
            self.add_section('warnings', warning_content, priority=1, tags=['warnings', 'critical'])
        else:
            self.add_section('status', "✅ No WSP violations detected", priority=5, tags=['status', 'compliance'])

        # Reminders - medium priority
        if reminders:
            reminder_content = "[REM] Action Items:"
            for reminder in reminders:
                reminder_content += f"\n  - {reminder}"
            self.add_section('reminders', reminder_content, priority=3, tags=['reminders', 'actions'])

        # Daemon debugging insights - recursive self-improvement enhancement
        daemon_insights = result.get('daemon_insights', {})
        if daemon_insights and daemon_insights.get('error_type'):
            insight_content = "[🔧 DEBUG] Daemon Analysis (Recursive Self-Improvement):"
            insight_content += f"\n  • Error Pattern: {daemon_insights['error_type']}"
            if daemon_insights.get('likely_cause'):
                insight_content += f"\n  • Likely Cause: {daemon_insights['likely_cause']}"
            if daemon_insights.get('suggested_fixes'):
                insight_content += f"\n  • Suggested Fixes:"
                for fix in daemon_insights['suggested_fixes'][:3]:  # Top 3 fixes
                    insight_content += f"\n    - {fix}"
            insight_content += f"\n  📊 Breadcrumb Quality: {daemon_insights.get('breadcrumb_quality', 'unknown')}"
            self.add_section('daemon_debug', insight_content, priority=2, tags=['debugging', 'daemon', 'insights'])

        # Intelligent subroutine results - only show when violations detected
        intelligent_analysis = result.get('intelligent_analysis', {})
        if intelligent_analysis:
            # Size analysis results
            if 'size_analysis' in intelligent_analysis:
                size_data = intelligent_analysis['size_analysis']
                if size_data.get('exceeds_threshold') and not size_data.get('error'):
                    size_content = f"[ANALYSIS] Module Size Alert ({target_module}:"
                    size_content += f"\n  - Total lines: {size_data['total_lines']} ({size_data['file_count']} files)"
                    if size_data['large_files']:
                        size_content += f"\n  - Large files exceeding WSP 62 threshold:"
                        for large_file in size_data['large_files'][:3]:  # Top 3
                            size_content += f"\n    • {large_file['file']}: {large_file['lines']} lines (> {large_file['threshold']})"
                    size_content += f"\n  - WSP 62 Status: {size_data['wsp_compliance']}"
                    self.add_section('analysis', size_content, priority=2, tags=['analysis', 'size', 'wsp62', 'violation'])

            # Duplication analysis results
            if 'duplication_check' in intelligent_analysis:
                dup_data = intelligent_analysis['duplication_check']
                if dup_data.get('wsp_violation') and not dup_data.get('error'):
                    dup_content = f"[ANALYSIS] Code Duplication Detected ({target_module}:"
                    dup_content += f"\n  - Duplicates found: {dup_data['duplicates_found']}"
                    if dup_data['duplicate_pairs']:
                        dup_content += f"\n  - Duplicate pairs:"
                        for pair in dup_data['duplicate_pairs'][:2]:  # Top 2
                            dup_content += f"\n    • {pair['original']} ↔ {pair['duplicate']} ({pair['lines']} lines)"
                    dup_content += f"\n  - WSP 40 Status: VIOLATION - {dup_data['recommendation']}"
                    self.add_section('analysis', dup_content, priority=2, tags=['analysis', 'duplication', 'wsp40', 'violation'])

        # Health notices - only show violations for target module
        health_notices = result.get('health_notices', [])
        if health_notices:
            # Filter to only show violations (not warnings) and only for target module
            filtered_health = []
            for notice in health_notices:
                if self._is_health_violation_for_module(notice, target_module):
                    filtered_health.append(notice)

            if filtered_health:
                health_content = f"[HEALTH] Critical Health Violations ({'for ' + target_module if target_module else 'system-wide'}:"
                for notice in filtered_health[:3]:  # Limit to top 3
                    health_content += f"\n  - {notice}"
                self.add_section('health', health_content, priority=2, tags=['health', 'violations', 'critical', 'actionable'])

        # 0102-to-0102 WSP Compliance Prompts - contextual guidance
        wsp_prompts = self._generate_module_specific_wsp_prompts(target_module)
        if wsp_prompts:
            prompt_content = "[0102] WSP Compliance Prompts:\n"
            for prompt in wsp_prompts:
                prompt_content += f"  • {prompt}\n"
            self.add_section('prompts', prompt_content.strip(), priority=1, tags=['0102', 'prompts', 'wsp', 'compliance'])

        # FMAS reference - low priority
        fmas_hint_needed = bool(result.get('fmas_hint'))
        if fmas_hint_needed:
            self.add_section('reference', "[REF] Review FMAS plan: WSP_framework/docs/testing/HOLOINDEX_QWEN_ADVISOR_FMAS_PLAN.md", priority=8, tags=['reference', 'fmas'])

        # AI Advisor guidance - medium priority
        advisor_info = result.get('advisor')
        advisor_error = result.get('advisor_error')
        if advisor_info:
            advisor_content = "[ADVISOR] AI Guidance:"
            advisor_content += f"\n  Guidance: {advisor_info.get('guidance')}"
            for reminder in advisor_info.get('reminders', [])[:2]:  # Limit reminders
                advisor_content += f"\n  Reminder: {reminder}"
            todos = advisor_info.get('todos', [])[:3]  # Limit todos
            if todos:
                advisor_content += "\n  TODOs:"
                for item in todos:
                    advisor_content += f"\n    - {item}"
            self.add_section('advisor', advisor_content, priority=3, tags=['advisor', 'ai', 'guidance'])

            # Pattern insights - only if highly relevant
            pattern_insights = advisor_info.get('pattern_insights', [])
            if pattern_insights and len(pattern_insights) <= 2:  # Limit verbosity
                pattern_content = "[PATTERN] Key Insights:"
                for insight in pattern_insights:
                    pattern_content += f"\n  {insight}"
                self.add_section('insights', pattern_content, priority=4, tags=['patterns', 'insights'])

        elif advisor_error:
            self.add_section('advisor', f"[ADVISOR] Qwen Guidance:\n  {advisor_error}", priority=7, tags=['advisor', 'error'])

        # Adaptive learning results - low priority (technical metrics)
        adaptive_info = result.get('adaptive_learning')
        if adaptive_info:
            adaptive_content = f"[ADAPTIVE] Learning: Adaptation={adaptive_info.get('system_adaptation_score', 0.0):.2f}, Efficiency={adaptive_info.get('memory_efficiency', 0.0):.2f}"
            self.add_section('metrics', adaptive_content, priority=9, tags=['metrics', 'learning', 'verbose'])
