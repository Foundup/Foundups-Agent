#!/usr/bin/env python3
"""
Verification script for TarsAccountSwapper and NoQuotaStreamChecker fixes.
Includes FoundUps rotation and NameError fix verification.
"""

import asyncio
import logging
import os
import sys
import re
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def verify_dae_methods():
    """Verify AutoModeratorDAE has the required methods and configuration."""
    logger.info("\n" + "="*50)
    logger.info("VERIFYING AUTOMODERATORDAE CONFIG")
    logger.info("="*50)
    
    from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
    
    # Check for _studio_channel_id_from_url
    if hasattr(AutoModeratorDAE, '_studio_channel_id_from_url'):
        logger.info("✅ AutoModeratorDAE._studio_channel_id_from_url EXISTS")
        
        # Test the regex
        dae = AutoModeratorDAE(None)
        test_url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
        found_id = dae._studio_channel_id_from_url(test_url)
        if found_id == "UC-LSSlOZwpGIRIYihaz8zCw":
            logger.info(f"✅ Regex successful: {found_id}")
        else:
            logger.error(f"❌ Regex failed: {found_id}")
    else:
        logger.error("❌ AutoModeratorDAE._studio_channel_id_from_url MISSING")

async def verify_stream_checker():
    """Verify NoQuotaStreamChecker correctly identifies channel_id and filters results."""
    logger.info("\n" + "="*50)
    logger.info("VERIFYING NO-QUOTA STREAM CHECKER")
    logger.info("="*50)
    
    from modules.platform_integration.stream_resolver.src.no_quota_stream_checker import NoQuotaStreamChecker
    
    checker = NoQuotaStreamChecker()
    
    # Test Move2Japan (UC-LSSlOZwpGIRIYihaz8zCw)
    target_cid = "UC-LSSlOZwpGIRIYihaz8zCw"
    logger.info(f"Checking {target_cid} (Move2Japan)...")
    
    result = checker.check_channel_for_live(target_cid, "Move2Japan")
    
    if result and result.get('live'):
        found_cid = result.get('channel_id')
        logger.info(f"✅ Found LIVE stream: {result.get('video_id')}")
        logger.info(f"✅ Channel ID: {found_cid}")
        if found_cid == target_cid:
            logger.info("✅ CHANNEL ID MATCH CONFIRMED")
        else:
            logger.error(f"❌ CHANNEL ID MISMATCH: {found_cid} != {target_cid}")
    else:
        logger.info("ℹ️ No live stream found for Move2Japan (expected if offline)")

async def verify_account_swapper():
    """Verify TarsAccountSwapper using user-provided DOM paths."""
    logger.info("\n" + "="*50)
    logger.info("VERIFYING TARS ACCOUNT SWAPPER")
    logger.info("="*50)
    
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from modules.communication.video_comments.skillz.tars_account_swapper.account_swapper_skill import TarsAccountSwapper
    
    try:
        port = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9222"))
        opts = Options()
        opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        driver = webdriver.Chrome(options=opts)
        
        swapper = TarsAccountSwapper(driver)
        
        # Test 1: Switch to UnDaoDu
        logger.info("Attempting switch to UnDaoDu...")
        success = await swapper.swap_to("UnDaoDu")
        if success:
            logger.info("✅ SUCCESS: Swapped to UnDaoDu")
        else:
            logger.error("❌ FAILED: Could not swap to UnDaoDu")
            
        await asyncio.sleep(3)
        
        # Test 2: Switch to FoundUps
        logger.info("Attempting switch to FoundUps...")
        success = await swapper.swap_to("FoundUps")
        if success:
            logger.info("✅ SUCCESS: Swapped to FoundUps")
        else:
            logger.error("❌ FAILED: Could not swap to FoundUps")
            
        await asyncio.sleep(3)
        
        # Test 3: Switch back to Move2Japan
        logger.info("Attempting switch back to Move2Japan...")
        success = await swapper.swap_to("Move2Japan")
        if success:
            logger.info("✅ SUCCESS: Swapped back to Move2Japan")
        else:
            logger.error("❌ FAILED: Could not swap back to Move2Japan")
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")

async def main():
    logger.info("STARTING FIX VERIFICATION")
    
    # Verify DAE methods Existence (checks NameError)
    await verify_dae_methods()
    
    # Verify stream checker logic
    await verify_stream_checker()
    
    # Verify account swapper (requires browser)
    if os.getenv("REALLY_TEST_BROWSER", "false").lower() in ("true", "1", "yes"):
        await verify_account_swapper()
    else:
        logger.info("\nSkipping browser-based TarsAccountSwapper test. Set REALLY_TEST_BROWSER=true to run.")

if __name__ == "__main__":
    asyncio.run(main())
