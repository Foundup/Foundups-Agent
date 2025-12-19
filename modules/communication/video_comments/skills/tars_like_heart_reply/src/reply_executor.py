"""
Browser Reply Executor - Extracted from comment_engagement_dae.py

WSP 62 Refactoring: Reduces comment_engagement_dae.py from 2064 to ~1400 lines
Extracted reply execution logic (~600 lines total).

Pattern: Dependency injection (driver, human, selectors passed to constructor)
"""

import asyncio
import logging
import os
import random
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Anti-detection: Human behavior simulation availability
try:
    from modules.infrastructure.foundups_selenium.src.human_behavior import get_human_behavior
    HUMAN_BEHAVIOR_AVAILABLE = True
except ImportError:
    HUMAN_BEHAVIOR_AVAILABLE = False


class BrowserReplyExecutor:
    """
    Handles all reply execution for YouTube Studio comments.
    
    Responsibilities:
    - Execute replies to top-level comments
    - Execute replies to nested comments  
    - Process all nested replies in a thread
    - Anti-detection: Human-like typing with typos
    """
    
    def __init__(self, driver, human, selectors):
        """
        Args:
            driver: Selenium WebDriver instance
            human: HumanBehavior instance (or None)
            selectors: Dict of DOM selectors
        """
        self.driver = driver
        self.human = human
        self.selectors = selectors

    async def process_nested_replies(
        self,
        parent_thread_idx: int,
        do_like: bool,
        do_heart: bool,
        use_intelligent_reply: bool
    ) -> List[Dict[str, Any]]:
        """
        Process nested replies within a comment thread.

        Addresses user's challenges:
        1. Skips if Move2Japan already replied (DOM detection)
        2. Uses relative selectors (no absolute positions)
        3. No expansion needed (Studio shows all replies)

        Args:
            parent_thread_idx: Index of parent thread (1-based)
            do_like: Whether to like replies
            do_heart: Whether to heart replies
            use_intelligent_reply: Whether to generate intelligent replies

        Returns:
            List of engagement results for each reply
        """
        # Check if nested reply engagement is enabled
        engage_nested = os.getenv("YT_ENGAGE_NESTED_REPLIES", "false").lower() in ("1", "true", "yes")
        if not engage_nested:
            return []

        max_nested = int(os.getenv("YT_MAX_NESTED_REPLIES", "5"))
        logger.info(f"[NESTED] Checking thread {parent_thread_idx} for nested replies (max: {max_nested})")

        results = []

        try:
            # Query nested replies using relative selectors (position-independent)
            nested_data = self.driver.execute_script("""
                const threadIdx = arguments[0];
                const threads = document.querySelectorAll('ytcp-comment-thread');
                const thread = threads[threadIdx];
                if (!thread) return {has_replies: false, error: 'Thread not found'};

                // Check for nested reply container
                const repliesContainer = thread.querySelector('ytcp-comment-replies');
                if (!repliesContainer) return {has_replies: false};

                // Check if Move2Japan already replied (skip if so)
                const channelBadge = repliesContainer.querySelector(
                    'ytcp-comment-author[aria-label*="Move2Japan"], ' +
                    '[class*="creator-badge"], ' +
                    '[aria-label*="owner"]'
                );
                if (channelBadge) {
                    return {
                        has_replies: true,
                        channel_already_replied: true,
                        author: channelBadge.textContent.trim()
                    };
                }

                // Get all nested reply elements (relative to thread, not absolute positions!)
                const replyElements = repliesContainer.querySelectorAll(
                    'ytcp-comment-replies[class*="expanded"]'
                );

                // Extract reply data
                const replies = [];
                replyElements.forEach((replyEl, idx) => {
                    const authorEl = replyEl.querySelector('ytcp-comment-author');
                    const contentEl = replyEl.querySelector('[id*="content-text"]');

                    replies.push({
                        index: idx,
                        author: authorEl ? authorEl.textContent.trim() : 'Unknown',
                        text: contentEl ? contentEl.textContent.trim() : '',
                        has_like_btn: !!replyEl.querySelector('ytcp-icon-button[aria-label*="Like"]'),
                        has_heart_btn: !!replyEl.querySelector('ytcp-comment-creator-heart'),
                        has_reply_btn: !!replyEl.querySelector('[id*="reply-button"]')
                    });
                });

                return {
                    has_replies: replies.length > 0,
                    channel_already_replied: false,
                    reply_count: replies.length,
                    replies: replies
                };
            """, parent_thread_idx - 1)

            if not nested_data or not nested_data.get('has_replies'):
                logger.info(f"[NESTED] No nested replies in thread {parent_thread_idx}")
                return []

            if nested_data.get('channel_already_replied'):
                logger.info(f"[NESTED] Skipping thread {parent_thread_idx} - Move2Japan already replied")
                logger.info(f"[NESTED]   Author detected: {nested_data.get('author', 'Unknown')}")
                return []

            reply_count = nested_data.get('reply_count', 0)
            replies = nested_data.get('replies', [])

            logger.info(f"[NESTED] Found {reply_count} nested replies (will process up to {max_nested})")

            # Process each nested reply (limit to max_nested)
            for reply_data in replies[:max_nested]:
                reply_idx = reply_data['index']
                author = reply_data['author']
                text_preview = reply_data['text'][:50] + '...' if len(reply_data['text']) > 50 else reply_data['text']

                logger.info(f"[NESTED] Processing reply {reply_idx + 1}/{min(reply_count, max_nested)}")
                logger.info(f"[NESTED]   Author: {author}")
                logger.info(f"[NESTED]   Preview: {text_preview}")

                reply_result = {
                    'author_name': author,
                    'text': reply_data['text'],
                    'like': False,
                    'heart': False,
                    'reply': False,
                    'nested': True  # Mark as nested reply
                }

                # Like nested reply (relative selector within thread!)
                if do_like and reply_data['has_like_btn']:
                    like_success = self.driver.execute_script("""
                        const threadIdx = arguments[0];
                        const replyIdx = arguments[1];
                        const threads = document.querySelectorAll('ytcp-comment-thread');
                        const thread = threads[threadIdx];
                        if (!thread) return false;

                        const repliesContainer = thread.querySelector('ytcp-comment-replies');
                        if (!repliesContainer) return false;

                        const replyElements = repliesContainer.querySelectorAll(
                            'ytcp-comment-replies[class*="expanded"]'
                        );
                        const reply = replyElements[replyIdx];
                        if (!reply) return false;

                        const likeBtn = reply.querySelector('ytcp-icon-button[aria-label*="Like"]');
                        if (!likeBtn) return false;

                        likeBtn.click();
                        return true;
                    """, parent_thread_idx - 1, reply_idx)

                    reply_result['like'] = bool(like_success)
                    if like_success:
                        logger.info(f"[NESTED] ✅ Liked reply from {author}")
                        await asyncio.sleep(self.human.human_delay(0.8, 0.3) if self.human else 0.8)

                # Heart nested reply (same relative selector pattern)
                if do_heart and reply_data['has_heart_btn']:
                    heart_success = self.driver.execute_script("""
                        const threadIdx = arguments[0];
                        const replyIdx = arguments[1];
                        const threads = document.querySelectorAll('ytcp-comment-thread');
                        const thread = threads[threadIdx];
                        if (!thread) return false;

                        const repliesContainer = thread.querySelector('ytcp-comment-replies');
                        if (!repliesContainer) return false;

                        const replyElements = repliesContainer.querySelectorAll(
                            'ytcp-comment-replies[class*="expanded"]'
                        );
                        const reply = replyElements[replyIdx];
                        if (!reply) return false;

                        const heartBtn = reply.querySelector('ytcp-comment-creator-heart');
                        if (!heartBtn) return false;

                        heartBtn.click();
                        return true;
                    """, parent_thread_idx - 1, reply_idx)

                    reply_result['heart'] = bool(heart_success)
                    if heart_success:
                        logger.info(f"[NESTED] ❤️ Hearted reply from {author}")
                        await asyncio.sleep(self.human.human_delay(0.8, 0.3) if self.human else 0.8)

                # Reply to nested reply (if intelligent replies enabled)
                if use_intelligent_reply and reply_data['has_reply_btn']:
                    # Generate intelligent reply for nested conversation
                    try:
                        from .intelligent_reply_generator import generate_intelligent_reply
                        intelligent_reply = await generate_intelligent_reply(
                            comment_text=reply_data['text'],
                            author_name=author,
                            context={'is_nested_reply': True, 'parent_thread': parent_thread_idx}
                        )

                        if intelligent_reply:
                            # Open reply box and type (uses same logic as parent comments)
                            reply_posted = await self._execute_nested_reply(
                                parent_thread_idx,
                                reply_idx,
                                intelligent_reply
                            )
                            reply_result['reply'] = reply_posted
                            reply_result['reply_text'] = intelligent_reply if reply_posted else None

                            if reply_posted:
                                logger.info(f"[NESTED] 💬 Replied to {author}: {intelligent_reply[:50]}...")
                    except Exception as e:
                        logger.warning(f"[NESTED] Reply generation failed: {e}")

                results.append(reply_result)

            logger.info(f"[NESTED] Processed {len(results)} nested replies in thread {parent_thread_idx}")

        except Exception as e:
            logger.error(f"[NESTED] Error processing nested replies: {e}", exc_info=True)

        return results

    async def execute_nested_reply(self, parent_thread_idx: int, reply_idx: int, reply_text: str) -> bool:
        """Execute reply to a nested reply (relative positioning)."""
        try:
            # Open reply box for nested reply
            opened = self.driver.execute_script("""
                const threadIdx = arguments[0];
                const replyIdx = arguments[1];
                const threads = document.querySelectorAll('ytcp-comment-thread');
                const thread = threads[threadIdx];
                if (!thread) return false;

                const repliesContainer = thread.querySelector('ytcp-comment-replies');
                if (!repliesContainer) return false;

                const replyElements = repliesContainer.querySelectorAll(
                    'ytcp-comment-replies[class*="expanded"]'
                );
                const reply = replyElements[replyIdx];
                if (!reply) return false;

                const replyBtn = reply.querySelector('[id*="reply-button"] button');
                if (!replyBtn) return false;

                replyBtn.click();
                return true;
            """, parent_thread_idx - 1, reply_idx)

            if not opened:
                return False

            await asyncio.sleep(self.human.human_delay(1.5, 0.6) if self.human else 1.5)

            # Type reply (same as parent comment logic)
            typed = self.driver.execute_script("""
                const threadIdx = arguments[0];
                const replyIdx = arguments[1];
                const text = arguments[2];
                const threads = document.querySelectorAll('ytcp-comment-thread');
                const thread = threads[threadIdx];
                if (!thread) return false;

                // Find the reply's textarea (it appears after clicking Reply button)
                const textarea = thread.querySelector('textarea[id*="textarea"]');
                if (!textarea) return false;

                textarea.value = text;
                textarea.dispatchEvent(new Event('input', {bubbles: true}));
                return true;
            """, parent_thread_idx - 1, reply_idx, reply_text)

            if not typed:
                return False

            await asyncio.sleep(self.human.human_delay(1.0, 0.4) if self.human else 1.0)

            # Submit reply
            submitted = self.driver.execute_script("""
                const threadIdx = arguments[0];
                const threads = document.querySelectorAll('ytcp-comment-thread');
                const thread = threads[threadIdx];
                if (!thread) return false;

                const submitBtn = thread.querySelector('[id*="submit-button"] button');
                if (!submitBtn) return false;

                submitBtn.click();
                return true;
            """, parent_thread_idx - 1)

            return bool(submitted)

        except Exception as e:
            logger.warning(f"[NESTED] Reply execution failed: {e}")
            return False

    async def execute_reply(self, comment_idx: int, reply_text: str) -> bool:
        """Execute reply flow: Open box -> Type -> Submit."""
        thread_selector = self.SELECTORS["comment_thread"]

        # Open reply box
        reply_open = self.driver.execute_script(
            """
            const threadSelector = arguments[0];
            const threadIndex = arguments[1];
            const threads = document.querySelectorAll(threadSelector);
            const thread = threads[threadIndex];
            if (!thread) return {success: false, error: 'Thread not found'};

            let replyBtn = thread.querySelector('#reply-button-end button');
            if (!replyBtn) replyBtn = thread.querySelector('ytcp-button#reply-button button');
            if (!replyBtn) replyBtn = thread.querySelector('button[aria-label=\"Reply\"]');
            if (!replyBtn) {
              const buttons = thread.querySelectorAll('button');
              for (const btn of buttons) {
                if ((btn.textContent || '').trim() === 'Reply') {
                  replyBtn = btn;
                  break;
                }
              }
            }

            if (!replyBtn) return {success: false, error: 'Reply button not found'};
            try { replyBtn.scrollIntoView({behavior: 'smooth', block: 'center'}); } catch (e) {}
            replyBtn.click();
            return {success: true};
            """,
            thread_selector,
            comment_idx - 1,
        )

        if not reply_open or not reply_open.get("success"):
            if reply_open and reply_open.get("error"):
                logger.warning(f"[REPLY] DOM open failed: {reply_open.get('error')}")
            return False

        # Human-like delay after opening reply box (randomized 0.6s-2.4s)
        if self.human:
            await asyncio.sleep(self.human.human_delay(1.5, 0.6))
        else:
            await asyncio.sleep(1.5)

        # Type into reply editor (textarea or contenteditable)
        # Anti-Detection (WSP 49): Human typing with character-by-character simulation
        # PRIMARY: Selenium human_type() (0.08s-0.28s per char, 5% typo rate)
        # FALLBACK: execute_script() instant insertion (Shadow DOM compatibility)
        typed_via_selenium = False

        if self.human and HUMAN_BEHAVIOR_AVAILABLE:
            try:
                from selenium.webdriver.common.by import By

                # Find thread via Selenium
                threads = self.driver.find_elements(By.CSS_SELECTOR, thread_selector)
                if comment_idx > len(threads):
                    raise ValueError(f"Thread {comment_idx} not found")

                thread = threads[comment_idx - 1]

                # Try multiple selectors to find the editor
                editor_selectors = [
                    "ytcp-comment-creator [contenteditable='true']",
                    "[contenteditable='true']",
                    "textarea#textarea",
                    "textarea",
                    "input[type='text']",
                ]

                editor = None
                for selector in editor_selectors:
                    try:
                        editor = thread.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue

                if not editor:
                    # Try global search as fallback
                    for selector in editor_selectors:
                        try:
                            editor = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except:
                            continue

                if editor:
                    # Human-like typing: character-by-character with typos (0102 like)
                    self.human.scroll_to_element(editor)
                    await asyncio.sleep(self.human.human_delay(0.2, 0.5))
                    editor.click()
                    await asyncio.sleep(self.human.human_delay(0.3, 0.5))

                    # Type text with human behavior (0.08s-0.28s per char, 5% typo rate)
                    self.human.human_type(editor, reply_text)

                    logger.info(f"[REPLY] Text typed via human_type() - ANTI-DETECTION ✓ (0102 like)")
                    typed_via_selenium = True
                else:
                    logger.warning(f"[REPLY] Selenium editor not found, falling back...")

            except Exception as selenium_error:
                logger.warning(f"[REPLY] Selenium typing failed: {selenium_error}, falling back...")

        # Fallback: JavaScript-based character-by-character typing (Shadow DOM compatible)
        # This is the "0102 like" approach - types each character with human delays
        if not typed_via_selenium:
            # Step 1: Find and prepare the editor
            prep_result = self.driver.execute_script(
                """
                const threadSelector = arguments[0];
                const threadIndex = arguments[1];
                const threads = document.querySelectorAll(threadSelector);
                const thread = threads[threadIndex];
                if (!thread) return {success: false, error: 'Thread not found'};

                const selectors = [
                  "ytcp-comment-creator [contenteditable='true']",
                  "[contenteditable='true']",
                  "textarea#textarea",
                  "textarea",
                  "input[type='text']",
                ];

                function findEditor() {
                  for (const sel of selectors) {
                    const local = thread.querySelector(sel);
                    if (local) return local;
                    const global = document.querySelector(sel);
                    if (global) return global;
                  }
                  return null;
                }

                const editor = findEditor();
                if (!editor) return {success: false, error: 'Reply editor not found'};

                // Prepare editor
                try { editor.scrollIntoView({behavior: 'smooth', block: 'center'}); } catch (e) {}
                try { editor.click(); } catch (e) {}
                try { editor.focus(); } catch (e) {}

                // Store editor reference globally for character-by-character typing
                window.__ytReplyEditor = editor;
                window.__ytReplyIsTextarea = (editor.tagName || '').toUpperCase() === 'TEXTAREA' ||
                                              (editor.tagName || '').toUpperCase() === 'INPUT';

                return {success: true, tag: editor.tagName, isTextarea: window.__ytReplyIsTextarea};
                """,
                thread_selector,
                comment_idx - 1,
            )

            if not prep_result or not prep_result.get("success"):
                logger.warning(f"[REPLY] Editor preparation failed: {prep_result.get('error') if prep_result else 'Unknown'}")
                return False

            logger.info(f"[REPLY] Editor found (tag={prep_result.get('tag')}), starting character-by-character typing (0102 like)...")

            # Step 2: Type character-by-character with human-like delays
            import random

            chars_typed = 0
            i = 0
            while i < len(reply_text):
                char = reply_text[i]

                # 5% chance of typo (like human_type())
                if random.random() < 0.05 and i > 0:
                    # Type wrong character
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz ')
                    self.driver.execute_script(
                        """
                        const editor = window.__ytReplyEditor;
                        const isTextarea = window.__ytReplyIsTextarea;
                        const char = arguments[0];

                        if (isTextarea) {
                          editor.value += char;
                          editor.dispatchEvent(new Event('input', {bubbles: true}));
                        } else {
                          const textNode = document.createTextNode(char);
                          editor.appendChild(textNode);
                          editor.dispatchEvent(new Event('input', {bubbles: true}));
                        }
                        """,
                        wrong_char
                    )

                    # Pause (realize mistake)
                    if self.human:
                        await asyncio.sleep(self.human.human_delay(0.15, 0.5))
                    else:
                        await asyncio.sleep(random.uniform(0.1, 0.3))

                    # Backspace
                    self.driver.execute_script(
                        """
                        const editor = window.__ytReplyEditor;
                        const isTextarea = window.__ytReplyIsTextarea;

                        if (isTextarea) {
                          editor.value = editor.value.slice(0, -1);
                          editor.dispatchEvent(new Event('input', {bubbles: true}));
                        } else {
                          if (editor.lastChild) editor.removeChild(editor.lastChild);
                          editor.dispatchEvent(new Event('input', {bubbles: true}));
                        }
                        """
                    )

                    # Small delay after correction
                    if self.human:
                        await asyncio.sleep(self.human.human_delay(0.1, 0.5))
                    else:
                        await asyncio.sleep(random.uniform(0.05, 0.15))

                # Type the correct character
                try:
                    self.driver.execute_script(
                        """
                        const editor = window.__ytReplyEditor;
                        const isTextarea = window.__ytReplyIsTextarea;
                        const char = arguments[0];

                        // Defensive check: editor might be cleared by YouTube SPA re-render
                        if (!editor) {
                            throw new Error('Editor reference lost - YouTube DOM may have re-rendered');
                        }

                        if (isTextarea) {
                          editor.value += char;
                          editor.dispatchEvent(new Event('input', {bubbles: true}));
                        } else {
                          const textNode = document.createTextNode(char);
                          editor.appendChild(textNode);
                          editor.dispatchEvent(new Event('input', {bubbles: true}));
                        }
                        """,
                        char
                    )
                except Exception as e:
                    logger.warning(f"[REPLY] Character typing failed at position {chars_typed}: {e}")
                    logger.warning("[REPLY] YouTube DOM may have changed - aborting reply")
                    return False

                chars_typed += 1

                # Human-like delay between characters (0.08s-0.28s base, with variance)
                if self.human:
                    char_delay = self.human.human_delay(0.08, 0.7)  # 70% variance: 0.024s-0.136s
                else:
                    char_delay = random.uniform(0.05, 0.20)

                # Longer pause after punctuation (like humans)
                if char in '.!?,;:\n':
                    char_delay *= random.uniform(1.5, 2.5)

                await asyncio.sleep(char_delay)
                i += 1

            # Cleanup global reference
            self.driver.execute_script(
                """
                delete window.__ytReplyEditor;
                delete window.__ytReplyIsTextarea;
                """
            )

            logger.info(f"[REPLY] Typed {chars_typed} characters with human delays - ANTI-DETECTION ✓ (0102 like)")

        # Human-like delay before submit (randomized 0.4s-1.2s)
        if self.human:
            await asyncio.sleep(self.human.human_delay(0.8, 0.5))
        else:
            await asyncio.sleep(0.8)

        # Submit
        submit_result = self.driver.execute_script(
            """
            const threadSelector = arguments[0];
            const threadIndex = arguments[1];
            const threads = document.querySelectorAll(threadSelector);
            const thread = threads[threadIndex];
            if (!thread) return {success: false, error: 'Thread not found'};

            let submitBtn =
              thread.querySelector('#submit-button button') ||
              thread.querySelector('ytcp-button#submit-button button') ||
              document.querySelector('ytcp-comment-creator #submit-button button');

            if (submitBtn && !submitBtn.disabled) {
              submitBtn.click();
              return {success: true};
            }
            return {success: false, error: 'Submit button not found/disabled'};
            """,
            thread_selector,
            comment_idx - 1,
        )

        if not submit_result or not submit_result.get("success"):
            if submit_result and submit_result.get("error"):
                logger.warning(f"[REPLY] DOM submit failed: {submit_result.get('error')}")
            return False

        return True
    
