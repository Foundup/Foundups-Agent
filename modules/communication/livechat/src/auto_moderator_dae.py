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
import time
from typing import Optional, Dict
from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
from modules.platform_integration.youtube_auth.src.monitored_youtube_service import create_monitored_service
from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver

# Import WSP-compliant livechat_core
from .livechat_core import LiveChatCore

logger = logging.getLogger(__name__)


class AutoModeratorDAE:
    """
    WSP-Compliant Auto Moderator DAE
    
    Phases per WSP 27:
    -1: Signal - YouTube chat messages
     0: Knowledge - User profiles, chat history
     1: Protocol - Moderation rules, consciousness responses
     2: Agentic - Autonomous moderation and interaction
    """
    
    def __init__(self):
        """Initialize the Auto Moderator DAE."""
        logger.info("[ROCKET] Initializing Auto Moderator DAE (WSP-Compliant)")
        
        self.service = None
        self.credentials = None
        self.credential_set = None
        self.livechat = None
        self.stream_resolver = None
        self._last_stream_id = None
        self.transition_start = None
        
        # WRE Integration for recursive learning
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

        # QWEN Intelligence Integration for smart decision making
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

        # QWEN YouTube Integration for channel prioritization
        try:
            from .qwen_youtube_integration import get_qwen_youtube
            self.qwen_youtube = get_qwen_youtube()  # Use singleton for shared intelligence
            logger.info("[BOT][AI] [QWEN-YOUTUBE] Channel prioritization intelligence connected")
        except Exception as e:
            logger.debug(f"[BOT][AI] [QWEN-YOUTUBE] Integration not available: {e}")
            self.qwen_youtube = None

        self.high_priority_pending = False
        self.priority_reason = None

        logger.info("[OK] Auto Moderator DAE initialized")
    
    def connect(self) -> bool:
        """
        Phase -1/0: Connect to YouTube - NO-QUOTA mode by default.
        Only use API tokens when we actually find a stream.
        AUTOMATICALLY REFRESHES TOKENS on startup to keep them fresh!

        Returns:
            Success status
        """
        logger.info("🔌 Starting in NO-QUOTA mode to preserve API tokens...")

        # TOKEN REFRESH DISABLED DURING STARTUP - Prevents blocking on OAuth
        # Token refresh should be done before starting the daemon using:
        # python modules/platform_integration/youtube_auth/scripts/auto_refresh_tokens.py
        logger.info("[IDEA] Token refresh happens on-demand when authentication is needed")
        logger.info("   To manually refresh: python modules/platform_integration/youtube_auth/scripts/auto_refresh_tokens.py")

        # Default to NO-QUOTA mode for stream searching
        # We'll only authenticate when we actually find a stream
        self.service = None
        self.credential_set = "NO-QUOTA"
        logger.info("🌐 Using NO-QUOTA web scraping for stream discovery")
        logger.info("🛡️ Smart verification: NO-QUOTA first, API only for live/uncertain videos")
        logger.info("💰 MAXIMUM API preservation - API only when posting is possible")

        return True
    
    def find_livestream(self) -> Optional[Dict[str, Optional[str]]]:
        """
        Find active livestream on the channel.
        Can check multiple channels if configured.
        QWEN intelligence decides HOW to search based on patterns.

        Returns:
            Stream metadata dict containing video_id, live_chat_id, channel_id, and channel_name, or None
        """
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
                logger.info(f"[BOT][AI] [QWEN-MONITOR] ⚠️ Monitor analysis incomplete: {e}")

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
        channels_to_check = [
            os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UCklMTNnu5POwRmQsg5JJumA'),  # Move2Japan channel - PRIORITY 1
            os.getenv('CHANNEL_ID2', 'UCSNTUXjAgpd4sgWYP0xoJgw'),  # FoundUps channel - PRIORITY 2
            os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw'),   # UnDaoDu main channel - PRIORITY 3
        ]
        
        # Filter out None values and remove duplicates
        channels_to_check = [ch for ch in channels_to_check if ch]

        # Show rotation header with clear channel list
        logger.info("="*60)
        logger.info("[REFRESH] CHANNEL ROTATION CHECK (NO-QUOTA MODE with QWEN Intelligence)")
        logger.info("[BOT][AI] [QWEN-INIT] Starting intelligent channel rotation analysis")

        # PRIORITY 0: [BOT][AI] First Principles - "Is the last video still live?"
        # Check cache + DB BEFORE any channel rotation logic
        logger.info("[BOT][AI] [QWEN-FIRST-PRINCIPLES] ❓ Is the last video still live?")
        try:
            # Call resolve_stream with None to trigger Priority 1 (cache) and Priority 1.5 (Qwen DB check)
            # This checks: 1) session_cache.json, 2) last stream in DB with lenient threshold + API
            pre_check_result = self.stream_resolver.resolve_stream(channel_id=None)
            if pre_check_result and pre_check_result[0]:
                logger.info(f"[BOT][AI] [QWEN-SUCCESS] [OK] Last known stream still live! Instant reconnection.")
                logger.info(f"[ROCKET] Skipping ALL channel rotation - already found active stream: {pre_check_result[0]}")
                # Return immediately with the cached stream - no need for any other checks
                return pre_check_result
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
                    channel_emoji = "🍣" if "Move2Japan" in channel_name else ("🧘" if "UnDaoDu" in channel_name else ("🐕" if "FoundUps" in channel_name else "🎉"))
                    logger.info(f"[{channel_emoji} Channel {i}/{len(channels_to_check)}] {channel_name}: STREAM FOUND!")
                else:
                    check_results[channel_name] = '⏳ offline'
                    logger.info(f"[⏳ Channel {i}/{len(channels_to_check)}] {channel_name}: No active stream")
            except Exception as e:
                logger.error(f"🔎 [{i}/{len(channels_to_check)}] {channel_name}... ERROR: {e}")
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
                    logger.info(f"⚠️ Found stream on {channel_name} but chat_id not available (likely quota exhausted)")

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
                            logger.warning(f"⚠️ Credential rotation failed - still no chat_id")
                            logger.info(f"[OK] Accepting stream anyway - video ID: {video_id} [CELEBRATE]")
                    except Exception as e:
                        logger.error(f"[FAIL] Error during credential rotation: {e}")
                        logger.info(f"[OK] Accepting stream anyway - video ID: {video_id} [CELEBRATE]")
                else:
                    logger.info(f"[OK] Found stream on {channel_name} with video ID: {video_id} [CELEBRATE]")

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

                logger.info(f"📺 Stream title: {stream_title}")

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
                logger.info(f"  • {stream['channel_name']}: {stream['video_id']}")

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
                logger.info(f"⏭️ [SEMANTIC-SWITCH] Skipped posting - stream already active in current session")

            logger.info(f"📺 Will monitor first stream: {found_streams[0]['channel_name']}")
            logger.info("[BOT][AI] [QWEN-SUCCESS] Stream detection successful - transitioning to monitor phase")
            return first_stream_to_monitor
        else:
            # Show rotation summary
            logger.info("\n" + "="*60)
            logger.info("[CLIPBOARD] ROTATION SUMMARY:")
            for channel, status in check_results.items():
                logger.info(f"   {channel}: {status}")
            logger.info(f"\n[FAIL] No active livestreams found (checked {len(channels_to_check)} channels: 🍣🧘🐕)")

            # QWEN provides intelligence summary
            if self.qwen_youtube:
                logger.info("[BOT][AI] [QWEN-LEARN] Recording no-stream pattern for time optimization")
                summary = self.qwen_youtube.get_intelligence_summary()
                logger.info(f"[BOT][AI] [QWEN-SUMMARY] Current intelligence state:")
                for line in summary.split('\n')[:5]:  # Show first 5 lines
                    if line.strip():
                        logger.info(f"    {line}")

            logger.info(f"⏳ Will check again in 30 minutes...")
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
        logger.info("📱 SOCIAL MEDIA POSTING ORCHESTRATION")
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
                break
            
            # Calculate intelligent delay based on retries and failures
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
                    logger.info(f"📺 No stream found. Checking again in {delay:.0f} seconds...")
                elif delay < 300:
                    logger.info(f"⏳ No stream found. Waiting {delay/60:.1f} minutes (adaptive idle)...")
                else:
                    logger.info(f"💤 Idle mode: {delay/60:.1f} minutes (adaptive)")
            
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
        
        stream_info = result or {}
        video_id = stream_info.get('video_id')
        live_chat_id = stream_info.get('live_chat_id')
        channel_id = stream_info.get('channel_id')
        channel_name = stream_info.get('channel_name')

        # Now that we found a stream, try to authenticate for full functionality
        # Authenticate FIRST, then get chat_id with API
        if not self.service and video_id:
            logger.info("🔐 Stream found! Attempting authentication for chat interaction...")
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
                        target_channel_id = channel_id or os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')
                        auth_result = self.stream_resolver.resolve_stream(target_channel_id)
                        if auth_result and len(auth_result) > 1:
                            resolved_video_id = auth_result[0]
                            if resolved_video_id and resolved_video_id != video_id:
                                logger.info(f"🔁 API resolved stream {resolved_video_id} (replacing {video_id})")
                                video_id = resolved_video_id
                                stream_info['video_id'] = video_id
                            live_chat_id = auth_result[1]
                            stream_info['live_chat_id'] = live_chat_id
                            logger.info(f"[OK] Got chat ID with API: {live_chat_id[:20]}...")
                        else:
                            logger.warning("⚠️ Could not get chat ID even with API")
            except Exception as e:
                logger.warning(f"⚠️ Authentication failed: {e}")
                logger.info("🌐 Continuing in NO-QUOTA mode (view-only)")

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

        # Start monitoring
        logger.info("="*60)
        logger.info("👁️ MONITORING CHAT - WSP-COMPLIANT ARCHITECTURE")
        logger.info("="*60)

        try:
            await self.livechat.start_listening()
        except KeyboardInterrupt:
            logger.info("⏹️ Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        finally:
            if self.livechat:
                self.livechat.stop_listening()
    
    async def run(self):
        """
        Main entry point - full DAE lifecycle.
        """
        logger.info("=" * 60)
        logger.info("[AI] AUTO MODERATOR DAE STARTING")
        logger.info("WSP-Compliant: Using livechat_core architecture")
        logger.info("=" * 60)
        
        # Phase -1/0: Connect and authenticate
        if not self.connect():
            logger.error("Failed to connect to YouTube")
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
                        logger.info(f"⚠️ Idle automation completed with issues ({idle_result.get('duration', 0):.1f}s)")
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
                logger.info("⏹️ Stopped by user")
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
