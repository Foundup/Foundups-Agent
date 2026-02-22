# Simulator Satellite Stores (WSP 78)

## Owner
- Module: `modules/foundups/simulator`

## Stores
- `memory/fam_audit.db` / `memory/fam_events.jsonl`
  - Per-run FAM event audit artifacts (Layer C: audit/event).
- `memory/sustainability_matrix_audit/*/fam_audit.db`
  - Monte Carlo and matrix run audit artifacts.
- `memory/validation_runs*/**/fam_audit.db`
  - Scenario validation snapshots for reproducibility.

## Retention Policy
- Single-run debug stores: retain 30 days.
- Validation/matrix artifacts: retain until explicitly archived or pruned.

## Why Not Layer B Operational DB
- These files are disposable run artifacts.
- Folding them into `data/foundups.db` would bloat operational storage and slow routine queries/backups.

## Migration Decision
- Permanent satellite classification (documented exception under WSP 78 Satellite Store Policy).
- No migration to Layer B planned.

