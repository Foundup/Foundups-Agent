# WSP 90 Phase 2 - Entrypoint Files Review

**Status**: PENDING
**Created**: 2026-02-26
**Owner**: 0102
**Priority**: Low (system works, this is cleanup)

## Context

Phase 1 (complete) fixed 78 non-entrypoint library modules.
Phase 2 (this doc) covers 155 entrypoint files that still have UTF-8 wrapping.

## Why Deferred

Entrypoint files (`if __name__ == "__main__":`) may legitimately need UTF-8 wrapping when run standalone (not via main.py). Each needs individual review.

## Files Remaining

Run to see current list:
```bash
python modules/development/wsp_tools/scripts/fix_wsp90_utf8_bulk.py --dry-run --include-entrypoints
```

## Review Criteria

For each file, determine:

| Scenario | Action |
|----------|--------|
| Always run via main.py | Remove wrapping (main.py handles it) |
| Can be run standalone | Add guard: `if not os.environ.get('FOUNDUPS_UTF8_WRAPPED')` |
| Test file | Usually safe to remove (pytest handles encoding) |
| Script in scripts/ | Likely needs guard (often run directly) |

## Execution Plan

1. Run `--dry-run --include-entrypoints` to get list
2. Categorize files by type (test, script, module)
3. Apply appropriate fix per category
4. Validate with `py_compile`

## Command to Apply (when ready)

```bash
# Review first!
python modules/development/wsp_tools/scripts/fix_wsp90_utf8_bulk.py --dry-run --include-entrypoints -v

# Then apply
python modules/development/wsp_tools/scripts/fix_wsp90_utf8_bulk.py --apply --include-entrypoints
```

## Completion Criteria

- [ ] All 155 entrypoint files reviewed
- [ ] Each has appropriate fix (removed or guarded)
- [ ] `--dry-run` reports 0 pending
- [ ] System smoke test passes
