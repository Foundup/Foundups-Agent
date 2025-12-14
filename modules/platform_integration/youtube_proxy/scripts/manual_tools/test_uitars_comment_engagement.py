"""
0102 Autonomous Comment Engagement - UI-TARS + Selenium Hybrid
=============================================================

FLOW PER COMMENT:
1. Read comment text (yt-formatted-string#content-text)
2. Classify commenter (MOD/TROLL/SUBSCRIBER/REGULAR)
3. LIKE (click thumbs up)
4. HEART (click heart)
5. REPLY (intelligent reply based on classification)
   - Click reply button to open textarea
   - Type in textarea#textarea
   - Click submit button
6. REFRESH page (removes replied comment)
7. Repeat for next comment

ARCHITECTURE:
- UI-TARS Vision: Verification of visual state changes
- Selenium DOM: Reliable clicking and text extraction
- Intelligent Reply: BanterEngine + Whack-a-MAGA mockery

WSP Compliance: WSP 77 (AI Overseer), WSP 96 (WRE Skills), WSP 27 (DAE Architecture)
"""
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)


import asyncio
import os
import sys
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add repo root to path
repo_root = REPO_ROOT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
CHROME_PORT = int(os.getenv("FOUNDUPS_CHROME_PORT", "9222"))
TARS_API_URL = os.getenv("TARS_API_URL", "http://127.0.0.1:1234")
CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"  # Move2Japan

# Import intelligent reply generator
try:
    from modules.communication.video_comments.src.intelligent_reply_generator import (
        get_reply_generator, generate_intelligent_reply, CommenterType
    )
    INTELLIGENT_REPLIES_AVAILABLE = True
    logger.info("[INIT] Intelligent reply generator loaded")
except ImportError as e:
    INTELLIGENT_REPLIES_AVAILABLE = False
    logger.warning(f"[INIT] Intelligent replies not available: {e}")

# Telemetry
TELEMETRY_DIR = repo_root / "telemetry" / "feedback" / "comment_engagement"
TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)


class CommentEngagementDAE:
    """
    Autonomous YouTube Comment Engagement DAE
    
    Combines:
    - LM Studio + UI-TARS for vision understanding
    - Selenium for reliable DOM interaction
    - Pattern Memory for learning
    
    Actions:
    1. LIKE (thumbs up) - ytcp-icon-button[aria-label='Like']
    2. HEART (love) - ytcp-icon-button[aria-label='Heart']
    3. REPLY - button[aria-label='Reply'] + text input + submit
    """
    
    # DOM Selectors (verified working in YouTube Studio)
    SELECTORS = {
        'comment_thread': 'ytcp-comment-thread',
        'like': "ytcp-icon-button[aria-label='Like']",
        'heart': "ytcp-icon-button[aria-label='Heart']",
        'reply_btn': "#reply-button-end button, ytcp-button#reply-button button",
        'reply_input': "textarea#textarea, textarea[placeholder*='reply']",
        'reply_submit': "#submit-button button, ytcp-button#submit-button button",
    }
    
    # Vision descriptions for UI-TARS (when DOM fails)
    VISION_DESCRIPTIONS = {
        'like': 'gray thumbs up icon in the comment action bar',
        'heart': 'gray outlined heart icon next to thumbs down',
        'reply': 'Reply text button at the start of comment action bar',
    }

    def __init__(self, use_vision: bool = True, use_dom: bool = True):
        """
        Initialize engagement DAE.
        
        Args:
            use_vision: Enable UI-TARS vision for verification/fallback
            use_dom: Enable Selenium DOM clicking (recommended)
        """
        self.use_vision = use_vision
        self.use_dom = use_dom
        self.driver = None
        self.ui_tars_bridge = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.stats = {
            'comments_processed': 0,
            'likes': 0,
            'hearts': 0,
            'replies': 0,
            'errors': 0,
        }
    
    async def connect(self):
        """Connect to browser and vision system."""
        logger.info(f"[CONNECT] Initializing DAE (vision={self.use_vision}, dom={self.use_dom})")
        
        # Connect to existing Chrome via debugging port
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info(f"[CONNECT] Browser connected: {self.driver.current_url[:60]}...")
        except Exception as e:
            logger.error(f"[CONNECT] Browser connection failed: {e}")
            raise
        
        # Initialize UI-TARS Bridge if enabled
        if self.use_vision:
            try:
                from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge
                self.ui_tars_bridge = UITarsBridge(browser_port=CHROME_PORT)
                await self.ui_tars_bridge.connect()
                logger.info(f"[CONNECT] UI-TARS Vision ready (LM Studio: {TARS_API_URL})")
            except Exception as e:
                logger.warning(f"[CONNECT] UI-TARS unavailable: {e}")
                self.use_vision = False
        
        return True
    
    async def navigate_to_inbox(self):
        """Navigate to YouTube Studio comments inbox."""
        inbox_url = f"https://studio.youtube.com/channel/{CHANNEL_ID}/comments/inbox"
        logger.info(f"[NAV] Navigating to: {inbox_url}")
        self.driver.get(inbox_url)
        await asyncio.sleep(5)  # Wait for React app to load
        logger.info(f"[NAV] Arrived at comments inbox")
    
    def get_comment_count(self) -> int:
        """Count visible comments on page."""
        count = self.driver.execute_script(f"""
            return document.querySelectorAll('{self.SELECTORS["comment_thread"]}').length;
        """)
        return count or 0
    
    def extract_comment_data(self, comment_idx: int) -> Dict[str, Any]:
        """
        Extract comment text and author info from DOM.
        
        Reads from: yt-formatted-string#content-text
        """
        try:
            data = self.driver.execute_script("""
                const threads = document.querySelectorAll('ytcp-comment-thread');
                const thread = threads[arguments[0]];
                if (!thread) return null;
                
                // Extract comment text from yt-formatted-string#content-text
                let text = '';
                const contentText = thread.querySelector('yt-formatted-string#content-text');
                if (contentText) {
                    text = contentText.textContent.trim();
                } else {
                    const contentEl = thread.querySelector('#content, .comment-text');
                    text = contentEl ? contentEl.textContent.trim() : '';
                }
                
                // Extract author name
                let authorName = 'Unknown';
                const authorEl = thread.querySelector('#author-text, .author-name, a[href*="channel"]');
                if (authorEl) {
                    authorName = authorEl.textContent.trim().replace('@', '').replace(/\\s+/g, ' ');
                }
                
                // Check for mod/subscriber badges
                const modBadge = thread.querySelector('.mod-badge, [aria-label*="Moderator"]');
                const isMod = !!modBadge;
                const subBadge = thread.querySelector('.subscriber-badge, [aria-label*="Member"]');
                const isSubscriber = !!subBadge;
                
                return {
                    text: text.substring(0, 500),
                    author_name: authorName,
                    is_mod: isMod,
                    is_subscriber: isSubscriber
                };
            """, comment_idx)
            
            if data:
                logger.info(f"[EXTRACT] Comment: '{data.get('text', '')[:60]}...' by {data.get('author_name')}")
            
            return data or {'text': '', 'author_name': 'Unknown', 'is_mod': False, 'is_subscriber': False}
            
        except Exception as e:
            logger.warning(f"[EXTRACT] Failed: {e}")
            return {'text': '', 'author_name': 'Unknown', 'is_mod': False, 'is_subscriber': False}
    
    def generate_reply(self, comment_data: Dict[str, Any]) -> str:
        """Generate intelligent reply based on commenter context."""
        if INTELLIGENT_REPLIES_AVAILABLE:
            try:
                generator = get_reply_generator()
                reply = generator.generate_reply_for_comment(comment_data)
                
                # Get classification for logging
                profile = generator.classify_commenter(
                    author_name=comment_data.get('author_name', ''),
                    comment_text=comment_data.get('text', ''),
                    is_mod=comment_data.get('is_mod', False),
                    is_subscriber=comment_data.get('is_subscriber', False)
                )
                logger.info(f"[REPLY-GEN] {profile.commenter_type.value} -> '{reply[:50]}...'")
                return reply
            except Exception as e:
                logger.warning(f"[REPLY-GEN] Failed: {e}")
        
        return "Thanks for the comment! 🎌"
    
    async def click_element_dom(self, comment_idx: int, element_type: str) -> bool:
        """
        Click element using DOM selector (most reliable).
        
        Args:
            comment_idx: 1-based comment index (1 = first comment)
            element_type: 'like', 'heart', 'reply_btn', 'reply_submit'
        
        Returns:
            True if clicked successfully
        """
        # Use array indexing instead of nth-child (more reliable)
        element_selector = self.SELECTORS[element_type]
        
        result = self.driver.execute_script(f"""
            const threads = document.querySelectorAll('{self.SELECTORS["comment_thread"]}');
            const thread = threads[arguments[0]];  // 0-based index
            if (!thread) return {{success: false, error: 'Comment thread not found'}};
            
            const el = thread.querySelector(arguments[1]);
            if (!el) return {{success: false, error: 'Element not found in thread'}};
            
            thread.scrollIntoView({{behavior: 'smooth', block: 'center'}});
            el.click();
            return {{success: true}};
        """, comment_idx - 1, element_selector)  # Convert to 0-based
        
        return result.get('success', False) if result else False
    
    async def click_element_vision(self, description: str) -> Dict[str, Any]:
        """
        Click element using UI-TARS vision (fallback).
        
        Args:
            description: Human-readable description of element
        
        Returns:
            Dict with success, confidence, coordinates
        """
        if not self.ui_tars_bridge:
            return {'success': False, 'error': 'Vision not available'}
        
        try:
            result = await self.ui_tars_bridge.click(description, driver=self.driver)
            return {
                'success': result.success,
                'confidence': result.confidence,
                'coordinates': result.metadata.get('coordinates'),
                'error': result.error,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def verify_with_vision(self, description: str) -> Dict[str, Any]:
        """
        Verify element state using UI-TARS vision.
        
        Args:
            description: What to look for (e.g., "filled blue thumbs up")
        
        Returns:
            Dict with success, confidence
        """
        if not self.ui_tars_bridge:
            return {'success': True, 'confidence': 0.5, 'note': 'Vision unavailable, assuming success'}
        
        try:
            result = await self.ui_tars_bridge.verify(description, driver=self.driver)
            return {
                'success': result.success,
                'confidence': result.confidence,
            }
        except Exception as e:
            return {'success': False, 'confidence': 0, 'error': str(e)}
    
    async def engage_comment(
        self, 
        comment_idx: int, 
        reply_text: str = "",
        use_intelligent_reply: bool = True
    ) -> Dict[str, Any]:
        """
        Engage with a single comment: Like + Heart + Reply.
        
        Flow:
        1. Extract comment text (yt-formatted-string#content-text)
        2. Classify commenter and generate intelligent reply
        3. LIKE (click thumbs up)
        4. HEART (click heart)
        5. REPLY (click reply -> type -> submit)
        
        Args:
            comment_idx: 1-based comment index (always 1 for per-comment refresh)
            reply_text: Custom reply (overrides intelligent reply if provided)
            use_intelligent_reply: Generate intelligent reply based on context
        
        Returns:
            Dict with results for each action
        """
        results = {
            'comment_idx': comment_idx,
            'like': False,
            'heart': False,
            'reply': False,
            'author_name': 'Unknown',
            'comment_text': '',
            'commenter_type': 'unknown',
            'reply_text': '',
            'errors': [],
        }
        
        # 0. EXTRACT comment data
        comment_data = self.extract_comment_data(comment_idx - 1)  # 0-based
        results['author_name'] = comment_data.get('author_name', 'Unknown')
        results['comment_text'] = comment_data.get('text', '')[:100]
        
        logger.info(f"[ENGAGE] Processing comment {comment_idx} from {results['author_name']}...")
        
        # Generate intelligent reply if not provided
        actual_reply_text = reply_text
        if not actual_reply_text and use_intelligent_reply:
            actual_reply_text = self.generate_reply(comment_data)
            if INTELLIGENT_REPLIES_AVAILABLE:
                try:
                    generator = get_reply_generator()
                    profile = generator.classify_commenter(
                        author_name=comment_data.get('author_name', ''),
                        comment_text=comment_data.get('text', ''),
                        is_mod=comment_data.get('is_mod', False),
                        is_subscriber=comment_data.get('is_subscriber', False)
                    )
                    results['commenter_type'] = profile.commenter_type.value
                except:
                    pass
        
        results['reply_text'] = actual_reply_text
        
        # 1. LIKE (thumbs up)
        logger.info(f"  [LIKE] Clicking Like button...")
        if self.use_dom:
            like_ok = await self.click_element_dom(comment_idx, 'like')
        else:
            like_result = await self.click_element_vision(self.VISION_DESCRIPTIONS['like'])
            like_ok = like_result.get('success', False)
        
        if like_ok:
            await asyncio.sleep(1)
            # Verify with vision if available
            if self.use_vision:
                verify = await self.verify_with_vision("filled or highlighted thumbs up button")
                results['like'] = verify.get('confidence', 0) >= 0.5
                logger.info(f"  [LIKE] {'✓' if results['like'] else '✗'} (confidence: {verify.get('confidence', 0):.2f})")
            else:
                results['like'] = True
                logger.info(f"  [LIKE] ✓ (DOM click)")
            self.stats['likes'] += 1 if results['like'] else 0
        else:
            results['errors'].append('Like button not found')
            logger.warning(f"  [LIKE] ✗ Failed")
        
        await asyncio.sleep(1)
        
        # 2. HEART (love)
        logger.info(f"  [HEART] Clicking Heart button...")
        if self.use_dom:
            heart_ok = await self.click_element_dom(comment_idx, 'heart')
        else:
            heart_result = await self.click_element_vision(self.VISION_DESCRIPTIONS['heart'])
            heart_ok = heart_result.get('success', False)
        
        if heart_ok:
            await asyncio.sleep(1)
            if self.use_vision:
                verify = await self.verify_with_vision("filled red heart icon")
                results['heart'] = verify.get('confidence', 0) >= 0.5
                logger.info(f"  [HEART] {'✓' if results['heart'] else '✗'} (confidence: {verify.get('confidence', 0):.2f})")
            else:
                results['heart'] = True
                logger.info(f"  [HEART] ✓ (DOM click)")
            self.stats['hearts'] += 1 if results['heart'] else 0
        else:
            results['errors'].append('Heart button not found')
            logger.warning(f"  [HEART] ✗ Failed")
        
        await asyncio.sleep(1)
        
        # 3. REPLY (always if intelligent replies enabled or custom text provided)
        if actual_reply_text:
            logger.info(f"  [REPLY] Opening reply box...")
            
            # Click the Reply button to open the reply box
            reply_open = self.driver.execute_script("""
                const threads = document.querySelectorAll(arguments[0]);
                const thread = threads[arguments[1]];
                if (!thread) return {success: false, error: 'Thread not found'};
                
                // Find Reply button - try multiple selectors
                let replyBtn = thread.querySelector('#reply-button-end button');
                if (!replyBtn) replyBtn = thread.querySelector('ytcp-button#reply-button button');
                if (!replyBtn) replyBtn = thread.querySelector('button[aria-label="Reply"]');
                if (!replyBtn) {
                    // Try finding by text content
                    const buttons = thread.querySelectorAll('button');
                    for (const btn of buttons) {
                        if (btn.textContent.trim() === 'Reply') {
                            replyBtn = btn;
                            break;
                        }
                    }
                }
                
                if (!replyBtn) return {success: false, error: 'Reply button not found'};
                
                replyBtn.click();
                return {success: true};
            """, self.SELECTORS["comment_thread"], comment_idx - 1)
            
            if reply_open and reply_open.get('success'):
                await asyncio.sleep(2)  # Wait for reply box to open
                
                # Type into the textarea
                type_result = self.driver.execute_script("""
                    const threads = document.querySelectorAll(arguments[0]);
                    const thread = threads[arguments[1]];
                    if (!thread) return {success: false, error: 'Thread not found'};
                    
                    // Find textarea - try multiple selectors
                    let textarea = thread.querySelector('textarea#textarea');
                    if (!textarea) textarea = thread.querySelector('textarea[placeholder*="reply"]');
                    if (!textarea) textarea = thread.querySelector('textarea');
                    if (!textarea) textarea = document.querySelector('ytcp-comment-creator textarea');
                    
                    if (!textarea) return {success: false, error: 'Textarea not found'};
                    
                    textarea.click();
                    textarea.focus();
                    textarea.value = arguments[2];
                    
                    // Trigger input event to enable submit button
                    textarea.dispatchEvent(new Event('input', {bubbles: true}));
                    
                    return {success: true};
                """, self.SELECTORS["comment_thread"], comment_idx - 1, actual_reply_text)
                
                if type_result and type_result.get('success'):
                    logger.info(f"  [REPLY] Typed: '{actual_reply_text[:50]}...'")
                    await asyncio.sleep(1)
                    
                    # Click submit button
                    submit_ok = self.driver.execute_script("""
                        const threads = document.querySelectorAll(arguments[0]);
                        const thread = threads[arguments[1]];
                        if (!thread) return false;
                        
                        // Find submit button - try multiple selectors
                        let submitBtn = thread.querySelector('#submit-button button');
                        if (!submitBtn) submitBtn = thread.querySelector('ytcp-button#submit-button button');
                        if (!submitBtn) submitBtn = document.querySelector('ytcp-comment-creator #submit-button button');
                        
                        if (submitBtn && !submitBtn.disabled) {
                            submitBtn.click();
                            return true;
                        }
                        return false;
                    """, self.SELECTORS["comment_thread"], comment_idx - 1)
                    
                    results['reply'] = bool(submit_ok)
                    logger.info(f"  [REPLY] {'✓' if results['reply'] else '✗'} Posted")
                    self.stats['replies'] += 1 if results['reply'] else 0
                else:
                    error_msg = type_result.get('error', 'Unknown') if type_result else 'No result'
                    results['errors'].append(f'Could not type reply: {error_msg}')
                    logger.warning(f"  [REPLY] ✗ Typing failed: {error_msg}")
            else:
                error_msg = reply_open.get('error', 'Unknown') if reply_open else 'No result'
                results['errors'].append(f'Reply button not found: {error_msg}')
                logger.warning(f"  [REPLY] ✗ Could not open reply box: {error_msg}")
        
        self.stats['comments_processed'] += 1
        return results
    
    async def engage_all_comments(
        self,
        max_comments: int = 10,
        reply_text: str = "",
        refresh_between: bool = True,
        use_intelligent_reply: bool = True
    ) -> Dict[str, Any]:
        """
        Engage with all visible comments - ONE AT A TIME with refresh after each.
        
        Flow per comment:
        1. Read comment text (yt-formatted-string#content-text)
        2. LIKE (click thumbs up)
        3. HEART (click heart)
        4. REPLY (intelligent reply based on commenter type)
        5. REFRESH (removes replied comment, shows next)
        6. Repeat
        
        Args:
            max_comments: Max comments to process total
            reply_text: Custom reply (overrides intelligent if provided)
            refresh_between: Refresh page after each comment
            use_intelligent_reply: Generate intelligent replies based on context
        
        Returns:
            Summary of engagement session
        """
        mode = "Intelligent" if use_intelligent_reply else "Custom"
        logger.info(f"\n{'='*60}")
        logger.info(f" 0102 AUTONOMOUS COMMENT ENGAGEMENT")
        logger.info(f" Session: {self.session_id}")
        logger.info(f" Max comments: {max_comments}")
        logger.info(f" Reply mode: {mode}")
        logger.info(f" Flow: LIKE -> HEART -> REPLY -> REFRESH (per comment)")
        logger.info(f"{'='*60}\n")
        
        all_results = []
        total_processed = 0
        
        # Loop until NO comments remain OR max reached (max_comments=0 means unlimited)
        while True:
            # Get current comment count
            comment_count = self.get_comment_count()
            
            if comment_count == 0:
                logger.info("[ENGAGE] ✅ ALL COMMENTS PROCESSED! Community tab clear!")
                self.stats['all_processed'] = True
                break
            
            # Check max limit (0 = unlimited)
            if max_comments > 0 and total_processed >= max_comments:
                logger.info(f"[ENGAGE] Reached max limit ({max_comments}), {comment_count} comments remaining")
                self.stats['all_processed'] = False
                break
            
            # Always process the FIRST visible comment (index 1)
            # After reply + refresh, the next comment becomes first
            max_label = "∞" if max_comments == 0 else str(max_comments)
            logger.info(f"\n[ENGAGE] === Comment {total_processed + 1}/{max_label} ===")
            
            result = await self.engage_comment(
                1,  # Always first comment
                reply_text,
                use_intelligent_reply=use_intelligent_reply
            )
            all_results.append(result)
            total_processed += 1
            
            # Log result
            status = "✅" if result.get('reply') else "⚠️"
            logger.info(f"[ENGAGE] {status} {result.get('author_name')} ({result.get('commenter_type')})")
            if result.get('reply_text'):
                logger.info(f"[ENGAGE]    Reply: '{result.get('reply_text')[:50]}...'")
            
            # Refresh after EACH comment to remove it and show next
            # Always refresh unless max_comments reached (and max > 0)
            should_refresh = refresh_between and (max_comments == 0 or total_processed < max_comments)
            if should_refresh:
                logger.info("[REFRESH] Refreshing to load next comment...")
                self.driver.refresh()
                await asyncio.sleep(5)
        
        # Final summary
        summary = {
            'session_id': self.session_id,
            'total_processed': total_processed,
            'stats': self.stats,
            'results': all_results,
        }
        
        # Save telemetry
        telemetry_file = TELEMETRY_DIR / f"session_{self.session_id}.json"
        with open(telemetry_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"\n{'='*60}")
        logger.info(f" SESSION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f" Comments processed: {self.stats['comments_processed']}")
        logger.info(f" Likes: {self.stats['likes']}")
        logger.info(f" Hearts: {self.stats['hearts']}")
        logger.info(f" Replies: {self.stats['replies']}")
        logger.info(f" Errors: {self.stats['errors']}")
        all_done = self.stats.get('all_processed', False)
        logger.info(f" All processed: {'✅ YES' if all_done else '⚠️ NO (more remaining)'}")
        logger.info(f" Telemetry: {telemetry_file}")
        logger.info(f"{'='*60}\n")
        
        return summary
    
    def close(self):
        """Clean up resources."""
        if self.ui_tars_bridge:
            self.ui_tars_bridge.close()
        # Don't close Selenium driver (we're attached to existing Chrome)
        logger.info("[CLOSE] DAE resources released")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="0102 Autonomous Comment Engagement")
    parser.add_argument("--max-comments", type=int, default=0, help="Max comments to process (0 = unlimited, clear all)")
    parser.add_argument("--reply-text", type=str, default="", help="Custom reply (overrides intelligent)")
    parser.add_argument("--vision-only", action="store_true", help="Use vision for all clicks (no DOM)")
    parser.add_argument("--dom-only", action="store_true", help="Use DOM only (no vision verification)")
    parser.add_argument("--no-refresh", action="store_true", help="Don't refresh page between comments")
    parser.add_argument("--no-intelligent-reply", action="store_true", help="Disable intelligent replies")
    parser.add_argument("--json-output", action="store_true", help="Output JSON result for subprocess parsing")
    args = parser.parse_args()
    
    # Configure mode
    use_vision = not args.dom_only
    use_dom = not args.vision_only
    use_intelligent_reply = not args.no_intelligent_reply
    
    dae = CommentEngagementDAE(use_vision=use_vision, use_dom=use_dom)
    
    try:
        await dae.connect()
        await dae.navigate_to_inbox()
        
        summary = await dae.engage_all_comments(
            max_comments=args.max_comments,
            reply_text=args.reply_text,
            refresh_between=not args.no_refresh,
            use_intelligent_reply=use_intelligent_reply,
        )
        
        # Output JSON for subprocess parsing if requested
        if args.json_output:
            import json
            print(json.dumps(summary, default=str))
        
        return summary
        
    except Exception as e:
        logger.error(f"[ERROR] Engagement failed: {e}", exc_info=True)
        error_result = {'error': str(e), 'stats': {'comments_processed': 0, 'errors': 1}}
        if args.json_output:
            import json
            print(json.dumps(error_result, default=str))
        return error_result
    
    finally:
        dae.close()


if __name__ == "__main__":
    asyncio.run(main())

