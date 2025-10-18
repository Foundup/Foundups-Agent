#!/usr/bin/env python3
"""
Test Social Media Posting Integration - WSP FMAS Compliant
Tests the refactored _post_stream_to_linkedin method and orchestrator integration

WSP Compliance:
- WSP 5: Test coverage for social media posting refactoring
- WSP 22: ModLog integration for architectural changes
- WSP 27: DAE architecture validation (orchestrator pattern)
- WSP 84: Code verification - existing modules vs new patterns

Test Coverage:
- Functionality: Orchestrator integration, fallback mechanisms
- Modularity: Clean separation between YouTube DAE and posting orchestrator  
- Audit: Sequential posting validation, content generation verification
- System-level: Error handling, import failures, credential validation

Architecture Under Test:
- PRIMARY: YouTube DAE -> SimplePostingOrchestrator -> Platform adapters
- FALLBACK: YouTube DAE -> Direct posting (sequential: LinkedIn -> X)
- VALIDATION: Browser conflict prevention, proper error handling
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.communication.livechat.src.livechat_core import LiveChatCore
from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE


class TestSocialMediaPosting(unittest.TestCase):
    """Test cases for social media posting functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_youtube = MagicMock()
        self.video_id = "test_video_123"
        self.live_chat_id = "test_chat_456"
        
        # Create LiveChatCore instance
        self.livechat = LiveChatCore(
            youtube_service=self.mock_youtube,
            video_id=self.video_id,
            live_chat_id=self.live_chat_id
        )
    
    def test_orchestrator_path_success(self):
        """Test successful orchestrator posting"""
        async def run_test():
            # Mock successful orchestrator import and posting
            with patch('modules.communication.livechat.src.livechat_core.logger') as mock_logger:
                with patch.dict('sys.modules', {'modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator': MagicMock()}):
                    # Mock the orchestrator
                    mock_orchestrator_module = MagicMock()
                    mock_orchestrator = MagicMock()
                    mock_response = MagicMock()
                    mock_response.success_count = 2
                    mock_response.failure_count = 0
                    mock_response.results = [
                        MagicMock(success=True, platform=MagicMock(value='linkedin'), message='Posted successfully'),
                        MagicMock(success=True, platform=MagicMock(value='x_twitter'), message='Posted successfully')
                    ]
                    
                    mock_orchestrator.post_stream_notification = AsyncMock(return_value=mock_response)
                    mock_orchestrator_module.SimplePostingOrchestrator.return_value = mock_orchestrator
                    
                    with patch.dict('sys.modules', {'modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator': mock_orchestrator_module}):
                        # Test the posting method
                        await self.livechat._post_stream_to_linkedin()
                        
                        # Verify orchestrator was called
                        mock_orchestrator.post_stream_notification.assert_called_once()
                        call_args = mock_orchestrator.post_stream_notification.call_args
                        self.assertIn('stream_title', call_args.kwargs)
                        self.assertIn('stream_url', call_args.kwargs)
                        
                        # Verify logging
                        mock_logger.info.assert_any_call("[ORCHESTRATOR] Using social media orchestrator for posting")
                        mock_logger.info.assert_any_call("[ORCHESTRATOR] [OK] linkedin: Posted successfully")
                        mock_logger.info.assert_any_call("[ORCHESTRATOR] [OK] x_twitter: Posted successfully")
        
        asyncio.run(run_test())
    
    def test_orchestrator_import_failure_fallback(self):
        """Test fallback when orchestrator import fails"""
        async def run_test():
            # Mock the fallback method
            with patch.object(self.livechat, '_fallback_direct_posting', new_callable=AsyncMock) as mock_fallback:
                with patch('modules.communication.livechat.src.livechat_core.logger') as mock_logger:
                    # Force import error
                    with patch('builtins.__import__', side_effect=ImportError("No module named 'oauth'")):
                        # Test the posting method
                        await self.livechat._post_stream_to_linkedin()
                        
                        # Verify fallback was called
                        mock_fallback.assert_called_once()
                        call_args = mock_fallback.call_args[0]
                        self.assertIn('youtube.com/watch?v=', call_args[0])  # stream_url
                        self.assertEqual(call_args[1], None)  # stream_title (None by default)
                        
                        # Verify logging
                        mock_logger.error.assert_any_call(
                            "[ORCHESTRATOR] Social media orchestrator not available: No module named 'oauth'"
                        )
        
        asyncio.run(run_test())
    
    def test_fallback_direct_posting_sequential_behavior(self):
        """Test that fallback method posts sequentially with proper delays"""
        async def run_test():
            # Mock environment variables
            with patch.dict('os.environ', {'LINKEDIN_EMAIL': 'test@example.com', 'LINKEDIN_PASSWORD': 'pass'}):
                with patch.dict('os.environ', {'X_Acc1': 'testuser', 'x_Acc_pass': 'pass'}):
                    # Mock the poster modules
                    mock_linkedin_poster = MagicMock()
                    mock_linkedin_poster.post_to_company_page.return_value = True
                    
                    mock_x_poster = MagicMock()
                    mock_x_poster.post_to_x.return_value = True
                    
                    with patch('modules.platform_integration.linkedin_agent.src.anti_detection_poster.AntiDetectionLinkedIn', return_value=mock_linkedin_poster):
                        with patch('modules.platform_integration.x_twitter.src.x_anti_detection_poster.AntiDetectionX', return_value=mock_x_poster):
                            with patch('modules.communication.livechat.src.livechat_core.logger') as mock_logger:
                                with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                                    # Test fallback posting
                                    await self.livechat._fallback_direct_posting(
                                        "https://youtube.com/watch?v=test123",
                                        "Test Stream Title"
                                    )
                                    
                                    # Verify sequential behavior - LinkedIn first
                                    mock_linkedin_poster.post_to_company_page.assert_called_once()
                                    
                                    # Verify 5-second delay for browser cleanup
                                    mock_sleep.assert_any_call(5)
                                    
                                    # Verify X posting after delay
                                    mock_x_poster.post_to_x.assert_called_once()
                                    
                                    # Verify logging shows sequential approach
                                    mock_logger.info.assert_any_call(
                                        "[FALLBACK] SEQUENTIAL posting: LinkedIn first, then X (5sec delay)"
                                    )
        
        asyncio.run(run_test())
    
    def test_fallback_content_generation(self):
        """Test that fallback generates proper content format"""
        async def run_test():
            # Mock environment - no credentials to skip actual posting
            with patch.dict('os.environ', {}, clear=True):
                with patch('modules.communication.livechat.src.livechat_core.logger') as mock_logger:
                    # Test with title
                    await self.livechat._fallback_direct_posting(
                        "https://youtube.com/watch?v=test123",
                        "Amazing AI Development Stream"
                    )
                    
                    # Check content format was logged (would be used in actual posting)
                    # The method should create content like:
                    # @UnDaoDu going live!
                    # Amazing AI Development Stream
                    # https://youtube.com/watch?v=test123
                    
                    mock_logger.info.assert_any_call("[FALLBACK] Stream title: Amazing AI Development Stream")
                    mock_logger.info.assert_any_call("[INFO] LinkedIn credentials not configured")
                    mock_logger.info.assert_any_call("[INFO] X/Twitter credentials not configured")
        
        asyncio.run(run_test())
    
    def test_stream_url_generation(self):
        """Test that stream URL is properly generated from video_id"""
        expected_url = f"https://www.youtube.com/watch?v={self.video_id}"
        
        # The _post_stream_to_linkedin method should generate this URL
        # We can verify this by checking what gets passed to the orchestrator
        async def run_test():
            with patch.dict('sys.modules', {'modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator': MagicMock()}):
                mock_orchestrator_module = MagicMock()
                mock_orchestrator = MagicMock()
                mock_response = MagicMock()
                mock_response.success_count = 0
                mock_response.failure_count = 0
                mock_response.results = []
                
                mock_orchestrator.post_stream_notification = AsyncMock(return_value=mock_response)
                mock_orchestrator_module.SimplePostingOrchestrator.return_value = mock_orchestrator
                
                with patch.dict('sys.modules', {'modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator': mock_orchestrator_module}):
                    await self.livechat._post_stream_to_linkedin()
                    
                    # Verify the URL was generated correctly
                    call_args = mock_orchestrator.post_stream_notification.call_args
                    self.assertEqual(call_args.kwargs['stream_url'], expected_url)
        
        asyncio.run(run_test())

    def test_simple_solution_stream_trigger(self):
        """Test the simple solution: Stream detection -> Social orchestration trigger"""
        async def run_test():
            # Create AutoModeratorDAE instance
            dae = AutoModeratorDAE()

            # Mock the service for _get_stream_details
            mock_service = MagicMock()
            mock_response = {
                'items': [{
                    'snippet': {
                        'title': 'Test Live Stream Title'
                    }
                }]
            }
            mock_service.videos().list().execute.return_value = mock_response
            dae.service = mock_service

            # Mock the social orchestration
            mock_response_obj = MagicMock()
            mock_response_obj.all_successful.return_value = True
            mock_response_obj.results = [
                MagicMock(success=True, platform=MagicMock(value='linkedin'), message='Posted to LinkedIn'),
                MagicMock(success=True, platform=MagicMock(value='x_twitter'), message='Posted to X')
            ]

            with patch('modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator.SimplePostingOrchestrator') as mock_orchestrator_class:
                mock_orchestrator = MagicMock()
                mock_orchestrator.post_stream_notification = AsyncMock(return_value=mock_response_obj)
                mock_orchestrator_class.return_value = mock_orchestrator

                # Test the simple trigger mechanism
                await dae._trigger_social_media_posting("test_video_123", "test_chat_456")

                # Verify orchestration was called with correct parameters
                mock_orchestrator.post_stream_notification.assert_called_once()
                call_args = mock_orchestrator.post_stream_notification.call_args

                self.assertEqual(call_args.kwargs['stream_title'], 'Test Live Stream Title')
                self.assertEqual(call_args.kwargs['stream_url'], 'https://www.youtube.com/watch?v=test_video_123')

        asyncio.run(run_test())

    def test_simple_solution_orchestration_handling(self):
        """Test that social orchestration properly handles the posting request"""
        async def run_test():
            # Create AutoModeratorDAE instance
            dae = AutoModeratorDAE()

            # Mock the SimplePostingOrchestrator
            with patch('modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator.SimplePostingOrchestrator') as mock_orchestrator_class:
                mock_orchestrator = MagicMock()
                mock_response = MagicMock()
                mock_response.all_successful.return_value = True
                mock_response.results = [
                    MagicMock(success=True, platform=MagicMock(value='linkedin'), message='Success'),
                    MagicMock(success=True, platform=MagicMock(value='x_twitter'), message='Success')
                ]

                mock_orchestrator.post_stream_notification = AsyncMock(return_value=mock_response)
                mock_orchestrator_class.return_value = mock_orchestrator

                # Test sending to orchestration
                await dae._send_to_social_orchestration("Test Stream", "https://youtube.com/test")

                # Verify orchestrator was called correctly
                mock_orchestrator.post_stream_notification.assert_called_once_with(
                    stream_title="Test Stream",
                    stream_url="https://youtube.com/test"
                )

        asyncio.run(run_test())


def run_tests():
    """Run the test suite"""
    print("\n" + "="*60)
    print("TESTING SOCIAL MEDIA POSTING INTEGRATION - ENHANCED")
    print("="*60)
    print("Testing refactored _post_stream_to_linkedin method")
    print("- Orchestrator integration path")
    print("- Fallback direct posting path")
    print("- Sequential posting behavior")
    print("- Content generation")
    print("- [U+2B50] SIMPLE SOLUTION: Stream detection -> Social orchestration")
    print("="*60)
    
    unittest.main(verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()