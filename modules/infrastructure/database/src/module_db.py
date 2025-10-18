# -*- coding: utf-8 -*-
import sys
import io


"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

WSP 78: Module Database Base Class

Each module gets its own database tables with automatic prefixing:
modules_{module_name}_{table_name}

This provides isolation while keeping everything in one database.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class ModuleDB:
    """
    Base database class for modules (WSP 78).

    Automatically prefixes all tables with: modules_{module_name}_

    Example:
        chat_rules = ModuleDB("chat_rules")
        # Creates tables like: modules_chat_rules_moderators
    """

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.db = DatabaseManager()
        self.table_prefix = f"modules_{module_name}_"
        self._init_tables()

    def _init_tables(self) -> None:
        """Initialize module-specific tables. Override in subclasses."""
        pass

    def _get_full_table_name(self, table_name: str) -> str:
        """Get the full table name with prefix"""
        return f"{self.table_prefix}{table_name}"

    def create_table(self, table_name: str, schema: str) -> None:
        """Create a module table with the given schema"""
        full_table = self._get_full_table_name(table_name)
        query = f"CREATE TABLE IF NOT EXISTS {full_table} ({schema})"

        try:
            self.db.execute_write(query)
            logger.debug(f"Created table: {full_table}")
        except Exception as e:
            logger.error(f"Failed to create table {full_table}: {e}")
            raise

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """Insert a record into a module table"""
        full_table = self._get_full_table_name(table_name)

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())

        query = f"INSERT INTO {full_table} ({columns}) VALUES ({placeholders})"
        return self.db.execute_write(query, values)

    def update(self, table_name: str, data: Dict[str, Any], where_clause: str, where_params: tuple) -> int:
        """Update records in a module table"""
        full_table = self._get_full_table_name(table_name)

        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        values = tuple(data.values()) + where_params

        query = f"UPDATE {full_table} SET {set_clause} WHERE {where_clause}"
        return self.db.execute_write(query, values)

    def delete(self, table_name: str, where_clause: str, where_params: tuple) -> int:
        """Delete records from a module table"""
        full_table = self._get_full_table_name(table_name)
        query = f"DELETE FROM {full_table} WHERE {where_clause}"
        return self.db.execute_write(query, where_params)

    def select(self, table_name: str, where_clause: str = "", where_params: tuple = (),
               order_by: str = "", limit: int = 0) -> List[Dict[str, Any]]:
        """Select records from a module table"""
        full_table = self._get_full_table_name(table_name)

        query = f"SELECT * FROM {full_table}"

        if where_clause:
            query += f" WHERE {where_clause}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit > 0:
            query += f" LIMIT {limit}"

        return self.db.execute_query(query, where_params)

    def get_by_id(self, table_name: str, record_id: Any) -> Optional[Dict[str, Any]]:
        """Get a single record by ID"""
        results = self.select(table_name, "id = ?", (record_id,))
        return results[0] if results else None

    def count(self, table_name: str, where_clause: str = "", where_params: tuple = ()) -> int:
        """Count records in a module table"""
        full_table = self._get_full_table_name(table_name)

        query = f"SELECT COUNT(*) as count FROM {full_table}"
        if where_clause:
            query += f" WHERE {where_clause}"

        result = self.db.execute_query(query, where_params)
        return result[0]['count'] if result else 0

    def upsert(self, table_name: str, data: Dict[str, Any], id_field: str = "id") -> int:
        """Insert or update a record"""
        if id_field in data:
            existing = self.get_by_id(table_name, data[id_field])
            if existing:
                # Update
                update_data = {k: v for k, v in data.items() if k != id_field}
                return self.update(table_name, update_data, f"{id_field} = ?", (data[id_field],))
            else:
                # Insert
                return self.insert(table_name, data)
        else:
            # Insert without ID check
            return self.insert(table_name, data)

    def store_json(self, table_name: str, record_id: str, data: Dict[str, Any]) -> int:
        """Store a dictionary as JSON in the database"""
        json_data = json.dumps(data)
        return self.upsert(table_name, {"id": record_id, "data": json_data, "updated_at": datetime.now().isoformat()})

    def load_json(self, table_name: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Load a dictionary from JSON in the database"""
        record = self.get_by_id(table_name, record_id)
        if record and 'data' in record:
            try:
                return json.loads(record['data'])
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON for {record_id}")
                return None
        return None

    def log_activity(self, activity_type: str, details: Dict[str, Any]) -> int:
        """Log module activity"""
        activity_table = "activity_log"
        self.create_table(activity_table, """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        """)

        return self.insert(activity_table, {
            "activity_type": activity_type,
            "details": json.dumps(details)
        })

    def get_recent_activity(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent module activity"""
        return self.select("activity_log", order_by="timestamp DESC", limit=limit)
