# -*- coding: utf-8 -*-
"""
Style Guardrails - Enforce 012's style rules on generated content.

WSP Compliance:
    WSP 77: Agent Coordination (Digital Twin guardrails)
    WSP 91: DAE Observability

Purpose:
    Load and enforce style rules:
    - Banned phrases blocking
    - Max/min length enforcement
    - Emoji rules (inline only)
    - "No fluff" rule (strip filler phrases)
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Default filler phrases to strip
DEFAULT_FILLERS = [
    "Sure!",
    "Absolutely!",
    "Of course!",
    "Great question!",
    "Thanks for asking!",
    "I'd be happy to",
    "Let me explain",
    "Well,",
    "So,",
    "Basically,",
    "Actually,",
]


class StyleGuardrails:
    """
    Enforce 012's style rules on generated content.
    
    Example:
        >>> sg = StyleGuardrails()
        >>> text, violations = sg.enforce("Sure! I think this is great!")
        >>> # text: "This is great!" (stripped filler, banned phrase flagged)
    """
    
    def __init__(
        self,
        rules_file: Optional[str] = None,
        banned_file: Optional[str] = None
    ):
        """
        Initialize guardrails.
        
        Args:
            rules_file: Path to style_rules.json
            banned_file: Path to banned_phrases.json
        """
        base_dir = Path(__file__).parent.parent / "data"
        
        self.rules_file = Path(rules_file) if rules_file else base_dir / "style_rules.json"
        self.banned_file = Path(banned_file) if banned_file else base_dir / "banned_phrases.json"
        
        self._load_rules()
    
    def _load_rules(self) -> None:
        """Load rules from JSON files."""
        # Load style rules
        if self.rules_file.exists():
            with open(self.rules_file, "r", encoding="utf-8") as f:
                self.rules = json.load(f)
        else:
            self.rules = {
                "max_comment_length": 300,
                "min_comment_length": 10,
                "emoji_rules": {"max_emojis": 2, "allowed_positions": ["inline"]},
                "required_tone": ["friendly", "expert", "direct"],
            }
        
        # Load banned phrases
        if self.banned_file.exists():
            with open(self.banned_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.banned_phrases = data if isinstance(data, list) else data.get("banned_phrases", [])
        else:
            self.banned_phrases = [
                "I think",
                "In my opinion",
                "To be honest",
                "Basically,",
                "Actually,",
            ]
        
        self.filler_phrases = DEFAULT_FILLERS
        
        logger.info(f"[GUARDRAILS] Loaded {len(self.banned_phrases)} banned phrases")
    
    def enforce(
        self,
        text: str,
        strict: bool = False
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Enforce all style rules on text.
        
        Args:
            text: Input text to check/fix
            strict: If True, block on any violation; else fix what we can
            
        Returns:
            Tuple of (cleaned_text, list of violations)
        """
        violations = []
        cleaned = text
        
        # 1. Strip filler phrases (no-fluff rule)
        cleaned, filler_violations = self._strip_fillers(cleaned)
        violations.extend(filler_violations)
        
        # 2. Check banned phrases
        banned_violations = self._check_banned(cleaned)
        violations.extend(banned_violations)
        
        # 3. Check length
        length_violations = self._check_length(cleaned)
        violations.extend(length_violations)
        
        # 4. Check emoji rules
        emoji_violations = self._check_emojis(cleaned)
        violations.extend(emoji_violations)
        
        return cleaned, violations
    
    def _strip_fillers(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Strip filler phrases from beginning."""
        violations = []
        cleaned = text.strip()
        
        for filler in self.filler_phrases:
            if cleaned.lower().startswith(filler.lower()):
                violations.append({
                    "rule": "no_fluff",
                    "message": f"Stripped filler: '{filler}'",
                    "severity": "info"
                })
                cleaned = cleaned[len(filler):].lstrip()
        
        return cleaned, violations
    
    def _check_banned(self, text: str) -> List[Dict[str, Any]]:
        """Check for banned phrases."""
        violations = []
        text_lower = text.lower()
        
        for phrase in self.banned_phrases:
            if phrase.lower() in text_lower:
                violations.append({
                    "rule": "banned_phrase",
                    "message": f"Contains banned phrase: '{phrase}'",
                    "severity": "warning"
                })
        
        return violations
    
    def _check_length(self, text: str) -> List[Dict[str, Any]]:
        """Check length constraints."""
        violations = []
        
        max_len = self.rules.get("max_comment_length", 300)
        min_len = self.rules.get("min_comment_length", 10)
        
        if len(text) > max_len:
            violations.append({
                "rule": "max_length",
                "message": f"Text too long: {len(text)} > {max_len}",
                "severity": "error"
            })
        
        if len(text) < min_len:
            violations.append({
                "rule": "min_length",
                "message": f"Text too short: {len(text)} < {min_len}",
                "severity": "warning"
            })
        
        return violations
    
    def _check_emojis(self, text: str) -> List[Dict[str, Any]]:
        """Check emoji rules (inline only, not at end)."""
        violations = []
        emoji_rules = self.rules.get("emoji_rules", {})
        
        # Simple emoji pattern
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "]+",
            flags=re.UNICODE
        )
        
        emojis = emoji_pattern.findall(text)
        max_emojis = emoji_rules.get("max_emojis", 2)
        
        if len(emojis) > max_emojis:
            violations.append({
                "rule": "max_emojis",
                "message": f"Too many emojis: {len(emojis)} > {max_emojis}",
                "severity": "warning"
            })
        
        # Check if emoji at end only (violation if inline required)
        allowed_positions = emoji_rules.get("allowed_positions", ["inline"])
        if "inline" in allowed_positions and text.rstrip() != text.rstrip("".join(emojis)):
            # Emoji at end - check if that's not allowed
            if "end" not in allowed_positions and emojis:
                # Check if ALL emojis are at end
                text_stripped = text.rstrip()
                if text_stripped.endswith(tuple(emojis)):
                    violations.append({
                        "rule": "emoji_position",
                        "message": "Emojis should be inline, not at end",
                        "severity": "info"
                    })
        
        return violations
    
    def is_valid(self, text: str) -> bool:
        """Check if text passes all rules without errors."""
        _, violations = self.enforce(text)
        return not any(v.get("severity") == "error" for v in violations)
    
    def get_violations_summary(self, violations: List[Dict[str, Any]]) -> str:
        """Get human-readable summary of violations."""
        if not violations:
            return "No violations"
        
        return "; ".join(v["message"] for v in violations)


# Optional: NeMo Guardrails integration
NEMO_ENV_PATH = "E:/HoloIndex/nemo_env/Lib/site-packages"


def get_nemo_guardrails():
    """
    Get NeMo Guardrails instance if available.

    Checks both local venv and dedicated NeMo venv at E:/HoloIndex/nemo_env.

    Returns:
        RailsConfig instance or None
    """
    import sys

    # Try local import first
    try:
        from nemoguardrails import RailsConfig, LLMRails
        logger.info("[GUARDRAILS] NeMo loaded from local environment")
    except ImportError:
        # Try NeMo venv
        if NEMO_ENV_PATH not in sys.path:
            sys.path.insert(0, NEMO_ENV_PATH)
        try:
            from nemoguardrails import RailsConfig, LLMRails
            logger.info("[GUARDRAILS] NeMo loaded from E:/HoloIndex/nemo_env")
        except ImportError:
            logger.debug("[GUARDRAILS] nemoguardrails not installed")
            return None

    try:
        config_path = Path(__file__).parent.parent / "config" / "guardrails"
        if config_path.exists():
            config = RailsConfig.from_path(str(config_path))
            return LLMRails(config)
        else:
            logger.debug(f"[GUARDRAILS] Config path not found: {config_path}")
    except Exception as e:
        logger.warning(f"[GUARDRAILS] Failed to load NeMo: {e}")

    return None


def is_nemo_available() -> bool:
    """Check if NeMo Guardrails is available for import."""
    import sys

    try:
        from nemoguardrails import RailsConfig
        return True
    except ImportError:
        pass

    # Try NeMo venv
    if NEMO_ENV_PATH not in sys.path:
        sys.path.insert(0, NEMO_ENV_PATH)
    try:
        from nemoguardrails import RailsConfig
        return True
    except ImportError:
        return False


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Style Guardrails Test")
    print("=" * 60)
    
    sg = StyleGuardrails()
    
    test_cases = [
        "Sure! I think this is great!",
        "The visa process in Japan requires a sponsor.",
        "A" * 350,  # Too long
        "Hi 😀😀😀😀😀",  # Too many emojis
    ]
    
    for text in test_cases:
        cleaned, violations = sg.enforce(text)
        print(f"\nInput: {text[:50]}...")
        print(f"Output: {cleaned[:50]}...")
        print(f"Violations: {sg.get_violations_summary(violations)}")
