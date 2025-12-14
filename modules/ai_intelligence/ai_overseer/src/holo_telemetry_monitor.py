# -*- coding: utf-8 -*-
"""
HoloDAE Telemetry Monitor - Bridge HoloDAE JSONL telemetry to AI Overseer event_queue

Implements Priority 1 from dual-channel architecture analysis:
- Tails holo_index/logs/telemetry/*.jsonl files
- Parses JSONL events (module_status, system_alerts, search_request)
- Feeds events into AI Overseer event_queue for pattern learning

WSP Compliance:
- WSP 91: Structured logging and observability
- WSP 80: DAE coordination (HoloDAE → AI Overseer)
- WSP 62: Modularity (<500 lines)

Architecture:
```
HoloDAE (writes JSONL) → HoloTelemetryMonitor (tail+parse) → AI Overseer event_queue
```

This creates the "cardiovascular system" feedback loop for recursive self-improvement.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from asyncio import Queue

logger = logging.getLogger(__name__)


class HoloTelemetryMonitor:
    """
    Monitor HoloDAE JSONL telemetry and feed events to AI Overseer.

    Watches holo_index/logs/telemetry/*.jsonl files for:
    - module_status: Module health changes (critical → refactor triggers)
    - system_alerts: WSP violations, size thresholds
    - search_request: HoloIndex query patterns

    Feeds into AI Overseer event_queue for:
    - Skill triggering (auto-refactoring on critical modules)
    - Pattern learning (module health trends)
    - WRE integration (skill outcome correlation)
    """

    def __init__(
        self,
        repo_root: Path,
        event_queue: 'Queue',
        telemetry_dir: Optional[Path] = None
    ):
        """
        Initialize telemetry monitor.

        Args:
            repo_root: Repository root path
            event_queue: AI Overseer async event queue
            telemetry_dir: Override telemetry directory (default: holo_index/logs/telemetry)
        """
        self.repo_root = repo_root
        self.event_queue = event_queue
        self.telemetry_dir = telemetry_dir or (repo_root / "holo_index" / "logs" / "telemetry")

        # Track file positions for tailing
        self.file_positions: Dict[str, int] = {}

        # Track seen events to avoid duplicates
        self.seen_events: set = set()

        # Monitor state
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None

        # Statistics
        self.events_processed = 0
        self.events_queued = 0
        self.parse_errors = 0

        logger.info(
            "[HOLO-TELEMETRY] Initialized monitor | telemetry_dir=%s",
            self.telemetry_dir
        )

    async def start_monitoring(self, poll_interval: float = 2.0):
        """
        Start background telemetry monitoring.

        Args:
            poll_interval: Seconds between directory scans
        """
        if self.running:
            logger.warning("[HOLO-TELEMETRY] Already running")
            return

        self.running = True
        self.monitor_task = asyncio.create_task(
            self._monitoring_loop(poll_interval)
        )
        logger.info("[HOLO-TELEMETRY] Started monitoring | poll_interval=%.1fs", poll_interval)

    async def stop_monitoring(self):
        """Stop background monitoring."""
        if not self.running:
            return

        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

    async def run_once(self) -> List[Dict[str, Any]]:
        """
        Process telemetry files one time (tail from last positions).

        Returns:
            List of actionable events (also enqueued to event_queue).
        """
        events: List[Dict[str, Any]] = []
        if not self.telemetry_dir.exists():
            return events

        jsonl_files = sorted(self.telemetry_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        for jsonl_file in jsonl_files:
            file_events = await self._process_file(jsonl_file)
            events.extend(file_events)
        return events

    async def _monitoring_loop(self, poll_interval: float):
        """
        Main monitoring loop - tail JSONL files and feed events to queue.

        Args:
            poll_interval: Seconds between scans
        """
        logger.debug("[HOLO-TELEMETRY] Monitoring loop started")

        while self.running:
            try:
                await self._process_telemetry_files()
                await asyncio.sleep(poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("[HOLO-TELEMETRY] Loop error: %s", e, exc_info=True)
                await asyncio.sleep(poll_interval)

    async def _process_telemetry_files(self):
        """
        Scan telemetry directory and process new JSONL entries.

        Implements file tailing pattern:
        1. List all *.jsonl files in telemetry_dir
        2. For each file, read from last known position
        3. Parse JSONL lines into events
        4. Queue events for AI Overseer
        """
        if not self.telemetry_dir.exists():
            logger.debug("[HOLO-TELEMETRY] Telemetry dir not found: %s", self.telemetry_dir)
            return

        jsonl_files = sorted(self.telemetry_dir.glob("*.jsonl"))

        for jsonl_file in jsonl_files:
            await self._tail_jsonl_file(jsonl_file)

    async def _tail_jsonl_file(self, file_path: Path):
        """
        Tail a single JSONL file from last read position.

        Args:
            file_path: Path to JSONL file
        """
        file_key = str(file_path)
        last_position = self.file_positions.get(file_key, 0)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Seek to last position
                f.seek(last_position)

                # Read new lines
                new_lines = f.readlines()

                # Update position
                self.file_positions[file_key] = f.tell()

                # Process new events
                for line in new_lines:
                    await self._parse_and_queue_event(line.strip(), file_path)

        except Exception as e:
            logger.error("[HOLO-TELEMETRY] Failed to tail %s: %s", file_path.name, e)

    async def _process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a telemetry file from last position (one-shot use by run_once).

        Args:
            file_path: Path to JSONL file

        Returns:
            List of actionable events parsed from this file.
        """
        file_key = str(file_path)
        last_position = self.file_positions.get(file_key, 0)
        events: List[Dict[str, Any]] = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                self.file_positions[file_key] = f.tell()

                for line in new_lines:
                    enriched = await self._parse_and_queue_event(line.strip(), file_path, collect_only=False)
                    if enriched is not None:
                        events.append(enriched)
        except Exception as e:
            logger.error("[HOLO-TELEMETRY] Failed to process %s: %s", file_path.name, e)

        return events

    async def _parse_and_queue_event(self, line: str, source_file: Path, collect_only: bool = False) -> Optional[Dict[str, Any]]:
        """
        Parse JSONL line and queue event if actionable.

        Args:
            line: JSONL line
            source_file: Source file path
            collect_only: If True, return the enriched event instead of enqueuing (used by run_once)
        """
        if not line:
            return None

        try:
            event = json.loads(line)
            self.events_processed += 1

            # Generate event ID to avoid duplicates
            event_id = self._generate_event_id(event)
            if event_id in self.seen_events:
                return None

            self.seen_events.add(event_id)

            # Only queue actionable events
            if self._is_actionable_event(event):
                # Enrich event with metadata
                enriched_event = {
                    **event,
                    "source": "holodae_telemetry",
                    "telemetry_file": source_file.name,
                    "processed_at": datetime.now().isoformat()
                }

                if collect_only:
                    return enriched_event

                await self.event_queue.put(enriched_event)
                self.events_queued += 1

                logger.debug(
                    "[HOLO-TELEMETRY] Queued event | type=%s module=%s",
                    event.get("event"),
                    event.get("module", "N/A")
                )

        except json.JSONDecodeError as e:
            self.parse_errors += 1
            logger.warning("[HOLO-TELEMETRY] JSON parse error: %s | line=%s", e, line[:100])
        except Exception as e:
            logger.error("[HOLO-TELEMETRY] Event processing error: %s", e, exc_info=True)

        return None

    def _generate_event_id(self, event: Dict[str, Any]) -> str:
        """
        Generate unique event ID to avoid duplicate processing.

        Args:
            event: Parsed JSONL event

        Returns:
            Event ID string
        """
        # Combine timestamp + event type + module/query for uniqueness
        parts = [
            event.get("timestamp", ""),
            event.get("session", ""),
            event.get("event", ""),
            event.get("module", event.get("query", ""))
        ]
        return "|".join(str(p) for p in parts)

    def _is_actionable_event(self, event: Dict[str, Any]) -> bool:
        """
        Determine if event should trigger AI Overseer action.

        Actionable events:
        - module_status with severity=critical (refactor triggers)
        - system_alerts with WSP violations
        - search_request patterns (for learning)

        Args:
            event: Parsed JSONL event

        Returns:
            True if event should be queued
        """
        event_type = event.get("event")

        # Critical module status (auto-refactoring trigger)
        if event_type == "module_status":
            severity = event.get("severity")
            if severity == "critical":
                return True

        # System alerts (WSP violations)
        if event_type == "system_alerts":
            alerts = event.get("alerts", [])
            if alerts:  # Any alerts are actionable
                return True

        # Search patterns (for learning, lower priority)
        if event_type == "search_request":
            # Only queue if search found results (code_hits or wsp_hits > 0)
            code_hits = event.get("code_hits", 0)
            wsp_hits = event.get("wsp_hits", 0)
            if code_hits > 0 or wsp_hits > 0:
                return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get telemetry monitor statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "running": self.running,
            "events_processed": self.events_processed,
            "events_queued": self.events_queued,
            "parse_errors": self.parse_errors,
            "files_tracked": len(self.file_positions),
            "seen_events": len(self.seen_events),
            "telemetry_dir": str(self.telemetry_dir)
        }

    async def process_historical_telemetry(
        self,
        max_files: int = 10,
        max_events_per_file: int = 100
    ):
        """
        One-time processing of recent telemetry files (e.g., on startup).

        Args:
            max_files: Maximum number of recent files to process
            max_events_per_file: Maximum events per file
        """
        if not self.telemetry_dir.exists():
            return

        logger.info("[HOLO-TELEMETRY] Processing historical telemetry")

        # Get most recent JSONL files
        jsonl_files = sorted(
            self.telemetry_dir.glob("*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:max_files]

        for jsonl_file in jsonl_files:
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-max_events_per_file:]

                    for line in lines:
                        await self._parse_and_queue_event(line.strip(), jsonl_file)

                # Mark file as fully processed
                self.file_positions[str(jsonl_file)] = jsonl_file.stat().st_size

            except Exception as e:
                logger.error("[HOLO-TELEMETRY] Failed to process %s: %s", jsonl_file.name, e)

        logger.info(
            "[HOLO-TELEMETRY] Historical processing complete | files=%d queued=%d",
            len(jsonl_files),
            self.events_queued
        )
