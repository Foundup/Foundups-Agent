"""
WSP 78: Distributed Module Database Protocol - Core Database Manager

One Database, Three Namespaces:
- modules.*     # All module data
- foundups.*    # Independent FoundUp projects
- agents.*      # Agent memory and state

This implements the unified database architecture for the entire FoundUps system.
"""

import sqlite3
import os
import json
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Single database manager for entire system (WSP 78).

    One database file with three namespaces:
    - modules.*     # Module-specific data
    - foundups.*    # FoundUp project data
    - agents.*      # Agent memory and learning
    """

    _instance: Optional['DatabaseManager'] = None
    _db_path = "data/foundups.db"

    def __new__(cls) -> 'DatabaseManager':
        """Singleton pattern for database manager"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self) -> None:
        """Initialize database with optimal settings"""
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        with self.get_connection() as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys=ON")
            # Set reasonable cache size
            conn.execute("PRAGMA cache_size=-64000")  # ~64MB cache

            logger.info("Database initialized with WAL mode and optimizations")

    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as dict list"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        result = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return len(result) > 0

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table"""
        return self.execute_query(f"PRAGMA table_info({table_name})")

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            with self.get_connection() as conn:
                # Use SQLite backup API for safe backup
                backup_conn = sqlite3.connect(backup_path)
                conn.backup(backup_conn)
                backup_conn.close()
                logger.info(f"Database backup created: {backup_path}")
                return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}

        # Get table counts
        tables = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )

        for table in tables:
            table_name = table['name']
            count = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
            stats[table_name] = count[0]['count'] if count else 0

        # Get database file size
        if os.path.exists(self._db_path):
            stats['file_size_bytes'] = os.path.getsize(self._db_path)
        else:
            stats['file_size_bytes'] = 0

        return stats
