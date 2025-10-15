"""
Priority Scorer Data Structures - WSP Compliant Module

WSP Compliance: WSP 49 (Module Structure), WSP 11 (Interface Standards)
Contains all data structures and enums for the priority scoring system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Any, Dict


class PriorityLevel(Enum):
    """Priority levels for scoring."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MINIMAL = 5


@dataclass
class ScoringFactors:
    """Factors used for priority scoring."""
    complexity: float = 0.0
    importance: float = 0.0
    impact: float = 0.0
    urgency: float = 0.0
    dependencies: float = 0.0
    resources: float = 0.0
    risk: float = 0.0
    wsp_compliance: float = 0.0
    business_value: float = 0.0
    technical_debt: float = 0.0


@dataclass
class PriorityScore:
    """Result of priority scoring operation."""
    item_id: str
    name: str
    category: str
    priority_level: PriorityLevel
    score: float
    factors: ScoringFactors
    recommendations: List[str]
    estimated_effort: str
    wsp_references: List[str]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'category': self.category,
            'priority_level': self.priority_level.name,
            'score': self.score,
            'factors': {
                'complexity': self.factors.complexity,
                'importance': self.factors.importance,
                'impact': self.factors.impact,
                'urgency': self.factors.urgency,
                'dependencies': self.factors.dependencies,
                'resources': self.factors.resources,
                'risk': self.factors.risk,
                'wsp_compliance': self.factors.wsp_compliance,
                'business_value': self.factors.business_value,
                'technical_debt': self.factors.technical_debt,
            },
            'recommendations': self.recommendations,
            'estimated_effort': self.estimated_effort,
            'wsp_references': self.wsp_references,
            'timestamp': self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriorityScore':
        """Create from dictionary (deserialization)."""
        return cls(
            item_id=data['item_id'],
            name=data['name'],
            category=data['category'],
            priority_level=PriorityLevel[data['priority_level']],
            score=data['score'],
            factors=ScoringFactors(**data['factors']),
            recommendations=data['recommendations'],
            estimated_effort=data['estimated_effort'],
            wsp_references=data['wsp_references'],
            timestamp=datetime.fromisoformat(data['timestamp']),
        )
