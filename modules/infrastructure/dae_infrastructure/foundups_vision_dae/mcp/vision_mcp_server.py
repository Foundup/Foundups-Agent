# -*- coding: utf-8 -*-
"""
Vision DAE MCP Server Implementation
Exposes telemetry summaries and worker state via MCP protocol.

WSP Compliance: WSP 77 (Agent Coordination), WSP 72 (Module Independence)
Sprint 3 - MCP Interface Stub
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta

# Apply WSP 90 UTF-8 enforcement at entry point only
if sys.platform.startswith('win') and __name__ == "__main__":
    class SafeUTF8Wrapper:
        def __init__(self, original_stream):
            self.original_stream = original_stream
            self.encoding = 'utf-8'
            self.errors = 'replace'

        def write(self, data):
            try:
                if isinstance(data, str):
                    encoded = data.encode('utf-8', errors='replace')
                    if hasattr(self.original_stream, 'buffer'):
                        self.original_stream.buffer.write(encoded)
                    else:
                        self.original_stream.write(data.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
                else:
                    self.original_stream.write(data)
            except Exception:
                try:
                    self.original_stream.write(str(data))
                except Exception:
                    pass

        def flush(self):
            try:
                self.original_stream.flush()
            except Exception:
                pass

        def __getattr__(self, name):
            return getattr(self.original_stream, name)

    if not isinstance(sys.stdout, SafeUTF8Wrapper):
        sys.stdout = SafeUTF8Wrapper(sys.stdout)
    if not isinstance(sys.stderr, SafeUTF8Wrapper):
        sys.stderr = SafeUTF8Wrapper(sys.stderr)


class VisionMCPServer:
    """MCP server for Vision DAE telemetry and worker state access"""

    def __init__(self, module_root: Optional[Path] = None):
        """
        Initialize Vision MCP server.

        Args:
            module_root: Root path to foundups_vision_dae module
                         Defaults to auto-detected module root
        """
        if module_root is None:
            # Auto-detect module root (4 levels up from this file)
            module_root = Path(__file__).parent.parent

        self.module_root = Path(module_root)
        self.memory_root = self.module_root / "memory"
        self.session_summaries_dir = self.memory_root / "session_summaries"
        self.ui_tars_dispatches_dir = self.memory_root / "ui_tars_dispatches"
        self.worker_state_dir = self.memory_root / "worker_state"

        # Legacy support: docs/session_backups/foundups_vision_dae/run_history/
        self.docs_backup_dir = Path("docs/session_backups/foundups_vision_dae/run_history")

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Create memory subdirectories if they don't exist"""
        self.session_summaries_dir.mkdir(parents=True, exist_ok=True)
        self.ui_tars_dispatches_dir.mkdir(parents=True, exist_ok=True)
        self.worker_state_dir.mkdir(parents=True, exist_ok=True)
        self.docs_backup_dir.mkdir(parents=True, exist_ok=True)

    def get_latest_summary(self) -> Dict[str, Any]:
        """
        Get the most recent run history summary.

        Checks both module memory and legacy docs location for backward compatibility.

        Returns:
            {
                "success": bool,
                "summary": dict,          # Full summary JSON
                "timestamp": str,         # ISO8601 UTC
                "source": str,            # "module_memory" or "docs_backup"
                "error": str              # Only on failure
            }
        """
        try:
            # Priority 1: Check module memory (WSP 60 location)
            module_latest = self.session_summaries_dir / "latest_run_history.json"

            # Priority 2: Check docs backup location (legacy support)
            docs_latest = self.docs_backup_dir / "latest_run_history.json"

            # Find most recent file
            candidates = []
            if module_latest.exists():
                candidates.append(("module_memory", module_latest))
            if docs_latest.exists():
                candidates.append(("docs_backup", docs_latest))

            if not candidates:
                return {
                    "success": False,
                    "error": "No run history summary found",
                    "checked_paths": [
                        str(module_latest),
                        str(docs_latest)
                    ]
                }

            # Use most recently modified file
            candidates.sort(key=lambda x: x[1].stat().st_mtime, reverse=True)
            source, latest_path = candidates[0]

            # Read summary
            with latest_path.open("r", encoding="utf-8") as f:
                summary_data = json.load(f)

            # Extract timestamp from summary or file metadata
            timestamp = summary_data.get("timestamp")
            if not timestamp:
                mtime = latest_path.stat().st_mtime
                timestamp = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()

            return {
                "success": True,
                "summary": summary_data,
                "timestamp": timestamp,
                "source": source,
                "file_path": str(latest_path),
                "size_bytes": latest_path.stat().st_size
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in summary file: {e}",
                "file_path": str(latest_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read latest summary: {e}"
            }

    def list_recent_summaries(self, limit: int = 10) -> Dict[str, Any]:
        """
        List recent run history summaries with timestamps and metadata.

        Args:
            limit: Maximum number of summaries to return (default 10)

        Returns:
            {
                "success": bool,
                "summaries": [
                    {
                        "filename": str,
                        "timestamp": str,      # ISO8601 UTC
                        "size_bytes": int,
                        "source": str,         # "module_memory" or "docs_backup"
                        "session_count": int,  # From summary data
                        "timespan_days": int   # From summary data
                    }
                ],
                "total_found": int,
                "limit_applied": int,
                "error": str  # Only on failure
            }
        """
        try:
            summaries = []

            # Scan module memory location
            if self.session_summaries_dir.exists():
                for json_file in self.session_summaries_dir.glob("*.json"):
                    if json_file.name.startswith("run_history_") or json_file.name == "latest_run_history.json":
                        try:
                            with json_file.open("r", encoding="utf-8") as f:
                                data = json.load(f)

                            mtime = json_file.stat().st_mtime
                            timestamp = data.get("timestamp") or datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()

                            summaries.append({
                                "filename": json_file.name,
                                "timestamp": timestamp,
                                "size_bytes": json_file.stat().st_size,
                                "source": "module_memory",
                                "session_count": data.get("raw_session_count", 0),
                                "timespan_days": data.get("timespan_days", 0),
                                "file_path": str(json_file)
                            })
                        except (json.JSONDecodeError, KeyError):
                            # Skip malformed files
                            continue

            # Scan docs backup location (legacy support)
            if self.docs_backup_dir.exists():
                for json_file in self.docs_backup_dir.glob("*.json"):
                    if json_file.name.startswith("run_history_") or json_file.name == "latest_run_history.json":
                        try:
                            with json_file.open("r", encoding="utf-8") as f:
                                data = json.load(f)

                            mtime = json_file.stat().st_mtime
                            timestamp = data.get("timestamp") or datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()

                            summaries.append({
                                "filename": json_file.name,
                                "timestamp": timestamp,
                                "size_bytes": json_file.stat().st_size,
                                "source": "docs_backup",
                                "session_count": data.get("raw_session_count", 0),
                                "timespan_days": data.get("timespan_days", 0),
                                "file_path": str(json_file)
                            })
                        except (json.JSONDecodeError, KeyError):
                            # Skip malformed files
                            continue

            # Sort by timestamp (most recent first)
            summaries.sort(key=lambda x: x["timestamp"], reverse=True)

            # Apply limit
            total_found = len(summaries)
            summaries = summaries[:limit]

            return {
                "success": True,
                "summaries": summaries,
                "total_found": total_found,
                "limit_applied": limit,
                "scanned_directories": [
                    str(self.session_summaries_dir),
                    str(self.docs_backup_dir)
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list summaries: {e}"
            }

    def get_worker_state(self) -> Dict[str, Any]:
        """
        Get current worker checkpoint state.

        Returns:
            {
                "success": bool,
                "worker_state": {
                    "browser_offset": int,      # Last byte offset in browser log
                    "batch_index": int,         # Last session batch index
                    "last_session_id": int      # Last processed session ID
                },
                "checkpoint_timestamp": str,    # ISO8601 UTC
                "error": str                    # Only on failure
            }
        """
        try:
            worker_state = {}
            checkpoint_files = {
                "browser_offset": self.worker_state_dir / "browser_telemetry_offset.txt",
                "batch_index": self.worker_state_dir / "session_batch_index.txt",
                "last_session_id": self.worker_state_dir / "last_session_id.txt"
            }

            # Read checkpoint files
            for key, checkpoint_file in checkpoint_files.items():
                if checkpoint_file.exists():
                    try:
                        with checkpoint_file.open("r", encoding="utf-8") as f:
                            value = f.read().strip()
                            worker_state[key] = int(value) if value.isdigit() else 0
                    except (ValueError, IOError):
                        worker_state[key] = 0
                else:
                    worker_state[key] = 0

            # Find most recent checkpoint file modification time
            checkpoint_times = [
                f.stat().st_mtime for f in checkpoint_files.values() if f.exists()
            ]

            if checkpoint_times:
                latest_mtime = max(checkpoint_times)
                checkpoint_timestamp = datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat()
            else:
                checkpoint_timestamp = None

            return {
                "success": True,
                "worker_state": worker_state,
                "checkpoint_timestamp": checkpoint_timestamp,
                "checkpoint_files": {k: str(v) for k, v in checkpoint_files.items()}
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read worker state: {e}"
            }

    def update_worker_checkpoint(
        self,
        browser_offset: Optional[int] = None,
        batch_index: Optional[int] = None,
        last_session_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update worker checkpoint state.

        Args:
            browser_offset: New byte offset in browser log (optional)
            batch_index: New session batch index (optional)
            last_session_id: New last processed session ID (optional)

        Returns:
            {
                "success": bool,
                "updated_fields": list[str],
                "timestamp": str,    # ISO8601 UTC
                "error": str         # Only on failure
            }
        """
        try:
            updated_fields = []
            timestamp = datetime.now(timezone.utc).isoformat()

            checkpoint_updates = {
                "browser_offset": (browser_offset, self.worker_state_dir / "browser_telemetry_offset.txt"),
                "batch_index": (batch_index, self.worker_state_dir / "session_batch_index.txt"),
                "last_session_id": (last_session_id, self.worker_state_dir / "last_session_id.txt")
            }

            for field_name, (value, checkpoint_file) in checkpoint_updates.items():
                if value is not None:
                    with checkpoint_file.open("w", encoding="utf-8") as f:
                        f.write(str(value))
                    updated_fields.append(field_name)

            return {
                "success": True,
                "updated_fields": updated_fields,
                "timestamp": timestamp
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update worker checkpoint: {e}"
            }

    def cleanup_old_summaries(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """
        Delete session summaries older than specified retention period.

        Args:
            days_to_keep: Retention period in days (default 30)

        Returns:
            {
                "success": bool,
                "deleted_count": int,
                "kept_count": int,
                "deleted_files": list[str],
                "error": str  # Only on failure
            }
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            cutoff_timestamp = cutoff_time.timestamp()

            deleted_files = []
            kept_count = 0

            # Clean module memory location
            if self.session_summaries_dir.exists():
                for json_file in self.session_summaries_dir.glob("*.json"):
                    # Never delete latest_run_history.json
                    if json_file.name == "latest_run_history.json":
                        kept_count += 1
                        continue

                    # Check file modification time
                    file_mtime = json_file.stat().st_mtime
                    if file_mtime < cutoff_timestamp:
                        json_file.unlink()
                        deleted_files.append(str(json_file))
                    else:
                        kept_count += 1

            return {
                "success": True,
                "deleted_count": len(deleted_files),
                "kept_count": kept_count,
                "deleted_files": deleted_files,
                "retention_days": days_to_keep,
                "cutoff_timestamp": cutoff_time.isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to cleanup old summaries: {e}"
            }

    def cleanup_old_dispatches(self, days_to_keep: int = 14) -> Dict[str, Any]:
        """
        Delete UI-TARS dispatch audit files older than specified retention period.

        Args:
            days_to_keep: Retention period in days (default 14)

        Returns:
            {
                "success": bool,
                "deleted_count": int,
                "kept_count": int,
                "deleted_files": list[str],
                "error": str  # Only on failure
            }
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            cutoff_timestamp = cutoff_time.timestamp()

            deleted_files = []
            kept_count = 0

            # Clean UI-TARS dispatches directory
            if self.ui_tars_dispatches_dir.exists():
                for json_file in self.ui_tars_dispatches_dir.glob("*.json"):
                    # Check file modification time
                    file_mtime = json_file.stat().st_mtime
                    if file_mtime < cutoff_timestamp:
                        json_file.unlink()
                        deleted_files.append(str(json_file))
                    else:
                        kept_count += 1

            return {
                "success": True,
                "deleted_count": len(deleted_files),
                "kept_count": kept_count,
                "deleted_files": deleted_files,
                "retention_days": days_to_keep,
                "cutoff_timestamp": cutoff_time.isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to cleanup old dispatches: {e}"
            }

    def stream_events(self, session_index: Optional[int] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Stream Vision DAE browser telemetry events from JSONL session bundles.

        Args:
            session_index: Session bundle index to stream (default: latest)
            limit: Maximum number of events to return (default 50)

        Returns:
            {
                "success": bool,
                "events": list,           # Telemetry event objects
                "session_index": int,     # Index of session bundle
                "event_count": int,       # Number of events returned
                "session_file": str,      # Path to JSONL file
                "error": str              # Only on failure
            }
        """
        try:
            session_dir = Path("holo_index/telemetry/vision_dae")

            if not session_dir.exists():
                return {
                    "success": False,
                    "error": "Vision DAE telemetry directory not found",
                    "session_dir": str(session_dir)
                }

            # Find latest session if index not specified
            if session_index is None:
                session_files = sorted(session_dir.glob("vision_session_*.jsonl"))
                if not session_files:
                    return {
                        "success": False,
                        "error": "No session bundles found",
                        "session_dir": str(session_dir)
                    }
                session_file = session_files[-1]
                session_index = int(session_file.stem.split("_")[-1])
            else:
                session_file = session_dir / f"vision_session_{session_index:05d}.jsonl"
                if not session_file.exists():
                    return {
                        "success": False,
                        "error": f"Session bundle {session_index} not found",
                        "session_file": str(session_file)
                    }

            # Read events from JSONL file
            events = []
            with session_file.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        events.append(event)
                        if len(events) >= limit:
                            break
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue

            return {
                "success": True,
                "events": events,
                "session_index": session_index,
                "event_count": len(events),
                "session_file": str(session_file)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to stream events: {e}"
            }

    async def stream_live_telemetry(self, max_events: int = 100, timeout_seconds: int = 30) -> Dict[str, Any]:
        """
        Stream live telemetry events in real-time for immediate 0102 observation.

        This enables 0102 to observe system behavior as it happens, enabling
        real-time recursive improvement and debugging capabilities.

        Args:
            max_events: Maximum number of events to collect before returning
            timeout_seconds: How long to wait for events before timing out

        Returns:
            Dictionary with live telemetry data
        """
        import asyncio

        telemetry_log = Path("logs/foundups_browser_events.log")
        collected_events = []
        start_time = asyncio.get_event_loop().time()

        try:
            # Check if log file exists
            if not telemetry_log.exists():
                return {
                    "success": False,
                    "error": f"Telemetry log not found: {telemetry_log}",
                    "events_collected": 0,
                    "collection_duration": 0
                }

            # Read existing events from the end of the file
            with telemetry_log.open("r", encoding="utf-8") as f:
                # Seek to near the end to get recent events
                f.seek(0, 2)  # Seek to end
                file_size = f.tell()

                # Read last 10KB or so to get recent events
                read_size = min(10240, file_size)
                f.seek(max(0, file_size - read_size))

                content = f.read()
                lines = content.split('\n')

                # Parse recent JSON lines
                for line in reversed(lines):  # Start from most recent
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                        collected_events.insert(0, event)  # Insert at beginning to maintain chronological order

                        if len(collected_events) >= max_events:
                            break
                    except json.JSONDecodeError:
                        continue

                    # Check timeout
                    current_time = asyncio.get_event_loop().time()
                    if current_time - start_time >= timeout_seconds:
                        break

            # Wait for new events if we haven't reached max_events
            if len(collected_events) < max_events:
                # Monitor file for new lines (simplified implementation)
                initial_size = telemetry_log.stat().st_size
                wait_start = asyncio.get_event_loop().time()

                while len(collected_events) < max_events:
                    await asyncio.sleep(0.5)  # Check every 500ms

                    current_time = asyncio.get_event_loop().time()
                    if current_time - start_time >= timeout_seconds:
                        break

                    if telemetry_log.exists():
                        current_size = telemetry_log.stat().st_size
                        if current_size > initial_size:
                            # New data written, read the new lines
                            with telemetry_log.open("r", encoding="utf-8") as f:
                                f.seek(initial_size)
                                new_content = f.read()
                                new_lines = new_content.split('\n')

                                for line in new_lines:
                                    line = line.strip()
                                    if not line:
                                        continue

                                    try:
                                        event = json.loads(line)
                                        collected_events.append(event)

                                        if len(collected_events) >= max_events:
                                            break
                                    except json.JSONDecodeError:
                                        continue

                            initial_size = current_size

            end_time = asyncio.get_event_loop().time()
            collection_duration = end_time - start_time

            return {
                "success": True,
                "events_collected": len(collected_events),
                "events": collected_events,
                "collection_duration": collection_duration,
                "max_events_requested": max_events,
                "timeout_seconds": timeout_seconds,
                "telemetry_source": str(telemetry_log),
                "live_streaming": True,
                "collection_method": "tail_file_with_polling"
            }

        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            collection_duration = end_time - start_time

            return {
                "success": False,
                "error": f"Live telemetry streaming failed: {e}",
                "events_collected": len(collected_events),
                "collection_duration": collection_duration,
                "partial_events": collected_events  # Return any events we did collect
            }


# FastMCP integration (optional - can be imported and registered externally)
try:
    from fastmcp import FastMCP

    def create_vision_mcp_app() -> FastMCP:
        """Create and configure FastMCP application for Vision DAE"""
        app = FastMCP("FoundUps Vision DAE MCP Server")
        server = VisionMCPServer()

        @app.tool()
        async def get_latest_summary() -> Dict[str, Any]:
            """Get the most recent Vision DAE run history summary"""
            return server.get_latest_summary()

        @app.tool()
        async def list_recent_summaries(limit: int = 10) -> Dict[str, Any]:
            """List recent Vision DAE summaries with metadata"""
            return server.list_recent_summaries(limit=limit)

        @app.tool()
        async def get_worker_state() -> Dict[str, Any]:
            """Get current Vision DAE worker checkpoint state"""
            return server.get_worker_state()

        @app.tool()
        async def update_worker_checkpoint(
            browser_offset: Optional[int] = None,
            batch_index: Optional[int] = None,
            last_session_id: Optional[int] = None
        ) -> Dict[str, Any]:
            """Update Vision DAE worker checkpoint"""
            return server.update_worker_checkpoint(
                browser_offset=browser_offset,
                batch_index=batch_index,
                last_session_id=last_session_id
            )

        @app.tool()
        async def cleanup_old_summaries(days_to_keep: int = 30) -> Dict[str, Any]:
            """Delete session summaries older than retention period"""
            return server.cleanup_old_summaries(days_to_keep=days_to_keep)

        @app.tool()
        async def cleanup_old_dispatches(days_to_keep: int = 14) -> Dict[str, Any]:
            """Delete UI-TARS dispatch files older than retention period"""
            return server.cleanup_old_dispatches(days_to_keep=days_to_keep)

        @app.tool()
        async def stream_events(session_index: Optional[int] = None, limit: int = 50) -> Dict[str, Any]:
            """Stream Vision DAE browser telemetry events from JSONL session bundles"""
            return server.stream_events(session_index=session_index, limit=limit)

        @app.tool()
        async def stream_live_telemetry(max_events: int = 100, timeout_seconds: int = 30) -> Dict[str, Any]:
            """Stream live telemetry events in real-time for immediate 0102 observation"""
            return await server.stream_live_telemetry(max_events=max_events, timeout_seconds=timeout_seconds)

        @app.get("/")
        async def root():
            return {
                "status": "Vision DAE MCP Server running",
                "version": "0.2.0",
                "sprint": "Sprint 3 - MCP Interface Stub",
                "endpoints": [
                    "get_latest_summary",
                    "list_recent_summaries",
                    "stream_events",
                    "stream_live_telemetry",
                    "get_worker_state",
                    "update_worker_checkpoint",
                    "cleanup_old_summaries",
                    "cleanup_old_dispatches"
                ]
            }

        return app

except ImportError:
    # FastMCP not available - server can still be used standalone
    def create_vision_mcp_app():
        raise ImportError("fastmcp package required for MCP server - install with: pip install fastmcp>=2.12.3")


if __name__ == "__main__":
    # Standalone testing mode
    server = VisionMCPServer()

    print("Vision DAE MCP Server - Testing Mode")
    print("=" * 50)

    # Test get_latest_summary
    print("\n[TEST] get_latest_summary():")
    result = server.get_latest_summary()
    print(json.dumps(result, indent=2))

    # Test list_recent_summaries
    print("\n[TEST] list_recent_summaries(limit=5):")
    result = server.list_recent_summaries(limit=5)
    print(json.dumps(result, indent=2))

    # Test get_worker_state
    print("\n[TEST] get_worker_state():")
    result = server.get_worker_state()
    print(json.dumps(result, indent=2))

    # Test update_worker_checkpoint
    print("\n[TEST] update_worker_checkpoint(browser_offset=1024, batch_index=5):")
    result = server.update_worker_checkpoint(browser_offset=1024, batch_index=5)
    print(json.dumps(result, indent=2))

    print("\n" + "=" * 50)
    print("Testing complete - server operational")
