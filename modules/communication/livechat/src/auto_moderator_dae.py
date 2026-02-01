"""
Auto Moderator DAE (Domain Autonomous Entity)
WSP-Compliant: WSP 27 (Universal DAE Architecture), WSP 3 (Module Organization)

This is the WSP-compliant version using livechat_core.
Orchestrates all chat moderation components following DAE architecture.

NAVIGATION: YouTube DAE lifecycle orchestrator.
-> Called by: main.py::monitor_youtube
-> Delegates to: StreamResolver, LiveChatCore, youtube_auth credential handlers
-> Related: NAVIGATION.py -> MODULE_GRAPH["core_flows"]["stream_detection_flow"]
-> Quick ref: NAVIGATION.py -> NEED_TO["boot auto moderator dae"]
"""

import asyncio
import logging
import os
import re
import threading
import time
from datetime import datetime
from typing import Optional, Dict
from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
from modules.platform_integration.youtube_auth.src.monitored_youtube_service import create_monitored_service
from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver

# Import WSP-compliant livechat_core
from .livechat_core import LiveChatCore
# Channel -> credential mapping helper
from .persona_registry import resolve_channel_credential_set
# Import extracted services (WSP 72: Module Independence, WSP 62: Large File Refactoring)
from .stream_discovery_service import StreamDiscoveryService
from .multi_channel_coordinator import MultiChannelCoordinator
# Activity Router for breadcrumb-based activity coordination (WSP 77)
from modules.infrastructure.activity_control.src.activity_control import (
    get_activity_router, ActivityType
)

logger = logging.getLogger(__name__)


def _env_truthy(name: str, default: str = "false") -> bool:
    """Environment variable truthy check - WSP-compliant utility function."""
    try:
        value = os.getenv(name, default).strip().lower()
        return value in ("1", "true", "yes", "y", "on")
    except Exception:
        return default.strip().lower() in ("1", "true", "yes", "y", "on")


def _is_session_error(error_text: Optional[str]) -> bool:
    if not error_text:
        return False
    lowered = error_text.lower()
    return any(fragment in lowered for fragment in (
        "invalid session id",
        "not connected to devtools",
        "session deleted",
        "disconnected",
        "session not created",
        "cannot connect to chrome",
        "cannot connect to microsoft edge",
    ))


class AutoModeratorDAE:
    """
    WSP-Compliant Auto Moderator DAE
    
    Phases per WSP 27:
    -1: Signal - YouTube chat messages
     0: Knowledge - User profiles, chat history
     1: Protocol - Moderation rules, consciousness responses
     2: Agentic - Autonomous moderation and interaction
    """
    
    def __init__(self, enable_ai_monitoring: bool = False):
        """
        Initialize the Auto Moderator DAE.

        Args:
            enable_ai_monitoring: Enable AI Overseer (Qwen/Gemma) monitoring for error detection
        """
        logger.info("[ROCKET] Initializing Auto Moderator DAE (WSP-Compliant)")

        self.service = None
        self.credentials = None
        self.credential_set = None
        self.livechat = None
        self.stream_resolver = None
        self._last_stream_id = None
        self.transition_start = None
        self.start_time = time.time()
        self.enable_ai_monitoring = enable_ai_monitoring
        self.heartbeat_service = None

        # Comment engagement subprocess tracking (prevent dual-process race condition)
        self._comment_engagement_task = None  # Active async task reference
        self._live_chat_active = False  # Mutex: True when live chat monitoring active
        self._comment_engagement_status = {}
        self._comment_engagement_active_channel = None
        self._live_stream_pending = False

        # Extracted services (WSP 62: Large File Refactoring)
        self.multi_channel_coordinator = None  # Lazy init

        # YouTube DAE Telemetry Store (WSP 91: DAEMON Observability)
        try:
            from .youtube_telemetry_store import YouTubeTelemetryStore
            self.telemetry = YouTubeTelemetryStore()
            logger.info("[DATA] YouTube DAE telemetry store initialized")
        except Exception as e:
            logger.warning(f"Telemetry store initialization failed: {e}")
            self.telemetry = None

        # Stream tracking for telemetry
        self.current_stream_id = None  # SQLite stream session ID
        self.last_heartbeat_time = time.time()
        
        # WRE Integration for recursive learning
        if _env_truthy("FOUNDUPS_ENABLE_WRE", "true"):
            try:
                from modules.infrastructure.wre_core.recursive_improvement.src.wre_integration import (
                    record_error, record_success, get_optimized_approach
                )
                self.wre_record_error = record_error
                self.wre_record_success = record_success
                self.wre_get_optimized = get_optimized_approach
                logger.info("[0102] WRE Recursive Learning connected to DAE")
            except Exception as e:
                logger.debug(f"WRE Integration not available: {e}")
                self.wre_record_error = None
                self.wre_record_success = None
                self.wre_get_optimized = None
        else:
            logger.info("[0102] WRE disabled (FOUNDUPS_ENABLE_WRE=0)")
            self.wre_record_error = None
            self.wre_record_success = None
            self.wre_get_optimized = None

        # QWEN Intelligence Integration for smart decision making
        if _env_truthy("FOUNDUPS_ENABLE_QWEN", "true"):
            try:
                from holo_index.qwen_advisor.intelligent_monitor import IntelligentMonitor, MonitoringContext
                from holo_index.qwen_advisor.rules_engine import ComplianceRulesEngine
                self.qwen_monitor = IntelligentMonitor()
                self.qwen_rules = ComplianceRulesEngine()
                self.MonitoringContext = MonitoringContext  # Store class reference for later use
                logger.info("[BOT][AI] [QWEN-DAE] Intelligence layer connected - YouTube DAE now has a brain")
            except Exception as e:
                logger.debug(f"[BOT][AI] [QWEN-DAE] Integration not available: {e}")
                self.qwen_monitor = None
                self.qwen_rules = None
                self.MonitoringContext = None
        else:
            logger.info("[BOT][AI] [QWEN-DAE] Disabled (FOUNDUPS_ENABLE_QWEN=0)")
            self.qwen_monitor = None
            self.qwen_rules = None
            self.MonitoringContext = None

        # QWEN YouTube Integration for channel prioritization
        if _env_truthy("FOUNDUPS_ENABLE_QWEN", "true"):
            try:
                from .qwen_youtube_integration import get_qwen_youtube
                self.qwen_youtube = get_qwen_youtube()  # Use singleton for shared intelligence
                logger.info("[BOT][AI] [QWEN-YOUTUBE] Channel prioritization intelligence connected")
            except Exception as e:
                logger.debug(f"[BOT][AI] [QWEN-YOUTUBE] Integration not available: {e}")
                self.qwen_youtube = None
        else:
            self.qwen_youtube = None

        self.high_priority_pending = False
        self.priority_reason = None

        # Community Monitor for YouTube comments (Phase 3 integration)
        self.community_monitor = None  # Initialized in run() when channel_id is known

        # AI Overseer singleton (initialized once, reused forever - saves 490-505ms every 5 minutes)
        self.ai_overseer = None  # Lazy init on first heartbeat

        # Phase 4H: Account rotation for Studio logic
        self.current_studio_channel_index = 0
        self.studio_runner = None
        self.studio_repo_root = None
        # Rotation cycle tracking - when all 4 done, trigger shorts scheduling
        self._rotation_processed_channels: set = set()
        self._shorts_scheduling_triggered = False

        # Shorts scheduling health tracking (2026-01-29: Hardened diagnostics)
        self._shorts_scheduler_available = False
        self._shorts_last_cycle_result = None  # {"timestamp", "total_scheduled", "channels", "errors"}
        self._shorts_total_cycles = 0
        self._shorts_total_scheduled = 0
        try:
            from modules.platform_integration.youtube_shorts_scheduler.src.scheduler import YouTubeShortsScheduler
            self._shorts_scheduler_available = True
            logger.info("[SHORTS] Scheduler module: AVAILABLE (YouTubeShortsScheduler imported OK)")
        except ImportError as ie:
            logger.warning(f"[SHORTS] Scheduler module: NOT AVAILABLE ({ie})")
            logger.warning("[SHORTS] Shorts scheduling will be SKIPPED in comment engagement loop")
        except Exception as e:
            logger.warning(f"[SHORTS] Scheduler module: IMPORT ERROR ({e})")

        # Extracted services (WSP 72: Module Independence)
        self.stream_discovery_service: Optional[StreamDiscoveryService] = None  # Lazy init

        logger.info("[OK] Auto Moderator DAE initialized")

    @staticmethod
    def _studio_channel_id_from_url(url: str) -> Optional[str]:
        if not url:
            return None
        match = re.search(r"studio\.youtube\.com/channel/([^/?#]+)/comments", url)
        return match.group(1) if match else None

    @classmethod
    def _is_studio_comments_url(cls, url: str) -> bool:
        return bool(cls._studio_channel_id_from_url(url))

    def _log_studio_context(self, channel_id: str, label: str = "", driver=None) -> None:
        url = None
        if driver is not None:
            try:
                url = driver.current_url
            except Exception:
                url = None

        if not url:
            try:
                from modules.infrastructure.foundups_vision.src.studio_account_switcher import get_account_switcher
                switcher = get_account_switcher()
                if switcher._connect_to_chrome():
                    url = switcher.driver.current_url
            except Exception as e:
                logger.debug(f"[STUDIO] Unable to read Studio URL: {e}")

        label_text = f" {label}" if label else ""
        if url:
            url_channel_id = self._studio_channel_id_from_url(url) or "unknown"
            url_base = url.split("#", 1)[0].split("?", 1)[0]
            logger.info(f"[STUDIO]{label_text} channel_id={channel_id} url={url_base} url_channel_id={url_channel_id}")
        else:
            logger.info(f"[STUDIO]{label_text} channel_id={channel_id} url=unknown")

    async def _verify_studio_inbox_clear(
        self,
        driver,
        channel_id: str,
        account_name: str,
        timeout_seconds: float,
    ) -> Optional[bool]:
        if not driver:
            logger.warning(f"[VERIFY] {account_name} inbox check skipped: no browser driver")
            return None

        target_url = f"https://studio.youtube.com/channel/{channel_id}/comments/inbox"
        try:
            current_url = driver.current_url
        except Exception as e:
            logger.warning(f"[VERIFY] {account_name} inbox check skipped: browser session error ({e})")
            return None

        if target_url not in (current_url or ""):
            logger.info(f"[VERIFY] Navigating to {account_name} inbox for final check: {target_url}")
            try:
                driver.get(target_url)
            except Exception as e:
                logger.warning(f"[VERIFY] {account_name} inbox navigation failed: {e}")
                return None
            await asyncio.sleep(5)

        self._log_studio_context(channel_id, label=f"{account_name} verify", driver=driver)

        start_time = time.time()
        last_count = None
        while (time.time() - start_time) < timeout_seconds:
            try:
                last_count = driver.execute_script(
                    "return document.querySelectorAll('ytcp-comment-thread').length"
                )
            except Exception as e:
                logger.warning(f"[VERIFY] {account_name} DOM count failed: {e}")
                return None

            if last_count and last_count > 0:
                logger.info(f"[VERIFY] {account_name} inbox NOT clear (threads={last_count})")
                return False

            try:
                permission_error = bool(driver.execute_script(
                    "const t=(document.body&&document.body.innerText)||'';"
                    "return t.includes(\"don't have permission\") || t.includes('Oops, you don\\'t have permission');"
                ))
            except Exception:
                permission_error = False

            if permission_error:
                logger.warning(f"[VERIFY] {account_name} permission error page - cannot verify inbox")
                return None

            try:
                empty_state = bool(driver.execute_script(
                    "const emptySelectors = ["
                    "'ytcp-comments-empty-state',"
                    "'.empty-state-content',"
                    "'[data-empty-state]',"
                    "'.ytcp-comment-surface-empty'"
                    "];"
                    "for (const sel of emptySelectors) {"
                    "  if (document.querySelector(sel)) return true;"
                    "}"
                    "const bodyText = (document.body && document.body.innerText) || '';"
                    "return bodyText.includes('No comments to respond to') || "
                    "bodyText.includes('All caught up') || "
                    "bodyText.includes('No new comments');"
                ))
            except Exception:
                empty_state = False

            if empty_state:
                logger.info(f"[VERIFY] {account_name} inbox empty state confirmed")
                return True

            await asyncio.sleep(0.5)

        logger.warning(f"[VERIFY] {account_name} inbox verification timeout (last_count={last_count})")
        return None

    async def _reconnect_chrome_driver(self, chrome_port: int):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from modules.infrastructure.dependency_launcher.src.dae_dependencies import launch_chrome

            chrome_ok, chrome_msg = launch_chrome()
            if not chrome_ok:
                logger.warning(f"[ROTATE] Chrome auto-launch failed: {chrome_msg}")
                return None

            opts = Options()
            opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_port}")
            return await asyncio.to_thread(webdriver.Chrome, options=opts)
        except Exception as e:
            logger.warning(f"[ROTATE] Chrome reconnect failed: {e}")
            return None

    async def _reconnect_edge_driver(self, edge_port: int):
        try:
            from selenium import webdriver
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from modules.infrastructure.dependency_launcher.src.dae_dependencies import launch_edge

            edge_ok, edge_msg = launch_edge()
            if not edge_ok:
                logger.warning(f"[ROTATE] Edge auto-launch failed: {edge_msg}")
                return None

            edge_opts = EdgeOptions()
            edge_opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{edge_port}")
            return await asyncio.to_thread(webdriver.Edge, options=edge_opts)
        except Exception as e:
            logger.warning(f"[ROTATE] Edge reconnect failed: {e}")
            return None
    
    def connect(self) -> bool:
        """
        Phase -1/0: Connect to YouTube - NO-QUOTA mode by default.
        Only use API tokens when we actually find a stream.
        AUTOMATICALLY REFRESHES TOKENS on startup to keep them fresh!

        Returns:
            Success status
        """
        logger.info("[NO-QUOTA] Starting in NO-QUOTA mode to preserve API tokens...")

        # TOKEN REFRESH DISABLED DURING STARTUP - Prevents blocking on OAuth
        # Token refresh should be done before starting the daemon using:
        # python modules/platform_integration/youtube_auth/scripts/auto_refresh_tokens.py
        logger.info("[IDEA] Token refresh happens on-demand when authentication is needed")
        logger.info("   To manually refresh: python modules/platform_integration/youtube_auth/scripts/auto_refresh_tokens.py")

        # Default to NO-QUOTA mode for stream searching
        # We'll only authenticate when we actually find a stream
        self.service = None
        self.credential_set = "NO-QUOTA"
        logger.info("[NO-QUOTA] Using web scraping for stream discovery")
        logger.info("[NO-QUOTA] Smart verification: NO-QUOTA first, API only for live/uncertain videos")
        logger.info("[NO-QUOTA] Maximum API preservation - API only when posting is possible")

        return True
    
    def find_livestream(self) -> Optional[Dict[str, Optional[str]]]:
        """
        Find active livestream on the channel.
        Delegates to StreamDiscoveryService (WSP 72: Module Independence).

        Returns:
            Stream metadata dict containing video_id, live_chat_id, channel_id, and channel_name, or None
        """
        # Lazy init StreamDiscoveryService
        if not self.stream_discovery_service:
            self.stream_discovery_service = StreamDiscoveryService(
                service=self.service,
                telemetry=self.telemetry,
                qwen_monitor=self.qwen_monitor,
                qwen_youtube=self.qwen_youtube,
                monitoring_context_class=self.MonitoringContext,
            )
            # Sync last stream ID for duplicate detection
            self.stream_discovery_service.set_last_stream_id(self._last_stream_id)

        # Delegate to service
        result = self.stream_discovery_service.find_livestream()

        # Sync state back from service
        if result:
            self._last_stream_id = result.get('video_id')
            self.current_stream_id = self.stream_discovery_service.get_current_stream_id()
            self.high_priority_pending = self.stream_discovery_service.high_priority_pending
            self.priority_reason = self.stream_discovery_service.priority_reason
            # Share stream_resolver for monitor_chat
            self.stream_resolver = self.stream_discovery_service.stream_resolver

        return result

    async def monitor_chat(self):
        """
        Phase 2: Autonomous chat monitoring and moderation.

        This is the main execution loop with intelligent throttling.
        Returns when stream ends/becomes inactive for seamless switching.
        """
        # Import the intelligent delay calculator and trigger
        # WSP 3 Phase 4: calculate_enhanced_delay moved to infrastructure/shared_utilities
        from modules.infrastructure.shared_utilities.delay_utils import DelayUtils
        delay_utils = DelayUtils()
        from modules.communication.livechat.src.stream_trigger import StreamTrigger, create_intelligent_delay
        
        # Initialize trigger mechanism
        trigger = StreamTrigger()
        trigger.create_trigger_instructions()
        
        # Keep looking for livestream until found
        retry_count = 0
        consecutive_failures = 0
        previous_delay = None
        quick_check_mode = False  # Flag for rapid checking after stream end
        
        while True:
            # Check for manual trigger
            if trigger.check_trigger():
                logger.info("[ALERT] Manual trigger detected! Checking for stream immediately...")
                consecutive_failures = 0  # Reset failures on manual trigger
                previous_delay = None
                trigger.reset()
            
            # Force fresh search if in quick check mode (after stream ended)
            if quick_check_mode:
                # Clear any cached data to ensure we find NEW streams
                if self.stream_resolver:
                    self.stream_resolver.clear_cache()
                    logger.info("[SEARCH] Quick check mode - cleared cache, searching for NEW stream")
            
            result = self.find_livestream()
            if result:
                # Reset counters on success
                retry_count = 0
                consecutive_failures = 0
                quick_check_mode = False  # Reset quick mode

                # Gate live chat handoff until the current inbox is cleared
                self._live_stream_pending = True
                if _env_truthy("YT_WAIT_FOR_INBOX_CLEAR", "true"):
                    await self._wait_for_inbox_clear()
                break
            
            # Calculate intelligent delay based on retries and failures
            if consecutive_failures > 0:
                # Exponential backoff for consecutive failures
                delay = min(60 * (2 ** (consecutive_failures - 1)), 1800)  # Max 30 mins
            else:
                # Normal retry interval
                delay = 300  # 5 minutes
            
            if not _env_truthy("YT_STREAM_RESOLVER_ENABLED", "true"):
                logger.debug(f"[SEARCH] Stream resolver DISABLED. Polling loop sleeping for {delay}s...")
            else:
                logger.info(f"[SEARCH] No live stream found. Retrying in {delay}s...")
            # Use trigger-aware delay for better idle behavior
            if quick_check_mode:
                priority_mode = getattr(self, 'high_priority_pending', False)
                base_step = 8 if priority_mode else 20
                max_quick = 24 if priority_mode else 45
                delay = min(max_quick, base_step * (consecutive_failures + 1))
                logger.info(f"[LIGHTNING] Quick check mode: Checking again in {delay}s for new stream")
            else:
                priority_mode = getattr(self, 'high_priority_pending', False)
                min_delay = 20.0 if priority_mode else 30.0
                max_delay = 120.0 if priority_mode else 600.0
                delay = create_intelligent_delay(
                    consecutive_failures=consecutive_failures,
                    previous_delay=previous_delay,
                    has_trigger=False,
                    min_delay=min_delay,
                    max_delay=max_delay
                )

                if priority_mode:
                    delay = min(delay, 90.0)
                    if self.priority_reason and consecutive_failures == 0:
                        logger.info(f"[BOT][AI] [QWEN-WATCH] {self.priority_reason}; tightening delay to {delay:.0f}s")

                # Show different messages based on delay length
                if delay < 60:
                    logger.info(f"[STREAM] No stream found. Checking again in {delay:.0f} seconds...")
                elif delay < 300:
                    logger.info(f"[IDLE] No stream found. Waiting {delay/60:.1f} minutes (adaptive idle)...")
                else:
                    logger.info(f"[IDLE] Idle mode: {delay/60:.1f} minutes (adaptive)")
            
            # Wait with intelligent delay, but check for triggers every 5 seconds
            elapsed = 0
            check_interval = 5  # Check for triggers every 5 seconds
            
            while elapsed < delay:
                # Wait for shorter interval
                wait_time = min(check_interval, delay - elapsed)
                await asyncio.sleep(wait_time)
                elapsed += wait_time
                
                # Check for trigger during wait
                if trigger.check_trigger():
                    logger.info("[ALERT] Trigger activated! Checking for stream now...")
                    consecutive_failures = 0  # Reset on trigger
                    previous_delay = None
                    trigger.reset()
                    break
            
            # Update counters
            retry_count += 1
            consecutive_failures += 1
            previous_delay = delay

            # HEALTH CHECK: Auto-restart comment engagement task if it crashed
            # 2026-01-30: The comment task can die from transient WebDriver errors,
            # network timeouts, or unhandled exceptions.  Without this watchdog,
            # commenting stops forever until the process is manually restarted.
            if self._comment_engagement_task and self._comment_engagement_task.done():
                # Retrieve and log the exception that killed the task
                try:
                    exc = self._comment_engagement_task.exception()
                    logger.error(f"[WATCHDOG] Comment engagement task CRASHED: {exc}", exc_info=exc)
                except (asyncio.CancelledError, asyncio.InvalidStateError):
                    logger.warning("[WATCHDOG] Comment engagement task ended (cancelled or invalid state)")

                # RESTART the task
                if self.studio_runner:
                    interval_minutes = int(os.getenv("COMMUNITY_ENGAGEMENT_INTERVAL_MINUTES", "10"))
                    exec_mode = os.getenv("COMMUNITY_EXEC_MODE", "subprocess")
                    startup_max = int(os.getenv("COMMUNITY_STARTUP_MAX_COMMENTS", "0"))
                    logger.info(f"[WATCHDOG] RESTARTING comment engagement task (interval={interval_minutes}m, mode={exec_mode})")
                    self._comment_engagement_task = asyncio.create_task(
                        self._comment_engagement_loop(
                            self.studio_runner,
                            max_comments=startup_max,
                            mode=exec_mode,
                            interval_minutes=interval_minutes,
                        )
                    )
                    logger.info("[WATCHDOG] Comment engagement task RESTARTED successfully")
                else:
                    logger.error("[WATCHDOG] Cannot restart comment engagement - no studio_runner available")

            # Phase 4H: ACCOUNT ROTATION FALLBACK
            # If no live stream found, switch account to process Studio comments for others
            if not result and _env_truthy("YT_ACCOUNT_ROTATION_ENABLED", "true"):
                logger.info("[ROTATE] No live streams found on any channel. Rotating Studio account...")
                try:
                    # Skip rotation while comment engagement is active
                    if self._comment_engagement_task and not self._comment_engagement_task.done():
                        logger.info("[ROTATE] Comment engagement active - skipping Studio account rotation")
                    else:
                        from modules.infrastructure.foundups_vision.src.studio_account_switcher import get_account_switcher
                        switcher = get_account_switcher()

                        skip_rotation = False
                        # If already on a Studio comments page, avoid rotating away
                        if _env_truthy("YT_STUDIO_LOCK_ON_COMMENTS", "true"):
                            if switcher._connect_to_chrome():
                                current_url = switcher.driver.current_url
                                if self._is_studio_comments_url(current_url):
                                    permission_error = False
                                    try:
                                        permission_error = bool(switcher.driver.execute_script(
                                            "const t=(document.body&&document.body.innerText)||'';"
                                            "return t.includes(\"don't have permission\") || "
                                            "t.includes('Oops, you don\\'t have permission');"
                                        ))
                                    except Exception:
                                        permission_error = False
                                    if permission_error:
                                        logger.warning("[ROTATE] Studio comments page shows permission error - allowing rotation")
                                    else:
                                        logger.info(f"[ROTATE] Studio comments page active ({current_url}) - skipping rotation")
                                        skip_rotation = True
                        if skip_rotation:
                            continue

                        # Channels to rotate through (names matching StudioAccountSwitcher list)
                        # Chrome (9222): Move2Japan, UnDaoDu | Edge (9223): FoundUps, RavingANTIFA
                        rotation_accounts = ["Move2Japan", "UnDaoDu", "FoundUps", "RavingANTIFA"]
                        self.current_studio_channel_index = (self.current_studio_channel_index + 1) % len(rotation_accounts)
                        target_account = rotation_accounts[self.current_studio_channel_index]

                        logger.info(f"[ROTATE] Switching Studio account to: {target_account} (Index {self.current_studio_channel_index})")
                        switch_result = await switcher.switch_to_account(target_account)

                        if switch_result.get("success"):
                            logger.info(f"[ROTATE] ✅ Successfully switched to {target_account}")

                            # Restart comment engagement for the new account
                            if self.studio_runner:
                                # Kill existing task if any
                                await self.terminate_comment_engagement()

                                target_channel_id = switch_result.get("channel_id")
                                exec_mode = os.getenv("COMMUNITY_EXEC_MODE", "subprocess")
                                startup_max = int(os.getenv("COMMUNITY_STARTUP_MAX_COMMENTS", "0"))

                                logger.info(f"[ROTATE] Starting comment engagement for {target_account} ({target_channel_id})...")
                                self._comment_engagement_task = asyncio.create_task(
                                    self._run_comment_engagement(self.studio_runner, target_channel_id, video_id=None, max_comments=startup_max, mode=exec_mode)
                                )
                        else:
                            logger.warning(f"[ROTATE] ⚠️ Account switch failed: {switch_result.get('error')}")

                except Exception as e:
                    logger.error(f"[ROTATE] ❌ Account rotation error: {e}")
        
        # Normalize result into dict (resolve_stream can return a tuple in some branches)
        if isinstance(result, tuple):
            # Tuple format: (video_id, chat_id)
            video_id, chat_id = (result + (None, None))[:2] if isinstance(result, tuple) else (None, None)
            result = {
                'video_id': video_id,
                'live_chat_id': chat_id,
                'channel_id': None,
                'channel_name': 'Unknown (tuple)'
            }

        stream_info = result or {}
        video_id = stream_info.get('video_id')
        live_chat_id = stream_info.get('live_chat_id')
        channel_id = stream_info.get('channel_id') or os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')
        channel_name = stream_info.get('channel_name') or 'Default Channel'

        # Set current_video_id for heartbeat tracking (fixes "Stream: None" issue)
        self.current_video_id = video_id
        logger.info(f"[FLOW-TRACE] Set current_video_id={video_id}")

        # Now that we found a stream, try to authenticate for full functionality
        # Authenticate FIRST, then get chat_id with API
        if not self.service and video_id:
            logger.info("[AUTH] Stream found! Attempting authentication for chat interaction...")
            try:
                force_set_raw = os.getenv("YT_FORCE_CREDENTIAL_SET", "").strip()
                token_index = None
                if force_set_raw:
                    try:
                        token_index = int(force_set_raw)
                        if token_index <= 0:
                            token_index = None
                            logger.warning(f"[AUTH] Invalid YT_FORCE_CREDENTIAL_SET={force_set_raw}; using auto-rotation")
                        else:
                            logger.info(f"[AUTH] Forcing credential set {token_index} (YT_FORCE_CREDENTIAL_SET)")
                    except ValueError:
                        logger.warning(f"[AUTH] Invalid YT_FORCE_CREDENTIAL_SET={force_set_raw}; using auto-rotation")
                if token_index is None:
                    pinned_set = resolve_channel_credential_set(
                        channel_name=channel_name,
                        channel_id=channel_id,
                    )
                    if pinned_set:
                        token_index = pinned_set
                        logger.info(f"[AUTH] Pinning credential set {token_index} for channel {channel_name}")
                service = get_authenticated_service(token_index=token_index) if token_index else get_authenticated_service()
                if service:
                    self.service = create_monitored_service(service)
                    self.credential_set = getattr(service, '_credential_set', "Unknown")
                    logger.info(f"[OK] Authenticated with credential set {self.credential_set}")

                    # Now try to get the chat_id with authenticated service
                    if not live_chat_id:
                        logger.info("[SEARCH] Getting chat ID with authenticated service...")
                        # Update existing resolver's service instead of creating new instance (prevents rapid init loop)
                        if self.stream_resolver:
                            self.stream_resolver.service = self.service
                        else:
                            self.stream_resolver = StreamResolver(self.service)
                        target_channel_id = channel_id or os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')
                        auth_result = self.stream_resolver.resolve_stream(target_channel_id)
                        if auth_result and len(auth_result) > 1:
                            resolved_video_id = auth_result[0]
                            if resolved_video_id and resolved_video_id != video_id:
                                logger.info(f"[API] Resolved stream {resolved_video_id} (replacing {video_id})")
                                video_id = resolved_video_id
                                stream_info['video_id'] = video_id
                            live_chat_id = auth_result[1]
                            stream_info['live_chat_id'] = live_chat_id
                            logger.info(f"[OK] Got chat ID with API: {live_chat_id[:20]}...")
                        else:
                            logger.warning("[WARN] Could not get chat ID even with API")
            except Exception as e:
                logger.warning(f"[WARN] Authentication failed: {e}")
                logger.info("[NO-QUOTA] Continuing in NO-QUOTA mode (view-only)")

        # WRE Monitor: Track stream transition completion
        if hasattr(self, 'wre_monitor') and self.wre_monitor:
            if self._last_stream_id and self.transition_start:
                transition_time = time.time() - self.transition_start
                self.wre_monitor.track_stream_transition(self._last_stream_id, video_id, transition_time)
            self._last_stream_id = video_id
            self.transition_start = time.time()

        # Create LiveChatCore instance
        self.livechat = LiveChatCore(
            youtube_service=self.service,
            video_id=video_id,
            live_chat_id=live_chat_id,
            channel_name=channel_name,
            channel_id=channel_id
        )

        # Initialize LiveChatCore (THIS TRIGGERS SOCIAL MEDIA POSTS!)
        logger.info("[ROCKET] Initializing LiveChatCore (includes social media posting)...")
        await self.livechat.initialize()

        # Phase 3: Initialize (or update) Community Monitor for YouTube comments
        # Phase 3P: Build channel rotation list for 24/7 processing
        channels_override = os.getenv("YT_CHANNELS_TO_CHECK", "").strip()
        if channels_override:
            all_channels = [ch.strip() for ch in channels_override.split(",") if ch.strip()]
        else:
            all_channels = [
                os.getenv('UNDAODU_CHANNEL_ID', 'UCfHM9Fw9HD-NwiS0seD_oIA'),   # UnDaoDu - PRIORITY 1 (active agent)
                os.getenv('RAVINGANTIFA_CHANNEL_ID', 'UCVSmg5aOhP4tnQ9KFUg97qA'),  # RavingANTIFA - PRIORITY 2 (cross-promo target)
                os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw'),  # Move2Japan - PRIORITY 3
                os.getenv('FOUNDUPS_CHANNEL_ID', 'UCSNTUXjAgpd4sgWYP0xoJgw'),  # FoundUps - PRIORITY 4
            ]
        all_channels = [ch for ch in all_channels if ch]  # Filter empty strings

        try:
            from .community_monitor import get_community_monitor
            self.community_monitor = get_community_monitor(
                channel_id=channel_id,
                chat_sender=self.livechat,  # For posting announcements
                telemetry_store=self.telemetry,  # For tracking stats
                all_channels=all_channels  # Phase 3P: Channel rotation list
            )
            logger.info(f"[COMMUNITY] Monitor initialized for {len(all_channels)} channels (24/7 rotation)")

            # Phase 3R (2025-12-24): Set live stream priority for comment processing
            # CRITICAL: Commenting follows live chat (not round-robin rotation)
            if self.community_monitor and video_id:
                self.community_monitor.set_live_priority(channel_id, video_id)
                logger.info(f"[COMMUNITY] 🎯 Live priority set for comment processing")
                logger.info(f"[COMMUNITY]   Channel: {channel_id}")
                logger.info(f"[COMMUNITY]   Video: {video_id}")
        except Exception as e:
            logger.warning(f"[COMMUNITY] Failed to initialize monitor: {e}")
            self.community_monitor = None

        # Phase 4: Comment engagement is DISABLED during live chat
        # User requirement: "Once on live chat, do NOT return to comments"
        # Comment engagement runs ONLY at startup, before first stream found
        logger.info("[LOCK] Comment engagement DISABLED during live chat (user requirement)")

        # Start monitoring
        logger.info("="*60)
        logger.info("MONITORING CHAT - WSP-COMPLIANT ARCHITECTURE")
        logger.info("="*60)

        # === CRITICAL: Terminate comment engagement BEFORE starting live chat ===
        # Prevents dual-process race condition (user requirement: lock to live chat only)
        await self.terminate_comment_engagement()
        self._live_stream_pending = False
        self._live_chat_active = True
        logger.info("[LOCK] Live chat mode ACTIVE - comment engagement DISABLED")

        # === CARDIOVASCULAR: Start heartbeat task (WSP 91) ===
        heartbeat_task = None
        if self.telemetry:
            heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info("[HEART] Heartbeat monitoring started (30s interval)")

        try:
            await self.livechat.start_listening()
        except KeyboardInterrupt:
            logger.info("[STOP] Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        finally:
            # === CARDIOVASCULAR: Stop heartbeat and record stream end (WSP 91) ===
            if heartbeat_task:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass
                logger.info("[HEART] Heartbeat monitoring stopped")

            # === CRITICAL: Reset live chat mutex (allow comment engagement restart) ===
            self._live_chat_active = False
            logger.info("[LOCK] Live chat mode INACTIVE - comment engagement can restart")

            if self.telemetry and self.current_stream_id:
                try:
                    self.telemetry.record_stream_end(self.current_stream_id)
                    logger.info(f"[HEART] Stream session ended (SQLite ID: {self.current_stream_id})")
                    self.current_stream_id = None
                except Exception as e:
                    logger.warning(f"Failed to record stream end: {e}")

            if self.livechat:
                self.livechat.stop_listening()

    async def terminate_comment_engagement(self):
        """
        Terminate any running comment engagement subprocess (prevent dual-process race condition).

        Called when switching from comment processing to live chat monitoring.
        WSP 49: Process isolation - ensure only ONE mode active at a time.
        """
        if self._comment_engagement_task and not self._comment_engagement_task.done():
            logger.info("[LOCK] Terminating comment engagement subprocess (switching to live chat)...")
            self._comment_engagement_task.cancel()
            try:
                await self._comment_engagement_task
            except asyncio.CancelledError:
                logger.info("[OK] Comment engagement subprocess terminated successfully")
            except Exception as e:
                logger.warning(f"[WARN] Comment engagement termination exception: {e}")
            self._comment_engagement_task = None
        else:
            logger.debug("[LOCK] No active comment engagement subprocess to terminate")

    async def _wait_for_inbox_clear(self):
        """
        Wait until the current Studio inbox is cleared before switching to live chat.

        This prevents account rotation or live chat takeover from interrupting
        a partially processed comments backlog.
        
        FIX (2025-12-31): Changed default from 0 (infinite) to 60 seconds.
        With UNLIMITED comment mode having 2-hour timeout, 0 would block live chat forever.
        """
        # FIX: Default to 60 seconds instead of 0 (infinite) to prevent blocking live chat forever
        timeout_seconds = int(os.getenv("YT_INBOX_CLEAR_TIMEOUT", "60"))
        start_time = time.time()

        logger.info(f"[LOCK] Live stream detected - waiting for inbox clear (timeout: {timeout_seconds}s)")

        # When a live stream is detected, ensure Edge channels (FoundUps → RavingANTIFA) have
        # at least been ATTEMPTED once before handing off to live chat. Otherwise we can switch
        # to live chat immediately (no active channel set yet) and starve those channels.
        # WSP 50: never assume 'no active channel' means work is complete.
        required_edge_channels = []
        try:
            required_edge_channels = [
                os.getenv("FOUNDUPS_CHANNEL_ID", "").strip(),
                os.getenv("RAVINGANTIFA_CHANNEL_ID", "").strip(),
            ]
            required_edge_channels = [c for c in required_edge_channels if c]
        except Exception:
            required_edge_channels = []

        while True:
            # If engagement is still running, wait it out.
            if self._comment_engagement_task and not self._comment_engagement_task.done():
                await asyncio.sleep(5)
            else:
                channel_id = self._comment_engagement_active_channel
                status = self._comment_engagement_status.get(channel_id or "", {})

                if channel_id and status.get("all_processed"):
                    logger.info(f"[LOCK] Inbox clear for channel {channel_id} - continuing to live chat")
                    return

                if not channel_id:
                    # If we have required Edge channels, wait until we have at least one status update
                    # for each (attempted), or until timeout.
                    if required_edge_channels:
                        missing = [c for c in required_edge_channels if c not in self._comment_engagement_status]
                        if missing:
                            logger.info(
                                "[LOCK] No active channel yet; waiting for Edge comment attempt(s) before live chat. missing=%s",
                                missing,
                            )
                            await asyncio.sleep(5)
                            continue
                    logger.warning("[LOCK] No active channel for inbox-clear check; proceeding to live chat")
                    return

                if not self.studio_runner:
                    logger.warning("[LOCK] Comment engagement runner unavailable; proceeding to live chat")
                    return

                logger.info(f"[LOCK] Inbox not clear for {channel_id}; re-running comment engagement")
                exec_mode = os.getenv("COMMUNITY_EXEC_MODE", "subprocess")
                startup_max = int(os.getenv("COMMUNITY_STARTUP_MAX_COMMENTS", "0"))
                self._comment_engagement_task = asyncio.create_task(
                    self._run_comment_engagement(
                        self.studio_runner,
                        channel_id,
                        video_id=None,
                        max_comments=startup_max,
                        mode=exec_mode,
                    )
                )
                await asyncio.sleep(5)

            if timeout_seconds and (time.time() - start_time) > timeout_seconds:
                logger.warning("[LOCK] Inbox-clear wait timed out; proceeding to live chat")
                return

    async def _run_comment_engagement(
        self,
        runner,
        channel_id: str,
        video_id: str,
        max_comments: int,
        mode: str
    ):
        """
        Run comment engagement with pluggable execution strategy.

        Sprint 1+2: Execution modes (subprocess|thread|inproc)
        - subprocess: Safest (SIGKILL guarantee), default
        - thread: Fast startup (<500ms), acceptable risk
        - inproc: Debug only (blocks event loop)

        This method is launched as an async task and does not block main DAE.
        """
        logger.info(f"[DAEMON][CARDIOVASCULAR] 🎬 _run_comment_engagement STARTED")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Channel: {channel_id}")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Video ID: {video_id}")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Max comments: {max_comments}")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Mode: {mode}")

        self._comment_engagement_active_channel = channel_id

        try:
            logger.info(f"[DAEMON][CARDIOVASCULAR] 🚀 Calling runner.run_engagement()...")
            self._log_studio_context(channel_id, label="comment_engagement")
            result = await runner.run_engagement(
                channel_id=channel_id,
                video_id=video_id,
                max_comments=max_comments
            )
            logger.info(f"[DAEMON][CARDIOVASCULAR] ✅ runner.run_engagement() returned!")

            # Log result
            result = result or {}
            stats = result.get('stats', {})
            error = result.get('error')

            self._comment_engagement_status[channel_id] = {
                "all_processed": bool(stats.get("all_processed", False)),
                "stats": stats,
                "error": error,
                "updated_at": time.time(),
            }

            if error:
                logger.error(f"[COMMUNITY] Engagement failed ({mode}): {error}")
                logger.error(f"[COMMUNITY] Stats: {stats}")
            else:
                logger.info(f"[COMMUNITY] Engagement complete ({mode}): {stats}")

        except Exception as e:
            logger.error(f"[COMMUNITY] Engagement exception ({mode}): {e}", exc_info=True)
            self._comment_engagement_status[channel_id] = {
                "all_processed": False,
                "stats": {},
                "error": str(e),
                "updated_at": time.time(),
            }

    async def _detect_current_channel_id(self, driver) -> Optional[str]:
        """
        Robustly detect the current channel ID from the browser state.
        Tries script execution first (most reliable), then improved regex.
        """
        if not driver:
            return None
            
        # 1. Try script execution (Internal YouTube config)
        try:
            channel_id = driver.execute_script(
                "return (window.yt && window.yt.config_ && window.yt.config_.CHANNEL_ID) || "
                "(window.ytcfg && typeof window.ytcfg.get === 'function' && window.ytcfg.get('CHANNEL_ID')) || "
                "null;"
            )
            if channel_id:
                logger.debug(f"[DETECT] Found channel ID via script: {channel_id}")
                return channel_id
        except Exception as e:
            logger.debug(f"[DETECT] Script detection failed: {e}")

        # 2. Try improved URL regex
        try:
            url = driver.current_url
            if not url:
                return None
                
            # Pattern 1: /channel/CHANNEL_ID/...
            match = re.search(r"studio\.youtube\.com/channel/([^/?#]+)", url)
            if match:
                return match.group(1)
                
            # Pattern 2: /video/VIDEO_ID/comments?d=CHANNEL_ID (sometimes present)
            # Pattern 3: Main site channel URLs
            match = re.search(r"youtube\.com/channel/([^/?#]+)", url)
            if match:
                return match.group(1)
        except Exception as e:
            logger.debug(f"[DETECT] URL detection failed: {e}")

        return None

    # NOTE: _studio_channel_id_from_url is defined at class top as @staticmethod (line 161-166)
    # This duplicate instance method was removed 2025-12-29 - was causing:
    # "missing 1 required positional argument: 'url'" when called via cls from @classmethod
    # Use _detect_current_channel_id(driver) for robust channel detection instead.

    async def _comment_engagement_loop(
        self,
        runner,
        max_comments: int,
        mode: str,
        interval_minutes: int = 10
    ):
        """
        INDEPENDENT comment engagement loop - runs regardless of stream state.

        Architecture (2026-01-30 Refactor — Per-Browser Parallel Loops):
        - Launches TWO independent loops: one for Chrome, one for Edge
        - Each browser cycles: Comments → Scheduling → Sleep independently
        - Chrome does NOT block Edge (and vice versa)
        - Phase 3 scheduling runs immediately after THAT browser's comments finish

        Previous architecture (2025-12-30 → 2026-01-29):
        - Single loop: Phase 1 (ALL comments) → Phase 3 (ALL scheduling) → sleep
        - Problem: Phase 1 blocked Phase 3 for up to 1 hour (UNLIMITED comments)

        Args:
            runner: EngagementRunner instance
            max_comments: Max comments per channel (0=UNLIMITED)
            mode: Execution mode (subprocess/thread/inproc)
            interval_minutes: Minutes between engagement cycles (default: 10)
        """
        logger.info("=" * 70)
        logger.info("[COMMENT-LOOP] PER-BROWSER PARALLEL ENGAGEMENT LOOPS STARTING")
        logger.info(f"[COMMENT-LOOP] Interval: {interval_minutes} minutes | Mode: {mode}")
        logger.info(f"[COMMENT-LOOP] Max per channel: {max_comments if max_comments > 0 else 'UNLIMITED'}")
        logger.info("[COMMENT-LOOP] Architecture: Each browser runs Comments → Scheduling independently")
        logger.info("[COMMENT-LOOP]   Chrome (9222): Move2Japan, UnDaoDu  → schedule → sleep")
        logger.info("[COMMENT-LOOP]   Edge   (9223): FoundUps, RavingANTIFA → schedule → sleep")
        logger.info("[COMMENT-LOOP] Neither browser blocks the other")
        logger.info("=" * 70)

        # TOP-LEVEL RESILIENCE with INDEPENDENT LOOP SUPERVISION
        # 2026-01-30: Each browser loop is supervised independently.
        # If Chrome crashes, Edge keeps running (and vice versa).
        # Previously asyncio.gather() would cancel the healthy loop
        # when the other crashed — this was a critical bug.
        try:
            await self._ensure_multi_channel_coordinator(runner, mode)
        except Exception as e:
            logger.error(f"[COMMENT-LOOP] Coordinator init FAILED: {e}", exc_info=True)
            logger.info("[COMMENT-LOOP] Retrying coordinator init in 30s...")
            await asyncio.sleep(30)
            # Retry once more before giving up
            await self._ensure_multi_channel_coordinator(runner, mode)

        # Supervisor: manages both browser loops independently
        _browser_tasks: dict = {}  # {"chrome": Task, "edge": Task}
        _RESTART_DELAY = 30
        _HEALTH_CHECK_INTERVAL = 60  # seconds between health checks

        # 2026-02-01: Per-browser locks prevent Phase 1 (comments) and Phase 3
        # (scheduling) from touching the same browser simultaneously.
        # The thread leak from asyncio.to_thread can't be interrupted, but the
        # lock ensures the next cycle waits until the leaked thread releases.
        _browser_locks: dict = {
            "chrome": asyncio.Lock(),
            "edge": asyncio.Lock(),
        }
        # Stop events: set when Phase 3 times out so the scheduler thread
        # knows to stop touching the browser ASAP.
        _scheduler_stop_events: dict = {
            "chrome": threading.Event(),
            "edge": threading.Event(),
        }

        def _create_browser_task(browser_name: str) -> asyncio.Task:
            """Create a browser engagement task."""
            task = asyncio.create_task(
                self._browser_engagement_loop(
                    browser_name=browser_name,
                    runner=runner,
                    max_comments=max_comments,
                    mode=mode,
                    interval_minutes=interval_minutes,
                    browser_lock=_browser_locks[browser_name],
                    scheduler_stop_event=_scheduler_stop_events[browser_name],
                ),
                name=f"engagement-{browser_name}",
            )
            logger.info(f"[SUPERVISOR] {browser_name.upper()} loop task CREATED")
            return task

        # Launch both loops
        for _browser in ("chrome", "edge"):
            _browser_tasks[_browser] = _create_browser_task(_browser)

        # Supervision loop: monitor both tasks, restart individually on failure
        while True:
            try:
                await asyncio.sleep(_HEALTH_CHECK_INTERVAL)

                for _browser in ("chrome", "edge"):
                    _task = _browser_tasks.get(_browser)
                    if _task is None or _task.done():
                        _tag = _browser.upper()
                        # Log what happened
                        if _task is not None:
                            try:
                                _exc = _task.exception()
                                if _exc:
                                    logger.error(
                                        f"[SUPERVISOR] {_tag} loop CRASHED: {_exc}",
                                        exc_info=_exc,
                                    )
                                else:
                                    logger.warning(f"[SUPERVISOR] {_tag} loop EXITED without error")
                            except (asyncio.CancelledError, asyncio.InvalidStateError):
                                logger.warning(f"[SUPERVISOR] {_tag} loop was cancelled")

                        # Restart just this browser's loop
                        logger.info(f"[SUPERVISOR] Restarting {_tag} loop in {_RESTART_DELAY}s...")
                        await asyncio.sleep(_RESTART_DELAY)

                        # Re-init coordinator if needed
                        try:
                            await self._ensure_multi_channel_coordinator(runner, mode)
                        except Exception as _coord_err:
                            logger.error(f"[SUPERVISOR] Coordinator re-init failed: {_coord_err}")

                        _browser_tasks[_browser] = _create_browser_task(_browser)

            except asyncio.CancelledError:
                logger.info("[SUPERVISOR] Supervisor CANCELLED — shutting down browser loops")
                for _b, _t in _browser_tasks.items():
                    if _t and not _t.done():
                        _t.cancel()
                raise
            except Exception as _sup_err:
                logger.error(f"[SUPERVISOR] Health check error: {_sup_err}", exc_info=True)
                await asyncio.sleep(10)

    async def _ensure_multi_channel_coordinator(self, runner, mode: str):
        """Lazy-init MultiChannelCoordinator with DAE callbacks (called once)."""
        if not self.multi_channel_coordinator:
            self.multi_channel_coordinator = MultiChannelCoordinator(
                log_studio_context=self._log_studio_context,
                verify_studio_inbox_clear=self._verify_studio_inbox_clear,
                reconnect_chrome_driver=self._reconnect_chrome_driver,
                reconnect_edge_driver=self._reconnect_edge_driver,
                detect_current_channel_id=self._detect_current_channel_id,
                update_engagement_status=lambda cid, status: self._comment_engagement_status.update({cid: status}),
                set_active_channel=lambda cid: setattr(self, '_comment_engagement_active_channel', cid),
                is_live_stream_pending=lambda: self._live_stream_pending,
            )

    async def _browser_engagement_loop(
        self,
        browser_name: str,
        runner,
        max_comments: int,
        mode: str,
        interval_minutes: int = 10,
        browser_lock: asyncio.Lock = None,
        scheduler_stop_event: threading.Event = None,
    ):
        """
        Per-browser engagement loop: Comments → Scheduling → Sleep.

        2026-01-30: Each browser independently cycles through its own channels.
        Chrome and Edge run in parallel — neither blocks the other.

        2026-02-01: Added browser_lock (asyncio.Lock) and scheduler_stop_event
        (threading.Event) to prevent Phase 1 / Phase 3 contention. The lock
        ensures only one phase touches the browser at a time. The stop_event
        tells a leaked scheduler thread to stop driving the browser.

        Args:
            browser_name: "chrome" or "edge"
            runner: EngagementRunner instance
            max_comments: Max comments per channel (0=UNLIMITED)
            mode: Execution mode
            interval_minutes: Minutes between cycles
            browser_lock: asyncio.Lock preventing concurrent browser access
            scheduler_stop_event: threading.Event to signal scheduler thread to stop
        """
        tag = browser_name.upper()
        cycle_count = 0
        interval_seconds = interval_minutes * 60

        logger.info(f"[{tag}-LOOP] Browser loop STARTED — cycling Comments → Scheduling every {interval_minutes} min")

        while True:
            try:
                cycle_count += 1
                cycle_start = time.time()
                logger.info("")
                logger.info("=" * 60)
                logger.info(f"[{tag}-LOOP] CYCLE #{cycle_count} STARTING")
                logger.info(f"[{tag}-LOOP]   Shorts scheduling: {'ENABLED' if self._shorts_scheduler_available else 'UNAVAILABLE'}")
                logger.info("=" * 60)

                # ============================================
                # PHASE 1: COMMENT ENGAGEMENT (this browser only)
                # HARDENED: 90-minute timeout prevents infinite hang if
                # WebDriver connect, OOPS recovery, or subprocess stalls.
                # 2026-02-01: Browser lock prevents contention with leaked
                # Phase 3 scheduler threads from the previous cycle.
                # ============================================
                phase1_start = time.time()
                phase1_timeout = int(os.getenv("COMMUNITY_PHASE1_TIMEOUT", "5400"))  # 90 min default
                comments_processed = 0

                if browser_lock:
                    logger.info(f"[{tag}-LOOP] PHASE 1: Acquiring browser lock...")
                    await browser_lock.acquire()
                    logger.info(f"[{tag}-LOOP] PHASE 1: Browser lock ACQUIRED")
                try:
                    logger.info(f"[{tag}-LOOP] PHASE 1: COMMENT ENGAGEMENT starting (timeout={phase1_timeout}s)...")
                    try:
                        comments_processed = await asyncio.wait_for(
                            self.multi_channel_coordinator.run_browser_engagement(
                                browser=browser_name,
                                runner=runner,
                                max_comments=max_comments,
                                mode=mode,
                            ),
                            timeout=phase1_timeout,
                        )
                    except asyncio.TimeoutError:
                        logger.error(f"[{tag}-LOOP] PHASE 1 TIMEOUT after {phase1_timeout}s — skipping to next phase")
                finally:
                    if browser_lock and browser_lock.locked():
                        browser_lock.release()
                        logger.debug(f"[{tag}-LOOP] PHASE 1: Browser lock RELEASED")
                phase1_elapsed = time.time() - phase1_start
                logger.info(f"[{tag}-LOOP] PHASE 1: COMMENT ENGAGEMENT complete ({phase1_elapsed:.1f}s, {comments_processed} comments)")

                # ACTIVITY ROUTING: Signal comment completion for this browser
                try:
                    activity_router = get_activity_router()
                    activity_router.signal_activity_complete(
                        ActivityType.COMMENT_ENGAGEMENT,
                        metadata={"cycle": cycle_count, "browser": browser_name, "comments": comments_processed}
                    )
                except Exception as e:
                    logger.debug(f"[{tag}-LOOP] [ACTIVITY-ROUTER] Signal failed: {e}")

                # ============================================
                # PHASE 2: VIDEO INDEXING (Chrome only, optional)
                # ============================================
                if browser_name == "chrome" and os.getenv("YT_VIDEO_INDEXING_ENABLED", "false").lower() in ("1", "true", "yes"):
                    try:
                        from modules.ai_intelligence.video_indexer.src.studio_ask_indexer import run_video_indexing_cycle
                        logger.info(f"[{tag}-LOOP] PHASE 2: VIDEO INDEXING starting...")
                        await run_video_indexing_cycle()
                        try:
                            activity_router = get_activity_router()
                            activity_router.signal_activity_complete(
                                ActivityType.VIDEO_INDEXING,
                                metadata={"method": "studio_ask_indexer", "browser": browser_name}
                            )
                        except Exception:
                            pass
                    except ImportError:
                        logger.debug(f"[{tag}-LOOP] Video indexer not available")
                    except Exception as e:
                        logger.warning(f"[{tag}-LOOP] Video indexing failed: {e}")

                # ============================================
                # PHASE 3: SHORTS SCHEDULING (this browser only)
                # ============================================
                phase3_start = time.time()
                shorts_enabled = os.getenv("YT_SHORTS_SCHEDULING_ENABLED", "true").lower() in ("1", "true", "yes")
                scheduled_count = 0
                error_count = 0

                logger.info(f"[{tag}-LOOP] PHASE 3: SHORTS SCHEDULING")
                logger.info(f"[{tag}-LOOP]   Enabled: {shorts_enabled} | Module: {self._shorts_scheduler_available}")

                if not shorts_enabled:
                    logger.info(f"[{tag}-LOOP] PHASE 3 SKIPPED: disabled")
                elif not self._shorts_scheduler_available:
                    logger.warning(f"[{tag}-LOOP] PHASE 3 SKIPPED: module unavailable")
                else:
                    # 2026-02-01: Acquire browser lock for Phase 3 to prevent
                    # contention if next cycle's Phase 1 starts while this is running.
                    if browser_lock:
                        logger.info(f"[{tag}-LOOP] PHASE 3: Acquiring browser lock...")
                        await browser_lock.acquire()
                        logger.info(f"[{tag}-LOOP] PHASE 3: Browser lock ACQUIRED")

                    # Clear stop event at start (fresh for this cycle)
                    if scheduler_stop_event:
                        scheduler_stop_event.clear()

                    try:
                        from modules.platform_integration.youtube_shorts_scheduler.scripts.launch import run_multi_channel_scheduler
                        max_shorts = int(os.getenv("YT_SHORTS_PER_CYCLE", "9999"))

                        phase3_timeout = int(os.getenv("YT_SHORTS_PHASE3_TIMEOUT", "3600"))  # 60 min default
                        logger.info(f"[{tag}-LOOP] Running scheduler for {browser_name} (max {max_shorts}/ch, timeout={phase3_timeout}s)...")

                        # run_multi_channel_scheduler uses asyncio.run() internally,
                        # so it must run in a thread to avoid nested event loop.
                        # HARDENED: timeout prevents infinite hang on browser stall.
                        # 2026-02-01: stop_event lets us tell the thread to stop
                        # if the timeout fires (threads can't be interrupted directly).
                        try:
                            results = await asyncio.wait_for(
                                asyncio.to_thread(
                                    run_multi_channel_scheduler,
                                    browser=browser_name,
                                    mode="schedule",
                                    max_per_channel=max_shorts,
                                    stop_event=scheduler_stop_event,
                                ),
                                timeout=phase3_timeout,
                            )
                        except asyncio.TimeoutError:
                            logger.error(f"[{tag}-LOOP] PHASE 3 TIMEOUT after {phase3_timeout}s")
                            # Signal the leaked thread to stop driving the browser
                            if scheduler_stop_event:
                                scheduler_stop_event.set()
                                logger.warning(f"[{tag}-LOOP] PHASE 3: Stop signal SENT to scheduler thread")
                            # Give thread a moment to notice and stop
                            await asyncio.sleep(5)
                            results = None

                        # Parse results
                        if isinstance(results, dict) and "channels" in results:
                            for ch_key, ch_data in results["channels"].items():
                                if isinstance(ch_data, dict):
                                    scheduled_count += ch_data.get("total_scheduled", 0)
                                    error_count += ch_data.get("total_errors", 0)

                        phase3_elapsed = time.time() - phase3_start
                        logger.info(f"[{tag}-LOOP] PHASE 3 COMPLETE: {scheduled_count} scheduled | {error_count} errors | {phase3_elapsed:.1f}s")

                        # Update DAE-level tracking (thread-safe: only one browser writes at a time per its own loop)
                        self._shorts_total_cycles += 1
                        self._shorts_total_scheduled += scheduled_count
                        self._shorts_last_cycle_result = {
                            "timestamp": datetime.now().isoformat(),
                            "cycle": cycle_count,
                            "browser": browser_name,
                            "total_scheduled": scheduled_count,
                            "total_errors": error_count,
                            "elapsed_seconds": phase3_elapsed,
                        }

                        # Signal scheduling complete
                        try:
                            activity_router = get_activity_router()
                            activity_router.signal_activity_complete(
                                ActivityType.SHORTS_SCHEDULING,
                                metadata={"total_scheduled": scheduled_count, "browser": browser_name}
                            )
                        except Exception:
                            pass

                    except ImportError as ie:
                        logger.warning(f"[{tag}-LOOP] IMPORT FAILED: {ie}")
                    except Exception as e:
                        logger.error(f"[{tag}-LOOP] PHASE 3 CRASHED: {e}", exc_info=True)
                    finally:
                        # 2026-02-01: ALWAYS release browser lock after Phase 3
                        if browser_lock and browser_lock.locked():
                            browser_lock.release()
                            logger.debug(f"[{tag}-LOOP] PHASE 3: Browser lock RELEASED")

                # ============================================
                # CYCLE SUMMARY + IDLE DETECTION
                # ============================================
                total_cycle_elapsed = time.time() - cycle_start
                is_idle = (comments_processed == 0 and scheduled_count == 0 and error_count == 0)

                logger.info("")
                logger.info("-" * 50)
                logger.info(f"[{tag}-LOOP] CYCLE #{cycle_count} COMPLETE ({total_cycle_elapsed:.1f}s)")
                logger.info(f"[{tag}-LOOP]   Comments: {comments_processed} | Scheduled: {scheduled_count} | Errors: {error_count}")
                logger.info(f"[{tag}-LOOP]   Lifetime: {self._shorts_total_cycles} scheduling cycles, {self._shorts_total_scheduled} total videos")

                # 2026-02-01: IDLE DETECTION — if this browser did zero work,
                # signal activity router so orchestration layer can assign work.
                if is_idle:
                    logger.info(f"[{tag}-LOOP] [IDLE-DETECT] Browser {tag} is IDLE — 0 comments, 0 scheduled")
                    try:
                        activity_router = get_activity_router()
                        activity_router.signal_activity_complete(
                            ActivityType.COMMENT_ENGAGEMENT,
                            metadata={
                                "cycle": cycle_count,
                                "browser": browser_name,
                                "idle": True,
                                "comments": 0,
                                "scheduled": 0,
                            }
                        )
                    except Exception as idle_err:
                        logger.debug(f"[{tag}-LOOP] [IDLE-DETECT] Router signal failed: {idle_err}")

                    # Shorten sleep when idle — check again sooner
                    idle_sleep = max(120, interval_seconds // 3)  # At least 2 min, at most 1/3 of normal
                    logger.info(f"[{tag}-LOOP] [IDLE-DETECT] Shortened sleep: {idle_sleep}s (instead of {interval_seconds}s)")
                    logger.info("-" * 50)
                    await asyncio.sleep(idle_sleep)
                else:
                    logger.info(f"[{tag}-LOOP] Sleeping {interval_minutes} minutes before next cycle...")
                    logger.info("-" * 50)
                    # Wait before next cycle
                    await asyncio.sleep(interval_seconds)

            except asyncio.CancelledError:
                logger.info(f"[{tag}-LOOP] Loop CANCELLED after {cycle_count} cycles")
                raise
            except Exception as e:
                logger.error(f"[{tag}-LOOP] Cycle #{cycle_count} EXCEPTION: {e}", exc_info=True)
                # Wait before retry on error
                await asyncio.sleep(60)

    async def _run_multi_channel_engagement(
        self,
        runner,
        max_comments: int,
        mode: str
    ):
        """
        Run comment engagement across ALL channels with account switching.
        Delegates to MultiChannelCoordinator (WSP 62: Large File Refactoring).

        NOTE (2026-01-30): This legacy method runs ALL browsers sequentially.
        The new per-browser architecture uses _browser_engagement_loop() instead,
        which calls coordinator.run_browser_engagement(browser=...) per browser.
        This method is kept for backward compatibility (e.g., COMMENT_ONLY mode
        or any code path that still calls it directly).

        Architecture (2025-12-28 Refactor):
        - Chrome (port 9222): Move2Japan + UnDaoDu (SAME Google account)
        - Edge (port 9223): FoundUps + RavingANTIFA (SAME Edge session)
        """
        await self._ensure_multi_channel_coordinator(runner, mode)

        await self.multi_channel_coordinator.run_multi_channel_engagement(
            runner=runner,
            max_comments=max_comments,
            mode=mode
        )
    async def run(self):
        """
        Main entry point - full DAE lifecycle.
        """
        logger.info("=" * 60)
        logger.info("[AI] AUTO MODERATOR DAE STARTING")
        logger.info("WSP-Compliant: Using livechat_core architecture")
        if self.enable_ai_monitoring:
            logger.info("[AI] AI Overseer (Qwen/Gemma) monitoring: ENABLED")
        logger.info("=" * 60)

        # Central automation audit run id (propagates to subprocesses via env inheritance)
        run_id = os.getenv("YT_AUTOMATION_RUN_ID", "").strip()
        if not run_id:
            run_id = f"yt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.environ["YT_AUTOMATION_RUN_ID"] = run_id

        logger.info(
            "[AUTOMATION-AUDIT] run_id=%s yt_automation=%s comment_engagement=%s livechat_send=%s stream_scraping=%s stream_resolver=%s",
            run_id,
            _env_truthy("YT_AUTOMATION_ENABLED", "true"),
            _env_truthy("YT_COMMENT_ENGAGEMENT_ENABLED", "true"),
            _env_truthy("YT_LIVECHAT_SEND_ENABLED", "true"),
            _env_truthy("YT_STREAM_SCRAPING_ENABLED", "true"),
            _env_truthy("YT_STREAM_RESOLVER_ENABLED", "true"),
        )
        logger.info(
            "[AUTOMATION-AUDIT] run_id=%s livechat_ui_actions=%s party_reactions=%s announcements=%s comment_only=%s stream_vision_disabled=%s",
            run_id,
            _env_truthy("YT_LIVECHAT_UI_ACTIONS_ENABLED", "true"),
            _env_truthy("YT_PARTY_REACTIONS_ENABLED", "true"),
            _env_truthy("YT_LIVECHAT_ANNOUNCEMENTS_ENABLED", "true"),
            _env_truthy("YT_COMMENT_ONLY_MODE", "false"),
            os.getenv("STREAM_VISION_DISABLED", "true"),
        )
        logger.info(
            "[AUTOMATION-AUDIT] run_id=%s comment_reactions=%s comment_like=%s comment_heart=%s comment_reply=%s",
            run_id,
            _env_truthy("YT_COMMENT_REACTIONS_ENABLED", "true"),
            _env_truthy("YT_COMMENT_LIKE_ENABLED", "true"),
            _env_truthy("YT_COMMENT_HEART_ENABLED", "true"),
            _env_truthy("YT_COMMENT_REPLY_ENABLED", "true"),
        )
        logger.info(
            "[AUTOMATION-AUDIT] run_id=%s reply_basic_only=%s reply_no_classification=%s reply_no_semantic_state=%s",
            run_id,
            _env_truthy("YT_REPLY_BASIC_ONLY", "false"),
            _env_truthy("YT_NO_CLASSIFICATION", "false"),
            _env_truthy("YT_NO_SEMANTIC_STATE", "false"),
        )
        logger.info(
            "[AUTOMATION-AUDIT] run_id=%s engagement_tempo=%s",
            run_id,
            os.getenv("YT_ENGAGEMENT_TEMPO", "012").upper(),
        )
        logger.info(
            "[AUTOMATION-AUDIT] run_id=%s shorts_scheduling=%s shorts_module=%s shorts_per_cycle=%s comment_only=%s",
            run_id,
            _env_truthy("YT_SHORTS_SCHEDULING_ENABLED", "true"),
            self._shorts_scheduler_available,
            os.getenv("YT_SHORTS_PER_CYCLE", "9999"),
            _env_truthy("YT_COMMENT_ONLY_MODE", "false"),
        )

        # Phase -2: Launch dependencies (Chrome + LM Studio for comment engagement)
        if _env_truthy("YT_DEPS_AUTO_LAUNCH", "true"):
            try:
                from modules.infrastructure.dependency_launcher.src.dae_dependencies import ensure_dependencies
                # Require LM Studio so UI-TARS vision is available before engagement
                dep_status = await ensure_dependencies(require_lm_studio=True)
                if not dep_status.get('chrome'):
                    logger.warning("[DEPS] Chrome not ready - comment engagement may fail")
                    logger.warning("[DEPS] Manual launch: chrome --remote-debugging-port=9222")
                if dep_status.get('lm_studio'):
                    logger.info("[DEPS] LM Studio ready (UI-TARS vision enabled on port 1234)")
                else:
                    logger.warning("[DEPS] LM Studio not ready - falling back to DOM-only actions")
            except ImportError:
                logger.debug("[DEPS] Dependency launcher not available")
            except Exception as e:
                logger.warning(f"[DEPS] Dependency check failed: {e}")
        else:
            logger.info("[DEPS] Auto-launch disabled (YT_DEPS_AUTO_LAUNCH=false)")

        # Phase -2.1: Startup comment engagement (runs even when no live stream)
        # First-principles: comments are a persistent backlog; do not gate on live chat.
        #
        # Sprint 1+2: Pluggable execution modes (subprocess=safest, thread=fast, inproc=debug)
        if os.getenv("COMMUNITY_STARTUP_ENGAGE", "true").lower() in ("1", "true", "yes"):
            try:
                from .engagement_runner import get_runner
                from pathlib import Path

                default_channel_id = os.getenv("COMMUNITY_CHANNEL_ID") or os.getenv('UNDAODU_CHANNEL_ID', 'UCfHM9Fw9HD-NwiS0seD_oIA')
                startup_max = int(os.getenv("COMMUNITY_STARTUP_MAX_COMMENTS", "0"))

                # Get execution mode (default: subprocess for safety)
                exec_mode = os.getenv("COMMUNITY_EXEC_MODE", "subprocess")
                # Repo root (auto_moderator_dae.py is at modules/communication/livechat/src/)
                repo_root = Path(__file__).resolve().parents[4]

                self.studio_repo_root = repo_root
                self.studio_runner = get_runner(mode=exec_mode, repo_root=repo_root)

                # 2025-12-30: INDEPENDENT comment engagement loop
                # This runs SEPARATELY from stream detection - no coupling!
                # Interval configurable via COMMUNITY_ENGAGEMENT_INTERVAL_MINUTES (default: 10)
                interval_minutes = int(os.getenv("COMMUNITY_ENGAGEMENT_INTERVAL_MINUTES", "10"))

                self._comment_engagement_task = asyncio.create_task(
                    self._comment_engagement_loop(
                        self.studio_runner,
                        max_comments=startup_max,
                        mode=exec_mode,
                        interval_minutes=interval_minutes
                    )
                )
                # CRITICAL: Give subprocess 3 seconds to launch before stream detection starts
                # This ensures Chrome opens Studio inbox before stream resolver hijacks the browser
                logger.info(f"[COMMUNITY] INDEPENDENT comment engagement loop started (every {interval_minutes} min)")
                logger.info(f"[COMMUNITY] Mode: {exec_mode} | Max per channel: {startup_max if startup_max > 0 else 'UNLIMITED'}")
                await asyncio.sleep(3)

            except Exception as e:
                logger.warning(f"[COMMUNITY] Startup engagement failed to launch: {e}")

        # Initialize AI Overseer heartbeat monitoring if enabled
        if self.enable_ai_monitoring:
            try:
                from .youtube_dae_heartbeat import YouTubeDAEHeartbeat
                self.heartbeat_service = YouTubeDAEHeartbeat(
                    dae_instance=self,
                    heartbeat_interval=30,
                    enable_ai_overseer=True
                )
                # Start heartbeat in background
                asyncio.create_task(self.heartbeat_service.start_heartbeat())
                logger.info("[HEARTBEAT] AI Overseer monitoring started - Qwen/Gemma watching for errors")
            except Exception as e:
                logger.warning(f"[HEARTBEAT] Failed to start AI Overseer monitoring: {e}")
                logger.warning("[HEARTBEAT] Continuing without AI monitoring")

        # Phase -1/0: Connect and authenticate
        if not self.connect():
            logger.error("Failed to connect to YouTube")
            return

        # COMMENT-ONLY MODE: Skip stream detection, only run comment engagement loop
        comment_only_mode = os.getenv("YT_COMMENT_ONLY_MODE", "false").lower() in ("1", "true", "yes")
        if comment_only_mode:
            interval_minutes = int(os.getenv("COMMUNITY_ENGAGEMENT_INTERVAL_MINUTES", "10"))
            logger.info("=" * 60)
            logger.info("[COMMENT-ONLY] Running in COMMENT-ONLY mode")
            logger.info("[COMMENT-ONLY] Stream detection DISABLED - comments loop only")
            logger.info(f"[COMMENT-ONLY] Comment engagement runs every {interval_minutes} minutes")
            logger.info("[COMMENT-ONLY] Press Ctrl+C to stop")
            logger.info("=" * 60)
            # Wait for comment engagement loop (runs independently in background)
            try:
                if self._comment_engagement_task:
                    await self._comment_engagement_task  # Wait for loop (never ends)
                else:
                    while True:
                        await asyncio.sleep(60)
            except KeyboardInterrupt:
                logger.info("[COMMENT-ONLY] Shutting down...")
            except asyncio.CancelledError:
                logger.info("[COMMENT-ONLY] Comment loop cancelled")
            return

        # Phase 2: Monitor autonomously - loop forever looking for streams
        consecutive_failures = 0
        stream_ended_normally = False

        while True:
            try:
                await self.monitor_chat()
                # If monitor_chat returns normally, stream ended - look for new one
                stream_ended_normally = True
                logger.info("[REFRESH] Stream ended or became inactive - seamless switching engaged")
                logger.info("[LIGHTNING] Immediately searching for new stream (agentic mode)...")

                # IMPORTANT: Release API credentials to go back to NO-QUOTA mode
                # This prevents wasting tokens while searching for new streams
                if self.service:
                    logger.info("[LOCK] Releasing API credentials - switching back to NO-QUOTA mode")
                    self.service = None
                    self.credential_set = "NO-QUOTA"

                # WRE Monitor: Mark transition start
                if hasattr(self, 'wre_monitor') and self.wre_monitor:
                    self.transition_start = time.time()

                # Reset the LiveChat instance for fresh connection
                if self.livechat:
                    self.livechat.stop_listening()
                    self.livechat = None

                # Reset current_video_id for heartbeat tracking
                self.current_video_id = None

                # Clear cached stream info to force fresh search
                if self.stream_resolver:
                    # Force stream resolver to use NO-QUOTA mode
                    self.stream_resolver.youtube = None
                    # Use the proper clear_cache method
                    self.stream_resolver.clear_cache()
                    logger.info("[REFRESH] Stream ended - cleared all caches for fresh NO-QUOTA search")
                
                # Execute idle automation tasks before waiting
                # WSP 35: Module Execution Automation during idle periods
                try:
                    from modules.infrastructure.idle_automation.src.idle_automation_dae import run_idle_automation
                    logger.info("[BOT] Executing idle automation tasks...")
                    idle_result = await run_idle_automation()
                    if idle_result.get("overall_success"):
                        logger.info(f"[OK] Idle automation completed successfully ({idle_result.get('duration', 0):.1f}s)")
                    else:
                        logger.info(f"[WARN] Idle automation completed with issues ({idle_result.get('duration', 0):.1f}s)")
                except ImportError:
                    logger.debug("Idle automation module not available - skipping")
                except Exception as e:
                    logger.warning(f"Idle automation failed: {e}")

                # Quick transition - only wait 5 seconds before looking for new stream
                await asyncio.sleep(5)
                consecutive_failures = 0  # Reset failure counter on clean exit

                # Set quick check mode for the next monitor_chat call
                # This will make it check more frequently after a stream ends
                logger.info("[TARGET] Entering quick-check mode for seamless stream detection")
                
            except KeyboardInterrupt:
                logger.info("[STOP] Stopped by user")
                break
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Error in monitoring loop (attempt #{consecutive_failures}): {e}")
                
                # Exponential backoff for retries
                wait_time = min(30 * (2 ** consecutive_failures), 600)  # Max 10 minutes
                logger.info(f"[REFRESH] Restarting in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
                # After too many failures, do a full reconnect
                if consecutive_failures >= 5:
                    logger.warning("[REFRESH] Too many failures - attempting full reconnection")
                    self.service = None  # Force re-authentication
                    consecutive_failures = 0
                    # Also reset stream resolver cache
                    if self.stream_resolver:
                        self.stream_resolver.clear_cache()
    
    async def _heartbeat_loop(self):
        """
        Background cardiovascular heartbeat loop (WSP 91: DAEMON Observability).

        Writes dual telemetry:
        - SQLite: Structured data for queries (youtube_heartbeats table)
        - JSONL: Streaming append-only data for tailing (logs/youtube_dae_heartbeat.jsonl)
        """
        import json
        from pathlib import Path

        heartbeat_count = 0
        # Track transitions so we can emit "state change" pulses for AI Overseer
        last_edge_comments_cleared = False

        try:
            while True:
                await asyncio.sleep(30)  # 30-second heartbeat interval
                heartbeat_count += 1

                try:
                    # Calculate uptime
                    uptime_seconds = time.time() - self.start_time

                    # Determine stream active status
                    stream_active = bool(self.livechat and self.livechat.is_running)

                    # Get moderation stats if available
                    chat_messages_per_min = 0.0
                    moderation_actions = 0
                    banter_responses = 0

                    if self.livechat:
                        try:
                            stats = self.livechat.get_moderation_stats()
                            # Calculate messages per minute (estimate from total / uptime)
                            total_messages = stats.get('total_messages', 0)
                            if uptime_seconds > 0:
                                chat_messages_per_min = (total_messages / uptime_seconds) * 60

                            moderation_actions = stats.get('spam_blocks', 0) + stats.get('toxic_blocks', 0)
                            banter_responses = stats.get('responses_sent', 0)
                        except Exception as e:
                            logger.debug(f"Stats collection failed: {e}")

                    # Get system resource usage (optional)
                    memory_mb = None
                    cpu_percent = None
                    try:
                        import psutil
                        process = psutil.Process()
                        memory_mb = process.memory_info().rss / 1024 / 1024
                        cpu_percent = process.cpu_percent()
                    except (ImportError, Exception):
                        pass

                    # Determine health status
                    status = "healthy"
                    if not stream_active:
                        status = "idle"
                    elif moderation_actions > 100:
                        status = "warning"  # High moderation activity

                    # === SQLite Write (structured data) ===
                    if self.telemetry:
                        self.telemetry.record_heartbeat(
                            status=status,
                            stream_active=stream_active,
                            chat_messages_per_min=chat_messages_per_min,
                            moderation_actions=moderation_actions,
                            banter_responses=banter_responses,
                            uptime_seconds=uptime_seconds,
                            memory_mb=memory_mb,
                            cpu_percent=cpu_percent
                        )

                    # === JSONL Write (streaming telemetry) ===
                    jsonl_path = Path("logs/youtube_dae_heartbeat.jsonl")
                    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

                    # Comment engagement summary (critical for "what next?" orchestration)
                    foundups_id = os.getenv("FOUNDUPS_CHANNEL_ID", "").strip()
                    raving_id = os.getenv("RAVINGANTIFA_CHANNEL_ID", "").strip()
                    comment_status = getattr(self, "_comment_engagement_status", {}) or {}
                    def _channel_summary(cid: str) -> dict:
                        if not cid:
                            return {"channel_id": "", "known": False}
                        s = comment_status.get(cid, {}) or {}
                        stats = s.get("stats", {}) or {}
                        return {
                            "channel_id": cid,
                            "known": True,
                            "all_processed": bool(s.get("all_processed", False)),
                            "comments_processed": int(stats.get("comments_processed", 0) or 0),
                            "errors": int(stats.get("errors", 0) or 0),
                            "updated_at": float(s.get("updated_at", 0.0) or 0.0),
                            "error": s.get("error"),
                        }

                    foundups_summary = _channel_summary(foundups_id)
                    raving_summary = _channel_summary(raving_id)
                    edge_comments_cleared = bool(
                        foundups_summary.get("known")
                        and raving_summary.get("known")
                        and foundups_summary.get("all_processed")
                        and raving_summary.get("all_processed")
                        and not foundups_summary.get("error")
                        and not raving_summary.get("error")
                    )

                    heartbeat_data = {
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "status": status,
                        "stream_active": stream_active,
                        "chat_messages_per_min": round(chat_messages_per_min, 2),
                        "moderation_actions": moderation_actions,
                        "banter_responses": banter_responses,
                        "uptime_seconds": round(uptime_seconds, 1),
                        "memory_mb": round(memory_mb, 2) if memory_mb else None,
                        "cpu_percent": round(cpu_percent, 2) if cpu_percent else None,
                        "heartbeat_count": heartbeat_count,
                        "comment_engagement": {
                            "live_stream_pending": bool(getattr(self, "_live_stream_pending", False)),
                            "live_chat_active": bool(getattr(self, "_live_chat_active", False)),
                            "active_channel_id": getattr(self, "_comment_engagement_active_channel", None),
                            "edge_comments_cleared": edge_comments_cleared,
                            "foundups": foundups_summary,
                            "ravingantifa": raving_summary,
                        },
                        "shorts_scheduling": {
                            "module_available": getattr(self, "_shorts_scheduler_available", False),
                            "enabled": os.getenv("YT_SHORTS_SCHEDULING_ENABLED", "true").lower() in ("1", "true", "yes"),
                            "total_cycles": getattr(self, "_shorts_total_cycles", 0),
                            "total_scheduled": getattr(self, "_shorts_total_scheduled", 0),
                            "last_cycle": getattr(self, "_shorts_last_cycle_result", None),
                        },
                    }
                    with open(jsonl_path, 'a', encoding='utf-8') as f:
                        json.dump(heartbeat_data, f)
                        f.write('\n')

                    # Emit a one-time event when Edge comments become fully cleared.
                    if edge_comments_cleared and not last_edge_comments_cleared:
                        last_edge_comments_cleared = True
                        event = {
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            "event": "edge_comments_cleared",
                            "channels": [c for c in [foundups_id, raving_id] if c],
                            "note": "FoundUps + RavingANTIFA all_processed=True; awaiting next action orchestration",
                        }
                        with open(jsonl_path, "a", encoding="utf-8") as f:
                            json.dump(event, f)
                            f.write("\n")
                    if not edge_comments_cleared:
                        last_edge_comments_cleared = False

                    # Log heartbeat every 10 pulses (every 5 minutes)
                    if heartbeat_count % 10 == 0:
                        logger.info(f"[HEART] Heartbeat #{heartbeat_count} - Status: {status}, Stream: {'ACTIVE' if stream_active else 'IDLE'}")

                        # === AI OVERSEER: Autonomous monitoring (every 5 minutes) ===
                        try:
                            from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer
                            from pathlib import Path as OverseerPath

                            # Initialize AI Overseer ONCE, reuse forever (saves 490-505ms per heartbeat)
                            # Repo root (auto_moderator_dae.py is at modules/communication/livechat/src/)
                            if self.ai_overseer is None:
                                repo_root = OverseerPath(__file__).resolve().parents[4]
                                self.ai_overseer = AIIntelligenceOverseer(repo_root)
                                logger.info("[AI-OVERSEER] Initialized singleton (first use)")

                            overseer = self.ai_overseer  # Reuse existing instance

                            # Read recent JSONL telemetry for error detection
                            recent_log_lines = []
                            with open(jsonl_path, 'r', encoding='utf-8') as f:
                                all_lines = f.readlines()
                                recent_log_lines = all_lines[-50:] if len(all_lines) > 50 else all_lines

                            if recent_log_lines:
                                # Convert JSONL to text for AI Overseer
                                bash_output = "".join(recent_log_lines)

                                # Monitor daemon with autonomous fixing enabled
                                skill_path = repo_root / "modules" / "communication" / "livechat" / "skillz" / "youtube_daemon_monitor.json"

                                # Run in executor to avoid blocking async loop
                                loop = asyncio.get_event_loop()
                                result = await loop.run_in_executor(
                                    None,
                                    lambda: overseer.monitor_daemon(
                                        bash_output=bash_output,
                                        skill_path=skill_path,
                                        auto_fix=True,
                                        chat_sender=None,
                                        announce_to_chat=False
                                    )
                                )

                                # Log AI Overseer results
                                if result.get("bugs_detected", 0) > 0:
                                    logger.warning(f"[AI-OVERSEER] Detected {result['bugs_detected']} errors in daemon")

                                if result.get("bugs_fixed", 0) > 0:
                                    logger.info(f"[AI-OVERSEER] Applied {result['bugs_fixed']} autonomous fixes")
                                    for fix in result.get("fixes_applied", []):
                                        if fix.get("needs_restart"):
                                            logger.warning("[AI-OVERSEER] Fix requires restart - daemon will restart on next cycle")

                        except Exception as e:
                            logger.debug(f"[AI-OVERSEER] Monitoring check failed: {e}")

                    # === COMMUNITY MONITOR: Autonomous comment engagement (every 20 pulses = 10 minutes) ===
                    # CRITICAL: DISABLE autonomous comment engagement during live chat
                    # User requirement: "Once on live chat, do NOT return to comments"
                    # Comment engagement runs ONLY at startup, before first stream found
                    if heartbeat_count % 20 == 0 and self.community_monitor:
                        if self._live_chat_active:
                            logger.debug(f"[LOCK] Pulse {heartbeat_count}: Comment engagement DISABLED (live chat active)")
                        else:
                            try:
                                logger.info(f"[COMMUNITY] Pulse {heartbeat_count}: Checking for comment engagement...")

                                # Check if we should engage now (verifies stream is active, no engagement in progress)
                                should_engage = await self.community_monitor.should_check_now(heartbeat_count)

                                if should_engage:
                                    # Launch autonomous engagement as subprocess (fire-and-forget)
                                    # This runs isolated from main.py's process, no browser hijacking!
                                    # max_comments=0 = UNLIMITED - process ALL comments until tab is clear!
                                    asyncio.create_task(self.community_monitor.check_and_engage(max_comments=0))
                                    logger.info("[COMMUNITY] Autonomous engagement launched (UNLIMITED mode - clearing all comments)")
                                else:
                                    logger.debug("[COMMUNITY] Skipping (stream not active or engagement in progress)")

                            except Exception as e:
                                logger.error(f"[COMMUNITY] Comment check failed: {e}")

                except Exception as e:
                    logger.error(f"[HEART] Heartbeat pulse failed: {e}")

        except asyncio.CancelledError:
            logger.info(f"[HEART] Heartbeat loop cancelled after {heartbeat_count} pulses")
            raise

    def get_status(self) -> dict:
        """Get current DAE status including shorts scheduling diagnostics."""
        status = {
            'connected': bool(self.service),
            'monitoring': bool(self.livechat and self.livechat.is_running),
            'credential_set': self.credential_set,
            'architecture': 'livechat_core (WSP-compliant)',
            'modules': {
                'message_processor': True,
                'chat_sender': True,
                'chat_poller': True,
                'session_manager': True,
                'moderation_stats': True,
                'consciousness': True,
                'grok': True,
                'throttle': True
            },
            'shorts_scheduling': {
                'module_available': self._shorts_scheduler_available,
                'enabled': os.getenv("YT_SHORTS_SCHEDULING_ENABLED", "true").lower() in ("1", "true", "yes"),
                'total_cycles': self._shorts_total_cycles,
                'total_scheduled': self._shorts_total_scheduled,
                'last_cycle': self._shorts_last_cycle_result,
            },
            'comment_engagement': {
                'task_active': bool(self._comment_engagement_task and not self._comment_engagement_task.done()),
                'active_channel': self._comment_engagement_active_channel,
                'channels_status': dict(self._comment_engagement_status),
            },
        }

        if self.livechat:
            status['stats'] = self.livechat.get_moderation_stats()

        return status


def main():
    """Main entry point for the Auto Moderator DAE."""
    class _LogRateLimiter(logging.Filter):
        """Rate-limit repetitive INFO logs to prevent chat spam."""

        def __init__(self) -> None:
            super().__init__()
            self._last_emit = {}
            self._interval = float(os.getenv("LIVECHAT_LOG_THROTTLE_SEC", "10") or 10)

        def filter(self, record: logging.LogRecord) -> bool:
            if record.levelno >= logging.WARNING:
                return True
            message = record.getMessage()
            key = f"{record.name}:{message}"
            now = time.time()
            last = self._last_emit.get(key, 0.0)
            if now - last >= self._interval:
                self._last_emit[key] = now
                return True
            return False

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger().addFilter(_LogRateLimiter())
    
    # Create and run DAE
    dae = AutoModeratorDAE()
    asyncio.run(dae.run())


if __name__ == "__main__":
    main()
