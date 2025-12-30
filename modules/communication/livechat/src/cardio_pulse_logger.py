"""
CARDIO PULSE - Cardiovascular Heartbeat Logger

Aggregates all system health metrics into a single concise heartbeat log line.
Replaces noisy repeated logs (BanterEngine init, quota warnings, etc.) with
one comprehensive status update.

First principles: The cardiovascular system's job is to provide ONE unified
health signal, not spam individual organ status reports.

WSP 91: Observability - Single source of truth for system health
WSP 48: Recursive Learning - Learn optimal logging patterns

Usage:
    from modules.communication.livechat.src.cardio_pulse_logger import get_cardio_pulse

    pulse = get_cardio_pulse()
    pulse.emit_heartbeat(
        quota_used=5000,
        poll_interval=10,
        messages_processed=145,
        errors=2
    )

Output Example:
    [CARDIO] ❤️ PULSE | Cred:1 Quota:50% Poll:10s Msg:145 Err:2 LLM:OK Stream:ACTIVE
"""

import logging
import time
from typing import Optional, Dict
from collections import deque

logger = logging.getLogger(__name__)

# Singleton instance
_pulse_instance: Optional['CardioPulse'] = None


class CardioPulse:
    """
    Cardiovascular heartbeat logger - ONE health signal for the entire system.

    Aggregates:
    - Quota usage & credential set
    - Poll interval & message throughput
    - Error rates
    - LLM service status
    - Stream activity
    """

    def __init__(self, heartbeat_interval: int = 60):
        """
        Initialize CARDIO PULSE logger.

        Args:
            heartbeat_interval: Seconds between heartbeat logs (default: 60)
        """
        self.heartbeat_interval = heartbeat_interval
        self.last_heartbeat = 0

        # Metrics tracking
        self.total_messages = 0
        self.total_errors = 0
        self.last_error_time = 0

        # Rate-limited noise suppression
        self._suppressed_logs = {}  # key -> count
        self._last_suppression_report = 0
        self._suppression_report_interval = 300  # Report every 5 minutes

        # System state
        self.credential_set = 1
        self.quota_percentage = 0.0
        self.poll_interval = 10
        self.stream_active = True
        self.llm_available = False

        logger.info("[CARDIO] ❤️ Cardiovascular heartbeat logger initialized")

    def emit_heartbeat(
        self,
        quota_used: Optional[int] = None,
        poll_interval: Optional[float] = None,
        messages_processed: Optional[int] = None,
        errors: Optional[int] = None,
        credential_set: Optional[int] = None,
        stream_active: Optional[bool] = None
    ):
        """
        Emit aggregated heartbeat if interval elapsed.

        Args:
            quota_used: YouTube API quota units used
            poll_interval: Current polling interval in seconds
            messages_processed: Total messages processed this session
            errors: Total errors this session
            credential_set: Active credential set number
            stream_active: Whether stream is currently active
        """
        now = time.time()

        # Update state
        if quota_used is not None:
            self.quota_percentage = (quota_used / 10000) * 100  # Assume 10k daily limit
        if poll_interval is not None:
            self.poll_interval = poll_interval
        if messages_processed is not None:
            self.total_messages = messages_processed
        if errors is not None:
            self.total_errors = errors
        if credential_set is not None:
            self.credential_set = credential_set
        if stream_active is not None:
            self.stream_active = stream_active

        # Only emit if interval elapsed
        if (now - self.last_heartbeat) < self.heartbeat_interval:
            return

        self.last_heartbeat = now

        # Build concise heartbeat line
        quota_str = f"{self.quota_percentage:.0f}%" if self.quota_percentage > 0 else "N/A"
        stream_str = "ACTIVE" if self.stream_active else "IDLE"
        llm_str = "OK" if self.llm_available else "OFF"

        # Calculate error rate
        error_rate = (self.total_errors / self.total_messages * 100) if self.total_messages > 0 else 0.0

        heartbeat_msg = (
            f"[CARDIO] ❤️ PULSE | "
            f"Cred:{self.credential_set} "
            f"Quota:{quota_str} "
            f"Poll:{self.poll_interval}s "
            f"Msg:{self.total_messages} "
            f"Err:{self.total_errors}({error_rate:.1f}%) "
            f"LLM:{llm_str} "
            f"Stream:{stream_str}"
        )

        logger.info(heartbeat_msg)

    def suppress_noise(self, log_key: str, message: str) -> bool:
        """
        Suppress repeated noisy logs. Returns True if should suppress.

        Args:
            log_key: Unique key for this log type (e.g., "banter_init", "quota_warning")
            message: The log message

        Returns:
            bool: True if log should be suppressed
        """
        now = time.time()

        # Track suppression counts
        if log_key not in self._suppressed_logs:
            self._suppressed_logs[log_key] = {"count": 0, "last_seen": now, "sample": message}
            return False  # First occurrence - allow

        self._suppressed_logs[log_key]["count"] += 1
        self._suppressed_logs[log_key]["last_seen"] = now

        # Report suppressions periodically
        if (now - self._last_suppression_report) > self._suppression_report_interval:
            self._report_suppressions()
            self._last_suppression_report = now

        return True  # Suppress subsequent occurrences

    def _report_suppressions(self):
        """Report aggregated suppressed logs."""
        if not self._suppressed_logs:
            return

        total_suppressed = sum(s["count"] for s in self._suppressed_logs.values())

        logger.info(f"[CARDIO] 🔇 Noise suppressed: {total_suppressed} logs across {len(self._suppressed_logs)} types")

        # Show top 3 most suppressed
        sorted_logs = sorted(
            self._suppressed_logs.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )

        for i, (key, data) in enumerate(sorted_logs[:3], 1):
            logger.debug(f"[CARDIO]   #{i} {key}: {data['count']} times - \"{data['sample'][:50]}...\"")

    def set_llm_status(self, available: bool):
        """Update LLM service availability status."""
        self.llm_available = available


def get_cardio_pulse() -> CardioPulse:
    """Get or create singleton CARDIO PULSE logger."""
    global _pulse_instance

    if _pulse_instance is None:
        _pulse_instance = CardioPulse()

    return _pulse_instance


def emit_pulse(**kwargs):
    """Convenience function to emit heartbeat."""
    pulse = get_cardio_pulse()
    pulse.emit_heartbeat(**kwargs)


def suppress_log(log_key: str, message: str) -> bool:
    """Convenience function to check if log should be suppressed."""
    pulse = get_cardio_pulse()
    return pulse.suppress_noise(log_key, message)
