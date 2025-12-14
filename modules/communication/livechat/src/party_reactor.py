"""
0102 Party Reactor - YouTube Live Chat Reaction Spam
====================================================

WSP Compliance: WSP 77 (Banter Engine), WSP 27 (DAE Phases)

Coordinates discovered via grid overlay:
- Toggle popup: x=359, y=759 (hover to open)
- 100%:         x=361, y=735
- Wide eyes:    x=357, y=708  
- Celebrate:    x=358, y=669
- Smiley:       x=357, y=635
- Heart:        x=359, y=599

NAVIGATION:
-> Called by: command_handler.py on !party command
-> Uses: Selenium WebDriver connection to Chrome
-> Related: modules/communication/livechat/skills/party_reactions.json
"""

import os
import time
import random
import logging
import asyncio
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Exact coordinates from grid overlay testing
TOGGLE = (359, 759)  # Hover here to open popup

REACTIONS = {
    '100':       (361, 735),
    'wide_eyes': (357, 708),
    'celebrate': (358, 669),
    'smiley':    (357, 635),
    'heart':     (359, 599),
}

REACTION_EMOJIS = {
    '100': '💯',
    'wide_eyes': '😲',
    'celebrate': '🎉',
    'smiley': '😊',
    'heart': '❤️',
}


class PartyReactor:
    """Handles !party command - spams reactions in YouTube Live Chat."""
    
    def __init__(self):
        self.driver = None
        self.in_iframe = False
        self._last_party_time = 0
        self._party_cooldown = 60  # 60 seconds between parties
        
    def _connect_to_chrome(self):
        """Connect to Chrome instance with remote debugging."""
        if self.driver:
            return True
            
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            port = int(os.getenv("FOUNDUPS_CHROME_PORT", "9222"))
            opts = Options()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            self.driver = webdriver.Chrome(options=opts)
            logger.info(f"[PARTY] Connected to Chrome: {self.driver.current_url[:40]}...")
            return True
        except Exception as e:
            logger.error(f"[PARTY] Failed to connect to Chrome: {e}")
            return False
            
    def _switch_to_chat_iframe(self):
        """Switch to the YouTube live chat iframe."""
        if self.in_iframe:
            return True
            
        try:
            from selenium.webdriver.common.by import By
            
            self.driver.switch_to.default_content()
            iframe = self.driver.find_element(By.CSS_SELECTOR, 'iframe#chatframe')
            self.driver.switch_to.frame(iframe)
            self.in_iframe = True
            logger.info("[PARTY] Switched to chat iframe")
            return True
        except Exception as e:
            logger.warning(f"[PARTY] No iframe found: {e}")
            self.in_iframe = False
            return False
            
    def _mouse_action(self, x: int, y: int, click: bool = True) -> bool:
        """Perform mouse hover and optionally click at coordinates."""
        js = f"""
        var el = document.elementFromPoint({x}, {y});
        if (el) {{
            ['mousemove', 'mouseenter', 'mouseover'].forEach(function(evtType) {{
                el.dispatchEvent(new MouseEvent(evtType, {{
                    bubbles: true, cancelable: true,
                    clientX: {x}, clientY: {y}, view: window
                }}));
            }});
            
            if ({'true' if click else 'false'}) {{
                el.dispatchEvent(new MouseEvent('mousedown', {{bubbles: true, clientX: {x}, clientY: {y}}}));
                el.dispatchEvent(new MouseEvent('mouseup', {{bubbles: true, clientX: {x}, clientY: {y}}}));
                el.dispatchEvent(new MouseEvent('click', {{bubbles: true, clientX: {x}, clientY: {y}}}));
            }}
            return true;
        }}
        return false;
        """
        try:
            return self.driver.execute_script(js)
        except Exception as e:
            logger.warning(f"[PARTY] Mouse action failed at ({x}, {y}): {e}")
            return False
            
    def _open_popup(self) -> bool:
        """Hover at toggle position to open reaction popup."""
        return self._mouse_action(TOGGLE[0], TOGGLE[1], click=False)
        
    def _click_reaction(self, reaction_name: str) -> bool:
        """Click a specific reaction."""
        if reaction_name not in REACTIONS:
            return False
        x, y = REACTIONS[reaction_name]
        return self._mouse_action(x, y, click=True)
        
    def spam_single(self, reaction_name: str, count: int = 10) -> int:
        """Spam a single reaction type."""
        if not self._connect_to_chrome():
            return 0
        if not self._switch_to_chat_iframe():
            return 0
            
        success = 0
        for i in range(count):
            # Re-open popup every 3 clicks
            if i % 3 == 0:
                self._open_popup()
                time.sleep(0.2)
                
            if self._click_reaction(reaction_name):
                success += 1
                
            time.sleep(random.uniform(0.1, 0.25))
            
        logger.info(f"[PARTY] {reaction_name}: {success}/{count} clicks")
        return success
        
    def party_mode(self, total_clicks: int = 30) -> Dict[str, int]:
        """Full party mode - spam all reactions randomly!"""
        now = time.time()
        
        # Cooldown check
        if now - self._last_party_time < self._party_cooldown:
            remaining = int(self._party_cooldown - (now - self._last_party_time))
            logger.warning(f"[PARTY] Cooldown active ({remaining}s remaining)")
            return {'cooldown': remaining}
            
        if not self._connect_to_chrome():
            return {'error': 'chrome_connection_failed'}
        if not self._switch_to_chat_iframe():
            return {'error': 'iframe_switch_failed'}
            
        logger.info(f"[PARTY] 🎉 PARTY MODE ACTIVATED! ({total_clicks} reactions)")
        
        reaction_names = list(REACTIONS.keys())
        results = {name: 0 for name in reaction_names}
        
        for i in range(total_clicks):
            # Pick random reaction
            reaction = random.choice(reaction_names)
            
            # Open popup
            self._open_popup()
            time.sleep(0.15)
            
            # Click reaction
            if self._click_reaction(reaction):
                results[reaction] += 1
                
            if (i + 1) % 10 == 0:
                logger.info(f"[PARTY] Progress: {i+1}/{total_clicks}")
                
            time.sleep(random.uniform(0.1, 0.25))
            
        self._last_party_time = now
        
        total = sum(results.values())
        logger.info(f"[PARTY] Complete! {total}/{total_clicks} reactions sent")
        
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
    """Async wrapper for triggering party mode."""
    reactor = get_party_reactor()
    
    # Run in thread to avoid blocking
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, reactor.party_mode, total_clicks)
    
    return reactor.get_party_summary(results)

