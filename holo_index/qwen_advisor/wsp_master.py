#!/usr/bin/env python3
"""
WSP Master System for HoloIndex

Makes HoloIndex a comprehensive WSP protocol expert that provides
intelligent guidance based on the complete WSP framework.

WSP Compliance: WSP 64 (Violation Prevention), WSP 87 (Code Navigation)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WSPGuidance:
    """Structured WSP guidance with metadata."""
    wsp_reference: str
    title: str
    guidance: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    context: str
    related_wsps: List[str]
    action_items: List[str]


@dataclass
class QueryAnalysis:
    """Analysis of user query for WSP relevance."""
    intent_category: str  # create, modify, search, debug, refactor, etc.
    wsp_relevance: Dict[str, float]  # WSP -> relevance score
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    suggested_wsps: List[str]
    prevention_focus: str  # What WSP violation to prevent


class WSPMaster:
    """
    WSP Master System - Makes HoloIndex an expert in all WSP protocols.

    Provides intelligent, context-aware guidance based on complete WSP framework
    rather than isolated protocol references.
    """

    def __init__(self, wsp_directory: Path = None):
        self.wsp_directory = wsp_directory or Path("WSP_framework/src")
        self.wsp_cache: Dict[str, Dict[str, Any]] = {}
        self.protocol_relationships = self._build_protocol_relationships()
        self._load_wsp_knowledge()

    def _build_protocol_relationships(self) -> Dict[str, List[str]]:
        """Build relationships between WSP protocols for intelligent cross-referencing."""
        return {
            "WSP 3": ["WSP 49", "WSP 55", "WSP 33"],  # Enterprise domains -> module structure
            "WSP 49": ["WSP 55", "WSP 33", "WSP 62"],  # Module structure -> creation & size limits
            "WSP 55": ["WSP 49", "WSP 33"],  # Module creation -> structure compliance
            "WSP 62": ["WSP 49", "WSP 88"],  # Large files -> refactoring workflow
            "WSP 87": ["WSP 50", "WSP 64", "WSP 84"],  # Navigation -> verification & memory
            "WSP 50": ["WSP 64", "WSP 22"],  # Verification -> prevention & docs
            "WSP 64": ["WSP 47", "WSP 31"],  # Prevention -> tracking & protection
            "WSP 84": ["WSP 60", "WSP 78"],  # Memory -> portal & database
            "WSP 22": ["WSP 57", "WSP 1"],  # ModLogs -> naming & narrative
            "WSP 37": ["WSP 84", "WSP 48"],  # Scoring -> memory & improvement
            "WSP 35": ["WSP 33", "WSP 55"],  # Advisor -> execution & creation
        }

    def _load_wsp_knowledge(self):
        """Load WSP protocol knowledge for intelligent guidance."""
        wsp_files = list(self.wsp_directory.glob("WSP_*.md"))
        for wsp_file in wsp_files:
            try:
                # Try UTF-8 first, then fall back to other encodings
                try:
                    with open(wsp_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Try with BOM handling
                    try:
                        with open(wsp_file, 'r', encoding='utf-8-sig') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        # Fall back to latin-1 which can handle any byte sequence
                        with open(wsp_file, 'r', encoding='latin-1') as f:
                            content = f.read()
                        logger.warning(f"Loaded {wsp_file.name} with latin-1 encoding (may have encoding issues)")

                # Extract WSP number (e.g., "WSP_31" -> "WSP_31")
                stem_parts = wsp_file.stem.split('_')
                if len(stem_parts) >= 2 and stem_parts[0] == 'WSP':
                    wsp_num = f"{stem_parts[0]}_{stem_parts[1]}"
                else:
                    wsp_num = wsp_file.stem
                self.wsp_cache[wsp_num] = {
                    'content': content,
                    'path': wsp_file,
                    'title': self._extract_title(content),
                    'status': self._extract_status(content),
                    'purpose': self._extract_purpose(content),
                    'relationships': self.protocol_relationships.get(wsp_num, [])
                }
            except Exception as e:
                logger.warning(f"Failed to load WSP {wsp_file}: {e}")

    def _extract_title(self, content: str) -> str:
        """Extract WSP title from content."""
        lines = content.split('\n')
        for line in lines[:10]:
            if line.startswith('#') and 'WSP' in line:
                return line.strip('#').strip()
        return "Unknown WSP"

    def _extract_status(self, content: str) -> str:
        """Extract WSP status."""
        if 'Status:** Active' in content:
            return 'ACTIVE'
        elif 'Status:** Draft' in content:
            return 'DRAFT'
        elif 'Status:** Deprecated' in content:
            return 'DEPRECATED'
        return 'UNKNOWN'

    def _extract_purpose(self, content: str) -> str:
        """Extract WSP purpose."""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Purpose:' in line or '**Purpose:**' in line:
                # Get next non-empty line
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip():
                        return lines[j].strip('- *').strip()
        return "Purpose not found"

    def analyze_query(self, query: str, search_results: List[Dict]) -> QueryAnalysis:
        """
        Analyze user query for WSP relevance and provide comprehensive guidance.

        Args:
            query: User's search query
            search_results: HoloIndex search results

        Returns:
            QueryAnalysis with WSP guidance and risk assessment
        """
        query_lower = query.lower()

        # Determine intent category
        intent_category = self._classify_intent(query_lower)

        # Calculate WSP relevance scores
        wsp_relevance = self._calculate_wsp_relevance(query_lower, intent_category, search_results)

        # Assess risk level
        risk_level = self._assess_risk_level(intent_category, wsp_relevance)

        # Get suggested WSPs (top 5 by relevance)
        suggested_wsps = sorted(wsp_relevance.keys(), key=lambda x: wsp_relevance[x], reverse=True)[:5]

        # Determine prevention focus
        prevention_focus = self._determine_prevention_focus(intent_category, suggested_wsps)

        return QueryAnalysis(
            intent_category=intent_category,
            wsp_relevance=wsp_relevance,
            risk_level=risk_level,
            suggested_wsps=suggested_wsps,
            prevention_focus=prevention_focus
        )

    def _classify_intent(self, query: str) -> str:
        """Classify user intent from query."""
        # Creation intents
        if any(word in query for word in ['create', 'new', 'build', 'implement', 'add']):
            return 'create'

        # Modification intents
        elif any(word in query for word in ['modify', 'change', 'update', 'edit', 'refactor']):
            return 'modify'

        # Search/debug intents
        elif any(word in query for word in ['find', 'search', 'locate', 'debug', 'fix', 'error']):
            return 'debug'

        # Testing intents
        elif any(word in query for word in ['test', 'testing', 'pytest', 'unit test']):
            return 'test'

        # Documentation intents
        elif any(word in query for word in ['doc', 'readme', 'interface', 'modlog']):
            return 'document'

        # Architecture intents
        elif any(word in query for word in ['architecture', 'structure', 'design', 'pattern']):
            return 'architect'

        return 'general'

    def _calculate_wsp_relevance(self, query: str, intent: str, search_results: List[Dict]) -> Dict[str, float]:
        """Calculate relevance scores for each WSP protocol."""
        relevance_scores = {}

        # Intent-based relevance mapping
        intent_mapping = {
            'create': ['WSP 55', 'WSP 49', 'WSP 33', 'WSP 3'],
            'modify': ['WSP 50', 'WSP 64', 'WSP 87', 'WSP 22'],
            'debug': ['WSP 87', 'WSP 50', 'WSP 64', 'WSP 84'],
            'test': ['WSP 22', 'WSP 50', 'WSP 49'],
            'document': ['WSP 22', 'WSP 57', 'WSP 1'],
            'architect': ['WSP 3', 'WSP 49', 'WSP 62', 'WSP 84'],
        }

        # Base relevance from intent
        base_wsps = intent_mapping.get(intent, ['WSP 87', 'WSP 50'])
        for wsp in base_wsps:
            relevance_scores[wsp] = 0.8

        # Query-specific relevance
        if 'module' in query:
            relevance_scores['WSP 49'] = max(relevance_scores.get('WSP 49', 0), 0.9)
            relevance_scores['WSP 55'] = max(relevance_scores.get('WSP 55', 0), 0.9)
            relevance_scores['WSP 3'] = max(relevance_scores.get('WSP 3', 0), 0.7)

        if 'file' in query or 'size' in query:
            relevance_scores['WSP 62'] = max(relevance_scores.get('WSP 62', 0), 0.9)
            relevance_scores['WSP 49'] = max(relevance_scores.get('WSP 49', 0), 0.8)

        if 'violation' in query or 'error' in query:
            relevance_scores['WSP 64'] = max(relevance_scores.get('WSP 64', 0), 0.9)
            relevance_scores['WSP 47'] = max(relevance_scores.get('WSP 47', 0), 0.8)

        if 'search' in query or 'find' in query:
            relevance_scores['WSP 87'] = max(relevance_scores.get('WSP 87', 0), 0.9)
            relevance_scores['WSP 50'] = max(relevance_scores.get('WSP 50', 0), 0.8)

        return relevance_scores

    def _assess_risk_level(self, intent: str, wsp_relevance: Dict[str, float]) -> str:
        """Assess risk level based on intent and WSP relevance."""
        high_risk_wsps = ['WSP 64', 'WSP 62', 'WSP 49']  # Prevention, size, structure
        critical_wsps = ['WSP 31', 'WSP 47']  # Protection, violation tracking

        # High risk intents
        if intent in ['create', 'modify']:
            if any(wsp in wsp_relevance and wsp_relevance[wsp] > 0.8 for wsp in high_risk_wsps):
                return 'HIGH'
            return 'MEDIUM'

        # Critical operations
        if any(wsp in wsp_relevance and wsp_relevance[wsp] > 0.7 for wsp in critical_wsps):
            return 'CRITICAL'

        return 'LOW'

    def _determine_prevention_focus(self, intent: str, suggested_wsps: List[str]) -> str:
        """Determine what WSP violation to focus on preventing."""
        prevention_mapping = {
            'create': 'WSP 49 violation (incorrect module structure)',
            'modify': 'WSP 50 violation (insufficient verification)',
            'debug': 'WSP 64 violation (missing prevention steps)',
            'test': 'WSP 49 violation (incorrect test placement)',
            'document': 'WSP 22 violation (missing ModLog updates)',
            'architect': 'WSP 3 violation (incorrect domain placement)'
        }

        return prevention_mapping.get(intent, 'General WSP compliance')

    def generate_comprehensive_guidance(self, query_analysis: QueryAnalysis) -> List[WSPGuidance]:
        """
        Generate comprehensive WSP guidance based on query analysis.

        Args:
            query_analysis: Analysis of user query

        Returns:
            List of WSP guidance items prioritized by relevance
        """
        guidance_items = []

        for wsp_num in query_analysis.suggested_wsps:
            if wsp_num in self.wsp_cache:
                wsp_data = self.wsp_cache[wsp_num]
                relevance = query_analysis.wsp_relevance.get(wsp_num, 0)

                # Generate contextual guidance based on intent
                guidance = self._generate_contextual_guidance(
                    wsp_num, wsp_data, query_analysis.intent_category, relevance
                )

                if guidance:
                    guidance_items.append(guidance)

        # Sort by relevance and priority
        guidance_items.sort(key=lambda x: (
            1 if x.priority == 'CRITICAL' else
            2 if x.priority == 'HIGH' else
            3 if x.priority == 'MEDIUM' else 4,
            -query_analysis.wsp_relevance.get(x.wsp_reference, 0)
        ), reverse=False)

        return guidance_items

    def _generate_contextual_guidance(self, wsp_num: str, wsp_data: Dict,
                                    intent: str, relevance: float) -> Optional[WSPGuidance]:
        """Generate contextual guidance for a specific WSP."""
        title = wsp_data.get('title', f'WSP {wsp_num}')

        # Context-specific guidance based on WSP and intent
        guidance_map = {
            ('WSP 49', 'create'): {
                'guidance': 'Follow module scaffolding: src/, tests/, memory/, docs/ directories required',
                'priority': 'CRITICAL',
                'actions': ['Create proper directory structure', 'Add __init__.py files', 'Set up test directory']
            },
            ('WSP 49', 'modify'): {
                'guidance': 'Verify module structure compliance before modifications',
                'priority': 'HIGH',
                'actions': ['Check directory scaffolding', 'Validate imports', 'Review test coverage']
            },
            ('WSP 55', 'create'): {
                'guidance': 'Use WSP 55 automated module creation workflow',
                'priority': 'CRITICAL',
                'actions': ['Run module creation automation', 'Follow scaffolding templates', 'Initialize documentation']
            },
            ('WSP 62', 'modify'): {
                'guidance': 'Check file size limits (800-1000 lines) before adding code',
                'priority': 'HIGH',
                'actions': ['Review current file size', 'Plan refactoring if approaching limit', 'Consider function extraction']
            },
            ('WSP 87', 'general'): {
                'guidance': 'Always search HoloIndex before implementing new functionality',
                'priority': 'CRITICAL',
                'actions': ['Run semantic search first', 'Check NAVIGATION.py', 'Review existing implementations']
            }
        }

        context_key = (wsp_num, intent)
        if context_key in guidance_map:
            info = guidance_map[context_key]
            return WSPGuidance(
                wsp_reference=wsp_num,
                title=title,
                guidance=info['guidance'],
                priority=info['priority'],
                context=f"Intent: {intent}, Relevance: {relevance:.1f}",
                related_wsps=wsp_data.get('relationships', []),
                action_items=info['actions']
            )

        # Default guidance for high-relevance WSPs
        if relevance > 0.7:
            return WSPGuidance(
                wsp_reference=wsp_num,
                title=title,
                guidance=wsp_data.get('purpose', 'Follow WSP protocol guidelines'),
                priority='MEDIUM' if wsp_num in ['WSP 50', 'WSP 64'] else 'LOW',
                context=f"Intent: {intent}, Relevance: {relevance:.1f}",
                related_wsps=wsp_data.get('relationships', []),
                action_items=['Review full WSP protocol', 'Apply relevant guidelines']
            )

        return None

    def get_wsp_summary(self, wsp_num: str) -> Optional[Dict[str, Any]]:
        """Get summary information for a specific WSP."""
        return self.wsp_cache.get(wsp_num)

    def get_related_wsps(self, wsp_num: str) -> List[str]:
        """Get WSPs related to the given WSP."""
        return self.protocol_relationships.get(wsp_num, [])
