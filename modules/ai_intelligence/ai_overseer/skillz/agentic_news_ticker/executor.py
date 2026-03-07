"""
Agentic News Ticker - Autonomous news aggregation for antifaFM stream.

Fetches news every 30 minutes and updates the OBS ticker headlines.

Usage:
    python -m ai_overseer.skillz.agentic_news_ticker.executor --update
    python -m ai_overseer.skillz.agentic_news_ticker.executor --daemon
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Paths
HEADLINES_FILE = PROJECT_ROOT / "modules" / "platform_integration" / "antifafm_broadcaster" / "data" / "headlines.json"

# Configuration
UPDATE_INTERVAL = int(os.getenv("AGENTIC_TICKER_INTERVAL", 1800))  # 30 minutes
MAX_HEADLINES = int(os.getenv("AGENTIC_TICKER_HEADLINES", 6))

# News search topics
SEARCH_TOPICS = [
    "labor union victory",
    "workers strike news",
    "antifascist protest",
    "community organizing",
    "mutual aid network",
    "climate activism news",
    "progressive movement",
]

# RSS Feed sources for real news
RSS_FEEDS = [
    "https://www.commondreams.org/rss.xml",           # Common Dreams
    "https://truthout.org/feed/",                      # Truthout
    "https://theintercept.com/feed/?rss",              # The Intercept
    "https://feeds.feedburner.com/Portside",           # Portside
    "https://www.democracynow.org/democracynow.rss",   # Democracy Now
    "https://jacobin.com/feed",                        # Jacobin
]

# Static headlines (fallback + branding)
STATIC_HEADLINES = [
    "antifaFM Radio - 24/7 Antifascist Beats",
    "foundups.com - Building Autonomous Ventures",
]


class AgenticNewsTicker:
    """Autonomous news aggregation for stream ticker."""

    def __init__(self):
        self.llm_client = None
        self.running = False

    async def _init_llm(self):
        """Initialize LLM client for news formatting."""
        try:
            from modules.infrastructure.shared_utilities.llm_client.src.client import LLMClient
            self.llm_client = LLMClient(model="qwen")
            return True
        except ImportError:
            logger.warning("[TICKER] LLM client not available, using raw headlines")
            return False

    async def search_news(self, topic: str) -> List[Dict[str, Any]]:
        """Search for news on a topic using web search."""
        try:
            # Try MCP web search
            from holo_index.qwen_advisor.llm_engine import search_web
            results = await search_web(f"{topic} news today", max_results=3)
            return results if results else []
        except Exception as e:
            logger.debug(f"[TICKER] Web search failed for {topic}: {e}")
            return []

    async def fetch_rss_headlines(self, feed_url: str) -> List[str]:
        """Fetch headlines from an RSS feed."""
        try:
            import urllib.request
            import xml.etree.ElementTree as ET

            headers = {'User-Agent': 'Mozilla/5.0 antifaFM News Bot'}
            req = urllib.request.Request(feed_url, headers=headers)

            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')

            # Parse RSS XML
            root = ET.fromstring(content)
            headlines = []

            # Try RSS 2.0 format
            for item in root.findall('.//item')[:5]:
                title = item.find('title')
                if title is not None and title.text:
                    headlines.append(title.text.strip())

            # Try Atom format
            if not headlines:
                for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry')[:5]:
                    title = entry.find('{http://www.w3.org/2005/Atom}title')
                    if title is not None and title.text:
                        headlines.append(title.text.strip())

            return headlines

        except Exception as e:
            logger.debug(f"[TICKER] RSS fetch failed for {feed_url}: {e}")
            return []

    async def search_news_duckduckgo(self, query: str) -> List[str]:
        """Fallback: Search news via DuckDuckGo directly."""
        try:
            import urllib.request
            import urllib.parse

            # DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                headlines = []

                # Extract from related topics
                for topic in data.get("RelatedTopics", [])[:3]:
                    if isinstance(topic, dict) and "Text" in topic:
                        text = topic["Text"]
                        if len(text) < 100:
                            headlines.append(text)

                return headlines

        except Exception as e:
            logger.debug(f"[TICKER] DuckDuckGo search failed: {e}")
            return []

    async def format_headline(self, raw_text: str) -> str:
        """Format a raw news item into a ticker-friendly headline."""
        # Simple formatting without LLM
        headline = raw_text.strip()

        # Truncate if too long
        if len(headline) > 80:
            headline = headline[:77] + "..."

        # Remove quotes
        headline = headline.replace('"', "'")

        return headline

    async def format_headlines_with_llm(self, raw_headlines: List[str]) -> List[str]:
        """Use LLM to format headlines for ticker."""
        if not self.llm_client or not raw_headlines:
            return raw_headlines

        try:
            prompt = f"""Format these news items into short, punchy ticker headlines (max 70 chars each).
Focus on progressive/labor/activism news. Return one headline per line.

Raw news:
{chr(10).join(raw_headlines[:10])}

Ticker headlines:"""

            response = await self.llm_client.complete(prompt, max_tokens=200)
            formatted = [line.strip() for line in response.split("\n") if line.strip()]
            return formatted[:MAX_HEADLINES]

        except Exception as e:
            logger.warning(f"[TICKER] LLM formatting failed: {e}")
            return raw_headlines

    async def fetch_all_news(self) -> List[str]:
        """Fetch news from RSS feeds and web search."""
        all_headlines = []

        # Primary: Fetch from RSS feeds
        for feed_url in RSS_FEEDS:
            feed_name = feed_url.split('/')[2]
            logger.info(f"[TICKER] Fetching: {feed_name}")

            headlines = await self.fetch_rss_headlines(feed_url)
            all_headlines.extend(headlines)

            # Small delay to avoid rate limiting
            await asyncio.sleep(0.3)

        # Fallback: Web search if RSS didn't return enough
        if len(all_headlines) < MAX_HEADLINES:
            for topic in SEARCH_TOPICS[:3]:
                logger.info(f"[TICKER] Searching: {topic}")
                results = await self.search_news_duckduckgo(f"{topic} news")
                all_headlines.extend(results)
                await asyncio.sleep(0.5)

        # Format headlines
        formatted = []
        seen = set()  # Dedupe
        for headline in all_headlines:
            formatted_hl = await self.format_headline(headline)
            if formatted_hl and len(formatted_hl) > 20:
                # Simple dedup by first 30 chars
                key = formatted_hl[:30].lower()
                if key not in seen:
                    seen.add(key)
                    formatted.append(formatted_hl)

        return formatted[:MAX_HEADLINES]

    async def update_headlines(self) -> bool:
        """Fetch news and update headlines.json."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating headlines...")

        # Fetch news
        news_headlines = await self.fetch_all_news()

        # Combine with static headlines
        all_headlines = []

        # Add static branding headlines
        for text in STATIC_HEADLINES:
            all_headlines.append({"text": text, "priority": 1, "source": "static"})

        # Add news headlines
        for text in news_headlines:
            all_headlines.append({"text": text, "priority": 2, "source": "news"})

        # Build output
        output = {
            "headlines": all_headlines,
            "scroll_speed": 100,
            "display_duration": 10,
            "last_updated": datetime.now().isoformat(),
            "updated_by": "agentic_news_ticker",
        }

        # Write to file
        try:
            HEADLINES_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(HEADLINES_FILE, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2)

            print(f"[OK] Updated {len(all_headlines)} headlines")
            for hl in all_headlines:
                source = hl.get("source", "unknown")
                print(f"  [{source}] {hl['text'][:60]}...")

            return True

        except Exception as e:
            logger.error(f"[TICKER] Failed to write headlines: {e}")
            return False

    async def run_daemon(self):
        """Run as daemon, updating every 30 minutes."""
        print("=" * 60)
        print("Agentic News Ticker Daemon")
        print("=" * 60)
        print(f"Update interval: {UPDATE_INTERVAL // 60} minutes")
        print(f"Headlines file: {HEADLINES_FILE}")
        print("Press Ctrl+C to stop")
        print("=" * 60)

        await self._init_llm()

        self.running = True

        try:
            while self.running:
                await self.update_headlines()

                # Wait for next update
                print(f"\n[WAIT] Next update in {UPDATE_INTERVAL // 60} minutes...")
                for _ in range(UPDATE_INTERVAL):
                    if not self.running:
                        break
                    await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\n[STOP] Daemon stopped")

        finally:
            self.running = False

    def stop(self):
        """Stop the daemon."""
        self.running = False


async def add_headline(text: str, author: str = "012"):
    """Add a custom headline."""
    data = {"headlines": [], "scroll_speed": 100, "display_duration": 10}

    if HEADLINES_FILE.exists():
        with open(HEADLINES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

    data["headlines"].insert(0, {
        "text": text,
        "priority": 1,
        "source": "manual",
    })

    data["last_updated"] = datetime.now().isoformat()
    data["updated_by"] = author

    with open(HEADLINES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"[OK] Added headline: {text}")


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(description="Agentic News Ticker")
    parser.add_argument("--update", action="store_true",
                        help="One-time headline update")
    parser.add_argument("--daemon", action="store_true",
                        help="Run as daemon (update every 30 min)")
    parser.add_argument("--add", type=str,
                        help="Add a custom headline")

    args = parser.parse_args()

    if args.add:
        asyncio.run(add_headline(args.add))
    elif args.daemon:
        ticker = AgenticNewsTicker()
        asyncio.run(ticker.run_daemon())
    else:
        # Default: one-time update
        ticker = AgenticNewsTicker()
        asyncio.run(ticker.update_headlines())
