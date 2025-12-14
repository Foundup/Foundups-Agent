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
    CHANNEL_HANDLES = {
        'UCklMTNnu5POwRmQsg5JJumA': '@MOVE2JAPAN',
        'UCSNTUXjAgpd4sgWYP0xoJgw': '@UnDaoDu',
        'UC-LSSlOZwpGIRIYihaz8zCw': '@Foundups',
    }
    
    def __init__(self):
        """Initialize vision stream checker."""
        self.driver = None
        self.vision_available = False
        self._check_vision_availability()
    
    def _check_vision_availability(self):
        """
        Check if browser and UI-TARS are available.

        Sprint 3.2: Uses BrowserManager for Edge/Chrome browser selection.
        Fallback chain: Edge → Chrome :9223 → Chrome :9222 → Scraping
        """
        try:
            from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

            # Get browser type preference (Edge or Chrome)
            browser_type = os.getenv("STREAM_BROWSER_TYPE", "edge").lower()
            stream_chrome_port = int(os.getenv("STREAM_CHROME_PORT", os.getenv("FOUNDUPS_CHROME_PORT", "9222")))

            browser_manager = get_browser_manager()

            # Try primary browser type
            try:
                if browser_type == "edge":
                    logger.info(f"[VISION] Attempting Edge browser for vision detection...")
                    self.driver = browser_manager.get_browser(
                        browser_type='edge',
                        profile_name='vision_stream_detection',
                        options={}
                    )
                    self.vision_available = True
                    logger.info(f"[VISION] ✅ Edge browser connected - vision mode available (browser separation active)")
                    return

                elif browser_type == "chrome":
                    logger.info(f"[VISION] Attempting Chrome browser on port {stream_chrome_port}...")
                    # For Chrome, use debug port if different from comment engagement
                    if stream_chrome_port != 9222:
                        logger.info(f"[VISION] Using Chrome on separate port :{ stream_chrome_port}")

                    from selenium import webdriver
                    from selenium.webdriver.chrome.options import Options

                    chrome_options = Options()
                    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{stream_chrome_port}")

                    self.driver = webdriver.Chrome(options=chrome_options)
                    self.vision_available = True
                    logger.info(f"[VISION] ✅ Chrome connected on port {stream_chrome_port} - vision mode available")
                    return

            except Exception as e:
                logger.warning(f"[VISION] {browser_type.title()} browser failed: {e}")

                # Fallback: Try Edge if Chrome was primary
                if browser_type == "chrome":
                    try:
                        logger.info(f"[VISION] Fallback: Attempting Edge browser...")
                        self.driver = browser_manager.get_browser(
                            browser_type='edge',
                            profile_name='vision_stream_detection',
                            options={}
                        )
                        self.vision_available = True
                        logger.info(f"[VISION] ✅ Edge browser connected (fallback) - vision mode available")
                        return
                    except Exception as edge_err:
                        logger.warning(f"[VISION] Edge fallback failed: {edge_err}")

                # Final fallback: Try Chrome on default port
                if browser_type == "edge":
                    try:
                        logger.info(f"[VISION] Fallback: Attempting Chrome on port 9222...")
                        from selenium import webdriver
                        from selenium.webdriver.chrome.options import Options

                        chrome_options = Options()
                        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:9222")

                        self.driver = webdriver.Chrome(options=chrome_options)
                        self.vision_available = True
                        logger.info(f"[VISION] ✅ Chrome connected on port 9222 (fallback) - vision mode available")
                        return
                    except Exception as chrome_err:
                        logger.warning(f"[VISION] Chrome fallback failed: {chrome_err}")

            # All fallbacks exhausted
            raise Exception("All browser options exhausted")

        except Exception as e:
            logger.info(f"[VISION] Browser not available ({e}) - will use scraping fallback")
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
    
    def close(self):
        """Clean up resources."""
        # Don't close driver - we're attached to existing Chrome
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
    Quick function to check channel using vision (with scraping fallback).
    
    Usage:
        result = check_channel_with_vision('UCklMTNnu5POwRmQsg5JJumA', 'Move2Japan')
        if result and result['live']:
            video_id = result['video_id']
    """
    checker = get_vision_stream_checker()
    return checker.check_channel_for_live(channel_id, channel_name)
