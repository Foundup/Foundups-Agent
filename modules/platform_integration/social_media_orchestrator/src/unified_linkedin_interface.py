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
    UNDAODU = "68706058"     # UnDaoDu page

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
                with open(self.history_file, 'r') as f:
                    self.posted_content = json.load(f)
            else:
                self.posted_content = {}
                os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        except Exception as e:
            logger.warning(f"[UNIFIED LINKEDIN] Could not load history: {e}")
            self.posted_content = {}

    def _save_history(self):
        """Save posting history"""
        try:
            with open(self.history_file, 'w') as f:
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

        # Step 2: Validate credentials
        if not (os.getenv('LINKEDIN_CLIENT_ID') and os.getenv('LINKEDIN_CLIENT_SECRET')):
            return LinkedInPostResult(
                success=False,
                message="LinkedIn API credentials not configured",
                timestamp=datetime.now(),
                content_type=request.content_type,
                company_page=request.company_page
            )

        # Step 3: Post via LinkedIn Scheduler with proper coordination
        logger.info("="*60)
        logger.info(f"[UNIFIED LINKEDIN] POSTING {request.content_type.value.upper()}")
        logger.info(f"[UNIFIED LINKEDIN] Target: {request.company_page.value}")
        logger.info(f"[UNIFIED LINKEDIN] Content: {len(request.content)} chars")
        logger.info("="*60)

        success = False
        error_message = None

        # Use threading to avoid blocking async code
        linkedin_completed = threading.Event()

        def post_thread():
            nonlocal success, error_message
            global _GLOBAL_LINKEDIN_POSTER

            try:
                with _POSTER_LOCK:
                    # Import AntiDetectionLinkedIn for browser automation (NOT API)
                    from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn

                    # Create or reuse global poster instance
                    if not _GLOBAL_LINKEDIN_POSTER:
                        logger.info("[UNIFIED LINKEDIN] Creating AntiDetection browser poster (NO API)")
                        _GLOBAL_LINKEDIN_POSTER = AntiDetectionLinkedIn()
                        logger.info("[UNIFIED LINKEDIN] AntiDetection browser poster created")
                    else:
                        logger.info("[UNIFIED LINKEDIN] Reusing existing browser poster")

                    try:
                        # Use browser automation to post (NOT API)
                        # AntiDetectionLinkedIn.post_to_company_page() returns True/False
                        success = _GLOBAL_LINKEDIN_POSTER.post_to_company_page(
                            content=request.content
                        )

                        if success:
                            logger.info(f"[UNIFIED LINKEDIN] ✅ Browser post successful to page {request.company_page.value}")
                        else:
                            error_message = "Browser automation post failed"
                            logger.warning(f"[UNIFIED LINKEDIN] ❌ Browser post failed: {error_message}")
                    except Exception as e:
                        error_message = str(e)
                        logger.error(f"[UNIFIED LINKEDIN] Exception during browser posting: {e}")

            except Exception as e:
                error_message = str(e)
                logger.error(f"[UNIFIED LINKEDIN] Exception during posting: {e}")

                # Check if this is a cancellation/duplicate attempt
                if any(indicator in error_message.lower() for indicator in ["window already closed", "target window already closed", "no such window"]):
                    logger.warning("[UNIFIED LINKEDIN] User cancellation detected - marking as duplicate")
                    # This will be marked as posted below to prevent future attempts

            finally:
                linkedin_completed.set()

        # Start posting thread
        thread = threading.Thread(target=post_thread, daemon=False)
        thread.start()

        # Wait for completion
        while not linkedin_completed.is_set():
            await asyncio.sleep(0.1)

        # Step 4: Update tracking and return result
        if success:
            self.mark_as_posted(request, success=True)
        elif "window already closed" in str(error_message):
            # User cancellation indicates duplicate - mark as posted
            self.mark_as_posted(request, success=True)
            logger.info("[UNIFIED LINKEDIN] Auto-marked as posted due to user cancellation")

        return LinkedInPostResult(
            success=success,
            message=error_message or "Posted successfully",
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
    content = f"🔴 LIVE: {stream_title}\n\nWatch: {stream_url}\n\n#LiveStream #AI #Technology"

    request = LinkedInPostRequest(
        content=content,
        content_type=LinkedInContentType.STREAM_NOTIFICATION,
        company_page=company_page,
        duplicate_check_key=video_id
    )

    return await unified_linkedin.post_to_linkedin(request)

async def post_git_commits(commit_summary: str, commit_hashes: List[str]) -> LinkedInPostResult:
    """Post git commit summary to LinkedIn (Development page)"""
    request = LinkedInPostRequest(
        content=commit_summary,
        content_type=LinkedInContentType.GIT_COMMIT,
        company_page=LinkedInCompanyPage.DEVELOPMENT,
        duplicate_check_key="|".join(sorted(commit_hashes))  # Combined hash for duplicate detection
    )

    return await unified_linkedin.post_to_linkedin(request)

async def post_development_update(update_content: str, update_id: str) -> LinkedInPostResult:
    """Post development update to LinkedIn (Development page)"""
    request = LinkedInPostRequest(
        content=update_content,
        content_type=LinkedInContentType.DEVELOPMENT_UPDATE,
        company_page=LinkedInCompanyPage.DEVELOPMENT,
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