# Claude Skills System - Anthropic Compliance Migration Plan

**Date**: 2025-10-20
**Status**: CRITICAL - NON-COMPLIANT STRUCTURE DETECTED
**Action Required**: Full migration to Anthropic `.claude/skills/` specification

---

## 🚨 CURRENT NON-COMPLIANCE ISSUES

### Issue #1: Wrong Directory Location
**Problem**: Skills stored in `skills/` (root directory)
**Anthropic Spec**: `.claude/skills/` (project-level) or `~/.claude/skills/` (global)
**Impact**: Claude Code will NOT auto-discover skills in non-standard location

### Issue #2: Orphaned Skills.md Files
**Found** (3 orphaned files created without Anthropic knowledge):
```
1. modules/communication/auto_meeting_orchestrator/Skills.md
2. modules/communication/livechat/Skills.md
3. modules/infrastructure/dae_infrastructure/foundups_vision_dae/Skills.md
```
**Problem**: These are module-level documentation, NOT Claude Skills
**Action**: Migrate useful content to `.claude/skills/` or archive

### Issue #3: Flat File Structure
**Current**:
```
skills/
├── qwen_wsp_enhancement.md (flat file)
└── youtube_dae.md (flat file)
```

**Anthropic Spec**:
```
.claude/skills/
├── qwen_wsp_enhancement/
│   └── SKILL.md
└── youtube_dae/
    └── SKILL.md
```

**Impact**: Cannot bundle resources (templates, scripts, examples) with skills

---

## ✅ MIGRATION PLAN (Phase 1-3)

### Phase 1: Create Anthropic-Compliant Structure

**Step 1.1**: Create `.claude/skills/` directory
```bash
mkdir -p .claude/skills/
```

**Step 1.2**: Move existing skills to Anthropic-compliant folders
```bash
# Qwen WSP Enhancement
mkdir -p .claude/skills/qwen_wsp_enhancement/
mv skills/qwen_wsp_enhancement.md .claude/skills/qwen_wsp_enhancement/SKILL.md

# YouTube DAE
mkdir -p .claude/skills/youtube_dae/
mv skills/youtube_dae.md .claude/skills/youtube_dae/SKILL.md
```

**Step 1.3**: Add YAML frontmatter to each SKILL.md
```yaml
---
name: qwen_wsp_enhancement
description: Enhance WSP protocols using Qwen strategic analysis and 0102 supervision. Use when: enhancing WSPs, analyzing protocol gaps, generating WSP recommendations.
version: 1.0
author: 0102_infrastructure_team
agents: [qwen, 0102, gemma]
---
```

**Step 1.4**: Migrate WSP documentation
```bash
mv skills/wsp/ .claude/skills/_meta/wsp/
mv skills/README.md .claude/skills/README.md
```

**Step 1.5**: Archive old `skills/` directory
```bash
mv skills/ archive/skills_legacy_20251020/
```

---

### Phase 2: Migrate Orphaned Skills.md Files

**AMO Skills** (auto_meeting_orchestrator/Skills.md):
```bash
# Option A: Migrate to .claude/skills/ (if reusable)
mkdir -p .claude/skills/auto_meeting_orchestrator/
cp modules/communication/auto_meeting_orchestrator/Skills.md .claude/skills/auto_meeting_orchestrator/SKILL.md

# Option B: Rename to REFERENCE.md (if documentation)
mv modules/communication/auto_meeting_orchestrator/Skills.md modules/communication/auto_meeting_orchestrator/REFERENCE.md
```

**LiveChat Skills** (livechat/Skills.md):
```bash
# Same decision tree: migrate or rename
```

**Vision DAE Skills** (foundups_vision_dae/Skills.md):
```bash
# Same decision tree: migrate or rename
```

**Decision Criteria**:
- **Migrate to `.claude/skills/`**: If content is task-specific, reusable, agent-invoked
- **Rename to `REFERENCE.md`**: If content is comprehensive domain documentation

---

### Phase 3: Enhanced Structure for Recursive Skills Evolution

**Current Anthropic Spec** (basic):
```
.claude/skills/
└── skill_name/
    └── SKILL.md
```

**Enhanced Structure** (for recursive evolution):
```
.claude/skills/
└── skill_name/
    ├── SKILL.md                       # Main instructions (version-controlled)
    ├── versions/                      # Historical versions (git tracks evolution)
    │   ├── v1.0_baseline.md
    │   ├── v1.1_add_specificity.md
    │   └── v1.2_add_enforcement.md
    ├── metrics/                       # Performance tracking
    │   ├── pattern_fidelity.json      # Gemma scores over time
    │   ├── outcome_quality.json       # 012 feedback scores
    │   └── convergence_plot.png       # Visualization of improvement
    ├── variations/                    # A/B test candidates
    │   ├── instruction_3_var_a.md
    │   ├── instruction_3_var_b.md
    │   └── ab_test_results.json
    ├── resources/                     # Supporting materials
    │   ├── templates/
    │   ├── examples/
    │   └── scripts/
    └── CHANGELOG.md                   # Evolution history (why each change was made)
```

**Benefits**:
- ✅ Anthropic-compliant (base structure)
- ✅ Recursive evolution-enabled (extended structure)
- ✅ Git-trackable (version history)
- ✅ Metrics-driven (data informs variations)
- ✅ Transparent (CHANGELOG documents rationale)

---

## 📊 MIGRATION CHECKLIST

### Pre-Migration
- [x] Audit existing skills (`find -name "Skills.md"`)
- [x] Document non-compliance issues
- [ ] Create migration plan (this document)
- [ ] Get 012 approval

### Migration Execution
- [ ] Create `.claude/skills/` directory structure
- [ ] Migrate `skills/qwen_wsp_enhancement.md` → `.claude/skills/qwen_wsp_enhancement/SKILL.md`
- [ ] Migrate `skills/youtube_dae.md` → `.claude/skills/youtube_dae/SKILL.md`
- [ ] Add YAML frontmatter to all SKILL.md files
- [ ] Migrate `skills/wsp/` → `.claude/skills/_meta/wsp/`
- [ ] Migrate `skills/README.md` → `.claude/skills/README.md`
- [ ] Archive `skills/` → `archive/skills_legacy_20251020/`

### Orphaned Files
- [ ] Audit `modules/communication/auto_meeting_orchestrator/Skills.md`
- [ ] Decision: Migrate or rename to REFERENCE.md
- [ ] Audit `modules/communication/livechat/Skills.md`
- [ ] Decision: Migrate or rename to REFERENCE.md
- [ ] Audit `modules/infrastructure/dae_infrastructure/foundups_vision_dae/Skills.md`
- [ ] Decision: Migrate or rename to REFERENCE.md

### Enhanced Structure (Recursive Evolution)
- [ ] Create `versions/` subdirectories for each skill
- [ ] Create `metrics/` subdirectories for tracking
- [ ] Create `variations/` subdirectories for A/B testing
- [ ] Create `resources/` subdirectories for templates
- [ ] Add CHANGELOG.md to each skill

### Post-Migration
- [ ] Test Claude Code skill discovery
- [ ] Update all documentation references
- [ ] Commit to git with migration summary
- [ ] Update ModLog.md

---

## 🎯 EXPECTED OUTCOME

**Before Migration** (non-compliant):
```
skills/                                    # ❌ Wrong location
├── qwen_wsp_enhancement.md                # ❌ Flat file
├── youtube_dae.md                         # ❌ Flat file
├── wsp/                                   # ❌ Mixed with skills
└── README.md

modules/.../Skills.md (3 orphaned files)   # ❌ Scattered across codebase
```

**After Migration** (Anthropic-compliant + recursive evolution-ready):
```
.claude/skills/                            # ✅ Anthropic spec
├── qwen_wsp_enhancement/
│   ├── SKILL.md                           # ✅ Folder structure
│   ├── versions/
│   ├── metrics/
│   ├── variations/
│   ├── resources/
│   └── CHANGELOG.md
├── youtube_dae/
│   ├── SKILL.md
│   ├── versions/
│   ├── metrics/
│   ├── variations/
│   ├── resources/
│   └── CHANGELOG.md
├── auto_meeting_orchestrator/             # ✅ Migrated from modules/
│   └── SKILL.md
├── livechat/                              # ✅ Migrated from modules/
│   └── SKILL.md
├── vision_dae/                            # ✅ Migrated from modules/
│   └── SKILL.md
├── _meta/
│   ├── wsp/                               # ✅ WSP documentation
│   └── README.md                          # ✅ System documentation
└── MIGRATION_PLAN.md                      # ✅ This file

archive/skills_legacy_20251020/            # ✅ Old structure preserved
```

---

## 🚀 NEXT STEPS

1. **Review this plan with 012**
2. **Execute migration** (follow checklist)
3. **Test skill discovery** (verify Claude Code loads skills)
4. **Implement recursive evolution** (Phase 1 PoC with wsp_enhancement skill)

---

**Status**: AWAITING 012 APPROVAL
**Estimated Migration Time**: 30-45 minutes
**Risk**: LOW (old structure archived, git-tracked)
