#!/usr/bin/env python3
"""
WorkContext - Core data model for tracking 0102's current work state

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Set, List, Optional


@dataclass
class WorkContext:
    """What 0102 is currently working on - tracks active development context"""

    active_files: Set[str] = field(default_factory=set)
    primary_module: Optional[str] = None
    task_pattern: str = "unknown"
    last_activity: datetime = field(default_factory=datetime.now)
    session_actions: List[str] = field(default_factory=list)

    def add_file(self, file_path: str):
        """Add a file to the active work context"""
        self.active_files.add(file_path)
        self.last_activity = datetime.now()

    def remove_file(self, file_path: str):
        """Remove a file from the active work context"""
        self.active_files.discard(file_path)
        self.last_activity = datetime.now()

    def add_action(self, action: str):
        """Record an action taken in this session"""
        self.session_actions.append(action)
        self.last_activity = datetime.now()

    def get_recent_files(self, limit: int = 5) -> List[str]:
        """Get the most recently active files"""
        # For now, return all files (could be enhanced with timestamps)
        return list(self.active_files)[:limit]

    def is_idle(self, timeout_minutes: int = 30) -> bool:
        """Check if work context indicates idle state"""
        return (datetime.now() - self.last_activity).total_seconds() > (timeout_minutes * 60)

    def get_summary(self) -> str:
        """Get a human-readable summary of the current work context"""
        summary_parts = []
        if self.primary_module:
            summary_parts.append(f"Module: {self.primary_module}")
        if self.task_pattern != "unknown":
            summary_parts.append(f"Pattern: {self.task_pattern}")
        if self.active_files:
            summary_parts.append(f"Active files: {len(self.active_files)}")
        if self.session_actions:
            summary_parts.append(f"Actions: {len(self.session_actions)}")

        return " | ".join(summary_parts) if summary_parts else "No active work context"
