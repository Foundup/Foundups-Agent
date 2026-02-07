"""
Vision Stream Checker - UI-TARS powered live stream detection
=============================================================

Uses foundups_vision (UI-TARS) to visually detect live streams.
Falls back to HTTP scraping if vision unavailable.

WSP References:
- WSP 77: Multi-tier Vision (UI-TARS primary, scraping fallback)
- WSP 27: DAE Architecture
- WSP 3: Functional distribution (uses infrastructure/foundups_vision)

0102 Directive: See the stream, know the stream.
"""

import asyncio
import logging
import os
import re
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class VisionStreamChecker:
    """
    UI-TARS powered live stream detection.
    
    Primary: Chrome + UI-TARS vision (authenticated, CAPTCHA immune)
    Fallback: HTTP scraping (when Chrome unavailable)
    
    Integration: Called by StreamResolver before HTTP scraping.
    """
    
    # Channel handles to check
    # FIXED 2025-12-31: Corrected channel ID to handle mapping
    CHANNEL_HANDLES = {
        'UC-LSSlOZwpGIRIYihaz8zCw': '@MOVE2JAPAN',   # Move2Japan (primary)
        'UCklMTNnu5POwRmQsg5JJumA': '@MOVE2JAPAN',   # Move2Japan (alternate)
        'UCfHM9Fw9HD-NwiS0seD_oIA': '@UnDaoDu',      # UnDaoDu
        'UCSNTUXjAgpd4sgWYP0xoJgw': '@FoundUps',     # FoundUps
        'UCVSmg5aOhP4tnQ9KFUg97qA': '@ravingantifa', # RavingANTIFA
    }
    
    def __init__(self):
        """Initialize vision stream checker."""
        self.driver = None
        self.vision_available = False
        self._check_vision_availability()
    
    def _check_vision_availability(self):
        """
        Check if browser and UI-TARS are available.

        ARCHITECTURE (2026-02-06):
        - Vision uses EDGE ONLY (port 9223)
        - Chrome (port 9222) is RESERVED for comment engagement
        - NO Chrome fallback - prevents browser hijacking

        If Edge unavailable, vision falls back to HTTP scraping.
        """
        try:
            from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

            browser_manager = get_browser_manager()

            # EDGE ONLY - Chrome is reserved for comment engagement
            logger.info("[VISION] Attempting Edge browser (Chrome reserved for comments)...")
            try:
                self.driver = browser_manager.get_browser(
                    browser_type='edge',
                    profile_name='vision_stream_detection',
                    options={},
                    dae_name='youtube_vision_dae',
                )
                self.vision_available = True
                logger.info("[VISION] ✅ Edge browser connected - vision mode available")
                logger.info("[VISION] Chrome (9222) remains available for comment engagement")
                return

            except Exception as e:
                logger.warning(f"[VISION] Edge browser failed: {e}")
                # NO Chrome fallback - Chrome is reserved for comments
                logger.info("[VISION] Edge unavailable - vision will use HTTP scraping")
                logger.info("[VISION] Chrome NOT used for vision (reserved for comment engagement)")
                raise Exception("Edge not available, Chrome reserved for comments")

        except Exception as e:
            logger.info(f"[VISION] Browser not available ({e}) - will use HTTP scraping")
            self.vision_available = False
            self.driver = None
    
    def check_channel_for_live(self, channel_id: str, channel_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Check if channel has live stream using vision (primary) or scraping (fallback).
        
        Args:
            channel_id: YouTube channel ID
            channel_name: Display name for logging
            
        Returns:
            Dict with live stream info if found, None otherwise
        """
        display_name = channel_name or channel_id
        
        # PRIMARY: Try vision-based detection
        if self.vision_available and self.driver:
            logger.info(f"[VISION] Checking {display_name} with UI-TARS vision...")
            result = self._check_with_vision(channel_id, channel_name)
            if result:
                return result
            logger.info(f"[VISION] No live stream detected visually for {display_name}")
        
        # FALLBACK: Use HTTP scraping
        logger.info(f"[SCRAPE] Falling back to HTTP scraping for {display_name}")
        return self._check_with_scraping(channel_id, channel_name)
    
    def _check_with_vision(self, channel_id: str, channel_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Use Chrome + visual inspection to detect live stream.
        
        CAPTCHA immune since browser is authenticated!
        """
        try:
            # Get channel handle
            handle = self.CHANNEL_HANDLES.get(channel_id, f"channel/{channel_id}")
            if not handle.startswith('@') and not handle.startswith('channel/'):
                handle = f"@{handle}"
            
            # Navigate to channel's live page
            live_url = f"https://www.youtube.com/{handle}/live"
            logger.info(f"[VISION] Navigating to: {live_url}")
            
            # Store current URL to restore later (CRITICAL: Don't hijack Studio inbox!)
            original_url = self.driver.current_url

            try:
                self.driver.get(live_url)

                # Wait for page load
                import time
                time.sleep(3)

                # Check if redirected to a video (means live stream exists!)
                current_url = self.driver.current_url
                logger.info(f"[VISION] Current URL: {current_url}")

                # If URL contains watch?v= we found a live stream!
                if 'watch?v=' in current_url:
                    video_id = self._extract_video_id(current_url)
                    if video_id:
                        logger.info(f"[VISION] LIVE STREAM DETECTED: {video_id}")

                        # Get title from page
                        title = self._get_video_title()

                        return {
                            'live': True,
                            'video_id': video_id,
                            'channel_name': channel_name,
                            'title': title or f"Live on {channel_name}",
                            'source': 'vision',
                            'method': 'ui_tars_chrome'
                        }

                # Check for LIVE badge on page using DOM
                is_live = self._check_live_indicators_dom()
                if is_live:
                    video_id = self._extract_video_id_from_page()
                    if video_id:
                        logger.info(f"[VISION] LIVE BADGE DETECTED: {video_id}")
                        return {
                            'live': True,
                            'video_id': video_id,
                            'channel_name': channel_name,
                            'source': 'vision_dom',
                            'method': 'live_badge_detection'
                        }

                # OCCUS (UI-TARS): Channel-home featured content fallback.
                # Some channel /live pages do not redirect even when a live tile exists on the home feed.
                home_live = self._extract_live_video_from_channel_home(handle=handle)
                if home_live and home_live.get('video_id'):
                    logger.info(f"[VISION] HOME-FEED LIVE TILE DETECTED: {home_live['video_id']}")
                    return {
                        'live': True,
                        'video_id': home_live['video_id'],
                        'channel_name': channel_name,
                        'title': home_live.get('title') or f"Live on {channel_name}",
                        'source': 'vision_channel_home',
                        'method': home_live.get('method', 'featured_dom_probe'),
                        'evidence': home_live.get('evidence', {})
                    }

                return None

            finally:
                # ALWAYS restore original URL (don't hijack Studio inbox!)
                if original_url and 'studio.youtube.com' in original_url:
                    logger.info(f"[VISION] Restoring original Studio URL: {original_url[:60]}...")
                    self.driver.get(original_url)
                    time.sleep(2)  # Allow Studio to reload
            
        except Exception as e:
            logger.warning(f"[VISION] Vision check failed: {e}")
            return None
    
    def _check_live_indicators_dom(self) -> bool:
        """Check for LIVE indicators using DOM inspection."""
        try:
            # Look for LIVE badge in DOM
            live_indicators = self.driver.execute_script("""
                // Check for various LIVE indicators
                const indicators = {
                    liveBadge: document.querySelector('[aria-label*="LIVE"]') !== null,
                    liveText: document.body.innerHTML.includes('>LIVE<'),
                    watchingNow: document.body.innerHTML.includes('watching now'),
                    liveBroadcast: document.body.innerHTML.includes('BADGE_STYLE_TYPE_LIVE_NOW'),
                    // YouTube thumbnail overlay renderer is often the strongest DOM signal.
                    liveOverlayRenderer: document.querySelector('ytd-thumbnail-overlay-time-status-renderer[overlay-style="LIVE"]') !== null
                };
                return indicators;
            """)
            
            if live_indicators:
                has_live = any(live_indicators.values())
                if has_live:
                    logger.info(f"[VISION-DOM] Live indicators: {live_indicators}")
                return has_live
                
        except Exception as e:
            logger.debug(f"[VISION-DOM] Check failed: {e}")
        
        return False

    def _extract_live_video_from_channel_home(self, handle: str) -> Optional[Dict[str, Any]]:
        """
        Navigate to channel home and attempt to detect a LIVE tile + extract its video_id.

        This is an OCCUS addition based on a concrete DOM anchor in channel featured content.
        We keep it resilient by checking multiple selectors rather than a single brittle path.
        """
        if not self.driver:
            return None

        try:
            home_url = f"https://www.youtube.com/{handle}"
            logger.info(f"[VISION] Channel-home fallback probe: {home_url}")
            self.driver.get(home_url)

            import time
            time.sleep(3)

            probe = self.driver.execute_script(r"""
                const result = {
                  live: false,
                  videoId: null,
                  title: null,
                  evidence: {}
                };

                // Primary anchor (user-provided neighborhood): featured content renderer.
                const featured = document.querySelector('ytd-channel-featured-content-renderer');
                result.evidence.hasFeaturedRenderer = !!featured;

                // Prefer explicit live overlay renderer (strong signal).
                const liveOverlay = document.querySelector('ytd-thumbnail-overlay-time-status-renderer[overlay-style="LIVE"]');
                result.evidence.hasLiveOverlay = !!liveOverlay;

                // A robust way to find the watch link near a live tile:
                // locate any anchor with id=thumbnail pointing to /watch?v= and validate it has live context.
                const candidateLinks = Array.from(document.querySelectorAll('a#thumbnail[href*="watch?v="]'));
                result.evidence.candidateThumbnailLinks = candidateLinks.length;

                function extractVideoIdFromHref(href) {
                  const m = href.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
                  return m ? m[1] : null;
                }

                // Heuristic: if we have a live overlay, walk up and find the nearest thumbnail link.
                if (liveOverlay) {
                  const container = liveOverlay.closest('ytd-thumbnail, ytd-video-renderer, ytd-grid-video-renderer, ytd-rich-item-renderer, ytd-rich-grid-media');
                  const link = container ? container.querySelector('a#thumbnail[href*="watch?v="]') : null;
                  result.evidence.liveOverlayContainer = container ? container.tagName : null;
                  result.evidence.liveOverlayHasLink = !!link;
                  if (link) {
                    const vid = extractVideoIdFromHref(link.getAttribute('href') || '');
                    if (vid) {
                      result.live = true;
                      result.videoId = vid;
                    }
                  }
                }

                // Fallback: scan thumbnails and require at least one "LIVE" semantic indicator in the tile.
                if (!result.live && candidateLinks.length) {
                  for (const link of candidateLinks.slice(0, 30)) {
                    const tile = link.closest('ytd-rich-item-renderer, ytd-video-renderer, ytd-grid-video-renderer, ytd-rich-grid-media, ytd-compact-video-renderer');
                    if (!tile) continue;

                    const tileHtml = tile.innerHTML || '';
                    const hasLiveText = tileHtml.includes('>LIVE<') || tileHtml.includes('"text":"LIVE"') || tileHtml.includes('BADGE_STYLE_TYPE_LIVE_NOW');
                    const hasWatchingNow = tileHtml.toLowerCase().includes('watching now');
                    const hasOverlay = tile.querySelector('ytd-thumbnail-overlay-time-status-renderer[overlay-style="LIVE"]') !== null;
                    if (!(hasLiveText || hasWatchingNow || hasOverlay)) continue;

                    const vid = extractVideoIdFromHref(link.getAttribute('href') || '');
                    if (vid) {
                      result.live = true;
                      result.videoId = vid;
                      result.evidence.tileMatched = tile.tagName;
                      result.evidence.tileHasOverlay = hasOverlay;
                      result.evidence.tileHasLiveText = hasLiveText;
                      result.evidence.tileHasWatchingNow = hasWatchingNow;
                      break;
                    }
                  }
                }

                // Title best-effort (optional)
                if (result.live) {
                  const titleEl = document.querySelector('meta[property="og:title"]');
                  if (titleEl && titleEl.content) result.title = titleEl.content;
                }

                return result;
            """)

            if not isinstance(probe, dict):
                return None
            if not probe.get('live') or not probe.get('videoId'):
                return None

            return {
                "video_id": probe.get("videoId"),
                "title": probe.get("title"),
                "method": "channel_home_dom",
                "evidence": probe.get("evidence", {}),
            }
        except Exception as e:
            logger.debug(f"[VISION] Channel-home probe failed: {e}")
            return None
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'/v/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _extract_video_id_from_page(self) -> Optional[str]:
        """Extract video ID from current page DOM."""
        try:
            video_id = self.driver.execute_script("""
                // Try multiple methods to get video ID
                // Method 1: URL
                const urlMatch = window.location.href.match(/watch\\?v=([a-zA-Z0-9_-]{11})/);
                if (urlMatch) return urlMatch[1];
                
                // Method 2: Canonical link
                const canonical = document.querySelector('link[rel="canonical"]');
                if (canonical) {
                    const match = canonical.href.match(/watch\\?v=([a-zA-Z0-9_-]{11})/);
                    if (match) return match[1];
                }
                
                // Method 3: Meta tags
                const ogUrl = document.querySelector('meta[property="og:url"]');
                if (ogUrl) {
                    const match = ogUrl.content.match(/watch\\?v=([a-zA-Z0-9_-]{11})/);
                    if (match) return match[1];
                }
                
                return null;
            """)
            return video_id
        except:
            return None
    
    def _get_video_title(self) -> Optional[str]:
        """Get video title from current page."""
        try:
            title = self.driver.execute_script("""
                // Try to get video title
                const titleEl = document.querySelector('h1.ytd-video-primary-info-renderer');
                if (titleEl) return titleEl.textContent.trim();
                
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle) return ogTitle.content;
                
                return document.title.replace(' - YouTube', '').trim();
            """)
            return title
        except:
            return None
    
    def _check_with_scraping(self, channel_id: str, channel_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Fallback: Use HTTP scraping to detect live stream.
        
        Called when Chrome/vision unavailable.
        """
        try:
            # Import the existing scraping checker
            from .no_quota_stream_checker import NoQuotaStreamChecker
            
            scraper = NoQuotaStreamChecker()
            result = scraper.check_channel_for_live(channel_id, channel_name)
            
            if result and result.get('live'):
                result['source'] = 'scraping_fallback'
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"[SCRAPE] Fallback scraping failed: {e}")
            return None
    
    def verify_video_is_live(self, video_id: str) -> Dict[str, Any]:
        """
        VERIFICATION ONLY: Check if a specific video is currently live.

        This method is for LIVE CHAT verification - checking if a known stream
        is still active. It does NOT discover streams (no channel navigation).

        Args:
            video_id: YouTube video ID to verify

        Returns:
            {
                'live': bool,
                'video_id': str,
                'title': str (if live),
                'source': 'vision_verify'
            }
        """
        if not self.vision_available or not self.driver:
            logger.info("[VISION-VERIFY] Vision not available, using HTTP fallback")
            return self._verify_with_http(video_id)

        try:
            # Go directly to the video (NO channel navigation!)
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"[VISION-VERIFY] Checking video: {video_id}")

            # Store current URL to restore
            original_url = self.driver.current_url

            try:
                self.driver.get(watch_url)

                import time
                time.sleep(2)  # Quick check, not full page load

                # Check for LIVE indicators
                is_live = self._check_live_indicators_dom()

                if is_live:
                    title = self._get_video_title()
                    logger.info(f"[VISION-VERIFY] Video {video_id} is LIVE")
                    return {
                        'live': True,
                        'video_id': video_id,
                        'title': title or 'Live Stream',
                        'source': 'vision_verify'
                    }
                else:
                    logger.info(f"[VISION-VERIFY] Video {video_id} is NOT live")
                    return {
                        'live': False,
                        'video_id': video_id,
                        'source': 'vision_verify'
                    }

            finally:
                # Restore original URL if it was Studio
                if original_url and 'studio.youtube.com' in original_url:
                    logger.info(f"[VISION-VERIFY] Restoring Studio URL")
                    self.driver.get(original_url)
                    time.sleep(1)

        except Exception as e:
            logger.warning(f"[VISION-VERIFY] Vision verify failed: {e}")
            return self._verify_with_http(video_id)

    def _verify_with_http(self, video_id: str) -> Dict[str, Any]:
        """HTTP fallback for video verification."""
        try:
            from .no_quota_stream_checker import NoQuotaStreamChecker
            scraper = NoQuotaStreamChecker()
            result = scraper.check_video_is_live(video_id)
            if result and result.get('live'):
                return {
                    'live': True,
                    'video_id': video_id,
                    'title': result.get('title', 'Live Stream'),
                    'source': 'http_verify'
                }
            return {
                'live': False,
                'video_id': video_id,
                'source': 'http_verify'
            }
        except Exception as e:
            logger.error(f"[HTTP-VERIFY] Fallback failed: {e}")
            return {'live': False, 'video_id': video_id, 'source': 'error'}

    def close(self):
        """Clean up resources."""
        # Don't close driver - we're attached to existing browser
        self.driver = None
        self.vision_available = False


# Singleton instance
_vision_checker_instance = None


def get_vision_stream_checker() -> VisionStreamChecker:
    """Get or create singleton VisionStreamChecker."""
    global _vision_checker_instance
    if _vision_checker_instance is None:
        _vision_checker_instance = VisionStreamChecker()
    return _vision_checker_instance


def check_channel_with_vision(channel_id: str, channel_name: str = None) -> Optional[Dict[str, Any]]:
    """
    DEPRECATED: Do not use for stream discovery - navigates browser.

    Use NO-QUOTA (HTTP scraping) for stream discovery instead.
    Use verify_video_with_vision() for verification of known video IDs.
    """
    logger.warning("[VISION] check_channel_with_vision is DEPRECATED - use NO-QUOTA for discovery")
    logger.warning("[VISION] This method navigates the browser and disrupts comment engagement")
    # Return None to force fallback to NO-QUOTA
    return None


def verify_video_with_vision(video_id: str) -> Dict[str, Any]:
    """
    VERIFICATION ONLY: Check if a specific video is currently live.

    For LIVE CHAT use - verifying a known stream is still active.
    Does NOT navigate to channels (no browser hijacking).
    Uses Edge only (Chrome reserved for comment engagement).

    Usage:
        result = verify_video_with_vision('dQw4w9WgXcQ')
        if result['live']:
            print(f"Stream still active: {result['title']}")

    Args:
        video_id: YouTube video ID to verify

    Returns:
        {'live': bool, 'video_id': str, 'title': str, 'source': str}
    """
    checker = get_vision_stream_checker()
    return checker.verify_video_is_live(video_id)
