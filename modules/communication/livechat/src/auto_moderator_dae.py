"""
Auto Moderator DAE (Domain Autonomous Entity)
WSP-Compliant: WSP 27 (Universal DAE Architecture), WSP 3 (Module Organization)

This is the WSP-compliant version using livechat_core.
Orchestrates all chat moderation components following DAE architecture.

NAVIGATION: YouTube DAE lifecycle orchestrator.
-> Called by: main.py::monitor_youtube
-> Delegates to: StreamResolver, LiveChatCore, youtube_auth credential handlers
-> Related: NAVIGATION.py -> MODULE_GRAPH["core_flows"]["stream_detection_flow"]
-> Quick ref: NAVIGATION.py -> NEED_TO["boot auto moderator dae"]
"""

import asyncio
import logging
import os
import time
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
        self._last_stream_id = None
        self.transition_start = None
        
        # WRE Integration for recursive learning
        try:
            from modules.infrastructure.wre_core.recursive_improvement.src.wre_integration import (
                record_error, record_success, get_optimized_approach
            )
            self.wre_record_error = record_error
            self.wre_record_success = record_success
            self.wre_get_optimized = get_optimized_approach
            logger.info("[0102] WRE Recursive Learning connected to DAE")
        except Exception as e:
            logger.debug(f"WRE Integration not available: {e}")
            self.wre_record_error = None
            self.wre_record_success = None
            self.wre_get_optimized = None
        
        logger.info("✅ Auto Moderator DAE initialized")
    
    def connect(self) -> bool:
        """
        Phase -1/0: Connect to YouTube - NO-QUOTA mode by default.
        Only use API tokens when we actually find a stream.

        Returns:
            Success status
        """
        logger.info("🔌 Starting in NO-QUOTA mode to preserve API tokens...")

        # Default to NO-QUOTA mode for stream searching
        # We'll only authenticate when we actually find a stream
        self.service = None
        self.credential_set = "NO-QUOTA"
        logger.info("🌐 Using NO-QUOTA web scraping for stream discovery")
        logger.info("💡 API tokens will only be used when active stream is found")

        return True
    
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
        
        # List of channels to check - FoundUps, Move2Japan, and UnDaoDu (WSP 3: Multi-channel support)
        channels_to_check = [
            os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw'),   # UnDaoDu main channel
            os.getenv('CHANNEL_ID2', 'UCSNTUXjAgpd4sgWYP0xoJgw'),  # FoundUps channel
            os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UCklMTNnu5POwRmQsg5JJumA'),  # Move2Japan channel
        ]
        
        # Filter out None values
        channels_to_check = [ch for ch in channels_to_check if ch]
        
        # Try each channel
        for i, channel_id in enumerate(channels_to_check, 1):
            logger.info(f"🔎 [{i}/{len(channels_to_check)}] Checking channel: {channel_id[:12]}...")
            try:
                result = self.stream_resolver.resolve_stream(channel_id)
                logger.info(f"🔎 [{i}/{len(channels_to_check)}] Channel {channel_id[:12]}... result: {'FOUND' if result and result[0] else 'NONE'}")
            except Exception as e:
                logger.error(f"🔎 [{i}/{len(channels_to_check)}] Channel {channel_id[:12]}... ERROR: {e}")
                result = None
            
            if result and result[0]:  # Accept stream even without chat_id
                video_id = result[0]
                live_chat_id = result[1] if len(result) > 1 else None

                if not live_chat_id:
                    logger.info(f"⚠️ Found stream but chat_id not available (likely quota exhausted)")
                    logger.info(f"✅ Accepting stream anyway - video ID: {video_id}")
                else:
                    logger.info(f"✅ Found stream on channel {channel_id[:12]}... with video ID: {video_id}")

                return video_id, live_chat_id
        
        logger.info(f"❌ No active livestream found on {len(channels_to_check)} channel(s)")
        return None
    
    async def monitor_chat(self):
        """
        Phase 2: Autonomous chat monitoring and moderation.
        
        This is the main execution loop with intelligent throttling.
        Returns when stream ends/becomes inactive for seamless switching.
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
        quick_check_mode = False  # Flag for rapid checking after stream end
        
        while True:
            # Check for manual trigger
            if trigger.check_trigger():
                logger.info("🚨 Manual trigger detected! Checking for stream immediately...")
                consecutive_failures = 0  # Reset failures on manual trigger
                previous_delay = None
                trigger.reset()
            
            # Force fresh search if in quick check mode (after stream ended)
            if quick_check_mode:
                # Clear any cached data to ensure we find NEW streams
                if self.stream_resolver:
                    self.stream_resolver.clear_cache()
                    logger.info("🔍 Quick check mode - cleared cache, searching for NEW stream")
            
            result = self.find_livestream()
            if result:
                # Reset counters on success
                retry_count = 0
                consecutive_failures = 0
                quick_check_mode = False  # Reset quick mode
                break
            
            # Calculate intelligent delay based on retries and failures
            # Use trigger-aware delay for better idle behavior
            if quick_check_mode:
                # After stream ends, check more frequently for new stream
                delay = min(60, 30 * (consecutive_failures + 1))  # 5s, 10s, 15s, 15s...
                logger.info(f"⚡ Quick check mode: Checking again in {delay}s for new stream")
            else:
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

        # Now that we found a stream, try to authenticate for full functionality
        # Authenticate FIRST, then get chat_id with API
        if not self.service and video_id:
            logger.info("🔐 Stream found! Attempting authentication for chat interaction...")
            try:
                service = get_authenticated_service()
                if service:
                    self.service = create_monitored_service(service)
                    self.credential_set = getattr(service, '_credential_set', "Unknown")
                    logger.info(f"✅ Authenticated with credential set {self.credential_set}")

                    # Now try to get the chat_id with authenticated service
                    if not live_chat_id:
                        logger.info("🔍 Getting chat ID with authenticated service...")
                        self.stream_resolver = StreamResolver(self.service)
                        auth_result = self.stream_resolver.resolve_stream(os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw'))
                        if auth_result and len(auth_result) > 1:
                            live_chat_id = auth_result[1]
                            logger.info(f"✅ Got chat ID with API: {live_chat_id[:20]}...")
                        else:
                            logger.warning("⚠️ Could not get chat ID even with API")
            except Exception as e:
                logger.warning(f"⚠️ Authentication failed: {e}")
                logger.info("🌐 Continuing in NO-QUOTA mode (view-only)")

        # WRE Monitor: Track stream transition completion
        if hasattr(self, 'wre_monitor') and self.wre_monitor:
            if self._last_stream_id and self.transition_start:
                transition_time = time.time() - self.transition_start
                self.wre_monitor.track_stream_transition(self._last_stream_id, video_id, transition_time)
            self._last_stream_id = video_id
            self.transition_start = time.time()

        # Create LiveChatCore instance
        self.livechat = LiveChatCore(
            youtube_service=self.service,
            video_id=video_id,
            live_chat_id=live_chat_id
        )

        # Initialize LiveChatCore (THIS TRIGGERS SOCIAL MEDIA POSTS!)
        logger.info("🚀 Initializing LiveChatCore (includes social media posting)...")
        await self.livechat.initialize()

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
        
        # Phase 2: Monitor autonomously - loop forever looking for streams
        consecutive_failures = 0
        stream_ended_normally = False
        
        while True:
            try:
                await self.monitor_chat()
                # If monitor_chat returns normally, stream ended - look for new one
                stream_ended_normally = True
                logger.info("🔄 Stream ended or became inactive - seamless switching engaged")
                logger.info("⚡ Immediately searching for new stream (agentic mode)...")

                # IMPORTANT: Release API credentials to go back to NO-QUOTA mode
                # This prevents wasting tokens while searching for new streams
                if self.service:
                    logger.info("🔒 Releasing API credentials - switching back to NO-QUOTA mode")
                    self.service = None
                    self.credential_set = "NO-QUOTA"

                # WRE Monitor: Mark transition start
                if hasattr(self, 'wre_monitor') and self.wre_monitor:
                    self.transition_start = time.time()

                # Reset the LiveChat instance for fresh connection
                if self.livechat:
                    self.livechat.stop_listening()
                    self.livechat = None

                # Clear cached stream info to force fresh search
                if self.stream_resolver:
                    # Force stream resolver to use NO-QUOTA mode
                    self.stream_resolver.youtube = None
                    # Use the proper clear_cache method
                    self.stream_resolver.clear_cache()
                    logger.info("🔄 Stream ended - cleared all caches for fresh NO-QUOTA search")
                
                # Execute idle automation tasks before waiting
                # WSP 35: Module Execution Automation during idle periods
                try:
                    from modules.infrastructure.idle_automation.src.idle_automation_dae import run_idle_automation
                    logger.info("🤖 Executing idle automation tasks...")
                    idle_result = await run_idle_automation()
                    if idle_result.get("overall_success"):
                        logger.info(f"✅ Idle automation completed successfully ({idle_result.get('duration', 0):.1f}s)")
                    else:
                        logger.info(f"⚠️ Idle automation completed with issues ({idle_result.get('duration', 0):.1f}s)")
                except ImportError:
                    logger.debug("Idle automation module not available - skipping")
                except Exception as e:
                    logger.warning(f"Idle automation failed: {e}")

                # Quick transition - only wait 5 seconds before looking for new stream
                await asyncio.sleep(5)
                consecutive_failures = 0  # Reset failure counter on clean exit

                # Set quick check mode for the next monitor_chat call
                # This will make it check more frequently after a stream ends
                logger.info("🎯 Entering quick-check mode for seamless stream detection")
                
            except KeyboardInterrupt:
                logger.info("⏹️ Stopped by user")
                break
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Error in monitoring loop (attempt #{consecutive_failures}): {e}")
                
                # Exponential backoff for retries
                wait_time = min(30 * (2 ** consecutive_failures), 600)  # Max 10 minutes
                logger.info(f"🔄 Restarting in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
                # After too many failures, do a full reconnect
                if consecutive_failures >= 5:
                    logger.warning("🔄 Too many failures - attempting full reconnection")
                    self.service = None  # Force re-authentication
                    consecutive_failures = 0
                    # Also reset stream resolver cache
                    if self.stream_resolver:
                        self.stream_resolver.clear_cache()
    
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
