# -*- coding: utf-8 -*-
"""
Transcript Validator - Gemma-based STT correction.

Uses video metadata and channel vocabulary to correct STT errors.

WSP Compliance:
    WSP 77: Agent Coordination (Gemma for fast validation)
    WSP 91: DAE Observability
"""
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CorrectionResult:
    """Result of transcript correction."""
    original_text: str
    corrected_text: str
    corrections: List[Dict[str, str]]  # [{original, corrected, confidence}]
    confidence: float


class TranscriptValidator:
    """
    Validate and correct STT transcripts using context.
    
    Uses:
    1. Video title - extract proper nouns
    2. Channel vocabulary - known terms
    3. Pattern matching - fuzzy matches
    4. Optional: Gemma for complex corrections
    """
    
    def __init__(
        self,
        vocabulary_dir: str = "memory/vocabulary",
        use_gemma: bool = False,
    ):
        """
        Initialize validator.
        
        Args:
            vocabulary_dir: Directory containing vocabulary JSONs
            use_gemma: Whether to use Gemma for complex corrections
        """
        self.vocabulary_dir = Path(vocabulary_dir)
        self.use_gemma = use_gemma
        self.vocabularies: Dict[str, Dict] = {}
        
        # Load all vocabularies
        self._load_vocabularies()
    
    def _load_vocabularies(self):
        """Load all channel vocabularies."""
        if not self.vocabulary_dir.exists():
            logger.warning(f"[VALIDATOR] Vocabulary dir not found: {self.vocabulary_dir}")
            return
        
        for vocab_file in self.vocabulary_dir.glob("*.json"):
            try:
                data = json.loads(vocab_file.read_text(encoding="utf-8"))
                channel = data.get("channel", vocab_file.stem)
                self.vocabularies[channel] = data
                logger.info(f"[VALIDATOR] Loaded vocabulary for: {channel}")
            except Exception as e:
                logger.warning(f"[VALIDATOR] Failed to load {vocab_file}: {e}")
    
    def extract_proper_nouns_from_title(self, title: str) -> List[str]:
        """
        Extract proper nouns from video title.
        
        Strategy:
        - Words starting with capitals
        - URLs/domains
        - Known patterns
        """
        proper_nouns = []
        
        # Extract capitalized words (excluding common words)
        common_words = {"The", "A", "An", "Is", "Are", "In", "On", "For", "To", "And", "Or", "Of"}
        words = re.findall(r'\b[A-Z][a-zA-Z0-9]*(?:\.[a-zA-Z]+)?\b', title)
        for word in words:
            if word not in common_words:
                proper_nouns.append(word)
        
        # Extract URLs/domains
        domains = re.findall(r'\b[\w]+\.(?:org|com|net|io|edu)\b', title, re.IGNORECASE)
        proper_nouns.extend(domains)
        
        return list(set(proper_nouns))
    
    def correct_segment(
        self,
        text: str,
        channel: str = "undaodu",
        video_title: str = "",
    ) -> CorrectionResult:
        """
        Correct a single transcript segment.
        
        Args:
            text: STT text to correct
            channel: Channel name for vocabulary lookup
            video_title: Video title for context
            
        Returns:
            CorrectionResult with corrections applied
        """
        corrections = []
        corrected_text = text
        
        # Get vocabulary for channel
        vocab = self.vocabularies.get(channel, {})
        mishearings = vocab.get("common_mishearings", {})
        proper_nouns = vocab.get("proper_nouns", [])
        
        # Add proper nouns from title
        title_nouns = self.extract_proper_nouns_from_title(video_title)
        
        # Step 1: Direct replacement of known mishearings
        for misheard, correct in mishearings.items():
            pattern = re.compile(re.escape(misheard), re.IGNORECASE)
            if pattern.search(corrected_text):
                old_text = corrected_text
                corrected_text = pattern.sub(correct, corrected_text)
                corrections.append({
                    "original": misheard,
                    "corrected": correct,
                    "confidence": 0.95,
                    "method": "vocabulary_lookup"
                })
                logger.debug(f"[VALIDATOR] Corrected '{misheard}' → '{correct}'")
        
        # Step 2: Case correction for proper nouns
        for noun in proper_nouns + title_nouns:
            # Find case-insensitive matches
            pattern = re.compile(re.escape(noun), re.IGNORECASE)
            matches = pattern.findall(corrected_text)
            for match in matches:
                if match != noun:  # Wrong case
                    corrected_text = corrected_text.replace(match, noun)
                    corrections.append({
                        "original": match,
                        "corrected": noun,
                        "confidence": 0.9,
                        "method": "case_correction"
                    })
        
        # Calculate overall confidence
        confidence = 1.0 if not corrections else min(c["confidence"] for c in corrections)
        
        return CorrectionResult(
            original_text=text,
            corrected_text=corrected_text,
            corrections=corrections,
            confidence=confidence
        )
    
    async def correct_transcript(
        self,
        segments: List[Dict[str, Any]],
        channel: str = "undaodu",
        video_title: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Correct all segments in a transcript.
        
        Args:
            segments: List of transcript segments with "text" field
            channel: Channel name
            video_title: Video title for context
            
        Returns:
            Corrected segments
        """
        corrected_segments = []
        total_corrections = 0
        
        for segment in segments:
            text = segment.get("text", "")
            result = self.correct_segment(text, channel, video_title)
            
            corrected_segment = segment.copy()
            corrected_segment["text"] = result.corrected_text
            
            if result.corrections:
                corrected_segment["_corrections"] = result.corrections
                total_corrections += len(result.corrections)
            
            corrected_segments.append(corrected_segment)
        
        logger.info(f"[VALIDATOR] Made {total_corrections} corrections across {len(segments)} segments")
        return corrected_segments
    
    def add_to_vocabulary(
        self,
        channel: str,
        proper_noun: Optional[str] = None,
        mishearing: Optional[Tuple[str, str]] = None,
    ):
        """
        Add new term to vocabulary (recursive improvement).
        
        Args:
            channel: Channel name
            proper_noun: New proper noun to add
            mishearing: Tuple of (misheard, correct)
        """
        if channel not in self.vocabularies:
            self.vocabularies[channel] = {
                "channel": channel,
                "proper_nouns": [],
                "common_mishearings": {}
            }
        
        vocab = self.vocabularies[channel]
        
        if proper_noun and proper_noun not in vocab.get("proper_nouns", []):
            vocab.setdefault("proper_nouns", []).append(proper_noun)
            logger.info(f"[VALIDATOR] Added proper noun: {proper_noun}")
        
        if mishearing:
            misheard, correct = mishearing
            vocab.setdefault("common_mishearings", {})[misheard] = correct
            logger.info(f"[VALIDATOR] Added mishearing: {misheard} → {correct}")
        
        # Save vocabulary
        vocab_path = self.vocabulary_dir / f"{channel}.json"
        vocab_path.write_text(json.dumps(vocab, indent=2, ensure_ascii=False), encoding="utf-8")


# Convenience function for SKILLz integration
async def validate_transcript_segments(
    segments: List[Dict],
    channel: str = "undaodu",
    video_title: str = "",
) -> List[Dict]:
    """
    Validate and correct transcript segments.
    
    Used by transcript_ask SKILLz.
    """
    validator = TranscriptValidator()
    return await validator.correct_transcript(segments, channel, video_title)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test correction
    validator = TranscriptValidator()
    
    test_text = "I'm the founder of edu.org education using information technology"
    result = validator.correct_segment(
        test_text,
        channel="undaodu",
        video_title="2009 Educational Singularity Vision - EDUIT.org"
    )
    
    print(f"Original: {result.original_text}")
    print(f"Corrected: {result.corrected_text}")
    print(f"Corrections: {result.corrections}")
