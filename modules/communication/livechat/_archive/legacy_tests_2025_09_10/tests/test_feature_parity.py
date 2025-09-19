"""
Test Feature Parity between old and new implementations
WSP-Compliant test to ensure all functionality is preserved
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.livechat_core import LiveChatCore
from src.message_processor import MessageProcessor
from src.chat_sender import ChatSender
from src.throttle_manager import ThrottleManager


class TestFeatureParity:
    """Verify all features from auto_moderator_simple are preserved"""
    
    @pytest.fixture
    def mock_youtube_service(self):
        """Create mock YouTube service"""
        service = Mock()
        service.liveChatMessages = Mock(return_value=Mock(
            insert=Mock(return_value=Mock(
                execute=Mock(return_value={"id": "test-msg-id"})
            ))
        ))
        service.channels = Mock(return_value=Mock(
            list=Mock(return_value=Mock(
                execute=Mock(return_value={"items": [{"id": "test-channel"}]})
            ))
        ))
        return service
    
    @pytest.fixture
    def livechat_core(self, mock_youtube_service):
        """Create LiveChatCore instance"""
        return LiveChatCore(
            youtube_service=mock_youtube_service,
            video_id="test-video",
            live_chat_id="test-chat"
        )
    
    @pytest.fixture
    def message_processor(self):
        """Create MessageProcessor instance"""
        return MessageProcessor()
    
    def test_consciousness_emoji_detection(self, message_processor):
        """Test: Consciousness emoji sequences are detected"""
        # Test single emojis
        assert message_processor.consciousness.detect_consciousness_command("✊")
        assert message_processor.consciousness.detect_consciousness_command("✋")
        assert message_processor.consciousness.detect_consciousness_command("🖐")
        
        # Test sequences
        assert message_processor.consciousness.detect_consciousness_command("✊✊✊")
        assert message_processor.consciousness.detect_consciousness_command("✊✋🖐")
        assert message_processor.consciousness.detect_consciousness_command("🖐🖐🖐")
    
    def test_factcheck_command_detection(self, message_processor):
        """Test: Fact-check commands are detected"""
        # Test full command
        assert message_processor._check_factcheck_command("factcheck @user")
        assert message_processor._check_factcheck_command("fc @user")
        
        # Test with emojis
        assert message_processor._check_factcheck_command("✊✊✊ fc @user")
        assert message_processor._check_factcheck_command("factcheck @John Doe")
    
    def test_maga_content_detection(self, message_processor):
        """Test: MAGA content is detected"""
        assert message_processor._check_maga_content("MAGA 2024")
        assert message_processor._check_maga_content("Trump 2024")
        assert message_processor._check_maga_content("Stop the steal")
        assert message_processor._check_maga_content("Make America Great Again")
        assert message_processor._check_maga_content("Let's go Brandon")
        
        # Should not detect normal content
        assert not message_processor._check_maga_content("Hello world")
        assert not message_processor._check_maga_content("Gaming stream")
    
    def test_adaptive_throttling(self):
        """Test: Adaptive throttling based on chat activity"""
        throttle = ThrottleManager(min_delay=2.0, max_delay=30.0)
        
        # Test quiet chat (< 5 msg/min)
        for _ in range(3):
            throttle.track_message()
        assert throttle.calculate_adaptive_delay() == 2.0  # Min delay
        
        # Test busy chat (> 30 msg/min)
        for _ in range(35):
            throttle.track_message()
        assert throttle.calculate_adaptive_delay() == 30.0  # Max delay
    
    @pytest.mark.asyncio
    async def test_message_processing_priority(self, message_processor):
        """Test: Messages are processed with correct priority"""
        # MOD consciousness command - highest priority
        mod_message = {
            "text": "✊✋🖐 test",
            "author_name": "TestMod",
            "author_id": "mod-id",
            "is_moderator": True,
            "has_consciousness": True,
            "has_factcheck": False,
            "has_maga": False
        }
        
        with patch.object(message_processor.consciousness, 
                         'process_consciousness_command',
                         new_callable=AsyncMock) as mock_consciousness:
            mock_consciousness.return_value = "Consciousness response"
            response = await message_processor.generate_response(mod_message)
            assert response == "Consciousness response"
            mock_consciousness.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_grok_integration(self, message_processor):
        """Test: Grok integration for fact-checking"""
        factcheck_message = {
            "text": "factcheck @user",
            "author_name": "Requester",
            "author_id": "req-id",
            "is_moderator": False,
            "has_consciousness": False,
            "has_factcheck": True,
            "has_maga": False
        }
        
        with patch.object(message_processor.grok, 
                         'fact_check',
                         new_callable=AsyncMock) as mock_grok:
            mock_grok.return_value = "Fact check result"
            response = await message_processor.generate_response(factcheck_message)
            assert response == "Fact check result"
    
    @pytest.mark.asyncio
    async def test_chat_sender_with_throttling(self, mock_youtube_service):
        """Test: Chat sender includes throttling"""
        sender = ChatSender(mock_youtube_service, "test-chat")
        
        # Mock the bot channel ID
        sender.bot_channel_id = "test-bot-channel"
        
        # Test throttling prevents spam
        with patch.object(sender.throttle, 'should_respond', return_value=False):
            result = await sender.send_message("Test message", "general")
            assert result is False  # Message not sent due to throttling
        
        # Test message sent when not throttled
        with patch.object(sender.throttle, 'should_respond', return_value=True):
            with patch.object(sender.throttle, 'calculate_adaptive_delay', return_value=0):
                result = await sender.send_message("Test message", "general")
                assert result is True  # Message sent successfully
    
    def test_moderation_stats_persistence(self, livechat_core):
        """Test: Moderation stats are tracked"""
        # Record some violations
        livechat_core.mod_stats.record_message()
        livechat_core.mod_stats.record_violation("user1", "spam")
        
        stats = livechat_core.get_moderation_stats()
        assert stats["total_messages"] == 1
        assert stats["total_violations"] == 1
    
    def test_session_management(self, livechat_core):
        """Test: Session management is functional"""
        assert livechat_core.session_manager is not None
        assert livechat_core.session_manager.video_id == "test-video"
    
    def test_backward_compatibility(self, mock_youtube_service):
        """Test: Backward compatibility maintained"""
        from src.livechat import LiveChatListener
        
        # Should be able to create with same interface
        listener = LiveChatListener(
            youtube_service=mock_youtube_service,
            video_id="test-video",
            live_chat_id="test-chat",
            agent_config={"test": "config"}
        )
        
        # Should have legacy attributes
        assert hasattr(listener, 'trigger_emojis')
        assert hasattr(listener, 'last_trigger_time')
        assert hasattr(listener, 'trigger_cooldown')
        assert hasattr(listener, 'message_queue')
        assert hasattr(listener, 'viewer_count')
    
    def test_all_features_present(self):
        """Test: Verify all major features are accessible"""
        features = {
            "consciousness": MessageProcessor().consciousness,
            "grok": MessageProcessor().grok,
            "throttle": ChatSender(Mock(), "test").throttle,
            "banter": MessageProcessor().banter_engine,
            "sentiment": MessageProcessor().sentiment_engine
        }
        
        # All features should be initialized
        for feature_name, feature_obj in features.items():
            assert feature_obj is not None, f"{feature_name} not initialized"
    
    @pytest.mark.asyncio
    async def test_async_performance(self, livechat_core):
        """Test: Async operations are non-blocking"""
        import time
        
        # Create multiple messages
        messages = [
            {"id": f"msg-{i}", 
             "snippet": {"displayMessage": f"Test {i}"}, 
             "authorDetails": {"displayName": f"User{i}", "channelId": f"ch-{i}"}}
            for i in range(10)
        ]
        
        # Process messages concurrently
        start = time.time()
        await livechat_core.process_message_batch(messages)
        elapsed = time.time() - start
        
        # Should be fast (concurrent, not sequential)
        assert elapsed < 1.0, "Processing should be concurrent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])