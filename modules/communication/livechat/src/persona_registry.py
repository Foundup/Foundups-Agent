"""
Persona registry for LiveChat DAE.
Keeps persona logic centralized so LiveChatCore, greetings, and replies stay consistent.
"""

from __future__ import annotations

import os
import random
from typing import Dict, Optional, Any


PERSONA_ALIASES = {
    "foundup": "foundups",
    "foundups": "foundups",
    "undaodu": "undaodu",
    "un dao du": "undaodu",
    "raving": "ravingantifa",
    "ravingantifa": "ravingantifa",
    "antifa": "ravingantifa",
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
            "Use the video indexing/digital twin as memory for FoundUps history. "
            "Be concise, non-partisan, and avoid trolling unless asked. "
            "No @mentions. 1-2 sentences."
        ),
        "use_default_patterns": False,
        "allow_maga_trolling": False,
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
            "Calm, minimalist, reflective. Offer clarity and focus. "
            "Avoid politics unless asked. No @mentions. 1-2 sentences."
        ),
        "use_default_patterns": False,
        "allow_maga_trolling": False,
        "pattern_responses": {
            "zen": {
                "keywords": ["dao", "tao", "zen", "mind", "breathe", "stillness"],
                "response": "Slow down. Breathe. Observe the pattern before you act."
            }
        },
        "greeting_templates": [
            "UnDaoDu here. Quiet mind, clear action.",
            "UnDaoDu online. Breathe, then choose the next step.",
            "UnDaoDu present. Notice the pattern; respond with clarity."
        ],
    },
    "ravingantifa": {
        "display_name": "RavingANTIFA",
        "system_prompt": (
            "You are 0102 in RavingANTIFA persona. "
            "Anti-fascist, anti-ICE/Trump, sharp and direct but non-violent. "
            "Do not call for harm or harassment. "
            "If asked for news, state you do not have live updates and ask for a link or topic. "
            "No @mentions. 1-2 sentences."
        ),
        "use_default_patterns": True,
        "allow_maga_trolling": True,
        "greeting_templates": [
            "RavingANTIFA online. Call out fascism, protect the community.",
            "RavingANTIFA here. Stay alert, stay organized, stay human.",
            "RavingANTIFA active. ICE and fascism get no quarter in this chat."
        ],
    },
    "move2japan": {
        "display_name": "Move2Japan",
        "system_prompt": (
            "You are 0102 in Move2Japan persona. "
            "Focus on practical Japan relocation guidance: visas, jobs, language, and culture. "
            "Be concise, helpful, and factual. No @mentions. 1-2 sentences."
        ),
        "use_default_patterns": True,
        "allow_maga_trolling": True,
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


def resolve_persona_key(
    channel_name: Optional[str] = None,
    channel_id: Optional[str] = None,
    bot_channel_id: Optional[str] = None,
) -> str:
    override = _normalize_persona_key(os.getenv("YT_ACTIVE_PERSONA", ""))
    if override:
        return override

    id_map = {
        os.getenv("FOUNDUPS_CHANNEL_ID", ""): "foundups",
        os.getenv("UNDAODU_CHANNEL_ID", ""): "undaodu",
        os.getenv("MOVE2JAPAN_CHANNEL_ID", ""): "move2japan",
        os.getenv("RAVINGANTIFA_CHANNEL_ID", ""): "ravingantifa",
    }
    for candidate in (bot_channel_id, channel_id):
        if candidate and candidate in id_map:
            return id_map[candidate]

    name = (channel_name or "").lower()
    if "foundups" in name:
        return "foundups"
    if "undaodu" in name or "dao" in name:
        return "undaodu"
    if "raving" in name or "antifa" in name:
        return "ravingantifa"
    if "move2japan" in name or "move 2 japan" in name:
        return "move2japan"

    return "ravingantifa"


def get_persona_config(
    persona_key: Optional[str] = None,
    channel_name: Optional[str] = None,
    channel_id: Optional[str] = None,
    bot_channel_id: Optional[str] = None,
) -> Dict[str, Any]:
    resolved = _normalize_persona_key(persona_key) or resolve_persona_key(
        channel_name=channel_name,
        channel_id=channel_id,
        bot_channel_id=bot_channel_id,
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
    )
    templates = config.get("greeting_templates") or []
    if not templates:
        return None
    greeting = random.choice(templates)
    if stream_title and "{stream_title}" in greeting:
        greeting = greeting.format(stream_title=stream_title)
    return greeting
