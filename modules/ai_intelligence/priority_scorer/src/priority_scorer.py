"""
Priority Scorer - WSP/WRE AI Intelligence Module

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive priority scoring and testing capabilities
- WSP 54 (Agent Duties): AI-powered priority scoring for autonomous development
- WSP 22 (ModLog): Change tracking and scoring history
- WSP 50 (Pre-Action Verification): Enhanced verification before priority scoring

Provides AI-powered priority scoring capabilities for autonomous development operations.
Enables 0102 pArtifacts to score and prioritize tasks, modules, and development activities.
"""

import json
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


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


class PriorityScorer:
    """
    AI-powered priority scorer for autonomous development operations.
    
    Provides comprehensive priority scoring including:
    - Multi-factor scoring algorithm
    - WSP compliance integration
    - Effort estimation
    - Risk assessment
    - Resource optimization
    """
    
    def __init__(self):
        """Initialize the priority scorer with WSP compliance standards."""
        self.factor_weights = {
            'complexity': 0.15,
            'importance': 0.20,
            'impact': 0.18,
            'urgency': 0.12,
            'dependencies': 0.10,
            'resources': 0.08,
            'risk': 0.07,
            'wsp_compliance': 0.05,
            'business_value': 0.03,
            'technical_debt': 0.02
        }
        
        self.wsp_keywords = [
            'wsp', 'protocol', 'compliance', '0102', 'partifact', 'quantum',
            'autonomous', 'agent', 'modular', 'testing', 'documentation'
        ]
        
    def score_item(self, item_data: Dict[str, Any]) -> PriorityScore:
        """
        Score a single item for priority.
        
        Args:
            item_data: Dictionary containing item information and factors
            
        Returns:
            PriorityScore with comprehensive scoring results
        """
        try:
            # Extract basic information
            item_id = item_data.get('id', 'unknown')
            name = item_data.get('name', 'Unnamed Item')
            category = item_data.get('category', 'general')
            
            # Calculate factors
            factors = self._calculate_factors(item_data)
            
            # Calculate overall score
            score = self._calculate_overall_score(factors)
            
            # Determine priority level
            priority_level = self._determine_priority_level(score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(factors, score)
            
            # Estimate effort
            estimated_effort = self._estimate_effort(factors)
            
            # Extract WSP references
            wsp_references = self._extract_wsp_references(item_data)
            
            return PriorityScore(
                item_id=item_id,
                name=name,
                category=category,
                priority_level=priority_level,
                score=score,
                factors=factors,
                recommendations=recommendations,
                estimated_effort=estimated_effort,
                wsp_references=wsp_references,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            # Return minimal score on error
            return PriorityScore(
                item_id=item_data.get('id', 'error'),
                name=item_data.get('name', 'Error Item'),
                category='error',
                priority_level=PriorityLevel.MINIMAL,
                score=0.0,
                factors=ScoringFactors(),
                recommendations=[f"Error during scoring: {str(e)}"],
                estimated_effort="Unknown",
                wsp_references=[],
                timestamp=datetime.now()
            )
    
    def score_multiple_items(self, items_data: List[Dict[str, Any]]) -> List[PriorityScore]:
        """
        Score multiple items and return sorted by priority.
        
        Args:
            items_data: List of item data dictionaries
            
        Returns:
            List of PriorityScore objects sorted by priority
        """
        scores = []
        
        for item_data in items_data:
            score = self.score_item(item_data)
            scores.append(score)
        
        # Sort by score (lower score = higher priority)
        scores.sort(key=lambda x: x.score)
        
        return scores
    
    def _calculate_factors(self, item_data: Dict[str, Any]) -> ScoringFactors:
        """Calculate individual scoring factors."""
        factors = ScoringFactors()
        
        # Complexity factor (0-10 scale)
        factors.complexity = min(max(item_data.get('complexity', 5.0), 0.0), 10.0)
        
        # Importance factor (0-10 scale)
        factors.importance = min(max(item_data.get('importance', 5.0), 0.0), 10.0)
        
        # Impact factor (0-10 scale)
        factors.impact = min(max(item_data.get('impact', 5.0), 0.0), 10.0)
        
        # Urgency factor (0-10 scale)
        factors.urgency = min(max(item_data.get('urgency', 5.0), 0.0), 10.0)
        
        # Dependencies factor (0-10 scale, higher = more dependencies)
        factors.dependencies = min(max(item_data.get('dependencies', 5.0), 0.0), 10.0)
        
        # Resources factor (0-10 scale, higher = more resources needed)
        factors.resources = min(max(item_data.get('resources', 5.0), 0.0), 10.0)
        
        # Risk factor (0-10 scale, higher = more risk)
        factors.risk = min(max(item_data.get('risk', 5.0), 0.0), 10.0)
        
        # WSP compliance factor (0-10 scale, higher = better compliance)
        factors.wsp_compliance = min(max(item_data.get('wsp_compliance', 5.0), 0.0), 10.0)
        
        # Business value factor (0-10 scale)
        factors.business_value = min(max(item_data.get('business_value', 5.0), 0.0), 10.0)
        
        # Technical debt factor (0-10 scale, higher = more debt)
        factors.technical_debt = min(max(item_data.get('technical_debt', 5.0), 0.0), 10.0)
        
        return factors
    
    def _calculate_overall_score(self, factors: ScoringFactors) -> float:
        """Calculate overall priority score using weighted factors."""
        score = 0.0
        
        # Apply weights to each factor
        score += factors.complexity * self.factor_weights['complexity']
        score += factors.importance * self.factor_weights['importance']
        score += factors.impact * self.factor_weights['impact']
        score += factors.urgency * self.factor_weights['urgency']
        score += factors.dependencies * self.factor_weights['dependencies']
        score += factors.resources * self.factor_weights['resources']
        score += factors.risk * self.factor_weights['risk']
        score += factors.wsp_compliance * self.factor_weights['wsp_compliance']
        score += factors.business_value * self.factor_weights['business_value']
        score += factors.technical_debt * self.factor_weights['technical_debt']
        
        # Normalize to 0-100 scale
        return min(max(score * 10, 0.0), 100.0)
    
    def _determine_priority_level(self, score: float) -> PriorityLevel:
        """Determine priority level based on score."""
        if score <= 20:
            return PriorityLevel.CRITICAL
        elif score <= 40:
            return PriorityLevel.HIGH
        elif score <= 60:
            return PriorityLevel.MEDIUM
        elif score <= 80:
            return PriorityLevel.LOW
        else:
            return PriorityLevel.MINIMAL
    
    def _generate_recommendations(self, factors: ScoringFactors, score: float) -> List[str]:
        """Generate recommendations based on factors and score."""
        recommendations = []
        
        # High complexity recommendations
        if factors.complexity > 7:
            recommendations.append("Consider breaking down into smaller tasks")
        
        # High risk recommendations
        if factors.risk > 7:
            recommendations.append("Implement additional testing and validation")
        
        # Low WSP compliance recommendations
        if factors.wsp_compliance < 3:
            recommendations.append("Priority: Address WSP compliance violations")
        
        # High technical debt recommendations
        if factors.technical_debt > 7:
            recommendations.append("Consider refactoring to reduce technical debt")
        
        # High dependencies recommendations
        if factors.dependencies > 7:
            recommendations.append("Coordinate with dependent modules")
        
        # High resource requirements
        if factors.resources > 7:
            recommendations.append("Ensure adequate resources are allocated")
        
        # Overall score recommendations
        if score <= 20:
            recommendations.append("CRITICAL: Immediate attention required")
        elif score <= 40:
            recommendations.append("HIGH: Schedule for next development cycle")
        elif score <= 60:
            recommendations.append("MEDIUM: Include in regular development planning")
        else:
            recommendations.append("LOW: Consider for future development cycles")
        
        return recommendations
    
    def _estimate_effort(self, factors: ScoringFactors) -> str:
        """Estimate effort based on factors."""
        # Calculate effort score based on complexity and resources
        effort_score = (factors.complexity + factors.resources) / 2
        
        if effort_score <= 2:
            return "Very Low (1-2 hours)"
        elif effort_score <= 4:
            return "Low (2-4 hours)"
        elif effort_score <= 6:
            return "Medium (4-8 hours)"
        elif effort_score <= 8:
            return "High (1-2 days)"
        else:
            return "Very High (3+ days)"
    
    def _extract_wsp_references(self, item_data: Dict[str, Any]) -> List[str]:
        """Extract WSP references from item data."""
        wsp_references = []
        
        # Check description and notes for WSP references
        description = item_data.get('description', '')
        notes = item_data.get('notes', '')
        combined_text = f"{description} {notes}".lower()
        
        # Look for WSP protocol references
        import re
        wsp_pattern = r'\b(?:wsp|protocol)\s*[#]?\s*(\d+)\b'
        wsp_matches = re.findall(wsp_pattern, combined_text, re.IGNORECASE)
        
        for match in wsp_matches:
            wsp_references.append(f"WSP {match}")
        
        # Look for WSP keywords
        for keyword in self.wsp_keywords:
            if keyword.lower() in combined_text:
                wsp_references.append(f"WSP keyword: {keyword}")
        
        # Remove duplicates
        unique_references = list(dict.fromkeys(wsp_references))
        return unique_references
    
    def save_scores(self, scores: List[PriorityScore], output_path: str) -> bool:
        """
        Save priority scores to file.
        
        Args:
            scores: List of PriorityScore objects
            output_path: Path to save the scores
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to JSON-serializable format
            scores_data = []
            for score in scores:
                score_dict = {
                    'item_id': score.item_id,
                    'name': score.name,
                    'category': score.category,
                    'priority_level': score.priority_level.name,
                    'score': score.score,
                    'factors': {
                        'complexity': score.factors.complexity,
                        'importance': score.factors.importance,
                        'impact': score.factors.impact,
                        'urgency': score.factors.urgency,
                        'dependencies': score.factors.dependencies,
                        'resources': score.factors.resources,
                        'risk': score.factors.risk,
                        'wsp_compliance': score.factors.wsp_compliance,
                        'business_value': score.factors.business_value,
                        'technical_debt': score.factors.technical_debt
                    },
                    'recommendations': score.recommendations,
                    'estimated_effort': score.estimated_effort,
                    'wsp_references': score.wsp_references,
                    'timestamp': score.timestamp.isoformat()
                }
                scores_data.append(score_dict)
            
            # Save as JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(scores_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving scores: {e}")
            return False
    
    def load_scores(self, file_path: str) -> List[PriorityScore]:
        """
        Load priority scores from file.
        
        Args:
            file_path: Path to the scores file
            
        Returns:
            List of PriorityScore objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                scores_data = json.load(f)
            
            scores = []
            for score_dict in scores_data:
                factors = ScoringFactors(**score_dict['factors'])
                score = PriorityScore(
                    item_id=score_dict['item_id'],
                    name=score_dict['name'],
                    category=score_dict['category'],
                    priority_level=PriorityLevel[score_dict['priority_level']],
                    score=score_dict['score'],
                    factors=factors,
                    recommendations=score_dict['recommendations'],
                    estimated_effort=score_dict['estimated_effort'],
                    wsp_references=score_dict['wsp_references'],
                    timestamp=datetime.fromisoformat(score_dict['timestamp'])
                )
                scores.append(score)
            
            return scores
            
        except Exception as e:
            print(f"Error loading scores: {e}")
            return []


def score_item(item_data: Dict[str, Any]) -> PriorityScore:
    """
    Convenience function to score a single item.
    
    Args:
        item_data: Item data dictionary
        
    Returns:
        PriorityScore with scoring results
    """
        scorer = PriorityScorer()
    return scorer.score_item(item_data)


def score_items(items_data: List[Dict[str, Any]]) -> List[PriorityScore]:
    """
    Convenience function to score multiple items.
    
    Args:
        items_data: List of item data dictionaries
        
    Returns:
        List of PriorityScore objects sorted by priority
    """
    scorer = PriorityScorer()
    return scorer.score_multiple_items(items_data)


if __name__ == "__main__":
    """Test the priority scorer with sample data."""
    # Sample items to score
    sample_items = [
        {
            'id': 'wsp_22_fix',
            'name': 'Fix WSP 22 ModLog violations',
            'category': 'compliance',
            'description': 'Create missing ModLog.md files for enterprise domains',
            'complexity': 3.0,
            'importance': 9.0,
            'impact': 8.0,
            'urgency': 9.0,
            'dependencies': 2.0,
            'resources': 4.0,
            'risk': 2.0,
            'wsp_compliance': 1.0,
            'business_value': 8.0,
            'technical_debt': 3.0
        },
        {
            'id': 'wsp_34_implementation',
            'name': 'Implement WSP 34 incomplete modules',
            'category': 'development',
            'description': 'Complete implementation of code_analyzer and other modules',
            'complexity': 7.0,
            'importance': 7.0,
            'impact': 6.0,
            'urgency': 6.0,
            'dependencies': 5.0,
            'resources': 6.0,
            'risk': 4.0,
            'wsp_compliance': 5.0,
            'business_value': 6.0,
            'technical_debt': 5.0
        }
    ]
    
    scorer = PriorityScorer()
    scores = scorer.score_multiple_items(sample_items)
    
    print("Priority Scores:")
    for score in scores:
        print(f"\n{score.name} ({score.category})")
        print(f"Priority Level: {score.priority_level.name}")
        print(f"Score: {score.score:.1f}")
        print(f"Effort: {score.estimated_effort}")
        print(f"WSP References: {score.wsp_references}")
        print(f"Recommendations: {score.recommendations}") 