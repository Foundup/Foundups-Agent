# -*- coding: utf-8 -*-
"""
AMO (Autonomous Meeting Orchestrator) MCP Server Implementation
Exposes heartbeat telemetry, meeting intents, presence profiles, and meeting history via MCP protocol.

WSP Compliance: WSP 77 (Agent Coordination), WSP 72 (Module Independence), WSP 91 (DAEMON Observability)
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta

# WSP 90: UTF-8 enforcement only at entry point
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


class AMOMCPServer:
    """MCP server for AMO cardiovascular telemetry and operational state access"""

    def __init__(self, module_root: Optional[Path] = None):
        """
        Initialize AMO MCP server.

        Args:
            module_root: Root path to auto_meeting_orchestrator module
                         Defaults to auto-detected module root
        """
        if module_root is None:
            # Auto-detect module root (4 levels up from this file)
            module_root = Path(__file__).parent.parent

        self.module_root = Path(module_root)
        self.memory_root = self.module_root / "memory"

        # Telemetry paths (WSP 91: DAEMON Observability)
        self.heartbeat_telemetry_file = Path("logs/amo_heartbeat.jsonl")
        self.meeting_history_file = self.memory_root / "meeting_history.jsonl"
        self.active_intents_file = self.memory_root / "active_intents.json"
        self.presence_profiles_file = self.memory_root / "presence_profiles.json"

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Create memory subdirectories if they don't exist"""
        self.memory_root.mkdir(parents=True, exist_ok=True)
        self.heartbeat_telemetry_file.parent.mkdir(parents=True, exist_ok=True)

    def get_heartbeat_health(self) -> Dict[str, Any]:
        """
        Get current AMO heartbeat health status and vital signs.

        Returns:
            {
                "success": bool,
                "health": {
                    "status": str,              # healthy/warning/critical/offline
                    "last_heartbeat": str,      # ISO8601 UTC
                    "uptime_seconds": float,
                    "active_intents": int,
                    "presence_updates": int,
                    "memory_usage_mb": float,
                    "cpu_usage_percent": float,
                    "pulse_count": int
                },
                "telemetry_source": str,
                "error": str                    # Only on failure
            }
        """
        try:
            # Read most recent heartbeat from JSONL telemetry
            if not self.heartbeat_telemetry_file.exists():
                return {
                    "success": False,
                    "error": "No heartbeat telemetry found - AMO may not be running",
                    "telemetry_file": str(self.heartbeat_telemetry_file)
                }

            # Read last line (most recent heartbeat)
            with open(self.heartbeat_telemetry_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if not lines:
                    return {
                        "success": False,
                        "error": "Heartbeat telemetry file empty",
                        "telemetry_file": str(self.heartbeat_telemetry_file)
                    }

                # Parse most recent heartbeat
                last_line = lines[-1].strip()
                heartbeat_data = json.loads(last_line)

            # Check if heartbeat is recent (within last 60 seconds)
            last_timestamp = datetime.fromisoformat(heartbeat_data['timestamp'])
            age_seconds = (datetime.now(timezone.utc) - last_timestamp.replace(tzinfo=timezone.utc)).total_seconds()

            if age_seconds > 60:
                heartbeat_data['status'] = 'stale'
                heartbeat_data['age_seconds'] = age_seconds

            return {
                "success": True,
                "health": heartbeat_data,
                "telemetry_source": str(self.heartbeat_telemetry_file),
                "heartbeat_age_seconds": age_seconds,
                "heartbeat_count": len(lines)
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in heartbeat telemetry: {e}",
                "telemetry_file": str(self.heartbeat_telemetry_file)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read heartbeat health: {e}"
            }

    def get_active_intents(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get currently active meeting intents with priority sorting.

        Args:
            limit: Maximum number of intents to return (default 10)

        Returns:
            {
                "success": bool,
                "intents": [
                    {
                        "requester_id": str,
                        "recipient_id": str,
                        "purpose": str,
                        "expected_outcome": str,
                        "duration_minutes": int,
                        "priority": str,
                        "created_at": str
                    }
                ],
                "total_active": int,
                "limit_applied": int,
                "error": str  # Only on failure
            }
        """
        try:
            # Check if active intents file exists
            if not self.active_intents_file.exists():
                return {
                    "success": True,
                    "intents": [],
                    "total_active": 0,
                    "message": "No active intents file - AMO may be freshly initialized"
                }

            # Read active intents
            with open(self.active_intents_file, 'r', encoding='utf-8') as f:
                intents_data = json.load(f)

            # Sort by priority (assuming priority enum values: LOW=1, MEDIUM=5, HIGH=8, URGENT=10)
            intents = intents_data.get('intents', [])
            intents.sort(key=lambda x: x.get('priority', 0), reverse=True)

            total_active = len(intents)
            intents = intents[:limit]

            return {
                "success": True,
                "intents": intents,
                "total_active": total_active,
                "limit_applied": limit,
                "source_file": str(self.active_intents_file)
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in active intents file: {e}",
                "file_path": str(self.active_intents_file)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read active intents: {e}"
            }

    def get_presence_status(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user presence/availability profiles across platforms.

        Args:
            user_id: Specific user ID to query (optional, returns all if None)

        Returns:
            {
                "success": bool,
                "profiles": {
                    "<user_id>": {
                        "platforms": {
                            "<platform>": "<status>"  # e.g., "discord": "online"
                        },
                        "overall_status": str,
                        "last_updated": str,
                        "confidence_score": float
                    }
                },
                "total_users": int,
                "error": str  # Only on failure
            }
        """
        try:
            # Check if presence profiles file exists
            if not self.presence_profiles_file.exists():
                return {
                    "success": True,
                    "profiles": {},
                    "total_users": 0,
                    "message": "No presence profiles file - no users tracked yet"
                }

            # Read presence profiles
            with open(self.presence_profiles_file, 'r', encoding='utf-8') as f:
                profiles_data = json.load(f)

            profiles = profiles_data.get('profiles', {})

            # Filter by user_id if specified
            if user_id is not None:
                if user_id in profiles:
                    profiles = {user_id: profiles[user_id]}
                else:
                    return {
                        "success": False,
                        "error": f"User '{user_id}' not found in presence profiles",
                        "available_users": list(profiles.keys())
                    }

            return {
                "success": True,
                "profiles": profiles,
                "total_users": len(profiles),
                "source_file": str(self.presence_profiles_file)
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in presence profiles file: {e}",
                "file_path": str(self.presence_profiles_file)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read presence status: {e}"
            }

    def get_meeting_history(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get completed meeting sessions history.

        Args:
            limit: Maximum number of meetings to return (default 20)

        Returns:
            {
                "success": bool,
                "meetings": [
                    {
                        "session_id": str,
                        "participants": list,
                        "purpose": str,
                        "platform": str,
                        "start_time": str,
                        "duration_minutes": int,
                        "status": str
                    }
                ],
                "total_meetings": int,
                "limit_applied": int,
                "error": str  # Only on failure
            }
        """
        try:
            # Check if meeting history file exists
            if not self.meeting_history_file.exists():
                return {
                    "success": True,
                    "meetings": [],
                    "total_meetings": 0,
                    "message": "No meeting history file - no meetings completed yet"
                }

            # Read meeting history from JSONL
            meetings = []
            with open(self.meeting_history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        meeting = json.loads(line.strip())
                        meetings.append(meeting)
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue

            # Sort by start_time (most recent first)
            meetings.sort(key=lambda x: x.get('start_time', ''), reverse=True)

            total_meetings = len(meetings)
            meetings = meetings[:limit]

            return {
                "success": True,
                "meetings": meetings,
                "total_meetings": total_meetings,
                "limit_applied": limit,
                "source_file": str(self.meeting_history_file)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read meeting history: {e}"
            }

    def stream_heartbeat_telemetry(self, limit: int = 50) -> Dict[str, Any]:
        """
        Stream recent AMO heartbeat telemetry events from JSONL.

        Args:
            limit: Maximum number of heartbeat events to return (default 50)

        Returns:
            {
                "success": bool,
                "heartbeats": list,       # Heartbeat event objects
                "event_count": int,       # Number of events returned
                "telemetry_file": str,    # Path to JSONL file
                "error": str              # Only on failure
            }
        """
        try:
            if not self.heartbeat_telemetry_file.exists():
                return {
                    "success": False,
                    "error": "Heartbeat telemetry file not found - AMO may not be running",
                    "telemetry_file": str(self.heartbeat_telemetry_file)
                }

            # Read heartbeat events from JSONL
            heartbeats = []
            with open(self.heartbeat_telemetry_file, 'r', encoding='utf-8') as f:
                # Read from end for most recent events
                lines = f.readlines()
                for line in reversed(lines):
                    try:
                        heartbeat = json.loads(line.strip())
                        heartbeats.insert(0, heartbeat)  # Maintain chronological order
                        if len(heartbeats) >= limit:
                            break
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue

            return {
                "success": True,
                "heartbeats": heartbeats,
                "event_count": len(heartbeats),
                "total_heartbeats": len(lines),
                "telemetry_file": str(self.heartbeat_telemetry_file)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to stream heartbeat telemetry: {e}"
            }

    def cleanup_old_telemetry(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """
        Cleanup old telemetry data to prevent unbounded growth.

        Args:
            days_to_keep: Retention period in days (default 30)

        Returns:
            {
                "success": bool,
                "deleted_heartbeats": int,
                "deleted_meetings": int,
                "kept_heartbeats": int,
                "kept_meetings": int,
                "error": str  # Only on failure
            }
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            deleted_heartbeats = 0
            kept_heartbeats = 0

            # Cleanup heartbeat telemetry (JSONL - rewrite file with recent events only)
            if self.heartbeat_telemetry_file.exists():
                recent_heartbeats = []
                with open(self.heartbeat_telemetry_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            heartbeat = json.loads(line.strip())
                            timestamp = datetime.fromisoformat(heartbeat['timestamp'])
                            if timestamp.replace(tzinfo=timezone.utc) >= cutoff_time:
                                recent_heartbeats.append(line)
                                kept_heartbeats += 1
                            else:
                                deleted_heartbeats += 1
                        except (json.JSONDecodeError, KeyError):
                            continue

                # Rewrite file with only recent heartbeats
                with open(self.heartbeat_telemetry_file, 'w', encoding='utf-8') as f:
                    f.writelines(recent_heartbeats)

            # Cleanup meeting history (similar approach)
            deleted_meetings = 0
            kept_meetings = 0
            if self.meeting_history_file.exists():
                recent_meetings = []
                with open(self.meeting_history_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            meeting = json.loads(line.strip())
                            start_time = datetime.fromisoformat(meeting['start_time'])
                            if start_time.replace(tzinfo=timezone.utc) >= cutoff_time:
                                recent_meetings.append(line)
                                kept_meetings += 1
                            else:
                                deleted_meetings += 1
                        except (json.JSONDecodeError, KeyError):
                            continue

                # Rewrite file with only recent meetings
                with open(self.meeting_history_file, 'w', encoding='utf-8') as f:
                    f.writelines(recent_meetings)

            return {
                "success": True,
                "deleted_heartbeats": deleted_heartbeats,
                "deleted_meetings": deleted_meetings,
                "kept_heartbeats": kept_heartbeats,
                "kept_meetings": kept_meetings,
                "retention_days": days_to_keep,
                "cutoff_timestamp": cutoff_time.isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to cleanup old telemetry: {e}"
            }


# FastMCP integration (optional - can be imported and registered externally)
try:
    from fastmcp import FastMCP

    def create_amo_mcp_app() -> FastMCP:
        """Create and configure FastMCP application for AMO"""
        app = FastMCP("FoundUps AMO MCP Server")
        server = AMOMCPServer()

        @app.tool()
        async def get_heartbeat_health() -> Dict[str, Any]:
            """Get current AMO heartbeat health status and vital signs"""
            return server.get_heartbeat_health()

        @app.tool()
        async def get_active_intents(limit: int = 10) -> Dict[str, Any]:
            """Get currently active meeting intents with priority sorting"""
            return server.get_active_intents(limit=limit)

        @app.tool()
        async def get_presence_status(user_id: Optional[str] = None) -> Dict[str, Any]:
            """Get user presence/availability profiles across platforms"""
            return server.get_presence_status(user_id=user_id)

        @app.tool()
        async def get_meeting_history(limit: int = 20) -> Dict[str, Any]:
            """Get completed meeting sessions history"""
            return server.get_meeting_history(limit=limit)

        @app.tool()
        async def stream_heartbeat_telemetry(limit: int = 50) -> Dict[str, Any]:
            """Stream recent AMO heartbeat telemetry events from JSONL"""
            return server.stream_heartbeat_telemetry(limit=limit)

        @app.tool()
        async def cleanup_old_telemetry(days_to_keep: int = 30) -> Dict[str, Any]:
            """Cleanup old telemetry data to prevent unbounded growth"""
            return server.cleanup_old_telemetry(days_to_keep=days_to_keep)

        @app.get("/")
        async def root():
            return {
                "status": "AMO MCP Server running",
                "version": "0.1.0",
                "module": "Autonomous Meeting Orchestrator",
                "endpoints": [
                    "get_heartbeat_health",
                    "get_active_intents",
                    "get_presence_status",
                    "get_meeting_history",
                    "stream_heartbeat_telemetry",
                    "cleanup_old_telemetry"
                ]
            }

        return app

except ImportError:
    # FastMCP not available - server can still be used standalone
    def create_amo_mcp_app():
        raise ImportError("fastmcp package required for MCP server - install with: pip install fastmcp>=2.12.3")


if __name__ == "__main__":
    # Standalone testing mode
    server = AMOMCPServer()

    print("AMO MCP Server - Testing Mode")
    print("=" * 50)

    # Test get_heartbeat_health
    print("\n[TEST] get_heartbeat_health():")
    result = server.get_heartbeat_health()
    print(json.dumps(result, indent=2))

    # Test get_active_intents
    print("\n[TEST] get_active_intents(limit=5):")
    result = server.get_active_intents(limit=5)
    print(json.dumps(result, indent=2))

    # Test get_presence_status
    print("\n[TEST] get_presence_status():")
    result = server.get_presence_status()
    print(json.dumps(result, indent=2))

    # Test get_meeting_history
    print("\n[TEST] get_meeting_history(limit=10):")
    result = server.get_meeting_history(limit=10)
    print(json.dumps(result, indent=2))

    print("\n" + "=" * 50)
    print("Testing complete - AMO MCP server operational")
