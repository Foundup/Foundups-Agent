#!/usr/bin/env python3
"""
Test Social Media Live Verification - WSP Compliant
Tests the social media orchestrator's live verification before posting.

WSP Compliance:
- WSP 3: Enterprise Domain Architecture (platform_integration domain)
- WSP 80: Cube-Level DAE Architecture
- WSP 50: Pre-Action Verification Protocol
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import (
    SimplePostingOrchestrator,
    Platform,
    PostResponse,
    PostResult
)


class TestSocialMediaLiveVerification:
    """Test suite for social media live verification"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return SimplePostingOrchestrator()

    @pytest.mark.asyncio
    async def test_verify_live_status_before_posting_not_live(self, orchestrator):
        """Test that posting is blocked when not live"""
        # The verification should fail when no live streams are found
        is_live = await orchestrator._verify_live_status_before_posting()

        # Should return False when no live streams are detected
        assert is_live is False

    @pytest.mark.asyncio
    async def test_post_stream_notification_blocked_when_not_live(self, orchestrator):
        """Test that post_stream_notification returns failure when not live"""
        response = await orchestrator.post_stream_notification(
            stream_title="Test Stream",
            stream_url="https://youtube.com/watch?v=test",
            platforms=[Platform.LINKEDIN, Platform.X_TWITTER]
        )

        # Should return failure response
        assert isinstance(response, PostResponse)
        assert response.success_count == 0
        assert response.failure_count == 2  # Both platforms should fail
        assert len(response.results) == 2

        # Check that results indicate live verification failure
        for result in response.results:
            assert result.success is False
            assert "Live verification failed" in result.message

    @pytest.mark.asyncio
    async def test_manual_verification_method(self, orchestrator):
        """Test the manual verification method"""
        result = await orchestrator.verify_live_status_manually()

        # Should return boolean
        assert isinstance(result, bool)

        # Should be False when no live streams (normal case)
        assert result is False

    @pytest.mark.asyncio
    async def test_post_response_structure(self, orchestrator):
        """Test that PostResponse has correct structure when verification fails"""
        response = await orchestrator.post_stream_notification(
            stream_title="Test Stream",
            stream_url="https://youtube.com/watch?v=test"
        )

        # Verify response structure
        assert hasattr(response, 'request_id')
        assert hasattr(response, 'results')
        assert hasattr(response, 'success_count')
        assert hasattr(response, 'failure_count')

        # Should start with "stream_post_"
        assert response.request_id.startswith("stream_post_")

        # All results should be failures
        assert all(not result.success for result in response.results)


class TestPlatformIntegration:
    """Test platform-specific integration"""

    @pytest.mark.asyncio
    async def test_platform_enum_values(self):
        """Test that platform enums have correct values"""
        assert Platform.LINKEDIN.value == "linkedin"
        assert Platform.X_TWITTER.value == "x_twitter"

    @pytest.mark.asyncio
    async def test_post_result_creation(self):
        """Test PostResult object creation"""
        result = PostResult(
            success=True,
            platform=Platform.LINKEDIN,
            message="Test message",
            timestamp=datetime.now()
        )

        assert result.success is True
        assert result.platform == Platform.LINKEDIN
        assert result.message == "Test message"
        assert isinstance(result.timestamp, datetime)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
