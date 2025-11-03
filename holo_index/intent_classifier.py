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

Intent Classifier for HoloDAE Query Orchestration
WSP Compliance: WSP 3 (Module Organization), WSP 50 (Pre-Action Verification)

Classifies user queries into intent types to enable smart component routing.
Part of Intent-Driven Orchestration Enhancement (2025-10-07).

Design Doc: docs/agentic_journals/HOLODAE_INTENT_ORCHESTRATION_DESIGN.md
"""

import re
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Query intent classification for component routing"""
    DOC_LOOKUP = "doc_lookup"          # "what does WSP 64 say"
    CODE_LOCATION = "code_location"    # "where is AgenticChatEngine"
    MODULE_HEALTH = "module_health"    # "check holo_index health"
    RESEARCH = "research"              # "how does PQN emergence work"
    GENERAL = "general"                # "find youtube auth" (fallback)


@dataclass
class OutputFormattingRules:
    """Context-aware output formatting based on query intent"""
    priority_sections: List[str]  # Order of information sections
    verbosity_level: str  # 'minimal', 'balanced', 'detailed', 'comprehensive'
    focus_description: str  # What this intent prioritizes
    suppress_sections: List[str] = None  # Sections to minimize/hide

    def __post_init__(self):
        if self.suppress_sections is None:
            self.suppress_sections = []


@dataclass
class IntentClassification:
    """Classification result with confidence and metadata"""
    intent: IntentType
    confidence: float
    patterns_matched: List[str]
    raw_query: str
    output_rules: OutputFormattingRules = None

    def __post_init__(self):
        if self.output_rules is None:
            self.output_rules = self._get_default_output_rules()

    def _get_default_output_rules(self) -> OutputFormattingRules:
        """Get context-aware output formatting rules for this intent"""
        rules_map = {
            IntentType.DOC_LOOKUP: OutputFormattingRules(
                priority_sections=['results', 'guidance', 'compliance'],
                verbosity_level='minimal',
                focus_description='Direct answers to documentation questions',
                suppress_sections=['orchestrator', 'alerts']
            ),
            IntentType.CODE_LOCATION: OutputFormattingRules(
                priority_sections=['results', 'context', 'health'],
                verbosity_level='balanced',
                focus_description='Quick code discovery with implementation context',
                suppress_sections=['orchestrator']
            ),
            IntentType.MODULE_HEALTH: OutputFormattingRules(
                priority_sections=['alerts', 'health', 'results'],
                verbosity_level='detailed',
                focus_description='Comprehensive system health and compliance analysis',
                suppress_sections=[]
            ),
            IntentType.RESEARCH: OutputFormattingRules(
                priority_sections=['results', 'orchestrator', 'mcp'],
                verbosity_level='comprehensive',
                focus_description='Deep analysis with full tool orchestration',
                suppress_sections=[]
            ),
            IntentType.GENERAL: OutputFormattingRules(
                priority_sections=['results', 'orchestrator', 'alerts'],
                verbosity_level='standard',
                focus_description='Balanced information for exploratory searches',
                suppress_sections=[]
            )
        }
        return rules_map.get(self.intent, rules_map[IntentType.GENERAL])

    def __str__(self) -> str:
        return f"{self.intent.value} (confidence: {self.confidence:.2f})"


class IntentClassifier:
    """
    Classifies HoloDAE search queries into intent types.

    Uses regex pattern matching to determine user intent, enabling
    smart component routing that reduces noise and improves signal.

    Token Budget: ~100 tokens per classification
    """

    # Intent detection patterns (order matters - more specific first)
    INTENT_PATTERNS: Dict[IntentType, List[str]] = {
        IntentType.DOC_LOOKUP: [
            r'what (?:does|is|are) (?:wsp|WSP)\s*\d+',
            r'(?:read|show|explain|display) (?:wsp|WSP)\s*\d+',
            r'documentation for (?:wsp|WSP)',
            r'what (?:does|is) (?:the )?(?:readme|interface|modlog)',
            r'(?:show|read|explain) (?:the )?(?:readme|interface\.md|modlog)',
            r'wsp\s*\d+\s+(?:says?|documents?|describes?)',
            # Enhanced patterns for broader doc lookup
            r'(?:docs?|documentation) (?:for|about|on)',
            r'(?:protocol|spec|standard) \d+',
            r'(?:wsp|protocol) (?:definition|explanation)',
        ],
        IntentType.CODE_LOCATION: [
            r'where (?:is|does|can i find)',
            r'find (?:the )?(?:class|function|method|file)',
            r'locate (?:the )?(?:code|implementation|definition)',
            r'(?:which|what) file (?:contains|has|defines)',
            r'(?:which|what) module (?:contains|has|implements)',
            r'show me (?:the )?(?:code|implementation) (?:for|of)',
            # Enhanced patterns for code finding
            r'(?:search|look) (?:for|up) (?:the )?\w+',
            r'\w+\.(?:py|js|ts|java|cpp|c\+\+|rs|go)',
            r'(?:class|function|method) \w+',
        ],
        IntentType.MODULE_HEALTH: [
            r'check (?:\w+\s)?health',
            r'(?:analyze|review|audit) (?:\w+\s)?(?:module|system)',
            r'(?:is|are) (?:there )?(?:any )?(?:issues|problems|errors|violations)',
            r'(?:wsp|compliance) (?:violations|issues|problems)',
            r'(?:module|system|code) status',
            r'(?:show|list) (?:module |system )?(?:issues|problems|violations)',
            # Enhanced patterns for health checking
            r'(?:test|lint|coverage) (?:status|results?)',
            r'(?:dependencies|requirements) (?:check|status)',
            r'(?:module|system) (?:analysis|review|audit)',
        ],
        IntentType.RESEARCH: [
            r'how (?:does|do|can|to)',
            r'(?:explain|describe) (?:how|the|what)',
            r'(?:what|why) (?:is|are|does)',
            r'(?:understand|learn) (?:about )?',
            r'tell me about',
            r'(?:architecture|design|pattern) (?:of|for)',
            # Enhanced patterns for research queries
            r'(?:can|does|will) (?:\w+\s)*(?:improve|help|work|function)',
            r'(?:servers?|systems?|tools?) (?:improve|enhance|optimize)',
            r'(?:integrate|connect|combine) (?:\w+\s)*with',
            r'(?:better|faster|smarter|efficient) (?:\w+\s)*(?:way|method|approach)',
            r'(?:optimize|improve|enhance) (?:\w+\s)*(?:performance|efficiency|workflow)',
        ],
        # GENERAL has no patterns - it's the fallback, but we'll improve component selection
    }

    def __init__(self):
        """Initialize intent classifier with compiled regex patterns"""
        self.compiled_patterns: Dict[IntentType, List[re.Pattern]] = {}

        for intent, patterns in self.INTENT_PATTERNS.items():
            self.compiled_patterns[intent] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in patterns
            ]

        logger.info("[INTENT-CLASSIFIER] Initialized with %d intent types", len(self.INTENT_PATTERNS))

    def classify(self, query: str) -> IntentClassification:
        """
        Classify query into intent type.

        Args:
            query: User's search query

        Returns:
            IntentClassification with intent type, confidence, and matched patterns

        Token Budget: ~100 tokens per classification
        """
        if not query or not query.strip():
            logger.warning("[INTENT-CLASSIFIER] Empty query - returning GENERAL intent")
            return IntentClassification(
                intent=IntentType.GENERAL,
                confidence=1.0,
                patterns_matched=[],
                raw_query=query
            )

        # Try each intent type (except GENERAL which is fallback)
        best_match: Optional[Tuple[IntentType, float, List[str]]] = None

        for intent in [IntentType.DOC_LOOKUP, IntentType.CODE_LOCATION,
                       IntentType.MODULE_HEALTH, IntentType.RESEARCH]:
            matches = self._match_patterns(query, intent)

            if matches:
                confidence = self._calculate_confidence(matches, query)

                if best_match is None or confidence > best_match[1]:
                    best_match = (intent, confidence, matches)

        # If no patterns matched, default to GENERAL
        if best_match is None:
            logger.info("[INTENT-CLASSIFIER] No patterns matched - GENERAL intent")
            return IntentClassification(
                intent=IntentType.GENERAL,
                confidence=0.5,  # Low confidence for fallback
                patterns_matched=[],
                raw_query=query
            )

        intent, confidence, patterns = best_match

        logger.info(
            "[INTENT-CLASSIFIER] Query '%s' classified as %s (confidence: %.2f, patterns: %d)",
            query[:50], intent.value, confidence, len(patterns)
        )

        return IntentClassification(
            intent=intent,
            confidence=confidence,
            patterns_matched=patterns,
            raw_query=query
        )

    def _match_patterns(self, query: str, intent: IntentType) -> List[str]:
        """
        Match query against patterns for given intent.

        Args:
            query: User query
            intent: Intent type to test

        Returns:
            List of matched pattern strings
        """
        matched = []

        patterns = self.compiled_patterns.get(intent, [])

        for i, pattern in enumerate(patterns):
            if pattern.search(query):
                # Record which pattern matched (for debugging/learning)
                matched.append(self.INTENT_PATTERNS[intent][i])

        return matched

    def _calculate_confidence(self, matches: List[str], query: str) -> float:
        """
        Calculate confidence score based on pattern matches.

        Args:
            matches: List of matched patterns
            query: Original query

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not matches:
            return 0.0

        # Base confidence from number of matches
        # 1 match = 0.75, 2+ matches = 0.9+
        base_confidence = min(0.75 + (len(matches) - 1) * 0.15, 0.95)

        # Boost confidence if match is at start of query (stronger signal)
        if self._has_early_match(matches, query):
            base_confidence = min(base_confidence + 0.05, 0.99)

        return base_confidence

    def _has_early_match(self, matches: List[str], query: str) -> bool:
        """
        Check if any pattern matched near the start of query.

        Early matches (first 20 chars) indicate stronger intent signal.

        Args:
            matches: Matched pattern strings
            query: Original query

        Returns:
            True if match found in first 20 characters
        """
        query_lower = query.lower()

        for pattern_str in matches:
            # Reconstruct simple regex to find match position
            # (just for position check, not full matching)
            pattern = re.compile(pattern_str, re.IGNORECASE)
            match = pattern.search(query_lower)

            if match and match.start() < 20:
                return True

        return False

    def get_stats(self) -> Dict[str, int]:
        """
        Get classifier statistics.

        Returns:
            Dict with pattern counts per intent type
        """
        return {
            intent.value: len(patterns)
            for intent, patterns in self.INTENT_PATTERNS.items()
        }


# Singleton instance for import convenience
_classifier_instance: Optional[IntentClassifier] = None


def get_classifier() -> IntentClassifier:
    """
    Get singleton IntentClassifier instance.

    Returns:
        Global IntentClassifier instance
    """
    global _classifier_instance

    if _classifier_instance is None:
        _classifier_instance = IntentClassifier()

    return _classifier_instance
