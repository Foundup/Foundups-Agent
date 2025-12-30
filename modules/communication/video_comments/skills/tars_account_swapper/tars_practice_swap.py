"""
Tars Practice Swap Script
=========================

Orchestrates the transition between Move2Japan and UnDaoDu for Tars reinforcement training.
"""

import asyncio
import logging
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .account_swapper_skill import TarsAccountSwapper

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def run_practice(target_account: str):
    """
    Practice the swap to a specific account.
    """
    chrome_port = 9222
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_port}")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        swapper = TarsAccountSwapper(driver)
        
        logger.info(f"[PRACTICE] Starting swap to {target_account}...")
        success = await swapper.swap_to(target_account)
        
        if success:
            logger.info(f"[PRACTICE] ✅ Successfully initiated swap to {target_account}")
        else:
            logger.error(f"[PRACTICE] ❌ Failed to swap to {target_account}")
            
    except Exception as e:
        logger.error(f"[PRACTICE] ❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tars Account Swapper Practice")
    parser.add_argument("--to", choices=["UnDaoDu", "Move2Japan"], required=True, help="Target account")
    args = parser.parse_args()
    
    asyncio.run(run_practice(args.to))
