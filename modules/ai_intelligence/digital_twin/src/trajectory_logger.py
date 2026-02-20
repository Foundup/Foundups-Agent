# -*- coding: utf-8 -*-
"""
Trajectory Logger - Auto-collect gold training data for Digital Twin.

WSP Compliance:
    WSP 77: Agent Coordination (feeds training pipeline)
    WSP 91: DAE Observability (structured logging)

Purpose:
    Records every decision, draft, and tool action as training triples:
    - (context → draft) for SFT
    - (context → decision) for decision model
    - (state → action) for tool-use training
"""

import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DraftLog:
    """Context → Draft training example."""
    timestamp: str
    context: Dict[str, Any]  # thread_context, audience, intent, platform
    draft_text: str
    accepted: bool
    confidence: float
    retrieved_snippets: List[str] = field(default_factory=list)


@dataclass
class DecisionLog:
    """Context → Decision training example."""
    timestamp: str
    context: Dict[str, Any]
    decision: str  # "comment", "ignore", "like_only"
    rationale: str
    confidence: float


@dataclass
class ActionLog:
    """State → Action training example for tool-use."""
    timestamp: str
    state: Dict[str, Any]  # url, dom_hash, screenshot_hash, last_action
    action: Dict[str, Any]  # tool, selector, args
    result: str  # "success", "failure", "timeout"
    error: Optional[str] = None
    retry_count: int = 0


class TrajectoryLogger:
    """
    Gold training data collector for Digital Twin.
    
    Writes JSONL files that become training datasets:
    - drafts.jsonl: (context → draft) for SFT
    - decisions.jsonl: (context → decision) for decision model
    - actions.jsonl: (state → action) for tool-use
    
    Example:
        >>> logger = TrajectoryLogger()
        >>> logger.log_draft(context, "Great question!", accepted=True)
        >>> logger.log_decision(context, "comment", "High relevance")
        >>> logger.log_action(state, action, "success")
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize trajectory logger.
        
        Args:
            base_path: Directory for JSONL files (default: data/trajectories/)
        """
        if base_path is None:
            base_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "trajectories"
            )
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.drafts_file = self.base_path / "drafts.jsonl"
        self.decisions_file = self.base_path / "decisions.jsonl"
        self.actions_file = self.base_path / "actions.jsonl"
        
        logger.info(f"[TRAJECTORY] Initialized at: {self.base_path}")
    
    def _append_jsonl(self, file_path: Path, data: dict) -> None:
        """Append a JSON line to file."""
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    
    def _get_timestamp(self) -> str:
        """Get ISO timestamp."""
        return datetime.now().isoformat()
    
    def log_draft(
        self,
        context: Dict[str, Any],
        draft_text: str,
        accepted: bool,
        confidence: float = 0.0,
        retrieved_snippets: Optional[List[str]] = None
    ) -> DraftLog:
        """
        Log a draft attempt for SFT training.
        
        Args:
            context: Thread context (thread_context, audience, intent, platform)
            draft_text: Generated comment text
            accepted: Whether 012 approved this draft
            confidence: Model confidence score
            retrieved_snippets: RAG snippets used
            
        Returns:
            DraftLog record
        """
        log = DraftLog(
            timestamp=self._get_timestamp(),
            context=context,
            draft_text=draft_text,
            accepted=accepted,
            confidence=confidence,
            retrieved_snippets=retrieved_snippets or []
        )
        
        self._append_jsonl(self.drafts_file, asdict(log))
        logger.debug(f"[TRAJECTORY] Draft logged: accepted={accepted}")
        
        return log
    
    def log_decision(
        self,
        context: Dict[str, Any],
        decision: str,
        rationale: str,
        confidence: float = 0.0
    ) -> DecisionLog:
        """
        Log a decision for decision model training.
        
        Args:
            context: Thread context
            decision: "comment", "ignore", or "like_only"
            rationale: Why this decision was made
            confidence: Model confidence score
            
        Returns:
            DecisionLog record
        """
        log = DecisionLog(
            timestamp=self._get_timestamp(),
            context=context,
            decision=decision,
            rationale=rationale,
            confidence=confidence
        )
        
        self._append_jsonl(self.decisions_file, asdict(log))
        logger.debug(f"[TRAJECTORY] Decision logged: {decision}")
        
        return log
    
    def log_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        result: str,
        error: Optional[str] = None,
        retry_count: int = 0
    ) -> ActionLog:
        """
        Log a tool action for tool-use training.
        
        Args:
            state: UI state (url, dom_hash, screenshot_hash, last_action)
            action: Action taken (tool, selector, args)
            result: "success", "failure", "timeout"
            error: Error message if failed
            retry_count: Number of retries attempted
            
        Returns:
            ActionLog record
        """
        log = ActionLog(
            timestamp=self._get_timestamp(),
            state=state,
            action=action,
            result=result,
            error=error,
            retry_count=retry_count
        )
        
        self._append_jsonl(self.actions_file, asdict(log))
        logger.debug(f"[TRAJECTORY] Action logged: {result}")
        
        return log
    
    def get_stats(self) -> Dict[str, int]:
        """Get count of logged items."""
        def count_lines(file_path: Path) -> int:
            if not file_path.exists():
                return 0
            with open(file_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        
        return {
            "drafts": count_lines(self.drafts_file),
            "decisions": count_lines(self.decisions_file),
            "actions": count_lines(self.actions_file),
        }
    
    @staticmethod
    def hash_dom(dom_content: str) -> str:
        """Create hash of DOM for state tracking."""
        return hashlib.sha256(dom_content.encode()).hexdigest()[:16]
    
    @staticmethod
    def hash_screenshot(image_bytes: bytes) -> str:
        """Create hash of screenshot for state tracking."""
        return hashlib.sha256(image_bytes).hexdigest()[:16]


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Trajectory Logger Test")
    print("=" * 60)
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tl = TrajectoryLogger(base_path=tmpdir)
        
        # Log draft
        tl.log_draft(
            context={"thread": "Japan visa question", "platform": "youtube"},
            draft_text="Great question! The visa process...",
            accepted=True,
            confidence=0.92
        )
        
        # Log decision
        tl.log_decision(
            context={"thread": "Spam comment", "platform": "youtube"},
            decision="ignore",
            rationale="Low relevance spam",
            confidence=0.95
        )
        
        # Log action
        tl.log_action(
            state={"url": "https://studio.youtube.com/...", "dom_hash": "abc123"},
            action={"tool": "click", "selector": "#reply-btn"},
            result="success"
        )
        
        stats = tl.get_stats()
        print(f"Stats: {stats}")
        print(f"Drafts: {stats['drafts']}")
        print(f"Decisions: {stats['decisions']}")
        print(f"Actions: {stats['actions']}")
