#!/usr/bin/env python3
"""
WSP 78: Agent Memory Database
Shared agent memory and state management.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from .db_manager import DatabaseManager


class AgentDB:
    """
    Shared agent memory and state (WSP 78).

    Provides:
    - Agent awakening states
    - Shared memory patterns
    - Error learning (WSP 48)
    """

    def __init__(self):
        """Initialize agent database."""
        self.db = DatabaseManager()
        self._init_tables()

    def _init_tables(self) -> None:
        """Create agent database tables."""
        with self.db.get_connection() as conn:
            # Agent awakening states
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_awakening (
                    agent_id TEXT PRIMARY KEY,
                    consciousness_level TEXT,
                    last_koan TEXT,
                    awakening_timestamp DATETIME
                )
            ''')

            # Shared memory patterns
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    pattern_type TEXT,
                    pattern_data JSON,
                    learned_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Error learning (WSP 48)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_hash TEXT UNIQUE,
                    error_type TEXT,
                    solution JSON,
                    occurrences INTEGER DEFAULT 1
                )
            ''')

    def record_awakening(self, agent_id: str, consciousness_level: str, koan: str = None) -> None:
        """Record agent awakening state."""
        with self.db.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO agents_awakening
                (agent_id, consciousness_level, last_koan, awakening_timestamp)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, consciousness_level, koan, datetime.now().isoformat()))

    def get_awakening_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get awakening state for agent."""
        result = self.db.execute_query('''
            SELECT * FROM agents_awakening WHERE agent_id = ?
        ''', (agent_id,))

        if result:
            return dict(result[0])
        return None

    def learn_pattern(self, agent_id: str, pattern_type: str, pattern_data: Dict[str, Any]) -> int:
        """Store a learned pattern."""
        return self.db.execute_write('''
            INSERT INTO agents_memory (agent_id, pattern_type, pattern_data)
            VALUES (?, ?, ?)
        ''', (agent_id, pattern_type, json.dumps(pattern_data)))

    def get_patterns(self, agent_id: str = None, pattern_type: str = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve learned patterns."""
        query = "SELECT * FROM agents_memory WHERE 1=1"
        params = []

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)

        query += " ORDER BY learned_at DESC LIMIT ?"
        params.append(limit)

        return self.db.execute_query(query, tuple(params))

    def record_error(self, error_hash: str, error_type: str, solution: Dict[str, Any]) -> None:
        """Record error learning (WSP 48)."""
        with self.db.get_connection() as conn:
            # Try to update existing error
            updated = conn.execute('''
                UPDATE agents_errors
                SET occurrences = occurrences + 1
                WHERE error_hash = ?
            ''', (error_hash,)).rowcount

            # If no existing error, insert new one
            if updated == 0:
                conn.execute('''
                    INSERT INTO agents_errors
                    (error_hash, error_type, solution, occurrences)
                    VALUES (?, ?, ?, 1)
                ''', (error_hash, error_type, json.dumps(solution)))

    def get_error_solution(self, error_hash: str) -> Optional[Dict[str, Any]]:
        """Get solution for error."""
        result = self.db.execute_query('''
            SELECT * FROM agents_errors WHERE error_hash = ?
        ''', (error_hash,))

        if result:
            row = dict(result[0])
            row['solution'] = json.loads(row['solution'])
            return row
        return None
