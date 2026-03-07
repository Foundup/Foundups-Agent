"""Convenience facade over DatabaseManager."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from .db_manager import DatabaseManager


class Database:
    """Small facade used by legacy call sites that import `database.Database`."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.manager = DatabaseManager()

    def query(self, sql: str, params: Sequence[Any] | Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        return self.manager.execute_query(sql, params)

    def write(self, sql: str, params: Sequence[Any] | Tuple[Any, ...] = ()) -> int:
        return self.manager.execute_write(sql, params)

    def process(self) -> Dict[str, Any]:
        """Return a lightweight health snapshot for compatibility callers."""
        return {
            "backend": self.manager.backend_info(),
            "stats": self.manager.get_stats(),
        }


def utility_database() -> Dict[str, Any]:
    """Return backend metadata for quick diagnostics."""
    return Database().manager.backend_info()

