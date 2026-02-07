"""
Video Indexer Telemetry - JSONL heartbeat and breadcrumb integration

WSP Compliance:
    - WSP 91: DAEMON Observability (structured telemetry output)
    - WSP 80: DAE Coordination (breadcrumb patterns for AI Overseer)

Output Files:
    - logs/video_indexer_heartbeat.jsonl - Health pulses (every 30s)
    - Breadcrumb DB - Pattern detection via breadcrumb_telemetry

Telemetry Format (JSONL):
    {"timestamp": "...", "status": "healthy", "uptime_seconds": 450, ...}

Grep-able Logging:
    [INDEXER-HEARTBEAT] Pulse #10 - Status: healthy
    [INDEXER-EVENT] video_start: Started indexing abc123
    [INDEXER-ERROR] Layer failed: visual - CUDA OOM
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class HeartbeatPayload:
    """Heartbeat telemetry payload."""
    timestamp: str
    status: str  # healthy, warning, critical, stopped
    uptime_seconds: float
    videos_indexed: int
    frames_processed: int
    errors_detected: int
    memory_mb: float
    cpu_percent: float
    current_video: Optional[str]
    current_layer: Optional[str]
    run_id: str
    automation_gates: Dict[str, Any]

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self), ensure_ascii=False)


@dataclass
class IndexingEvent:
    """Event during indexing process."""
    timestamp: str
    event_type: str  # video_start, layer_start, layer_complete, error, video_complete
    video_id: str
    layer: Optional[str]
    message: str
    metadata: Dict[str, Any]
    duration_ms: Optional[float] = None


# =============================================================================
# Health Calculator
# =============================================================================

class HealthCalculator:
    """
    Calculate health status based on metrics.

    Thresholds (configurable via env):
        - Memory > 500MB = warning, > 1024MB = critical
        - CPU > 70% = warning, > 90% = critical
        - Errors > 0 = critical
        - Uptime < 60s = warning (startup)
    """

    def __init__(self):
        self.memory_warning_mb = int(os.getenv("INDEXER_MEMORY_WARNING_MB", "500"))
        self.memory_critical_mb = int(os.getenv("INDEXER_MEMORY_CRITICAL_MB", "1024"))
        self.cpu_warning_pct = int(os.getenv("INDEXER_CPU_WARNING_PCT", "70"))
        self.cpu_critical_pct = int(os.getenv("INDEXER_CPU_CRITICAL_PCT", "90"))

    def calculate(
        self,
        uptime_seconds: float,
        memory_mb: float,
        cpu_percent: float,
        errors: int,
        stop_active: bool = False,
    ) -> str:
        """
        Calculate health status.

        Returns: "healthy", "warning", "critical", or "stopped"
        """
        if stop_active:
            return "stopped"

        # Critical conditions
        if errors > 0:
            return "critical"
        if memory_mb > self.memory_critical_mb:
            return "critical"
        if cpu_percent > self.cpu_critical_pct:
            return "critical"

        # Warning conditions
        if memory_mb > self.memory_warning_mb:
            return "warning"
        if cpu_percent > self.cpu_warning_pct:
            return "warning"
        if uptime_seconds < 60:
            return "warning"  # Startup phase

        return "healthy"


# =============================================================================
# Telemetry Writer
# =============================================================================

class IndexerTelemetry:
    """
    Telemetry system for Video Indexer DAE.

    Features:
        - JSONL heartbeat file (tailable)
        - Breadcrumb integration (pattern detection)
        - Structured logging with bracket tags

    Usage:
        telemetry = IndexerTelemetry()
        await telemetry.start_heartbeat_loop()

        telemetry.record_event("video_start", video_id, "Started indexing")
    """

    def __init__(self, config=None):
        """
        Initialize telemetry system.

        Args:
            config: IndexerConfig instance (optional, will load if not provided)
        """
        self.start_time = datetime.now()
        self.run_id = os.getenv("VIDEO_INDEXER_RUN_ID", f"run_{int(time.time())}")

        # Load config
        if config is None:
            from .indexer_config import get_indexer_config
            config = get_indexer_config()
        self.config = config

        # Telemetry file
        self.telemetry_path = config.telemetry_path
        self.telemetry_path.parent.mkdir(parents=True, exist_ok=True)

        # Emission mode (full or signal)
        self.telemetry_mode = os.getenv("INDEXER_TELEMETRY_MODE", "full").strip().lower()
        self.signal_every = int(os.getenv("INDEXER_TELEMETRY_SIGNAL_EVERY", "60"))
        self._last_status: Optional[str] = None

        # Health calculator
        self.health_calc = HealthCalculator()

        # Metrics
        self.videos_indexed = 0
        self.frames_processed = 0
        self.errors_detected = 0
        self.pulse_count = 0

        # Current state
        self.current_video: Optional[str] = None
        self.current_layer: Optional[str] = None

        # Layer metrics (for graceful degradation tracking)
        self.layer_metrics: Dict[str, Dict[str, Any]] = {
            "audio": {"success": 0, "failure": 0, "skipped": 0},
            "visual": {"success": 0, "failure": 0, "skipped": 0},
            "multimodal": {"success": 0, "failure": 0, "skipped": 0},
            "clips": {"success": 0, "failure": 0, "skipped": 0},
        }

        # Breadcrumb integration (optional)
        self._breadcrumbs = None
        self._init_breadcrumbs()

        logger.info(f"[INDEXER-TELEMETRY] Initialized (run_id={self.run_id})")

    def _init_breadcrumbs(self):
        """Initialize breadcrumb telemetry if available."""
        try:
            from modules.communication.livechat.src.breadcrumb_telemetry import (
                get_breadcrumb_telemetry,
            )
            self._breadcrumbs = get_breadcrumb_telemetry()
            logger.debug("[INDEXER-TELEMETRY] Breadcrumb integration enabled")
        except ImportError:
            logger.debug("[INDEXER-TELEMETRY] Breadcrumb integration not available")

    def _get_system_metrics(self) -> tuple:
        """Get current memory and CPU usage."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()
            return round(memory_mb, 1), round(cpu_percent, 1)
        except Exception:
            return 0.0, 0.0

    def _get_uptime(self) -> float:
        """Get uptime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    # =========================================================================
    # Heartbeat
    # =========================================================================

    async def start_heartbeat_loop(self, interval: int = 30):
        """
        Start async heartbeat loop.

        Args:
            interval: Seconds between pulses (default 30)
        """
        logger.info(f"[INDEXER-HEARTBEAT] Starting heartbeat loop (interval={interval}s)")
        while True:
            await self.pulse()
            await asyncio.sleep(interval)

    async def pulse(self):
        """Generate single heartbeat pulse."""
        try:
            uptime = self._get_uptime()
            memory_mb, cpu_percent = self._get_system_metrics()

            # Calculate health
            status = self.health_calc.calculate(
                uptime_seconds=uptime,
                memory_mb=memory_mb,
                cpu_percent=cpu_percent,
                errors=self.errors_detected,
                stop_active=self.config.stop_active,
            )

            # Build payload
            payload = HeartbeatPayload(
                timestamp=datetime.now(timezone.utc).isoformat(),
                status=status,
                uptime_seconds=round(uptime, 1),
                videos_indexed=self.videos_indexed,
                frames_processed=self.frames_processed,
                errors_detected=self.errors_detected,
                memory_mb=memory_mb,
                cpu_percent=cpu_percent,
                current_video=self.current_video,
                current_layer=self.current_layer,
                run_id=self.run_id,
                automation_gates=self.config.gate_snapshot(),
            )

            self.pulse_count += 1
            emit_pulse = self._should_emit_pulse(status)
            if emit_pulse:
                # Write to JSONL
                self._write_jsonl(payload.to_json())
                self._last_status = status

            if self.telemetry_mode == "full":
                if self.pulse_count % 10 == 0 or status != "healthy":
                    logger.info(
                        f"[INDEXER-HEARTBEAT] Pulse #{self.pulse_count} - "
                        f"Status: {status} | Videos: {self.videos_indexed} | "
                        f"Errors: {self.errors_detected} | Memory: {memory_mb}MB"
                    )
            elif emit_pulse:
                logger.info(
                    f"[INDEXER-HEARTBEAT] Pulse #{self.pulse_count} - "
                    f"Status: {status} | Videos: {self.videos_indexed} | "
                    f"Errors: {self.errors_detected} | Memory: {memory_mb}MB"
                )

        except Exception as e:
            logger.error(f"[INDEXER-HEARTBEAT] Pulse failed: {e}")

    def _write_jsonl(self, json_line: str):
        """Write line to JSONL file."""
        try:
            with open(self.telemetry_path, "a", encoding="utf-8") as f:
                f.write(json_line)
                f.write("\n")
        except Exception as e:
            logger.error(f"[INDEXER-TELEMETRY] JSONL write failed: {e}")

    # =========================================================================
    # Event Recording
    # =========================================================================

    def record_event(
        self,
        event_type: str,
        video_id: str,
        message: str,
        layer: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
    ):
        """
        Record indexing event.

        Args:
            event_type: Type of event (video_start, layer_start, etc.)
            video_id: Video being processed
            message: Human-readable message
            layer: Processing layer (audio, visual, etc.)
            metadata: Additional data
            duration_ms: Operation duration in milliseconds
        """
        event = IndexingEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            video_id=video_id,
            layer=layer,
            message=message,
            metadata=metadata or {},
            duration_ms=duration_ms,
        )

        if not self._should_emit_event(event_type):
            return

        # Log with bracket tag
        if layer:
            logger.info(f"[INDEXER-{layer.upper()}] {event_type}: {message}")
        else:
            logger.info(f"[INDEXER-EVENT] {event_type}: {message}")

        # Write to JSONL
        self._write_jsonl(json.dumps(asdict(event), ensure_ascii=False))

        # Store breadcrumb for pattern detection
        if self._breadcrumbs:
            self._breadcrumbs.store_breadcrumb(
                source_dae="video_indexer",
                phase=layer or "main",
                event_type=event_type,
                message=message,
                metadata=metadata or {},
            )

    def record_error(
        self,
        error: Exception,
        video_id: str,
        layer: Optional[str] = None,
        context: Optional[str] = None,
    ):
        """
        Record error event.

        Args:
            error: Exception that occurred
            video_id: Video being processed
            layer: Processing layer where error occurred
            context: Additional context
        """
        self.errors_detected += 1

        error_msg = f"{type(error).__name__}: {str(error)}"
        if context:
            error_msg = f"{context} - {error_msg}"

        self.record_event(
            event_type="error",
            video_id=video_id,
            message=error_msg,
            layer=layer,
            metadata={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
            },
        )

        logger.error(f"[INDEXER-ERROR] {error_msg}")

    def _should_emit_event(self, event_type: str) -> bool:
        if self.telemetry_mode == "full":
            return True
        if event_type == "error":
            return True
        if event_type in {"video_complete", "video_failed"}:
            return True
        return False

    def _should_emit_pulse(self, status: str) -> bool:
        if self.telemetry_mode == "full":
            return True
        if status in {"warning", "critical", "stopped"}:
            return True
        if self._last_status and status != self._last_status:
            return True
        if self.signal_every > 0 and (self.pulse_count % self.signal_every == 0):
            return True
        return False

    # =========================================================================
    # Layer Tracking
    # =========================================================================

    def layer_started(self, layer: str, video_id: str):
        """Mark layer as started."""
        self.current_layer = layer
        self.record_event(
            event_type="layer_start",
            video_id=video_id,
            message=f"Starting {layer} analysis",
            layer=layer,
        )

    def layer_completed(self, layer: str, video_id: str, duration_ms: float):
        """Mark layer as completed successfully."""
        self.layer_metrics[layer]["success"] += 1
        self.current_layer = None
        self.record_event(
            event_type="layer_complete",
            video_id=video_id,
            message=f"Completed {layer} analysis",
            layer=layer,
            duration_ms=duration_ms,
        )

    def layer_failed(self, layer: str, video_id: str, error: Exception):
        """Mark layer as failed."""
        self.layer_metrics[layer]["failure"] += 1
        self.current_layer = None
        self.record_error(error, video_id, layer, f"Layer {layer} failed")

    def layer_skipped(self, layer: str, video_id: str, reason: str):
        """Mark layer as skipped (disabled or graceful degradation)."""
        self.layer_metrics[layer]["skipped"] += 1
        self.record_event(
            event_type="layer_skipped",
            video_id=video_id,
            message=f"Skipped {layer}: {reason}",
            layer=layer,
            metadata={"reason": reason},
        )

    # =========================================================================
    # Video Tracking
    # =========================================================================

    def video_started(self, video_id: str, channel: str):
        """Mark video indexing as started."""
        self.current_video = video_id
        self.record_event(
            event_type="video_start",
            video_id=video_id,
            message=f"Started indexing video from {channel}",
            metadata={"channel": channel},
        )

    def video_completed(self, video_id: str, duration_ms: float):
        """Mark video indexing as completed."""
        self.videos_indexed += 1
        self.current_video = None
        self.record_event(
            event_type="video_complete",
            video_id=video_id,
            message=f"Completed indexing (took {duration_ms/1000:.1f}s)",
            duration_ms=duration_ms,
        )

    def video_failed(self, video_id: str, error: Exception):
        """Mark video indexing as failed."""
        self.current_video = None
        self.record_error(error, video_id, context="Video indexing failed")

    # =========================================================================
    # Metrics
    # =========================================================================

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        uptime = self._get_uptime()
        memory_mb, cpu_percent = self._get_system_metrics()

        return {
            "uptime_seconds": round(uptime, 1),
            "videos_indexed": self.videos_indexed,
            "frames_processed": self.frames_processed,
            "errors_detected": self.errors_detected,
            "pulse_count": self.pulse_count,
            "memory_mb": memory_mb,
            "cpu_percent": cpu_percent,
            "layer_metrics": self.layer_metrics,
            "health_status": self.health_calc.calculate(
                uptime, memory_mb, cpu_percent, self.errors_detected, self.config.stop_active
            ),
        }

    def get_layer_health(self) -> Dict[str, str]:
        """
        Get health status of each layer based on success/failure ratio.

        Returns dict like:
            {"audio": "healthy", "visual": "warning", ...}
        """
        health = {}
        for layer, metrics in self.layer_metrics.items():
            total = metrics["success"] + metrics["failure"]
            if total == 0:
                health[layer] = "unknown"
            elif metrics["failure"] == 0:
                health[layer] = "healthy"
            elif metrics["failure"] / total > 0.5:
                health[layer] = "critical"
            else:
                health[layer] = "warning"
        return health


# =============================================================================
# Singleton Instance
# =============================================================================

_telemetry_instance: Optional[IndexerTelemetry] = None


def get_indexer_telemetry() -> IndexerTelemetry:
    """Get singleton telemetry instance."""
    global _telemetry_instance
    if _telemetry_instance is None:
        _telemetry_instance = IndexerTelemetry()
    return _telemetry_instance


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Video Indexer Telemetry Test")
    print("=" * 60)

    telemetry = get_indexer_telemetry()

    # Simulate video indexing
    telemetry.video_started("test_video_123", "move2japan")
    telemetry.layer_started("audio", "test_video_123")
    time.sleep(0.1)
    telemetry.layer_completed("audio", "test_video_123", 100.5)
    telemetry.layer_skipped("visual", "test_video_123", "Disabled in config")
    telemetry.video_completed("test_video_123", 150.0)

    # Simulate error
    try:
        raise ValueError("Test error")
    except Exception as e:
        telemetry.record_error(e, "test_video_456", "multimodal", "Testing error handling")

    # Generate pulse
    asyncio.run(telemetry.pulse())

    # Show metrics
    print("\nMetrics:")
    import json
    print(json.dumps(telemetry.get_metrics(), indent=2))

    print(f"\nTelemetry written to: {telemetry.telemetry_path}")
