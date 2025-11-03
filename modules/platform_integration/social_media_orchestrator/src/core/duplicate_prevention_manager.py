"""
Duplicate Prevention Manager with QWEN Intelligence
Handles all duplicate post detection and history management with AI-powered decision-making
Enhanced with QWEN intelligence for platform health monitoring and pattern learning
"""

import os
import json
import sqlite3
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from enum import Enum


class PlatformHealth(Enum):
    """Health status of a social media platform"""
    HEALTHY = "HEALTHY"          # All good
    WARMING = "WARMING"          # Starting to hit limits
    HOT = "HOT"                  # Close to rate limits
    OVERHEATED = "OVERHEATED"    # Rate limited
    OFFLINE = "OFFLINE"          # Platform unavailable


class PostingStatus(Enum):
    """Status of a social media post"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RATE_LIMITED = "RATE_LIMITED"
    DUPLICATE = "DUPLICATE"
    SKIPPED = "SKIPPED"


class StreamState(Enum):
    """Current state tracked for a stream in the duplicate registry."""
    NEW = "NEW"
    POSTED = "POSTED"
    AUTO_MARKED = "AUTO_MARKED"
    ENDED = "ENDED"
    BLOCKED = "BLOCKED"
    STALE_ENDED = "STALE_ENDED"  # Auto-blocked due to ended/stale status
    LIVE_VERIFIED = "LIVE_VERIFIED"
    FAILED_ATTEMPT = "FAILED_ATTEMPT"


class DuplicatePreventionManager:
    """
    Manages duplicate post prevention across all platforms with QWEN intelligence.

    QWEN Features:
    - Platform health monitoring (heat levels)
    - Intelligent posting decisions
    - Pattern learning from outcomes
    - Rate limit prevention
    - Optimal timing and staggering
    """

    def __init__(self, db_path: str = None, json_path: str = None, qwen_enabled: bool = True):
        """
        Initialize duplicate prevention manager with QWEN intelligence

        Args:
            db_path: Path to SQLite database
            json_path: Path to JSON backup file
            qwen_enabled: Enable QWEN intelligence features
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.qwen_enabled = qwen_enabled

        # Default paths
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'memory', 'orchestrator_posted_streams.db'
        )
        self.json_path = json_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'memory', 'orchestrator_posted_streams.json'
        )

        # QWEN pattern memory path
        self.qwen_memory_path = Path(os.path.dirname(self.json_path)) / "qwen_patterns"
        if self.qwen_enabled:
            self.qwen_memory_path.mkdir(parents=True, exist_ok=True)

        # In-memory cache
        self.posted_streams = {}

        # QWEN Platform tracking
        self.platform_status = {
            'linkedin': {'health': PlatformHealth.HEALTHY, 'heat': 0, 'last_post': None},
            'x_twitter': {'health': PlatformHealth.HEALTHY, 'heat': 0, 'last_post': None},
            'discord': {'health': PlatformHealth.HEALTHY, 'heat': 0, 'last_post': None},
            'facebook': {'health': PlatformHealth.HEALTHY, 'heat': 0, 'last_post': None},
            'instagram': {'health': PlatformHealth.HEALTHY, 'heat': 0, 'last_post': None}
        }

        # QWEN Active posts tracking
        self.active_posts = {}

        # QWEN Pattern storage
        self.posting_patterns = []

        # Initialize storage
        self._ensure_database_exists()
        self._load_posted_history()

        # Load QWEN patterns if enabled
        if self.qwen_enabled:
            self._load_qwen_patterns()
            self.logger.info("[BOT][AI] [QWEN-SOCIAL] Intelligence features enabled")

    def _ensure_database_exists(self) -> None:
        """Ensure database and tables exist"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS posted_streams (
                        video_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        title TEXT,
                        url TEXT,
                        platforms_posted TEXT NOT NULL,
                        status TEXT DEFAULT 'POSTED',
                        ended_at TEXT,
                        notes TEXT
                    )
                ''')
                self._ensure_schema_columns(cursor)
                conn.commit()
                self.logger.info(f"[DB] Database initialized at {self.db_path}")

        except Exception as e:
            self.logger.error(f"[DB] Failed to initialize database: {e}")

    def _ensure_schema_columns(self, cursor: sqlite3.Cursor) -> None:
        """Ensure new schema columns exist for stream state tracking."""
        try:
            cursor.execute("PRAGMA table_info(posted_streams)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            if 'status' not in existing_columns:
                cursor.execute("ALTER TABLE posted_streams ADD COLUMN status TEXT DEFAULT 'POSTED'")
            if 'ended_at' not in existing_columns:
                cursor.execute("ALTER TABLE posted_streams ADD COLUMN ended_at TEXT")
            if 'notes' not in existing_columns:
                cursor.execute("ALTER TABLE posted_streams ADD COLUMN notes TEXT")
        except Exception as exc:
            self.logger.debug(f"[DB] Schema check failed: {exc}")

    def _load_posted_history(self) -> None:
        """Load posted history from database and JSON backup"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                rows = []
                try:
                    cursor.execute('''
                        SELECT video_id, timestamp, title, url, platforms_posted, status, ended_at, notes
                        FROM posted_streams
                    ''')
                    rows = cursor.fetchall()
                    for row in rows:
                        video_id, timestamp, title, url, platforms_str, status, ended_at, notes = row
                        platforms = json.loads(platforms_str) if platforms_str else []
                        self.posted_streams[video_id] = {
                            'timestamp': timestamp,
                            'title': title,
                            'url': url,
                            'platforms_posted': platforms,
                            'status': status or (StreamState.POSTED.value if platforms else StreamState.NEW.value),
                            'ended_at': ended_at,
                            'notes': notes
                        }
                except sqlite3.OperationalError:
                    cursor.execute('''
                        SELECT video_id, timestamp, title, url, platforms_posted
                        FROM posted_streams
                    ''')
                    rows = cursor.fetchall()
                    for row in rows:
                        video_id, timestamp, title, url, platforms_str = row
                        platforms = json.loads(platforms_str) if platforms_str else []
                        self.posted_streams[video_id] = {
                            'timestamp': timestamp,
                            'title': title,
                            'url': url,
                            'platforms_posted': platforms,
                            'status': StreamState.POSTED.value if platforms else StreamState.NEW.value,
                            'ended_at': None,
                            'notes': None
                        }
                self.logger.info(f"[DB] Loaded {len(self.posted_streams)} posted streams from database")
        except Exception as e:
            self.logger.warning(f"[DB] Could not load from database: {e}")
            self._load_posted_history_json()

    def _load_posted_history_json(self) -> None:
        """Load posted history from JSON backup"""
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r', encoding="utf-8") as f:
                    self.posted_streams = json.load(f)
                    for video_id, data in self.posted_streams.items():
                        data.setdefault('platforms_posted', [])
                        status = data.get('status')
                        if not status:
                            data['status'] = StreamState.POSTED.value if data['platforms_posted'] else StreamState.NEW.value
                        data.setdefault('ended_at', None)
                        data.setdefault('notes', None)
                    self.logger.info(f"[JSON] Loaded {len(self.posted_streams)} posted streams from JSON")
        except Exception as e:
            self.logger.warning(f"[JSON] Could not load history: {e}")
            self.posted_streams = {}

    def check_if_already_posted(self, video_id: str, live_status_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Check if a video has already been posted with enhanced logging and QWEN intelligence
        Now integrates live status to prevent posting about ended/stale streams

        Args:
            video_id: YouTube video ID
            live_status_info: Optional live status from LiveStatusVerifier
                            {'broadcast_content': 'live'|'completed'|'none',
                             'actual_end': ISO timestamp,
                             'age_hours': float}

        Returns:
            Dictionary with posting status and details
        """
        self.logger.info('=' * 60)
        self.logger.info('[DUPLICATE] Check initiated')
        if self.qwen_enabled:
            self.logger.info('[QWEN] Duplicate analysis active')
        self.logger.info(f'[DUPLICATE] Video ID: {video_id}')
        self.logger.info('=' * 60)

        default_result = {
            'video_id': video_id,
            'already_posted': False,
            'platforms_posted': [],
            'timestamp': None,
            'status': StreamState.NEW.value,
            'notes': None,
            'ended_at': None,
            'blocked_reason': None
        }

        self.logger.info('[CACHE] Checking in-memory cache...')
        if video_id in self.posted_streams:
            entry = self.posted_streams[video_id]
            platforms = entry.get('platforms_posted', [])
            timestamp = entry.get('timestamp')
            status_value = entry.get('status') or (StreamState.POSTED.value if platforms else StreamState.NEW.value)

            if platforms == ['failed_attempt'] and timestamp:
                try:
                    posted_time = datetime.fromisoformat(timestamp)
                    if datetime.now() - posted_time > timedelta(minutes=5):
                        self.logger.info('[CACHE] Failed attempt expired (>5 min); allowing retry')
                        self.posted_streams.pop(video_id, None)
                        self.logger.info('[CACHE] Cache entry cleared for retry')
                    else:
                        minutes_remaining = max(0, 5 - int((datetime.now() - posted_time).total_seconds() / 60))
                        entry['status'] = StreamState.FAILED_ATTEMPT.value
                        result = self._build_result_from_entry(video_id, entry)
                        result['blocked_reason'] = 'failed_attempt_cooldown'
                        self.logger.info(f'[CACHE] Failed attempt recorded; retry in {minutes_remaining} min')
                        self.logger.info('=' * 60)
                        return result
                except Exception:
                    pass

            entry['status'] = status_value
            result = self._build_result_from_entry(video_id, entry)

            if result['already_posted']:
                self._log_blocked_result('cache', result)
            else:
                self.logger.info('[CACHE] No prior posting recorded')

            self.logger.info('=' * 60)
            return result

        self.logger.info('[CACHE] Not found in memory cache')

        self.logger.info('[DB] Checking database...')
        db_result = self._check_database_for_post(video_id)
        if db_result:
            if db_result['already_posted']:
                self._log_blocked_result('database', db_result)
            else:
                self.logger.info('[DB] No prior posting recorded in database')
            self.logger.info('=' * 60)
            return db_result

        # INTEGRATE LIVE STATUS: Check if video is ended/stale before approving
        if live_status_info:
            stale_check = self._check_live_status_for_stale_content(video_id, live_status_info)
            if stale_check['is_stale']:
                # Override decision: block posting of ended/stale content
                default_result['already_posted'] = True  # Block posting
                default_result['blocked_reason'] = stale_check['reason']
                default_result['status'] = StreamState.STALE_ENDED.value
                default_result['ended_at'] = live_status_info.get('actual_end')
                default_result['notes'] = f"Auto-blocked: {stale_check['reason']}"

                # Persist this decision to prevent future checks (don't use mark_as_posted for blocks)
                self.posted_streams[video_id] = {
                    'timestamp': datetime.now().isoformat(),
                    'title': live_status_info.get('title', 'Unknown'),
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'platforms_posted': [],  # No platforms posted - it was blocked
                    'status': StreamState.STALE_ENDED.value,
                    'ended_at': live_status_info.get('actual_end'),
                    'notes': f"Auto-blocked: {stale_check['reason']}"
                }

                self.logger.info(f'[DUPLICATE] [FAIL] BLOCKED: {stale_check["reason"]}')
                self.logger.info('=' * 60)
                return default_result

        self.logger.info('[DUPLICATE] [OK] Video not recorded and not stale; safe to post')
        self.logger.info('=' * 60)
        return default_result

    def _check_live_status_for_stale_content(self, video_id: str, live_status_info: Dict[str, Any]) -> Dict[str, bool]:
        """
        Check if live status indicates stale/ended content that should be blocked

        Args:
            video_id: YouTube video ID
            live_status_info: Live status from LiveStatusVerifier

        Returns:
            Dict with 'is_stale' boolean and 'reason' string
        """
        broadcast_content = live_status_info.get('broadcast_content', 'none')
        age_hours = live_status_info.get('age_hours')

        # Always allow live streams
        if broadcast_content == 'live':
            return {'is_stale': False, 'reason': 'Stream is currently live'}

        # Block completed/ended streams
        if broadcast_content == 'completed':
            if age_hours is not None:
                if age_hours > 24:  # More than 1 day old
                    return {'is_stale': True, 'reason': f'Stream ended {age_hours:.1f} hours ago (>24h threshold)'}
                else:
                    return {'is_stale': True, 'reason': f'Stream has ended (age: {age_hours:.1f}h)'}
            else:
                return {'is_stale': True, 'reason': 'Stream has ended'}

        # Block streams that never went live (none status with end time)
        if broadcast_content == 'none' and live_status_info.get('actual_end'):
            return {'is_stale': True, 'reason': 'Stream never went live and has end time'}

        # Allow upcoming streams and unknown statuses
        return {'is_stale': False, 'reason': f'Stream status allows posting: {broadcast_content}'}

    def _build_result_from_entry(self, video_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Build a standardized result dictionary from an entry"""
        platforms = entry.get('platforms_posted', [])
        status = entry.get('status', StreamState.NEW.value)

        return {
            'video_id': video_id,
            'already_posted': len(platforms) > 0 or status in [StreamState.STALE_ENDED.value, StreamState.BLOCKED.value],
            'platforms_posted': platforms,
            'timestamp': entry.get('timestamp'),
            'status': status,
            'notes': entry.get('notes'),
            'ended_at': entry.get('ended_at'),
            'blocked_reason': entry.get('notes') if status == StreamState.STALE_ENDED.value else None
        }

    def _log_blocked_result(self, source: str, result: Dict[str, Any]) -> None:
        """Log a blocked result with appropriate messaging"""
        video_id = result.get('video_id')
        platforms = result.get('platforms_posted', [])
        blocked_reason = result.get('blocked_reason', 'already posted')
        status = result.get('status', 'unknown')

        if platforms:
            self.logger.info(f'[{source.upper()}] [FAIL] BLOCKED: Already posted to {platforms}')
        elif blocked_reason != 'already posted':
            self.logger.info(f'[{source.upper()}] [FAIL] BLOCKED: {blocked_reason}')
        else:
            self.logger.info(f'[{source.upper()}] [FAIL] BLOCKED: Status {status}')

    def _check_database_for_post(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Check database for posted video"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute('''
                        SELECT timestamp, title, url, platforms_posted, status, ended_at, notes
                        FROM posted_streams
                        WHERE video_id = ?
                    ''', (video_id,))
                    row = cursor.fetchone()
                except sqlite3.OperationalError:
                    cursor.execute('''
                        SELECT timestamp, title, url, platforms_posted
                        FROM posted_streams
                        WHERE video_id = ?
                    ''', (video_id,))
                    row = cursor.fetchone()
                    if not row:
                        return None
                    timestamp, title, url, platforms_str = row
                    platforms = json.loads(platforms_str) if platforms_str else []
                    entry = {
                        'timestamp': timestamp,
                        'title': title,
                        'url': url,
                        'platforms_posted': platforms,
                        'status': StreamState.POSTED.value if platforms else StreamState.NEW.value,
                        'ended_at': None,
                        'notes': None
                    }
                    self.posted_streams[video_id] = entry
                    return self._build_result_from_entry(video_id, entry)

                if not row:
                    return None

                timestamp, title, url, platforms_str, status, ended_at, notes = row
                platforms = json.loads(platforms_str) if platforms_str else []
                entry = {
                    'timestamp': timestamp,
                    'title': title,
                    'url': url,
                    'platforms_posted': platforms,
                    'status': status or (StreamState.POSTED.value if platforms else StreamState.NEW.value),
                    'ended_at': ended_at,
                    'notes': notes
                }
                self.posted_streams[video_id] = entry
                return self._build_result_from_entry(video_id, entry)

        except Exception as e:
            self.logger.warning(f"[DB] Could not load from database: {e}")
        return None

    def mark_as_posted(self, video_id: str, platform: str, title: str = None, url: str = None) -> None:
        """
        Mark a video as posted to a specific platform

        Args:
            video_id: YouTube video ID
            platform: Platform name (linkedin, x_twitter, etc)
            title: Optional video title
            url: Optional video URL
        """
        timestamp = datetime.now().isoformat()

        entry = self.posted_streams.get(video_id, {
            'timestamp': timestamp,
            'title': title,
            'url': url,
            'platforms_posted': [],
            'status': StreamState.NEW.value,
            'ended_at': None,
            'notes': None
        })

        if title:
            entry['title'] = title
        if url:
            entry['url'] = url

        entry['timestamp'] = timestamp
        entry.setdefault('platforms_posted', [])
        if platform not in entry['platforms_posted']:
            entry['platforms_posted'].append(platform)

        entry['status'] = StreamState.POSTED.value
        entry['ended_at'] = None
        entry['notes'] = None

        self.posted_streams[video_id] = entry

        self._save_to_database(
            video_id,
            entry['timestamp'],
            entry.get('title'),
            entry.get('url'),
            entry['platforms_posted'],
            entry['status'],
            entry.get('ended_at'),
            entry.get('notes')
        )

        self._save_posted_history_json()

        self.logger.info(f"[MARKED] Video {video_id} marked as posted to {platform}")

    def _save_to_database(self, video_id: str, timestamp: str, title: Optional[str],
                          url: Optional[str], platforms: List[str], status: str,
                          ended_at: Optional[str], notes: Optional[str]) -> None:
        """Save posted status to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO posted_streams
                    (video_id, timestamp, title, url, platforms_posted, status, ended_at, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video_id,
                    timestamp,
                    title,
                    url,
                    json.dumps(platforms),
                    status,
                    ended_at,
                    notes
                ))
                conn.commit()

        except Exception as e:
            self.logger.error(f"[DB] Failed to save to database: {e}")

    def _save_posted_history_json(self) -> None:
        """Save posted history to JSON backup"""
        try:
            os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
            with open(self.json_path, 'w', encoding="utf-8") as f:
                json.dump(self.posted_streams, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"[JSON] Failed to save history: {e}")

    def get_posting_stats(self) -> Dict[str, int]:
        """Get posting statistics with QWEN platform health"""
        stats = {
            'total_videos': len(self.posted_streams),
            'linkedin_posts': 0,
            'x_twitter_posts': 0,
            'multi_platform_posts': 0
        }

        for video_id, info in self.posted_streams.items():
            platforms = info.get('platforms_posted', [])
            if 'linkedin' in platforms:
                stats['linkedin_posts'] += 1
            if 'x_twitter' in platforms:
                stats['x_twitter_posts'] += 1
            if len(platforms) > 1:
                stats['multi_platform_posts'] += 1

        # Add QWEN platform health if enabled
        if self.qwen_enabled:
            stats['platform_health'] = {
                platform: {
                    'health': status['health'].value,
                    'heat': status['heat']
                }
                for platform, status in self.platform_status.items()
            }

        return stats

    # ========== QWEN INTELLIGENCE METHODS ==========

    def qwen_pre_posting_check(self, stream_info: Dict[str, Any],
                               target_platforms: List[str]) -> Dict[str, Any]:
        """
        QWEN intelligence check before posting to social media

        Args:
            stream_info: Information about the stream
            target_platforms: List of target platforms

        Returns:
            QWEN decision on whether/how to post
        """
        if not self.qwen_enabled:
            return {
                'should_post': True,
                'approved_platforms': target_platforms,
                'posting_order': target_platforms,
                'delays': {platform: 0 for platform in target_platforms},
                'warnings': [],
                'qwen_active': False
            }

        self.logger.info("[BOT][AI] [QWEN-PRE-POST] ======== PRE-POSTING ANALYSIS ========")

        decision = {
            'should_post': True,
            'approved_platforms': [],
            'rejected_platforms': {},
            'posting_order': [],
            'delays': {},
            'warnings': [],
            'optimizations': [],
            'qwen_active': True
        }

        video_id = stream_info.get('video_id')

        # 1. Enhanced duplicate check with time window
        duplicate_check = self._qwen_check_duplicate_window(video_id)
        if duplicate_check['is_duplicate']:
            self.logger.warning(f"[BOT][AI] [QWEN-DUPLICATE] Posted {duplicate_check['minutes_ago']} minutes ago!")
            decision['should_post'] = False
            decision['warnings'].append(f"Duplicate - posted {duplicate_check['minutes_ago']}m ago")
            return decision

        # 2. Platform health check
        for platform in target_platforms:
            health_check = self._qwen_check_platform_health(platform)

            if health_check['can_post']:
                decision['approved_platforms'].append(platform)
                decision['delays'][platform] = health_check['recommended_delay']
            else:
                decision['rejected_platforms'][platform] = health_check['reason']
                self.logger.info(f"[BOT][AI] [QWEN-REJECT] {platform}: {health_check['reason']}")

        # 3. Optimize posting order
        if decision['approved_platforms']:
            decision['posting_order'] = self._qwen_optimize_posting_order(
                decision['approved_platforms'], stream_info
            )
            self._qwen_add_stagger_delays(decision)

        # 4. Pattern-based optimizations
        optimizations = self._qwen_get_posting_optimizations(stream_info)
        decision['optimizations'] = optimizations

        self.logger.info(f"[BOT][AI] [QWEN-DECISION] Approved: {decision['approved_platforms']}")
        self.logger.info(f"[BOT][AI] [QWEN-ORDER] Posting order: {decision['posting_order']}")

        return decision

    def _qwen_check_duplicate_window(self, video_id: str, window_minutes: int = 30) -> Dict[str, Any]:
        """Check if video was posted within time window"""
        if video_id in self.posted_streams:
            posted_info = self.posted_streams[video_id]
            timestamp_str = posted_info.get('timestamp')

            if timestamp_str:
                try:
                    posted_time = datetime.fromisoformat(timestamp_str)
                    time_diff = (datetime.now() - posted_time).total_seconds() / 60

                    if time_diff < window_minutes:
                        return {
                            'is_duplicate': True,
                            'minutes_ago': int(time_diff),
                            'platforms': posted_info.get('platforms_posted', [])
                        }
                except Exception:
                    pass

        return {'is_duplicate': False}

    def _qwen_check_platform_health(self, platform: str) -> Dict[str, Any]:
        """Check if a platform is healthy enough for posting"""
        status = self.platform_status.get(platform, {})
        health = status.get('health', PlatformHealth.HEALTHY)
        heat = status.get('heat', 0)
        last_post = status.get('last_post')

        result = {
            'can_post': True,
            'recommended_delay': 0,
            'reason': None
        }

        # Check health status
        if health == PlatformHealth.OVERHEATED:
            result['can_post'] = False
            result['reason'] = "Platform overheated (rate limited)"
            return result
        elif health == PlatformHealth.OFFLINE:
            result['can_post'] = False
            result['reason'] = "Platform offline"
            return result

        # Check time since last post
        if last_post:
            time_since = time.time() - last_post

            # Platform-specific minimum delays
            min_delays = {
                'linkedin': 60,      # 1 minute minimum
                'x_twitter': 30,     # 30 seconds minimum
                'discord': 10,       # 10 seconds minimum
                'facebook': 120,     # 2 minutes minimum
                'instagram': 180     # 3 minutes minimum
            }

            min_delay = min_delays.get(platform, 30)

            if time_since < min_delay:
                result['recommended_delay'] = min_delay - time_since
                self.logger.info(f"[BOT][AI] [QWEN-DELAY] {platform}: Wait {result['recommended_delay']:.0f}s")

        # Adjust delay based on heat
        if heat >= 3:
            result['recommended_delay'] += 120  # Add 2 minutes
        elif heat >= 2:
            result['recommended_delay'] += 60   # Add 1 minute
        elif heat >= 1:
            result['recommended_delay'] += 30   # Add 30 seconds

        return result

    def _qwen_optimize_posting_order(self, platforms: List[str],
                                    stream_info: Dict[str, Any]) -> List[str]:
        """Optimize the order of platform posting"""
        # Priority order based on importance and success rates
        priority_map = {
            'linkedin': 1,    # Professional network - highest priority
            'x_twitter': 2,   # Real-time engagement
            'facebook': 3,    # Broad reach
            'discord': 4,     # Community notification
            'instagram': 5    # Visual platform
        }

        # Adjust based on channel
        channel = stream_info.get('channel_name', '').lower()
        if 'foundups' in channel:
            priority_map['linkedin'] = 0  # FoundUps prioritizes LinkedIn
        elif 'move2japan' in channel:
            priority_map['instagram'] = 2  # Travel content
            priority_map['x_twitter'] = 1

        # Sort platforms by priority
        sorted_platforms = sorted(platforms, key=lambda p: priority_map.get(p, 99))

        # Further optimize based on platform health
        healthy_first = []
        degraded = []

        for platform in sorted_platforms:
            health = self.platform_status[platform]['health']
            if health == PlatformHealth.HEALTHY:
                healthy_first.append(platform)
            else:
                degraded.append(platform)

        return healthy_first + degraded

    def _qwen_add_stagger_delays(self, decision: Dict[str, Any]) -> None:
        """Add stagger delays to prevent simultaneous posting"""
        base_delay = 0
        stagger = 15  # 15 seconds between posts

        for platform in decision['posting_order']:
            if platform in decision['delays']:
                decision['delays'][platform] += base_delay
            else:
                decision['delays'][platform] = base_delay

            base_delay += stagger

            self.logger.info(f"[BOT][AI] [QWEN-STAGGER] {platform}: {decision['delays'][platform]}s delay")

    def _qwen_get_posting_optimizations(self, stream_info: Dict[str, Any]) -> List[str]:
        """Get optimization recommendations based on patterns"""
        optimizations = []

        # Time-based optimizations
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 11:
            optimizations.append("Morning peak hours - expect high engagement")
        elif 19 <= current_hour <= 21:
            optimizations.append("Evening peak hours - optimal posting time")
        elif 2 <= current_hour <= 6:
            optimizations.append("Low activity hours - consider delaying")

        # Channel-based optimizations
        channel = stream_info.get('channel_name', '').lower()
        if 'foundups' in channel:
            optimizations.append("Business content - prioritize LinkedIn")
        elif 'move2japan' in channel:
            optimizations.append("Travel content - include Instagram")

        return optimizations

    def qwen_monitor_posting_progress(self, post_id: str, platform: str,
                                     status: PostingStatus, details: Dict[str, Any] = None) -> None:
        """
        Monitor the progress of a posting attempt with QWEN intelligence

        Args:
            post_id: Unique identifier for the post
            platform: Platform being posted to
            status: Current status
            details: Additional details about the posting
        """
        if not self.qwen_enabled:
            return

        self.logger.info(f"[BOT][AI] [QWEN-MONITOR] {platform}: {status.value}")

        # Update active posts
        if status == PostingStatus.IN_PROGRESS:
            self.active_posts[post_id] = {
                'platform': platform,
                'start_time': time.time(),
                'stream_info': details.get('stream_info', {}) if details else {}
            }
        elif post_id in self.active_posts:
            # Post completed (success or failure)
            post_data = self.active_posts.pop(post_id)
            duration = time.time() - post_data['start_time']

            # Update platform health based on outcome
            self._qwen_update_platform_health(platform, status, details)

            # Learn from the outcome
            self._qwen_learn_from_posting(platform, status, duration, details)

    def _qwen_update_platform_health(self, platform: str, status: PostingStatus,
                                    details: Dict[str, Any] = None) -> None:
        """Update platform health based on posting outcome"""
        if platform not in self.platform_status:
            return

        platform_data = self.platform_status[platform]

        if status == PostingStatus.SUCCESS:
            # Cool down on success
            platform_data['heat'] = max(0, platform_data['heat'] - 1)
            platform_data['last_post'] = time.time()

            # Update health
            if platform_data['heat'] == 0:
                platform_data['health'] = PlatformHealth.HEALTHY
            elif platform_data['heat'] <= 2:
                platform_data['health'] = PlatformHealth.WARMING

            self.logger.info(f"[BOT][AI] [QWEN-HEALTH] {platform}: {platform_data['health'].value} (heat={platform_data['heat']})")

        elif status == PostingStatus.RATE_LIMITED:
            # Heat up on rate limit
            platform_data['heat'] = min(5, platform_data['heat'] + 2)
            platform_data['health'] = PlatformHealth.OVERHEATED

            self.logger.warning(f"[BOT][AI] [QWEN-HEAT] {platform}: OVERHEATED! (heat={platform_data['heat']})")

        elif status == PostingStatus.FAILED:
            # Slight heat increase on failure
            platform_data['heat'] = min(5, platform_data['heat'] + 1)

            if platform_data['heat'] >= 4:
                platform_data['health'] = PlatformHealth.OVERHEATED
            elif platform_data['heat'] >= 2:
                platform_data['health'] = PlatformHealth.HOT

    def _qwen_learn_from_posting(self, platform: str, status: PostingStatus,
                                duration: float, details: Dict[str, Any] = None) -> None:
        """Learn patterns from posting outcomes"""
        pattern = {
            'platform': platform,
            'status': status.value,
            'duration': duration,
            'time': datetime.now().isoformat(),
            'hour': datetime.now().hour,
            'day': datetime.now().strftime('%A')
        }

        # Store pattern
        self.posting_patterns.append(pattern)
        if len(self.posting_patterns) > 100:
            self.posting_patterns = self.posting_patterns[-100:]

        # Save to QWEN pattern memory
        if self.qwen_enabled:
            self._save_qwen_patterns()

        self.logger.info(f"[BOT][AI] [QWEN-LEARN] Recorded {platform} pattern: {status.value}")

    def _load_qwen_patterns(self) -> None:
        """Load QWEN patterns from memory"""
        patterns_file = self.qwen_memory_path / "posting_patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r', encoding="utf-8") as f:
                    self.posting_patterns = json.load(f)
                self.logger.info(f"[BOT][AI] [QWEN-LOAD] Loaded {len(self.posting_patterns)} patterns")
            except Exception as e:
                self.logger.error(f"[BOT][AI] [QWEN-ERROR] Failed to load patterns: {e}")

        # Load platform heat levels
        heat_file = self.qwen_memory_path / "platform_heat.json"
        if heat_file.exists():
            try:
                with open(heat_file, 'r', encoding="utf-8") as f:
                    heat_data = json.load(f)
                    for platform, heat in heat_data.items():
                        if platform in self.platform_status:
                            self.platform_status[platform]['heat'] = heat
            except Exception as e:
                self.logger.error(f"[BOT][AI] [QWEN-ERROR] Failed to load heat levels: {e}")

    def _save_qwen_patterns(self) -> None:
        """Save QWEN patterns to memory"""
        try:
            # Save posting patterns
            patterns_file = self.qwen_memory_path / "posting_patterns.json"
            with open(patterns_file, 'w', encoding="utf-8") as f:
                json.dump(self.posting_patterns, f, indent=2, default=str)

            # Save platform heat levels
            heat_file = self.qwen_memory_path / "platform_heat.json"
            heat_data = {
                platform: status['heat']
                for platform, status in self.platform_status.items()
            }
            with open(heat_file, 'w', encoding="utf-8") as f:
                json.dump(heat_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"[BOT][AI] [QWEN-ERROR] Failed to save patterns: {e}")

    def qwen_get_posting_report(self) -> Dict[str, Any]:
        """Get QWEN intelligence report on posting status"""
        if not self.qwen_enabled:
            return {'qwen_active': False}

        report = {
            'qwen_active': True,
            'platform_health': {},
            'active_posts': len(self.active_posts),
            'recent_patterns': len(self.posting_patterns)
        }

        for platform, status in self.platform_status.items():
            report['platform_health'][platform] = {
                'health': status['health'].value,
                'heat': status['heat'],
                'can_post': status['health'] not in [PlatformHealth.OVERHEATED, PlatformHealth.OFFLINE]
            }

        return report