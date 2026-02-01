"""
OOPS Page Account Switch Tests
==============================

Tests for the direct OOPS page account switching flow.

This file also serves as UI-TARS training data documentation:
- Expected DOM elements on OOPS page
- Account picker structure after clicking "Switch account"
- Success/failure verification criteria

WSP Compliance:
- WSP 5: Test Coverage
- WSP 27: DAE Architecture (Action -> Verify)
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, AsyncMock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.communication.video_comments.skillz.tars_account_swapper.account_swapper_skill import (
    TarsAccountSwapper,
)

logger = logging.getLogger(__name__)


# =============================================================================
# UI-TARS TRAINING DATA: OOPS Page Structure
# =============================================================================
"""
OOPS PAGE ELEMENTS:
-------------------
1. Error message: Contains "don't have permission" or "Oops"
2. Switch account button: <button> or <ytcp-button> with text "Switch account"

DOM EXAMPLE (OOPS PAGE):
```html
<div class="error-container">
    <h1>Oops, you don't have permission to access this page</h1>
    <p>You may need to sign in with a different account</p>
    <button class="switch-account-btn">Switch account</button>
</div>
```

ACCOUNT PICKER (AFTER CLICKING SWITCH):
---------------------------------------
After clicking "Switch account" on OOPS page, the account picker appears.
Structure is same as clicking avatar -> "Switch account" on normal page.

Section 0 (Google Account A):
- ytd-account-section-list-renderer[0]
  - ytd-account-item-section-renderer
    - ytd-account-item-renderer[0] -> UnDaoDu
    - ytd-account-item-renderer[1] -> Move2Japan

Section 1 (Google Account B):
- ytd-account-section-list-renderer[1]
  - ytd-account-item-section-renderer
    - ytd-account-item-renderer[0] -> FoundUps
    - ytd-account-item-renderer[1] -> RavingANTIFA

SUCCESS CRITERIA:
-----------------
1. "Switch account" button found and clicked
2. Account picker appears (verify with DOM check)
3. Target account selected from picker
4. Page navigates to target channel
5. No longer on OOPS page (permission error gone)
"""


class TestOopsPageDetection:
    """Test OOPS page detection logic."""

    def test_is_permission_error_detects_oops(self):
        """Verify _is_permission_error detects OOPS page text."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = True

        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)

        # Mock the execute_script to return True for OOPS detection
        mock_driver.execute_script.return_value = True
        assert swapper._is_permission_error() is True

    def test_is_permission_error_returns_false_on_normal_page(self):
        """Verify _is_permission_error returns False on normal pages."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = False

        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)
        assert swapper._is_permission_error() is False

    def test_is_permission_error_handles_exception(self):
        """Verify _is_permission_error handles script execution errors."""
        mock_driver = Mock()
        mock_driver.execute_script.side_effect = Exception("Script error")

        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)
        assert swapper._is_permission_error() is False


class TestClickPermissionSwitch:
    """Test clicking 'Switch account' button on OOPS page."""

    def test_click_permission_switch_success(self):
        """Verify clicking Switch account button returns True on success."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = True

        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)
        assert swapper._click_permission_switch() is True

    def test_click_permission_switch_not_found(self):
        """Verify returns False when button not found."""
        mock_driver = Mock()
        mock_driver.execute_script.return_value = False

        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)
        assert swapper._click_permission_switch() is False

    def test_click_permission_switch_handles_exception(self):
        """Verify handles script execution errors."""
        mock_driver = Mock()
        mock_driver.execute_script.side_effect = Exception("DOM error")

        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)
        assert swapper._click_permission_switch() is False


class TestSwapFromOopsPage:
    """Test the direct OOPS page account switch flow."""

    @pytest.mark.asyncio
    async def test_swap_from_oops_page_success_flow(self):
        """Test successful OOPS page -> account picker -> select flow."""
        mock_driver = Mock()
        mock_driver.current_url = "https://studio.youtube.com/channel/test/oops"

        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)

        # Mock method responses for success path
        with patch.object(swapper, '_is_permission_error', side_effect=[True, False]):
            with patch.object(swapper, '_click_permission_switch', return_value=True):
                with patch.object(swapper, 'select_account', new_callable=AsyncMock, return_value=True):
                    with patch.object(swapper, 'navigate_to_comments', new_callable=AsyncMock):
                        with patch.object(swapper, '_ensure_target_access', new_callable=AsyncMock, return_value=True):
                            with patch.object(swapper, 'sleep_human', new_callable=AsyncMock):
                                with patch.object(swapper, '_verify_step', new_callable=AsyncMock):
                                    result = await swapper.swap_from_oops_page("FoundUps")

        assert result is True

    @pytest.mark.asyncio
    async def test_swap_from_oops_page_not_on_oops(self):
        """Test fallback to normal swap when not on OOPS page."""
        mock_driver = Mock()
        mock_driver.current_url = "https://youtube.com"

        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)

        # Mock: not on OOPS page, should fallback to swap_to
        with patch.object(swapper, '_is_permission_error', return_value=False):
            with patch.object(swapper, 'swap_to', new_callable=AsyncMock, return_value=True) as mock_swap_to:
                result = await swapper.swap_from_oops_page("FoundUps")

        assert result is True
        mock_swap_to.assert_called_once_with("FoundUps", navigate_to_comments=True)

    @pytest.mark.asyncio
    async def test_swap_from_oops_page_click_fails(self):
        """Test fallback when Switch account button click fails."""
        mock_driver = Mock()
        mock_driver.current_url = "https://studio.youtube.com/oops"

        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)

        with patch.object(swapper, '_is_permission_error', return_value=True):
            with patch.object(swapper, '_click_permission_switch', return_value=False):
                with patch.object(swapper, 'swap_to', new_callable=AsyncMock, return_value=True) as mock_swap_to:
                    result = await swapper.swap_from_oops_page("RavingANTIFA")

        assert result is True
        mock_swap_to.assert_called_once()

    @pytest.mark.asyncio
    async def test_swap_from_oops_page_select_fails(self):
        """Test failure when account selection fails."""
        mock_driver = Mock()

        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)

        with patch.object(swapper, '_is_permission_error', return_value=True):
            with patch.object(swapper, '_click_permission_switch', return_value=True):
                with patch.object(swapper, 'sleep_human', new_callable=AsyncMock):
                    with patch.object(swapper, '_verify_step', new_callable=AsyncMock):
                        with patch.object(swapper, 'select_account', new_callable=AsyncMock, return_value=False):
                            result = await swapper.swap_from_oops_page("Move2Japan")

        assert result is False


class TestAccountSectionMapping:
    """Test account section mapping for wrong account detection."""

    def test_account_picker_map_structure(self):
        """Verify ACCOUNT_PICKER_MAP matches expected structure."""
        mock_driver = Mock()
        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)

        # Section 0 (Google Account A)
        assert swapper.ACCOUNT_PICKER_MAP["UnDaoDu"]["section"] == 0
        assert swapper.ACCOUNT_PICKER_MAP["Move2Japan"]["section"] == 0

        # Section 1 (Google Account B)
        assert swapper.ACCOUNT_PICKER_MAP["FoundUps"]["section"] == 1
        assert swapper.ACCOUNT_PICKER_MAP["RavingANTIFA"]["section"] == 1

    def test_channels_config_has_all_four(self):
        """Verify all 4 channels are configured."""
        mock_driver = Mock()
        swapper = TarsAccountSwapper(mock_driver, ui_tars_verify=False)

        channels = swapper.CHANNELS
        assert "Move2Japan" in channels
        assert "UnDaoDu" in channels
        assert "FoundUps" in channels
        assert "RavingANTIFA" in channels


# =============================================================================
# UI-TARS TRAINING SCENARIOS
# =============================================================================
"""
SCENARIO 1: RavingANTIFA shows OOPS (browser on Account A)
-----------------------------------------------------------
Input State:
- Browser logged into Google Account A (UnDaoDu/Move2Japan session)
- Navigated to RavingANTIFA Studio URL
- OOPS page displayed

Expected Actions:
1. Detect OOPS page
2. Click "Switch account" button on OOPS page
3. Account picker appears showing Section 0 and Section 1
4. Click on Section 1, item 1 (RavingANTIFA)
5. Page reloads to RavingANTIFA Studio

Verification:
- URL contains RavingANTIFA channel ID (UCVSmg5aOhP4tnQ9KFUg97qA)
- No OOPS message visible
- Studio UI loads normally


SCENARIO 2: Move2Japan shows OOPS (browser on Account B)
---------------------------------------------------------
Input State:
- Browser logged into Google Account B (FoundUps/RavingANTIFA session)
- Navigated to Move2Japan Studio URL
- OOPS page displayed

Expected Actions:
1. Detect OOPS page
2. Click "Switch account" button
3. Click on Section 0, item 1 (Move2Japan)
4. Page reloads

Verification:
- URL contains Move2Japan channel ID (UC-LSSlOZwpGIRIYihaz8zCw)
- Studio UI loads normally


SCENARIO 3: Both FoundUps AND RavingANTIFA show OOPS
-----------------------------------------------------
This indicates browser is completely on wrong Google Account (Account A instead of B).

Input State:
- First try FoundUps -> OOPS
- Try fallback RavingANTIFA -> also OOPS
- Both Section 1 channels inaccessible

Expected Log Output:
```
[ROTATE] [Edge] OOPS PAGE detected for FoundUps
[ROTATE] [Edge] Trying fallback channel: RavingANTIFA
[ROTATE] [Edge] Fallback RavingANTIFA also shows OOPS
[ROTATE] [Edge] WRONG GOOGLE ACCOUNT: Browser appears to be on Google Account A,
                but needs Google Account B (FoundUps/RavingANTIFA) (Section 1)
[ROTATE] [Edge] Attempting DIRECT OOPS page switch for FoundUps...
```
"""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
