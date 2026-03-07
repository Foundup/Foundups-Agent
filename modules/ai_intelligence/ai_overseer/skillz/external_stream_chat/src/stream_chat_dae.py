"""
External Stream Chat DAE - DOM-based engagement with public YouTube Live streams.

WSP Compliance:
    - WSP 27: DAE Architecture (4-phase execution)
    - WSP 77: Agent Coordination (OpenClaw integration)
    - WSP 91: Observability (engagement telemetry)

This enables OpenClaw/AI Overseer to engage in ANY public stream's chat,
not just channels we own. Uses Selenium DOM automation since we can't use
YouTube API for streams we don't own.

Usage:
    chat = ExternalStreamChat(url="https://www.youtube.com/watch?v=...")
    await chat.connect()
    await chat.send_message("Hello!")
    await chat.party()  # Click hearts
"""

import asyncio
import logging
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Configuration
BROWSER_PORT = int(os.getenv("EXTERNAL_CHAT_PORT", "9223"))
SEND_DELAY = float(os.getenv("EXTERNAL_CHAT_SEND_DELAY", "2.0"))
PARTY_INTERVAL = float(os.getenv("EXTERNAL_CHAT_PARTY_INTERVAL", "5.0"))
MONITOR_INTERVAL = float(os.getenv("EXTERNAL_CHAT_MONITOR_INTERVAL", "3.0"))

# Trigger commands to watch for in chat
TRIGGER_COMMANDS = {
    '!party': 'party',       # Click hearts
    '!based': 'party',       # Alias for party
    '!hearts': 'party',      # Alias for party
    '!100': 'react_100',     # React with 100 emoji (future)
    '!celebrate': 'react_celebrate',  # React with celebrate (future)
}

# Telemetry
TELEMETRY_DIR = Path(__file__).parent.parent / "memory" / "external_chat_sessions"
TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ChatMessage:
    """Represents a chat message from the stream."""
    author: str
    text: str
    timestamp: datetime
    is_member: bool = False
    is_moderator: bool = False


class ExternalStreamChat:
    """
    DOM-based engagement with external YouTube Live streams.

    Architecture:
    - Phase -1 (Signal): Chat messages via DOM query
    - Phase 0 (Knowledge): Stream info, chat history
    - Phase 1 (Protocol): Message composition, timing
    - Phase 2 (Agentic): Send messages, click reactions
    """

    # YouTube Live Chat DOM Selectors
    SELECTORS = {
        # Chat input field (multiple fallbacks)
        'chat_input': "#input.yt-live-chat-text-input-field-renderer",
        'chat_input_contenteditable': "div#input[contenteditable='true']",
        'chat_input_placeholder': "[placeholder*='Chat']",
        'chat_frame': "iframe#chatframe",

        # Send button
        'send_button': "#send-button button",
        'send_button_alt': "yt-button-renderer#send-button button",
        'send_icon': "#send-button yt-icon",

        # Reactions panel (hearts, emojis) - LEFT of chat input
        'reaction_panel': "yt-live-chat-action-panel-renderer",
        'emoji_picker_button': "#emoji-picker-button",
        'heart_emoji': "[aria-label*='heart' i], [aria-label*='Heart']",
        'like_button': "[aria-label*='like' i], [aria-label*='Like']",

        # Super Chat/Sticker buttons (also in action panel)
        'super_chat_button': "#super-chat-button",
        'super_sticker_button': "#super-sticker-button",

        # Chat messages
        'chat_messages': "yt-live-chat-text-message-renderer",
        'author_name': "#author-name",
        'message_text': "#message",
        'chat_item': "yt-live-chat-item-list-renderer #items",
    }

    # Pixel offsets from chat input to reaction buttons
    REACTION_OFFSET = {
        'heart_x': -40,  # 40px left of chat input
        'heart_y': 0,    # Same vertical level
        'emoji_x': -80,  # 80px left for emoji picker
    }

    # Absolute coordinates for 1842x1004 viewport (M2M reference)
    # These are fallback when DOM selectors fail (iframe isolation)
    ABSOLUTE_COORDS = {
        'chat_input': (1260, 657),
        'send_button': (1430, 657),
        'heart_button': (1432, 657),
        'viewport': (1842, 1004),
    }

    # Full reaction coordinates from PartyReactor (livechat module)
    # All 5 emotions for proper !party mode: 💯 😲 🎉 😊 ❤️
    REACTION_COORDS = {
        '100': (359, 790),       # 💯
        'wide_eyes': (359, 754), # 😲
        'celebrate': (359, 718), # 🎉
        'smiley': (359, 682),    # 😊
        'heart': (359, 646),     # ❤️
    }

    REACTION_EMOJIS = {
        '100': '💯',
        'wide_eyes': '😲',
        'celebrate': '🎉',
        'smiley': '😊',
        'heart': '❤️',
    }

    def __init__(self, url: Optional[str] = None, browser_port: int = BROWSER_PORT):
        """
        Initialize external stream chat.

        Args:
            url: YouTube Live URL to engage with
            browser_port: Selenium debug port (default: 9223)
        """
        self.url = url
        self.browser_port = browser_port
        self.driver = None
        self.human = None
        self.connected = False
        self.chat_input_rect = None
        self.session_start = None
        self.messages_sent = 0
        self.reactions_clicked = 0
        self.in_iframe = False  # Track if we've switched to chat iframe
        self.monitoring = False  # Monitor mode active
        self.seen_messages = set()  # Track seen messages to avoid re-triggers
        self.triggers_executed = 0  # Count of trigger commands executed

    async def connect(self) -> bool:
        """Connect to browser and navigate to stream."""
        try:
            from selenium import webdriver
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # Connect to existing Edge debug session
            options = EdgeOptions()
            options.add_experimental_option("debuggerAddress", f"localhost:{self.browser_port}")

            self.driver = webdriver.Edge(options=options)
            logger.info(f"[OK] Connected to Edge on port {self.browser_port}")

            # Try to load human behavior for anti-detection
            try:
                from modules.infrastructure.foundups_selenium.src.human_behavior import get_human_behavior
                self.human = get_human_behavior(self.driver)
                logger.info("[OK] Human behavior simulation loaded")
            except ImportError:
                logger.warning("[WARN] Human behavior simulation not available")
                self.human = None

            # Navigate to stream if URL provided
            if self.url:
                await self._navigate_to_stream()

            self.connected = True
            self.session_start = datetime.now()
            return True

        except Exception as e:
            logger.error(f"[FAIL] Failed to connect: {e}")
            return False

    async def _navigate_to_stream(self) -> bool:
        """Navigate to the stream URL and wait for chat to load."""
        if not self.url:
            return False

        try:
            logger.info(f"[NAV] Navigating to: {self.url}")
            self.driver.get(self.url)

            # Wait for page to load
            await asyncio.sleep(3)

            # Check if we need to switch to chat iframe
            chat_frame = self._find_element(self.SELECTORS['chat_frame'])
            if chat_frame:
                logger.info("[FRAME] Switching to chat iframe")
                self.driver.switch_to.frame(chat_frame)

            # Wait for chat input to appear
            await self._wait_for_chat_input()

            return True

        except Exception as e:
            logger.error(f"[FAIL] Navigation failed: {e}")
            return False

    async def _wait_for_chat_input(self, timeout: int = 30) -> bool:
        """Wait for chat input to become available."""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        selectors_to_try = [
            self.SELECTORS['chat_input'],
            self.SELECTORS['chat_input_contenteditable'],
            self.SELECTORS['chat_input_placeholder'],
        ]

        for selector in selectors_to_try:
            try:
                wait = WebDriverWait(self.driver, timeout // len(selectors_to_try))
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

                # Store the chat input rect for pixel offset calculations
                self.chat_input_rect = element.rect
                logger.info(f"[OK] Chat input found: {selector}")
                logger.info(f"[POS] Chat input at x={self.chat_input_rect['x']}, y={self.chat_input_rect['y']}")
                return True

            except Exception:
                continue

        logger.warning("[WARN] Chat input not found - may need to sign in")
        return False

    def _find_element(self, selector: str):
        """Find element by CSS selector with error handling."""
        try:
            from selenium.webdriver.common.by import By
            return self.driver.find_element(By.CSS_SELECTOR, selector)
        except Exception:
            return None

    async def _switch_to_chat_iframe(self) -> bool:
        """Switch to chat iframe context if not already there."""
        if self.in_iframe:
            return True

        try:
            # Try to find and switch to chat iframe
            chat_frame = self._find_element(self.SELECTORS['chat_frame'])
            if chat_frame:
                self.driver.switch_to.frame(chat_frame)
                self.in_iframe = True
                logger.info("[IFRAME] Switched to chat iframe context")
                await asyncio.sleep(0.5)
                return True
            return False
        except Exception as e:
            logger.warning(f"[IFRAME] Could not switch to iframe: {e}")
            return False

    def _switch_to_default(self):
        """Switch back to main page context."""
        if self.in_iframe:
            try:
                self.driver.switch_to.default_content()
                self.in_iframe = False
                logger.info("[IFRAME] Switched back to main page")
            except Exception:
                pass

    async def _click_at_coordinates(self, x: int, y: int, randomize: bool = True) -> bool:
        """
        Click at absolute viewport coordinates.

        Used as fallback when DOM selectors fail due to iframe isolation.
        Coordinates are from M2M reference map at 1842x1004 viewport.

        Args:
            x: X coordinate
            y: Y coordinate
            randomize: Add +-3px randomization for anti-detection

        Returns:
            True if click was performed
        """
        try:
            from selenium.webdriver.common.action_chains import ActionChains

            # Add randomization for anti-detection
            if randomize:
                x += random.randint(-3, 3)
                y += random.randint(-3, 3)

            # Move to absolute position and click
            actions = ActionChains(self.driver)

            # First move to body element at (0,0), then offset to target
            body = self._find_element("body")
            if body:
                actions.move_to_element_with_offset(body, x, y)
                actions.click()
                actions.perform()
                logger.info(f"[COORD] Clicked at ({x}, {y})")
                return True

            logger.warning("[COORD] Could not find body element for coordinate click")
            return False

        except Exception as e:
            logger.error(f"[COORD] Coordinate click failed: {e}")
            return False

    async def _type_at_coordinates(self, x: int, y: int, text: str) -> bool:
        """
        Click at coordinates and type text.

        Args:
            x: X coordinate of input field
            y: Y coordinate of input field
            text: Text to type

        Returns:
            True if typing was successful
        """
        try:
            from selenium.webdriver.common.action_chains import ActionChains

            # Click to focus the input
            if not await self._click_at_coordinates(x, y):
                return False

            await asyncio.sleep(0.3)

            # Type with human-like delays
            actions = ActionChains(self.driver)
            for char in text:
                actions.send_keys(char)
                actions.pause(random.uniform(0.05, 0.15))  # 50-150ms per char
            actions.perform()

            logger.info(f"[COORD] Typed {len(text)} characters at ({x}, {y})")
            return True

        except Exception as e:
            logger.error(f"[COORD] Coordinate typing failed: {e}")
            return False

    async def send_message(self, text: str) -> bool:
        """
        Send a message to the stream chat.

        Tries DOM selectors first, falls back to coordinate-based clicking
        if iframe isolation prevents DOM access.

        Args:
            text: Message text to send

        Returns:
            True if message was sent successfully
        """
        if not self.connected:
            logger.error("[FAIL] Not connected to stream")
            return False

        if not text or not text.strip():
            logger.warning("[WARN] Cannot send empty message")
            return False

        try:
            # Try switching to chat iframe first
            await self._switch_to_chat_iframe()

            # Find chat input via DOM
            chat_input = None
            for selector in [self.SELECTORS['chat_input'],
                           self.SELECTORS['chat_input_contenteditable'],
                           self.SELECTORS['chat_input_placeholder']]:
                chat_input = self._find_element(selector)
                if chat_input:
                    break

            if chat_input:
                # DOM method - preferred
                if self.human:
                    self.human.human_click(chat_input)
                else:
                    chat_input.click()

                await asyncio.sleep(0.5)

                if self.human:
                    self.human.human_type(chat_input, text)
                else:
                    chat_input.send_keys(text)

                await asyncio.sleep(0.3)

                # Find and click send button
                send_button = None
                for selector in [self.SELECTORS['send_button'],
                               self.SELECTORS['send_button_alt'],
                               self.SELECTORS['send_icon']]:
                    send_button = self._find_element(selector)
                    if send_button:
                        break

                if send_button:
                    if self.human:
                        self.human.human_click(send_button)
                    else:
                        send_button.click()
                else:
                    from selenium.webdriver.common.keys import Keys
                    chat_input.send_keys(Keys.RETURN)

            else:
                # Coordinate fallback - iframe isolation
                logger.info("[COORD] DOM selectors failed, using coordinate fallback")
                self._switch_to_default()  # Exit iframe for absolute coords

                # Type at chat input coordinates
                coords = self.ABSOLUTE_COORDS
                if not await self._type_at_coordinates(coords['chat_input'][0],
                                                       coords['chat_input'][1],
                                                       text):
                    return False

                await asyncio.sleep(0.3)

                # Click send button
                if not await self._click_at_coordinates(coords['send_button'][0],
                                                        coords['send_button'][1]):
                    # Try Enter key as fallback
                    from selenium.webdriver.common.action_chains import ActionChains
                    from selenium.webdriver.common.keys import Keys
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.RETURN)
                    actions.perform()

            self.messages_sent += 1
            logger.info(f"[OK] Message sent: {text[:50]}...")

            # Anti-spam delay
            await asyncio.sleep(SEND_DELAY + random.uniform(0, 1))

            return True

        except Exception as e:
            logger.error(f"[FAIL] Failed to send message: {e}")
            return False

    async def party(self) -> bool:
        """
        Click the heart/reaction button (party mode).

        Strategy order:
        1. DOM selectors for heart/like buttons
        2. Pixel offset from chat input position
        3. Absolute coordinate fallback (M2M reference: 1432, 657)

        Returns:
            True if reaction was clicked successfully
        """
        if not self.connected:
            logger.error("[FAIL] Not connected to stream")
            return False

        try:
            from selenium.webdriver.common.action_chains import ActionChains

            # Try switching to chat iframe first
            await self._switch_to_chat_iframe()

            # Strategy 1: Try direct selector for heart/like buttons
            for selector in [self.SELECTORS['heart_emoji'],
                           self.SELECTORS['like_button'],
                           self.SELECTORS['emoji_picker_button']]:
                button = self._find_element(selector)
                if button:
                    if self.human:
                        self.human.human_click(button)
                    else:
                        button.click()
                    self.reactions_clicked += 1
                    logger.info("[PARTY] Clicked reaction button via DOM selector")
                    return True

            # Strategy 2: Use pixel offset from chat input
            if self.chat_input_rect:
                reaction_x = self.chat_input_rect['x'] + self.REACTION_OFFSET['heart_x']
                reaction_y = self.chat_input_rect['y'] + self.chat_input_rect['height'] // 2

                logger.info(f"[PARTY] Trying pixel offset: x={reaction_x}, y={reaction_y}")

                chat_input = self._find_element(self.SELECTORS['chat_input']) or \
                            self._find_element(self.SELECTORS['chat_input_contenteditable'])

                if chat_input:
                    actions = ActionChains(self.driver)
                    actions.move_to_element(chat_input)
                    actions.move_by_offset(self.REACTION_OFFSET['heart_x'], 0)
                    actions.click()
                    actions.perform()

                    self.reactions_clicked += 1
                    logger.info("[PARTY] Clicked via pixel offset from chat input")
                    return True

            # Strategy 3: Absolute coordinate fallback (M2M reference)
            logger.info("[PARTY] Using absolute coordinate fallback")
            self._switch_to_default()  # Exit iframe for absolute coords

            coords = self.ABSOLUTE_COORDS
            if await self._click_at_coordinates(coords['heart_button'][0],
                                                 coords['heart_button'][1]):
                self.reactions_clicked += 1
                logger.info(f"[PARTY] Clicked at absolute coords ({coords['heart_button'][0]}, {coords['heart_button'][1]})")
                return True

            logger.warning("[WARN] All party click strategies failed")
            return False

        except Exception as e:
            logger.error(f"[FAIL] Party click failed: {e}")
            return False

    async def party_full(self, clicks_per_emoji: int = 2) -> Dict[str, int]:
        """
        Full party mode - spam ALL 5 emotions like PartyReactor.

        Cycles through: 💯 😲 🎉 😊 ❤️

        Args:
            clicks_per_emoji: Number of clicks per emoji type

        Returns:
            Dict of emoji -> click count
        """
        if not self.connected:
            logger.error("[FAIL] Not connected to stream")
            return {"error": "not_connected"}

        results = {name: 0 for name in self.REACTION_COORDS.keys()}
        total_clicks = 0

        logger.info(f"[PARTY] 🎉 FULL PARTY MODE! Clicking all 5 emotions...")

        # Randomize order for human-like behavior
        emoji_order = list(self.REACTION_COORDS.keys())
        random.shuffle(emoji_order)

        for emoji_name in emoji_order:
            coords = self.REACTION_COORDS[emoji_name]
            emoji = self.REACTION_EMOJIS[emoji_name]

            for i in range(clicks_per_emoji):
                try:
                    # Use coordinate clicking
                    if await self._click_at_coordinates(coords[0], coords[1]):
                        results[emoji_name] += 1
                        total_clicks += 1
                        logger.info(f"[PARTY] {emoji} clicked ({i+1}/{clicks_per_emoji})")

                    # Random delay between clicks
                    await asyncio.sleep(random.uniform(0.3, 0.8))

                except Exception as e:
                    logger.warning(f"[PARTY] {emoji} click failed: {e}")

            # Pause between emoji types
            await asyncio.sleep(random.uniform(0.5, 1.5))

        self.reactions_clicked += total_clicks
        emoji_summary = " ".join([self.REACTION_EMOJIS[e] for e in emoji_order])
        logger.info(f"[PARTY] 🎉 Complete! {total_clicks} clicks: {emoji_summary}")

        return results

    async def party_loop(self, count: int = 10, interval: float = PARTY_INTERVAL) -> int:
        """
        Click hearts continuously in party mode (legacy - single emoji).

        For full 5-emoji party, use party_full() instead.

        Args:
            count: Number of times to click
            interval: Seconds between clicks

        Returns:
            Number of successful clicks
        """
        successful = 0
        logger.info(f"[PARTY] Starting party mode: {count} clicks, {interval}s interval")

        for i in range(count):
            if await self.party():
                successful += 1

            # Random interval to avoid detection
            wait_time = interval + random.uniform(-1, 2)
            await asyncio.sleep(max(1, wait_time))

        logger.info(f"[PARTY] Party complete: {successful}/{count} clicks")
        return successful

    async def get_recent_messages(self, limit: int = 10) -> List[ChatMessage]:
        """
        Get recent chat messages from the stream.

        Args:
            limit: Maximum messages to return

        Returns:
            List of ChatMessage objects
        """
        messages = []

        try:
            from selenium.webdriver.common.by import By

            # Find all chat message elements
            message_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                self.SELECTORS['chat_messages']
            )[-limit:]

            for elem in message_elements:
                try:
                    author = elem.find_element(By.CSS_SELECTOR, self.SELECTORS['author_name']).text
                    text = elem.find_element(By.CSS_SELECTOR, self.SELECTORS['message_text']).text

                    messages.append(ChatMessage(
                        author=author,
                        text=text,
                        timestamp=datetime.now()
                    ))
                except Exception:
                    continue

            return messages

        except Exception as e:
            logger.error(f"[FAIL] Failed to get messages: {e}")
            return []

    def get_status(self) -> Dict[str, Any]:
        """Get current session status."""
        return {
            "connected": self.connected,
            "url": self.url,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "messages_sent": self.messages_sent,
            "reactions_clicked": self.reactions_clicked,
            "triggers_executed": self.triggers_executed,
            "monitoring": self.monitoring,
            "chat_input_position": self.chat_input_rect,
        }

    async def monitor_and_engage(self, interval: float = MONITOR_INTERVAL) -> None:
        """
        Monitor chat for trigger commands and execute actions.

        Watches for commands like !party, !based, !hearts and executes
        the corresponding reaction. This enables autonomous engagement
        when viewers trigger commands in external stream chats.

        Args:
            interval: Seconds between chat polls (default: 3.0)
        """
        self.monitoring = True
        logger.info(f"[MONITOR] Starting chat monitor (interval: {interval}s)")
        logger.info(f"[MONITOR] Watching for triggers: {list(TRIGGER_COMMANDS.keys())}")

        while self.monitoring and self.connected:
            try:
                # Switch to iframe for DOM scraping
                await self._switch_to_chat_iframe()

                # Get recent messages
                messages = await self.get_recent_messages(limit=20)

                for msg in messages:
                    # Create unique key for deduplication
                    msg_key = f"{msg.author}:{msg.text}:{msg.timestamp.minute}"

                    if msg_key in self.seen_messages:
                        continue

                    self.seen_messages.add(msg_key)

                    # Check for trigger commands
                    text_lower = msg.text.lower().strip()
                    for trigger, action in TRIGGER_COMMANDS.items():
                        if trigger in text_lower:
                            logger.info(f"[TRIGGER] {msg.author} triggered '{trigger}' -> {action}")

                            if action == 'party':
                                # Execute FULL party (all 5 emotions)
                                results = await self.party_full(clicks_per_emoji=2)
                                if "error" not in results:
                                    total = sum(results.values())
                                    self.triggers_executed += 1
                                    logger.info(f"[PARTY] 🎉 Full party for {msg.author}: {total} clicks!")
                            # Future: Add other reaction types
                            elif action.startswith('react_'):
                                logger.info(f"[FUTURE] {action} not yet implemented")

                            break  # Only trigger once per message

                # Keep seen_messages from growing unbounded
                if len(self.seen_messages) > 500:
                    # Keep only the 200 most recent
                    self.seen_messages = set(list(self.seen_messages)[-200:])

            except Exception as e:
                logger.error(f"[MONITOR] Error in monitor loop: {e}")

            # Wait before next poll
            await asyncio.sleep(interval)

        logger.info("[MONITOR] Monitor stopped")

    def stop_monitoring(self):
        """Stop the chat monitor loop."""
        self.monitoring = False
        logger.info("[MONITOR] Stop requested")

    async def set_url(self, url: str) -> bool:
        """
        Switch to a different stream URL.

        Args:
            url: New YouTube Live URL

        Returns:
            True if navigation successful
        """
        self.url = url
        return await self._navigate_to_stream()

    def disconnect(self):
        """Disconnect from browser (don't close it)."""
        self.connected = False
        self.driver = None
        logger.info("[OK] Disconnected from browser")


# CLI entry point
async def main():
    """CLI entry point for external stream chat."""
    import argparse

    parser = argparse.ArgumentParser(description="External Stream Chat - OpenClaw")
    parser.add_argument("--url", type=str, help="YouTube Live URL to engage with")
    parser.add_argument("--message", type=str, help="Message to send")
    parser.add_argument("--party", action="store_true", help="Party mode (click hearts)")
    parser.add_argument("--party-count", type=int, default=10, help="Number of party clicks")
    parser.add_argument("--monitor", action="store_true", help="Monitor chat for !party triggers")
    parser.add_argument("--interactive", action="store_true", help="Interactive CLI mode")
    parser.add_argument("--port", type=int, default=BROWSER_PORT, help="Browser debug port")

    args = parser.parse_args()

    # Initialize
    chat = ExternalStreamChat(url=args.url, browser_port=args.port)

    if not await chat.connect():
        print("[FAIL] Could not connect to browser")
        return

    # Execute requested action
    if args.message:
        await chat.send_message(args.message)

    if args.party:
        print("[PARTY] 🎉 Full party mode - all 5 emotions!")
        results = await chat.party_full(clicks_per_emoji=args.party_count // 5 or 2)
        if "error" not in results:
            total = sum(results.values())
            print(f"[PARTY] Complete! {total} clicks: 💯 😲 🎉 😊 ❤️")

    if args.monitor:
        print(f"[MONITOR] Watching chat for triggers: {list(TRIGGER_COMMANDS.keys())}")
        print("[MONITOR] Press Ctrl+C to stop")
        try:
            await chat.monitor_and_engage()
        except KeyboardInterrupt:
            chat.stop_monitoring()
            print("\n[MONITOR] Stopped by user")

    if args.interactive:
        print("\n=== External Stream Chat CLI ===")
        print("Manual commands (you type):")
        print("  !send <msg>  - Send message to chat")
        print("  !party       - Full party mode (💯 😲 🎉 😊 ❤️)")
        print("  !heart       - Single heart click only")
        print("  !watch <url> - Switch to different stream")
        print("  !monitor     - Start watching chat for !party triggers")
        print("  !stop        - Stop monitor mode")
        print("  !status      - Show session info")
        print("  !quit        - Exit")
        print("")
        print(f"Chat triggers (viewers type): {list(TRIGGER_COMMANDS.keys())}")
        print("=" * 50)

        while True:
            try:
                cmd = input("\n> ").strip()

                if cmd.startswith("!send "):
                    msg = cmd[6:].strip()
                    await chat.send_message(msg)

                elif cmd == "!party":
                    print("[PARTY] 🎉 Full party mode - all 5 emotions!")
                    results = await chat.party_full(clicks_per_emoji=2)
                    if "error" not in results:
                        total = sum(results.values())
                        print(f"[PARTY] Complete! {total} clicks: 💯 😲 🎉 😊 ❤️")
                    else:
                        print(f"[PARTY] Failed: {results.get('error')}")

                elif cmd == "!heart":
                    print("[HEART] Clicking heart only...")
                    success = await chat.party()
                    print(f"[HEART] {'Success!' if success else 'Failed'}")

                elif cmd.startswith("!watch "):
                    new_url = cmd[7:].strip()
                    await chat.set_url(new_url)

                elif cmd == "!monitor":
                    print("[MONITOR] Starting chat monitor...")
                    print(f"[MONITOR] Watching for: {list(TRIGGER_COMMANDS.keys())}")
                    print("[MONITOR] Press Ctrl+C or type !stop to stop")
                    # Run monitor in background task
                    monitor_task = asyncio.create_task(chat.monitor_and_engage())
                    try:
                        # Wait a bit then check if still running
                        await asyncio.sleep(1)
                    except asyncio.CancelledError:
                        chat.stop_monitoring()

                elif cmd == "!stop":
                    chat.stop_monitoring()
                    print("[MONITOR] Stopped")

                elif cmd == "!status":
                    status = chat.get_status()
                    for k, v in status.items():
                        print(f"  {k}: {v}")

                elif cmd == "!quit":
                    chat.stop_monitoring()
                    break

                else:
                    print(f"Unknown: {cmd}")
                    print(f"Commands: !send, !party, !watch, !monitor, !stop, !status, !quit")

            except KeyboardInterrupt:
                chat.stop_monitoring()
                break

    chat.disconnect()
    print("\n[OK] Session ended")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(main())
