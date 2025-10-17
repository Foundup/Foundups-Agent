#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Overseer Database Layer (WSP 78)
-----------------------------------

Stores mission runs and phase results in the unified SQLite database
via the ModuleDB base class. Table names are automatically prefixed
with modules_ai_overseer_*
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime

from modules.infrastructure.database.src.module_db import ModuleDB


class OverseerDB(ModuleDB):
    """SQLite-backed storage for AI Overseer missions and phases."""

    def __init__(self) -> None:
        super().__init__("ai_overseer")

    def _init_tables(self) -> None:
        # Missions table: one row per mission
        self.create_table("missions", """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id TEXT NOT NULL UNIQUE,
            mission_type TEXT NOT NULL,
            status TEXT NOT NULL,
            success INTEGER NOT NULL DEFAULT 0,
            phases_completed INTEGER DEFAULT 0,
            phases_failed INTEGER DEFAULT 0,
            created_at DATETIME,
            completed_at DATETIME,
            details TEXT
        """)

        # Phase results: many rows per mission
        self.create_table("phase_results", """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id TEXT NOT NULL,
            phase INTEGER NOT NULL,
            name TEXT,
            agent TEXT,
            method TEXT,
            duration_ms REAL,
            success INTEGER NOT NULL DEFAULT 0,
            error TEXT,
            data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        """)

    def record_mission(self, mission_id: str, mission_type: str, status: str,
                       results: Dict[str, Any]) -> None:
        """Insert/replace mission aggregate and append per-phase rows."""
        # Aggregate
        phases_completed = results.get("phases_completed", 0)
        phases_failed = results.get("phases_failed", 0)
        success = 1 if results.get("success", False) else 0
        details = {k: v for k, v in results.items() if k not in {"phase_results"}}

        # Use INSERT OR REPLACE to keep mission_id unique
        full_missions = self._get_full_table_name("missions")
        query = f"""
            INSERT OR REPLACE INTO {full_missions}
            (mission_id, mission_type, status, success, phases_completed, phases_failed, created_at, completed_at, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()
        self.db.execute_write(query, (
            mission_id,
            mission_type,
            status,
            success,
            phases_completed,
            phases_failed,
            now,
            now,
            json_dumps_safe(details)
        ))

        # Phase rows
        phases: List[Dict[str, Any]] = results.get("phase_results", []) or []
        full_phases = self._get_full_table_name("phase_results")
        phase_query = f"""
            INSERT INTO {full_phases}
            (mission_id, phase, name, agent, method, duration_ms, success, error, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for p in phases:
            self.db.execute_write(phase_query, (
                mission_id,
                p.get("phase"),
                p.get("name"),
                p.get("agent"),
                p.get("method"),
                p.get("duration_ms"),
                1 if p.get("success") else 0,
                p.get("error"),
                json_dumps_safe(p)
            ))


def json_dumps_safe(data: Any) -> str:
    try:
        import json
        return json.dumps(data)
    except Exception:
        return "{}"


