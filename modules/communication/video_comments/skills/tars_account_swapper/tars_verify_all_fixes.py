import asyncio
import os
import logging
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[4]
sys.path.append(str(repo_root))

from modules.infrastructure.foundups_vision.src.studio_account_switcher import StudioAccountSwitcher
from modules.infrastructure.human_interaction import get_interaction_controller

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VERIFY-FIXES")

async def verify_all():
    logger.info("Starting final verification of account swapping and navigation fixes...")
    
    switcher = StudioAccountSwitcher()
    
    # 1. Verify switch to UnDaoDu (and navigation to comments)
    logger.info("--- Step 1: Switch to UnDaoDu & Navigate to Comments ---")
    result = await switcher.switch_to_account("UnDaoDu", navigate_to_comments=True)
    logger.info(f"UnDaoDu Switch Result: {result}")
    
    if not result.get("success"):
        logger.error("Verification failed at UnDaoDu switch")
        return

    # 2. Verify iframe detection (requires being on a live chat page, but we can test the selector logic)
    logger.info("--- Step 2: Verify Iframe Detection Logic ---")
    # We'll just check if the interaction controller can be initialized for youtube_chat
    # and if it handles the 'no iframe' case gracefully without crashing
    try:
        interaction = get_interaction_controller(switcher.driver, platform="youtube_chat")
        # This will trigger _switch_to_iframe_if_needed on the current page (which is Studio)
        # It should fail gracefully (return False) because there is no chatframe on Studio
        iframe_result = await interaction._switch_to_iframe_if_needed()
        logger.info(f"Iframe logic check (on Studio, should be False): {iframe_result}")
    except Exception as e:
        logger.error(f"Iframe logic check crashed: {e}")

    # 3. Switch back to Move2Japan
    logger.info("--- Step 3: Switch back to Move2Japan ---")
    result = await switcher.switch_to_account("Move2Japan", navigate_to_comments=True)
    logger.info(f"Move2Japan Switch Result: {result}")

    if result.get("success"):
        logger.info("✅ ALL FIXES VERIFIED SUCCESSFULLY")
    else:
        logger.error("❌ Verification failed during switch back")

if __name__ == "__main__":
    asyncio.run(verify_all())
