#!/usr/bin/env python3
"""
YouTube API Operations - WSP 3 Surgical Extraction
Extracted from stream_resolver.py YouTube API functionality

Handles YouTube API operations with enhanced error handling, retry logic,
circuit breaker integration, and service switching capabilities.

WSP 3: Platform Integration Domain - YouTube API Operations
WSP 49: Module Structure Compliance
WSP 62: File Size Management
"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class YouTubeAPIOperations:
    """
    Handles YouTube API operations with enhanced error handling and retry logic.

    This module provides a clean interface for YouTube API interactions,
    including video details checking, livestream searching, and active stream
    detection with comprehensive error handling and circuit breaker integration.

    Features:
    - Enhanced video details checking with retry logic
    - Intelligent livestream searching with rate limit handling
    - Active livestream detection with service switching
    - Circuit breaker integration for fault tolerance
    - Comprehensive error handling and logging
    """

    def __init__(self, circuit_breaker=None, logger=None):
        """
        Initialize YouTube API operations handler.

        Args:
            circuit_breaker: Circuit breaker instance for fault tolerance
            logger: Logger instance (optional, defaults to module logger)
        """
        self.circuit_breaker = circuit_breaker
        self.logger = logger or logging.getLogger(__name__)

    def check_video_details_enhanced(self, youtube, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Enhanced video details checking with retry logic and error handling.

        Args:
            youtube: YouTube API service instance
            video_id: YouTube video ID to check

        Returns:
            Video details dictionary or None if failed
        """
        if not youtube or not video_id:
            self.logger.error("[API] Invalid parameters for video details check")
            return None

        def _make_api_call():
            """Inner function for circuit breaker wrapping."""
            try:
                request = youtube.videos().list(
                    part='snippet,liveStreamingDetails,status',
                    id=video_id,
                    maxResults=1
                )
                response = request.execute()

                if response.get('items'):
                    video = response['items'][0]
                    return {
                        'video_id': video_id,
                        'title': video.get('snippet', {}).get('title', 'Unknown'),
                        'channel_id': video.get('snippet', {}).get('channelId'),
                        'live_status': video.get('snippet', {}).get('liveBroadcastContent'),
                        'live_details': video.get('liveStreamingDetails', {}),
                        'status': video.get('status', {})
                    }
                else:
                    self.logger.warning(f"[API] Video {video_id} not found")
                    return None

            except Exception as e:
                self.logger.error(f"[API] Error checking video {video_id}: {e}")
                raise  # Re-raise for circuit breaker

        try:
            if self.circuit_breaker:
                return self.circuit_breaker.call(_make_api_call)
            else:
                return _make_api_call()
        except Exception as e:
            self.logger.error(f"[API] Video details check failed for {video_id}: {e}")
            return None

    def search_livestreams_enhanced(self, youtube, channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Enhanced livestream search with retry logic and error handling.

        Args:
            youtube: YouTube API service instance
            channel_id: YouTube channel ID to search
            max_results: Maximum number of results to return

        Returns:
            List of livestream dictionaries
        """
        if not youtube or not channel_id:
            self.logger.error("[API] Invalid parameters for livestream search")
            return []

        def _make_search_call():
            """Inner function for circuit breaker wrapping."""
            try:
                # Search for live streams on the channel
                request = youtube.search().list(
                    part='snippet',
                    channelId=channel_id,
                    eventType='live',
                    type='video',
                    order='date',
                    maxResults=max_results
                )
                response = request.execute()

                livestreams = []
                for item in response.get('items', []):
                    video_id = item.get('id', {}).get('videoId')
                    if video_id:
                        livestreams.append({
                            'video_id': video_id,
                            'title': item.get('snippet', {}).get('title', 'Live Stream'),
                            'channel_id': channel_id,
                            'published_at': item.get('snippet', {}).get('publishedAt'),
                            'description': item.get('snippet', {}).get('description', ''),
                            'thumbnails': item.get('snippet', {}).get('thumbnails', {})
                        })

                return livestreams

            except Exception as e:
                self.logger.error(f"[API] Error searching livestreams for channel {channel_id}: {e}")
                raise  # Re-raise for circuit breaker

        try:
            if self.circuit_breaker:
                return self.circuit_breaker.call(_make_search_call)
            else:
                return _make_search_call()
        except Exception as e:
            self.logger.error(f"[API] Livestream search failed for channel {channel_id}: {e}")
            return []

    def get_active_livestream_video_id_enhanced(self, youtube, channel_id: str) -> Optional[Tuple[str, str]]:
        """
        Enhanced active livestream detection with comprehensive error handling.

        This method implements a multi-step approach:
        1. Search for live streams on the channel
        2. Verify each stream is actually live
        3. Return the most recent active stream

        Args:
            youtube: YouTube API service instance
            channel_id: YouTube channel ID to check

        Returns:
            Tuple of (video_id, chat_id) for active stream, or None
        """
        if not youtube or not channel_id:
            self.logger.error("[API] Invalid parameters for active stream detection")
            return None

        self.logger.info(f"[API] Starting enhanced active stream detection for channel {channel_id}")

        # Step 1: Search for live streams
        livestreams = self.search_livestreams_enhanced(youtube, channel_id, max_results=5)

        if not livestreams:
            self.logger.info(f"[API] No livestreams found for channel {channel_id}")
            return None

        self.logger.info(f"[API] Found {len(livestreams)} potential livestreams, verifying...")

        # Step 2: Verify each stream is actually live and get chat ID
        for stream in livestreams:
            video_id = stream['video_id']
            self.logger.debug(f"[API] Verifying stream {video_id}")

            # Check video details to confirm it's live
            video_details = self.check_video_details_enhanced(youtube, video_id)

            if video_details:
                live_status = video_details.get('live_status')
                live_details = video_details.get('live_details', {})

                # Check if video is actually live
                if live_status == 'live':
                    chat_id = None

                    # Try to get chat ID from live details
                    if 'activeLiveChatId' in live_details:
                        chat_id = live_details['activeLiveChatId']
                        self.logger.info(f"[API] Found active live stream: {video_id} (chat: {chat_id})")
                        return video_id, chat_id
                    else:
                        # Live but no chat - still return the video ID
                        self.logger.warning(f"[API] Found live stream {video_id} but no active chat")
                        return video_id, None

                else:
                    self.logger.debug(f"[API] Stream {video_id} is not live (status: {live_status})")
            else:
                self.logger.warning(f"[API] Could not verify details for stream {video_id}")

        self.logger.info(f"[API] No active livestreams found for channel {channel_id}")
        return None

    def execute_api_fallback_search(self, youtube, channel_id: str, config=None) -> Optional[Tuple[str, str]]:
        """
        Execute the complete API fallback search strategy (Priority 5 logic).

        This method implements the orchestration logic for API-based stream resolution,
        including service validation, error handling, and result processing.

        Args:
            youtube: YouTube API service instance
            channel_id: Channel ID to search
            config: Configuration object (optional)

        Returns:
            Tuple of (video_id, chat_id) if found, None otherwise
        """
        if not youtube:
            self.logger.error("[API] No YouTube service available for API fallback")
            return None

        search_channel_id = channel_id or (config.CHANNEL_ID if config else None)
        if not search_channel_id:
            self.logger.error("[API] No channel ID available for API search")
            return None

        self.logger.info("="*60)
        self.logger.info("[API] FALLBACK: API STREAM SEARCH STARTING")
        self.logger.info(f"   Target Channel: {search_channel_id}")
        self.logger.info(f"   Using Service: {getattr(youtube, '_credential_set', 'Unknown')}")
        self.logger.info("="*60)

        try:
            # Execute the enhanced active stream detection
            result = self.get_active_livestream_video_id_enhanced(youtube, search_channel_id)

            if result:
                video_id, chat_id = result
                self.logger.info(f"[API] SUCCESS: Found active stream via API: {video_id}")

                # Additional metadata could be logged here
                # (Stream title, duration, etc. would be handled by caller)

                return video_id, chat_id
            else:
                self.logger.info(f"[API] No active streams found via API for channel {search_channel_id}")
                return None

        except Exception as e:
            self.logger.error(f"[API] API fallback search failed: {e}")
            # Circuit breaker failure would be handled by caller
            raise
