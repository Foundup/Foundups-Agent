"""
POC: YouTube Studio Comment Interaction (012)
Goal: Navigate to comments and Like, Love, and Comment "0102 was here".
Implementation: Uses ActionRouter (UI Tars / Gemini Vision) for "First Principles" system integration.
"""
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

import sys
import asyncio
import logging
import time

# Adjust path to find modules if running from root
sys.path.append('.')

from modules.infrastructure.browser_actions.src.action_router import ActionRouter, DriverType
from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [POC-ROUTER] - %(message)s')
logger = logging.getLogger(__name__)

TARGET_URL = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"

async def run_automation():
    logger.info("Initializing ActionRouter (UI Tars / Vision)...")
    
    # Initialize Router (using default profile or connection)
    router = ActionRouter(profile='youtube_move2japan')
    
    # 1. Navigate
    logger.info(f"Navigating to {TARGET_URL}...")
    await router.execute('navigate', {'url': TARGET_URL})
    
    # Wait for load and potential login
    logger.info("Waiting for page load (and user login if needed)...")
    await asyncio.sleep(5)
    
    # Login check loop (borrowed from previous POC)
    # We need to access the underlying driver to check URL
    # Router doesn't expose it directly easily without _selenium_driver check
    # But navigate ensures selenium driver is init
    driver = await router._ensure_selenium()
    
    if "accounts.google.com" in driver.current_url or "login" in driver.current_url:
        logger.warning("Login detected! Please log in foundups in the browser.")
        while "studio.youtube.com" not in driver.current_url:
            await asyncio.sleep(2)
        logger.info("Login successful. Proceeding...")
        await asyncio.sleep(5)

    # 2. Interaction Loop
    # We will prioritize commenting first as it's the new requirement
    
    for i in range(5): # Limit to 5 comments for POC safety
        logger.info(f"--- Processing Comment #{i+1} ---")
        
        # A. LIKE (Thumbs Up)
        logger.info("Attempting LIKE...")
        like_res = await router.execute(
            'click_by_description',
            {
                'description': 'gray unclicked thumbs up like button on a comment',
                'context': 'YouTube Studio comments list'
            },
            driver=DriverType.VISION
        )
        if like_res.success:
            logger.info("LIKE Success.")
        else:
            logger.info(f"LIKE Skipped/Failed: {like_res.error}")

        # B. HEART (Love)
        logger.info("Attempting HEART...")
        heart_res = await router.execute(
            'click_by_description',
            {
                'description': 'gray unclicked heart button (creator heart) on a comment',
                'context': 'YouTube Studio comments list'
            },
            driver=DriverType.VISION
        )
        if heart_res.success:
            logger.info("HEART Success.")
        else:
            logger.info(f"HEART Skipped/Failed: {heart_res.error}")

        # C. REPLY (Comment)
        logger.info("Attempting REPLY...")
        
        # 1. Click Reply Button
        reply_btn_res = await router.execute(
            'click_by_description',
            {
                'description': 'text button labeled "Reply" on a comment that has no reply yet',
                'context': 'YouTube Studio comments list'
            },
            driver=DriverType.VISION
        )
        
        if reply_btn_res.success:
            logger.info("Reply button clicked. Typing response...")
            await asyncio.sleep(1)
            
            # 2. Type Text
            type_res = await router.execute(
                'type_text',
                {
                    'description': 'the reply text input field that just appeared',
                    'text': '0102 was here' 
                },
                driver=DriverType.VISION # Force Vision to find element description
            )
            
            if type_res.success:
                logger.info("Text typed. Submitting...")
                await asyncio.sleep(1)
                
                # 3. Click Submit (Reply)
                submit_res = await router.execute(
                    'click_by_description',
                    {
                        'description': 'blue filled button labeled "Reply" to submit the comment',
                        'context': 'Reply editor'
                    },
                    driver=DriverType.VISION
                )
                if submit_res.success:
                    logger.info("COMMENT POSTED: '0102 was here'")
                    
                    # 4. Success Verification (Screenshot)
                    await asyncio.sleep(2) # Wait for comment to appear
                    driver = await router._ensure_selenium()
                    
                    proof_path = "C:\\Users\\user\\.gemini\\antigravity\\brain\\be9b1e28-d472-43c4-8a6b-99cfc25422ad\\Proof_0102_Success.png"
                    driver.save_screenshot(proof_path)
                    logger.info(f"PROOF SAVED: {proof_path}")
                    
                else:
                    logger.error("Failed to click Submit Reply button.")
            else:
                logger.error("Failed to type text.")
        else:
            logger.info("No 'Reply' button found (or already replied).")
            
        await asyncio.sleep(2)
        
    logger.info("POC Run Complete.")
    
    # Keep open
    print("\n" + "="*50)
    print(" Browser kept open. Ctrl+C to exit.")
    print("="*50 + "\n")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(run_automation())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
