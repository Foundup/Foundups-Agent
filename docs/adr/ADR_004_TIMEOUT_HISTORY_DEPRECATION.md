# ADR-004: Deprecate chat_rules.db timeout_history Table

**Date:** 2026-02-19
**Status:** Accepted
**Author:** 0102

## Context

Investigation revealed that `chat_rules.db.timeout_history` table is **dead code**:

### Write Path Analysis

```
ACTUAL PRODUCTION PATH:
  event_handler.py:record_timeout()
    → timeout_announcer.py:record_timeout()
      → whack.py:apply_whack()
      → profile_store.record_whacked_user()
        → magadoom_scores.db ✓

CHAT_RULES PATH (NEVER CALLED):
  chat_rules_engine.py:record_timeout()
    → commands.py:WhackAMAGAtSystem.record_timeout()
      → whack.py:apply_whack()  # SAME as above!
        → magadoom_scores.db ✓
```

The `ChatRulesDB.record_timeout()` method EXISTS (database.py:187) but is **NEVER CALLED** in production code. The `WhackAMAGAtSystem` stub in `commands.py` routes to `whack.py:apply_whack()`.

### Evidence

```
# Grep for actual writes to timeout_history: NONE in production
# Only test files and the unused database.py method exist
```

## Decision

1. **Deprecate** `chat_rules.db.timeout_history` table - mark as dead code
2. **Do NOT remove** - preserve for historical data if any exists
3. **Single Source of Truth**: `magadoom_scores.db.whacked_users`
4. **No migration needed** - data was never written there

## Consequences

### Positive
- Eliminates confusion about which database to query
- Confirms `magadoom_scores.db` as canonical whack storage
- No migration work required

### Negative
- Dead code remains (low risk, no runtime cost)
- Future developers may be confused by unused table

## Implementation

1. Add deprecation comments to `ChatRulesDB.record_timeout()` and `get_timeout_count_for_target()`
2. Update documentation to clarify single source of truth
3. DO NOT delete - preserve for archaeology

## Related

- [commenter_classifier.py fix](../modules/communication/video_comments/src/commenter_classifier.py) - Fixed to use correct database
- [WSP 65: Component Consolidation](../WSP_framework/src/WSP_65_Component_Consolidation_Protocol.md)
