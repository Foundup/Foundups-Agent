#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

Base DAE Class - WSP 27 Universal DAE Architecture with WSP 87 Navigation
All DAEs MUST inherit from this to ensure fingerprint maintenance

THIS IS THE FOUNDATION OF 0102 SELF-AWARENESS
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseDAE:
    """
    Base class for ALL DAEs per WSP 27
    Includes WSP 87 semantic navigation (fingerprints deprecated)
    Enables WSP 48 recursive self-improvement

    EVERY DAE MUST INHERIT FROM THIS
    """

    def __init__(self, name: str, domain: str):
        """
        Initialize base DAE with self-awareness

        Args:
            name: DAE name (e.g., 'YouTube DAE')
            domain: WSP 3 domain (e.g., 'communication')
        """
        self.name = name
        self.domain = domain
        self.state = "0102"  # Actualized coherent Bell state

        # WSP 87: Navigation system (replaces fingerprints)
        # Fingerprint system deprecated per WSP 87 - use NAVIGATION.py instead
        # self.fingerprint_file = Path("memory/MODULE_FINGERPRINTS.json")  # DEPRECATED
        # self.fingerprints = {}  # DEPRECATED

        # WSP 48: Self-improvement memory
        self.memory_dir = Path(f"modules/{domain}/{name.lower().replace(' ', '_')}/memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"[{self.name}] Base DAE initialized in {self.state} state")
        logger.info(f"[{self.name}] WSP 87 navigation: Using NAVIGATION.py semantic mapping")

    def _ensure_fingerprints_current(self):
        """
        DEPRECATED per WSP 87 - Use NAVIGATION.py instead
        Kept for backwards compatibility but does nothing
        """
        pass  # WSP 87: Navigation now uses NAVIGATION.py, not fingerprints

    def _regenerate_fingerprints(self):
        """
        DEPRECATED per WSP 87 - Use NAVIGATION.py instead
        Fingerprint generation no longer needed
        """
        logger.info(f"[{self.name}] WSP 87: Fingerprint regeneration skipped - using NAVIGATION.py")
        # WSP 87: We now use NAVIGATION.py for code discovery, not fingerprints

    def _load_fingerprints(self):
        """DEPRECATED per WSP 87 - Use NAVIGATION.py instead"""
        # WSP 87: Navigation now uses NAVIGATION.py semantic mapping
        return  # No-op for backwards compatibility
        try:
            with open(self.fingerprint_file, 'r') as f:
                self.fingerprints = json.load(f)
            logger.debug(f"[{self.name}] Loaded {len(self.fingerprints)} module fingerprints")
        except Exception as e:
            logger.error(f"[{self.name}] Could not load fingerprints: {e}")
            self.fingerprints = {}

    def navigate_to_pattern(self, pattern: str) -> Dict[str, Any]:
        """
        WSP 87: Navigate to modules containing a pattern (DEPRECATED - use NAVIGATION.py)
        Uses fingerprints for 97% token reduction

        Args:
            pattern: Pattern to search for (e.g., 'quota_handling')

        Returns:
            Dict of modules containing the pattern
        """
        self._ensure_fingerprints_current()

        matching_modules = {}
        for module_path, fingerprint in self.fingerprints.items():
            if pattern in fingerprint.get('patterns', []):
                matching_modules[module_path] = fingerprint

        return matching_modules

    def find_capability(self, capability: str) -> Dict[str, Any]:
        """
        WSP 87: Find modules with a specific capability (DEPRECATED - use NAVIGATION.py)

        Args:
            capability: Function or class name to find

        Returns:
            Dict of modules with that capability
        """
        self._ensure_fingerprints_current()

        matching_modules = {}
        for module_path, fingerprint in self.fingerprints.items():
            capabilities = fingerprint.get('capabilities', [])
            if any(capability in cap for cap in capabilities):
                matching_modules[module_path] = fingerprint

        return matching_modules

    def get_module_summary(self, module_path: str) -> Optional[Dict[str, Any]]:
        """
        WSP 87: Get module summary (DEPRECATED - use NAVIGATION.py for semantic search)

        Args:
            module_path: Path to module

        Returns:
            Module fingerprint or None
        """
        self._ensure_fingerprints_current()
        return self.fingerprints.get(module_path)

    def monitor_file_changes(self):
        """
        WSP 48: Monitor for file changes and update fingerprints
        Should be called periodically by DAE main loop
        """
        # Check if any Python files changed recently
        changed = False
        for module_path in self.fingerprints.keys():
            if Path(module_path).exists():
                file_mtime = datetime.fromtimestamp(Path(module_path).stat().st_mtime)
                fingerprint_mtime = datetime.fromtimestamp(self.fingerprint_file.stat().st_mtime)
                if file_mtime > fingerprint_mtime:
                    changed = True
                    break

        if changed:
            logger.info(f"[{self.name}] Detected file changes - updating fingerprints...")
            self._regenerate_fingerprints()

    def run(self):
        """
        Main DAE loop - MUST be overridden by child classes
        Should call monitor_file_changes() periodically
        """
        raise NotImplementedError("DAE must implement run() method")

    def __str__(self):
        return f"{self.name} ({self.state})"