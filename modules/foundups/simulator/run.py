#!/usr/bin/env python
"""FoundUps Simulator - Main entrypoint.

Usage:
    python run.py                    # Run with defaults
    python run.py --ticks 1000       # Run for 1000 ticks
    python run.py --founders 5       # Start with 5 founder agents
    python run.py --users 20         # Start with 20 user agents
    python run.py --speed 4.0        # Run at 4 ticks per second
    python run.py --verbose          # Enable verbose logging
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.mesa_model import FoundUpsModel
from modules.foundups.simulator.render.terminal_view import TerminalView

logger = logging.getLogger(__name__)


class SimulatorRunner:
    """Main simulator runner with game loop."""

    def __init__(
        self,
        config: SimulatorConfig,
        fam_daemon: Optional["Any"] = None,
    ) -> None:
        """Initialize simulator runner.

        Args:
            config: Simulation configuration
            fam_daemon: Optional FAMDaemon for event SSoT
        """
        self._config = config
        self._model = FoundUpsModel(config=config, fam_daemon=fam_daemon)
        self._view = TerminalView(
            grid_width=config.grid_width,
            grid_height=config.grid_height,
            event_log_lines=config.event_log_lines,
        )
        self._running = False
        self._paused = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum: int, frame) -> None:
        """Handle interrupt signals."""
        logger.info(f"[RUNNER] Received signal {signum}, stopping...")
        self._running = False

    def run(self) -> None:
        """Run the main simulation loop."""
        self._running = True
        self._model.start()

        tick_interval = 1.0 / self._config.tick_rate_hz
        last_tick_time = time.time()
        last_render_time = time.time()
        render_interval = 0.1  # Render at ~10 FPS for smooth display

        logger.info(
            f"[RUNNER] Starting simulation: "
            f"{self._config.num_founder_agents} founders, "
            f"{self._config.num_user_agents} users, "
            f"{self._config.tick_rate_hz} ticks/sec"
        )

        try:
            while self._running:
                current_time = time.time()

                # Check tick limit
                if self._config.max_ticks and self._model.tick >= self._config.max_ticks:
                    logger.info(f"[RUNNER] Reached max ticks: {self._config.max_ticks}")
                    break

                # Step simulation at configured rate
                if not self._paused and (current_time - last_tick_time) >= tick_interval:
                    self._model.step()
                    last_tick_time = current_time

                    if self._config.verbose:
                        status = self._view.render_simple(self._model.state_store.get_state())
                        logger.debug(f"[RUNNER] {status}")

                # Render at steady framerate
                if (current_time - last_render_time) >= render_interval:
                    state = self._model.state_store.get_state()
                    self._view.render(state)
                    last_render_time = current_time

                # Small sleep to prevent CPU spinning
                time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("[RUNNER] Interrupted by user")
        finally:
            self._running = False
            self._model.stop()

        # Final stats
        stats = self._model.get_stats()
        print("\n" + "=" * 50)
        print("SIMULATION COMPLETE")
        print("=" * 50)
        print(f"  Total Ticks:    {stats['tick']}")
        print(f"  Total FoundUps: {stats['total_foundups']}")
        print(f"  Total Likes:    {stats['total_likes']}")
        print(f"  Total Stakes:   {stats['total_stakes']}")
        print(f"  Tokens Moved:   {stats['total_tokens']}")
        print("=" * 50)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="FoundUps Simulator - Autonomous FoundUp ecosystem simulation"
    )

    parser.add_argument(
        "--ticks", "-t",
        type=int,
        default=None,
        help="Maximum ticks to run (default: unlimited)"
    )
    parser.add_argument(
        "--founders", "-f",
        type=int,
        default=3,
        help="Number of founder agents (default: 3)"
    )
    parser.add_argument(
        "--users", "-u",
        type=int,
        default=10,
        help="Number of user agents (default: 10)"
    )
    parser.add_argument(
        "--speed", "-s",
        type=float,
        default=2.0,
        help="Tick rate in Hz (default: 2.0)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    setup_logging(args.verbose)

    # Build config from args
    config = SimulatorConfig(
        num_founder_agents=args.founders,
        num_user_agents=args.users,
        tick_rate_hz=args.speed,
        max_ticks=args.ticks,
        seed=args.seed,
        verbose=args.verbose,
    )

    # Try to connect to FAMDaemon if available
    fam_daemon = None
    try:
        from modules.foundups.agent_market.src.fam_daemon import get_fam_daemon
        fam_daemon = get_fam_daemon()
        logger.info("[MAIN] Connected to FAMDaemon (SSoT enabled)")
    except ImportError:
        logger.warning("[MAIN] FAMDaemon not available, running without SSoT")
    except Exception as e:
        logger.warning(f"[MAIN] Could not connect to FAMDaemon: {e}")

    # Run simulation
    runner = SimulatorRunner(config=config, fam_daemon=fam_daemon)
    runner.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
