# Archived LiveChat Documentation

## Purpose
Historical documents preserved for reference but not needed for daily operations.

## Archive Structure

### 📁 Folders

- **navigation/** - Superseded navigation documents (replaced by ENHANCED_NAVIGATION.md)
- **wsp_compliance/** - Historical WSP compliance reports (module is now compliant)
- **analyses/** - One-time SWOT and comparison analyses (decisions implemented)
- **implementation/** - Completed implementation guides (features now in production)
- **completed/** - Migration and deletion documentation (work completed)
- **misc/** - Miscellaneous redundant documents

## Why Archived?

These documents were archived to:
1. Reduce documentation bloat (30 → 7 essential docs)
2. Achieve WSP 83 compliance (no orphaned docs)
3. Improve navigation efficiency (90% token reduction)
4. Focus on operational documentation only

## Active Documentation

The 7 essential operational documents remain in `docs/`:
1. **ENHANCED_NAVIGATION.md** - WSP 86 navigation with fingerprints
2. **COMPLETE_FUNCTION_MAP.md** - Step-by-step function reference
3. **0102_SESSION_HANDOFF.md** - Session continuity guide
4. **STARTUP_FLOW.md** - Boot sequence documentation
5. **MODULE_DEPENDENCY_MAP.md** - Visual dependency graphs
6. **PQN_INTEGRATION.md** - PQN feature documentation
7. **YOUTUBE_DAE_CROSS_PLATFORM_SWITCHING.md** - Cross-platform logic

## Retrieval

If you need to reference archived documentation:
```bash
# Find specific archived doc
find _archive -name "*.md" | grep -i "keyword"

# View archive contents
ls -la _archive/*/
```

---
*Archived: 2025-09-15 following WSP 83 documentation audit*