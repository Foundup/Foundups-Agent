# -*- coding: utf-8 -*-
from __future__ import annotations

import ctypes
import hashlib
import json
import logging
import os
import sys
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _from_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_state_path() -> Path:
    return _repo_root() / "memory" / "key_hygiene.json"


def fingerprint_secret(secret: str) -> str:
    digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def is_interactive_session() -> bool:
    try:
        return bool(sys.stdin and sys.stdout and sys.stdin.isatty() and sys.stdout.isatty())
    except Exception:
        return False


@dataclass(frozen=True)
class KeyRotationEvent:
    service: str
    key_source: str
    fingerprint: str
    reason: str
    detail: Optional[str] = None


class KeyHygiene:
    """
    Minimal key hygiene tracking + operator prompting.

    - Stores only fingerprints (sha256), never raw key values.
    - Writes state to `memory/key_hygiene.json` (gitignored).
    - Prompts are throttled to avoid spam.
    """

    def __init__(
        self,
        service: str,
        urls: Optional[Tuple[str, ...]] = None,
        state_path: Optional[Path] = None,
    ) -> None:
        self.service = service
        self.urls = tuple(urls or ())
        self.state_path = state_path or _default_state_path()

    @staticmethod
    def default_genai_urls() -> Tuple[str, ...]:
        return (
            "https://aistudio.google.com/app/apikey",
            "https://console.cloud.google.com/apis/credentials",
        )

    def enabled(self) -> bool:
        return _env_truthy("FOUNDUPS_ENABLE_KEY_HYGIENE", "true")

    def rotate_days(self) -> int:
        return _env_int("FOUNDUPS_KEY_HYGIENE_ROTATE_DAYS", 30)

    def prompt_cooldown_hours(self) -> int:
        return _env_int("FOUNDUPS_KEY_HYGIENE_PROMPT_COOLDOWN_HOURS", 12)

    def open_browser_enabled(self) -> bool:
        return _env_truthy("FOUNDUPS_KEY_HYGIENE_OPEN_BROWSER", "true")

    def popup_enabled(self) -> bool:
        return _env_truthy("FOUNDUPS_KEY_HYGIENE_POPUP", "false")

    def _load_state(self) -> Dict[str, Any]:
        try:
            if not self.state_path.exists():
                return {"version": 1, "services": {}}
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return {"version": 1, "services": {}}

    def _save_state(self, state: Dict[str, Any]) -> None:
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
            tmp_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
            tmp_path.replace(self.state_path)
        except Exception:
            pass

    def _ensure_entry(self, state: Dict[str, Any], fingerprint: str) -> Dict[str, Any]:
        services = state.setdefault("services", {})
        service_state = services.setdefault(self.service, {})
        keys = service_state.setdefault("keys", {})
        return keys.setdefault(
            fingerprint,
            {
                "first_seen": None,
                "last_seen": None,
                "key_source": None,
                "compromised": None,
                "last_prompted": None,
                "prompt_count": 0,
            },
        )

    def record_key_seen(self, key_source: str, secret_value: str) -> str:
        fingerprint = fingerprint_secret(secret_value)
        now = _now_utc()
        state = self._load_state()
        entry = self._ensure_entry(state, fingerprint)

        if not entry.get("first_seen"):
            entry["first_seen"] = _to_iso(now)
        entry["last_seen"] = _to_iso(now)
        entry["key_source"] = key_source
        self._save_state(state)
        return fingerprint

    def mark_compromised(self, fingerprint: str, reason: str, detail: Optional[str] = None) -> None:
        now = _now_utc()
        state = self._load_state()
        entry = self._ensure_entry(state, fingerprint)
        entry["compromised"] = {"at": _to_iso(now), "reason": reason, "detail": detail}
        self._save_state(state)

    def _should_prompt(self, state: Dict[str, Any], fingerprint: str) -> Optional[str]:
        service_state = (state.get("services") or {}).get(self.service) or {}
        entry = (service_state.get("keys") or {}).get(fingerprint) or {}

        rotate_days = self.rotate_days()
        if rotate_days > 0:
            first_seen = _from_iso(entry.get("first_seen"))
            if first_seen and (_now_utc() - first_seen) >= timedelta(days=rotate_days):
                return "age"

        compromised = entry.get("compromised")
        if compromised and compromised.get("reason"):
            return "compromised"

        return None

    def maybe_prompt_rotation(
        self,
        key_source: str,
        fingerprint: str,
        *,
        reason_hint: Optional[str] = None,
        interactive: Optional[bool] = None,
    ) -> Optional[KeyRotationEvent]:
        if not self.enabled():
            return None

        if not fingerprint:
            return None

        state = self._load_state()
        entry = self._ensure_entry(state, fingerprint)

        reason = reason_hint or self._should_prompt(state, fingerprint)
        if not reason:
            return None

        cooldown = timedelta(hours=max(self.prompt_cooldown_hours(), 1))
        last_prompted = _from_iso(entry.get("last_prompted"))
        if last_prompted and (_now_utc() - last_prompted) < cooldown:
            return None

        entry["last_prompted"] = _to_iso(_now_utc())
        entry["prompt_count"] = int(entry.get("prompt_count") or 0) + 1
        self._save_state(state)

        detail = None
        compromised = entry.get("compromised") or {}
        if reason == "compromised":
            detail = compromised.get("detail")

        evt = KeyRotationEvent(
            service=self.service,
            key_source=key_source,
            fingerprint=fingerprint,
            reason=reason,
            detail=detail,
        )

        self._notify_operator(evt, interactive=is_interactive_session() if interactive is None else interactive)
        return evt

    def _notify_operator(self, event: KeyRotationEvent, *, interactive: bool) -> None:
        msg_lines = [
            "[KEY-HYGIENE] API key rotation required",
            f"  service: {event.service}",
            f"  source: {event.key_source}",
            f"  fingerprint: {event.fingerprint[:19]}…",
            f"  reason: {event.reason}",
        ]
        if event.reason == "compromised":
            msg_lines.append("  action: key was flagged leaked by provider; revoke + replace immediately")
        elif event.reason == "age":
            msg_lines.append("  action: proactive rotation recommended (key age threshold reached)")

        msg_lines.append("  steps:")
        msg_lines.append("    1) Open key page(s) and create a new key")
        msg_lines.append("    2) Replace the env var in `.env` (prefer VEO3_API_KEY for Shorts)")
        msg_lines.append("    3) Restart 0102")
        if self.urls:
            for url in self.urls:
                msg_lines.append(f"    - {url}")

        payload = {
            "event": "key_rotation_required",
            "service": event.service,
            "key_source": event.key_source,
            "fingerprint": event.fingerprint,
            "reason": event.reason,
        }
        logger.warning("[KEY-HYGIENE] %s", json.dumps(payload, sort_keys=True))

        if interactive:
            for line in msg_lines:
                print(line)
            if event.reason == "compromised":
                self._maybe_popup("\n".join(msg_lines))
                self._maybe_open_urls()

    def _maybe_open_urls(self) -> None:
        if not self.open_browser_enabled():
            return
        for url in self.urls:
            try:
                webbrowser.open(url, new=2)
            except Exception:
                continue

    def _maybe_popup(self, message: str) -> None:
        if not self.popup_enabled():
            return
        if not sys.platform.startswith("win"):
            return
        try:
            ctypes.windll.user32.MessageBoxW(0, message, "FoundUps Key Hygiene", 0x00001000)
        except Exception:
            return
