"""
News Ticker for antifaFM OBS Stream (Layer 2.5C)

Displays scrolling headlines at the bottom of the stream.
Headlines are loaded from data/headlines.json and can be updated by mods.

Usage:
    python -m antifafm_broadcaster.src.news_ticker
    python -m antifafm_broadcaster.src.news_ticker --interval 15
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Paths
MODULE_ROOT = Path(__file__).parent.parent
HEADLINES_FILE = MODULE_ROOT / "data" / "headlines.json"

# OBS Text source settings
TICKER_SOURCE_NAME = "News Ticker"
TICKER_FONT = "Arial"
TICKER_FONT_SIZE = 36
TICKER_COLOR = 0xFFFFFFFF  # White (ABGR format for OBS)
TICKER_BG_COLOR = 0xCC000000  # Semi-transparent black


class NewsTicker:
    """Manages scrolling news ticker in OBS."""

    def __init__(self, interval: int = 10):
        """
        Initialize news ticker.

        Args:
            interval: Seconds between headline changes
        """
        self.interval = interval
        self.headlines: List[Dict[str, Any]] = []
        self.current_index = 0
        self.controller = None
        self.running = False

    def load_headlines(self) -> bool:
        """Load headlines from JSON file."""
        try:
            if HEADLINES_FILE.exists():
                with open(HEADLINES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.headlines = data.get("headlines", [])
                    logger.info(f"[TICKER] Loaded {len(self.headlines)} headlines")
                    return True
            else:
                logger.warning(f"[TICKER] Headlines file not found: {HEADLINES_FILE}")
                return False
        except Exception as e:
            logger.error(f"[TICKER] Error loading headlines: {e}")
            return False

    def get_current_headline(self) -> str:
        """Get the current headline text."""
        if not self.headlines:
            return "antifaFM Radio - 24/7 Antifascist Music"

        headline = self.headlines[self.current_index]
        return headline.get("text", "")

    def next_headline(self) -> str:
        """Advance to next headline and return it."""
        if self.headlines:
            self.current_index = (self.current_index + 1) % len(self.headlines)
        return self.get_current_headline()

    async def connect(self) -> bool:
        """Connect to OBS."""
        try:
            from modules.platform_integration.antifafm_broadcaster.src.obs_controller import OBSController
            host = os.getenv("OBS_WEBSOCKET_HOST", "localhost")
            self.controller = OBSController(host=host)
            return await self.controller.connect()
        except Exception as e:
            logger.error(f"[TICKER] Connection failed: {e}")
            return False

    async def create_ticker_source(self) -> bool:
        """Create or update the news ticker text source in OBS."""
        if not self.controller or not self.controller.connected:
            return False

        try:
            scene_name = await self.controller.get_current_scene()
            if not scene_name:
                return False

            ws = self.controller.ws

            # Check if ticker already exists
            inputs = ws.get_input_list()
            existing = [inp['inputName'] for inp in inputs.inputs]

            # Simple settings for text_gdiplus
            settings = {
                "text": self.get_current_headline(),
            }

            if TICKER_SOURCE_NAME in existing:
                ws.set_input_settings(TICKER_SOURCE_NAME, settings, True)
                logger.info("[TICKER] Updated existing ticker source")
            else:
                # Use versioned source type names (OBS 28+)
                ws.create_input(
                    scene_name,
                    TICKER_SOURCE_NAME,
                    "text_gdiplus_v3",  # Windows text source (GDI+ v3)
                    {"text": self.get_current_headline()},
                    True
                )
                logger.info("[TICKER] Created ticker source")
                logger.info("[TICKER] Created ticker source")

            # Position at bottom of screen
            await self.controller.set_source_bounds(
                TICKER_SOURCE_NAME,
                x=0, y=1030,  # Bottom of 1080p screen
                width=1920, height=50
            )

            return True

        except Exception as e:
            logger.error(f"[TICKER] Create source failed: {e}")
            return False

    async def update_ticker_text(self, text: str) -> bool:
        """Update the ticker text."""
        if not self.controller or not self.controller.connected:
            return False

        try:
            self.controller.ws.set_input_settings(
                TICKER_SOURCE_NAME,
                {"text": text},
                True  # Overlay mode
            )
            return True
        except Exception as e:
            logger.error(f"[TICKER] Update text failed: {e}")
            return False

    async def run(self):
        """Run the news ticker loop."""
        print("=" * 60)
        print("antifaFM News Ticker")
        print("=" * 60)

        self.load_headlines()
        print(f"Headlines: {len(self.headlines)}")
        print(f"Interval: {self.interval} seconds")
        print("Press Ctrl+C to stop")
        print("=" * 60)

        if not await self.connect():
            print("[ERROR] Could not connect to OBS")
            return

        # Create ticker source
        await self.create_ticker_source()

        self.running = True

        try:
            while self.running:
                headline = self.get_current_headline()
                print(f"[TICKER] {headline}")
                await self.update_ticker_text(headline)

                # Wait for interval
                for _ in range(self.interval):
                    if not self.running:
                        break
                    await asyncio.sleep(1)

                # Advance to next headline
                self.next_headline()

                # Check for updated headlines file
                self.load_headlines()

        except KeyboardInterrupt:
            print("\n[STOP] Ticker stopped")

        finally:
            self.running = False
            if self.controller:
                self.controller.disconnect()

    def stop(self):
        """Stop the ticker loop."""
        self.running = False


async def add_headlines(texts: List[str], author: str = "012"):
    """Add new headlines to the file."""
    data = {"headlines": [], "scroll_speed": 100, "display_duration": 10}

    if HEADLINES_FILE.exists():
        with open(HEADLINES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

    for text in texts:
        data["headlines"].append({
            "text": text,
            "priority": 2,
        })

    data["last_updated"] = datetime.now().isoformat()
    data["updated_by"] = author

    with open(HEADLINES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"[OK] Added {len(texts)} headlines")


async def test_ticker():
    """Quick test of ticker functionality."""
    ticker = NewsTicker(interval=5)
    ticker.load_headlines()

    print("Headlines loaded:")
    for i, h in enumerate(ticker.headlines):
        print(f"  {i+1}. {h['text']}")

    if await ticker.connect():
        await ticker.create_ticker_source()
        print("\n[OK] Ticker source created in OBS")

        # Show each headline for 3 seconds
        for _ in range(len(ticker.headlines)):
            headline = ticker.get_current_headline()
            print(f"[SHOW] {headline}")
            await ticker.update_ticker_text(headline)
            await asyncio.sleep(3)
            ticker.next_headline()

        ticker.controller.disconnect()
        print("\n[DONE] Ticker test complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="News Ticker for antifaFM")
    parser.add_argument("--interval", type=int, default=10,
                        help="Seconds between headline changes")
    parser.add_argument("--test", action="store_true",
                        help="Run quick test")
    parser.add_argument("--add", nargs="+",
                        help="Add headlines: --add 'Headline 1' 'Headline 2'")

    args = parser.parse_args()

    if args.add:
        asyncio.run(add_headlines(args.add))
    elif args.test:
        asyncio.run(test_ticker())
    else:
        ticker = NewsTicker(interval=args.interval)
        asyncio.run(ticker.run())
