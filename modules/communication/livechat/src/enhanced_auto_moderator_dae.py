#!/usr/bin/env python3
"""
Enhanced Auto Moderator DAE with Intelligent Throttling
WSP-Compliant: WSP 27 (DAE Architecture), WSP 48 (Recursive Improvement), WSP 80 (Cube-Level DAE)

Enhanced version with intelligent API throttling, recursive learning, and agentic behaviors.
Maintains backward compatibility while adding advanced features.
"""

import asyncio
import logging
import os
import sys
from typing import Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from modules.platform_integration.youtube_auth.src.youtube_auth import YouTubeAuthManager
from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver
from modules.communication.livechat.src.enhanced_livechat_core import EnhancedLiveChatCore
from modules.communication.livechat.src.livechat_core import LiveChatCore
from modules.communication.livechat.src.stream_trigger import StreamTrigger
from modules.communication.livechat.src.intelligent_delay import create_intelligent_delay

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedAutoModeratorDAE:
    """
    Enhanced DAE that automatically finds and monitors YouTube livestreams.
    Includes intelligent throttling, recursive learning, and agentic behaviors.
    
    WSP 27 Phase Architecture:
    - Phase -1: Signal detection (find stream)
    - Phase 0: Knowledge gathering (authenticate)
    - Phase 1: Protocol engagement (connect to chat)
    - Phase 2: Agentic operation (monitor and respond)
    """
    
    def __init__(self, enhanced_mode: bool = True):
        """
        Initialize Enhanced Auto Moderator DAE.
        
        Args:
            enhanced_mode: Whether to use enhanced features (default: True)
        """
        self.service = None
        self.stream_resolver = None
        self.livechat = None
        self.enhanced_mode = enhanced_mode
        
        # Feature flags for enhanced mode
        self.enable_intelligent_throttle = enhanced_mode
        self.enable_recursive_learning = enhanced_mode
        self.enable_0102_responses = enhanced_mode
        self.enable_magadoom = enhanced_mode
        self.enable_troll_detection = enhanced_mode
        
        logger.info(f"🧠 Enhanced Auto Moderator DAE initialized (enhanced_mode={enhanced_mode})")
    
    def connect(self) -> bool:
        """
        Phase 0: Establish YouTube connection with authentication.
        Enhanced with intelligent credential rotation.
        """
        try:
            logger.info("=" * 60)
            logger.info("🔐 PHASE 0: AUTHENTICATION")
            logger.info("=" * 60)
            
            # Initialize auth manager with intelligent credential rotation
            auth_manager = YouTubeAuthManager()
            
            # Get authenticated service with quota tracking
            self.service = auth_manager.get_authenticated_service()
            
            if self.service:
                logger.info("✅ YouTube authentication successful")
                
                # Initialize stream resolver
                self.stream_resolver = StreamResolver(self.service)
                
                # Log credential set info if available
                if hasattr(auth_manager, 'current_set'):
                    logger.info(f"📊 Using credential set: {auth_manager.current_set}")
                
                return True
            else:
                logger.error("❌ Failed to authenticate with YouTube")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def find_livestream(self) -> Optional[Tuple[str, str]]:
        """
        Phase -1: Find active livestream using stream resolver.
        Enhanced with intelligent retry and caching.
        """
        if not self.stream_resolver:
            logger.error("Stream resolver not initialized")
            return None
        
        try:
            # Clear cache for fresh search if enhanced mode
            if self.enhanced_mode and hasattr(self.stream_resolver, 'clear_cache'):
                self.stream_resolver.clear_cache()
            
            result = self.stream_resolver.find_live_stream()
            
            if result:
                video_id = result.get('video_id')
                live_chat_id = result.get('live_chat_id')
                channel_name = result.get('channel_title', 'Unknown')
                viewer_count = result.get('viewer_count', 'N/A')
                
                logger.info("="*60)
                logger.info(f"🎥 STREAM FOUND!")
                logger.info(f"📺 Channel: {channel_name}")
                logger.info(f"🔗 Video ID: {video_id}")
                logger.info(f"👥 Viewers: {viewer_count}")
                logger.info(f"💬 Chat ID: {live_chat_id}")
                logger.info("="*60)
                
                # Track stream discovery in enhanced mode
                if self.enhanced_mode and self.livechat:
                    self.livechat.intelligent_throttle.track_api_call(quota_cost=100)
                
                return video_id, live_chat_id
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error finding stream: {e}")
            
            # Handle quota errors intelligently in enhanced mode
            if self.enhanced_mode and '403' in str(e):
                logger.warning("⚠️ Quota error detected, switching credentials...")
                if self.livechat:
                    asyncio.create_task(self.livechat.handle_quota_error(e))
            
            return None
    
    async def monitor_with_auto_find(self):
        """
        Main monitoring loop with intelligent stream finding and enhanced features.
        """
        # Initialize trigger for manual stream checks
        trigger = StreamTrigger()
        
        # Track state for intelligent behavior
        consecutive_failures = 0
        retry_count = 0
        previous_delay = None
        quick_check_mode = False
        
        while True:
            logger.info("🔍 Searching for livestream...")
            
            # Check for manual trigger
            if trigger.check_trigger():
                logger.info("🚨 Manual trigger detected! Searching immediately...")
                consecutive_failures = 0
                previous_delay = None
                trigger.reset()
            
            # Force fresh search if in quick check mode
            if quick_check_mode:
                if self.stream_resolver:
                    self.stream_resolver.clear_cache()
                    logger.info("🔍 Quick check mode - cleared cache, searching for NEW stream")
            
            result = self.find_livestream()
            if result:
                # Reset counters on success
                retry_count = 0
                consecutive_failures = 0
                quick_check_mode = False
                break
            
            # Calculate intelligent delay
            if quick_check_mode:
                delay = min(15, 5 * (consecutive_failures + 1))
                logger.info(f"⚡ Quick check mode: Checking again in {delay}s for new stream")
            else:
                delay = create_intelligent_delay(
                    consecutive_failures=consecutive_failures,
                    previous_delay=previous_delay,
                    has_trigger=True
                )
                
                if delay < 60:
                    logger.info(f"📺 No stream found. Checking again in {delay:.0f} seconds...")
                elif delay < 300:
                    logger.info(f"⏳ No stream found. Waiting {delay/60:.1f} minutes...")
                else:
                    logger.info(f"💤 Idle mode: {delay/60:.1f} minutes (or until triggered)")
            
            # Wait with trigger checking
            elapsed = 0
            check_interval = 5
            
            while elapsed < delay:
                wait_time = min(check_interval, delay - elapsed)
                await asyncio.sleep(wait_time)
                elapsed += wait_time
                
                if trigger.check_trigger():
                    logger.info("🚨 Trigger activated! Checking for stream now...")
                    consecutive_failures = 0
                    previous_delay = None
                    trigger.reset()
                    break
            
            retry_count += 1
            consecutive_failures += 1
            previous_delay = delay
        
        video_id, live_chat_id = result
        
        # Create LiveChat instance (enhanced or regular based on mode)
        if self.enhanced_mode:
            logger.info("🧠 Creating Enhanced LiveChat with intelligent features...")
            self.livechat = EnhancedLiveChatCore(
                youtube_service=self.service,
                video_id=video_id,
                live_chat_id=live_chat_id
            )
            
            # Configure enhanced features
            self.livechat.enable_feature('0102', self.enable_0102_responses)
            self.livechat.enable_feature('magadoom', self.enable_magadoom)
            self.livechat.enable_feature('troll', self.enable_troll_detection)
            self.livechat.enable_feature('learning', self.enable_recursive_learning)
            
            # Set full agentic mode if all features enabled
            if all([self.enable_0102_responses, self.enable_magadoom, 
                   self.enable_troll_detection, self.enable_recursive_learning]):
                self.livechat.set_agentic_mode(True)
                logger.info("🤖 FULL AGENTIC MODE ENGAGED")
        else:
            logger.info("📺 Creating standard LiveChat...")
            self.livechat = LiveChatCore(
                youtube_service=self.service,
                video_id=video_id,
                live_chat_id=live_chat_id
            )
        
        # Start monitoring
        logger.info("="*60)
        logger.info("👁️ MONITORING CHAT - ENHANCED DAE ARCHITECTURE")
        logger.info("="*60)
        
        try:
            await self.livechat.start_listening()
        except KeyboardInterrupt:
            logger.info("⏹️ Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            
            # Handle errors intelligently in enhanced mode
            if self.enhanced_mode and '403' in str(e):
                await self.livechat.handle_quota_error(e)
        finally:
            if self.livechat:
                self.livechat.stop_listening()
    
    async def run(self):
        """
        Main entry point - full DAE lifecycle with enhanced features.
        """
        logger.info("=" * 60)
        logger.info("🧠 ENHANCED AUTO MODERATOR DAE STARTING")
        logger.info(f"Mode: {'ENHANCED' if self.enhanced_mode else 'STANDARD'}")
        logger.info("WSP-Compliant: Using enhanced architecture")
        logger.info("=" * 60)
        
        # Phase -1/0: Connect and authenticate
        if not self.connect():
            logger.error("Failed to connect to YouTube")
            return
        
        # Phase 1/2: Find stream and monitor
        await self.monitor_with_auto_find()
    
    def configure_features(self, **kwargs):
        """
        Configure enhanced features.
        
        Args:
            intelligent_throttle: Enable intelligent throttling
            recursive_learning: Enable recursive learning
            0102_responses: Enable 0102 consciousness responses
            magadoom: Enable MAGADOOM announcements
            troll_detection: Enable troll detection
        """
        for feature, enabled in kwargs.items():
            if hasattr(self, f'enable_{feature}'):
                setattr(self, f'enable_{feature}', enabled)
                logger.info(f"{'✅' if enabled else '❌'} {feature} {'enabled' if enabled else 'disabled'}")


async def main():
    """Main entry point with command line argument support"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Auto Moderator DAE')
    parser.add_argument('--standard', action='store_true', 
                       help='Use standard mode without enhancements')
    parser.add_argument('--no-learning', action='store_true',
                       help='Disable recursive learning')
    parser.add_argument('--no-0102', action='store_true',
                       help='Disable 0102 consciousness responses')
    parser.add_argument('--no-magadoom', action='store_true',
                       help='Disable MAGADOOM announcements')
    parser.add_argument('--no-troll', action='store_true',
                       help='Disable troll detection')
    
    args = parser.parse_args()
    
    # Create DAE with appropriate mode
    enhanced_mode = not args.standard
    dae = EnhancedAutoModeratorDAE(enhanced_mode=enhanced_mode)
    
    # Configure features based on arguments
    if enhanced_mode:
        dae.configure_features(
            recursive_learning=not args.no_learning,
            enable_0102_responses=not args.no_0102,
            enable_magadoom=not args.no_magadoom,
            enable_troll_detection=not args.no_troll
        )
    
    # Run the DAE
    await dae.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Enhanced Auto Moderator DAE stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)