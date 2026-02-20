# Database Module — Architecture

> System-specific implementation of [WSP 78: Database Architecture & Scaling Protocol](../../WSP_framework/src/WSP_78_Database_Architecture_Scaling_Protocol.md)

## Unified Database: `data/foundups.db`

Single SQLite file, three namespaces, managed by `DatabaseManager` singleton.

### Current Table Registry

#### Agent Tables (`agents_*`) — [agent_db.py](src/agent_db.py)

| Table                          | Purpose                                           |
| ------------------------------ | ------------------------------------------------- |
| `agents_awakening`             | Agent consciousness state tracking                |
| `agents_memory`                | Learned patterns (type + JSON data)               |
| `agents_errors`                | Error learning with solutions (WSP 48)            |
| `agents_breadcrumbs`           | Multi-agent coordination trails (WSP 54)          |
| `agents_contracts`             | Handoff task assignment between agents            |
| `agents_collaboration_signals` | Agent availability and skills                     |
| `agents_coordination_events`   | Inter-agent communication events                  |
| `agents_autonomous_tasks`      | Discovered work items with priority               |
| `agents_social_posts`          | Agent-generated social media posts for 012 review |

#### Module Documentation Registry

| Table                        | Purpose                                  |
| ---------------------------- | ---------------------------------------- |
| `modules`                    | Registered modules (name, path, domain)  |
| `module_documents`           | Documents per module (type, path, title) |
| `document_relationships`     | Bidirectional doc links                  |
| `module_wsp_implementations` | WSP protocols per module                 |
| `document_cross_references`  | Cross-references in documents            |

#### Infrastructure Tables

| Table                    | Purpose                                 |
| ------------------------ | --------------------------------------- |
| `index_refresh_tracking` | HoloIndex refresh timestamps and counts |
| `selenium_sessions`      | Browser telemetry via `TelemetryStore`  |

---

## Satellite DBs (Outside Unified Store)

These databases exist outside `foundups.db`. Each has a rationale, but consolidation is a future goal per WSP 78.

| File                                                              | Owner                        | Rationale                                   |
| ----------------------------------------------------------------- | ---------------------------- | ------------------------------------------- |
| `social_media_orchestrator/memory/orchestrator_posted_streams.db` | `DuplicatePreventionManager` | YouTube video dedup — high-frequency writes |
| `foundups_vision/data/training/*.db`                              | `VisionTrainingCollector`    | Large binary blobs (screenshots)            |
| `holo_index/violations.db`                                        | HoloIndex                    | File violation tracking                     |
| Various `chroma.sqlite3`                                          | ChromaDB                     | Vector embeddings — managed by library      |
| `modules/foundups/simulator/memory/*/fam_audit.db`                | FAM Simulator                | Per-run audit logs                          |
| `modules/gamification/*/data/*.db`                                | Gamification                 | Game scores and quiz data                   |

### Migration Path

- **Phase 1 (Now)**: New features write to `data/foundups.db`
- **Phase 2**: Migrate `DuplicatePreventionManager` to unified DB
- **Phase 3**: Leave ChromaDB and binary-heavy stores as satellite (by design)

---

## File Structure

```
modules/infrastructure/database/
├── ARCHITECTURE.md              ← you are here
├── src/
│   ├── db_manager.py            # Core singleton (WSP 78)
│   ├── module_db.py             # Module base class with auto-prefixing
│   ├── agent_db.py              # Agent memory + social post capture
│   ├── quantum_agent_db.py      # Quantum encoding extensions
│   ├── quantum_schema.sql       # Quantum table schemas
│   ├── quantum_encoding.py      # Quantum data encoding
│   ├── database.py              # Legacy compatibility
│   ├── dae_orchestration_hub.py # DAE coordination
│   ├── dae_orchestration_integration.py
│   ├── chromadb_corruption_prevention.py
│   └── chromadb_scaling_analysis.py
├── data/
│   └── foundups.db              # Single unified database
└── tests/
    └── test_corruption_prevention.py
```

---

## Post Capture Review Workflow

```
draft → pending_review → approved → posted
                       ↘ rejected
```

```python
from modules.infrastructure.database.src.agent_db import AgentDB
db = AgentDB()

# Agent records a post
post_id = db.record_post('linkedin', 'comment', 'Your VC model is dead...',
                         identity='UnDaoDu', tone='pushback')
# 012 reviews
posts = db.get_posts_for_review()
db.approve_post(post_id, notes='good pushback')
# Agent publishes
db.mark_posted(post_id)
```

_Last Updated: 2026-02-19_
