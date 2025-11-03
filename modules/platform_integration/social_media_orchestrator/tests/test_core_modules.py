"""
Unit Tests for Social Media Orchestrator Core Modules
Tests all refactored components individually
"""



import unittest
import os
import sys
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import (
    DuplicatePreventionManager,
    LiveStatusVerifier,
    ChannelConfigurationManager,
    PlatformPostingService,
    PostingStatus,
    LinkedInPage,
    XAccount
)


class TestDuplicatePreventionManager(unittest.TestCase):
    """Test duplicate prevention functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = DuplicatePreventionManager()
        self.manager.memory_file = os.path.join(self.temp_dir, 'test_posted.json')

    def test_check_not_posted(self):
        """Test checking video that hasn't been posted"""
        result = self.manager.check_if_already_posted('TEST_VIDEO_123')
        self.assertFalse(result['already_posted'])
        self.assertEqual(result['platforms_posted'], [])

    def test_mark_as_posted(self):
        """Test marking video as posted"""
        success = self.manager.mark_as_posted(
            video_id='TEST_VIDEO_456',
            title='Test Stream',
            url='https://youtube.com/test',
            platforms=['linkedin', 'x_twitter']
        )
        self.assertTrue(success)

        # Check if marked correctly
        result = self.manager.check_if_already_posted('TEST_VIDEO_456')
        self.assertTrue(result['already_posted'])
        self.assertIn('linkedin', result['platforms_posted'])
        self.assertIn('x_twitter', result['platforms_posted'])

    def test_stale_stream_blocking(self):
        """Test that ended/stale streams are blocked by duplicate manager"""
        import tempfile
        import os

        # Create a temporary database to avoid conflicts with other tests
        temp_dir = tempfile.mkdtemp()
        temp_db = os.path.join(temp_dir, 'test_stale.db')

        # Create manager with fresh database
        from src.core.duplicate_prevention_manager import DuplicatePreventionManager
        test_manager = DuplicatePreventionManager(db_path=temp_db)

        # Create a mock live status info for an ended stream
        live_status_info = {
            'broadcast_content': 'completed',
            'actual_end': '2025-10-01T12:00:00Z',
            'age_hours': 2.0  # 2 hours ago
        }

        # Test that duplicate manager blocks ended streams
        result = test_manager.check_if_already_posted('ENDED_STREAM_123', live_status_info)

        # Should be blocked
        self.assertTrue(result['already_posted'])
        self.assertEqual(result['blocked_reason'], 'Stream has ended (age: 2.0h)')
        self.assertEqual(result['status'], 'STALE_ENDED')

        # Verify it was persisted to prevent future checks
        result2 = test_manager.check_if_already_posted('ENDED_STREAM_123')
        self.assertTrue(result2['already_posted'])
        self.assertEqual(result2['status'], 'STALE_ENDED')

        # Test passed - stale stream blocking works

    def test_partial_posting(self):
        """Test video posted to only one platform"""
        self.manager.mark_as_posted(
            video_id='PARTIAL_123',
            title='Partial Test',
            url='https://youtube.com/partial',
            platforms=['linkedin']
        )

        result = self.manager.check_if_already_posted('PARTIAL_123')
        self.assertTrue(result['already_posted'])
        self.assertEqual(len(result['platforms_posted']), 1)
        self.assertIn('linkedin', result['platforms_posted'])
        self.assertNotIn('x_twitter', result['platforms_posted'])

    def test_posting_stats(self):
        """Test getting posting statistics"""
        # Add some test data
        self.manager.mark_as_posted('VIDEO_1', 'Test 1', 'url1', ['linkedin'])
        self.manager.mark_as_posted('VIDEO_2', 'Test 2', 'url2', ['x_twitter'])
        self.manager.mark_as_posted('VIDEO_3', 'Test 3', 'url3', ['linkedin', 'x_twitter'])

        stats = self.manager.get_posting_stats()
        self.assertEqual(stats['total_posted'], 3)
        self.assertEqual(stats['linkedin_posts'], 2)
        self.assertEqual(stats['x_posts'], 2)


class TestLiveStatusVerifier(unittest.TestCase):
    """Test live status verification"""

    def setUp(self):
        """Set up test fixtures"""
        self.verifier = LiveStatusVerifier()

    @patch('src.core.live_status_verifier.build')
    def test_verify_live_youtube_api(self, mock_build):
        """Test verifying live status via YouTube API"""
        # Mock YouTube API response
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.videos().list().execute.return_value = {
            'items': [{
                'snippet': {
                    'liveBroadcastContent': 'live'
                }
            }]
        }

        result = self.verifier.verify_live_status('LIVE_VIDEO_123')
        self.assertTrue(result)

    def test_cache_functionality(self):
        """Test caching of live status"""
        # Set cache
        self.verifier._live_cache['CACHED_VIDEO'] = {
            'is_live': True,
            'timestamp': datetime.now()
        }

        # Should return from cache
        result = self.verifier.verify_live_status('CACHED_VIDEO')
        self.assertTrue(result)

    def test_cache_expiry(self):
        """Test cache expiry after timeout"""
        from datetime import timedelta

        # Set expired cache
        self.verifier._live_cache['OLD_VIDEO'] = {
            'is_live': True,
            'timestamp': datetime.now() - timedelta(minutes=10)
        }

        # Should not use expired cache
        with patch.object(self.verifier, '_verify_via_youtube_api', return_value=False):
            result = self.verifier.verify_live_status('OLD_VIDEO')
            self.assertFalse(result)

    def test_clear_cache(self):
        """Test clearing cache"""
        self.verifier._live_cache = {
            'VIDEO_1': {'is_live': True, 'timestamp': datetime.now()},
            'VIDEO_2': {'is_live': False, 'timestamp': datetime.now()}
        }

        # Clear specific video
        self.verifier.clear_cache('VIDEO_1')
        self.assertNotIn('VIDEO_1', self.verifier._live_cache)
        self.assertIn('VIDEO_2', self.verifier._live_cache)

        # Clear all
        self.verifier.clear_cache()
        self.assertEqual(len(self.verifier._live_cache), 0)


class TestChannelConfigurationManager(unittest.TestCase):
    """Test channel configuration management"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(self.temp_dir, 'test_config.json')
        self.manager = ChannelConfigurationManager(config_path=config_file)

    def test_default_channels(self):
        """Test default channel configuration"""
        channels = self.manager.get_all_channel_names()
        self.assertIn('@UnDaoDu', channels)
        self.assertIn('@FoundUps', channels)
        self.assertIn('Move 2 Japan', channels)

    def test_get_channel_config(self):
        """Test getting specific channel config"""
        config = self.manager.get_channel_config('@FoundUps')
        self.assertIsNotNone(config)
        self.assertEqual(config['linkedin_page'], LinkedInPage.FOUNDUPS.value)
        self.assertEqual(config['x_account'], XAccount.FOUNDUPS.value)
        self.assertTrue(config['use_foundups_x'])

    def test_linkedin_to_x_mapping(self):
        """Test mapping LinkedIn page to X account"""
        x_account = self.manager.get_x_account_for_linkedin_page(
            LinkedInPage.UNDAODU.value
        )
        self.assertEqual(x_account, XAccount.MOVE2JAPAN.value)

        x_account = self.manager.get_x_account_for_linkedin_page(
            LinkedInPage.FOUNDUPS.value
        )
        self.assertEqual(x_account, XAccount.FOUNDUPS.value)

    def test_channel_enabled_status(self):
        """Test checking if channel is enabled"""
        self.assertTrue(self.manager.is_channel_enabled('@FoundUps'))

        # Disable a channel
        self.manager.update_channel_config('@FoundUps', {'enabled': False})
        self.assertFalse(self.manager.is_channel_enabled('@FoundUps'))

    def test_add_new_channel(self):
        """Test adding new channel configuration"""
        new_config = {
            'channel_id': 'NEW_CHANNEL_ID',
            'channel_name': 'Test Channel',
            'linkedin_page': '123456',
            'x_account': 'TestAccount',
            'enabled': True
        }

        success = self.manager.add_channel('@TestChannel', new_config)
        self.assertTrue(success)

        # Verify it was added
        config = self.manager.get_channel_config('@TestChannel')
        self.assertIsNotNone(config)
        self.assertEqual(config['channel_name'], 'Test Channel')


class TestPlatformPostingService(unittest.TestCase):
    """Test platform posting service"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = PlatformPostingService(browser_timeout=10)

    def test_browser_configuration(self):
        """Test browser configuration for accounts"""
        # FoundUps should use Edge
        browser = self.service._get_x_browser('FoundUps')
        self.assertEqual(browser, 'edge')

        # Move2Japan should use Chrome
        browser = self.service._get_x_browser('Move2Japan')
        self.assertEqual(browser, 'chrome')

    def test_linkedin_formatting(self):
        """Test LinkedIn post formatting"""
        content = self.service._format_linkedin_post(
            title='Test Stream Title',
            url='https://youtube.com/test'
        )

        self.assertIn('LIVE NOW', content)
        self.assertIn('Test Stream Title', content)
        self.assertIn('https://youtube.com/test', content)
        self.assertLessEqual(len(content), 3000)

    def test_x_formatting(self):
        """Test X/Twitter post formatting"""
        content = self.service._format_x_post(
            title='Test Stream',
            url='https://youtube.com/test'
        )

        self.assertIn('LIVE', content)
        self.assertIn('Test Stream', content)
        self.assertIn('https://youtube.com/test', content)
        self.assertLessEqual(len(content), 280)

    def test_x_formatting_long_title(self):
        """Test X formatting with long title"""
        long_title = 'A' * 300  # Very long title
        content = self.service._format_x_post(
            title=long_title,
            url='https://youtube.com/test'
        )

        self.assertLessEqual(len(content), 280)
        self.assertIn('...', content)  # Should be truncated

    @patch('subprocess.run')
    def test_post_to_linkedin_success(self, mock_run):
        """Test successful LinkedIn posting"""
        mock_run.return_value = MagicMock(returncode=0, stderr='')

        result = self.service.post_to_linkedin(
            title='Test',
            url='https://test.com',
            linkedin_page='123456'
        )

        self.assertEqual(result.status, PostingStatus.SUCCESS)
        self.assertEqual(result.platform, 'linkedin')

    @patch('subprocess.run')
    def test_post_to_x_failure(self, mock_run):
        """Test failed X posting"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr='Browser automation failed'
        )

        result = self.service.post_to_x(
            title='Test',
            url='https://test.com',
            x_account='TestAccount'
        )

        self.assertEqual(result.status, PostingStatus.FAILED)
        self.assertEqual(result.platform, 'x_twitter')
        self.assertIn('Browser automation failed', result.error)

    def test_validate_configuration(self):
        """Test configuration validation"""
        validation = self.service.validate_configuration()

        self.assertIn('valid', validation)
        self.assertIn('errors', validation)
        self.assertIn('info', validation)
        self.assertIn('browser_config', validation['info'])


class TestIntegration(unittest.TestCase):
    """Integration tests for refactored modules"""

    def setUp(self):
        """Set up test fixtures"""
        from src.refactored_posting_orchestrator import RefactoredPostingOrchestrator
        self.orchestrator = RefactoredPostingOrchestrator()

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes all components"""
        self.assertIsNotNone(self.orchestrator.duplicate_manager)
        self.assertIsNotNone(self.orchestrator.status_verifier)
        self.assertIsNotNone(self.orchestrator.channel_config)
        self.assertIsNotNone(self.orchestrator.posting_service)

    @patch.object(LiveStatusVerifier, 'verify_live_status', return_value=True)
    def test_handle_stream_detected(self, mock_verify):
        """Test handling stream detection event"""
        result = self.orchestrator.handle_stream_detected(
            video_id='TEST_123',
            title='Test Stream',
            url='https://youtube.com/test',
            channel_name='@FoundUps'
        )

        self.assertIn('video_id', result)
        self.assertEqual(result['video_id'], 'TEST_123')
        self.assertIn('platforms', result)

    def test_migration_bridge(self):
        """Test migration bridge compatibility"""
        from src.orchestrator_migration import get_migration_bridge

        bridge = get_migration_bridge()
        self.assertIsNotNone(bridge)

        # Test backward compatible API
        result = bridge.check_if_already_posted('MIGRATION_TEST')
        self.assertIn('already_posted', result)
        self.assertIn('platforms_posted', result)


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicatePreventionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestLiveStatusVerifier))
    suite.addTests(loader.loadTestsFromTestCase(TestChannelConfigurationManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformPostingService))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)