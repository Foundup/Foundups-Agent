#!/usr/bin/env python3
"""
Migrate agent_permissions JSONL files to SQLite

Migrates:
- permission_events.jsonl → foundup.db:permission_events table
- confidence_events.jsonl → foundup.db:confidence_events table

WSP Compliance:
- WSP 15 (MPS): P0 Critical priority (MPS 16)
- WSP 50 (Pre-Action): Validates data before migration
- WSP 22 (ModLog): Logs migration results
"""

import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
MEMORY_DIR = REPO_ROOT / "modules/ai_intelligence/agent_permissions/memory"
DB_PATH = REPO_ROOT / "data/foundup.db"

PERMISSION_JSONL = MEMORY_DIR / "permission_events.jsonl"
CONFIDENCE_JSONL = MEMORY_DIR / "confidence_events.jsonl"


def read_jsonl(file_path: Path) -> List[Dict]:
    """Read JSONL file and return list of events"""
    events = []
    if not file_path.exists():
        logger.warning(f"[SKIP] {file_path} does not exist")
        return events

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                event = json.loads(line.strip())
                events.append(event)
            except json.JSONDecodeError as e:
                logger.error(f"[ERROR] Line {line_num} in {file_path}: {e}")
                continue

    logger.info(f"[OK] Read {len(events)} events from {file_path.name}")
    return events


def migrate_permission_events(conn: sqlite3.Connection) -> Tuple[int, int]:
    """Migrate permission_events.jsonl to SQLite"""
    events = read_jsonl(PERMISSION_JSONL)
    if not events:
        return 0, 0

    migrated = 0
    failed = 0

    for event in events:
        try:
            conn.execute('''
                INSERT INTO permission_events (
                    agent_id, event_type, permission_level, granted_at,
                    granted_by, confidence, justification, approval_signature,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('agent_id'),
                event.get('event_type'),
                event.get('permission'),
                event.get('granted_at'),
                event.get('granted_by'),
                event.get('confidence_at_grant'),
                event.get('justification'),
                event.get('approval_signature'),
                json.dumps(event.get('metadata', {}))
            ))
            migrated += 1
        except Exception as e:
            logger.error(f"[ERROR] Failed to migrate permission event: {e}")
            failed += 1

    conn.commit()
    logger.info(f"[OK] Migrated {migrated} permission events ({failed} failed)")
    return migrated, failed


def migrate_confidence_events(conn: sqlite3.Connection) -> Tuple[int, int]:
    """Migrate confidence_events.jsonl to SQLite"""
    events = read_jsonl(CONFIDENCE_JSONL)
    if not events:
        return 0, 0

    migrated = 0
    failed = 0

    for event in events:
        try:
            conn.execute('''
                INSERT INTO confidence_events (
                    agent_id, confidence_before, confidence_after,
                    event_type, success, validation, recorded_at,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('agent_id'),
                event.get('confidence_before'),
                event.get('confidence_after'),
                event.get('event_type'),
                event.get('success'),
                event.get('validation'),
                event.get('timestamp'),
                json.dumps(event.get('details', {}))
            ))
            migrated += 1
        except Exception as e:
            logger.error(f"[ERROR] Failed to migrate confidence event: {e}")
            failed += 1

    conn.commit()
    logger.info(f"[OK] Migrated {migrated} confidence events ({failed} failed)")
    return migrated, failed


def log_migration(conn: sqlite3.Connection, domain: str, files: int, records: int, success: bool):
    """Log migration to migration_log table"""
    conn.execute('''
        INSERT INTO migration_log (
            domain, jsonl_files_migrated, records_migrated,
            started_at, completed_at, status
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        domain,
        files,
        records,
        datetime.now().isoformat(),
        datetime.now().isoformat(),
        'completed' if success else 'failed'
    ))
    conn.commit()


def main():
    """Run migration"""
    logger.info("=" * 80)
    logger.info("[MIGRATION] agent_permissions JSONL → SQLite")
    logger.info("=" * 80)

    # Connect to database
    if not DB_PATH.exists():
        logger.error(f"[ERROR] Database not found: {DB_PATH}")
        logger.error("Run: python -c 'from pathlib import Path; ... create schema'")
        return 1

    conn = sqlite3.connect(DB_PATH)

    try:
        # Migrate permissions
        logger.info("\n[STEP 1] Migrating permission_events.jsonl...")
        perm_migrated, perm_failed = migrate_permission_events(conn)

        # Migrate confidence
        logger.info("\n[STEP 2] Migrating confidence_events.jsonl...")
        conf_migrated, conf_failed = migrate_confidence_events(conn)

        # Log migration
        total_migrated = perm_migrated + conf_migrated
        total_failed = perm_failed + conf_failed
        success = total_failed == 0

        log_migration(conn, 'agent_permissions', 2, total_migrated, success)

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("[SUMMARY] Migration Complete")
        logger.info("=" * 80)
        logger.info(f"  Permission events: {perm_migrated} migrated ({perm_failed} failed)")
        logger.info(f"  Confidence events: {conf_migrated} migrated ({conf_failed} failed)")
        logger.info(f"  Total: {total_migrated} records migrated")
        logger.info(f"  Status: {'SUCCESS' if success else 'PARTIAL (some failures)'}")
        logger.info("\n[NEXT] Update agent_permissions to write to SQLite instead of JSONL")

        return 0 if success else 1

    finally:
        conn.close()


if __name__ == '__main__':
    exit(main())
