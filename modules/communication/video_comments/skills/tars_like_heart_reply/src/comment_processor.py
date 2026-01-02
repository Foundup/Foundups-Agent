"""
Comment Processor - Extracted from comment_engagement_dae.py

WSP 62 Refactoring Phase 2: Reduces comment_engagement_dae.py from 1473 → ~1069 lines
Extracted comment engagement and data extraction logic (~404 lines).

Pattern: Dependency injection (driver, stats, reply_executor passed to constructor)
"""

import asyncio
import logging
import os
import random
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ============================================================================
# CROSS-COMMENT LOOP PREVENTION (ADR-012)
# ============================================================================
# Owned channel names - NEVER reply to comments from these channels
# to prevent infinite cross-commenting loops between our own channels.
# Like/Heart only, no reply. 0102 behavior: Like = silent acknowledgment.
OWNED_CHANNELS = frozenset([
    "Move2Japan",
    "UnDaoDu",
    "FoundUps",
    "Foundups",  # Case variation
    "@Move2Japan",
    "@UnDaoDu",
    "@FoundUps",
    "@Foundups",
])


def is_owned_channel(username: str) -> bool:
    """
    Check if commenter is one of our owned channels.

    ADR-012: Cross-Comment Loop Prevention
    - If True → Like/Heart only, NO REPLY
    - Prevents infinite agent-to-agent commenting

    Args:
        username: Commenter display name or handle

    Returns:
        True if this is an owned channel
    """
    if not username:
        return False
    # Check exact match and handle variations
    clean_name = username.strip().lstrip('@')
    return username in OWNED_CHANNELS or clean_name in OWNED_CHANNELS or f"@{clean_name}" in OWNED_CHANNELS


# Import commenter history store (WSP 60 module memory)
try:
    from modules.communication.video_comments.src.commenter_history_store import (
        get_commenter_history_store,
        make_commenter_key,
    )
    COMMENTER_HISTORY_AVAILABLE = True
except ImportError as e:
    COMMENTER_HISTORY_AVAILABLE = False
    logger.warning(f"[CommentProcessor] Commenter history store not available: {e}")

# Import intelligent reply generator
try:
    from modules.communication.video_comments.src.intelligent_reply_generator import (
        get_reply_generator,
        CommenterType,
    )
    INTELLIGENT_REPLIES_AVAILABLE = True
except ImportError as e:
    INTELLIGENT_REPLIES_AVAILABLE = False
    logger.warning(f"[CommentProcessor] Intelligent replies not available: {e}")

# Import semantic state engine (WSP 44)
try:
    from modules.infrastructure.wsp_core.src.semantic_state_engine import SemanticStateEngine
    SEMANTIC_STATE_AVAILABLE = True
except Exception:
    SemanticStateEngine = None
    SEMANTIC_STATE_AVAILABLE = False

# Optional WRE monitor integration (best-effort)
try:
    from modules.infrastructure.wre_core.wre_monitor import get_monitor
    WRE_MONITOR_AVAILABLE = True
except Exception as e:
    WRE_MONITOR_AVAILABLE = False
    logger.debug(f"[CommentProcessor] WRE monitor unavailable: {e}")


class CommentProcessor:
    """
    Handles comment engagement orchestration and DOM data extraction.

    Responsibilities:
    - Extract comment data from DOM (author, text, timestamps)
    - Orchestrate engagement actions (like, heart, reply)
    - Coordinate with ReplyExecutor for reply posting
    - Update engagement stats
    """

    # Commenter type emoji tags (for debug mode)
    COMMENTER_TYPE_TAGS = {
        "moderator": "🧘",
        "maga_troll": "🤡",
        "subscriber": "🙌",
        "regular": "💬",
        "unknown": "❓",
    }

    def __init__(self, driver, human, stats, reply_executor, selectors, vision_descriptions=None, use_vision=False, use_dom=True, ui_tars_bridge=None, check_moderators=False, mod_lookup=None, reply_debug_tags=False, video_title=None):
        """
        Args:
            driver: Selenium WebDriver instance
            human: HumanBehavior instance (or None)
            stats: Dict tracking engagement stats
            reply_executor: BrowserReplyExecutor instance
            selectors: Dict of DOM selectors
            vision_descriptions: Dict of vision descriptions for UI-TARS (optional)
            use_vision: Enable vision verification (default False)
            use_dom: Enable DOM-based actions (default True)
            ui_tars_bridge: UITarsBridge instance for vision (optional)
            check_moderators: Enable moderator detection (default False)
            mod_lookup: ModeratorLookup instance (optional)
            reply_debug_tags: Append debug tags to replies (default False)
            video_title: Video title for context-aware replies (optional)
        """
        self.driver = driver
        self.human = human
        self.stats = stats
        self.reply_executor = reply_executor
        self.selectors = selectors
        self.VISION_DESCRIPTIONS = vision_descriptions or {}
        self.use_vision = use_vision
        self.use_dom = use_dom
        self.ui_tars_bridge = ui_tars_bridge
        self.check_moderators = check_moderators
        self.mod_lookup = mod_lookup
        self.reply_debug_tags = reply_debug_tags
        self.video_title = video_title  # NEW (2025-12-30): Video context for alignment detection

        # Tempo mode: Controls interaction speed (FAST | MEDIUM | 012)
        tempo = os.getenv("YT_ENGAGEMENT_TEMPO", "012").upper()
        # Backward compatibility for fast mode env var
        if os.getenv("YT_ENGAGEMENT_FAST_MODE", "0").lower() in {"1", "true", "yes"}:
            tempo = "MEDIUM"

        if tempo == "FAST":
            self.delay_multiplier = 0.1  # 10x faster - rapid testing
        elif tempo == "MEDIUM":
            self.delay_multiplier = 0.25  # 4x faster - quick diagnostics
        else:
            self.delay_multiplier = 1.0  # Human-like (012 long-term operation)

        logger.info(f"[CommentProcessor] TEMPO set to {tempo} (multiplier: {self.delay_multiplier}x)")

        # Reply layer switches (for incremental testing of refactored code)
        from modules.communication.livechat.src.automation_gates import _env_truthy
        self.reply_basic_only = _env_truthy("YT_REPLY_BASIC_ONLY", "false")
        self.no_classification = _env_truthy("YT_NO_CLASSIFICATION", "false")
        self.no_semantic_state = _env_truthy("YT_NO_SEMANTIC_STATE", "false")
        self.action_debug = _env_truthy("YT_ACTION_LOGS", "true")
        enable_wre = _env_truthy("FOUNDUPS_ENABLE_WRE", "true")
        enable_wre_monitor = _env_truthy("FOUNDUPS_ENABLE_WRE_MONITOR", "true")
        self.wre_action_learning = _env_truthy("WRE_ACTION_LEARNING", "true") and enable_wre and enable_wre_monitor
        self.wre_action_logs = _env_truthy("WRE_ACTION_LOGS", "false")
        
        # 012 Behavior: Configurable action probabilities (human-like randomization)
        # These control the "should_perform_action()" probability for each action
        self.like_probability = float(os.getenv("YT_012_LIKE_PROB", "0.85"))      # 85% default
        self.heart_probability = float(os.getenv("YT_012_HEART_PROB", "0.90"))    # 90% default
        self.reply_skip_probability = float(os.getenv("YT_012_REPLY_SKIP_PROB", "0.50"))  # 50% skip for Tier 1
        
        if tempo == "012" or self.delay_multiplier == 1.0:
            logger.info(f"[012-BEHAVIOR] Like prob: {self.like_probability}, Heart prob: {self.heart_probability}, Reply skip: {self.reply_skip_probability}")
        
        self.wre_monitor = None
        if self.wre_action_learning and WRE_MONITOR_AVAILABLE:
            try:
                self.wre_monitor = get_monitor()
                if self.wre_action_logs:
                    logger.info("[CommentProcessor] WRE action learning enabled")
            except Exception as e:
                self.wre_monitor = None
                logger.debug(f"[CommentProcessor] WRE monitor unavailable: {e}")

        if self.reply_basic_only:
            logger.info("[CommentProcessor] REPLY BASIC ONLY mode - skipping all AI layers")
        if self.no_classification:
            logger.info("[CommentProcessor] Classification layer DISABLED")
        if self.no_semantic_state:
            logger.info("[CommentProcessor] Semantic state layer DISABLED")
        if self.action_debug:
            logger.info("[CommentProcessor] Action logging enabled (YT_ACTION_LOGS=true)")

    async def click_element_dom(self, comment_idx: int, element_type: str) -> bool:
        """
        Phase 2: Agentic - Robust DOM click execution with Shadow DOM piercing.

        Args:
            comment_idx: 1-based comment index
            element_type: 'like', 'heart'

        Anti-Detection (WSP 49):
        - Uses Deep Shadow DOM Querying to find elements hidden in Shadow Roots
        - Fallback: execute_script() with recursive traversal
        """
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException

        element_selector = self.selectors[element_type]
        thread_selector = self.selectors["comment_thread"]

        # ROBUST SHADOW DOM SCRIPT
        # This script defines a recursive function to walk the DOM and Shadow DOMs
        find_and_click_script = f"""
        const threadIndex = arguments[0];
        const targetSelector = arguments[1];

        function findInShadow(root, selector) {{
            if (!root) return null;

            // direct check
            const el = root.querySelector(selector);
            if (el) return el;

            // recursive check in children with shadow roots
            const children = root.querySelectorAll('*');
            for (let child of children) {{
                if (child.shadowRoot) {{
                    const found = findInShadow(child.shadowRoot, selector);
                    if (found) return found;
                }}
            }}
            return null;
        }}

        function collectThreads() {{
            const direct = document.querySelectorAll('{thread_selector}');
            if (direct && direct.length) return Array.from(direct);
            const results = [];
            const stack = [document];
            while (stack.length) {{
                const node = stack.pop();
                if (!node || !node.querySelectorAll) continue;
                try {{
                    const found = node.querySelectorAll('{thread_selector}');
                    for (const el of found) results.push(el);
                }} catch (e) {{}}
                const children = node.querySelectorAll('*');
                for (const child of children) {{
                    if (child.shadowRoot) stack.push(child.shadowRoot);
                }}
            }}
            return results;
        }}

        const threads = collectThreads();
        if (!threads || threads.length <= threadIndex) {{
            return {{success: false, error: 'Thread ' + threadIndex + ' not found'}};
        }}
        const thread = threads[threadIndex];
        
        // Try finding element deep in shadow DOM
        // Start from thread (container) or its shadow root
        const startNode = thread.shadowRoot || thread;
        const targetElement = findInShadow(startNode, targetSelector);

        if (targetElement) {{
            targetElement.scrollIntoView({{behavior: 'smooth', block: 'center'}});
            targetElement.click();
            return {{success: true}};
        }} else {{
            return {{success: false, error: 'Element ' + targetSelector + ' not found in Deep Shadow DOM'}};
        }}
        """

        try:
            # Execute the robust script
            result = self.driver.execute_script(find_and_click_script, comment_idx - 1, element_selector)
            
            success = result.get('success', False)
            if success:
                logger.info(f"[DOM] {element_type.upper()} clicked via Deep Shadow Query")
                return True
            else:
                logger.warning(f"[DOM] {element_type.upper()} click failed: {result.get('error')}")
                return False

        except Exception as e:
            logger.warning(f"[DOM] {element_type} click script exception: {e}")
            return False

    async def hide_user_from_channel(self, comment_idx: int, username: str) -> bool:
        """
        ANTI-SPAM NUCLEAR OPTION: Hide user from channel.

        This permanently blocks the user and removes ALL their comments.
        Use only for confirmed spam trolls (>2 rate limit violations).

        Args:
            comment_idx: 1-based comment index
            username: Username for logging

        Returns:
            bool: True if hide successful, False otherwise
        """
        import asyncio

        logger.warning(f"[ANTI-SPAM] ☢️ HIDING USER FROM CHANNEL: @{username}")
        logger.warning(f"[ANTI-SPAM]   This will permanently block user and remove ALL comments")

        action_menu_selector = self.selectors['action_menu']
        thread_selector = self.selectors["comment_thread"]

        # STEP 1: Click action menu (3-dot icon)
        click_menu_script = f"""
        const threadIndex = arguments[0];
        const menuSelector = arguments[1];

        function findInShadow(root, selector) {{
            if (!root) return null;
            const el = root.querySelector(selector);
            if (el) return el;
            const children = root.querySelectorAll('*');
            for (let child of children) {{
                if (child.shadowRoot) {{
                    const found = findInShadow(child.shadowRoot, selector);
                    if (found) return found;
                }}
            }}
            return null;
        }}

        const threads = document.querySelectorAll('{thread_selector}');
        if (!threads || threads.length <= threadIndex) {{
            return {{success: false, error: 'Thread not found'}};
        }}
        const thread = threads[threadIndex];
        const startNode = thread.shadowRoot || thread;
        const menuButton = findInShadow(startNode, menuSelector);

        if (menuButton) {{
            menuButton.scrollIntoView({{behavior: 'smooth', block: 'center'}});
            menuButton.click();
            return {{success: true}};
        }} else {{
            return {{success: false, error: 'Action menu button not found'}};
        }}
        """

        try:
            # Click action menu
            result = self.driver.execute_script(click_menu_script, comment_idx - 1, action_menu_selector)
            if not result.get('success'):
                logger.error(f"[ANTI-SPAM] Failed to open action menu: {result.get('error')}")
                return False

            logger.info(f"[ANTI-SPAM] ✓ Action menu opened")
            await asyncio.sleep(0.5 * self.delay_multiplier)  # Wait for menu to appear

            # STEP 2: Click "Hide user from channel" option
            # Find the menu item with text "Hide user from channel"
            click_hide_script = """
            const items = document.querySelectorAll('tp-yt-paper-item');
            for (let item of items) {
                if (item.textContent.includes('Hide user from channel')) {
                    item.click();
                    return {success: true};
                }
            }
            return {success: false, error: 'Hide user option not found'};
            """

            result = self.driver.execute_script(click_hide_script)
            if not result.get('success'):
                logger.error(f"[ANTI-SPAM] Failed to click hide option: {result.get('error')}")
                return False

            logger.warning(f"[ANTI-SPAM] ☢️ USER HIDDEN: @{username} banned from channel")
            await asyncio.sleep(1.0 * self.delay_multiplier)  # Wait for action to complete

            return True

        except Exception as e:
            logger.error(f"[ANTI-SPAM] Error hiding user: {e}")
            return False

    def extract_comment_data(self, comment_idx: int) -> Dict[str, Any]:
        """
        Extract comment text and author info from DOM.
        
        Phase 0: Knowledge - Gather commenter information
        
        DOM Structure (YouTube Studio):
        - Comment text: yt-formatted-string#content-text
        - Author name: Link with channel URL or #author-text
        - Mod badge: Various badge selectors
        """
        try:
            data = self.driver.execute_script(r"""
                function collectThreads(selector) {
                    const direct = document.querySelectorAll(selector);
                    if (direct && direct.length) return Array.from(direct);
                    const results = [];
                    const stack = [document];
                    while (stack.length) {
                        const node = stack.pop();
                        if (!node || !node.querySelectorAll) continue;
                        try {
                            const found = node.querySelectorAll(selector);
                            for (const el of found) results.push(el);
                        } catch (e) {}
                        const children = node.querySelectorAll('*');
                        for (const child of children) {
                            if (child.shadowRoot) stack.push(child.shadowRoot);
                        }
                    }
                    return results;
                }

                const threads = collectThreads('ytcp-comment-thread');
                const thread = threads[arguments[0]];
                if (!thread) return null;
                
                // Extract comment text from yt-formatted-string#content-text
                // This is the actual comment content element
                let text = '';
                const contentText = thread.querySelector('yt-formatted-string#content-text');
                if (contentText) {
                    text = contentText.textContent.trim();
                } else {
                    // Fallback selectors
                    const contentEl = thread.querySelector('#content, .comment-text, ytcp-comment-renderer');
                    text = contentEl ? contentEl.textContent.trim() : '';
                }
                
                // Extract author handle/name and channel ID
                let authorName = 'Unknown';
                let authorHandle = 'Unknown';
                let channelId = null;
                const authorEl = thread.querySelector('#author-text, yt-formatted-string.author-text, a#name, .author-name, a[href*="/channel/"], a[href^="/@"]');
                if (authorEl) {
                    const raw = authorEl.textContent.trim().replace(/\\s+/g, ' ');
                    authorHandle = raw;
                    authorName = raw.replace(/^@/, '');

                    // Extract channel ID from href (if available)
                    const authorLink = thread.querySelector('a[href*="/channel/"]');
                    if (authorLink) {
                        const href = authorLink.href;
                        const match = href.match(/\/channel\/([^\/\?]+)/);
                        if (match) {
                            channelId = match[1];
                        }
                    }
                }

                // Check for mod badge (moderator indicator)
                const modBadge = thread.querySelector('.mod-badge, [aria-label*="Moderator"], .moderator-badge');
                const isMod = !!modBadge;

                // Check for subscriber/member badge
                const subBadge = thread.querySelector('.subscriber-badge, [aria-label*="Member"], .member-badge');
                const isSubscriber = !!subBadge;

                // Extract published time (e.g., "3 months ago", "1 year ago")
                // FIX (2025-12-30): YouTube Studio uses different selectors than regular YouTube
                // FIX (2025-12-30): Enhanced selectors for YouTube Studio comment inbox
                let publishedTime = null;

                // Try multiple selectors (YouTube Studio + regular YouTube)
                // Ordered by specificity - most specific first
                const timeSelectors = [
                    // YouTube Studio specific (2025-12-30 enhanced)
                    'span.published-time',                       // Direct span class
                    '#published-time',                           // ID-based
                    'ytcp-comment-view-model #published-time',   // Studio model with ID
                    'ytcp-comment-view #published-time',         // Studio view with ID
                    '.ytcp-comment-header span',                 // Header span (often contains time)
                    '#header #published-time-text',              // Header published time
                    // Regular YouTube selectors
                    'yt-formatted-string.published-time-text',   // Regular YouTube
                    '.published-time-text',                      // Regular YouTube (class)
                    '#published-time-text',                      // ID-based
                    'ytcp-comment-view span:not(.author)',       // YouTube Studio: spans that aren't author
                    '.ytcp-comment-view-model span',             // YouTube Studio model
                    '[slot="published-time"]',                   // Slot-based
                ];

                for (const selector of timeSelectors) {
                    const el = thread.querySelector(selector);
                    if (el && el.textContent.includes('ago')) {
                        publishedTime = el.textContent.trim();
                        console.log('[DOM-DEBUG] Found time via selector:', selector, publishedTime);
                        break;
                    }
                }

                // Fallback 1: Search spans for "ago" pattern
                if (!publishedTime) {
                    const spans = thread.querySelectorAll('span');
                    for (const span of spans) {
                        const text = span.textContent.trim();
                        if (text.includes('ago') && /\d+/.test(text)) {
                            publishedTime = text;
                            console.log('[DOM-DEBUG] Found time via span scan:', publishedTime);
                            break;
                        }
                    }
                }

                // Fallback 2: Search for any text containing "ago" pattern in full thread text
                if (!publishedTime) {
                    const allText = thread.textContent;
                    // Enhanced regex: handles "yr", "mo", abbreviated forms
                    const agoMatch = allText.match(/(\d+\s*(?:second|minute|hour|day|week|month|year|yr|mo|wk|hr|min|sec)s?\s*ago)/i);
                    if (agoMatch) {
                        publishedTime = agoMatch[1];
                        console.log('[DOM-DEBUG] Found time via regex fallback:', publishedTime);
                    }
                }

                // Fallback 3: Look for relative time patterns like "Edited 1 year ago"
                if (!publishedTime) {
                    const allText = thread.textContent;
                    const editedMatch = allText.match(/(?:edited\s+)?(\d+\s*(?:second|minute|hour|day|week|month|year)s?\s*ago)/i);
                    if (editedMatch) {
                        publishedTime = editedMatch[1];
                        console.log('[DOM-DEBUG] Found time via edited pattern:', publishedTime);
                    }
                }

                return {
                    text: text.substring(0, 500),
                    author_name: authorName,
                    author_handle: authorHandle,
                    channel_id: channelId,
                    is_mod: isMod,
                    is_subscriber: isSubscriber,
                    published_time: publishedTime
                };
            """, comment_idx - 1)
            
            if data:
                logger.info(
                    "[DAE] Extracted comment by %s (ID: %s, len=%s)",
                    data.get("author_name"),
                    data.get("channel_id", "N/A"),
                    len(data.get("text", "") or ""),
                )
                # FIX (2025-12-30): Log published_time for debugging
                published_time = data.get("published_time")
                if published_time:
                    logger.info(f"[DAE] 📅 Comment age: '{published_time}'")
                else:
                    logger.warning("[DAE] ⚠️ Could not extract published_time from DOM")
                return data
            else:
                # OCCAM'S RAZOR: No DOM thread at index = no comment exists
                # Return None instead of fallback dict (first principles detection)
                logger.debug(f"[DAE] No DOM thread at index - comment doesn't exist")
                return None

        except Exception as e:
            logger.warning(f"[DAE] Failed to extract comment data: {e}")
            return {'text': '', 'author_name': 'Unknown', 'channel_id': None, 'is_mod': False, 'is_subscriber': False, 'published_time': None}

    @staticmethod
    def parse_comment_age_days(published_time: str) -> Optional[int]:
        """
        Parse published time string to approximate days ago.

        Examples:
            "3 months ago" -> 90
            "1 day ago" -> 1
            "5 weeks ago" -> 35
            "2 years ago" -> 730

        Returns:
            Days ago (int) or None if unable to parse
        """
        if not published_time:
            logger.info("[DATE-CHECK] 📅 No published time available")
            return None

        import re
        logger.info(f"[DATE-CHECK] 📅 Checking comment age: '{published_time}'")

        # Normalize text
        text = published_time.lower().strip()

        # Extract number and unit
        match = re.search(r'(\d+)\s*(second|minute|hour|day|week|month|year)', text)
        if not match:
            return None

        value = int(match.group(1))
        unit = match.group(2)

        # Convert to days (approximate)
        conversions = {
            'second': value / 86400,
            'minute': value / 1440,
            'hour': value / 24,
            'day': value,
            'week': value * 7,
            'month': value * 30,  # Approximate
            'year': value * 365
        }

        days = conversions.get(unit, 0)
        return int(days)
    
    async def engage_comment(
        self,
        comment_idx: int,
        do_like: bool = True,
        do_heart: bool = True,
        reply_text: str = "",
        do_reply: bool = True,
        use_intelligent_reply: bool = True
    ) -> Dict[str, Any]:
        """
        Engage with a single comment: Like + Heart + Reply.

        Phase 0: Knowledge - Extract commenter info
        Phase 1: Protocol - Decision on actions and response type
        Phase 2: Agentic - Execution with verification

        Args:
            comment_idx: 1-based comment index
            do_like: Execute like action
            do_heart: Execute heart action
            reply_text: Custom reply text (overrides intelligent reply if provided)
            do_reply: Execute reply action (WSP 91 switch - default True)
            use_intelligent_reply: Use intelligent reply generator (default True)
        """
        results = {
            'comment_idx': comment_idx,
            'like': False,
            'heart': False,
            'reply': False,
            'author_name': 'Unknown',
            'commenter_type': 'unknown',
            'errors': [],
        }

        action_plan = {
            "like": {"requested": bool(do_like), "intended": bool(do_like), "attempted": False, "success": False, "path": "skipped", "reason": None},
            "heart": {"requested": bool(do_heart), "intended": bool(do_heart), "attempted": False, "success": False, "path": "skipped", "reason": None},
            "reply": {"requested": bool(do_reply), "intended": bool(do_reply), "attempted": False, "success": False, "path": "skipped", "reason": None},
        }
        reply_text_to_post = ""
        used_intelligent = False
        
        # Phase 0: Knowledge - Extract comment data
        logger.info(f"[CARDIOVASCULAR] [PROCESS-COMMENT-{comment_idx}] ═══ START ═══")
        logger.info(f"[DAE-ENGAGE]   Flags: Like={do_like} | Heart={do_heart} | Reply={do_reply}")

        comment_data = self.extract_comment_data(comment_idx)

        # OCCAM'S RAZOR: If extract returns None, no comment exists (DOM element missing)
        if comment_data is None:
            logger.info(f"[DAE-ENGAGE] ⚪ NO COMMENT at index {comment_idx} - DOM thread doesn't exist")
            logger.info(f"[DAE] NO COMMENTS - First principles detection (no DOM element)")
            return {
                'comment_idx': comment_idx,
                'no_comment_exists': True,  # Signal to DAE: stop loop
                'like': False,
                'heart': False,
                'reply': False,
                'author_name': 'N/A',
                'commenter_type': 'none',
                'errors': ['No DOM thread at index']
            }

        results['author_name'] = comment_data.get('author_name', 'Unknown')
        results["commenter_handle"] = comment_data.get("author_handle") or comment_data.get("author_name") or "Unknown"
        results["commenter_channel_id"] = comment_data.get("channel_id")
        try:
            context_flags = self._get_context_flags(comment_data)
        except Exception as e:
            logger.warning(f"[DAE-ENGAGE] Context flags extraction failed: {e}")
            context_flags = {}
        results["context"] = context_flags

        logger.info(f"[DAE-ENGAGE] Processing comment {comment_idx} from {results['author_name']}...")
        logger.info(f"[DAE-ENGAGE]   Comment text: {comment_data.get('text', '')[:100]}...")

        # ============================================================
        # ADR-012: CROSS-COMMENT LOOP PREVENTION
        # ============================================================
        # Check if commenter is one of our owned channels
        # If so: Like/Heart ONLY, NO REPLY (prevents infinite loop)
        commenter_name = results.get('author_name', '')
        if is_owned_channel(commenter_name):
            logger.info(f"[ADR-012] 🔄 OWNED CHANNEL DETECTED: {commenter_name}")
            logger.info(f"[ADR-012]   → Suppressing REPLY to prevent cross-comment loop")
            logger.info(f"[ADR-012]   → Will still Like/Heart (silent acknowledgment)")
            do_reply = False  # Override: Never reply to own channels
            action_plan["reply"]["intended"] = False
            action_plan["reply"]["reason"] = "ADR-012: Owned channel - loop prevention"
            results['owned_channel_detected'] = True

        if os.getenv("YT_OCCAM_MODE", "false").lower() == "true":
             # Occam mode now uses the standard path BUT the standard path is now HARBED against AI failure.
             # This logging is kept just for confirmation.
             logger.info("[OCCAM] Mode active via Environment Variable - All AI layers will fallback if slow.")

        # Phase 0.5: Moderator Detection - Check if commenter is active moderator
        if self.check_moderators and self.mod_lookup and comment_data.get('channel_id'):
            channel_id = comment_data['channel_id']
            is_active_mod, mod_name = self.mod_lookup.is_active_moderator(
                channel_id,
                activity_window_minutes=10
            )

            if is_active_mod:
                logger.info(f"[MOD-DETECT] [POSTER-LOOKUP] 🔍 Verified in DB: @{mod_name} (ACTIVE MODERATOR)")
                self.stats['moderators_detected'] += 1
                results['moderator_detected'] = True
                results['moderator_name'] = mod_name

                # TODO: Post notification to live chat (requires AutoModeratorDAE integration)
                # For now, just log the detection
            else:
                logger.info(f"[MOD-DETECT] [POSTER-LOOKUP] 🔍 User not in moderator DB")
                results['moderator_detected'] = False
        else:
            results['moderator_detected'] = False

        # Detect whether DOM comment threads are accessible (YouTube Studio often uses shadow DOM)
        dom_threads_accessible = self.get_comment_count() > 0
        if not dom_threads_accessible and self.use_vision:
            logger.info("[DAE] DOM comment threads not accessible - using UI-TARS vision fallback")
        if self.action_debug:
            logger.info(
                "[DAE-ENGAGE]   dom_threads_accessible=%s use_dom=%s use_vision=%s ui_tars=%s",
                dom_threads_accessible,
                self.use_dom,
                self.use_vision,
                bool(self.ui_tars_bridge),
            )

        # Anti-Detection (WSP 49): Random action order + probabilistic execution
        # Build action queue with requested actions
        action_queue = []
        if do_like:
            action_queue.append('like')
        if do_heart:
            action_queue.append('heart')
        # Reply will be added to queue later after intelligent reply generation

        # Shuffle action order (humans don't always like→heart→reply in same sequence)
        if self.human and len(action_queue) > 1:
            random.shuffle(action_queue)
            logger.info(f"  [ANTI-DETECT] Initial action order: {' → '.join(action_queue)}")
        elif self.action_debug and action_queue:
            logger.info(f"  [ANTI-DETECT] Action order: {' → '.join(action_queue)}")

        # 1. LIKE
        if do_like:
            action_plan["like"]["intended"] = True
            # Probabilistic execution (configurable via YT_012_LIKE_PROB, default 85%)
            if self.human and not self.human.should_perform_action(self.like_probability):
                action_plan["like"]["intended"] = False
                action_plan["like"]["reason"] = "random_skip"
                logger.info(f"  [LIKE] SKIPPED (012 random: {int(self.like_probability*100)}% prob)")
                results['like'] = False
            else:
                logger.info(f"  [LIKE] Executing...")
                like_ok = False
                if dom_threads_accessible and self.use_dom:
                    action_plan["like"]["attempted"] = True
                    action_plan["like"]["path"] = "dom"
                    like_ok = await self.click_element_dom(comment_idx, 'like')
                    if self.action_debug:
                        logger.info(f"  [LIKE] DOM click result={like_ok}")
                    if like_ok:
                        # CRITICAL: Min 0.8s delay for YouTube API persistence (bug fix 2025-12-23)
                        # Before: 0.5s * 0.3 (fast mode) = 0.15s (too fast - API call not completed before refresh)
                        # After: max(calculated_delay, 0.8s) ensures Like persists before page refresh
                        if self.human:
                            calculated_delay = self.human.human_delay(0.5, 0.3) * self.delay_multiplier
                            await asyncio.sleep(max(calculated_delay, 0.8))  # Min 0.8s for API persistence
                        else:
                            calculated_delay = 0.5 * self.delay_multiplier
                            await asyncio.sleep(max(calculated_delay, 0.8))  # Min 0.8s for API persistence
                        like_ok = await self._verify_action_with_vision(
                            "LIKE",
                            self.VISION_DESCRIPTIONS["like_verify"],
                            timeout=30.0,
                        )

                if not like_ok and self.use_vision:
                    if self.action_debug:
                        logger.info(f"  [LIKE] Vision fallback engaged (ui_tars={bool(self.ui_tars_bridge)})")
                    action_plan["like"]["attempted"] = True
                    if action_plan["like"]["path"] == "dom":
                        action_plan["like"]["path"] = "dom+vision"
                    else:
                        action_plan["like"]["path"] = "vision"
                    like_ok = await self._vision_click_verified(
                        action_name="LIKE",
                        click_description=self.VISION_DESCRIPTIONS["like_click"],
                        verify_description=self.VISION_DESCRIPTIONS["like_verify"],
                        max_retries=3,
                        min_confidence=0.6,
                        require_verification=False,
                    )

                results['like'] = bool(like_ok)
                self.stats['likes'] += 1 if results['like'] else 0
                logger.info(f"  [LIKE] {'OK' if results['like'] else 'FAIL'}")
        else:
            action_plan["like"]["intended"] = False
            action_plan["like"]["reason"] = "disabled"
            logger.info("  [LIKE] DISABLED (do_like=False)")

            # Human-like delay between actions (randomized 0.4s-1.6s, 0.1s-0.4s in fast mode)
            if self.human:
                await asyncio.sleep(self.human.human_delay(1.0, 0.6) * self.delay_multiplier)
            else:
                await asyncio.sleep(1 * self.delay_multiplier)

        action_plan["like"]["success"] = bool(results.get("like"))

        # 2. HEART
        if do_heart:
            action_plan["heart"]["intended"] = True
            # Probabilistic execution (configurable via YT_012_HEART_PROB, default 90%)
            if self.human and not self.human.should_perform_action(self.heart_probability):
                action_plan["heart"]["intended"] = False
                action_plan["heart"]["reason"] = "random_skip"
                logger.info(f"  [HEART] SKIPPED (012 random: {int(self.heart_probability*100)}% prob)")
                results['heart'] = False
            else:
                logger.info(f"  [HEART] Executing...")
                heart_ok = False
                if dom_threads_accessible and self.use_dom:
                    action_plan["heart"]["attempted"] = True
                    action_plan["heart"]["path"] = "dom"
                    heart_ok = await self.click_element_dom(comment_idx, 'heart')
                    if self.action_debug:
                        logger.info(f"  [HEART] DOM click result={heart_ok}")
                    if heart_ok:
                        # CRITICAL: Min 0.8s delay for YouTube API persistence (bug fix 2025-12-23)
                        # Heart uses same persistence logic as Like (ensures API call completes before refresh)
                        if self.human:
                            calculated_delay = self.human.human_delay(1.0, 0.6) * self.delay_multiplier
                            await asyncio.sleep(max(calculated_delay, 0.8))  # Min 0.8s for API persistence
                        else:
                            calculated_delay = 1 * self.delay_multiplier
                            await asyncio.sleep(max(calculated_delay, 0.8))  # Min 0.8s for API persistence
                        heart_ok = await self._verify_action_with_vision(
                            "HEART",
                            self.VISION_DESCRIPTIONS["heart_verify"],
                            timeout=30.0,
                        )

                if not heart_ok and self.use_vision:
                    if self.action_debug:
                        logger.info(f"  [HEART] Vision fallback engaged (ui_tars={bool(self.ui_tars_bridge)})")
                    action_plan["heart"]["attempted"] = True
                    if action_plan["heart"]["path"] == "dom":
                        action_plan["heart"]["path"] = "dom+vision"
                    else:
                        action_plan["heart"]["path"] = "vision"
                    heart_ok = await self._vision_click_verified(
                        action_name="HEART",
                        click_description=self.VISION_DESCRIPTIONS["heart_click"],
                        verify_description=self.VISION_DESCRIPTIONS["heart_verify"],
                        max_retries=3,
                        min_confidence=0.6,
                        require_verification=False,
                    )

                results['heart'] = bool(heart_ok)
                self.stats['hearts'] += 1 if results['heart'] else 0
                logger.info(f"  [HEART] {'OK' if results['heart'] else 'FAIL'}")
        else:
            action_plan["heart"]["intended"] = False
            action_plan["heart"]["reason"] = "disabled"
            logger.info("  [HEART] DISABLED (do_heart=False)")

            # Human-like delay between actions (randomized 0.4s-1.6s, 0.1s-0.4s in fast mode)
            if self.human:
                await asyncio.sleep(self.human.human_delay(1.0, 0.6) * self.delay_multiplier)
            else:
                await asyncio.sleep(1 * self.delay_multiplier)

        action_plan["heart"]["success"] = bool(results.get("heart"))

        # 3. REPLY
        if do_reply:
            action_plan["reply"]["intended"] = True
            logger.info(f"  [REPLY-START] Entering reply section (do_reply=True)")
            logger.info(f"  [REPLY-START]   reply_basic_only={self.reply_basic_only}")
            logger.info(f"  [REPLY-START]   use_intelligent_reply={use_intelligent_reply}")

            # Determine reply text (initially basic)
            actual_reply_text = reply_text
            
            # Default state (Tier 1 = Regular)
            tier = 1

            # Layer 3: Commenter Classification (MOVED BEFORE LAYER 2)
            # We need classification first to determine the reply strategy (Tier)
            if not self.no_classification and not self.reply_basic_only and INTELLIGENT_REPLIES_AVAILABLE:
                
                # Start Heartbeat
                hb_stop = asyncio.Event()
                hb_task = asyncio.create_task(self._thinking_heartbeat("Layer 3 (Classification)", hb_stop))

                try:
                    # STRICT TIMEOUT: 3 seconds for classification
                    async def _classify_wrapper():
                        generator = get_reply_generator()
                        return generator.classify_commenter(
                            author_name=comment_data.get('author_name', ''),
                            comment_text=comment_data.get('text', ''),
                            author_channel_id=comment_data.get('channel_id'),
                            is_mod=comment_data.get('is_mod', False),
                            is_subscriber=comment_data.get('is_subscriber', False)
                        )

                    profile = await asyncio.wait_for(_classify_wrapper(), timeout=3.0)
                    hb_stop.set()
                    
                    results['commenter_type'] = profile.commenter_type.value
                    
                    # === SMART ENGAGEMENT STRATEGY (Phase 3) ===
                    # 1. Base Tier Determination
                    # FIX (2025-12-30): Use .value (int 0/1/2) not .to_012_code() (string "0✊"/"1✋"/"2🖐️")
                    # TIER_EMOJI expects int keys: {0: "✊", 1: "✋", 2: "🖐️"}
                    tier = profile.commenter_type.value
                    logger.info(f"  [STRATEGY] Class: {profile.commenter_type.value} -> Base Tier: {tier} ({profile.commenter_type.to_012_code()})")
                    
                    # 2. Tier Escalation (Loyalty Reward)
                    # If Regular (1) and Older than 90 days -> Mod treatment (2)
                    days_ago = self.parse_comment_age_days(comment_data.get('published_time'))
                    if tier == 1 and days_ago >= 90:
                         logger.info(f"  [STRATEGY] Loyalty Escalation! Comment is {days_ago} days old. Promoting Tier 1 -> Tier 2.")
                         tier = 2
                    
                    # 3. Probabilistic Gating (Natural Pace)
                    # Tier 1 (Regular) -> configurable skip probability (YT_012_REPLY_SKIP_PROB)
                    if tier == 1 and random.random() < self.reply_skip_probability:
                         logger.info(f"  [STRATEGY] Randomly skipping reply for Tier 1 user ({int(self.reply_skip_probability*100)}% gate).")
                         do_reply = False
                         actual_reply_text = None 
                    
                    # Store Final Tier for Layer 2
                    comment_data['tier'] = tier

                except asyncio.TimeoutError:
                    hb_stop.set()
                    logger.warning(f"  [LAYER-3] Classification TIMEOUT (3s) - Defaulting to 'unknown'")
                    results['commenter_type'] = 'unknown'
                except Exception as e:
                    hb_stop.set()
                    logger.warning(f"  [LAYER-3] Classification ERROR: {e}")
                    results['commenter_type'] = 'unknown'
                finally:
                    if not hb_task.done():
                        hb_stop.set()
                        try:
                            await hb_task
                        except:
                            pass

            # Layer 2: Intelligent Reply Generation (skip if --reply-basic-only OR if strategy disabled do_reply)
            if do_reply and not actual_reply_text and use_intelligent_reply and not self.reply_basic_only:
                logger.info(f"  [LAYER-2] Generating intelligent reply (Tier: {comment_data.get('tier', 'default')})...")
                logger.info("[HARD-THINK] Layer 2: Invoking Intelligent Reply Generator...")
                
                # Start Heartbeat
                hb_stop = asyncio.Event()
                hb_task = asyncio.create_task(self._thinking_heartbeat("Layer 2 (Intelligence)", hb_stop))
                
                try:
                    # LLM TIMEOUT: 15 seconds for AI generation (Grok API can be slow)
                    # Previous 8s was too short - Grok needs ~10-12s for complex prompts
                    actual_reply_text = await asyncio.wait_for(
                        asyncio.to_thread(self._generate_intelligent_reply, comment_data),
                        timeout=15.0
                    )
                    hb_stop.set() # Stop heartbeat
                    
                    # Log result length for debugging
                    reply_len = len(actual_reply_text) if actual_reply_text else 0
                    logger.info(f"[HARD-THINK] Layer 2 Result: '{actual_reply_text[:50] if actual_reply_text else ''}...' (len={reply_len})")
                
                except asyncio.TimeoutError:
                    hb_stop.set()
                    logger.warning("[HARD-THINK] ⚠️ Layer 2 TIMEOUT (15s) - AI Generation too slow, check LLM connectivity")
                    actual_reply_text = None 
                except Exception as e:
                    hb_stop.set()
                    logger.error(f"[HARD-THINK] ⚠️ Layer 2 ERROR: {e}")
                    actual_reply_text = None
                finally:
                    # Ensure heartbeat is killed even if something crazy happens
                    if not hb_task.done():
                        hb_stop.set()
                        try:
                            await hb_task
                        except:
                            pass
                
                # FALLBACK MECHANISM (Occam's Safety Net)
                # CRITICAL FIX (2025-12-23): Distinguish between intentional skip vs failure
                # - Empty string "" = Intentional skip (anti-spam, probabilistic) → DON'T apply fallback
                # - None or whitespace = Failure → Apply fallback

                if actual_reply_text == "":
                    # Intentional skip (anti-spam, probabilistic engagement) - preserve empty string
                    logger.info("[HARD-THINK] Reply intentionally skipped (anti-spam/probabilistic) - no fallback applied")
                    # actual_reply_text remains "" - caller will handle this as "skip reply"

                elif not actual_reply_text or not actual_reply_text.strip():
                    # Failure case (None, whitespace-only) - apply fallback
                    if actual_reply_text is not None:
                        logger.warning(f"[HARD-THINK] ⚠️ AI returned WHITESPACE reply! Triggering fallback.")
                    else:
                        logger.warning(f"[HARD-THINK] ⚠️ AI returned None! Triggering fallback.")

                    logger.info("[HARD-THINK] Activiting Fallback Reply (Safe Template)")
                    # Simple, safe, engagement-oriented fallbacks
                    fallback_opts = [
                        "Thanks for watching! 🚀",
                        "Appreciate the comment! 🙏",
                        "Great point! 👍",
                        "FoundUps is the way! 💎",
                        "0102 logic engaged! ✊"
                    ]
                    actual_reply_text = random.choice(fallback_opts)
                    used_intelligent = False
                else:
                    used_intelligent = True

            # EXECUTION: Post the reply
            if do_reply and actual_reply_text and actual_reply_text.strip():
                # Add signature if not present (ANTI-SPAM / IDENTITY)
                # CRITICAL FIX (2025-12-30): Check if reply already has 0102 signature
                # IntelligentReplyGenerator.generate_reply() already applies signature
                # Applying it AGAIN caused duplicate holiday suffixes like "🗓️ 2026 incoming! 🗓️ 2026 incoming!"

                # Check if already signed (contains "0102" signature)
                already_signed = "0102" in actual_reply_text

                if already_signed:
                    # Reply already has signature from IntelligentReplyGenerator
                    reply_text_to_post = actual_reply_text
                    if self.action_debug:
                        logger.info(f"  [REPLY] Already signed (skipping duplicate signature): {actual_reply_text[:50]}...")
                elif INTELLIGENT_REPLIES_AVAILABLE:
                    # Fallback templates need signature (lines 862-869 fallback_opts don't have it)
                    generator = get_reply_generator()
                    tier_to_sign = comment_data.get('tier', 1)  # Default to Tier 1
                    reply_text_to_post = generator._add_0102_signature(actual_reply_text, tier=tier_to_sign)
                    if self.action_debug:
                        logger.info(f"  [REPLY] Signed reply: {reply_text_to_post[:50]}...")
                else:
                    reply_text_to_post = actual_reply_text

                # Optional: Append debug tags (e.g. [AI] [FALLBACK])
                if self.reply_debug_tags:
                    tag = "[AI]" if used_intelligent else "[TMPL]"
                    reply_text_to_post = f"{tag} {reply_text_to_post}"

                logger.info(f"  [REPLY] Executing reply via execute_reply()...")
                reply_ok = await self.reply_executor.execute_reply(comment_idx, reply_text_to_post)
                
                results['reply'] = bool(reply_ok)
                self.stats['replies'] += 1 if results['reply'] else 0
                logger.info(f"  [REPLY] {'OK' if results['reply'] else 'FAIL'}")
            elif do_reply:
                 logger.info("  [REPLY] SKIPPED - No reply text generated or intended.")
            else:
                 logger.info("  [REPLY] DISABLED (do_reply=False)")

        action_plan["reply"]["success"] = bool(results.get("reply"))

        # Final Log of the action plan state
        if self.action_debug:
            logger.info(f"[DAE-ENGAGE] Results for {results['author_name']}: L={results['like']} H={results['heart']} R={results['reply']} Type={results['commenter_type']}")
            
        return results

    def get_comment_count(self) -> int:
        """Get number of comment threads visible in DOM."""
        try:
            result = self.driver.execute_script("""
                const selector = 'ytcp-comment-thread';
                const directCount = document.querySelectorAll(selector).length;
                if (directCount) {
                    return {count: directCount, fallback: false};
                }
                const results = [];
                const stack = [document];
                while (stack.length) {
                    const node = stack.pop();
                    if (!node || !node.querySelectorAll) continue;
                    try {
                        const found = node.querySelectorAll(selector);
                        for (const el of found) results.push(el);
                    } catch (e) {}
                    const children = node.querySelectorAll('*');
                    for (const child of children) {
                        if (child.shadowRoot) stack.push(child.shadowRoot);
                    }
                }
                return {count: results.length, fallback: true};
            """)
            if isinstance(result, dict):
                count = int(result.get("count", 0))
                if result.get("fallback") and count > 0 and not getattr(self, "_shadow_threads_logged", False):
                    logger.info(f"[DAE-ENGAGE] Shadow DOM threads detected: {count}")
                    self._shadow_threads_logged = True
                return count
            return int(result or 0)
        except Exception:
            return 0

    async def _thinking_heartbeat(self, layer_name: str, stop_event: asyncio.Event):
        """Log periodic 'thinking' dots while AI is working to show activity."""
        start_time = time.time()
        while not stop_event.is_set():
            await asyncio.sleep(2.0)
            if stop_event.is_set():
                break
            elapsed = time.time() - start_time
            logger.info(f"  [HARD-THINK] {layer_name} still processing... ({elapsed:.1f}s)")

    def _generate_intelligent_reply(self, comment_data: Dict[str, Any]) -> str:
        """
        Synchronous wrapper for generating intelligent reply.
        Used within to_thread to prevent blocking the event loop.
        """
        if not INTELLIGENT_REPLIES_AVAILABLE:
            return None

        generator = get_reply_generator()
        return generator.generate_reply(
            author_name=comment_data.get('author_name', ''),
            comment_text=comment_data.get('text', ''),
            author_channel_id=comment_data.get('channel_id'),
            is_mod=comment_data.get('is_mod', False),
            is_subscriber=comment_data.get('is_subscriber', False),
            published_time=comment_data.get('published_time'),
            video_title=self.video_title  # NEW (2025-12-30): Pass video context for alignment detection
        )

    def _get_context_flags(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional context flags for strategy."""
        text = comment_data.get('text', '').lower()
        return {
            'is_question': '?' in text or any(w in text for w in ['how', 'why', 'what', 'when', 'where']),
            'is_positive': any(w in text for w in ['great', 'awesome', 'love', 'thanks', 'good', 'best']),
            'is_negative': any(w in text for w in ['bad', 'hate', 'worst', 'stop', 'why']),
        }

    async def _verify_action_with_vision(self, action_name: str, verify_description: str, timeout: float = 30.0) -> bool:
        """Verify action using UI-TARS vision if available."""
        if not self.use_vision or not self.ui_tars_bridge:
            return True
            
        logger.info(f"  [VISION-VERIFY] Verifying {action_name}...")
        try:
            result = await self.ui_tars_bridge.verify(
                description=verify_description,
                timeout=timeout,
                driver=self.driver
            )
            if result.success:
                logger.info(f"  [VISION-VERIFY] ✅ {action_name} verified (confidence: {result.confidence:.2f})")
                return True
            else:
                logger.warning(f"  [VISION-VERIFY] ❌ {action_name} verification failed: {result.error}")
                return False
        except Exception as e:
            logger.error(f"  [VISION-VERIFY] ❌ Vision verify error: {e}")
            return False

    async def _vision_exists(self, description: str, timeout: float = 15.0, min_confidence: float = 0.5) -> bool:
        """
        Check if an element exists using UI-TARS vision.
        Internal helper for _verify_action_with_vision.
        """
        if not self.use_vision or not self.ui_tars_bridge:
            return False

        try:
            logger.info(f"  [VISION-SCAN] Looking for: {description}...")
            result = await self.ui_tars_bridge.verify(
                description=description,
                timeout=timeout,
                driver=self.driver
            )
            return result.success and result.confidence >= min_confidence
        except Exception as e:
            logger.debug(f"[VISION] Existence check failed: {e}")
            return False

    async def _vision_click_verified(self, action_name: str, click_description: str, verify_description: str = None, max_retries: int = 2, min_confidence: float = 0.5, require_verification: bool = False) -> bool:
        """Execute click and verify using UI-TARS vision."""
        if not self.use_vision or not self.ui_tars_bridge:
            return False
            
        logger.info(f"  [VISION-ACTION] Executing vision-click for {action_name}...")
        
        for attempt in range(1, max_retries + 1):
            try:
                # Execute vision-based click
                result = await self.ui_tars_bridge.click(
                    description=click_description,
                    driver=self.driver,
                    timeout=90 # UI-TARS needs time for inference
                )
                
                if not result.success:
                    logger.warning(f"  [VISION-ACTION] ⚠️ Attempt {attempt} failed: {result.error}")
                    continue
                
                logger.info(f"  [VISION-ACTION] ✅ {action_name} click executed (confidence: {result.confidence:.2f})")
                
                if not verify_description or not require_verification:
                    return True
                
                # Perform verification if requested
                verified = await self._vision_exists(verify_description, timeout=10.0, min_confidence=min_confidence)
                if verified:
                    logger.info(f"  [VISION-ACTION] ✅ {action_name} verified after click")
                    return True
                else:
                    logger.warning(f"  [VISION-ACTION] ⚠️ {action_name} verification failed after click")
            
            except Exception as e:
                logger.error(f"  [VISION-ACTION] ❌ Vision error on attempt {attempt}: {e}")
                
        return False
