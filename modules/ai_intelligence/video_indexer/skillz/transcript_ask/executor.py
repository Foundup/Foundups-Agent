# -*- coding: utf-8 -*-
"""
Transcript Ask SKILLz Executor

Extract full transcripts from YouTube videos using the "Ask" Gemini feature.

WSP Compliance:
    WSP 96: Micro Chain-of-Thought
    WSP 91: DAE Observability
    WSP 72: Module Independence
"""
import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TranscriptResult:
    """Result from transcript extraction."""
    video_id: str
    segments: List[Dict[str, Any]]
    full_text: str
    success: bool
    error: Optional[str] = None
    extraction_method: str = "youtube_ask_gemini"


class TranscriptAskExecutor:
    """
    Execute transcript extraction via YouTube's Ask Gemini feature.
    
    Uses browser automation to:
    1. Navigate to video watch page
    2. Click Ask button
    3. Query for full transcript
    4. Parse Gemini response
    5. Save to video JSON
    """
    
    # Transcript prompt
    TRANSCRIPT_PROMPT = """Give me the complete word-for-word transcript of this video with timestamps.
Format each segment as: [MM:SS] Text spoken
Include everything that was said."""
    
    # DOM selectors
    SELECTORS = {
        "ask_button": [
            'button[aria-label="Ask"]',
            '#flexible-item-buttons yt-button-view-model button',
        ],
        "ask_input": [
            'textarea[placeholder*="Ask"]',
            'input[placeholder*="Ask"]',
            '.gemini-input textarea',
        ],
        "ask_response": [
            '.gemini-response',
            '.ask-response-content',
            '.gemini-chat-response',
        ],
    }
    
    def __init__(
        self,
        driver=None,
        output_dir: str = "memory/video_index",
    ):
        """
        Initialize executor.
        
        Args:
            driver: Selenium WebDriver (if None, will connect to existing)
            output_dir: Directory for video JSONs
        """
        self.driver = driver
        self.output_dir = Path(output_dir)
    
    async def _human_delay(self, base: float = 1.0, variance: float = 0.3):
        """Add human-like delay."""
        import random
        delay = base + random.uniform(-variance, variance)
        await asyncio.sleep(max(0.1, delay))
    
    def _parse_transcript_response(self, response_text: str) -> List[Dict]:
        """
        Parse transcript segments from Gemini response.
        
        Expected format: [MM:SS] Text spoken
        """
        segments = []
        
        # Pattern: [0:00] or [00:00] or [0:00:00]
        pattern = r'\[(\d+:[\d:]+)\]\s*(.+?)(?=\[\d+:[\d:]+\]|$)'
        
        for match in re.finditer(pattern, response_text, re.DOTALL):
            timestamp, text = match.groups()
            segments.append({
                "start_time": timestamp.strip(),
                "text": text.strip(),
            })
        
        # If no timestamp pattern found, try line-by-line
        if not segments:
            lines = response_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('['):
                    segments.append({
                        "start_time": "0:00",
                        "text": line,
                    })
        
        return segments
    
    async def extract_transcript(
        self,
        video_id: str,
        channel: str = "undaodu",
    ) -> TranscriptResult:
        """
        Extract transcript for a video.
        
        Args:
            video_id: YouTube video ID
            channel: Channel folder name
            
        Returns:
            TranscriptResult with segments and full text
        """
        if not self.driver:
            return TranscriptResult(
                video_id=video_id,
                segments=[],
                full_text="",
                success=False,
                error="No browser driver available"
            )
        
        try:
            # Step 1: Navigate to video
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"[TRANSCRIPT-ASK] Navigating to {video_url}")
            self.driver.get(video_url)
            await self._human_delay(5.0, 0.5)
            
            # Step 2: Find and click Ask button
            ask_button = self.driver.execute_script("""
                // Method 1: Precise path
                const flexItems = document.querySelector('#flexible-item-buttons');
                if (flexItems) {
                    const viewModels = flexItems.querySelectorAll('yt-button-view-model');
                    for (let vm of viewModels) {
                        if (vm.textContent.trim().toLowerCase() === 'ask') {
                            const btn = vm.querySelector('button');
                            if (btn) return btn;
                        }
                    }
                }
                // Method 2: aria-label
                return document.querySelector('button[aria-label="Ask"]');
            """)
            
            if not ask_button:
                return TranscriptResult(
                    video_id=video_id,
                    segments=[],
                    full_text="",
                    success=False,
                    error="Ask button not found"
                )
            
            ask_button.click()
            logger.info("[TRANSCRIPT-ASK] Clicked Ask button")
            await self._human_delay(3.0, 0.3)
            
            # Step 3: Find input and send transcript prompt
            ask_input = None
            for selector in self.SELECTORS["ask_input"]:
                try:
                    ask_input = self.driver.find_element("css selector", selector)
                    if ask_input:
                        break
                except:
                    continue
            
            if not ask_input:
                return TranscriptResult(
                    video_id=video_id,
                    segments=[],
                    full_text="",
                    success=False,
                    error="Ask input not found"
                )
            
            ask_input.clear()
            ask_input.send_keys(self.TRANSCRIPT_PROMPT)
            await self._human_delay(1.0, 0.2)
            
            # Submit
            from selenium.webdriver.common.keys import Keys
            ask_input.send_keys(Keys.ENTER)
            logger.info("[TRANSCRIPT-ASK] Sent transcript prompt")
            await self._human_delay(10.0, 1.0)  # Wait for Gemini
            
            # Step 4: Get response
            response_text = ""
            for selector in self.SELECTORS["ask_response"]:
                try:
                    response_el = self.driver.find_element("css selector", selector)
                    response_text = response_el.text
                    if response_text:
                        break
                except:
                    continue
            
            if not response_text:
                # Fallback: get body text
                response_text = self.driver.find_element("css selector", "body").text[-5000:]
            
            # Step 5: Parse transcript
            segments = self._parse_transcript_response(response_text)
            full_text = " ".join(s["text"] for s in segments)
            
            logger.info(f"[TRANSCRIPT-ASK] Extracted {len(segments)} segments")
            
            # Step 6: Save to JSON
            await self._save_to_json(video_id, channel, segments, full_text)
            
            return TranscriptResult(
                video_id=video_id,
                segments=segments,
                full_text=full_text,
                success=True
            )
            
        except Exception as e:
            logger.error(f"[TRANSCRIPT-ASK] Error: {e}")
            return TranscriptResult(
                video_id=video_id,
                segments=[],
                full_text="",
                success=False,
                error=str(e)
            )
    
    async def _save_to_json(
        self,
        video_id: str,
        channel: str,
        segments: List[Dict],
        full_text: str,
    ):
        """Save transcript to video JSON."""
        channel_dir = self.output_dir / channel
        channel_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = channel_dir / f"{video_id}.json"
        
        # Load existing or create new
        if json_path.exists():
            data = json.loads(json_path.read_text(encoding="utf-8"))
        else:
            data = {"video_id": video_id}
        
        # Update audio section
        data.setdefault("audio", {})
        data["audio"]["segments"] = segments
        data["audio"]["full_transcript"] = full_text
        data["audio"]["extraction_method"] = "youtube_ask_gemini"
        data["audio"]["extracted_at"] = datetime.now().isoformat()
        
        # Save
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"[TRANSCRIPT-ASK] Saved to {json_path}")


async def execute_skill(
    video_id: str,
    channel: str = "undaodu",
    driver=None,
) -> Dict[str, Any]:
    """
    Execute the transcript_ask skill.
    
    Args:
        video_id: YouTube video ID
        channel: Channel folder name
        driver: Selenium WebDriver
        
    Returns:
        Skill execution result
    """
    executor = TranscriptAskExecutor(driver=driver)
    result = await executor.extract_transcript(video_id, channel)
    
    return {
        "skill_name": "transcript_ask",
        "video_id": video_id,
        "success": result.success,
        "segments_count": len(result.segments),
        "full_text_length": len(result.full_text),
        "error": result.error,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Transcript Ask SKILLz - Run via integration or test script")
