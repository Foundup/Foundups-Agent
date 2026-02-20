"""Terminal-based ASCII renderer for FoundUps simulator.

Renders the simulation state as ASCII art in the terminal.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..state_store import SimulatorState, FoundUpTile, AgentState


# ANSI escape codes for colors
class Colors:
    """ANSI color codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Bright variants
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


class TerminalView:
    """ASCII terminal renderer for the simulator.

    Layout:
    +------------------------------------------+
    | FOUNDUPS SIMULATOR  Tick: XXX  FPS: X.X  |
    +------------------------------------------+
    |  FOUNDUP GRID (10x6)                     |
    |  [F0] [F1] [F2] [ ] [ ] [ ] [ ] [ ] [ ]  |
    |  ...                                     |
    +------------------------------------------+
    | AGENTS | METRICS | EVENT LOG             |
    +------------------------------------------+
    """

    # Grid cell characters
    EMPTY_CELL = "[ ]"
    CELL_WIDTH = 7  # Width of each cell including padding

    def __init__(
        self,
        grid_width: int = 10,
        grid_height: int = 6,
        event_log_lines: int = 10,
        use_colors: bool = True,
    ) -> None:
        """Initialize terminal view.

        Args:
            grid_width: Width of the FoundUp grid
            grid_height: Height of the FoundUp grid
            event_log_lines: Number of event log lines to show
            use_colors: Whether to use ANSI colors
        """
        self._grid_width = grid_width
        self._grid_height = grid_height
        self._event_log_lines = event_log_lines
        self._use_colors = use_colors and self._supports_colors()

        # Calculate terminal dimensions
        self._term_width = max(80, grid_width * self.CELL_WIDTH + 4)

    def _supports_colors(self) -> bool:
        """Check if terminal supports ANSI colors."""
        # Windows terminal detection
        if sys.platform == "win32":
            return os.environ.get("TERM") or os.environ.get("WT_SESSION")
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colors enabled."""
        if self._use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text

    def _clear_screen(self) -> None:
        """Clear terminal screen."""
        if sys.platform == "win32":
            os.system("cls")
        else:
            print("\033[2J\033[H", end="")

    def _render_header(self, state: "SimulatorState") -> List[str]:
        """Render header section."""
        lines = []

        # Title bar
        title = "FOUNDUPS SIMULATOR"
        tick_info = f"Tick: {state.tick:05d}"
        fps = 1.0 / max(0.001, state.elapsed_seconds / max(1, state.tick)) if state.tick > 0 else 0.0
        fps_info = f"FPS: {fps:.1f}"
        daemon_status = self._color("[DAEMON OK]", Colors.GREEN) if state.daemon_running else self._color("[NO DAEMON]", Colors.RED)

        header = f"  {self._color(title, Colors.BOLD + Colors.CYAN)}  {tick_info}  {fps_info}  {daemon_status}"

        separator = "=" * self._term_width
        lines.append(self._color(separator, Colors.DIM))
        lines.append(header)
        lines.append(self._color(separator, Colors.DIM))

        return lines

    def _render_grid(self, state: "SimulatorState") -> List[str]:
        """Render FoundUp grid."""
        lines = []
        lines.append(self._color("  FOUNDUP GRID", Colors.BOLD))
        lines.append("")

        for y in range(self._grid_height):
            row = "  "
            for x in range(self._grid_width):
                foundup_id = state.foundup_grid[y][x] if y < len(state.foundup_grid) else None

                if foundup_id and foundup_id in state.foundups:
                    tile = state.foundups[foundup_id]
                    cell = self._render_tile(tile)
                else:
                    cell = self._color(self.EMPTY_CELL, Colors.DIM)

                row += cell + " "

            lines.append(row)

        lines.append("")
        return lines

    def _render_tile(self, tile: "FoundUpTile") -> str:
        """Render a single FoundUp tile."""
        # Use token symbol, truncated to 3 chars
        symbol = tile.token_symbol[:3] if tile.token_symbol else "???"

        # Color based on glow intensity (activity)
        if tile.glow_intensity > 0.7:
            color = Colors.BRIGHT_YELLOW + Colors.BOLD
        elif tile.glow_intensity > 0.3:
            color = Colors.BRIGHT_GREEN
        elif tile.likes > 0 or tile.stakes > 0:
            color = Colors.GREEN
        else:
            color = Colors.CYAN

        return self._color(f"[{symbol}]", color)

    def _render_agents_panel(self, state: "SimulatorState") -> List[str]:
        """Render agents status panel."""
        lines = []
        lines.append(self._color("  AGENTS", Colors.BOLD))

        # Count by type and status
        founders = [a for a in state.agents.values() if a.agent_type == "founder"]
        users = [a for a in state.agents.values() if a.agent_type == "user"]

        active_founders = sum(1 for a in founders if a.status == "active")
        active_users = sum(1 for a in users if a.status == "active")
        broke_count = sum(1 for a in state.agents.values() if a.status == "broke")

        lines.append(f"  Founders: {self._color(str(active_founders), Colors.MAGENTA)}/{len(founders)}")
        lines.append(f"  Users:    {self._color(str(active_users), Colors.BLUE)}/{len(users)}")
        lines.append(f"  Broke:    {self._color(str(broke_count), Colors.RED)}")

        # Show top agents by activity
        lines.append("")
        lines.append(self._color("  TOP AGENTS", Colors.DIM))

        sorted_agents = sorted(
            state.agents.values(),
            key=lambda a: a.likes_given + a.stakes_made + a.foundups_created,
            reverse=True
        )[:5]

        for agent in sorted_agents:
            type_color = Colors.MAGENTA if agent.agent_type == "founder" else Colors.BLUE
            activity = agent.likes_given + agent.stakes_made + agent.foundups_created
            lines.append(
                f"  {self._color(agent.agent_id[:10], type_color)}: "
                f"{activity} acts, {agent.tokens} tok"
            )

        return lines

    def _render_metrics_panel(self, state: "SimulatorState") -> List[str]:
        """Render global metrics panel."""
        lines = []
        lines.append(self._color("  METRICS", Colors.BOLD))

        lines.append(f"  FoundUps:   {self._color(str(state.total_foundups), Colors.CYAN)}")
        lines.append(f"  Likes:      {self._color(str(state.total_likes), Colors.GREEN)}")
        lines.append(f"  Stakes:     {self._color(str(state.total_stakes), Colors.YELLOW)}")
        lines.append(f"  Tokens:     {self._color(str(state.total_tokens_circulating), Colors.BRIGHT_YELLOW)}")
        lines.append("")
        lines.append(self._color("  DAEMON", Colors.DIM))
        lines.append(f"  Heartbeats: {state.daemon_heartbeat_count}")
        lines.append(f"  Last HB:    tick {state.last_heartbeat_tick}")

        return lines

    def _render_event_log(self, state: "SimulatorState") -> List[str]:
        """Render event log panel."""
        lines = []
        lines.append(self._color("  EVENT LOG", Colors.BOLD))

        # Show recent events
        events = state.recent_events[-self._event_log_lines:]

        for event in events:
            # Truncate display text
            text = event.display_text[:45] if len(event.display_text) > 45 else event.display_text

            # Color by event type
            if event.event_type == "foundup_created":
                color = Colors.BRIGHT_CYAN
            elif event.event_type == "heartbeat":
                color = Colors.DIM
            elif "payout" in event.event_type:
                color = Colors.BRIGHT_YELLOW
            elif "task" in event.event_type:
                color = Colors.GREEN
            else:
                color = Colors.WHITE

            lines.append(f"  {self._color(text, color)}")

        # Pad to fixed height
        while len(lines) < self._event_log_lines + 1:
            lines.append("")

        return lines

    def _render_footer(self) -> List[str]:
        """Render footer with controls."""
        lines = []
        separator = "-" * self._term_width
        lines.append(self._color(separator, Colors.DIM))
        controls = "  [Q] Quit  [P] Pause  [+/-] Speed  [V] Verbose"
        lines.append(self._color(controls, Colors.DIM))
        return lines

    def render(self, state: "SimulatorState", clear: bool = True) -> None:
        """Render the full simulator view.

        Args:
            state: Current simulator state
            clear: Whether to clear screen first
        """
        if clear:
            self._clear_screen()

        # Build all sections
        output_lines = []

        # Header
        output_lines.extend(self._render_header(state))

        # Grid
        output_lines.extend(self._render_grid(state))

        # Three-column layout: Agents | Metrics | Event Log
        agents_lines = self._render_agents_panel(state)
        metrics_lines = self._render_metrics_panel(state)
        event_lines = self._render_event_log(state)

        # Combine columns (simple vertical for now)
        col_separator = self._color("-" * self._term_width, Colors.DIM)
        output_lines.append(col_separator)

        # Side by side rendering
        max_rows = max(len(agents_lines), len(metrics_lines), len(event_lines))
        col_width = self._term_width // 3

        for i in range(max_rows):
            agent_text = agents_lines[i] if i < len(agents_lines) else ""
            metric_text = metrics_lines[i] if i < len(metrics_lines) else ""
            event_text = event_lines[i] if i < len(event_lines) else ""

            # Pad columns (approximate - ANSI codes make exact width tricky)
            row = f"{agent_text:<30}{metric_text:<25}{event_text}"
            output_lines.append(row)

        # Footer
        output_lines.extend(self._render_footer())

        # Print all at once for smooth rendering
        print("\n".join(output_lines))

    def render_simple(self, state: "SimulatorState") -> str:
        """Render a simple one-line status (for logging)."""
        return (
            f"Tick {state.tick:05d} | "
            f"FoundUps: {state.total_foundups} | "
            f"Likes: {state.total_likes} | "
            f"Stakes: {state.total_stakes}"
        )
