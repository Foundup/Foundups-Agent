# FoundUps Simulator

Visual simulation of the autonomous FoundUp ecosystem.

## Architecture

```
FAMDaemon (SSoT)
    ↓ emits events
event_bus.py
    ↓ normalizes
state_store.py (renderable state)
    ↓ reads
render/ (terminal_view, pygame_view)

mesa_model.py (agent behaviors)
    ↓ calls
adapters/fam_bridge.py
    ↓ uses
FAM modules (no new logic)
```

## Key Principles

1. **FAMDaemon events = Single Source of Truth (SSoT)**
2. **state_store derives renderable state from event stream**
3. **Render layer reads ONLY from state_store**
4. **Adapters bridge to existing FAM code - NO logic invention**
5. **Phantom plugs ONLY where logic is missing**

## Usage

```bash
# Run with defaults (3 founders, 10 users, 2 ticks/sec)
python -m modules.foundups.simulator.run

# Run for 1000 ticks then stop
python -m modules.foundups.simulator.run --ticks 1000

# Customize agents and speed
python -m modules.foundups.simulator.run --founders 5 --users 20 --speed 4.0

# Verbose logging
python -m modules.foundups.simulator.run --verbose
```

## Configuration

Edit `config.py` to adjust:
- Number of agents
- Tick rate (simulation speed)
- Random seed (determinism)
- Viewport size

## Views

### Terminal View (Default)
- Top: FoundUp Mall grid (tiles with likes/tokens)
- Bottom: FAMDaemon event log + agent states

### Pygame View (Optional)
- Pixel tiles with interaction glow
- HUD panel with token flow
- Scrollable event log

## Agent Types

- **FounderAgent**: Creates FoundUps via TokenFactory + Foundup model
- **UserAgent**: Like/follow/stake behaviors using FAM interfaces

## Event Flow

1. Mesa model steps agents
2. Agents call FAM adapters (fam_bridge.py)
3. FAM modules emit events to FAMDaemon
4. event_bus captures and normalizes events
5. state_store updates renderable state
6. Render reads state_store and draws

## WSP References

- WSP 91: Observability (FAMDaemon integration)
- WSP 72: Module independence (adapters don't invent logic)
