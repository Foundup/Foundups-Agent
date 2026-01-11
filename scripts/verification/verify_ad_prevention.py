import os
import asyncio
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Mock the imports for the test environment
import sys
sys.path.append(os.path.abspath("O:/Foundups-Agent"))

from modules.infrastructure.human_interaction.src.interaction_controller import InteractionController
from modules.infrastructure.human_interaction.src.platform_profiles import PlatformProfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ad_prevention():
    print("Starting Ad Prevention Verification...")
    # Setup chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Load the mock HTML
        file_path = "file://" + os.path.abspath("O:/Foundups-Agent/test_ad_prevention.html")
        logger.info(f"Loading {file_path}")
        driver.get(file_path)
        
        # Load the YouTube Chat profile
        profile = PlatformProfile("O:/Foundups-Agent/modules/infrastructure/human_interaction/platforms/youtube_chat.json")
        controller = InteractionController(driver, profile)
        
        # Test 1: Try to click a 'safe' element (a reaction)
        # Note: We need to mock the coordinate mapping or just test the sentinel logic directly.
        # Let's find the element and pass it to _is_safe_element which is where the magic happens.
        
        print("--- TEST 1: Safe Element (Reaction) ---")
        reaction_el = driver.find_element(By.ID, "reaction_100")
        is_safe = controller._is_safe_element(reaction_el, 361, 735) # Coordinates from profile
        print(f"Is reaction_100 safe? {is_safe}")
        assert is_safe == True, "Reaction element should be safe"

        # Test 2: Try to click an 'ad' element by ID
        print("--- TEST 2: Ad Element (by ID) ---")
        ad_el = driver.find_element(By.ID, "ad-slot-1")
        is_safe = controller._is_safe_element(ad_el, 800, 200)
        print(f"Is ad-slot-1 safe? {is_safe}")
        assert is_safe == False, "Ad element by ID should be blocked"

        # Test 3: Try to click a 'promoted' element (by Class)
        print("--- TEST 3: Promoted Element (by Class) ---")
        promoted_el = driver.find_element(By.CLASS_NAME, "promoted-item")
        is_safe = controller._is_safe_element(promoted_el, 800, 400)
        print(f"Is promoted-item safe? {is_safe}")
        assert is_safe == False, "Promoted element should be blocked"

        # Test 4: Coordinate Boundary Check (Upper half of screen)
        print("--- TEST 4: Out of Bounds Check (Top of screen) ---")
        is_safe = controller._is_safe_element(reaction_el, 500, 300) # y=300 is blocked by y_min=450
        print(f"Is coordinate (500, 300) safe? {is_safe}")
        assert is_safe == False, "Coordinates with y < 450 should be blocked"

        # Test 5: Verify the coordinate limits are actually working
        print("--- TEST 5: Upper Bound Check ---")
        is_safe = controller._is_safe_element(reaction_el, 500, 600) # y=600 should be fine
        print(f"Is coordinate (500, 600) safe? {is_safe}")
        assert is_safe == True, "Coordinates with y > 450 should be allowed"

        print("\n✅ ALL AD PREVENTION TESTS PASSED!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise e
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(test_ad_prevention())
