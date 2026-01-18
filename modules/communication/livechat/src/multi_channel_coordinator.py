"""
Multi-Channel Comment Engagement Coordinator

Extracted from AutoModeratorDAE per WSP 62 (Large File Refactoring).
Handles Chrome + Edge browser rotation for multi-channel comment engagement.

Architecture (2025-12-28, Hardened 2026-01-18):
- Chrome (port 9222): Move2Japan + UnDaoDu (SAME Google account)
- Edge (port 9223): FoundUps + RavingANTIFA (SAME Edge session)

Hardening Features (2026-01-18):
1. BIDIRECTIONAL FALLBACK:
   - Chrome: Move2Japan ↔ UnDaoDu
   - Edge: FoundUps ↔ RavingANTIFA
   - If target channel shows "Oops" page, try fallback before account switch

2. OOPS PAGE DETECTION:
   - Detects "don't have permission" / "Oops" / "access denied" pages
   - Triggers fallback logic automatically

3. BROWSER SESSION RECOVERY:
   - Handles NoSuchWindowException (window closed)
   - Step 1: Try reconnect to existing browser
   - Step 2: If reconnect fails, relaunch browser
   - Step 3: If relaunch fails, skip remaining channels

WSP References:
- WSP 62: Large File Refactoring Enforcement Protocol
- WSP 72: Module Independence (single responsibility)
- WSP 84: Code Reuse (delegates to existing browser infrastructure)
- WSP 73: Digital Twin Architecture (browser routing)
"""

import os
import time
import asyncio
import logging
from typing import Optional, Dict, Any, Callable, List, Tuple, Awaitable

logger = logging.getLogger(__name__)


def _env_truthy(key: str, default: str = "false") -> bool:
    """Check if env var is truthy (true/1/yes)."""
    val = os.getenv(key, default).lower()
    return val in ("true", "1", "yes")


def _is_session_error(error_text: str) -> bool:
    """Check if error indicates a recoverable session error."""
    if not error_text:
        return False
    error_lower = error_text.lower()
    return any(phrase in error_lower for phrase in [
        "session",
        "disconnected",
        "target closed",
        "connection refused",
        "not connected",
        "no such window",  # NoSuchWindowException
        "window already closed",
        "web view not found",
    ])


def _is_oops_page(driver) -> bool:
    """
    Detect if current page is an 'Oops' permission error page.

    Returns True if page shows permission error (wrong account logged in).
    """
    try:
        page_text = driver.execute_script("return document.body?.innerText || '';")
        page_lower = page_text.lower()
        return (
            "don't have permission" in page_lower or
            "oops" in page_lower or
            "you need permission" in page_lower or
            "access denied" in page_lower
        )
    except Exception:
        return False


# Bidirectional fallback mapping
# When target channel shows Oops, try fallback first before account switch
CHANNEL_FALLBACKS = {
    # Chrome channels (same Google account)
    "Move2Japan": "UnDaoDu",
    "UnDaoDu": "Move2Japan",
    # Edge channels (same Edge session)
    "FoundUps": "RavingANTIFA",
    "RavingANTIFA": "FoundUps",
}

# Channel name to ID mapping
CHANNEL_IDS = {
    "Move2Japan": os.getenv("MOVE2JAPAN_CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw"),
    "UnDaoDu": os.getenv("UNDAODU_CHANNEL_ID", "UCfHM9Fw9HD-NwiS0seD_oIA"),
    "FoundUps": os.getenv("FOUNDUPS_CHANNEL_ID", "UCSNTUXjAgpd4sgWYP0xoJgw"),
    "RavingANTIFA": os.getenv("RAVINGANTIFA_CHANNEL_ID", "UCVSmg5aOhP4tnQ9KFUg97qA"),
}

# Reverse mapping
CHANNEL_NAMES = {v: k for k, v in CHANNEL_IDS.items()}


class MultiChannelCoordinator:
    """
    Coordinates comment engagement across multiple YouTube channels.

    Uses Chrome for channels under the same Google account (account switching)
    and Edge for channels under different Google accounts (separate browser).
    """

    def __init__(
        self,
        # Callbacks for DAE integration
        log_studio_context: Callable[[str, str, Any], None],
        verify_studio_inbox_clear: Callable[[Any, str, str, float], Awaitable[Optional[bool]]],
        reconnect_chrome_driver: Callable[[int], Awaitable[Any]],
        reconnect_edge_driver: Callable[[int], Awaitable[Any]],
        detect_current_channel_id: Callable[[Any], Awaitable[Optional[str]]],
        # State callbacks
        update_engagement_status: Callable[[str, Dict[str, Any]], None],
        set_active_channel: Callable[[str], None],
        is_live_stream_pending: Callable[[], bool],
    ):
        """
        Initialize coordinator with callbacks to DAE.

        Args:
            log_studio_context: Callback to log Studio context
            verify_studio_inbox_clear: Callback to verify inbox is clear
            reconnect_chrome_driver: Callback to reconnect Chrome
            reconnect_edge_driver: Callback to reconnect Edge
            detect_current_channel_id: Callback to detect current channel
            update_engagement_status: Callback to update engagement status dict
            set_active_channel: Callback to set active channel ID
            is_live_stream_pending: Callback to check if live stream pending
        """
        self.log_studio_context = log_studio_context
        self.verify_studio_inbox_clear = verify_studio_inbox_clear
        self.reconnect_chrome_driver = reconnect_chrome_driver
        self.reconnect_edge_driver = reconnect_edge_driver
        self.detect_current_channel_id = detect_current_channel_id
        self.update_engagement_status = update_engagement_status
        self.set_active_channel = set_active_channel
        self.is_live_stream_pending = is_live_stream_pending

    async def run_multi_channel_engagement(
        self,
        runner,
        max_comments: int,
        mode: str
    ) -> int:
        """
        Run comment engagement across ALL channels with account switching.

        Flow:
        1. Process Move2Japan comments (Chrome)
        2. Switch to UnDaoDu (Chrome - same account picker)
        3. Process FoundUps comments (Edge - separate browser)
        4. Check live stream signal before each channel
        5. If live detected -> pause rotation for that channel

        Args:
            runner: CommentEngagementRunner instance
            max_comments: Maximum comments per channel (0 = unlimited)
            mode: Execution mode string

        Returns:
            Total comments processed across all channels
        """
        strict_inbox = _env_truthy("YT_INBOX_STRICT", "true")
        edge_parallel = _env_truthy("YT_EDGE_PARALLEL", "true")
        edge_first = _env_truthy("YT_EDGE_FIRST", "true")

        # CHROME ACCOUNTS (same Google account - can switch via YouTube picker)
        chrome_accounts: List[Tuple[str, str]] = [
            ("Move2Japan", os.getenv("MOVE2JAPAN_CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw")),
            ("UnDaoDu", os.getenv("UNDAODU_CHANNEL_ID", "UCfHM9Fw9HD-NwiS0seD_oIA")),
        ]

        # EDGE ACCOUNTS (different Google account - requires separate browser)
        # NOTE: RavingANTIFA added 2026-01-09, shares Edge browser with FoundUps
        edge_accounts: List[Tuple[str, str]] = [
            ("FoundUps", os.getenv("FOUNDUPS_CHANNEL_ID", "UCSNTUXjAgpd4sgWYP0xoJgw")),
            ("RavingANTIFA", os.getenv("RAVINGANTIFA_CHANNEL_ID", "UCVSmg5aOhP4tnQ9KFUg97qA")),
        ]

        total_channels = len(chrome_accounts) + len(edge_accounts)
        logger.info("=" * 70)
        logger.info("[ROTATE] MULTI-CHANNEL COMMENT ENGAGEMENT")
        logger.info(f"[ROTATE] Processing {total_channels} channels:")
        logger.info(f"[ROTATE]   Chrome (9222): {', '.join([a[0] for a in chrome_accounts])}")
        logger.info(f"[ROTATE]   Edge (9223): {', '.join([a[0] for a in edge_accounts])}")
        logger.info(f"[ROTATE] Mode: {mode} | Max per channel: {max_comments if max_comments > 0 else 'UNLIMITED'}")
        logger.info("=" * 70)

        total_processed = 0
        chrome_driver = None
        swapper = None
        rotation_halt = False
        edge_task = None

        # Start Edge in parallel if enabled
        if edge_parallel:
            try:
                edge_task = asyncio.create_task(
                    self._run_edge_engagement(runner, edge_accounts, max_comments, strict_inbox)
                )
                logger.info("[ROTATE] Edge scheduled in PARALLEL (YT_EDGE_PARALLEL=true)")
            except Exception as e:
                logger.warning(f"[ROTATE] Failed to schedule Edge task: {e}")
                edge_task = None

        # Optional ordering: run Edge FIRST when not parallel (matches ops expectation:
        # FoundUps/RavingANTIFA are often the immediate targets before live chat handoff)
        if (not edge_parallel) and edge_first:
            total_processed += await self._run_edge_engagement(
                runner, edge_accounts, max_comments, strict_inbox
            )

        # Process Chrome channels
        skip_chrome = _env_truthy("YT_SKIP_CHROME", "false")
        if skip_chrome:
            logger.info("[ROTATE] SKIPPING CHROME (YT_SKIP_CHROME=true) - Testing Edge only")

        if not skip_chrome:
            chrome_result = await self._run_chrome_engagement(
                runner, chrome_accounts, max_comments, strict_inbox
            )
            total_processed += chrome_result

        # Handle Edge result
        if not edge_parallel:
            if not edge_first:
                total_processed += await self._run_edge_engagement(
                    runner, edge_accounts, max_comments, strict_inbox
                )
        elif edge_task:
            try:
                total_processed += await edge_task
            except Exception as e:
                logger.warning(f"[ROTATE] Edge task failed: {e}")

        logger.info("=" * 70)
        logger.info("[ROTATE] MULTI-CHANNEL ENGAGEMENT COMPLETE")
        logger.info(f"[ROTATE] Total comments processed: {total_processed}")
        logger.info(f"[ROTATE] Channels: Chrome ({len(chrome_accounts)}) + Edge ({len(edge_accounts)})")
        logger.info("=" * 70)

        return total_processed

    async def _run_edge_engagement(
        self,
        runner,
        edge_accounts: List[Tuple[str, str]],
        max_comments: int,
        strict_inbox: bool
    ) -> int:
        """
        Run comment engagement via Edge (port 9223) for multiple accounts.

        IMPORTANT: Runs independently of Chrome - separate browser session.
        Processes accounts sequentially. If multiple channels share the same Edge session,
        we must explicitly switch the active channel in the YouTube account picker to avoid
        "no permission" pages when navigating directly to a channel inbox URL.
        
        Updated 2026-01-09: Now supports multiple Edge accounts (FoundUps + RavingANTIFA).
        """
        total_processed = 0
        edge_driver = None
        edge_port = int(os.getenv("FOUNDUPS_EDGE_PORT", "9223"))
        edge_swapper = None

        try:
            from selenium import webdriver
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from modules.infrastructure.dependency_launcher.src.dae_dependencies import (
                launch_edge, STUDIO_FILTER
            )
            from modules.communication.video_comments.skillz.tars_account_swapper.account_swapper_skill import TarsAccountSwapper

            edge_ok, edge_msg = launch_edge()
            if not edge_ok:
                logger.warning(f"[ROTATE] Edge auto-launch failed: {edge_msg}")

            edge_opts = EdgeOptions()
            edge_opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{edge_port}")
            edge_driver = await asyncio.to_thread(webdriver.Edge, options=edge_opts)
            logger.info(f"[ROTATE] Connected to Edge on port {edge_port}")
            edge_swapper = TarsAccountSwapper(edge_driver)

        except Exception as e:
            logger.warning(f"[ROTATE] Edge connection failed: {e}")
            logger.warning("[ROTATE] Edge channels will be skipped")
            logger.warning("[ROTATE] To enable: Launch Edge with --remote-debugging-port=9223")
            return 0

        # Process each Edge account
        for idx, (account_name, channel_id) in enumerate(edge_accounts, 1):
            # Check live stream signal
            try:
                from modules.platform_integration.stream_resolver.src.live_stream_signal import get_live_channel
                live_channel = get_live_channel()
            except ImportError:
                live_channel = None

            if live_channel == channel_id:
                logger.info(f"[SIGNAL] {account_name} has live stream - skipping comment processing")
                continue

            logger.info(f"\n[ROTATE] [Edge {idx}/{len(edge_accounts)}] Processing {account_name} comments...")

            try:
                from modules.infrastructure.dependency_launcher.src.dae_dependencies import STUDIO_FILTER

                # Navigate directly to Studio inbox for this channel
                # (Account picker swap is optional - direct URL navigation often works if both accounts signed in)
                studio_url = (
                    f"https://studio.youtube.com/channel/{channel_id}/comments/inbox?filter={STUDIO_FILTER}"
                )
                logger.info(f"[ROTATE] [Edge] Navigating directly to {account_name} Studio inbox...")
                logger.info(f"[ROTATE] [Edge] URL: {studio_url}")
                await asyncio.to_thread(edge_driver.get, studio_url)
                await asyncio.sleep(5)

                # Check for permission error (wrong account signed in)
                # HARDENED: Use bidirectional fallback before account switch
                try:
                    if _is_oops_page(edge_driver):
                        logger.warning(f"[ROTATE] [Edge] 🚨 OOPS PAGE detected for {account_name}")

                        # STEP 1: Try bidirectional fallback first (no account switch needed)
                        fallback_channel = CHANNEL_FALLBACKS.get(account_name)
                        if fallback_channel:
                            logger.info(f"[ROTATE] [Edge] 🔄 Trying fallback channel: {fallback_channel}")
                            fallback_id = CHANNEL_IDS.get(fallback_channel)
                            fallback_url = (
                                f"https://studio.youtube.com/channel/{fallback_id}/comments/inbox?filter={STUDIO_FILTER}"
                            )
                            await asyncio.to_thread(edge_driver.get, fallback_url)
                            await asyncio.sleep(5)

                            if not _is_oops_page(edge_driver):
                                # Fallback works! Process fallback channel instead
                                logger.info(f"[ROTATE] [Edge] ✅ Fallback to {fallback_channel} successful!")
                                # Update to process fallback channel
                                account_name = fallback_channel
                                channel_id = fallback_id
                                studio_url = fallback_url
                            else:
                                logger.warning(f"[ROTATE] [Edge] 🚨 Fallback {fallback_channel} also shows OOPS")

                        # STEP 2: If still on Oops (or no fallback), try account switch
                        if _is_oops_page(edge_driver):
                            logger.warning(f"[ROTATE] [Edge] Attempting account switch for {account_name}...")
                            if edge_swapper:
                                switched = await edge_swapper.swap_to(account_name, navigate_to_comments=True)
                                if not switched:
                                    logger.error(f"[ROTATE] [Edge] Account swap failed for {account_name}; skipping")
                                    logger.warning(f"[ROTATE] [Edge] FIX: Sign into {account_name} in Edge browser")
                                    continue
                                await asyncio.sleep(3)

                                # STEP 3: Verify after account switch
                                if _is_oops_page(edge_driver):
                                    logger.error(f"[ROTATE] [Edge] Still on OOPS after account switch; skipping {account_name}")
                                    continue
                except Exception as perm_err:
                    logger.debug(f"[ROTATE] [Edge] Permission check error: {perm_err}")

                self.log_studio_context(channel_id, f"{account_name} comment_engagement", edge_driver)
                self.set_active_channel(channel_id)

                logger.info(f"[ROTATE] [Edge] 🚀 Launching comment processor for {account_name}...")
                result = await runner.run_engagement(
                    channel_id=channel_id,
                    video_id=None,
                    max_comments=max_comments,
                    browser_port=9223,
                )

                result = result or {}
                stats = result.get("stats", {})
                processed = stats.get("comments_processed", 0)
                total_processed += processed

                self.update_engagement_status(channel_id, {
                    "all_processed": bool(stats.get("all_processed", False)),
                    "stats": stats,
                    "error": result.get("error"),
                    "updated_at": time.time(),
                })

                error_text = result.get("error")
                session_recovered = False

                if error_text:
                    logger.error(f"[ROTATE] {account_name} engagement failed: {error_text}")
                else:
                    logger.info(f"[ROTATE] {account_name} complete: {processed} comments processed")

                # Session recovery
                if error_text and _is_session_error(error_text) and _env_truthy("YT_RECONNECT_ON_SESSION_ERROR", "true"):
                    logger.warning(f"[ROTATE] Edge session error on {account_name}; attempting reconnect")
                    edge_driver = await self.reconnect_edge_driver(edge_port)
                    if edge_driver:
                        try:
                            await asyncio.to_thread(edge_driver.get, studio_url)
                            await asyncio.sleep(5)
                        except Exception as refresh_err:
                            logger.warning(f"[ROTATE] Edge navigation after reconnect failed: {refresh_err}")
                        session_recovered = True
                    else:
                        logger.warning(f"[ROTATE] Edge reconnect failed for {account_name}")

                # Inbox verification with retries
                processed = await self._verify_and_retry_engagement(
                    edge_driver, runner, channel_id, account_name,
                    max_comments, 9223, processed, strict_inbox, error_text, session_recovered
                )
                total_processed += processed - stats.get("comments_processed", 0)  # Add retry delta

            except Exception as e:
                error_str = str(e)
                logger.error(f"[ROTATE] {account_name} exception: {e}", exc_info=True)
                self.update_engagement_status(channel_id, {
                    "all_processed": False,
                    "stats": {},
                    "error": error_str,
                    "updated_at": time.time(),
                })

                # HARDENED: Try browser relaunch on window closed errors
                if _is_session_error(error_str):
                    logger.warning(f"[ROTATE] [Edge] 🔄 Session error detected - attempting browser recovery...")

                    # Step 1: Try reconnect first
                    edge_driver = await self.reconnect_edge_driver(edge_port)

                    # Step 2: If reconnect fails, try relaunch
                    if edge_driver is None:
                        logger.warning(f"[ROTATE] [Edge] Reconnect failed - attempting relaunch...")
                        try:
                            from modules.infrastructure.dependency_launcher.src.dae_dependencies import launch_edge
                            relaunch_ok, relaunch_msg = launch_edge(force=True)
                            if relaunch_ok:
                                await asyncio.sleep(5)  # Wait for browser to start
                                edge_opts = EdgeOptions()
                                edge_opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{edge_port}")
                                edge_driver = await asyncio.to_thread(webdriver.Edge, options=edge_opts)
                                edge_swapper = TarsAccountSwapper(edge_driver)
                                logger.info(f"[ROTATE] [Edge] ✅ Browser relaunched successfully")
                            else:
                                logger.error(f"[ROTATE] [Edge] ❌ Browser relaunch failed: {relaunch_msg}")
                        except Exception as relaunch_err:
                            logger.error(f"[ROTATE] [Edge] ❌ Relaunch exception: {relaunch_err}")

                    if edge_driver is None:
                        logger.error(f"[ROTATE] [Edge] ❌ Cannot recover browser session - skipping remaining Edge channels")
                        break

            # Check live stream pending
            if self.is_live_stream_pending() and _env_truthy("YT_STOP_ROTATION_ON_LIVE", "true"):
                logger.info(f"[ROTATE] Live stream pending - stopping Edge rotation after {account_name}")
                break

        return total_processed


    async def _run_chrome_engagement(
        self,
        runner,
        chrome_accounts: List[Tuple[str, str]],
        max_comments: int,
        strict_inbox: bool
    ) -> int:
        """
        Run comment engagement on Chrome channels (Move2Japan + UnDaoDu).

        Uses TarsAccountSwapper for account switching within same Google account.
        """
        total_processed = 0
        chrome_driver = None
        swapper = None
        rotation_halt = False

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from modules.communication.video_comments.skillz.tars_account_swapper.account_swapper_skill import TarsAccountSwapper
            from modules.infrastructure.dependency_launcher.src.dae_dependencies import launch_chrome

            chrome_port = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9222"))
            chrome_ok, chrome_msg = launch_chrome()
            if not chrome_ok:
                logger.warning(f"[ROTATE] Chrome auto-launch failed: {chrome_msg}")

            opts = Options()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_port}")
            chrome_driver = await asyncio.to_thread(webdriver.Chrome, options=opts)
            swapper = TarsAccountSwapper(chrome_driver)
            logger.info(f"[ROTATE] Connected to Chrome on port {chrome_port}")

            # Smart rotation: detect current account to minimize switching
            chrome_accounts = await self._optimize_rotation_order(chrome_driver, chrome_accounts)

        except Exception as e:
            logger.error(f"[ROTATE] Failed to connect to Chrome: {e}")
            logger.warning("[ROTATE] Chrome channels (Move2Japan, UnDaoDu) will be skipped")
            return 0

        # Process each Chrome account
        for idx, (account_name, channel_id) in enumerate(chrome_accounts, 1):
            # Check live stream signal
            try:
                from modules.platform_integration.stream_resolver.src.live_stream_signal import get_live_channel
                live_channel = get_live_channel()
            except ImportError:
                live_channel = None

            if live_channel == channel_id:
                logger.info(f"[SIGNAL] {account_name} has live stream - prioritizing live chat over comments")
                continue

            logger.info(f"\n[ROTATE] [Chrome {idx}/{len(chrome_accounts)}] Processing {account_name} comments...")

            try:
                # Account switching
                logger.info(f"[ROTATE] Switching to {account_name}...")
                success = await swapper.swap_to(account_name)

                if not success:
                    logger.warning(f"[ROTATE] Failed to switch to {account_name}")
                    if idx == 1:
                        logger.info(f"[ROTATE] Assuming already on {account_name}, continuing...")
                    else:
                        logger.warning(f"[ROTATE] Skipping {account_name}")
                        continue
                else:
                    logger.info(f"[ROTATE] Switched to {account_name} successfully")

                # Refresh for fresh comments (async to not block event loop)
                logger.info(f"[ROTATE] Refreshing page for {account_name}...")
                await asyncio.to_thread(chrome_driver.refresh)
                await asyncio.sleep(5)

                # HARDENED: Check for Oops page after switch/refresh
                if _is_oops_page(chrome_driver):
                    logger.warning(f"[ROTATE] [Chrome] 🚨 OOPS PAGE detected for {account_name}")

                    # Try bidirectional fallback first
                    fallback_channel = CHANNEL_FALLBACKS.get(account_name)
                    if fallback_channel:
                        logger.info(f"[ROTATE] [Chrome] 🔄 Trying fallback channel: {fallback_channel}")
                        fallback_id = CHANNEL_IDS.get(fallback_channel)
                        fallback_success = await swapper.swap_to(fallback_channel)
                        if fallback_success:
                            await asyncio.to_thread(chrome_driver.refresh)
                            await asyncio.sleep(5)
                            if not _is_oops_page(chrome_driver):
                                logger.info(f"[ROTATE] [Chrome] ✅ Fallback to {fallback_channel} successful!")
                                account_name = fallback_channel
                                channel_id = fallback_id
                            else:
                                logger.warning(f"[ROTATE] [Chrome] 🚨 Fallback {fallback_channel} also shows OOPS - skipping")
                                continue
                        else:
                            logger.warning(f"[ROTATE] [Chrome] Fallback switch failed - skipping {account_name}")
                            continue
                    else:
                        logger.warning(f"[ROTATE] [Chrome] No fallback available - skipping {account_name}")
                        continue

            except Exception as e:
                logger.error(f"[ROTATE] Account switch error: {e}")
                if idx > 1:
                    continue

            # Process comments
            try:
                self.set_active_channel(channel_id)
                self.log_studio_context(channel_id, f"{account_name} comment_engagement", chrome_driver)

                logger.info(f"[ROTATE] [Chrome] 🚀 Launching comment processor for {account_name}...")
                result = await runner.run_engagement(
                    channel_id=channel_id,
                    video_id=None,
                    max_comments=max_comments
                )

                result = result or {}
                stats = result.get('stats', {})
                processed = stats.get('comments_processed', 0)
                total_processed += processed

                self.update_engagement_status(channel_id, {
                    "all_processed": bool(stats.get("all_processed", False)),
                    "stats": stats,
                    "error": result.get('error'),
                    "updated_at": time.time(),
                })

                error_text = result.get('error')
                session_recovered = False

                if error_text:
                    logger.error(f"[ROTATE] {account_name} engagement failed: {error_text}")
                else:
                    logger.info(f"[ROTATE] {account_name} complete: {processed} comments processed")

                # Session recovery
                if error_text and _is_session_error(error_text) and _env_truthy("YT_RECONNECT_ON_SESSION_ERROR", "true"):
                    logger.warning(f"[ROTATE] Chrome session error on {account_name}; attempting reconnect")
                    chrome_driver = await self.reconnect_chrome_driver(chrome_port)
                    if chrome_driver:
                        swapper = TarsAccountSwapper(chrome_driver)
                        try:
                            await swapper.swap_to(account_name)
                        except Exception as swap_err:
                            logger.warning(f"[ROTATE] Chrome reconnect swap failed: {swap_err}")
                        try:
                            await asyncio.to_thread(chrome_driver.refresh)
                            await asyncio.sleep(5)
                        except Exception as refresh_err:
                            logger.warning(f"[ROTATE] Chrome refresh after reconnect failed: {refresh_err}")
                        session_recovered = True
                    else:
                        logger.warning(f"[ROTATE] Chrome reconnect failed for {account_name}")

                # Verify and retry
                processed = await self._verify_and_retry_engagement(
                    chrome_driver, runner, channel_id, account_name,
                    max_comments, 9222, processed, strict_inbox, error_text, session_recovered
                )
                total_processed += processed - stats.get('comments_processed', 0)  # Add retry delta

                # Check halt conditions
                if strict_inbox:
                    if error_text and not session_recovered:
                        logger.warning(f"[VERIFY] Strict inbox mode: holding rotation on {account_name} (error)")
                        rotation_halt = True

            except Exception as e:
                logger.error(f"[ROTATE] {account_name} exception: {e}", exc_info=True)
                self.update_engagement_status(channel_id, {
                    "all_processed": False,
                    "stats": {},
                    "error": str(e),
                    "updated_at": time.time(),
                })
                if strict_inbox:
                    rotation_halt = True

            if rotation_halt:
                logger.warning(f"[ROTATE] Rotation halted after {account_name}")
                break

            # Check live stream pending
            if self.is_live_stream_pending() and _env_truthy("YT_STOP_ROTATION_ON_LIVE", "true"):
                logger.info(f"[ROTATE] Live stream pending - stopping Chrome rotation after {account_name}")
                break

        return total_processed

    async def _optimize_rotation_order(
        self,
        chrome_driver,
        chrome_accounts: List[Tuple[str, str]]
    ) -> List[Tuple[str, str]]:
        """
        Optimize rotation order based on current browser state.

        If already on a target channel, move it to front to minimize switching.
        """
        try:
            current_url = chrome_driver.current_url
            url_base = (current_url or "").split("#", 1)[0].split("?", 1)[0]
            logger.info(f"[ROTATE] Current Chrome URL: {url_base}")

            current_channel_id = await self.detect_current_channel_id(chrome_driver)

            if current_channel_id:
                current_account = next(
                    (acc for acc in chrome_accounts if acc[1] == current_channel_id), None
                )
                if current_account:
                    logger.info(f"[ROTATE] [SMART] Detected active session on {current_account[0]}")
                    logger.info(f"[ROTATE] [SMART] Reordering queue: {current_account[0]} -> Others")
                    chrome_accounts = list(chrome_accounts)  # Copy
                    chrome_accounts.remove(current_account)
                    chrome_accounts.insert(0, current_account)
                else:
                    logger.info(f"[ROTATE] [SMART] Current channel {current_channel_id} not in rotation list")
            else:
                logger.info("[ROTATE] [SMART] Not currently on a Studio channel page")

        except Exception as e:
            logger.warning(f"[ROTATE] [SMART] Failed to detect current state: {e}")

        return chrome_accounts

    async def _verify_and_retry_engagement(
        self,
        driver,
        runner,
        channel_id: str,
        account_name: str,
        max_comments: int,
        browser_port: int,
        processed: int,
        strict_inbox: bool,
        error_text: Optional[str],
        session_recovered: bool
    ) -> int:
        """
        Verify inbox is clear and retry engagement if needed.
        """
        verify_retries = int(os.getenv("YT_INBOX_VERIFY_RETRIES", "1"))
        verify_timeout = float(os.getenv("YT_INBOX_VERIFY_TIMEOUT", "15"))
        verify_result = None

        for attempt in range(1, verify_retries + 1):
            verify_result = await self.verify_studio_inbox_clear(
                driver, channel_id, account_name, verify_timeout
            )

            if verify_result is True:
                break

            if verify_result is False:
                logger.warning(
                    f"[VERIFY] {account_name} inbox not clear; re-running engagement "
                    f"(attempt {attempt}/{verify_retries})"
                )
                self.set_active_channel(channel_id)
                self.log_studio_context(channel_id, f"{account_name} comment_engagement_retry", driver)

                retry_result = await runner.run_engagement(
                    channel_id=channel_id,
                    video_id=None,
                    max_comments=max_comments,
                    browser_port=browser_port,
                )

                retry_result = retry_result or {}
                retry_stats = retry_result.get('stats', {})
                retry_processed = retry_stats.get('comments_processed', 0)

                self.update_engagement_status(channel_id, {
                    "all_processed": bool(retry_stats.get("all_processed", False)),
                    "stats": retry_stats,
                    "error": retry_result.get('error'),
                    "updated_at": time.time(),
                })

                if retry_result.get('error'):
                    logger.error(f"[ROTATE] {account_name} retry failed: {retry_result.get('error')}")
                else:
                    logger.info(f"[ROTATE] {account_name} retry complete: {retry_processed} comments processed")

                processed += retry_processed
                continue

            logger.warning(f"[VERIFY] {account_name} inbox verification inconclusive; will recheck next cycle")
            break

        # Handle strict inbox mode results
        if strict_inbox:
            if verify_result is False:
                logger.warning(f"[VERIFY] Strict inbox mode: holding rotation on {account_name} (unprocessed comments)")
            elif verify_result is None:
                logger.info(f"[VERIFY] {account_name} verification inconclusive; continuing to next channel")

        return processed
