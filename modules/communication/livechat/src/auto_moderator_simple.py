#!/usr/bin/env python3
"""
Simple YouTube Auto-Moderator with Memory - WSP Compliant
Tracks users in database, timeouts MAGA supporters (not mods)
"""

import asyncio
import logging
import sys
import os
import sqlite3
from datetime import datetime
from typing import Dict, Set

# Windows UTF-8 fix
if os.name == 'nt':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from modules.infrastructure.oauth_management.src.oauth_manager import get_authenticated_service_with_fallback

class SimpleBotWithMemory:
    """Simple bot that remembers users and moderates MAGA content"""
    
    def __init__(self):
        self.service = None
        self.channel_id = None
        self.live_chat_id = None
        self.next_page_token = None
        self.processed_ids = set()
        
        # Setup database in WSP-compliant memory location
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'memory', 'auto_moderator.db'
        )
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.setup_database()
        
        # Pro-Trump phrases to detect
        self.maga_phrases = [
            "love trump", "love maga", "vote trump", "trump 2024", "maga 2024",
            "trump is great", "trump won", "stop the steal", "let's go brandon",
            "make america great again", "trump train", "save america"
        ]
    
    def setup_database(self):
        """Create simple database tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            role TEXT,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            message_count INTEGER DEFAULT 0,
            timeout_count INTEGER DEFAULT 0
        )''')
        
        # Timeout log
        c.execute('''CREATE TABLE IF NOT EXISTS timeouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            username TEXT,
            reason TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()
        logger.info(f"📁 Database ready: {self.db_path}")
    
    def capture_user(self, user_id: str, username: str, role: str):
        """Add or update user in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if user exists
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        
        if user:
            # Update existing user
            c.execute("""UPDATE users SET 
                username = ?, role = ?, last_seen = ?, message_count = message_count + 1
                WHERE user_id = ?""", 
                (username, role, datetime.now(), user_id))
        else:
            # New user
            c.execute("""INSERT INTO users 
                (user_id, username, role, first_seen, last_seen, message_count)
                VALUES (?, ?, ?, ?, ?, 1)""",
                (user_id, username, role, datetime.now(), datetime.now()))
            logger.info(f"📝 NEW USER: {username} ({role})")
        
        conn.commit()
        conn.close()
    
    def log_timeout(self, user_id: str, username: str, reason: str):
        """Log a timeout to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("INSERT INTO timeouts (user_id, username, reason) VALUES (?, ?, ?)",
                  (user_id, username, reason))
        
        c.execute("UPDATE users SET timeout_count = timeout_count + 1 WHERE user_id = ?",
                  (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
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
    
    def authenticate(self):
        """Connect to YouTube"""
        logger.info("🔌 Connecting to YouTube...")
        auth = get_authenticated_service_with_fallback()
        if not auth:
            logger.error("❌ Authentication failed")
            return False
        
        self.service, _, _ = auth
        
        # Get channel
        response = self.service.channels().list(part='snippet', mine=True).execute()
        if response.get('items'):
            self.channel_id = response['items'][0]['id']
            logger.info(f"✅ Connected as: {response['items'][0]['snippet']['title']}")
            return True
        return False
    
    def find_stream(self):
        """Find active livestream"""
        logger.info("🔍 Looking for livestream...")
        
        # Check broadcasts
        response = self.service.liveBroadcasts().list(
            part="id,snippet,status", mine=True
        ).execute()
        
        for item in response.get('items', []):
            if item['status']['lifeCycleStatus'] == 'live':
                self.live_chat_id = item['snippet'].get('liveChatId')
                if self.live_chat_id:
                    logger.info(f"✅ Found stream: {item['snippet']['title']}")
                    return True
        
        logger.info("❌ No active stream found")
        return False
    
    def check_maga(self, text):
        """Check if message contains pro-MAGA content"""
        text_lower = text.lower()
        for phrase in self.maga_phrases:
            if phrase in text_lower:
                return phrase  # Return which phrase matched
        return None
    
    def process_command(self, text: str, user_id: str) -> str:
        """Process simple commands"""
        if text.lower() == '/stats':
            stats = self.get_user_stats(user_id)
            if stats:
                return f"Messages: {stats['messages']}, Timeouts: {stats['timeouts']}"
        return None
    
    async def monitor(self):
        """Main monitoring loop"""
        logger.info("="*60)
        logger.info("👁️ MONITORING CHAT - MOD IMMUNITY ACTIVE")
        logger.info("="*60)
        
        # First poll - mark all as seen
        response = self.service.liveChatMessages().list(
            liveChatId=self.live_chat_id,
            part="id,snippet,authorDetails"
        ).execute()
        
        for item in response.get('items', []):
            self.processed_ids.add(item['id'])
        
        logger.info(f"✅ Ignoring {len(self.processed_ids)} old messages")
        self.next_page_token = response.get('nextPageToken')
        
        # Send greeting
        greeting = "🤖 Auto-moderator active. Mods are immune. MAGA supporters get 10s timeout."
        try:
            self.service.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": self.live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {"messageText": greeting}
                    }
                }
            ).execute()
            logger.info(f"📤 Sent: {greeting}")
        except:
            pass
        
        # Monitor loop
        while True:
            try:
                # Get new messages
                response = self.service.liveChatMessages().list(
                    liveChatId=self.live_chat_id,
                    part="id,snippet,authorDetails",
                    pageToken=self.next_page_token
                ).execute()
                
                self.next_page_token = response.get('nextPageToken')
                
                for item in response.get('items', []):
                    msg_id = item['id']
                    
                    # Skip if already seen
                    if msg_id in self.processed_ids:
                        continue
                    
                    self.processed_ids.add(msg_id)
                    
                    # Get message details
                    details = item['authorDetails']
                    author = details['displayName']
                    user_id = details['channelId']
                    text = item['snippet'].get('textMessageDetails', {}).get('messageText', '')
                    
                    # Skip our own messages
                    if user_id == self.channel_id:
                        continue
                    
                    # Determine role
                    if details.get('isChatOwner'):
                        role = 'OWNER'
                    elif details.get('isChatModerator'):
                        role = 'MOD'
                    elif details.get('isChatSponsor'):
                        role = 'MEMBER'
                    else:
                        role = 'USER'
                    
                    # Capture user to database
                    self.capture_user(user_id, author, role)
                    
                    # MODS/OWNERS ARE COMPLETELY EXEMPT
                    if role in ['MOD', 'OWNER']:
                        logger.info(f"🛡️ {author} ({role}): {text[:50]}... [EXEMPT - IGNORED]")
                        continue
                    
                    # Check for commands (members only)
                    if text.startswith('/') and role == 'MEMBER':
                        response = self.process_command(text, user_id)
                        if response:
                            self.service.liveChatMessages().insert(
                                part="snippet",
                                body={
                                    "snippet": {
                                        "liveChatId": self.live_chat_id,
                                        "type": "textMessageEvent",
                                        "textMessageDetails": {"messageText": f"@{author} {response}"}
                                    }
                                }
                            ).execute()
                            logger.info(f"📊 Command response sent to {author}")
                        continue
                    
                    # Check for MAGA content (regular users and members)
                    maga_match = self.check_maga(text)
                    if maga_match:
                        logger.info(f"🚨 MAGA DETECTED from {author} ({role}): '{maga_match}'")
                        
                        # Log timeout
                        self.log_timeout(user_id, author, f"Said: {maga_match}")
                        
                        # Send timeout (only works if bot is mod)
                        timeout_msg = f"/timeout @{author} 10"
                        try:
                            self.service.liveChatMessages().insert(
                                part="snippet",
                                body={
                                    "snippet": {
                                        "liveChatId": self.live_chat_id,
                                        "type": "textMessageEvent",
                                        "textMessageDetails": {"messageText": timeout_msg}
                                    }
                                }
                            ).execute()
                            logger.info(f"⏱️ TIMEOUT: {author} for 10 seconds")
                        except:
                            pass
                        
                        # Send response
                        response_msg = f"@{author} Pro-MAGA content detected: '{maga_match}' [10s timeout]"
                        try:
                            self.service.liveChatMessages().insert(
                                part="snippet",
                                body={
                                    "snippet": {
                                        "liveChatId": self.live_chat_id,
                                        "type": "textMessageEvent",
                                        "textMessageDetails": {"messageText": response_msg}
                                    }
                                }
                            ).execute()
                        except:
                            pass
                    else:
                        logger.debug(f"💬 {author} ({role}): {text[:50]}...")
                
                # Wait before next poll
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("\n👋 Shutting down...")
                
                # Show session stats
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM users")
                user_count = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM timeouts")
                timeout_count = c.fetchone()[0]
                conn.close()
                
                logger.info("="*60)
                logger.info(f"📊 SESSION STATS:")
                logger.info(f"   Users captured: {user_count}")
                logger.info(f"   Timeouts issued: {timeout_count}")
                logger.info("="*60)
                break
                
            except Exception as e:
                logger.error(f"Error: {e}")
                await asyncio.sleep(5)
    
    async def run(self):
        """Main entry point"""
        if not self.authenticate():
            return
        
        while True:
            if self.find_stream():
                await self.monitor()
                logger.info("Stream ended")
            else:
                logger.info("Waiting 30 seconds...")
                await asyncio.sleep(30)

async def main():
    """Entry point for main.py"""
    bot = SimpleBotWithMemory()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())