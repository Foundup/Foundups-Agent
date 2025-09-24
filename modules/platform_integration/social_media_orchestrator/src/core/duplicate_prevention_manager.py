"""
Duplicate Prevention Manager
Handles all duplicate post detection and history management
Extracted from simple_posting_orchestrator.py for better separation of concerns
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class DuplicatePreventionManager:
    """Manages duplicate post prevention across all platforms"""

    def __init__(self, db_path: str = None, json_path: str = None):
        """
        Initialize duplicate prevention manager

        Args:
            db_path: Path to SQLite database
            json_path: Path to JSON backup file
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # Default paths
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'memory', 'orchestrator_posted_streams.db'
        )
        self.json_path = json_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'memory', 'orchestrator_posted_streams.json'
        )

        # In-memory cache
        self.posted_streams = {}

        # Initialize storage
        self._ensure_database_exists()
        self._load_posted_history()

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
                        platforms_posted TEXT NOT NULL
                    )
                ''')
                conn.commit()
                self.logger.info(f"[DB] Database initialized at {self.db_path}")

        except Exception as e:
            self.logger.error(f"[DB] Failed to initialize database: {e}")

    def _load_posted_history(self) -> None:
        """Load posted history from database and JSON backup"""
        # First try database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT video_id, timestamp, title, url, platforms_posted
                    FROM posted_streams
                ''')

                for row in cursor.fetchall():
                    video_id, timestamp, title, url, platforms_str = row
                    platforms = json.loads(platforms_str) if platforms_str else []

                    self.posted_streams[video_id] = {
                        'timestamp': timestamp,
                        'title': title,
                        'url': url,
                        'platforms_posted': platforms
                    }

                self.logger.info(f"[DB] Loaded {len(self.posted_streams)} posted streams from database")

        except Exception as e:
            self.logger.warning(f"[DB] Could not load from database: {e}")
            self._load_posted_history_json()

    def _load_posted_history_json(self) -> None:
        """Load posted history from JSON backup"""
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r') as f:
                    self.posted_streams = json.load(f)
                    self.logger.info(f"[JSON] Loaded {len(self.posted_streams)} posted streams from JSON")
        except Exception as e:
            self.logger.warning(f"[JSON] Could not load history: {e}")
            self.posted_streams = {}

    def check_if_already_posted(self, video_id: str) -> Dict[str, Any]:
        """
        Check if a video has already been posted with enhanced logging

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with posting status and details
        """
        self.logger.info("="*60)
        self.logger.info("🔍 DUPLICATE PREVENTION CHECK INITIATED")
        self.logger.info(f"📹 Video ID: {video_id}")
        self.logger.info("="*60)

        # Check in-memory cache first
        self.logger.info("📂 Checking in-memory cache...")
        if video_id in self.posted_streams:
            posted_info = self.posted_streams[video_id]
            platforms = posted_info.get('platforms_posted', [])
            timestamp = posted_info.get('timestamp')

            self.logger.info("✅ FOUND IN MEMORY CACHE:")
            self.logger.info(f"   • Platforms posted: {platforms}")
            self.logger.info(f"   • Posted at: {timestamp}")
            self.logger.info("🚫 DUPLICATE PREVENTION ACTIVE - Will skip these platforms")
            self.logger.info("="*60)

            return {
                'video_id': video_id,
                'already_posted': True,
                'platforms_posted': platforms,
                'timestamp': timestamp
            }

        self.logger.info("❌ NOT in memory cache")

        # Check database as backup
        self.logger.info("🗄️ Checking database...")
        db_result = self._check_database_for_post(video_id)

        if db_result and db_result.get('already_posted'):
            platforms = db_result.get('platforms_posted', [])
            timestamp = db_result.get('timestamp')

            self.logger.info("✅ FOUND IN DATABASE:")
            self.logger.info(f"   • Platforms posted: {platforms}")
            self.logger.info(f"   • Posted at: {timestamp}")
            self.logger.info("🚫 DUPLICATE PREVENTION ACTIVE - Will skip these platforms")
            self.logger.info("="*60)

            # Update memory cache
            self.posted_streams[video_id] = {
                'timestamp': timestamp,
                'platforms_posted': platforms
            }

            return db_result

        self.logger.info("❌ NOT in database")
        self.logger.info("✅ NEW VIDEO - OK to post to all platforms")
        self.logger.info("="*60)

        return {
            'video_id': video_id,
            'already_posted': False,
            'platforms_posted': [],
            'timestamp': None
        }

    def _check_database_for_post(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Check database for posted video"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, title, url, platforms_posted
                    FROM posted_streams
                    WHERE video_id = ?
                ''', (video_id,))

                row = cursor.fetchone()
                if row:
                    timestamp, title, url, platforms_str = row
                    platforms = json.loads(platforms_str) if platforms_str else []

                    return {
                        'video_id': video_id,
                        'already_posted': True,
                        'platforms_posted': platforms,
                        'timestamp': timestamp,
                        'title': title,
                        'url': url
                    }

        except Exception as e:
            self.logger.error(f"[DB] Error checking database: {e}")

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

        # Update in-memory cache
        if video_id not in self.posted_streams:
            self.posted_streams[video_id] = {
                'timestamp': timestamp,
                'title': title,
                'url': url,
                'platforms_posted': []
            }

        if platform not in self.posted_streams[video_id]['platforms_posted']:
            self.posted_streams[video_id]['platforms_posted'].append(platform)

        # Save to database
        self._save_to_database(video_id, timestamp, title, url,
                              self.posted_streams[video_id]['platforms_posted'])

        # Save to JSON backup
        self._save_posted_history_json()

        self.logger.info(f"[MARKED] Video {video_id} marked as posted to {platform}")

    def _save_to_database(self, video_id: str, timestamp: str, title: str,
                          url: str, platforms: List[str]) -> None:
        """Save posted status to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO posted_streams
                    (video_id, timestamp, title, url, platforms_posted)
                    VALUES (?, ?, ?, ?, ?)
                ''', (video_id, timestamp, title, url, json.dumps(platforms)))
                conn.commit()

        except Exception as e:
            self.logger.error(f"[DB] Failed to save to database: {e}")

    def _save_posted_history_json(self) -> None:
        """Save posted history to JSON backup"""
        try:
            os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
            with open(self.json_path, 'w') as f:
                json.dump(self.posted_streams, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"[JSON] Failed to save history: {e}")

    def get_posting_stats(self) -> Dict[str, int]:
        """Get posting statistics"""
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

        return stats