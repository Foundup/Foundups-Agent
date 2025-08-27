"""
Auto Moderator DAE (Domain Autonomous Entity)
WSP-Compliant: WSP 27 (Universal DAE Architecture), WSP 3 (Module Organization)

This is the WSP-compliant version using livechat_core.
Orchestrates all chat moderation components following DAE architecture.
"""

import asyncio
import logging
import os
from typing import Optional
from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
from modules.platform_integration.youtube_auth.src.monitored_youtube_service import create_monitored_service
from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver

# Import WSP-compliant livechat_core
from .livechat_core import LiveChatCore

logger = logging.getLogger(__name__)


class AutoModeratorDAE:
    """
    WSP-Compliant Auto Moderator DAE
    
    Phases per WSP 27:
    -1: Signal - YouTube chat messages
     0: Knowledge - User profiles, chat history
     1: Protocol - Moderation rules, consciousness responses
     2: Agentic - Autonomous moderation and interaction
    """
    
    def __init__(self):
        """Initialize the Auto Moderator DAE."""
        logger.info("🚀 Initializing Auto Moderator DAE (WSP-Compliant)")
        
        self.service = None
        self.credentials = None
        self.credential_set = None
        self.livechat = None
        self.stream_resolver = None
        
        logger.info("✅ Auto Moderator DAE initialized")
    
    def connect(self) -> bool:
        """
        Phase -1/0: Connect to YouTube and authenticate.
        
        Returns:
            Success status
        """
        logger.info("🔌 Connecting to YouTube...")
        
        # Get authenticated YouTube service
        service = get_authenticated_service()
        if not service:
            logger.error("❌ Failed to authenticate with YouTube")
            return False
        
        # Wrap with monitoring to track quota
        self.service = create_monitored_service(service)
        self.credential_set = getattr(service, '_credential_set', "Unknown")
        logger.info(f"✅ Authenticated with credential set {self.credential_set} (quota monitoring enabled)")
        
        # Get channel info
        try:
            response = self.service.channels().list(
                part='snippet',
                mine=True
            ).execute()
            
            if response.get('items'):
                channel = response['items'][0]
                channel_id = channel['id']
                channel_name = channel['snippet']['title']
                logger.info(f"✅ Connected as: {channel_name}")
                return True
            else:
                logger.error("❌ No channel found for authenticated user")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to get channel info: {e}")
            return False
    
    def find_livestream(self) -> Optional[tuple]:
        """
        Find active livestream on the channel.
        Can check multiple channels if configured.
        
        Returns:
            Tuple of (video_id, live_chat_id) or None
        """
        logger.info("🔍 Looking for livestream...")
        
        if not self.stream_resolver:
            self.stream_resolver = StreamResolver(self.service)
        
        # List of channels to check - you can add more channels here
        channels_to_check = [
            os.getenv('CHANNEL_ID', 'UCklMTNnu5POwRmQsg5JJumA'),  # Move2Japan main
            # Add backup channels here if needed:
            # os.getenv('BACKUP_CHANNEL_ID'),  # Backup channel
            # 'UC_ANOTHER_CHANNEL_ID',  # Another channel you want to monitor
        ]
        
        # Filter out None values
        channels_to_check = [ch for ch in channels_to_check if ch]
        
        # Try each channel
        for channel_id in channels_to_check:
            logger.info(f"🔎 Checking channel: {channel_id[:12]}...")
            result = self.stream_resolver.resolve_stream(channel_id)
            
            if result and result[0] and result[1]:
                video_id, live_chat_id = result
                logger.info(f"✅ Found stream on channel {channel_id[:12]}... with video ID: {video_id}")
                return video_id, live_chat_id
        
        logger.info(f"❌ No active livestream found on {len(channels_to_check)} channel(s)")
        return None
    
    async def monitor_chat(self):
        """
        Phase 2: Autonomous chat monitoring and moderation.
        
        This is the main execution loop with intelligent throttling.
        """
        # Import the intelligent delay calculator and trigger
        from modules.platform_integration.stream_resolver.src.stream_resolver import calculate_enhanced_delay
        from modules.communication.livechat.src.stream_trigger import StreamTrigger, create_intelligent_delay
        
        # Initialize trigger mechanism
        trigger = StreamTrigger()
        trigger.create_trigger_instructions()
        
        # Keep looking for livestream until found
        retry_count = 0
        consecutive_failures = 0
        previous_delay = None
        
        while True:
            # Check for manual trigger
            if trigger.check_trigger():
                logger.info("🚨 Manual trigger detected! Checking for stream immediately...")
                consecutive_failures = 0  # Reset failures on manual trigger
                previous_delay = None
                trigger.reset()
            
            result = self.find_livestream()
            if result:
                # Reset counters on success
                retry_count = 0
                consecutive_failures = 0
                break
            
            # Calculate intelligent delay based on retries and failures
            # Use trigger-aware delay for better idle behavior
            delay = create_intelligent_delay(
                consecutive_failures=consecutive_failures,
                previous_delay=previous_delay,
                has_trigger=True  # We have trigger capability
            )
            
            # Show different messages based on delay length
            if delay < 60:
                logger.info(f"📺 No stream found. Checking again in {delay:.0f} seconds...")
            elif delay < 300:
                logger.info(f"⏳ No stream found. Waiting {delay/60:.1f} minutes (quota conservation mode)...")
            else:
                logger.info(f"💤 Idle mode: {delay/60:.1f} minutes (or until triggered)")
                logger.info(f"💡 Tip: echo TRIGGER > stream_trigger.txt to check immediately")
            
            # Wait with intelligent delay, but check for triggers every 5 seconds
            elapsed = 0
            check_interval = 5  # Check for triggers every 5 seconds
            
            while elapsed < delay:
                # Wait for shorter interval
                wait_time = min(check_interval, delay - elapsed)
                await asyncio.sleep(wait_time)
                elapsed += wait_time
                
                # Check for trigger during wait
                if trigger.check_trigger():
                    logger.info("🚨 Trigger activated! Checking for stream now...")
                    consecutive_failures = 0  # Reset on trigger
                    previous_delay = None
                    trigger.reset()
                    break
            
            # Update counters
            retry_count += 1
            consecutive_failures += 1
            previous_delay = delay
        
        video_id, live_chat_id = result
        
        # Create LiveChatCore instance
        self.livechat = LiveChatCore(
            youtube_service=self.service,
            video_id=video_id,
            live_chat_id=live_chat_id
        )
        
        # Start monitoring
        logger.info("="*60)
        logger.info("👁️ MONITORING CHAT - WSP-COMPLIANT ARCHITECTURE")
        logger.info("="*60)
        
        try:
            await self.livechat.start_listening()
        except KeyboardInterrupt:
            logger.info("⏹️ Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        finally:
            if self.livechat:
                self.livechat.stop_listening()
    
    async def run(self):
        """
        Main entry point - full DAE lifecycle.
        """
        logger.info("=" * 60)
        logger.info("🧠 AUTO MODERATOR DAE STARTING")
        logger.info("WSP-Compliant: Using livechat_core architecture")
        logger.info("=" * 60)
        
        # Phase -1/0: Connect and authenticate
        if not self.connect():
            logger.error("Failed to connect to YouTube")
            return
        
        # Phase 2: Monitor autonomously - loop forever
        while True:
            try:
                await self.monitor_chat()
                # If monitor_chat returns, stream ended - look for new one
                logger.info("🔄 Stream ended. Looking for new stream...")
                await asyncio.sleep(10)  # Brief pause before looking again
            except KeyboardInterrupt:
                logger.info("⏹️ Stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                logger.info("🔄 Restarting in 30 seconds...")
                await asyncio.sleep(30)
    
    def get_status(self) -> dict:
        """Get current DAE status."""
        status = {
            'connected': bool(self.service),
            'monitoring': bool(self.livechat and self.livechat.is_running),
            'credential_set': self.credential_set,
            'architecture': 'livechat_core (WSP-compliant)',
            'modules': {
                'message_processor': True,
                'chat_sender': True,
                'chat_poller': True,
                'session_manager': True,
                'moderation_stats': True,
                'consciousness': True,
                'grok': True,
                'throttle': True
            }
        }
        
        if self.livechat:
            status['stats'] = self.livechat.get_moderation_stats()
        
        return status


def main():
    """Main entry point for the Auto Moderator DAE."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run DAE
    dae = AutoModeratorDAE()
    asyncio.run(dae.run())


if __name__ == "__main__":
    main()