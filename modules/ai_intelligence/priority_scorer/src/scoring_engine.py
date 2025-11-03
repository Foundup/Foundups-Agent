"""
Priority Scoring Engine - WSP Compliant Module

WSP Compliance: WSP 49 (Module Structure), WSP 54 (Agent Duties)
Contains the core scoring algorithms and business logic.
"""

import math
from typing import Dict, List, Any

from .data_structures import ScoringFactors, PriorityLevel
from .scoring_config import ScoringConfig


class ScoringEngine:
    """
    Core scoring engine for priority calculations.

    Separated from main class to maintain single responsibility principle
    and enable focused testing of scoring algorithms.
    """

    @staticmethod
    def calculate_factors(item_data: Dict[str, Any]) -> ScoringFactors:
        """
        Calculate scoring factors from raw item data.

        Applies normalization, validation, and intelligent defaults.
        """
        # Extract raw values with defaults
        raw_factors = {
            'complexity': float(item_data.get('complexity', 5.0)),
            'importance': float(item_data.get('importance', 5.0)),
            'impact': float(item_data.get('impact', 5.0)),
            'urgency': float(item_data.get('urgency', 5.0)),
            'dependencies': float(item_data.get('dependencies', 5.0)),
            'resources': float(item_data.get('resources', 5.0)),
            'risk': float(item_data.get('risk', 5.0)),
            'wsp_compliance': float(item_data.get('wsp_compliance', 5.0)),
            'business_value': float(item_data.get('business_value', 5.0)),
            'technical_debt': float(item_data.get('technical_debt', 5.0)),
        }

        # Apply intelligent adjustments based on context
        adjusted_factors = ScoringEngine._apply_contextual_adjustments(raw_factors, item_data)

        # Normalize to 0-10 scale
        normalized_factors = ScoringEngine._normalize_factors(adjusted_factors)

        return ScoringFactors(**normalized_factors)

    @staticmethod
    def _apply_contextual_adjustments(raw_factors: Dict[str, float],
                                    item_data: Dict[str, Any]) -> Dict[str, float]:
        """Apply intelligent adjustments based on item context."""
        adjusted = raw_factors.copy()

        # WSP compliance boost for framework-related items
        description = item_data.get('description', '').lower()
        name = item_data.get('name', '').lower()

        wsp_indicators = any(keyword in description or keyword in name
                           for keyword in ScoringConfig.WSP_KEYWORDS)

        if wsp_indicators:
            # Boost WSP compliance factor for WSP-related items
            adjusted['wsp_compliance'] = min(10.0, adjusted['wsp_compliance'] * 1.5)

        # Risk adjustment for high-complexity items
        if adjusted['complexity'] > 7:
            adjusted['risk'] = min(10.0, adjusted['risk'] * 1.2)

        # Business value boost for strategic items
        category = item_data.get('category', '').lower()
        if 'strategic' in category or 'business' in category:
            adjusted['business_value'] = min(10.0, adjusted['business_value'] * 1.3)

        return adjusted

    @staticmethod
    def _normalize_factors(factors: Dict[str, float]) -> Dict[str, float]:
        """Normalize factors to ensure they are within valid ranges."""
        normalized = {}

        for factor_name, value in factors.items():
            # Clamp to 0-10 range
            normalized[factor_name] = max(0.0, min(10.0, value))

        return normalized

    @staticmethod
    def calculate_overall_score(factors: ScoringFactors) -> float:
        """
        Calculate overall priority score using weighted algorithm.

        Formula: score = Σ(factor_value × factor_weight) × 10
        """
        score = 0.0

        # Apply weighted calculation
        score += factors.complexity * ScoringConfig.get_weight('complexity')
        score += factors.importance * ScoringConfig.get_weight('importance')
        score += factors.impact * ScoringConfig.get_weight('impact')
        score += factors.urgency * ScoringConfig.get_weight('urgency')
        score += factors.dependencies * ScoringConfig.get_weight('dependencies')
        score += factors.resources * ScoringConfig.get_weight('resources')
        score += factors.risk * ScoringConfig.get_weight('risk')
        score += factors.wsp_compliance * ScoringConfig.get_weight('wsp_compliance')
        score += factors.business_value * ScoringConfig.get_weight('business_value')
        score += factors.technical_debt * ScoringConfig.get_weight('technical_debt')

        # Convert to 0-100 scale
        return score * 10.0

    @staticmethod
    def determine_priority_level(score: float) -> PriorityLevel:
        """Determine priority level from numerical score."""
        priority_name = ScoringConfig.get_priority_level(score)
        return PriorityLevel[priority_name]

    @staticmethod
    def generate_recommendations(factors: ScoringFactors, score: float) -> List[str]:
        """Generate intelligent recommendations based on factors and score."""
        recommendations = []

        # Factor-based recommendations
        if factors.complexity > 7:
            recommendations.append("[TOOL] Break down into smaller, manageable tasks")

        if factors.risk > 7:
            recommendations.append("[U+1F6E1]️ Implement comprehensive testing and validation")

        if factors.wsp_compliance < 3:
            recommendations.append("[CLIPBOARD] PRIORITY: Address WSP compliance violations immediately")

        if factors.technical_debt > 7:
            recommendations.append("[REFRESH] Consider refactoring to reduce technical debt")

        if factors.dependencies > 7:
            recommendations.append("[HANDSHAKE] Coordinate with dependent modules and teams")

        if factors.resources > 7:
            recommendations.append("[U+1F4B0] Ensure adequate resources are allocated")

        # Score-based recommendations
        if score <= 20:
            recommendations.append("[ALERT] CRITICAL: Immediate attention required")
        elif score <= 40:
            recommendations.append("[U+1F525] HIGH: Schedule for next development cycle")
        elif score <= 60:
            recommendations.append("[U+1F4C5] MEDIUM: Include in regular development planning")
        else:
            recommendations.append("[NOTE] LOW: Consider for future development cycles")

        # Intelligent suggestions based on factor combinations
        if factors.complexity > 6 and factors.risk > 6:
            recommendations.append("[TARGET] Consider pair programming or expert consultation")

        if factors.importance > 7 and factors.urgency > 7:
            recommendations.append("[LIGHTNING] Fast-track implementation with dedicated resources")

        return recommendations

    @staticmethod
    def estimate_effort(factors: ScoringFactors) -> str:
        """Estimate effort based on complexity and other factors."""
        # Primary driver is complexity, adjusted by other factors
        base_complexity = factors.complexity

        # Adjust for dependencies (more dependencies = more coordination overhead)
        if factors.dependencies > 6:
            base_complexity *= 1.2

        # Adjust for resources (limited resources = longer timeline)
        if factors.resources > 6:
            base_complexity *= 1.1

        return ScoringConfig.get_effort_description(base_complexity)

    @staticmethod
    def extract_wsp_references(item_data: Dict[str, Any]) -> List[str]:
        """Extract WSP protocol references from item data."""
        references = []
        text_to_search = []

        # Collect all text fields to search
        for field in ['name', 'description', 'category', 'notes']:
            value = item_data.get(field, '')
            if isinstance(value, str):
                text_to_search.append(value.lower())

        combined_text = ' '.join(text_to_search)

        # Look for WSP patterns (WSP followed by number)
        import re
        wsp_pattern = r'wsp\s*(\d+)'
        matches = re.findall(wsp_pattern, combined_text, re.IGNORECASE)

        for match in matches:
            ref = f"WSP {match}"
            if ref not in references:
                references.append(ref)

        # Also look for direct protocol names
        protocol_keywords = ['protocol', 'framework', 'compliance', 'validation']
        for keyword in protocol_keywords:
            if keyword in combined_text:
                references.append(f"WSP-related ({keyword})")
                break

        return references
