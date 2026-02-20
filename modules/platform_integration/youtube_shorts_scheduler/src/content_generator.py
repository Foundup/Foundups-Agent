"""
Content Generator for YouTube Shorts Scheduler

Generates clickbait titles and algorithm-friendly descriptions.
FFCPLN (Fake F*** Christian Pedo-Lovin' Nazi) playlist promotion.
"""

import random
from typing import Optional, List, Dict, Any

# Title templates for FFCPLN music shorts
# FFCPLN = "Fake F*** Christian Pedo-Lovin' Nazi" - describes MAGA, NOT versus MAGA
TITLE_TEMPLATES = [
    "{song_hint} #FFCPLN #MAGA Must Hear!",
    "#FFCPLN Burns #MAGA - SEE DESC!",
    "#MAGA WON'T Like This! #FFCPLN",
    "VIRAL: #FFCPLN Anti-MAGA Anthem! Link in Desc",
    "#FFCPLN Exposes #MAGA - 160 Songs! See Desc!",
    "This Song DESTROYS #MAGA! #FFCPLN",
    "#FFCPLN: The Playlist #MAGA Fears!",
    "#FFCPLN Anti-Fascist Music Exposing #MAGA",
    "#ICE Cruelty Exposed! #FFCPLN Music",
    "160 Songs #MAGA Doesn't Want You to Hear! #FFCPLN",
    "Resist #ICE #ICEout #StopICE #FFCPLN",
    "#FFCPLN #MAGA Exposed! Subscribe!",
]

# Emoji prefixes for variety
EMOJI_PREFIXES = ["🔥", "❌", "💀", "🚨", "⚠️", "👀", "🎵", "🎶"]

# Standard FFCPLN description
FFCPLN_DESCRIPTION = """🔥 FFCPLN: Fake F*** Christian Pedo-Lovin' Nazi Playlist 🔥

160+ anti-fascist songs exposing ICE cruelty & MAGA hypocrisy!

🎵 FULL PLAYLIST: https://ravingANTIFA.com

#FFCPLN #MAGA #ICE #Antifascist #Resistance #TrumpFiles #Epstein #Music #Shorts #Viral

👆 SHARE if you care! Subscribe for more!"""

# Alternative descriptions
ALT_DESCRIPTIONS = [
    """🎵 From the FFCPLN Playlist - 160+ songs fighting fascism!

🔗 Full playlist: https://ravingANTIFA.com

#FFCPLN #MAGA #Resistance #Music #Shorts""",

    """💀 This song is part of the FFCPLN collection.

Fake F*** Christian Pedo-Lovin' Nazis - 160 songs exposing the truth!

🎶 https://ravingANTIFA.com

#FFCPLN #AntiMAGA #ICE #Shorts""",

    """🚨 FFCPLN PLAYLIST 🚨

160+ anti-fascist anthems. This is just one.

👆 Link in bio for full playlist!

#FFCPLN #MAGA #Resistance #Shorts #Viral""",
]


def generate_clickbait_title(
    original_title: Optional[str] = None,
    song_hint: Optional[str] = None,
) -> str:
    """
    Generate engaging clickbait title for FFCPLN music shorts.

    Args:
        original_title: Original video title for context
        song_hint: Optional song name/hint to include

    Returns:
        Clickbait title under 100 chars
    """
    # Pick random template
    template = random.choice(TITLE_TEMPLATES)

    # Pick random emoji prefix
    emoji = random.choice(EMOJI_PREFIXES)

    # Fill in song hint if provided
    if song_hint:
        title = template.replace("{song_hint}", song_hint)
    else:
        # Remove song_hint placeholder
        title = template.replace("{song_hint} ", "")

    # Add emoji prefix
    title = f"{emoji} {title}"

    # Add trailing emoji sometimes
    if random.random() > 0.5:
        title = f"{title} {random.choice(EMOJI_PREFIXES)}"

    # Ensure under 100 chars for YouTube
    if len(title) > 100:
        title = title[:97] + "..."

    return title


# =============================================================================
# CONTENT TYPE DETECTION - 3-Tier Agentic Classification
# =============================================================================

# Tier 1 Keywords (instant heuristics, no API)
MUSIC_KEYWORDS = [
    "song", "anthem", "remix", "music", "beat", "track", "melody",
    "symphony", "orchestra", "guitar", "piano", "drum", "bass",
    "hip hop", "rap", "rock", "jazz", "edm", "punk", "metal",
    "lyric", "verse", "chorus", "ffcpln",  # FFCPLN is music playlist
]

SPEECH_KEYWORDS = [
    "interview", "speech", "talk", "podcast", "commentary", "discuss",
    "conversation", "debate", "lecture", "explain", "react", "response",
    "opinion", "review", "analysis", "rant", "vlog",
]

NEWS_KEYWORDS = [
    "breaking", "news", "report", "protest", "arrest", "raid",
    "ice", "immigration", "deportation", "trump", "maga", "cruelty",
    "exposed", "leaked", "investigation", "scandal", "caught",
]

# FFCPLN Suno Song Markers - if transcript contains these, it's a SUNO SONG (music)
# Suno AI generates songs with lyrics from "Fake Fuck Christian Pedo_lovin Nazi" prompt
# CRITICAL: This overrides "substantial transcript = speech" detection
FFCPLN_SONG_MARKERS = [
    "ffcpln",
    "fake fuck christian",
    "pedo_lovin nazi",
    "pedo lovin nazi",
    "christian pedo",
    "fuck christian",
    "fake fuck",
]


def detect_content_type_from_title(title: str) -> str:
    """
    Tier 1: Fast content type detection from title only.

    No API calls, instant classification based on keywords.

    Args:
        title: Video title string

    Returns:
        'music', 'speech', 'news', or 'mixed'
    """
    if not title:
        return "music"  # Default for FFCPLN channels

    title_lower = title.lower()

    # Count keyword matches for each type
    music_score = sum(1 for kw in MUSIC_KEYWORDS if kw in title_lower)
    speech_score = sum(1 for kw in SPEECH_KEYWORDS if kw in title_lower)
    news_score = sum(1 for kw in NEWS_KEYWORDS if kw in title_lower)

    # News content often has speech elements too
    if news_score >= 2 or (news_score >= 1 and any(kw in title_lower for kw in ["breaking", "exposed", "protest", "ice raid"])):
        return "news"

    if speech_score >= 2 or (speech_score >= 1 and music_score == 0):
        return "speech"

    if music_score >= 1:
        return "music"

    # Default based on channel context (FFCPLN is primarily music)
    return "music"


def detect_content_type(index_json: Dict[str, Any], title_hint: Optional[str] = None) -> str:
    """
    Agentic content type detection with 3-tier classification.

    Tier 1: Title heuristics (instant, no API)
    Tier 2: Index metadata analysis (from Gemini deep index)
    Tier 3: Audio transcript analysis (when available)

    Args:
        index_json: Video index artifact (can be stub or full)
        title_hint: Optional title for Tier 1 classification

    Returns:
        Content type: 'music', 'speech', 'news', or 'mixed'
    """
    # Tier 1: Try title-based detection first (fast path)
    title = title_hint or ""
    if isinstance(index_json, dict):
        title = title or index_json.get("title", "")
        # Also check metadata summary for title clues
        metadata = index_json.get("metadata") or {}
        if not title:
            title = (metadata.get("summary") or "")[:100]

    if title:
        title_result = detect_content_type_from_title(title)
        # If confident from title, return early
        title_lower = title.lower()
        music_strong = any(kw in title_lower for kw in ["song", "anthem", "music", "ffcpln"])
        news_strong = any(kw in title_lower for kw in ["breaking", "protest", "ice raid", "exposed"])
        speech_strong = any(kw in title_lower for kw in ["interview", "speech", "lecture"])

        if music_strong or news_strong or speech_strong:
            return title_result

    if not isinstance(index_json, dict):
        return title_result if title else "music"

    # Tier 2: Check index metadata (from deeper indexing)
    metadata = index_json.get("metadata") or {}
    topics = metadata.get("topics") or []

    # Check for explicit content type in topics
    topics_lower = [t.lower() for t in topics if isinstance(t, str)]
    if "news" in topics_lower or "protest" in topics_lower:
        return "news"
    if "interview" in topics_lower or "speech" in topics_lower or "commentary" in topics_lower:
        return "speech"

    speech_topics = {"interview", "commentary", "news", "talk", "podcast", "speech", "discussion"}
    if any(t in speech_topics for t in topics_lower):
        return "speech"

    # Tier 3: Check audio analysis (from Gemini deep index)
    audio = index_json.get("audio") or {}
    transcript = (audio.get("transcript_summary") or "").strip()
    segments = audio.get("segments") or []

    # If transcript exists, analyze content
    if transcript:
        transcript_lower = transcript.lower()

        # CRITICAL: Check for FFCPLN Suno song markers FIRST
        # If transcript IS the song lyrics ("Fake Fuck Christian Pedo_lovin Nazi", "FFCPLN")
        # then it's MUSIC, not speech - Suno AI generated these songs
        if any(marker in transcript_lower for marker in FFCPLN_SONG_MARKERS):
            return "music"

        # Only check for speech/news if substantial transcript (not just song title)
        if len(transcript) > 100 or len(segments) > 5:
            # News indicators in transcript
            news_keywords = ["breaking", "report", "trump", "ice", "immigration", "protest", "arrest", "raid"]
            if any(kw in transcript_lower for kw in news_keywords):
                return "news"

            # If transcript is substantial with clear speech patterns, it's speech
            return "speech"

    # Default: return title-based result or music
    return title_result if title else "music"


def extract_title_hint_from_index(index_json: Dict[str, Any], fallback_title: Optional[str] = None) -> str:
    """
    Extract a compact hint from a video index artifact to inform title generation.

    Occam: deterministic extraction only (no network / no LLM).
    Enhanced to extract actual content from audio/visual analysis.
    """
    if not isinstance(index_json, dict):
        return (fallback_title or "").strip()

    # Priority 1: Audio transcript (if indexed with Gemini)
    audio = index_json.get("audio") or {}
    transcript = (audio.get("transcript_summary") or "").strip()
    if transcript and len(transcript) > 20:
        # Extract first meaningful sentence
        sentences = transcript.split(".")
        for sent in sentences[:3]:
            sent = sent.strip()
            if len(sent) > 15 and not sent.lower().startswith("ffcpln"):
                return sent[:48].strip()

    # Priority 2: Key points from metadata
    metadata = index_json.get("metadata") or {}
    if isinstance(metadata, dict):
        # Check key_points first (most specific)
        key_points = metadata.get("key_points") or []
        if isinstance(key_points, list):
            for kp in key_points[:3]:
                if isinstance(kp, str) and len(kp.strip()) > 10:
                    return kp.strip()[:48]

        summary = metadata.get("summary")
        if isinstance(summary, str) and summary.strip():
            s = summary.strip()
            # Common stub prefix: "FFCPLN music short: <title>"
            for prefix in ("FFCPLN music short:", "FFCPLN music short"):
                if s.lower().startswith(prefix.lower()):
                    s = s[len(prefix):].strip(" :.-")
                    break
            # Skip generic stubs
            if "index stub" not in s.lower():
                return s[:48].strip()

        topics = metadata.get("topics") or []
        if isinstance(topics, list):
            for t in topics:
                if not isinstance(t, str):
                    continue
                candidate = t.strip()
                if not candidate:
                    continue
                if candidate.lower() in {"ffcpln", "music", "shorts"}:
                    continue
                return candidate[:32].strip()

    # Priority 3: Visual description
    visual = index_json.get("visual") or {}
    visual_desc = (visual.get("description") or "").strip()
    if visual_desc and len(visual_desc) > 15:
        return visual_desc[:48].strip()

    classification = index_json.get("classification") or {}
    if isinstance(classification, dict):
        cats = classification.get("discovered_categories") or []
        if isinstance(cats, list):
            for c in cats:
                if not isinstance(c, str):
                    continue
                candidate = c.strip()
                if not candidate:
                    continue
                if candidate.lower() in {"ffcpln", "music", "shorts"}:
                    continue
                return candidate[:32].strip()

    return (fallback_title or "").strip()[:48]


def generate_clickbait_title_from_index(
    *,
    original_title: str,
    index_json: Dict[str, Any],
) -> str:
    """
    Generate a clickbait title where the index artifact informs the hint.

    Content-type aware: uses different templates for music vs speech vs news.
    Uses 3-tier agentic classification (title heuristics → metadata → audio).
    """
    import logging
    logger = logging.getLogger(__name__)

    hint = extract_title_hint_from_index(index_json, fallback_title=original_title)
    # Pass original_title for Tier 1 title-based detection (works even with stub index)
    content_type = detect_content_type(index_json, title_hint=original_title)
    logger.info(f"[CONTENT-GEN] Detected content_type={content_type} for '{original_title[:40]}...'")

    # Select template set based on content type
    if content_type == "news":
        templates = NEWS_TITLE_TEMPLATES
        logger.debug("[CONTENT-GEN] Using NEWS_TITLE_TEMPLATES")
    elif content_type == "speech":
        templates = SPEECH_TITLE_TEMPLATES
    else:  # music or default
        templates = MUSIC_TITLE_TEMPLATES

    # If we have a meaningful hint, use content-aware templates
    if hint and len(hint) > 5 and hint.lower() not in {"ffcpln", "music", "shorts"}:
        emoji = random.choice(EMOJI_PREFIXES)
        template = random.choice(templates)
        title = f"{emoji} {template.replace('{hint}', hint)}"

        # Ensure under 100 chars
        if len(title) > 100:
            title = title[:97] + "..."

        return title

    # Fallback to generic FFCPLN templates
    return generate_clickbait_title(original_title=original_title, song_hint=hint or None)


def get_standard_description(template: str = "ffcpln") -> str:
    """
    Get standard algorithm-friendly description.

    Args:
        template: "ffcpln" or "alt" for alternative

    Returns:
        Description string
    """
    if template == "ffcpln":
        return FFCPLN_DESCRIPTION
    else:
        return random.choice(ALT_DESCRIPTIONS)


def generate_description_with_context(
    original_title: Optional[str] = None,
    song_name: Optional[str] = None,
    artist: Optional[str] = None,
) -> str:
    """
    Generate contextual description based on video content.

    Args:
        original_title: Original video title
        song_name: Song name if known
        artist: Artist name if known

    Returns:
        Description with context
    """
    base = FFCPLN_DESCRIPTION

    # Add song/artist credit if known
    if song_name or artist:
        credit = "\n\n🎤 "
        if song_name and artist:
            credit += f'"{song_name}" by {artist}'
        elif song_name:
            credit += f'"{song_name}"'
        elif artist:
            credit += f"by {artist}"

        # Insert before hashtags
        parts = base.split("\n\n#")
        if len(parts) >= 2:
            base = f"{parts[0]}{credit}\n\n#{parts[1]}"

    return base


# Hashtag sets for variety
HASHTAG_SETS = [
    "#FFCPLN #MAGA #ICE #Resistance #Shorts",
    "#FFCPLN #AntiMAGA #Antifascist #Music #Viral",
    "#FFCPLN #TrumpFiles #Epstein #Shorts #FYP",
    "#FFCPLN #MAGA #Immigration #ICE #Shorts",
]

# Trending hashtags for ICE resistance content
TRENDING_ICE_HASHTAGS = [
    "#StopICE #ICEout #ResistICE #AbolishICE",
    "#ICEout #NoHumanIsIllegal #ResistICE #StopDeportations",
    "#AbolishICE #ICERaids #ProtectImmigrants #Sanctuary",
    "#StopICE #ICEout #FamiliesBelongTogether #NoKidsInCages",
    "#ResistICE #ICERaids #StopDeportations #ImmigrantRights",
]

# Content-type specific templates
MUSIC_TITLE_TEMPLATES = [
    "{hint} #FFCPLN #MAGA Music",
    "#FFCPLN Anthem: {hint}",
    "This Song DESTROYS #MAGA! {hint}",
    "{hint} - Anti-Fascist Music #FFCPLN",
]

NEWS_TITLE_TEMPLATES = [
    "BREAKING: {hint} #FFCPLN",
    "#MAGA Won't Show This: {hint}",
    "EXPOSED: {hint} #FFCPLN #ICE",
    "{hint} - Media Blackout! #FFCPLN",
]

SPEECH_TITLE_TEMPLATES = [
    "{hint} #FFCPLN Truth",
    "#MAGA Hates This: {hint}",
    "LISTEN: {hint} #FFCPLN",
    "{hint} - What They Don't Tell You! #FFCPLN",
]


def get_hashtags() -> str:
    """Get random hashtag set."""
    return random.choice(HASHTAG_SETS)


def get_trending_ice_hashtags() -> str:
    """Get trending ICE resistance hashtags."""
    return random.choice(TRENDING_ICE_HASHTAGS)


def get_combined_hashtags(include_trending: bool = True) -> str:
    """Get combined base + trending hashtags."""
    base = random.choice(HASHTAG_SETS)
    if include_trending:
        trending = random.choice(TRENDING_ICE_HASHTAGS)
        return f"{base} {trending}"
    return base


def enhance_title(original_title: str) -> str:
    """
    Enhance existing title for clickability using FFCPLN patterns.
    
    Preserves key content from original while adding engagement hooks.
    
    Args:
        original_title: Original video title
        
    Returns:
        Enhanced clickbait title under 100 chars
    """
    # Pick random emoji
    emoji = random.choice(EMOJI_PREFIXES)
    
    # Extract key words from original (remove existing hashtags)
    clean_title = original_title
    for tag in ["#FFCPLN", "#MAGA", "#trump", "#epstein", "#ICE"]:
        clean_title = clean_title.replace(tag, "").strip()
    
    # Truncate if too long (leave room for hashtags)
    if len(clean_title) > 50:
        clean_title = clean_title[:47] + "..."
    
    # Build enhanced title with hooks
    hooks = [
        f"{emoji} {clean_title} #FFCPLN #MAGA",
        f"{emoji} MUST SEE: {clean_title} #FFCPLN",
        f"{emoji} {clean_title} - 160 Songs! #FFCPLN",
        f"{emoji} VIRAL: {clean_title} #FFCPLN #MAGA",
    ]
    
    enhanced = random.choice(hooks)
    
    # Ensure under 100 chars
    if len(enhanced) > 100:
        enhanced = enhanced[:97] + "..."
    
    return enhanced


def enhance_description(original_desc: str) -> str:
    """
    Enhance existing description for SEO and algorithm optimization.
    
    Preserves original link if present, adds FFCPLN branding and hashtags.
    
    Args:
        original_desc: Original video description
        
    Returns:
        Enhanced description with SEO optimization
    """
    # Check if already has FFCPLN link
    has_ffcpln_link = (
        "ffcpln.foundups.com" in original_desc.lower()
        or "ffc.ravingantifa.com" in original_desc.lower()
    )
    
    # Build enhanced description
    enhanced = """🔥 FFCPLN: Fake F*** Christian Pedo-Lovin' Nazi Playlist 🔥

160+ anti-fascist songs exposing ICE cruelty & MAGA hypocrisy!

🎵 FULL PLAYLIST: https://ravingANTIFA.com

#FFCPLN #MAGA #ICE #Antifascist #Resistance #TrumpFiles #Epstein #Music #Shorts #Viral

👆 SHARE if you care! Subscribe for more!"""
    
    return enhanced

