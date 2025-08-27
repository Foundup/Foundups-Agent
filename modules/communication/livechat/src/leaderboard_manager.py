"""
Leaderboard Manager - Whack-a-MAGA Leaderboard System
Tracks lifetime, monthly, weekly stats for all moderators
"""

import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LeaderboardManager:
    """Manages leaderboards for whack-a-MAGA gamification"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure leaderboard tables exist"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Ensure weekly columns exist
        try:
            c.execute('ALTER TABLE mod_stats ADD COLUMN weekly_xp INTEGER DEFAULT 0')
            c.execute('ALTER TABLE mod_stats ADD COLUMN weekly_smacks INTEGER DEFAULT 0')
            c.execute('ALTER TABLE mod_stats ADD COLUMN current_week TEXT')
            c.execute('ALTER TABLE mod_stats ADD COLUMN kill_streak INTEGER DEFAULT 0')
            c.execute('ALTER TABLE mod_stats ADD COLUMN best_streak INTEGER DEFAULT 0')
            conn.commit()
        except:
            pass  # Columns already exist
        
        conn.close()
    
    def update_mod_stats(self, mod_id: str, mod_name: str, xp_gained: int, 
                        kill_streak: int = 0) -> None:
        """Update mod statistics in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        current_week = datetime.now().strftime("%Y-W%U")
        current_month = datetime.now().strftime("%Y-%m")
        
        # Check if we need to reset weekly/monthly stats
        c.execute("SELECT current_week, current_month FROM mod_stats WHERE mod_id = ?", (mod_id,))
        result = c.fetchone()
        
        if result:
            stored_week, stored_month = result
            
            # Reset weekly stats if new week
            if stored_week != current_week:
                c.execute("""UPDATE mod_stats 
                           SET weekly_xp = 0, weekly_smacks = 0, current_week = ?
                           WHERE mod_id = ?""", (current_week, mod_id))
            
            # Reset monthly stats if new month  
            if stored_month != current_month:
                c.execute("""UPDATE mod_stats
                           SET monthly_xp = 0, monthly_smacks = 0, current_month = ?
                           WHERE mod_id = ?""", (current_month, mod_id))
        
        # Update or insert mod stats
        c.execute("""INSERT OR REPLACE INTO mod_stats 
                    (mod_id, mod_name, total_xp, total_smacks,
                     weekly_xp, weekly_smacks, current_week,
                     monthly_xp, monthly_smacks, current_month,
                     kill_streak, best_streak)
                    VALUES (?, ?, 
                            COALESCE((SELECT total_xp FROM mod_stats WHERE mod_id = ?), 0) + ?,
                            COALESCE((SELECT total_smacks FROM mod_stats WHERE mod_id = ?), 0) + 1,
                            COALESCE((SELECT weekly_xp FROM mod_stats WHERE mod_id = ?), 0) + ?,
                            COALESCE((SELECT weekly_smacks FROM mod_stats WHERE mod_id = ?), 0) + 1,
                            ?,
                            COALESCE((SELECT monthly_xp FROM mod_stats WHERE mod_id = ?), 0) + ?,
                            COALESCE((SELECT monthly_smacks FROM mod_stats WHERE mod_id = ?), 0) + 1,
                            ?,
                            ?,
                            MAX(?, COALESCE((SELECT best_streak FROM mod_stats WHERE mod_id = ?), 0)))""",
                 (mod_id, mod_name, mod_id, xp_gained, mod_id, mod_id, xp_gained, mod_id,
                  current_week, mod_id, xp_gained, mod_id, current_month,
                  kill_streak, kill_streak, mod_id))
        
        conn.commit()
        conn.close()
    
    def get_leaderboard(self, period: str = "lifetime", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get leaderboard for specified period
        
        Args:
            period: "lifetime", "monthly", "weekly"
            limit: Number of top players to return
            
        Returns:
            List of leaderboard entries
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if period == "weekly":
            order_by = "weekly_xp"
            extra_fields = ", weekly_xp, weekly_smacks"
        elif period == "monthly":
            order_by = "monthly_xp"
            extra_fields = ", monthly_xp, monthly_smacks"
        else:  # lifetime
            order_by = "total_xp"
            extra_fields = ", total_xp, total_smacks"
        
        query = f"""SELECT mod_id, mod_name, level, prestige_class, 
                          kill_streak, best_streak {extra_fields}
                   FROM mod_stats
                   ORDER BY {order_by} DESC
                   LIMIT ?"""
        
        c.execute(query, (limit,))
        results = c.fetchall()
        
        leaderboard = []
        for i, row in enumerate(results, 1):
            if period == "weekly":
                leaderboard.append({
                    "rank": i,
                    "mod_id": row[0],
                    "mod_name": row[1],
                    "level": row[2],
                    "prestige_class": row[3],
                    "current_streak": row[4],
                    "best_streak": row[5],
                    "xp": row[6],
                    "whacks": row[7]
                })
            elif period == "monthly":
                leaderboard.append({
                    "rank": i,
                    "mod_id": row[0],
                    "mod_name": row[1],
                    "level": row[2],
                    "prestige_class": row[3],
                    "current_streak": row[4],
                    "best_streak": row[5],
                    "xp": row[6],
                    "whacks": row[7]
                })
            else:  # lifetime
                leaderboard.append({
                    "rank": i,
                    "mod_id": row[0],
                    "mod_name": row[1],
                    "level": row[2],
                    "prestige_class": row[3],
                    "current_streak": row[4],
                    "best_streak": row[5],
                    "xp": row[6],
                    "whacks": row[7]
                })
        
        conn.close()
        return leaderboard
    
    def format_leaderboard(self, period: str = "lifetime") -> str:
        """Format leaderboard for chat display"""
        leaderboard = self.get_leaderboard(period, limit=5)
        
        if not leaderboard:
            return f"📊 No {period} stats yet!"
        
        title_emoji = {
            "lifetime": "🏆",
            "monthly": "📅",
            "weekly": "📆"
        }
        
        lines = [f"{title_emoji[period]} WHACK-A-MAGA {period.upper()} LEADERBOARD:"]
        
        for entry in leaderboard:
            rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][entry["rank"] - 1]
            lines.append(
                f"{rank_emoji} {entry['mod_name']} - "
                f"Level {entry['level']} {entry['prestige_class']} | "
                f"{entry['xp']} XP | {entry['whacks']} whacks"
            )
            if entry["best_streak"] > 10:
                lines[-1] += f" | 🔥 Best: {entry['best_streak']} streak!"
        
        return "\n".join(lines)
    
    def get_mod_stats(self, mod_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive stats for a specific mod"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""SELECT mod_name, level, prestige_class,
                           total_xp, total_smacks,
                           monthly_xp, monthly_smacks,
                           weekly_xp, weekly_smacks,
                           kill_streak, best_streak,
                           smacks_10s, smacks_60s, smacks_600s, smacks_1800s, smacks_86400s
                    FROM mod_stats
                    WHERE mod_id = ?""", (mod_id,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return {
            "mod_name": result[0],
            "level": result[1],
            "prestige_class": result[2],
            "lifetime": {"xp": result[3], "whacks": result[4]},
            "monthly": {"xp": result[5], "whacks": result[6]},
            "weekly": {"xp": result[7], "whacks": result[8]},
            "current_streak": result[9],
            "best_streak": result[10],
            "timeout_breakdown": {
                "10s": result[11],
                "60s": result[12],
                "10m": result[13],
                "30m": result[14],
                "24h": result[15]
            }
        }
    
    def format_mod_stats(self, mod_id: str) -> str:
        """Format individual mod stats for display"""
        stats = self.get_mod_stats(mod_id)
        
        if not stats:
            return "No stats found!"
        
        lines = [
            f"📊 {stats['mod_name']} - Level {stats['level']} {stats['prestige_class']}",
            f"🏆 Lifetime: {stats['lifetime']['xp']} XP | {stats['lifetime']['whacks']} whacks",
            f"📅 Monthly: {stats['monthly']['xp']} XP | {stats['monthly']['whacks']} whacks",
            f"📆 Weekly: {stats['weekly']['xp']} XP | {stats['weekly']['whacks']} whacks"
        ]
        
        if stats['best_streak'] > 5:
            lines.append(f"🔥 Best Streak: {stats['best_streak']} | Current: {stats['current_streak']}")
        
        # Add timeout breakdown if significant
        breakdown = stats['timeout_breakdown']
        if sum(breakdown.values()) > 10:
            lines.append(
                f"⏱️ Timeouts: {breakdown['10s']}x10s | {breakdown['60s']}x60s | "
                f"{breakdown['10m']}x10m | {breakdown['30m']}x30m | {breakdown['24h']}x24h"
            )
        
        return "\n".join(lines)