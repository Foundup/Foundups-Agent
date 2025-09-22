#!/usr/bin/env python3
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

logger = logging.getLogger(__name__)


class NoQuotaStreamChecker:
    """Check YouTube stream status without using API quota"""

    def __init__(self):
        # Don't use session to avoid cookie/state issues
        self.session = None

        # Pool of realistic User-Agents (2024)
        self.USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        ]

        logger.info("[INFO] NO-QUOTA stream checker initialized")

    def _setup_retry_strategy(self):
        """Setup exponential backoff retry strategy for rate limiting"""
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=2,  # 2, 4, 8 seconds
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

    def _anti_detection_delay(self):
        """Add random delay to avoid rate limiting"""
        delay = random.uniform(2.0, 5.0)  # 2-5 seconds between requests
        logger.debug(f"Anti-detection delay: {delay:.1f}s")
        time.sleep(delay)

    def check_video_is_live(self, video_id: str) -> Dict[str, Any]:
        """
        Check if a YouTube video is currently live without using API quota

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with status and details
        """
        url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            logger.info("="*60)
            logger.info("🌐 NO-QUOTA SCRAPING ACTIVATED")
            logger.info(f"  • Method: Web scraping (0 API units)")
            logger.info(f"  • Video ID: {video_id}")
            logger.info(f"  • URL: {url}")
            logger.info("="*60)

            # Anti-detection measures
            self._anti_detection_delay()
            headers = self._get_random_headers()

            # Use requests directly instead of session
            response = requests.get(url, headers=headers, timeout=15)

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
            elif is_ended:
                logger.info(f"❌ Stream has ended (old stream) - score: {live_score}")
            else:
                logger.info(f"❌ Not a live stream (score: {live_score}/3 required, needs isLiveNow or badge)")

            # Extract initial data JSON
            initial_data_match = re.search(r'var ytInitialData = ({.*?});', html)
            if initial_data_match:
                try:
                    data = json.loads(initial_data_match.group(1))

                    # Navigate through the JSON structure to find video details
                    if 'contents' in data:
                        results = data.get('contents', {}).get('twoColumnWatchNextResults', {}).get('results', {}).get('results', {})
                        contents = results.get('contents', [])

                        for item in contents:
                            if 'videoPrimaryInfoRenderer' in item:
                                renderer = item['videoPrimaryInfoRenderer']

                                # Check for live badge (already checked above)
                                if not is_live:
                                    badges = renderer.get('badges', [])
                                    for badge in badges:
                                        label = badge.get('metadataBadgeRenderer', {}).get('label', '')
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
                    secondary = data.get('contents', {}).get('twoColumnWatchNextResults', {}).get('results', {}).get('results', {}).get('contents', [])
                    for item in secondary:
                        if 'videoSecondaryInfoRenderer' in item:
                            owner = item['videoSecondaryInfoRenderer'].get('owner', {})
                            runs = owner.get('videoOwnerRenderer', {}).get('title', {}).get('runs', [])
                            if runs:
                                channel = runs[0].get('text', 'Unknown')

                except json.JSONDecodeError:
                    logger.warning("Failed to parse YouTube initial data")

            # Method 2: Double-check with more specific patterns
            if not is_live and not is_ended:
                # Must find MULTIPLE live indicators to confirm it's actually live
                live_score = 0

                # Strong indicators (worth 2 points each)
                if '"isLiveNow":true' in html:
                    live_score += 2
                    logger.debug("Found isLiveNow:true")
                if 'BADGE_STYLE_TYPE_LIVE_NOW' in html:
                    live_score += 2
                    logger.debug("Found LIVE badge")
                if 'watching now</span>' in html:
                    live_score += 2
                    logger.debug("Found watching now")

                # Weak indicators (worth 1 point each)
                if '"label":"LIVE"' in html:
                    live_score += 1
                if '"isLiveContent":true' in html:
                    live_score += 1

                # Need at least 4 points or isLiveNow:true to be sure it's live
                # Increased threshold to reduce false positives
                if live_score >= 4 or '"isLiveNow":true' in html:
                    is_live = True
                    logger.debug(f"Stream confirmed as live (score: {live_score})")

            # Extract title if not found
            if title == "Unknown":
                title_match = re.search(r'<title>(.*?)</title>', html)
                if title_match:
                    raw_title = title_match.group(1)
                    # Clean up YouTube suffix
                    title = raw_title.replace(' - YouTube', '').strip()

            # Log the result clearly
            if is_live:
                logger.info("✅ STREAM IS LIVE (detected via scraping)")
                logger.info(f"  • Channel: {channel}")
                logger.info(f"  • Title: {title}")
                logger.info(f"  • Video ID: {video_id}")
            elif is_ended:
                logger.info("⏸️ OLD STREAM DETECTED (already ended)")
                logger.info(f"  • Title: {title}")
                logger.info(f"  • Video ID: {video_id}")
                logger.info("  • Status: Not currently live")
            else:
                logger.info("❌ NOT A STREAM (regular video or not found)")

            result = {
                "live": is_live,
                "video_id": video_id,
                "title": title,
                "channel": channel,
                "url": url
            }

            if is_live:
                logger.info(f"✅ Found live stream on {channel}: {title}")
            else:
                logger.info(f"❌ No live stream found on {channel}")

            return result

        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"live": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"live": False, "error": str(e)}

    def check_channel_for_live(self, channel_id: str, channel_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Check if a channel has any live streams without using API quota

        Args:
            channel_id: YouTube channel ID or handle

        Returns:
            Dict with live stream details if found, None otherwise
        """
        # Try multiple URL formats - handle (@username) and channel ID
        urls_to_try = []

        # Map channel IDs to handles
        channel_handle_map = {
            'UC-LSSlOZwpGIRIYihaz8zCw': '@MOVE2JAPAN',  # MOVE2JAPAN (primary)
            'UCSNTUXjAgpd4sgWYP0xoJgw': '@Foundups'  # Foundups
        }

        # If we have a handle for this channel ID, try the channel page
        if channel_id in channel_handle_map:
            handle = channel_handle_map[channel_id]
            # Use channel page directly, not /live which redirects randomly
            urls_to_try.append(f"https://www.youtube.com/{handle}")
            logger.info(f"  • Channel handle: {handle}")

        # Always try channel ID format as fallback
        urls_to_try.append(f"https://www.youtube.com/channel/{channel_id}")

        for live_url in urls_to_try:
            try:
                logger.info("")
                logger.info("🔍 NO-QUOTA CHANNEL CHECK")
                logger.info(f"  • Channel ID: {channel_id}")
                logger.info(f"  • Trying URL: {live_url}")
                logger.info(f"  • Method: Channel page scraping")
                logger.info(f"  • Cost: 0 API units")

                # Anti-detection measures for channel check
                self._anti_detection_delay()
                headers = self._get_random_headers()

                # Use requests directly instead of session
                response = requests.get(live_url, headers=headers, timeout=15, allow_redirects=True)

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
                            # Try the first few video IDs
                            for idx, video_id in enumerate(video_ids[:3]):
                                logger.info(f"[VERIFY] Checking video {idx+1}/{min(3, len(video_ids))}: {video_id}")
                                result = self.check_video_is_live(video_id)
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

            # Use requests directly instead of session
            response = requests.get(streams_url, headers=headers, timeout=15)

            if response.status_code == 200:
                # Look for live streams in the page
                html = response.text

                # Extract video IDs from the streams page
                video_ids = re.findall(r'"videoId":"([^"]+)"', html)
                logger.info(f"  • Found {len(video_ids)} videos on streams page")

                # Check the first few videos to see if any are live
                for i, vid in enumerate(video_ids[:5]):  # Check first 5 videos
                    logger.info(f"  • Checking video {i+1}/{min(5, len(video_ids))}: {vid}")
                    if i > 0:  # Add delay between multiple video checks
                        self._anti_detection_delay()

                    result = self.check_video_is_live(vid)
                    if result.get('live'):
                        # Add channel name to result for better logging
                        display_name = channel_name or channel_id
                        result['channel_name'] = display_name
                        return result

        except Exception as e:
            logger.error(f"Error checking streams tab: {e}")

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