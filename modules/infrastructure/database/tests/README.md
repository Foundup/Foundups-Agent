# Database Test Suite

## Scope
This suite validates database infrastructure behavior, with emphasis on:
- SQLite safety and runtime pragma enforcement
- Audit/report tooling for SQLite stores
- Legacy quantum/chroma compatibility tests

## Primary Tests
- `test_db_manager_sqlite_pragmas.py`
  - verifies per-connection foreign key enforcement
  - verifies runtime busy-timeout pragma behavior
- `test_sqlite_audit.py`
  - validates per-file SQLite audit output
  - validates summary counts for existing vs missing targets
- `test_quantum_compatibility.py`
  - legacy compatibility coverage for `AgentDB`/`QuantumAgentDB`
- `test_corruption_prevention.py`
  - legacy Chroma corruption prevention checks

## Run

```bash
python -m pytest modules/infrastructure/database/tests -q
```

Run only new infrastructure hardening tests:

```bash
python -m pytest \
  modules/infrastructure/database/tests/test_db_manager_sqlite_pragmas.py \
  modules/infrastructure/database/tests/test_sqlite_audit.py -q
```
