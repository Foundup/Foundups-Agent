#!/usr/bin/env python3
"""
FoundUps Agent - Main Entry Point

Simplified architecture focusing on core functionality:
1. Clean authentication setup
2. Livestream discovery
3. Chat listener initialization
4. Graceful error handling
"""

import logging
import os
import sys
import asyncio
import signal
from dotenv import load_dotenv

# Configure logging first with UTF-8 support
import sys
import os

# Set console to UTF-8 if possible (Windows fix)
if os.name == 'nt':  # Windows
    try:
        # Try to set console to UTF-8
        os.system('chcp 65001 > nul')
    except:
        pass

# Create console handler with error handling for emojis
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create file handler with UTF-8 encoding
file_handler = logging.FileHandler('foundups_agent.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Set up logging with both handlers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler]
)

from modules.platform_integration.stream_resolver.stream_resolver.src.stream_resolver import StreamResolver
from modules.communication.livechat.livechat.src.livechat import LiveChatListener
from utils.oauth_manager import get_authenticated_service_with_fallback
from utils.env_loader import get_env_variable

logger = logging.getLogger(__name__)

class FoundUpsAgent:
    """Main application controller for FoundUps Agent."""
    
    def __init__(self):
        self.running = False
        self.service = None
        self.current_listener = None
        self.stream_resolver = None
        
    async def initialize(self):
        """Initialize the agent with authentication and configuration."""
        logger.info("🚀 Initializing FoundUps Agent...")
        
        # Load environment variables
        load_dotenv()
        
        # Get required configuration
        self.channel_id = get_env_variable("CHANNEL_ID")
        if not self.channel_id:
            raise ValueError("CHANNEL_ID not found in environment variables")
            
        # Setup authentication
        auth_result = get_authenticated_service_with_fallback()
        if not auth_result:
            raise RuntimeError("Failed to authenticate with YouTube API")
            
        self.service, credentials, credential_set = auth_result
        logger.info(f"✅ Authentication successful with {credential_set}")
        
        # Initialize stream resolver with session caching
        self.stream_resolver = StreamResolver(self.service)
        logger.info("📋 Stream resolver initialized with session caching")
        
        return True
        
    async def find_livestream(self):
        """Find an active livestream using session caching for faster reconnection."""
        logger.info(f"🔍 Searching for active livestream...")
        
        try:
            result = self.stream_resolver.resolve_stream(self.channel_id)
            if result:
                video_id, chat_id = result
                logger.info(f"✅ Found active livestream: {video_id[:8]}...")
                return video_id, chat_id
            else:
                logger.info("⏳ No active livestream found")
                return None, None
                
        except Exception as e:
            logger.error(f"❌ Error finding livestream: {e}")
            return None, None
            
    async def start_chat_listener(self, video_id, chat_id):
        """Start the chat listener for the given livestream."""
        logger.info(f"💬 Starting chat listener for video: {video_id[:8]}...")
        
        try:
            self.current_listener = LiveChatListener(self.service, video_id, chat_id)
            await self.current_listener.start_listening()
            
        except Exception as e:
            logger.error(f"❌ Chat listener error: {e}")
            
        finally:
            self.current_listener = None
            
    async def run(self):
        """Main application loop."""
        self.running = True
        logger.info("🎯 FoundUps Agent started - Monitoring for livestreams...")
        
        while self.running:
            try:
                # Look for active livestream
                video_id, chat_id = await self.find_livestream()
                
                if video_id and chat_id:
                    # Start chat listener
                    await self.start_chat_listener(video_id, chat_id)
                    logger.info("📡 Chat session ended, searching for new livestream...")
                else:
                    # Wait before checking again
                    logger.info("⏳ Waiting 30 seconds before next check...")
                    await asyncio.sleep(30)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Shutdown requested by user")
                break
                
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                logger.info("⏳ Waiting 60 seconds before retry...")
                await asyncio.sleep(60)
                
        logger.info("👋 FoundUps Agent shutdown complete")
        
    def stop(self):
        """Stop the agent gracefully."""
        logger.info("🛑 Stopping FoundUps Agent...")
        self.running = False
        
        if self.current_listener:
            self.current_listener.stop_listening()

async def main():
    """Application entry point."""
    agent = FoundUpsAgent()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"📡 Received signal {signum}")
        agent.stop()
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize and run
        await agent.initialize()
        await agent.run()
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    # Run the application
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
