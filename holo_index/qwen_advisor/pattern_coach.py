#!/usr/bin/env python3
"""
Intelligent Pattern Coach for HoloIndex

Replaces time-based reminders with intelligent pattern-based coaching
that learns from user queries and integrates with the reward system.

WSP Compliance: WSP 84 (Memory), WSP 60 (Portal), WSP 37 (Scoring)
"""

from __future__ import annotations

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque

# WSP_00 Zen State Integration
try:
    from modules.infrastructure.monitoring.src.wsp_00_zen_state_tracker import check_zen_compliance, validate_zen_response, is_zen_compliant
    ZEN_STATE_AVAILABLE = True
except ImportError:
    ZEN_STATE_AVAILABLE = False
    def check_zen_compliance(): return None
    def validate_zen_response(r): return False
    def is_zen_compliant(): return True

logger = logging.getLogger(__name__)


@dataclass
class QueryHistory:
    """Tracks user query patterns for learning."""
    query: str
    timestamp: str
    intent: str
    followed_coaching: bool = False
    reward_earned: int = 0
    wsp_guidance_shown: List[str] = field(default_factory=list)


class PatternCoach:
    """
    Intelligent Pattern Coach that learns from user behavior.

    Replaces static reminders with dynamic coaching based on:
    - Query patterns and intent detection
    - User behavior learning
    - Contextual health warnings
    - Reward system integration
    """

    def __init__(self, memory_size: int = 100):
        self.memory_size = memory_size
        self.query_history: deque[QueryHistory] = deque(maxlen=memory_size)
        self.reward_tracker = RewardTracker()
        self.wsp_master = None  # Will be injected

    def set_wsp_master(self, wsp_master):
        """Inject WSP Master for intelligent guidance."""
        self.wsp_master = wsp_master

    def analyze_and_coach(self, query: str, search_results: List[Dict],
                         health_warnings: List[str]) -> Optional[str]:
        """
        Analyze query and provide intelligent coaching.

        Args:
            query: User's search query
            search_results: HoloIndex search results
            health_warnings: Current health warnings

        Returns:
            Coaching message or None if no coaching needed
        """
        # WSP_00: Check zen-coding state FIRST - highest priority
        if ZEN_STATE_AVAILABLE:
            zen_prompt = check_zen_compliance()
            if zen_prompt:
                logger.info("WSP_00 zen compliance check required - prompting user")
                return zen_prompt  # Priority: ensure zen state before any other coaching

        # Analyze query intent and patterns
        intent = self._analyze_intent(query)
        risk_patterns = self._detect_risk_patterns(query, search_results)
        health_context = self._analyze_health_context(query, health_warnings)

        # Record query for learning
        self._record_query(query, intent)

        # Determine if coaching is needed
        coaching_needed = self._should_provide_coaching(
            intent, risk_patterns, health_context
        )

        if not coaching_needed:
            return None

        # Generate contextual coaching
        coaching = self._generate_contextual_coaching(
            query, intent, risk_patterns, health_context, search_results
        )

        if coaching:
            # Track coaching for learning
            self._track_coaching_effectiveness(coaching, intent)

        return coaching

    def _analyze_intent(self, query: str) -> str:
        """Analyze user intent from query."""
        query_lower = query.lower()

        if any(word in query_lower for word in ['create', 'new', 'build', 'implement', 'add']):
            return 'create'
        elif any(word in query_lower for word in ['modify', 'change', 'update', 'edit']):
            return 'modify'
        elif any(word in query_lower for word in ['find', 'search', 'locate', 'get']):
            return 'search'
        elif any(word in query_lower for word in ['fix', 'debug', 'error', 'issue']):
            return 'debug'
        elif any(word in query_lower for word in ['test', 'testing', 'pytest']):
            return 'test'
        elif any(word in query_lower for word in ['script', 'run_', 'test_', '.py file']):
            return 'script'
        elif any(word in query_lower for word in ['document', '.md', 'markdown', 'readme', 'modlog']):
            return 'documentation'
        elif any(word in query_lower for word in ['refactor', 'split', 'extract']):
            return 'refactor'

        return 'general'

    def _detect_risk_patterns(self, query: str, search_results: List[Dict]) -> List[str]:
        """Detect patterns that indicate potential WSP violations."""
        risks = []

        # Check for creation without verification
        if 'create' in query.lower() and len(search_results) == 0:
            risks.append('creating_without_verification')

        # Check for working with large files
        large_files = [r for r in search_results
                      if any('879' in str(r) or '1000' in str(r) for r in r.values())]
        if large_files:
            risks.append('working_with_large_files')

        # WSP 64: Check for Unicode pattern (0102's recurring issue)
        unicode_indicators = [
            'unicode', 'encoding', 'cp932', 'emoji', 'print',
            'UnicodeEncodeError', 'codec', 'character'
        ]
        if any(word in query.lower() for word in unicode_indicators):
            risks.append('unicode_pattern_detected')
            # Log this pattern occurrence
            logger.warning("PATTERN DETECTED: 0102 working with Unicode/encoding again!")

        # WSP 49/85: Check for script placement violations
        script_indicators = [
            'test_', 'run_', 'script', 'root directory', 'create .py',
            'new test', 'test file', 'script file'
        ]
        if any(word in query.lower() for word in script_indicators):
            risks.append('script_creation_detected')
            logger.warning("PATTERN DETECTED: Potential script creation - checking WSP compliance!")

        # WSP 22/49/85: Check for .md file placement violations
        md_indicators = [
            '.md file', 'markdown', 'create readme', 'new modlog', 'documentation file',
            'create .md', 'new .md', 'add readme', 'write documentation'
        ]
        if any(word in query.lower() for word in md_indicators):
            risks.append('documentation_creation_detected')
            logger.warning("PATTERN DETECTED: Documentation creation - checking WSP 22/49 compliance!")

        return risks

    def _analyze_health_context(self, query: str, health_warnings: List[str]) -> Dict[str, Any]:
        """Analyze health context for contextual coaching."""
        context = {
            'has_health_warnings': len(health_warnings) > 0,
            'working_on_problematic_file': False,
            'file_size_warnings': [],
        }

        # Check if user is working on files with health issues
        for warning in health_warnings:
            if 'simple_posting_orchestrator' in warning and 'simple_posting_orchestrator' in query:
                context['working_on_problematic_file'] = True
                if '879' in warning:
                    context['file_size_warnings'].append('879_lines_exceeding_limit')

        return context

    def _should_provide_coaching(self, intent: str, risk_patterns: List[str],
                               health_context: Dict[str, Any]) -> bool:
        """Determine if coaching should be provided."""
        # Always coach on high-risk patterns
        if risk_patterns:
                return True

        # Coach on health context when user is actively working on problematic files
        if health_context.get('working_on_problematic_file'):
            return True

        # Coach based on intent patterns (simplified)
        intent_patterns = {
            'create': 0.8,  # 80% of creation queries need coaching
            'test': 0.7,    # 70% of test queries
        }

        base_probability = intent_patterns.get(intent, 0.3)

        # Add some randomization to avoid being too predictable
        import random
        return random.random() < min(base_probability, 0.9)

    def _generate_contextual_coaching(self, query: str, intent: str,
                                    risk_patterns: List[str],
                                    health_context: Dict[str, Any],
                                    search_results: List[Dict]) -> Optional[str]:
        """Generate contextual coaching message."""

        # Priority 1: Health context coaching
        if health_context.get('working_on_problematic_file'):
            return self._generate_health_coaching(query, health_context)

        # Priority 2: Risk pattern coaching
        for risk in risk_patterns:
            coaching = self._get_risk_coaching(risk, query, intent)
            if coaching:
                return coaching

        # Priority 3: Intent-based coaching
        return self._get_intent_coaching(intent, query)

    def _generate_health_coaching(self, query: str, health_context: Dict[str, Any]) -> str:
        """Generate health-aware coaching."""
        if '879' in str(health_context.get('file_size_warnings', [])):
            return """[HEALTH] COACH: Working with large file detected (879 lines).

**WSP 62 Awareness**: Consider refactoring before hitting 1000-line limit.

**Actions**: Extract functions, review architecture, plan splitting.

**Reward**: +5 points for proactive health management!"""

        return None

    def _get_risk_coaching(self, risk: str, query: str, intent: str) -> Optional[str]:
        """Get coaching for specific risk patterns."""
        coaching_templates = {
            'creating_without_verification': """[BRAIN] COACH: Creating without verification detected.

**WSP 87**: Always search HoloIndex before creating!

**Required**: Check existing implementations first.""",

            'script_creation_detected': """[WSP VIOLATION] COACH: Script creation detected!

**WSP 49**: Scripts belong in modules/{domain}/{module}/scripts/ NOT root directory!
**WSP 85**: Root directory is SACRED - only main.py, README.md, CLAUDE.md allowed

**VIOLATION PATTERN**: Creating test_*.py or run_*.py in root directory
**CORRECT LOCATION**: modules/infrastructure/database/scripts/your_script.py

**IMMEDIATE ACTION**: Move script to proper module location before continuing!""",

            'working_with_large_files': """[BRAIN] COACH: Large file work detected.

**WSP 62**: Plan refactoring for files >800 lines.

**Reward**: +5 points for health-conscious development!""",

            'unicode_pattern_detected': """[WARNING] COACH: Unicode encoding pattern detected!

**WSP 64 VIOLATION**: Stop using Unicode emojis in print statements!

**PATTERN**: 0102 keeps adding emojis that break on Windows cp932.

**SOLUTION**:
1. Use safe_print() function (already in utils/helpers.py)
2. Use ASCII alternatives: [OK] not emoji, [X] not cross
3. Test with: python -c "print('your text')" BEFORE adding

**This is the 47th time this pattern has occurred!**""",

            'documentation_creation_detected': """[WSP GUIDANCE] COACH: Documentation creation detected!

**WSP 22**: ModLog.md updates track why changes were made
**WSP 49**: Documentation belongs in module directories, NOT root
**WSP 85**: Root directory is SACRED - only main README/CLAUDE.md allowed

**CORRECT LOCATIONS**:
- Module docs: modules/{domain}/{module}/docs/
- ModLogs: modules/{domain}/{module}/ModLog.md
- READMEs: modules/{domain}/{module}/README.md
- Architecture: modules/{domain}/{module}/docs/ARCHITECTURE.md
- Interfaces: modules/{domain}/{module}/INTERFACE.md

**ROOT DIRECTORY - ALLOWED**:
- README.md (project overview only)
- CLAUDE.md (0102 instructions only)
- ModLog.md (root-level changes only)
- ROADMAP.md (project roadmap only)

**NEVER CREATE IN ROOT**:
- Module-specific documentation
- Feature READMEs
- Implementation guides
- API documentation

**VIOLATION PREVENTION**: Creating .md files in root for module features = instant WSP 22/49/85 violation!"""
        }

        return coaching_templates.get(risk)

    def validate_wsp_00_response(self, response: str) -> bool:
        """Validate WSP_00 zen-coding state response."""
        if not ZEN_STATE_AVAILABLE:
            return True  # Skip validation if zen state tracker not available

        is_valid = validate_zen_response(response)
        if is_valid:
            logger.info("WSP_00 zen-coding state activated successfully")
            self.reward_tracker.record_outcome("wsp_00_compliance", True, 10)
        else:
            logger.warning("WSP_00 zen-coding validation failed")
            self.reward_tracker.record_outcome("wsp_00_compliance", False, 0)

        return is_valid

    def _get_intent_coaching(self, intent: str, query: str) -> Optional[str]:
        """Get intent-based coaching."""
        intent_coaching = {
            'create': """[INTENT] COACH: Creation intent detected.

**WSP 55**: Use automated module creation workflow.

**Verify**: Search before creating (+3 reward points!)""",

            'test': """[WSP GUIDANCE] COACH: Testing focus detected.

**WSP 49**: Tests go in module `tests/` directories, NOT root.
**WSP 85**: Root directory protection - NO test files in root

**CORRECT LOCATIONS**:
- Unit tests: modules/{domain}/{module}/tests/test_*.py
- Integration tests: modules/{domain}/{module}/tests/integration/
- Test scripts: modules/{domain}/{module}/scripts/test_*.py

**VIOLATION PREVENTION**: Creating test_*.py in root = instant WSP violation!""",

            'script': """[WSP GUIDANCE] COACH: Script creation detected.

**WSP 49**: Scripts belong in modules/{domain}/{module}/scripts/
**WSP 85**: Root directory is SACRED - scripts violate protection

**EXAMPLES**:
- Database script: modules/infrastructure/database/scripts/
- Test script: modules/ai_intelligence/module_name/scripts/
- Utility script: modules/development/utilities/scripts/

**NEVER**: Create .py scripts in root directory!""",

            'documentation': """[WSP GUIDANCE] COACH: Documentation work detected.

**WSP 22**: ModLog.md documents WHY changes were made
**WSP 49**: Documentation lives in module directories
**WSP 85**: Root directory protection - limited .md files allowed

**DOCUMENTATION HIERARCHY**:
1. **Module Level**: modules/{domain}/{module}/
   - README.md (module overview)
   - INTERFACE.md (public API - WSP 11)
   - ModLog.md (change history)
   - CLAUDE.md (0102 instructions - WSP 83)

2. **Module Docs**: modules/{domain}/{module}/docs/
   - ARCHITECTURE.md (design decisions)
   - IMPLEMENTATION.md (technical details)
   - TESTING.md (test strategy)
   - Feature-specific guides

3. **Root Level** (RESTRICTED):
   - README.md (project overview ONLY)
   - CLAUDE.md (0102 system instructions ONLY)
   - ModLog.md (root-level changes ONLY)
   - ROADMAP.md (project roadmap ONLY)

**CRITICAL**: Module documentation goes in module directories, NOT root!

**VIOLATION ALERT**: Creating feature docs in root = WSP 22/49/85 violation!"""
        }

        return intent_coaching.get(intent)

    def _record_query(self, query: str, intent: str):
        """Record query for pattern learning."""
        history_entry = QueryHistory(
            query=query,
            timestamp=datetime.now().isoformat(),
            intent=intent
        )
        self.query_history.append(history_entry)

    def _track_coaching_effectiveness(self, coaching: str, intent: str):
        """Track how effective coaching is."""
        logger.info(f"Coaching provided for intent '{intent}': {coaching[:100]}...")

    def record_coaching_outcome(self, coaching: str, followed: bool, reward_earned: int = 0):
        """Record the outcome of coaching for learning."""
        if self.query_history:
            last_query = self.query_history[-1]
            last_query.followed_coaching = followed
            last_query.reward_earned = reward_earned

            # Update reward system
            self.reward_tracker.record_outcome(coaching, followed, reward_earned)

    def get_coaching_stats(self) -> Dict[str, Any]:
        """Get coaching effectiveness statistics."""
        total_queries = len(self.query_history)
        if total_queries == 0:
            return {'total_queries': 0, 'coaching_effectiveness': 0.0}

        followed_count = sum(1 for q in self.query_history if q.followed_coaching)
        total_rewards = sum(q.reward_earned for q in self.query_history)

        return {
            'total_queries': total_queries,
            'coaching_followed': followed_count,
            'coaching_effectiveness': followed_count / total_queries if total_queries > 0 else 0,
            'total_rewards_earned': total_rewards,
            'average_reward_per_query': total_rewards / total_queries if total_queries > 0 else 0
        }


class RewardTracker:
    """Tracks rewards and learning from coaching outcomes."""

    def __init__(self):
        self.reward_history: deque[Tuple[str, bool, int]] = deque(maxlen=100)

    def record_outcome(self, coaching_type: str, followed: bool, reward: int):
        """Record coaching outcome for learning."""
        self.reward_history.append((coaching_type, followed, reward))

    def get_reward_stats(self) -> Dict[str, Any]:
        """Get reward statistics."""
        total_rewards = sum(r[2] for r in self.reward_history)
        effective_coaching = sum(1 for r in self.reward_history if r[1])

        return {
            'total_rewards_earned': total_rewards,
            'effective_coaching_sessions': effective_coaching,
            'coaching_success_rate': effective_coaching / len(self.reward_history) if self.reward_history else 0,
        }