"""
Breadcrumb Telemetry - Persistent storage for all DAE breadcrumbs

Module: communication/livechat
WSP Reference: WSP 91 (DAEmon Observability), WSP 77 (Agent Coordination)
Status: Production

This module provides centralized breadcrumb storage for all DAEs.
Similar to chat_telemetry_store.py but for system events.

Architecture:
    All DAEs → Breadcrumb Hub (this) → SQLite storage
                                      ↓
                              AI Overseer monitors
                                      ↓
                              Qwen/Gemma analyze patterns
                                      ↓
                              Critical alerts → Send to chat

Key Insight: "livestream is not always running" → Breadcrumbs need PERSISTENT storage
"""

import sqlite3
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)


class BreadcrumbTelemetry:
    """
    Persistent storage for all DAE breadcrumbs.

    Stores breadcrumbs from:
        - comment_engagement_dae
        - livechat_core
        - party_reactor
        - ai_overseer
        - youtube_shorts
        - Any future DAEs

    Enables:
        - WRE learning (breadcrumbs = training data)
        - AI Overseer pattern detection
        - 0102 troubleshooting
        - Community alerts
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize breadcrumb telemetry store.

        Args:
            db_path: Override default database path (for testing)
        """
        if db_path is None:
            self.db_path = Path("modules/communication/livechat/memory/breadcrumb_telemetry.db")
        else:
            self.db_path = db_path

        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()
        logger.info(f"[BREADCRUMB-TELEMETRY] Initialized: {self.db_path}")

    def _init_db(self):
        """Create breadcrumbs table if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS breadcrumbs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source_dae TEXT NOT NULL,
                phase TEXT,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                metadata TEXT,
                session_id TEXT
            )
        ''')

        # Index for fast pattern queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON breadcrumbs(timestamp)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_event_type
            ON breadcrumbs(event_type)
        ''')

        conn.commit()
        conn.close()

    def store_breadcrumb(
        self,
        source_dae: str,
        event_type: str,
        message: str,
        phase: Optional[str] = None,
        metadata: Optional[Dict] = None,
        session_id: Optional[str] = None
    ):
        """
        Store breadcrumb from any DAE.

        Args:
            source_dae: DAE name (e.g., 'comment_engagement', 'livechat', 'party_reactor')
            event_type: Event classification (e.g., 'no_comments', 'navigation', 'wsp_violation')
            message: Human-readable message
            phase: Optional phase identifier (e.g., 'PHASE-1', 'DAE-NAV')
            metadata: Optional JSON-serializable context
            session_id: Optional session identifier for grouping

        Example:
            >>> telemetry = BreadcrumbTelemetry()
            >>> telemetry.store_breadcrumb(
            ...     source_dae='comment_engagement',
            ...     phase='PHASE-2',
            ...     event_type='no_comments_detected',
            ...     message='Inbox cleared via Occam detection',
            ...     metadata={'comment_count': 0, 'detection_method': 'DOM'}
            ... )
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO breadcrumbs (timestamp, source_dae, phase, event_type, message, metadata, session_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    datetime.now().isoformat(),
                    source_dae,
                    phase,
                    event_type,
                    message,
                    json.dumps(metadata or {}),
                    session_id
                )
            )

            conn.commit()
            conn.close()

            logger.debug(f"[BREADCRUMB] {source_dae}/{event_type}: {message}")

        except Exception as e:
            logger.error(f"[BREADCRUMB-TELEMETRY] Failed to store breadcrumb: {e}")

    def get_recent_breadcrumbs(
        self,
        minutes: int = 5,
        source_dae: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve recent breadcrumbs.

        Args:
            minutes: Time window to search
            source_dae: Filter by DAE source
            event_type: Filter by event type

        Returns:
            List of breadcrumb dicts with keys: id, timestamp, source_dae, phase, event_type, message, metadata
        """
        try:
            cutoff = datetime.now() - timedelta(minutes=minutes)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT id, timestamp, source_dae, phase, event_type, message, metadata " \
                    "FROM breadcrumbs WHERE timestamp >= ?"
            params = [cutoff.isoformat()]

            if source_dae:
                query += " AND source_dae = ?"
                params.append(source_dae)

            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)

            query += " ORDER BY timestamp DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            breadcrumbs = []
            for row in rows:
                breadcrumbs.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'source_dae': row[2],
                    'phase': row[3],
                    'event_type': row[4],
                    'message': row[5],
                    'metadata': json.loads(row[6]) if row[6] else {}
                })

            return breadcrumbs

        except Exception as e:
            logger.error(f"[BREADCRUMB-TELEMETRY] Failed to retrieve breadcrumbs: {e}")
            return []

    def get_repeated_patterns(
        self,
        minutes: int = 5,
        min_occurrences: int = 2
    ) -> List[Tuple[str, str, str, int]]:
        """
        Detect repeated patterns for AI Overseer analysis.

        Args:
            minutes: Time window to analyze
            min_occurrences: Minimum repetitions to qualify as pattern

        Returns:
            List of tuples: (source_dae, event_type, message, count)

        Example:
            >>> patterns = telemetry.get_repeated_patterns(minutes=5, min_occurrences=3)
            >>> for source, event, msg, count in patterns:
            ...     print(f"{source}/{event} repeated {count}x: {msg}")
        """
        try:
            cutoff = datetime.now() - timedelta(minutes=minutes)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT source_dae, event_type, message, COUNT(*) as count "
                "FROM breadcrumbs WHERE timestamp >= ? "
                "GROUP BY source_dae, event_type, message "
                "HAVING count >= ? "
                "ORDER BY count DESC",
                (cutoff.isoformat(), min_occurrences)
            )

            patterns = cursor.fetchall()
            conn.close()

            return patterns

        except Exception as e:
            logger.error(f"[BREADCRUMB-TELEMETRY] Failed to detect patterns: {e}")
            return []

    def get_event_count(
        self,
        event_type: str,
        minutes: int = 5,
        source_dae: Optional[str] = None
    ) -> int:
        """
        Count occurrences of specific event type.

        Args:
            event_type: Event to count
            minutes: Time window
            source_dae: Optional filter by DAE

        Returns:
            Count of events
        """
        try:
            cutoff = datetime.now() - timedelta(minutes=minutes)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if source_dae:
                cursor.execute(
                    "SELECT COUNT(*) FROM breadcrumbs "
                    "WHERE timestamp >= ? AND event_type = ? AND source_dae = ?",
                    (cutoff.isoformat(), event_type, source_dae)
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) FROM breadcrumbs "
                    "WHERE timestamp >= ? AND event_type = ?",
                    (cutoff.isoformat(), event_type)
                )

            count = cursor.fetchone()[0]
            conn.close()

            return count

        except Exception as e:
            logger.error(f"[BREADCRUMB-TELEMETRY] Failed to count events: {e}")
            return 0

    def clear_old_breadcrumbs(self, days: int = 7):
        """
        Clean up old breadcrumbs (WRE learning retention).

        Args:
            days: Keep breadcrumbs newer than N days

        Returns:
            Number of breadcrumbs deleted
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM breadcrumbs WHERE timestamp < ?",
                (cutoff.isoformat(),)
            )

            deleted = cursor.rowcount
            conn.commit()
            conn.close()

            logger.info(f"[BREADCRUMB-TELEMETRY] Cleaned up {deleted} old breadcrumbs (>{days} days)")
            return deleted

        except Exception as e:
            logger.error(f"[BREADCRUMB-TELEMETRY] Failed to clean up: {e}")
            return 0


# Singleton instance for module-level access
_telemetry_instance = None


def get_breadcrumb_telemetry() -> BreadcrumbTelemetry:
    """Get or create singleton breadcrumb telemetry instance."""
    global _telemetry_instance
    if _telemetry_instance is None:
        _telemetry_instance = BreadcrumbTelemetry()
    return _telemetry_instance


# CLI test interface
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    telemetry = BreadcrumbTelemetry()

    # Test 1: Store sample breadcrumbs
    print("\n=== Test 1: Store breadcrumbs ===")
    telemetry.store_breadcrumb(
        source_dae='comment_engagement',
        phase='PHASE-1',
        event_type='no_comments_detected',
        message='Inbox cleared via Occam detection',
        metadata={'comment_count': 0, 'detection_method': 'DOM'}
    )

    telemetry.store_breadcrumb(
        source_dae='party_reactor',
        event_type='party_triggered',
        message='Party started (10 reactions)',
        metadata={'click_count': 10, 'user': 'TestUser'}
    )

    # Test 2: Retrieve recent breadcrumbs
    print("\n=== Test 2: Recent breadcrumbs ===")
    recent = telemetry.get_recent_breadcrumbs(minutes=5)
    for bc in recent:
        print(f"  [{bc['source_dae']}] {bc['event_type']}: {bc['message']}")

    # Test 3: Create artificial pattern
    print("\n=== Test 3: Detect patterns ===")
    for i in range(5):
        telemetry.store_breadcrumb(
            source_dae='ai_overseer',
            event_type='wsp_violation',
            message='Module holo_dae missing: README.md'
        )

    patterns = telemetry.get_repeated_patterns(minutes=5, min_occurrences=3)
    for source, event, msg, count in patterns:
        print(f"  PATTERN: {source}/{event} ({count}x) - {msg}")

    # Test 4: Event count
    print("\n=== Test 4: Event count ===")
    count = telemetry.get_event_count('wsp_violation', minutes=5)
    print(f"  WSP violations in last 5min: {count}")
