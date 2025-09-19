#!/usr/bin/env python3
"""
Test Live Verification System - WSP Compliant
Tests the live verification functionality to ensure social media posting only occurs when streams are actually live.

WSP Compliance:
- WSP 3: Enterprise Domain Architecture (communication domain)
- WSP 80: Cube-Level DAE Architecture
- WSP 50: Pre-Action Verification Protocol
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import the DAE and verification methods
from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE


class TestLiveVerification:
    """Test suite for live verification system"""

    @pytest.fixture
    def mock_service(self):
        """Mock YouTube service for testing"""
        service = Mock()

        # Mock videos().list() response
        mock_response = {
            "items": [{
                "liveStreamingDetails": {
                    "actualStartTime": "2024-01-01T12:00:00Z",
                    "concurrentViewers": 150
                },
                "status": {
                    "privacyStatus": "public"
                },
                "snippet": {
                    "title": "Test Live Stream"
                }
            }]
        }

        service.videos.return_value.list.return_value.execute.return_value = mock_response
        return service

    @pytest.fixture
    def dae_instance(self, mock_service):
        """Create DAE instance with mocked service"""
        dae = AutoModeratorDAE()
        dae.service = mock_service
        return dae

    @pytest.mark.asyncio
    async def test_verify_live_stream_success(self, dae_instance):
        """Test successful live stream verification"""
        video_id = "test_video_123"

        result = await dae_instance._verify_stream_is_actually_live(video_id)

        assert result is True
        # Verify the service was called correctly
        dae_instance.service.videos.assert_called_once()
        dae_instance.service.videos().list.assert_called_once_with(
            part="liveStreamingDetails,snippet,status",
            id=video_id
        )

    @pytest.mark.asyncio
    async def test_verify_stream_not_found(self, dae_instance):
        """Test verification when video is not found"""
        # Mock empty response (video not found)
        dae_instance.service.videos.return_value.list.return_value.execute.return_value = {"items": []}

        video_id = "nonexistent_video"
        result = await dae_instance._verify_stream_is_actually_live(video_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_verify_stream_not_actually_live_no_start_time(self, dae_instance):
        """Test verification when stream has no actual start time"""
        # Mock response with no actualStartTime
        mock_response = {
            "items": [{
                "liveStreamingDetails": {
                    "scheduledStartTime": "2024-01-01T12:00:00Z",
                    # No actualStartTime - stream not actually live
                },
                "status": {"privacyStatus": "public"},
                "snippet": {"title": "Scheduled Stream"}
            }]
        }
        dae_instance.service.videos.return_value.list.return_value.execute.return_value = mock_response

        video_id = "scheduled_stream"
        result = await dae_instance._verify_stream_is_actually_live(video_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_verify_stream_ended(self, dae_instance):
        """Test verification when stream has ended"""
        # Mock response with actualEndTime (stream ended)
        mock_response = {
            "items": [{
                "liveStreamingDetails": {
                    "actualStartTime": "2024-01-01T12:00:00Z",
                    "actualEndTime": "2024-01-01T13:00:00Z",  # Stream ended
                    "concurrentViewers": 0
                },
                "status": {"privacyStatus": "public"},
                "snippet": {"title": "Ended Stream"}
            }]
        }
        dae_instance.service.videos.return_value.list.return_value.execute.return_value = mock_response

        video_id = "ended_stream"
        result = await dae_instance._verify_stream_is_actually_live(video_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_verify_private_stream(self, dae_instance):
        """Test verification when stream is private"""
        # Mock response with private status
        mock_response = {
            "items": [{
                "liveStreamingDetails": {
                    "actualStartTime": "2024-01-01T12:00:00Z",
                    "concurrentViewers": 50
                },
                "status": {"privacyStatus": "private"},  # Private stream
                "snippet": {"title": "Private Stream"}
            }]
        }
        dae_instance.service.videos.return_value.list.return_value.execute.return_value = mock_response

        video_id = "private_stream"
        result = await dae_instance._verify_stream_is_actually_live(video_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_verify_api_error(self, dae_instance):
        """Test verification when API call fails"""
        # Mock API error
        dae_instance.service.videos.return_value.list.return_value.execute.side_effect = Exception("API Error")

        video_id = "error_video"
        result = await dae_instance._verify_stream_is_actually_live(video_id)

        # Should return False on error (safety first)
        assert result is False

    @pytest.mark.asyncio
    async def test_social_media_verification_integration(self):
        """Test the social media orchestrator live verification"""
        from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import SimplePostingOrchestrator

        orchestrator = SimplePostingOrchestrator()

        # Test manual verification method
        result = await orchestrator.verify_live_status_manually()

        # This should work even without actual API calls (will fail verification but not crash)
        assert isinstance(result, bool)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
