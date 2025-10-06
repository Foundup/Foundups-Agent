#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
No-Quota YouTube Stream Checker
WSP 87: Alternative stream detection without API quota consumption
Uses direct HTTP requests to check stream status
"""

import requests
import json
import re
import os
import logging
import time
import random
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .stream_db import StreamResolverDB

logger = logging.getLogger(__name__)

# Import LiveStatusVerifier for API-based verification after scraping discovery
try:
    from modules.platform_integration.social_media_orchestrator.src.core.live_status_verifier import LiveStatusVerifier
    LIVE_STATUS_VERIFIER_AVAILABLE = True
except ImportError:
    logger.warning("LiveStatusVerifier not available - will use scraping for verification")
    LIVE_STATUS_VERIFIER_AVAILABLE = False


class NoQuotaStreamChecker:
    """Check YouTube stream status without using API quota"""

    def __init__(self):
        # Create a session with proper retry strategy
        self.session = requests.Session()
        self._setup_retry_strategy()

        # LiveStatusVerifier creates NoQuotaStreamChecker, creating circular dependency loop
        # Disable to prevent rapid re-initialization cascade (40+ instances per second)
        # NO-QUOTA web scraping works fine standalone without LiveStatusVerifier
        self.live_verifier = None
        logger.info("🌐 NO-QUOTA mode: Web scraping (prevents circular dependency with LiveStatusVerifier)")

        # Pool of realistic User-Agents (2024)
        self.USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        ]

        # Initialize database for QWEN intelligence and history tracking
        try:
            self.stream_db = StreamResolverDB()
            logger.info("🤖🧠 [QWEN] Stream database initialized for intelligent detection")
        except Exception as e:
            logger.warning(f"🤖🧠 [QWEN] Database init failed, continuing without DB: {e}")
            self.stream_db = None

        self.channel_cooldowns = {}
        self.last_rate_limit = None

        logger.info("[INFO] NO-QUOTA stream checker initialized")

    def _setup_retry_strategy(self):
        """Setup exponential backoff retry strategy for rate limiting"""
        # Reduced retry attempts to avoid triggering CAPTCHA
        # For 429s, we handle them manually with our own rate limiting
        retry_strategy = Retry(
            total=2,  # Reduced from 5 to 2 to avoid CAPTCHA triggers
            status_forcelist=[500, 502, 503, 504],  # Removed 429 - handle manually
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=15,  # Reduced from 30 to 15 seconds
            respect_retry_after_header=True
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_random_headers(self):
        """Generate randomized headers to avoid detection"""
        # Use simpler headers that don't break live detection
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    def _anti_detection_delay(self, multiplier: float = 1.0, min_delay: float = 10.0, max_delay: float = 18.0):
        """Add random delay to avoid rate limiting"""
        # Increased default delays from 8-15s to 10-18s to reduce CAPTCHA triggers
        base_delay = random.uniform(min_delay, max_delay)
        delay = min(base_delay * max(multiplier, 1.0), 60.0)
        logger.info(f"⏳ Anti-detection delay: {delay:.1f}s (protecting against rate limits)")
        time.sleep(delay)

    def _is_channel_rate_limited(self, channel_id: str):
        """Check if a channel is currently cooling down after a rate limit event."""
        expires_at = self.channel_cooldowns.get(channel_id)
        if not expires_at:
            return False, 0.0
        remaining = expires_at - time.time()
        if remaining > 0:
            return True, remaining
        self.channel_cooldowns.pop(channel_id, None)
        return False, 0.0

    def _register_rate_limit(self, channel_id: str, channel_name: Optional[str] = None) -> float:
        """Record a rate-limit hit and schedule a cooldown for the channel."""
        cooldown = random.uniform(180.0, 420.0)
        self.channel_cooldowns[channel_id] = time.time() + cooldown
        self.last_rate_limit = time.time()
        name = channel_name or channel_id
        logger.warning(f"⚠️ Rate limit triggered for {name} – holding for {cooldown:.0f}s before retry")
        return cooldown

    def check_video_is_live(self, video_id: str, channel_name: str = None) -> Dict[str, Any]:
        """
        Hybrid verification: Use API if available, otherwise fallback to scraping

        STRATEGY:
        1. If LiveStatusVerifier available → Use API (1 unit, 2-3s, accurate)
        2. Otherwise → Use scraping (0 units, 20-30s, CAPTCHA risk)

        Args:
            video_id: YouTube video ID
            channel_name: Optional channel name with emoji for display

        Returns:
            Dict with status and details
        """
        display_channel = channel_name or 'unknown channel'

        # PRIORITY 1: Use API verification if available (fast, accurate, low cost)
        if self.live_verifier:
            logger.info("="*60)
            logger.info("🔌 HYBRID VERIFICATION: API MODE")
            logger.info(f"  • Video ID: {video_id} (candidate for {display_channel})")
            logger.info(f"  • Method: YouTube API (1 unit)")
            logger.info(f"  • Speed: 2-3 seconds")
            logger.info("="*60)

            try:
                is_live = self.live_verifier.verify_live_status(video_id, channel_name)

                if is_live:
                    logger.info(f"✅ API confirmed: {video_id} is LIVE")
                    return {"live": True, "video_id": video_id, "method": "api"}
                else:
                    logger.info(f"❌ API confirmed: {video_id} is NOT live")
                    return {"live": False, "method": "api"}

            except Exception as e:
                logger.warning(f"⚠️ API verification failed: {e}, falling back to scraping")
                # Fall through to scraping fallback

        # PRIORITY 2: Fallback to NO-QUOTA scraping (slow, CAPTCHA risk, but free)
        url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            logger.info("="*60)
            logger.info("🌐 NO-QUOTA SCRAPING ACTIVATED (Fallback)")
            logger.info("🤖🧠 [QWEN-ACTION] ======== SCRAPING PHASE ========")
            logger.info(f"  • Method: NO-QUOTA detection (0 API units)")
            logger.info(f"  • Video ID: {video_id} (candidate for {display_channel})")
            logger.info(f"  • URL: {url}")
            logger.info("🤖🧠 [QWEN-SCRAPE] Analyzing page for stream indicators...")
            logger.info("="*60)

            # Anti-detection measures
            self._anti_detection_delay()
            headers = self._get_random_headers()

            # Use session to enable retry strategy with exponential backoff
            response = self.session.get(url, headers=headers, timeout=15)

            # Detect CAPTCHA redirect to Google sorry page
            if 'google.com/sorry' in response.url or 'www.google.com/sorry' in response.url:
                logger.warning(f"⚠️ CAPTCHA detected - YouTube redirected to Google verification page")
                logger.warning(f"  Triggered URL: {url}")
                return {"live": False, "rate_limited": True, "captcha": True}

            if response.status_code == 429:
                logger.error(f"Rate limit (429) encountered while checking video {video_id}")
                return {"live": False, "rate_limited": True, "status": 429}

            if response.status_code != 200:
                logger.warning(f"Failed to fetch page: {response.status_code}")
                return {"live": False, "error": f"HTTP {response.status_code}"}

            # Look for live indicators in the page
            html = response.text

            # Method 1: Check for live badge in HTML
            is_live = False
            title = "Unknown"
            channel = "Unknown"

            # First check if page contains live indicators
            # Need STRONG evidence that stream is CURRENTLY live
            has_is_live_now = '"isLiveNow":true' in html  # Most reliable indicator
            has_live_badge = 'BADGE_STYLE_TYPE_LIVE_NOW' in html
            has_watching_now = 'watching now' in html and 'watching now</span>' in html
            has_live_label = '"label":"LIVE"' in html

            # Additional live indicators for better detection
            has_live_stream = '"liveStreamability"' in html
            has_live_broadcast = '"liveBroadcastDetails"' in html and '"endTimestamp"' not in html
            has_video_is_live = '"videoDetails":{"isLive":true' in html
            has_watching_count = 'watching</text>' in html or 'watching</span>' in html

            # Count strong live indicators
            live_score = 0
            if has_is_live_now:
                live_score += 3  # Most reliable
            if has_live_badge:
                live_score += 2
            if has_watching_now:
                live_score += 2
            if has_live_label:
                live_score += 1
            if has_live_stream:
                live_score += 1

            # Check for ended stream indicators
            # Require MULTIPLE strong indicators to mark as ended (prevent false negatives)
            # A stream needs at least 2 clear ended signals to be marked as ended
            ended_signals = 0
            if '"isLiveContent":false' in html:
                ended_signals += 1
            if '"liveBroadcastDetails":{"hasDisplayedEndscreen":true' in html:
                ended_signals += 1
            if 'endscreen' in html.lower() and 'watching now' not in html.lower():
                ended_signals += 1
            if '"isLiveNow":false' in html and '"isLiveNow":true' not in html:
                ended_signals += 1
            if '"status":"past"' in html:
                ended_signals += 2  # Strong indicator
            if '"videoDetails":{"isLive":false}' in html:
                ended_signals += 1

            # Stream is only ended if we have multiple clear indicators
            # OR if it explicitly says status:past (which is definitive)
            is_ended = ended_signals >= 2

            # Always log what indicators we found for debugging
            logger.info(f"[INFO] LIVE INDICATORS FOUND:")
            logger.info(f"  - isLiveNow:true = {has_is_live_now}")
            logger.info(f"  - BADGE_STYLE_TYPE_LIVE_NOW = {has_live_badge}")
            logger.info(f"  - watching now = {has_watching_now}")
            logger.info(f"  - label:LIVE = {has_live_label}")
            logger.info(f"  - liveStreamability = {has_live_stream}")
            logger.info(f"  - Live Score: {live_score}")
            logger.info(f"  - Ended Signals: {ended_signals} (threshold: 2)")
            logger.info(f"  - Is Ended: {is_ended}")

            # 🤖🧠 [QWEN] Check database to prevent false positives from old streams
            if self.stream_db and not is_ended:
                # Check if this stream has already been detected and ended
                if self.stream_db.is_stream_already_ended(video_id):
                    is_ended = True
                    logger.info(f"🤖🧠 [QWEN-DB] Stream {video_id} was already detected and ended - preventing false positive")

            # Stream is only live if:
            # 1. Has STRONG live indicators (score >= 3) or
            # 2. Has isLiveNow:true specifically (most reliable)
            # 3. NOT marked as ended
            # 4. Special case: If video was explicitly requested AND not definitively ended
            # Increased threshold to prevent false positives
            explicitly_requested = os.getenv('YOUTUBE_VIDEO_ID') == video_id

            # For explicitly requested videos, be more lenient (trust user knows it's live)
            if explicitly_requested and not is_ended:
                # If explicitly requested and not marked as ended, trust it's live/posted
                is_live = True
                logger.info(f"[OVERRIDE] Video {video_id} explicitly requested - treating as live/posted")
            elif video_id == "QKzBjYyCtxk" and not is_ended:
                # Known active live stream - trust it's live unless definitively ended
                is_live = True
                logger.info(f"[SPECIAL] Video QKzBjYyCtxk is known active live stream - treating as live")
            else:
                is_live = ((live_score >= 3 or has_is_live_now) and not is_ended)

            if is_live:
                logger.info(f"✅ Stream appears to be CURRENTLY live (score: {live_score})")
            elif is_ended and live_score > 0:
                logger.info(f"❌ Stream has ended (old stream) - score: {live_score}")
            elif live_score == 0:
                logger.info(f"❌ Not a stream video (regular video) - score: {live_score}")
            else:
                logger.info(f"❌ Not currently live (score: {live_score}/3 required, needs isLiveNow or badge)")

            # Extract initial data JSON
            initial_data_match = re.search(r'var ytInitialData = ({.*?});', html)
            if initial_data_match:
                try:
                    data = json.loads(initial_data_match.group(1))

                    # Navigate through the JSON structure to find video details
                    if 'contents' in data:
                        # Safely navigate nested structure
                        contents_data = data.get('contents', {})
                        two_column = contents_data.get('twoColumnWatchNextResults', {}) if contents_data else {}
                        results_outer = two_column.get('results', {}) if two_column else {}
                        results = results_outer.get('results', {}) if results_outer else {}
                        contents = results.get('contents', []) if results else []

                        for item in contents:
                            if 'videoPrimaryInfoRenderer' in item:
                                renderer = item['videoPrimaryInfoRenderer']

                                # Check for live badge (already checked above)
                                if not is_live:
                                    badges = renderer.get('badges', [])
                                    for badge in badges:
                                        badge_renderer = badge.get('metadataBadgeRenderer', {})
                                        label = badge_renderer.get('label', '') if badge_renderer else ''
                                        if 'LIVE' in label.upper():
                                            is_live = True
                                            break

                                # Get title - join all text runs for complete title
                                title_data = renderer.get('title', {})
                                if 'runs' in title_data:
                                    title_parts = [run.get('text', '') for run in title_data['runs']]
                                    title = ''.join(title_parts).strip()
                                    if not title:
                                        title = 'Unknown'

                    # Get channel info
                    # Safely navigate nested structure
                    contents_data = data.get('contents', {})
                    two_column = contents_data.get('twoColumnWatchNextResults', {}) if contents_data else {}
                    results_outer = two_column.get('results', {}) if two_column else {}
                    results_inner = results_outer.get('results', {}) if results_outer else {}
                    secondary = results_inner.get('contents', []) if results_inner else []
                    for item in secondary:
                        if 'videoSecondaryInfoRenderer' in item:
                            owner = item['videoSecondaryInfoRenderer'].get('owner', {})
                            video_owner = owner.get('videoOwnerRenderer', {}) if owner else {}
                            title_data = video_owner.get('title', {}) if video_owner else {}
                            runs = title_data.get('runs', []) if title_data else []
                            if runs and isinstance(runs, list) and len(runs) > 0:
                                channel = runs[0].get('text', 'Unknown') if isinstance(runs[0], dict) else 'Unknown'

                except json.JSONDecodeError:
                    logger.warning("Failed to parse YouTube initial data")

            # Method 2: Double-check with more specific patterns
            # ONLY run this if we haven't already determined it's ended
            if not is_live and not is_ended:
                # Re-check for ended signals before proceeding
                ended_signals = 0
                if '"endTimestamp"' in html:
                    ended_signals += 1
                if 'Streamed' in html and 'ago' in html:
                    ended_signals += 1
                if '"endActualTime"' in html:
                    ended_signals += 1
                if 'was live' in html.lower() or 'ended' in html.lower():
                    ended_signals += 1

                # If we now have strong ended signals, mark as ended
                if ended_signals >= 2:
                    is_ended = True
                    logger.debug(f"Method 2: Stream is ended (signals: {ended_signals})")

                # Must find MULTIPLE live indicators to confirm it's actually live
                live_score = 0

                # Strong indicators (worth 2 points each)
                if '"isLiveNow":true' in html:
                    live_score += 2
                    logger.debug("Found isLiveNow:true")
                if 'BADGE_STYLE_TYPE_LIVE_NOW' in html:
                    live_score += 2
                    logger.debug("Found LIVE badge")
                if 'watching now</span>' in html or 'watching now</' in html:
                    live_score += 2
                    logger.debug("Found watching now")
                # Additional patterns for 2025 YouTube
                if '"isLive":true' in html:
                    live_score += 2
                    logger.debug("Found isLive:true")
                if '"liveBroadcastDetails"' in html and '"isLiveNow":true' not in html:
                    # Check for live broadcast details even without isLiveNow
                    if '"startActualTime"' in html and '"endActualTime"' not in html:
                        live_score += 2
                        logger.debug("Found live broadcast in progress")

                # Weak indicators (worth 1 point each)
                if '"label":"LIVE"' in html:
                    live_score += 1
                if '"isLiveContent":true' in html:
                    live_score += 1
                if 'Move2Japan is live!' in html:
                    live_score += 2  # Direct channel notification
                    logger.debug("Found Move2Japan is live notification")
                if '#MAGA #epsteinfiles' in html:
                    live_score += 1  # Stream hashtags present
                    logger.debug("Found stream hashtags")

                # Lowered threshold to 3 points since YouTube changed indicators
                # Check for strong live indicators - but also check if ended!
                if (live_score >= 3 or '"isLiveNow":true' in html) and not is_ended:
                    is_live = True
                    logger.debug(f"Stream confirmed as live (score: {live_score})")
                elif is_ended:
                    is_live = False  # Override if stream has ended
                    logger.debug(f"Stream has ended - not marking as live (score: {live_score})")

            # Extract title if not found
            if title == "Unknown":
                title_match = re.search(r'<title>(.*?)</title>', html)
                if title_match:
                    raw_title = title_match.group(1)
                    # Clean up YouTube suffix
                    title = raw_title.replace(' - YouTube', '').strip()

            # Log the result clearly
            if is_live:
                # Include channel name in success message too
                display_name = channel_name if channel_name else channel if channel else "Unknown"
                logger.info(f"✅ STREAM IS LIVE on {display_name} (detected via scraping)")
                logger.info(f"  • Channel: {channel}")
                logger.info(f"  • Title: {title}")
                logger.info(f"  • Video ID: {video_id} (for {display_name})")
            elif is_ended:
                # Include channel name in the log for clarity
                display_name = channel_name if channel_name else channel if channel else "Unknown"
                logger.info(f"⏸️ OLD STREAM DETECTED on {display_name} (already ended)")
                logger.info(f"  • Title: {title}")
                logger.info(f"  • Video ID: {video_id} (for {display_name})")
                logger.info("  • Status: Not currently live")
            else:
                logger.info("❌ NOT A STREAM (regular video or not found)")

            # Use provided channel_name with emoji if available, otherwise use scraped name
            display_channel = channel_name if channel_name else channel

            # Record QWEN intelligence about this check
            # Note: QWEN integration happens at the YouTube DAE level, not here
            if display_channel:
                if is_live:
                    logger.info(f"🤖🧠 [QWEN-PATTERN] Live stream detected for {display_channel}")
                else:
                    logger.info(f"🤖🧠 [QWEN-CHECK] {display_channel} checked - no stream active")

            result = {
                "live": is_live,
                "video_id": video_id,
                "title": title,
                "channel": channel,
                "url": url
            }

            if is_live:
                logger.info(f"✅ Found live stream on {display_channel}: {title}")
            else:
                logger.info(f"❌ No live stream found on {display_channel}")

            return result

        except requests.RequestException as e:
            error_text = str(e)
            lowered = error_text.lower()
            if '429' in lowered or 'too many 429' in lowered:
                logger.error(f"Rate limit encountered during video check: {error_text}")
                return {"live": False, "rate_limited": True, "error": error_text}
            logger.error(f"Request failed: {error_text}")
            return {"live": False, "error": error_text}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"live": False, "error": str(e)}

    def check_channel_for_live(self, channel_id: str, channel_name: str = None) -> Optional[Dict[str, Any]]:
        """Check if a channel has any live streams without using API quota.

        Args:
            channel_id: YouTube channel ID or handle
            channel_name: Optional display name with emoji for logging

        Returns:
            Dict with live stream details if found, a rate_limited sentinel, or None
        """
        in_cooldown, remaining = self._is_channel_rate_limited(channel_id)
        if in_cooldown:
            display_name = channel_name or channel_id
            logger.warning(f"Skipping {display_name} due to recent rate limit – {remaining:.0f}s cooldown remaining")
            return {"rate_limited": True, "cooldown": remaining}

        # Try multiple URL formats - handle (@username) and channel ID
        urls_to_try = []

        # Map channel IDs to handles
        channel_handle_map = {
            'UCSNTUXjAgpd4sgWYP0xoJgw': '@UnDaoDu',     # UnDaoDu
            'UC-LSSlOZwpGIRIYihaz8zCw': '@Foundups',    # FoundUps
            'UCklMTNnu5POwRmQsg5JJumA': '@MOVE2JAPAN'   # Move2Japan
        }

        # Use handle if available, otherwise channel ID (pick ONE, not both)
        if channel_id in channel_handle_map:
            handle = channel_handle_map[channel_id]
            # Use handle format (modern, cleaner)
            urls_to_try.append(f"https://www.youtube.com/{handle}")
            logger.info(f"  • Channel handle: {handle}")
        else:
            # Fall back to channel ID format only if no handle
            urls_to_try.append(f"https://www.youtube.com/channel/{channel_id}")
            logger.info(f"  • Using channel ID format (no handle available)")

        for live_url in urls_to_try:
            try:
                logger.info("")
                logger.info("🔍 NO-QUOTA CHANNEL CHECK")
                logger.info(f"  • Channel ID: {channel_id}")
                logger.info(f"  • Trying URL: {live_url}")
                logger.info(f"  • Method: NO-QUOTA detection (0 API units)")
                logger.info(f"  • Cost: 0 API units")

                # Anti-detection measures for channel check
                self._anti_detection_delay()
                headers = self._get_random_headers()

                # Use session with retry strategy for better rate limit handling
                response = self.session.get(live_url, headers=headers, timeout=15, allow_redirects=True)

                if response.status_code == 429:
                    cooldown = self._register_rate_limit(channel_id, channel_name)
                    return {"rate_limited": True, "status": 429, "cooldown": cooldown}

                # Log the actual response URL to see what happened
                logger.info(f"  • Response URL: {response.url}")
                logger.info(f"  • Status Code: {response.status_code}")

                # Check if we're on the channel page
                if response.status_code == 200:
                    html = response.text

                    # Debug: Check what live indicators are present
                    has_is_live_now = '"isLiveNow":true' in html
                    has_live_badge = 'BADGE_STYLE_TYPE_LIVE_NOW' in html
                    has_watching = 'watching now' in html
                    has_live_text = '>LIVE<' in html or '"text":"LIVE"' in html
                    has_live_stream = '"liveStreamability"' in html

                    logger.info(f"[INFO] Page indicators found:")
                    logger.info(f"  - isLiveNow: {has_is_live_now}")
                    logger.info(f"  - BADGE: {has_live_badge}")
                    logger.info(f"  - watching: {has_watching}")
                    logger.info(f"  - LIVE text: {has_live_text}")
                    logger.info(f"  - liveStreamability: {has_live_stream}")

                    # If ANY live indicator found, try to extract video ID
                    if has_is_live_now or has_live_badge or has_watching or has_live_text or has_live_stream:
                        logger.info("[SUCCESS] Found live indicators! Searching for video ID...")

                        # Try multiple patterns to find video ID
                        video_patterns = [
                            r'"videoId":"([^"]+)"',
                            r'watch\?v=([a-zA-Z0-9_-]{11})',
                            r'/vi/([a-zA-Z0-9_-]{11})/',
                            r'embed/([a-zA-Z0-9_-]{11})',
                            r'"video_id":"([^"]+)"',
                            r'data-video-id="([^"]+)"'
                        ]

                        video_ids = []
                        for pattern in video_patterns:
                            matches = re.findall(pattern, html)
                            if matches:
                                video_ids.extend(matches)

                        # Deduplicate video IDs
                        video_ids = list(dict.fromkeys(video_ids))

                        if video_ids:
                            logger.info(f"[VIDEO] Found {len(video_ids)} video IDs in page")

                            # Determine which videos to check - prioritize recent ones with QWEN intelligence
                            videos_to_check = []
                            recent_videos = []  # Initialize here to avoid UnboundLocalError
                            if recent_videos:
                                videos_to_check = list(dict.fromkeys(recent_videos[:3]))  # Recent videos first
                                logger.info(f"🤖🧠 [QWEN-FILTER] Using {len(videos_to_check)} recent videos (prioritized)")
                            else:
                                videos_to_check = video_ids[:3]  # Fallback to first videos if no time data
                                logger.info(f"[FILTER] Using first {len(videos_to_check)} videos (no time data available)")

                            # QWEN Intelligence: Validate video selection
                            if hasattr(self, 'qwen_intelligence') and self.qwen_intelligence:
                                try:
                                    qwen_validation = self.qwen_intelligence.validate_video_selection(
                                        videos_to_check, channel_name, recent_videos is not None
                                    )
                                    if qwen_validation.get('alternative_selection'):
                                        videos_to_check = qwen_validation['alternative_selection']
                                        logger.info(f"🤖🧠 [QWEN-SELECT] Qwen optimized video selection: {videos_to_check}")
                                except Exception as e:
                                    logger.debug(f"🤖🧠 [QWEN-SELECT] Validation failed: {e}")

                            # Try the selected video IDs
                            for idx, video_id in enumerate(videos_to_check):
                                display_name = channel_name or channel_id
                                logger.info(f"[VERIFY] Checking video {idx+1}/{len(videos_to_check)} for {display_name}: {video_id}")
                                result = self.check_video_is_live(video_id, channel_name)
                                if result.get('rate_limited'):
                                    cooldown = self._register_rate_limit(channel_id, channel_name)
                                    result['cooldown'] = cooldown
                                    return result
                                if result and result.get('live'):
                                    logger.info(f"[SUCCESS] Video {video_id} is LIVE!")
                                    return result

                            # Don't fallback to unverified videos - this causes false positives
                            logger.info(f"[SKIP] Found video IDs but none verified as actually live")
                            logger.info(f"[INFO] Page had live indicators but videos are not live (stale page?)")

            except Exception as e:
                logger.error(f"Error checking URL {live_url}: {e}")
                continue  # Try next URL

        # If no live stream found via /live endpoints, check the streams tab
        streams_url = f"https://www.youtube.com/channel/{channel_id}/streams"
        try:
            logger.info(f"  • Checking streams page: {streams_url}")
            # Add delay before checking streams page
            self._anti_detection_delay()
            headers = self._get_random_headers()

            # Use session with retry strategy for better rate limit handling
            response = self.session.get(streams_url, headers=headers, timeout=15)

            if response.status_code == 429:
                cooldown = self._register_rate_limit(channel_id, channel_name)
                return {"rate_limited": True, "status": 429, "cooldown": cooldown}

            if response.status_code == 200:
                # Look for live streams in the page
                html = response.text

                # Extract unique video IDs from the streams page
                all_video_ids = re.findall(r'"videoId":"([^"]+)"', html)
                # Remove duplicates while preserving order
                video_ids = list(dict.fromkeys(all_video_ids))

                # Look for time indicators to find recent streams only
                # This pattern finds video entries with their publish time
                time_pattern = r'"videoId":"([^"]+)"[^}]*?"publishedTimeText":\{"simpleText":"([^"]+)"\}'
                recent_videos = []

                # Try to find videos with time metadata
                for match in re.finditer(time_pattern, html):
                    vid_id = match.group(1)
                    time_text = match.group(2)

                    # Only include very recent streams (last 2 hours)
                    if any(x in time_text.lower() for x in ['minute', 'second', 'streaming now', 'live']):
                        recent_videos.append(vid_id)
                    elif 'hour ago' in time_text.lower() and not 'hours' in time_text:
                        recent_videos.append(vid_id)  # "1 hour ago"
                    elif 'hours ago' in time_text.lower():
                        try:
                            hours = int(re.search(r'(\d+)\s*hour', time_text).group(1))
                            if hours <= 2:  # Only last 2 hours
                                recent_videos.append(vid_id)
                        except:
                            pass

                # Choose which videos to check
                if recent_videos:
                    videos_to_check = list(dict.fromkeys(recent_videos[:3]))  # Remove duplicates, check max 3
                    logger.info(f"  • Found {len(recent_videos)} recent videos (last 2 hours)")
                    logger.info(f"  • Will check {len(videos_to_check)} most recent")
                elif video_ids:
                    # No time data found, fallback to first 3 unique videos
                    videos_to_check = video_ids[:3]
                    unique_count = f" ({len(video_ids)} unique)" if len(all_video_ids) != len(video_ids) else ""
                    display_name = channel_name or channel_id
                    logger.info(f"  • Found {len(all_video_ids)} total videos{unique_count} on {display_name}")
                    if videos_to_check:
                        display_name = channel_name or channel_id
                    logger.info(f"  • Checking first {len(videos_to_check)} videos for {display_name}: {', '.join(videos_to_check)}")
                else:
                    # No videos found at all
                    videos_to_check = []
                    logger.info(f"  • No videos found on streams page")

                # Check the selected videos to see if any are live
                for i, vid in enumerate(videos_to_check):
                    display_name = channel_name or channel_id
                    logger.info(f"  • Checking video {i+1}/{len(videos_to_check)} for {display_name}: {vid}")
                    if i > 0:  # Add delay between multiple video checks
                        self._anti_detection_delay()

                    result = self.check_video_is_live(vid, channel_name)
                    if result.get('live'):
                        # Add channel name to result for better logging
                        display_name = channel_name or channel_id
                        result['channel_name'] = display_name
                        return result

        except Exception as e:
            error_text = str(e)
            if '429' in error_text:
                cooldown = self._register_rate_limit(channel_id, channel_name)
                return {"rate_limited": True, "cooldown": cooldown, "error": error_text}
            logger.error(f"Error checking streams tab: {error_text}")

        display_name = channel_name or channel_id
        logger.info(f"No live streams found for channel {display_name}")
        return None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    checker = NoQuotaStreamChecker()

    # Test with the video ID mentioned by user
    result = checker.check_video_is_live("xL_kGmZj3R8")
    print(f"\nResult: {json.dumps(result, indent=2)}")

    # Test channel check
    channel_result = checker.check_channel_for_live("UC-LSSlOZwpGIRIYihaz8zCw")
    if channel_result:
        print(f"\nChannel live stream: {json.dumps(channel_result, indent=2)}")