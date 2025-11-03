# Nested Module Violations - Fix Plan

**Date**: 2025-10-26
**Detected by**: gemma_nested_module_detector skill (100% fidelity)
**Total Violations**: 5 (2 CRITICAL, 3 HIGH)

---

## Violations Detected

### CRITICAL: modules/modules/ai_intelligence/
```
Current:  modules/modules/ai_intelligence/ai_overseer/
Correct:  modules/ai_intelligence/ai_overseer/
```

**Contents**:
- ai_overseer/ (entire module duplicated)

**Fix**: Delete modules/modules/ entirely (ai_overseer already exists in correct location)

---

### HIGH: modules/ai_intelligence/ai_intelligence/banter_engine/
```
Current:  modules/ai_intelligence/ai_intelligence/banter_engine/
Correct:  modules/ai_intelligence/banter_engine/
```

**Contents**:
- banter_engine/memory/chat_logs/ (session data, ~50MB of chat logs)
- README.md, INTERFACE.md, src/, tests/

**Fix**: Move modules/ai_intelligence/ai_intelligence/* → modules/ai_intelligence/

**Risk**: Session data contains valuable chat history - BACKUP FIRST

---

### HIGH: modules/ai_intelligence/pqn_mcp/modules/
```
Current:  modules/ai_intelligence/pqn_mcp/modules/ai_intelligence/
Correct:  modules/ai_intelligence/pqn_mcp/ (flatten)
```

**User Feedback**: "module folder needs removed and investigated"

**Fix**: Investigate contents, then remove nested structure

---

### HIGH: modules/communication/livechat/modules/gamification/
```
Current:  modules/communication/livechat/modules/gamification/
Correct:  modules/gamification/whack_a_magat/ (already exists)
```

**Hypothesis**: Old copy of gamification module

**Fix**: Check if duplicate, then remove

---

### HIGH: modules/platform_integration/stream_resolver/modules/infrastructure/
```
Current:  modules/platform_integration/stream_resolver/modules/infrastructure/
Correct:  modules/infrastructure/ (if global) OR platform_integration/stream_resolver/infrastructure/ (if local)
```

**Hypothesis**: Nested dependency copy

**Fix**: Investigate purpose, then remove or flatten

---

## Fix Strategy (Micro-Sprints)

### Sprint 1: Investigation (100 tokens)
1. Check if modules/modules/ai_intelligence is exact duplicate
2. Verify banter_engine/memory has unique data
3. Investigate pqn_mcp/modules contents
4. Compare livechat/modules/gamification to modules/gamification
5. Understand stream_resolver/modules/infrastructure purpose

**Output**: Investigation report with safe/unsafe to delete flags

---

### Sprint 2: Safe Deletions (50 tokens)
Delete confirmed duplicates:
1. modules/modules/ (if exact duplicate of ai_intelligence/)
2. livechat/modules/gamification (if duplicate)
3. pqn_mcp/modules (if empty or duplicate)

**Safety**: Backup first with `git status` check

---

### Sprint 3: Data Migration (150 tokens)
Move unique data:
1. Backup banter_engine/memory/ chat logs
2. Move ai_intelligence/ai_intelligence/* → ai_intelligence/
3. Update any imports referencing old paths
4. Verify no broken references

---

### Sprint 4: Validation (100 tokens)
1. Run gemma_nested_module_detector again
2. Verify 0 violations found
3. Test that modules still import correctly
4. Run pytest on affected modules

**Success Criteria**: 0 violations, all tests pass

---

## WSP Compliance

**Violations Fixed**:
- WSP 3: Module Organization (domain structure)
- WSP 49: Module Structure (file placement)

**Process**:
- WSP 50: Pre-Action Verification (investigate before delete)
- WSP 22: ModLog updates after fix

---

## Estimated Token Cost

| Sprint | Tokens | Agent |
|--------|--------|-------|
| Investigation | 100 | Qwen (strategic) |
| Safe Deletions | 50 | 0102 (manual) |
| Data Migration | 150 | Qwen + 0102 |
| Validation | 100 | Gemma (pattern check) |
| **Total** | **400** | Multi-agent |

---

## Next Steps

**Immediate**: Execute Sprint 1 (Investigation)

**Command**:
```bash
# Check if modules/modules is duplicate
diff -r modules/modules/ai_intelligence modules/ai_intelligence

# Check banter_engine contents
ls -lah modules/ai_intelligence/ai_intelligence/banter_engine/memory

# Investigate pqn_mcp
ls -lah modules/ai_intelligence/pqn_mcp/modules

# Compare gamification
diff -r modules/communication/livechat/modules/gamification modules/gamification

# Check stream_resolver
ls -lah modules/platform_integration/stream_resolver/modules/infrastructure
```

**After Investigation**: Create `NESTED_MODULE_INVESTIGATION_RESULTS.md` for 0102 approval
