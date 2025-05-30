#!/usr/bin/env python3
"""
FoundUps Agent - Main Entry Point with Multi-Agent Management

Enhanced architecture with same-account conflict prevention:
1. Multi-agent management system integration
2. Automatic conflict detection and resolution
3. Safe agent selection (UnDaoDu preferred over Move2Japan)
4. Clean authentication setup with agent coordination
5. Livestream discovery with session caching
6. Chat listener initialization with bot identity management
7. Graceful error handling and recovery
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
from modules.infrastructure.agent_management.agent_management.src.multi_agent_manager import (
    get_agent_manager, MultiAgentManager, AgentIdentity
)
from utils.oauth_manager import get_authenticated_service, get_authenticated_service_with_fallback
from utils.env_loader import get_env_variable

logger = logging.getLogger(__name__)

class FoundUpsAgent:
    """Main application controller for FoundUps Agent with multi-agent support."""
    
    def __init__(self):
        self.running = False
        self.service = None
        self.current_listener = None
        self.stream_resolver = None
        self.agent_manager: MultiAgentManager = None
        self.current_agent: AgentIdentity = None
        self.user_channel_id = None
        
    async def initialize(self, force_agent: str = None):
        """
        Initialize the agent with multi-agent management and conflict prevention.
        
        Args:
            force_agent: Force specific agent (e.g., "UnDaoDu" to avoid Move2Japan conflicts)
        """
        logger.info("🚀 Initializing FoundUps Agent with Multi-Agent Management...")
        
        # Load environment variables
        load_dotenv()
        
        # Get required configuration
        self.user_channel_id = get_env_variable("CHANNEL_ID")
        if not self.user_channel_id:
            raise ValueError("CHANNEL_ID not found in environment variables")
            
        logger.info(f"👤 User Channel ID: {self.user_channel_id[:8]}...{self.user_channel_id[-4:]}")
        
        # Initialize multi-agent management system
        self.agent_manager = get_agent_manager()
        success = self.agent_manager.initialize(self.user_channel_id)
        
        if not success:
            raise RuntimeError("Failed to initialize multi-agent management system")
        
        # Try to select an agent
        selected_agent = self.agent_manager.select_agent(preferred_name="UnDaoDu")
        
        if not selected_agent:
            logger.warning("⚠️ Could not select UnDaoDu, trying auto-selection...")
            selected_agent = self.agent_manager.select_agent()
            
        if not selected_agent:
            logger.warning("⚠️ No agents available due to conflicts, using credential rotation...")
            # Use credential rotation instead of agent selection
            auth_result = get_authenticated_service_with_fallback()
            if not auth_result:
                logger.error("💥 Fatal error: No working credentials available!")
                return False
                
            self.service, credentials, credential_set = auth_result
            logger.info(f"🔑 Using credential rotation: {credential_set}")
            
            # Create a mock agent identity for the working credential
            class MockAgent:
                def __init__(self, credential_set):
                    self.credential_set = credential_set
                    self.channel_name = f"CredentialRotation_{credential_set}"
                    self.agent_id = f"mock_agent_{credential_set}"
                    self.status = "active"
                    self.channel_id = "mock_channel_id"
            
            selected_agent = MockAgent(credential_set)
            logger.info(f"✅ Selected agent: {selected_agent.channel_name} ({selected_agent.credential_set})")
            
            # Register the mock agent with the agent manager's registry
            self.agent_manager.registry.agents[selected_agent.agent_id] = selected_agent
        else:
            # Authenticate with selected agent's credentials
            credential_index = int(selected_agent.credential_set.split('_')[1]) - 1
            logger.info(f"🔑 Using credential index {credential_index} for {selected_agent.credential_set}")
            auth_result = get_authenticated_service(credential_index)
            
            if not auth_result:
                logger.error(f"❌ Authentication failed for {selected_agent.channel_name}")
                return False
                
            self.service, credentials = auth_result
        
        self.current_agent = selected_agent
        logger.info(f"✅ Selected agent: {selected_agent.channel_name} ({selected_agent.credential_set})")
        
        # Initialize stream resolver with session caching
        self.stream_resolver = StreamResolver(self.service)
        logger.info("📋 Stream resolver initialized with session caching")
        
        # Show conflict warnings if any
        conflicted_agents = self.agent_manager.registry.get_conflicted_agents()
        if conflicted_agents:
            logger.warning("⚠️ SAME-ACCOUNT CONFLICTS DETECTED:")
            for agent in conflicted_agents:
                logger.warning(f"   • {agent.channel_name} ({agent.credential_set}) - Cannot be used")
            logger.info("💡 These agents share the same account as the user and are blocked for safety")
        
        return True
        
    async def find_livestream(self):
        """Find an active livestream using session caching for faster reconnection."""
        logger.info(f"🔍 Searching for active livestream...")
        
        try:
            result = self.stream_resolver.resolve_stream(self.user_channel_id)
            if result:
                video_id, chat_id = result
                logger.info(f"✅ Found active livestream: {video_id[:8]}...")
                return video_id, chat_id
            else:
                logger.info("⏳ No active livestream found")
                logger.info("⏳ Waiting 60 seconds before next check")  # Increased from 30 to 60 seconds
                await asyncio.sleep(60)
                return None, None
                
        except Exception as e:
            logger.error(f"❌ Error finding livestream: {e}")
            return None, None
            
    async def start_chat_listener(self, video_id, chat_id):
        """Start the chat listener for the given livestream with agent session management."""
        logger.info(f"💬 Starting chat listener for video: {video_id[:8]}...")
        
        try:
            # Start agent session
            stream_title = "Live Stream"  # Will be updated by stream resolver
            success = self.agent_manager.start_agent_session(
                self.current_agent, 
                video_id, 
                stream_title
            )
            
            if not success:
                logger.error("❌ Failed to start agent session")
                logger.info("⏳ Waiting 10 seconds before retrying...")
                await asyncio.sleep(10)  # Add delay to prevent rapid retry loop
                return
            
            # Create chat listener with bot identity management
            self.current_listener = LiveChatListener(self.service, video_id, chat_id)
            
            # Set greeting message during initialization
            greeting = f"Hello everyone ✊✋🖐! {self.current_agent.channel_name} reporting for duty. I'm here to listen and learn (and maybe crack a joke). Beep boop!"
            self.current_listener.greeting_message = greeting
            
            # Set bot identity list for self-detection
            bot_identities = self.agent_manager.get_bot_identity_list()
            if hasattr(self.current_listener, 'set_bot_identities'):
                self.current_listener.set_bot_identities(bot_identities)
            
            # Start listening (no parameters needed)
            await self.current_listener.start_listening()
            
        except Exception as e:
            logger.error(f"❌ Chat listener error: {e}")
            
        finally:
            # End agent session
            if self.agent_manager and self.current_agent:
                self.agent_manager.end_current_session()
            self.current_listener = None
            
    async def run(self):
        """Main application loop with multi-agent coordination."""
        self.running = True
        logger.info("🎯 FoundUps Agent started - Monitoring for livestreams...")
        logger.info(f"🤖 Active Agent: {self.current_agent.channel_name}")
        
        while self.running:
            try:
                # Look for active livestream
                video_id, chat_id = await self.find_livestream()
                
                if video_id and chat_id:
                    # Start chat listener with agent session
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
            
        if self.agent_manager and self.current_agent:
            self.agent_manager.end_current_session()

async def main():
    """Application entry point with agent selection."""
    agent = FoundUpsAgent()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"📡 Received signal {signum}")
        agent.stop()
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Check for forced agent selection via environment variable
        force_agent = os.getenv("FORCE_AGENT")
        if not force_agent:
            # Default: Force UnDaoDu to avoid Move2Japan same-account conflicts
            force_agent = "UnDaoDu"
            logger.info("🎯 Defaulting to UnDaoDu agent to avoid same-account conflicts")
        
        # Initialize with forced agent selection
        await agent.initialize(force_agent=force_agent)
        await agent.run()
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        return 1
        
    return 0

def show_agent_status():
    """Show current multi-agent status."""
    from modules.infrastructure.agent_management.agent_management.src.multi_agent_manager import show_agent_status
    show_agent_status()

def force_agent_selection(agent_name: str):
    """Force selection of a specific agent."""
    os.environ["FORCE_AGENT"] = agent_name
    logger.info(f"🎯 Environment set to force agent: {agent_name}")
    logger.info("💡 Restart the application to use the new agent")

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            show_agent_status()
            sys.exit(0)
        elif command == "force-undaodu":
            force_agent_selection("UnDaoDu")
            sys.exit(0)
        elif command == "force-move2japan":
            logger.warning("⚠️ WARNING: Move2Japan may have same-account conflicts!")
            force_agent_selection("Move2Japan")
            sys.exit(0)
        elif command.startswith("force-"):
            agent_name = command[6:].replace("-", "")
            force_agent_selection(agent_name)
            sys.exit(0)
        elif command in ["help", "-h", "--help"]:
            print("\n🤖 FoundUps Agent - Multi-Agent Management")
            print("=" * 50)
            print("Usage:")
            print("  python main.py                    # Run with UnDaoDu (safe)")
            print("  python main.py status             # Show agent status")
            print("  python main.py force-undaodu      # Force UnDaoDu agent")
            print("  python main.py force-move2japan   # Force Move2Japan (risky)")
            print("  python main.py help               # Show this help")
            print("\nEnvironment Variables:")
            print("  FORCE_AGENT=UnDaoDu              # Force specific agent")
            print("  CHANNEL_ID=UC...                 # User's channel ID")
            print("\nSame-Account Conflict Prevention:")
            print("  • UnDaoDu agent is recommended (different account)")
            print("  • Move2Japan agent may conflict if user is logged in as Move2Japan")
            print("  • System automatically detects and prevents conflicts")
            sys.exit(0)
    
    # Run the application
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
