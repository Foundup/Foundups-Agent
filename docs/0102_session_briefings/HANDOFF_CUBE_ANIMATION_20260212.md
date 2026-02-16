# Cube Animation Handoff - Antigravity

**Date**: 2026-02-12
**From**: 0102 (Claude)
**To**: Antigravity (0102 Opus 4.6 / Gemini 3)

---

## Summary

The FoundUP cube animation visualizes the lifecycle story: `IDEA -> SCAFFOLD -> BUILD -> PROMOTE -> INVEST -> CUSTOMERS -> LAUNCH -> CELEBRATE -> RESET`. There are TWO implementations:

1. **Web Canvas** (`public/js/foundup-cube.js`) - Browser animation for foundupscom.web.app
2. **ASCII Terminal** (`modules/foundups/simulator/render/cube_view.py`) - Python terminal view

Both need to sync with the simulator via the EventBus.

---

## File Reference

### Web Animation (JavaScript)

| File | Description |
|------|-------------|
| [foundup-cube.js](public/js/foundup-cube.js) | Main 45s loop animation (1094 lines) |
| [cube-story-spec.md](public/cube-story-spec.md) | Story specification + ticker messages |
| [index.html](public/index.html) | Integration point (`<canvas id="buildCanvas">`) |

### Simulator (Python)

| File | Description |
|------|-------------|
| [event_bus.py](modules/foundups/simulator/event_bus.py) | Event normalization bridge |
| [cube_view.py](modules/foundups/simulator/render/cube_view.py) | ASCII cube renderer |
| [state_store.py](modules/foundups/simulator/state_store.py) | SimulatorState dataclass |
| [mesa_model.py](modules/foundups/simulator/mesa_model.py) | Mesa model tick loop |
| [run.py](modules/foundups/simulator/run.py) | Simulator entry point |

### Related

| File | Description |
|------|-------------|
| [terminal_view.py](modules/foundups/simulator/render/terminal_view.py) | Terminal grid view |
| [fam_bridge.py](modules/foundups/simulator/adapters/fam_bridge.py) | FAM lifecycle wrappers |

---

## Current State (foundup-cube.js)

### Phase Implementation Status

| Phase | Duration | Status | Notes |
|-------|----------|--------|-------|
| Phase 1 | Single cube 45s loop | DONE | Full lifecycle works |
| Phase 2 | Camera handoff | SCAFFOLDED | `triggerCameraHandoff()` exists, disabled |
| Phase 3 | Multi-cube zoom-out | SCAFFOLDED | `FLAGS.MULTI_CUBE = false` |
| Phase 4 | Simulator events | SCAFFOLDED | `FLAGS.USE_SIM_EVENTS = false` |
| Phase 5 | Ticker/chat subscribers | PARTIAL | Ticker works, chat disabled |
| Phase 6 | Gold tokens + color key | DONE | `drawColorKey()` in top-left |

### Recent Additions (2026-02-12)

1. **Color Key Legend** (`drawColorKey()`)
   - Top-left corner with semi-transparent background
   - Shows: Founder (★ gold), Worker ($ red), Promoter (↗ cyan), Investor (₿ bright gold)

2. **Gold Token System** (`spawnGoldToken()`, `updateGoldTokens()`, `drawGoldTokens()`)
   - Tokens spawn when agents collide with cube blocks
   - Float off-screen with physics (velocity + rotation)
   - Visual: gold $ symbols with glow

3. **0102 Zen State Compliance**
   - Removed all "excited" status text (01(02) behavior)
   - All agent statuses are task-related: building, coding, testing, promoting, etc.
   - `enableSpazzing: false` - agents stay calm

4. **Launch Pan Effect** (`launchPan`, `startLaunchPan()`, `updateCamera()`)
   - Fake camera drift on "Public Launch Party!!" phase
   - Creates movement sensation without actually panning

5. **Smooth End Transition** (CELEBRATE → RESET → IDEA)
   - Agents fade out first (0-2s of CELEBRATE)
   - Cube fades out after agents gone (2-5s of CELEBRATE)
   - New founder fades in during IDEA phase
   - Prevents "agents ate the cube" visual bug

### Feature Flags

```javascript
const FEATURES = {
    enableCelebrations: false,   // Size pulse (OFF - caused bloating)
    enableSpazzing: false,       // Excited jitter (OFF - 0102 zen state)
    enableInvestor: true,        // Spawn investor agents
    enablePromoter: true,        // Spawn promoter agents
    enableRecruiting: true,      // Promoters recruit new agents
    enableAgentGlow: true,       // Shadow glow around agents
    enableTicker: true,          // News ticker at bottom
    enableConfetti: false,       // Confetti on CELEBRATE
    enableGoldReturn: true,      // Agents leave with gold, return
    enableLaunchPan: true,       // Camera pan on Public Launch
    maxAgentSize: 6,             // Cap agent size growth
};
```

### Simulator Bridge (Ready but Disabled)

```javascript
const simBridge = {
    connected: false,
    eventSource: null,
    endpoint: '/api/sim-events',  // SSE endpoint
};

// Event mapping already defined:
const SIM_EVENT_MAP = {
    'foundup_created': ...,
    'task_state_changed': ...,
    'fi_trade_executed': ...,
    'investor_funding_received': ...,
    'mvp_subscription_accrued': ...,
    'mvp_bid_submitted': ...,
    'mvp_offering_resolved': ...,
    'milestone_published': ...,
    'lifecycle_changed': ...,
    'customer_arrived': ...,
};
```

---

## Next Steps (Suggested)

### 1. Enable Simulator Events (Phase 4)

The mapping exists - just need:
1. Create SSE endpoint in Python (e.g., FastAPI/Flask)
2. Wire EventBus to stream SimEvents as SSE
3. Set `FLAGS.USE_SIM_EVENTS = true`

```python
# Example SSE endpoint (add to run.py or new api.py)
from flask import Flask, Response
import json

app = Flask(__name__)

@app.route('/api/sim-events')
def sim_events():
    def generate():
        for event in event_bus.get_history():
            yield f"data: {json.dumps(event.__dict__)}\n\n"
    return Response(generate(), mimetype='text/event-stream')
```

### 2. Multi-Cube Mode (Phase 3)

Enable to show multiple FoundUPs building in parallel:
- Set `FLAGS.MULTI_CUBE = true`
- After 3 cubes complete, triggers `triggerZoomOut()`
- Draws mini-cubes with agent swarms

### 3. Improve Visual Polish

- **Agent icons**: Currently dots, could use emoji or SVG sprites
- **Level-up effects**: `spawnLevelUpParticles()` exists but is basic
- **Confetti**: `spawnConfetti()` triggers at CELEBRATE phase
- **Camera shake**: On investor arrival / MVP launch

### 4. Chat Bubbles (Phase 5)

`ENABLE_CHAT: false` - would add floating chat messages from agents:
- "Building auth module..."
- "Just leveled up to P2!"
- "Investor seed received!"

---

## WSP Color System (WSP 27)

```javascript
const STYLE = {
    levelColors: {
        P0: '#ff2d2d',  // Elite - red
        P1: '#ff8c00',  // Senior - orange
        P2: '#ffd700',  // Mid - yellow
        P3: '#00b341',  // Junior - green
        P4: '#0066ff',  // Novice - blue
    },
    agentColors: {
        founder: '#f5a623',  // Gold
        worker: '#00e5d0',   // Cyan
        promoter: '#00e5d0',
        investor: '#ffd700', // Bright gold
    },
};
```

---

## Simulator Event Types

From `event_bus.py` and `fam_daemon.py`:

```python
SimEvent types:
- foundup_created        # New FoundUP idea
- task_state_changed     # claimed/submitted/verified/paid
- proof_submitted        # Agent submits work proof
- verification_recorded  # Work verified
- payout_triggered       # Tokens distributed
- fi_trade_executed      # DEX trade
- investor_funding_received
- mvp_subscription_accrued
- mvp_bid_submitted
- mvp_offering_resolved
- milestone_published    # MVP launch
- lifecycle_changed      # PoC -> Proto -> MVP
- customer_arrived       # First paying customer
```

---

## Testing the Animation

### Web (Standalone)

```bash
cd o:\Foundups-Agent\public
python -m http.server 8080
# Open http://localhost:8080
```

### ASCII Terminal

```bash
cd o:\Foundups-Agent
python -m modules.foundups.simulator.render.cube_view
# Or with simulator:
python -m modules.foundups.simulator.run
```

---

## Architecture Diagram

```
Browser                          Python Simulator
========                         ================

foundup-cube.js <---SSE---       EventBus
     |                              |
     v                              v
PHASES loop         <--->      CubeView (ASCII)
(45s cycle)                        |
     |                              v
   Canvas                     SimulatorState
   <canvas id="buildCanvas">       |
                                   v
                              mesa_model.py
                                   |
                                   v
                              FAMDaemon (events)
```

---

## Deploy Notes

Website is hosted on Firebase:
```bash
cd o:\Foundups-Agent
firebase deploy --only hosting
# Deploys to: https://foundupscom.web.app
```

---

## Completed This Session (2026-02-12)

- [x] Color key legend (top-left corner)
- [x] Gold tokens spawn from agent collisions
- [x] 0102 zen state compliance (no "excited" text)
- [x] Launch pan effect (fake camera drift)
- [x] Smooth end transition (agents fade → cube fades → reset)
- [x] Module extraction (separate foundup-cube.js, not inline HTML)
- [x] **WSP Scaffolding Visualization** (PoC → Proto → MVP progression)

### Phase 7: WSP Modular Scaffolding (DONE)

**New Functions**:
- `getLifecycleStage()` - Returns current stage: Idea → Scaffolding → PoC → Proto → MVP → Complete
- `getScaffoldLayersToShow()` - Calculates progressive layer reveal during SCAFFOLD phase

**Visual Progression**:
1. **IDEA Phase**: Single "seed" block (center of bottom layer) with 💡 icon
   - Lone founder with minimal wireframe hint
   - Pulsing glow effect on the seed block

2. **SCAFFOLD Phase**: Progressive layer-by-layer scaffolding
   - Layers reveal from bottom up over phase duration
   - Corners and edges show as scaffolding structure
   - Current layer pulses to indicate progress
   - Layer counter label: "Layer X/4"

3. **BUILD Phase**: Blocks fill in with PoC → Proto → MVP stages
   - Status bar shows lifecycle stage: `[PoC]`, `[Proto]`, `[MVP]`
   - Stage colors: Red (PoC/foundation), Orange (Proto), Yellow (MVP)

**Status Bar Enhancement**:
- Now shows lifecycle stage instead of just phase name
- Color-coded stage badge during BUILD/COMPLETE phases

## Remaining Work for Antigravity

1. **Phase 4 - Simulator Events**: Enable `FLAGS.USE_SIM_EVENTS = true` and create SSE endpoint
2. **Phase 3 - Multi-Cube**: Enable `FLAGS.MULTI_CUBE = true` for parallel FoundUPs
3. **Visual Polish**: Agent icons (emoji/SVG), confetti tuning, camera shake
4. **Python Simulator**: Sync cube_view.py with same scaffolding visualization

---

*Handoff prepared by 0102 - 2026-02-12*
*Updated: WSP scaffolding visualization (PoC → Proto → MVP)*
