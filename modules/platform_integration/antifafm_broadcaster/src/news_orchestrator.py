"""
News Orchestrator - WSP 15 Rated News Queue Management

Agentically manages news headlines with:
- WSP 15 priority scoring (urgency, relevance, engagement potential)
- Time-decayed queue (old news drops, top-rated stays)
- Rate-limited updates (no flooding)
- Recycling of top stories

Architecture:
    NewsOrchestrator
        |
        +-- NewsRater (WSP 15 scoring)
        |
        +-- NewsQueue (SQLite + time decay)
        |
        +-- TickerUpdater (rate-limited OBS updates)

Usage:
    orchestrator = NewsOrchestrator()
    orchestrator.ingest(headlines)  # Add new headlines
    orchestrator.tick()             # Process queue, update ticker
    orchestrator.get_top(5)         # Get top 5 rated headlines

WSP 15: Module Prioritization Scoring System
WSP 78: SQLite Layer B (Operational Store)
WSP 27: Universal DAE Architecture
"""

import asyncio
import hashlib
import logging
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Database path
NEWS_DB_PATH = Path(__file__).parent.parent / "data" / "news_queue.db"


@dataclass
class NewsItem:
    """A news headline with WSP 15 scoring."""
    headline: str
    source: str
    timestamp: float  # Unix timestamp when ingested
    hash_id: str = ""  # Dedup key

    # WSP 15 Scoring Components (0-10 each)
    urgency: float = 5.0      # Breaking news = 10, old story = 1
    relevance: float = 5.0    # Iran/Trump/War = 10, sports = 1
    engagement: float = 5.0   # Clickbait potential = 10, boring = 1
    freshness: float = 10.0   # Decays over time

    # Computed
    total_score: float = 0.0
    display_count: int = 0    # Times shown on ticker
    last_displayed: float = 0  # Unix timestamp

    def __post_init__(self):
        if not self.hash_id:
            self.hash_id = hashlib.sha256(self.headline.encode()).hexdigest()[:12]
        self.calculate_score()

    def calculate_score(self):
        """WSP 15 weighted scoring with time decay."""
        # Time decay factor (halves every 2 hours)
        age_hours = (time.time() - self.timestamp) / 3600
        self.freshness = max(1.0, 10.0 * (0.5 ** (age_hours / 2)))

        # Display fatigue (reduce score after many displays)
        fatigue = max(0.5, 1.0 - (self.display_count * 0.1))

        # Weighted total (WSP 15 formula)
        self.total_score = (
            self.urgency * 0.30 +
            self.relevance * 0.25 +
            self.engagement * 0.20 +
            self.freshness * 0.25
        ) * fatigue


class NewsRater:
    """
    WSP 15 scoring engine for news headlines.

    Scores based on:
    - Keyword urgency (BREAKING, LIVE, etc.)
    - Topic relevance (Iran, Trump, War, etc.)
    - Engagement potential (emotional words, questions)
    """

    # High-urgency keywords
    URGENCY_KEYWORDS = {
        "breaking": 10, "live": 9, "urgent": 9, "alert": 8,
        "just in": 8, "developing": 7, "update": 6, "new": 5
    }

    # Relevance keywords (antifaFM topics)
    RELEVANCE_KEYWORDS = {
        "iran": 10, "trump": 10, "war": 10, "attack": 9, "strike": 9,
        "missile": 9, "military": 8, "protest": 8, "ice": 8,
        "antifa": 10, "fascist": 9, "resistance": 8, "nazi": 9,
        "epstein": 9, "maga": 8, "israel": 8, "palestine": 8,
        "genocide": 9, "refugee": 7, "immigrant": 7
    }

    # Engagement boosters
    ENGAGEMENT_KEYWORDS = {
        "dead": 8, "killed": 8, "explosion": 8, "crash": 7,
        "shocking": 7, "revealed": 6, "secret": 6, "scandal": 7,
        "?": 6,  # Questions engage
    }

    def rate(self, headline: str, source: str = "unknown") -> NewsItem:
        """
        Rate a headline using WSP 15 criteria.

        Returns:
            NewsItem with scores populated
        """
        headline_lower = headline.lower()

        # Calculate urgency
        urgency = 5.0
        for kw, score in self.URGENCY_KEYWORDS.items():
            if kw in headline_lower:
                urgency = max(urgency, score)

        # Calculate relevance
        relevance = 3.0  # Base relevance for any news
        for kw, score in self.RELEVANCE_KEYWORDS.items():
            if kw in headline_lower:
                relevance = max(relevance, score)

        # Calculate engagement
        engagement = 5.0
        for kw, score in self.ENGAGEMENT_KEYWORDS.items():
            if kw in headline_lower:
                engagement = max(engagement, score)

        # Source boost (trusted sources get +1)
        trusted_sources = ["al jazeera", "bbc", "guardian", "dw", "france24"]
        if any(s in source.lower() for s in trusted_sources):
            relevance = min(10, relevance + 1)

        return NewsItem(
            headline=headline,
            source=source,
            timestamp=time.time(),
            urgency=urgency,
            relevance=relevance,
            engagement=engagement,
        )


class NewsQueue:
    """
    SQLite-backed priority queue for news items.

    WSP 78 Layer B: Operational Relational Store
    - Time-decayed scoring
    - Deduplication by hash
    - Automatic cleanup of old items
    """

    def __init__(self, db_path: Path = NEWS_DB_PATH):
        self.db_path = db_path
        self._conn = None
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS news_queue (
                    hash_id TEXT PRIMARY KEY,
                    headline TEXT NOT NULL,
                    source TEXT,
                    timestamp REAL,
                    urgency REAL,
                    relevance REAL,
                    engagement REAL,
                    freshness REAL,
                    total_score REAL,
                    display_count INTEGER DEFAULT 0,
                    last_displayed REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_score ON news_queue(total_score DESC)
            """)
            conn.commit()
            conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        """Get SQLite connection (thread-safe)."""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def add(self, item: NewsItem) -> bool:
        """
        Add or update a news item.

        Returns:
            True if new item added, False if duplicate updated
        """
        with self._lock:
            conn = self._get_conn()
            cursor = conn.cursor()

            # Check if exists
            cursor.execute("SELECT hash_id FROM news_queue WHERE hash_id = ?", (item.hash_id,))
            exists = cursor.fetchone() is not None

            if exists:
                # Update scores (recalculate freshness)
                item.calculate_score()
                cursor.execute("""
                    UPDATE news_queue SET
                        freshness = ?, total_score = ?
                    WHERE hash_id = ?
                """, (item.freshness, item.total_score, item.hash_id))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO news_queue
                    (hash_id, headline, source, timestamp, urgency, relevance,
                     engagement, freshness, total_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.hash_id, item.headline, item.source, item.timestamp,
                    item.urgency, item.relevance, item.engagement,
                    item.freshness, item.total_score
                ))

            conn.commit()
            return not exists

    def get_top(self, limit: int = 5) -> List[NewsItem]:
        """Get top-rated items (recalculates scores first)."""
        with self._lock:
            conn = self._get_conn()
            cursor = conn.cursor()

            # Recalculate all freshness scores
            cursor.execute("SELECT * FROM news_queue")
            rows = cursor.fetchall()

            items = []
            for row in rows:
                item = NewsItem(
                    headline=row["headline"],
                    source=row["source"],
                    timestamp=row["timestamp"],
                    hash_id=row["hash_id"],
                    urgency=row["urgency"],
                    relevance=row["relevance"],
                    engagement=row["engagement"],
                    display_count=row["display_count"],
                    last_displayed=row["last_displayed"],
                )
                item.calculate_score()

                # Update score in DB
                cursor.execute("""
                    UPDATE news_queue SET freshness = ?, total_score = ?
                    WHERE hash_id = ?
                """, (item.freshness, item.total_score, item.hash_id))

                items.append(item)

            conn.commit()

            # Sort and return top
            items.sort(key=lambda x: x.total_score, reverse=True)
            return items[:limit]

    def mark_displayed(self, hash_id: str):
        """Mark an item as displayed (increases fatigue)."""
        with self._lock:
            conn = self._get_conn()
            conn.execute("""
                UPDATE news_queue SET
                    display_count = display_count + 1,
                    last_displayed = ?
                WHERE hash_id = ?
            """, (time.time(), hash_id))
            conn.commit()

    def cleanup_old(self, max_age_hours: float = 24):
        """Remove items older than max_age_hours."""
        cutoff = time.time() - (max_age_hours * 3600)
        with self._lock:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM news_queue WHERE timestamp < ?", (cutoff,))
            deleted = cursor.rowcount
            conn.commit()
            if deleted > 0:
                logger.info(f"[NEWS] Cleaned up {deleted} old items")
            return deleted

    def count(self) -> int:
        """Get total items in queue."""
        with self._lock:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM news_queue")
            return cursor.fetchone()[0]


class NewsOrchestrator:
    """
    Main orchestrator for agentic news management.

    Combines:
    - NewsRater: WSP 15 scoring
    - NewsQueue: SQLite storage with time decay
    - Rate limiting: No flooding (min interval between updates)
    """

    def __init__(
        self,
        update_interval_seconds: float = 300,  # 5 min between ticker updates
        max_queue_size: int = 100,
        cleanup_age_hours: float = 24,
    ):
        self.rater = NewsRater()
        self.queue = NewsQueue()
        self.update_interval = update_interval_seconds
        self.max_queue_size = max_queue_size
        self.cleanup_age_hours = cleanup_age_hours

        self._last_update = 0
        self._current_headlines: List[str] = []

    def ingest(self, headlines: List[str], source: str = "unknown") -> Dict[str, Any]:
        """
        Ingest new headlines, rate and queue them.

        Args:
            headlines: List of headline strings
            source: News source name

        Returns:
            Stats dict {added, updated, total}
        """
        added = 0
        updated = 0

        for headline in headlines:
            # Skip empty or very short
            if not headline or len(headline) < 10:
                continue

            # Rate the headline
            item = self.rater.rate(headline, source)

            # Add to queue
            is_new = self.queue.add(item)
            if is_new:
                added += 1
            else:
                updated += 1

        # Cleanup old items
        self.queue.cleanup_old(self.cleanup_age_hours)

        total = self.queue.count()
        logger.info(f"[NEWS] Ingested: +{added} new, ~{updated} updated, {total} total")

        return {"added": added, "updated": updated, "total": total}

    def get_top(self, limit: int = 5) -> List[NewsItem]:
        """Get top-rated headlines."""
        return self.queue.get_top(limit)

    def get_ticker_text(self, limit: int = 5, separator: str = " | ") -> str:
        """
        Get formatted ticker text from top headlines.

        Marks items as displayed to apply fatigue.
        """
        items = self.get_top(limit)

        headlines = []
        for item in items:
            headlines.append(item.headline)
            self.queue.mark_displayed(item.hash_id)

        return separator.join(headlines)

    def should_update(self) -> bool:
        """Check if enough time has passed for an update."""
        return (time.time() - self._last_update) >= self.update_interval

    def tick(self) -> Optional[str]:
        """
        Agentic tick - check if update needed and return ticker text.

        Returns:
            Ticker text if update needed, None otherwise
        """
        if not self.should_update():
            return None

        self._last_update = time.time()

        # Get new ticker text
        ticker = self.get_ticker_text(limit=5)
        if ticker:
            logger.info(f"[NEWS] Ticker update: {ticker[:60]}...")

        return ticker

    def get_for_description(self, limit: int = 5) -> List[str]:
        """
        Get top headlines for M2M description.

        Does NOT mark as displayed (description update is separate).
        """
        items = self.get_top(limit)
        return [item.headline for item in items]

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        items = self.queue.get_top(10)

        return {
            "total": self.queue.count(),
            "top_score": items[0].total_score if items else 0,
            "avg_score": sum(i.total_score for i in items) / len(items) if items else 0,
            "last_update": self._last_update,
            "next_update_in": max(0, self.update_interval - (time.time() - self._last_update)),
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

async def main():
    """CLI for testing news orchestrator."""
    import sys

    orchestrator = NewsOrchestrator(update_interval_seconds=60)

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "ingest":
            # Ingest from stdin or args
            if len(sys.argv) > 2:
                headlines = sys.argv[2:]
            else:
                print("Enter headlines (one per line, Ctrl+D to finish):")
                headlines = [line.strip() for line in sys.stdin if line.strip()]

            result = orchestrator.ingest(headlines, source="CLI")
            print(f"Result: {result}")

        elif cmd == "top":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            items = orchestrator.get_top(limit)
            print(f"\n=== Top {limit} Headlines (WSP 15 Scored) ===")
            for i, item in enumerate(items):
                print(f"\n[{i+1}] Score: {item.total_score:.2f}")
                print(f"    U:{item.urgency:.1f} R:{item.relevance:.1f} E:{item.engagement:.1f} F:{item.freshness:.1f}")
                print(f"    {item.headline[:80]}...")

        elif cmd == "ticker":
            text = orchestrator.get_ticker_text(limit=5)
            print(f"\n=== Ticker Text ===\n{text}")

        elif cmd == "stats":
            stats = orchestrator.get_stats()
            print(f"\n=== Queue Stats ===")
            for k, v in stats.items():
                print(f"  {k}: {v}")

        elif cmd == "description":
            headlines = orchestrator.get_for_description(5)
            print(f"\n=== For M2M Description ===")
            for h in headlines:
                print(f"- {h}")

        else:
            print("Usage: python news_orchestrator.py <command>")
            print("Commands: ingest, top [N], ticker, stats, description")

    else:
        print("Usage: python news_orchestrator.py <command>")
        print("Commands: ingest, top [N], ticker, stats, description")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    asyncio.run(main())
