"""
Priority Scorer - WSP/WRE AI Intelligence Module (REFACTORED)

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive priority scoring and testing capabilities
- WSP 54 (Agent Duties): AI-powered priority scoring for autonomous development
- WSP 22 (ModLog): Change tracking and scoring history
- WSP 50 (Pre-Action Verification): Enhanced verification before priority scoring

Provides AI-powered priority scoring capabilities for autonomous development operations.
Enables 0102 pArtifacts to score and prioritize tasks, modules, and development activities.

REFACTORED ARCHITECTURE (First Principles):
- Separated concerns into focused modules for maintainability
- data_structures.py: Data models and serialization
- scoring_config.py: Configuration constants and thresholds
- scoring_engine.py: Core scoring algorithms and business logic
- persistence.py: File I/O operations and data persistence

File size reduced from 491 lines to focused orchestration layer.
"""

from typing import Dict, List, Any
from datetime import datetime

from .data_structures import PriorityScore, ScoringFactors, PriorityLevel
from .scoring_engine import ScoringEngine
from .persistence import ScorePersistence


class PriorityScorer:
    """
    AI-powered priority scorer for autonomous development operations.

    This is the orchestration layer that coordinates the separated modules.
    Maintains the same public API while delegating to focused components.
    """

    def __init__(self):
        """Initialize the priority scorer with WSP compliance standards."""
        # No internal state needed - all logic delegated to focused modules
        pass

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

            # Delegate to scoring engine
            factors = ScoringEngine.calculate_factors(item_data)
            score = ScoringEngine.calculate_overall_score(factors)
            priority_level = ScoringEngine.determine_priority_level(score)
            recommendations = ScoringEngine.generate_recommendations(factors, score)
            estimated_effort = ScoringEngine.estimate_effort(factors)
            wsp_references = ScoringEngine.extract_wsp_references(item_data)

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
            List of PriorityScore objects sorted by priority (highest first)
        """
        scores = []

        for item_data in items_data:
            score = self.score_item(item_data)
            scores.append(score)

        # Sort by score descending (highest priority first)
        scores.sort(key=lambda s: s.score, reverse=True)

        return scores

    def save_scores(self, scores: List[PriorityScore], output_path: str) -> bool:
        """
        Save priority scores to file.

        Args:
            scores: List of PriorityScore objects to save
            output_path: Path to save the scores

        Returns:
            bool: True if successful, False otherwise
        """
        return ScorePersistence.save_scores(scores, output_path)

    def load_scores(self, file_path: str) -> List[PriorityScore]:
        """
        Load priority scores from file.

        Args:
            file_path: Path to the saved scores file

        Returns:
            List[PriorityScore]: List of loaded scores
        """
        return ScorePersistence.load_scores(file_path)

    def save_scores_csv(self, scores: List[PriorityScore], output_path: str) -> bool:
        """
        Save priority scores to CSV format.

        Args:
            scores: List of PriorityScore objects to save
            output_path: Path to save the CSV file

        Returns:
            bool: True if successful, False otherwise
        """
        return ScorePersistence.save_scores_csv(scores, output_path)

    def get_score_summary(self, scores: List[PriorityScore]) -> Dict[str, Any]:
        """
        Generate summary statistics for scores.

        Args:
            scores: List of PriorityScore objects

        Returns:
            Dict containing summary statistics
        """
        return ScorePersistence.get_score_summary(scores)


# Convenience functions for backward compatibility
def score_item(item_data: Dict[str, Any]) -> PriorityScore:
    """
    Convenience function for single item scoring.

    Args:
        item_data: Item data dictionary

    Returns:
        PriorityScore object
    """
    scorer = PriorityScorer()
    return scorer.score_item(item_data)


def score_items(items_data: List[Dict[str, Any]]) -> List[PriorityScore]:
    """
    Convenience function for multiple item scoring.

    Args:
        items_data: List of item data dictionaries

    Returns:
        List of PriorityScore objects sorted by priority
    """
    scorer = PriorityScorer()
    return scorer.score_multiple_items(items_data)
