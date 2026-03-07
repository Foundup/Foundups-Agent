"""
Move2Japan Command Handler (WSP 95 — Skillz Wardrobe)
======================================================

BC0 conversational state machine for Move2Japan FoundUp intake.
Triggered by !move2japan / !m2j / !japan in YouTube Livechat DAE.

Loads skillz from bc0_m2j_intake.json and manages per-stakeholder
conversation state through BC0.1 → BC0.6.

NAVIGATION: livechat/src/message_processor.py → Priority 3.4
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Skillz JSON paths
_SKILLZ_DIR = Path(__file__).resolve().parent.parent.parent / "livechat" / "skillz"
_BC0_SKILLZ_PATH = _SKILLZ_DIR / "bc0_m2j_intake.json"

# Import stakeholder DB from the FoundUp module
try:
    from modules.foundups.move2japan.src.m2j_stakeholder_db import M2JStakeholderDB
except ImportError:
    M2JStakeholderDB = None


def _load_skillz(path: Path) -> Dict[str, Any]:
    """Load a skillz JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error(f"[M2J] Failed to load skillz {path}: {exc}")
        return {}


# Precompile urgency number detector
_URGENCY_RE = re.compile(r"^[!/ ]*([1-5])\b")
# Passport detection patterns
_PASSPORT_YES = re.compile(r"\b(yes|yeah|yep|yup|got it|have it|have one|i do|si|ya)\b", re.IGNORECASE)
_PASSPORT_NO = re.compile(r"\b(no|nope|nah|don.?t have|dont have|never had)\b", re.IGNORECASE)
_PASSPORT_EXPIRED = re.compile(r"\b(expired?|out of date|needs renewal|renew)\b", re.IGNORECASE)
_PASSPORT_PROGRESS = re.compile(r"\b(applying|in progress|waiting|applied|pending)\b", re.IGNORECASE)


class Move2JapanHandler:
    """
    BC0 conversational state machine for Move2Japan FoundUp.

    States:
        BC0.1 — Intent captured, send welcome + urgency question
        BC0.2 — Waiting for timeframe answer
        BC0.3 — Timeframe classified, ask passport
        BC0.4 — Waiting for passport answer
        BC0.5 — Passport classified, make route decision
        BC0.6 — Route decision delivered, conversation complete
    """

    def __init__(self):
        self.skillz = _load_skillz(_BC0_SKILLZ_PATH)
        self.templates = self.skillz.get("response_templates", {})
        self.routing = self.skillz.get("routing_matrix", {})
        self.intent_buckets = self.skillz.get("intent_buckets", {})
        self.urgency_levels = self.skillz.get("urgency_levels", {})

        # Initialize stakeholder DB
        self.db: Optional[M2JStakeholderDB] = None
        if M2JStakeholderDB:
            try:
                self.db = M2JStakeholderDB()
                logger.info("[M2J] Stakeholder DB connected")
            except Exception as exc:
                logger.error(f"[M2J] Failed to init stakeholder DB: {exc}")
        else:
            logger.warning("[M2J] Stakeholder DB not available (import failed)")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_command(
        self, text: str, username: str, user_id: str, role: str
    ) -> Optional[str]:
        """
        Process a !move2japan command or follow-up message.

        Returns response text or None.
        """
        text_stripped = text.strip()

        # Get or create stakeholder
        stakeholder = self._get_or_create_stakeholder(user_id, username)
        bc0_state = stakeholder.get("bc0_state", "BC0.1")

        logger.info(
            f"[M2J] Handler: user={username} state={bc0_state} text='{text_stripped[:60]}'"
        )

        # Check for emotional redirect first (any state)
        if self._is_emotional(text_stripped):
            response = self.templates.get(
                "emotional_redirect",
                "Let's make this practical. How soon are you thinking about moving, and do you have your passport?",
            )
            # Reset to urgency question
            self._update_state(user_id, "BC0.2")
            return f"@{username} {response}"

        # Check if this is a direct topic question that should be redirected
        intent_bucket = self._classify_intent_bucket(text_stripped)
        if intent_bucket and bc0_state in ("BC0.1", "BC0.2"):
            template = self.templates.get("redirect_to_gate", "")
            topic_labels = {
                "jobs": "Jobs and work",
                "visa": "Visa and immigration",
                "housing": "Housing",
                "cost": "Cost of living",
                "qualification": "Qualifications and eligibility",
            }
            topic = topic_labels.get(intent_bucket, intent_bucket.title())
            response = template.replace("{topic}", topic) if template else (
                f"{topic} is a huge part of the move. "
                "First so I know your stage: how soon are you thinking, and do you have your passport?"
            )
            self._update_state(user_id, "BC0.2")
            return f"@{username} {response}"

        # State machine dispatch
        if bc0_state == "BC0.1":
            return self._handle_bc0_1(user_id, username, text_stripped)
        elif bc0_state in ("BC0.2", "BC0.3"):
            return self._handle_bc0_2_3(user_id, username, text_stripped)
        elif bc0_state in ("BC0.4", "BC0.5"):
            return self._handle_bc0_4_5(user_id, username, text_stripped)
        elif bc0_state == "BC0.6":
            return self._handle_bc0_6(user_id, username, text_stripped)
        else:
            # Unknown state — reset
            self._update_state(user_id, "BC0.1")
            return self._handle_bc0_1(user_id, username, text_stripped)

    # ------------------------------------------------------------------
    # State Handlers
    # ------------------------------------------------------------------

    def _handle_bc0_1(self, user_id: str, username: str, text: str) -> str:
        """BC0.1 — Initial trigger. Send welcome + urgency question."""
        # Check if they included a number with the command (e.g., "!m2j 3")
        urgency = self._parse_urgency(text)
        if urgency:
            return self._process_urgency(user_id, username, urgency)

        welcome = self.templates.get(
            "welcome",
            "🇯🇵 How soon are you thinking about moving to Japan?\n\n"
            "1️⃣ Just exploring\n2️⃣ Maybe 1-2 years\n3️⃣ Within 12 months\n"
            "4️⃣ Within 6 months\n5️⃣ ASAP",
        )
        self._update_state(user_id, "BC0.2")
        return f"@{username} {welcome}"

    def _handle_bc0_2_3(self, user_id: str, username: str, text: str) -> str:
        """BC0.2/3 — Waiting for urgency answer."""
        urgency = self._parse_urgency(text)
        if urgency:
            return self._process_urgency(user_id, username, urgency)

        # Didn't get a number — re-prompt gently
        return (
            f"@{username} Just pick a number 1-5 for how soon you're thinking:\n"
            "1️⃣ Exploring  2️⃣ 1-2 years  3️⃣ 12 months  4️⃣ 6 months  5️⃣ ASAP"
        )

    def _handle_bc0_4_5(self, user_id: str, username: str, text: str) -> str:
        """BC0.4/5 — Waiting for passport answer."""
        passport = self._parse_passport(text)
        if passport:
            return self._process_passport(user_id, username, passport)

        # Didn't get a clear passport answer — re-prompt
        return (
            f"@{username} Do you already have a passport? "
            "Yes / No / Expired / Not sure"
        )

    def _handle_bc0_6(self, user_id: str, username: str, text: str) -> str:
        """BC0.6 — Route already delivered. Handle re-engagement."""
        # If they type !move2japan again, show their current status
        stakeholder = self._get_or_create_stakeholder(user_id, username)
        urgency = stakeholder.get("urgency_level", "unknown")
        passport = stakeholder.get("passport_status", "unknown")

        if passport in ("no", "expired", "in_progress"):
            return (
                f"@{username} Welcome back! Your status: timeline={urgency}, passport={passport}. "
                "Get that passport in motion first — type !m2j when it's ready and we'll move forward. "
                "📬 Updates: movetojapan.info"
            )
        else:
            return (
                f"@{username} Welcome back! Your status: timeline={urgency}, passport=✅. "
                "You're past the first gate. "
                "🗺️ Track your roadmap: movetojapan.foundups.com"
            )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def _parse_urgency(self, text: str) -> Optional[str]:
        """Extract urgency number (1-5) from text."""
        # Check for bare number
        match = _URGENCY_RE.search(text)
        if match:
            return match.group(1)
        # Check for number after command prefix
        for pattern in [r"!move2japan\s+(\d)", r"!m2j\s+(\d)", r"!japan\s+(\d)"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1) in "12345":
                return match.group(1)
        return None

    def _parse_passport(self, text: str) -> Optional[str]:
        """Extract passport status from text."""
        if _PASSPORT_EXPIRED.search(text):
            return "expired"
        if _PASSPORT_PROGRESS.search(text):
            return "in_progress"
        if _PASSPORT_NO.search(text):
            return "no"
        if _PASSPORT_YES.search(text):
            return "yes"
        return None

    def _classify_intent_bucket(self, text: str) -> Optional[str]:
        """Classify user's message into an intent bucket."""
        text_lower = text.lower()
        for bucket, config in self.intent_buckets.items():
            keywords = config.get("keywords", [])
            for kw in keywords:
                if kw in text_lower:
                    logger.debug(f"[M2J] Intent bucket: {bucket} (keyword: {kw})")
                    return bucket
        return None

    def _is_emotional(self, text: str) -> bool:
        """Check if the message is emotionally loaded."""
        emotional_kw = self.intent_buckets.get("emotional", {}).get("keywords", [])
        text_lower = text.lower()
        return any(kw in text_lower for kw in emotional_kw)

    # ------------------------------------------------------------------
    # State Transitions
    # ------------------------------------------------------------------

    def _process_urgency(self, user_id: str, username: str, urgency_num: str) -> str:
        """Process urgency answer and move to passport question."""
        urgency_map = {
            "1": "explorer", "2": "planner", "3": "serious",
            "4": "imminent", "5": "urgent",
        }
        urgency_label = urgency_map.get(urgency_num, "explorer")
        timeline_map = {
            "1": "exploring", "2": "12_24_months", "3": "12_months",
            "4": "6_months", "5": "asap",
        }
        timeline = timeline_map.get(urgency_num, "exploring")

        self._update_state(user_id, "BC0.4", {
            "urgency_level": urgency_label,
            "timeline_estimate": timeline,
        })

        ack = self.templates.get(
            "timeframe_ack",
            "Got it. Do you already have a passport? Yes / No / Expired / Not sure",
        )
        return f"@{username} {ack}"

    def _process_passport(self, user_id: str, username: str, passport: str) -> str:
        """Process passport answer and deliver route decision."""
        stakeholder = self._get_or_create_stakeholder(user_id, username)
        urgency_label = stakeholder.get("urgency_level", "explorer")

        self._update_state(user_id, "BC0.6", {
            "passport_status": passport,
        })

        # Build routing key — e.g., "serious_yes" or "exploring_no"
        passport_key = "yes" if passport in ("yes",) else "no"
        route_key = f"{urgency_label}_{passport_key}"
        route_config = self.routing.get(route_key, {})
        message_key = route_config.get("message_key", "")

        response = self.templates.get(message_key, "")
        if not response:
            # Fallback based on passport status
            if passport_key == "no":
                response = self.templates.get("no_passport", "Get your passport first — that's step one.")
            else:
                response = self.templates.get("yes_passport", "You're past the first gate. Next up: figuring out your move path.")

        logger.info(
            f"[M2J] Route decision: {route_key} → {route_config.get('route', 'unknown')} "
            f"for {username} ({user_id})"
        )

        return f"@{username} {response}"

    # ------------------------------------------------------------------
    # Stakeholder DB Helpers
    # ------------------------------------------------------------------

    def _get_or_create_stakeholder(self, user_id: str, username: str) -> Dict[str, Any]:
        """Get or create stakeholder record."""
        if self.db:
            return self.db.get_or_create(user_id, username)
        # In-memory fallback when DB is unavailable
        return {
            "stakeholder_id": user_id,
            "chat_handle": username,
            "bc0_state": "BC0.1",
            "urgency_level": "unknown",
            "passport_status": "unknown",
        }

    def _update_state(
        self, user_id: str, new_state: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update stakeholder's BC0 state and optional extra fields."""
        updates = {"bc0_state": new_state}
        if extra:
            updates.update(extra)
        if self.db:
            self.db.update_stakeholder(user_id, updates)
        logger.debug(f"[M2J] State transition → {new_state} for {user_id}")

    # ------------------------------------------------------------------
    # Info Commands
    # ------------------------------------------------------------------

    def handle_info_command(self, text: str, username: str, user_id: str) -> Optional[str]:
        """Handle !m2j info / !m2j stats sub-commands."""
        text_lower = text.lower().strip()

        if "stats" in text_lower or "status" in text_lower:
            stakeholder = self._get_or_create_stakeholder(user_id, username)
            urgency = stakeholder.get("urgency_level", "unknown")
            passport = stakeholder.get("passport_status", "unknown")
            stage = stakeholder.get("current_stage", "BC0")
            return (
                f"@{username} 🇯🇵 M2J Status: "
                f"stage={stage} | timeline={urgency} | passport={passport}"
            )

        if "reset" in text_lower:
            self._update_state(user_id, "BC0.1", {
                "urgency_level": "unknown",
                "passport_status": "unknown",
                "current_stage": "BC0",
            })
            return f"@{username} 🔄 Move2Japan progress reset. Type !m2j to start fresh."

        return None
