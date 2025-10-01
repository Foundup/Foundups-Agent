#!/usr/bin/env python3
"""
FileSystemWatcher - Real-time file system monitoring service

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration)
"""

import os
from typing import List, Dict, Set
from pathlib import Path


class FileSystemWatcher:
    """Real-time file system monitoring for detecting code changes"""

    def __init__(self, watch_paths: List[str] = None):
        """Initialize the file system watcher

        Args:
            watch_paths: List of directory paths to monitor
        """
        self.watch_paths = watch_paths or ["holo_index/", "modules/", "WSP_framework/"]
        self.file_timestamps: Dict[str, float] = {}
        self.recent_changes: List[str] = []
        self.ignored_patterns = {'.git', '__pycache__', 'node_modules', '.pytest_cache'}
        self.watched_extensions = {'.py', '.md', '.json', '.txt', '.yaml', '.yml'}

    def scan_for_changes(self) -> List[str]:
        """Scan for file changes since last check

        Returns:
            List of file paths that have been modified
        """
        changes = []

        for watch_path in self.watch_paths:
            if not os.path.exists(watch_path):
                continue

            changes.extend(self._scan_directory(watch_path))

        # Update recent changes history
        self.recent_changes = changes[-50:]  # Keep last 50 changes

        return changes

    def _scan_directory(self, directory: str) -> List[str]:
        """Scan a single directory for changes"""
        changes = []

        try:
            for root, dirs, files in os.walk(directory):
                # Filter out ignored directories
                dirs[:] = [d for d in dirs if self._should_watch_directory(d)]

                for file in files:
                    if self._should_watch_file(file):
                        file_path = os.path.join(root, file)
                        if self._has_file_changed(file_path):
                            changes.append(file_path)
        except (OSError, IOError) as e:
            # Log error but don't crash
            print(f"[FSW-ERROR] Failed to scan {directory}: {e}")

        return changes

    def _should_watch_directory(self, dirname: str) -> bool:
        """Check if a directory should be watched"""
        return (
            not dirname.startswith('.') and
            dirname not in self.ignored_patterns and
            not dirname.endswith('.egg-info')
        )

    def _should_watch_file(self, filename: str) -> bool:
        """Check if a file should be watched based on extension"""
        if filename.startswith('.'):
            return False

        _, ext = os.path.splitext(filename)
        return ext in self.watched_extensions

    def _has_file_changed(self, file_path: str) -> bool:
        """Check if a file has been modified since last scan"""
        try:
            current_mtime = os.path.getmtime(file_path)

            if file_path not in self.file_timestamps:
                # New file - record timestamp and consider it changed
                self.file_timestamps[file_path] = current_mtime
                return True
            elif current_mtime > self.file_timestamps[file_path]:
                # File modified - update timestamp
                self.file_timestamps[file_path] = current_mtime
                return True
            else:
                # No change
                return False

        except (OSError, IOError):
            # File might be temporarily inaccessible
            return False

    def get_recent_changes(self, limit: int = 10) -> List[str]:
        """Get the most recent file changes"""
        return self.recent_changes[-limit:] if self.recent_changes else []

    def get_watched_files_count(self) -> int:
        """Get the total number of files being watched"""
        return len(self.file_timestamps)

    def get_watched_paths(self) -> List[str]:
        """Get the list of paths being watched"""
        return self.watch_paths.copy()

    def clear_timestamps(self):
        """Clear all stored timestamps (useful for resetting state)"""
        self.file_timestamps.clear()
        self.recent_changes.clear()

    def get_status_summary(self) -> str:
        """Get a status summary of the watcher"""
        watched_files = self.get_watched_files_count()
        recent_changes = len(self.recent_changes)

        return f"Watching {watched_files} files across {len(self.watch_paths)} paths | {recent_changes} recent changes"
