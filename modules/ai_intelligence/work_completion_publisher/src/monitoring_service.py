"""
Monitoring Service - Continuously monitors 0102 work and auto-publishes

Runs in background, periodically checking for significant work completion.
When detected, automatically triggers git push and social posting.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from .work_analyzer import WorkAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringService:
    """
    Background service that monitors 0102 work and publishes automatically.

    This is the core autonomous publishing loop.
    """

    def __init__(
        self,
        check_interval_seconds: int = 300,  # Check every 5 minutes
        auto_publish: bool = True
    ):
        self.check_interval = check_interval_seconds
        self.auto_publish = auto_publish
        self.analyzer = WorkAnalyzer()
        self.is_running = False
        self.checks_performed = 0
        self.publications_made = 0

        logger.info(f"MonitoringService initialized (interval: {check_interval_seconds}s, auto_publish: {auto_publish})")

    async def start(self):
        """Start continuous monitoring"""
        self.is_running = True
        logger.info("[rocket] Monitoring service started - watching for significant work")

        try:
            while self.is_running:
                await self._perform_check()
                await asyncio.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        finally:
            self.is_running = False

    def stop(self):
        """Stop monitoring"""
        self.is_running = False
        logger.info("Monitoring service stopped")

    async def _perform_check(self):
        """Perform a single work completion check"""
        self.checks_performed += 1
        logger.info(f"[magnifying glass] Check #{self.checks_performed} - evaluating work session...")

        try:
            # Evaluate current session
            should_publish, content = await self.analyzer.evaluate_current_session()

            if should_publish:
                logger.info(f"[star] Significant work detected (score: {content.significance_score:.2f})")
                logger.info(f"[text right arrow] Commit: {content.commit_message}")

                if self.auto_publish:
                    # Auto-publish
                    success = await self.analyzer.publish(content)

                    if success:
                        self.publications_made += 1
                        logger.info(f"[check mark] Publication #{self.publications_made} successful")
                        logger.info("[party popper] Work published to git and social media!")
                    else:
                        logger.error("[cross mark] Publication failed")
                else:
                    logger.info("[info] Auto-publish disabled - skipping publication")
            else:
                logger.info("[hourglass] Work in progress - not yet significant enough")

        except Exception as e:
            logger.error(f"Check error: {e}")

    def get_stats(self) -> dict:
        """Get monitoring statistics"""
        return {
            'is_running': self.is_running,
            'checks_performed': self.checks_performed,
            'publications_made': self.publications_made,
            'last_check_time': datetime.now().isoformat()
        }


def start_monitoring(
    check_interval: int = 300,
    auto_publish: bool = True
) -> MonitoringService:
    """
    Start work completion monitoring service.

    This is the main entry point for autonomous publishing.

    Args:
        check_interval: Seconds between checks (default 5 minutes)
        auto_publish: Whether to auto-publish or just notify

    Returns:
        MonitoringService instance
    """
    service = MonitoringService(
        check_interval_seconds=check_interval,
        auto_publish=auto_publish
    )

    # Start in background task
    asyncio.create_task(service.start())

    return service


async def demo_monitoring_service():
    """Demonstrate monitoring service"""
    print("=== Work Completion Monitoring Demo ===\n")
    print("Starting monitoring service...")
    print("(Will check every 30 seconds for demo purposes)\n")

    service = MonitoringService(
        check_interval_seconds=30,  # Faster for demo
        auto_publish=False  # Dry run for demo
    )

    # Run for limited time in demo
    try:
        await asyncio.wait_for(service.start(), timeout=120)
    except asyncio.TimeoutError:
        print("\nDemo complete!")
        service.stop()

    # Show stats
    stats = service.get_stats()
    print(f"\n=== Statistics ===")
    print(f"Checks performed: {stats['checks_performed']}")
    print(f"Publications made: {stats['publications_made']}")

    return service


if __name__ == "__main__":
    asyncio.run(demo_monitoring_service())
