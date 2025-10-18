#!/usr/bin/env python3
"""
WSP 1/3/84 Compliant: Enhanced Commands Extension
Adds /help and /smacks commands to existing RPG system
"""

from typing import Dict, List, Optional
from modules.communication.chat_rules.src.database import ChatRulesDB
from modules.communication.chat_rules.src.rpg_leveling_system import RPGCommands

class EnhancedCommands(RPGCommands):
    """Extends RPGCommands with additional slash commands"""
    
    def __init__(self, db: ChatRulesDB = None):
        """Initialize enhanced command system"""
        super().__init__(db)
        
        # Add new commands to registry
        self.commands.update({
            '/help': self.cmd_help,
            '/smacks': self.cmd_smacks,
        })
    
    def cmd_help(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Show all available commands"""
        return ("[GAME] Commands: /help /stats /level /smacks /leaderboard /score /rank | "
                "[U+270A][U+270B][U+1F590]️ = 0102 consciousness")
    
    def cmd_smacks(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Show timeout breakdown by duration"""
        # Get timeout stats from database
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN duration_seconds = 10 THEN 1 ELSE 0 END) as s10,
                    SUM(CASE WHEN duration_seconds = 60 THEN 1 ELSE 0 END) as s60,
                    SUM(CASE WHEN duration_seconds = 600 THEN 1 ELSE 0 END) as s600,
                    SUM(CASE WHEN duration_seconds = 1800 THEN 1 ELSE 0 END) as s1800,
                    SUM(CASE WHEN duration_seconds = 86400 THEN 1 ELSE 0 END) as s86400,
                    SUM(CASE WHEN duration_seconds < 0 THEN 1 ELSE 0 END) as shidden,
                    COUNT(*) as total
                FROM timeout_history
                WHERE mod_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result and result['total'] > 0:
                s10, s60, s600, s1800, s86400, shidden, total = result
                
                breakdown = []
                if s10: breakdown.append(f"10s:{s10}")
                if s60: breakdown.append(f"1m:{s60}")
                if s600: breakdown.append(f"10m:{s600}")
                if s1800: breakdown.append(f"30m:{s1800}")
                if s86400: breakdown.append(f"24h:{s86400}")
                if shidden: breakdown.append(f"Hidden:{shidden}")
                
                if breakdown:
                    return f"Total: {total} smacks | {' | '.join(breakdown)}"
                else:
                    return "No smacks recorded yet. Start fragging MAGAts!"
            else:
                return "No combat record found. Start timing out MAGAts!"
    
    def process_command(self, text: str, user_id: str, user_name: str) -> Optional[str]:
        """Process a command and return response"""
        if not text.startswith('/'):
            return None
        
        parts = text.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.commands:
            return self.commands[cmd](user_id, user_name, args)
        
        return None