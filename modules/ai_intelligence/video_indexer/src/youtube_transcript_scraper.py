# -*- coding: utf-8 -*-
"""
YouTube Transcript Scraper - DOM-based transcript extraction.

WSP Compliance:
    WSP 72: Module Independence
    WSP 84: Code Reuse (uses foundups_selenium)

Purpose:
    Scrape verbatim transcripts from YouTube's transcript panel via DOM.
    Free, no API limits, uses YouTube's own ASR captions.
    
    Stacking order:
    1. Gemini API → summaries (semantic)
    2. YouTube DOM → verbatim (free) ← THIS MODULE
    3. Whisper → verbatim (HIGH-tier only)
"""

import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TranscriptSegment:
    """Single transcript segment with timestamp."""
    text: str
    start_time: float  # seconds
    end_time: Optional[float] = None
    

@dataclass 
class YouTubeTranscript:
    """Complete transcript from YouTube DOM."""
    video_id: str
    segments: List[TranscriptSegment]
    full_text: str
    language: str = "en"
    source: str = "youtube_dom"
    scraped_at: str = ""
    

class YouTubeTranscriptScraper:
    """
    Scrape transcripts from YouTube's transcript panel via Selenium.
    
    DOM Flow:
    1. Navigate to youtube.com/watch?v={video_id}
    2. Click description "...more" to expand
    3. Click "Show transcript" button
    4. Scrape transcript segments
    
    Example:
        >>> scraper = YouTubeTranscriptScraper()
        >>> transcript = scraper.scrape_transcript("dQw4w9WgXcQ")
        >>> print(transcript.full_text[:100])
    """
    
    # DOM Selectors (YouTube 2026)
    SELECTORS = {
        # Expand description button
        "expand_description": [
            "tp-yt-paper-button#expand",
            "#description-inline-expander tp-yt-paper-button",
            "#expand.button",
        ],
        # Show transcript button
        "show_transcript": [
            "ytd-video-description-transcript-section-renderer button",
            "button[aria-label='Show transcript']",
            "#primary-button button",
        ],
        # Transcript container
        "transcript_container": [
            "ytd-transcript-renderer",
            "ytd-engagement-panel-section-list-renderer[target-id='engagement-panel-searchable-transcript']",
        ],
        # Individual segments
        "transcript_segments": [
            "ytd-transcript-segment-renderer",
            "div.segment-container",
        ],
        # Timestamp within segment
        "segment_timestamp": [
            ".segment-timestamp",
            "div.segment-timestamp",
        ],
        # Text within segment
        "segment_text": [
            ".segment-text",
            "yt-formatted-string.segment-text",
        ],
    }
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30,
        human_like: bool = True
    ):
        """
        Initialize scraper.
        
        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in seconds
            human_like: Use human-like delays and scrolling
        """
        self.headless = headless
        self.timeout = timeout
        self.human_like = human_like
        self.driver = None
    
    def _get_driver(self):
        """Get or create Selenium driver using existing foundups_selenium infrastructure."""
        if self.driver:
            return self.driver
        
        try:
            # Use existing undetected browser from foundups_selenium (WSP 84 reuse)
            from modules.infrastructure.foundups_selenium.src.undetected_browser import (
                get_undetected_browser
            )
            self.driver = get_undetected_browser(headless=self.headless)
            logger.info("[TRANSCRIPT] Using undetected browser from foundups_selenium")
            
            # Get HumanBehavior instance for anti-detection
            from modules.infrastructure.foundups_selenium.src.human_behavior import HumanBehavior
            self.human = HumanBehavior(self.driver)
            logger.info("[TRANSCRIPT] HumanBehavior initialized")
            
        except ImportError:
            # Fallback to basic selenium
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            
            self.driver = webdriver.Chrome(options=options)
            self.human = None
            logger.info("[TRANSCRIPT] Using basic Chrome driver (no anti-detection)")
        
        self.driver.set_page_load_timeout(self.timeout)
        return self.driver
    
    def _find_element_multi(self, selectors: List[str]):
        """Try multiple selectors until one works."""
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        
        driver = self._get_driver()
        
        for selector in selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except NoSuchElementException:
                continue
        
        return None
    
    def _find_elements_multi(self, selectors: List[str]) -> List:
        """Try multiple selectors for finding multiple elements."""
        from selenium.webdriver.common.by import By
        
        driver = self._get_driver()
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return elements
        
        return []
    
    def _human_delay(self, min_s: float = 0.5, max_s: float = 1.5):
        """Add human-like delay using HumanBehavior if available."""
        if self.human_like:
            if hasattr(self, 'human') and self.human:
                # Use existing HumanBehavior.human_delay (WSP 84 reuse)
                base = (min_s + max_s) / 2
                variance = (max_s - min_s) / (min_s + max_s)
                delay = self.human.human_delay(base, variance)
                time.sleep(delay)
            else:
                import random
                time.sleep(random.uniform(min_s, max_s))
    
    def _parse_timestamp(self, ts_text: str) -> float:
        """Parse timestamp text to seconds."""
        # Handle formats: "0:00", "1:23", "1:23:45"
        ts_text = ts_text.strip()
        parts = ts_text.split(":")
        
        try:
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            else:
                return 0.0
        except ValueError:
            return 0.0
    
    def scrape_transcript(self, video_id: str) -> Optional[YouTubeTranscript]:
        """
        Scrape transcript from YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            YouTubeTranscript or None if unavailable
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        from datetime import datetime
        
        driver = self._get_driver()
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            logger.info(f"[TRANSCRIPT] Navigating to {video_id}")
            driver.get(url)
            self._human_delay(2, 3)
            
            # Wait for video player to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#movie_player"))
            )
            
            # Step 1: Expand description
            expand_btn = self._find_element_multi(self.SELECTORS["expand_description"])
            if expand_btn:
                logger.debug("[TRANSCRIPT] Clicking expand description")
                expand_btn.click()
                self._human_delay()
            
            # Step 2: Click "Show transcript"
            transcript_btn = self._find_element_multi(self.SELECTORS["show_transcript"])
            if not transcript_btn:
                logger.warning(f"[TRANSCRIPT] No transcript button for {video_id}")
                return None
            
            logger.debug("[TRANSCRIPT] Clicking show transcript")
            transcript_btn.click()
            self._human_delay(1, 2)
            
            # Step 3: Wait for transcript panel
            transcript_container = None
            for selector in self.SELECTORS["transcript_container"]:
                try:
                    transcript_container = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not transcript_container:
                logger.warning(f"[TRANSCRIPT] Transcript panel not found for {video_id}")
                return None
            
            # Step 4: Scroll to load all segments
            self._scroll_transcript_panel(transcript_container)
            
            # Step 5: Extract segments
            segments = self._extract_segments()
            
            if not segments:
                logger.warning(f"[TRANSCRIPT] No segments extracted for {video_id}")
                return None
            
            # Build result
            full_text = " ".join(s.text for s in segments)
            
            return YouTubeTranscript(
                video_id=video_id,
                segments=segments,
                full_text=full_text,
                language="en",  # TODO: detect language
                source="youtube_dom",
                scraped_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"[TRANSCRIPT] Error scraping {video_id}: {e}")
            return None
    
    def _scroll_transcript_panel(self, container):
        """Scroll transcript panel to load all segments."""
        driver = self._get_driver()
        
        try:
            # Scroll within the transcript container
            last_height = 0
            for _ in range(10):  # Max scrolls
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight",
                    container
                )
                self._human_delay(0.3, 0.5)
                
                new_height = driver.execute_script(
                    "return arguments[0].scrollHeight",
                    container
                )
                
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Scroll back to top
            driver.execute_script("arguments[0].scrollTop = 0", container)
            
        except Exception as e:
            logger.debug(f"[TRANSCRIPT] Scroll error: {e}")
    
    def _extract_segments(self) -> List[TranscriptSegment]:
        """Extract transcript segments from DOM."""
        segments = []
        
        segment_elements = self._find_elements_multi(self.SELECTORS["transcript_segments"])
        
        for elem in segment_elements:
            try:
                # Get timestamp
                ts_elem = self._find_child(elem, self.SELECTORS["segment_timestamp"])
                ts_text = ts_elem.text if ts_elem else "0:00"
                start_time = self._parse_timestamp(ts_text)
                
                # Get text
                text_elem = self._find_child(elem, self.SELECTORS["segment_text"])
                text = text_elem.text.strip() if text_elem else ""
                
                if text:
                    segments.append(TranscriptSegment(
                        text=text,
                        start_time=start_time
                    ))
                    
            except Exception as e:
                logger.debug(f"[TRANSCRIPT] Segment extraction error: {e}")
                continue
        
        # Calculate end times
        for i, seg in enumerate(segments[:-1]):
            seg.end_time = segments[i + 1].start_time
        
        if segments:
            segments[-1].end_time = segments[-1].start_time + 5  # Estimate
        
        logger.info(f"[TRANSCRIPT] Extracted {len(segments)} segments")
        return segments
    
    def _find_child(self, parent, selectors: List[str]):
        """Find child element using multiple selectors."""
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        
        for selector in selectors:
            try:
                return parent.find_element(By.CSS_SELECTOR, selector)
            except NoSuchElementException:
                continue
        return None
    
    def batch_scrape(
        self,
        video_ids: List[str],
        delay: float = 2.0
    ) -> Dict[str, Optional[YouTubeTranscript]]:
        """
        Scrape transcripts for multiple videos.
        
        Args:
            video_ids: List of video IDs
            delay: Seconds between requests
            
        Returns:
            Dict mapping video_id → YouTubeTranscript or None
        """
        results = {}
        
        for i, vid in enumerate(video_ids):
            logger.info(f"[TRANSCRIPT] Scraping {i+1}/{len(video_ids)}: {vid}")
            results[vid] = self.scrape_transcript(vid)
            
            if i < len(video_ids) - 1:
                time.sleep(delay)
        
        return results
    
    def close(self):
        """Close browser driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


# =============================================================================
# Utility Functions
# =============================================================================

def to_index_format(transcript: YouTubeTranscript) -> Dict[str, Any]:
    """Convert to video_index storage format."""
    return {
        "video_id": transcript.video_id,
        "source": "youtube_dom",
        "language": transcript.language,
        "scraped_at": transcript.scraped_at,
        "segments": [
            {
                "text": s.text,
                "start": s.start_time,
                "end": s.end_time or s.start_time + 5,
            }
            for s in transcript.segments
        ],
        "full_text": transcript.full_text,
    }


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("YouTube Transcript Scraper Test")
    print("=" * 60)
    
    # Test with a known video
    test_id = "8_DUQaqY6Tc"  # Education Singularity
    
    with YouTubeTranscriptScraper(headless=False) as scraper:
        result = scraper.scrape_transcript(test_id)
        
        if result:
            print(f"Video: {result.video_id}")
            print(f"Segments: {len(result.segments)}")
            print(f"First segment: {result.segments[0].text[:50]}...")
            print(f"Full text preview: {result.full_text[:200]}...")
        else:
            print("Transcript not available")
