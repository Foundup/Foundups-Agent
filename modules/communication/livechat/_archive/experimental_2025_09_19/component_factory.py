"""
Component Factory - WSP-Compliant Singleton Pattern
WSP 49: Module Directory Structure Standards
WSP 40: Architectural Coherence Protocol

Eliminates component duplication across YouTube DAE modules.
Provides centralized access to shared instances.
"""

import logging
from typing import Optional, Dict, Any
from threading import Lock

logger = logging.getLogger(__name__)


class ComponentFactory:
    """
    WSP-Compliant Component Factory
    
    Singleton pattern for shared YouTube DAE components.
    Eliminates duplication of BanterEngine, GrokGreetingGenerator, etc.
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ComponentFactory, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize factory if not already done."""
        if not getattr(self, '_initialized', False):
            logger.info("🏭 Initializing Component Factory (WSP-Compliant)")
            
            # Shared component instances
            self._banter_engine = None
            self._greeting_generator = None
            self._memory_manager = None
            self._llm_bypass_engine = None
            self._emoji_limiter = None
            self._consciousness_handler = None
            self._sentiment_engine_0102 = None  # Pure 0102 intelligence
            
            # Configuration
            self._memory_dir = "memory"
            self._trigger_emojis = ["✊", "✋", "🖐️"]  # Centralized emoji config
            
            self._initialized = True
            logger.info("✅ Component Factory initialized")
    
    @property
    def memory_dir(self) -> str:
        """Get standardized memory directory."""
        return self._memory_dir
    
    @property 
    def trigger_emojis(self) -> list:
        """Get standardized trigger emojis."""
        return self._trigger_emojis.copy()
    
    def get_banter_engine(self):
        """Get shared BanterEngine instance."""
        if self._banter_engine is None:
            try:
                from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
                self._banter_engine = BanterEngine()
                logger.info("🎭 BanterEngine instance created")
            except ImportError as e:
                logger.warning(f"BanterEngine not available: {e}")
                self._banter_engine = None
        return self._banter_engine
    
    def get_greeting_generator(self, stream_title: str = ""):
        """Get shared GrokGreetingGenerator instance."""
        if self._greeting_generator is None:
            try:
                from modules.communication.livechat.src.greeting_generator import GrokGreetingGenerator
                self._greeting_generator = GrokGreetingGenerator(stream_title=stream_title)
                logger.info("👋 GrokGreetingGenerator instance created")
            except ImportError as e:
                logger.warning(f"GrokGreetingGenerator not available: {e}")
                self._greeting_generator = None
        return self._greeting_generator
    
    def get_memory_manager(self, memory_dir: Optional[str] = None):
        """Get shared ChatMemoryManager instance."""
        if self._memory_manager is None:
            try:
                from modules.communication.livechat.src.chat_memory_manager import ChatMemoryManager
                dir_path = memory_dir or self._memory_dir
                self._memory_manager = ChatMemoryManager(dir_path)
                logger.info("🧠 ChatMemoryManager instance created")
            except ImportError as e:
                logger.warning(f"ChatMemoryManager not available: {e}")
                self._memory_manager = None
        return self._memory_manager
    
    def get_llm_bypass_engine(self):
        """Get shared LLMBypassEngine instance."""
        if self._llm_bypass_engine is None:
            try:
                from modules.communication.livechat.src.llm_bypass_engine import LLMBypassEngine
                self._llm_bypass_engine = LLMBypassEngine()
                logger.info("🔄 LLMBypassEngine instance created")
            except ImportError as e:
                logger.warning(f"LLMBypassEngine not available: {e}")
                self._llm_bypass_engine = None
        return self._llm_bypass_engine
    
    def get_emoji_limiter(self):
        """Get shared EmojiResponseLimiter instance."""
        if self._emoji_limiter is None:
            try:
                from modules.communication.livechat.src.emoji_response_limiter import EmojiResponseLimiter
                self._emoji_limiter = EmojiResponseLimiter()
                logger.info("⚡ EmojiResponseLimiter instance created")
            except ImportError as e:
                logger.debug(f"EmojiResponseLimiter not available: {e}")
                self._emoji_limiter = None
        return self._emoji_limiter
    
    def get_consciousness_handler(self, sentiment_engine, grok_integration=None):
        """Get shared ConsciousnessHandler instance."""
        if self._consciousness_handler is None:
            try:
                from modules.communication.livechat.src.consciousness_handler import ConsciousnessHandler
                self._consciousness_handler = ConsciousnessHandler(sentiment_engine, grok_integration)
                logger.info("🧠 ConsciousnessHandler instance created")
            except ImportError as e:
                logger.warning(f"ConsciousnessHandler not available: {e}")
                self._consciousness_handler = None
        return self._consciousness_handler
    
    def get_sentiment_engine_0102(self):
        """Get shared AgenticSentiment0102 instance - Pure 0102 intelligence."""
        if self._sentiment_engine_0102 is None:
            try:
                from modules.ai_intelligence.banter_engine.src.agentic_sentiment_0102 import AgenticSentiment0102
                self._sentiment_engine_0102 = AgenticSentiment0102()
                logger.info("🧠✨ AgenticSentiment0102 (Pure 0102 Intelligence) instance created")
            except ImportError as e:
                logger.warning(f"AgenticSentiment0102 not available: {e}")
                self._sentiment_engine_0102 = None
        return self._sentiment_engine_0102
    
    def get_moderation_stats(self, memory_dir: Optional[str] = None):
        """Get ModerationStats instance (not singleton - needs separate instances)."""
        try:
            from modules.communication.livechat.src.moderation_stats import ModerationStats
            dir_path = memory_dir or self._memory_dir
            return ModerationStats(dir_path)
        except ImportError as e:
            logger.warning(f"ModerationStats not available: {e}")
            return None
    
    def get_session_manager(self, youtube_service, video_id: str):
        """Get SessionManager instance (not singleton - needs separate instances)."""
        try:
            from modules.communication.livechat.src.session_manager import SessionManager
            return SessionManager(youtube_service, video_id)
        except ImportError as e:
            logger.warning(f"SessionManager not available: {e}")
            return None
    
    def reset_factory(self):
        """Reset all cached instances (for testing or configuration changes)."""
        logger.info("🔄 Resetting Component Factory")
        self._banter_engine = None
        self._greeting_generator = None
        self._memory_manager = None
        self._llm_bypass_engine = None
        self._emoji_limiter = None
        self._consciousness_handler = None
        self._sentiment_engine_0102 = None  # Pure 0102 intelligence
        logger.info("✅ Component Factory reset complete")


# Convenience function for easy access
def get_factory() -> ComponentFactory:
    """Get the ComponentFactory singleton instance."""
    return ComponentFactory()
