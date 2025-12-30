"""
Breadcrumb Monitor - AI Overseer Pattern Detection

Module: ai_intelligence/ai_overseer
WSP Reference: WSP 77 (Agent Coordination), WSP 91 (DAEmon Observability)
Status: Production

This module monitors breadcrumb telemetry for patterns and anomalies.
Uses Gemma (fast classification) and Qwen (strategic analysis).

Architecture:
    Breadcrumb Telemetry (persistent storage)
              ↓
    Breadcrumb Monitor (this)
              ↓
    Gemma: Fast pattern classification (is_critical?)
              ↓
    Qwen: Strategic analysis (what's wrong + how to fix)
              ↓
    Livechat: Send alerts to community

Key Insight: Replace log spam with intelligent alerts
"""

import logging
import asyncio
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BreadcrumbMonitor:
    """
    AI Overseer component for breadcrumb pattern monitoring.

    Monitors breadcrumb telemetry for:
        - Repeated patterns (WSP violations, navigation loops, etc.)
        - Critical events (errors, failures, anomalies)
        - Performance degradation (slowdowns, timeouts)
        - Security issues (unauthorized access, etc.)

    Uses:
        - Gemma for binary classification (is_critical?)
        - Qwen for strategic analysis (what's wrong + recommendations)
        - Livechat for community alerts
    """

    def __init__(self, livechat_sender):
        """
        Initialize breadcrumb monitor.

        Args:
            livechat_sender: LiveChatCore instance for sending alerts
        """
        self.livechat = livechat_sender
        self.alerted_patterns = set()  # Deduplicate alerts (session-level)
        self.monitoring = False

        # Import telemetry
        try:
            from modules.communication.livechat.src.breadcrumb_telemetry import get_breadcrumb_telemetry
            self.telemetry = get_breadcrumb_telemetry()
            logger.info("[BREADCRUMB-MONITOR] Telemetry connected")
        except Exception as e:
            logger.error(f"[BREADCRUMB-MONITOR] Failed to connect telemetry: {e}")
            self.telemetry = None

        # Import Gemma for classification (optional)
        self.gemma_available = False
        try:
            # TODO: Import Gemma client when ready
            # from modules.ai_intelligence.gemma_validator import GemmaValidator
            # self.gemma = GemmaValidator()
            # self.gemma_available = True
            pass
        except Exception as e:
            logger.debug(f"[BREADCRUMB-MONITOR] Gemma not available: {e}")

        # Import Qwen for analysis (optional)
        self.qwen_available = False
        try:
            # TODO: Import Qwen client when ready
            # from modules.infrastructure.shared_utilities.llm_client.src.client import get_llm_client
            # self.qwen = get_llm_client('qwen')
            # self.qwen_available = True
            pass
        except Exception as e:
            logger.debug(f"[BREADCRUMB-MONITOR] Qwen not available: {e}")

    async def start_monitoring(self, interval_seconds: int = 30):
        """
        Start monitoring breadcrumb patterns.

        Args:
            interval_seconds: How often to check for patterns (default: 30s)
        """
        if not self.telemetry:
            logger.error("[BREADCRUMB-MONITOR] Cannot start - telemetry unavailable")
            return

        self.monitoring = True
        logger.info(f"[BREADCRUMB-MONITOR] Started monitoring (interval: {interval_seconds}s)")

        while self.monitoring:
            try:
                await self._check_patterns()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"[BREADCRUMB-MONITOR] Monitoring error: {e}")
                await asyncio.sleep(interval_seconds)

    def stop_monitoring(self):
        """Stop monitoring breadcrumb patterns."""
        self.monitoring = False
        logger.info("[BREADCRUMB-MONITOR] Stopped monitoring")

    async def _check_patterns(self):
        """Check for repeated patterns and send alerts if critical."""
        if not self.telemetry:
            return

        # Get repeated patterns from last 5 minutes (min 2 occurrences)
        patterns = self.telemetry.get_repeated_patterns(minutes=5, min_occurrences=2)

        for source_dae, event_type, message, count in patterns:
            pattern_key = f"{source_dae}:{event_type}"

            # Skip if already alerted this session
            if pattern_key in self.alerted_patterns:
                continue

            # Classify pattern criticality
            is_critical = await self._classify_pattern_criticality(
                source_dae, event_type, message, count
            )

            if is_critical:
                # Analyze and generate alert
                alert = await self._generate_alert(
                    source_dae, event_type, message, count
                )

                # Send alert to chat
                if self.livechat and alert:
                    try:
                        await self.livechat.send_chat_message(
                            message_text=f"⚠️ [AI OVERSEER] {alert} ✊✋🖐️",
                            response_type='general',
                            skip_delay=True
                        )
                        logger.info(f"[BREADCRUMB-MONITOR] Sent alert: {alert[:50]}...")
                    except Exception as e:
                        logger.error(f"[BREADCRUMB-MONITOR] Failed to send alert: {e}")

                # Mark as alerted
                self.alerted_patterns.add(pattern_key)

    async def _classify_pattern_criticality(
        self,
        source_dae: str,
        event_type: str,
        message: str,
        count: int
    ) -> bool:
        """
        Classify if pattern is critical using Gemma (fast binary classification).

        Args:
            source_dae: Source DAE name
            event_type: Event type
            message: Event message
            count: Number of occurrences

        Returns:
            True if critical, False otherwise
        """
        # Fallback heuristics if Gemma unavailable
        if not self.gemma_available:
            # Rule-based classification
            critical_events = {
                'wsp_violation',
                'navigation_failure',
                'navigation_loop',
                'api_error',
                'database_error',
                'security_violation'
            }

            if event_type in critical_events:
                return True

            # High repetition = critical
            if count >= 5:
                return True

            return False

        # TODO: Use Gemma for binary classification
        # prompt = f"Is this pattern critical? Event: {event_type}, Count: {count}, Message: {message}"
        # result = self.gemma.classify(prompt)
        # return result == 0  # 0 = critical, 1 = normal

        return False

    async def _generate_alert(
        self,
        source_dae: str,
        event_type: str,
        message: str,
        count: int
    ) -> Optional[str]:
        """
        Generate human-readable alert using Qwen (strategic analysis).

        Args:
            source_dae: Source DAE name
            event_type: Event type
            message: Event message
            count: Number of occurrences

        Returns:
            Alert message or None
        """
        # Fallback templates if Qwen unavailable
        if not self.qwen_available:
            templates = {
                'wsp_violation': f"Detected {count} WSP violations from {source_dae} - structural issues need fixing",
                'navigation_failure': f"{source_dae} navigation failed {count}x - check browser/network",
                'navigation_loop': f"{source_dae} stuck in navigation loop ({count}x) - logic error",
                'api_error': f"{source_dae} API errors ({count}x) - quota or auth issue",
                'database_error': f"{source_dae} database errors ({count}x) - check DB connection",
            }

            return templates.get(event_type, f"{source_dae}/{event_type} repeated {count}x - investigate")

        # TODO: Use Qwen for strategic analysis
        # prompt = f"""Analyze this breadcrumb pattern and generate a concise alert (30 words max):
        #
        # Source: {source_dae}
        # Event: {event_type}
        # Message: {message}
        # Count: {count} occurrences in 5 minutes
        #
        # Generate alert with:
        # 1. What's happening
        # 2. Recommended action
        # """
        # alert = self.qwen.get_response(prompt)
        # return alert

        return None

    def get_pattern_summary(self, minutes: int = 30) -> Dict:
        """
        Get summary of recent breadcrumb patterns.

        Args:
            minutes: Time window to analyze

        Returns:
            Dict with pattern statistics
        """
        if not self.telemetry:
            return {}

        patterns = self.telemetry.get_repeated_patterns(minutes=minutes, min_occurrences=2)

        summary = {
            'total_patterns': len(patterns),
            'by_source': {},
            'by_event_type': {},
            'critical_count': 0
        }

        for source_dae, event_type, message, count in patterns:
            # Count by source
            if source_dae not in summary['by_source']:
                summary['by_source'][source_dae] = 0
            summary['by_source'][source_dae] += count

            # Count by event type
            if event_type not in summary['by_event_type']:
                summary['by_event_type'][event_type] = 0
            summary['by_event_type'][event_type] += count

            # Count critical patterns
            if event_type in {'wsp_violation', 'navigation_failure', 'api_error', 'database_error'}:
                summary['critical_count'] += 1

        return summary


# Singleton instance for module-level access
_monitor_instance = None


def get_breadcrumb_monitor(livechat_sender) -> BreadcrumbMonitor:
    """Get or create singleton breadcrumb monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = BreadcrumbMonitor(livechat_sender)
    return _monitor_instance


# CLI test interface
if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Mock livechat sender
    class MockLivechat:
        async def send_chat_message(self, message_text, response_type='general', skip_delay=False):
            print(f"[MOCK-CHAT] {message_text}")
            return True

    # Create monitor
    mock_livechat = MockLivechat()
    monitor = BreadcrumbMonitor(mock_livechat)

    # Test pattern summary
    print("\n=== Test: Pattern Summary ===")
    summary = monitor.get_pattern_summary(minutes=30)
    print(f"Total patterns: {summary.get('total_patterns', 0)}")
    print(f"By source: {summary.get('by_source', {})}")
    print(f"By event type: {summary.get('by_event_type', {})}")
    print(f"Critical count: {summary.get('critical_count', 0)}")

    # Test alert generation
    print("\n=== Test: Alert Generation ===")
    async def test_alert():
        alert = await monitor._generate_alert(
            source_dae='comment_engagement',
            event_type='wsp_violation',
            message='Module holo_dae missing: README.md',
            count=50
        )
        print(f"Alert: {alert}")

    asyncio.run(test_alert())
