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
import time
from datetime import datetime
from typing import Optional, Dict
from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
from modules.platform_integration.youtube_auth.src.monitored_youtube_service import create_monitored_service
from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver

# Import WSP-compliant livechat_core
from .livechat_core import LiveChatCore

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
        Can check multiple channels if configured.
        QWEN intelligence decides HOW to search based on patterns.

        Returns:
            Stream metadata dict containing video_id, live_chat_id, channel_id, and channel_name, or None
        """
        # WSP 91: Component Isolation (Zero-down)
        if not _env_truthy("YT_STREAM_RESOLVER_ENABLED", "true"):
            logger.debug("[SEARCH] Stream resolver DISABLED via YT_STREAM_RESOLVER_ENABLED")
            return None

        logger.info("[SEARCH] Looking for livestream...")

        # QWEN Intelligence: Analyze context before searching
        logger.info("[BOT][AI] [QWEN-ANALYZE] QWEN analyzing stream detection strategy...")
        if self.qwen_monitor and self.MonitoringContext:
            try:
                context = self.MonitoringContext(
                    query="youtube_stream_detection",
                    search_results=[],
                    patterns_detected=["channel_rotation", "no_quota_mode"]
                )
                monitoring_result = self.qwen_monitor.monitor(context)

                # Log QWEN's decision-making process with robot+brain emojis
                health_status = getattr(monitoring_result, 'health_status', None)
                if health_status:
                    logger.info(f"[BOT][AI] [QWEN-HEALTH] [UP] System health: {health_status}")
                    insights = getattr(monitoring_result, 'insights', None)
                    if insights:
                        logger.info(f"[BOT][AI] [QWEN-INSIGHT] [SEARCH] {insights}")
                analysis = getattr(monitoring_result, 'analysis', None)
                if analysis:
                    logger.info(f"[BOT][AI] [QWEN-ANALYSIS] {analysis}")
            except Exception as e:
                logger.info(f"[BOT][AI] [QWEN-MONITOR] [WARN] Monitor analysis incomplete: {e}")

        if not self.stream_resolver:
            # Initialize StreamResolver with service if available, otherwise None to trigger NO-QUOTA mode
            try:
                self.stream_resolver = StreamResolver(self.service)
                # WSP 3 Phase 4: circuit_breaker removed from StreamResolver (moved to youtube_api_ops)
                logger.info("[REFRESH] StreamResolver initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize StreamResolver with service: {e}")
                logger.info("[REFRESH] Falling back to NO-QUOTA mode initialization")
                # Initialize without service to force NO-QUOTA mode
                self.stream_resolver = StreamResolver(None)

        # Reset priority tracking for this rotation
        self.high_priority_pending = False
        self.priority_reason = None

        # List of channels to check - PRIORITIZE MOVE2JAPAN FIRST (WSP 3: Multi-channel support)
        channels_override = os.getenv("YT_CHANNELS_TO_CHECK", "").strip()
        if channels_override:
            channels_to_check = [ch.strip() for ch in channels_override.split(",") if ch.strip()]
            logger.info(f"[CONFIG] Using YT_CHANNELS_TO_CHECK override ({len(channels_to_check)} channels)")
        else:
            channels_to_check = [
                os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw'),  # Move2Japan channel - PRIORITY 1 - FIXED!
                os.getenv('FOUNDUPS_CHANNEL_ID', 'UCSNTUXjAgpd4sgWYP0xoJgw'),  # FoundUps channel - PRIORITY 2
                os.getenv('UNDAODU_CHANNEL_ID', 'UCfHM9Fw9HD-NwiS0seD_oIA'),   # UnDaoDu channel - PRIORITY 3 - FIXED!
                os.getenv('TEST_CHANNEL_ID', ''),  # Optional: safe test channel (disabled for social posting by default)
            ]
        
        # Filter out None values and remove duplicates
        channels_to_check = [ch for ch in channels_to_check if ch]

        # Show rotation header with clear channel list
        logger.info("="*60)
        logger.info("[REFRESH] CHANNEL ROTATION CHECK (NO-QUOTA MODE with QWEN Intelligence)")
        logger.info("[BOT][AI] [QWEN-INIT] Starting intelligent channel rotation analysis")

        # PRIORITY 0: [BOT][AI] First Principles - "Is the last video still live?"
        # Check cache + DB BEFORE any channel rotation logic
        logger.info("[BOT][AI] [QWEN-FIRST-PRINCIPLES] Is the last video still live?")
        try:
            # Call resolve_stream with None to trigger Priority 1 (cache) and Priority 1.5 (Qwen DB check)
            # This checks: 1) session_cache.json, 2) last stream in DB with lenient threshold + API
            pre_check_result = self.stream_resolver.resolve_stream(channel_id=None)
            if pre_check_result and pre_check_result[0]:
                logger.info(f"[BOT][AI] [QWEN-SUCCESS] [OK] Last known stream still live! Instant reconnection.")
                logger.info(f"[ROCKET] Skipping ALL channel rotation - already found active stream: {pre_check_result[0]}")

                # Convert tuple to dict format (resolve_stream returns tuple, but monitor_chat expects dict)
                video_id = pre_check_result[0]
                live_chat_id = pre_check_result[1] if len(pre_check_result) > 1 else None

                # Build dict with required keys
                stream_dict = {
                    'video_id': video_id,
                    'live_chat_id': live_chat_id,
                    'channel_id': None,  # Unknown from cache - will be resolved during authentication
                    'channel_name': 'Cached Stream'
                }
                logger.info(f"[FLOW-TRACE] Converted cache result to dict: {stream_dict}")
                return stream_dict
            else:
                logger.info(f"[BOT][AI] [QWEN-INFO] [FAIL] No cached stream or last stream ended - need full channel scan")
        except Exception as e:
            logger.warning(f"[BOT][AI] [QWEN-ERROR] First principles check failed: {e} - proceeding to channel rotation")

        # Use QWEN to prioritize channels if available
        if hasattr(self, 'qwen_youtube') and self.qwen_youtube:
            # First check if QWEN recommends checking at all
            should_check, reason = self.qwen_youtube.should_check_now()
            logger.info(f"[BOT][AI] [QWEN-GLOBAL] Global check decision: {should_check} - {reason}")

            if not should_check:
                logger.warning(f"[BOT][AI] [QWEN-DECISION] Skipping channel checks: {reason}")
                return None

            # Build channel list with proper names
            channel_list = []
            for ch_id in channels_to_check:
                ch_name = self.stream_resolver._get_channel_display_name(ch_id) if self.stream_resolver else ch_id
                channel_list.append((ch_id, ch_name))

            # Get QWEN's prioritized order
            prioritized = self.qwen_youtube.prioritize_channels(channel_list)
            logger.info(f"[BOT][AI] [QWEN-PRIORITY] [TARGET] Analyzed and reordered {len(prioritized)} channels")

            if prioritized:
                top_channel_id, top_channel_name, top_score = prioritized[0]
                if top_score >= 1.05:
                    self.high_priority_pending = True
                    self.priority_reason = f"High-confidence window for {top_channel_name} (score {top_score:.2f})"
                else:
                    self.high_priority_pending = False
                    self.priority_reason = None
            else:
                self.high_priority_pending = False
                self.priority_reason = None

            # Reorder channels based on QWEN priority (extract channel IDs from tuples)
            channels_to_check = [ch_id for ch_id, _, _ in prioritized]

            # Log the optimized order with scores
            for ch_id, ch_name, score in prioritized[:3]:  # Show top 3
                logger.info(f"[BOT][AI] [QWEN-SCORE] {ch_name}: Priority score {score:.2f}")

            logger.info(f"[BOT][AI] [QWEN-ORDER] Optimized check order based on heat levels and patterns")

        logger.info(f"   Checking {len(channels_to_check)} channels in QWEN-optimized sequence:")
        for idx, ch_id in enumerate(channels_to_check, 1):
            ch_name = self.stream_resolver._get_channel_display_name(ch_id) if self.stream_resolver else ch_id
            logger.info(f"   {idx}. {ch_name}")
        logger.info("="*60)

        # Try each channel and collect all active streams
        found_streams = []  # Collect all found streams for social media posting
        first_stream_to_monitor = None  # The stream we'll actually monitor
        check_results = {}  # Track results for summary

        for i, channel_id in enumerate(channels_to_check, 1):
            channel_name = self.stream_resolver._get_channel_display_name(channel_id)
            logger.info(f"\n[[SEARCH] Channel {i}/{len(channels_to_check)}] Checking {channel_name}...")
            logger.info(f"[BOT][AI] [QWEN-SCAN] Initiating channel scan #{i}")
            try:
                result = self.stream_resolver.resolve_stream(channel_id)
                if result and result[0]:
                    check_results[channel_name] = '[OK] LIVE'
                    # Get channel-specific emoji
                    channel_tag = "MOVE2JAPAN" if "Move2Japan" in channel_name else ("UNDAODU" if "UnDaoDu" in channel_name else ("FOUNDUPS" if "FoundUps" in channel_name else "CHANNEL"))
                    logger.info(f"[{channel_tag} Channel {i}/{len(channels_to_check)}] {channel_name}: STREAM FOUND!")
                else:
                    check_results[channel_name] = "offline"
                    logger.info(f"[CHECK Channel {i}/{len(channels_to_check)}] {channel_name}: No active stream")
            except Exception as e:
                logger.error(f"[CHECK {i}/{len(channels_to_check)}] {channel_name}... ERROR: {e}")
                result = None
                # Continue checking other channels even if one fails
                continue

            if result and result[0]:  # Accept stream even without chat_id
                logger.info(f"[FLOW-TRACE] Stream found! result={result}")
                video_id = result[0]
                live_chat_id = result[1] if len(result) > 1 else None
                logger.info(f"[FLOW-TRACE] video_id={video_id}, chat_id={live_chat_id}")

                channel_name = self.stream_resolver._get_channel_display_name(channel_id)
                logger.info(f"[FLOW-TRACE] channel_name={channel_name}")
                if not live_chat_id:
                    logger.info(f"[WARN] Found stream on {channel_name} but chat_id not available (likely quota exhausted)")

                    # CRITICAL: Attempt to get chat_id with credential rotation
                    logger.info(f"[REFRESH] Attempting to get chat_id with credential rotation...")
                    try:
                        # Reuse existing stream_resolver to avoid rapid re-initialization loop
                        # Creating new StreamResolver() every retry causes 20+ inits/sec (StreamDB migration spam)
                        retry_result = self.stream_resolver.resolve_stream(channel_id=channel_id)

                        if retry_result and len(retry_result) > 1 and retry_result[1]:
                            live_chat_id = retry_result[1]
                            logger.info(f"[OK] Got chat_id after credential rotation: {live_chat_id}")
                        else:
                            logger.warning("[WARN] Credential rotation failed - still no chat_id")
                            logger.info(f"[OK] Accepting stream anyway - video ID: {video_id} [CELEBRATE]")
                    except Exception as e:
                        logger.error(f"[FAIL] Error during credential rotation: {e}")
                        logger.info(f"[OK] Accepting stream anyway - video ID: {video_id} [CELEBRATE]")
                else:
                    logger.info(f"[OK] Found stream on {channel_name} with video ID: {video_id} [CELEBRATE]")

                # === CARDIOVASCULAR: Record stream start (WSP 91) ===
                if self.telemetry:
                    try:
                        self.current_stream_id = self.telemetry.record_stream_start(
                            video_id=video_id,
                            channel_name=channel_name,
                            channel_id=channel_id
                        )
                        logger.info(f"[HEART] Stream session started (SQLite ID: {self.current_stream_id})")
                    except Exception as e:
                        logger.warning(f"Failed to record stream start: {e}")

                # QWEN learns from successful detection
                if self.qwen_youtube:
                    self.qwen_youtube.record_stream_found(channel_id, channel_name, video_id)
                    logger.info(f"[BOT][AI] [QWEN-LEARN] [BOOKS] Recorded successful stream detection pattern")

                # Social media posting is handled by social media DAE orchestrator
                # Store stream info for later posting coordination
                logger.info(f"[NOTE] Detected stream on {channel_name} - queueing for social media posting")

                # Get stream title for social media posting
                stream_title = None
                if self.stream_resolver:
                    # Try to get title from stream resolver
                    stream_title = self.stream_resolver._get_stream_title(video_id)

                if not stream_title:
                    # Fallback: Use channel name + "Live Stream"
                    stream_title = f"{channel_name} is LIVE!"

                logger.info(f"[STREAM] Stream title: {stream_title}")

                # Store the stream info
                stream_info = {
                    'video_id': video_id,
                    'live_chat_id': live_chat_id,
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'title': stream_title  # Add actual title for social media posting
                }
                logger.info(f"[FLOW-TRACE] Created stream_info: {stream_info}")
                found_streams.append(stream_info)
                logger.info(f"[FLOW-TRACE] Appended to found_streams, count={len(found_streams)}")

                # Remember the first stream found for monitoring
                if not first_stream_to_monitor:
                    first_stream_to_monitor = stream_info
                    logger.info(f"[FLOW-TRACE] Set first_stream_to_monitor")

                # CRITICAL FIX: Break out of channel checking loop immediately when we find streams
                # We only need ONE stream to monitor, so stop wasting time checking other channels
                logger.info(f"[TARGET] Found active stream on {channel_name} - stopping channel scan to post immediately")
                logger.info(f"[FLOW-TRACE] About to break from channel loop")
                break  # Exit the channel checking loop

        # Report results
        logger.info(f"[FLOW-TRACE] After channel loop: found_streams count={len(found_streams)}")
        logger.info("[BOT][AI] [QWEN-EVALUATE] Analyzing search results...")
        if found_streams:
            logger.info(f"[FLOW-TRACE] Entering found_streams block, count={len(found_streams)}")
            # Deduplicate streams by video_id (same stream may appear on multiple channels)
            unique_streams = {}
            for stream in found_streams:
                video_id = stream['video_id']
                if video_id not in unique_streams:
                    unique_streams[video_id] = stream
                else:
                    # Log that we found a duplicate
                    logger.info(f"[DUPLICATE] Same stream {video_id} found on {stream['channel_name']} (already found on {unique_streams[video_id]['channel_name']})")

            # Use only unique streams
            found_streams = list(unique_streams.values())
            logger.info(f"[FLOW-TRACE] After dedup: unique streams count={len(found_streams)}")

            if found_streams and not first_stream_to_monitor:
                first_stream_to_monitor = found_streams[0]
                logger.info(f"[FLOW-TRACE] Updated first_stream_to_monitor after dedup")

            logger.info(f"\n[OK] Found {len(found_streams)} unique stream(s):")
            for stream in found_streams:
                logger.info(f"  - {stream['channel_name']}: {stream['video_id']}")

            # SEMANTIC SWITCHING: Only post if this is a NEW stream (not same one we're already monitoring)
            should_post = True
            for stream in found_streams:
                if stream['video_id'] == self._last_stream_id:
                    logger.info(f"[REFRESH] [SEMANTIC-SWITCH] Already monitoring/posted stream {stream['video_id']} - skipping duplicate post")
                    should_post = False
                    break

            # Only trigger social media posting if we have NEW unique streams
            if should_post:
                if len(found_streams) == 1:
                    logger.info(f"[NOTE] Single NEW stream detected on {found_streams[0]['channel_name']} - posting to social media")
                elif len(found_streams) > 1:
                    logger.info(f"[NOTE] Multiple NEW unique streams detected - posting all to social media")

                # Trigger social media posting for new unique streams only
                logger.info(f"[FINGERPRINT-HANDOFF-1] About to call _trigger_social_media_posting_for_streams with {len(found_streams)} streams")
                import time
                time.sleep(0.5)  # Brief pause for visibility
                self._trigger_social_media_posting_for_streams(found_streams)
                logger.info(f"[FINGERPRINT-HANDOFF-2] Returned from _trigger_social_media_posting_for_streams")
            else:
                logger.info("[SEMANTIC-SWITCH] Skipped posting - stream already active in current session")

            logger.info(f"[STREAM] Will monitor first stream: {found_streams[0]['channel_name']}")
            logger.info("[BOT][AI] [QWEN-SUCCESS] Stream detection successful - transitioning to monitor phase")
            return first_stream_to_monitor
        else:
            # Show rotation summary
            logger.info("\n" + "="*60)
            logger.info("[CLIPBOARD] ROTATION SUMMARY:")
            for channel, status in check_results.items():
                logger.info(f"   {channel}: {status}")
            logger.info(f"\n[FAIL] No active livestreams found (checked {len(channels_to_check)} channels)")

            # QWEN provides intelligence summary
            if self.qwen_youtube:
                logger.info("[BOT][AI] [QWEN-LEARN] Recording no-stream pattern for time optimization")
                summary = self.qwen_youtube.get_intelligence_summary()
                logger.info(f"[BOT][AI] [QWEN-SUMMARY] Current intelligence state:")
                for line in summary.split('\n')[:5]:  # Show first 5 lines
                    if line.strip():
                        logger.info(f"    {line}")

            logger.info("Will check again in 30 minutes...")
            logger.info("="*60)
            return None

    def _trigger_social_media_posting_for_streams(self, found_streams):
        """
        Trigger social media posting for detected streams using proper orchestration.
        Handles sequential posting and channel-specific logic.
        """
        import time
        logger.info("[FINGERPRINT-HANDOFF-3] === ENTERED _trigger_social_media_posting_for_streams ===")
        time.sleep(0.5)
        logger.info(f"[FINGERPRINT-HANDOFF-4] Received {len(found_streams)} streams")
        logger.info("="*80)
        logger.info("[SOCIAL] SOCIAL MEDIA POSTING ORCHESTRATION")
        logger.info("="*80)

        try:
            logger.info("[FINGERPRINT-HANDOFF-5] Importing refactored_posting_orchestrator...")
            time.sleep(0.5)
            # Import the refactored posting orchestrator
            from modules.platform_integration.social_media_orchestrator.src.refactored_posting_orchestrator import get_orchestrator
            logger.info("[FINGERPRINT-HANDOFF-6] Calling get_orchestrator()...")
            time.sleep(0.5)
            orchestrator = get_orchestrator()
            logger.info(f"[FINGERPRINT-HANDOFF-7] Orchestrator loaded: {type(orchestrator).__name__}")
            time.sleep(0.5)
            logger.info("[OK] Social media orchestrator loaded")

            # Hand off ALL streams to social media orchestrator
            # The orchestrator handles priority, sequencing, browser selection, and LinkedIn page mapping
            logger.info(f"[HANDOFF] Sending {len(found_streams)} stream(s) to Social Media Orchestrator")
            logger.info(f"[FINGERPRINT-HANDOFF-8] About to call handle_multiple_streams_detected()...")
            time.sleep(0.5)

            # Use the new multi-stream handler method (WSP 3 compliant)
            result = orchestrator.handle_multiple_streams_detected(found_streams)
            logger.info(f"[FINGERPRINT-HANDOFF-9] Orchestrator returned: success={result.get('success')}")
            time.sleep(0.5)

            if result.get('success'):
                logger.info(f"[SUCCESS] Orchestrator processed {result.get('streams_processed')} streams")
            else:
                logger.warning(f"[WARNING] Orchestrator reported issues: {result.get('errors')}")

            # All posting now handled by orchestrator
            logger.info("[COMPLETE] Social media posting handoff complete")
            logger.info("[FINGERPRINT-HANDOFF-10] === EXITING _trigger_social_media_posting_for_streams ===")
            logger.info("[FLOW-TRACE] === EXITING _trigger_social_media_posting_for_streams (success) ===")

        except ImportError as e:
            logger.error(f"[FLOW-TRACE] ImportError in _trigger_social_media_posting_for_streams: {e}")
            logger.error(f"[FAIL] Failed to import social media orchestrator: {e}")
        except Exception as e:
            logger.error(f"[FLOW-TRACE] Exception in _trigger_social_media_posting_for_streams: {e}")
            logger.error(f"[FAIL] Social media posting orchestration failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.error("[FLOW-TRACE] === EXITING _trigger_social_media_posting_for_streams (error) ===")

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
                        rotation_accounts = ["Move2Japan", "UnDaoDu", "FoundUps"]
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
                service = get_authenticated_service()
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
                os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw'),  # Move2Japan - PRIORITY 1 - FIXED!
                os.getenv('FOUNDUPS_CHANNEL_ID', 'UCSNTUXjAgpd4sgWYP0xoJgw'),  # FoundUps - PRIORITY 2
                os.getenv('UNDAODU_CHANNEL_ID', 'UCfHM9Fw9HD-NwiS0seD_oIA'),   # UnDaoDu - PRIORITY 3 - FIXED!
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

        Architecture (2025-12-30 Fix):
        - This loop runs INDEPENDENTLY from stream detection
        - Processes all channels every `interval_minutes` minutes
        - Does NOT stop when live stream is found
        - Stream detection runs in PARALLEL (separate task)

        Args:
            runner: EngagementRunner instance
            max_comments: Max comments per channel (0=UNLIMITED)
            mode: Execution mode (subprocess/thread/inproc)
            interval_minutes: Minutes between engagement cycles (default: 10)
        """
        cycle_count = 0
        interval_seconds = interval_minutes * 60

        logger.info("=" * 70)
        logger.info("[COMMENT-LOOP] INDEPENDENT COMMENT ENGAGEMENT LOOP STARTED")
        logger.info(f"[COMMENT-LOOP] Interval: {interval_minutes} minutes | Mode: {mode}")
        logger.info(f"[COMMENT-LOOP] Max per channel: {max_comments if max_comments > 0 else 'UNLIMITED'}")
        logger.info("[COMMENT-LOOP] This loop runs INDEPENDENTLY from stream detection")
        logger.info("=" * 70)

        while True:
            try:
                cycle_count += 1
                logger.info(f"\n[COMMENT-LOOP] === Cycle #{cycle_count} starting ===")

                # Run multi-channel engagement
                await self._run_multi_channel_engagement(runner, max_comments=max_comments, mode=mode)

                logger.info(f"[COMMENT-LOOP] Cycle #{cycle_count} complete - sleeping {interval_minutes} minutes...")

                # Wait before next cycle
                await asyncio.sleep(interval_seconds)

            except asyncio.CancelledError:
                logger.info(f"[COMMENT-LOOP] Loop cancelled after {cycle_count} cycles")
                raise
            except Exception as e:
                logger.error(f"[COMMENT-LOOP] Cycle #{cycle_count} error: {e}")
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

        Architecture (2025-12-28 Refactor):
        - Chrome (port 9222): Move2Japan + UnDaoDu (SAME Google account)
        - Edge (port 9223): FoundUps (DIFFERENT Google account)

        Flow:
        1. Process Move2Japan comments (Chrome)
        2. Switch to UnDaoDu (Chrome - same account picker)
        3. Process FoundUps comments (Edge - separate browser)
        4. Check live stream signal before each channel
        5. If live detected → pause rotation for that channel

        Uses TarsAccountSwapper for Chrome channels only (same Google account).
        FoundUps requires direct Edge connection.
        """
        strict_inbox = _env_truthy("YT_INBOX_STRICT", "true")
        # Edge can run independently (separate browser + port). Default to parallel so
        # FoundUps is not starved behind long Chrome/UnDaoDu runs.
        edge_parallel = _env_truthy("YT_EDGE_PARALLEL", "true")

        # CHROME ACCOUNTS (same Google account - can switch via YouTube picker)
        chrome_accounts = [
            ("Move2Japan", os.getenv("MOVE2JAPAN_CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw")),
            ("UnDaoDu", os.getenv("UNDAODU_CHANNEL_ID", "UCfHM9Fw9HD-NwiS0seD_oIA")),
        ]

        # EDGE ACCOUNT (different Google account - requires separate browser)
        edge_account = ("FoundUps", os.getenv("FOUNDUPS_CHANNEL_ID", "UCSNTUXjAgpd4sgWYP0xoJgw"))

        total_channels = len(chrome_accounts) + 1  # Chrome accounts + FoundUps (Edge)
        logger.info("=" * 70)
        logger.info("[ROTATE] MULTI-CHANNEL COMMENT ENGAGEMENT")
        logger.info(f"[ROTATE] Processing {total_channels} channels:")
        logger.info(f"[ROTATE]   Chrome (9222): {', '.join([a[0] for a in chrome_accounts])}")
        logger.info(f"[ROTATE]   Edge (9223): {edge_account[0]}")
        logger.info(f"[ROTATE] Mode: {mode} | Max per channel: {max_comments if max_comments > 0 else 'UNLIMITED'}")
        logger.info("=" * 70)

        total_processed = 0
        chrome_driver = None
        swapper = None
        rotation_halt = False
        edge_task = None

        async def _run_edge_foundups() -> int:
            """
            Run FoundUps comment engagement via Edge (port 9223).

            IMPORTANT: Do NOT mutate `self._comment_engagement_active_channel` here when running
            in parallel, otherwise inbox-clear gating (live stream switch) can point at the wrong
            channel. We still write status into `self._comment_engagement_status`.
            """
            edge_driver = None
            foundups_name, foundups_channel_id = edge_account

            # FRESH SIGNAL CHECK for FoundUps
            try:
                from modules.platform_integration.stream_resolver.src.live_stream_signal import get_live_channel
                live_channel = get_live_channel()
            except ImportError:
                live_channel = None

            # Check if FoundUps has a live stream (skip if so)
            if live_channel == foundups_channel_id:
                logger.info(f"[SIGNAL] {foundups_name} has live stream - skipping comment processing")
                return 0

            logger.info(f"\n[ROTATE] [Edge] Processing {foundups_name} comments...")

            try:
                from selenium import webdriver
                from selenium.webdriver.edge.options import Options as EdgeOptions
                from modules.infrastructure.dependency_launcher.src.dae_dependencies import launch_edge

                edge_port = int(os.getenv("FOUNDUPS_EDGE_PORT", "9223"))
                edge_ok, edge_msg = launch_edge()
                if not edge_ok:
                    logger.warning(f"[ROTATE] Edge auto-launch failed: {edge_msg}")
                edge_opts = EdgeOptions()
                edge_opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{edge_port}")

                # Non-blocking Edge connection
                edge_driver = await asyncio.to_thread(webdriver.Edge, options=edge_opts)
                logger.info(f"[ROTATE] Connected to Edge on port {edge_port}")

                # Navigate to FoundUps Studio inbox (ensure correct page)
                from modules.infrastructure.dependency_launcher.src.dae_dependencies import STUDIO_FILTER
                foundups_studio_url = (
                    f"https://studio.youtube.com/channel/{foundups_channel_id}/comments/inbox?filter={STUDIO_FILTER}"
                )
                logger.info(f"[ROTATE] Navigating to {foundups_name} Studio inbox...")
                await asyncio.to_thread(edge_driver.get, foundups_studio_url)
                await asyncio.sleep(5)

                self._log_studio_context(
                    foundups_channel_id,
                    label=f"{foundups_name} comment_engagement",
                    driver=edge_driver,
                )
                result = await runner.run_engagement(
                    channel_id=foundups_channel_id,
                    video_id=None,
                    max_comments=max_comments,
                    browser_port=9223,  # Edge browser for FoundUps account
                )

                result = result or {}
                stats = result.get("stats", {})
                processed = stats.get("comments_processed", 0)

                self._comment_engagement_status[foundups_channel_id] = {
                    "all_processed": bool(stats.get("all_processed", False)),
                    "stats": stats,
                    "error": result.get("error"),
                    "updated_at": time.time(),
                }

                error_text = result.get("error")
                session_recovered = False

                if error_text:
                    logger.error(f"[ROTATE] ❌ {foundups_name} engagement failed: {error_text}")
                else:
                    logger.info(f"[ROTATE] ✅ {foundups_name} complete: {processed} comments processed")

                if error_text and _is_session_error(error_text) and _env_truthy("YT_RECONNECT_ON_SESSION_ERROR", "true"):
                    logger.warning(f"[ROTATE] Edge session error on {foundups_name}; attempting reconnect")
                    edge_driver = await self._reconnect_edge_driver(edge_port)
                    if edge_driver:
                        try:
                            await asyncio.to_thread(edge_driver.get, foundups_studio_url)
                            await asyncio.sleep(5)
                        except Exception as refresh_err:
                            logger.warning(f"[ROTATE] Edge navigation after reconnect failed: {refresh_err}")
                        session_recovered = True
                    else:
                        logger.warning(f"[ROTATE] Edge reconnect failed for {foundups_name}")

                verify_retries = int(os.getenv("YT_INBOX_VERIFY_RETRIES", "1"))
                verify_timeout = float(os.getenv("YT_INBOX_VERIFY_TIMEOUT", "15"))
                verify_result = None
                for attempt in range(1, verify_retries + 1):
                    verify_result = await self._verify_studio_inbox_clear(
                        edge_driver,
                        foundups_channel_id,
                        foundups_name,
                        timeout_seconds=verify_timeout,
                    )
                    if verify_result is True:
                        break
                    if verify_result is False:
                        logger.warning(
                            f"[VERIFY] {foundups_name} inbox not clear; re-running engagement "
                            f"(attempt {attempt}/{verify_retries})"
                        )
                        self._log_studio_context(
                            foundups_channel_id,
                            label=f"{foundups_name} comment_engagement_retry",
                            driver=edge_driver,
                        )
                        retry_result = await runner.run_engagement(
                            channel_id=foundups_channel_id,
                            video_id=None,
                            max_comments=max_comments,
                            browser_port=9223,
                        )

                        retry_result = retry_result or {}
                        retry_stats = retry_result.get("stats", {})
                        retry_processed = retry_stats.get("comments_processed", 0)

                        self._comment_engagement_status[foundups_channel_id] = {
                            "all_processed": bool(retry_stats.get("all_processed", False)),
                            "stats": retry_stats,
                            "error": retry_result.get("error"),
                            "updated_at": time.time(),
                        }

                        if retry_result.get("error"):
                            logger.error(f"[ROTATE] ❌ {foundups_name} retry failed: {retry_result.get('error')}")
                        else:
                            logger.info(
                                f"[ROTATE] ✅ {foundups_name} retry complete: {retry_processed} comments processed"
                            )
                        processed += retry_processed
                        continue

                    logger.warning(
                        f"[VERIFY] {foundups_name} inbox verification inconclusive; will recheck next cycle"
                    )
                    break

                if strict_inbox:
                    if error_text and not session_recovered:
                        logger.warning(f"[VERIFY] Strict inbox mode: holding rotation on {foundups_name} (error)")
                    elif verify_result is False:
                        logger.warning(
                            f"[VERIFY] Strict inbox mode: holding rotation on {foundups_name} (unprocessed comments)"
                        )
                    elif verify_result is None:
                        logger.info(f"[VERIFY] {foundups_name} verification inconclusive; next cycle will recheck")

                return int(processed or 0)
            except Exception as e:
                logger.warning(f"[ROTATE] ⚠️ Edge connection failed: {e}")
                logger.warning(f"[ROTATE] {foundups_name} comments will be skipped")
                logger.warning(f"[ROTATE] To enable: Launch Edge with --remote-debugging-port=9223")
                return 0

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 1: CHROME CHANNELS (Move2Japan + UnDaoDu - same Google account)
        # ═══════════════════════════════════════════════════════════════════
        # DEBUG: Set YT_SKIP_CHROME=true to skip Chrome and test Edge only
        skip_chrome = _env_truthy("YT_SKIP_CHROME", "false")
        if skip_chrome:
            logger.info("[ROTATE] ⏭️ SKIPPING CHROME (YT_SKIP_CHROME=true) - Testing Edge only")

        if not skip_chrome:
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from modules.communication.video_comments.skills.tars_account_swapper.account_swapper_skill import TarsAccountSwapper
                from modules.infrastructure.dependency_launcher.src.dae_dependencies import launch_chrome

                chrome_port = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9222"))
                chrome_ok, chrome_msg = launch_chrome()
                if not chrome_ok:
                    logger.warning(f"[ROTATE] Chrome auto-launch failed: {chrome_msg}")
                opts = Options()
                opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_port}")

                # FIX (2025-12-31): Use asyncio.to_thread to prevent blocking event loop
                # This was blocking stream detection from running!
                chrome_driver = await asyncio.to_thread(webdriver.Chrome, options=opts)
                swapper = TarsAccountSwapper(chrome_driver)
                logger.info(f"[ROTATE] Connected to Chrome on port {chrome_port}")

                # SMART ROTATION: Detect current account state to minimize switching
                # Check current URL to see if we are already on one of the target channels
                try:
                    current_url = chrome_driver.current_url
                    # Noise control: Studio adds long querystring filters; we only need the stable base path.
                    url_base = (current_url or "").split("#", 1)[0].split("?", 1)[0]
                    logger.info(f"[ROTATE] Current Chrome URL: {url_base}")
                    current_channel_id = await self._detect_current_channel_id(chrome_driver)

                    if current_channel_id:
                        # Find if this channel ID is in our list
                        current_account = next((acc for acc in chrome_accounts if acc[1] == current_channel_id), None)

                        if current_account:
                            logger.info(f"[ROTATE] [SMART] Detected active session on {current_account[0]}")
                            logger.info(f"[ROTATE] [SMART] Reordering queue: {current_account[0]} -> Others")

                            # Move current account to front
                            chrome_accounts.remove(current_account)
                            chrome_accounts.insert(0, current_account)
                        else:
                            logger.info(f"[ROTATE] [SMART] Current channel {current_channel_id} not in rotation list")
                    else:
                        logger.info("[ROTATE] [SMART] Not currently on a Studio channel page")

                except Exception as e:
                    logger.warning(f"[ROTATE] [SMART] Failed to detect current state: {e}")

            except Exception as e:
                logger.error(f"[ROTATE] ❌ Failed to connect to Chrome: {e}")
                logger.warning(f"[ROTATE] Chrome channels (Move2Japan, UnDaoDu) will be skipped")

        # Start Edge in parallel (separate browser) so it isn't blocked behind long Chrome runs.
        if edge_parallel:
            try:
                edge_task = asyncio.create_task(_run_edge_foundups())
                logger.info("[ROTATE] Edge scheduled in PARALLEL (YT_EDGE_PARALLEL=true)")
            except Exception as e:
                logger.warning(f"[ROTATE] Failed to schedule Edge task: {e}")
                edge_task = None

        # Check live stream signal before processing
        if swapper:
            for idx, (account_name, channel_id) in enumerate(chrome_accounts, 1):
                # FRESH SIGNAL CHECK: Check if this channel has a live stream (pause rotation)
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
                    logger.info(f"[ROTATE] Switching to {account_name}...")
                    success = await swapper.swap_to(account_name)

                    if not success:
                        logger.warning(f"[ROTATE] ⚠️ Failed to switch to {account_name}")
                        if idx == 1:
                            logger.info(f"[ROTATE] Assuming already on {account_name}, continuing...")
                        else:
                            logger.warning(f"[ROTATE] Skipping {account_name}")
                            continue
                    else:
                        logger.info(f"[ROTATE] ✅ Switched to {account_name} successfully")

                    # HUMAN-LIKE: Refresh page for fresh comments
                    logger.info(f"[ROTATE] Refreshing page for {account_name}...")
                    chrome_driver.refresh()
                    await asyncio.sleep(5)

                except Exception as e:
                    logger.error(f"[ROTATE] ❌ Account switch error: {e}")
                    if idx > 1:
                        continue

                # Process comments
                try:
                    self._comment_engagement_active_channel = channel_id
                    self._log_studio_context(channel_id, label=f"{account_name} comment_engagement", driver=chrome_driver)
                    result = await runner.run_engagement(
                        channel_id=channel_id,
                        video_id=None,
                        max_comments=max_comments
                    )

                    result = result or {}
                    stats = result.get('stats', {})
                    processed = stats.get('comments_processed', 0)
                    total_processed += processed

                    self._comment_engagement_status[channel_id] = {
                        "all_processed": bool(stats.get("all_processed", False)),
                        "stats": stats,
                        "error": result.get('error'),
                        "updated_at": time.time(),
                    }

                    error_text = result.get('error')
                    session_recovered = False

                    if result.get('error'):
                        logger.error(f"[ROTATE] ❌ {account_name} engagement failed: {result.get('error')}")
                    else:
                        logger.info(f"[ROTATE] ✅ {account_name} complete: {processed} comments processed")

                    if error_text and _is_session_error(error_text) and _env_truthy("YT_RECONNECT_ON_SESSION_ERROR", "true"):
                        logger.warning(f"[ROTATE] Chrome session error on {account_name}; attempting reconnect")
                        chrome_driver = await self._reconnect_chrome_driver(chrome_port)
                        if chrome_driver:
                            swapper = TarsAccountSwapper(chrome_driver)
                            try:
                                await swapper.swap_to(account_name)
                            except Exception as swap_err:
                                logger.warning(f"[ROTATE] Chrome reconnect swap failed: {swap_err}")
                            try:
                                chrome_driver.refresh()
                                await asyncio.sleep(5)
                            except Exception as refresh_err:
                                logger.warning(f"[ROTATE] Chrome refresh after reconnect failed: {refresh_err}")
                            session_recovered = True
                        else:
                            logger.warning(f"[ROTATE] Chrome reconnect failed for {account_name}")

                    verify_retries = int(os.getenv("YT_INBOX_VERIFY_RETRIES", "1"))
                    verify_timeout = float(os.getenv("YT_INBOX_VERIFY_TIMEOUT", "15"))
                    verify_result = None
                    for attempt in range(1, verify_retries + 1):
                        verify_result = await self._verify_studio_inbox_clear(
                            chrome_driver,
                            channel_id,
                            account_name,
                            timeout_seconds=verify_timeout,
                        )
                        if verify_result is True:
                            break
                        if verify_result is False:
                            logger.warning(
                                f"[VERIFY] {account_name} inbox not clear; re-running engagement "
                                f"(attempt {attempt}/{verify_retries})"
                            )
                            self._comment_engagement_active_channel = channel_id
                            self._log_studio_context(
                                channel_id,
                                label=f"{account_name} comment_engagement_retry",
                                driver=chrome_driver,
                            )
                            retry_result = await runner.run_engagement(
                                channel_id=channel_id,
                                video_id=None,
                                max_comments=max_comments
                            )

                            retry_result = retry_result or {}
                            retry_stats = retry_result.get('stats', {})
                            retry_processed = retry_stats.get('comments_processed', 0)
                            total_processed += retry_processed

                            self._comment_engagement_status[channel_id] = {
                                "all_processed": bool(retry_stats.get("all_processed", False)),
                                "stats": retry_stats,
                                "error": retry_result.get('error'),
                                "updated_at": time.time(),
                            }

                            if retry_result.get('error'):
                                logger.error(
                                    f"[ROTATE] ❌ {account_name} retry failed: {retry_result.get('error')}"
                                )
                            else:
                                logger.info(
                                    f"[ROTATE] ✅ {account_name} retry complete: {retry_processed} comments processed"
                                )
                            continue

                        logger.warning(
                            f"[VERIFY] {account_name} inbox verification inconclusive; will recheck next cycle"
                        )
                        break


                    if strict_inbox:
                        if error_text and not session_recovered:
                            logger.warning(f"[VERIFY] Strict inbox mode: holding rotation on {account_name} (error)")
                            rotation_halt = True
                        elif verify_result is False:
                            # FIX (2025-12-30): Only halt on False (confirmed has comments), NOT on None (inconclusive)
                            # None = timeout/error → continue to next channel (Edge/FoundUps)
                            # False = confirmed unprocessed comments → halt and retry
                            logger.warning(f"[VERIFY] Strict inbox mode: holding rotation on {account_name} (unprocessed comments)")
                            rotation_halt = True
                        elif verify_result is None:
                            # Inconclusive verification - log but continue rotation
                            logger.info(f"[VERIFY] {account_name} verification inconclusive; continuing to next channel")
                except Exception as e:
                    logger.error(f"[ROTATE] ❌ {account_name} exception: {e}", exc_info=True)
                    self._comment_engagement_status[channel_id] = {
                        "all_processed": False,
                        "stats": {},
                        "error": str(e),
                        "updated_at": time.time(),
                    }
                    if strict_inbox:
                        rotation_halt = True

                if rotation_halt:
                    logger.warning(f"[ROTATE] Rotation halted after {account_name}")
                    break

                # Check for live stream signal after each channel
                if self._live_stream_pending and _env_truthy("YT_STOP_ROTATION_ON_LIVE", "true"):
                    logger.info(f"[ROTATE] Live stream pending - stopping Chrome rotation after {account_name}")
                    break

        # Run Edge sequentially if parallel is disabled (legacy behavior)
        if not edge_parallel:
            total_processed += await _run_edge_foundups()
        elif edge_task:
            # Edge already running; incorporate counts if/when it completes.
            try:
                total_processed += await edge_task
            except Exception as e:
                logger.warning(f"[ROTATE] Edge task failed: {e}")

        logger.info("=" * 70)
        logger.info(f"[ROTATE] ✅ MULTI-CHANNEL ENGAGEMENT COMPLETE")
        logger.info(f"[ROTATE] Total comments processed: {total_processed}")
        logger.info(f"[ROTATE] Channels: Chrome ({len(chrome_accounts)}) + Edge (1)")
        logger.info("=" * 70)

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

                default_channel_id = os.getenv("COMMUNITY_CHANNEL_ID") or os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')
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
                        "heartbeat_count": heartbeat_count
                    }
                    with open(jsonl_path, 'a', encoding='utf-8') as f:
                        json.dump(heartbeat_data, f)
                        f.write('\n')

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
                                skill_path = repo_root / "modules" / "communication" / "livechat" / "skills" / "youtube_daemon_monitor.json"

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
        """Get current DAE status."""
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
            }
        }

        if self.livechat:
            status['stats'] = self.livechat.get_moderation_stats()

        return status


def main():
    """Main entry point for the Auto Moderator DAE."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run DAE
    dae = AutoModeratorDAE()
    asyncio.run(dae.run())


if __name__ == "__main__":
    main()
