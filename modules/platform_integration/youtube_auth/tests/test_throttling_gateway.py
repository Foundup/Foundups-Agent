#!/usr/bin/env python3
"""
Test script to verify MonitoredYouTubeService throttling is working.
WSP 86: Navigation and debugging for throttling bypass issue.
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


import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
from modules.platform_integration.youtube_auth.src.monitored_youtube_service import create_monitored_service
from modules.platform_integration.youtube_auth.src.quota_monitor import QuotaMonitor

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG to see all throttling messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_throttling():
    """Test if throttling gateway is working."""
    
    logger.info("=" * 60)
    logger.info("[U+1F9EA] TESTING MONITORED YOUTUBE SERVICE THROTTLING")
    logger.info("=" * 60)
    
    # Get authenticated service
    logger.info("\n1️⃣ Getting authenticated service...")
    try:
        raw_service = get_authenticated_service()
        logger.info("[OK] Got raw YouTube service")
    except Exception as e:
        logger.error(f"[FAIL] Failed to get service: {e}")
        return
    
    # Wrap with monitoring
    logger.info("\n2️⃣ Wrapping with monitoring...")
    monitored = create_monitored_service(raw_service)
    logger.info("[OK] Created monitored service")
    
    # Check current quota
    logger.info("\n3️⃣ Checking current quota...")
    quota_monitor = QuotaMonitor()
    summary = quota_monitor.get_usage_summary()
    
    for set_num, set_info in summary['sets'].items():
        logger.info(f"   Set {set_num}: {set_info['used']}/{set_info['limit']} ({set_info['usage_percent']:.1f}%)")
    
    # Try to make an API call
    logger.info("\n4️⃣ Testing API call interception...")
    logger.info("   Making channels().list() call...")
    
    try:
        # This should trigger the monitoring wrapper
        response = monitored.channels().list(
            part='snippet',
            mine=True
        ).execute()
        
        if response.get('items'):
            channel = response['items'][0]['snippet']['title']
            logger.info(f"   [OK] API call succeeded: Channel = {channel}")
        else:
            logger.info("   [U+26A0]️ API call succeeded but no channel found")
            
    except Exception as e:
        if "Quota Protection" in str(e):
            logger.warning(f"   [FORBIDDEN] API call BLOCKED by quota protection: {e}")
        else:
            logger.error(f"   [FAIL] API call failed: {e}")
    
    # Check if monitoring logged anything
    logger.info("\n5️⃣ Checking monitoring logs...")
    logger.info("   Look for:")
    logger.info("   - [SEARCH] MonitoredYouTubeService.__getattr__ messages")
    logger.info("   - [U+1F3AC] Intercepted API call messages")
    logger.info("   - [DATA] Pre-approved or [FORBIDDEN] BLOCKED messages")
    
    # Get updated quota
    logger.info("\n6️⃣ Checking quota after call...")
    summary_after = quota_monitor.get_usage_summary()
    
    for set_num, set_info in summary_after['sets'].items():
        before = summary['sets'][set_num]['used']
        after = set_info['used']
        if after > before:
            logger.info(f"   Set {set_num}: {before} -> {after} (+{after - before} units used)")
        else:
            logger.info(f"   Set {set_num}: {after} (no change)")
    
    logger.info("\n" + "=" * 60)
    logger.info("[U+1F3C1] TEST COMPLETE - Check logs above for monitoring activity")
    logger.info("=" * 60)

if __name__ == "__main__":
    test_throttling()
