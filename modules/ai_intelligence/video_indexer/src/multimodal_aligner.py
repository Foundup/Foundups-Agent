"""
Multimodal Aligner - Cross-modal alignment for audio + visual moments.

WSP Compliance:
    - WSP 72: Module Independence
    - WSP 77: Agent Coordination (embedding alignment)

Purpose:
    Synchronize audio content (transcript segments) with visual content
    (shots, keyframes) to create unified "moments" that capture the
    full context of video content.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Moment:
    """
    Aligned audio-visual moment in video.

    A moment represents a coherent segment where audio and visual
    content are synchronized and meaningful together.
    """
    start_time: float
    end_time: float
    duration: float
    audio_content: str
    visual_description: str
    engagement_score: float  # 0-1
    speaker: Optional[str] = None
    shot_type: Optional[str] = None  # "closeup", "wide", "medium"


@dataclass
class Highlight:
    """
    High-engagement moment suitable for clips/highlights.
    """
    moment: Moment
    highlight_type: str  # "quote", "reaction", "visual_peak"
    confidence: float
    suggested_title: Optional[str] = None


# =============================================================================
# Multimodal Aligner
# =============================================================================

class MultimodalAligner:
    """
    Cross-modal alignment: sync audio moments with visual content.

    Example:
        >>> aligner = MultimodalAligner()
        >>> moments = aligner.align_moments(audio_result, visual_result)
        >>> highlights = aligner.detect_highlights(moments)
    """

    def __init__(
        self,
        alignment_tolerance: float = 0.5,
        min_moment_duration: float = 3.0,
    ):
        """
        Initialize aligner.

        Args:
            alignment_tolerance: Seconds tolerance for time alignment
            min_moment_duration: Minimum moment length in seconds
        """
        self.alignment_tolerance = alignment_tolerance
        self.min_moment_duration = min_moment_duration

        logger.info(f"[MULTIMODAL-ALIGNER] Initialized (tolerance={alignment_tolerance}s)")

    def align_moments(
        self,
        audio_segments: List[dict],
        visual_shots: List[dict],
    ) -> List[Moment]:
        """
        Align audio and visual content into moments.

        Args:
            audio_segments: List of transcript segments with timestamps
            visual_shots: List of shot boundaries with timestamps

        Returns:
            List of aligned Moment objects
        """
        logger.info("[MULTIMODAL-ALIGNER] Aligning audio and visual moments...")

        if not audio_segments:
            logger.warning("[MULTIMODAL-ALIGNER] No audio segments provided")
            return []

        moments = []

        for segment in audio_segments:
            seg_start = segment.get("start_time", 0)
            seg_end = segment.get("end_time", 0)
            seg_text = segment.get("text", "")

            # Find overlapping visual shots
            visual_desc = self._find_visual_context(seg_start, seg_end, visual_shots)

            # Calculate engagement score
            engagement = self._calculate_engagement(seg_text, visual_desc)

            moment = Moment(
                start_time=seg_start,
                end_time=seg_end,
                duration=seg_end - seg_start,
                audio_content=seg_text,
                visual_description=visual_desc,
                engagement_score=engagement,
                speaker=segment.get("speaker"),
            )

            if moment.duration >= self.min_moment_duration:
                moments.append(moment)

        logger.info(f"[MULTIMODAL-ALIGNER] Created {len(moments)} moments")
        return moments

    def _find_visual_context(
        self,
        start_time: float,
        end_time: float,
        visual_shots: List[dict],
    ) -> str:
        """Find visual context for time range."""
        if not visual_shots:
            return "no visual data"

        # Find shots that overlap with time range
        overlapping = []
        for shot in visual_shots:
            shot_start = shot.get("start_time", 0)
            shot_end = shot.get("end_time", 0)

            # Check for overlap
            if shot_start <= end_time and shot_end >= start_time:
                overlapping.append(shot)

        if not overlapping:
            return "cut away"

        # Describe the visual context
        descriptions = []
        for shot in overlapping:
            desc = shot.get("description", f"shot at {shot.get('start_time', 0):.1f}s")
            descriptions.append(desc)

        return "; ".join(descriptions)

    def _calculate_engagement(self, audio: str, visual: str) -> float:
        """
        Calculate engagement score based on content.

        Heuristic scoring:
        - Strong audio hooks increase score
        - Visual variety increases score
        - Face presence increases score
        """
        score = 0.5  # Base score

        # Audio engagement factors
        hook_phrases = [
            "here's what", "the truth is", "nobody tells you",
            "the secret is", "most people don't", "watch this",
        ]
        audio_lower = audio.lower()
        for phrase in hook_phrases:
            if phrase in audio_lower:
                score += 0.1
                break

        # Question mark indicates engagement
        if "?" in audio:
            score += 0.05

        # Exclamation indicates energy
        if "!" in audio:
            score += 0.05

        # Visual engagement factors
        if "face" in visual.lower():
            score += 0.1
        if "closeup" in visual.lower():
            score += 0.05

        return min(score, 1.0)

    def detect_highlights(
        self,
        moments: List[Moment],
        min_score: float = 0.7,
    ) -> List[Highlight]:
        """
        Detect high-engagement moments worthy of highlights.

        Args:
            moments: List of aligned moments
            min_score: Minimum engagement score for highlight

        Returns:
            List of Highlight objects
        """
        logger.info(f"[MULTIMODAL-ALIGNER] Detecting highlights (min_score={min_score})...")

        highlights = []

        for moment in moments:
            if moment.engagement_score >= min_score:
                highlight_type = self._classify_highlight(moment)
                highlights.append(
                    Highlight(
                        moment=moment,
                        highlight_type=highlight_type,
                        confidence=moment.engagement_score,
                        suggested_title=self._generate_title(moment),
                    )
                )

        logger.info(f"[MULTIMODAL-ALIGNER] Found {len(highlights)} highlights")
        return highlights

    def _classify_highlight(self, moment: Moment) -> str:
        """Classify what type of highlight this is."""
        audio = moment.audio_content.lower()

        if any(phrase in audio for phrase in ["here's what", "the truth is", "secret"]):
            return "quote"
        elif "!" in moment.audio_content:
            return "reaction"
        elif "face" in moment.visual_description.lower():
            return "talking_head"
        else:
            return "general"

    def _generate_title(self, moment: Moment) -> Optional[str]:
        """Generate suggested title for highlight."""
        # Simple title extraction from first sentence
        audio = moment.audio_content
        if len(audio) > 50:
            # Find first sentence
            for end in [".", "!", "?"]:
                idx = audio.find(end)
                if 0 < idx < 80:
                    return audio[: idx + 1]
            return audio[:50] + "..."
        return audio if audio else None


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Multimodal Aligner Test")
    print("=" * 60)

    aligner = MultimodalAligner()

    # Test data
    audio_segments = [
        {"start_time": 0, "end_time": 5, "text": "Here's what nobody tells you about Japan."},
        {"start_time": 5, "end_time": 10, "text": "The visa process is actually simple."},
        {"start_time": 10, "end_time": 15, "text": "Most people don't know this secret!"},
    ]

    visual_shots = [
        {"start_time": 0, "end_time": 7, "description": "face closeup"},
        {"start_time": 7, "end_time": 15, "description": "document on screen"},
    ]

    moments = aligner.align_moments(audio_segments, visual_shots)
    print(f"Aligned moments: {len(moments)}")

    for m in moments:
        print(f"  [{m.start_time:.1f}-{m.end_time:.1f}] {m.audio_content[:40]}... (score={m.engagement_score:.2f})")

    highlights = aligner.detect_highlights(moments, min_score=0.6)
    print(f"Highlights: {len(highlights)}")
