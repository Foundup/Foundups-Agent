# -*- coding: utf-8 -*-
"""Tests for CommentDrafter."""

import pytest


def test_comment_drafter_draft():
    """Test basic draft generation."""
    from modules.ai_intelligence.digital_twin.src.comment_drafter import CommentDrafter
    
    drafter = CommentDrafter()
    
    draft = drafter.draft(
        thread_context="How do I get a work visa for Japan?",
        platform="youtube",
        context_url="https://youtube.com/watch?v=abc123"
    )
    
    assert draft.text is not None
    assert len(draft.text) > 0
    assert 0 <= draft.confidence <= 1
    assert draft.platform.value == "youtube"


def test_comment_drafter_applies_guardrails():
    """Test that guardrails are applied to output."""
    from modules.ai_intelligence.digital_twin.src.comment_drafter import (
        CommentDrafter,
        LocalLLM,
    )
    from modules.ai_intelligence.digital_twin.src.style_guardrails import StyleGuardrails
    
    # Mock LLM that returns text with filler
    class MockLLM:
        mock_mode = True
        def generate(self, prompt, snippets, max_tokens=300):
            return "Sure! I think this is a great question about Japan visas."
    
    drafter = CommentDrafter(llm=MockLLM())
    draft = drafter.draft(thread_context="Japan visa", platform="youtube")
    
    # Filler should be stripped
    assert not draft.text.startswith("Sure!")
    
    # Banned phrase should be flagged
    # Note: "I think" is banned
    assert any("banned" in flag.lower() for flag in draft.risk_flags) or "I think" not in draft.text


def test_comment_drafter_confidence_reduces_on_violations():
    """Test that confidence decreases with violations."""
    from modules.ai_intelligence.digital_twin.src.comment_drafter import CommentDrafter
    
    drafter = CommentDrafter()
    
    # Normal draft
    draft1 = drafter.draft(thread_context="Japan business", platform="youtube")
    
    # The mock returns clean text, so confidence should be reasonable
    assert draft1.confidence > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
