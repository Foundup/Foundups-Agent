"""
Stream Health Monitor for antifaFM YouTube Live Broadcaster

Auto-recovery system with exponential backoff for FFmpeg streaming.

WSP Compliance:
- WSP 27: Universal DAE Architecture (Phase 2: Agentic autonomy)
- WSP 91: DAEMON Observability (health metrics)
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Awaitable

logger = logging.getLogger(__name__)


class HealthState(Enum):
    """Health monitor states."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"  # Minor issues, still running
    UNHEALTHY = "unhealthy"  # Major issues, attempting recovery
    RECOVERING = "recovering"  # In recovery process
    FAILED = "failed"  # Recovery failed, needs manual intervention


@dataclass
class HealthMetrics:
    """Streaming health metrics."""
    state: HealthState = HealthState.HEALTHY
    uptime_seconds: float = 0.0
    restart_count: int = 0
    last_restart_time: Optional[float] = None
    consecutive_failures: int = 0
    last_check_time: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class RecoveryConfig:
    """Configuration for recovery behavior."""
    initial_delay: float = 5.0  # Initial retry delay in seconds
    max_delay: float = 300.0  # Max retry delay (5 minutes)
    backoff_multiplier: float = 2.0  # Exponential backoff multiplier
    max_consecutive_failures: int = 5  # Before entering FAILED state
    health_check_interval: float = 30.0  # How often to check health


class StreamHealthMonitor:
    """
    Monitors FFmpeg stream health and performs auto-recovery.

    Uses exponential backoff for restart attempts to avoid rapid
    restart loops during persistent failures.
    """

    def __init__(
        self,
        check_fn: Callable[[], bool],
        restart_fn: Callable[[], Awaitable[bool]],
        config: Optional[RecoveryConfig] = None,
    ):
        """
        Initialize health monitor.

        Args:
            check_fn: Sync function that returns True if stream is healthy
            restart_fn: Async function to restart stream, returns True on success
            config: Recovery configuration
        """
        self.check_fn = check_fn
        self.restart_fn = restart_fn
        self.config = config or RecoveryConfig()
        self.metrics = HealthMetrics()
        self._running = False
        self._current_delay = self.config.initial_delay
        self._monitor_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start health monitoring loop."""
        if self._running:
            logger.warning("Health monitor already running")
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("[HEALTH] Stream health monitor started")

    async def stop(self) -> None:
        """Stop health monitoring loop."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None
        logger.info("[HEALTH] Stream health monitor stopped")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await self._check_health()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(self.config.health_check_interval)

    async def _check_health(self) -> None:
        """Check stream health and trigger recovery if needed."""
        if self.metrics.state == HealthState.FAILED:
            return

        self.metrics.last_check_time = time.time()

        try:
            is_healthy = self.check_fn()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            is_healthy = False

        if is_healthy:
            self._on_healthy()
        else:
            await self._on_unhealthy()

    def _on_healthy(self) -> None:
        """Handle healthy state - reset failure counters."""
        if self.metrics.state != HealthState.HEALTHY:
            logger.info("[HEALTH] Stream recovered - now healthy")

        self.metrics.state = HealthState.HEALTHY
        self.metrics.consecutive_failures = 0
        self.metrics.error_message = None
        self._current_delay = self.config.initial_delay  # Reset backoff

    async def _on_unhealthy(self) -> None:
        """Handle unhealthy state - attempt recovery."""
        if self.metrics.state == HealthState.FAILED:
            return

        self.metrics.consecutive_failures += 1

        if self.metrics.consecutive_failures >= self.config.max_consecutive_failures:
            self.metrics.state = HealthState.FAILED
            self.metrics.error_message = (
                f"Max failures reached ({self.config.max_consecutive_failures}). "
                "Manual intervention required."
            )
            logger.error(f"[HEALTH] {self.metrics.error_message}")
            self._running = False
            return

        self.metrics.state = HealthState.RECOVERING
        logger.warning(
            f"[HEALTH] Stream unhealthy (failure {self.metrics.consecutive_failures}/"
            f"{self.config.max_consecutive_failures}). Attempting recovery in {self._current_delay:.1f}s..."
        )

        # Wait with backoff
        await asyncio.sleep(self._current_delay)

        # Attempt restart
        try:
            success = await self.restart_fn()
            if success:
                self.metrics.restart_count += 1
                self.metrics.last_restart_time = time.time()
                logger.info(f"[HEALTH] Stream restarted successfully (total restarts: {self.metrics.restart_count})")
                # Don't reset to healthy yet - next check will confirm
                self.metrics.state = HealthState.HEALTHY
            else:
                self.metrics.state = HealthState.UNHEALTHY
                self.metrics.error_message = "Restart returned False"
                logger.warning("[HEALTH] Restart attempt failed")
        except Exception as e:
            self.metrics.state = HealthState.UNHEALTHY
            self.metrics.error_message = str(e)
            logger.error(f"[HEALTH] Restart error: {e}")

        # Increase backoff for next attempt
        self._current_delay = min(
            self._current_delay * self.config.backoff_multiplier,
            self.config.max_delay
        )

    def reset(self) -> None:
        """Reset health monitor state (e.g., after manual intervention)."""
        self.metrics = HealthMetrics()
        self._current_delay = self.config.initial_delay
        logger.info("[HEALTH] Health monitor reset")

    def get_metrics(self) -> dict:
        """Get current health metrics as dict."""
        return {
            "state": self.metrics.state.value,
            "uptime_seconds": self.metrics.uptime_seconds,
            "restart_count": self.metrics.restart_count,
            "last_restart_time": self.metrics.last_restart_time,
            "consecutive_failures": self.metrics.consecutive_failures,
            "last_check_time": self.metrics.last_check_time,
            "error_message": self.metrics.error_message,
            "next_retry_delay": self._current_delay,
        }

    @property
    def is_healthy(self) -> bool:
        """Quick check if stream is in healthy state."""
        return self.metrics.state == HealthState.HEALTHY

    @property
    def needs_intervention(self) -> bool:
        """Check if manual intervention is needed."""
        return self.metrics.state == HealthState.FAILED


# Testing
if __name__ == "__main__":
    import random

    logging.basicConfig(level=logging.DEBUG)

    # Simulate a flaky stream
    stream_healthy = True
    restart_count = 0

    def check_stream() -> bool:
        global stream_healthy
        # Simulate random failures
        if random.random() < 0.3:
            stream_healthy = False
        return stream_healthy

    async def restart_stream() -> bool:
        global stream_healthy, restart_count
        restart_count += 1
        print(f"[TEST] Restart attempt #{restart_count}")
        # Simulate 70% success rate
        if random.random() < 0.7:
            stream_healthy = True
            return True
        return False

    async def main():
        monitor = StreamHealthMonitor(
            check_fn=check_stream,
            restart_fn=restart_stream,
            config=RecoveryConfig(
                initial_delay=1.0,
                max_delay=10.0,
                health_check_interval=2.0,
                max_consecutive_failures=3,
            )
        )

        await monitor.start()

        # Run for 30 seconds
        for i in range(15):
            print(f"\n[TEST] Iteration {i+1}/15 - Metrics: {monitor.get_metrics()}")
            await asyncio.sleep(2)

        await monitor.stop()
        print(f"\n[TEST] Final metrics: {monitor.get_metrics()}")

    asyncio.run(main())
