"""
Chat Database Manager Module
WSP-Compliant: WSP 3 (Module Organization)

Manages all database operations for chat users, timeouts, and statistics.
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple, List

logger = logging.getLogger(__name__)


class ChatDatabase:
    """Manages chat database operations"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to database file (creates if not exists)
        """
        if not db_path:
            # Default WSP-compliant location
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'memory', 'auto_moderator.db'
            )
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.setup_database()
        logger.info(f"📁 Database ready: {db_path}")
        
    def setup_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            role TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER DEFAULT 0,
            timeout_count INTEGER DEFAULT 0
        )''')
        
        # Timeouts table
        c.execute('''CREATE TABLE IF NOT EXISTS timeouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            username TEXT,
            reason TEXT,
            duration INTEGER,
            xp_earned INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # MOD stats table
        c.execute('''CREATE TABLE IF NOT EXISTS mod_stats (
            mod_id TEXT PRIMARY KEY,
            mod_name TEXT,
            smacks_10s INTEGER DEFAULT 0,
            smacks_60s INTEGER DEFAULT 0,
            smacks_600s INTEGER DEFAULT 0,
            smacks_1800s INTEGER DEFAULT 0,
            smacks_86400s INTEGER DEFAULT 0,
            smacks_hidden INTEGER DEFAULT 0,
            total_smacks INTEGER DEFAULT 0,
            total_xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            prestige_class TEXT DEFAULT 'Novice',
            last_10s_target TEXT,
            last_10s_time TIMESTAMP,
            monthly_xp INTEGER DEFAULT 0,
            monthly_smacks INTEGER DEFAULT 0,
            current_month TEXT
        )''')
        
        conn.commit()
        conn.close()
        
    def capture_user(self, user_id: str, username: str, role: str = 'USER'):
        """
        Capture or update user in database.
        
        Args:
            user_id: YouTube channel ID
            username: Display name
            role: User role (OWNER, MOD, MEMBER, USER)
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""INSERT OR REPLACE INTO users 
                     (user_id, username, role, last_seen, message_count)
                     VALUES (?, ?, ?, CURRENT_TIMESTAMP,
                             COALESCE((SELECT message_count FROM users WHERE user_id = ?), 0) + 1)""",
                  (user_id, username, role, user_id))
        
        conn.commit()
        conn.close()
        
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """
        Get user statistics.
        
        Args:
            user_id: User ID to lookup
            
        Returns:
            User stats dict or None
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        
        if user:
            stats = {
                'username': user[1],
                'role': user[2],
                'messages': user[5],
                'timeouts': user[6]
            }
        else:
            stats = None
        
        conn.close()
        return stats
    
    def log_timeout(self, user_id: str, username: str, reason: str, duration_sec: int = 10):
        """
        Log a timeout event.
        
        Args:
            user_id: User who was timed out
            username: Username
            reason: Reason for timeout
            duration_sec: Duration in seconds
        """
        xp_earned = self.calculate_xp(duration_sec)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Log the timeout
        c.execute("INSERT INTO timeouts (user_id, username, reason, duration, xp_earned) VALUES (?, ?, ?, ?, ?)",
                  (user_id, username, reason, duration_sec, xp_earned))
        
        # Update user stats
        c.execute("UPDATE users SET timeout_count = timeout_count + 1 WHERE user_id = ?",
                  (user_id,))
        
        # Update MOD stats (simplified - assumes bot is the mod)
        self._update_mod_stats(conn, "bot", username, duration_sec, xp_earned)
        
        conn.commit()
        conn.close()
    
    def _update_mod_stats(self, conn, mod_id: str, target: str, duration_sec: int, xp_earned: int):
        """Update mod statistics."""
        c = conn.cursor()
        
        # Determine timeout category
        timeout_col = "smacks_10s"
        if duration_sec == -1:
            timeout_col = "smacks_hidden"
        elif duration_sec >= 86400:
            timeout_col = "smacks_86400s"
        elif duration_sec >= 1800:
            timeout_col = "smacks_1800s"
        elif duration_sec >= 600:
            timeout_col = "smacks_600s"
        elif duration_sec >= 60:
            timeout_col = "smacks_60s"
        
        # Get current month
        current_month = datetime.now().strftime("%Y-%m")
        
        # Update or insert mod stats
        c.execute(f"""INSERT OR REPLACE INTO mod_stats 
                     (mod_id, mod_name, {timeout_col}, total_smacks, total_xp, 
                      level, prestige_class, monthly_xp, monthly_smacks, current_month,
                      last_10s_target, last_10s_time)
                     VALUES (?, ?, 
                             COALESCE((SELECT {timeout_col} FROM mod_stats WHERE mod_id = ?), 0) + 1,
                             COALESCE((SELECT total_smacks FROM mod_stats WHERE mod_id = ?), 0) + 1,
                             COALESCE((SELECT total_xp FROM mod_stats WHERE mod_id = ?), 0) + ?,
                             ?, ?,
                             COALESCE((SELECT monthly_xp FROM mod_stats WHERE mod_id = ?), 0) + ?,
                             COALESCE((SELECT monthly_smacks FROM mod_stats WHERE mod_id = ?), 0) + 1,
                             ?,
                             CASE WHEN ? = 10 THEN ? ELSE 
                                 COALESCE((SELECT last_10s_target FROM mod_stats WHERE mod_id = ?), '') END,
                             CASE WHEN ? = 10 THEN ? ELSE 
                                 (SELECT last_10s_time FROM mod_stats WHERE mod_id = ?) END)""",
                  (mod_id, "Bot", mod_id, mod_id, mod_id, xp_earned,
                   *self.get_level_from_xp(xp_earned), mod_id, xp_earned, mod_id, current_month,
                   duration_sec, target, mod_id, duration_sec, datetime.now().isoformat(), mod_id))
    
    def calculate_xp(self, duration_sec: int) -> int:
        """Calculate XP earned from timeout duration."""
        if duration_sec <= 10:
            return 5
        elif duration_sec <= 60:
            return 10
        elif duration_sec <= 600:
            return 20
        elif duration_sec <= 1800:
            return 30
        elif duration_sec <= 86400:
            return 50
        else:
            return 100
    
    def get_level_from_xp(self, total_xp: int) -> Tuple[int, str]:
        """Calculate level and prestige from total XP."""
        if total_xp < 100:
            return (1, "Novice")
        elif total_xp < 500:
            return (2, "Apprentice")
        elif total_xp < 1000:
            return (3, "Journeyman")
        elif total_xp < 2000:
            return (4, "Expert")
        elif total_xp < 5000:
            return (5, "Master")
        else:
            return (6, "Grandmaster")
    
    def get_owner_ids(self) -> set:
        """Get all owner user IDs."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE role = 'OWNER'")
        owner_ids = {row[0] for row in c.fetchall()}
        conn.close()
        return owner_ids
    
    def check_monthly_reset(self):
        """Check and perform monthly stats reset if needed."""
        current_month = datetime.now().strftime("%Y-%m")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if we need to reset monthly stats
        c.execute("SELECT DISTINCT current_month FROM mod_stats")
        stored_months = c.fetchall()
        
        if stored_months and stored_months[0][0] != current_month:
            # Reset monthly stats
            c.execute("""UPDATE mod_stats 
                        SET monthly_xp = 0, monthly_smacks = 0, current_month = ?""",
                     (current_month,))
            conn.commit()
            logger.info(f"📅 Monthly stats reset for {current_month}")
        
        conn.close()