# -*- coding: utf-8 -*-
"""Tests for TrajectoryLogger."""

import json
import tempfile
from pathlib import Path

import pytest


def test_trajectory_logger_writes_drafts():
    """Test that drafts are written to JSONL."""
    from modules.ai_intelligence.digital_twin.src.trajectory_logger import TrajectoryLogger
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tl = TrajectoryLogger(base_path=tmpdir)
        
        tl.log_draft(
            context={"thread": "test thread"},
            draft_text="Test draft",
            accepted=True,
            confidence=0.9
        )
        
        # Check file exists and has content
        drafts_file = Path(tmpdir) / "drafts.jsonl"
        assert drafts_file.exists()
        
        with open(drafts_file) as f:
            line = f.readline()
            data = json.loads(line)
        
        assert data["draft_text"] == "Test draft"
        assert data["accepted"] is True
        assert data["confidence"] == 0.9


def test_trajectory_logger_writes_decisions():
    """Test that decisions are written to JSONL."""
    from modules.ai_intelligence.digital_twin.src.trajectory_logger import TrajectoryLogger
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tl = TrajectoryLogger(base_path=tmpdir)
        
        tl.log_decision(
            context={"thread": "test"},
            decision="comment",
            rationale="High relevance",
            confidence=0.85
        )
        
        decisions_file = Path(tmpdir) / "decisions.jsonl"
        assert decisions_file.exists()
        
        with open(decisions_file) as f:
            data = json.loads(f.readline())
        
        assert data["decision"] == "comment"
        assert data["rationale"] == "High relevance"


def test_trajectory_logger_writes_actions():
    """Test that actions are written to JSONL."""
    from modules.ai_intelligence.digital_twin.src.trajectory_logger import TrajectoryLogger
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tl = TrajectoryLogger(base_path=tmpdir)
        
        tl.log_action(
            state={"url": "https://example.com"},
            action={"tool": "click", "selector": "#btn"},
            result="success"
        )
        
        actions_file = Path(tmpdir) / "actions.jsonl"
        assert actions_file.exists()
        
        with open(actions_file) as f:
            data = json.loads(f.readline())
        
        assert data["result"] == "success"
        assert data["action"]["tool"] == "click"


def test_trajectory_logger_stats():
    """Test get_stats returns correct counts."""
    from modules.ai_intelligence.digital_twin.src.trajectory_logger import TrajectoryLogger
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tl = TrajectoryLogger(base_path=tmpdir)
        
        tl.log_draft({}, "draft1", True, 0.9)
        tl.log_draft({}, "draft2", False, 0.5)
        tl.log_decision({}, "ignore", "low relevance", 0.8)
        
        stats = tl.get_stats()
        
        assert stats["drafts"] == 2
        assert stats["decisions"] == 1
        assert stats["actions"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
