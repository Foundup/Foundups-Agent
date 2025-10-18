# Root Directory Cleanup - WSP 15 MPS Analysis

**Date**: 2025-10-14
**Context**: Foundational system orchestration before full functionality
**Decision Required**: Choose best cleanup approach for 18 root violations

---

## [TARGET] FILE PURPOSE ANALYSIS (Deep Research)

### Log Files (Origin: main.py logging)
| File | Size | PURPOSE | Keep/Archive/Delete |
|------|------|---------|---------------------|
| `main.log` | 90 MB | **ACTIVE** - Current system logs | [OK] KEEP (move to logs/) |
| `youtube_dae_*.log` | 1 MB total | **HISTORICAL** - Legacy testing logs (Sept 30) | [BOX] ARCHIVE |
| `m2j_monitor.log` | 66 bytes | **ACTIVE** - Stream monitoring | [OK] KEEP (move to logs/) |
| `test_shorts_logging.log` | 2 KB | **TESTING** - Development artifact | [BOX] ARCHIVE |

**Purpose**: System observability and debugging. Main.log is CRITICAL for production monitoring.

---

### Test Scripts (Origin: Session development)
| File | PURPOSE | Current Use | Keep/Archive/Delete |
|------|---------|-------------|---------------------|
| `authorize_set10_nonemoji.py` | **ACTIVE TOOL** - Reauthorize OAuth Set 10 (FoundUps) when expired | Still needed | [OK] KEEP (move to scripts/) |
| `test_veo3_fixed.py` | **ONE-TIME FIX** - Validated VEO3 duration parameter fix (Oct 13) | Completed | [BOX] ARCHIVE |
| `test_git_fixes.py` | **ONE-TIME FIX** - Validated git credential rotation fix (Oct 11) | Completed | [BOX] ARCHIVE |
| `debug_codeindex.py` | **DEVELOPMENT** - HoloIndex debugging (Oct 13) | May be useful | [OK] KEEP (move to holo_index/scripts/) |

**Purpose**: Development validation and operational tools. `authorize_set10_nonemoji.py` is CRITICAL for OAuth maintenance.

---

### Temp Files (Origin: Various sessions)
| File | PURPOSE | Current Use | Keep/Archive/Delete |
|------|---------|-------------|---------------------|
| `012.txt` | **PERSONAL NOTES** - 012's working memory (1.4 MB, Oct 13) | Active scratchpad | [OK] KEEP (move to temp/) |
| `stream_trigger.txt` | **MANUAL TRIGGER** - Force stream check (20 bytes) | Development tool | [OK] KEEP (move to temp/) |
| `temp_012_first2k.txt` | **DEBUG DUMP** - Analysis artifact (Oct 9) | Completed | [BOX] ARCHIVE |
| `temp_log_analysis.txt` | **DEBUG DUMP** - Log analysis (Oct 13) | Completed | [BOX] ARCHIVE |
| `temp_test.txt` | **TEST ARTIFACT** - Minimal test (Sept 28) | Obsolete | [FAIL] DELETE |

**Purpose**: Working memory and development artifacts. `012.txt` is the human's active thought space.

---

### Data Directories
| Directory | PURPOSE | Current Use | Action |
|-----------|---------|-------------|--------|
| `holo_index_data/` | HoloIndex persistent storage (ChromaDB) | ACTIVE - semantic search | [OK] MOVE to holo_index/data/ |

**Purpose**: HoloIndex semantic search database. CRITICAL for system intelligence.

---

### Security Documentation
| File | PURPOSE | Action |
|------|---------|--------|
| `SECURITY_CLEANUP_NEEDED.md` | Git history cleanup plan (1728 browser files, 189MB) | [OK] MOVE to docs/security/ |

**Purpose**: Security remediation tracking. Important reference document.

---

## [DATA] WSP 15 MPS SCORING - 4 SOLUTION OPTIONS

### Option 1: Archive + Selective Move (Recommended by 012)
**Philosophy**: "Understand purpose before deleting. Archive is safer than delete."

**Actions**:
1. Create `logs/` directory
2. Create `logs/archive/` for historical logs
3. Create `temp/` directory for active working files
4. Create `docs/archive/session_artifacts/` for completed test scripts
5. Move files based on PURPOSE analysis above
6. Update `main.py` to log to `logs/main.log`
7. Move `holo_index_data/` to `holo_index/data/`
8. Create RootDirectoryGuardian for future prevention

**MPS Breakdown**:
- **Complexity (C)**: 3 - Requires careful file analysis and multiple moves
- **Importance (I)**: 5 - Foundational system needs clean base
- **Deferability (D)**: 1 - Must fix before full orchestration
- **Impact (P)**: 5 - Enables clear mental model + prevents future violations
- **TOTAL MPS**: 3+5+1+5 = **14 (P1 - HIGH PRIORITY)**

**Pros**:
- [OK] Nothing lost - can recover anything
- [OK] Respects 012's working memory (012.txt preserved)
- [OK] Operational tools remain accessible
- [OK] Historical artifacts documented
- [OK] Clear mental model of root directory

**Cons**:
- ⏱️ Takes 15-20 minutes to execute
- [U+1F4C1] Creates more directories to manage
- [SEARCH] Need to track archive locations

---

### Option 2: Aggressive Delete (Fastest)
**Philosophy**: "Clean slate. If we need it, regenerate it."

**Actions**:
1. Delete ALL logs except main.log (move to logs/)
2. Delete ALL test scripts
3. Delete ALL temp files
4. Move holo_index_data/ only
5. Update main.py logging
6. Create RootDirectoryGuardian

**MPS Breakdown**:
- **Complexity (C)**: 1 - Simple delete operations
- **Importance (I)**: 5 - Clean root critical
- **Deferability (D)**: 1 - Must fix before orchestration
- **Impact (P)**: 3 - Clean root, but risk losing useful artifacts
- **TOTAL MPS**: 1+5+1+3 = **10 (P2 - MEDIUM PRIORITY)**

**Pros**:
- [LIGHTNING] Fast execution (< 5 minutes)
- [TARGET] Minimalist approach
- [RULER] Simplest implementation

**Cons**:
- [U+26A0]️ Risk losing useful tools (authorize_set10_nonemoji.py)
- [U+26A0]️ 012.txt deleted (personal notes lost)
- [U+26A0]️ No historical reference
- [U+26A0]️ Can't recover if needed

---

### Option 3: Gradual Migration (Safest)
**Philosophy**: "Move one category at a time, test between each."

**Actions**:
1. **Phase 1**: Move logs -> Test system
2. **Phase 2**: Move test scripts -> Test system
3. **Phase 3**: Move temp files -> Test system
4. **Phase 4**: Move holo_index_data -> Test HoloIndex
5. **Phase 5**: Update main.py logging
6. **Phase 6**: Create RootDirectoryGuardian

**MPS Breakdown**:
- **Complexity (C)**: 4 - Multiple phases with testing
- **Importance (I)**: 5 - Clean root critical
- **Deferability (D)**: 3 - Can take time
- **Impact (P)**: 4 - Safe but slow
- **TOTAL MPS**: 4+5+3+4 = **16 (P0 - CRITICAL but slow)**

**Pros**:
- [OK] Safest approach - test after each move
- [OK] Can rollback if issues found
- [OK] Minimal risk

**Cons**:
- ⏱️ Takes 30-45 minutes total
- [REFRESH] Multiple restarts required
- [U+1F40C] Slow progress

---

### Option 4: Smart Archive with Auto-Cleanup (Best Long-term)
**Philosophy**: "Archive everything, auto-delete after 90 days unless flagged important."

**Actions**:
1. Move ALL violations to appropriate locations (like Option 1)
2. Create `logs/archive/` with auto-cleanup policy
3. Create `docs/archive/` with retention tags
4. Create `temp/` with 30-day auto-cleanup
5. Implement RootDirectoryGuardian with retention policy
6. Add cleanup daemon that runs monthly

**MPS Breakdown**:
- **Complexity (C)**: 5 - Requires auto-cleanup system
- **Importance (I)**: 5 - Sets up long-term health
- **Deferability (D)**: 4 - Can implement incrementally
- **Impact (P)**: 5 - Self-healing system
- **TOTAL MPS**: 5+5+4+5 = **19 (P0 - CRITICAL for long-term)**

**Pros**:
- [OK] Self-healing system
- [OK] Nothing lost initially
- [OK] Automatic maintenance
- [OK] Best for long-term health

**Cons**:
- ⏱️ Takes 2-3 hours to implement fully
- [TOOL] Requires new cleanup daemon
- [AI] More complexity to maintain

---

## [U+1F3C6] RECOMMENDATION

### **OPTION 1: Archive + Selective Move**

**Rationale**:
1. **Respects 012's Input**: You said "understand purpose before deleting" - Option 1 does this
2. **Foundational Focus**: You said "foundational system needs orchestrating first" - Option 1 cleans without risk
3. **Balanced Approach**: Not too slow (Option 3), not too risky (Option 2)
4. **Preservation**: All artifacts saved for potential future reference
5. **Sandbox Philosophy**: You said "FoundUps is your sandbox to re-engineer" - keep the tools!

**Why Not Others?**:
- **Option 2**: Too risky - loses `authorize_set10_nonemoji.py` (critical OAuth tool) and `012.txt` (personal notes)
- **Option 3**: Too slow - delays full system orchestration
- **Option 4**: Right direction but over-engineering for current phase

---

## [CLIPBOARD] OPTION 1 IMPLEMENTATION PLAN

### Phase 1: Directory Structure (1 minute)
```bash
mkdir -p logs/archive
mkdir -p temp
mkdir -p docs/security
mkdir -p docs/archive/session_artifacts
mkdir -p modules/platform_integration/youtube_auth/scripts
mkdir -p holo_index/scripts
```

### Phase 2: Move Active Logs (2 minutes)
```bash
mv main.log logs/
mv m2j_monitor.log logs/
```

### Phase 3: Archive Historical Logs (1 minute)
```bash
mv youtube_dae_fixed.log logs/archive/
mv youtube_dae_fresh.log logs/archive/
mv youtube_dae_monitor.log logs/archive/
mv test_shorts_logging.log logs/archive/
```

### Phase 4: Move Active Tools (2 minutes)
```bash
mv authorize_set10_nonemoji.py modules/platform_integration/youtube_auth/scripts/
mv debug_codeindex.py holo_index/scripts/
```

### Phase 5: Archive Completed Tests (1 minute)
```bash
mv test_veo3_fixed.py docs/archive/session_artifacts/
mv test_git_fixes.py docs/archive/session_artifacts/
```

### Phase 6: Organize Temp Files (2 minutes)
```bash
mv 012.txt temp/
mv stream_trigger.txt temp/
mv temp_012_first2k.txt docs/archive/session_artifacts/
mv temp_log_analysis.txt docs/archive/session_artifacts/
rm temp_test.txt  # Only file we DELETE
```

### Phase 7: Move Data Directory (1 minute)
```bash
mv holo_index_data holo_index/data
# Update HoloIndex config to point to new location
```

### Phase 8: Move Security Doc (1 minute)
```bash
mv SECURITY_CLEANUP_NEEDED.md docs/security/GIT_HISTORY_CLEANUP.md
```

### Phase 9: Fix main.py Logging (2 minutes)
```python
# Update main.py
logging.basicConfig(
    filename='logs/main.log',  # Changed from 'main.log'
    ...
)
```

### Phase 10: Verify & Test (3 minutes)
```bash
# Check root is clean
ls -la *.log *.txt *.py | wc -l  # Should be 0

# Test main.py starts
python main.py --youtube --no-lock

# Test HoloIndex works
python holo_index.py --search "test"
```

**Total Time**: 15 minutes

---

## [REFRESH] POST-CLEANUP: Phase 2 (Root Directory Guardian)

**After** root is clean, implement prevention:

1. Create `holo_index/qwen_advisor/components/root_directory_guardian.py`
2. Integrate with HoloIndex main search
3. Add pre-commit hook
4. Test automated detection

**Estimated Time**: 30 minutes
**Status**: Phase 2 work (do AFTER Phase 1 complete)

---

## [OK] SUCCESS CRITERIA

### Before
- 18 files violating WSP 85
- 90 MB main.log in root
- No archive system
- No prevention

### After
- 0 violations (only sacred files in root)
- Organized logs/ and temp/ directories
- Historical artifacts preserved in docs/archive/
- Tools accessible in proper module locations
- Ready for full system orchestration

---

## [TARGET] DECISION POINT

**Question for 012**:

I recommend **Option 1: Archive + Selective Move** because:
1. It preserves everything (including your 012.txt notes)
2. It's fast enough (15 min) to not delay orchestration
3. It respects the "understand before deleting" principle
4. It keeps critical tools (authorize_set10_nonemoji.py) accessible

**Do you approve Option 1?** If yes, I'll execute the 10-phase plan immediately.

**Alternative**: If you prefer a different option (2, 3, or 4), I can execute that instead.

---

**Status**: ⏸️ AWAITING 012 APPROVAL
**Next**: Execute chosen option -> Full system orchestration
