#!/usr/bin/env python3
"""
Enhanced YouTube Live Chat Monitor with Full Terminal Logging
WSP-Compliant implementation for troubleshooting
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('live_chat_debug.log', encoding='utf-8')
    ]
)

# WSP-compliant imports
from modules.infrastructure.oauth_management.src.oauth_manager import get_authenticated_service_with_fallback
from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine

class LiveChatMonitor:
    """Enhanced Live Chat Monitor with Full Debug Output"""
    
    def __init__(self):
        self.service = None
        self.channel_id = None
        self.live_chat_id = None
        self.next_page_token = None
        self.processed_messages = set()
        self.banter_engine = BanterEngine()
        self.logger = logging.getLogger('LiveChatMonitor')
        self.start_time = None  # Track when monitoring started
        self.last_response_time = 0  # Track last response time for cooldown
        self.response_cooldown = 15  # Minimum seconds between responses
        self.last_response_to = {}  # Track who we last responded to and when
        self.user_cooldown = 30  # Don't respond to same user for 30 seconds
        
    def authenticate(self) -> bool:
        """Authenticate with YouTube"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 YOUTUBE LIVE CHAT MONITOR WITH BANTER ENGINE")
        self.logger.info("=" * 60)
        
        auth_result = get_authenticated_service_with_fallback()
        if not auth_result:
            self.logger.error("❌ Authentication failed!")
            return False
            
        self.service, credentials, credential_set = auth_result
        self.logger.info(f"✅ Authenticated with {credential_set}")
        
        # Get channel info
        try:
            response = self.service.channels().list(part='snippet', mine=True).execute()
            if response.get('items'):
                channel = response['items'][0]
                self.channel_id = channel['id']
                channel_title = channel['snippet']['title']
                self.logger.info(f"📺 Channel: {channel_title}")
                self.logger.info(f"🆔 Channel ID: {self.channel_id}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to get channel info: {e}")
            return False
            
    def find_livestream(self) -> bool:
        """Find active livestream"""
        self.logger.info("🔍 Searching for active livestream...")
        
        try:
            # Check live broadcasts
            response = self.service.liveBroadcasts().list(
                part="id,snippet,status",
                mine=True
            ).execute()
            
            for item in response.get('items', []):
                if item['status']['lifeCycleStatus'] == 'live':
                    video_id = item['id']
                    title = item['snippet']['title']
                    self.live_chat_id = item['snippet'].get('liveChatId')
                    
                    if self.live_chat_id:
                        self.logger.info(f"🔴 LIVE: {title}")
                        self.logger.info(f"📹 Video ID: {video_id}")
                        self.logger.info(f"💬 Chat ID: {self.live_chat_id}")
                        return True
                        
            # Try search method
            response = self.service.search().list(
                part="id,snippet",
                channelId=self.channel_id,
                eventType="live",
                type="video",
                maxResults=1
            ).execute()
            
            if response.get('items'):
                video_id = response['items'][0]['id']['videoId']
                
                # Get chat ID
                video_response = self.service.videos().list(
                    part="liveStreamingDetails",
                    id=video_id
                ).execute()
                
                if video_response.get('items'):
                    self.live_chat_id = video_response['items'][0].get('liveStreamingDetails', {}).get('activeLiveChatId')
                    if self.live_chat_id:
                        self.logger.info(f"🔴 LIVE: Found stream")
                        self.logger.info(f"💬 Chat ID: {self.live_chat_id}")
                        return True
                        
            self.logger.info("❌ No active livestream found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error finding livestream: {e}")
            return False
            
    def get_chat_messages(self) -> list:
        """Get new chat messages"""
        try:
            request = self.service.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="id,snippet,authorDetails",
                pageToken=self.next_page_token
            )
            
            response = request.execute()
            self.next_page_token = response.get('nextPageToken')
            
            messages = []
            for item in response.get('items', []):
                msg_id = item['id']
                
                # Skip processed messages
                if msg_id in self.processed_messages:
                    continue
                    
                self.processed_messages.add(msg_id)
                
                author = item['authorDetails']['displayName']
                author_channel = item['authorDetails']['channelId']
                text = item['snippet']['textMessageDetails']['messageText']
                timestamp = item['snippet']['publishedAt']
                
                # Check if user is moderator
                is_moderator = item['authorDetails'].get('isChatModerator', False)
                is_owner = item['authorDetails'].get('isChatOwner', False)
                
                messages.append({
                    'id': msg_id,
                    'author': author,
                    'author_channel': author_channel,
                    'text': text,
                    'timestamp': timestamp,
                    'is_moderator': is_moderator,
                    'is_owner': is_owner
                })
                
            return messages
            
        except Exception as e:
            self.logger.error(f"Error getting messages: {e}")
            return []
            
    def process_with_banter(self, message: Dict[str, Any]) -> Optional[str]:
        """Process message through banter engine"""
        text = message['text']
        author = message['author']
        
        # Process through banter engine
        state, response = self.banter_engine.process_input(text)
        
        # Log the processing
        self.logger.debug(f"Banter State: {state}")
        
        if response:
            # Personalize response
            if author not in response:
                response = f"@{author} {response}"
            return response
        return None
        
    def send_message(self, text: str) -> bool:
        """Send message to live chat"""
        try:
            request = self.service.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": self.live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": text
                        }
                    }
                }
            )
            
            response = request.execute()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
            
    async def monitor_chat(self):
        """Main monitoring loop"""
        self.logger.info("=" * 60)
        self.logger.info("📡 MONITORING LIVE CHAT - Press Ctrl+C to stop")
        self.logger.info("=" * 60)
        
        # Set start time BEFORE first poll to ignore old messages
        self.start_time = datetime.now()
        
        # First poll to get page token and mark all existing messages as processed
        self.logger.info("⏳ Ignoring chat history...")
        initial_messages = self.get_chat_messages()
        for msg in initial_messages:
            self.processed_messages.add(msg['id'])  # Mark as already seen
        self.logger.info(f"✅ Marked {len(initial_messages)} historical messages as processed")
        
        # Send greeting AFTER marking old messages
        greeting = "🤖 Banter Bot activated! Send emoji sequences like ✊✋🖐️"
        if self.send_message(greeting):
            self.logger.info(f"📤 SENT: {greeting}")
        
        poll_interval = 5  # seconds
        last_poll = time.time()  # Initialize with current time
        
        while True:
            try:
                current_time = time.time()
                
                # Poll for messages
                if current_time - last_poll >= poll_interval:
                    messages = self.get_chat_messages()
                    last_poll = current_time
                    
                    for msg in messages:
                        # Display message in terminal
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        author = msg['author']
                        author_channel = msg['author_channel']
                        text = msg['text']
                        is_mod = msg['is_moderator']
                        is_owner = msg['is_owner']
                        
                        # Color codes for terminal
                        CYAN = '\033[96m'
                        BLUE = '\033[94m'
                        GREEN = '\033[92m'
                        YELLOW = '\033[93m'
                        PURPLE = '\033[95m'
                        RED = '\033[91m'
                        RESET = '\033[0m'
                        
                        # Show incoming message with moderator badge
                        if is_owner:
                            badge = "👑"  # Owner
                            color = RED
                        elif is_mod:
                            badge = "🔧"  # Moderator (blue wrench)
                            color = BLUE
                        else:
                            badge = ""
                            color = CYAN
                            
                        print(f"{color}[{timestamp}] {badge} {author}: {text}{RESET}")
                        
                        # Skip our own messages
                        if author_channel == self.channel_id:
                            self.logger.debug(f"Skipping our own message")
                            continue
                            
                        # Skip if not moderator or owner
                        if not (is_mod or is_owner):
                            self.logger.debug(f"Skipping non-moderator: {author}")
                            continue
                        
                        # Check for emoji sequences
                        emoji_sequences = [
                            "✊✊✊", "✊✊✋", "✊✊🖐️", "✊✋✋", "✊✋🖐️",
                            "✊🖐️🖐️", "✋✋✋", "✋✋🖐️", "✋🖐️🖐️", "🖐️🖐️🖐️"
                        ]
                        
                        has_sequence = any(seq in text for seq in emoji_sequences)
                        
                        if has_sequence:
                            print(f"{YELLOW}[{timestamp}] 🎯 EMOJI SEQUENCE FROM MODERATOR!{RESET}")
                        
                        # Only respond if there's an emoji sequence from a moderator
                        if has_sequence:
                            # Check user-specific cooldown
                            if author_channel in self.last_response_to:
                                user_last_response = self.last_response_to[author_channel]
                                time_since_user = current_time - user_last_response
                                if time_since_user < self.user_cooldown:
                                    wait_time = self.user_cooldown - time_since_user
                                    print(f"{YELLOW}[{timestamp}] ⏳ User cooldown for {author}: {wait_time:.1f}s{RESET}")
                                    continue
                            
                            # Check global cooldown
                            time_since_last = current_time - self.last_response_time
                            if time_since_last < self.response_cooldown:
                                wait_time = self.response_cooldown - time_since_last
                                print(f"{YELLOW}[{timestamp}] ⏳ Global cooldown: {wait_time:.1f}s remaining{RESET}")
                            else:
                                # Process with banter
                                response = self.process_with_banter(msg)
                                
                                if response and "No sequence detected" not in str(response):
                                    print(f"{PURPLE}[{timestamp}] 🤖 BANTER: {response}{RESET}")
                                    
                                    # Send response ONLY ONCE
                                    if self.send_message(response):
                                        print(f"{GREEN}[{timestamp}] ✅ RESPONSE SENT ONCE{RESET}")
                                        self.last_response_time = current_time
                                        self.last_response_to[author_channel] = current_time
                                    else:
                                        print(f"[{timestamp}] ❌ Failed to send response")
                        else:
                            # Just log that we saw the message
                            self.logger.debug(f"Non-sequence message from {author}: {text}")
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                self.logger.info("\n👋 Shutting down...")
                break
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(5)
                
    async def run(self):
        """Main entry point"""
        if not self.authenticate():
            return
            
        while True:
            if self.find_livestream():
                await self.monitor_chat()
                self.logger.info("Stream ended or disconnected")
            else:
                self.logger.info("Waiting 30 seconds for livestream...")
                await asyncio.sleep(30)

async def main():
    monitor = LiveChatMonitor()
    await monitor.run()

if __name__ == "__main__":
    print("Starting Enhanced Live Chat Monitor...")
    print("This will show ALL chat messages and banter responses")
    print("-" * 60)
    asyncio.run(main())