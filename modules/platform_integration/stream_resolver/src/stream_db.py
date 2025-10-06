"""
Stream Resolver Database Module

Uses WSP 78 database architecture to store and analyze stream patterns.
Replaces JSON files with proper database tables for better performance and analysis.
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from modules.infrastructure.database.src.module_db import ModuleDB

logger = logging.getLogger(__name__)

class StreamResolverDB(ModuleDB):
    """
    Database interface for stream resolver patterns and history.

    Stores stream times, durations, and patterns to enable intelligent checking.
    """

    def __init__(self):
        super().__init__("stream_resolver")
        logger.info("Stream Resolver Database initialized")

    def _init_tables(self) -> None:
        """Initialize stream resolver tables"""

        # Stream times - when streams actually happen
        self.create_table("stream_times", """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL,
            video_id TEXT NOT NULL,
            stream_start DATETIME NOT NULL,
            stream_end DATETIME,
            duration_seconds INTEGER,
            day_of_week INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            minute INTEGER NOT NULL,
            title TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        """)

        # Check history - when we checked for streams
        self.create_table("check_history", """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            found BOOLEAN NOT NULL DEFAULT FALSE,
            day_of_week INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            response_time_ms INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        """)

        # Stream patterns - learned patterns for optimization
        self.create_table("stream_patterns", """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            pattern_data TEXT NOT NULL,
            confidence REAL DEFAULT 0.0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(channel_id, pattern_type)
        """)

        # Channel statistics
        self.create_table("channel_stats", """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL UNIQUE,
            total_checks INTEGER DEFAULT 0,
            streams_found INTEGER DEFAULT 0,
            avg_response_time_ms REAL DEFAULT 0.0,
            last_check DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        """)

        # Migrate existing JSON data if available (one-time operation)
        self.migrate_json_data()

    def record_stream_start(self, channel_id: str, video_id: str, title: str = None) -> int:
        """Record when a stream starts"""
        now = datetime.now()
        return self.insert("stream_times", {
            "channel_id": channel_id,
            "video_id": video_id,
            "stream_start": now.isoformat(),
            "day_of_week": now.weekday(),
            "hour": now.hour,
            "minute": now.minute,
            "title": title
        })

    def record_stream_end(self, video_id: str, duration_seconds: int) -> int:
        """Record when a stream ends"""
        return self.update(
            "stream_times",
            {"stream_end": datetime.now().isoformat(), "duration_seconds": duration_seconds},
            "video_id = ? AND stream_end IS NULL",
            (video_id,)
        )

    def is_stream_already_ended(self, video_id: str) -> bool:
        """
        Check if a stream has already been detected and ended.
        This prevents re-detecting old streams as live.

        🤖🧠 [QWEN] Intelligence: Learn from past detections to prevent false positives
        """
        result = self.select(
            "stream_times",
            "video_id = ? AND stream_end IS NOT NULL",
            (video_id,)
        )
        if result:
            logger.info(f"🤖🧠 [QWEN-DB] Stream {video_id} already ended - preventing false positive")
            return True
        return False

    def get_recent_stream_for_channel(self, channel_id: str, hours: int = 24) -> Optional[Dict]:
        """
        Get the most recent stream for a channel within the specified hours.

        🤖🧠 [QWEN] Intelligence: Track recent streams to avoid duplicate detection
        """
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        result = self.select(
            "stream_times",
            "channel_id = ? AND stream_start > ? ORDER BY stream_start DESC LIMIT 1",
            (channel_id, cutoff)
        )
        if result:
            logger.info(f"🤖🧠 [QWEN-DB] Found recent stream for {channel_id}: {result[0]['video_id']}")
            return result[0]
        return None

    def record_check(self, channel_id: str, found: bool, response_time_ms: int = None) -> int:
        """Record a stream check attempt"""
        now = datetime.now()
        return self.insert("check_history", {
            "channel_id": channel_id,
            "timestamp": now.isoformat(),
            "found": found,
            "day_of_week": now.weekday(),
            "hour": now.hour,
            "response_time_ms": response_time_ms
        })

    def update_channel_stats(self, channel_id: str, response_time_ms: int = None) -> None:
        """Update channel statistics after a check"""
        # Get current stats
        stats = self.select("channel_stats", "channel_id = ?", (channel_id,))

        if not stats:
            # First time seeing this channel
            self.insert("channel_stats", {
                "channel_id": channel_id,
                "total_checks": 1,
                "streams_found": 0,
                "avg_response_time_ms": response_time_ms or 0,
                "last_check": datetime.now().isoformat()
            })
        else:
            stat = stats[0]
            total_checks = stat['total_checks'] + 1
            avg_response = stat['avg_response_time_ms']

            if response_time_ms is not None:
                # Update rolling average
                avg_response = (avg_response * stat['total_checks'] + response_time_ms) / total_checks

            self.update(
                "channel_stats",
                {
                    "total_checks": total_checks,
                    "avg_response_time_ms": avg_response,
                    "last_check": datetime.now().isoformat()
                },
                "channel_id = ?",
                (channel_id,)
            )

    def get_stream_patterns(self, channel_id: str) -> Dict[str, Any]:
        """Get learned patterns for a channel"""
        patterns = self.select("stream_patterns", "channel_id = ?", (channel_id,))

        result = {}
        for pattern in patterns:
            try:
                result[pattern['pattern_type']] = {
                    "data": json.loads(pattern['pattern_data']),
                    "confidence": pattern['confidence'],
                    "last_updated": pattern['last_updated']
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to decode pattern data for {pattern['pattern_type']}")

        return result

    def save_stream_pattern(self, channel_id: str, pattern_type: str,
                           pattern_data: Dict[str, Any], confidence: float = 0.0) -> int:
        """
        Save a learned pattern using INSERT OR REPLACE to handle UNIQUE constraint.

        The stream_patterns table has UNIQUE(channel_id, pattern_type), so we must use
        INSERT OR REPLACE instead of generic upsert() which only checks 'id' field.

        This prevents "UNIQUE constraint failed" errors when updating existing patterns.
        """
        full_table = self._get_full_table_name("stream_patterns")

        query = f"""
            INSERT OR REPLACE INTO {full_table}
            (channel_id, pattern_type, pattern_data, confidence, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """

        params = (
            channel_id,
            pattern_type,
            json.dumps(pattern_data),
            confidence,
            datetime.now().isoformat()
        )

        return self.db.execute_write(query, params)

    def get_optimal_check_times(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get optimal times to check for streams based on historical data"""
        # Get stream times for the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)

        streams = self.select(
            "stream_times",
            "channel_id = ? AND stream_start > ?",
            (channel_id, thirty_days_ago.isoformat()),
            "stream_start ASC"
        )

        if not streams:
            return []

        # Analyze patterns by hour of day
        hourly_patterns = {}
        for stream in streams:
            hour = stream['hour']
            if hour not in hourly_patterns:
                hourly_patterns[hour] = {"count": 0, "days": set()}

            hourly_patterns[hour]["count"] += 1
            hourly_patterns[hour]["days"].add(stream['day_of_week'])

        # Calculate confidence scores
        optimal_times = []
        for hour, data in hourly_patterns.items():
            confidence = min(data["count"] / 10.0, 1.0)  # Max confidence at 10 streams
            avg_per_day = data["count"] / max(len(data["days"]), 1)

            optimal_times.append({
                "hour": hour,
                "stream_count": data["count"],
                "avg_per_day": avg_per_day,
                "confidence": confidence,
                "recommendation": "HIGH" if confidence > 0.7 else "MEDIUM" if confidence > 0.3 else "LOW"
            })

        return sorted(optimal_times, key=lambda x: x["confidence"], reverse=True)

    def get_channel_stats(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a channel"""
        stats = self.select("channel_stats", "channel_id = ?", (channel_id,))
        return stats[0] if stats else None

    def get_recent_streams(self, channel_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent streams for a channel"""
        return self.select(
            "stream_times",
            "channel_id = ?",
            (channel_id,),
            "stream_start DESC",
            limit
        )

    def predict_next_stream_time(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Predict when the next stream might start based on patterns"""
        patterns = self.get_optimal_check_times(channel_id)

        if not patterns:
            return None

        # Get the most confident prediction
        best_pattern = patterns[0]

        # Find the next occurrence of this hour
        now = datetime.now()
        next_check = now.replace(hour=best_pattern["hour"], minute=0, second=0, microsecond=0)

        if next_check <= now:
            next_check = next_check + timedelta(days=1)

        return {
            "predicted_hour": best_pattern["hour"],
            "confidence": best_pattern["confidence"],
            "next_check_time": next_check.isoformat(),
            "reason": f"Based on {best_pattern['stream_count']} historical streams"
        }

    def migrate_json_data(self) -> None:
        """Migrate data from JSON files to database"""
        logger.info("Starting JSON data migration...")

        # Migrate stream_history.json
        try:
            if os.path.exists("memory/stream_history.json"):
                with open("memory/stream_history.json", "r") as f:
                    history = json.load(f)

                # This is minimal data, just log it
                logger.info(f"Migrated stream history: {history}")
        except Exception as e:
            logger.error(f"Failed to migrate stream_history.json: {e}")

        # Migrate stream_schedule_patterns.json
        try:
            if os.path.exists("memory/stream_schedule_patterns.json"):
                with open("memory/stream_schedule_patterns.json", "r") as f:
                    patterns = json.load(f)

                if "stream_times" in patterns:
                    for stream_time in patterns["stream_times"]:
                        try:
                            # Convert to database format
                            dt = datetime.fromisoformat(stream_time["timestamp"])
                            self.insert("stream_times", {
                                "channel_id": "UC-LSSlOZwpGIRIYihaz8zCw",  # Default channel
                                "video_id": stream_time["video_id"],
                                "stream_start": stream_time["timestamp"],
                                "day_of_week": stream_time["day_of_week"],
                                "hour": stream_time["hour"],
                                "minute": stream_time["minute"],
                                "title": f"Stream at {stream_time['hour']}:{stream_time['minute']:02d}",
                                "created_at": datetime.now().isoformat()
                            })
                        except Exception as e:
                            logger.error(f"Failed to migrate stream time: {e}")

                logger.info(f"Migrated {len(patterns.get('stream_times', []))} stream patterns")
        except Exception as e:
            logger.error(f"Failed to migrate stream_schedule_patterns.json: {e}")

        logger.info("JSON data migration completed")

    def analyze_and_update_patterns(self, channel_id: str) -> None:
        """Analyze recent stream data and update patterns for better predictions."""
        logger.info(f"Analyzing patterns for channel {channel_id}")

        # Get recent stream data for analysis (last 30 days)
        recent_streams = self.get_recent_streams(channel_id, limit=50)

        if not recent_streams:
            logger.info(f"No recent streams to analyze for {channel_id}")
            return

        # Analyze hour patterns
        hour_frequency = {}
        day_frequency = {}

        for stream in recent_streams:
            hour = stream['hour']
            day = stream['day_of_week']

            hour_frequency[hour] = hour_frequency.get(hour, 0) + 1
            day_frequency[day] = day_frequency.get(day, 0) + 1

        # Calculate confidence based on consistency
        total_streams = len(recent_streams)

        # Find most common hour with confidence
        if hour_frequency:
            most_common_hour = max(hour_frequency.keys(), key=lambda h: hour_frequency[h])
            hour_confidence = hour_frequency[most_common_hour] / total_streams

            # Save hour pattern
            self.save_stream_pattern(
                channel_id,
                "preferred_hour",
                {
                    "hour": most_common_hour,
                    "frequency": hour_frequency[most_common_hour],
                    "distribution": hour_frequency
                },
                confidence=hour_confidence
            )
            logger.info(f"Updated hour pattern: {most_common_hour}:00 (confidence: {hour_confidence:.2f})")

        # Find most common day with confidence
        if day_frequency:
            most_common_day = max(day_frequency.keys(), key=lambda d: day_frequency[d])
            day_confidence = day_frequency[most_common_day] / total_streams

            # Save day pattern
            self.save_stream_pattern(
                channel_id,
                "preferred_day",
                {
                    "day_of_week": most_common_day,
                    "frequency": day_frequency[most_common_day],
                    "distribution": day_frequency
                },
                confidence=day_confidence
            )

            # Map day number to name for logging
            day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            day_name = day_names[most_common_day] if most_common_day < 7 else str(most_common_day)
            logger.info(f"Updated day pattern: {day_name} (confidence: {day_confidence:.2f})")

        # Calculate average stream duration for better timing
        durations = [s['duration_seconds'] for s in recent_streams if s.get('duration_seconds')]
        if durations:
            avg_duration = sum(durations) / len(durations)
            self.save_stream_pattern(
                channel_id,
                "average_duration",
                {"seconds": avg_duration, "minutes": avg_duration / 60},
                confidence=0.7 if len(durations) > 5 else 0.4
            )
            logger.info(f"Updated duration pattern: {avg_duration/60:.1f} minutes average")

    def get_stream_analytics(self, channel_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics for a channel"""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Get streams in time period
        streams = self.select(
            "stream_times",
            "channel_id = ? AND stream_start > ?",
            (channel_id, cutoff_date.isoformat())
        )

        # Get checks in time period
        checks = self.select(
            "check_history",
            "channel_id = ? AND timestamp > ?",
            (channel_id, cutoff_date.isoformat())
        )

        # Calculate metrics
        total_streams = len(streams)
        total_checks = len(checks)
        successful_checks = len([c for c in checks if c['found']])

        # Average streams per day
        days_covered = days
        avg_streams_per_day = total_streams / days_covered if days_covered > 0 else 0

        # Success rate
        success_rate = successful_checks / total_checks if total_checks > 0 else 0

        # Most common stream hours
        hour_counts = {}
        for stream in streams:
            hour = stream['hour']
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        most_common_hour = max(hour_counts.keys(), key=lambda h: hour_counts[h]) if hour_counts else None

        return {
            "channel_id": channel_id,
            "time_period_days": days,
            "total_streams": total_streams,
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "success_rate": success_rate,
            "avg_streams_per_day": avg_streams_per_day,
            "most_common_stream_hour": most_common_hour,
            "streams_by_hour": hour_counts
        }
