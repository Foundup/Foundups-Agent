"""
Clip Generator - Generate clip candidates for short-form content.

WSP Compliance:
    - WSP 72: Module Independence
    - WSP 27: DAE Architecture (clip extraction pipeline)
    - WSP 91: DAE Observability (telemetry integration)

Purpose:
    Extract potential short-form clips (15-60s) from longer videos.
    Score clips for viral potential and generate metadata for
    YouTube Shorts scheduling pipeline.

Integration:
    - Receives multimodal moments from MultimodalAligner
    - Outputs clip candidates for YouTube Shorts scheduling
"""

import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ClipCandidate:
    """
    Potential clip for short-form content.
    """
    clip_id: str
    source_video: str
    start_time: float
    end_time: float
    duration: float
    hook: str  # Opening line/visual
    title_suggestion: str
    description_suggestion: str
    virality_score: float  # 0-1
    moments: List[dict] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class ClipGeneratorResult:
    """Complete clip generation result for video_indexer pipeline."""
    candidates: List[ClipCandidate]
    total_candidates: int
    avg_virality: float
    best_candidate: Optional[ClipCandidate] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for pipeline consumption."""
        return {
            "candidates": [asdict(c) for c in self.candidates],
            "total_candidates": self.total_candidates,
            "avg_virality": self.avg_virality,
            "best_candidate": asdict(self.best_candidate) if self.best_candidate else None,
        }


# =============================================================================
# Clip Generator
# =============================================================================

class ClipGenerator:
    """
    Generate clip candidates from video moments.

    Identifies segments with high engagement potential and
    packages them for short-form content creation.

    Example:
        >>> generator = ClipGenerator()
        >>> candidates = generator.generate_candidates(moments)
        >>> for clip in candidates:
        ...     print(f"{clip.title_suggestion}: {clip.virality_score:.2f}")
    """

    def __init__(
        self,
        min_duration: float = 15.0,
        max_duration: float = 60.0,
        min_virality: float = 0.6,
    ):
        """
        Initialize clip generator.

        Args:
            min_duration: Minimum clip duration in seconds
            max_duration: Maximum clip duration in seconds
            min_virality: Minimum virality score to include
        """
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.min_virality = min_virality

        logger.info(
            f"[CLIP-GENERATOR] Initialized (duration={min_duration}-{max_duration}s, "
            f"min_virality={min_virality})"
        )

    def generate_clips(
        self,
        multimodal_data: Dict,
        video_id: str,
    ) -> ClipGeneratorResult:
        """
        Main entry point for video_indexer pipeline.

        Generates clip candidates from multimodal alignment data.

        Args:
            multimodal_data: Dict with moments and highlights from MultimodalAligner
            video_id: Source video ID

        Returns:
            ClipGeneratorResult with candidates and metrics
        """
        logger.info(f"[CLIP-GENERATOR] Generating clips for {video_id}...")

        # Extract moments from multimodal data
        moments = multimodal_data.get("moments", [])

        # Generate candidates
        candidates = self.generate_candidates(moments, video_id)

        # Calculate metrics
        avg_virality = (
            sum(c.virality_score for c in candidates) / len(candidates)
            if candidates
            else 0
        )
        best_candidate = candidates[0] if candidates else None

        result = ClipGeneratorResult(
            candidates=candidates,
            total_candidates=len(candidates),
            avg_virality=avg_virality,
            best_candidate=best_candidate,
        )

        logger.info(
            f"[CLIP-GENERATOR] Generated {len(candidates)} clips, "
            f"avg virality={avg_virality:.2f}"
        )
        return result

    def generate_candidates(
        self,
        moments: List[dict],
        video_id: str = "unknown",
    ) -> List[ClipCandidate]:
        """
        Generate clip candidates from moments.

        Args:
            moments: List of aligned moments with engagement scores
            video_id: Source video ID

        Returns:
            List of ClipCandidate objects sorted by virality
        """
        logger.info(f"[CLIP-GENERATOR] Generating candidates from {len(moments)} moments")

        if not moments:
            return []

        candidates = []
        clip_idx = 0

        # Strategy 1: Single high-engagement moments
        for moment in moments:
            duration = moment.get("duration", 0)
            engagement = moment.get("engagement_score", 0)

            if self.min_duration <= duration <= self.max_duration:
                virality = self._score_virality(moment)
                if virality >= self.min_virality:
                    clip_idx += 1
                    candidates.append(
                        self._create_candidate(
                            clip_idx=clip_idx,
                            video_id=video_id,
                            moments=[moment],
                            virality=virality,
                        )
                    )

        # Strategy 2: Combine adjacent high-engagement moments
        combined = self._combine_adjacent_moments(moments, video_id, clip_idx)
        candidates.extend(combined)

        # Sort by virality score
        candidates.sort(key=lambda c: c.virality_score, reverse=True)

        logger.info(f"[CLIP-GENERATOR] Generated {len(candidates)} candidates")
        return candidates

    def _score_virality(self, moment: dict) -> float:
        """
        Score moment for viral potential.

        Factors:
        - Engagement score (from multimodal aligner)
        - Hook strength (opening line)
        - Duration (optimal: 30-45s)
        - Question/answer pattern
        """
        base_score = moment.get("engagement_score", 0.5)

        # Duration bonus (30-45s is optimal for Shorts)
        duration = moment.get("duration", 0)
        if 30 <= duration <= 45:
            base_score += 0.1
        elif duration < 20 or duration > 55:
            base_score -= 0.1

        # Hook bonus
        audio = moment.get("audio_content", "").lower()
        strong_hooks = [
            "here's what nobody",
            "the truth is",
            "most people don't know",
            "watch what happens",
            "you won't believe",
        ]
        for hook in strong_hooks:
            if hook in audio:
                base_score += 0.15
                break

        # Question pattern bonus
        if "?" in moment.get("audio_content", ""):
            base_score += 0.05

        return min(max(base_score, 0), 1.0)

    def _combine_adjacent_moments(
        self,
        moments: List[dict],
        video_id: str,
        start_idx: int,
    ) -> List[ClipCandidate]:
        """Combine adjacent moments into longer clips."""
        candidates = []

        if len(moments) < 2:
            return candidates

        clip_idx = start_idx

        # Try combining 2-3 adjacent moments
        for i in range(len(moments) - 1):
            combined_duration = 0
            combined_moments = []

            for j in range(i, min(i + 3, len(moments))):
                moment = moments[j]
                combined_duration += moment.get("duration", 0)
                combined_moments.append(moment)

                if self.min_duration <= combined_duration <= self.max_duration:
                    avg_engagement = sum(
                        m.get("engagement_score", 0) for m in combined_moments
                    ) / len(combined_moments)

                    if avg_engagement >= 0.5:
                        virality = avg_engagement * 0.9  # Slight penalty for combining
                        if virality >= self.min_virality:
                            clip_idx += 1
                            candidates.append(
                                self._create_candidate(
                                    clip_idx=clip_idx,
                                    video_id=video_id,
                                    moments=combined_moments,
                                    virality=virality,
                                )
                            )

                if combined_duration > self.max_duration:
                    break

        return candidates

    def _create_candidate(
        self,
        clip_idx: int,
        video_id: str,
        moments: List[dict],
        virality: float,
    ) -> ClipCandidate:
        """Create ClipCandidate from moments."""
        start_time = moments[0].get("start_time", 0)
        end_time = moments[-1].get("end_time", 0)

        # Extract hook from first moment
        first_audio = moments[0].get("audio_content", "")
        hook = first_audio[:100] if first_audio else "Watch this..."

        # Generate title
        title = self._generate_title(moments)

        # Generate description
        description = self._generate_description(moments)

        # Extract tags
        tags = self._extract_tags(moments)

        return ClipCandidate(
            clip_id=f"{video_id}_clip_{clip_idx:03d}",
            source_video=video_id,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            hook=hook,
            title_suggestion=title,
            description_suggestion=description,
            virality_score=virality,
            moments=[
                {
                    "start": m.get("start_time", 0),
                    "end": m.get("end_time", 0),
                    "content": m.get("audio_content", "")[:50],
                }
                for m in moments
            ],
            tags=tags,
        )

    def _generate_title(self, moments: List[dict]) -> str:
        """Generate title from moments."""
        # Use first strong statement or question
        for moment in moments:
            audio = moment.get("audio_content", "")
            if "?" in audio:
                # Use question as title
                idx = audio.find("?")
                return audio[: idx + 1][:80]
            elif any(h in audio.lower() for h in ["here's", "truth", "secret"]):
                # Use hook phrase
                return audio[:80]

        # Default: first 60 chars
        first_audio = moments[0].get("audio_content", "") if moments else ""
        return first_audio[:60] + "..." if len(first_audio) > 60 else first_audio

    def _generate_description(self, moments: List[dict]) -> str:
        """Generate description from moments."""
        all_text = " ".join(m.get("audio_content", "") for m in moments)
        return all_text[:200] + "..." if len(all_text) > 200 else all_text

    def _extract_tags(self, moments: List[dict]) -> List[str]:
        """Extract relevant tags from moments."""
        # TODO: Implement proper keyword extraction
        tags = ["shorts", "viral"]

        all_text = " ".join(m.get("audio_content", "") for m in moments).lower()

        # Topic-based tags
        if "japan" in all_text:
            tags.append("japan")
        if "visa" in all_text:
            tags.append("visa")
        if "business" in all_text:
            tags.append("business")

        return tags


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Clip Generator Test")
    print("=" * 60)

    generator = ClipGenerator(min_duration=10, max_duration=60, min_virality=0.5)

    # Test data
    moments = [
        {
            "start_time": 0,
            "end_time": 25,
            "duration": 25,
            "audio_content": "Here's what nobody tells you about starting a business in Japan.",
            "engagement_score": 0.8,
        },
        {
            "start_time": 25,
            "end_time": 45,
            "duration": 20,
            "audio_content": "The visa process is actually much simpler than people think.",
            "engagement_score": 0.6,
        },
        {
            "start_time": 45,
            "end_time": 70,
            "duration": 25,
            "audio_content": "Most people don't know this secret that saved me months!",
            "engagement_score": 0.85,
        },
    ]

    candidates = generator.generate_candidates(moments, video_id="test_video")
    print(f"Generated {len(candidates)} candidates:")

    for clip in candidates:
        print(f"\n  {clip.clip_id}:")
        print(f"    Duration: {clip.duration:.1f}s")
        print(f"    Virality: {clip.virality_score:.2f}")
        print(f"    Title: {clip.title_suggestion[:50]}...")
        print(f"    Tags: {clip.tags}")
