# -*- coding: utf-8 -*-
"""
Gemma Segment Classifier - Fast Segment Quality Classification

WSP Compliance:
    WSP 77: Agent Coordination (Gemma Phase 1 - fast pattern matching)
    WSP 84: Code Reuse (follows gemma_validator.py pattern)
    WSP 91: DAE Observability

Purpose:
    Classify video segments by quality tier for Digital Twin training:
    - 0 = LOW (background noise, unclear speech, off-topic)
    - 1 = REGULAR (standard content, usable for context)
    - 2 = HIGH (quotable, clear insight, training-worthy)

Architecture:
    Uses Gemma 3 270M via llama_cpp for binary classification (<50ms)
    Pattern Source: gemma_validator.py (lines 68-116)

Usage:
    from modules.ai_intelligence.video_indexer.src.gemma_segment_classifier import (
        GemmaSegmentClassifier,
        get_segment_classifier
    )

    classifier = get_segment_classifier()
    result = classifier.classify_segment(
        segment_text="The key insight is that education must be democratized globally",
        video_title="Global Education Reform",
        speaker="012"
    )
    # Returns: {'tier': 2, 'confidence': 0.85, 'reason': 'Clear insight - training worthy'}
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class SegmentClassification:
    """Classification result for a video segment."""
    tier: int  # 0, 1, or 2
    confidence: float  # 0.0 to 1.0
    reason: str
    latency_ms: int
    is_training_worthy: bool  # tier >= 2


# =============================================================================
# Gemma Segment Classifier
# =============================================================================

class GemmaSegmentClassifier:
    """
    Fast segment quality classification using Gemma 3 270M.

    Binary classification tasks (<50ms):
    - Is this segment quotable/insightful? (HIGH tier)
    - Is this segment clear and on-topic? (REGULAR tier)
    - Is this segment noise/filler? (LOW tier)

    WSP 77: Phase 1 fast pattern matching before Qwen escalation
    """

    # Training-worthy keywords (boost to HIGH tier)
    HIGH_TIER_KEYWORDS = [
        "the key insight",
        "the truth is",
        "what I learned",
        "the real reason",
        "most people don't realize",
        "the secret is",
        "here's what nobody",
        "fundamentally",
        "paradigm shift",
        "singularity",
        "education must",
        "the future of",
    ]

    # Low-tier indicators (demote to LOW tier)
    LOW_TIER_KEYWORDS = [
        "um",
        "uh",
        "you know",
        "like I said",
        "anyway",
        "so yeah",
        "[music]",
        "[applause]",
        "[inaudible]",
    ]

    def __init__(self, model_path: Optional[Path] = None, use_gemma: bool = True):
        """
        Initialize segment classifier.

        Args:
            model_path: Path to Gemma GGUF model (default: E:/HoloIndex/models/)
            use_gemma: Enable Gemma validation (can be disabled for fast heuristic-only mode)
        """
        if model_path is None:
            model_path = Path("E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf")

        self.model_path = model_path
        self.use_gemma = use_gemma
        self.gemma_llm = None  # Lazy loaded

        logger.info(f"[GEMMA-SEGMENT] Classifier initialized (use_gemma={use_gemma})")

    def _initialize_gemma(self) -> bool:
        """
        Initialize Gemma 3 270M model via llama_cpp.

        Pattern from: gemma_validator.py lines 68-116
        """
        if not self.use_gemma:
            return False

        if self.gemma_llm is not None:
            return True

        try:
            from llama_cpp import Llama
            import os

            logger.info(f"[GEMMA-SEGMENT] Loading model from {self.model_path}")

            if not self.model_path.exists():
                logger.error(f"[GEMMA-SEGMENT] Model not found: {self.model_path}")
                return False

            # Suppress llama.cpp loading noise
            old_stdout, old_stderr = os.dup(1), os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)

            try:
                os.dup2(devnull, 1)
                os.dup2(devnull, 2)

                self.gemma_llm = Llama(
                    model_path=str(self.model_path),
                    n_ctx=512,  # Small context for binary classification
                    n_threads=2,  # Fast inference
                    n_gpu_layers=0,  # CPU-only for consistency
                    verbose=False
                )

            finally:
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stdout)
                os.close(old_stderr)

            logger.info("[GEMMA-SEGMENT] Model loaded successfully")
            return True

        except ImportError:
            logger.warning("[GEMMA-SEGMENT] llama_cpp not installed")
            return False
        except Exception as e:
            logger.error(f"[GEMMA-SEGMENT] Failed to load: {e}")
            return False

    def _gemma_inference(self, prompt: str) -> Optional[str]:
        """Run Gemma inference for binary classification."""
        if not self._initialize_gemma():
            return None

        start_time = datetime.now()

        try:
            response = self.gemma_llm(
                prompt,
                max_tokens=10,  # Just "YES" or "NO" or "0/1/2"
                temperature=0.0,  # Deterministic
                stop=["\n", "###"],
                echo=False
            )

            latency = int((datetime.now() - start_time).total_seconds() * 1000)

            if isinstance(response, dict) and 'choices' in response:
                text = response['choices'][0]['text'].strip()
            else:
                text = str(response).strip()

            logger.debug(f"[GEMMA-SEGMENT] Inference ({latency}ms): {text}")
            return text

        except Exception as e:
            logger.error(f"[GEMMA-SEGMENT] Inference failed: {e}")
            return None

    def _heuristic_classify(self, segment_text: str) -> Dict:
        """
        Fast heuristic classification (fallback when Gemma unavailable).

        Rule-based classification <5ms.
        """
        text_lower = segment_text.lower()
        word_count = len(segment_text.split())

        # Check for LOW tier indicators
        for keyword in self.LOW_TIER_KEYWORDS:
            if keyword in text_lower:
                return {
                    'tier': 0,
                    'confidence': 0.70,
                    'reason': f'Low tier: contains "{keyword}"'
                }

        # Too short = LOW tier
        if word_count < 5:
            return {
                'tier': 0,
                'confidence': 0.80,
                'reason': 'Too short (< 5 words)'
            }

        # Check for HIGH tier indicators
        for keyword in self.HIGH_TIER_KEYWORDS:
            if keyword in text_lower:
                return {
                    'tier': 2,
                    'confidence': 0.75,
                    'reason': f'High tier: contains insight keyword "{keyword}"'
                }

        # Longer segments with good structure = higher confidence regular
        if word_count >= 20:
            return {
                'tier': 1,
                'confidence': 0.70,
                'reason': 'Regular: substantive content'
            }

        # Default to REGULAR
        return {
            'tier': 1,
            'confidence': 0.60,
            'reason': 'Regular: standard content'
        }

    def _gemma_classify(self, segment_text: str, video_title: str) -> Optional[Dict]:
        """
        Gemma-based classification for borderline cases.

        Binary question: Is this segment training-worthy? (YES/NO)
        """
        if not self._initialize_gemma():
            return None

        prompt = f"""Rate this video transcript segment for AI training quality.
Is this segment clear, insightful, and worth using to train a digital twin?

Video: {video_title}
Segment: {segment_text}

Answer ONLY: YES (high quality) or NO (regular/low quality)
Rating:"""

        response = self._gemma_inference(prompt)

        if response:
            response_clean = response.strip().upper()

            if "YES" in response_clean:
                return {
                    'tier': 2,
                    'confidence': 0.85,
                    'reason': 'Gemma: training-worthy segment'
                }
            elif "NO" in response_clean:
                return {
                    'tier': 1,
                    'confidence': 0.75,
                    'reason': 'Gemma: regular quality'
                }

        return None

    def classify_segment(
        self,
        segment_text: str,
        video_title: str = "",
        speaker: str = "",
        timestamp: float = 0.0
    ) -> SegmentClassification:
        """
        Classify a video segment by quality tier.

        Two-phase classification (WSP 77):
        1. Heuristic pre-filter (<5ms)
        2. Gemma validation for borderline cases (<50ms)

        Args:
            segment_text: Transcript text of the segment
            video_title: Title of the source video
            speaker: Speaker identifier (e.g., "012")
            timestamp: Start time in seconds

        Returns:
            SegmentClassification with tier (0/1/2), confidence, and reason
        """
        start_time = datetime.now()

        # Phase 1: Heuristic pre-filter
        heuristic = self._heuristic_classify(segment_text)

        # If heuristic is confident, skip Gemma
        if heuristic['confidence'] >= 0.80:
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            return SegmentClassification(
                tier=heuristic['tier'],
                confidence=heuristic['confidence'],
                reason=heuristic['reason'],
                latency_ms=latency,
                is_training_worthy=(heuristic['tier'] >= 2)
            )

        # Phase 2: Gemma validation for borderline cases
        if self.use_gemma:
            gemma_result = self._gemma_classify(segment_text, video_title)

            if gemma_result:
                latency = int((datetime.now() - start_time).total_seconds() * 1000)
                return SegmentClassification(
                    tier=gemma_result['tier'],
                    confidence=gemma_result['confidence'],
                    reason=gemma_result['reason'],
                    latency_ms=latency,
                    is_training_worthy=(gemma_result['tier'] >= 2)
                )

        # Fallback to heuristic result
        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        return SegmentClassification(
            tier=heuristic['tier'],
            confidence=heuristic['confidence'],
            reason=heuristic['reason'],
            latency_ms=latency,
            is_training_worthy=(heuristic['tier'] >= 2)
        )

    def classify_batch(
        self,
        segments: List[Dict],
        video_title: str = ""
    ) -> List[SegmentClassification]:
        """
        Classify multiple segments in batch.

        Args:
            segments: List of segment dicts with 'text' key
            video_title: Source video title

        Returns:
            List of SegmentClassification results
        """
        results = []
        for seg in segments:
            text = seg.get('text', '') or seg.get('transcript', '')
            speaker = seg.get('speaker', '')
            timestamp = seg.get('start', 0.0)

            result = self.classify_segment(
                segment_text=text,
                video_title=video_title,
                speaker=speaker,
                timestamp=timestamp
            )
            results.append(result)

        # Log summary
        tier_counts = {0: 0, 1: 0, 2: 0}
        for r in results:
            tier_counts[r.tier] += 1

        logger.info(
            f"[GEMMA-SEGMENT] Batch classified {len(segments)} segments: "
            f"LOW={tier_counts[0]}, REGULAR={tier_counts[1]}, HIGH={tier_counts[2]}"
        )

        return results

    def get_training_worthy_segments(
        self,
        segments: List[Dict],
        video_title: str = ""
    ) -> List[Dict]:
        """
        Filter segments to only training-worthy (tier >= 2).

        Returns segments enriched with classification metadata.
        """
        classifications = self.classify_batch(segments, video_title)

        worthy = []
        for seg, cls in zip(segments, classifications):
            if cls.is_training_worthy:
                enriched = dict(seg)
                enriched['quality_tier'] = cls.tier
                enriched['quality_confidence'] = cls.confidence
                enriched['quality_reason'] = cls.reason
                worthy.append(enriched)

        logger.info(
            f"[GEMMA-SEGMENT] {len(worthy)}/{len(segments)} segments training-worthy"
        )

        return worthy


# =============================================================================
# Singleton Factory
# =============================================================================

_classifier_instance = None


def get_segment_classifier(model_path: Optional[Path] = None, use_gemma: bool = True) -> GemmaSegmentClassifier:
    """Get or create singleton segment classifier."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = GemmaSegmentClassifier(model_path=model_path, use_gemma=use_gemma)
    return _classifier_instance


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Gemma Segment Classifier Test")
    print("=" * 60)

    classifier = get_segment_classifier()

    test_segments = [
        {
            'text': "The key insight is that education must be democratized globally",
            'speaker': '012'
        },
        {
            'text': "Um, so yeah, anyway, like I was saying",
            'speaker': '012'
        },
        {
            'text': "The paradigm shift in education technology will enable every child access",
            'speaker': '012'
        },
        {
            'text': "Nice weather today",
            'speaker': 'other'
        },
        {
            'text': "The real reason most educational startups fail is they don't understand the singularity",
            'speaker': '012'
        },
    ]

    print("\n--- Individual Classification ---")
    for seg in test_segments:
        result = classifier.classify_segment(
            segment_text=seg['text'],
            video_title="Education Singularity",
            speaker=seg['speaker']
        )
        tier_label = ['LOW', 'REGULAR', 'HIGH'][result.tier]
        print(f"[{tier_label}] ({result.confidence:.2f}, {result.latency_ms}ms): {seg['text'][:50]}...")
        print(f"       Reason: {result.reason}")

    print("\n--- Batch Classification ---")
    results = classifier.classify_batch(test_segments, "Education Singularity")
    print(f"Total: {len(results)} segments")

    print("\n--- Training-Worthy Filter ---")
    worthy = classifier.get_training_worthy_segments(test_segments, "Education Singularity")
    print(f"Training-worthy: {len(worthy)}/{len(test_segments)}")
    for w in worthy:
        print(f"  - {w['text'][:60]}...")
