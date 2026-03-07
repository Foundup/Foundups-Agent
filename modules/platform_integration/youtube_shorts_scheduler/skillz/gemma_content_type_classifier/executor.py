#!/usr/bin/env python3
"""
Gemma Content Type Classifier - Skill Executor

AI-driven content type classification for YouTube Shorts scheduling.
Replaces static description_template config with dynamic classification.

WSP Compliance:
    WSP 95: SKILLz Wardrobe Protocol (micro chain-of-thought)
    WSP 77: Agent Coordination (Gemma fast path, Qwen fallback)
    WSP 27: Phase 0 KNOWLEDGE (classification before action)

Usage:
    from .executor import classify_content
    result = classify_content(title="FFCPLN Anthem", channel="move2japan")
    template = result["description_template"]
"""

import re
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type taxonomy for description template selection."""
    FFCPLN_MUSIC = "ffcpln_music"
    FFCPLN_NEWS = "ffcpln_news"
    STARTUP_TECH = "startup_tech"
    MINDFULNESS = "mindfulness"
    PERSONAL_VLOG = "personal_vlog"


@dataclass
class ClassificationResult:
    """Result of content type classification."""
    content_type: ContentType
    description_template: str
    confidence: float
    method: str
    patterns: Dict[str, bool]
    channel_key: str


# Channel -> baseline template mapping
CHANNEL_BASELINES = {
    "move2japan": ("ffcpln", ContentType.FFCPLN_MUSIC),
    "antifafm": ("ffcpln", ContentType.FFCPLN_MUSIC),
    "foundups": ("foundups", ContentType.STARTUP_TECH),
    "undaodu": ("undaodu", ContentType.MINDFULNESS),
}

# FFCPLN markers (Suno AI song lyrics + hashtags)
FFCPLN_MARKERS = [
    r"\bffcpln\b",
    r"#ffcpln",
    r"fake\s*f[u\*]+ck\s*christian",
    r"pedo[_\s-]*lov[ie]n['\s]*nazi",
    r"christian\s*pedo",
]

# News/protest markers
NEWS_MARKERS = [
    r"\bbreaking\b",
    r"\bexposed\b",
    r"\bleaked\b",
    r"\bice\s*raid",
    r"\bdeportation\b",
    r"\bprotest\b",
    r"\barrest\b",
    r"\bcruelty\b",
    r"\bimmigration\b",
]

# Startup/tech markers
STARTUP_MARKERS = [
    r"\bstartup\b",
    r"\bentrepreneur",
    r"\bfounder\b",
    r"\bventure\b",
    r"\bpavs\b",
    r"\bautonomous\b",
    r"\bagent\b",
    r"\binnovation\b",
]

# Mindfulness markers
MINDFULNESS_MARKERS = [
    r"\bmindfulness\b",
    r"\bmeditation\b",
    r"\bzen\b",
    r"\bpeace\b",
    r"\btao\b",
    r"\bdao\b",
    r"\bwu\s*wei\b",
    r"\bnon[_\s-]*doing\b",
    r"\bbreathe\b",
    r"\bcalm\b",
    r"\bpresent\b",
]


def _check_markers(text: str, markers: List[str]) -> int:
    """Count marker matches in text (case-insensitive)."""
    if not text:
        return 0
    text_lower = text.lower()
    return sum(1 for m in markers if re.search(m, text_lower, re.IGNORECASE))


def classify_content(
    title: str,
    channel: str,
    metadata: Optional[Dict[str, Any]] = None,
    transcript: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Classify video content and select appropriate description template.

    This is the main skill executor - implements micro chain-of-thought pattern
    from WSP 95 with pattern tracking at each step.

    Args:
        title: Video title
        channel: Channel key (move2japan, undaodu, foundups, antifafm)
        metadata: Optional index artifact with audio/visual analysis
        transcript: Optional transcript text (from index or separate)

    Returns:
        Classification result dict with:
        - content_type: The detected content type
        - description_template: Template key for get_standard_description()
        - confidence: 0.0-1.0 confidence score
        - method: Which detection step triggered classification
        - patterns: Pattern fidelity tracking dict
    """
    # Initialize pattern tracking (WSP 95 fidelity scoring)
    patterns = {
        "channel_baseline_set": False,
        "ffcpln_marker_check": False,
        "news_marker_check": False,
        "startup_marker_check": False,
        "mindfulness_marker_check": False,
        "fallback_applied": False,
        "specific_classification": False,
    }

    # Extract transcript from metadata if not provided
    if transcript is None and metadata:
        audio = metadata.get("audio") or {}
        transcript = audio.get("transcript_summary") or ""

    # Combine searchable text
    combined_text = f"{title} {transcript or ''}"

    # === Step 1: CHANNEL_IDENTITY_CHECK ===
    channel_lower = channel.lower() if channel else ""
    baseline_template, baseline_type = CHANNEL_BASELINES.get(
        channel_lower, ("ffcpln", ContentType.FFCPLN_MUSIC)
    )
    patterns["channel_baseline_set"] = True
    logger.debug(f"[SKILL] Channel baseline: {channel_lower} -> {baseline_template}")

    # === Step 2: FFCPLN_MARKER_DETECTION ===
    ffcpln_score = _check_markers(combined_text, FFCPLN_MARKERS)
    patterns["ffcpln_marker_check"] = True

    if ffcpln_score >= 1:
        patterns["specific_classification"] = True
        logger.info(f"[SKILL] FFCPLN marker detected (score={ffcpln_score})")
        return _build_result(
            content_type=ContentType.FFCPLN_MUSIC,
            template="ffcpln",
            confidence=min(0.95, 0.7 + ffcpln_score * 0.1),
            method="ffcpln_marker_detection",
            patterns=patterns,
            channel=channel_lower,
        )

    # === Step 3: NEWS_PROTEST_DETECTION ===
    news_score = _check_markers(combined_text, NEWS_MARKERS)
    patterns["news_marker_check"] = True

    if news_score >= 2 and channel_lower in ["move2japan", "antifafm"]:
        patterns["specific_classification"] = True
        logger.info(f"[SKILL] News/protest detected (score={news_score})")
        return _build_result(
            content_type=ContentType.FFCPLN_NEWS,
            template="ffcpln",  # Still uses FFCPLN template but with ICE news hooks
            confidence=min(0.90, 0.6 + news_score * 0.1),
            method="news_protest_detection",
            patterns=patterns,
            channel=channel_lower,
        )

    # === Step 4: STARTUP_TECH_DETECTION ===
    startup_score = _check_markers(combined_text, STARTUP_MARKERS)
    patterns["startup_marker_check"] = True

    if startup_score >= 1 and channel_lower == "foundups":
        patterns["specific_classification"] = True
        logger.info(f"[SKILL] Startup/tech detected (score={startup_score})")
        return _build_result(
            content_type=ContentType.STARTUP_TECH,
            template="foundups",
            confidence=min(0.90, 0.7 + startup_score * 0.1),
            method="startup_tech_detection",
            patterns=patterns,
            channel=channel_lower,
        )

    # === Step 5: MINDFULNESS_DETECTION ===
    mindfulness_score = _check_markers(combined_text, MINDFULNESS_MARKERS)
    patterns["mindfulness_marker_check"] = True

    if mindfulness_score >= 1 and channel_lower == "undaodu":
        patterns["specific_classification"] = True
        logger.info(f"[SKILL] Mindfulness detected (score={mindfulness_score})")
        return _build_result(
            content_type=ContentType.MINDFULNESS,
            template="undaodu",
            confidence=min(0.90, 0.7 + mindfulness_score * 0.1),
            method="mindfulness_detection",
            patterns=patterns,
            channel=channel_lower,
        )

    # === Step 6: FALLBACK_CLASSIFICATION ===
    patterns["fallback_applied"] = True
    logger.info(f"[SKILL] Fallback to channel baseline: {baseline_template}")

    return _build_result(
        content_type=baseline_type,
        template=baseline_template,
        confidence=0.60,  # Lower confidence for fallback
        method="channel_baseline_fallback",
        patterns=patterns,
        channel=channel_lower,
    )


def _build_result(
    content_type: ContentType,
    template: str,
    confidence: float,
    method: str,
    patterns: Dict[str, bool],
    channel: str,
) -> Dict[str, Any]:
    """Build standardized classification result dict."""
    return {
        "content_type": content_type.value,
        "description_template": template,
        "confidence": round(confidence, 3),
        "method": method,
        "patterns": patterns,
        "channel_key": channel,
    }


def get_pattern_fidelity(patterns: Dict[str, bool]) -> float:
    """
    Calculate pattern fidelity score for WSP 95 metrics.

    Fidelity = patterns_executed / total_patterns
    """
    if not patterns:
        return 0.0

    executed = sum(1 for v in patterns.values() if v)
    total = len(patterns)

    return round(executed / total, 3) if total > 0 else 0.0


# Convenience function for direct CLI/test usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        title = sys.argv[1]
        channel = sys.argv[2]
        result = classify_content(title=title, channel=channel)
        print(f"Content Type: {result['content_type']}")
        print(f"Template: {result['description_template']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Method: {result['method']}")
        print(f"Fidelity: {get_pattern_fidelity(result['patterns'])}")
    else:
        print("Usage: python executor.py <title> <channel>")
        print("Example: python executor.py '#FFCPLN Anthem' move2japan")
