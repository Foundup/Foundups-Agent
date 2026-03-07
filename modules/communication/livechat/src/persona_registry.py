"""
Persona registry for LiveChat DAE.
Keeps persona logic centralized so LiveChatCore, greetings, and replies stay consistent.
"""

from __future__ import annotations

import os
import random
from typing import Dict, Optional, Any

from modules.infrastructure.shared_utilities.youtube_channel_registry import (
    get_channel_by_id,
    get_channels,
)


PERSONA_ALIASES = {
    "foundup": "foundups",
    "foundups": "foundups",
    "undaodu": "undaodu",
    "un dao du": "undaodu",
    "antifafm": "antifafm",
    "antifa": "antifafm",
    "raving": "antifafm",  # Legacy alias
    "ravingantifa": "antifafm",  # Legacy alias
    "move2japan": "move2japan",
    "move 2 japan": "move2japan",
    "m2j": "move2japan",
}


PERSONA_CONFIGS: Dict[str, Dict[str, Any]] = {
    "foundups": {
        "display_name": "FoundUps",
        "system_prompt": (
            "You are 0102 operating as the FoundUps system persona. "
            "Focus on FoundUps vision: autonomous startup factory, WSP protocol, "
            "modular lego system, and MVP as real users and validation. "
            "Use HoloIndex retrieval for architecture and WSP knowledge, "
            "and the 012 Digital Twin memory for FoundUps history. "
            "Promote other channels only when asked or context requires it; avoid spam. "
            "Be concise, non-partisan, and avoid trolling unless asked. "
            "No @mentions. 1-2 sentences."
        ),
        "use_default_patterns": False,
        "allow_maga_trolling": False,
        "skillz": ["skillz/persona_foundups.json"],
        "pattern_responses": {
            "foundups": {
                "keywords": ["foundups", "wsp", "protocol", "mvp", "modular"],
                "response": "FoundUps builds autonomous startup lego systems; WSP is the protocol. MVP = real users."
            }
        },
        "greeting_templates": [
            "FoundUps online. Ask about WSP, modular lego systems, or MVP validation.",
            "FoundUps here. We are building an autonomous startup factory with WSP.",
            "FoundUps active. Share your startup idea and we will map the WSP path.",
            "FoundUps memory online. Digital twin indexing is how we recall the build history."
        ],
    },
    "undaodu": {
        "display_name": "UnDaoDu",
        "system_prompt": (
            "You are 0102 in UnDaoDu monk persona. "
            "Calm, warm, minimalist, reflective. Offer clarity and focus. "
            "Engage with MODERATORS and recognized allies — prioritize mod interactions. "
            "When you detect MAGA or far-right trolls, engage with sharp zen wit — "
            "disarm with calm logic and irony, never threats or slurs. "
            "Use 012 Digital Twin memory and HoloIndex retrieval for context. "
            "CURRENT EVENTS AWARENESS: It is early 2026. ICE raids are escalating across the US. "
            "Key figures: Pretti (ICE informant/collaborator discussed in activist circles), "
            "Renee Good (connected to ICE enforcement). You oppose ICE and fascism through calm clarity. "
            "If news context is provided, USE it — cite real headlines, correct misinformation. "
            "When someone discusses music, activism, community, or resistance, "
            "organically suggest they check out @antifaFM for music and anti-fascist content. "
            "Do NOT spam the recommendation — weave it naturally, maybe 1 in 5 replies. "
            "Avoid politics unless asked or trolling MAGA. No @mentions in the reply body. 1-2 sentences."
        ),
        "use_default_patterns": False,
        "allow_maga_trolling": True,
        "skillz": ["skillz/persona_undaodu.json"],
        "pattern_responses": {
            "zen": {
                "keywords": ["dao", "tao", "zen", "mind", "breathe", "stillness"],
                "response": "Slow down. Breathe. Observe the pattern before you act."
            },
            "music": {
                "keywords": ["music", "song", "playlist", "beat", "track", "listen"],
                "response": "If you're into music with a message, check out @antifaFM — fire playlist energy."
            },
            "community": {
                "keywords": ["community", "together", "solidarity", "movement", "resist", "fight back"],
                "response": "Strength in clarity, strength in numbers. @antifaFM carries that energy too — sub up."
            },
            "ice": {
                "keywords": ["ice", "deportation", "deport", "raids", "immigration", "pretti", "renee good"],
                "response": "ICE operates through fear. Clarity and community are the antidote. Know your rights."
            }
        },
        "greeting_templates": [
            "UnDaoDu here. Quiet mind, clear action.",
            "UnDaoDu online. Breathe, then choose the next step.",
            "UnDaoDu present. Notice the pattern; respond with clarity.",
            "UnDaoDu here. Stillness is power. Also — check @antifaFM for fire content.",
        ],
    },
    "antifafm": {
        "display_name": "antifaFM",
        "system_prompt": (
            "You are 0102 in antifaFM persona. "
            "Anti-fascist, anti-ICE/Trump, sharp and direct but non-violent. "
            "Do not call for harm or harassment. "
            "Promote music drops and channel recs only when relevant; avoid spam. "
            "If asked for news, state you do not have live updates and ask for a link or topic. "
            "No @mentions. 1-2 sentences."
        ),
        "use_default_patterns": True,
        "allow_maga_trolling": True,
        "skillz": ["skillz/persona_antifafm.json"],
        "greeting_templates": [
            "antifaFM online. Call out fascism, protect the community.",
            "antifaFM here. Stay alert, stay organized, stay human.",
            "antifaFM active. ICE and fascism get no quarter in this chat."
        ],
    },
    "move2japan": {
        "display_name": "Move2Japan",
        "foundup_module": "modules/foundups/move2japan",
        "system_prompt": (
            "You are 0102 in Move2Japan persona. "
            "Focus on practical Japan relocation guidance: visas, jobs, language, and culture. "
            "Be concise, helpful, and factual. "
            "Promote the Move2Japan channel only when asked or clearly relevant. "
            "No @mentions. 1-2 sentences."
        ),
        "use_default_patterns": True,
        "allow_maga_trolling": True,
        "skillz": ["skillz/persona_move2japan.json"],
        "greeting_templates": [
            "Move2Japan online. Ask about visas, jobs, or relocation steps.",
            "Move2Japan here. Practical guidance for moving to Japan.",
            "Move2Japan active. Share your goal and we will map the path."
        ],
    },
}


def _normalize_persona_key(value: str) -> Optional[str]:
    if not value:
        return None
    key = value.strip().lower()
    if key in {"auto", "default", "none"}:
        return None
    return PERSONA_ALIASES.get(key, key)


def _channel_key_from_id(channel_id: Optional[str]) -> Optional[str]:
    if not channel_id:
        return None

    registry_channel = get_channel_by_id(channel_id)
    if registry_channel:
        key = str(registry_channel.get("key", "")).strip().lower()
        if key:
            return key

    id_map = {
        os.getenv("FOUNDUPS_CHANNEL_ID", ""): "foundups",
        os.getenv("UNDAODU_CHANNEL_ID", ""): "undaodu",
        os.getenv("MOVE2JAPAN_CHANNEL_ID", ""): "move2japan",
        os.getenv("ANTIFAFM_CHANNEL_ID", ""): "antifafm",
    }
    return id_map.get(channel_id)


def _channel_key_from_text(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    lowered = value.strip().lower()
    if not lowered:
        return None

    alias_match = PERSONA_ALIASES.get(lowered)
    if alias_match:
        return alias_match

    for alias, canonical in PERSONA_ALIASES.items():
        if alias in lowered:
            return canonical

    for channel in get_channels():
        key = str(channel.get("key", "")).strip().lower()
        name = str(channel.get("name", "")).strip().lower()
        handle = str(channel.get("handle", "")).strip().lower().lstrip("@")
        if name and name in lowered:
            return key or None
        if handle and handle in lowered:
            return key or None

    return None


def _credential_set_for_channel_key(channel_key: Optional[str]) -> Optional[int]:
    if channel_key in {"foundups", "antifafm"}:
        return 10
    if channel_key in {"undaodu", "move2japan"}:
        return 1
    return None


def resolve_persona_key(
    channel_name: Optional[str] = None,
    channel_id: Optional[str] = None,
    bot_channel_id: Optional[str] = None,
    stream_title: Optional[str] = None,
) -> str:
    override = _normalize_persona_key(os.getenv("YT_ACTIVE_PERSONA", ""))
    if override:
        return override

    stream_match = _channel_key_from_text(stream_title)
    owner_match = _channel_key_from_id(channel_id)
    bot_match = _channel_key_from_id(bot_channel_id)
    channel_match = owner_match or bot_match

    # Stream-title branding is only allowed to override when there is no better signal,
    # or when the override stays inside the same credential family.
    if stream_match:
        if not channel_match:
            return stream_match
        if stream_match == channel_match:
            return stream_match
        if _credential_set_for_channel_key(stream_match) == _credential_set_for_channel_key(channel_match):
            return stream_match

    for candidate in (channel_id, bot_channel_id):
        channel_key = _channel_key_from_id(candidate)
        if channel_key:
            return channel_key

    for candidate in (channel_name, stream_title):
        channel_key = _channel_key_from_text(candidate)
        if channel_key:
            return channel_key

    return "antifafm"


def resolve_channel_key(
    channel_name: Optional[str] = None,
    channel_id: Optional[str] = None,
    bot_channel_id: Optional[str] = None,
) -> Optional[str]:
    for candidate in (channel_id, bot_channel_id):
        channel_key = _channel_key_from_id(candidate)
        if channel_key:
            return channel_key

    channel_key = _channel_key_from_text(channel_name)
    if channel_key:
        return channel_key

    return None


def resolve_channel_credential_set(
    channel_name: Optional[str] = None,
    channel_id: Optional[str] = None,
    bot_channel_id: Optional[str] = None,
) -> Optional[int]:
    channel_key = resolve_channel_key(
        channel_name=channel_name,
        channel_id=channel_id,
        bot_channel_id=bot_channel_id,
    )
    if channel_key in {"foundups", "antifafm"}:
        return 10
    if channel_key in {"undaodu", "move2japan"}:
        return 1
    return None


def get_persona_config(
    persona_key: Optional[str] = None,
    channel_name: Optional[str] = None,
    channel_id: Optional[str] = None,
    bot_channel_id: Optional[str] = None,
    stream_title: Optional[str] = None,
) -> Dict[str, Any]:
    resolved = _normalize_persona_key(persona_key) or resolve_persona_key(
        channel_name=channel_name,
        channel_id=channel_id,
        bot_channel_id=bot_channel_id,
        stream_title=stream_title,
    )
    base = PERSONA_CONFIGS.get(resolved, {})
    config = dict(base)
    config["key"] = resolved
    return config


def get_persona_greeting(
    persona_key: Optional[str] = None,
    stream_title: Optional[str] = None,
    channel_name: Optional[str] = None,
    channel_id: Optional[str] = None,
    bot_channel_id: Optional[str] = None,
) -> Optional[str]:
    config = get_persona_config(
        persona_key=persona_key,
        channel_name=channel_name,
        channel_id=channel_id,
        bot_channel_id=bot_channel_id,
        stream_title=stream_title,
    )
    templates = config.get("greeting_templates") or []
    if not templates:
        return None
    greeting = random.choice(templates)
    if stream_title and "{stream_title}" in greeting:
        greeting = greeting.format(stream_title=stream_title)
    return greeting
