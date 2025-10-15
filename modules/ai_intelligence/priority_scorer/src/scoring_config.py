"""
Priority Scorer Configuration - WSP Compliant Module

WSP Compliance: WSP 70 (Configuration Standards), WSP 49 (Module Structure)
Contains all configuration constants and scoring parameters.
"""

from typing import Dict, List


class ScoringConfig:
    """Configuration constants for priority scoring."""

    # Factor weights for scoring algorithm (must sum to 1.0)
    FACTOR_WEIGHTS: Dict[str, float] = {
        'complexity': 0.15,      # Technical complexity
        'importance': 0.20,      # Strategic importance
        'impact': 0.18,          # System impact
        'urgency': 0.12,         # Time sensitivity
        'dependencies': 0.10,    # Dependency complexity
        'resources': 0.08,       # Resource requirements
        'risk': 0.07,           # Risk level
        'wsp_compliance': 0.05,  # WSP compliance status
        'business_value': 0.03,  # Business value delivered
        'technical_debt': 0.02   # Technical debt impact
    }

    # WSP-related keywords for compliance detection
    WSP_KEYWORDS: List[str] = [
        'wsp', 'protocol', 'compliance', '0102', 'partifact', 'quantum',
        'autonomous', 'agent', 'modular', 'testing', 'documentation',
        'framework', 'recursive', 'intelligence', 'validation'
    ]

    # Score thresholds for priority levels
    PRIORITY_THRESHOLDS = {
        'critical': 80,    # CRITICAL: Score >= 80
        'high': 60,        # HIGH: Score >= 60
        'medium': 40,      # MEDIUM: Score >= 40
        'low': 20,         # LOW: Score >= 20
        'minimal': 0       # MINIMAL: Score < 20
    }

    # Effort estimation thresholds
    EFFORT_THRESHOLDS = {
        'trivial': 2.0,    # Complexity <= 2.0
        'small': 4.0,      # Complexity <= 4.0
        'medium': 6.0,     # Complexity <= 6.0
        'large': 8.0,      # Complexity <= 8.0
        'epic': 10.0       # Complexity > 8.0
    }

    # Effort descriptions
    EFFORT_DESCRIPTIONS = {
        'trivial': '1-2 hours (simple task)',
        'small': '1-2 days (focused work)',
        'medium': '3-5 days (coordinated effort)',
        'large': '1-2 weeks (significant work)',
        'epic': '2-4 weeks (major undertaking)'
    }

    @classmethod
    def validate_weights(cls) -> bool:
        """Validate that factor weights sum to 1.0."""
        total = sum(cls.FACTOR_WEIGHTS.values())
        return abs(total - 1.0) < 0.001  # Allow small floating point errors

    @classmethod
    def get_weight(cls, factor: str) -> float:
        """Get weight for a specific factor."""
        return cls.FACTOR_WEIGHTS.get(factor, 0.0)

    @classmethod
    def get_priority_level(cls, score: float) -> str:
        """Determine priority level from score."""
        if score >= cls.PRIORITY_THRESHOLDS['critical']:
            return 'CRITICAL'
        elif score >= cls.PRIORITY_THRESHOLDS['high']:
            return 'HIGH'
        elif score >= cls.PRIORITY_THRESHOLDS['medium']:
            return 'MEDIUM'
        elif score >= cls.PRIORITY_THRESHOLDS['low']:
            return 'LOW'
        else:
            return 'MINIMAL'

    @classmethod
    def get_effort_category(cls, complexity: float) -> str:
        """Determine effort category from complexity."""
        if complexity <= cls.EFFORT_THRESHOLDS['trivial']:
            return 'trivial'
        elif complexity <= cls.EFFORT_THRESHOLDS['small']:
            return 'small'
        elif complexity <= cls.EFFORT_THRESHOLDS['medium']:
            return 'medium'
        elif complexity <= cls.EFFORT_THRESHOLDS['large']:
            return 'large'
        else:
            return 'epic'

    @classmethod
    def get_effort_description(cls, complexity: float) -> str:
        """Get effort description for complexity level."""
        category = cls.get_effort_category(complexity)
        return cls.EFFORT_DESCRIPTIONS[category]


# Validate configuration on import
if not ScoringConfig.validate_weights():
    raise ValueError("Factor weights must sum to 1.0")
