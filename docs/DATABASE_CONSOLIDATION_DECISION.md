# Database Consolidation Decision - Unified foundups.db

**Date**: 2025-10-21
**Decision By**: 012 (user) + 0102 (implementation)
**Status**: APPROVED - Execution via Gemma/Qwen Pipeline

---

## Executive Summary

**DECISION**: Consolidate all scattered JSONL telemetry files into a single unified SQLite database at `data/foundups.db`.

**REASON**: Current architecture has 20+ JSONL files across modules with no cross-module query capability, concurrency risks, and no indexing.

**EXECUTION**:
1. **Gemma** audits all JSONL files → `data/gemma_jsonl_audit_report.json`
2. **Qwen** analyzes audit → designs schema → `docs/DATABASE_CONSOLIDATION_STRATEGY.md`
3. **0102** reviews Qwen's plan → executes migration → validates tests

---

## Current State (Problem)

### Scattered JSONL Files

```
modules/ai_intelligence/agent_permissions/memory/
├── permission_events.jsonl
└── confidence_events.jsonl

modules/communication/livechat/logs/
├── chat_messages.jsonl
└── youtube_dae_heartbeat.jsonl

modules/infrastructure/foundups_selenium/logs/
└── selenium_sessions.jsonl

... and many more across modules
```

### Problems

1. **No Cross-Module Queries**: Cannot join permissions + confidence + chat history
2. **Concurrency Risks**: Multiple processes writing to same file = corruption risk
3. **No Indexing**: Linear scan O(n) for all lookups
4. **No Analytics**: Cannot run SQL queries for debugging/dashboards
5. **Duplicated Code**: Each module reinvents JSONL append logic

---

## Proposed Architecture (Solution)

### Unified Database

```
data/foundups.db (SQLite)
├── permission_events         (agent permission grants/revocations)
├── confidence_events         (agent confidence tracking)
├── chat_messages             (livechat history)
├── selenium_sessions         (browser automation telemetry)
├── daemon_health             (heartbeat monitoring)
├── error_events              (system errors)
└── metrics_events            (performance metrics)
```

### Benefits

1. **Cross-Module Queries**:
   ```sql
   -- Get all events for agent X across permissions + confidence + chat
   SELECT * FROM (
     SELECT timestamp, 'permission' as type, event_type FROM permission_events WHERE agent_id='gemma_dead_code_detection'
     UNION ALL
     SELECT timestamp, 'confidence' as type, event_type FROM confidence_events WHERE agent_id='gemma_dead_code_detection'
   ) ORDER BY timestamp DESC;
   ```

2. **Thread-Safe**: SQLite handles concurrent writes with WAL mode
3. **Indexed Lookups**: Fast queries by agent_id, timestamp, event_type
4. **SQL Analytics**: Complex queries for debugging, dashboards, reports
5. **Atomic Transactions**: No partial write corruption
6. **Single Source of Truth**: One database, not 20+ JSONL files

---

## Implementation Plan

### Phase 1: Gemma Audit (Read-Only)

**Skill**: [.claude/skills/gemma_jsonl_database_audit.json](.claude/skills/gemma_jsonl_database_audit.json)

**Objective**: Find ALL JSONL files and categorize for migration

**Operations**:
1. Find all `**/*.jsonl` files
2. Grep for `open.*\.jsonl.*'[aw]'` (find writers)
3. Categorize by domain: permissions, confidence, chat, telemetry, etc.
4. Assess concurrency risk: high/medium/low
5. Output: `data/gemma_jsonl_audit_report.json`

**Success**: >= 10 files discovered, >= 5 domains categorized

---

### Phase 2: Qwen Analysis (Strategic Design)

**Skill**: [.claude/skills/qwen_database_consolidation_strategy.json](.claude/skills/qwen_database_consolidation_strategy.json)

**Objective**: Design unified database schema and migration plan

**Deliverables**:
1. **Strategy Report**: `docs/DATABASE_CONSOLIDATION_STRATEGY.md`
2. **SQL Schema**: `data/foundups_db_schema.sql`
3. **Migration Checklist**: `data/db_migration_checklist.json`

**Schema Example**:
```sql
CREATE TABLE permission_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    permission_level TEXT,
    granted_by TEXT,
    confidence REAL,
    justification TEXT,
    approval_signature TEXT,
    metadata_json TEXT
);

CREATE INDEX idx_permission_agent ON permission_events(agent_id);
CREATE INDEX idx_permission_timestamp ON permission_events(timestamp);
```

**Migration Priority**:
1. **High Priority**: Concurrency risks (permissions, confidence) - migrate first
2. **Medium Priority**: Cross-module queries (chat, sessions)
3. **Low Priority**: Simple logs (errors, metrics) - migrate last

---

### Phase 3: 0102 Execution (Implementation)

**Objective**: Migrate modules to use TelemetryStore pattern

**Steps**:
1. Review Qwen's strategy report
2. Approve schema design
3. Create `modules/infrastructure/telemetry_store/` (generalized TelemetryStore)
4. Migrate `agent_permissions` module first (highest priority)
5. Run tests (21 confidence tests + 15 permission tests = 36 total)
6. Migrate remaining modules incrementally
7. Deprecate JSONL files after successful migration

**Reference Implementation**: `modules/infrastructure/foundups_selenium/src/telemetry_store.py`

---

## Success Criteria

✓ **Gemma Audit Complete**: >= 10 JSONL files discovered
✓ **Qwen Strategy Approved**: Schema design + migration plan validated by 0102
✓ **agent_permissions Migrated**: 36/36 tests passing with SQLite backend
✓ **Cross-Module Query Working**: Can join permissions + confidence events via SQL
✓ **Concurrency Safe**: Multiple processes can write simultaneously

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing JSONL readers | High | Phase migration - keep JSONL during transition |
| SQLite file locking on Windows | Medium | Use WAL mode + autocommit |
| Migration data loss | High | Keep JSONL backups until migration validated |
| Performance degradation | Low | SQLite faster than JSONL line parsing |

---

## Skills Created

1. **Gemma**: [.claude/skills/gemma_jsonl_database_audit.json](.claude/skills/gemma_jsonl_database_audit.json)
2. **Qwen**: [.claude/skills/qwen_database_consolidation_strategy.json](.claude/skills/qwen_database_consolidation_strategy.json)

---

## WSP Compliance

- **WSP 77**: Agent Coordination (Gemma audit → Qwen strategy → 0102 execution)
- **WSP 50**: Pre-Action Verification (design before migration)
- **WSP 72**: Module Independence (TelemetryStore abstraction)
- **WSP 91**: Observability (unified telemetry architecture)

---

## Next Steps

**IMMEDIATE**:
1. Run Gemma skill: `gemma_jsonl_database_audit`
2. Wait for: `data/gemma_jsonl_audit_report.json`
3. Run Qwen skill: `qwen_database_consolidation_strategy`
4. Wait for: `docs/DATABASE_CONSOLIDATION_STRATEGY.md`
5. Review Qwen's report with 012
6. Execute migration starting with `agent_permissions` module

**FUTURE**:
- Dashboard integration (query foundups.db for visualizations)
- Export utilities (foundups.db → CSV/JSON for external analysis)
- Backup/restore utilities
- Multi-DB support (dev/staging/prod databases)

---

**Status**: DECISION APPROVED - Skills created, awaiting Gemma execution
**Owner**: 012 (decision) + 0102 (execution)
**Priority**: High (fixes concurrency risks + enables cross-module analytics)
