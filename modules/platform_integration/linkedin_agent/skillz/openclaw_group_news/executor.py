#!/usr/bin/env python3
"""
OpenClaw Group News Poster - Executor

Posts OpenClaw news to LinkedIn Group 6729915.
Runs BEFORE comment engagement in the LinkedIn automation flow.

WSP References:
- WSP 78: Database logging to agents_social_posts
- WSP 42: LinkedIn platform integration
- WSP 96: WRE Skills protocol
"""

import os
import sys
import time
import random
import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Constants
LINKEDIN_GROUP_ID = "6729915"
LINKEDIN_GROUP_URL = f"https://www.linkedin.com/groups/{LINKEDIN_GROUP_ID}/"
MAX_POSTS_PER_DAY = 3
MIN_POST_INTERVAL_HOURS = 4
RELEVANCE_THRESHOLD = 0.6
DUPLICATE_CHECK_DAYS = 7


@dataclass
class NewsItem:
    """News item from search results."""
    title: str
    url: str
    source: str
    published_date: Optional[datetime] = None
    summary: Optional[str] = None

    def content_hash(self) -> str:
        """Generate hash for duplicate detection."""
        return hashlib.sha256(self.url.encode()).hexdigest()[:16]


class NewsRelevanceRater:
    """
    Simple 4-dimension news relevance scoring.
    Lighter than WSP 15 MPS - focused on news posting.
    """

    # Source authority tiers
    AUTHORITY_TIERS = {
        "high": ["techcrunch", "wired", "theverge", "arstechnica", "venturebeat",
                 "reuters", "bloomberg", "wsj", "nytimes", "forbes"],
        "medium": ["medium", "dev.to", "hackernews", "reddit", "substack", "github"],
        "low": []  # Default for unknown sources
    }

    @staticmethod
    def rate(item: NewsItem) -> float:
        """
        Rate news relevance (0.0-1.0).

        Dimensions (weights):
        - Recency (0.3): How recent is the article?
        - Authority (0.2): Source credibility
        - Relevance (0.4): OpenClaw mention strength
        - Engagement (0.1): Breaking news potential
        """
        recency = NewsRelevanceRater._score_recency(item.published_date)
        authority = NewsRelevanceRater._score_authority(item.source)
        relevance = NewsRelevanceRater._score_relevance(item.title, item.summary)
        engagement = NewsRelevanceRater._score_engagement(item.title)

        score = (recency * 0.3) + (authority * 0.2) + (relevance * 0.4) + (engagement * 0.1)

        logger.debug(f"[NEWS_RATE] {item.title[:50]}... "
                    f"recency={recency:.2f} auth={authority:.2f} "
                    f"rel={relevance:.2f} eng={engagement:.2f} -> {score:.2f}")

        return round(score, 3)

    @staticmethod
    def _score_recency(pub_date: Optional[datetime]) -> float:
        """Score based on publication date."""
        if not pub_date:
            return 0.3  # Unknown date - assume moderately old

        age = datetime.now() - pub_date
        if age < timedelta(hours=24):
            return 1.0
        elif age < timedelta(days=3):
            return 0.7
        elif age < timedelta(days=7):
            return 0.5
        else:
            return 0.2

    @staticmethod
    def _score_authority(source: str) -> float:
        """Score based on source credibility."""
        source_lower = source.lower()

        for tier, sources in NewsRelevanceRater.AUTHORITY_TIERS.items():
            for s in sources:
                if s in source_lower:
                    if tier == "high":
                        return 1.0
                    elif tier == "medium":
                        return 0.6

        return 0.3  # Unknown source

    @staticmethod
    def _score_relevance(title: str, summary: Optional[str]) -> float:
        """Score based on OpenClaw mention strength."""
        text = f"{title} {summary or ''}".lower()

        # Direct OpenClaw mention
        if "openclaw" in text:
            return 1.0

        # OpenClaw ecosystem terms (high relevance)
        ecosystem_terms = ["lobster.cash", "crossmint", "peeka", "lobster cash"]
        if any(term in text for term in ecosystem_terms):
            return 0.95

        # AI agent framework terms (medium-high relevance)
        agent_terms = ["ai agent framework", "autonomous agent", "llm agent",
                      "agent orchestration", "ai orchestration", "multi-agent"]
        if any(term in text for term in agent_terms):
            return 0.8

        # General related terms
        related_terms = ["open source ai", "ai agents", "agent framework",
                        "autonomous agents", "llm agents", "ai assistant framework"]
        matches = sum(1 for term in related_terms if term in text)

        if matches >= 2:
            return 0.7
        elif matches == 1:
            return 0.5

        return 0.2

    @staticmethod
    def _score_engagement(title: str) -> float:
        """Score based on engagement potential."""
        title_lower = title.lower()

        # Breaking news indicators
        if any(word in title_lower for word in ["launch", "release", "announce", "join", "partner"]):
            return 1.0

        # Update indicators
        if any(word in title_lower for word in ["update", "new", "add", "improve"]):
            return 0.6

        return 0.3


class OpenClawGroupPoster:
    """
    Posts news to LinkedIn OpenClaw Group.
    Uses anti-detection patterns from foundups_selenium.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize poster with database connection.

        Args:
            db_path: Path to unified database (WSP 78).
                     Default: modules/infrastructure/database/data/foundups.db
        """
        self.db_path = db_path or self._get_default_db_path()
        self._init_db()
        self.driver = None

    def _get_default_db_path(self) -> str:
        """Get default database path per WSP 78."""
        base = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
        return os.path.join(base, "modules", "infrastructure", "database", "data", "foundups.db")

    def _init_db(self) -> None:
        """Initialize agents_social_posts table."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents_social_posts (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                group_id TEXT,
                content TEXT NOT NULL,
                source_url TEXT,
                content_hash TEXT,
                relevance_score REAL,
                posted_at TIMESTAMP,
                post_status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_social_posts_platform ON agents_social_posts(platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_social_posts_hash ON agents_social_posts(content_hash)")

        conn.commit()
        conn.close()
        logger.info(f"[DB] agents_social_posts table initialized: {self.db_path}")

    def can_post_today(self) -> Tuple[bool, str]:
        """
        Check if posting is allowed based on rate limits.

        Returns:
            Tuple of (allowed, reason)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check daily limit
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) FROM agents_social_posts
            WHERE platform = 'linkedin'
            AND group_id = ?
            AND date(posted_at) = ?
            AND post_status = 'posted'
        """, (LINKEDIN_GROUP_ID, today))

        daily_count = cursor.fetchone()[0]
        if daily_count >= MAX_POSTS_PER_DAY:
            conn.close()
            return False, f"Daily limit reached ({daily_count}/{MAX_POSTS_PER_DAY})"

        # Check minimum interval
        cursor.execute("""
            SELECT posted_at FROM agents_social_posts
            WHERE platform = 'linkedin'
            AND group_id = ?
            AND post_status = 'posted'
            ORDER BY posted_at DESC LIMIT 1
        """, (LINKEDIN_GROUP_ID,))

        last_post = cursor.fetchone()
        conn.close()

        if last_post:
            last_time = datetime.fromisoformat(last_post[0])
            hours_since = (datetime.now() - last_time).total_seconds() / 3600
            if hours_since < MIN_POST_INTERVAL_HOURS:
                return False, f"Too soon since last post ({hours_since:.1f}h < {MIN_POST_INTERVAL_HOURS}h)"

        return True, f"OK ({daily_count}/{MAX_POSTS_PER_DAY} today)"

    def is_duplicate(self, item: NewsItem) -> bool:
        """Check if URL was posted recently."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=DUPLICATE_CHECK_DAYS)).isoformat()
        cursor.execute("""
            SELECT id FROM agents_social_posts
            WHERE content_hash = ?
            AND created_at > ?
        """, (item.content_hash(), cutoff))

        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def format_post(self, item: NewsItem) -> str:
        """Format news item as LinkedIn post."""
        parts = [item.title]

        if item.summary:
            # Truncate summary if too long
            summary = item.summary[:500] + "..." if len(item.summary) > 500 else item.summary
            parts.append(f"\n\n{summary}")

        parts.append(f"\n\nSource: {item.url}")
        parts.append("\n\n#OpenClaw #AI #Agents")

        return "".join(parts)

    def post_to_group(self, item: NewsItem, dry_run: bool = False) -> bool:
        """
        Post news item to LinkedIn group.

        Args:
            item: NewsItem to post
            dry_run: If True, log but don't actually post

        Returns:
            True if successful (or dry_run), False otherwise
        """
        # Check rate limits
        can_post, reason = self.can_post_today()
        if not can_post:
            logger.warning(f"[RATE_LIMIT] Cannot post: {reason}")
            return False

        # Check duplicate
        if self.is_duplicate(item):
            logger.info(f"[DUPLICATE] Already posted: {item.url}")
            return False

        # Generate post content
        content = self.format_post(item)
        score = NewsRelevanceRater.rate(item)

        # Generate post ID
        post_id = f"ln_grp_{LINKEDIN_GROUP_ID}_{item.content_hash()}_{int(time.time())}"

        if dry_run:
            logger.info(f"[DRY_RUN] Would post to group {LINKEDIN_GROUP_ID}:")
            logger.info(f"  Title: {item.title}")
            logger.info(f"  Score: {score:.2f}")
            logger.info(f"  Content:\n{content[:200]}...")

            # Still log to DB as 'dry_run' status
            self._log_post(post_id, content, item, score, status="dry_run")
            return True

        # Actual posting via Selenium
        try:
            success = self._selenium_post_to_group(content)
            status = "posted" if success else "failed"
            self._log_post(post_id, content, item, score, status=status)
            return success
        except Exception as e:
            logger.error(f"[POST_ERROR] {e}")
            self._log_post(post_id, content, item, score, status="error")
            return False

    def _log_post(self, post_id: str, content: str, item: NewsItem,
                  score: float, status: str) -> None:
        """Log post to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO agents_social_posts
            (id, platform, group_id, content, source_url, content_hash,
             relevance_score, posted_at, post_status)
            VALUES (?, 'linkedin', ?, ?, ?, ?, ?, datetime('now'), ?)
        """, (post_id, LINKEDIN_GROUP_ID, content, item.url,
              item.content_hash(), score, status))

        conn.commit()
        conn.close()
        logger.info(f"[DB] Logged post {post_id} with status={status}")

    def _selenium_post_to_group(self, content: str) -> bool:
        """
        Post to LinkedIn group using Selenium.
        Uses anti-detection patterns from foundups_selenium.
        """
        try:
            from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn

            poster = AntiDetectionLinkedIn()

            # Navigate to group
            if not poster.driver:
                poster.create_driver()

            poster.driver.get(LINKEDIN_GROUP_URL)
            time.sleep(random.uniform(2, 4))  # Human-like delay

            # Click "Start a post in this group"
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            start_btn = WebDriverWait(poster.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                    "button.share-box-feed-entry__trigger, button[class*='share-box']"))
            )
            poster.human.human_click(start_btn) if hasattr(poster, 'human') and poster.human else start_btn.click()
            time.sleep(random.uniform(1, 2))

            # Type content
            editor = WebDriverWait(poster.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.ql-editor, div[contenteditable='true']"))
            )
            poster.human_type(editor, content) if hasattr(poster, 'human_type') else editor.send_keys(content)
            time.sleep(random.uniform(1, 2))

            # Click Post
            post_btn = WebDriverWait(poster.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                    "button.share-actions__primary-action, button[class*='primary-action']"))
            )
            poster.human.human_click(post_btn) if hasattr(poster, 'human') and poster.human else post_btn.click()

            time.sleep(random.uniform(3, 5))  # Wait for post

            logger.info(f"[POST] Successfully posted to group {LINKEDIN_GROUP_ID}")
            return True

        except Exception as e:
            logger.error(f"[SELENIUM] Post failed: {e}")
            return False


def search_openclaw_news(max_results: int = 10) -> List[NewsItem]:
    """
    Search for OpenClaw news using DuckDuckGo.

    Searches for:
    - OpenClaw updates, features, security
    - Related projects (lobster.cash, Crossmint)
    - New agents (Peeka, etc.)

    Args:
        max_results: Maximum number of results to return

    Returns:
        List of NewsItem objects
    """
    logger.info(f"[SEARCH] Searching for OpenClaw news (max={max_results})")

    # Search queries targeting OpenClaw ecosystem (reduced to avoid rate limits)
    search_queries = [
        "OpenClaw AI agent",
        "OpenClaw framework",
        "lobster.cash Crossmint",
    ]

    all_items: List[NewsItem] = []
    seen_urls: set = set()

    try:
        from duckduckgo_search import DDGS

        ddg = DDGS()

        for i, query in enumerate(search_queries):
            # Rate limit avoidance: delay between queries (2-4 seconds)
            if i > 0:
                delay = random.uniform(2.0, 4.0)
                logger.debug(f"[SEARCH] Rate limit delay: {delay:.1f}s")
                time.sleep(delay)

            try:
                # Search news specifically
                results = list(ddg.news(query, max_results=5, timelimit="m"))  # Last month

                for r in results:
                    url = r.get("url", "")
                    if url in seen_urls or not url:
                        continue
                    seen_urls.add(url)

                    # Parse date
                    pub_date = None
                    date_str = r.get("date", "")
                    if date_str:
                        try:
                            # DDG returns ISO format dates
                            pub_date = datetime.fromisoformat(date_str.replace("Z", "+00:00").split("+")[0])
                        except (ValueError, TypeError):
                            pass

                    item = NewsItem(
                        title=r.get("title", ""),
                        url=url,
                        source=r.get("source", "unknown"),
                        published_date=pub_date,
                        summary=r.get("body", ""),
                    )
                    all_items.append(item)
                    logger.debug(f"[SEARCH] Found: {item.title[:50]}... from {item.source}")

                    if len(all_items) >= max_results:
                        break

            except Exception as e:
                logger.warning(f"[SEARCH] Query '{query}' failed: {e}")
                continue

            if len(all_items) >= max_results:
                break

        # Also try general web search if news didn't find enough
        if len(all_items) < max_results // 2:
            time.sleep(random.uniform(2.0, 4.0))  # Rate limit delay
            try:
                # Try multiple web search queries
                web_queries = ["OpenClaw", "OpenClaw AI framework", "Peeka AI agent"]
                for wq in web_queries:
                    if len(all_items) >= max_results:
                        break
                    try:
                        results = list(ddg.text(wq, max_results=5))
                        for r in results:
                            url = r.get("href", r.get("link", ""))
                            if url in seen_urls or not url:
                                continue
                            seen_urls.add(url)

                            item = NewsItem(
                                title=r.get("title", ""),
                                url=url,
                                source=_extract_source(url),
                                summary=r.get("body", ""),
                            )
                            all_items.append(item)
                        time.sleep(random.uniform(1.0, 2.0))  # Delay between web queries
                    except Exception as e:
                        logger.debug(f"[SEARCH] Web query '{wq}' failed: {e}")
                        continue

            except Exception as e:
                logger.warning(f"[SEARCH] Web search fallback failed: {e}")

    except ImportError:
        logger.error("[SEARCH] duckduckgo-search not installed. Run: pip install duckduckgo-search")
        return []

    except Exception as e:
        logger.error(f"[SEARCH] Search failed: {e}")
        return []

    logger.info(f"[SEARCH] Found {len(all_items)} news items")
    return all_items[:max_results]


def _extract_source(url: str) -> str:
    """Extract source name from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        # Get main domain name
        parts = domain.split(".")
        if len(parts) >= 2:
            return parts[-2]  # e.g., "techcrunch" from "techcrunch.com"
        return domain
    except Exception:
        return "unknown"


def run_openclaw_news_flow(dry_run: bool = True) -> Dict:
    """
    Main execution flow for OpenClaw news posting.

    Args:
        dry_run: If True, don't actually post

    Returns:
        Dict with execution results
    """
    logger.info("[FLOW] Starting OpenClaw news flow")

    # 1. Search for news
    news_items = search_openclaw_news(max_results=10)

    if not news_items:
        logger.info("[FLOW] No news items found")
        return {"status": "no_news", "items_found": 0, "posted": False}

    # 2. Rate and filter
    rater = NewsRelevanceRater()
    rated_items = [(item, rater.rate(item)) for item in news_items]
    filtered = [(item, score) for item, score in rated_items if score >= RELEVANCE_THRESHOLD]

    logger.info(f"[FLOW] {len(news_items)} items found, {len(filtered)} passed threshold")

    if not filtered:
        return {"status": "below_threshold", "items_found": len(news_items), "posted": False}

    # 3. Post top item
    poster = OpenClawGroupPoster()
    top_item, score = max(filtered, key=lambda x: x[1])

    success = poster.post_to_group(top_item, dry_run=dry_run)

    return {
        "status": "posted" if success else "failed",
        "items_found": len(news_items),
        "items_filtered": len(filtered),
        "top_item": top_item.title,
        "top_score": score,
        "posted": success,
        "dry_run": dry_run
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # Test with dry run
    result = run_openclaw_news_flow(dry_run=True)
    print(f"\nResult: {result}")
