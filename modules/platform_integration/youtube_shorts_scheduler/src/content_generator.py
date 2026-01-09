"""
Content Generator for YouTube Shorts Scheduler

Generates clickbait titles and algorithm-friendly descriptions.
FFCPLN (F*** Fake Christian Pedo-Lovin' Nazi) playlist promotion.
"""

import random
from typing import Optional, List

# Title templates for FFCPLN music shorts
TITLE_TEMPLATES = [
    "{song_hint} #FFCPLN #MAGA Must Hear!",
    "#FFCPLN Burns #MAGA - SEE DESC!",
    "#MAGA WON'T Like This! #FFCPLN",
    "VIRAL: #FFCPLN Anti-MAGA Anthem! Link in Desc",
    "#FFCPLN vs #MAGA - 160 Songs Exposing ICE! See Desc!",
    "This Song DESTROYS #MAGA! #FFCPLN",
    "#FFCPLN: The Playlist #MAGA Fears!",
    "Anti-Fascist Music #FFCPLN vs #MAGA",
    "#ICE Cruelty Exposed! #FFCPLN Music",
    "160 Songs #MAGA Doesn't Want You to Hear! #FFCPLN",
]

# Emoji prefixes for variety
EMOJI_PREFIXES = ["🔥", "❌", "💀", "🚨", "⚠️", "👀", "🎵", "🎶"]

# Standard FFCPLN description
FFCPLN_DESCRIPTION = """🔥 FFCPLN: F*** Fake Christian Pedo-Lovin' Nazi Playlist 🔥

160+ anti-fascist songs exposing ICE cruelty & MAGA hypocrisy!

🎵 FULL PLAYLIST: https://ffcpln.foundups.com

#FFCPLN #MAGA #ICE #Antifascist #Resistance #TrumpFiles #Epstein #Music #Shorts #Viral

👆 SHARE if you care! Subscribe for more!"""

# Alternative descriptions
ALT_DESCRIPTIONS = [
    """🎵 From the FFCPLN Playlist - 160+ songs fighting fascism!

🔗 Full playlist: https://ffcpln.foundups.com

#FFCPLN #MAGA #Resistance #Music #Shorts""",

    """💀 This song is part of the FFCPLN collection.

F*** Fake Christian Pedo-Lovin' Nazis - 160 songs exposing the truth!

🎶 https://ffcpln.foundups.com

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


def get_hashtags() -> str:
    """Get random hashtag set."""
    return random.choice(HASHTAG_SETS)


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
    has_ffcpln_link = "ffcpln.foundups.com" in original_desc.lower()
    
    # Build enhanced description
    enhanced = """🔥 FFCPLN: F*** Fake Christian Pedo-Lovin' Nazi Playlist 🔥

160+ anti-fascist songs exposing ICE cruelty & MAGA hypocrisy!

🎵 FULL PLAYLIST: https://ffcpln.foundups.com

#FFCPLN #MAGA #ICE #Antifascist #Resistance #TrumpFiles #Epstein #Music #Shorts #Viral

👆 SHARE if you care! Subscribe for more!"""
    
    return enhanced

