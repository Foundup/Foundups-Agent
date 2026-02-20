#!/usr/bin/env python3
"""
Unified LinkedIn Interface - WSP 3 Compliant Centralized LinkedIn Posting
Consolidates all LinkedIn posting through single interface to prevent duplicates

This module replaces direct usage of AntiDetectionLinkedIn across the codebase
All systems must use this interface instead of importing LinkedIn agent directly

WSP Compliance:
- WSP 3: Functional distribution through orchestrator
- WSP 17: Reusable pattern for platform posting
- WSP 84: Consolidates existing LinkedIn functionality
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import os
import json
import asyncio
import threading
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")

# Global singleton to prevent multiple browser instances
_GLOBAL_LINKEDIN_POSTER = None
_POSTER_LOCK = threading.Lock()

class LinkedInContentType(Enum):
    """Types of content that can be posted to LinkedIn"""
    STREAM_NOTIFICATION = "stream_notification"
    GIT_COMMIT = "git_commit"
    DEVELOPMENT_UPDATE = "development_update"
    GENERAL_POST = "general_post"

class LinkedInCompanyPage(Enum):
    """Supported LinkedIn company pages"""
    FOUNDUPS = "1263645"     # FoundUps main page
    MOVE2JAPAN = "104834798" # Move2Japan page (same as FoundUps for streams)
    UNDAODU = "68706058"     # UnDaoDu page (CORRECTED back to 68706058)

@dataclass
class LinkedInPostRequest:
    """Unified request structure for LinkedIn posting"""
    content: str
    content_type: LinkedInContentType
    company_page: LinkedInCompanyPage = LinkedInCompanyPage.FOUNDUPS
    duplicate_check_key: Optional[str] = None  # For duplicate prevention
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LinkedInPostResult:
    """Result from LinkedIn posting attempt"""
    success: bool
    message: str
    timestamp: datetime
    content_type: LinkedInContentType
    company_page: LinkedInCompanyPage
    duplicate_prevented: bool = False

class UnifiedLinkedInInterface:
    """
    Centralized LinkedIn posting interface.

    All LinkedIn posting in the system must go through this interface
    to ensure proper coordination and duplicate prevention.
    """

    def __init__(self):
        self.posted_content = {}  # Centralized duplicate tracking
        self.history_file = "memory/unified_linkedin_history.json"
        self._load_history()

        # Load posted content from orchestrator for compatibility
        self._sync_with_orchestrator()

        logger.info("[UNIFIED LINKEDIN] Interface initialized - All LinkedIn posting centralized")

    def _load_history(self):
        """Load posting history for duplicate prevention"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding="utf-8") as f:
                    self.posted_content = json.load(f)
            else:
                self.posted_content = {}
                os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        except Exception as e:
            logger.warning(f"[UNIFIED LINKEDIN] Could not load history: {e}")
            self.posted_content = {}

    def _post_direct_via_selenium(self, request: LinkedInPostRequest) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Fallback posting without MCP (direct Selenium)."""
        try:
            from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn
            from modules.platform_integration.social_media_orchestrator.src.gemini_vision_analyzer import GeminiVisionAnalyzer

            poster = AntiDetectionLinkedIn()
            poster.setup_driver(use_existing_session=True)

            gemini_analysis = None
            if _env_truthy("FOUNDUPS_CAPTURE_SCREENSHOT", "true"):
                screenshot = poster.driver.get_screenshot_as_png()
                gemini = GeminiVisionAnalyzer(api_key=os.getenv('GOOGLE_AISTUDIO_API_KEY'))
                gemini_analysis = gemini.analyze_posting_ui(screenshot)

            success = poster.post_to_company_page(content=request.content, company_id=request.company_page.value)
            return success, gemini_analysis, None
        except Exception as e:
            return False, None, str(e)

    def _save_history(self):
        """Save posting history"""
        try:
            with open(self.history_file, 'w', encoding="utf-8") as f:
                json.dump(self.posted_content, f, indent=2)
        except Exception as e:
            logger.error(f"[UNIFIED LINKEDIN] Could not save history: {e}")

    def _sync_with_orchestrator(self):
        """Sync with orchestrator's posted streams to prevent duplicates"""
        try:
            # Import orchestrator to get its history
            from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import orchestrator

            # Copy orchestrator's posted streams into our tracking
            for video_id, stream_data in orchestrator.posted_streams.items():
                if 'linkedin' in stream_data.get('platforms_posted', []):
                    duplicate_key = f"stream_{video_id}"
                    self.posted_content[duplicate_key] = {
                        'timestamp': stream_data.get('timestamp'),
                        'content_type': 'stream_notification',
                        'company_page': LinkedInCompanyPage.FOUNDUPS.value,
                        'source': 'orchestrator_sync'
                    }

            logger.info(f"[UNIFIED LINKEDIN] Synced {len(orchestrator.posted_streams)} streams from orchestrator")

        except Exception as e:
            logger.warning(f"[UNIFIED LINKEDIN] Could not sync with orchestrator: {e}")

    def check_duplicate(self, request: LinkedInPostRequest) -> bool:
        """
        Check if content would be a duplicate post.

        Args:
            request: LinkedIn post request

        Returns:
            True if duplicate, False if new content
        """
        if not request.duplicate_check_key:
            return False  # No duplicate check requested

        duplicate_key = f"{request.content_type.value}_{request.duplicate_check_key}"

        if duplicate_key in self.posted_content:
            logger.info(f"[UNIFIED LINKEDIN] Duplicate detected: {duplicate_key}")
            return True

        return False

    def mark_as_posted(self, request: LinkedInPostRequest, success: bool = True):
        """Mark content as posted to prevent future duplicates"""
        if request.duplicate_check_key:
            duplicate_key = f"{request.content_type.value}_{request.duplicate_check_key}"
            self.posted_content[duplicate_key] = {
                'timestamp': datetime.now().isoformat(),
                'content_type': request.content_type.value,
                'company_page': request.company_page.value,
                'success': success,
                'content_length': len(request.content)
            }
            self._save_history()
            logger.info(f"[UNIFIED LINKEDIN] Marked as posted: {duplicate_key}")

    async def post_to_linkedin(self, request: LinkedInPostRequest) -> LinkedInPostResult:
        """
        Post content to LinkedIn with unified coordination.

        This is the ONLY method all systems should use for LinkedIn posting.

        Args:
            request: LinkedIn post request

        Returns:
            Result of posting attempt
        """

        # Step 1: Duplicate check
        if self.check_duplicate(request):
            logger.info(f"[UNIFIED LINKEDIN] Skipping duplicate post")
            return LinkedInPostResult(
                success=False,
                message="Content already posted (duplicate prevented)",
                timestamp=datetime.now(),
                content_type=request.content_type,
                company_page=request.company_page,
                duplicate_prevented=True
            )

        # Step 2: Post via MCP Server (Selenium - no API credentials needed)
        logger.info("="*60)
        logger.info(f"[UNIFIED LINKEDIN] POSTING {request.content_type.value.upper()}")
        logger.info(f"[UNIFIED LINKEDIN] Target: {request.company_page.value}")
        logger.info(f"[UNIFIED LINKEDIN] Content: {len(request.content)} chars")
        logger.info("="*60)

        success = False
        error_message = None

        # Post via MCP FastMCP HoloIndex Server
        # MCP server handles: Selenium + Gemini Vision + Training Data Collection
        try:
            import random
            from holo_index.mcp_client.holo_mcp_client import HoloIndexMCPClient

            logger.info("[UNIFIED LINKEDIN] Using MCP FastMCP HoloIndex Server for posting")

            # ANTI-DETECTION: Random delay before posting (2-5 seconds)
            # Mimics human reading/reviewing content before posting
            pre_post_delay = random.uniform(2.0, 5.0)
            logger.info(f"[ANTI-DETECTION] Waiting {pre_post_delay:.1f}s before posting (human-like behavior)")
            await asyncio.sleep(pre_post_delay)

            mcp_client = HoloIndexMCPClient()

            # Call MCP tool: post_to_linkedin_via_selenium
            # This automatically:
            # 1. Uses Selenium browser automation (no API)
            # 2. Captures screenshot and analyzes with Gemini Vision
            # 3. Saves training pattern to holo_index/training/selenium_patterns.json
            result = await mcp_client.call_tool(
                "post_to_linkedin_via_selenium",
                content=request.content,
                company_id=request.company_page.value,
                capture_screenshot=True  # Enable Gemini Vision analysis
            )

            # ANTI-DETECTION: Random delay after posting (1-3 seconds)
            # Mimics human verifying post success
            post_post_delay = random.uniform(1.0, 3.0)
            logger.info(f"[ANTI-DETECTION] Waiting {post_post_delay:.1f}s after posting (human-like verification)")
            await asyncio.sleep(post_post_delay)

            success = result.get("success", False)
            error_message = result.get("error", None) if not success else None

            if success:
                logger.info(f"[UNIFIED LINKEDIN] [OK] MCP post successful to page {request.company_page.value}")
                logger.info(f"[UNIFIED LINKEDIN] Training pattern saved: {result.get('training_pattern_id')}")

                # Log Gemini Vision analysis if available
                gemini_analysis = result.get("gemini_analysis")
                if gemini_analysis:
                    logger.info(f"[UNIFIED LINKEDIN] Gemini Vision UI analysis: {gemini_analysis.get('ui_state', 'N/A')}")
            else:
                error_message = error_message or "MCP posting failed"
                logger.warning(f"[UNIFIED LINKEDIN] [FAIL] MCP post failed: {error_message}")

        except Exception as e:
            error_message = str(e)
            logger.error(f"[UNIFIED LINKEDIN] Exception during MCP posting: {e}")

            # Check if this is a cancellation/duplicate attempt
            if any(indicator in error_message.lower() for indicator in ["window already closed", "target window already closed", "no such window"]):
                logger.warning("[UNIFIED LINKEDIN] User cancellation detected - marking as duplicate")
                # This will be marked as posted below to prevent future attempts

        if not success and _env_truthy("FOUNDUPS_SOCIAL_POST_FALLBACK", "true"):
            logger.warning("[UNIFIED LINKEDIN] MCP failed - attempting direct Selenium fallback")
            direct_success, gemini_analysis, direct_error = self._post_direct_via_selenium(request)
            if direct_success:
                success = True
                error_message = None
                logger.info(f"[UNIFIED LINKEDIN] [OK] Direct Selenium post successful to page {request.company_page.value}")
                if gemini_analysis:
                    logger.info(f"[UNIFIED LINKEDIN] Gemini Vision UI analysis: {gemini_analysis.get('ui_state', 'N/A')}")
            else:
                error_message = direct_error or error_message or "Direct Selenium posting failed"
                logger.warning(f"[UNIFIED LINKEDIN] [FAIL] Direct Selenium fallback failed: {error_message}")

        # Step 4: AUTO-TRIGGER X/TWITTER POST if LinkedIn succeeded
        x_post_success = False
        x_post_message = None

        if success and request.metadata and request.metadata.get('auto_post_to_x'):
            try:
                logger.info("="*60)
                logger.info("[UNIFIED LINKEDIN] LinkedIn post successful - AUTO-TRIGGERING X post")
                logger.info("="*60)

                # ANTI-DETECTION: Wait 3 seconds between platforms (mimics 012 switching tabs)
                logger.info("[ANTI-DETECTION] Waiting 3s before X post (platform switching)")
                await asyncio.sleep(3)

                # Import unified X interface
                from .unified_x_interface import unified_x, XPostRequest, XContentType, XAccount

                # Prepare X content (must be [U+2264]280 chars)
                x_content = request.metadata.get('x_content')
                if not x_content:
                    # Auto-generate condensed version from LinkedIn content
                    x_content = request.content[:250] + "..." if len(request.content) > 250 else request.content

                # Create X post request
                x_request = XPostRequest(
                    content=x_content,
                    content_type=XContentType.GIT_COMMIT if request.content_type == LinkedInContentType.GIT_COMMIT else XContentType.GENERAL_POST,
                    account=XAccount.FOUNDUPS,  # Default to FoundUps
                    duplicate_check_key=request.duplicate_check_key
                )

                # Post to X (automatically includes anti-detection delays)
                x_result = await unified_x.post_to_x(x_request)
                x_post_success = x_result.success
                x_post_message = x_result.message

                if x_post_success:
                    logger.info("[UNIFIED LINKEDIN] [OK] X post auto-triggered successfully")
                else:
                    logger.warning(f"[UNIFIED LINKEDIN] [U+26A0]️ X post auto-trigger failed: {x_post_message}")

            except Exception as e:
                logger.error(f"[UNIFIED LINKEDIN] Exception during X auto-trigger: {e}")
                x_post_message = str(e)

        # Step 5: Update tracking and return result
        if success:
            self.mark_as_posted(request, success=True)
        elif "window already closed" in str(error_message):
            # User cancellation indicates duplicate - mark as posted
            self.mark_as_posted(request, success=True)
            logger.info("[UNIFIED LINKEDIN] Auto-marked as posted due to user cancellation")

        return LinkedInPostResult(
            success=success,
            message=error_message or "Posted successfully" + (f" | X: {x_post_message}" if x_post_success or x_post_message else ""),
            timestamp=datetime.now(),
            content_type=request.content_type,
            company_page=request.company_page
        )

    def get_posting_statistics(self) -> Dict[str, Any]:
        """Get statistics about LinkedIn posting activity"""
        stats = {
            'total_posts': len(self.posted_content),
            'by_content_type': {},
            'by_company_page': {},
            'recent_posts': []
        }

        for key, data in self.posted_content.items():
            content_type = data.get('content_type', 'unknown')
            company_page = data.get('company_page', 'unknown')

            stats['by_content_type'][content_type] = stats['by_content_type'].get(content_type, 0) + 1
            stats['by_company_page'][company_page] = stats['by_company_page'].get(company_page, 0) + 1

            if len(stats['recent_posts']) < 10:
                stats['recent_posts'].append({
                    'key': key,
                    'timestamp': data.get('timestamp'),
                    'content_type': content_type
                })

        return stats

# Singleton instance for global use
unified_linkedin = UnifiedLinkedInInterface()

# Convenience functions for common use cases
async def post_stream_notification(stream_title: str, stream_url: str, video_id: str,
                                 company_page: LinkedInCompanyPage = LinkedInCompanyPage.FOUNDUPS) -> LinkedInPostResult:
    """Post a stream notification to LinkedIn"""
    content = f"[U+1F534] LIVE: {stream_title}\n\nWatch: {stream_url}\n\n#LiveStream #AI #Technology"

    request = LinkedInPostRequest(
        content=content,
        content_type=LinkedInContentType.STREAM_NOTIFICATION,
        company_page=company_page,
        duplicate_check_key=video_id
    )

    return await unified_linkedin.post_to_linkedin(request)

async def post_git_commits(commit_summary: str, commit_hashes: List[str], x_content: Optional[str] = None, auto_post_to_x: bool = True) -> LinkedInPostResult:
    """
    Post git commit summary to LinkedIn (FoundUps page).

    Args:
        commit_summary: LinkedIn post content
        commit_hashes: List of commit hashes for duplicate detection
        x_content: Optional X/Twitter content (auto-generated if None)
        auto_post_to_x: If True, automatically post to X after LinkedIn succeeds

    Returns:
        LinkedInPostResult with both LinkedIn and X status
    """
    request = LinkedInPostRequest(
        content=commit_summary,
        content_type=LinkedInContentType.GIT_COMMIT,
        company_page=LinkedInCompanyPage.FOUNDUPS,
        duplicate_check_key="|".join(sorted(commit_hashes)),  # Combined hash for duplicate detection
        metadata={
            'auto_post_to_x': auto_post_to_x,
            'x_content': x_content  # Will auto-generate if None
        }
    )

    return await unified_linkedin.post_to_linkedin(request)

async def post_development_update(update_content: str, update_id: str) -> LinkedInPostResult:
    """Post development update to LinkedIn (FoundUps page)"""
    request = LinkedInPostRequest(
        content=update_content,
        content_type=LinkedInContentType.DEVELOPMENT_UPDATE,
        company_page=LinkedInCompanyPage.FOUNDUPS,
        duplicate_check_key=update_id
    )

    return await unified_linkedin.post_to_linkedin(request)

async def post_general_content(content: str, company_page: LinkedInCompanyPage = LinkedInCompanyPage.FOUNDUPS,
                              duplicate_key: Optional[str] = None) -> LinkedInPostResult:
    """Post general content to LinkedIn"""
    request = LinkedInPostRequest(
        content=content,
        content_type=LinkedInContentType.GENERAL_POST,
        company_page=company_page,
        duplicate_check_key=duplicate_key
    )

    return await unified_linkedin.post_to_linkedin(request)

if __name__ == "__main__":
    # Test the unified interface
    import asyncio

    async def test_unified_interface():
        """Test the unified LinkedIn interface"""
        print("="*80)
        print("TESTING UNIFIED LINKEDIN INTERFACE")
        print("="*80)

        # Test duplicate detection
        result1 = await post_stream_notification(
            "Test Stream",
            "https://www.youtube.com/watch?v=TEST123",
            "TEST123"
        )
        print(f"First post result: {result1.success} - {result1.message}")

        # Test duplicate prevention
        result2 = await post_stream_notification(
            "Test Stream",
            "https://www.youtube.com/watch?v=TEST123",
            "TEST123"
        )
        print(f"Duplicate post result: {result2.success} - {result2.message}")
        print(f"Duplicate prevented: {result2.duplicate_prevented}")

        # Show statistics
        stats = unified_linkedin.get_posting_statistics()
        print(f"\nPosting statistics: {stats}")

    asyncio.run(test_unified_interface())
