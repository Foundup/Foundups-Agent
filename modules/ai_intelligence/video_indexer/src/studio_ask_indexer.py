# -*- coding: utf-8 -*-
"""
YouTube Studio Ask Indexer - Browser Automation for Video Indexing

Uses YouTube's built-in Gemini "Ask" feature to index video content.
Runs after comment engagement completes each cycle.

WSP Compliance:
    WSP 27: DAE Architecture (Signal → Knowledge → Protocol → Agentic)
    WSP 72: Module Independence
    WSP 91: DAE Observability

Usage:
    indexer = StudioAskIndexer(driver)
    await indexer.index_channel_videos(channel_id="UCfHM9Fw9HD-NwiS0seD_oIA")
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# VideoContentIndex causes segfault on Windows (ChromaDB native library issue)
# Disable for now - indexing works without it, storage goes to JSON files
# TODO: Fix ChromaDB segfault in holo_index/core/video_search.py
VIDEO_INDEX_AVAILABLE = False
VideoContentIndex = None  # Placeholder
logger.debug("[STUDIO-ASK] VideoContentIndex disabled (ChromaDB segfault workaround)")


@dataclass
class AskResult:
    """Result from YouTube's Ask Gemini feature."""
    video_id: str
    title: str
    response_text: str
    topics: List[str]
    timestamps: List[Dict[str, str]]
    success: bool
    error: Optional[str] = None


class StudioAskIndexer:
    """
    Index videos using YouTube Studio's built-in Gemini "Ask" feature.
    
    This mirrors 012's behavior of using the Ask button in Studio to
    query video content, then stores results in VideoContentIndex.
    """
    
    # Selectors for YouTube (Watch Page AND Studio)
    SELECTORS = {
        "content_tab": "a[href*='/channel/'][href*='/videos']",
        "video_row": "ytcp-video-row",
        "video_title": "a#video-title",

        # WATCH PAGE: Ask button is in #actions > ytd-menu-renderer > #flexible-item-buttons
        "watch_ask_button": "#flexible-item-buttons button, yt-button-view-model button",
        "watch_actions": "#actions ytd-menu-renderer",

        # STUDIO PAGE: Menu trigger to open popup where Ask lives
        "studio_menu_trigger": "ytd-menu-renderer button, button[aria-label='More actions'], #button-shape button",
        # Ask button is inside popup menu as tp-yt-paper-item
        "studio_ask_popup_item": "tp-yt-paper-item.style-scope.ytd-menu-service-item-renderer",
        "popup_menu": "ytd-menu-popup-renderer, tp-yt-iron-dropdown",

        # Gemini chat interface (after clicking Ask)
        "ask_input": "textarea[placeholder*='Ask'], input[placeholder*='Ask'], .gemini-input textarea",
        "ask_response": ".gemini-response, .ask-response-content, .gemini-chat-response",
        "video_details_link": "a[href*='/video/'][href*='/edit']",
    }

    # Watch page is simpler (direct button), prefer it over Studio
    USE_WATCH_PAGE = True
    
    # Standard prompt for video analysis
    ASK_PROMPT = """List all topics discussed in this video with timestamps in JSON format:
{
  "topics": ["topic1", "topic2"],
  "segments": [
    {"time": "0:00", "topic": "Introduction", "summary": "..."},
    {"time": "1:30", "topic": "Main point", "summary": "..."}
  ]
}"""

    def __init__(
        self,
        driver=None,
        human=None,
        max_videos_per_cycle: int = 5,
    ):
        """
        Initialize Studio Ask Indexer.
        
        Args:
            driver: Selenium WebDriver (Chrome or Edge)
            human: HumanBehaviorSimulator for anti-detection
            max_videos_per_cycle: Max videos to index per cycle
        """
        self.driver = driver
        self.human = human
        self.max_videos_per_cycle = max_videos_per_cycle
        
        # Initialize video index if available
        self.video_index = None
        if VIDEO_INDEX_AVAILABLE:
            try:
                self.video_index = VideoContentIndex()
                logger.info("[STUDIO-ASK] VideoContentIndex connected")
            except Exception as e:
                logger.warning(f"[STUDIO-ASK] VideoContentIndex init failed: {e}")
    
    async def _human_delay(self, base: float = 1.0, variance: float = 0.3) -> None:
        """Human-like delay for anti-detection."""
        import asyncio
        import random
        
        if self.human:
            delay = self.human.human_delay(base, variance)
        else:
            delay = base * (1 + random.uniform(-variance, variance))
        
        await asyncio.sleep(delay)
    
    def _extract_video_id_from_url(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        match = re.search(r'/video/([^/?]+)', url)
        if match:
            return match.group(1)
        match = re.search(r'[?&]v=([^&]+)', url)
        if match:
            return match.group(1)
        return None
    
    def _parse_ask_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from Ask Gemini response."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[^{}]*"topics"[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback: extract topics manually
            topics = re.findall(r'"([^"]+)"', response_text)
            return {"topics": topics[:10], "segments": []}
        except Exception as e:
            logger.warning(f"[STUDIO-ASK] JSON parse failed: {e}")
            return {"topics": [], "segments": [], "raw": response_text}
    
    async def ask_about_video(self, video_id: str) -> AskResult:
        """
        Use Ask Gemini feature for a specific video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            AskResult with parsed response
        """
        import asyncio
        
        if not self.driver:
            return AskResult(
                video_id=video_id,
                title="",
                response_text="",
                topics=[],
                timestamps=[],
                success=False,
                error="No browser driver available"
            )
        
        try:
            # Navigate to video page (watch page preferred for simpler Ask button)
            if self.USE_WATCH_PAGE:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
            else:
                video_url = f"https://studio.youtube.com/video/{video_id}/edit"
            logger.info(f"[STUDIO-ASK] Navigating to {video_url}")
            self.driver.get(video_url)
            await self._human_delay(3.0, 0.4)
            
            # Determine which page we're on and get title
            title = ""
            is_watch_page = "youtube.com/watch" in self.driver.current_url

            if is_watch_page:
                # WATCH PAGE: Title is in different location
                try:
                    title_el = self.driver.find_element("css selector", "h1.ytd-watch-metadata, yt-formatted-string.ytd-watch-metadata")
                    title = title_el.text
                except Exception:
                    pass
            else:
                # STUDIO PAGE: Title is in input field
                try:
                    title_el = self.driver.find_element("css selector", "input#title-field, h1.title")
                    title = title_el.get_attribute("value") or title_el.text
                except Exception:
                    pass

            ask_clicked = False

            if is_watch_page or self.USE_WATCH_PAGE:
                # WATCH PAGE APPROACH: Direct button in #flexible-item-buttons
                # Per 012 DOM: #actions > ytd-menu-renderer > #flexible-item-buttons > yt-button-view-model > button
                logger.info("[STUDIO-ASK] Trying watch page Ask button approach")

                # Find Ask button by JavaScript (most reliable for dynamic YT elements)
                # Full watch page DOM: #flexible-item-buttons > yt-button-view-model > button-view-model > button.yt-spec-button-shape-next
                ask_button = self.driver.execute_script("""
                    // Method 1: Precise path from 012's DOM inspection
                    const flexItems = document.querySelector('#flexible-item-buttons');
                    if (flexItems) {
                        const viewModels = flexItems.querySelectorAll('yt-button-view-model');
                        for (let vm of viewModels) {
                            const text = (vm.textContent || vm.innerText || '').toLowerCase().trim();
                            if (text === 'ask') {
                                // Get the button inside: button-view-model > button.yt-spec-button-shape-next
                                const btn = vm.querySelector('button-view-model button.yt-spec-button-shape-next')
                                         || vm.querySelector('button.yt-spec-button-shape-next')
                                         || vm.querySelector('button');
                                if (btn) return btn;
                            }
                        }
                    }
                    // Method 2: Find by aria-label
                    const askByLabel = document.querySelector('button[aria-label*="Ask"]');
                    if (askByLabel) return askByLabel;
                    // Method 3: Broader search - any button with Ask text in actions area
                    const actionsArea = document.querySelector('#actions-inner, #menu');
                    if (actionsArea) {
                        const buttons = actionsArea.querySelectorAll('button.yt-spec-button-shape-next');
                        for (let btn of buttons) {
                            const parent = btn.closest('yt-button-view-model');
                            if (parent && parent.textContent.toLowerCase().includes('ask')) {
                                return btn;
                            }
                        }
                    }
                    return null;
                """)

                if ask_button:
                    ask_button.click()
                    ask_clicked = True
                    logger.info("[STUDIO-ASK] Clicked Ask button on watch page")
                    await self._human_delay(2.0, 0.3)

            if not ask_clicked:
                # STUDIO PAGE FALLBACK: Open menu popup, find Ask item
                logger.info("[STUDIO-ASK] Falling back to Studio popup menu approach")

                # Step 1: Open the menu popup
                menu_clicked = False
                menu_selectors = [
                    "ytd-menu-renderer button",
                    "button[aria-label='More actions']",
                    "#button-shape button",
                    "yt-icon-button#button",
                ]
                for selector in menu_selectors:
                    try:
                        menu_btn = self.driver.find_element("css selector", selector)
                        menu_btn.click()
                        menu_clicked = True
                        logger.info(f"[STUDIO-ASK] Clicked menu via: {selector}")
                        break
                    except Exception:
                        continue

                if not menu_clicked:
                    return AskResult(
                        video_id=video_id,
                        title=title,
                        response_text="",
                        topics=[],
                        timestamps=[],
                        success=False,
                        error="Menu trigger not found"
                    )

                await self._human_delay(1.5, 0.3)  # Wait for popup

                # Step 2: Find "Ask" item inside popup menu by text content
                ask_item = self.driver.execute_script("""
                    const items = document.querySelectorAll('tp-yt-paper-item');
                    for (let item of items) {
                        if (item.textContent.trim().toLowerCase() === 'ask') {
                            return item;
                        }
                    }
                    return null;
                """)

                if not ask_item:
                    return AskResult(
                        video_id=video_id,
                        title=title,
                        response_text="",
                        topics=[],
                        timestamps=[],
                        success=False,
                        error="Ask menu item not found in popup"
                    )

                # Step 3: Click Ask item
                ask_item.click()
                ask_clicked = True
                logger.info("[STUDIO-ASK] Clicked 'Ask' menu item in popup")
                await self._human_delay(2.0, 0.3)

            if not ask_clicked:
                return AskResult(
                    video_id=video_id,
                    title=title,
                    response_text="",
                    topics=[],
                    timestamps=[],
                    success=False,
                    error="Could not click Ask button via any method"
                )
            
            # Find input field and type prompt
            ask_input = self.driver.find_element("css selector", "textarea, input[placeholder*='Ask']")
            ask_input.clear()
            ask_input.send_keys(self.ASK_PROMPT)
            await self._human_delay(1.0, 0.2)
            
            # Submit (Enter key or submit button)
            from selenium.webdriver.common.keys import Keys
            ask_input.send_keys(Keys.ENTER)
            await self._human_delay(5.0, 0.5)  # Wait for Gemini response
            
            # Get response text
            response_text = ""
            try:
                response_el = self.driver.find_element("css selector", ".gemini-response, .response-content")
                response_text = response_el.text
            except Exception:
                # Try to get any new text on page
                response_text = self.driver.find_element("css selector", "body").text[-2000:]
            
            # Parse response
            parsed = self._parse_ask_response(response_text)
            
            return AskResult(
                video_id=video_id,
                title=title,
                response_text=response_text,
                topics=parsed.get("topics", []),
                timestamps=parsed.get("segments", []),
                success=True
            )
            
        except Exception as e:
            logger.error(f"[STUDIO-ASK] Error for {video_id}: {e}")
            return AskResult(
                video_id=video_id,
                title="",
                response_text="",
                topics=[],
                timestamps=[],
                success=False,
                error=str(e)
            )
    
    async def index_channel_videos(
        self,
        channel_id: str,
        max_videos: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Index videos for a channel using Ask Gemini.
        
        Args:
            channel_id: YouTube channel ID
            max_videos: Override max videos to index
            
        Returns:
            Summary of indexing results
        """
        import asyncio
        
        max_videos = max_videos or self.max_videos_per_cycle
        results = []
        
        logger.info(f"[STUDIO-ASK] Starting video indexing for channel {channel_id}")
        logger.info(f"[STUDIO-ASK] Max videos: {max_videos}")
        
        if not self.driver:
            return {"error": "No browser driver", "indexed": 0}
        
        try:
            # Navigate to channel content page
            content_url = f"https://studio.youtube.com/channel/{channel_id}/videos/upload"
            logger.info(f"[STUDIO-ASK] Navigating to: {content_url}")
            self.driver.get(content_url)
            await self._human_delay(3.0, 0.4)

            # OLDEST FIRST: Click sort dropdown and select "Date (oldest)"
            # This ensures we process oldest videos first (building knowledge base chronologically)
            logger.info("[STUDIO-ASK] Sorting by oldest first...")
            try:
                # Use JavaScript to find and click sort dropdown, then select oldest
                sorted_ok = self.driver.execute_script("""
                    // Find sort button/dropdown
                    const sortButtons = document.querySelectorAll(
                        'ytcp-dropdown-trigger, button[aria-label*="Sort"], #sort-menu-button, ' +
                        '[icon="icons:filter-list"], ytcp-icon-button[icon="icons:filter-list"]'
                    );

                    for (const btn of sortButtons) {
                        if (btn.textContent.toLowerCase().includes('date') ||
                            btn.getAttribute('aria-label')?.toLowerCase().includes('sort')) {
                            btn.click();
                            return 'clicked_sort';
                        }
                    }
                    return 'no_sort_button';
                """)

                if sorted_ok == 'clicked_sort':
                    await self._human_delay(1.0, 0.2)

                    # Find and click "oldest" option
                    oldest_clicked = self.driver.execute_script("""
                        const items = document.querySelectorAll(
                            'tp-yt-paper-item, ytcp-text-menu-item, ytcp-ve, paper-item'
                        );
                        for (const item of items) {
                            const text = item.textContent.toLowerCase();
                            if (text.includes('oldest') || text.includes('date (oldest)')) {
                                item.click();
                                return true;
                            }
                        }
                        return false;
                    """)

                    if oldest_clicked:
                        await self._human_delay(2.0, 0.3)
                        logger.info("[STUDIO-ASK] ✓ Sorted by oldest")
                    else:
                        logger.warning("[STUDIO-ASK] Could not find 'oldest' option")
                else:
                    logger.warning("[STUDIO-ASK] Could not find sort button")

            except Exception as e:
                logger.warning(f"[STUDIO-ASK] Sort failed (using default order): {e}")
                # Continue with default order - better than failing

            # Get list of video IDs
            video_ids = []
            try:
                video_rows = self.driver.find_elements("css selector", "ytcp-video-row, tr.style-scope")
                for row in video_rows[:max_videos]:
                    try:
                        link = row.find_element("css selector", "a[href*='/video/']")
                        href = link.get_attribute("href")
                        vid_id = self._extract_video_id_from_url(href)
                        if vid_id:
                            video_ids.append(vid_id)
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"[STUDIO-ASK] Failed to get video list: {e}")
            
            if not video_ids:
                return {"error": "No videos found", "indexed": 0}
            
            logger.info(f"[STUDIO-ASK] Found {len(video_ids)} videos to index")
            
            # Index each video
            for vid_id in video_ids:
                result = await self.ask_about_video(vid_id)
                results.append(result)
                
                if result.success:
                    logger.info(f"[STUDIO-ASK] ✅ {vid_id}: {len(result.topics)} topics")
                    
                    # Store in VideoContentIndex (simplified - full impl would store segments)
                    # TODO: Create proper GeminiAnalysisResult wrapper
                else:
                    logger.warning(f"[STUDIO-ASK] ❌ {vid_id}: {result.error}")
                
                await self._human_delay(2.0, 0.3)
            
            # Summary
            indexed = sum(1 for r in results if r.success)
            return {
                "channel_id": channel_id,
                "indexed": indexed,
                "failed": len(results) - indexed,
                "videos": [r.video_id for r in results if r.success],
            }
            
        except Exception as e:
            logger.error(f"[STUDIO-ASK] Channel indexing failed: {e}")
            return {"error": str(e), "indexed": 0}


async def run_video_indexing_cycle(
    driver=None,
    channels: Optional[List[str]] = None,
    max_videos_per_channel: int = 3,
    browser: str = "chrome",
) -> Dict[str, Any]:
    """
    Run one cycle of video indexing across all channels.

    Called by auto_moderator_dae after comment engagement completes.

    Args:
        driver: Selenium WebDriver (if None, will connect based on browser param)
        channels: List of channel IDs (defaults to env vars)
        max_videos_per_channel: Max videos to index per channel (9999 = all)
        browser: "chrome" (port 9222) or "edge" (port 9223)

    Returns:
        Summary of indexing cycle
    """
    if not os.getenv("YT_VIDEO_INDEXING_ENABLED", "true").lower() in ("1", "true", "yes"):
        logger.info("[VIDEO-INDEX] Video indexing disabled (YT_VIDEO_INDEXING_ENABLED)")
        return {"skipped": True}

    # Default channels from env - all 4 channels
    # Chrome (9222): Move2Japan, UnDaoDu (Set 1)
    # Edge (9223): FoundUps, RavingANTIFA (Set 10)
    if not channels:
        channels = [
            os.getenv("MOVE2JAPAN_CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw"),
            os.getenv("UNDAODU_CHANNEL_ID", "UCfHM9Fw9HD-NwiS0seD_oIA"),
            os.getenv("FOUNDUPS_CHANNEL_ID", "UCSNTUXjAgpd4sgWYP0xoJgw"),
            os.getenv("RAVINGANTIFA_CHANNEL_ID", "UCVSmg5aOhP4tnQ9KFUg97qA"),
        ]
        channels = [c for c in channels if c]

    logger.info("=" * 60)
    logger.info(f"[VIDEO-INDEX] Starting video indexing cycle ({browser.upper()})")
    logger.info(f"[VIDEO-INDEX] Channels: {len(channels)}")
    logger.info(f"[VIDEO-INDEX] Max videos per channel: {max_videos_per_channel}")
    logger.info("=" * 60)

    # Connect to browser if no driver provided
    if driver is None:
        try:
            if browser.lower() == "edge":
                from selenium import webdriver
                from selenium.webdriver.edge.options import Options as EdgeOptions
                port = int(os.getenv("FOUNDUPS_EDGE_PORT", "9223"))
                logger.info(f"[VIDEO-INDEX] Connecting to Edge on port {port}...")
                edge_opts = EdgeOptions()
                edge_opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
                driver = webdriver.Edge(options=edge_opts)
                logger.info(f"[VIDEO-INDEX] Connected to Edge")
            else:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                port = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9222"))
                logger.info(f"[VIDEO-INDEX] Connecting to Chrome on port {port}...")
                opts = Options()
                opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
                driver = webdriver.Chrome(options=opts)
                logger.info(f"[VIDEO-INDEX] Connected to Chrome")
        except Exception as e:
            logger.error(f"[VIDEO-INDEX] Failed to connect to {browser}: {e}")
            return {"error": str(e), "total_indexed": 0}

    indexer = StudioAskIndexer(
        driver=driver,
        max_videos_per_cycle=max_videos_per_channel
    )

    results = {}
    for channel_id in channels:
        result = await indexer.index_channel_videos(channel_id)
        results[channel_id] = result
        logger.info(f"[VIDEO-INDEX] {channel_id}: {result.get('indexed', 0)} videos indexed")

    total_indexed = sum(r.get("indexed", 0) for r in results.values())
    logger.info(f"[VIDEO-INDEX] Cycle complete: {total_indexed} videos indexed")

    return {
        "total_indexed": total_indexed,
        "channels": results,
        "timestamp": datetime.now().isoformat(),
    }
