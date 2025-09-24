"""
Refactored Posting Orchestrator
Clean, modular orchestrator using extracted core components
Replaces the monolithic simple_posting_orchestrator.py
"""

import os
import logging
import threading
from typing import Dict, Optional, Any

# Import all core components
from .core import (
    DuplicatePreventionManager,
    LiveStatusVerifier,
    ChannelConfigurationManager,
    PlatformPostingService,
    LinkedInPage,
    XAccount,
    PostingStatus
)


class RefactoredPostingOrchestrator:
    """
    Clean orchestrator that coordinates all social media posting activities
    Uses modular core components for better maintainability
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator with core components

        Args:
            config: Optional configuration dictionary
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or {}

        # Initialize core components
        self.duplicate_manager = DuplicatePreventionManager()
        self.status_verifier = LiveStatusVerifier()
        self.channel_config = ChannelConfigurationManager()
        self.posting_service = PlatformPostingService(
            browser_timeout=self.config.get('browser_timeout', 120)
        )

        # State
        self.is_posting = False
        self.last_posted_video = None

        self.logger.info("✅ RefactoredPostingOrchestrator initialized with core components")

    def handle_stream_detected(
        self,
        video_id: str,
        title: str,
        url: str,
        channel_name: str
    ) -> Dict[str, Any]:
        """
        Main entry point for stream detection events
        Coordinates all posting activities

        Args:
            video_id: YouTube video ID
            title: Stream title
            url: Stream URL
            channel_name: Channel name/handle

        Returns:
            Results dictionary with posting status
        """
        self.logger.info("="*80)
        self.logger.info("🎬 STREAM DETECTION EVENT RECEIVED")
        self.logger.info(f"📹 Video: {video_id}")
        self.logger.info(f"📺 Channel: {channel_name}")
        self.logger.info(f"📝 Title: {title}")
        self.logger.info(f"🔗 URL: {url}")
        self.logger.info("="*80)

        results = {
            'video_id': video_id,
            'posted': False,
            'platforms': {},
            'errors': []
        }

        # Step 1: Check if already posting
        if self.is_posting:
            self.logger.warning("⚠️ Already posting, skipping duplicate request")
            results['errors'].append("Already processing another posting request")
            return results

        # Step 2: Check duplicate
        duplicate_check = self.duplicate_manager.check_if_already_posted(video_id)
        if duplicate_check['already_posted']:
            self.logger.info("🔁 Video already posted, skipping")
            results['platforms'] = {
                platform: 'already_posted'
                for platform in duplicate_check.get('platforms_posted', [])
            }
            return results

        # Step 3: Verify live status
        if not self.status_verifier.verify_live_status(video_id):
            self.logger.warning("⚠️ Stream not verified as live, skipping")
            results['errors'].append("Stream not verified as live")
            return results

        # Step 4: Get channel configuration
        channel_config = self.channel_config.get_channel_config(channel_name)
        if not channel_config:
            self.logger.error(f"❌ No configuration found for channel: {channel_name}")
            results['errors'].append(f"No configuration for channel: {channel_name}")
            return results

        if not channel_config.get('enabled', True):
            self.logger.info(f"🔕 Channel {channel_name} is disabled, skipping")
            results['errors'].append(f"Channel {channel_name} is disabled")
            return results

        # Step 5: Post to platforms in background
        self.logger.info("🚀 Starting background posting thread")
        posting_thread = threading.Thread(
            target=self._post_to_platforms_background,
            args=(video_id, title, url, channel_config, results),
            daemon=True
        )
        posting_thread.start()

        # Return immediately (posting happens in background)
        return results

    def _post_to_platforms_background(
        self,
        video_id: str,
        title: str,
        url: str,
        channel_config: Dict[str, Any],
        results: Dict[str, Any]
    ):
        """
        Background thread for posting to platforms

        Args:
            video_id: YouTube video ID
            title: Stream title
            url: Stream URL
            channel_config: Channel configuration
            results: Results dictionary to update
        """
        try:
            self.is_posting = True

            # Get platform accounts
            linkedin_page = channel_config.get('linkedin_page')
            x_account = channel_config.get('x_account')

            if not linkedin_page and not x_account:
                self.logger.error("❌ No platform accounts configured")
                results['errors'].append("No platform accounts configured")
                return

            # Post to both platforms
            if linkedin_page and x_account:
                self.logger.info("📢 Posting to both LinkedIn and X/Twitter")

                linkedin_result, x_result = self.posting_service.post_to_both_platforms(
                    title=title,
                    url=url,
                    linkedin_page=linkedin_page,
                    x_account=x_account
                )

                # Update results
                results['platforms']['linkedin'] = linkedin_result.status.value
                results['platforms']['x_twitter'] = x_result.status.value

                # Mark as posted if successful
                platforms_posted = []
                if linkedin_result.status == PostingStatus.SUCCESS:
                    platforms_posted.append('linkedin')
                if x_result.status == PostingStatus.SUCCESS:
                    platforms_posted.append('x_twitter')

                if platforms_posted:
                    self.duplicate_manager.mark_as_posted(
                        video_id=video_id,
                        title=title,
                        url=url,
                        platforms=platforms_posted
                    )
                    results['posted'] = True
                    self.last_posted_video = video_id

            # Post to LinkedIn only
            elif linkedin_page:
                self.logger.info("📘 Posting to LinkedIn only")

                linkedin_result = self.posting_service.post_to_linkedin(
                    title=title,
                    url=url,
                    linkedin_page=linkedin_page
                )

                results['platforms']['linkedin'] = linkedin_result.status.value

                if linkedin_result.status == PostingStatus.SUCCESS:
                    self.duplicate_manager.mark_as_posted(
                        video_id=video_id,
                        title=title,
                        url=url,
                        platforms=['linkedin']
                    )
                    results['posted'] = True
                    self.last_posted_video = video_id

            # Post to X only
            elif x_account:
                self.logger.info("🐦 Posting to X/Twitter only")

                x_result = self.posting_service.post_to_x(
                    title=title,
                    url=url,
                    x_account=x_account
                )

                results['platforms']['x_twitter'] = x_result.status.value

                if x_result.status == PostingStatus.SUCCESS:
                    self.duplicate_manager.mark_as_posted(
                        video_id=video_id,
                        title=title,
                        url=url,
                        platforms=['x_twitter']
                    )
                    results['posted'] = True
                    self.last_posted_video = video_id

            # Log final results
            self.logger.info("="*60)
            self.logger.info("📊 POSTING COMPLETE")
            self.logger.info(f"✅ Success: {results['posted']}")
            self.logger.info(f"📱 Platforms: {results['platforms']}")
            self.logger.info("="*60)

        except Exception as e:
            self.logger.error(f"❌ Background posting error: {str(e)}")
            results['errors'].append(str(e))
        finally:
            self.is_posting = False

    def get_posting_stats(self) -> Dict[str, Any]:
        """
        Get posting statistics

        Returns:
            Statistics dictionary
        """
        stats = self.duplicate_manager.get_posting_stats()
        stats['is_posting'] = self.is_posting
        stats['last_posted_video'] = self.last_posted_video
        stats['channel_config'] = self.channel_config.get_configuration_summary()

        return stats

    def clear_live_cache(self, video_id: Optional[str] = None):
        """
        Clear live status cache

        Args:
            video_id: Optional specific video ID to clear
        """
        if video_id:
            self.status_verifier.clear_cache(video_id)
        else:
            self.status_verifier.clear_cache()

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate all component configurations

        Returns:
            Validation results
        """
        validation = {
            'valid': True,
            'components': {}
        }

        # Validate posting service
        posting_validation = self.posting_service.validate_configuration()
        validation['components']['posting_service'] = posting_validation
        if not posting_validation['valid']:
            validation['valid'] = False

        # Check channel configurations
        channels = self.channel_config.get_enabled_channels()
        validation['components']['channels'] = {
            'enabled': channels,
            'count': len(channels)
        }
        if not channels:
            validation['valid'] = False

        return validation


# Singleton instance
_orchestrator_instance = None


def get_orchestrator() -> RefactoredPostingOrchestrator:
    """
    Get singleton orchestrator instance

    Returns:
        RefactoredPostingOrchestrator instance
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = RefactoredPostingOrchestrator()
    return _orchestrator_instance


# Public API for backward compatibility
def handle_stream_detected(video_id: str, title: str, url: str, channel_name: str) -> Dict[str, Any]:
    """
    Public API for stream detection events
    Maintains backward compatibility with existing code

    Args:
        video_id: YouTube video ID
        title: Stream title
        url: Stream URL
        channel_name: Channel name/handle

    Returns:
        Results dictionary
    """
    orchestrator = get_orchestrator()
    return orchestrator.handle_stream_detected(video_id, title, url, channel_name)