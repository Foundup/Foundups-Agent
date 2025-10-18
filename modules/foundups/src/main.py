#!/usr/bin/env python3
"""
FoundUps LiveChat Module - WRE Compatible Entry Point

This module provides the original FoundUps Agent YouTube LiveChat functionality
as a WRE-accessible module. It maintains all multi-agent and authentication
capabilities while being integrated into the WRE ecosystem.

Entry point for WRE Module Switchboard.
"""

import logging
import os
import sys
import asyncio
import signal
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Set console to UTF-8 if possible (Windows fix)
if os.name == 'nt':  # Windows
    try:
        os.system('chcp 65001 > nul')
    except:
        pass

# Configure logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler(project_root / 'foundups_livechat.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

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
    logger.info("[BOT] Multi-agent management system available")
except ImportError as e:
    MULTI_AGENT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"[U+26A0]️ Multi-agent system not available: {e}")
    logger.info("[REFRESH] Will use simple authentication fallback")

# Always import fallback authentication
from utils.oauth_manager import get_authenticated_service_with_fallback
from utils.env_loader import get_env_variable

logger = logging.getLogger(__name__)

class FoundUpsLiveChatModule:
    """FoundUps LiveChat functionality as a WRE module."""
    
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
        """Initialize the module with multi-agent management or fallback to simple auth."""
        logger.info("[ROCKET] Initializing FoundUps LiveChat Module...")
        
        # Load environment variables
        load_dotenv()
        
        # Get required configuration
        self.channel_id = get_env_variable("CHANNEL_ID")
        if not self.channel_id:
            raise ValueError("CHANNEL_ID not found in environment variables")
            
        logger.info(f"[U+1F464] User Channel ID: {self.channel_id[:8]}...{self.channel_id[-4:]}")
        
        # Try multi-agent setup first
        if MULTI_AGENT_AVAILABLE:
            try:
                return await self._try_multi_agent_setup(force_agent)
            except Exception as e:
                logger.error(f"[FAIL] Multi-agent setup failed: {e}")
                logger.info("[REFRESH] Falling back to simple authentication...")
        
        # Fallback to simple authentication
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
            logger.info("[TARGET] Defaulting to UnDaoDu agent to avoid same-account conflicts")
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
        self.youtube_proxy = YouTubeProxy(credentials)
        self.using_multi_agent = True
        return True
    
    async def _fallback_simple_setup(self):
        """Fallback to simple authentication setup."""
        logger.info("[REFRESH] Using simple authentication fallback...")
        
        # Setup authentication using fallback method
        auth_result = get_authenticated_service_with_fallback()
        if not auth_result:
            raise RuntimeError("Failed to authenticate with YouTube API")
            
        self.service, credentials, credential_set = auth_result
        logger.info(f"[OK] Simple authentication successful with {credential_set}")
        
        # Initialize the YouTube proxy with session caching
        self.youtube_proxy = YouTubeProxy(credentials)
        logger.info("[CLIPBOARD] YouTube proxy initialized.")
        self.using_multi_agent = False
        return True
        
    async def find_livestream(self):
        """Find an active livestream using session caching for faster reconnection."""
        logger.info(f"[SEARCH] Searching for active livestream...")
        
        try:
            result = self.youtube_proxy.find_active_livestream(self.channel_id)
            if result:
                video_id, chat_id = result
                logger.info(f"[OK] Found active livestream: {video_id[:8]}...")
                return video_id, chat_id
            else:
                logger.info("⏳ No active livestream found")
                return None, None
                
        except Exception as e:
            logger.error(f"[FAIL] Error finding livestream: {e}")
            return None, None
            
    async def start_chat_listener(self, video_id, chat_id):
        """Start the chat listener for the given livestream."""
        logger.info(f"[U+1F4AC] Starting chat listener for video: {video_id[:8]}...")
        
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
                    logger.error("[FAIL] Failed to start agent session")
                    logger.info("⏳ Waiting 10 seconds before retrying...")
                    await asyncio.sleep(10)
                    return
            
            # Create chat listener with bot identity management and agent configuration
            if self.using_multi_agent and self.current_agent:
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
            logger.error(f"[FAIL] Chat listener error: {e}")
            
        finally:
            # End agent session if using multi-agent
            if self.using_multi_agent and self.agent_manager:
                self.agent_manager.end_current_session()
            self.current_listener = None
            
    async def run(self):
        """Main module execution loop."""
        self.running = True
        mode = "Multi-Agent" if self.using_multi_agent else "Simple"
        logger.info(f"[TARGET] FoundUps LiveChat Module started in {mode} mode")
        
        print("\n" + "="*60)
        print("  FoundUps LiveChat Module - WRE Integration  ".center(60))
        print("="*60 + "\n")
        
        while self.running:
            try:
                # Look for active livestream
                video_id, chat_id = await self.find_livestream()
                
                if video_id and chat_id:
                    # Start chat listener
                    await self.start_chat_listener(video_id, chat_id)
                    logger.info("[U+1F4E1] Chat session ended, searching for new livestream...")
                else:
                    # Wait before checking again
                    logger.info("⏳ Waiting 30 seconds before next check...")
                    await asyncio.sleep(30)
                    
            except KeyboardInterrupt:
                logger.info("[STOP] Module shutdown requested by user")
                break
                
            except Exception as e:
                logger.error(f"[FAIL] Unexpected error: {e}")
                logger.info("⏳ Waiting 60 seconds before retry...")
                await asyncio.sleep(60)
                
        logger.info("[U+1F44B] FoundUps LiveChat Module shutdown complete")
        
    def stop(self):
        """Stop the module gracefully."""
        logger.info("[STOP] Stopping FoundUps LiveChat Module...")
        self.running = False
        
        if self.current_listener:
            self.current_listener.stop_listening()

async def main():
    """Main entry point for the FoundUps LiveChat module."""
    
    print("[ROCKET] Starting FoundUps LiveChat Module via WRE...")
    
    module = FoundUpsLiveChatModule()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"[U+1F4E1] Received signal {signum}")
        module.stop()
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize and run
        await module.initialize()
        await module.run()
        
    except Exception as e:
        logger.error(f"[U+1F4A5] Fatal error in FoundUps LiveChat Module: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 