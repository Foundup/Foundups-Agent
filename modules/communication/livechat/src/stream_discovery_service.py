"""
Stream Discovery Service - Extracted from AutoModeratorDAE
WSP-Compliant: WSP 72 (Module Independence), WSP 3 (Single Responsibility)

Handles:
- Livestream detection across multiple channels
- QWEN-intelligent channel prioritization
- Social media posting triggers for new streams
- Telemetry recording for stream sessions

NAVIGATION: Stream discovery and social media handoff.
-> Called by: AutoModeratorDAE.find_livestream (delegated)
-> Delegates to: StreamResolver, QWEN integration, Social Media Orchestrator
"""

import logging
import os
import time
from typing import Optional, Dict, List, Any, Callable

from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver

logger = logging.getLogger(__name__)


def _env_truthy(name: str, default: str = "false") -> bool:
    """Environment variable truthy check."""
    try:
        value = os.getenv(name, default).strip().lower()
        return value in ("1", "true", "yes", "y", "on")
    except Exception:
        return default.strip().lower() in ("1", "true", "yes", "y", "on")


class StreamDiscoveryService:
    """
    Service for discovering livestreams across YouTube channels.

    Extracted from AutoModeratorDAE to follow Single Responsibility Principle.
    Uses QWEN intelligence for channel prioritization and pattern learning.
    """

    def __init__(
        self,
        service: Optional[Any] = None,
        telemetry: Optional[Any] = None,
        qwen_monitor: Optional[Any] = None,
        qwen_youtube: Optional[Any] = None,
        monitoring_context_class: Optional[type] = None,
    ):
        """
        Initialize StreamDiscoveryService with optional dependencies.

        Args:
            service: YouTube API service (can be None for NO-QUOTA mode)
            telemetry: YouTubeTelemetryStore for stream session recording
            qwen_monitor: IntelligentMonitor for health analysis
            qwen_youtube: QWEN YouTube integration for channel prioritization
            monitoring_context_class: MonitoringContext class for QWEN
        """
        self.service = service
        self.telemetry = telemetry
        self.qwen_monitor = qwen_monitor
        self.qwen_youtube = qwen_youtube
        self.MonitoringContext = monitoring_context_class

        self.stream_resolver: Optional[StreamResolver] = None
        self._last_stream_id: Optional[str] = None
        self.current_stream_id: Optional[int] = None  # SQLite session ID

        # Priority tracking
        self.high_priority_pending = False
        self.priority_reason: Optional[str] = None

        logger.info("[STREAM-DISCOVERY] Service initialized")

    def set_last_stream_id(self, stream_id: Optional[str]) -> None:
        """Set the last monitored stream ID (for duplicate detection)."""
        self._last_stream_id = stream_id

    def get_current_stream_id(self) -> Optional[int]:
        """Get the current SQLite stream session ID."""
        return self.current_stream_id

    def _get_channels_to_check(self) -> List[str]:
        """Get list of channels to check, respecting environment overrides."""
        channels_override = os.getenv("YT_CHANNELS_TO_CHECK", "").strip()
        if channels_override:
            channels = [ch.strip() for ch in channels_override.split(",") if ch.strip()]
            logger.info(f"[CONFIG] Using YT_CHANNELS_TO_CHECK override ({len(channels)} channels)")
            return channels

        # Default channel list - PRIORITIZE MOVE2JAPAN FIRST
        channels = [
            os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw'),
            os.getenv('FOUNDUPS_CHANNEL_ID', 'UCSNTUXjAgpd4sgWYP0xoJgw'),
            os.getenv('UNDAODU_CHANNEL_ID', 'UCfHM9Fw9HD-NwiS0seD_oIA'),
            os.getenv('TEST_CHANNEL_ID', ''),
        ]
        return [ch for ch in channels if ch]

    def _run_qwen_analysis(self) -> None:
        """Run QWEN analysis before stream detection."""
        if not self.qwen_monitor or not self.MonitoringContext:
            return

        try:
            context = self.MonitoringContext(
                query="youtube_stream_detection",
                search_results=[],
                patterns_detected=["channel_rotation", "no_quota_mode"]
            )
            monitoring_result = self.qwen_monitor.monitor(context)

            health_status = getattr(monitoring_result, 'health_status', None)
            if health_status:
                logger.info(f"[QWEN-HEALTH] System health: {health_status}")
                insights = getattr(monitoring_result, 'insights', None)
                if insights:
                    logger.info(f"[QWEN-INSIGHT] {insights}")
            analysis = getattr(monitoring_result, 'analysis', None)
            if analysis:
                logger.info(f"[QWEN-ANALYSIS] {analysis}")
        except Exception as e:
            logger.info(f"[QWEN-MONITOR] Monitor analysis incomplete: {e}")

    def _check_cached_stream(self) -> Optional[Dict[str, Optional[str]]]:
        """
        Check if last known stream is still live (Priority 0).
        Returns stream dict if found, None otherwise.
        """
        if not self.stream_resolver:
            return None

        logger.info("[QWEN-FIRST-PRINCIPLES] Is the last video still live?")
        try:
            pre_check_result = self.stream_resolver.resolve_stream(channel_id=None)
            if pre_check_result and pre_check_result[0]:
                logger.info(f"[QWEN-SUCCESS] Last known stream still live! Instant reconnection.")
                video_id = pre_check_result[0]
                live_chat_id = pre_check_result[1] if len(pre_check_result) > 1 else None

                return {
                    'video_id': video_id,
                    'live_chat_id': live_chat_id,
                    'channel_id': None,
                    'channel_name': 'Cached Stream'
                }
            else:
                logger.info("[QWEN-INFO] No cached stream or last stream ended - need full channel scan")
        except Exception as e:
            logger.warning(f"[QWEN-ERROR] First principles check failed: {e}")

        return None

    def _prioritize_channels_with_qwen(self, channels: List[str]) -> List[str]:
        """Use QWEN to prioritize channel order if available."""
        if not self.qwen_youtube:
            return channels

        # Check if QWEN recommends checking at all
        should_check, reason = self.qwen_youtube.should_check_now()
        logger.info(f"[QWEN-GLOBAL] Global check decision: {should_check} - {reason}")

        if not should_check:
            logger.warning(f"[QWEN-DECISION] Skipping channel checks: {reason}")
            return []

        # Build channel list with names
        channel_list = []
        for ch_id in channels:
            ch_name = self.stream_resolver._get_channel_display_name(ch_id) if self.stream_resolver else ch_id
            channel_list.append((ch_id, ch_name))

        # Get QWEN's prioritized order
        prioritized = self.qwen_youtube.prioritize_channels(channel_list)
        logger.info(f"[QWEN-PRIORITY] Analyzed and reordered {len(prioritized)} channels")

        if prioritized:
            top_channel_id, top_channel_name, top_score = prioritized[0]
            if top_score >= 1.05:
                self.high_priority_pending = True
                self.priority_reason = f"High-confidence window for {top_channel_name} (score {top_score:.2f})"
            else:
                self.high_priority_pending = False
                self.priority_reason = None

            # Log top 3 scores
            for ch_id, ch_name, score in prioritized[:3]:
                logger.info(f"[QWEN-SCORE] {ch_name}: Priority score {score:.2f}")

            return [ch_id for ch_id, _, _ in prioritized]

        self.high_priority_pending = False
        self.priority_reason = None
        return channels

    def _record_stream_telemetry(self, video_id: str, channel_name: str, channel_id: str) -> None:
        """Record stream start in telemetry store."""
        if not self.telemetry:
            return

        try:
            self.current_stream_id = self.telemetry.record_stream_start(
                video_id=video_id,
                channel_name=channel_name,
                channel_id=channel_id
            )
            logger.info(f"[HEART] Stream session started (SQLite ID: {self.current_stream_id})")
        except Exception as e:
            logger.warning(f"Failed to record stream start: {e}")

    def find_livestream(self) -> Optional[Dict[str, Optional[str]]]:
        """
        Find active livestream on configured channels.
        Uses QWEN intelligence for channel prioritization.

        Returns:
            Stream metadata dict containing video_id, live_chat_id, channel_id,
            and channel_name, or None if no stream found.
        """
        # WSP 91: Component Isolation
        if not _env_truthy("YT_STREAM_RESOLVER_ENABLED", "true"):
            logger.debug("[SEARCH] Stream resolver DISABLED via YT_STREAM_RESOLVER_ENABLED")
            return None

        logger.info("[SEARCH] Looking for livestream...")

        # QWEN Intelligence: Analyze context before searching
        logger.info("[QWEN-ANALYZE] QWEN analyzing stream detection strategy...")
        self._run_qwen_analysis()

        # Initialize StreamResolver if needed
        if not self.stream_resolver:
            try:
                self.stream_resolver = StreamResolver(self.service)
                logger.info("[REFRESH] StreamResolver initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize StreamResolver with service: {e}")
                logger.info("[REFRESH] Falling back to NO-QUOTA mode")
                self.stream_resolver = StreamResolver(None)

        # Reset priority tracking
        self.high_priority_pending = False
        self.priority_reason = None

        # Priority 0: Check if last stream is still live
        cached_result = self._check_cached_stream()
        if cached_result:
            logger.info(f"[ROCKET] Skipping channel rotation - already found active stream: {cached_result['video_id']}")
            return cached_result

        # Get channels to check
        channels_to_check = self._get_channels_to_check()

        # Show rotation header
        logger.info("=" * 60)
        logger.info("[REFRESH] CHANNEL ROTATION CHECK (NO-QUOTA MODE with QWEN Intelligence)")
        logger.info("[QWEN-INIT] Starting intelligent channel rotation analysis")

        # Prioritize with QWEN
        channels_to_check = self._prioritize_channels_with_qwen(channels_to_check)
        if not channels_to_check:
            return None

        logger.info(f"   Checking {len(channels_to_check)} channels in QWEN-optimized sequence:")
        for idx, ch_id in enumerate(channels_to_check, 1):
            ch_name = self.stream_resolver._get_channel_display_name(ch_id) if self.stream_resolver else ch_id
            logger.info(f"   {idx}. {ch_name}")
        logger.info("=" * 60)

        # Check each channel
        found_streams: List[Dict] = []
        first_stream_to_monitor: Optional[Dict] = None
        check_results: Dict[str, str] = {}

        for i, channel_id in enumerate(channels_to_check, 1):
            channel_name = self.stream_resolver._get_channel_display_name(channel_id)
            logger.info(f"\n[SEARCH Channel {i}/{len(channels_to_check)}] Checking {channel_name}...")
            logger.info(f"[QWEN-SCAN] Initiating channel scan #{i}")

            try:
                result = self.stream_resolver.resolve_stream(channel_id)
                if result and result[0]:
                    check_results[channel_name] = '[OK] LIVE'
                    channel_tag = "MOVE2JAPAN" if "Move2Japan" in channel_name else (
                        "UNDAODU" if "UnDaoDu" in channel_name else (
                            "FOUNDUPS" if "FoundUps" in channel_name else "CHANNEL"
                        )
                    )
                    logger.info(f"[{channel_tag} Channel {i}/{len(channels_to_check)}] {channel_name}: STREAM FOUND!")
                else:
                    check_results[channel_name] = "offline"
                    logger.info(f"[CHECK Channel {i}/{len(channels_to_check)}] {channel_name}: No active stream")
            except Exception as e:
                logger.error(f"[CHECK {i}/{len(channels_to_check)}] {channel_name}... ERROR: {e}")
                result = None
                continue

            if result and result[0]:
                video_id = result[0]
                live_chat_id = result[1] if len(result) > 1 else None

                if not live_chat_id:
                    logger.info(f"[WARN] Found stream on {channel_name} but chat_id not available")
                    # Attempt credential rotation
                    try:
                        retry_result = self.stream_resolver.resolve_stream(channel_id=channel_id)
                        if retry_result and len(retry_result) > 1 and retry_result[1]:
                            live_chat_id = retry_result[1]
                            logger.info(f"[OK] Got chat_id after credential rotation: {live_chat_id}")
                    except Exception as e:
                        logger.error(f"[FAIL] Error during credential rotation: {e}")
                else:
                    logger.info(f"[OK] Found stream on {channel_name} with video ID: {video_id}")

                # Record telemetry
                self._record_stream_telemetry(video_id, channel_name, channel_id)

                # QWEN learns from successful detection
                if self.qwen_youtube:
                    self.qwen_youtube.record_stream_found(channel_id, channel_name, video_id)
                    logger.info("[QWEN-LEARN] Recorded successful stream detection pattern")

                # Get stream title
                stream_title = None
                if self.stream_resolver:
                    stream_title = self.stream_resolver._get_stream_title(video_id)
                if not stream_title:
                    stream_title = f"{channel_name} is LIVE!"

                stream_info = {
                    'video_id': video_id,
                    'live_chat_id': live_chat_id,
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'title': stream_title
                }
                found_streams.append(stream_info)

                if not first_stream_to_monitor:
                    first_stream_to_monitor = stream_info

                logger.info(f"[TARGET] Found active stream on {channel_name} - stopping channel scan")
                break

        # Process results
        logger.info(f"[QWEN-EVALUATE] Analyzing search results...")
        if found_streams:
            # Deduplicate by video_id
            unique_streams = {}
            for stream in found_streams:
                video_id = stream['video_id']
                if video_id not in unique_streams:
                    unique_streams[video_id] = stream
                else:
                    logger.info(f"[DUPLICATE] Same stream {video_id} found on multiple channels")

            found_streams = list(unique_streams.values())
            if found_streams and not first_stream_to_monitor:
                first_stream_to_monitor = found_streams[0]

            logger.info(f"\n[OK] Found {len(found_streams)} unique stream(s):")
            for stream in found_streams:
                logger.info(f"  - {stream['channel_name']}: {stream['video_id']}")

            # Check for duplicate posting
            should_post = True
            for stream in found_streams:
                if stream['video_id'] == self._last_stream_id:
                    logger.info(f"[SEMANTIC-SWITCH] Already monitoring stream {stream['video_id']} - skipping duplicate post")
                    should_post = False
                    break

            if should_post:
                logger.info(f"[NOTE] NEW stream(s) detected - posting to social media")
                self._trigger_social_media_posting(found_streams)
            else:
                logger.info("[SEMANTIC-SWITCH] Skipped posting - stream already active")

            logger.info(f"[STREAM] Will monitor first stream: {found_streams[0]['channel_name']}")
            logger.info("[QWEN-SUCCESS] Stream detection successful - transitioning to monitor phase")
            return first_stream_to_monitor
        else:
            # Show rotation summary
            logger.info("\n" + "=" * 60)
            logger.info("[CLIPBOARD] ROTATION SUMMARY:")
            for channel, status in check_results.items():
                logger.info(f"   {channel}: {status}")
            logger.info(f"\n[FAIL] No active livestreams found (checked {len(channels_to_check)} channels)")

            # QWEN summary
            if self.qwen_youtube:
                logger.info("[QWEN-LEARN] Recording no-stream pattern for time optimization")
                summary = self.qwen_youtube.get_intelligence_summary()
                logger.info("[QWEN-SUMMARY] Current intelligence state:")
                for line in summary.split('\n')[:5]:
                    if line.strip():
                        logger.info(f"    {line}")

            logger.info("Will check again in 30 minutes...")
            logger.info("=" * 60)
            return None

    def _trigger_social_media_posting(self, found_streams: List[Dict]) -> None:
        """
        Trigger social media posting for detected streams.
        Delegates to SocialMediaOrchestrator.
        """
        logger.info("=" * 80)
        logger.info("[SOCIAL] SOCIAL MEDIA POSTING ORCHESTRATION")
        logger.info("=" * 80)

        try:
            from modules.platform_integration.social_media_orchestrator.src.refactored_posting_orchestrator import get_orchestrator
            orchestrator = get_orchestrator()
            logger.info("[OK] Social media orchestrator loaded")

            logger.info(f"[HANDOFF] Sending {len(found_streams)} stream(s) to Social Media Orchestrator")
            result = orchestrator.handle_multiple_streams_detected(found_streams)

            if result.get('success'):
                logger.info(f"[SUCCESS] Orchestrator processed {result.get('streams_processed')} streams")
            else:
                logger.warning(f"[WARNING] Orchestrator reported issues: {result.get('errors')}")

            logger.info("[COMPLETE] Social media posting handoff complete")

        except ImportError as e:
            logger.error(f"[FAIL] Failed to import social media orchestrator: {e}")
        except Exception as e:
            logger.error(f"[FAIL] Social media posting orchestration failed: {e}")
            import traceback
            logger.error(traceback.format_exc())


# Factory function for easy instantiation
def create_stream_discovery_service(
    service: Optional[Any] = None,
    telemetry: Optional[Any] = None,
    qwen_monitor: Optional[Any] = None,
    qwen_youtube: Optional[Any] = None,
    monitoring_context_class: Optional[type] = None,
) -> StreamDiscoveryService:
    """Create a StreamDiscoveryService with the given dependencies."""
    return StreamDiscoveryService(
        service=service,
        telemetry=telemetry,
        qwen_monitor=qwen_monitor,
        qwen_youtube=qwen_youtube,
        monitoring_context_class=monitoring_context_class,
    )
