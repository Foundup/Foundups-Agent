#!/usr/bin/env python3
"""
WRE Skills Metrics Ingestion
Batch ingestion from JSON append-only files to SQLite for analytics
WSP Compliance: WSP 77 (Agent Coordination), WSP 91 (DAEMON Observability)
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import argparse

logger = logging.getLogger(__name__)


class MetricsIngestor:
    """
    Batch ingestion engine for WRE skills metrics

    Reads newline-delimited JSON files and ingests into SQLite for analytics.
    Tracks ingestion watermarks to avoid duplicate processing.
    """

    def __init__(self, sqlite_path: Optional[Path] = None, json_dir: Optional[Path] = None):
        """
        Initialize metrics ingestor

        Args:
            sqlite_path: Path to SQLite database (defaults to skills/skills_metrics.db)
            json_dir: Directory containing JSON metrics files (defaults to recursive_improvement/metrics/)
        """
        if sqlite_path is None:
            self.sqlite_path = Path(__file__).parent / "skills_metrics.db"
        else:
            self.sqlite_path = Path(sqlite_path)

        if json_dir is None:
            self.json_dir = Path(__file__).parent.parent / "recursive_improvement" / "metrics"
        else:
            self.json_dir = Path(json_dir)

        self.conn = None
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create SQLite schema if it doesn't exist"""
        self.conn = sqlite3.connect(str(self.sqlite_path))
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Skills registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                skill_id TEXT PRIMARY KEY,
                skill_name TEXT NOT NULL,
                promotion_state TEXT NOT NULL,
                primary_agent TEXT NOT NULL,
                intent_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_promoted_at TIMESTAMP,
                version TEXT DEFAULT '1.0'
            )
        """)

        # Execution metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_metrics (
                execution_id TEXT PRIMARY KEY,
                skill_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                pattern_fidelity REAL,
                outcome_quality REAL,
                execution_time_ms INTEGER,
                patterns_followed INTEGER,
                patterns_missed INTEGER,
                decision TEXT,
                expected_decision TEXT,
                correct BOOLEAN,
                exception BOOLEAN,
                agent TEXT NOT NULL,
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
            )
        """)

        # Promotion events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promotion_events (
                event_id TEXT PRIMARY KEY,
                skill_id TEXT NOT NULL,
                from_state TEXT NOT NULL,
                to_state TEXT NOT NULL,
                approver TEXT,
                approval_ticket TEXT,
                timestamp TIMESTAMP NOT NULL,
                reason TEXT,
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
            )
        """)

        # Rollback events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rollback_events (
                event_id TEXT PRIMARY KEY,
                skill_id TEXT NOT NULL,
                from_state TEXT NOT NULL,
                to_state TEXT NOT NULL,
                trigger_reason TEXT NOT NULL,
                trigger_metric TEXT,
                timestamp TIMESTAMP NOT NULL,
                automated BOOLEAN,
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
            )
        """)

        # Ingestion watermarks (track what's been ingested)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_watermarks (
                file_name TEXT PRIMARY KEY,
                last_ingested_line INTEGER DEFAULT 0,
                last_ingested_timestamp REAL,
                last_ingestion_run TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes for query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_skill ON execution_metrics(skill_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_timestamp ON execution_metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_promotion_skill ON promotion_events(skill_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rollback_skill ON rollback_events(skill_id)")

        self.conn.commit()
        logger.info(f"[METRICS-DB] Schema ensured: {self.sqlite_path}")

    def ingest_all(self, batch_size: int = 1000) -> Dict[str, int]:
        """
        Ingest all new metrics from JSON files

        Args:
            batch_size: Number of records to ingest per transaction

        Returns:
            Dict with ingestion counts per metric type
        """
        stats = {
            "fidelity": 0,
            "outcomes": 0,
            "performance": 0,
            "promotions": 0,
            "rollbacks": 0
        }

        # Ingest fidelity metrics
        for filepath in self.json_dir.glob("*_fidelity.json"):
            count = self._ingest_file(filepath, "fidelity", batch_size)
            stats["fidelity"] += count

        # Ingest outcome metrics
        for filepath in self.json_dir.glob("*_outcomes.json"):
            count = self._ingest_file(filepath, "outcomes", batch_size)
            stats["outcomes"] += count

        # Ingest performance metrics
        for filepath in self.json_dir.glob("*_performance.json"):
            count = self._ingest_file(filepath, "performance", batch_size)
            stats["performance"] += count

        # Ingest promotion/rollback events
        for filepath in self.json_dir.glob("*_promotion_log.json"):
            count = self._ingest_file(filepath, "promotion_log", batch_size)
            # Distinguish promotions vs rollbacks in the file
            stats["promotions"] += count  # Approximation
            stats["rollbacks"] += 0  # Both in same file

        logger.info(f"[METRICS-INGEST] Ingestion complete: {stats}")
        return stats

    def _ingest_file(self, filepath: Path, metric_type: str, batch_size: int) -> int:
        """
        Ingest metrics from a single JSON file

        Args:
            filepath: Path to JSON metrics file
            metric_type: Type of metrics (fidelity, outcomes, performance, promotion_log)
            batch_size: Batch size for transactions

        Returns:
            Number of records ingested
        """
        if not filepath.exists():
            return 0

        filename = filepath.name

        # Get watermark (last ingested line)
        cursor = self.conn.cursor()
        cursor.execute("SELECT last_ingested_line FROM ingestion_watermarks WHERE file_name = ?", (filename,))
        row = cursor.fetchone()
        watermark = row[0] if row else 0

        # Read new lines only
        new_metrics = []
        current_line = 0

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    current_line += 1
                    if current_line <= watermark:
                        continue  # Skip already ingested

                    if line.strip():
                        try:
                            metric = json.loads(line)
                            new_metrics.append((current_line, metric))
                        except json.JSONDecodeError as e:
                            logger.warning(f"[METRICS-INGEST] Malformed JSON in {filename} line {current_line}: {e}")
        except Exception as e:
            logger.error(f"[METRICS-INGEST] Failed to read {filename}: {e}")
            return 0

        if not new_metrics:
            return 0

        # Batch ingest
        ingested_count = 0
        for i in range(0, len(new_metrics), batch_size):
            batch = new_metrics[i:i + batch_size]
            self._ingest_batch(batch, metric_type)
            ingested_count += len(batch)

        # Update watermark
        last_line = new_metrics[-1][0]
        cursor.execute("""
            INSERT OR REPLACE INTO ingestion_watermarks (file_name, last_ingested_line, last_ingested_timestamp, last_ingestion_run)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (filename, last_line, time.time()))
        self.conn.commit()

        logger.info(f"[METRICS-INGEST] Ingested {ingested_count} records from {filename}")
        return ingested_count

    def _ingest_batch(self, batch: List[tuple], metric_type: str) -> None:
        """
        Ingest a batch of metrics into SQLite

        Args:
            batch: List of (line_number, metric_dict) tuples
            metric_type: Type of metrics
        """
        cursor = self.conn.cursor()

        for _, metric in batch:
            try:
                if metric_type == "fidelity":
                    self._ingest_fidelity_metric(cursor, metric)
                elif metric_type == "outcomes":
                    self._ingest_outcome_metric(cursor, metric)
                elif metric_type == "performance":
                    self._ingest_performance_metric(cursor, metric)
                elif metric_type == "promotion_log":
                    if metric.get("event_type") == "promotion":
                        self._ingest_promotion_event(cursor, metric)
                    elif metric.get("event_type") == "rollback":
                        self._ingest_rollback_event(cursor, metric)
            except Exception as e:
                logger.warning(f"[METRICS-INGEST] Failed to ingest metric: {e}")
                # Continue with next metric

        self.conn.commit()

    def _ingest_fidelity_metric(self, cursor, metric: Dict) -> None:
        """Ingest fidelity metric into execution_metrics table"""
        cursor.execute("""
            INSERT OR REPLACE INTO execution_metrics (
                execution_id, skill_id, timestamp, pattern_fidelity,
                patterns_followed, patterns_missed, agent, exception
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metric["execution_id"],
            metric["skill_name"],
            metric["timestamp"],
            metric["pattern_fidelity"],
            metric["patterns_followed"],
            metric["patterns_missed"],
            metric["agent"],
            False
        ))

    def _ingest_outcome_metric(self, cursor, metric: Dict) -> None:
        """Ingest outcome metric into execution_metrics table"""
        cursor.execute("""
            INSERT OR REPLACE INTO execution_metrics (
                execution_id, skill_id, timestamp, decision, expected_decision,
                correct, agent, exception
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metric["execution_id"],
            metric["skill_name"],
            metric["timestamp"],
            metric["decision"],
            metric.get("expected_decision"),
            metric["correct"],
            metric["agent"],
            False
        ))

    def _ingest_performance_metric(self, cursor, metric: Dict) -> None:
        """Ingest performance metric into execution_metrics table"""
        cursor.execute("""
            INSERT OR REPLACE INTO execution_metrics (
                execution_id, skill_id, timestamp, execution_time_ms,
                exception, agent
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            metric["execution_id"],
            metric["skill_name"],
            metric["timestamp"],
            metric["execution_time_ms"],
            metric["exception_occurred"],
            metric["agent"]
        ))

    def _ingest_promotion_event(self, cursor, event: Dict) -> None:
        """Ingest promotion event"""
        cursor.execute("""
            INSERT OR REPLACE INTO promotion_events (
                event_id, skill_id, from_state, to_state, approver,
                approval_ticket, timestamp, reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event["event_id"],
            event["skill_name"],
            event["from_state"],
            event["to_state"],
            event["approver"],
            event["approval_ticket"],
            event["timestamp"],
            event["reason"]
        ))

    def _ingest_rollback_event(self, cursor, event: Dict) -> None:
        """Ingest rollback event"""
        cursor.execute("""
            INSERT OR REPLACE INTO rollback_events (
                event_id, skill_id, from_state, to_state, trigger_reason,
                trigger_metric, timestamp, automated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event["event_id"],
            event["skill_name"],
            event["from_state"],
            event["to_state"],
            event["trigger_reason"],
            event["trigger_metric"],
            event["timestamp"],
            event["automated"]
        ))

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """CLI entry point for metrics ingestion"""
    parser = argparse.ArgumentParser(description="Ingest WRE skills metrics from JSON to SQLite")
    parser.add_argument("--json-path", type=str, help="Path to JSON metrics directory")
    parser.add_argument("--sqlite-db", type=str, help="Path to SQLite database")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for ingestion")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

    # Initialize ingestor
    ingestor = MetricsIngestor(
        sqlite_path=Path(args.sqlite_db) if args.sqlite_db else None,
        json_dir=Path(args.json_path) if args.json_path else None
    )

    # Run ingestion
    start_time = time.time()
    stats = ingestor.ingest_all(batch_size=args.batch_size)
    elapsed = time.time() - start_time

    print(f"\n[OK] Ingestion complete in {elapsed:.2f}s")
    print(f"  Fidelity metrics: {stats['fidelity']}")
    print(f"  Outcome metrics: {stats['outcomes']}")
    print(f"  Performance metrics: {stats['performance']}")
    print(f"  Promotion events: {stats['promotions']}")
    print(f"  Rollback events: {stats['rollbacks']}")
    print(f"  Total: {sum(stats.values())}")

    ingestor.close()


if __name__ == "__main__":
    main()
