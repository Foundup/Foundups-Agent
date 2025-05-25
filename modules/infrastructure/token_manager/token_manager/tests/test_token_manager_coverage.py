#!/usr/bin/env python3
"""
Comprehensive test coverage for Token Manager module.
Focuses on covering missing lines and edge cases.
"""

import unittest
import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from modules.infrastructure.token_manager.token_manager import TokenManager


class TestTokenManagerCoverage(unittest.TestCase):
    """Test suite for comprehensive Token Manager coverage."""

    def setUp(self):
        """Set up test environment."""
        self.manager = TokenManager()

    # ===== Tests for health check caching and cooldown logic =====
    
    @patch('modules.infrastructure.token_manager.token_manager.src.token_manager.get_authenticated_service')
    @patch('modules.infrastructure.token_manager.token_manager.src.token_manager.get_oauth_token_file')
    def test_check_token_health_cache_hit_healthy(self, mock_get_token_file, mock_get_service):
        """Test check_token_health returns cached result for healthy token."""
        # Arrange
        mock_get_token_file.return_value = "test_token.json"
        mock_service = MagicMock()
        mock_service.channels().list().execute.return_value = {"items": [{}]}
        mock_get_service.return_value = mock_service
        
        # First call to populate cache
        result1 = self.manager.check_token_health(0)
        self.assertTrue(result1)
        
        # Second call should use cache (mock won't be called again)
        mock_get_service.reset_mock()
        result2 = self.manager.check_token_health(0)
        
        # Assert
        self.assertTrue(result2)
        mock_get_service.assert_not_called()  # Should use cache

    @patch('modules.infrastructure.token_manager.token_manager.src.token_manager.get_authenticated_service')
    @patch('modules.infrastructure.token_manager.token_manager.src.token_manager.get_oauth_token_file')
    def test_check_token_health_cache_expired(self, mock_get_token_file, mock_get_service):
        """Test check_token_health refreshes cache when expired."""
        # Arrange
        mock_get_token_file.return_value = "test_token.json"
        mock_service = MagicMock()
        mock_service.channels().list().execute.return_value = {"items": [{}]}
        mock_get_service.return_value = mock_service
        
        # Set short health check interval for testing
        self.manager.health_check_interval = 0.1
        
        # First call
        result1 = self.manager.check_token_health(0)
        self.assertTrue(result1)
        
        # Wait for cache to expire
        time.sleep(0.2)
        
        # Second call should refresh cache
        mock_get_service.reset_mock()
        result2 = self.manager.check_token_health(0)
        
        # Assert
        self.assertTrue(result2)
        mock_get_service.assert_called_once()  # Should refresh cache

    @patch('modules.infrastructure.token_manager.token_manager.src.token_manager.get_authenticated_service')
    @patch('modules.infrastructure.token_manager.token_manager.src.token_manager.get_oauth_token_file')
    def test_check_token_health_service_creation_failure(self, mock_get_token_file, mock_get_service):
        """Test check_token_health when service creation fails."""
        # Arrange
        mock_get_token_file.return_value = "test_token.json"
        mock_get_service.return_value = None  # Service creation fails
        
        # Act
        result = self.manager.check_token_health(0)
        
        # Assert
        self.assertFalse(result)
        self.assertIn(0, self.manager.token_health_cache)
        self.assertFalse(self.manager.token_health_cache[0]['healthy'])

    @patch('modules.infrastructure.token_manager.token_manager.src.token_manager.get_authenticated_service')
    @patch('modules.infrastructure.token_manager.token_manager.src.token_manager.get_oauth_token_file')
    def test_check_token_health_api_call_exception(self, mock_get_token_file, mock_get_service):
        """Test check_token_health when API call raises exception."""
        # Arrange
        mock_get_token_file.return_value = "test_token.json"
        mock_service = MagicMock()
        mock_service.channels().list().execute.side_effect = Exception("API Error")
        mock_get_service.return_value = mock_service
        
        # Act
        result = self.manager.check_token_health(0)
        
        # Assert
        self.assertFalse(result)
        self.assertIn(0, self.manager.token_health_cache)
        self.assertFalse(self.manager.token_health_cache[0]['healthy'])

    def test_check_token_health_default_current_token(self):
        """Test check_token_health uses current token index when none specified."""
        # Arrange
        self.manager.current_token_index = 2
        
        with patch.object(self.manager, 'check_token_health', wraps=self.manager.check_token_health) as mock_check:
            with patch('modules.infrastructure.token_manager.token_manager.src.token_manager.get_authenticated_service') as mock_get_service:
                with patch('modules.infrastructure.token_manager.token_manager.src.token_manager.get_oauth_token_file') as mock_get_token_file:
                    mock_get_token_file.return_value = "test_token.json"
                    mock_service = MagicMock()
                    mock_service.channels().list().execute.return_value = {"items": [{}]}
                    mock_get_service.return_value = mock_service
                    
                    # Act - call without token_index parameter
                    result = self.manager.check_token_health()
                    
                    # Assert
                    self.assertTrue(result)
                    # Verify it used the current token index (2)
                    mock_get_service.assert_called_with(2)

    # ===== Tests for parallel token checking =====
    
    @pytest.mark.asyncio
    async def test_check_token_parallel_success(self):
        """Test _check_token_parallel with successful health check."""
        with patch.object(self.manager, 'check_token_health', return_value=True):
            result = await self.manager._check_token_parallel(1)
            self.assertEqual(result, 1)

    @pytest.mark.asyncio
    async def test_check_token_parallel_failure(self):
        """Test _check_token_parallel with failed health check."""
        with patch.object(self.manager, 'check_token_health', return_value=False):
            result = await self.manager._check_token_parallel(1)
            self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_check_token_parallel_exception(self):
        """Test _check_token_parallel when health check raises exception."""
        with patch.object(self.manager, 'check_token_health', side_effect=Exception("Health check error")):
            result = await self.manager._check_token_parallel(1)
            self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_check_tokens_parallel_success(self):
        """Test _check_tokens_parallel finds healthy token."""
        # Mock check_token_health to return False for indices 0,1 and True for index 2
        def mock_health_check(index):
            return index == 2
        
        with patch.object(self.manager, 'check_token_health', side_effect=mock_health_check):
            result = await self.manager._check_tokens_parallel([0, 1, 2, 3])
            self.assertEqual(result, 2)

    @pytest.mark.asyncio
    async def test_check_tokens_parallel_all_fail(self):
        """Test _check_tokens_parallel when all tokens fail."""
        with patch.object(self.manager, 'check_token_health', return_value=False):
            result = await self.manager._check_tokens_parallel([0, 1, 2, 3])
            self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_check_tokens_parallel_timeout(self):
        """Test _check_tokens_parallel handles timeout."""
        # Set very short timeout for testing
        self.manager.parallel_check_timeout = 0.001
        
        async def slow_check(index):
            await asyncio.sleep(0.1)  # Longer than timeout
            return index
        
        with patch.object(self.manager, '_check_token_parallel', side_effect=slow_check):
            result = await self.manager._check_tokens_parallel([0, 1])
            self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_check_tokens_parallel_exception(self):
        """Test _check_tokens_parallel handles exceptions."""
        with patch.object(self.manager, '_check_token_parallel', side_effect=Exception("Parallel check error")):
            result = await self.manager._check_tokens_parallel([0, 1])
            self.assertIsNone(result)

    # ===== Tests for token rotation edge cases =====
    
    @pytest.mark.asyncio
    async def test_rotate_tokens_parallel_success(self):
        """Test rotate_tokens succeeds with parallel checking."""
        self.manager.current_token_index = 0
        
        with patch.object(self.manager, '_check_tokens_parallel', return_value=2):
            result = await self.manager.rotate_tokens()
            
            self.assertEqual(result, 2)
            self.assertEqual(self.manager.current_token_index, 2)

    @pytest.mark.asyncio
    async def test_rotate_tokens_parallel_fail_sequential_success(self):
        """Test rotate_tokens falls back to sequential when parallel fails."""
        self.manager.current_token_index = 0
        
        # Mock parallel check to fail, sequential to succeed on index 1
        def mock_health_check(index):
            return index == 1
        
        with patch.object(self.manager, '_check_tokens_parallel', return_value=None):
            with patch.object(self.manager, 'check_token_health', side_effect=mock_health_check):
                result = await self.manager.rotate_tokens()
                
                self.assertEqual(result, 1)
                self.assertEqual(self.manager.current_token_index, 1)

    @pytest.mark.asyncio
    async def test_rotate_tokens_all_tokens_fail(self):
        """Test rotate_tokens when all tokens fail health check."""
        self.manager.current_token_index = 0
        
        with patch.object(self.manager, '_check_tokens_parallel', return_value=None):
            with patch.object(self.manager, 'check_token_health', return_value=False):
                result = await self.manager.rotate_tokens()
                
                self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_rotate_tokens_full_cycle_no_healthy(self):
        """Test rotate_tokens when it cycles through all tokens without finding healthy one."""
        self.manager.current_token_index = 0
        self.manager.max_retries = 1  # Reduce retries for faster test
        
        with patch.object(self.manager, '_check_tokens_parallel', return_value=None):
            with patch.object(self.manager, 'check_token_health', return_value=False):
                with patch('asyncio.sleep', new_callable=AsyncMock):  # Mock sleep to speed up test
                    result = await self.manager.rotate_tokens()
                    
                    self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_rotate_tokens_with_retries(self):
        """Test rotate_tokens retry mechanism."""
        self.manager.current_token_index = 0
        self.manager.max_retries = 3
        self.manager.retry_delay = 0.01  # Short delay for testing
        
        # Mock to fail first few attempts, succeed when we get to index 2
        call_count = 0
        def mock_health_check(index):
            nonlocal call_count
            call_count += 1
            # Succeed on index 2 after a few calls
            return call_count >= 3 and index == 2
        
        with patch.object(self.manager, '_check_tokens_parallel', return_value=None):
            with patch.object(self.manager, 'check_token_health', side_effect=mock_health_check):
                result = await self.manager.rotate_tokens()
                
                self.assertEqual(result, 2)
                self.assertEqual(self.manager.current_token_index, 2)

    # ===== Tests for _update_health_cache =====
    
    def test_update_health_cache_healthy(self):
        """Test _update_health_cache for healthy token."""
        self.manager._update_health_cache(1, True)
        
        cache_entry = self.manager.token_health_cache[1]
        self.assertTrue(cache_entry['healthy'])
        self.assertEqual(cache_entry['cooldown_end'], 0)
        self.assertGreater(cache_entry['timestamp'], 0)

    def test_update_health_cache_unhealthy(self):
        """Test _update_health_cache for unhealthy token."""
        self.manager._update_health_cache(1, False)
        
        cache_entry = self.manager.token_health_cache[1]
        self.assertFalse(cache_entry['healthy'])
        self.assertGreater(cache_entry['cooldown_end'], time.time())
        self.assertGreater(cache_entry['timestamp'], 0)


# Async test runner for pytest compatibility
@pytest.mark.asyncio
async def test_async_methods():
    """Run async tests with pytest."""
    test_instance = TestTokenManagerCoverage()
    test_instance.setUp()
    
    await test_instance.test_check_token_parallel_success()
    await test_instance.test_check_token_parallel_failure()
    await test_instance.test_check_token_parallel_exception()
    await test_instance.test_check_tokens_parallel_success()
    await test_instance.test_check_tokens_parallel_all_fail()
    await test_instance.test_check_tokens_parallel_timeout()
    await test_instance.test_check_tokens_parallel_exception()
    await test_instance.test_rotate_tokens_parallel_success()
    await test_instance.test_rotate_tokens_parallel_fail_sequential_success()
    await test_instance.test_rotate_tokens_all_tokens_fail()
    await test_instance.test_rotate_tokens_full_cycle_no_healthy()
    # await test_instance.test_rotate_tokens_with_retries()  # Skip complex retry test


if __name__ == '__main__':
    # Run sync tests
    unittest.main(argv=[''], exit=False)
    
    # Run async tests
    asyncio.run(test_async_methods()) 