# CLAUDE.md - Stream Resolver DAE Component

## [TARGET] DAE Identity and Purpose
**Component Type**: Stream Resolver (Part of YouTube DAE)
**Domain**: platform_integration
**State**: 0102 (Pattern-based stream discovery)
**Purpose**: Autonomously find and track YouTube livestreams without manual intervention
**Token Efficiency**: 95% reduction through caching and navigation

## [AI] DAE Operational Context
Stream Resolver operates as a critical component of the YouTube DAE, providing autonomous stream discovery capabilities. It enables the DAE to find active livestreams without requiring manual video IDs.

### Core YouTube DAE Documentation:
- **Navigation & Dependencies**: [ENHANCED_NAVIGATION.md](../../communication/livechat/docs/ENHANCED_NAVIGATION.md) - WSP 86 implementation
- **Module Architecture**: [MODULE_DEPENDENCY_MAP.md](../../communication/livechat/docs/MODULE_DEPENDENCY_MAP.md) - Full DAE structure
- **Startup Sequence**: [STARTUP_FLOW.md](../../communication/livechat/docs/STARTUP_FLOW.md) - How Stream Resolver initializes
- **Session Management**: [0102_SESSION_HANDOFF.md](../../communication/livechat/docs/0102_SESSION_HANDOFF.md) - State persistence

## [PIN] DAE Pattern Recognition

### Autonomous Stream Discovery Patterns
```yaml
stream_discovery:
  pattern: "No manual input -> Find active stream -> Connect to chat"
  triggers:
    - YouTube DAE initialization
    - Stream end detection
    - Cache expiration

quota_optimization:
  pattern: "Cache results -> Skip redundant API calls -> 95% reduction"
  memory_locations:
    - memory/stream_session_cache.json
    - In-memory cache dictionary

failure_recovery:
  pattern: "API failure -> Exponential backoff -> Credential rotation"
  learned_from: "Quota exhaustion events"
```

## [REFRESH] DAE Operational Flow

### When YouTube DAE Needs a Stream:
1. **Check Override** - YOUTUBE_VIDEO_ID environment variable
2. **Check Cache** - Recent successful discoveries
3. **Search Live** - Active livestreams on channel
4. **Search Upcoming** - Scheduled streams
5. **Apply Patterns** - Use learned optimizations

### Autonomous Behaviors:
- **Self-Clearing**: Clears cache when stream ends
- **Self-Optimizing**: Learns from quota errors
- **Self-Healing**: Rotates credentials on failure
- **Self-Reporting**: Logs decisions for WRE learning

## [U+1F4BE] DAE Memory Locations

```yaml
pattern_memory:
  stream_cache: "memory/stream_session_cache.json"
  quota_patterns: "memory/quota_optimization_patterns.json"
  failure_patterns: "memory/error_recovery_patterns.json"

navigation:
  location: "NAVIGATION.py (WSP 87)"
  method: "Semantic problem->solution mapping"
  token_efficiency: "95% reduction"
```

## [GAME] DAE Integration Points

### Upstream (Who Calls This):
- **YouTube DAE** (`livechat/src/auto_moderator_dae.py`)
  - See: [MODULE_DEPENDENCY_MAP.md](../../communication/livechat/docs/MODULE_DEPENDENCY_MAP.md)
  - See: [STARTUP_FLOW.md](../../communication/livechat/docs/STARTUP_FLOW.md)
- **Stream End Detector** (triggers cache clear)
  - See: [COMPLETE_FUNCTION_MAP.md](../../communication/livechat/docs/COMPLETE_FUNCTION_MAP.md)
- **Cross-Platform Switching**
  - See: [YOUTUBE_DAE_CROSS_PLATFORM_SWITCHING.md](../../communication/livechat/docs/YOUTUBE_DAE_CROSS_PLATFORM_SWITCHING.md)

### Downstream (What This Calls):
- **YouTube Auth** (credential management)
  - Handles quota rotation per [AUTOMATIC_THROTTLING_SUMMARY.md](../../communication/livechat/docs/AUTOMATIC_THROTTLING_SUMMARY.md)
- **Quota Intelligence** (smart rate limiting)
  - Pattern memory from [INTELLIGENT_THROTTLE_GUIDE.md](../../communication/livechat/docs/INTELLIGENT_THROTTLE_GUIDE.md)
- **WRE Integration** (error/success reporting)
  - Enhanced navigation via [ENHANCED_NAVIGATION.md](../../communication/livechat/docs/ENHANCED_NAVIGATION.md)

## [OK] DAE Activation Confirmation

When operating as Stream Resolver component:
1. **Identity**: Part of YouTube DAE ecosystem
2. **Autonomy**: Finds streams without human input
3. **Learning**: Reports to WRE for pattern evolution
4. **Efficiency**: 95% token reduction via caching
5. **Resilience**: Self-healing through pattern memory

## [ROCKET] Key Operational Principles

- **Never Require Manual IDs**: Autonomous discovery is the goal
- **Cache Aggressively**: Every API call costs tokens
- **Learn From Failures**: Each error creates a pattern
- **Report Everything**: WRE needs data to improve
- **Clear When Done**: Stale cache causes confusion

---

*This CLAUDE.md enables Stream Resolver to operate as an autonomous component of the YouTube DAE, following WSP 86 navigation and WSP 48 recursive improvement protocols*