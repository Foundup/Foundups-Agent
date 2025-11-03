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

Tests for Feedback Learner
WSP Compliance: WSP 5 (Test Coverage), WSP 6 (Test Audit)

Tests feedback-driven learning and component weight adjustment.
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from holo_index.feedback_learner import (
    FeedbackLearner,
    FeedbackRating,
    FeedbackRecord,
    get_learner
)
from holo_index.intent_classifier import IntentType


class TestFeedbackLearner:
    """Test suite for FeedbackLearner"""

    @pytest.fixture
    def temp_memory(self):
        """Fixture providing temporary memory directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def learner(self, temp_memory):
        """Fixture providing FeedbackLearner instance"""
        return FeedbackLearner(memory_root=temp_memory)

    # Feedback Recording Tests

    def test_record_good_feedback(self, learner):
        """Test recording GOOD feedback"""
        feedback_id = learner.record_feedback(
            query="what does WSP 64 say",
            intent=IntentType.DOC_LOOKUP,
            components_executed=["wsp_documentation_guardian", "module_analysis"],
            rating=FeedbackRating.GOOD
        )

        assert feedback_id is not None
        assert len(learner.feedback_history) == 1
        assert learner.metrics["total_feedback"] == 1
        assert learner.metrics["good_ratings"] == 1

    def test_record_noisy_feedback(self, learner):
        """Test recording NOISY feedback"""
        feedback_id = learner.record_feedback(
            query="where is AgenticChatEngine",
            intent=IntentType.CODE_LOCATION,
            components_executed=[
                "module_analysis",
                "orphan_analysis",
                "file_size_monitor",
                "health_analysis"  # This one was noisy
            ],
            rating=FeedbackRating.NOISY,
            notes="Too many health warnings for code location query"
        )

        assert feedback_id is not None
        assert len(learner.feedback_history) == 1
        assert learner.metrics["total_feedback"] == 1
        assert learner.metrics["noisy_ratings"] == 1

    def test_record_missing_feedback(self, learner):
        """Test recording MISSING feedback"""
        feedback_id = learner.record_feedback(
            query="check holo_index health",
            intent=IntentType.MODULE_HEALTH,
            components_executed=["health_analysis"],
            rating=FeedbackRating.MISSING,
            notes="Should have included orphan analysis"
        )

        assert feedback_id is not None
        assert len(learner.feedback_history) == 1
        assert learner.metrics["missing_ratings"] == 1

    def test_multiple_feedback_records(self, learner):
        """Test recording multiple feedback instances"""
        for i in range(5):
            learner.record_feedback(
                query=f"test query {i}",
                intent=IntentType.GENERAL,
                components_executed=["module_analysis"],
                rating=FeedbackRating.GOOD
            )

        assert len(learner.feedback_history) == 5
        assert learner.metrics["total_feedback"] == 5

    # Weight Adjustment Tests

    def test_good_feedback_increases_weights(self, learner):
        """Test GOOD feedback increases component weights"""
        components = ["wsp_documentation_guardian", "module_analysis"]

        # Record good feedback
        learner.record_feedback(
            query="what does WSP 64 say",
            intent=IntentType.DOC_LOOKUP,
            components_executed=components,
            rating=FeedbackRating.GOOD
        )

        # Check weights increased
        for component in components:
            weight = learner.get_component_weight(IntentType.DOC_LOOKUP, component)
            assert weight > 0.5  # Should be higher than neutral (0.5)
            assert weight == 0.6  # Exactly +0.1 from default

    def test_noisy_feedback_decreases_weights(self, learner):
        """Test NOISY feedback decreases component weights"""
        components = ["health_analysis", "vibecoding_analysis"]

        # Record noisy feedback
        learner.record_feedback(
            query="where is AgenticChatEngine",
            intent=IntentType.CODE_LOCATION,
            components_executed=components,
            rating=FeedbackRating.NOISY
        )

        # Check weights decreased
        for component in components:
            weight = learner.get_component_weight(IntentType.CODE_LOCATION, component)
            assert weight < 0.5  # Should be lower than neutral
            assert weight == 0.35  # Exactly -0.15 from default

    def test_missing_feedback_no_weight_change(self, learner):
        """Test MISSING feedback does not auto-adjust weights"""
        components = ["health_analysis"]

        # Record missing feedback
        learner.record_feedback(
            query="check holo_index health",
            intent=IntentType.MODULE_HEALTH,
            components_executed=components,
            rating=FeedbackRating.MISSING
        )

        # Weight should remain at default (no automatic adjustment)
        weight = learner.get_component_weight(IntentType.MODULE_HEALTH, components[0])
        assert weight == 0.5

    def test_weight_accumulation(self, learner):
        """Test weights accumulate over multiple feedback cycles"""
        component = "module_analysis"

        # 3x GOOD feedback
        for i in range(3):
            learner.record_feedback(
                query=f"query {i}",
                intent=IntentType.GENERAL,
                components_executed=[component],
                rating=FeedbackRating.GOOD
            )

        weight = learner.get_component_weight(IntentType.GENERAL, component)
        assert weight == 0.8  # 0.5 + (3 * 0.1)

    def test_weight_bounds_enforcement(self, learner):
        """Test weights stay within [0.0, 1.0] bounds"""
        component = "test_component"

        # 10x GOOD feedback (should max at 1.0)
        for i in range(10):
            learner.record_feedback(
                query=f"query {i}",
                intent=IntentType.GENERAL,
                components_executed=[component],
                rating=FeedbackRating.GOOD
            )

        weight = learner.get_component_weight(IntentType.GENERAL, component)
        assert weight == 1.0  # Should cap at 1.0

        # 10x NOISY feedback (should bottom at 0.0)
        for i in range(10):
            learner.record_feedback(
                query=f"query {i}",
                intent=IntentType.GENERAL,
                components_executed=[component],
                rating=FeedbackRating.NOISY
            )

        weight = learner.get_component_weight(IntentType.GENERAL, component)
        assert weight == 0.0  # Should floor at 0.0

    # Component Filtering Tests

    def test_get_filtered_components_no_learning(self, learner):
        """Test filtering with no learned weights returns all components"""
        available = ["comp1", "comp2", "comp3"]

        filtered = learner.get_filtered_components(
            intent=IntentType.DOC_LOOKUP,
            available_components=available
        )

        assert filtered == available

    def test_get_filtered_components_with_weights(self, learner):
        """Test filtering based on learned weights"""
        # Train: comp1 is good, comp2 is noisy
        learner.record_feedback(
            query="test",
            intent=IntentType.GENERAL,
            components_executed=["comp1"],
            rating=FeedbackRating.GOOD
        )
        learner.record_feedback(
            query="test",
            intent=IntentType.GENERAL,
            components_executed=["comp2"],
            rating=FeedbackRating.NOISY
        )

        available = ["comp1", "comp2", "comp3"]

        filtered = learner.get_filtered_components(
            intent=IntentType.GENERAL,
            available_components=available,
            threshold=0.3
        )

        # comp1 (weight: 0.6) and comp3 (default: 0.5) should be included
        # comp2 (weight: 0.35) should be included (just above threshold)
        assert "comp1" in filtered
        assert "comp3" in filtered

    def test_filter_threshold_adjustment(self, learner):
        """Test different threshold values"""
        # Train comp1 higher
        for i in range(3):
            learner.record_feedback(
                query=f"test {i}",
                intent=IntentType.GENERAL,
                components_executed=["comp1"],
                rating=FeedbackRating.GOOD
            )

        available = ["comp1", "comp2"]

        # Low threshold - both included
        filtered_low = learner.get_filtered_components(
            intent=IntentType.GENERAL,
            available_components=available,
            threshold=0.3
        )
        assert len(filtered_low) == 2

        # High threshold - only comp1 included
        filtered_high = learner.get_filtered_components(
            intent=IntentType.GENERAL,
            available_components=available,
            threshold=0.7
        )
        assert len(filtered_high) == 1
        assert "comp1" in filtered_high

    def test_filter_safety_minimum(self, learner):
        """Test filtering always returns at least one component"""
        # Train all components as noisy
        for comp in ["comp1", "comp2"]:
            for i in range(5):
                learner.record_feedback(
                    query=f"test {i}",
                    intent=IntentType.GENERAL,
                    components_executed=[comp],
                    rating=FeedbackRating.NOISY
                )

        available = ["comp1", "comp2"]

        # Even with very low weights, should return components
        filtered = learner.get_filtered_components(
            intent=IntentType.GENERAL,
            available_components=available,
            threshold=0.3
        )

        # Should fall back to all components for safety
        assert len(filtered) >= 1

    # Memory Persistence Tests

    def test_memory_persistence(self, temp_memory):
        """Test feedback history persists across instances"""
        # Create learner and record feedback
        learner1 = FeedbackLearner(memory_root=temp_memory)
        learner1.record_feedback(
            query="test query",
            intent=IntentType.GENERAL,
            components_executed=["comp1"],
            rating=FeedbackRating.GOOD
        )

        # Create new instance - should load from disk
        learner2 = FeedbackLearner(memory_root=temp_memory)

        assert len(learner2.feedback_history) == 1
        assert learner2.feedback_history[0].query == "test query"
        assert learner2.metrics["total_feedback"] == 1

    def test_weight_persistence(self, temp_memory):
        """Test learned weights persist across instances"""
        # Create learner and train weights
        learner1 = FeedbackLearner(memory_root=temp_memory)
        learner1.record_feedback(
            query="test",
            intent=IntentType.DOC_LOOKUP,
            components_executed=["wsp_documentation_guardian"],
            rating=FeedbackRating.GOOD
        )

        # Create new instance - should load weights
        learner2 = FeedbackLearner(memory_root=temp_memory)

        weight = learner2.get_component_weight(
            IntentType.DOC_LOOKUP,
            "wsp_documentation_guardian"
        )
        assert weight == 0.6  # Learned weight should persist

    # Statistics Tests

    def test_get_feedback_stats(self, learner):
        """Test feedback statistics calculation"""
        # Record mixed feedback
        learner.record_feedback(
            query="q1", intent=IntentType.GENERAL,
            components_executed=["comp1"], rating=FeedbackRating.GOOD
        )
        learner.record_feedback(
            query="q2", intent=IntentType.GENERAL,
            components_executed=["comp2"], rating=FeedbackRating.GOOD
        )
        learner.record_feedback(
            query="q3", intent=IntentType.GENERAL,
            components_executed=["comp3"], rating=FeedbackRating.NOISY
        )

        stats = learner.get_feedback_stats()

        assert stats["total_feedback"] == 3
        assert stats["good_ratings"] == 2
        assert stats["noisy_ratings"] == 1
        assert stats["good_rate"] == 2/3
        assert stats["noisy_rate"] == 1/3

    def test_get_feedback_history_filters(self, learner):
        """Test feedback history filtering"""
        # Record different types
        learner.record_feedback(
            query="doc query", intent=IntentType.DOC_LOOKUP,
            components_executed=["comp1"], rating=FeedbackRating.GOOD
        )
        learner.record_feedback(
            query="code query", intent=IntentType.CODE_LOCATION,
            components_executed=["comp2"], rating=FeedbackRating.NOISY
        )
        learner.record_feedback(
            query="health query", intent=IntentType.MODULE_HEALTH,
            components_executed=["comp3"], rating=FeedbackRating.GOOD
        )

        # Filter by intent
        doc_feedback = learner.get_feedback_history(intent=IntentType.DOC_LOOKUP)
        assert len(doc_feedback) == 1
        assert doc_feedback[0].query == "doc query"

        # Filter by rating
        good_feedback = learner.get_feedback_history(rating=FeedbackRating.GOOD)
        assert len(good_feedback) == 2

        # Combined filters
        code_noisy = learner.get_feedback_history(
            intent=IntentType.CODE_LOCATION,
            rating=FeedbackRating.NOISY
        )
        assert len(code_noisy) == 1

    # Integration Tests

    def test_real_world_learning_cycle(self, learner):
        """Test complete learning cycle with realistic scenario"""
        # Scenario: User queries "what does WSP 64 say"
        # System executes all 7 components
        # User rates as NOISY because health warnings were irrelevant

        all_components = [
            "wsp_documentation_guardian",
            "module_analysis",
            "health_analysis",
            "vibecoding_analysis",
            "orphan_analysis",
            "file_size_monitor",
            "pattern_coach"
        ]

        # First query - all components execute
        learner.record_feedback(
            query="what does WSP 64 say",
            intent=IntentType.DOC_LOOKUP,
            components_executed=all_components,
            rating=FeedbackRating.NOISY,
            notes="Too many warnings for doc lookup"
        )

        # User rates again, but this time with fewer components
        relevant_only = ["wsp_documentation_guardian", "module_analysis"]
        learner.record_feedback(
            query="what does WSP 80 say",
            intent=IntentType.DOC_LOOKUP,
            components_executed=relevant_only,
            rating=FeedbackRating.GOOD
        )

        # After learning, system should filter components
        filtered = learner.get_filtered_components(
            intent=IntentType.DOC_LOOKUP,
            available_components=all_components,
            threshold=0.4
        )

        # wsp_documentation_guardian and module_analysis should have highest weights
        assert "wsp_documentation_guardian" in filtered
        assert "module_analysis" in filtered

        # Some noisy components should be filtered out
        assert len(filtered) < len(all_components)

    # Singleton Tests

    def test_get_learner_singleton(self):
        """Test get_learner returns singleton instance"""
        learner1 = get_learner()
        learner2 = get_learner()

        assert learner1 is learner2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
