#!/usr/bin/env python3
"""
Violation Tracking System for HoloIndex
Provides structured storage and querying of WSP violations
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class Violation:
    """Represents a WSP violation record."""
    id: str
    timestamp: datetime
    wsp: str  # Changed from wsp_number
    module: str  # Changed from module_path
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    agent: str  # Changed from agent_id
    remediation_status: str = "pending"
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        if self.metadata:
            result['metadata'] = json.dumps(self.metadata)
        return result

    @classmethod
    def from_row(cls, row: tuple) -> 'Violation':
        """Create from database row."""
        return cls(
            id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            wsp=row[2],  # Changed from wsp_number
            module=row[3],  # Changed from module_path
            severity=row[4],
            description=row[5],
            agent=row[6],  # Changed from agent_id
            remediation_status=row[7],
            metadata=json.loads(row[8]) if row[8] else None  # Adjusted index
        )


class ViolationTracker:
    """Manages WSP violation storage and retrieval."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize violation tracker with database."""
        # Use WSP 78 unified database instead of separate file
        from modules.infrastructure.database.src.db_manager import DatabaseManager

        self.db_manager = DatabaseManager()
        self.conn = None  # Will use db_manager's connection
        self._create_tables()

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        with self.db_manager.get_connection() as conn:
            # Use WSP 78 namespace: modules_holo_index_violations
            conn.execute("""
                CREATE TABLE IF NOT EXISTS modules_holo_index_violations (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    wsp TEXT NOT NULL,
                    module TEXT NOT NULL,
                    severity TEXT CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
                    description TEXT,
                    agent TEXT,
                    remediation_status TEXT DEFAULT 'pending',
                    metadata JSON
                )
            """)

            # Create indexes for efficient querying
            conn.execute("CREATE INDEX IF NOT EXISTS idx_holo_violations_module ON modules_holo_index_violations(module)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_holo_violations_wsp ON modules_holo_index_violations(wsp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_holo_violations_severity ON modules_holo_index_violations(severity)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_holo_violations_timestamp ON modules_holo_index_violations(timestamp)")

    def record_violation(self, violation: Violation) -> None:
        """Record a new violation."""
        data = violation.to_dict()
        with self.db_manager.get_connection() as conn:
            conn.execute("""
                INSERT INTO modules_holo_index_violations
                (id, timestamp, wsp, module, severity, description,
                 agent, remediation_status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['id'],
                data['timestamp'],
                data['wsp'],  # Updated field name
                data['module'],  # Updated field name
                data['severity'],
                data['description'],
                data['agent'],  # Updated field name
                data['remediation_status'],
                data.get('metadata')
            ))

    def record_health_violation(self, module_path: str, line_count: int,
                               severity: str, wsp: str = "WSP 87") -> None:
        """Convenience method to record health violations."""
        violation_id = f"v-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{Path(module_path).stem}"

        if line_count > 1500:
            description = f"CRITICAL: File has {line_count} lines (mandatory split required)"
        elif line_count > 1000:
            description = f"File exceeds guideline ({line_count} lines, limit 1000)"
        else:
            description = f"File approaching limit ({line_count} lines)"

        violation = Violation(
            id=violation_id,
            timestamp=datetime.now(timezone.utc),
            wsp=wsp,  # Updated field name
            module=module_path,  # Updated field name
            severity=severity,
            description=description,
            agent="0102",  # Updated field name
            metadata={"line_count": line_count}
        )

        self.record_violation(violation)

    def get_violations_by_module(self, module_path: str) -> List[Violation]:
        """Get all violations for a specific module."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM modules_holo_index_violations
                WHERE module = ?
                ORDER BY timestamp DESC
            """, (module_path,))

            return [Violation.from_row(row) for row in cursor.fetchall()]

    def get_violations_by_severity(self, severity: str) -> List[Violation]:
        """Get all violations of a specific severity."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM modules_holo_index_violations
                WHERE severity = ?
                ORDER BY timestamp DESC
            """, (severity,))

            return [Violation.from_row(row) for row in cursor.fetchall()]

    def get_pending_violations(self) -> List[Violation]:
        """Get all violations pending remediation."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM modules_holo_index_violations
                WHERE remediation_status = 'pending'
                ORDER BY severity DESC, timestamp DESC
            """)

            return [Violation.from_row(row) for row in cursor.fetchall()]

    def get_all_violations(self) -> List[Violation]:
        """Get all violations."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM modules_holo_index_violations
                ORDER BY timestamp DESC
            """)

            return [Violation.from_row(row) for row in cursor.fetchall()]

    def mark_remediated(self, violation_id: str) -> None:
        """Mark a violation as remediated."""
        with self.db_manager.get_connection() as conn:
            conn.execute("""
                UPDATE modules_holo_index_violations
                SET remediation_status = 'remediated'
                WHERE id = ?
            """, (violation_id,))

    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary statistics of violations."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical,
                    SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) as high,
                    SUM(CASE WHEN severity = 'MEDIUM' THEN 1 ELSE 0 END) as medium,
                    SUM(CASE WHEN severity = 'LOW' THEN 1 ELSE 0 END) as low,
                    SUM(CASE WHEN remediation_status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN remediation_status = 'remediated' THEN 1 ELSE 0 END) as remediated
                FROM modules_holo_index_violations
            """)

            row = cursor.fetchone()
            if row:
                return {
                    "total": row[0],
                    "by_severity": {
                        "critical": row[1] or 0,
                        "high": row[2] or 0,
                        "medium": row[3] or 0,
                        "low": row[4] or 0
                    },
                    "by_status": {
                        "pending": row[5] or 0,
                        "remediated": row[6] or 0
                    }
                }
            else:
                return {
                    "total": 0,
                    "by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                    "by_status": {"pending": 0, "remediated": 0}
                }

    def export_to_jsonl(self, output_path: Path) -> None:
        """Export violations to JSONL format."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM modules_holo_index_violations ORDER BY timestamp")

        with open(output_path, 'w') as f:
            for row in cursor:
                violation = Violation.from_row(row)
                f.write(json.dumps(violation.to_dict()) + '\n')

    def import_from_jsonl(self, input_path: Path) -> int:
        """Import violations from JSONL file."""
        count = 0
        with open(input_path, 'r') as f:
            for line in f:
                data = json.loads(line.strip())
                violation = Violation(
                    id=data['id'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    wsp_number=data['wsp_number'],
                    module_path=data['module_path'],
                    severity=data['severity'],
                    description=data['description'],
                    agent_id=data['agent_id'],
                    remediation_status=data.get('remediation_status', 'pending'),
                    remediation_date=datetime.fromisoformat(data['remediation_date'])
                                   if data.get('remediation_date') else None,
                    metadata=data.get('metadata')
                )
                try:
                    self.record_violation(violation)
                    count += 1
                except sqlite3.IntegrityError:
                    # Skip duplicates
                    pass

        return count

    def close(self) -> None:
        """Close method for compatibility - DatabaseManager handles connections."""
        # DatabaseManager handles connection lifecycle automatically
        pass


# CLI for testing and management
if __name__ == "__main__":
    import sys

    tracker = ViolationTracker()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python violation_tracker.py summary")
        print("  python violation_tracker.py pending")
        print("  python violation_tracker.py export <file.jsonl>")
        print("  python violation_tracker.py import <file.jsonl>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "summary":
        summary = tracker.get_violation_summary()
        print(f"Total violations: {summary['total']}")
        print(f"By severity: {summary['by_severity']}")
        print(f"By status: {summary['by_status']}")

    elif command == "pending":
        violations = tracker.get_pending_violations()
        for v in violations[:10]:  # Show first 10
            print(f"[{v.severity}] {v.module_path}: {v.description}")

    elif command == "export" and len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
        tracker.export_to_jsonl(output_path)
        print(f"Exported to {output_path}")

    elif command == "import" and len(sys.argv) > 2:
        input_path = Path(sys.argv[2])
        count = tracker.import_from_jsonl(input_path)
        print(f"Imported {count} violations")

    tracker.close()