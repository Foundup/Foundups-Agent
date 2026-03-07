"""
Dynamic Metadata Daemon - Auto-update title/description with TOP news

Monitors news via NewsOrchestrator (WSP 15 scoring) and automatically
updates stream title/description when significant news changes occur.

Flow:
    News Source → NewsOrchestrator → WSP 15 scoring → Top news changed?
                                                            ↓ YES
                                         generate_clickbait_title(top_news)
                                         generate_m2m_description(top_news)
                                                            ↓
                                         API update (if live) or DOM (if past)

Usage:
    # Start daemon
    python dynamic_metadata_daemon.py start

    # Check status
    python dynamic_metadata_daemon.py status

    # Manual trigger
    python dynamic_metadata_daemon.py update

WSP 15: Module Prioritization Scoring System
WSP 27: Universal DAE Architecture
WSP 78: SQLite Layer B
"""

import asyncio
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Configuration
CHECK_INTERVAL_SECONDS = int(os.getenv("METADATA_CHECK_INTERVAL", "300"))  # 5 min
UPDATE_COOLDOWN_SECONDS = int(os.getenv("METADATA_UPDATE_COOLDOWN", "600"))  # 10 min between updates

# Title update thresholds (MAJOR events only)
TITLE_URGENCY_THRESHOLD = float(os.getenv("TITLE_URGENCY_THRESHOLD", "8.0"))  # Only BREAKING/LIVE
TITLE_SCORE_THRESHOLD = float(os.getenv("TITLE_SCORE_THRESHOLD", "8.5"))  # High WSP 15 score

# Description update thresholds (SEO - more frequent)
DESCRIPTION_UPDATE_INTERVAL = int(os.getenv("DESCRIPTION_UPDATE_INTERVAL", "1800"))  # 30 min


@dataclass
class MetadataState:
    """Track current metadata state for change detection."""
    # Title state (MAJOR events only)
    last_title: str = ""
    last_title_update: float = 0
    title_update_count: int = 0
    last_major_headline: str = ""

    # Description state (SEO - more frequent)
    last_description_update: float = 0
    description_update_count: int = 0
    top_headline_hash: str = ""
    top_score: float = 0.0


class DynamicMetadataDaemon:
    """
    Daemon that monitors news and auto-updates stream metadata.

    Features:
    - WSP 15 scored news queue
    - Change detection (only update when top news changes)
    - Rate limiting (cooldown between updates)
    - API-first, DOM-fallback
    """

    def __init__(
        self,
        check_interval: float = CHECK_INTERVAL_SECONDS,
        update_cooldown: float = UPDATE_COOLDOWN_SECONDS,
        title_urgency_threshold: float = TITLE_URGENCY_THRESHOLD,
        title_score_threshold: float = TITLE_SCORE_THRESHOLD,
        description_interval: float = DESCRIPTION_UPDATE_INTERVAL,
    ):
        self.check_interval = check_interval
        self.update_cooldown = update_cooldown
        self.title_urgency_threshold = title_urgency_threshold
        self.title_score_threshold = title_score_threshold
        self.description_interval = description_interval

        self.state = MetadataState()
        self._running = False
        self._orchestrator = None

    def _get_orchestrator(self):
        """Lazy load NewsOrchestrator."""
        if self._orchestrator is None:
            from modules.platform_integration.antifafm_broadcaster.src.news_orchestrator import NewsOrchestrator
            self._orchestrator = NewsOrchestrator(update_interval_seconds=60)
        return self._orchestrator

    def _compute_headline_hash(self, headlines: List[str]) -> str:
        """Compute hash of top headlines for change detection."""
        combined = "|".join(headlines[:3])  # Top 3
        return hashlib.sha256(combined.encode()).hexdigest()[:12]

    def should_update_title(self, top_items) -> bool:
        """
        Determine if TITLE should be updated (MAJOR events only).

        Title changes only for:
        - Urgency >= 8 (BREAKING, LIVE keywords)
        - Total score >= 8.5
        - Different from last major headline
        """
        if not top_items:
            return False

        top_item = top_items[0]

        # Check cooldown
        time_since_update = time.time() - self.state.last_title_update
        if time_since_update < self.update_cooldown:
            return False

        # Must be a MAJOR event
        is_major = (
            top_item.urgency >= self.title_urgency_threshold or
            top_item.total_score >= self.title_score_threshold
        )

        if not is_major:
            logger.debug(f"[DAEMON] Not major event: U={top_item.urgency:.1f}, S={top_item.total_score:.2f}")
            return False

        # Must be different from last major headline
        if top_item.headline == self.state.last_major_headline:
            return False

        logger.info(f"[DAEMON] MAJOR EVENT detected: {top_item.headline[:50]}...")
        logger.info(f"[DAEMON] Urgency: {top_item.urgency:.1f}, Score: {top_item.total_score:.2f}")
        return True

    def should_update_description(self, top_items) -> bool:
        """
        Determine if DESCRIPTION should be updated (SEO - more frequent).

        Description updates when:
        - Top headlines changed (new news for SEO)
        - Enough time has passed since last update
        """
        if not top_items:
            return False

        # Check interval
        time_since_update = time.time() - self.state.last_description_update
        if time_since_update < self.description_interval:
            return False

        # Check if headlines changed
        headlines = [item.headline for item in top_items]
        current_hash = self._compute_headline_hash(headlines)

        if current_hash != self.state.top_headline_hash:
            logger.info(f"[DAEMON] News changed for SEO update")
            return True

        return False

    async def fetch_news(self) -> int:
        """
        Fetch news from sources and ingest into orchestrator.

        Returns:
            Number of new headlines ingested
        """
        orchestrator = self._get_orchestrator()

        # Try multiple news sources
        all_headlines = []

        # Source 1: DuckDuckGo News (free)
        try:
            from modules.platform_integration.antifafm_broadcaster.scripts.launch import _fetch_news_headlines
            headlines = _fetch_news_headlines() if callable(_fetch_news_headlines) else []
            if headlines:
                all_headlines.extend(headlines)
                logger.debug(f"[DAEMON] Fetched {len(headlines)} from DDG News")
        except Exception as e:
            logger.debug(f"[DAEMON] DDG News fetch failed: {e}")

        # Source 2: RSS feeds (if configured)
        try:
            from modules.platform_integration.antifafm_broadcaster.src.news_sources import fetch_rss_headlines
            rss_headlines = fetch_rss_headlines()
            if rss_headlines:
                all_headlines.extend(rss_headlines)
                logger.debug(f"[DAEMON] Fetched {len(rss_headlines)} from RSS")
        except Exception:
            pass  # RSS module may not exist

        # Ingest all headlines
        if all_headlines:
            result = orchestrator.ingest(all_headlines, source="multi")
            return result.get("added", 0)

        return 0

    async def update_metadata(
        self,
        update_title: bool = False,
        update_description: bool = False,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Generate and apply new title/description from top news.

        Args:
            update_title: Update title (MAJOR events only)
            update_description: Update description (SEO)
            force: Force update regardless of thresholds

        Returns:
            dict with success status and details
        """
        orchestrator = self._get_orchestrator()
        top_items = orchestrator.get_top(5)

        if not top_items:
            return {"success": False, "error": "No news in queue"}

        headlines = [item.headline for item in top_items]

        from modules.platform_integration.antifafm_broadcaster.src.youtube_broadcast_manager import (
            generate_clickbait_title, generate_m2m_description
        )

        # Determine what to update
        title = None
        description = None
        changes = []

        if update_title or force:
            title = generate_clickbait_title(headlines)
            changes.append(f"title={title[:40]}")
            logger.info(f"[DAEMON] Generated TITLE (major event): {title}")

        if update_description or force:
            description = generate_m2m_description(headlines)
            changes.append("description=SEO_NEWS")
            logger.info(f"[DAEMON] Generated DESCRIPTION with {len(headlines)} headlines for SEO")

        if not title and not description:
            return {"success": False, "error": "Nothing to update"}

        # Try API first (for live streams)
        try:
            from modules.platform_integration.antifafm_broadcaster.src.youtube_broadcast_manager import YouTubeBroadcastManager
            manager = YouTubeBroadcastManager()
            result = await manager.update_current_broadcast(title=title, description=description)

            if result.get("success"):
                logger.info("[DAEMON] Updated via API (live stream)")
                self._update_state(top_items, title, update_title, update_description)
                return {"success": True, "method": "api", "changes": changes}
        except Exception as e:
            logger.debug(f"[DAEMON] API update failed: {e}")

        # Fallback to DOM (for past broadcasts)
        try:
            from modules.platform_integration.antifafm_broadcaster.skillz.manage_metadata_editor import (
                edit_broadcast_metadata
            )
            result = await edit_broadcast_metadata(
                video_index=0,  # Most recent
                title=title,
                description=description
            )

            if result.get("success"):
                logger.info("[DAEMON] Updated via DOM (manage page)")
                self._update_state(top_items, title, update_title, update_description)
                return {"success": True, "method": "dom", "changes": changes}
        except Exception as e:
            logger.debug(f"[DAEMON] DOM update failed: {e}")

        return {"success": False, "error": "Both API and DOM updates failed"}

    def _update_state(self, top_items, title: Optional[str], updated_title: bool, updated_desc: bool):
        """Update internal state after successful update."""
        headlines = [item.headline for item in top_items]
        now = time.time()

        if updated_title and title:
            self.state.last_title = title
            self.state.last_title_update = now
            self.state.title_update_count += 1
            self.state.last_major_headline = top_items[0].headline if top_items else ""
            logger.info(f"[DAEMON] Title state updated: {title[:40]}...")

        if updated_desc:
            self.state.last_description_update = now
            self.state.description_update_count += 1
            self.state.top_headline_hash = self._compute_headline_hash(headlines)
            self.state.top_score = top_items[0].total_score if top_items else 0
            logger.info(f"[DAEMON] Description state updated for SEO")

    async def tick(self) -> Optional[Dict[str, Any]]:
        """
        Single daemon tick:
        1. Fetch news
        2. Check if TITLE update needed (MAJOR events)
        3. Check if DESCRIPTION update needed (SEO)
        4. Update accordingly

        Returns:
            Update result if performed, None otherwise
        """
        # Fetch fresh news
        new_count = await self.fetch_news()

        # Get top items
        orchestrator = self._get_orchestrator()
        top_items = orchestrator.get_top(5)

        if not top_items:
            return None

        # Check what needs updating
        update_title = self.should_update_title(top_items)
        update_desc = self.should_update_description(top_items)

        if update_title or update_desc:
            return await self.update_metadata(
                update_title=update_title,
                update_description=update_desc
            )

        return None

    async def run(self):
        """
        Main daemon loop.

        Runs continuously, checking for news updates and
        triggering metadata updates when needed.
        """
        self._running = True
        logger.info(f"[DAEMON] Starting dynamic metadata daemon")
        logger.info(f"[DAEMON] Check interval: {self.check_interval}s, Cooldown: {self.update_cooldown}s")

        while self._running:
            try:
                result = await self.tick()

                if result:
                    if result.get("success"):
                        print(f"[{datetime.now().strftime('%H:%M')}] UPDATED: {result.get('title', '')[:50]}...")
                    else:
                        print(f"[{datetime.now().strftime('%H:%M')}] Update failed: {result.get('error')}")
                else:
                    # No update needed
                    orchestrator = self._get_orchestrator()
                    stats = orchestrator.get_stats()
                    logger.debug(f"[DAEMON] No update needed. Queue: {stats['total']}, Top score: {stats['top_score']:.2f}")

                await asyncio.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("[DAEMON] Stopping...")
                break
            except Exception as e:
                logger.error(f"[DAEMON] Error in tick: {e}")
                await asyncio.sleep(60)  # Wait before retry

        self._running = False
        logger.info("[DAEMON] Stopped")

    def stop(self):
        """Stop the daemon."""
        self._running = False

    def get_status(self) -> Dict[str, Any]:
        """Get daemon status."""
        orchestrator = self._get_orchestrator()
        stats = orchestrator.get_stats()
        top_items = orchestrator.get_top(1)
        top_item = top_items[0] if top_items else None

        return {
            "running": self._running,
            # Title stats (MAJOR events)
            "title_updates": self.state.title_update_count,
            "last_title": self.state.last_title[:50] if self.state.last_title else None,
            "title_cooldown": max(0, self.update_cooldown - (time.time() - self.state.last_title_update)),
            # Description stats (SEO)
            "desc_updates": self.state.description_update_count,
            "desc_cooldown": max(0, self.description_interval - (time.time() - self.state.last_description_update)),
            # Queue stats
            "queue_size": stats["total"],
            "top_score": stats["top_score"],
            "top_urgency": top_item.urgency if top_item else 0,
            "is_major_event": (top_item.urgency >= self.title_urgency_threshold or
                             top_item.total_score >= self.title_score_threshold) if top_item else False,
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

async def main():
    import sys

    daemon = DynamicMetadataDaemon()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "start":
            print("=== Dynamic Metadata Daemon ===")
            print(f"Check interval: {daemon.check_interval}s")
            print(f"Update cooldown: {daemon.update_cooldown}s")
            print("Press Ctrl+C to stop")
            print()
            await daemon.run()

        elif cmd == "update":
            print("[DAEMON] Manual update triggered...")
            result = await daemon.update_metadata()
            print(f"Result: {result}")

        elif cmd == "status":
            # Do a tick to refresh stats
            await daemon.fetch_news()
            status = daemon.get_status()
            print("\n=== Daemon Status ===")
            for k, v in status.items():
                print(f"  {k}: {v}")

        elif cmd == "tick":
            print("[DAEMON] Single tick...")
            result = await daemon.tick()
            if result:
                print(f"Update result: {result}")
            else:
                print("No update needed")
            print(f"\nStatus: {daemon.get_status()}")

        else:
            print("Usage: python dynamic_metadata_daemon.py <command>")
            print("Commands: start, update, status, tick")
    else:
        print("Usage: python dynamic_metadata_daemon.py <command>")
        print("Commands: start, update, status, tick")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    asyncio.run(main())
