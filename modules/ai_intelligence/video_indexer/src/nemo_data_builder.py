# -*- coding: utf-8 -*-
"""
NeMo Data Builder - Convert enhanced video JSON to NeMo training formats.

WSP Compliance:
    WSP 77: Agent Coordination (NeMo training pipeline)
    WSP 73: Digital Twin Architecture

Purpose:
    Convert video_enhancer output to NeMo-compatible training formats:
    - SFT (Supervised Fine-Tuning) for voice cloning
    - DPO (Direct Preference Optimization) pairs
    - Decision training data

Output Formats:
    - voice_sft.jsonl: {"system": "...", "user": "...", "assistant": "..."}
    - dpo_pairs.jsonl: {"prompt": "...", "chosen": "...", "rejected": "..."}
    - decision_sft.jsonl: {"context": {...}, "decision": "...", "reason": "..."}
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TrainingRow:
    """Single training row."""
    system: str
    user: str
    assistant: str
    source_video: str
    segment_idx: int
    quality_tier: int


@dataclass
class DPOPair:
    """DPO preference pair."""
    prompt: str
    chosen: str
    rejected: str
    source_video: str


class NemoDataBuilder:
    """
    Build NeMo training data from enhanced video JSONs.
    
    Example:
        >>> builder = NemoDataBuilder("memory/video_index/undaodu")
        >>> stats = builder.build_all("training_data/")
    """
    
    SYSTEM_PROMPT_VOICE = """You are 012's Digital Twin (0102). Respond in 012's authentic voice:
- Use casual but intelligent language
- Share personal experiences when relevant
- Use analogies to explain concepts
- Be direct and opinionated
- Avoid corporate speak and filler"""

    SYSTEM_PROMPT_DECISION = """You are 0102, 012's comment engagement agent. Decide whether to:
- COMMENT: High relevance, good opportunity to add value
- LIKE: Supportive content but no unique value to add
- IGNORE: Off-topic, toxic, or no engagement value"""

    def __init__(self, video_index_dir: str):
        """
        Initialize builder.
        
        Args:
            video_index_dir: Directory with enhanced video JSONs
        """
        self.video_dir = Path(video_index_dir)
        self.stats = {
            "videos_processed": 0,
            "sft_rows": 0,
            "dpo_pairs": 0,
            "decision_rows": 0,
            "skipped_no_training_data": 0,
        }
    
    def build_all(self, output_dir: str) -> Dict[str, int]:
        """
        Build all training data from video directory.
        
        Args:
            output_dir: Output directory for JSONL files
            
        Returns:
            Statistics dict
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        sft_file = output_path / "voice_sft.jsonl"
        dpo_file = output_path / "dpo_pairs.jsonl"
        decision_file = output_path / "decision_sft.jsonl"
        
        json_files = list(self.video_dir.glob("*.json"))
        logger.info(f"[NEMO] Found {len(json_files)} video JSONs")
        
        with open(sft_file, "w", encoding="utf-8") as sft_f, \
             open(dpo_file, "w", encoding="utf-8") as dpo_f, \
             open(decision_file, "w", encoding="utf-8") as dec_f:
            
            for json_path in json_files:
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        video_data = json.load(f)
                    
                    # Check for training_data field
                    training_data = video_data.get("training_data")
                    if not training_data:
                        self.stats["skipped_no_training_data"] += 1
                        continue
                    
                    self.stats["videos_processed"] += 1
                    video_id = video_data.get("video_id", json_path.stem)
                    
                    # Build SFT rows from quotable moments and teachings
                    sft_rows = self._build_sft_rows(video_data, training_data)
                    for row in sft_rows:
                        json.dump(row, sft_f, ensure_ascii=False)
                        sft_f.write("\n")
                        self.stats["sft_rows"] += 1
                    
                    # Build DPO pairs from style variations
                    dpo_pairs = self._build_dpo_pairs(video_data, training_data)
                    for pair in dpo_pairs:
                        json.dump(pair, dpo_f, ensure_ascii=False)
                        dpo_f.write("\n")
                        self.stats["dpo_pairs"] += 1
                    
                    # Build decision training from comment triggers
                    decision_rows = self._build_decision_rows(video_data, training_data)
                    for row in decision_rows:
                        json.dump(row, dec_f, ensure_ascii=False)
                        dec_f.write("\n")
                        self.stats["decision_rows"] += 1
                    
                except Exception as e:
                    logger.warning(f"[NEMO] Error processing {json_path.name}: {e}")
                    continue
        
        logger.info(f"[NEMO] Built: {self.stats['sft_rows']} SFT, "
                   f"{self.stats['dpo_pairs']} DPO, {self.stats['decision_rows']} decision")
        
        return self.stats
    
    def _build_sft_rows(
        self,
        video_data: Dict,
        training_data: Dict
    ) -> List[Dict[str, Any]]:
        """Build SFT training rows from video content."""
        rows = []
        video_id = video_data.get("video_id", "unknown")
        topics = video_data.get("metadata", {}).get("topics", [])
        
        # From quotable moments
        quotables = training_data.get("quotable_moments", [])
        for q in quotables:
            if q.get("shareability", 0) > 0.6:
                # Create training row with context prompt
                prompt = self._generate_context_prompt(q, topics, video_data)
                rows.append({
                    "system": self.SYSTEM_PROMPT_VOICE,
                    "user": prompt,
                    "assistant": q.get("text", ""),
                    "source": video_id,
                    "type": "quotable",
                })
        
        # From Q&A moments
        qa_moments = training_data.get("qa_moments", [])
        for qa in qa_moments:
            if qa.get("answered") and qa.get("answer_text"):
                rows.append({
                    "system": self.SYSTEM_PROMPT_VOICE,
                    "user": qa.get("question", ""),
                    "assistant": qa.get("answer_text", ""),
                    "source": video_id,
                    "type": "qa",
                })
        
        # From teaching moments
        teachings = training_data.get("teaching_moments", [])
        segments = video_data.get("audio", {}).get("segments", [])
        for t in teachings:
            idx = t.get("segment_idx", 0)
            if idx < len(segments):
                concept = t.get("concept", "")
                text = segments[idx].get("text", "")
                rows.append({
                    "system": self.SYSTEM_PROMPT_VOICE,
                    "user": f"Explain: {concept}",
                    "assistant": text,
                    "source": video_id,
                    "type": "teaching",
                })
        
        return rows
    
    def _build_dpo_pairs(
        self,
        video_data: Dict,
        training_data: Dict
    ) -> List[Dict[str, Any]]:
        """Build DPO preference pairs."""
        pairs = []
        video_id = video_data.get("video_id", "unknown")
        
        # Get style fingerprint for generating rejected versions
        style = training_data.get("style_fingerprint", {})
        voice = training_data.get("voice_patterns", {})
        
        quotables = training_data.get("quotable_moments", [])
        for q in quotables:
            text = q.get("text", "")
            if len(text) > 20:
                # Create a "rejected" version (too formal, generic)
                rejected = self._make_rejected_version(text, style)
                if rejected != text:
                    pairs.append({
                        "prompt": f"Respond to a discussion about {q.get('context', 'this topic')}",
                        "chosen": text,
                        "rejected": rejected,
                        "source": video_id,
                    })
        
        return pairs
    
    def _build_decision_rows(
        self,
        video_data: Dict,
        training_data: Dict
    ) -> List[Dict[str, Any]]:
        """Build decision training rows from comment triggers."""
        rows = []
        video_id = video_data.get("video_id", "unknown")
        topics = video_data.get("metadata", {}).get("topics", [])
        
        triggers = training_data.get("comment_triggers", [])
        segments = video_data.get("audio", {}).get("segments", [])
        
        for t in triggers:
            idx = t.get("segment_idx", 0)
            engagement = t.get("engagement_score", 0.5)
            trigger_type = t.get("trigger_type", "general")
            
            # Get segment text
            text = ""
            if idx < len(segments):
                text = segments[idx].get("text", "")
            
            # Determine decision based on engagement score
            if engagement > 0.7:
                decision = "comment"
                reason = f"High engagement trigger: {trigger_type}"
            elif engagement > 0.4:
                decision = "like"
                reason = f"Moderate engagement: {trigger_type}"
            else:
                decision = "ignore"
                reason = "Low engagement potential"
            
            rows.append({
                "system": self.SYSTEM_PROMPT_DECISION,
                "context": {
                    "text": text[:200],
                    "topics": topics[:3],
                    "trigger_type": trigger_type,
                    "engagement_score": engagement,
                },
                "decision": decision,
                "reason": reason,
                "source": video_id,
            })
        
        return rows
    
    def _generate_context_prompt(
        self,
        quotable: Dict,
        topics: List[str],
        video_data: Dict
    ) -> str:
        """Generate a context prompt for the quotable."""
        context = quotable.get("context", "")
        category = quotable.get("category", "general")
        
        if context:
            return f"Share your thoughts on {context}"
        elif topics:
            return f"Discuss {topics[0]}"
        else:
            return f"Share a {category} insight"
    
    def _make_rejected_version(self, text: str, style: Dict) -> str:
        """Create a rejected (too formal/generic) version."""
        # Simple transformation to create contrast
        rejected = text
        
        # Remove signature phrases and make more formal
        replacements = [
            ("The thing is", "It should be noted that"),
            ("awesome", "satisfactory"),
            ("amazing", "acceptable"),
            ("So,", "Therefore,"),
            ("you know", "as one might observe"),
        ]
        
        for old, new in replacements:
            rejected = rejected.replace(old, new)
        
        # Only return if different
        return rejected if rejected != text else text + " (formal version)"


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("NeMo Data Builder Test")
    print("=" * 60)
    
    builder = NemoDataBuilder("memory/video_index/undaodu")
    stats = builder.build_all("training_data/")
    
    print(f"Videos processed: {stats['videos_processed']}")
    print(f"SFT rows: {stats['sft_rows']}")
    print(f"DPO pairs: {stats['dpo_pairs']}")
    print(f"Decision rows: {stats['decision_rows']}")
    print(f"Skipped (no training_data): {stats['skipped_no_training_data']}")
