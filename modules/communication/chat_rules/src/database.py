#!/usr/bin/env python3
"""
Simple SQLite Database for Chat Rules System
WSP Compliant - Lightweight persistence layer
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class ChatRulesDB:
    """Simple SQLite database for chat rules persistence"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            # WSP-compliant data location
            module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(module_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "chat_rules.db")
        else:
            self.db_path = db_path
        
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Create tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Moderator profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS moderators (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    total_points INTEGER DEFAULT 0,
                    level TEXT DEFAULT 'ROOKIE',
                    whacks_count INTEGER DEFAULT 0,
                    daily_timeout_count INTEGER DEFAULT 0,
                    daily_reset_time TIMESTAMP,
                    combo_multiplier REAL DEFAULT 1.0,
                    last_action TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Timeout history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS timeout_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mod_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    target_name TEXT,
                    duration_seconds INTEGER,
                    points_earned INTEGER,
                    reason TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (mod_id) REFERENCES moderators (user_id)
                )
            ''')
            
            # Timeout stats table (summary by duration)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS timeout_stats (
                    mod_id TEXT NOT NULL,
                    duration_category TEXT NOT NULL,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (mod_id, duration_category),
                    FOREIGN KEY (mod_id) REFERENCES moderators (user_id)
                )
            ''')
            
            # Achievements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mod_id TEXT NOT NULL,
                    achievement_name TEXT NOT NULL,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (mod_id) REFERENCES moderators (user_id),
                    UNIQUE(mod_id, achievement_name)
                )
            ''')
            
            # User cooldowns table (for anti-gaming)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cooldowns (
                    mod_id TEXT NOT NULL,
                    cooldown_type TEXT NOT NULL,
                    expires_at TIMESTAMP,
                    PRIMARY KEY (mod_id, cooldown_type),
                    FOREIGN KEY (mod_id) REFERENCES moderators (user_id)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timeout_history_mod ON timeout_history(mod_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timeout_history_target ON timeout_history(target_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timeout_timestamp ON timeout_history(timestamp)')
            
            logger.info(f"Database initialized at {self.db_path}")
    
    # Moderator operations
    
    def get_or_create_moderator(self, user_id: str, display_name: str) -> Dict:
        """Get existing moderator or create new one"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Try to get existing
            cursor.execute('SELECT * FROM moderators WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            
            # Create new moderator
            cursor.execute('''
                INSERT INTO moderators (user_id, display_name) 
                VALUES (?, ?)
            ''', (user_id, display_name))
            
            return {
                'user_id': user_id,
                'display_name': display_name,
                'total_points': 0,
                'level': 'ROOKIE',
                'whacks_count': 0
            }
    
    def update_moderator_points(self, user_id: str, points: int, level: str = None):
        """Update moderator points and optionally level"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if level:
                cursor.execute('''
                    UPDATE moderators 
                    SET total_points = ?, level = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (points, level, user_id))
            else:
                cursor.execute('''
                    UPDATE moderators 
                    SET total_points = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (points, user_id))
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top moderators by points"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, display_name, total_points, level, whacks_count
                FROM moderators
                ORDER BY total_points DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Timeout tracking
    
    def record_timeout(self, mod_id: str, target_id: str, target_name: str, 
                      duration_seconds: int, points_earned: int, reason: str):
        """Record a timeout action"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert timeout record
            cursor.execute('''
                INSERT INTO timeout_history 
                (mod_id, target_id, target_name, duration_seconds, points_earned, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (mod_id, target_id, target_name, duration_seconds, points_earned, reason))
            
            # Update timeout stats
            duration_category = self._categorize_duration(duration_seconds)
            cursor.execute('''
                INSERT INTO timeout_stats (mod_id, duration_category, count)
                VALUES (?, ?, 1)
                ON CONFLICT(mod_id, duration_category) 
                DO UPDATE SET count = count + 1
            ''', (mod_id, duration_category))
            
            # Update moderator's whack count
            cursor.execute('''
                UPDATE moderators 
                SET whacks_count = whacks_count + 1,
                    last_action = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (mod_id,))
    
    def get_timeout_stats(self, mod_id: str) -> Dict[str, int]:
        """Get timeout statistics for a moderator"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT duration_category, count
                FROM timeout_stats
                WHERE mod_id = ?
            ''', (mod_id,))
            
            stats = {}
            for row in cursor.fetchall():
                stats[row['duration_category']] = row['count']
            
            return stats
    
    def get_recent_timeout_target(self, mod_id: str, target_id: str, minutes: int = 30) -> bool:
        """Check if mod recently timed out this target (for anti-gaming)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM timeout_history
                WHERE mod_id = ? 
                AND target_id = ?
                AND timestamp > datetime('now', '-' || ? || ' minutes')
            ''', (mod_id, target_id, minutes))
            
            return cursor.fetchone()['count'] > 0
    
    def get_recent_10s_timeouts(self, mod_id: str, minutes: int = 10) -> int:
        """Count recent 10-second timeouts (for spam detection)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM timeout_history
                WHERE mod_id = ?
                AND duration_seconds <= 10
                AND timestamp > datetime('now', '-' || ? || ' minutes')
            ''', (mod_id, minutes))
            
            return cursor.fetchone()['count']
    
    # Cooldown management
    
    def set_cooldown(self, mod_id: str, cooldown_type: str, minutes: int):
        """Set a cooldown for anti-gaming"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO cooldowns (mod_id, cooldown_type, expires_at)
                VALUES (?, ?, datetime('now', '+' || ? || ' minutes'))
            ''', (mod_id, cooldown_type, minutes))
    
    def check_cooldown(self, mod_id: str, cooldown_type: str) -> Optional[int]:
        """Check if cooldown is active, return minutes remaining"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT (julianday(expires_at) - julianday('now')) * 24 * 60 as minutes_left
                FROM cooldowns
                WHERE mod_id = ? AND cooldown_type = ?
                AND expires_at > datetime('now')
            ''', (mod_id, cooldown_type))
            
            row = cursor.fetchone()
            if row and row['minutes_left'] > 0:
                return int(row['minutes_left'])
            return None
    
    def clean_expired_cooldowns(self):
        """Remove expired cooldowns"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM cooldowns
                WHERE expires_at <= datetime('now')
            ''')
    
    # Achievement tracking
    
    def add_achievement(self, mod_id: str, achievement_name: str):
        """Add an achievement for a moderator"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO achievements (mod_id, achievement_name)
                    VALUES (?, ?)
                ''', (mod_id, achievement_name))
                return True
            except sqlite3.IntegrityError:
                # Achievement already exists
                return False
    
    def get_achievements(self, mod_id: str) -> List[str]:
        """Get all achievements for a moderator"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT achievement_name, earned_at
                FROM achievements
                WHERE mod_id = ?
                ORDER BY earned_at DESC
            ''', (mod_id,))
            
            return [row['achievement_name'] for row in cursor.fetchall()]
    
    # Daily reset handling
    
    def reset_daily_counts(self):
        """Reset daily timeout counts for all moderators"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE moderators
                SET daily_timeout_count = 0,
                    daily_reset_time = CURRENT_TIMESTAMP
                WHERE date(daily_reset_time) < date('now')
                OR daily_reset_time IS NULL
            ''')
    
    def get_daily_timeout_count(self, mod_id: str) -> int:
        """Get today's timeout count for a moderator"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # First check if we need to reset
            cursor.execute('''
                SELECT daily_timeout_count, daily_reset_time
                FROM moderators
                WHERE user_id = ?
            ''', (mod_id,))
            
            row = cursor.fetchone()
            if not row:
                return 0
            
            # Check if reset needed
            if row['daily_reset_time']:
                reset_time = datetime.fromisoformat(row['daily_reset_time'])
                if reset_time.date() < datetime.now().date():
                    # Reset needed
                    cursor.execute('''
                        UPDATE moderators
                        SET daily_timeout_count = 0,
                            daily_reset_time = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (mod_id,))
                    return 0
            
            return row['daily_timeout_count'] or 0
    
    def increment_daily_count(self, mod_id: str):
        """Increment daily timeout count"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE moderators
                SET daily_timeout_count = COALESCE(daily_timeout_count, 0) + 1
                WHERE user_id = ?
            ''', (mod_id,))
    
    # Utility methods
    
    def _categorize_duration(self, seconds: int) -> str:
        """Categorize timeout duration"""
        if seconds <= 10:
            return '10s'
        elif seconds <= 60:
            return '60s'
        elif seconds <= 300:
            return '5m'
        elif seconds <= 600:
            return '10m'
        elif seconds <= 3600:
            return '1h'
        else:
            return '24h'
    
    def migrate_from_json(self, json_path: str):
        """Migrate data from old JSON format to database"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for user_id, mod_data in data.get('moderators', {}).items():
                    # Insert moderator
                    cursor.execute('''
                        INSERT OR REPLACE INTO moderators 
                        (user_id, display_name, total_points, level, whacks_count)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        user_id,
                        mod_data.get('display_name', 'Unknown'),
                        mod_data.get('total_points', 0),
                        mod_data.get('level', 'ROOKIE'),
                        mod_data.get('whacks_count', 0)
                    ))
                    
                    # Insert achievements
                    for achievement in mod_data.get('achievements', []):
                        try:
                            cursor.execute('''
                                INSERT INTO achievements (mod_id, achievement_name)
                                VALUES (?, ?)
                            ''', (user_id, achievement))
                        except sqlite3.IntegrityError:
                            pass  # Achievement already exists
                
                logger.info(f"Migration complete from {json_path}")
                return True
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    db = ChatRulesDB()
    
    # Create/get a moderator
    mod = db.get_or_create_moderator("mod123", "TestMod")
    print(f"Moderator: {mod}")
    
    # Record a timeout
    db.record_timeout(
        mod_id="mod123",
        target_id="troll456",
        target_name="TrollUser",
        duration_seconds=60,
        points_earned=15,
        reason="MAGA spam"
    )
    
    # Update points
    db.update_moderator_points("mod123", 100, "BRONZE")
    
    # Get leaderboard
    leaderboard = db.get_leaderboard(limit=5)
    print(f"Leaderboard: {leaderboard}")
    
    # Check cooldowns
    db.set_cooldown("mod123", "severity_2", 10)
    remaining = db.check_cooldown("mod123", "severity_2")
    print(f"Cooldown remaining: {remaining} minutes")
    
    # Get timeout stats
    stats = db.get_timeout_stats("mod123")
    print(f"Timeout stats: {stats}")