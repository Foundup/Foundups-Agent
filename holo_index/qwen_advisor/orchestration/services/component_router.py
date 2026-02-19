from typing import Dict, List, Any
from enum import Enum

# Define IntentType locally to avoid circular imports if possible, 
# or import from where it's defined if it's in a shared module.
# Assuming it's available in the broader scope, but for safety defining strings here.

COMPONENT_META = {
    'health_analysis': ('[PILL][OK]', 'Health & WSP Compliance'),
    'vibecoding_analysis': ('[AI]', 'Vibecoding Analysis'),
    'file_size_monitor': ('[RULER]', 'File Size Monitor'),
    'pattern_coach': ('[IDEA]', 'Pattern Coach'),
    'orphan_analysis': ('[GHOST]', 'Orphan Analysis'),
    'wsp_documentation_guardian': ('[BOOKS]', 'WSP Documentation Guardian'),
    'module_analysis': ('[LINK]', 'Module Analysis'),
}

class ComponentRouter:
    """
    Selects relevant HoloDAE components based on user intent and query context.
    """

    def __init__(self):
        # Intent-to-Component Routing Map (ENHANCEMENT 2025-10-07)
        self.INTENT_COMPONENT_MAP = {
            'doc_lookup': [
                'wsp_documentation_guardian',  # Primary - WSP/README/INTERFACE docs
                'module_analysis'              # Secondary - module context
            ],
            'code_location': [
                'module_analysis',             # Primary - Verify module + location context
                'file_size_monitor'            # Secondary - Surface large-file hotspots
            ],
            'fix_error': [
                'health_analysis',             # Primary - Check for errors
                'module_analysis'              # Secondary - Find local module context
            ],
            'research': [
                'pattern_coach',               # Primary - Explain architecture/patterns
                'wsp_documentation_guardian'   # Secondary - Internal docs
            ],
            'general': [
                # Dynamic selection handled by _select_general_components
            ]
        }

    def select_components(self, intent: str, query: str, files: List[str], modules: List[str]) -> List[str]:
        """
        Select components based on intent.
        """
        if intent == 'general':
            return self._select_general_components(query, files, modules)
        
        # Check for orphan archaeology specific routing
        if 'orphan' in query.lower():
            return self._select_orphan_archaeology_components(query)

        return self.INTENT_COMPONENT_MAP.get(intent, self._select_general_components(query, files, modules))

    def _select_general_components(self, query: str, files: List[str], modules: List[str]) -> List[str]:
        """
        FIRST PRINCIPLES: Intelligently select 2-3 most relevant components for GENERAL queries
        """
        selected = []
        query_lower = query.lower()

        # 1. Health Analysis - Always relevant if "error", "fix", "broken"
        if any(w in query_lower for w in ['error', 'fix', 'broken', 'issue', 'bug']):
            selected.append('health_analysis')

        # 2. WSP Documentation - Relevant if "wsp", "doc", "how to", "guide"
        if any(w in query_lower for w in ['wsp', 'doc', 'how', 'guide', 'rule']):
            selected.append('wsp_documentation_guardian')

        # 3. Module Analysis - Relevant if specific modules mentioned or files found
        if modules or any(w in query_lower for w in ['module', 'structure', 'dependency']):
            selected.append('module_analysis')

        # 4. Vibecoding - Relevant if "vibe", "style", "pattern"
        if any(w in query_lower for w in ['vibe', 'style', 'pattern']):
            selected.append('vibecoding_analysis')

        # Default fallback if nothing specific selected
        if not selected:
            selected = ['health_analysis', 'wsp_documentation_guardian']

        # Limit to top 3 to respect token budget
        return selected[:3]

    def _select_orphan_archaeology_components(self, query: str) -> List[str]:
        """
        FIRST PRINCIPLES: Specialized component selection for orphan archaeology queries
        """
        return ['orphan_analysis', 'module_analysis']
