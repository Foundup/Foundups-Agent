"""
antifaFM LinkedIn Post Generator

Generates LinkedIn posts for antifaFM live streams on GeoZai page (104834798).
Aligned with FFCPLN anti-fascist music brand.
"""

import random
from typing import Dict, Any, Optional
from datetime import datetime


# Post templates aligned with FFCPLN messaging
TEMPLATES = {
    "stream_announcement": """🔴 LIVE NOW: antifaFM - 24/7 Music for Fighting Fascism

The resistance has a soundtrack. 160+ songs for democracy.

🎵 Tune in: {stream_url}

#FFCPLN #Democracy2026 #Resistance #AntiFascist #Music

👆 2026 is the year. Join us.""",

    "urgency": """🚨 antifaFM is LIVE - The Playlist They Fear

160 songs MAGA doesn't want you to hear.
24/7 anti-fascist radio. No commercials. No compromise.

🔴 {stream_url}

#FFCPLN #Democracy #Antifascist #TrumpFiles

250 years of freedom at stake. Music matters.""",

    "community": """✊ antifaFM Live Stream - Democracy's Soundtrack

Fighting for:
🗳️ Democracy over authoritarianism
💪 Labor rights over exploitation
🏥 Reproductive freedom
🌍 Climate action
🛡️ Immigrant rights vs ICE cruelty

🎵 Listen now: {stream_url}

#FFCPLN #Resistance #Democracy2026 #Music""",

    "direct_action": """🔥 antifaFM: 24/7 Anti-Fascist Radio - LIVE

160+ songs. One mission: Defend democracy.

2026 is not the year to be silent.
This is the year to turn it UP.

🔴 Join the resistance: {stream_url}

#FFCPLN #AntiFascist #Democracy #Music #Resistance""",

    "night_shift": """🌙 antifaFM Late Night - The Resistance Never Sleeps

24/7 anti-fascist radio. 160+ songs fighting for democracy.

While they sleep, we organize.
While they dream, we resist.

🎵 {stream_url}

#FFCPLN #Resistance #NightOwls #AntiFascist #Music""",

    "weekend": """🎸 Weekend Resistance: antifaFM LIVE

160+ songs. 24/7. No breaks. No surrender.

This weekend, turn up the resistance.

🔴 {stream_url}

#FFCPLN #WeekendVibes #Democracy2026 #AntiFascist #Music"""
}


def select_template() -> str:
    """
    Select appropriate template based on time of day and day of week.

    Returns:
        Template key
    """
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0=Monday, 6=Sunday

    # Weekend (Sat/Sun)
    if weekday >= 5:
        return random.choice(["weekend", "community", "direct_action"])

    # Night shift (10pm - 6am)
    if hour >= 22 or hour < 6:
        return "night_shift"

    # Morning (6am - 12pm) - urgency
    if 6 <= hour < 12:
        return random.choice(["urgency", "stream_announcement"])

    # Afternoon/Evening - mix
    return random.choice(["stream_announcement", "community", "direct_action"])


def generate_post(
    video_id: str,
    title: Optional[str] = None,
    template_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a LinkedIn post for antifaFM stream.

    Args:
        video_id: YouTube video ID
        title: Optional stream title (usually ignored for template)
        template_key: Optional specific template to use

    Returns:
        Dict with post_content and metadata
    """
    stream_url = f"https://www.youtube.com/watch?v={video_id}"

    # Select template
    if template_key and template_key in TEMPLATES:
        selected_template = template_key
    else:
        selected_template = select_template()

    # Generate post
    template = TEMPLATES[selected_template]
    post_content = template.format(stream_url=stream_url)

    # Extract hashtags
    hashtags = [word for word in post_content.split() if word.startswith('#')]

    return {
        "post_content": post_content,
        "template_used": selected_template,
        "stream_url": stream_url,
        "video_id": video_id,
        "hashtags": hashtags,
        "char_count": len(post_content),
        "confidence": 0.95,
        "patterns": {
            "ffcpln_aligned": "#FFCPLN" in post_content,
            "url_included": stream_url in post_content,
            "hashtags_present": len(hashtags) >= 3,
            "under_3000_chars": len(post_content) < 3000
        }
    }


def get_all_templates() -> Dict[str, str]:
    """Return all available templates for preview."""
    return TEMPLATES.copy()


# Quick test
if __name__ == "__main__":
    result = generate_post("test123")
    print(f"Template: {result['template_used']}")
    print(f"Chars: {result['char_count']}")
    print("-" * 40)
    print(result['post_content'])
