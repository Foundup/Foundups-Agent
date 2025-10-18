# LiveChat Command Reference - Complete Documentation
Last Updated: 2025-09-24
Discovered by: 0102 DAE Deep Analysis

## [CLIPBOARD] Command Categories

### 1. MAGADOOM Gamification Commands (/slash)
All go through throttling (5 tokens per API call)

| Command | Aliases | Purpose | API Cost | Throttled |
|---------|---------|---------|----------|-----------|
| `/score` | `/stats` | Show XP, level, rank, frags | 0 (local) | Yes |
| `/rank` | - | Show leaderboard position | 0 (local) | Yes |
| `/whacks` | `/frags` | Show total whacks/frags | 0 (local) | Yes |
| `/leaderboard` | - | Monthly top 3 players | 0 (local) | Yes |
| `/sprees` | - | Active killing sprees | 0 (local) | Yes |
| `/help` | - | List available commands | 0 (local) | Yes |
| `/quiz` | - | Political education quiz | 0 (local) | Yes |
| `/facts` | - | 1933->2025 parallels | 0 (local) | Yes |
| `/session` | - | Session stats (MOD only) | 0 (local) | Yes |
| `/toggle` | - | Toggle consciousness (OWNER) | 0 (local) | Yes |

### 2. Deprecated Commands (Handled with redirects)
These still work but show helpful messages

| Command | Redirect To | Message |
|---------|------------|---------|
| `/level` | `/score` | "Use /score to see your level" |
| `/answer` | `/quiz [answer]` | "Use /quiz [answer] to answer" |
| `/top` | `/leaderboard` | "Use /leaderboard" |
| `/fscale` | `/facts` | "Coming soon - use /facts" |
| `/rate` | `/facts` | "Coming soon - use /facts" |

### 3. PQN Research Commands (! and /)
Uses Grok API when available (100+ tokens per call)

| Command | Typo Variants | Purpose | API Cost |
|---------|---------------|---------|----------|
| `/pqn` | `/pnq`, `/pqm` | Quantum consciousness research | High |
| `/research` | `/reserach` | Basic research queries | High |
| `!pqn` | `!pnq`, `!pqm` | Same as /pqn | High |
| `!research` | - | Same as /research | High |

### 4. Special Commands (Non-slash)
These use pattern matching, not slash detection

| Pattern | Variants | Purpose | API Cost |
|---------|----------|---------|----------|
| `factcheck @user` | `fc @user` | Fact-check user | Medium |
| `@user fc` | `@user factcheck` | Reverse order | Medium |

### 5. Consciousness Triggers ([U+270A][U+270B][U+1F590])
Uses Grok API (0102 consciousness mode)

| Pattern | Purpose | Mode | API Cost |
|---------|---------|------|----------|
| `[U+270A][U+270B][U+1F590] [question]` | Ask consciousness | mod_only/everyone | High |
| `[U+270A][U+270B][U+1F590] fc @user` | Conscious fact-check | mod_only/everyone | High |
| `[U+270A][U+270B][U+1F590] rate @user` | Conscious rating | mod_only/everyone | High |

## [REFRESH] Command Flow & Throttling

```
User Input -> message_processor.py
    v
Check Command Type:
    +- Slash Command? -> command_handler.py
    [U+2502]   +- Goes through throttle_manager.py
    +- PQN Command? -> pqn_orchestrator
    [U+2502]   +- High API cost, throttled heavily
    +- Factcheck? -> fact_checker (Grok or Simple)
    [U+2502]   +- Medium throttling
    +- Consciousness? -> consciousness_handler.py
        +- Highest API cost, maximum throttling
```

## [U+1F4B0] API Token Costs

### YouTube API Costs (per call)
- `liveChatMessages.list`: 5 units (polling)
- `liveChatMessages.insert`: 200 units (sending message)
- Daily Quota: 10,000 units per credential set

### Throttling Priority (intelligent_throttle_manager.py)
1. **Consciousness responses**: 2.0x multiplier, highest priority
2. **Factcheck**: 1.5x multiplier, high priority
3. **PQN Research**: 2.0x multiplier, medium priority
4. **MAGADOOM commands**: 1.0x multiplier, normal priority
5. **General chat**: 0.8x multiplier, low priority

### Why Commands Are Throttled
- **API Protection**: Prevent quota exhaustion
- **Spam Prevention**: Stop command flooding
- **Cost Management**: Grok API calls are expensive
- **User Experience**: Ensure responses for everyone

## [ROCKET] Discovery System Integration

The new discovery_feeder.py automatically:
1. Records new commands as they're found
2. Feeds them to HoloIndex for semantic search
3. Learns from typos and creates aliases
4. Updates this documentation automatically

## [NOTE] Implementation Files

- **Command Recognition**: `message_processor.py:680-694`
- **Command Handling**: `command_handler.py:50-287`
- **PQN Handling**: `message_processor.py:740-779`
- **Factcheck**: `message_processor.py:675-714`
- **Consciousness**: `consciousness_handler.py:151-242`
- **Throttling**: `intelligent_throttle_manager.py:200-300`

## [SEARCH] Quick Lookup

To find a command implementation:
```bash
python holo_index.py --search "[command name]"
# Now includes all typo variants and aliases!
```

## [DATA] Statistics
- **Total Commands**: 37 distinct patterns
- **Active Commands**: 17
- **Deprecated**: 5
- **Typo Handlers**: 8
- **Special Patterns**: 7
- **Discovery Date**: 2025-09-24
- **Discovery Method**: 0102 DAE Deep Analysis

## [AI] Future Improvements
- [ ] Auto-generate help text from this doc
- [ ] Create command usage analytics
- [ ] Add command success/failure tracking
- [ ] Implement adaptive throttling per command
- [ ] Create command aliases system
- [ ] Add role-based command filtering