"""
Platform Posting Service
Handles platform-specific posting logic (LinkedIn, X/Twitter)
Extracted from simple_posting_orchestrator.py for better separation of concerns
"""

import os
import sys
import time
import logging
import subprocess
from typing import Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass


class PostingStatus(Enum):
    """Posting status codes"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    ALREADY_POSTED = "already_posted"
    BROWSER_ERROR = "browser_error"
    TIMEOUT = "timeout"


@dataclass
class PostingResult:
    """Result of a posting attempt"""
    platform: str
    status: PostingStatus
    message: str
    error: Optional[str] = None
    duration: float = 0.0


class PlatformPostingService:
    """Handles platform-specific posting to LinkedIn and X/Twitter"""

    def __init__(self, browser_timeout: int = 120, posting_delay: int = 15):
        """
        Initialize posting service

        Args:
            browser_timeout: Timeout for browser operations in seconds
            posting_delay: Delay between posts in seconds to avoid rate limiting
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.browser_timeout = browser_timeout
        self.posting_delay = posting_delay
        self.last_post_time = 0

        # Poster script paths
        self.linkedin_poster = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'linkedin_agent', 'src', 'anti_detection_poster.py'
        )

        self.x_poster = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'x_twitter', 'src', 'x_anti_detection_poster.py'
        )

        # Browser configuration
        self.browser_config = {
            'linkedin': 'chrome',  # LinkedIn uses Chrome for all accounts
            'x_foundups': 'edge',  # FoundUps X account uses Edge
            'x_geozei': 'chrome'   # GeozeAi/Move2Japan X account uses Chrome
        }

    def post_to_linkedin(self, title: str, url: str, linkedin_page: str) -> PostingResult:
        """
        Post to LinkedIn using anti-detection poster

        Args:
            title: Stream title
            url: Stream URL
            linkedin_page: LinkedIn page ID

        Returns:
            PostingResult with status and details
        """
        start_time = time.time()

        try:
            # Channel-to-LinkedIn page validation
            page_mapping = {
                "104834798": "GeoZai (Move2Japan)",  # Corrected GeoZai page ID
                "165749317": "UnDaoDu",
                "1263645": "FoundUps"
            }

            # Verify we're posting to a valid page
            if linkedin_page not in page_mapping:
                self.logger.error(f"❌ Invalid LinkedIn page ID: {linkedin_page}")
                return PostingResult(
                    platform="linkedin",
                    status=PostingStatus.FAILED,
                    message="Invalid LinkedIn page ID",
                    error=f"Unknown page ID: {linkedin_page}",
                    duration=time.time() - start_time
                )

            # Log which page we're posting to for verification
            page_name = page_mapping[linkedin_page]
            self.logger.info(f"✅ Verified LinkedIn page: {page_name} (ID: {linkedin_page})")

            # Double-check channel mapping from title
            if "Move2Japan" in title and linkedin_page != "104834798":
                self.logger.warning(f"⚠️ MISMATCH: Move2Japan stream should post to GeoZai (104834798), but got {linkedin_page}")
            elif "UnDaoDu" in title and linkedin_page != "165749317":
                self.logger.warning(f"⚠️ MISMATCH: UnDaoDu stream should post to UnDaoDu (165749317), but got {linkedin_page}")
            elif "FoundUps" in title and linkedin_page != "1263645":
                self.logger.warning(f"⚠️ MISMATCH: FoundUps stream should post to FoundUps (1263645), but got {linkedin_page}")

            # Apply posting delay to slow down requests
            current_time = time.time()
            time_since_last = current_time - self.last_post_time
            if time_since_last < self.posting_delay:
                delay_needed = self.posting_delay - time_since_last
                self.logger.info(f"⏳ LinkedIn: Applying posting delay: {delay_needed:.1f}s to avoid rate limiting")
                time.sleep(delay_needed)

            self.logger.info("="*60)
            self.logger.info("📘 LINKEDIN POSTING STARTED")
            self.logger.info(f"📹 Title: {title}")
            self.logger.info(f"🔗 URL: {url}")
            self.logger.info(f"📄 Page: {page_name} ({linkedin_page})")

            # Check if poster script exists
            if not os.path.exists(self.linkedin_poster):
                error_msg = f"LinkedIn poster not found: {self.linkedin_poster}"
                self.logger.error(f"❌ {error_msg}")
                return PostingResult(
                    platform="linkedin",
                    status=PostingStatus.FAILED,
                    message="Poster script not found",
                    error=error_msg,
                    duration=time.time() - start_time
                )

            # Prepare post content
            post_content = self._format_linkedin_post(title, url)

            # Run anti-detection poster
            self.logger.info(f"🚀 Launching anti-detection poster for {page_name} (browser: {self.browser_config['linkedin']})")
            self.logger.info(f"📌 Posting to LinkedIn page ID: {linkedin_page}")

            try:
                result = subprocess.run(
                    [sys.executable, self.linkedin_poster, linkedin_page, post_content],
                    capture_output=True,
                    text=True,
                    timeout=self.browser_timeout
                )

                if result.returncode == 0:
                    self.logger.info("✅ LinkedIn post successful!")
                    self.logger.info(f"📊 Duration: {time.time() - start_time:.2f}s")
                    return PostingResult(
                        platform="linkedin",
                        status=PostingStatus.SUCCESS,
                        message="Posted successfully",
                        duration=time.time() - start_time
                    )
                else:
                    error_msg = result.stderr or "Unknown error"
                    self.logger.error(f"❌ LinkedIn posting failed: {error_msg}")
                    return PostingResult(
                        platform="linkedin",
                        status=PostingStatus.FAILED,
                        message="Posting failed",
                        error=error_msg,
                        duration=time.time() - start_time
                    )

            except subprocess.TimeoutExpired:
                self.logger.error(f"⏱️ LinkedIn posting timed out after {self.browser_timeout}s")
                return PostingResult(
                    platform="linkedin",
                    status=PostingStatus.TIMEOUT,
                    message="Browser operation timed out",
                    error=f"Timeout after {self.browser_timeout}s",
                    duration=time.time() - start_time
                )

        except Exception as e:
            self.logger.error(f"❌ LinkedIn posting error: {str(e)}")
            return PostingResult(
                platform="linkedin",
                status=PostingStatus.FAILED,
                message="Unexpected error",
                error=str(e),
                duration=time.time() - start_time
            )

    def post_to_x(self, title: str, url: str, x_account: str) -> PostingResult:
        """
        Post to X/Twitter using anti-detection poster

        Args:
            title: Stream title
            url: Stream URL
            x_account: X account name (Move2Japan or FoundUps)

        Returns:
            PostingResult with status and details
        """
        start_time = time.time()

        try:
            # Apply posting delay to slow down requests
            current_time = time.time()
            time_since_last = current_time - self.last_post_time
            if time_since_last < self.posting_delay:
                delay_needed = self.posting_delay - time_since_last
                self.logger.info(f"⏳ X/Twitter: Applying posting delay: {delay_needed:.1f}s to avoid rate limiting")
                time.sleep(delay_needed)

            self.logger.info("="*60)
            self.logger.info("🐦 X/TWITTER POSTING STARTED")
            self.logger.info(f"📹 Title: {title}")
            self.logger.info(f"🔗 URL: {url}")
            self.logger.info(f"👤 Account: @{x_account}")

            # Check if poster script exists
            if not os.path.exists(self.x_poster):
                error_msg = f"X poster not found: {self.x_poster}"
                self.logger.error(f"❌ {error_msg}")
                return PostingResult(
                    platform="x_twitter",
                    status=PostingStatus.FAILED,
                    message="Poster script not found",
                    error=error_msg,
                    duration=time.time() - start_time
                )

            # Determine browser based on account
            browser = self._get_x_browser(x_account)
            self.logger.info(f"🌐 Using {browser} browser for @{x_account}")

            # Prepare post content
            post_content = self._format_x_post(title, url)

            # Run anti-detection poster
            self.logger.info(f"🚀 Launching anti-detection poster (browser: {browser})")

            try:
                # Pass browser as environment variable
                env = os.environ.copy()
                env['X_BROWSER'] = browser
                env['X_ACCOUNT'] = x_account

                result = subprocess.run(
                    [sys.executable, self.x_poster, x_account, post_content],
                    capture_output=True,
                    text=True,
                    timeout=self.browser_timeout,
                    env=env
                )

                if result.returncode == 0:
                    self.logger.info("✅ X/Twitter post successful!")
                    self.logger.info(f"📊 Duration: {time.time() - start_time:.2f}s")
                    return PostingResult(
                        platform="x_twitter",
                        status=PostingStatus.SUCCESS,
                        message="Posted successfully",
                        duration=time.time() - start_time
                    )
                else:
                    error_msg = result.stderr or "Unknown error"
                    self.logger.error(f"❌ X posting failed: {error_msg}")
                    return PostingResult(
                        platform="x_twitter",
                        status=PostingStatus.FAILED,
                        message="Posting failed",
                        error=error_msg,
                        duration=time.time() - start_time
                    )

            except subprocess.TimeoutExpired:
                self.logger.error(f"⏱️ X posting timed out after {self.browser_timeout}s")
                return PostingResult(
                    platform="x_twitter",
                    status=PostingStatus.TIMEOUT,
                    message="Browser operation timed out",
                    error=f"Timeout after {self.browser_timeout}s",
                    duration=time.time() - start_time
                )

        except Exception as e:
            self.logger.error(f"❌ X posting error: {str(e)}")
            return PostingResult(
                platform="x_twitter",
                status=PostingStatus.FAILED,
                message="Unexpected error",
                error=str(e),
                duration=time.time() - start_time
            )

    def post_to_both_platforms(
        self,
        title: str,
        url: str,
        linkedin_page: str,
        x_account: str
    ) -> Tuple[PostingResult, PostingResult]:
        """
        Post to both LinkedIn and X/Twitter

        Args:
            title: Stream title
            url: Stream URL
            linkedin_page: LinkedIn page ID
            x_account: X account name

        Returns:
            Tuple of (LinkedIn result, X result)
        """
        self.logger.info("="*60)
        self.logger.info("🚀 DUAL PLATFORM POSTING INITIATED")
        self.logger.info("="*60)

        # Post to LinkedIn first
        linkedin_result = self.post_to_linkedin(title, url, linkedin_page)

        # Small delay between platforms
        time.sleep(2)

        # Post to X/Twitter
        x_result = self.post_to_x(title, url, x_account)

        # Summary
        self.logger.info("="*60)
        self.logger.info("📊 POSTING SUMMARY")
        self.logger.info(f"📘 LinkedIn: {linkedin_result.status.value} ({linkedin_result.duration:.2f}s)")
        self.logger.info(f"🐦 X/Twitter: {x_result.status.value} ({x_result.duration:.2f}s)")
        self.logger.info("="*60)

        return linkedin_result, x_result

    def _get_x_browser(self, x_account: str) -> str:
        """
        Determine which browser to use for X account

        Args:
            x_account: X account name

        Returns:
            Browser name (chrome or edge)
        """
        # FoundUps uses Edge, all others use Chrome
        if x_account.lower() == "foundups":
            return self.browser_config['x_foundups']
        else:
            return self.browser_config['x_geozei']

    def _format_linkedin_post(self, title: str, url: str) -> str:
        """
        Format content for LinkedIn post

        Args:
            title: Stream title
            url: Stream URL

        Returns:
            Formatted post content
        """
        # LinkedIn allows up to 3000 characters
        content = f"🔴 LIVE NOW: {title}\n\n"
        content += f"Join the conversation: {url}\n\n"
        content += "#LiveStream #Tech #Coding #AI #Innovation"

        # Truncate if too long
        if len(content) > 2900:
            content = content[:2900] + "..."

        return content

    def _format_x_post(self, title: str, url: str) -> str:
        """
        Format content for X/Twitter post

        Args:
            title: Stream title
            url: Stream URL

        Returns:
            Formatted post content
        """
        # X has 280 character limit
        content = f"🔴 LIVE: {title}\n{url}"

        # Add hashtags if room
        hashtags = " #live #coding #AI"
        if len(content) + len(hashtags) <= 280:
            content += hashtags

        # Truncate if too long
        if len(content) > 280:
            # Reserve space for URL (23 chars) and ellipsis
            max_title_len = 280 - 23 - 10  # URL + "LIVE: " + "..."
            truncated_title = title[:max_title_len] + "..."
            content = f"🔴 LIVE: {truncated_title}\n{url}"

        return content

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate posting service configuration

        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }

        # Check poster scripts
        if not os.path.exists(self.linkedin_poster):
            results['errors'].append(f"LinkedIn poster not found: {self.linkedin_poster}")
            results['valid'] = False
        else:
            results['info']['linkedin_poster'] = "Found"

        if not os.path.exists(self.x_poster):
            results['errors'].append(f"X poster not found: {self.x_poster}")
            results['valid'] = False
        else:
            results['info']['x_poster'] = "Found"

        # Check browser availability (optional)
        try:
            # Try to check if Chrome is available
            result = subprocess.run(['where', 'chrome'], capture_output=True, text=True)
            if result.returncode == 0:
                results['info']['chrome'] = "Available"
            else:
                results['warnings'].append("Chrome browser not found in PATH")
        except:
            pass

        try:
            # Try to check if Edge is available
            result = subprocess.run(['where', 'msedge'], capture_output=True, text=True)
            if result.returncode == 0:
                results['info']['edge'] = "Available"
            else:
                results['warnings'].append("Edge browser not found in PATH")
        except:
            pass

        results['info']['browser_config'] = self.browser_config
        results['info']['timeout'] = f"{self.browser_timeout}s"

        return results