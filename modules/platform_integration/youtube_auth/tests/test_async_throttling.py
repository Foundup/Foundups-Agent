#!/usr/bin/env python3
"""
Test if async execution bypasses MonitoredYouTubeService throttling.
WSP 86: Debugging throttling bypass in async context.
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


import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
from modules.platform_integration.youtube_auth.src.monitored_youtube_service import create_monitored_service

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_async_api_call():
    """Test if async executor bypasses monitoring."""
    
    logger.info("="*60)
    logger.info("[TARGET] TESTING ASYNC API CALL MONITORING")
    logger.info("="*60)
    
    # Get monitored service
    raw_service = get_authenticated_service()
    monitored = create_monitored_service(raw_service)
    logger.info("[OK] Created monitored service")
    
    # Test 1: Direct synchronous call
    logger.info("\n1️⃣ Testing SYNCHRONOUS call...")
    try:
        response = monitored.channels().list(
            part='snippet',
            mine=True
        ).execute()
        logger.info("[OK] Sync call succeeded")
    except Exception as e:
        logger.error(f"[FAIL] Sync call failed: {e}")
    
    # Test 2: Async executor call (how ChatPoller does it)
    logger.info("\n2️⃣ Testing ASYNC EXECUTOR call...")
    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(
            None,
            lambda: monitored.channels().list(
                part='snippet',
                mine=True
            ).execute()
        )
        logger.info("[OK] Async executor call succeeded")
    except Exception as e:
        logger.error(f"[FAIL] Async executor call failed: {e}")
    
    # Test 3: Pass service through function (simulate ChatPoller)
    logger.info("\n3️⃣ Testing PASSED SERVICE in async...")
    
    class MockChatPoller:
        def __init__(self, youtube_service):
            self.youtube = youtube_service
            logger.info("[U+1F9D1]‍[U+1F4BB] MockChatPoller initialized")
        
        async def make_api_call(self):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self.youtube.channels().list(
                    part='snippet',
                    mine=True
                ).execute()
            )
    
    poller = MockChatPoller(monitored)
    try:
        response = await poller.make_api_call()
        logger.info("[OK] MockChatPoller async call succeeded")
    except Exception as e:
        logger.error(f"[FAIL] MockChatPoller async call failed: {e}")
    
    logger.info("\n" + "="*60)
    logger.info("[U+1F3C1] ASYNC TEST COMPLETE")
    logger.info("Look for [U+1F3AC] Intercepted API call messages above")
    logger.info("="*60)

if __name__ == "__main__":
    asyncio.run(test_async_api_call())
