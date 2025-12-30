import pytest
import os
import sys
# Add project root to sys.path
sys.path.append("O:\\Foundups-Agent")

from unittest.mock import MagicMock, patch
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from modules.infrastructure.human_interaction.src.interaction_controller import InteractionController

# File to store test results for agent verification
RESULTS_FILE = "O:\\Foundups-Agent\\test_results.txt"

def write_result(msg):
    with open(RESULTS_FILE, "a") as f:
        f.write(msg + "\n")

@pytest.fixture(autouse=True)
def clear_results():
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)
    write_result("TEST SESSION START")

@pytest.mark.asyncio
async def test_hover_action_fallback_on_out_of_bounds():
    driver = MagicMock()
    # Mock driver properties
    driver.execute_script.return_value = MagicMock() # Mock element
    
    controller = InteractionController(driver, platform="youtube_chat")
    # Mock human behavior to throw OutOfBounds
    controller.human = MagicMock()
    controller.human.move_to_element_human_like.side_effect = MoveTargetOutOfBoundsException("Out of bounds!")
    
    # Mock ActionChains for T1 fallback
    with patch("selenium.webdriver.common.action_chains.ActionChains") as mock_ac:
        # T1 fails too
        mock_ac.return_value.move_to_element.side_effect = Exception("T1 Fail")
        
        # This should hit T2 (JS)
        success = await controller.hover_action("party_toggle")
        
        assert success is True
        # Verify JS was called (T2)
        js_called = any("el.dispatchEvent" in call[0][0] for call in driver.execute_script.call_args_list)
        assert js_called
        write_result("test_hover_action_fallback_on_out_of_bounds: PASS")

@pytest.mark.asyncio
async def test_click_action_fallback_on_out_of_bounds():
    driver = MagicMock()
    driver.execute_script.return_value = MagicMock() 
    
    controller = InteractionController(driver, platform="youtube_chat")
    controller.human = MagicMock()
    # T0 fails
    controller.human.human_click.side_effect = MoveTargetOutOfBoundsException("Out of bounds!")
    
    with patch("selenium.webdriver.common.action_chains.ActionChains") as mock_ac:
        # T1 fails
        mock_ac.return_value.move_to_element.return_value.click.side_effect = Exception("T1 Fail")
        
        # This should hit T2 (JS)
        success = await controller.click_action("reaction_celebrate")
        
        assert success is True
        # Verify JS click was called (T2)
        js_called = any("arguments[0].click();" in call[0][0] for call in driver.execute_script.call_args_list)
        assert js_called
        write_result("test_click_action_fallback_on_out_of_bounds: PASS")

def pytest_sessionfinish(session, exitstatus):
    write_result(f"TEST SESSION FINISHED with exitstatus: {exitstatus}")

if __name__ == "__main__":
    import asyncio
    async def run_manual():
        try:
            await test_hover_action_fallback_on_out_of_bounds()
            await test_click_action_fallback_on_out_of_bounds()
            write_result("MANUAL RUN COMPLETE")
        except Exception as e:
            write_result(f"MANUAL RUN FAILED: {e}")
            import traceback
            write_result(traceback.format_exc())

    asyncio.run(run_manual())
