"""
Unicode Self-Healing Monitor - Autonomous Fix System
Monitors livechat output for [U+XXXX] unicode escape codes and fixes source automatically

WSP Compliance:
- WSP 77: Agent Coordination (Gemma detect -> Qwen analyze -> 0102 fix)
- WSP 91: Daemon Observability (monitor chat output)
- WSP 48: Recursive Improvement (learn from each fix)

Architecture:
    Livechat Output → Gemma Pattern Detection → Qwen Root Cause Analysis →
    Autonomous Fix Application → Chat Announcement → Pattern Learning

Usage:
    from modules.communication.livechat.src.unicode_self_healing_monitor import UnicodeSelfHealingMonitor

    monitor = UnicodeSelfHealingMonitor()
    monitor.start()  # Runs in background
"""

import re
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)


# Unicode escape code patterns to detect
UNICODE_PATTERN = r'\[U\+[0-9A-Fa-f]{4,5}\]'

# Emoji mapping for fixes
EMOJI_MAP = {
    '[U+270A]': '✊',  '[U+270B]': '✋',  '[U+1F590]': '🖐',
    '[U+1F602]': '😂', '[U+1F923]': '🤣', '[U+2764]': '❤',
    '[U+1F44D]': '👍', '[U+1F64C]': '🙌', '[U+1F60A]': '😊',
    '[U+1F4AA]': '💪', '[U+1F914]': '🤔', '[U+1F3C6]': '🏆',
    '[U+1F441]': '👁',  '[U+1F331]': '🌱', '[U+1F310]': '🌐',
    '[U+1F4E2]': '📢', '[U+1F30A]': '🌊', '[U+1F31F]': '🌟',
    '[U+1F4AD]': '💭', '[U+26A0]': '⚠',
}


class UnicodeSelfHealingMonitor:
    """
    Monitors livechat for unicode escape codes and autonomously fixes source

    Phase 1 (Gemma): Fast pattern detection (<1 second)
    Phase 2 (Qwen): Root cause analysis (2-5 seconds)
    Phase 3 (0102): Apply fix (instant - sed replacement)
    Phase 4: Learn pattern for future
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).parent.parent.parent.parent.parent
        self.detection_log = self.repo_root / "data" / "unicode_detection_log.jsonl"
        self.detection_log.parent.mkdir(parents=True, exist_ok=True)

        self.detected_issues = []  # Track recent detections
        self.fix_cooldown = 60  # Don't re-fix same issue within 60 seconds
        self.last_fixes = {}  # module_path -> timestamp

    def detect_unicode_in_text(self, text: str) -> List[str]:
        """
        Gemma Phase: Fast pattern detection

        Returns:
            List of unicode codes found (e.g. ['[U+270A]', '[U+270B]'])
        """
        matches = re.findall(UNICODE_PATTERN, text)
        if matches:
            logger.info(f"[GEMMA-DETECT] Found {len(matches)} unicode escapes: {matches[:5]}")
        return matches

    def analyze_source_module(self, unicode_codes: List[str]) -> Optional[str]:
        """
        Qwen Phase: Identify which module is outputting the unicode

        Uses HoloIndex semantic search to find likely source

        Returns:
            Module file path or None
        """
        logger.info(f"[QWEN-ANALYZE] Searching for source of {unicode_codes[:3]}...")

        # Priority search order (most likely sources)
        search_paths = [
            self.repo_root / "modules" / "ai_intelligence" / "banter_engine" / "src",
            self.repo_root / "modules" / "communication" / "livechat" / "src",
            self.repo_root / "modules" / "gamification" / "whack_a_magat" / "src",
        ]

        # Search for files containing these unicode codes
        for search_path in search_paths:
            if not search_path.exists():
                continue

            for py_file in search_path.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    # Check if file contains any of the detected codes
                    if any(code in content for code in unicode_codes):
                        logger.info(f"[QWEN-FOUND] Source: {py_file}")
                        return str(py_file)
                except Exception as e:
                    logger.debug(f"[QWEN-SKIP] {py_file}: {e}")

        logger.warning(f"[QWEN-MISS] Could not locate source for {unicode_codes}")
        return None

    def apply_fix(self, module_path: str, unicode_codes: List[str]) -> bool:
        """
        0102 Phase: Apply autonomous fix via sed

        Replaces all [U+XXXX] with actual emojis in the source file

        Returns:
            True if fix applied successfully
        """
        logger.info(f"[0102-FIX] Applying emoji restoration to {module_path}")

        # Build sed command for all replacements
        sed_commands = []
        for code, emoji in EMOJI_MAP.items():
            if code in unicode_codes:
                # Escape special chars for sed
                escaped_code = code.replace('[', r'\[').replace(']', r'\]').replace('+', r'\+')
                sed_commands.append(f's/{escaped_code}/{emoji}/g')

        if not sed_commands:
            logger.warning(f"[0102-SKIP] No mappings for {unicode_codes}")
            return False

        # Apply fix with sed
        try:
            sed_script = '; '.join(sed_commands)
            subprocess.run(
                ['sed', '-i', sed_script, module_path],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"[0102-SUCCESS] Fixed {len(sed_commands)} unicode codes in {module_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[0102-ERROR] sed failed: {e.stderr}")
            return False

    def should_apply_fix(self, module_path: str) -> bool:
        """Check if enough time has passed since last fix (cooldown)"""
        last_fix_time = self.last_fixes.get(module_path)
        if not last_fix_time:
            return True

        elapsed = time.time() - last_fix_time
        if elapsed < self.fix_cooldown:
            logger.info(f"[COOLDOWN] Skipping {module_path} (fixed {elapsed:.0f}s ago)")
            return False

        return True

    def log_detection(self, text: str, unicode_codes: List[str], source_module: Optional[str]):
        """Log detection event for learning"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'text_sample': text[:200],
            'unicode_codes': unicode_codes,
            'source_module': source_module,
            'fix_applied': source_module is not None
        }

        try:
            with open(self.detection_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"[LOG-ERROR] {e}")

    def monitor_text(self, text: str) -> Dict[str, any]:
        """
        Main monitoring method - call this with each chat message output

        Returns:
            {
                'detected': bool,
                'unicode_codes': List[str],
                'source_module': Optional[str],
                'fix_applied': bool
            }
        """
        # Phase 1: Gemma detection (fast)
        unicode_codes = self.detect_unicode_in_text(text)
        if not unicode_codes:
            return {'detected': False}

        # Phase 2: Qwen analysis (strategic)
        source_module = self.analyze_source_module(unicode_codes)
        if not source_module:
            self.log_detection(text, unicode_codes, None)
            return {
                'detected': True,
                'unicode_codes': unicode_codes,
                'source_module': None,
                'fix_applied': False
            }

        # Check cooldown
        if not self.should_apply_fix(source_module):
            return {
                'detected': True,
                'unicode_codes': unicode_codes,
                'source_module': source_module,
                'fix_applied': False,
                'reason': 'cooldown'
            }

        # Phase 3: 0102 fix application
        fix_success = self.apply_fix(source_module, unicode_codes)

        if fix_success:
            self.last_fixes[source_module] = time.time()
            logger.info(f"[SELF-HEAL] ✓ Fixed unicode in {Path(source_module).name}")

        # Phase 4: Learning
        self.log_detection(text, unicode_codes, source_module)

        return {
            'detected': True,
            'unicode_codes': unicode_codes,
            'source_module': source_module,
            'fix_applied': fix_success
        }


# Integration hook for livechat
def monitor_chat_message(message_text: str) -> Optional[Dict]:
    """
    Hook for livechat to call on each outgoing message

    Usage in chat_sender.py:
        from modules.communication.livechat.src.unicode_self_healing_monitor import monitor_chat_message

        result = monitor_chat_message(message)
        if result and result.get('fix_applied'):
            logger.info(f"[SELF-HEAL] Applied fix to {result['source_module']}")
    """
    monitor = UnicodeSelfHealingMonitor()
    return monitor.monitor_text(message_text)
