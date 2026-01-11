import os
import sys
import logging
from unittest.mock import MagicMock

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath("O:/Foundups-Agent")
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from modules.infrastructure.human_interaction.src.interaction_controller import InteractionController
from modules.infrastructure.human_interaction.src.platform_profiles import PlatformProfile

# Configure logging to verify sentinel messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def print_f(msg):
    print(msg)
    sys.stdout.flush()

def test_sentinel_logic():
    print_f("=== STARTING UNIT TEST FOR AD PREVENTION LOGIC ===")
    
    # 1. Mock the Driver
    mock_driver = MagicMock()
    
    # Initialize with real platform name
    controller = InteractionController(mock_driver, "youtube_chat")
    
    # Now mock the profile inside the controller
    mock_profile = MagicMock()
    mock_profile.safety_bounds = {
        "x_min": 0,
        "x_max": 1000,
        "y_min": 450,
        "y_max": 1000,
        "forbidden_selectors": [
            "[id*='ad']",
            ".yt-ad",
            ".promoted",
            "iframe:not(#chatframe)"
        ]
    }
    controller.profile = mock_profile
    
    # 2. Test Case: Out of Bounds Coordinates (Top of screen)
    print_f("\nTest Case 1: Out of Bounds Coordinates (y=300)")
    mock_element = MagicMock()
    # Mocking execute_script to return non-ad details
    mock_driver.execute_script.return_value = {
        'tag': 'DIV', 'id': 'chat-item', 'className': 'yt-chat-item', 
        'html': '<div>Chat message</div>', 'isForbidden': False
    }
    
    is_safe = controller._is_safe_element(mock_element, 500, 300)
    print_f(f"Result: {is_safe}")
    assert is_safe == False, "Logic Error: Should have blocked y < 450"

    # 3. Test Case: Safe Coordinates + Safe Element
    print_f("\nTest Case 2: Safe Coordinates (y=600) + Safe Element")
    is_safe = controller._is_safe_element(mock_element, 500, 600)
    print_f(f"Result: {is_safe}")
    assert is_safe == True, "Logic Error: Should have allowed safe interaction"

    # 4. Test Case: Ad Signature Detection (Keyword in ID)
    print_f("\nTest Case 3: Ad Signature (ID='ad-slot-1')")
    mock_driver.execute_script.return_value = {
        'tag': 'DIV', 'id': 'ad-slot-1', 'className': 'renderer', 
        'html': '<div id=\"ad-slot-1\">Ad</div>', 'isForbidden': False
    }
    is_safe = controller._is_safe_element(mock_element, 500, 600)
    print_f(f"Result: {is_safe}")
    assert is_safe == False, "Logic Error: Should have blocked 'ad' keyword"

    # 5. Test Case: Forbidden Selector Match (Simulated from JS)
    print_f("\nTest Case 4: Forbidden Selector Match")
    mock_driver.execute_script.return_value = {
        'tag': 'DIV', 'id': 'something', 'className': 'promoted', 
        'html': '<div>Promoted</div>', 'isForbidden': True
    }
    is_safe = controller._is_safe_element(mock_element, 500, 600)
    print_f(f"Result: {is_safe}")
    assert is_safe == False, "Logic Error: Should have blocked forbidden selector match"

    # 6. Test Case: Special Case - yt-renderer (Allowed if no 'ad')
    print_f("\nTest Case 5: yt-renderer (Allowed if no 'ad')")
    mock_driver.execute_script.return_value = {
        'tag': 'DIV', 'id': 'item-renderer', 'className': 'yt-renderer', 
        'html': '<div>Chat element</div>', 'isForbidden': False
    }
    is_safe = controller._is_safe_element(mock_element, 500, 600)
    print_f(f"Result for generic renderer: {is_safe}")
    assert is_safe == True, "Logic Error: Generic renderer should be allowed if no 'ad' signature"

    print_f("\n✅ ALL UNIT TESTS PASSED!")

if __name__ == "__main__":
    test_sentinel_logic()
