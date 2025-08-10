#!/usr/bin/env python3
"""
FoundUps Agent - Main Entry Point

Multi-agent architecture with fallback to simplified core functionality:
1. Attempt multi-agent setup with conflict detection
2. Fallback to simple authentication if multi-agent fails
3. Livestream discovery
4. Chat listener initialization  
5. Graceful error handling

Recent Updates (2025-08-10):
- Fixed Unicode encoding issues for Windows (cp932 codec)
- Replaced 4 emoji characters with ASCII-safe alternatives
- Enhanced UTF-8 console configuration for Windows
- Improved error resilience for international character sets
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

from modules.platform_integration.youtube_proxy.src.youtube_proxy import YouTubeProxy
from modules.communication.livechat.src.livechat import LiveChatListener

# Import multi-agent system with fallback
try:
    from modules.infrastructure.agent_management.src.multi_agent_manager import MultiAgentManager
    MULTI_AGENT_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("[INFO] Multi-agent management system available")
except ImportError as e:
    MULTI_AGENT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"[WARN] Multi-agent system not available: {e}")
    logger.info("[INFO] Will use simple authentication fallback")

# Always import fallback authentication
from utils.oauth_manager import get_authenticated_service_with_fallback
from utils.env_loader import get_env_variable

logger = logging.getLogger(__name__)

try:
    from modules.wre_core.src.engine import WRE
except ImportError as e:
    logger.error(f"[ERROR] WRE import failed: {e}")
    WRE = None

# Placeholder for YouTube LiveChat agent import
# Note: LiveChatAgent doesn't exist - LiveChatListener is the correct class
# This is kept for backward compatibility with older code
LiveChatAgent = None

class FoundUpsAgent:
    """Main application controller for FoundUps Agent with multi-agent support and fallback."""
    
    def __init__(self):
        self.running = False
        self.service = None
        self.current_listener = None
        self.youtube_proxy = None
        self.agent_manager = None
        self.current_agent = None
        self.channel_id = None
        self.using_multi_agent = False
        
    async def initialize(self, force_agent: str = None):
        """Initialize the agent with multi-agent management or fallback to simple auth."""
        logger.info("[INFO] Initializing FoundUps Agent with Multi-Agent Management...")
        
        # Load environment variables
        load_dotenv()
        
        # Get required configuration
        self.channel_id = get_env_variable("CHANNEL_ID")
        if not self.channel_id:
            raise ValueError("CHANNEL_ID not found in environment variables")
            
        logger.info(f"[USER] Channel ID: {self.channel_id[:8]}...{self.channel_id[-4:]}")
        
        # Try multi-agent setup first
        if MULTI_AGENT_AVAILABLE:
            try:
                return await self._try_multi_agent_setup(force_agent)
            except Exception as e:
                logger.error(f"[ERROR] Multi-agent setup failed: {e}")
                logger.info("[INFO] Falling back to simple authentication...")
        
        # Fallback to simple authentication (clean4 approach)
        return await self._fallback_simple_setup()
    
    async def _try_multi_agent_setup(self, force_agent: str = None):
        """Try to set up multi-agent management system."""
        self.agent_manager = MultiAgentManager()
        
        # Initialize multi-agent system
        success = self.agent_manager.initialize(self.channel_id)
        if not success:
            raise RuntimeError("Multi-agent initialization failed")
        
        # Select an agent
        if force_agent:
            logger.info(f"[TARGET] Attempting to force selection of agent: {force_agent}")
            self.current_agent = self.agent_manager.select_agent(force_agent)
        else:
            # Default to UnDaoDu to avoid same-account conflicts
            logger.info(f"[TARGET] Defaulting to UnDaoDu agent to avoid same-account conflicts")
            self.current_agent = self.agent_manager.select_agent("UnDaoDu")
        
        if not self.current_agent:
            raise RuntimeError("No suitable agent found")
        
        # Get the service from the selected agent's credentials
        credential_index = int(self.current_agent.credential_set.split('_')[1]) - 1
        
        # Import at the correct time
        from modules.infrastructure.oauth_management.src.oauth_manager import get_authenticated_service
        auth_result = get_authenticated_service(credential_index)
        if not auth_result:
            raise RuntimeError(f"Failed to authenticate with agent {self.current_agent.channel_name}")
        
        self.service, credentials = auth_result
        logger.info(f"[OK] Multi-agent authentication successful with {self.current_agent.channel_name}")
        
        # Initialize the YouTube proxy
        self.youtube_proxy = YouTubeProxy(logger=logger)
        self.youtube_proxy.credentials = credentials
        self.using_multi_agent = True
        return True
    
    async def _fallback_simple_setup(self):
        """Fallback to simple authentication setup (clean4 approach)."""
        logger.info("[INFO] Using simple authentication fallback...")
        
        # Setup authentication using fallback method
        auth_result = get_authenticated_service_with_fallback()
        if not auth_result:
            raise RuntimeError("Failed to authenticate with YouTube API")
            
        self.service, credentials, credential_set = auth_result
        logger.info(f"[OK] Simple authentication successful with {credential_set}")
        
        # Initialize the YouTube proxy with session caching
        self.youtube_proxy = YouTubeProxy(logger=logger)
        self.youtube_proxy.credentials = credentials
        logger.info("[INFO] YouTube proxy initialized.")
        self.using_multi_agent = False
        return True
        
    async def find_livestream(self):
        """Find an active livestream using session caching for faster reconnection."""
        logger.info(f"[INFO] Searching for active livestream...")
        
        try:
            result = self.youtube_proxy.find_active_livestream(self.channel_id)
            if result:
                video_id, chat_id = result
                logger.info(f"[OK] Found active livestream: {video_id[:8]}...")
                return video_id, chat_id
            else:
                logger.info("[INFO] No active livestream found")
                return None, None
                
        except Exception as e:
            logger.error(f"[ERROR] Error finding livestream: {e}")
            return None, None
            
    async def start_chat_listener(self, video_id, chat_id):
        """Start the chat listener for the given livestream."""
        logger.info(f"[INFO] Starting chat listener for video: {video_id[:8]}...")
        
        try:
            # Start agent session if using multi-agent
            if self.using_multi_agent and self.agent_manager and self.current_agent:
                stream_title = self.youtube_proxy.get_stream_title(video_id)
                success = self.agent_manager.start_agent_session(
                    self.current_agent, 
                    video_id, 
                    stream_title
                )
                if not success:
                    logger.error("[ERROR] Failed to start agent session")
                    logger.info("[INFO] Waiting 10 seconds before retrying...")
                    await asyncio.sleep(10)  # Add delay to prevent rapid retry loop
                    return
            
            # Create chat listener with bot identity management and agent configuration
            if self.using_multi_agent and self.current_agent:
                # Create agent_config dict with just the admin_users data the LiveChatListener expects
                agent_config = {
                    "admin_users": self.current_agent.admin_users
                } if self.current_agent.admin_users else None
                
                self.current_listener = LiveChatListener(
                    self.service, 
                    video_id, 
                    chat_id,
                    agent_config=agent_config
                )
            else:
                # Simple setup for fallback mode
                self.current_listener = LiveChatListener(
                    self.service, 
                    video_id, 
                    chat_id
                )
            
            # Set greeting message during initialization
            if self.using_multi_agent and self.current_agent:
                self.current_listener.greeting_message = f"[BOT] {self.current_agent.channel_name} is now monitoring chat!"
            
            await self.current_listener.start_listening()
            
        except Exception as e:
            logger.error(f"[ERROR] Chat listener error: {e}")
            
        finally:
            # End agent session if using multi-agent
            if self.using_multi_agent and self.agent_manager:
                self.agent_manager.end_current_session()
            self.current_listener = None
            
    async def run(self):
        """Main application loop."""
        self.running = True
        mode = "Multi-Agent" if self.using_multi_agent else "Simple"
        logger.info(f"[START] FoundUps Agent started in {mode} mode - Monitoring for livestreams...")
        
        while self.running:
            try:
                # Look for active livestream
                video_id, chat_id = await self.find_livestream()
                
                if video_id and chat_id:
                    # Start chat listener
                    await self.start_chat_listener(video_id, chat_id)
                    logger.info("[CHAT] Chat session ended, searching for new livestream...")
                else:
                    # Wait before checking again
                    logger.info("[INFO] Waiting 30 seconds before next check...")
                    await asyncio.sleep(30)
                    
            except KeyboardInterrupt:
                logger.info("[INFO] Shutdown requested by user")
                break
                
            except Exception as e:
                logger.error(f"[ERROR] Unexpected error: {e}")
                logger.info("[INFO] Waiting 60 seconds before retry...")
                await asyncio.sleep(60)
                
        logger.info("[INFO] FoundUps Agent shutdown complete")
        
    def stop(self):
        """Stop the agent gracefully."""
        logger.info("[INFO] Stopping FoundUps Agent...")
        self.running = False
        
        if self.current_listener:
            self.current_listener.stop_listening()

def launch_youtube_agent():
    if LiveChatAgent:
        logger.info("[INFO] Starting YouTube LiveChat Agent...")
        agent = LiveChatAgent()
        agent.run()
    else:
        logger.error("[ERROR] YouTube LiveChat Agent not available.")

def main():
    if WRE:
        logger.info("[INFO] FoundUps Agent - Initializing WRE (Windsurf Recursive Engine)...")
        wre = WRE()
        try:
            wre.start()
        except Exception as e:
            logger.error(f"[ERROR] WRE runtime error: {e}")
            logger.info("[INFO] Falling back to YouTube LiveChat module...")
            launch_youtube_agent()
    else:
        logger.info("[INFO] WRE unavailable, launching YouTube LiveChat module...")
        launch_youtube_agent()

if __name__ == "__main__":
    main()
