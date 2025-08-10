#!/usr/bin/env python3
"""
YouTube Live Chat Monitor with Banter Engine
WSP-Compliant implementation using existing modules
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Optional

# WSP-compliant imports from existing modules
from modules.infrastructure.oauth_management.src.oauth_manager import get_authenticated_service_with_fallback
from modules.communication.livechat.src.livechat import LiveChatListener
from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
from modules.platform_integration.youtube_proxy.src.youtube_proxy import YouTubeProxy

# Configure terminal logging with colors
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'CHAT': '\033[94m',     # Blue
        'BANTER': '\033[95m',   # Purple
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color based on level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Special formatting for chat messages
        if hasattr(record, 'chat_msg'):
            return f"{self.COLORS['CHAT']}[{timestamp}] 💬 {record.getMessage()}{reset}"
        elif hasattr(record, 'banter_msg'):
            return f"{self.COLORS['BANTER']}[{timestamp}] 🤖 {record.getMessage()}{reset}"
        else:
            return f"{color}[{timestamp}] [{record.levelname}] {record.getMessage()}{reset}"

class YouTubeMonitor:
    """WSP-Compliant YouTube Live Chat Monitor"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.credential_set = None
        self.youtube_proxy = None
        self.listener = None
        self.channel_id = None
        self.channel_title = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Set up colored terminal logging"""
        logger = logging.getLogger('YouTubeMonitor')
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        logger.handlers = []
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)
        
        # File handler for persistence
        file_handler = logging.FileHandler('youtube_monitor.log', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        
        return logger
    
    def authenticate(self) -> bool:
        """Authenticate with YouTube using WSP OAuth management"""
        self.logger.info("Authenticating with YouTube API...")
        
        auth_result = get_authenticated_service_with_fallback()
        if not auth_result:
            self.logger.error("Authentication failed!")
            return False
        
        self.service, self.credentials, self.credential_set = auth_result
        self.logger.info(f"✅ Authenticated with {self.credential_set}")
        
        # Get channel info
        try:
            response = self.service.channels().list(
                part='snippet,statistics',
                mine=True
            ).execute()
            
            if response.get('items'):
                channel = response['items'][0]
                self.channel_id = channel['id']
                self.channel_title = channel['snippet']['title']
                stats = channel.get('statistics', {})
                
                self.logger.info(f"📺 Channel: {self.channel_title}")
                self.logger.info(f"👥 Subscribers: {stats.get('subscriberCount', 'N/A')}")
                self.logger.info(f"📹 Total Videos: {stats.get('videoCount', 'N/A')}")
                return True
            else:
                self.logger.error("No channel found for authenticated user")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to get channel info: {e}")
            return False
    
    def find_livestream(self) -> Optional[tuple]:
        """Find active livestream using existing modules"""
        self.logger.info("🔍 Searching for active livestream...")
        
        try:
            # Method 1: Check live broadcasts
            response = self.service.liveBroadcasts().list(
                part="id,snippet,status",
                mine=True
            ).execute()
            
            for item in response.get('items', []):
                if item['status']['lifeCycleStatus'] == 'live':
                    video_id = item['id']
                    title = item['snippet']['title']
                    chat_id = item['snippet'].get('liveChatId')
                    
                    if chat_id:
                        self.logger.info(f"🔴 LIVE: {title}")
                        self.logger.info(f"📹 Video ID: {video_id}")
                        return video_id, chat_id
            
            # Method 2: Search for live videos
            response = self.service.search().list(
                part="id,snippet",
                channelId=self.channel_id,
                eventType="live",
                type="video",
                maxResults=1
            ).execute()
            
            if response.get('items'):
                video_id = response['items'][0]['id']['videoId']
                title = response['items'][0]['snippet']['title']
                
                # Get chat ID from video details
                video_response = self.service.videos().list(
                    part="liveStreamingDetails",
                    id=video_id
                ).execute()
                
                if video_response.get('items'):
                    chat_id = video_response['items'][0].get('liveStreamingDetails', {}).get('activeLiveChatId')
                    if chat_id:
                        self.logger.info(f"🔴 LIVE: {title}")
                        self.logger.info(f"📹 Video ID: {video_id}")
                        return video_id, chat_id
            
            self.logger.info("No active livestream found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding livestream: {e}")
            return None
    
    async def monitor_chat(self, video_id: str, chat_id: str):
        """Monitor live chat using existing LiveChatListener"""
        self.logger.info("🎬 Starting chat monitor...")
        self.logger.info("Press Ctrl+C to stop monitoring")
        
        # Initialize LiveChatListener with banter engine
        self.listener = LiveChatListener(
            youtube_service=self.service,
            video_id=video_id,
            live_chat_id=chat_id
        )
        
        # Start listening and log messages as they come
        try:
            # The LiveChatListener will handle everything internally
            # We just need to start it
            await self.listener.start_listening()
        except KeyboardInterrupt:
            self.logger.info("\n⏹️ Stopping monitor...")
        except Exception as e:
            self.logger.error(f"Monitor error: {e}")
        finally:
            if hasattr(self.listener, 'stop_listening'):
                self.listener.stop_listening()
            self.logger.info("Monitor stopped")
    
    async def run(self):
        """Main monitoring loop"""
        self.logger.info("=" * 50)
        self.logger.info("🚀 YouTube Live Chat Monitor with Banter Engine")
        self.logger.info("=" * 50)
        
        # Authenticate
        if not self.authenticate():
            self.logger.error("Failed to authenticate. Exiting.")
            return
        
        # Main monitoring loop
        while True:
            try:
                # Find livestream
                result = self.find_livestream()
                
                if result:
                    video_id, chat_id = result
                    self.logger.info("=" * 50)
                    self.logger.info("📡 MONITORING LIVE CHAT")
                    self.logger.info("=" * 50)
                    
                    # Monitor chat
                    await self.monitor_chat(video_id, chat_id)
                    
                    self.logger.info("Stream ended or disconnected")
                else:
                    self.logger.info("⏳ No livestream active. Waiting 30 seconds...")
                    await asyncio.sleep(30)
                    
            except KeyboardInterrupt:
                self.logger.info("\n👋 Shutting down...")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                self.logger.info("Retrying in 60 seconds...")
                await asyncio.sleep(60)

async def main():
    """Main entry point"""
    monitor = YouTubeMonitor()
    await monitor.run()

if __name__ == "__main__":
    # Run the monitor
    asyncio.run(main())