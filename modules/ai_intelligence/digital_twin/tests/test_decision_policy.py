# -*- coding: utf-8 -*-
"""Tests for DecisionPolicy."""

import pytest


def test_decision_policy_comment_high_relevance():
    """Test that high relevance triggers comment."""
    from modules.ai_intelligence.digital_twin.src.decision_policy import DecisionPolicy
    from modules.ai_intelligence.digital_twin.src.schemas import CommentAction
    
    policy = DecisionPolicy()
    
    decision = policy.decide(
        relevance_score=0.9,
        toxicity_score=0.1
    )
    
    assert decision.action == CommentAction.COMMENT
    assert decision.should_comment is True


def test_decision_policy_like_medium_relevance():
    """Test that medium relevance triggers like."""
    from modules.ai_intelligence.digital_twin.src.decision_policy import DecisionPolicy
    from modules.ai_intelligence.digital_twin.src.schemas import CommentAction
    
    policy = DecisionPolicy()
    
    decision = policy.decide(
        relevance_score=0.5,
        toxicity_score=0.1
    )
    
    assert decision.action == CommentAction.LIKE
    assert decision.should_comment is False


def test_decision_policy_ignore_low_relevance():
    """Test that low relevance triggers ignore."""
    from modules.ai_intelligence.digital_twin.src.decision_policy import DecisionPolicy
    from modules.ai_intelligence.digital_twin.src.schemas import CommentAction
    
    policy = DecisionPolicy()
    
    decision = policy.decide(
        relevance_score=0.2,
        toxicity_score=0.1
    )
    
    assert decision.action == CommentAction.IGNORE
    assert decision.should_comment is False


def test_decision_policy_ignore_high_toxicity():
    """Test that high toxicity triggers ignore regardless of relevance."""
    from modules.ai_intelligence.digital_twin.src.decision_policy import DecisionPolicy
    from modules.ai_intelligence.digital_twin.src.schemas import CommentAction
    
    policy = DecisionPolicy()
    
    decision = policy.decide(
        relevance_score=0.9,
        toxicity_score=0.5  # Above threshold
    )
    
    assert decision.action == CommentAction.IGNORE
    assert decision.should_comment is False


def test_decision_policy_relevance_estimation():
    """Test simple relevance estimation."""
    from modules.ai_intelligence.digital_twin.src.decision_policy import DecisionPolicy
    
    policy = DecisionPolicy()
    
    # High relevance text
    high = policy.estimate_relevance("How do I get a Japan visa for my startup?")
    assert high > 0.5
    
    # Low relevance text
    low = policy.estimate_relevance("What's for dinner tonight?")
    assert low < 0.5


def test_decision_policy_toxicity_estimation():
    """Test simple toxicity estimation."""
    from modules.ai_intelligence.digital_twin.src.decision_policy import DecisionPolicy
    
    policy = DecisionPolicy()
    
    # Toxic text
    toxic = policy.estimate_toxicity("You are an idiot and this is a scam!")
    assert toxic > 0.5
    
    # Clean text
    clean = policy.estimate_toxicity("Thank you for the helpful information!")
    assert clean < 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
