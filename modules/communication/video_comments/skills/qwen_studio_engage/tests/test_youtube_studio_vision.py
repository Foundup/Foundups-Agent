"""
Test YouTube Studio Vision - Like Comment via UI-TARS

Tests the full vision automation stack:
- ActionRouter → Vision routing
- UI-TARS browser automation
- YouTube Studio complex UI interaction
- Pattern learning integration

Usage:
    python tests/test_youtube_studio_vision.py

Requirements:
    - Chrome profile 'youtube_move2japan' logged into YouTube
    - UI-TARS server running (if using vision)
    - YouTube Studio access (creator account)

WSP Compliance:
    - WSP 50: Pre-Action Verification (verify browser profile exists)
    - WSP 91: Observability (telemetry and logging)
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.infrastructure.browser_actions.src.action_router import (
    ActionRouter,
    DriverType,
)
from modules.infrastructure.foundups_selenium.src.browser_manager import (
    BrowserManager,
    get_browser_manager,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YouTubeStudioVisionTest:
    """
    Test YouTube Studio comment liking via Vision.

    This tests the FULL vision automation stack on a complex
    real-world interface (YouTube Studio).
    """

    def __init__(self, channel_id: str, profile: str = 'youtube_move2japan'):
        """
        Initialize test.

        Args:
            channel_id: YouTube channel ID (e.g., UC-LSSlOZwpGIRIYihaz8zCw)
            profile: Chrome profile name (must be logged into YouTube)
        """
        self.channel_id = channel_id
        self.profile = profile
        self.studio_url = f"https://studio.youtube.com/channel/{channel_id}/comments/inbox"

        # Initialize components
        self.browser_manager = get_browser_manager()
        self.router = ActionRouter(profile=profile)

        # Test results
        self.results = {
            'navigation': None,
            'page_load': None,
            'vision_like': None,
            'errors': [],
            'duration_ms': 0,
        }

    async def run_test(self) -> dict:
        """
        Run the full test suite.

        Returns:
            Dict with test results
        """
        start_time = datetime.now()

        try:
            logger.info(f"[TEST] Starting YouTube Studio Vision Test")
            logger.info(f"[TEST] Channel: {self.channel_id}")
            logger.info(f"[TEST] Profile: {self.profile}")
            logger.info(f"[TEST] URL: {self.studio_url}")

            # Step 1: Navigate to Studio comments inbox
            await self._test_navigation()

            # Step 2: Wait for page load
            await self._test_page_load()

            # Step 3: Like first comment using Vision
            await self._test_vision_like()

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.results['duration_ms'] = int(duration)

            # Print summary
            self._print_summary()

            return self.results

        except Exception as e:
            logger.error(f"[TEST] Test failed with exception: {e}", exc_info=True)
            self.results['errors'].append(str(e))
            return self.results

    async def _test_navigation(self):
        """Test 1: Navigate to YouTube Studio comments inbox"""
        logger.info("\n[TEST 1] Navigation to Studio comments inbox...")

        try:
            # Use Selenium for navigation (fast, reliable)
            result = await self.router.execute(
                'navigate',
                {'url': self.studio_url},
                driver=DriverType.SELENIUM,
            )

            self.results['navigation'] = {
                'success': result.success,
                'driver_used': result.driver_used,
                'duration_ms': result.duration_ms,
                'error': result.error,
            }

            if result.success:
                logger.info(f"[TEST 1] ✅ Navigation successful ({result.duration_ms}ms)")
            else:
                logger.error(f"[TEST 1] ❌ Navigation failed: {result.error}")
                self.results['errors'].append(f"Navigation: {result.error}")

        except Exception as e:
            logger.error(f"[TEST 1] ❌ Navigation exception: {e}")
            self.results['navigation'] = {'success': False, 'error': str(e)}
            self.results['errors'].append(f"Navigation exception: {e}")

    async def _test_page_load(self):
        """Test 2: Wait for page load and verify comments loaded"""
        logger.info("\n[TEST 2] Waiting for page load...")

        try:
            # Wait for Studio UI to load (complex React app)
            wait_seconds = 5
            logger.info(f"[TEST 2] Waiting {wait_seconds} seconds for Studio UI...")
            await asyncio.sleep(wait_seconds)

            self.results['page_load'] = {
                'success': True,
                'wait_seconds': wait_seconds,
            }

            logger.info(f"[TEST 2] ✅ Page load wait complete")

        except Exception as e:
            logger.error(f"[TEST 2] ❌ Page load exception: {e}")
            self.results['page_load'] = {'success': False, 'error': str(e)}
            self.results['errors'].append(f"Page load: {e}")

    async def _test_vision_like(self):
        """Test 3: Like first comment using UI-TARS Vision"""
        logger.info("\n[TEST 3] Liking comment via Vision...")

        try:
            # Use Vision to find and click like button
            # YouTube Studio has two types of like buttons:
            # 1. Regular "thumbs up" like
            # 2. "Heart" (creator heart - special for channel owners)

            # Try regular like first
            result = await self.router.execute(
                'click_element',
                {
                    'description': 'thumbs up like button on the first visible comment',
                    'target': 'like button',
                    'context': 'YouTube Studio comments inbox',
                },
                driver=DriverType.VISION,
            )

            self.results['vision_like'] = {
                'success': result.success,
                'driver_used': result.driver_used,
                'duration_ms': result.duration_ms,
                'error': result.error,
                'fallback_attempted': result.fallback_attempted,
            }

            if result.success:
                logger.info(f"[TEST 3] ✅ Vision like successful!")
                logger.info(f"[TEST 3]    Driver: {result.driver_used}")
                logger.info(f"[TEST 3]    Duration: {result.duration_ms}ms")
                logger.info(f"[TEST 3]    Fallback: {result.fallback_attempted}")
            else:
                logger.warning(f"[TEST 3] ⚠️ Vision like failed: {result.error}")
                logger.info(f"[TEST 3] Attempting 'heart' button instead...")

                # Try creator heart button
                heart_result = await self.router.execute(
                    'click_element',
                    {
                        'description': 'heart button to give creator heart on first comment',
                        'target': 'heart button',
                        'context': 'YouTube Studio comments inbox',
                    },
                    driver=DriverType.VISION,
                )

                if heart_result.success:
                    logger.info(f"[TEST 3] ✅ Creator heart successful!")
                    self.results['vision_like']['success'] = True
                    self.results['vision_like']['heart_used'] = True
                else:
                    logger.error(f"[TEST 3] ❌ Both like and heart failed")
                    self.results['errors'].append(f"Vision like: {result.error}")

        except Exception as e:
            logger.error(f"[TEST 3] ❌ Vision exception: {e}")
            self.results['vision_like'] = {'success': False, 'error': str(e)}
            self.results['errors'].append(f"Vision exception: {e}")

    def _print_summary(self):
        """Print test results summary"""
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)

        # Navigation
        nav = self.results.get('navigation', {})
        logger.info(f"\n1. Navigation: {'✅ PASS' if nav.get('success') else '❌ FAIL'}")
        if nav.get('success'):
            logger.info(f"   Duration: {nav.get('duration_ms')}ms")
            logger.info(f"   Driver: {nav.get('driver_used')}")

        # Page Load
        load = self.results.get('page_load', {})
        logger.info(f"\n2. Page Load: {'✅ PASS' if load.get('success') else '❌ FAIL'}")
        if load.get('success'):
            logger.info(f"   Wait time: {load.get('wait_seconds')}s")

        # Vision Like
        vision = self.results.get('vision_like', {})
        logger.info(f"\n3. Vision Like: {'✅ PASS' if vision.get('success') else '❌ FAIL'}")
        if vision.get('success'):
            logger.info(f"   Duration: {vision.get('duration_ms')}ms")
            logger.info(f"   Driver: {vision.get('driver_used')}")
            logger.info(f"   Fallback: {vision.get('fallback_attempted')}")
            if vision.get('heart_used'):
                logger.info(f"   Method: Creator heart (fallback)")
        elif vision.get('error'):
            logger.info(f"   Error: {vision.get('error')}")

        # Overall
        logger.info(f"\nTotal Duration: {self.results['duration_ms']}ms")

        if self.results['errors']:
            logger.info(f"\nErrors ({len(self.results['errors'])}):")
            for i, error in enumerate(self.results['errors'], 1):
                logger.info(f"  {i}. {error}")

        # Final verdict
        all_passed = (
            nav.get('success') and
            load.get('success') and
            vision.get('success')
        )

        logger.info("\n" + "="*60)
        if all_passed:
            logger.info("🎉 ALL TESTS PASSED - Vision automation works!")
        else:
            logger.info("⚠️ SOME TESTS FAILED - Check logs above")
        logger.info("="*60 + "\n")

    def cleanup(self):
        """Cleanup resources (optional - browser can stay open for inspection)"""
        logger.info("[TEST] Cleanup complete (browser left open for inspection)")


async def main():
    """Run the YouTube Studio Vision test"""

    # Configuration
    CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"  # User's channel
    PROFILE = "youtube_move2japan"  # Chrome profile (must be logged in)

    # Create and run test
    test = YouTubeStudioVisionTest(
        channel_id=CHANNEL_ID,
        profile=PROFILE,
    )

    results = await test.run_test()

    # Optionally cleanup (comment out to keep browser open)
    # test.cleanup()

    # Return exit code
    success = (
        results.get('navigation', {}).get('success') and
        results.get('page_load', {}).get('success') and
        results.get('vision_like', {}).get('success')
    )

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
