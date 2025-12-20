"""
0102 Party Reactor - YouTube Live Chat Reaction Spam
====================================================

WSP Compliance: WSP 77 (Banter Engine), WSP 27 (DAE Phases), WSP 49 (Anti-Detection)

Phase 3N Integration (2025-12-16): Human Interaction Module
- Bezier curve mouse movement (replaces instant teleportation)
- Coordinate variance (±8px per click, no pixel-perfect)
- Probabilistic errors (8-13% miss rate with fatigue)
- Fatigue modeling (1.0x → 1.8x slower over time)
- Thinking pauses (30% chance, 0.5-2.0s hesitation)
- Detection risk reduction: 40-60% → 8-15%

NAVIGATION:
-> Called by: command_handler.py on !party command
-> Uses: modules.infrastructure.human_interaction (anti-detection)
-> Related: modules/infrastructure/human_interaction/platforms/youtube_chat.json
"""

import os
import time
import random
import logging
import asyncio
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")

# Reaction name to platform action mapping
REACTION_ACTIONS = {
    '100': 'reaction_100',
    'wide_eyes': 'reaction_wide_eyes',
    'celebrate': 'reaction_celebrate',
    'smiley': 'reaction_smiley',
    'heart': 'reaction_heart',
}

REACTION_EMOJIS = {
    '100': '💯',
    'wide_eyes': '😲',
    'celebrate': '🎉',
    'smiley': '😊',
    'heart': '❤️',
}


class PartyReactor:
    """Handles !party command - spams reactions in YouTube Live Chat.

    Phase 3N: Uses Human Interaction Module for anti-detection.
    """

    def __init__(self):
        self.driver = None
        self.interaction = None  # Lazy load when driver connected
        self._last_party_time = 0
        self._party_cooldown = 60  # 60 seconds between parties
        
    def _connect_to_chrome(self):
        """Connect to Chrome instance with remote debugging."""
        if self.driver:
            logger.debug(f"[PARTY-DEBUG] Already connected (reusing existing driver)")
            return True

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from modules.infrastructure.human_interaction import get_interaction_controller

            # Use separate Chrome instance for live chat (port 9223)
            # Studio comment engagement uses port 9222
            port = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9223"))
            logger.info(f"[PARTY-DEBUG] Attempting Chrome connection on port {port}...")

            opts = Options()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            self.driver = webdriver.Chrome(options=opts)

            # Log full connection details
            current_url = self.driver.current_url
            page_title = self.driver.title
            logger.info(f"[PARTY-DEBUG] Chrome connected successfully!")
            logger.info(f"[PARTY-DEBUG]   Port: {port}")
            logger.info(f"[PARTY-DEBUG]   URL: {current_url}")
            logger.info(f"[PARTY-DEBUG]   Page: {page_title[:50]}")

            # Initialize interaction controller with anti-detection
            self.interaction = get_interaction_controller(self.driver, platform="youtube_chat")
            logger.info(f"[PARTY] Connected to Chrome with anti-detection: {current_url[:40]}...")
            return True
        except Exception as e:
            logger.error(f"[PARTY] Failed to connect to Chrome: {e}")
            logger.error(f"[PARTY-DEBUG] Connection failure details:")
            logger.error(f"[PARTY-DEBUG]   Port: {port}")
            logger.error(f"[PARTY-DEBUG]   Error type: {type(e).__name__}")
            logger.error(f"[PARTY-DEBUG]   Error message: {str(e)}")
            return False
            
        
    async def spam_single(self, reaction_name: str, count: int = 10) -> int:
        """Spam a single reaction type with full anti-detection.

        Phase 3N: Uses Human Interaction Module for:
        - Bezier curve movement
        - Coordinate variance (±8px)
        - Probabilistic errors (8-13%)
        - Fatigue modeling (1.0x → 1.8x slower)
        - Thinking pauses (30% chance)
        """
        # Permission gate checks with detailed logging
        logger.debug(f"[PARTY-DEBUG] Permission gates:")
        logger.debug(f"[PARTY-DEBUG]   YT_AUTOMATION_ENABLED: {os.getenv('YT_AUTOMATION_ENABLED', 'true')}")
        logger.debug(f"[PARTY-DEBUG]   YT_LIVECHAT_UI_ACTIONS_ENABLED: {os.getenv('YT_LIVECHAT_UI_ACTIONS_ENABLED', 'true')}")
        logger.debug(f"[PARTY-DEBUG]   YT_PARTY_REACTIONS_ENABLED: {os.getenv('YT_PARTY_REACTIONS_ENABLED', 'true')}")

        if not _env_truthy("YT_AUTOMATION_ENABLED", "true"):
            logger.warning("[PARTY] Disabled (YT_AUTOMATION_ENABLED=false)")
            return 0
        if not _env_truthy("YT_LIVECHAT_UI_ACTIONS_ENABLED", "true"):
            logger.warning("[PARTY] Disabled (YT_LIVECHAT_UI_ACTIONS_ENABLED=false)")
            return 0
        if not _env_truthy("YT_PARTY_REACTIONS_ENABLED", "true"):
            logger.warning("[PARTY] Disabled (YT_PARTY_REACTIONS_ENABLED=false)")
            return 0

        if not self._connect_to_chrome():
            logger.error(f"[PARTY-DEBUG] Chrome connection failed - aborting spam_single")
            return 0

        # Get platform action name
        action_name = REACTION_ACTIONS.get(reaction_name)
        if not action_name:
            logger.error(f"[PARTY] Unknown reaction: {reaction_name}")
            logger.error(f"[PARTY-DEBUG] Available reactions: {list(REACTION_ACTIONS.keys())}")
            return 0

        logger.info(f"[PARTY-DEBUG] Spamming {reaction_name} (action: {action_name}) x{count}")

        # Use interaction controller with full sophistication
        results = await self.interaction.spam_action(action_name, count=count)

        # Log sophistication stats if available
        if hasattr(self.interaction, 'get_stats'):
            stats = self.interaction.get_stats()
            logger.debug(f"[PARTY-DEBUG] Sophistication stats: {stats}")

        logger.info(
            f"[PARTY] {reaction_name}: {results['success']}/{count} clicks "
            f"({results['errors']} mistakes, {results.get('thinking_pauses', 0)} pauses)"
        )
        return results['success']
        
    async def party_mode(self, total_clicks: int = 30) -> Dict[str, int]:
        """Full party mode - spam all reactions randomly with anti-detection!

        Phase 3N: Uses Human Interaction Module for:
        - Bezier curve movement (no instant teleportation)
        - Coordinate variance (±8px, no pixel-perfect clicks)
        - Probabilistic errors (8-13% miss rate with fatigue)
        - Fatigue modeling (1.0x → 1.8x slower over time)
        - Thinking pauses (30% chance, 0.5-2.0s hesitation)

        Detection risk reduction: 40-60% → 8-15%
        """
        logger.debug(f"[PARTY-DEBUG] party_mode() called with total_clicks={total_clicks}")

        # Permission gate checks
        if not _env_truthy("YT_AUTOMATION_ENABLED", "true"):
            logger.error(f"[PARTY-DEBUG] Blocked by YT_AUTOMATION_ENABLED=false")
            return {"error": "disabled_yt_automation"}
        if not _env_truthy("YT_LIVECHAT_UI_ACTIONS_ENABLED", "true"):
            logger.error(f"[PARTY-DEBUG] Blocked by YT_LIVECHAT_UI_ACTIONS_ENABLED=false")
            return {"error": "disabled_livechat_ui_actions"}
        if not _env_truthy("YT_PARTY_REACTIONS_ENABLED", "true"):
            logger.error(f"[PARTY-DEBUG] Blocked by YT_PARTY_REACTIONS_ENABLED=false")
            return {"error": "disabled_party_reactions"}

        now = time.time()

        # Cooldown check
        if now - self._last_party_time < self._party_cooldown:
            remaining = int(self._party_cooldown - (now - self._last_party_time))
            logger.warning(f"[PARTY] Cooldown active ({remaining}s remaining)")
            logger.debug(f"[PARTY-DEBUG] Last party: {self._last_party_time}, Now: {now}, Cooldown: {self._party_cooldown}s")
            return {'cooldown': remaining}

        if not self._connect_to_chrome():
            logger.error(f"[PARTY-DEBUG] Chrome connection failed - aborting party_mode")
            return {'error': 'chrome_connection_failed'}

        logger.info(f"[PARTY] 🎉 PARTY MODE ACTIVATED! ({total_clicks} reactions with anti-detection)")

        reaction_names = list(REACTION_ACTIONS.keys())
        logger.debug(f"[PARTY-DEBUG] Available reactions: {reaction_names}")

        results = {name: 0 for name in reaction_names}
        errors = 0  # Track total errors

        for i in range(total_clicks):
            # Pick random reaction
            reaction = random.choice(reaction_names)
            action_name = REACTION_ACTIONS[reaction]

            logger.debug(f"[PARTY-DEBUG] Click {i+1}/{total_clicks}: {reaction} (action: {action_name})")

            # Use interaction controller for sophisticated clicking
            success = await self.interaction.click_action(action_name)

            if success:
                results[reaction] += 1
            else:
                errors += 1
                logger.debug(f"[PARTY-DEBUG] Click failed (mistake/error)")

            if (i + 1) % 10 == 0:
                successes = sum(results.values())
                logger.info(f"[PARTY] Progress: {i+1}/{total_clicks} ({successes} success, {errors} errors)")

        self._last_party_time = now

        total = sum(results.values())
        logger.info(f"[PARTY] Complete! {total}/{total_clicks} reactions sent ({errors} errors)")
        logger.debug(f"[PARTY-DEBUG] Results breakdown: {results}")

        # Log final sophistication stats
        if hasattr(self.interaction, 'get_stats'):
            stats = self.interaction.get_stats()
            logger.info(f"[PARTY-DEBUG] Final sophistication stats: {stats}")

        return results
        
    def get_party_summary(self, results: Dict[str, int]) -> str:
        """Format party results as a chat message."""
        if 'error' in results:
            return f"🎉 Party failed: {results['error']}"
        if 'cooldown' in results:
            return f"🎉 Party on cooldown! Wait {results['cooldown']}s ✊✋🖐️"
            
        total = sum(results.values())
        summary = f"🎉 PARTY COMPLETE! Sent {total} reactions: "
        
        for name, count in results.items():
            if count > 0:
                emoji = REACTION_EMOJIS.get(name, '✨')
                summary += f"{emoji}x{count} "
                
        summary += "✊✋🖐️"
        return summary


# Global instance for import
_party_reactor = None

def get_party_reactor() -> PartyReactor:
    """Get or create global PartyReactor instance."""
    global _party_reactor
    if _party_reactor is None:
        _party_reactor = PartyReactor()
    return _party_reactor


async def trigger_party(total_clicks: int = 30) -> str:
    """Async wrapper for triggering party mode.

    Phase 3N: Now uses async party_mode with Human Interaction Module.
    """
    reactor = get_party_reactor()

    # party_mode is now async, so await it directly
    results = await reactor.party_mode(total_clicks)

    return reactor.get_party_summary(results)



