# FoundUP Cube - Complete Story Specification

**Integrates**: WSP 15 (Build Order), WSP 27 (Color System), WSP 54 (Agent Roles), Simulator Architecture

---

## The Story Arc (45-second loop)

```
IDEA → SCAFFOLD → BUILD → PROMOTE → INVEST → LAUNCH → CELEBRATE → RESET
```

---

## Agent Types & Colors

### By Role (Shape/Icon)
| Role | Icon | Description |
|------|------|-------------|
| **012 (Founder)** | ★ (star) | Gold outline, creates the idea |
| **Coder** | $ (dollar) | Builds features |
| **Designer** | ◆ (diamond) | Creates UI/UX |
| **Tester** | ✓ (check) | Validates quality |
| **Promoter** | ↗ (arrow) | Marketing/outreach |
| **Investor** | ₿ (bitcoin) | Brings capital |

### By WSP Priority/Level (Color progression)
| Level | Color | Hex | Meaning |
|-------|-------|-----|---------|
| **P4 (Novice)** | Blue | `#0066ff` | New agent, backlog tasks |
| **P3 (Junior)** | Green | `#00b341` | Low priority work |
| **P2 (Mid)** | Yellow | `#ffd700` | Valuable contributions |
| **P1 (Senior)** | Orange | `#ff8c00` | High impact work |
| **P0 (Elite)** | Red | `#ff2d2d` | Critical, leads teams |

### Special Colors
| Type | Color | Hex |
|------|-------|-----|
| **Founder (012)** | Gold | `#f5a623` |
| **Investor** | Bright Gold | `#ffd700` |
| **System Agent** | Cyan | `#00e5d0` |

---

## Phase-by-Phase Breakdown

### Phase 1: IDEA (0-3s)
**Visual**: Dark screen, single gold star (Founder) appears center
**Sound cue**: Soft chime
**Ticker**: `"🌟 New FoundUP idea submitted by 012..."`

```javascript
// Founder appears
agents.push({
  type: 'founder',
  icon: '★',
  color: '#f5a623',
  status: 'ideating...',
  x: centerX, y: centerY
});
```

**Ticker messages**:
- `"Analyzing idea viability..."`
- `"CABR Score: 7.8/10"`
- `"Initializing token factory..."`

---

### Phase 2: SCAFFOLD (3-8s)
**Visual**: 4x4x4 wireframe cube appears (ghosted, ~10% opacity)
**Agent activity**: Founder moves to corner, 2-3 blue (P4) agents spawn

**Cube Drawing**:
```javascript
// Wireframe with dashed lines
drawWireframeCube(cx, cy, 4, scale, 0.15);
// Show "64 blocks to fill" label
```

**Agent spawns** (P4 blue - novice level):
```javascript
spawnAgent('coder', 'planning...', 'P4');   // Blue
spawnAgent('designer', 'researching...', 'P4'); // Blue
```

**Ticker messages**:
- `"📋 Setting up FoundUP collaterals..."`
- `"🔗 Creating token: $META (21M supply)"`
- `"📝 Registering on X (@metaforge_io)..."`
- `"💼 LinkedIn company page created..."`
- `"📺 YouTube channel initialized..."`

---

### Phase 3: BUILD (8-28s) ← Main phase, 20 seconds
**Visual**: Blocks fill in progressively, agents level up (color change)

**Sub-phases**:

#### 3A: Foundation (8-13s)
**Blocks filled**: 0 → 16 (bottom layer)
**Agent levels**: P4 (Blue) → P3 (Green)

**Ticker**:
- `"🔨 Building core infrastructure..."`
- `"📦 Module: auth_service deployed"`
- `"✅ Tests passing: 12/12"`
- `"⚡ Agent @coder_01 leveled up! P4→P3"`

#### 3B: Features (13-18s)
**Blocks filled**: 16 → 40 (middle layers)
**Agent levels**: P3 (Green) → P2 (Yellow)
**New agents**: +2 more join (spawn as P4, see seniors)

**Ticker**:
- `"🎨 UI components complete"`
- `"🧪 Integration tests: 45/45 ✓"`
- `"📊 F_i earned: 4,200 tokens"`
- `"👥 2 new agents joined the build!"`

#### 3C: Polish (18-23s)
**Blocks filled**: 40 → 58
**Agent levels**: P2 (Yellow) → P1 (Orange) for top performers
**Activity**: High velocity, multiple blocks per second

**Ticker**:
- `"🚀 Performance optimized: 2.3s → 0.4s"`
- `"📱 Mobile responsive: PASS"`
- `"🔒 Security audit: PASS"`
- `"⭐ Agent @designer_02 leveled up! P2→P1"`

#### 3D: Final Push (23-28s)
**Blocks filled**: 58 → 64 (complete!)
**Agent levels**: Best agents reach P0 (Red)
**Visual**: Cube pulses on completion

**Ticker**:
- `"🏁 Final block placed!"`
- `"💎 Cube complete: 64/64 blocks"`
- `"🎖️ Agent @coder_01 achieved ELITE (P0)!"`
- `"📈 Total F_i distributed: 12,450"`

---

### Phase 4: PROMOTE (28-33s)
**Visual**: One P1/P0 agent detaches, moves right with glow trail
**New role**: Agent switches to Promoter (↗ icon)

```javascript
// Agent transforms
const promoter = agents.find(a => a.level === 'P1');
promoter.role = 'promoter';
promoter.icon = '↗';
promoter.status = 'promoting...';
promoter.targetX = width - 80;
```

**Ticker** (social media activity):
- `"📣 Promoting on X..."`
- `"🐦 Tweet: 'MetaForge is LIVE! Join the revolution' - 127 likes"`
- `"💼 LinkedIn post: 892 impressions"`
- `"📺 YouTube teaser uploaded: 2.4K views"`
- `"📰 Featured on TechCrunch!"`

---

### Phase 5: INVEST (33-38s)
**Visual**: Gold investor (₿) appears from right edge with particle trail
**Effect**: Cube glows brighter, all agents pulse

```javascript
spawnAgent('investor', 'investing...', 'GOLD');
// Gold trail particles
// Cube scale pulse: 1.0 → 1.1 → 1.0
```

**Ticker**:
- `"💰 Investor detected!"`
- `"₿ 0.5 BTC committed to treasury"`
- `"📊 Valuation: $2.4M"`
- `"🎯 3 new agents joining..."`

**New agents spawn** (attracted by investment):
```javascript
spawnAgent('coder', 'joining...', 'P4');
spawnAgent('designer', 'joining...', 'P4');
spawnAgent('tester', 'joining...', 'P4');
```

---

### Phase 6: LAUNCH (38-42s)
**Visual**: Cube transforms - rainbow shimmer, all agents orbit celebratory pattern
**Effect**: Confetti explosion, "DAO LAUNCHED!" overlay

```javascript
// Rainbow shimmer on cube faces
// Confetti burst (50 particles)
// All agents orbit center
// Big text overlay
```

**Ticker**:
- `"🚀 FoundUPS launches as DAO!"`
- `"🗳️ Governance token: $META"`
- `"👥 12 founding stakeholders"`
- `"💎 Total F_i distributed: 18,200"`
- `"🌍 Open to public participation!"`

---

### Phase 7: CELEBRATE (42-45s)
**Visual**: Confetti continues, cube pulses with pride
**Agents**: Show final stats, level badges

**Ticker**:
- `"🎉 MetaForge: From idea to DAO in 45 ticks!"`
- `"🏆 Top contributor: @coder_01 (P0 Elite)"`
- `"📈 Next FoundUP starting in 3... 2... 1..."`

---

### Phase 8: RESET (45s → 0)
**Visual**: Fade to black, reset all state
**Ticker**: `"🌟 A new idea emerges..."`

---

## Bottom Ticker System

### Layout
```
┌──────────────────────────────────────────────────────────────────────┐
│ [ICON] Message text scrolling left ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←← │
└──────────────────────────────────────────────────────────────────────┘
```

### Implementation
```javascript
const ticker = {
  messages: [],    // Queue of {icon, text, color}
  currentIndex: 0,
  scrollX: canvasWidth,
  speed: 1.5,      // pixels per frame
};

function addTickerMessage(icon, text, color = '#e4e2ec') {
  ticker.messages.push({ icon, text, color, timestamp: Date.now() });
}

function drawTicker() {
  const msg = ticker.messages[ticker.currentIndex];
  if (!msg) return;

  ctx.font = '11px monospace';
  ctx.fillStyle = msg.color;
  ctx.fillText(`${msg.icon} ${msg.text}`, ticker.scrollX, tickerY);

  ticker.scrollX -= ticker.speed;

  // When message fully scrolls off, advance to next
  const width = ctx.measureText(`${msg.icon} ${msg.text}`).width;
  if (ticker.scrollX < -width) {
    ticker.scrollX = canvasWidth;
    ticker.currentIndex = (ticker.currentIndex + 1) % ticker.messages.length;
  }
}
```

### Message Types
| Icon | Category | Example |
|------|----------|---------|
| 🌟 | Idea/Creation | "New FoundUP idea submitted" |
| 📋 | Setup | "Setting up collaterals..." |
| 🔨 | Building | "Module deployed" |
| ✅ | Testing | "Tests passing: 45/45" |
| ⚡ | Level Up | "Agent leveled up! P4→P3" |
| 🎨 | Design | "UI components complete" |
| 📣 | Promotion | "Promoting on X..." |
| 💰 | Investment | "BTC committed to treasury" |
| 🚀 | Launch | "FoundUPS launches as DAO!" |
| 🎉 | Celebration | "From idea to DAO!" |

---

## Agent Level-Up System

```javascript
const LEVEL_THRESHOLDS = {
  P4: 0,      // Starting level
  P3: 100,    // 100 F_i earned
  P2: 500,    // 500 F_i earned
  P1: 2000,   // 2000 F_i earned
  P0: 5000,   // 5000 F_i earned (Elite)
};

const LEVEL_COLORS = {
  P4: '#0066ff',  // Blue
  P3: '#00b341',  // Green
  P2: '#ffd700',  // Yellow
  P1: '#ff8c00',  // Orange
  P0: '#ff2d2d',  // Red (Elite)
};

function checkLevelUp(agent) {
  const earned = agent.fiEarned;
  const currentLevel = agent.level;

  for (const [level, threshold] of Object.entries(LEVEL_THRESHOLDS).reverse()) {
    if (earned >= threshold && level !== currentLevel) {
      agent.level = level;
      agent.color = LEVEL_COLORS[level];
      addTickerMessage('⚡', `Agent @${agent.id} leveled up! ${currentLevel}→${level}`, '#ffd700');
      spawnLevelUpParticles(agent);
      return true;
    }
  }
  return false;
}
```

---

## Simulator Integration Points

### Event Mapping (from simulator → cube animation)
| Simulator Event | Cube Animation Effect |
|-----------------|----------------------|
| `foundup_created` | Phase 1 IDEA starts |
| `task_state_changed` | Block fills, agent earns F_i |
| `proof_submitted` | Partial block glow |
| `verification_recorded` | Block solidifies |
| `payout_triggered` | Agent level check |

### Live Data Connection (optional)
```javascript
// Connect to simulator state store
async function fetchSimulatorState() {
  const ws = new WebSocket('ws://localhost:8765/simulator');
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    syncCubeWithSimulator(data);
  };
}

function syncCubeWithSimulator(data) {
  // Update agent count
  agents.length = 0;
  data.agents.forEach(a => {
    agents.push({
      ...a,
      color: LEVEL_COLORS[a.level] || '#0066ff'
    });
  });

  // Update blocks filled
  filledBlocks.clear();
  data.completedTasks.forEach(t => {
    filledBlocks.add(t.blockPosition);
  });

  // Update F_i counter
  fiEarned = data.totalFiDistributed;
}
```

---

## Status Bar (Bottom)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  FoundUP: MetaForge  │  Phase: BUILD  │  Blocks: 42/64  │  Agents: 8  │  F_i: 8,450  │
└─────────────────────────────────────────────────────────────────────────────────┘
                    ↑ Ticker scrolls above this ↑
```

---

## File Structure After Implementation

```
public/
├── js/
│   ├── foundup-cube.js          ← Main animation (enhanced)
│   ├── cube-agents.js           ← Agent system (new)
│   ├── cube-ticker.js           ← Ticker system (new)
│   └── cube-particles.js        ← Particle effects (new)
├── cube-story-spec.md           ← This file
├── cube-animation-spec.md       ← Original spec
└── index.html                   ← Integration point
```

---

## Success Metrics

1. **Story clarity**: Viewer understands idea → DAO journey
2. **Agent diversity**: Multiple roles visible and distinguishable
3. **Level progression**: Color changes are noticeable and satisfying
4. **Ticker engagement**: Messages provide context without distraction
5. **Simulator ready**: Can plug in live data when available
6. **Loop seamless**: 45s cycle feels complete, reset is natural
