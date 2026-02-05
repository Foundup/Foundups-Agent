"""
DAE Vitals - Cardiovascular System for DAE Operations

Module: platform_integration/youtube_shorts_scheduler/src
WSP Reference: WSP 91 (DAEmon Observability), WSP 94 (Agent Coordination)
Status: Production

Provides real-time health monitoring for DAE operations with:
- Vitals tracking (ops/min, error rate, oops events)
- Auto-stop on critical thresholds
- Console dashboard for 0102 observation
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class DAEVitals:
    """
    Cardiovascular vitals for DAE health monitoring.
    
    Tracks operational health and triggers auto-stop on critical conditions.
    """
    
    # Counters
    ops_count: int = 0
    error_count: int = 0
    oops_count: int = 0
    fallback_count: int = 0
    channels_processed: int = 0
    channels_skipped: int = 0

    # Activity tracking
    current_activity: str = "idle"
    scheduling_cycles: int = 0
    indexing_cycles: int = 0
    videos_scheduled: int = 0
    videos_indexed: int = 0
    videos_tagged: int = 0

    # Timestamps
    session_start: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    
    # Thresholds (configurable)
    error_rate_critical: float = 0.15  # 15%
    oops_critical: int = 2
    stall_timeout_seconds: float = 300  # 5 min
    
    def heartbeat(self) -> None:
        """Update last heartbeat timestamp."""
        self.last_heartbeat = time.time()
    
    def record_op(self, success: bool = True) -> None:
        """Record an operation (success or error)."""
        self.ops_count += 1
        if not success:
            self.error_count += 1
        self.heartbeat()
    
    def record_oops(self) -> None:
        """Record an oops page detection."""
        self.oops_count += 1
        self.heartbeat()
    
    def record_fallback(self, success: bool = True) -> None:
        """Record a fallback attempt."""
        self.fallback_count += 1
        if success:
            self.record_op(success=True)
        else:
            self.record_op(success=False)
    
    def record_channel(self, processed: bool = True) -> None:
        """Record a channel processing result."""
        if processed:
            self.channels_processed += 1
        else:
            self.channels_skipped += 1
        self.heartbeat()

    def record_activity_start(self, activity: str) -> None:
        """Record start of a new activity phase."""
        self.current_activity = activity
        self.heartbeat()

    def record_scheduling_cycle(self, videos_scheduled: int = 0) -> None:
        """Record a scheduling cycle completion."""
        self.scheduling_cycles += 1
        self.videos_scheduled += videos_scheduled
        self.heartbeat()

    def record_indexing_cycle(self, videos_indexed: int = 0) -> None:
        """Record an indexing cycle completion."""
        self.indexing_cycles += 1
        self.videos_indexed += videos_indexed
        self.heartbeat()

    def record_tagging(self, count: int = 1) -> None:
        """Record videos tagged with Gemini-generated hashtags."""
        self.videos_tagged += count
        self.heartbeat()
    
    @property
    def session_minutes(self) -> float:
        """Session duration in minutes."""
        return (time.time() - self.session_start) / 60
    
    @property
    def ops_per_minute(self) -> float:
        """Operations per minute."""
        if self.session_minutes <= 0:
            return 0
        return self.ops_count / self.session_minutes
    
    @property
    def error_rate(self) -> float:
        """Error rate as percentage (0.0-1.0)."""
        if self.ops_count <= 0:
            return 0.0
        return self.error_count / self.ops_count
    
    @property
    def seconds_since_heartbeat(self) -> float:
        """Seconds since last heartbeat."""
        return time.time() - self.last_heartbeat
    
    def is_stalled(self) -> bool:
        """Check if DAE is stalled (no heartbeat for stall_timeout)."""
        return self.seconds_since_heartbeat > self.stall_timeout_seconds
    
    def is_critical(self) -> bool:
        """Check if any vital is in critical state."""
        return (
            self.error_rate > self.error_rate_critical or
            self.oops_count > self.oops_critical or
            self.is_stalled()
        )
    
    def get_status_emoji(self) -> str:
        """Get status emoji based on vitals."""
        if self.is_critical():
            return "🛑"  # Critical
        elif self.error_rate > 0.05 or self.oops_count > 0:
            return "⚠️"  # Warning
        return "✅"  # Healthy
    
    def to_dashboard(self) -> str:
        """Format vitals as console dashboard for 012 observation."""
        status = self.get_status_emoji()

        # Base metrics (always show)
        parts = [
            f"[VITALS] {status}",
            f"🎯 {self.current_activity.upper()}",
            f"❤️ {self.ops_per_minute:.1f} ops/min",
            f"🩸 {self.error_rate*100:.1f}% errors",
        ]

        # Only show warnings if non-zero
        if self.oops_count > 0:
            parts.append(f"⚠️ {self.oops_count} oops")
        if self.fallback_count > 0:
            parts.append(f"🔄 {self.fallback_count} fallbacks")

        # Activity-specific metrics (only if > 0)
        if self.videos_scheduled > 0:
            parts.append(f"📅 {self.videos_scheduled} scheduled")
        if self.videos_indexed > 0:
            parts.append(f"📚 {self.videos_indexed} indexed")
        if self.videos_tagged > 0:
            parts.append(f"🏷️ {self.videos_tagged} tagged")

        # Progress (always show)
        total_channels = self.channels_processed + self.channels_skipped
        if total_channels > 0:
            parts.append(f"📂 {self.channels_processed}/{total_channels} channels")

        parts.append(f"🧠 {self.session_minutes:.0f}min")

        return " | ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for telemetry/reporting."""
        return {
            "current_activity": self.current_activity,
            "ops_count": self.ops_count,
            "error_count": self.error_count,
            "error_rate": self.error_rate,
            "oops_count": self.oops_count,
            "fallback_count": self.fallback_count,
            "channels_processed": self.channels_processed,
            "channels_skipped": self.channels_skipped,
            "scheduling_cycles": self.scheduling_cycles,
            "indexing_cycles": self.indexing_cycles,
            "videos_scheduled": self.videos_scheduled,
            "videos_indexed": self.videos_indexed,
            "videos_tagged": self.videos_tagged,
            "session_minutes": self.session_minutes,
            "ops_per_minute": self.ops_per_minute,
            "is_critical": self.is_critical(),
            "is_stalled": self.is_stalled(),
        }
    
    def check_and_alert(self) -> Optional[str]:
        """
        Check vitals and return alert message if critical.
        
        Returns:
            Alert message if critical, None otherwise.
        """
        if self.is_critical():
            reasons = []
            if self.error_rate > self.error_rate_critical:
                reasons.append(f"error_rate={self.error_rate*100:.1f}%>{self.error_rate_critical*100:.0f}%")
            if self.oops_count > self.oops_critical:
                reasons.append(f"oops={self.oops_count}>{self.oops_critical}")
            if self.is_stalled():
                reasons.append(f"stalled={self.seconds_since_heartbeat:.0f}s>{self.stall_timeout_seconds:.0f}s")
            return f"[VITALS] 🛑 CRITICAL: {', '.join(reasons)}"
        return None
    
    def emit_to_telemetry(self, phase: str = "vitals_update") -> None:
        """
        Emit vitals to breadcrumb_telemetry for AI Overseer and 012 review.
        
        Stores vitals in SQLite so 012 can paste logs to 0102 later.
        """
        try:
            from modules.communication.livechat.src.breadcrumb_telemetry import get_breadcrumb_telemetry
            telemetry = get_breadcrumb_telemetry()
            
            event_type = "vitals_critical" if self.is_critical() else "vitals_update"
            telemetry.store_breadcrumb(
                source_dae="youtube_shorts_scheduler",
                phase=phase,
                event_type=event_type,
                message=self.to_dashboard(),
                metadata=self.to_dict()
            )
        except ImportError:
            pass  # Telemetry not available
        except Exception as e:
            logger.warning(f"[VITALS] Failed to emit telemetry: {e}")


# Singleton for module-level access
_vitals_instance: Optional[DAEVitals] = None


def get_dae_vitals() -> DAEVitals:
    """Get or create singleton DAEVitals instance."""
    global _vitals_instance
    if _vitals_instance is None:
        _vitals_instance = DAEVitals()
    return _vitals_instance


def reset_dae_vitals() -> DAEVitals:
    """Reset and return fresh DAEVitals instance."""
    global _vitals_instance
    _vitals_instance = DAEVitals()
    return _vitals_instance


# CLI test
if __name__ == "__main__":
    import time
    
    vitals = DAEVitals()
    
    # Simulate operations
    for i in range(10):
        vitals.record_op(success=i % 3 != 0)  # 30% failures
        time.sleep(0.1)
    
    vitals.record_oops()
    vitals.record_fallback(success=True)
    vitals.record_channel(processed=True)
    
    print(vitals.to_dashboard())
    print(f"Critical: {vitals.is_critical()}")
    alert = vitals.check_and_alert()
    if alert:
        print(alert)
