"""
Priority Scorer Persistence - WSP Compliant Module

WSP Compliance: WSP 49 (Module Structure), WSP 60 (Memory Architecture)
Handles file I/O operations for score persistence and loading.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Union

from .data_structures import PriorityScore


class ScorePersistence:
    """
    Handles persistence operations for priority scores.

    Separated from main class to maintain single responsibility principle
    and enable focused testing of I/O operations.
    """

    @staticmethod
    def save_scores(scores: List[PriorityScore], output_path: Union[str, Path]) -> bool:
        """
        Save priority scores to JSON file.

        Args:
            scores: List of PriorityScore objects to save
            output_path: Path to save the scores

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            output_path = Path(output_path)

            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert scores to dictionaries
            score_data = {
                'metadata': {
                    'version': '1.0',
                    'total_scores': len(scores),
                    'generated_at': str(scores[0].timestamp) if scores else None,
                },
                'scores': [score.to_dict() for score in scores]
            }

            # Write to file with atomic operation
            temp_path = output_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(score_data, f, indent=2, ensure_ascii=False)

            # Atomic move
            temp_path.replace(output_path)

            return True

        except Exception as e:
            print(f"Error saving scores to {output_path}: {e}")
            return False

    @staticmethod
    def load_scores(file_path: Union[str, Path]) -> List[PriorityScore]:
        """
        Load priority scores from JSON file.

        Args:
            file_path: Path to the saved scores file

        Returns:
            List[PriorityScore]: List of loaded scores
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                print(f"Score file not found: {file_path}")
                return []

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate structure
            if 'scores' not in data:
                print(f"Invalid score file format: {file_path}")
                return []

            # Convert dictionaries back to PriorityScore objects
            scores = []
            for score_dict in data['scores']:
                try:
                    score = PriorityScore.from_dict(score_dict)
                    scores.append(score)
                except Exception as e:
                    print(f"Error loading score: {e}")
                    continue

            return scores

        except Exception as e:
            print(f"Error loading scores from {file_path}: {e}")
            return []

    @staticmethod
    def save_scores_csv(scores: List[PriorityScore], output_path: Union[str, Path]) -> bool:
        """
        Save priority scores to CSV format for analysis.

        Args:
            scores: List of PriorityScore objects to save
            output_path: Path to save the CSV file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import csv

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'item_id', 'name', 'category', 'priority_level', 'score',
                    'complexity', 'importance', 'impact', 'urgency', 'dependencies',
                    'resources', 'risk', 'wsp_compliance', 'business_value', 'technical_debt',
                    'estimated_effort', 'wsp_references', 'timestamp'
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for score in scores:
                    row = {
                        'item_id': score.item_id,
                        'name': score.name,
                        'category': score.category,
                        'priority_level': score.priority_level.name,
                        'score': f"{score.score:.1f}",
                        'complexity': f"{score.factors.complexity:.1f}",
                        'importance': f"{score.factors.importance:.1f}",
                        'impact': f"{score.factors.impact:.1f}",
                        'urgency': f"{score.factors.urgency:.1f}",
                        'dependencies': f"{score.factors.dependencies:.1f}",
                        'resources': f"{score.factors.resources:.1f}",
                        'risk': f"{score.factors.risk:.1f}",
                        'wsp_compliance': f"{score.factors.wsp_compliance:.1f}",
                        'business_value': f"{score.factors.business_value:.1f}",
                        'technical_debt': f"{score.factors.technical_debt:.1f}",
                        'estimated_effort': score.estimated_effort,
                        'wsp_references': '; '.join(score.wsp_references),
                        'timestamp': score.timestamp.isoformat(),
                    }
                    writer.writerow(row)

            return True

        except Exception as e:
            print(f"Error saving CSV to {output_path}: {e}")
            return False

    @staticmethod
    def get_score_summary(scores: List[PriorityScore]) -> Dict[str, Any]:
        """
        Generate summary statistics for a list of scores.

        Args:
            scores: List of PriorityScore objects

        Returns:
            Dict containing summary statistics
        """
        if not scores:
            return {
                'total_scores': 0,
                'average_score': 0.0,
                'priority_distribution': {},
                'category_distribution': {},
                'date_range': None,
            }

        # Calculate basic statistics
        total_scores = len(scores)
        avg_score = sum(score.score for score in scores) / total_scores

        # Priority distribution
        priority_dist = {}
        for score in scores:
            priority = score.priority_level.name
            priority_dist[priority] = priority_dist.get(priority, 0) + 1

        # Category distribution
        category_dist = {}
        for score in scores:
            category = score.category
            category_dist[category] = category_dist.get(category, 0) + 1

        # Date range
        timestamps = [score.timestamp for score in scores]
        date_range = {
            'earliest': min(timestamps).isoformat(),
            'latest': max(timestamps).isoformat(),
        }

        return {
            'total_scores': total_scores,
            'average_score': round(avg_score, 1),
            'priority_distribution': priority_dist,
            'category_distribution': category_dist,
            'date_range': date_range,
        }
