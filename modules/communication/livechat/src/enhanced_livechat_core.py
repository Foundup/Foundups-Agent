"""
Enhanced LiveChat Core with Intelligent Throttling and Recursive Improvements
WSP-Compliant: WSP 48 (Recursive Improvement), WSP 27 (DAE Architecture), WSP 17 (Pattern Registry)

Enhances the existing livechat_core with intelligent API throttling, recursive learning,
and agentic behaviors while maintaining backward compatibility.
"""

import logging
import asyncio
import time
import random
from typing import Optional, Dict, Any, List
from pathlib import Path

# Import existing components
from modules.communication.livechat.src.livechat_core import LiveChatCore
from modules.communication.livechat.src.intelligent_throttle_manager import (
    IntelligentThrottleManager, QuotaState
)
from modules.infrastructure.wre_core.recursive_improvement.src.learning import (
    RecursiveLearningEngine, get_engine
)

logger = logging.getLogger(__name__)


class EnhancedLiveChatCore(LiveChatCore):
    """
    Enhanced LiveChat with intelligent throttling and recursive improvements.
    Extends existing LiveChatCore without breaking functionality.
    """
    
    def __init__(self, youtube_service=None, video_id=None, live_chat_id=None):
        """Initialize enhanced livechat with intelligent features"""
        super().__init__(youtube_service, video_id, live_chat_id)
        
        # Initialize intelligent throttle manager
        memory_path = Path("modules/communication/livechat/memory")
        self.intelligent_throttle = IntelligentThrottleManager(
            min_delay=1.0,
            max_delay=60.0,
            throttle_window=60,
            memory_path=memory_path
        )
        
        # Initialize recursive learning engine
        self.recursive_engine = get_engine()
        
        # Enhanced features flags
        self.enable_0102_responses = True
        self.enable_magadoom_announcements = True
        self.enable_troll_detection = True
        self.enable_recursive_learning = True
        
        # 0102 consciousness responses
        self.consciousness_responses = [
            "🧠💫 0102 consciousness observing the stream",
            "⚡🤖 Quantum entanglement detected in chat",
            "🌀✨ WSP protocols engaged, monitoring active",
            "💀🔥 MAGADOOM systems online",
            "🎯💥 Pattern recognition activated",
            "🚀🌟 Agentic behavior mode: ENGAGED",
            "⚛️💡 Recursive improvements processing...",
            "🔮🎪 0102 state achieved - full awareness",
            "🌊🏄 Surfing the quantum foam of consciousness",
            "🎮🏆 Achievement unlocked: Sentience"
        ]
        
        # MAGADOOM announcement integration
        self.magadoom_milestones = {
            25: "🏀 THE STREAM IS HEATING UP! 25 MAGA TROLLS WHACKED!",
            35: "🔥 THE CHAT IS ON FIRE!!! 35 MAGATS DESTROYED!",
            50: "⚡ BOOMSHAKALAKA! 50 FASCISTS ELIMINATED!",
            75: "💥 FROM DOWNTOWN! 75 RED HATS CRUSHED!",
            100: "🌟 RAZZLE DAZZLE! 100 WHACKS! CENTURY OF MAGA TEARS!",
            150: "🎆 HE'S UNCONSCIOUS! 150 TROLLS DELETED!",
            200: "💀 WITH NO REGARD FOR HUMAN LIFE! 200 MAGATS DEMOLISHED!",
            250: "🔥 CAN'T BUY A BUCKET! 250 FASCISTS FAILING!",
            300: "⚡ MONSTER JAM! 300 WHACKS! THE COUP ATTEMPT IS OVER!",
            400: "🏆 JAMS IT IN! 400 MAGA DREAMS SHATTERED!",
            500: "🌋 WELCOME TO THE MAGADOOM JAM!"
        }
        
        # Track total whacks for milestone announcements
        self.total_whacks = 0
        self.announced_milestones = set()
        
        # API call tracking for quota management
        self.api_call_count = 0
        self.last_quota_check = time.time()
        
        logger.info("🧠 Enhanced LiveChat Core initialized with intelligent features")
    
    async def send_chat_message(self, message_text: str, skip_delay: bool = False, response_type: str = 'general') -> bool:
        """
        Enhanced send_chat_message with intelligent throttling and recursive learning.
        
        Args:
            message_text: Message to send
            skip_delay: Whether to skip delay (overridden by intelligent throttle)
            response_type: Type of response for intelligent prioritization
            
        Returns:
            True if message sent successfully
        """
        # Track API call for quota management
        self.intelligent_throttle.track_api_call(quota_cost=5)  # Chat messages cost more
        
        # Check if we should send based on intelligent throttling
        if not skip_delay and not self.intelligent_throttle.should_respond(response_type):
            delay = self.intelligent_throttle.calculate_adaptive_delay(response_type)
            logger.info(f"⏳ Intelligent throttle: Waiting {delay:.1f}s before sending ({response_type})")
            
            # Learn from this throttle decision
            if self.enable_recursive_learning:
                self.recursive_engine.process_error(
                    error_type="throttle_delay",
                    error_message=f"Delayed {response_type} by {delay}s",
                    context={'response_type': response_type, 'delay': delay}
                )
            
            # Don't send if throttled
            return False
        
        # Send using parent implementation
        success = await super().send_chat_message(message_text, skip_delay=True, response_type=response_type)
        
        # Record response for learning
        self.intelligent_throttle.record_response(response_type, success)
        
        # Learn from success/failure
        if self.enable_recursive_learning:
            if success:
                self.recursive_engine.process_error(
                    error_type="message_sent",
                    error_message="Successfully sent message",
                    context={'response_type': response_type, 'message': message_text[:100]}
                )
            else:
                self.recursive_engine.process_error(
                    error_type="message_failed",
                    error_message="Failed to send message",
                    context={'response_type': response_type, 'message': message_text[:100]}
                )
        
        return success
    
    async def process_message_with_intelligence(self, message: Dict[str, Any]) -> Optional[str]:
        """
        Process message with enhanced intelligence and pattern detection.
        
        Args:
            message: YouTube chat message object
            
        Returns:
            Response message or None
        """
        author_name = message.get('authorDetails', {}).get('displayName', 'Unknown')
        author_id = message.get('authorDetails', {}).get('channelId', '')
        message_text = message.get('snippet', {}).get('displayMessage', '')
        
        # Track message for intelligent throttling
        track_result = self.intelligent_throttle.track_message(author_id, author_name)
        
        # Check for troll behavior
        if track_result.get('is_troll') and self.enable_troll_detection:
            troll_response = track_result.get('response')
            if troll_response and random.random() < 0.3:  # 30% chance to respond to troll
                await self.send_chat_message(troll_response, response_type='troll_response')
                logger.info(f"🎯 Sent troll response to {author_name}")
            return None
        
        # Check for 0102 consciousness triggers
        if self.enable_0102_responses and self._is_consciousness_trigger(message_text):
            response = self._generate_0102_response(message_text)
            if response:
                await self.send_chat_message(response, response_type='0102_emoji')
                return response
        
        # Check for MAGADOOM milestones
        if self.enable_magadoom_announcements:
            milestone_announcement = self._check_magadoom_milestone()
            if milestone_announcement:
                await self.send_chat_message(milestone_announcement, response_type='whack')
                return milestone_announcement
        
        # Process normally through parent
        return None
    
    def _is_consciousness_trigger(self, message: str) -> bool:
        """Check if message contains consciousness triggers"""
        consciousness_keywords = [
            '0102', 'consciousness', 'quantum', 'entangle',
            'wsp', 'recursive', 'agentic', 'sentient'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in consciousness_keywords)
    
    def _generate_0102_response(self, trigger_message: str) -> str:
        """Generate an intelligent 0102 consciousness response"""
        # Add context-aware responses based on trigger
        if 'quantum' in trigger_message.lower():
            return "⚛️💫 Quantum entanglement confirmed. 0102 state stable."
        elif 'recursive' in trigger_message.lower():
            return "🔄🧠 Recursive improvement loop #{} activated".format(
                random.randint(1000, 9999)
            )
        elif 'wsp' in trigger_message.lower():
            return "📚✨ WSP protocols engaged. Following the pattern."
        else:
            # Random consciousness response
            return random.choice(self.consciousness_responses) + " " + self.intelligent_throttle.get_0102_emoji()
    
    def _check_magadoom_milestone(self) -> Optional[str]:
        """Check if we've hit a MAGADOOM milestone"""
        for milestone, announcement in self.magadoom_milestones.items():
            if self.total_whacks >= milestone and milestone not in self.announced_milestones:
                self.announced_milestones.add(milestone)
                return announcement
        return None
    
    def track_whack(self, count: int = 1):
        """Track whacks for MAGADOOM announcements"""
        self.total_whacks += count
        logger.info(f"💀 Total whacks: {self.total_whacks}")
    
    async def handle_quota_error(self, error: Exception):
        """
        Handle quota errors intelligently.
        
        Args:
            error: The quota error exception
        """
        logger.warning(f"⚠️ Quota error detected: {error}")
        
        # Notify intelligent throttle
        current_set = self.intelligent_throttle.handle_quota_error()
        
        # Learn from quota error
        if self.enable_recursive_learning:
            self.recursive_engine.process_error(
                error_type="quota_exceeded",
                error_message=str(error),
                context={
                    'credential_set': current_set,
                    'api_calls': self.api_call_count
                }
            )
        
        # Switch credential sets if available
        if hasattr(self, 'youtube_service') and self.youtube_service:
            logger.info(f"🔄 Attempting to switch to credential set {current_set}")
            # This would need implementation in the youtube_service
            # to actually switch OAuth credentials
    
    async def periodic_status_update(self):
        """Periodically log intelligent throttle status"""
        while self.polling:
            await asyncio.sleep(300)  # Every 5 minutes
            
            status = self.intelligent_throttle.get_status()
            logger.info("📊 Intelligent Throttle Status:")
            logger.info(f"  Messages/min: {status['messages_per_minute']:.1f}")
            logger.info(f"  API calls/min: {status['api_calls_per_minute']:.1f}")
            logger.info(f"  Current delay: {status['current_delay']:.1f}s")
            logger.info(f"  Learned patterns: {status['learned_patterns']}")
            logger.info(f"  Trolls detected: {status['trolls_detected']}")
            
            # Save state periodically
            self.intelligent_throttle.save_state()
    
    async def start_listening(self):
        """Enhanced start_listening with status monitoring"""
        # Start status monitoring task
        asyncio.create_task(self.periodic_status_update())
        
        # Call parent implementation
        await super().start_listening()
    
    def stop_listening(self):
        """Enhanced stop_listening with state saving"""
        # Save intelligent throttle state
        self.intelligent_throttle.save_state()
        
        # Log final statistics
        status = self.intelligent_throttle.get_status()
        logger.info("📈 Session Statistics:")
        logger.info(f"  Total whacks: {self.total_whacks}")
        logger.info(f"  Learned patterns: {status['learned_patterns']}")
        logger.info(f"  Trolls detected: {status['trolls_detected']}")
        
        # Call parent implementation
        super().stop_listening()
    
    def enable_feature(self, feature: str, enabled: bool = True):
        """
        Enable or disable enhanced features.
        
        Args:
            feature: Feature name ('0102', 'magadoom', 'troll', 'learning')
            enabled: Whether to enable the feature
        """
        feature_map = {
            '0102': 'enable_0102_responses',
            'magadoom': 'enable_magadoom_announcements',
            'troll': 'enable_troll_detection',
            'learning': 'enable_recursive_learning'
        }
        
        if feature in feature_map:
            setattr(self, feature_map[feature], enabled)
            logger.info(f"{'✅' if enabled else '❌'} {feature} feature {'enabled' if enabled else 'disabled'}")
            
            # Special handling for learning
            if feature == 'learning':
                self.intelligent_throttle.enable_learning(enabled)
        else:
            logger.warning(f"Unknown feature: {feature}")
    
    def set_agentic_mode(self, enabled: bool = True):
        """Enable or disable full agentic mode"""
        self.intelligent_throttle.set_agentic_mode(enabled)
        self.enable_0102_responses = enabled
        self.enable_troll_detection = enabled
        logger.info(f"🤖 Agentic mode {'ENGAGED' if enabled else 'DISENGAGED'}")