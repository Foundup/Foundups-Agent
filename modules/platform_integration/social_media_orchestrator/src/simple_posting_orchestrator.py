#!/usr/bin/env python3
"""
Simple Social Media Posting Orchestrator
WSP Compliant: Separation of concerns - handles posting logic for all DAE modules

This orchestrator provides a clean interface for any module (YouTube, etc.)
to post to social media without handling browser automation directly.

Implements sequential posting to prevent browser conflicts.

NAVIGATION: Posts verified stream events to LinkedIn and X/Twitter.
-> Called by: modules/platform_integration/stream_resolver/src/stream_resolver.py::_trigger_social_media_post
-> Delegates to: LinkedInPoster, XPoster, content/content_orchestrator.py
-> Related: NAVIGATION.py -> MODULE_GRAPH["core_flows"]["stream_detection_flow"]
-> Quick ref: NAVIGATION.py -> NEED_TO["post to linkedin/twitter"]
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import threading

logger = logging.getLogger(__name__)
        self.request_counter = 0
        self.posted_streams = self._load_posted_history()
        self.posting_in_progress = set()  # Prevent concurrent posting of same stream

        # SINGLETON POSTER INSTANCES - Reuse same browser sessions
        self._linkedin_poster = None
        self._x_poster = None

        # Register cleanup on exit
        import atexit
        atexit.register(self._cleanup_browsers)

    def _cleanup_browsers(self):
        """Clean up browser instances on exit"""
        global _GLOBAL_LINKEDIN_POSTER, _GLOBAL_X_POSTER

        try:
            if _GLOBAL_LINKEDIN_POSTER and hasattr(_GLOBAL_LINKEDIN_POSTER, 'driver'):
                if _GLOBAL_LINKEDIN_POSTER.driver:
                    try:
                        _GLOBAL_LINKEDIN_POSTER.driver.quit()
                        self.logger.info("[CLEANUP] LinkedIn browser closed")
                    except:
                        pass  # Browser already closed
                _GLOBAL_LINKEDIN_POSTER = None

            if _GLOBAL_X_POSTER and hasattr(_GLOBAL_X_POSTER, 'driver'):
                if _GLOBAL_X_POSTER.driver:
                    try:
                        _GLOBAL_X_POSTER.driver.quit()
                        self.logger.info("[CLEANUP] X browser closed")
                    except:
                        pass  # Browser already closed
                _GLOBAL_X_POSTER = None
        except Exception as e:
            self.logger.debug(f"[CLEANUP] Error during cleanup: {e}")
    
    async def post_stream_notification(self, stream_title: str, stream_url: str,
                                     platforms: Optional[List[Platform]] = None) -> PostResponse:
        """
        Post stream notification to social media platforms.

        SIMPLIFIED: Trusts the caller's stream detection.
        - No redundant API verification (scraping already detected it)
        - Prevents duplicate posting via cache
        - Clear logging at every step
        """
        self.request_counter += 1
        request_id = f"stream_post_{self.request_counter}_{datetime.now().strftime('%H%M%S')}"

        if platforms is None:
            platforms = [Platform.LINKEDIN, Platform.X_TWITTER]

        # Extract video ID from URL for duplicate tracking
        import re
        video_id_match = re.search(r'[?&]v=([^&]+)', stream_url)
        video_id = video_id_match.group(1) if video_id_match else stream_url

        # CRITICAL: Check for duplicate posting FIRST
        logger.info("="*80)
        logger.info(f"[ORCHESTRATOR] 🎯 SOCIAL MEDIA POSTING REQUEST")
        logger.info(f"[ORCHESTRATOR] 📺 Stream: {stream_title}")
        logger.info(f"[ORCHESTRATOR] 🔗 URL: {stream_url}")
        logger.info(f"[ORCHESTRATOR] 🆔 Video ID: {video_id}")
        logger.info("="*80)

        # Check which platforms have already posted (per-platform duplicate prevention)
        platforms_to_post = []
        platforms_already_posted = []

        if video_id in self.posted_streams:
            posted_info = self.posted_streams[video_id]
            previously_posted = posted_info.get('platforms_posted', [])

            for platform in platforms:
                if platform.value in previously_posted:
                    platforms_already_posted.append(platform)
                    logger.info(f"[ORCHESTRATOR] ✓ {platform.value} already posted at {posted_info['timestamp']}")
                else:
                    platforms_to_post.append(platform)
                    logger.info(f"[ORCHESTRATOR] 📱 {platform.value} not yet posted - will attempt")
        else:
            # New stream - post to all platforms
            platforms_to_post = platforms
            logger.info(f"[ORCHESTRATOR] ✅ NEW STREAM - Will post to all platforms")

        # If all platforms already posted, return early
        if not platforms_to_post:
            logger.warning(f"[ORCHESTRATOR] 🛡️ ALL PLATFORMS ALREADY POSTED")
            return PostResponse(
                request_id=request_id,
                results=[
                    PostResult(
                        success=False,
                        platform=platform,
                        message=f"Already posted at {self.posted_streams[video_id]['timestamp']}",
                        timestamp=datetime.now()
                    ) for platform in platforms_already_posted
                ],
                success_count=0,
                failure_count=len(platforms_already_posted)
            )

        # Check if posting is already in progress
        if video_id in self.posting_in_progress:
            logger.warning(f"[ORCHESTRATOR] ⏳ POSTING ALREADY IN PROGRESS for {video_id}")
            return PostResponse(
                request_id=request_id,
                results=[
                    PostResult(
                        success=False,
                        platform=platform,
                        message="Posting already in progress",
                        timestamp=datetime.now()
                    ) for platform in platforms
                ],
                success_count=0,
                failure_count=len(platforms)
            )

        # Mark as in progress
        self.posting_in_progress.add(video_id)

        logger.info(f"[ORCHESTRATOR] ✅ PROCEEDING WITH POST")
        logger.info(f"[ORCHESTRATOR] 🚀 POSTING TO: {[p.value for p in platforms_to_post]}")
        if platforms_already_posted:
            logger.info(f"[ORCHESTRATOR] ⏭️ SKIPPING: {[p.value for p in platforms_already_posted]} (already posted)")

        # Create post content
        content = f"""@UnDaoDu going live!

{stream_title}

{stream_url}"""

        self.logger.info(f"[ORCHESTRATOR] Processing post request {request_id}")
        self.logger.info(f"[ORCHESTRATOR] Platforms to post: {[p.value for p in platforms_to_post]}")
        self.logger.info(f"[ORCHESTRATOR] Content: {stream_title}")

        # SEQUENTIAL POSTING - LinkedIn first, then X ONLY if LinkedIn succeeds
        results = []

        # Add skipped platforms to results
        for platform in platforms_already_posted:
            results.append(PostResult(
                success=False,
                platform=platform,
                message="Already posted - skipped",
                timestamp=datetime.now()
            ))

        # Track LinkedIn success for conditional X posting
        # CRITICAL: If LinkedIn was already posted, consider it successful for X posting
        linkedin_posted_successfully = Platform.LINKEDIN in platforms_already_posted

        # DEBUG: Log what platforms we're iterating over
        self.logger.info(f"[DEBUG] platforms_to_post = {[p.value for p in platforms_to_post]}")
        self.logger.info(f"[DEBUG] Starting platform iteration loop...")

        for platform in platforms_to_post:
            if platform == Platform.LINKEDIN:
                self.logger.info("="*80)
                self.logger.info("[ORCHESTRATOR] 🔵 STARTING LINKEDIN POSTING SEQUENCE")
                self.logger.info(f"[ORCHESTRATOR] ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                self.logger.info("="*80)

                result = await self._post_to_linkedin(content)
                results.append(result)
                linkedin_posted_successfully = result.success

                # DEBUG: Log the LinkedIn result
                self.logger.info(f"[DEBUG] LinkedIn result: success={result.success}, message={result.message}")
                self.logger.info(f"[DEBUG] linkedin_posted_successfully = {linkedin_posted_successfully}")

                if result.success:
                    self.logger.info("="*80)
                    self.logger.info("[ORCHESTRATOR] ✅ LINKEDIN POSTED SUCCESSFULLY")
                    self.logger.info(f"[ORCHESTRATOR] ⏰ Completed at: {datetime.now().strftime('%H:%M:%S')}")
                    self.logger.info("="*80)

                    # CRITICAL: Save LinkedIn success immediately to prevent re-posting
                    if video_id not in self.posted_streams:
                        self.posted_streams[video_id] = {
                            'timestamp': datetime.now().isoformat(),
                            'title': stream_title,
                            'url': stream_url,
                            'platforms_posted': []
                        }

                    if 'linkedin' not in self.posted_streams[video_id]['platforms_posted']:
                        self.posted_streams[video_id]['platforms_posted'].append('linkedin')
                        self._save_posted_history()
                        self.logger.info(f"[ORCHESTRATOR] 💾 Saved LinkedIn post to history immediately")

                    # Wait for browser cleanup before next platform
                    if Platform.X_TWITTER in platforms_to_post:  # Only wait if X will post
                        self.logger.info("[ORCHESTRATOR] ⏳ BROWSER CLEANUP DELAY: Starting 10-second wait...")
                        for i in range(10, 0, -1):
                            self.logger.info(f"[ORCHESTRATOR] ⏳ Cleanup countdown: {i} seconds remaining...")
                            await asyncio.sleep(1)
                        self.logger.info("[ORCHESTRATOR] ✅ Browser cleanup complete - ready for X")
                else:
                    self.logger.warning("="*80)
                    self.logger.warning("[ORCHESTRATOR] ❌ LINKEDIN FAILED - X WILL BE SKIPPED")
                    self.logger.warning(f"[ORCHESTRATOR] ⏰ Failed at: {datetime.now().strftime('%H:%M:%S')}")
                    self.logger.warning(f"[ORCHESTRATOR] 📝 Reason: {result.message}")
                    self.logger.warning("="*80)

            elif platform == Platform.X_TWITTER:
                # CRITICAL: Only post to X if LinkedIn was successful
                if not linkedin_posted_successfully:
                    self.logger.warning("="*80)
                    self.logger.warning("[ORCHESTRATOR] ⏭️ SKIPPING X/TWITTER")
                    self.logger.warning("[ORCHESTRATOR] 📝 Reason: LinkedIn posting failed")
                    self.logger.warning(f"[ORCHESTRATOR] ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                    self.logger.warning("="*80)
                    results.append(PostResult(
                        success=False,
                        platform=Platform.X_TWITTER,
                        message="Skipped - LinkedIn posting failed",
                        timestamp=datetime.now()
                    ))
                else:
                    self.logger.info("="*80)
                    self.logger.info("[ORCHESTRATOR] 🐦 STARTING X/TWITTER POSTING SEQUENCE")
                    self.logger.info("[ORCHESTRATOR] ✅ Prerequisite: LinkedIn posted successfully")
                    self.logger.info(f"[ORCHESTRATOR] ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                    self.logger.info("="*80)

                    result = await self._post_to_x_twitter(content)
                    results.append(result)

                    if result.success:
                        self.logger.info("="*80)
                        self.logger.info("[ORCHESTRATOR] ✅ X/TWITTER POSTED SUCCESSFULLY")
                        self.logger.info(f"[ORCHESTRATOR] ⏰ Completed at: {datetime.now().strftime('%H:%M:%S')}")
                        self.logger.info("="*80)

                        # CRITICAL: Save X success immediately to prevent re-posting
                        if video_id not in self.posted_streams:
                            self.posted_streams[video_id] = {
                                'timestamp': datetime.now().isoformat(),
                                'title': stream_title,
                                'url': stream_url,
                                'platforms_posted': []
                            }

                        if 'x_twitter' not in self.posted_streams[video_id]['platforms_posted']:
                            self.posted_streams[video_id]['platforms_posted'].append('x_twitter')
                            self._save_posted_history()
                            self.logger.info(f"[ORCHESTRATOR] 💾 Saved X/Twitter post to history immediately")
                    else:
                        self.logger.warning("="*80)
                        self.logger.warning("[ORCHESTRATOR] ❌ X/TWITTER POSTING FAILED")
                        self.logger.warning(f"[ORCHESTRATOR] 📝 Reason: {result.message}")
                        self.logger.warning(f"[ORCHESTRATOR] ⏰ Failed at: {datetime.now().strftime('%H:%M:%S')}")
                        self.logger.warning("="*80)
        
        # Count successes and failures
        success_count = sum(1 for r in results if r.success)
        failure_count = len(results) - success_count
        
        response = PostResponse(
            request_id=request_id,
            results=results,
            success_count=success_count,
            failure_count=failure_count
        )

        # Record in posted history (merge with existing if partial success)
        if success_count > 0 or len(platforms) == 0:  # Save even when testing with no platforms
            # Get existing platforms if stream was partially posted before
            existing_platforms = []
            if video_id in self.posted_streams:
                existing_platforms = self.posted_streams[video_id].get('platforms_posted', [])

            # Add newly successful platforms
            newly_posted = [r.platform.value for r in results
                          if r.success and r.message != "Already posted - skipped"]

            # Merge platforms (avoid duplicates)
            all_posted_platforms = list(set(existing_platforms + newly_posted))

            self.posted_streams[video_id] = {
                'timestamp': datetime.now().isoformat(),
                'title': stream_title,
                'url': stream_url,
                'platforms_posted': all_posted_platforms
            }
            self._save_posted_history()
            logger.info(f"[ORCHESTRATOR] 💾 Saved to posted history: {video_id}")
            logger.info(f"[ORCHESTRATOR] 📊 Platforms posted: {all_posted_platforms}")

        # Remove from in-progress set
        self.posting_in_progress.discard(video_id)

        self.logger.info(f"[ORCHESTRATOR] Completed {request_id}: {success_count}/{len(results)} successful")
        return response

    async def _verify_live_status_before_posting(self) -> bool:
        """
        SIMPLIFIED: Since we now trust the caller's detection, this is optional.
        Only used for manual verification calls.
        """
        try:
            self.logger.info("[VERIFICATION] Manual verification requested...")

            # Use scraping only - no API needed
            try:
                from modules.platform_integration.stream_resolver.src.no_quota_stream_checker import NoQuotaStreamChecker
                scraper = NoQuotaStreamChecker()

                # Check both channels
                channels = [
                    ("UC-LSSlOZwpGIRIYihaz8zCw", "UnDaoDu"),
                    ("UCSNTUXjAgpd4sgWYP0xoJgw", "FoundUps")
                ]

                for channel_id, channel_name in channels:
                    live_info = scraper.check_channel_for_live(channel_id)
                    if live_info:
                        self.logger.info(f"[VERIFICATION] ✅ {channel_name} is LIVE")
                        return True

                self.logger.info("[VERIFICATION] 📭 No channels are live")
                return False

            except Exception as e:
                self.logger.error(f"[VERIFICATION] Scraping failed: {e}")
                # When in doubt, trust the original detection
                return True

        except Exception as e:
            self.logger.error(f"[VERIFICATION] Error in manual verification: {e}")
            return True  # Trust the original detection

    def check_if_already_posted(self, video_id: str) -> Dict[str, Any]:
        """
        Check if a video has already been posted to social media platforms.

        Args:
            video_id: YouTube video ID to check

        Returns:
            Dictionary with posting status for each platform
        """
        result = {
            'video_id': video_id,
            'already_posted': False,
            'platforms_posted': [],
            'timestamp': None
        }

        if video_id in self.posted_streams:
            posted_info = self.posted_streams[video_id]
            result['already_posted'] = True
            result['platforms_posted'] = posted_info.get('platforms_posted', [])
            result['timestamp'] = posted_info.get('timestamp')

            self.logger.info(f"[CHECK] Video {video_id} already posted to: {result['platforms_posted']}")
        else:
            self.logger.info(f"[CHECK] Video {video_id} has NOT been posted yet")

        return result

    async def verify_live_status_manually(self) -> bool:
        """
        🚨 ENHANCEMENT TRIGGER: Manual verification method

        This method can be called independently to verify if @UnDaoDu and Move2Japan
        are currently live. Useful for testing and manual triggers.

        Returns True if at least one channel is confirmed live.
        """
        return await self._verify_live_status_before_posting()

    def _load_posted_history(self) -> dict:
        """Load history of posted streams from SQLite database"""
        import sqlite3
        import json
        import os

        # Use existing whack-a-maga database for all gamification/tracking
        # Navigate from platform_integration/social_media_orchestrator/src to modules root
        module_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(
            module_root,
            "gamification", "whack_a_magat", "data", "magadoom_scores.db"
        )

        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS social_posts (
                    video_id TEXT PRIMARY KEY,
                    title TEXT,
                    url TEXT,
                    platforms_posted TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Load all posted streams
            cursor.execute("SELECT video_id, title, url, platforms_posted, timestamp FROM social_posts")
            rows = cursor.fetchall()

            history = {}
            for video_id, title, url, platforms_json, timestamp in rows:
                platforms = json.loads(platforms_json) if platforms_json else []
                history[video_id] = {
                    'title': title,
                    'url': url,
                    'platforms_posted': platforms,
                    'timestamp': timestamp
                }

            conn.close()
            self.logger.info(f"[ORCHESTRATOR] 📚 Loaded {len(history)} posted streams from database")
            return history

        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] Error loading from database: {e}")
            # Fallback to JSON if database fails
            return self._load_posted_history_json()

    def _load_posted_history_json(self) -> dict:
        """Fallback: Load history from JSON file"""
        import json
        history_file = "memory/orchestrator_posted_streams.json"
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
                self.logger.info(f"[ORCHESTRATOR] 📚 Loaded {len(history)} posted streams from JSON fallback")
                return history
        except FileNotFoundError:
            self.logger.info("[ORCHESTRATOR] 📚 No JSON history found, starting fresh")
            return {}
        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] Error loading JSON: {e}")
            return {}

    def _save_posted_history(self):
        """Save posted history to SQLite database"""
        import sqlite3
        import json
        import os
        from datetime import datetime

        # Use existing whack-a-maga database
        # Navigate from platform_integration/social_media_orchestrator/src to modules root
        module_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(
            module_root,
            "gamification", "whack_a_magat", "data", "magadoom_scores.db"
        )

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Update or insert each stream
            for video_id, data in self.posted_streams.items():
                platforms_json = json.dumps(data.get('platforms_posted', []))

                cursor.execute("""
                    INSERT OR REPLACE INTO social_posts
                    (video_id, title, url, platforms_posted, timestamp, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    video_id,
                    data.get('title', ''),
                    data.get('url', ''),
                    platforms_json,
                    data.get('timestamp', datetime.now().isoformat()),
                    datetime.now().isoformat()
                ))

            conn.commit()
            conn.close()
            self.logger.info(f"[ORCHESTRATOR] 💾 Saved {len(self.posted_streams)} posted streams to database")

        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] Error saving to database: {e}")
            # Fallback to JSON
            self._save_posted_history_json()

    def _save_posted_history_json(self):
        """Fallback: Save to JSON file"""
        import json
        import os

        os.makedirs("memory", exist_ok=True)
        history_file = "memory/orchestrator_posted_streams.json"

        try:
            with open(history_file, 'w') as f:
                json.dump(self.posted_streams, f, indent=2)
            self.logger.info(f"[ORCHESTRATOR] 💾 Saved {len(self.posted_streams)} posted streams to JSON")
        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] Error saving JSON: {e}")

    async def _post_to_linkedin(self, content: str) -> PostResult:
        """Post to LinkedIn using existing anti-detection poster"""
        try:
            self.logger.info("="*60)
            self.logger.info("[LINKEDIN] 🔵 ATTEMPTING LINKEDIN POST")
            self.logger.info("="*60)

            if not (os.getenv('LINKEDIN_EMAIL') and os.getenv('LINKEDIN_PASSWORD')):
                self.logger.warning("[LINKEDIN] ❌ LinkedIn credentials not configured")
                return PostResult(
                    success=False,
                    platform=Platform.LINKEDIN,
                    message="LinkedIn credentials not configured",
                    timestamp=datetime.now()
                )

            self.logger.info("[LINKEDIN] ✅ Credentials found")
            self.logger.info(f"[LINKEDIN] 📝 Content length: {len(content)} chars")
            self.logger.info("[LINKEDIN] 🚀 Starting anti-detection poster...")

            # Use unified LinkedIn interface (WSP 3 compliant)
            from modules.platform_integration.social_media_orchestrator.src.unified_linkedin_interface import post_stream_notification, post_general_content

            # Extract video ID for duplicate prevention
            video_id = None
            import re
            video_match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', content)
            if video_match:
                video_id = video_match.group(1)

            if video_id:
                # Extract title from content
                lines = content.split('\n')
                title = lines[0] if lines else "Live Stream"
                if title.startswith("🔴 LIVE: "):
                    title = title[9:]  # Remove prefix

                # Extract URL
                url_match = re.search(r'https://[^\s]+', content)
                stream_url = url_match.group(0) if url_match else f"https://www.youtube.com/watch?v={video_id}"

                # Use specialized stream notification function
                self.logger.info(f"[LINKEDIN] Using unified interface for stream: {video_id}")
                result = await post_stream_notification(title, stream_url, video_id)
            else:
                # Fallback to general posting
                self.logger.info("[LINKEDIN] Using unified interface for general content")
                result = await post_general_content(content)

            # Convert to orchestrator's PostResult format
            if result.success:
                self.logger.info("[LINKEDIN] ✅ LinkedIn posting successful (unified)")
                return PostResult(
                    success=True,
                    platform=Platform.LINKEDIN,
                    message="Posted successfully via unified interface",
                    timestamp=result.timestamp
                )
            else:
                self.logger.warning(f"[ORCHESTRATOR] ❌ LinkedIn posting failed (unified): {result.message}")
                return PostResult(
                    success=False,
                    platform=Platform.LINKEDIN,
                    message=result.message,
                    timestamp=result.timestamp
                )
            
        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] LinkedIn error: {e}")
            return PostResult(
                success=False,
                platform=Platform.LINKEDIN,
                message=str(e),
                timestamp=datetime.now()
            )
    
    async def _post_to_x_twitter(self, content: str) -> PostResult:
        """Post to X/Twitter using existing anti-detection poster"""
        try:
            self.logger.info("="*60)
            self.logger.info("[X/TWITTER] 🐦 ATTEMPTING X/TWITTER POST")
            self.logger.info("="*60)

            if not (os.getenv('X_Acc1') and os.getenv('x_Acc_pass')):
                self.logger.warning("[X/TWITTER] ❌ X/Twitter credentials not configured")
                return PostResult(
                    success=False,
                    platform=Platform.X_TWITTER,
                    message="X/Twitter credentials not configured",
                    timestamp=datetime.now()
                )

            self.logger.info("[X/TWITTER] ✅ Credentials found")
            self.logger.info(f"[X/TWITTER] 📝 Content length: {len(content)} chars")
            self.logger.info("[X/TWITTER] 🚀 Starting anti-detection poster...")
            
            # Import and use existing X poster
            from modules.platform_integration.x_twitter.src.x_anti_detection_poster import AntiDetectionX
            
            # Run in thread to not block async (same pattern as livechat)
            import threading
            
            x_success = False
            error_message = None
            x_completed = threading.Event()
            
            def post_to_x():
                nonlocal x_success, error_message
                global _GLOBAL_X_POSTER

                try:
                    # Use global singleton with thread-safe lock
                    with _POSTER_LOCK:
                        # Check if browser was manually closed
                        browser_closed = False
                        if _GLOBAL_X_POSTER:
                            try:
                                # Try to access the browser to see if it's still alive
                                if _GLOBAL_X_POSTER.driver:
                                    _ = _GLOBAL_X_POSTER.driver.current_url
                            except Exception as e:
                                self.logger.warning("[X THREAD] ⚠️ Browser was manually closed")
                                self.logger.info("[X THREAD] 🔄 Will create new instance")
                                browser_closed = True
                                _GLOBAL_X_POSTER = None

                        # REUSE GLOBAL SINGLETON INSTANCE - Only ONE browser window
                        if _GLOBAL_X_POSTER is None:
                            if browser_closed:
                                self.logger.info("[X THREAD] 🔄 Recreating X poster after manual close...")
                            else:
                                self.logger.info("[X THREAD] [NEW] Creating GLOBAL singleton X poster...")
                            self.logger.info("[X THREAD] [GLOBAL] This will open ONE browser window")
                            _GLOBAL_X_POSTER = AntiDetectionX()
                            self.logger.info("[X THREAD] ✅ Global X poster created")
                        else:
                            self.logger.info("[X THREAD] ♻️ REUSING GLOBAL X instance")
                            self.logger.info("[X THREAD] 🌐 Browser window already open")

                        self.logger.info("[X THREAD] 📤 Calling post_to_x()...")
                        self.logger.info(f"[X THREAD] ⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
                        result = _GLOBAL_X_POSTER.post_to_x(content)  # Note: removed video_id param
                        self.logger.info(f"[X THREAD] ⏰ End time: {datetime.now().strftime('%H:%M:%S')}")

                    x_success = bool(result)
                    if not x_success:
                        error_message = "X poster returned False"
                except Exception as e:
                    error_message = str(e)
                finally:
                    x_completed.set()
            
            thread = threading.Thread(target=post_to_x, daemon=False)
            thread.start()
            
            # Wait for completion (convert to async wait)
            while not x_completed.is_set():
                await asyncio.sleep(0.1)
            
            if x_success:
                self.logger.info("[ORCHESTRATOR] ✅ X/Twitter posting successful")
                return PostResult(
                    success=True,
                    platform=Platform.X_TWITTER,
                    message="Posted successfully",
                    timestamp=datetime.now()
                )
            else:
                self.logger.warning(f"[ORCHESTRATOR] ❌ X/Twitter posting failed: {error_message}")
                return PostResult(
                    success=False,
                    platform=Platform.X_TWITTER,
                    message=error_message or "Unknown error",
                    timestamp=datetime.now()
                )
            
        except Exception as e:
            self.logger.error(f"[ORCHESTRATOR] X/Twitter error: {e}")
            return PostResult(
                success=False,
                platform=Platform.X_TWITTER,
                message=str(e),
                timestamp=datetime.now()
            )


# Convenient instance for import
orchestrator = SimplePostingOrchestrator()


# Convenience functions for easy import
async def post_stream_notification(stream_title: str, stream_url: str) -> PostResponse:
    """Convenience function for posting stream notifications"""
    return await orchestrator.post_stream_notification(stream_title, stream_url)


def handle_stream_detected(video_id: str, stream_title: str = None) -> None:
    """
    Handle stream detection from stream_resolver - runs posting in background.
    This is the WSP 3 compliant entry point for stream detection events.

    Args:
        video_id: YouTube video ID of detected stream
        stream_title: Optional title of stream
    """
    import threading
    import asyncio

    logger = logging.getLogger(__name__)

    def post_in_background():
        try:
            # Check if already posted
            status = orchestrator.check_if_already_posted(video_id)
            if status['already_posted']:
                platforms = status['platforms_posted']
                logger.info(f"[ORCHESTRATOR] Video {video_id} already posted to: {platforms}")

            # Build stream URL
            stream_url = f"https://www.youtube.com/watch?v={video_id}"
            final_title = stream_title or "Live Stream"

            logger.info(f"[ORCHESTRATOR] Processing stream detected: {final_title}")

            # Run async method in sync context
            response = asyncio.run(orchestrator.post_stream_notification(
                stream_title=final_title,
                stream_url=stream_url,
                platforms=[Platform.LINKEDIN, Platform.X_TWITTER]
            ))

            # Log results
            if response.all_successful():
                logger.info(f"[ORCHESTRATOR] ✅ Posted to all platforms successfully")
            else:
                logger.info(f"[ORCHESTRATOR] Posted to {response.success_count}/{len(response.results)} platforms")

        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Background posting error: {e}")

    # Start posting in background thread
    thread = threading.Thread(target=post_in_background, daemon=True)
    thread.start()
    logger.info(f"[ORCHESTRATOR] Social media posting triggered in background for {video_id}")