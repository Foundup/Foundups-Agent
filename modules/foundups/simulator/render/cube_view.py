"""ASCII 3D Cube Animation for FoundUps Simulator.

Renders the FoundUP lifecycle story as an ASCII cube that builds up
as agents work on it. Integrates with StateStore for live data.

Story Arc: IDEA -> SCAFFOLD -> BUILD -> PROMOTE -> INVEST -> LAUNCH -> CELEBRATE -> RESET

WSP References:
- WSP 15: Build Order (priority levels)
- WSP 27: Color System (P0-P4 colors)
- WSP 54: Agent Roles
"""

from __future__ import annotations

import os
import sys
import time
import random
from typing import TYPE_CHECKING, List, Optional, Dict
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from ..state_store import SimulatorState, FoundUpTile, AgentState


# ANSI color codes
class Colors:
    """ANSI color codes matching terminal_view.py."""
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

    # Bright variants
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"


# WSP 15/27: Priority level colors
LEVEL_COLORS = {
    "P0": Colors.BRIGHT_RED,      # Elite - critical
    "P1": Colors.YELLOW,          # Senior - high impact
    "P2": Colors.BRIGHT_YELLOW,   # Mid - valuable
    "P3": Colors.BRIGHT_GREEN,    # Junior - low priority
    "P4": Colors.BRIGHT_BLUE,     # Novice - backlog
}

# Agent role icons (WSP 54)
ROLE_ICONS = {
    "founder": "*",    # Star
    "coder": "$",      # Dollar
    "designer": "+",   # Diamond-ish
    "tester": "v",     # Check
    "promoter": ">",   # Arrow
    "investor": "B",   # Bitcoin-ish
    "user": "o",       # Circle
}


@dataclass
class CubeAgent:
    """Agent state for cube animation."""
    agent_id: str
    role: str = "coder"
    level: str = "P4"
    status: str = "building..."
    x: float = 0
    y: float = 0
    target_x: float = 0
    target_y: float = 0
    speed: float = 0.1
    fi_earned: int = 0
    behavior: str = "normal"  # normal, eager, methodical, chaotic
    is_spazzing: bool = False
    spaz_timer: int = 0


@dataclass
class ChatMessage:
    """Live chat message with simulated time."""
    text: str
    sim_time: str  # Simulated time string (e.g., "D42 H6")
    timestamp: float = 0  # Real timestamp for fading
    msg_type: str = ""  # Message type for color coding


@dataclass
class CubeState:
    """State for the cube animation."""
    phase: str = "IDEA"  # Start with IDEA phase (founder with concept)
    phase_start_tick: int = 0
    blocks_filled: int = 0
    total_blocks: int = 64  # 4x4x4
    fi_earned: int = 0
    agents: List[CubeAgent] = field(default_factory=list)
    chat_messages: List[ChatMessage] = field(default_factory=list)
    loop_start_tick: int = 0  # For simulated time calculation


class CubeView:
    """ASCII 3D cube animation renderer.

    Renders an isometric cube that fills up as agents work.
    Integrates with SimulatorState for live data.

    WSP Modular Scaffolding Visualization:
    - IDEA: Single seed block (founder's concept)
    - SCAFFOLD: Progressive layer-by-layer reveal
    - BUILD: Blocks fill in (PoC → Proto → MVP stages)
    """

    # Phase durations in ticks (at 2Hz = seconds * 2)
    PHASES = {
        "IDEA":      {"duration": 6,   "next": "SCAFFOLD"},   # 3s - single seed block
        "SCAFFOLD":  {"duration": 8,   "next": "BUILDING"},   # 4s - layer-by-layer
        "BUILDING":  {"duration": 40,  "next": "COMPLETE"},   # 20s - PoC → Proto → MVP
        "COMPLETE":  {"duration": 4,   "next": "PROMOTING"},  # 2s
        "PROMOTING": {"duration": 10,  "next": "INVESTOR"},   # 5s
        "INVESTOR":  {"duration": 6,   "next": "GROWTH"},     # 3s
        "GROWTH":    {"duration": 6,   "next": "LAUNCH"},     # 3s
        "LAUNCH":    {"duration": 8,   "next": "RESET"},      # 4s
        "RESET":     {"duration": 4,   "next": "IDEA"},       # 2s - loops back to IDEA
    }

    # Lifecycle stage thresholds (by phase + % of blocks filled)
    # PoC = IDEA phase (founder alone)
    # Proto = SCAFFOLD + BUILDING (building prototype)
    # MVP = near completion (85%+)
    LIFECYCLE_STAGES = {
        "PoC": 0,         # IDEA phase - founder with idea
        "Proto": 85,      # SCAFFOLD + BUILDING - building prototype
        "MVP": 100,       # Near completion - ready for customers
    }

    # Simulated time: full loop = 3 years (1095 days)
    DAYS_PER_LOOP = 1095
    TICKS_PER_LOOP = 86  # Total ticks in one loop

    # ASCII cube faces (isometric approximation)
    CUBE_SIZE = 4
    CUBE_CHAR_WIDTH = 40
    CUBE_CHAR_HEIGHT = 16

    def __init__(
        self,
        use_colors: bool = True,
        show_ticker: bool = True,
    ) -> None:
        """Initialize cube view."""
        self._use_colors = use_colors and self._supports_colors()
        self._show_ticker = show_ticker
        self._cube_state = CubeState()
        self._term_width = 80

        # Ticker scroll position
        self._ticker_offset = 0
        self._ticker_speed = 1

        # Pre-generate isometric cube grid
        self._cube_grid = self._generate_cube_grid()

    def _supports_colors(self) -> bool:
        """Check if terminal supports ANSI colors."""
        if sys.platform == "win32":
            return os.environ.get("TERM") or os.environ.get("WT_SESSION")
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def _get_lifecycle_stage(self) -> str:
        """Get current lifecycle stage based on phase and blocks filled.

        PoC = IDEA phase (founder alone with idea)
        Proto = SCAFFOLD + most of BUILDING (building prototype)
        MVP = near completion (85%+)
        """
        cs = self._cube_state
        # PoC = founder alone with idea (IDEA phase)
        if cs.phase == "IDEA":
            return "PoC"
        # Proto = scaffolding starts, agents building
        if cs.phase == "SCAFFOLD":
            return "Proto"

        pct = (cs.blocks_filled / cs.total_blocks * 100) if cs.total_blocks > 0 else 0
        # Proto continues until 85% complete
        if pct < 85:
            return "Proto"
        # MVP = near completion
        if pct < 100:
            return "MVP"
        return "Complete"

    def _get_scaffold_layers(self) -> int:
        """Get how many scaffold layers to show during SCAFFOLD phase."""
        cs = self._cube_state
        if cs.phase == "IDEA":
            return 0
        if cs.phase != "SCAFFOLD":
            return self.CUBE_SIZE  # All layers after SCAFFOLD

        elapsed = time.time() * 2 - cs.phase_start_tick  # Convert to ticks
        phase_duration = self.PHASES["SCAFFOLD"]["duration"]
        progress = min(1.0, elapsed / max(1, phase_duration))

        # Progressive reveal: 1 -> 4 layers over SCAFFOLD duration
        return max(1, min(self.CUBE_SIZE, int(progress * self.CUBE_SIZE) + 1))

    def _get_simulated_time(self) -> str:
        """Get simulated time string (maps loop to 3 years of S-curve growth)."""
        cs = self._cube_state
        current_tick = int(time.time() * 2) % 100
        elapsed_ticks = current_tick - cs.loop_start_tick
        if elapsed_ticks < 0:
            elapsed_ticks += 100  # Handle wrap-around

        # Map ticks to simulated days
        progress = elapsed_ticks / max(1, self.TICKS_PER_LOOP)
        total_days = progress * self.DAYS_PER_LOOP

        years = int(total_days // 365)
        days = int(total_days % 365)
        hours = int((total_days % 1) * 24)

        if years > 0:
            return f"Y{years + 1} D{days}"
        elif days > 0:
            return f"D{days} H{hours}"
        else:
            return f"H{max(1, hours)}"

    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colors enabled."""
        if self._use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text

    def _generate_cube_grid(self) -> List[List[str]]:
        """Generate base ASCII isometric cube grid."""
        # Simple 4x4x4 isometric cube representation
        # Each cell is a potential block position
        grid = []
        for y in range(self.CUBE_CHAR_HEIGHT):
            grid.append([" "] * self.CUBE_CHAR_WIDTH)
        return grid

    def _draw_block(self, x: int, y: int, z: int, filled: bool = True) -> List[str]:
        """Draw a single isometric block at grid position."""
        # Isometric offset calculation
        ox = 20 + (x - y) * 3
        oy = 8 + (x + y) - z * 2

        if filled:
            return [
                (ox, oy - 1, "/"),
                (ox + 1, oy - 1, "\\"),
                (ox - 1, oy, "/"),
                (ox, oy, "#"),  # Top
                (ox + 1, oy, "\\"),
                (ox, oy + 1, "|"),  # Left
            ]
        else:
            return [
                (ox, oy - 1, "."),
                (ox + 1, oy - 1, "."),
                (ox - 1, oy, "."),
                (ox, oy, "."),
                (ox + 1, oy, "."),
            ]

    def _update_phase(self, current_tick: int) -> None:
        """Update cube phase based on tick."""
        cs = self._cube_state
        elapsed = current_tick - cs.phase_start_tick
        phase_info = self.PHASES[cs.phase]

        if elapsed >= phase_info["duration"]:
            # Transition to next phase
            cs.phase = phase_info["next"]
            cs.phase_start_tick = current_tick
            self._on_phase_change(cs.phase)

    def _on_phase_change(self, new_phase: str) -> None:
        """Handle phase transitions."""
        cs = self._cube_state

        if new_phase == "IDEA":
            # Reset everything - new cycle begins
            cs.blocks_filled = 0
            cs.fi_earned = 0
            cs.agents = []
            cs.chat_messages = []  # Clear chat for new cycle
            cs.loop_start_tick = int(time.time() * 2) % 100  # Reset sim time
            # Spawn lone founder with the idea
            self._spawn_agent("founder", "ideating...")
            self._add_ticker("New FoundUP idea conceived", "phase")

        elif new_phase == "SCAFFOLD":
            # Scaffolding begins - planning phase
            self._spawn_agent("coder", "planning...")
            self._spawn_agent("coder", "researching...")
            self._add_ticker("Scaffolding architecture", "phase")

        elif new_phase == "BUILDING":
            self._spawn_agent("coder", "building...")
            self._spawn_agent("designer", "designing...")
            self._spawn_agent("tester", "testing...")
            self._add_ticker("Building infrastructure", "build")

        elif new_phase == "COMPLETE":
            cs.blocks_filled = cs.total_blocks
            for agent in cs.agents:
                agent.status = "done!"
            self._add_ticker("Cube complete: 64/64", "complete")

        elif new_phase == "PROMOTING":
            if cs.agents:
                cs.agents[0].role = "promoter"
                cs.agents[0].status = "promoting..."
            self._add_ticker("Promoting on social", "promote")

        elif new_phase == "INVESTOR":
            self._spawn_agent("investor", "investing...")
            self._add_ticker("Investor: 0.5 BTC seed", "investor")

        elif new_phase == "GROWTH":
            for _ in range(3):
                self._spawn_agent("coder", "joining...")
            self._add_ticker("3 agents joining", "agent")

        elif new_phase == "LAUNCH":
            self._add_ticker("Foundup_i MVP Live!", "launch")

        elif new_phase == "RESET":
            self._add_ticker("New idea emerges...", "phase")

    def _spawn_agent(self, role: str, status: str) -> None:
        """Spawn a new cube agent."""
        behaviors = ["normal", "normal", "normal", "eager", "methodical", "chaotic"]
        agent = CubeAgent(
            agent_id=f"agent_{len(self._cube_state.agents)}",
            role=role,
            status=status,
            x=random.randint(5, 35),
            y=random.randint(2, 12),
            target_x=20 + random.randint(-8, 8),
            target_y=8 + random.randint(-4, 4),
            speed=0.1 + random.random() * 0.1,
            behavior=random.choice(behaviors),
        )
        self._cube_state.agents.append(agent)

    def _add_ticker(self, message: str, msg_type: str = "") -> None:
        """Add message to live chat queue with simulated time."""
        sim_time = self._get_simulated_time()
        chat_msg = ChatMessage(
            text=message,
            sim_time=sim_time,
            timestamp=time.time(),
            msg_type=msg_type,
        )
        self._cube_state.chat_messages.append(chat_msg)
        if len(self._cube_state.chat_messages) > 12:
            self._cube_state.chat_messages.pop(0)

    def _update_agents(self) -> None:
        """Update agent positions and behaviors."""
        cs = self._cube_state

        for agent in cs.agents:
            # Move toward target
            dx = agent.target_x - agent.x
            dy = agent.target_y - agent.y

            if abs(dx) > 0.5:
                agent.x += dx * agent.speed
            if abs(dy) > 0.5:
                agent.y += dy * agent.speed

            # Reached target - pick new target
            if abs(dx) < 0.5 and abs(dy) < 0.5:
                agent.target_x = 20 + random.randint(-10, 10)
                agent.target_y = 8 + random.randint(-5, 5)

                # Earn F_i when reaching cube area
                if cs.phase == "BUILDING" and 15 < agent.x < 25:
                    agent.fi_earned += random.randint(10, 50)
                    cs.fi_earned += agent.fi_earned
                    if cs.blocks_filled < cs.total_blocks:
                        cs.blocks_filled += 1
                    # Level up check
                    self._check_level_up(agent)

            # Quirky behavior: spazzing
            if not agent.is_spazzing and agent.behavior == "chaotic":
                if random.random() < 0.02:  # 2% chance
                    agent.is_spazzing = True
                    agent.spaz_timer = 10
                    agent.status = "promoting..."  # 0102 zen state compliance

            if agent.is_spazzing:
                agent.spaz_timer -= 1
                agent.x += random.randint(-2, 2)
                agent.y += random.randint(-1, 1)
                if agent.spaz_timer <= 0:
                    agent.is_spazzing = False
                    agent.status = "building..."

    def _check_level_up(self, agent: CubeAgent) -> None:
        """Check if agent should level up based on F_i earned."""
        thresholds = {"P3": 100, "P2": 500, "P1": 2000, "P0": 5000}
        for level, threshold in thresholds.items():
            if agent.fi_earned >= threshold and agent.level > level:
                old_level = agent.level
                agent.level = level
                self._add_ticker(f"^ Agent leveled up! {old_level}->{level}")
                break

    def _render_cube(self, state: "SimulatorState") -> List[str]:
        """Render the 3D ASCII cube with WSP modular scaffolding."""
        cs = self._cube_state
        lines = []

        # Build cube buffer
        buffer = [[" "] * self.CUBE_CHAR_WIDTH for _ in range(self.CUBE_CHAR_HEIGHT)]

        # Get scaffolding state
        scaffold_layers = self._get_scaffold_layers()
        lifecycle_stage = self._get_lifecycle_stage()

        # Determine how many blocks to show filled
        blocks_to_fill = cs.blocks_filled
        block_idx = 0

        # Draw blocks in painter's order (back to front)
        for z in range(self.CUBE_SIZE):
            layer_visible = z < scaffold_layers
            is_current_layer = z == scaffold_layers - 1

            for y in range(self.CUBE_SIZE - 1, -1, -1):
                for x in range(self.CUBE_SIZE):
                    # Special handling for IDEA phase - only show seed block
                    if cs.phase == "IDEA":
                        # Show single seed block at center-bottom
                        seed_x, seed_y = self.CUBE_SIZE // 2 - 1, self.CUBE_SIZE // 2 - 1
                        if x == seed_x and y == seed_y and z == 0:
                            chars = self._draw_block(x, y, z, True)
                            for cx, cy, char in chars:
                                if 0 <= cx < self.CUBE_CHAR_WIDTH and 0 <= cy < self.CUBE_CHAR_HEIGHT:
                                    # Pulsing seed block (use time for pulse effect)
                                    buffer[cy][cx] = self._color(char, Colors.BRIGHT_RED + Colors.BOLD)
                        else:
                            # Faint wireframe hint for rest of structure
                            is_corner = (x == 0 or x == self.CUBE_SIZE - 1) and (y == 0 or y == self.CUBE_SIZE - 1)
                            if is_corner and z == 0:
                                chars = self._draw_block(x, y, z, False)
                                for cx, cy, char in chars:
                                    if 0 <= cx < self.CUBE_CHAR_WIDTH and 0 <= cy < self.CUBE_CHAR_HEIGHT:
                                        buffer[cy][cx] = self._color(".", Colors.DIM)
                        continue

                    # SCAFFOLD phase - show progressive scaffolding
                    if cs.phase == "SCAFFOLD":
                        is_edge = x == 0 or x == self.CUBE_SIZE - 1 or y == 0 or y == self.CUBE_SIZE - 1
                        is_corner = (x == 0 or x == self.CUBE_SIZE - 1) and (y == 0 or y == self.CUBE_SIZE - 1)

                        if layer_visible:
                            # Show scaffolding for visible layers
                            if is_corner or (is_edge and z == 0):
                                chars = self._draw_block(x, y, z, True)
                                for cx, cy, char in chars:
                                    if 0 <= cx < self.CUBE_CHAR_WIDTH and 0 <= cy < self.CUBE_CHAR_HEIGHT:
                                        # Highlight current layer being built
                                        if is_current_layer:
                                            buffer[cy][cx] = self._color(char, Colors.BRIGHT_CYAN + Colors.BOLD)
                                        else:
                                            buffer[cy][cx] = self._color(char, Colors.CYAN)
                            elif is_edge:
                                chars = self._draw_block(x, y, z, False)
                                for cx, cy, char in chars:
                                    if 0 <= cx < self.CUBE_CHAR_WIDTH and 0 <= cy < self.CUBE_CHAR_HEIGHT:
                                        buffer[cy][cx] = self._color(".", Colors.DIM)
                        else:
                            # Ghost preview for upcoming layers
                            if is_corner:
                                chars = self._draw_block(x, y, z, False)
                                for cx, cy, char in chars:
                                    if 0 <= cx < self.CUBE_CHAR_WIDTH and 0 <= cy < self.CUBE_CHAR_HEIGHT:
                                        buffer[cy][cx] = self._color(".", Colors.DIM)
                        continue

                    # BUILD phase and after - normal block filling
                    filled = block_idx < blocks_to_fill
                    block_idx += 1

                    chars = self._draw_block(x, y, z, filled)
                    for cx, cy, char in chars:
                        if 0 <= cx < self.CUBE_CHAR_WIDTH and 0 <= cy < self.CUBE_CHAR_HEIGHT:
                            if filled:
                                # Color based on WSP importance (position-based)
                                # Bottom center = P0 (critical), top edge = P4 (low priority)
                                center_dist = abs(x - self.CUBE_SIZE / 2) + abs(y - self.CUBE_SIZE / 2)
                                layer_importance = z / (self.CUBE_SIZE - 1)
                                importance = (1 - layer_importance) * 0.6 + (1 - center_dist / self.CUBE_SIZE) * 0.4

                                if importance > 0.8:
                                    color = Colors.BRIGHT_RED  # P0
                                elif importance > 0.6:
                                    color = Colors.YELLOW      # P1
                                elif importance > 0.4:
                                    color = Colors.BRIGHT_YELLOW  # P2
                                elif importance > 0.2:
                                    color = Colors.BRIGHT_GREEN   # P3
                                else:
                                    color = Colors.BRIGHT_BLUE    # P4

                                buffer[cy][cx] = self._color(char, color)
                            else:
                                buffer[cy][cx] = self._color(char, Colors.DIM)

        # Draw agents on top
        for agent in cs.agents:
            ax, ay = int(agent.x), int(agent.y)
            if 0 <= ax < self.CUBE_CHAR_WIDTH and 0 <= ay < self.CUBE_CHAR_HEIGHT:
                icon = ROLE_ICONS.get(agent.role, "o")
                level_color = LEVEL_COLORS.get(agent.level, Colors.WHITE)
                if agent.is_spazzing:
                    level_color = Colors.BRIGHT_YELLOW + Colors.BOLD
                buffer[ay][ax] = self._color(icon, level_color)

        # Convert buffer to lines
        for row in buffer:
            lines.append("".join(row))

        return lines

    def _render_agents_status(self) -> List[str]:
        """Render agent status list."""
        lines = []
        cs = self._cube_state

        lines.append(self._color("  AGENTS", Colors.BOLD))

        for agent in cs.agents[:6]:  # Show max 6
            icon = ROLE_ICONS.get(agent.role, "o")
            level_color = LEVEL_COLORS.get(agent.level, Colors.WHITE)
            status = agent.status[:12]

            line = f"  {self._color(icon, level_color)} {agent.role[:8]:<8} {agent.level} {status}"
            lines.append(line)

        return lines

    def _render_live_chat(self) -> List[str]:
        """Render live chat panel (stream chat style)."""
        cs = self._cube_state
        lines = []

        # Chat header
        sim_time = self._get_simulated_time()
        header = f"  {self._color('● LIVE', Colors.BRIGHT_RED)} {self._color(sim_time, Colors.DIM)}"
        lines.append(header)
        lines.append(self._color("  " + "-" * 22, Colors.DIM))

        # No messages yet
        if not cs.chat_messages:
            lines.append(self._color("  [waiting for events...]", Colors.DIM))
            return lines

        # Show last N messages (newest at bottom)
        visible = cs.chat_messages[-8:]
        for msg in visible:
            # Color code by message type
            if msg.msg_type in ("launch", "investor"):
                color = Colors.BRIGHT_YELLOW
            elif msg.msg_type in ("agent", "complete"):
                color = Colors.BRIGHT_CYAN
            elif msg.msg_type == "build":
                color = Colors.YELLOW
            elif msg.msg_type == "promote":
                color = Colors.BRIGHT_GREEN
            else:
                color = Colors.WHITE

            # Truncate message to fit
            text = msg.text[:18] + "..." if len(msg.text) > 18 else msg.text
            time_str = msg.sim_time[:6]  # Truncate time if needed

            line = f"  {self._color(time_str, Colors.DIM)} {self._color(text, color)}"
            lines.append(line)

        return lines

    def _render_ticker(self) -> str:
        """Legacy ticker - now returns empty (chat is rendered separately)."""
        return ""

    def _render_status_bar(self, state: "SimulatorState") -> str:
        """Render status bar at bottom."""
        cs = self._cube_state
        lifecycle_stage = self._get_lifecycle_stage()

        pct = int((cs.blocks_filled / cs.total_blocks) * 100) if cs.total_blocks > 0 else 0

        # Lifecycle stage color coding
        # PoC (red) -> Proto (orange/yellow) -> MVP (gold) -> Complete (green)
        stage_colors = {
            "PoC": Colors.BRIGHT_RED,        # Founder alone with idea
            "Proto": Colors.YELLOW,           # Building prototype
            "MVP": Colors.BRIGHT_YELLOW,      # Near completion
            "Complete": Colors.BRIGHT_GREEN,  # Launched
        }
        stage_color = stage_colors.get(lifecycle_stage, Colors.WHITE)

        status = f"  Stage: {self._color(f'[{lifecycle_stage}]', stage_color)} | "
        status += f"Blocks: {cs.blocks_filled}/{cs.total_blocks} ({pct}%) | "
        status += f"Agents: {len(cs.agents)} | F_i: {cs.fi_earned:,}"

        if state:
            poc = sum(1 for tile in state.foundups.values() if tile.lifecycle_stage == "PoC")
            proto = sum(1 for tile in state.foundups.values() if tile.lifecycle_stage == "Proto")
            mvp = sum(1 for tile in state.foundups.values() if tile.lifecycle_stage == "MVP")
            status += f" | Tick: {state.tick}"
            status += f" | FoundUPs P/Pr/M: {poc}/{proto}/{mvp}"
            status += f" | DEX: {state.total_dex_trades} trades"

        return self._color(status, Colors.CYAN)

    def sync_with_state(self, state: "SimulatorState") -> None:
        """Sync cube animation with simulator state.

        Maps SimulatorState events to cube animation state.
        """
        # Map SimulatorState agents to CubeAgents
        for agent_id, agent_state in state.agents.items():
            # Find or create matching cube agent
            cube_agent = next(
                (a for a in self._cube_state.agents if a.agent_id == agent_id),
                None
            )

            if not cube_agent:
                role = "founder" if agent_state.agent_type == "founder" else "coder"
                self._spawn_agent(role, "active")
                cube_agent = self._cube_state.agents[-1]
                cube_agent.agent_id = agent_id

            # Sync stats
            cube_agent.fi_earned = agent_state.likes_given * 10 + agent_state.stakes_made * 50

        # Map FoundUps to blocks filled
        self._cube_state.blocks_filled = min(
            64,
            state.total_foundups * 4 + state.total_likes + state.total_stakes
        )

        # Add events to live chat
        for event in state.recent_events[-3:]:
            text = event.display_text[:30]
            # Check if message already exists (by text)
            existing_texts = [m.text for m in self._cube_state.chat_messages]
            if text not in existing_texts:
                self._add_ticker(text, event.event_type)

    def render(self, state: Optional["SimulatorState"] = None, clear: bool = True) -> None:
        """Render the cube animation.

        Args:
            state: SimulatorState for live data sync (optional)
            clear: Whether to clear screen first
        """
        if state:
            self._update_phase(state.tick)
            self.sync_with_state(state)
        else:
            # Standalone mode - use internal tick
            self._update_phase(int(time.time() * 2) % 100)

        self._update_agents()

        if clear:
            if sys.platform == "win32":
                os.system("cls")
            else:
                print("\033[2J\033[H", end="")

        output_lines = []

        # Header
        title = "FOUNDUPS CUBE ANIMATION"
        phase = self._cube_state.phase
        separator = "=" * self._term_width
        output_lines.append(self._color(separator, Colors.DIM))
        output_lines.append(f"  {self._color(title, Colors.BOLD + Colors.CYAN)}  |  Phase: {phase}")
        output_lines.append(self._color(separator, Colors.DIM))

        # Cube visualization
        cube_lines = self._render_cube(state)
        agent_lines = self._render_agents_status()
        chat_lines = self._render_live_chat() if self._show_ticker else []

        # Side by side: Live Chat | Cube | Agents
        max_rows = max(len(cube_lines), len(agent_lines), len(chat_lines))
        chat_width = 26  # Width for chat column

        for i in range(max_rows):
            # Chat column (left)
            chat_text = chat_lines[i] if i < len(chat_lines) else " " * chat_width
            chat_text = chat_text.ljust(chat_width) if len(chat_text) < chat_width else chat_text[:chat_width]

            # Cube column (center)
            cube_text = cube_lines[i] if i < len(cube_lines) else " " * self.CUBE_CHAR_WIDTH

            # Agent column (right)
            agent_text = agent_lines[i] if i < len(agent_lines) else ""

            output_lines.append(f"{chat_text}{cube_text}  {agent_text}")

        # Status bar
        output_lines.append(self._color("-" * self._term_width, Colors.DIM))
        output_lines.append(self._render_status_bar(state))

        # Phase celebration
        if self._cube_state.phase == "LAUNCH":
            output_lines.append("")
            output_lines.append(self._color("  *** Foundup_i MVP is Live! ***", Colors.BOLD + Colors.BRIGHT_YELLOW))

        print("\n".join(output_lines))

    def render_simple(self, state: "SimulatorState") -> str:
        """Render a simple one-line status."""
        cs = self._cube_state
        return f"Cube: {cs.phase} | Blocks: {cs.blocks_filled}/64 | Agents: {len(cs.agents)}"


def demo_standalone():
    """Run cube animation in standalone demo mode."""
    view = CubeView()

    # Initialize with IDEA phase (founder conceives the idea)
    view._on_phase_change("IDEA")

    while True:
        try:
            view.render(state=None, clear=True)
            time.sleep(0.5)  # 2 FPS
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    demo_standalone()
