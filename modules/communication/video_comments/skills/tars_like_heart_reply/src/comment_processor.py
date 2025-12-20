"""
Comment Processor - Extracted from comment_engagement_dae.py

WSP 62 Refactoring Phase 2: Reduces comment_engagement_dae.py from 1473 → ~1069 lines
Extracted comment engagement and data extraction logic (~404 lines).

Pattern: Dependency injection (driver, stats, reply_executor passed to constructor)
"""

import asyncio
import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CommentProcessor:
    """
    Handles comment engagement orchestration and DOM data extraction.
    
    Responsibilities:
    - Extract comment data from DOM (author, text, timestamps)
    - Orchestrate engagement actions (like, heart, reply)
    - Coordinate with ReplyExecutor for reply posting
    - Update engagement stats
    """
    
    def __init__(self, driver, human, stats, reply_executor, selectors):
        """
        Args:
            driver: Selenium WebDriver instance
            human: HumanBehavior instance (or None)
            stats: Dict tracking engagement stats
            reply_executor: BrowserReplyExecutor instance
            selectors: Dict of DOM selectors
        """
        self.driver = driver
        self.human = human
        self.stats = stats
        self.reply_executor = reply_executor
        self.selectors = selectors

    async def click_element_dom(self, comment_idx: int, element_type: str) -> bool:
        """
        Phase 2: Agentic - DOM click execution with HUMAN-LIKE behavior.

        Args:
            comment_idx: 1-based comment index
            element_type: 'like', 'heart'

        Anti-Detection (WSP 49):
        - Primary: Selenium-native clicks with Bezier curves (anti-detection)
        - Fallback: execute_script() if Selenium fails (compatibility)
        """
        from selenium.webdriver.common.by import By

        # Try Selenium-native click first (anti-detection)
        if self.human:
            try:
                # Find the comment thread
                threads = self.driver.find_elements(By.CSS_SELECTOR, self.selectors["comment_thread"])
                if comment_idx > len(threads):
                    logger.warning(f"[DOM] Thread {comment_idx} not found (only {len(threads)} threads)")
                    raise ValueError(f"Thread {comment_idx} not found")

                thread = threads[comment_idx - 1]

                # Find the target element within the thread
                element_selector = self.selectors[element_type]
                element = thread.find_element(By.CSS_SELECTOR, element_selector)

                # Human-like interaction (anti-detection)
                # Scroll to element with smooth scrolling
                self.human.scroll_to_element(element)
                # Random pause before click (thinking time)
                await asyncio.sleep(self.human.human_delay(0.3, 0.5))
                # Click with Bezier curve mouse movement
                self.human.human_click(element)

                logger.info(f"[DOM] {element_type.upper()} clicked (human-like=True, method=selenium-native)")
                return True

            except Exception as selenium_error:
                logger.warning(f"[DOM] Selenium-native click failed: {selenium_error}, falling back to execute_script()")
                # Fall through to execute_script() fallback below

        # Fallback: execute_script() (works with Shadow DOM, less anti-detection)
        try:
            element_selector = self.selectors[element_type]

            result = self.driver.execute_script(f"""
                const threads = document.querySelectorAll('{self.selectors["comment_thread"]}');
                const thread = threads[arguments[0]];
                if (!thread) return {{success: false, error: 'Thread not found'}};

                const el = thread.querySelector(arguments[1]);
                if (!el) return {{success: false, error: 'Element not found'}};

                thread.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                el.click();
                return {{success: true}};
            """, comment_idx - 1, element_selector)

            success = result.get('success', False) if result else False
            logger.info(f"[DOM] {element_type.upper()} clicked (human-like={bool(self.human)}, method=execute_script, success={success})")
            return success

        except Exception as e:
            logger.warning(f"[DOM] {element_type} click failed (all methods): {e}")
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
                const threads = document.querySelectorAll('ytcp-comment-thread');
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

                return {
                    text: text.substring(0, 500),
                    author_name: authorName,
                    author_handle: authorHandle,
                    channel_id: channelId,
                    is_mod: isMod,
                    is_subscriber: isSubscriber
                };
            """, comment_idx - 1)
            
            if data:
                logger.info(
                    "[DAE] Extracted comment by %s (ID: %s, len=%s)",
                    data.get("author_name"),
                    data.get("channel_id", "N/A"),
                    len(data.get("text", "") or ""),
                )

            return data or {'text': '', 'author_name': 'Unknown', 'channel_id': None, 'is_mod': False, 'is_subscriber': False}

        except Exception as e:
            logger.warning(f"[DAE] Failed to extract comment data: {e}")
            return {'text': '', 'author_name': 'Unknown', 'channel_id': None, 'is_mod': False, 'is_subscriber': False}
    
    async def engage_comment(
        self,
        comment_idx: int,
        do_like: bool = True,
        do_heart: bool = True,
        reply_text: str = "",
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
        
        # Phase 0: Knowledge - Extract comment data
        comment_data = self._extract_comment_data(comment_idx)
        results['author_name'] = comment_data.get('author_name', 'Unknown')
        results["commenter_handle"] = comment_data.get("author_handle") or comment_data.get("author_name") or "Unknown"
        results["commenter_channel_id"] = comment_data.get("channel_id")
        context_flags = self._get_context_flags(comment_data)
        results["context"] = context_flags

        logger.info(f"[DAE-ENGAGE] Processing comment {comment_idx} from {results['author_name']}...")

        # Phase 0.5: Moderator Detection - Check if commenter is active moderator
        if self.check_moderators and self.mod_lookup and comment_data.get('channel_id'):
            channel_id = comment_data['channel_id']
            is_active_mod, mod_name = self.mod_lookup.is_active_moderator(
                channel_id,
                activity_window_minutes=10
            )

            if is_active_mod:
                logger.info(f"[MOD-DETECT] ACTIVE MODERATOR: {mod_name} commented!")
                logger.info(f"[MOD-DETECT] Notification: @{mod_name} commented on the community tab!")
                self.stats['moderators_detected'] += 1
                results['moderator_detected'] = True
                results['moderator_name'] = mod_name

                # TODO: Post notification to live chat (requires AutoModeratorDAE integration)
                # For now, just log the detection
            else:
                results['moderator_detected'] = False
        else:
            results['moderator_detected'] = False

        # Detect whether DOM comment threads are accessible (YouTube Studio often uses shadow DOM)
        dom_threads_accessible = self.get_comment_count() > 0
        if not dom_threads_accessible and self.use_vision:
            logger.info("[DAE] DOM comment threads not accessible - using UI-TARS vision fallback")

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

        # 1. LIKE
        if do_like:
            # Probabilistic execution (85% chance - humans don't like EVERY comment)
            if self.human and not self.human.should_perform_action(0.85):
                logger.info(f"  [LIKE] SKIPPED (random selectivity - anti-detection)")
                results['like'] = False
            else:
                logger.info(f"  [LIKE] Executing...")
                like_ok = False
                if dom_threads_accessible and self.use_dom:
                    like_ok = await self.click_element_dom(comment_idx, 'like')
                    if like_ok:
                        # Human-like delay after like (randomized 0.4s-1.6s)
                        if self.human:
                            await asyncio.sleep(self.human.human_delay(1.0, 0.6))
                        else:
                            await asyncio.sleep(1)
                        like_ok = await self._verify_action_with_vision(
                            "LIKE",
                            self.VISION_DESCRIPTIONS["like_verify"],
                            timeout=30.0,
                        )

                if not like_ok and self.use_vision:
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

            # Human-like delay between actions (randomized 0.4s-1.6s)
            if self.human:
                await asyncio.sleep(self.human.human_delay(1.0, 0.6))
            else:
                await asyncio.sleep(1)
        
        # 2. HEART
        if do_heart:
            # Probabilistic execution (90% chance - creator hearts are special but not guaranteed)
            if self.human and not self.human.should_perform_action(0.90):
                logger.info(f"  [HEART] SKIPPED (random selectivity - anti-detection)")
                results['heart'] = False
            else:
                logger.info(f"  [HEART] Executing...")
                heart_ok = False
                if dom_threads_accessible and self.use_dom:
                    heart_ok = await self.click_element_dom(comment_idx, 'heart')
                    if heart_ok:
                        # Human-like delay after heart (randomized 0.4s-1.6s)
                        if self.human:
                            await asyncio.sleep(self.human.human_delay(1.0, 0.6))
                        else:
                            await asyncio.sleep(1)
                        heart_ok = await self._verify_action_with_vision(
                            "HEART",
                            self.VISION_DESCRIPTIONS["heart_verify"],
                            timeout=30.0,
                        )

                if not heart_ok and self.use_vision:
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

            # Human-like delay between actions (randomized 0.4s-1.6s)
            if self.human:
                await asyncio.sleep(self.human.human_delay(1.0, 0.6))
            else:
                await asyncio.sleep(1)
        
        # 3. REPLY
        # Determine reply text
        actual_reply_text = reply_text
        if not actual_reply_text and use_intelligent_reply:
            # Generate intelligent reply based on commenter context
            actual_reply_text = self._generate_intelligent_reply(comment_data)
            
            # Track commenter type for stats
            if INTELLIGENT_REPLIES_AVAILABLE:
                try:
                    generator = get_reply_generator()
                    profile = generator.classify_commenter(
                        author_name=comment_data.get('author_name', ''),
                        comment_text=comment_data.get('text', ''),
                        author_channel_id=comment_data.get('channel_id'),
                        is_mod=comment_data.get('is_mod', False),
                        is_subscriber=comment_data.get('is_subscriber', False)
                    )
                    results['commenter_type'] = profile.commenter_type.value
                except Exception:
                    pass

        used_intelligent = bool((not reply_text) and use_intelligent_reply and INTELLIGENT_REPLIES_AVAILABLE)
        semantic_intent = self._compute_semantic_state(
            used_intelligent_reply=used_intelligent,
            has_studio_history=bool(context_flags.get("has_studio_history")),
            has_chat_history=bool(context_flags.get("has_chat_history")),
            like_ok=bool(results.get("like")),
            heart_ok=bool(results.get("heart")),
            reply_ok=bool(actual_reply_text),
        )
        if semantic_intent:
            results["semantic_state_intent"] = semantic_intent["code"]
            results["semantic_state_intent_reason"] = semantic_intent.get("reason")
            results["semantic_state_intent_digits"] = semantic_intent.get("digits")
            results["semantic_state_intent_context_level"] = semantic_intent.get("context_level")

        reply_text_raw = actual_reply_text
        reply_text_to_post = actual_reply_text
        if actual_reply_text:
            reply_text_to_post = self._append_debug_tag(
                actual_reply_text,
                commenter_type=str(results.get("commenter_type") or "unknown"),
                semantic_state=semantic_intent,
            )
        
        if reply_text_to_post:
            # Probabilistic execution (95% chance - replies show high engagement but not guaranteed)
            if self.human and not self.human.should_perform_action(0.95):
                logger.info(f"  [REPLY] SKIPPED (random selectivity - anti-detection)")
                results['reply'] = False
            else:
                logger.info(f"  [REPLY] Executing (len={len(reply_text_to_post)})")
                reply_ok = False
                if dom_threads_accessible and self.use_dom:
                    reply_ok = await self.reply_executor.execute_reply(comment_idx, reply_text_to_post)
                    if reply_ok:
                        verified = await self._verify_action_with_vision(
                            "REPLY",
                            self.VISION_DESCRIPTIONS["reply_verify"],
                            timeout=40.0,
                        )
                        if not verified:
                            logger.warning("[VISION] REPLY verification uncertain after DOM submit; proceeding to avoid duplicate replies")

                if not reply_ok and self.use_vision and self.ui_tars_bridge:
                    opened = await self._vision_click_verified(
                        action_name="REPLY_OPEN",
                        click_description=self.VISION_DESCRIPTIONS["reply_open_click"],
                        verify_description=self.VISION_DESCRIPTIONS["reply_box_verify"],
                        max_retries=3,
                        min_confidence=0.5,
                    )
                    if opened:
                        # Human-like delay before typing (randomized 0.4s-1.2s)
                        if self.human:
                            await asyncio.sleep(self.human.human_delay(0.8, 0.5))
                        else:
                            await asyncio.sleep(0.8)
                        type_res = await self.ui_tars_bridge.type_text(
                            description=self.VISION_DESCRIPTIONS["reply_input"],
                            text=reply_text_to_post,
                            driver=self.driver,
                            timeout=90,
                        )
                        if type_res.success:
                            # Human-like delay before submit (randomized 0.4s-1.2s)
                            if self.human:
                                await asyncio.sleep(self.human.human_delay(0.8, 0.5))
                            else:
                                await asyncio.sleep(0.8)
                            reply_ok = await self._vision_click_verified(
                                action_name="REPLY_SUBMIT",
                                click_description=self.VISION_DESCRIPTIONS["reply_submit"],
                                verify_description=None,
                                max_retries=3,
                                min_confidence=0.5,
                            )
                            if reply_ok:
                                verified = await self._verify_action_with_vision(
                                    "REPLY",
                                    self.VISION_DESCRIPTIONS["reply_verify"],
                                    timeout=40.0,
                                )
                                if not verified:
                                    logger.warning("[VISION] REPLY verification uncertain after vision submit; proceeding to avoid duplicate replies")
                        else:
                            logger.warning(f"[REPLY] Vision type failed: {type_res.error}")
                            results["errors"].append(f"vision_type_failed: {type_res.error}")

                results['reply'] = bool(reply_ok)
                results['reply_text'] = reply_text_raw
                if reply_text_to_post != reply_text_raw:
                    results['reply_text_posted'] = reply_text_to_post
                self.stats['replies'] += 1 if results['reply'] else 0
            logger.info(f"  [REPLY] {'OK' if results['reply'] else 'FAIL'}")

        semantic_actual = self._compute_semantic_state(
            used_intelligent_reply=used_intelligent,
            has_studio_history=bool(context_flags.get("has_studio_history")),
            has_chat_history=bool(context_flags.get("has_chat_history")),
            like_ok=bool(results.get("like")),
            heart_ok=bool(results.get("heart")),
            reply_ok=bool(results.get("reply")),
        )
        if semantic_actual:
            results["semantic_state"] = semantic_actual["code"]
            results["semantic_state_emoji"] = semantic_actual["emoji"]
            results["semantic_state_name"] = semantic_actual["name"]
            results["semantic_state_reason"] = semantic_actual.get("reason")
            results["semantic_state_digits"] = semantic_actual.get("digits")
            results["semantic_context_level"] = semantic_actual.get("context_level")
        
        self.stats['comments_processed'] += 1

        if COMMENTER_HISTORY_AVAILABLE:
            try:
                store = get_commenter_history_store()
                store.record_interaction(
                    commenter_handle=(comment_data.get("author_handle") or comment_data.get("author_name")),
                    commenter_channel_id=comment_data.get("channel_id"),
                    comment_text=comment_data.get("text", ""),
                    reply_text=(actual_reply_text if results.get("reply") else None),
                    liked=bool(results.get("like")),
                    hearted=bool(results.get("heart")),
                    replied=bool(results.get("reply")),
                    commenter_type=str(results.get("commenter_type") or "unknown"),
                )
            except Exception as e:
                logger.debug(f"[DAE] Failed to record commenter history: {e}")

        return results

