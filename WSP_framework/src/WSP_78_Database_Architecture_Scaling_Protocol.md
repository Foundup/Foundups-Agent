# WSP 78: Database Architecture & Scaling Protocol

## Core Principle: One Database, Three Namespaces

**"Simple shared storage with module isolation that scales infinitely"**

Every FoundUp MUST use a single database with three logical namespaces. No microservices. No per-module databases. One file, three prefixes.

---

## The Three Namespaces

```
{foundup}.db
├── modules_*     # All module data (auto-prefixed per module)
├── foundups_*    # Independent FoundUp project data
└── agents_*      # Agent memory, state, and captured outputs
```

### Namespace Rules

| Namespace | Prefix Pattern                  | Example                                | Owner                                        |
| --------- | ------------------------------- | -------------------------------------- | -------------------------------------------- |
| Modules   | `modules_{module_name}_{table}` | `modules_chat_rules_moderators`        | Individual modules via `ModuleDB` base class |
| FoundUps  | `foundups_{project}_{table}`    | `foundups_youtube_bot_channels`        | Independent FoundUp projects                 |
| Agents    | `agents_{table}`                | `agents_memory`, `agents_social_posts` | Agent infrastructure                         |

---

## Required Infrastructure

### 1. Database Manager (Singleton)

Every FoundUp MUST have a single `DatabaseManager` that:

- Manages one database file
- Enables WAL mode for concurrency
- Enables foreign keys
- Provides thread-safe connection management
- Exposes `execute_query()` (reads) and `execute_write()` (writes)

### 2. Module Base Class

Every module that stores data MUST extend a `ModuleDB` base class that:

- Auto-prefixes all tables with `modules_{module_name}_`
- Provides standard CRUD operations
- Prevents table naming conflicts between modules

### 3. Agent State Tables

Agent data MUST be stored in the unified database under `agents_*` prefix. This includes:

- Awakening/consciousness state
- Learned patterns and memory
- Error learning
- Coordination and contracts
- **All agent-generated outputs** (posts, comments, actions) for operator review

---

## Scaling Path

| Stage | Technology    | When        | Changes Required                           |
| ----- | ------------- | ----------- | ------------------------------------------ |
| 1     | SQLite        | 0–10K users | None — WAL handles concurrency             |
| 2     | PostgreSQL    | 10K–100K    | Change connection string to `DATABASE_URL` |
| 3     | Read Replicas | 100K–1M     | Add connection pooling and read routing    |
| 4     | Sharding      | 1M+         | Shard by namespace                         |

> [!IMPORTANT]
> Do NOT pre-optimize. Stay on SQLite until you outgrow it. The namespace design means scaling requires zero code changes — only infrastructure changes.

---

## Satellite DB Exceptions

Some data MAY live outside the unified database when:

- Managed by a third-party library (e.g., ChromaDB vector stores)
- Contains large binary blobs that would bloat the main DB
- Is ephemeral/disposable (per-run logs, training batches)

All satellite DBs MUST be documented in the system's `ARCHITECTURE.md` with justification and a consolidation plan.

---

## Anti-Patterns

❌ Creating separate databases per module
❌ Storing agent outputs only in-memory (must persist for operator review)
❌ Using microservices before 1M+ users
❌ Skipping the review workflow for agent-generated content

✅ One database, three namespaces
✅ Auto-prefixed module tables
✅ All agent outputs captured to SQL
✅ Plan for scaling, don't pre-optimize

---

_Protocol Status: ACTIVE_
_Version: 3.0.0_
_Last Updated: 2026-02-19_
