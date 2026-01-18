# -*- coding: utf-8 -*-
"""
Demo: Draft and Decide - End-to-end Digital Twin demo.

Usage:
    python -m modules.ai_intelligence.digital_twin.scripts.demo_draft_and_decide

This script demonstrates the full Digital Twin pipeline:
1. Load sample thread context
2. Retrieve from VoiceMemory
3. Generate draft comment
4. Make engagement decision
5. Log trajectory
"""

import json
import logging
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.ai_intelligence.digital_twin.src.schemas import (
    CommentAction,
    CommentDecision,
    CommentDraft,
)
from modules.ai_intelligence.digital_twin.src.voice_memory import VoiceMemory
from modules.ai_intelligence.digital_twin.src.style_guardrails import StyleGuardrails
from modules.ai_intelligence.digital_twin.src.comment_drafter import CommentDrafter
from modules.ai_intelligence.digital_twin.src.decision_policy import DecisionPolicy
from modules.ai_intelligence.digital_twin.src.trajectory_logger import TrajectoryLogger


def run_demo():
    """Run the Digital Twin demo pipeline."""
    print("=" * 70)
    print("Digital Twin Demo: Draft and Decide")
    print("=" * 70)
    
    # Sample thread context
    thread_context = """
    User: Hey @012, I'm thinking about moving to Japan to start a business.
    Any tips on the visa process? I've heard it's complicated.
    
    Other user: Yeah I tried and gave up, it's impossible without a sponsor.
    """
    
    print("\n[1] THREAD CONTEXT")
    print("-" * 50)
    print(thread_context.strip())
    
    # Initialize components
    print("\n[2] INITIALIZING COMPONENTS")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample voice corpus
        corpus_dir = Path(tmpdir) / "corpus"
        corpus_dir.mkdir()
        
        sample_comments = [
            {
                "text": "The Japan visa process requires a sponsor company. I went through this myself.",
                "id": "c1",
                "type": "comment"
            },
            {
                "text": "Starting a business in Japan requires capital and a solid business plan.",
                "id": "c2",
                "type": "comment"
            },
            {
                "text": "Tokyo has a great startup ecosystem. Happy to share more details!",
                "id": "c3",
                "type": "comment"
            },
        ]
        
        with open(corpus_dir / "samples.json", "w") as f:
            json.dump(sample_comments, f)
        
        # Build voice memory
        index_dir = Path(tmpdir) / "index"
        vm = VoiceMemory()
        count = vm.build_index(str(corpus_dir), str(index_dir))
        print(f"  VoiceMemory: Indexed {count} documents")
        
        # Initialize other components
        guardrails = StyleGuardrails()
        print(f"  StyleGuardrails: Loaded {len(guardrails.banned_phrases)} banned phrases")
        
        drafter = CommentDrafter(
            voice_memory=vm,
            guardrails=guardrails
        )
        print("  CommentDrafter: Initialized")
        
        policy = DecisionPolicy()
        print("  DecisionPolicy: Initialized")
        
        trajectory_dir = Path(tmpdir) / "trajectories"
        tlogger = TrajectoryLogger(base_path=str(trajectory_dir))
        print(f"  TrajectoryLogger: Writing to {trajectory_dir}")
        
        # Step 1: Retrieve from VoiceMemory
        print("\n[3] VOICE MEMORY RETRIEVAL")
        print("-" * 50)
        
        results = vm.query("Japan visa business startup", k=3)
        for i, r in enumerate(results):
            print(f"  {i+1}. [{r.get('score', 0):.2f}] {r['text'][:60]}...")
        
        # Step 2: Generate draft
        print("\n[4] COMMENT DRAFT")
        print("-" * 50)
        
        draft = drafter.draft(
            thread_context=thread_context,
            platform="youtube",
            context_url="https://youtube.com/watch?v=demo123"
        )
        
        print(f"  Platform: {draft.platform}")
        print(f"  Text: {draft.text}")
        print(f"  Confidence: {draft.confidence:.2f}")
        print(f"  Risk flags: {draft.risk_flags or 'None'}")
        
        # Step 3: Make decision
        print("\n[5] ENGAGEMENT DECISION")
        print("-" * 50)
        
        relevance = policy.estimate_relevance(thread_context)
        toxicity = policy.estimate_toxicity(thread_context)
        
        decision = policy.decide(
            relevance_score=relevance,
            toxicity_score=toxicity,
            thread_id="demo_thread_1"
        )
        
        print(f"  Relevance: {relevance:.2f}")
        print(f"  Toxicity: {toxicity:.2f}")
        print(f"  Action: {decision.action.value}")
        print(f"  Reason: {decision.reason}")
        print(f"  Confidence: {decision.confidence:.2f}")
        
        # Step 4: Log trajectory
        print("\n[6] TRAJECTORY LOGGING")
        print("-" * 50)
        
        tlogger.log_draft(
            context={"thread": thread_context, "platform": "youtube"},
            draft_text=draft.text,
            accepted=decision.action == CommentAction.COMMENT,
            confidence=draft.confidence,
            retrieved_snippets=[r["text"] for r in results]
        )
        
        tlogger.log_decision(
            context={"thread": thread_context, "relevance": relevance},
            decision=decision.action.value,
            rationale=decision.reason,
            confidence=decision.confidence
        )
        
        stats = tlogger.get_stats()
        print(f"  Logged drafts: {stats['drafts']}")
        print(f"  Logged decisions: {stats['decisions']}")
        
        # Final output
        print("\n[7] FINAL OUTPUT (JSON)")
        print("-" * 50)
        
        output = {
            "draft": {
                "text": draft.text,
                "confidence": draft.confidence,
                "risk_flags": draft.risk_flags,
            },
            "decision": {
                "action": decision.action.value,
                "reason": decision.reason,
                "confidence": decision.confidence,
            }
        }
        
        print(json.dumps(output, indent=2))
        
        print("\n" + "=" * 70)
        print("Demo complete! All components working.")
        print("=" * 70)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    run_demo()
