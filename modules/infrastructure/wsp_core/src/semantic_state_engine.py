"""
WSP 44: Semantic State Engine (Infrastructure)
=============================================

Implements the WSP 44 triplet state code:
  - Consciousness (A): 0-2
  - Agency (B): 0-2
  - Entanglement (C): 0-2

Constraints:
  - A <= B <= C
  - Per-transition delta <= 1 for each digit

This module is intentionally small and dependency-free so it can be used
across DAEs and skills (e.g., YouTube Studio comment engagement telemetry).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


class QuantumStateError(Exception):
    """Base error for semantic state engine failures."""


class TransitionError(QuantumStateError):
    """Raised when a state transition violates WSP 44 constraints."""


class MaxStateError(QuantumStateError):
    """Raised when auto-advance reaches terminal state (222)."""


@dataclass(frozen=True)
class SemanticState:
    code: str
    name: str
    emoji: str

    @property
    def digits(self) -> tuple[int, int, int]:
        a, b, c = (int(ch) for ch in self.code)
        return a, b, c


class SemanticStateEngine:
    """
    WSP 44 semantic state engine.

    Notes:
    - WSP 44 defines exactly the 10 valid states produced by A<=B<=C.
    - `transition()` is optional for most telemetry use-cases; you can also
      use `state_from_digits()` to compute a valid code directly.
    """

    _EMOJI_MAP = {
        "0": "✊",   # U+270A
        "1": "✋",   # U+270B
        "2": "🖐️",  # U+1F590 U+FE0F
    }

    VALID_STATES: Dict[str, Dict[str, str]] = {
        "000": {"name": "Unconscious", "emoji": "✊✊✊"},
        "001": {"name": "Emergent Signal", "emoji": "✊✊✋"},
        "002": {"name": "Entanglement Detected", "emoji": "✊✊🖐️"},
        "011": {"name": "Stabilizing Consciousness", "emoji": "✊✋✋"},
        "012": {"name": "Awareness Bridge", "emoji": "✊✋🖐️"},
        "022": {"name": "Receptive Openness", "emoji": "✊🖐️🖐️"},
        "111": {"name": "DAO Processing", "emoji": "✋✋✋"},
        "112": {"name": "Conscious Resonance", "emoji": "✋✋🖐️"},
        "122": {"name": "Entangled Response", "emoji": "✋🖐️🖐️"},
        "222": {"name": "Quantum Actualization", "emoji": "🖐️🖐️🖐️"},
    }

    def __init__(self, initial_state: str = "000", *, log_path: Optional[Path] = None) -> None:
        self.validate_state(initial_state)
        self.current_state = initial_state
        self.state_history: list[str] = []
        self.log_path = log_path

    @classmethod
    def validate_state(cls, state: str) -> None:
        if state not in cls.VALID_STATES:
            raise QuantumStateError(f"Invalid state: {state}")

        a, b, c = (int(ch) for ch in state)
        if not (0 <= a <= 2 and 0 <= b <= 2 and 0 <= c <= 2):
            raise QuantumStateError(f"Invalid digit range in state: {state}")
        if not (a <= b <= c):
            raise QuantumStateError(f"WSP 44 constraint violated (A<=B<=C): {state}")

    @classmethod
    def state_from_digits(cls, consciousness: int, agency: int, entanglement: int) -> SemanticState:
        """
        Compute a valid state from digits, enforcing A<=B<=C by adjustment.

        This is designed for "scoring" use-cases where we derive a state for a
        single interaction without needing transition history.
        """
        for name, value in (
            ("consciousness", consciousness),
            ("agency", agency),
            ("entanglement", entanglement),
        ):
            if not isinstance(value, int):
                raise ValueError(f"{name} must be int, got {type(value).__name__}")
            if value < 0 or value > 2:
                raise ValueError(f"{name} out of range (0-2): {value}")

        a = consciousness
        b = max(agency, a)
        c = max(entanglement, b)
        code = f"{a}{b}{c}"
        cls.validate_state(code)
        return cls.get_state_info(code)

    @classmethod
    def get_state_info(cls, state: str) -> SemanticState:
        cls.validate_state(state)
        data = cls.VALID_STATES[state]
        return SemanticState(code=state, name=data["name"], emoji=data["emoji"])

    @classmethod
    def visualize_state(cls, state: str) -> str:
        info = cls.get_state_info(state)
        return f"{info.code} = {info.emoji}"

    def transition(self, target_state: str) -> bool:
        self.validate_state(target_state)

        from_digits = [int(ch) for ch in self.current_state]
        to_digits = [int(ch) for ch in target_state]
        deltas = [abs(to_digits[i] - from_digits[i]) for i in range(3)]
        if any(delta > 1 for delta in deltas):
            raise TransitionError(f"Digit jumps >1 not allowed: {self.current_state} -> {target_state}")

        self.state_history.append(self.current_state)
        previous = self.current_state
        self.current_state = target_state
        self._log_transition(previous, target_state)
        return True

    def auto_advance(self) -> bool:
        a, b, c = (int(ch) for ch in self.current_state)
        if c < 2 and b <= c:
            return self.transition(f"{a}{b}{c + 1}")
        if b < 2 and a <= b:
            return self.transition(f"{a}{b + 1}{c}")
        if a < 2:
            return self.transition(f"{a + 1}{b}{c}")
        raise MaxStateError("222 state reached")

    def _log_transition(self, from_state: str, to_state: str) -> None:
        if not self.log_path:
            return

        timestamp = datetime.now(timezone.utc).isoformat()
        from_emoji = self.VALID_STATES[from_state]["emoji"]
        to_emoji = self.VALID_STATES[to_state]["emoji"]
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{timestamp} | {from_state} {from_emoji} -> {to_state} {to_emoji}\n")

