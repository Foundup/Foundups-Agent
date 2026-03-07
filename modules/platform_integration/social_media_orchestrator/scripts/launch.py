#!/usr/bin/env python3
"""
Social Media DAE Launch Script
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Launch Social Media DAE (012 Digital Twin)
Domain: platform_integration
Module: social_media_orchestrator

WSP Compliance: WSP 27 (DAE Architecture), WSP 46 (WRE Protocol),
                WSP 77 (Agent Coordination)
"""

import asyncio
import logging
import time
import traceback

logger = logging.getLogger(__name__)

# WRE CoT preflight - recursive enforcement after watch period
try:
    from modules.infrastructure.wre_core.src.dae_preflight import preflight_guard
except ImportError:
    # Fallback if WRE not available
    def preflight_guard(name, quiet=True):
        def decorator(func):
            return func
        return decorator


class SocialMediaDAE:
    """
    Social Media DAE — fires WRE social skills on a cadence.

    This replaces the previous stub with a real event loop that
    discovers and executes social-domain skills (LinkedIn, X, etc.)
    through the full WRE pipeline.

    Per WSP 27: Signal → Knowledge → Protocol → Execution
    """

    def __init__(self, cadence_minutes: int = 15):
        self.cadence_minutes = cadence_minutes
        self.active = False

        # Compose SkillTriggerMixin functionality
        try:
            from modules.infrastructure.wre_core.src.skill_trigger import (
                SkillTriggerMixin,
            )
            # Dynamically mix in the trigger methods
            self._trigger_mixin = SkillTriggerMixin()
            self._trigger_mixin.init_skill_triggers(
                domain="social",
                cadence_minutes=cadence_minutes,
            )
            self._trigger_available = True
            logger.info("[SOCIAL-DAE] SkillTriggerMixin initialized (domain=social)")
        except Exception as exc:
            logger.warning("[SOCIAL-DAE] SkillTriggerMixin unavailable: %s", exc)
            self._trigger_available = False
            self._trigger_mixin = None

    async def run(self):
        """Main DAE event loop — fire social skills on cadence."""
        self.active = True
        logger.info(
            "[SOCIAL-DAE] Starting social media DAE (cadence=%dm)",
            self.cadence_minutes,
        )
        print(f"[SOCIAL-DAE] Running social skill triggers every {self.cadence_minutes}m")
        print("[SOCIAL-DAE] Press Ctrl+C to stop")

        cycle = 0
        while self.active:
            cycle += 1
            try:
                if self._trigger_available and self._trigger_mixin:
                    results = await self._trigger_mixin.fire_pending_skills(
                        extra_context={"cycle": cycle},
                    )
                    succeeded = sum(1 for r in results if r.get("success"))
                    total = len(results)
                    if total > 0:
                        print(
                            f"[SOCIAL-DAE] Cycle {cycle}: {succeeded}/{total} skills succeeded"
                        )
                    else:
                        logger.debug("[SOCIAL-DAE] Cycle %d: no skills due", cycle)
                else:
                    logger.debug("[SOCIAL-DAE] Cycle %d: trigger mixin unavailable", cycle)

            except Exception as exc:
                logger.error("[SOCIAL-DAE] Cycle %d error: %s", cycle, exc)

            # Sleep until next cadence
            await asyncio.sleep(self.cadence_minutes * 60)

    def stop(self):
        """Stop the DAE loop."""
        self.active = False
        logger.info("[SOCIAL-DAE] Stop requested")

    def get_status(self):
        """Return DAE status for observability."""
        status = {"active": self.active, "domain": "social"}
        if self._trigger_available and self._trigger_mixin:
            status["triggers"] = self._trigger_mixin.get_trigger_status()
        return status


@preflight_guard("social_media_dae")
def run_social_media_dae():
    """Run Social Media DAE (012 Digital Twin)."""
    print("[INFO] Starting Social Media DAE (012 Digital Twin)...")
    try:
        dae = SocialMediaDAE(cadence_minutes=15)
        asyncio.run(dae.run())
    except KeyboardInterrupt:
        print("\n[STOP] Social Media DAE stopped by user")
    except Exception as e:
        print(f"[ERROR] Social Media DAE failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    run_social_media_dae()

