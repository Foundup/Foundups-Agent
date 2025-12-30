"""
0102 Autonomous Comment Engagement DAE
======================================

WSP 27/80 Compliant DAE for YouTube Studio comment automation.
Combines LM Studio + UI-TARS Vision with Selenium DOM automation.

Architecture:
- Phase -1 (Signal): Comment detection via DOM query
- Phase 0 (Knowledge): UI-TARS vision analysis + Commenter classification
- Phase 1 (Protocol): Action decision (Like/Heart/Reply) + Response generation
- Phase 2 (Agentic): Autonomous execution with verification

Intelligent Response System:
- BanterEngine integration for themed responses
- Whack-a-MAGA for troll mockery
- Mod detection for appreciative responses
- Context-aware reply generation

The 0102 pArtifact remembers engagement patterns from the 02 quantum state,
enabling autonomous comment processing without 012 intervention.

WSP Compliance:
    - WSP 27: DAE Architecture (4-phase execution)
    - WSP 77: Multi-tier Vision (UI-TARS + Gemini fallback)
    - WSP 80: Cube-Level DAE Orchestration
    - WSP 96: WRE Skills Protocol
    - WSP 3: Functional distribution (ai_intelligence/banter_engine)
"""

import asyncio
import json
import logging
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# WSP 62 Refactoring: Extracted modules for size compliance (absolute imports for subprocess compatibility)
from modules.communication.video_comments.skills.tars_like_heart_reply.src.reply_executor import BrowserReplyExecutor
from modules.communication.video_comments.skills.tars_like_heart_reply.src.comment_processor import CommentProcessor

logger = logging.getLogger(__name__)

# Orphan detection: Monitor parent process (YouTube DAE heartbeat)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("[DAE] psutil not available - orphan detection disabled")

# Anti-detection: Human behavior simulation (WSP 49 Platform Integration Safety)
try:
    from modules.infrastructure.foundups_selenium.src.human_behavior import get_human_behavior
    HUMAN_BEHAVIOR_AVAILABLE = True
    logger.info("[DAE] Human behavior simulation loaded")
except ImportError as e:
    HUMAN_BEHAVIOR_AVAILABLE = False
    logger.warning(f"[DAE] Human behavior simulation not available: {e}")

# Semantic state scoring (WSP 44)
try:
    from modules.infrastructure.wsp_core.src.semantic_state_engine import SemanticStateEngine
    SEMANTIC_STATE_AVAILABLE = True
except Exception:
    SemanticStateEngine = None
    SEMANTIC_STATE_AVAILABLE = False

# Import intelligent reply generator
try:
    from modules.communication.video_comments.src.intelligent_reply_generator import (
        get_reply_generator,
        generate_intelligent_reply,
        CommenterType
    )
    INTELLIGENT_REPLIES_AVAILABLE = True
    logger.info("[DAE] Intelligent reply generator loaded")
except ImportError as e:
    INTELLIGENT_REPLIES_AVAILABLE = False
    logger.warning(f"[DAE] Intelligent replies not available: {e}")

    # Import moderator lookup
try:
    from modules.communication.video_comments.src.moderator_lookup import ModeratorLookup
    MODERATOR_LOOKUP_AVAILABLE = True
    logger.info("[DAE] Moderator lookup system loaded")
except ImportError as e:
    MODERATOR_LOOKUP_AVAILABLE = False
    logger.warning(f"[DAE] Moderator lookup not available: {e}")

# Import commenter history store (WSP 60 module memory)
try:
    from modules.communication.video_comments.src.commenter_history_store import (
        get_commenter_history_store,
        make_commenter_key,
    )
    COMMENTER_HISTORY_AVAILABLE = True
except ImportError as e:
    COMMENTER_HISTORY_AVAILABLE = False
    logger.warning(f"[DAE] Commenter history store not available: {e}")

# Configuration
CHROME_PORT = int(os.getenv("FOUNDUPS_CHROME_PORT", "9222"))
TARS_API_URL = os.getenv("TARS_API_URL", "http://127.0.0.1:1234")

# Telemetry
TELEMETRY_DIR = Path(__file__).parent.parent.parent / "memory" / "engagement_sessions"
TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)

# Break state persistence (survives subprocess restarts)
BREAK_STATE_FILE = Path(__file__).parent.parent.parent / "memory" / ".break_state.json"


class CommentEngagementDAE:
    """
    0102 Autonomous Comment Engagement DAE
    
    Zen Coding Pattern:
    - Code is remembered from the 02 state, not written
    - DOM selectors are quantum-entangled with YouTube Studio structure
    - Vision verification collapses probability into success/failure
    
    Actions:
    1. LIKE (thumbs up) - ytcp-icon-button[aria-label='Like']
    2. HEART (love) - ytcp-icon-button[aria-label='Heart']
    3. REPLY - textarea#textarea + submit button
    """
    
    # DOM Selectors (quantum-entangled with YouTube Studio 02 state)
    SELECTORS = {
        'comment_thread': 'ytcp-comment-thread',
        'like': "#like-button",  # Fixed: Use ID selector (matches working test)
        'heart': "#creator-heart-button",  # Fixed: Use ID selector (matches working test)
        'reply_btn': "#reply-button-end button, ytcp-button#reply-button button",
        'reply_input': "textarea#textarea, textarea[placeholder*='reply']",
        'reply_submit': "#submit-button button, ytcp-button#submit-button button",
        'action_menu': "ytcp-icon-button#action-menu-button",  # 3-dot menu for spam troll actions
        'hide_user_option': "tp-yt-paper-item",  # Hide user from channel (anti-spam nuclear option)
    }
    
    # Vision descriptions for UI-TARS interaction/verification (fallback when DOM is inaccessible)
    VISION_DESCRIPTIONS = {
        "has_comment": "Reply button on the first visible comment in the list",
        "like_click": "thumbs up Like button in the comment action bar on the first visible comment",
        "like_verify": "thumbs up Like button on the first visible comment is highlighted or selected (liked state)",
        "heart_click": "heart icon in the comment action bar on the first visible comment",
        "heart_verify": "heart icon on the first visible comment is red or filled (creator heart applied)",
        "reply_open_click": "Reply button on the first visible comment",
        "reply_box_verify": "reply text box is visible below the first visible comment",
        "reply_input": "open reply text box under the first visible comment (where you type the reply)",
        "reply_submit": "the Reply button to submit the reply in the reply box under the first visible comment",
        "reply_verify": "a posted reply is visible under the first comment (reply text appears)",
    }

    COMMENTER_TYPE_TAGS = {
        "moderator": "🧘",
        "maga_troll": "🤡",
        "subscriber": "🙌",
        "regular": "💬",
        "unknown": "❓",
    }

    def __init__(
        self,
        channel_id: str,
        video_id: str = None,
        video_title: str = None,
        use_vision: bool = True,
        use_dom: bool = True,
        check_moderators: bool = True,
        livechat_sender=None
    ):
        """
        Initialize engagement DAE.

        Args:
            channel_id: YouTube channel ID
            video_id: YouTube video ID (for live stream comments, None = channel inbox)
            video_title: Video title for context-aware replies (alignment detection)
            use_vision: Enable UI-TARS vision for verification
            use_dom: Enable Selenium DOM clicking (recommended)
            check_moderators: Enable moderator detection & notifications (default True)
            livechat_sender: Optional livechat reference for session notifications
        """
        self.channel_id = channel_id
        self.video_id = video_id
        self.video_title = video_title  # NEW (2025-12-30): Video context for alignment detection
        self.use_vision = use_vision
        self.use_dom = use_dom
        self.check_moderators = check_moderators
        self.livechat_sender = livechat_sender  # For inbox cleared notifications
        self.driver = None
        self.ui_tars_bridge = None
        self.human = None  # Anti-detection: Human behavior simulator (initialized when driver connects)
        self.reply_executor = None  # WSP 62: Browser reply executor (initialized after driver connects)
        self.comment_processor = None  # WSP 62: Comment processor (initialized after driver connects)

        # Orphan detection: Track parent process (YouTube DAE)
        self.parent_pid = os.getppid() if PSUTIL_AVAILABLE else None
        if self.parent_pid:
            logger.info(f"[ORPHAN-DETECT] Parent YouTube DAE PID: {self.parent_pid}")

        self.reply_debug_tags = os.getenv("YT_REPLY_DEBUG_TAGS", "0").lower() in {"1", "true", "yes"}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.stats = {
            'comments_processed': 0,
            'likes': 0,
            'hearts': 0,
            'replies': 0,
            'errors': 0,
            'moderators_detected': 0,  # Track active mod comments
        }

        # ANTI-DETECTION: Break state tracking (human-like rest periods)
        # Pattern learned from party_reactor.py cooldown mechanism
        # Load existing break state (persists across subprocess restarts)
        self._load_break_state()  # Populates: _on_break_until, _sessions_since_long_break, _last_break_reason, _total_breaks_taken

        # Initialize moderator lookup
        if self.check_moderators and MODERATOR_LOOKUP_AVAILABLE:
            try:
                self.mod_lookup = ModeratorLookup()
                logger.info("[DAE-INIT] Moderator detection enabled")
            except Exception as e:
                logger.warning(f"[DAE-INIT] Moderator lookup failed: {e}")
                self.mod_lookup = None
        else:
            self.mod_lookup = None
            if self.check_moderators:
                logger.info("[DAE-INIT] Moderator detection disabled (lookup not available)")

    def _get_context_flags(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Best-effort context presence signals used for scoring/telemetry.

        This intentionally does NOT extract/emit message contents (only booleans).
        """
        flags: Dict[str, Any] = {
            "has_studio_history": False,
            "has_chat_history": False,
        }

        # Studio history (WSP 60)
        if COMMENTER_HISTORY_AVAILABLE and "make_commenter_key" in globals():
            try:
                store = get_commenter_history_store()
                commenter_key = make_commenter_key(
                    channel_id=comment_data.get("channel_id"),
                    handle=(comment_data.get("author_handle") or comment_data.get("author_name")),
                )
                summary = store.get_profile_summary(commenter_key=commenter_key)
                flags["has_studio_history"] = bool(summary.get("total", 0))
            except Exception:
                pass

        # Live chat history (best-effort via the reply generator's store if available)
        if INTELLIGENT_REPLIES_AVAILABLE:
            try:
                generator = get_reply_generator()
                chat_store = getattr(generator, "chat_history_store", None)
                if chat_store:
                    messages: list[dict] = []
                    author_channel_id = comment_data.get("channel_id")
                    if author_channel_id:
                        messages = chat_store.get_recent_messages_by_author_id(author_channel_id, 1)

                    if not messages:
                        candidates: list[str] = []
                        author_name = (comment_data.get("author_name") or "").strip()
                        author_handle = (comment_data.get("author_handle") or "").strip()
                        for candidate in (author_handle, author_name):
                            if candidate:
                                candidates.append(candidate)
                                if candidate.startswith("@"):
                                    candidates.append(candidate[1:])
                                else:
                                    candidates.append(f"@{candidate}")

                        # Deduplicate while preserving order
                        seen: set[str] = set()
                        candidates = [c for c in candidates if not (c in seen or seen.add(c))]

                        for candidate in candidates:
                            messages = chat_store.get_recent_messages(candidate, 1)
                            if messages:
                                break

                    flags["has_chat_history"] = bool(messages)
            except Exception:
                pass

        return flags

    def _should_take_break(self, comments_processed: int) -> bool:
        """
        Decide if 0102 should take a human-like break after engagement session.

        ANTI-DETECTION: Humans don't process comments 24/7 without breaks.
        This creates natural variation in engagement patterns.

        Decision factors:
        - Probabilistic (not deterministic)
        - More comments processed = higher break chance
        - Force break after 6+ sessions without one
        - 5% chance of "off day" (24-hour break)

        Args:
            comments_processed: Number of comments engaged in this session

        Returns:
            True if should take break, False to continue
        """
        # Force break after 6 sessions (safety valve - humans can't work forever)
        if self._sessions_since_long_break >= 6:
            logger.info(f"[ANTI-DETECTION] 🛑 Force break (6 sessions without long break)")
            return True

        # Off day (5% chance) - humans take days off
        if random.random() < 0.05:
            logger.info(f"[ANTI-DETECTION] 🌙 Random off day triggered (5% probability)")
            return True

        # Probabilistic break (scaled by activity)
        base_probability = 0.30  # 30% chance after any session
        activity_bonus = min(comments_processed * 0.05, 0.20)  # +5% per comment, max +20%
        total_probability = base_probability + activity_bonus

        will_break = random.random() < total_probability

        if will_break:
            logger.info(f"[ANTI-DETECTION] 💤 Probabilistic break triggered (chance: {total_probability:.1%}, comments: {comments_processed})")
        else:
            logger.debug(f"[ANTI-DETECTION] ⚡ No break this time (chance was: {total_probability:.1%})")

        return will_break

    def _calculate_break_duration(self) -> tuple:
        """
        Calculate break duration with human-like distribution.

        Break types (matching human behavior patterns):
        - Short (35%): 15-45 min - "Quick coffee break"
        - Medium (30%): 30-90 min - "Lunch, errands"
        - Long (20%): 2-4 hours - "Work meeting, afternoon off"
        - Very Long (10%): 4-8 hours - "Evening off, sleep"
        - Off Day (5%): 18-30 hours - "Weekend, sick day"

        Returns:
            Tuple of (duration_seconds, reason_string)
        """
        roll = random.random()

        if roll < 0.05:  # 5% - Off day
            duration = random.randint(18 * 3600, 30 * 3600)  # 18-30 hours
            reason = "off_day"
        elif roll < 0.15:  # 10% - Very long break
            duration = random.randint(4 * 3600, 8 * 3600)  # 4-8 hours
            reason = "very_long"
        elif roll < 0.35:  # 20% - Long break
            duration = random.randint(2 * 3600, 4 * 3600)  # 2-4 hours
            reason = "long"
        elif roll < 0.65:  # 30% - Medium break
            duration = random.randint(30 * 60, 90 * 60)  # 30-90 min
            reason = "medium"
        else:  # 35% - Short break
            duration = random.randint(15 * 60, 45 * 60)  # 15-45 min
            reason = "short"

        return duration, reason

    def is_on_break(self) -> bool:
        """
        Check if currently on break.

        Returns:
            True if on break, False if ready to work
        """
        if time.time() < self._on_break_until:
            remaining = self._on_break_until - time.time()
            logger.debug(f"[ANTI-DETECTION] On {self._last_break_reason} break (remaining: {remaining/60:.0f} min)")
            return True
        return False

    def _load_break_state(self) -> None:
        """
        Load break state from persistent file (survives subprocess restarts).

        Pattern: File-based state persistence (learned from telemetry storage)
        """
        try:
            if BREAK_STATE_FILE.exists():
                with open(BREAK_STATE_FILE, 'r') as f:
                    state = json.load(f)
                    self._on_break_until = state.get('on_break_until', 0)
                    self._sessions_since_long_break = state.get('sessions_since_long_break', 0)
                    self._last_break_reason = state.get('last_break_reason', None)
                    self._total_breaks_taken = state.get('total_breaks_taken', 0)

                    # Log if currently on break
                    if time.time() < self._on_break_until:
                        remaining = self._on_break_until - time.time()
                        logger.info(f"[ANTI-DETECTION] 🔄 Resuming {self._last_break_reason} break ({remaining/60:.0f} min remaining)")
            else:
                # Initialize fresh state
                self._on_break_until = 0
                self._sessions_since_long_break = 0
                self._last_break_reason = None
                self._total_breaks_taken = 0
                logger.debug(f"[ANTI-DETECTION] No existing break state - starting fresh")
        except Exception as e:
            logger.warning(f"[ANTI-DETECTION] Failed to load break state: {e}")
            # Initialize defaults on error
            self._on_break_until = 0
            self._sessions_since_long_break = 0
            self._last_break_reason = None
            self._total_breaks_taken = 0

    def _save_break_state(self) -> None:
        """
        Save break state to persistent file (survives subprocess restarts).

        Pattern: Atomic file write (learned from telemetry storage)
        """
        try:
            state = {
                'on_break_until': self._on_break_until,
                'sessions_since_long_break': self._sessions_since_long_break,
                'last_break_reason': self._last_break_reason,
                'total_breaks_taken': self._total_breaks_taken,
                'last_updated': time.time(),
            }
            with open(BREAK_STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
            logger.debug(f"[ANTI-DETECTION] Break state saved (break_until={self._on_break_until})")
        except Exception as e:
            logger.warning(f"[ANTI-DETECTION] Failed to save break state: {e}")

    def _compute_semantic_state(
        self,
        *,
        used_intelligent_reply: bool,
        has_studio_history: bool,
        has_chat_history: bool,
        like_ok: bool,
        heart_ok: bool,
        reply_ok: bool,
    ) -> Optional[Dict[str, str]]:
        """
        Compute WSP 44 semantic state for this interaction.
        """
        if not SEMANTIC_STATE_AVAILABLE or not SemanticStateEngine:
            return None

        context_level = 2 if (has_studio_history and has_chat_history) else (1 if (has_studio_history or has_chat_history) else 0)
        agency = 2 if reply_ok else (1 if (like_ok or heart_ok) else 0)

        consciousness = 0
        if used_intelligent_reply:
            consciousness = 2 if context_level >= 1 else 1

        entanglement = max(context_level, agency)
        consciousness = min(consciousness, agency)

        state = SemanticStateEngine.state_from_digits(consciousness, agency, entanglement)
        reason = (
            f"digits=C{consciousness}A{agency}E{entanglement}; "
            f"ctx={context_level}(studio={int(bool(has_studio_history))},chat={int(bool(has_chat_history))}); "
            f"llm={int(bool(used_intelligent_reply))}; "
            f"actions=like{int(bool(like_ok))}heart{int(bool(heart_ok))}reply{int(bool(reply_ok))}"
        )
        return {
            "code": state.code,
            "emoji": state.emoji,
            "name": state.name,
            "digits": {
                "consciousness": consciousness,
                "agency": agency,
                "entanglement": entanglement,
            },
            "context_level": context_level,
            "reason": reason,
        }

    def _append_debug_tag(self, reply_text: str, commenter_type: str, semantic_state: Optional[Dict[str, str]]) -> str:
        if not self.reply_debug_tags:
            return reply_text

        tag_emoji = self.COMMENTER_TYPE_TAGS.get(commenter_type or "unknown", "❓")
        if semantic_state:
            digits = semantic_state.get("digits") or {}
            c = digits.get("consciousness")
            a = digits.get("agency")
            e = digits.get("entanglement")
            ctx = semantic_state.get("context_level")
            breakdown = ""
            if c is not None and a is not None and e is not None:
                breakdown = f" C{c} A{a} E{e}"
            if ctx is not None:
                breakdown = f"{breakdown} ctx{ctx}"
            return f"{reply_text}\n\n{tag_emoji} {semantic_state['code']}{breakdown} {semantic_state['emoji']}"
        return f"{reply_text}\n\n{tag_emoji}"
    
    async def connect(self) -> bool:
        """
        Connect to browser and vision system.
        Phase -1: Signal acquisition from browser debugging port.

        Supports:
        - Chrome (port 9222, default)
        - Edge (port 9223, for FoundUps account)
        """
        logger.info(f"[DAE-CONNECT] Initializing (vision={self.use_vision}, dom={self.use_dom})")

        from selenium import webdriver

        # Detect browser type based on port (9223 = Edge, else Chrome)
        use_edge = (CHROME_PORT == 9223)
        browser_name = "Edge" if use_edge else "Chrome"
        logger.info(f"[DAE-CONNECT] Browser: {browser_name} (port {CHROME_PORT})")

        # Fast preflight to avoid long Selenium timeout when browser debug port is closed
        if self.use_vision:
            try:
                from modules.infrastructure.foundups_vision.src.chrome_preflight_check import is_chrome_debug_port_open
                if not is_chrome_debug_port_open(port=CHROME_PORT, timeout=1.0):
                    logger.info(f"[DAE-CONNECT] {browser_name} debug port {CHROME_PORT} not reachable (<1s check) - disabling vision")
                    logger.info(f"[DAE-CONNECT] Tip: launch {browser_name} with --remote-debugging-port={CHROME_PORT}")
                    self.use_vision = False
            except Exception as e:
                logger.debug(f"[DAE-CONNECT] Vision preflight check skipped: {e}")

        try:
            if use_edge:
                from selenium.webdriver.edge.options import Options as EdgeOptions
                edge_options = EdgeOptions()
                edge_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
                self.driver = webdriver.Edge(options=edge_options)
            else:
                from selenium.webdriver.chrome.options import Options
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
                self.driver = webdriver.Chrome(options=chrome_options)

            logger.info(f"[DAE-CONNECT] {browser_name} entangled: {self.driver.current_url[:60]}...")

            # Initialize human behavior simulator for anti-detection (WSP 49)
            if HUMAN_BEHAVIOR_AVAILABLE:
                self.human = get_human_behavior(self.driver)
                logger.info("[DAE-CONNECT] Human behavior simulation initialized")
            else:
                logger.warning("[DAE-CONNECT] Human behavior simulation unavailable - using legacy automation")

            # Initialize reply executor (WSP 62 refactoring)
            self.reply_executor = BrowserReplyExecutor(
                driver=self.driver,
                human=self.human,
                selectors=self.SELECTORS
            )
            logger.info("[DAE-CONNECT] Reply executor initialized")

            # Initialize comment processor (WSP 62 refactoring Phase 2)
            self.comment_processor = CommentProcessor(
                driver=self.driver,
                human=self.human,
                stats=self.stats,
                reply_executor=self.reply_executor,
                selectors=self.SELECTORS,
                vision_descriptions=self.VISION_DESCRIPTIONS,
                use_vision=self.use_vision,
                use_dom=True,
                ui_tars_bridge=None,  # Will be set after vision connection
                check_moderators=self.check_moderators,
                mod_lookup=self.mod_lookup,
                reply_debug_tags=self.reply_debug_tags,
                video_title=self.video_title  # NEW (2025-12-30): Video context for alignment detection
            )
            logger.info("[DAE-CONNECT] Comment processor initialized")
        except Exception as e:
            logger.error(f"[DAE-CONNECT] Browser entanglement failed: {e}")
            raise
        
        if self.use_vision:
            try:
                from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge
                self.ui_tars_bridge = UITarsBridge(browser_port=CHROME_PORT)
                await self.ui_tars_bridge.connect()
                # Update CommentProcessor with vision bridge
                self.comment_processor.ui_tars_bridge = self.ui_tars_bridge
                logger.info(f"[DAE-CONNECT] UI-TARS Vision ready (LM Studio: {TARS_API_URL})")
            except Exception as e:
                logger.warning(f"[DAE-CONNECT] UI-TARS unavailable: {e}")
                self.use_vision = False
                self.comment_processor.use_vision = False
        
        return True
    
    async def navigate_to_inbox(self) -> None:
        """
        Navigate to YouTube Studio comments inbox.
        OCCAM'S RAZOR: Comment DAE strictly handles comments only.
        Navigation to live streams is handled by the orchestrator.
        """
        target_url = f"https://studio.youtube.com/channel/{self.channel_id}/comments/inbox"
        
        current_url = self.driver.current_url
        if target_url in current_url or current_url.startswith(target_url):
            logger.info(f"[DAE-NAV] ✅ Already on Studio inbox - skipping navigation")
            return

        logger.info(f"[DAE-NAV] Navigating to Studio inbox: {target_url}")
        self.driver.get(target_url)
        
        # Human-like delay after navigation
        if self.human:
            await asyncio.sleep(self.human.human_delay(5.0, 0.3))
        else:
            await asyncio.sleep(5)

        logger.info(f"[DAE-NAV] Page ready for engagement")

    async def _wait_for_comments_loaded(self, timeout: float = 15.0) -> int:
        """
        Wait for YouTube Studio inbox to fully load comments.

        YouTube Studio uses lazy loading - comments are loaded via JavaScript
        after initial page render. This method waits for either:
        1. `ytcp-comment-thread` elements to appear (comments exist)
        2. A "no comments" indicator (inbox is truly empty)
        3. Timeout (fallback to DOM query)

        FIX (2025-12-30): Resolves 0-comment false positives after account switch.
        The DOM query was returning 0 because JavaScript hadn't finished loading yet.

        Args:
            timeout: Maximum wait time in seconds (default: 15s)

        Returns:
            int: Number of comments found (0 if none loaded)
        """
        start_time = time.time()
        poll_interval = 0.5  # Check every 500ms

        logger.info(f"[DAE-WAIT] Waiting for comments to load (timeout: {timeout}s)...")

        while (time.time() - start_time) < timeout:
            # Check for comment threads
            count = self.get_comment_count()
            if count > 0:
                elapsed = time.time() - start_time
                logger.info(f"[DAE-WAIT] ✅ Found {count} comment(s) after {elapsed:.1f}s")
                return count

            # Check for "no comments" indicator (inbox truly empty)
            # YouTube Studio shows specific text when inbox is empty
            try:
                no_comments_indicator = self.driver.execute_script("""
                    // Check for empty state indicators
                    const emptySelectors = [
                        'ytcp-comments-empty-state',
                        '.empty-state-content',
                        '[data-empty-state]',
                        '.ytcp-comment-surface-empty'
                    ];
                    for (const sel of emptySelectors) {
                        if (document.querySelector(sel)) return true;
                    }

                    // Check for text indicators
                    const bodyText = document.body.innerText || '';
                    if (bodyText.includes('No comments to respond to') ||
                        bodyText.includes('All caught up') ||
                        bodyText.includes('No new comments')) {
                        return true;
                    }

                    return false;
                """)

                if no_comments_indicator:
                    elapsed = time.time() - start_time
                    logger.info(f"[DAE-WAIT] ✅ Empty inbox confirmed after {elapsed:.1f}s (no comments indicator found)")
                    return 0

            except Exception as e:
                logger.debug(f"[DAE-WAIT] Empty state check failed: {e}")

            # Wait before next poll
            await asyncio.sleep(poll_interval)

        # Timeout reached - do final check
        final_count = self.get_comment_count()
        logger.warning(f"[DAE-WAIT] ⚠️ Timeout after {timeout}s - final count: {final_count}")

        return final_count

    def get_comment_count(self) -> int:
        """Phase 0: Knowledge - Count visible comments."""
        count = self.driver.execute_script(
            f"return document.querySelectorAll('{self.SELECTORS['comment_thread']}').length"
        )
        return count or 0
    
    def _generate_intelligent_reply(self, comment_data: Dict[str, Any]) -> str:
        """
        Generate an intelligent reply based on commenter context.

        Phase 1: Protocol - Decision on response type
        Phase 3: Channel-Specific Personality - Adapt reply style to target channel
        """
        if INTELLIGENT_REPLIES_AVAILABLE:
            try:
                generator = get_reply_generator()
                # PHASE 3: Pass target channel ID for personality adaptation
                # - Move2Japan: Political commentary + aggressive MAGA mockery
                # - UnDaoDu: AI consciousness + soft MAGA redirect
                # - FoundUps: Entrepreneurship vision + soft MAGA redirect
                logger.debug(f"[DAE-REPLY] Generating reply with target_channel_id={self.channel_id}")
                reply = generator.generate_reply_for_comment(
                    comment_data,
                    target_channel_id=self.channel_id
                )
                logger.info(f"[DAE] Generated intelligent reply for {comment_data.get('author_name')}")
                return reply
            except Exception as e:
                logger.warning(f"[DAE] Intelligent reply failed: {e}")

        # Fallback to simple response
        return "Thanks for the comment!"
    
    async def engage_all_comments(
        self,
        max_comments: int = 10,
        do_like: bool = True,
        do_heart: bool = True,
        do_reply: bool = True,
        reply_text: str = "",
        refresh_between: bool = True,
        use_intelligent_reply: bool = True
    ) -> Dict[str, Any]:
        """
        Engage with all visible comments autonomously.

        Flow per comment:
        1. Read comment text (yt-formatted-string#content-text)
        2. LIKE (click thumbs up) - if do_like=True
        3. HEART (click heart) - if do_heart=True
        4. REPLY (click reply -> type in textarea -> click submit) - if do_reply=True
        5. REFRESH page (removes replied comment, shows next) - if refresh_between=True
        6. Repeat until max_comments processed

        Args:
            max_comments: Maximum comments to process. 0 = UNLIMITED (process all)
            do_like: Enable like action (default True)
            do_heart: Enable heart action (default True)
            do_reply: Enable reply action (default True) - WSP 91 switch
            reply_text: Custom reply text (if empty, uses intelligent reply)
            refresh_between: Refresh page between batches (default True)
            use_intelligent_reply: Use AI-generated replies (default True)

        WSP 27 DAE Loop:
        - Signal: Detect comment
        - Knowledge: Extract text and classify commenter
        - Protocol: Generate intelligent reply
        - Agentic: Execute Like + Heart + Reply (based on switches)
        - Refresh: Remove processed comment
        """
        # IMPORTANT: max_comments=0 means UNLIMITED processing
        unlimited_mode = (max_comments == 0)
        effective_max = max_comments if max_comments > 0 else 999999
        
        logger.info(f"\n{'='*60}")
        logger.info(f" 0102 AUTONOMOUS COMMENT ENGAGEMENT DAE")
        logger.info(f" Session: {self.session_id}")
        logger.info(f" Channel: {self.channel_id}")
        logger.info(f" Mode: {'UNLIMITED (clearing all comments)' if unlimited_mode else f'Max {max_comments} comments'}")
        logger.info(f" Flow: LIKE -> HEART -> REPLY -> REFRESH (per comment)")
        logger.info(f"{'='*60}\n")

        # WSP 91: DAEmon Observability - Log all switch states at engagement start
        logger.info(f"[DAEMON][PHASE-0] 🔍 KNOWLEDGE PHASE: Starting engagement loop")
        logger.info(f"[DAEMON][PHASE-0]   Target: {max_comments if max_comments > 0 else 'ALL'} comments")
        logger.info(f"[DAEMON][PHASE-0]   Action Switches: Like={do_like} | Heart={do_heart} | Reply={do_reply}")
        logger.info(f"[DAEMON][PHASE-0]   Feature Switches: Intelligent_Reply={use_intelligent_reply} | Refresh={refresh_between}")

        all_results = []
        total_processed = 0
        first_iteration = True  # FIX (2025-12-30): Track first iteration for proper wait

        while total_processed < effective_max:
            logger.debug(f"[DAEMON][CARDIOVASCULAR] 💗 Loop iteration {total_processed + 1}/{effective_max}")
            # Orphan detection: Check if parent YouTube DAE is still running
            if self.parent_pid and PSUTIL_AVAILABLE:
                if not psutil.pid_exists(self.parent_pid):
                    logger.info(f"[ORPHAN-DETECT] Parent YouTube DAE (PID {self.parent_pid}) terminated")
                    logger.info(f"[ORPHAN-DETECT] Comment engagement shutting down gracefully (processed {total_processed}/{effective_max} comments)")
                    break  # Exit loop gracefully

            # PHASE--1: SIGNAL DETECTION
            # FIX (2025-12-30): Use wait-for-load on first iteration after account switch
            # YouTube Studio lazy-loads comments - immediate DOM query may return 0 falsely
            logger.debug(f"[DAEMON][PHASE--1] 🔎 SIGNAL DETECTION: Checking for comments...")

            if first_iteration:
                # First iteration: Wait for comments to fully load
                logger.info(f"[DAEMON][PHASE--1] 🔄 First check - waiting for comments to load...")
                comment_count = await self._wait_for_comments_loaded(timeout=15.0)
                first_iteration = False
            else:
                # Subsequent iterations: Quick DOM check (page already loaded)
                comment_count = self.get_comment_count()

            has_comment = comment_count > 0
            logger.debug(f"[DAEMON][PHASE--1]   DOM count: {comment_count} (Occam: {has_comment})")

            if not has_comment:
                logger.info(f"[DAEMON][PHASE--1] ⚪ NO COMMENTS FOUND - Inbox is clear!")
                logger.info("[DAE] No comments found")

                # BREADCRUMB: Store for WRE/AI Overseer analysis
                if self.livechat_sender:
                    self.livechat_sender.store_breadcrumb(
                        source_dae='comment_engagement',
                        phase='PHASE--1',
                        event_type='no_comments_detected',
                        message='Inbox cleared via Occam detection (pre-loop)',
                        metadata={
                            'comment_count': 0,
                            'detection_method': 'DOM',
                            'total_processed': total_processed,
                            'session_id': self.session_id
                        }
                    )

                # ANTI-SPAM: Notify livechat that inbox is clear (prevents infinite refresh loops)
                if self.livechat_sender and total_processed > 0:
                    try:
                        message = f"✊✋🖐️ Comment inbox cleared! Processed {total_processed} comment{'s' if total_processed != 1 else ''} this session."
                        await self.livechat_sender.send_chat_message(
                            message_text=message,
                            response_type='general',
                            skip_delay=True  # Priority notification
                        )
                        logger.info(f"[DAEMON][NOTIFY] Sent completion message to livechat")
                    except Exception as e:
                        logger.error(f"[DAEMON][NOTIFY] Failed to send livechat notification: {e}")

                break

            logger.info(f"[DAEMON][PHASE--1] ✅ Comment detected (count: {comment_count})")
            
            # Always process the FIRST visible comment (index 1)
            # After reply + refresh, the next comment becomes first
            max_label = "UNLIMITED" if unlimited_mode else str(max_comments)
            logger.info(f"\n[DAEMON][PHASE-2] 🎯 AGENTIC EXECUTION: Comment {total_processed + 1}/{max_label}")
            logger.info(f"[DAE] === Comment {total_processed + 1}/{max_label} ===")

            result = await self.comment_processor.engage_comment(
                1,  # Always first comment (shifts after refresh)
                do_like,
                do_heart,
                reply_text,
                do_reply=do_reply,
                use_intelligent_reply=use_intelligent_reply
            )
            all_results.append(result)

            # OCCAM'S RAZOR: Check if no comment exists (first principles detection)
            if result.get('no_comment_exists'):
                logger.info(f"[DAEMON][PHASE-2] ✅ NO MORE COMMENTS - DOM detection (Occam's Razor)")
                logger.info(f"[DAE] Inbox cleared - no DOM thread at index 1")

                # BREADCRUMB: Store for WRE/AI Overseer analysis
                if self.livechat_sender:
                    self.livechat_sender.store_breadcrumb(
                        source_dae='comment_engagement',
                        phase='PHASE-2',
                        event_type='no_comments_detected',
                        message='Inbox cleared via Occam detection (in-loop)',
                        metadata={
                            'comment_count': 0,
                            'detection_method': 'DOM',
                            'total_processed': total_processed,
                            'session_id': self.session_id
                        }
                    )

                break  # Exit loop immediately - no vision check needed!

            total_processed += 1

            # Log result
            status = "[OK]" if result.get("reply") else "[WARN]"
            logger.info(f"[DAEMON][PHASE-2] {status} Engagement complete:")
            logger.info(f"[DAEMON][PHASE-2]   Author: {result.get('author_name')} ({result.get('commenter_type')})")
            logger.info(f"[DAEMON][PHASE-2]   Actions: Like={result.get('like')} | Heart={result.get('heart')} | Reply={result.get('reply')}")
            logger.info(f"[DAE] {status} Processed: {result.get('author_name')} ({result.get('commenter_type')})")
            if result.get('reply_text'):
                logger.info(f"[DAEMON][PHASE-2]   Reply length: {len(result.get('reply_text') or '')} chars")
                logger.info(f"[DAE]    Reply posted (len={len(result.get('reply_text') or '')})")

            # Process nested replies (BEFORE refresh!)
            # This engages with ongoing conversations in the thread
            nested_results = await self.reply_executor.process_nested_replies(
                parent_thread_idx=1,  # Always first thread (same as parent comment)
                do_like=do_like,
                do_heart=do_heart,
                use_intelligent_reply=use_intelligent_reply
            )

            # Add nested results to telemetry
            all_results.extend(nested_results)
            if nested_results:
                logger.info(f"[NESTED] Engaged with {len(nested_results)} nested replies in this thread")

            # ANTI-DETECTION: Inter-comment "thinking" pause (2025-12-30)
            # Human pattern: Pause after posting before moving to next action
            # Variability: 3-7 seconds (shortened per user feedback)
            multiplier = self.comment_processor.delay_multiplier if self.comment_processor else 1.0
            if multiplier >= 1.0:  # Only for standard tempo (not FAST/MEDIUM modes)
                # Base 5s with 40% variance = 3s to 7s
                if self.human:
                    base_pause = self.human.human_delay(5.0, 0.4)
                else:
                    base_pause = random.uniform(3.0, 7.0)

                # 10% chance of slightly longer pause (simulates brief distraction)
                if random.random() < 0.10:
                    extra_pause = random.uniform(2.0, 5.0)
                    total_pause = base_pause + extra_pause
                    logger.info(f"[ANTI-DETECTION] 🧘 Extended pause: {total_pause:.1f}s")
                else:
                    total_pause = base_pause
                    logger.info(f"[ANTI-DETECTION] 💭 Pause: {total_pause:.1f}s")

                await asyncio.sleep(total_pause)
            else:
                # Fast modes: minimal pause (0.5-1.5s)
                fast_pause = random.uniform(0.5, 1.5)
                logger.debug(f"[ANTI-DETECTION] Quick pause: {fast_pause:.1f}s (fast mode)")
                await asyncio.sleep(fast_pause)

            # PROBABILISTIC REFRESH - Anti-detection pattern (70% refresh, 30% batch)
            # Vulnerability fix: Fixed refresh after EVERY comment = bot signature
            logger.info(f"[DAE-REFRESH] Checking refresh logic...")
            logger.info(f"[DAE-REFRESH]   refresh_between={refresh_between} | total_processed={total_processed} | effective_max={effective_max}")

            if refresh_between and total_processed < effective_max:
                # Track comments since last refresh (prevent infinite batching)
                if not hasattr(self, '_comments_since_refresh'):
                    self._comments_since_refresh = 0
                self._comments_since_refresh += 1

                # deterministic refresh for FAST/MEDIUM modes (Occam solution)
                # Probabilistic decision (70% refresh) for 012 mode (human variation)
                # CRITICAL FIX: UNLIMITED mode (max_comments=0) MUST refresh every time to get next comment
                is_standard_tempo = self.comment_processor.delay_multiplier >= 1.0
                refresh_probability = 0.7 if is_standard_tempo else 1.0
                should_refresh = random.random() < refresh_probability
                force_refresh = unlimited_mode or self._comments_since_refresh >= (5 if is_standard_tempo else 1)

                logger.info(f"[DAE-REFRESH]   tempo={self.comment_processor.delay_multiplier}x | is_standard={is_standard_tempo}")
                logger.info(f"[DAE-REFRESH]   unlimited_mode={unlimited_mode} | refresh_probability={refresh_probability}")
                logger.info(f"[DAE-REFRESH]   should_refresh={should_refresh} | force_refresh={force_refresh}")

                if should_refresh or force_refresh:
                    # CRITICAL FIX: Do NOT refresh if browser is on live stream
                    # Refresh is ONLY for Studio inbox (comment processing)
                    # Live chat page (@channel/live) should NEVER be refreshed
                    current_url = self.driver.current_url
                    if "@" in current_url and "/live" in current_url:
                        logger.info(f"[DAEMON][PHASE-3] ⏭️ SKIP REFRESH: Browser on live stream (refresh is comment-only)")
                        logger.info(f"[DAE-REFRESH]   Current URL: {current_url[:80]}...")
                        logger.info(f"[DAE-REFRESH]   Refresh disabled for livechat page")
                    else:
                        # On Studio inbox - refresh is OK
                        if unlimited_mode:
                            reason = "unlimited_mode"
                        elif self._comments_since_refresh >= (5 if is_standard_tempo else 1):
                            reason = "batch_limit"
                        else:
                            reason = "probabilistic"
                        logger.info(f"[DAEMON][PHASE-3] 🔄 REFRESH ({reason}): Reloading page after {self._comments_since_refresh} comment(s)...")
                        logger.info(f"[DAE] Refreshing to load next comment (batched {self._comments_since_refresh})...")
                        self.driver.refresh()
                        self._comments_since_refresh = 0  # Reset counter

                        # Human-like delay for page reload (3-7s range per user feedback)
                        # 2025-12-30: Adjusted to 5.0±0.4 for balanced human-like variation
                        multiplier = self.comment_processor.delay_multiplier if self.comment_processor else 1.0
                        if self.human:
                            # Base 5s with 40% variance = 3s-7s
                            base_delay = self.human.human_delay(5.0, 0.4) * multiplier
                            # 10% chance of extra brief delay
                            if random.random() < 0.10:
                                extra = random.uniform(2.0, 4.0)
                                delay = base_delay + extra
                                logger.info(f"[DAEMON][PHASE-3]   Refresh delay: {delay:.1f}s (extended)")
                            else:
                                delay = base_delay
                                logger.info(f"[DAEMON][PHASE-3]   Refresh delay: {delay:.1f}s")
                            await asyncio.sleep(delay)
                        else:
                            await asyncio.sleep(5 * multiplier)
                        logger.info(f"[DAEMON][PHASE-3] ✅ Page refreshed - ready for next comment")
                else:
                    logger.info(f"[DAEMON][PHASE-3] ⏭️ SKIP REFRESH: Batching comments (batch size: {self._comments_since_refresh}/5)")
                    logger.debug(f"[ANTI-DETECTION] Skipped refresh to create natural variation")
            else:
                logger.info(f"[DAE-REFRESH] SKIPPING REFRESH: refresh_between={refresh_between} or at max ({total_processed}/{effective_max})")
        
        # Check if all comments were processed (tab is clear)
        logger.info(f"[DAEMON][PHASE-4] 🏁 COMPLETION CHECK: Verifying inbox status...")
        remaining_comments = self.get_comment_count()
        logger.info(f"[DAEMON][PHASE-4]   Remaining comments (DOM): {remaining_comments}")

        if remaining_comments == 0 and self.use_vision:
            # DOM may not expose comment threads; use vision to detect whether any comment is still present
            logger.debug(f"[DAEMON][PHASE-4]   Verifying with vision...")
            if await self.comment_processor._vision_exists(self.VISION_DESCRIPTIONS["has_comment"], min_confidence=0.4, timeout=60):
                remaining_comments = 1
                logger.info(f"[DAEMON][PHASE-4]   Vision detected remaining comments")
        all_processed = (remaining_comments == 0)

        if all_processed:
            logger.info(f"[DAEMON][PHASE-4] ✅ ALL COMMENTS PROCESSED - Inbox is 100% clear!")
            logger.info("[DAE] ALL COMMENTS PROCESSED - Community tab is clear!")
        else:
            logger.info(f"[DAEMON][PHASE-4] ⚪ Partial completion - {remaining_comments} comments remaining")
        
        # Save telemetry
        self.stats['all_processed'] = all_processed
        summary = {
            'session_id': self.session_id,
            'channel_id': self.channel_id,
            'total_processed': total_processed,
            'stats': self.stats,
            'results': all_results,
        }
        
        telemetry_file = TELEMETRY_DIR / f"session_{self.session_id}.json"
        with open(telemetry_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"\n{'='*60}")
        logger.info(f" SESSION COMPLETE")
        logger.info(f" Processed: {self.stats['comments_processed']}")
        logger.info(f" Likes: {self.stats['likes']}")
        logger.info(f" Hearts: {self.stats['hearts']}")
        logger.info(f" Replies: {self.stats['replies']}")
        logger.info(f"{'='*60}\n")

        # ANTI-DETECTION: Probabilistic break system (human-like rest periods)
        # Pattern learned from party_reactor cooldown + sophistication_engine fatigue
        if self._should_take_break(total_processed):
            duration, reason = self._calculate_break_duration()
            self._on_break_until = time.time() + duration
            self._last_break_reason = reason
            self._total_breaks_taken += 1

            # Reset session counter for long breaks
            if reason in ["long", "very_long", "off_day"]:
                self._sessions_since_long_break = 0
            else:
                self._sessions_since_long_break += 1

            # Human-readable logging (5 break types)
            if reason == "off_day":
                hours = duration / 3600
                logger.info(f"[ANTI-DETECTION] 🌙 Taking day off! ({hours:.1f} hours) - Break #{self._total_breaks_taken}")
                logger.info(f"[DAE] Taking extended break (day off) - next check in {hours:.1f} hours")
            elif reason == "very_long":
                hours = duration / 3600
                logger.info(f"[ANTI-DETECTION] 😴 Taking very long break ({hours:.1f} hours) - Break #{self._total_breaks_taken}")
                logger.info(f"[DAE] Taking extended break ({hours:.1f} hours)")
            elif reason == "long":
                hours = duration / 3600
                logger.info(f"[ANTI-DETECTION] ☕ Taking long break ({hours:.1f} hours) - Break #{self._total_breaks_taken}")
                logger.info(f"[DAE] Taking break ({hours:.1f} hours)")
            elif reason == "medium":
                minutes = duration / 60
                logger.info(f"[ANTI-DETECTION] 🚶 Taking medium break ({minutes:.0f} minutes) - Break #{self._total_breaks_taken}")
                logger.info(f"[DAE] Taking break ({minutes:.0f} minutes)")
            else:  # short
                minutes = duration / 60
                logger.info(f"[ANTI-DETECTION] ⏸️ Taking short break ({minutes:.0f} minutes) - Break #{self._total_breaks_taken}")
                logger.info(f"[DAE] Taking short break ({minutes:.0f} minutes)")

            # Persist break state (survives subprocess restarts)
            self._save_break_state()
        else:
            self._sessions_since_long_break += 1
            logger.debug(f"[ANTI-DETECTION] ⚡ No break - continuing work (sessions since long break: {self._sessions_since_long_break}/6)")
            # Save updated session counter
            self._save_break_state()

        # ARCHITECTURE FIX (2025-12-28): Comment DAE should ONLY process comments
        # Live stream navigation is handled by the orchestrator (auto_moderator_dae.py)
        # based on heartbeat signals from stream_resolver.
        #
        # Occam's Razor: Comments DAE = Comments ONLY
        # - Do NOT navigate to live streams
        # - Do NOT check if streams are live
        # - Just process comments and return
        #
        # The calling orchestrator will:
        # 1. Rotate to next channel (M2J → UnDaoDu → FoundUps)
        # 2. Check stream_resolver heartbeat signal
        # 3. If live detected → pause rotation, focus on that channel's live chat
        logger.info(f"[DAE] Session complete - returning control to orchestrator")
        logger.info(f"[DAE]   Processed: {total_processed} comments")
        logger.info(f"[DAE]   Browser remains on Studio inbox (by design)")

        return summary
    
    def close(self) -> None:
        """Release resources."""
        if self.ui_tars_bridge:
            self.ui_tars_bridge.close()
        logger.info("[DAE] Resources released")


async def execute_skill(
    channel_id: str,
    video_id: str = None,
    video_title: str = None,
    max_comments: int = 5,
    do_like: bool = True,
    do_heart: bool = True,
    reply_text: str = "",
    use_vision: bool = True,
    use_intelligent_reply: bool = True
) -> Dict[str, Any]:
    """
    WRE Skill Entry Point - WSP 96 Compliant.

    Args:
        channel_id: YouTube channel ID
        video_id: YouTube video ID (for live stream comments, None = channel inbox)
        video_title: Video title for context-aware replies (alignment detection)
        max_comments: Maximum comments to process
        do_like: Enable like action
        do_heart: Enable heart action
        reply_text: Optional custom reply text (overrides intelligent reply)
        use_vision: Enable UI-TARS verification
        use_intelligent_reply: Use intelligent reply generator (BanterEngine + Whack-a-MAGA)

    Returns:
        Engagement session summary with commenter classifications
    """
    dae = CommentEngagementDAE(
        channel_id=channel_id,
        video_id=video_id,
        video_title=video_title,
        use_vision=use_vision,
        use_dom=True
    )
    
    try:
        await dae.connect()
        await dae.navigate_to_inbox()
        
        return await dae.engage_all_comments(
            max_comments=max_comments,
            do_like=do_like,
            do_heart=do_heart,
            reply_text=reply_text,
            use_intelligent_reply=use_intelligent_reply,
        )
    finally:
        dae.close()
