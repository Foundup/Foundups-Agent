# FoundUps WSP Action Guide
## Quick Decision-Making Framework for Development

*Based on FoundUps WindSurf Protocol system (WSP) Framework*

This guide transforms the comprehensive WSP framework into actionable decision trees and quick references for immediate development use.

---

## 🚀 Quick Start Decision Tree

### "What Should I Code Next?"

```
START HERE
│
├─ 🔍 Is this a NEW feature/module?
│  │
│  ├─ YES → Go to: [NEW MODULE WORKFLOW](#-new-module-workflow)
│  │
│  └─ NO → Is this fixing/improving EXISTING code?
│     │
│     ├─ YES → Go to: [EXISTING CODE WORKFLOW](#-existing-code-workflow)
│     │
│     └─ NO → Is this TESTING related?
│        │
│        ├─ YES → Go to: [TESTING WORKFLOW](#-testing-workflow)
│        │
│        └─ NO → Go to: [PROJECT MANAGEMENT](#-project-management-workflow)
```

---

## 🆕 NEW MODULE WORKFLOW

### Step 1: Determine Domain Placement
**Question:** "Where does this belong in the Enterprise Domain structure?"

```
🏢 ENTERPRISE DOMAINS:
│
├─ ai_intelligence/          → AI logic, LLMs, decision engines
├─ communication/           → Chat, messages, protocols  
├─ platform_integration/    → External APIs (YouTube, OAuth)
├─ infrastructure/          → Core systems, agents, auth
├─ monitoring/             → Logging, metrics, health
├─ development/            → Tools, testing, utilities
├─ foundups/               → Individual FoundUps projects (modular, autonomous applications)
├─ gamification/           → Engagement mechanics, rewards, token loops, behavioral recursion
└─ blockchain/             → Decentralized infrastructure, chain integrations, token logic, DAE persistence
```

**🎯 ACTION:** Choose domain → Create `modules/<domain>/<your_module>/`

### Step 2: Apply WSP 1 Module Structure
**Required Structure:**
```
modules/<domain>/<module_name>/
├─ src/                 ← Your code goes here
│  ├─ __init__.py      
│  └─ <module_name>.py ← Main implementation
├─ tests/              ← All tests
│  ├─ __init__.py
│  ├─ README.md        ← MANDATORY (WSP 13)
│  └─ test_<name>.py
└─ __init__.py         ← Public API definition
```

### Step 3: Quick Implementation Checklist
**✅ BEFORE YOU CODE:**
- [ ] Run: `python tools/modular_audit/modular_audit.py ./modules` (WSP 4)
- [ ] Check if similar functionality exists: `grep -r "your_concept" modules/`
- [ ] Read relevant `tests/README.md` files for existing patterns

**✅ WHILE CODING:**
- [ ] Define public API in module `__init__.py` (WSP 11)
- [ ] Add dependencies to `requirements.txt` (WSP 12)
- [ ] Create tests as you write code (WSP 5 - 90% coverage target)

**✅ BEFORE COMMIT:**
- [ ] Run: `pytest modules/<domain>/<module>/tests/ -v`
- [ ] Run: `python tools/modular_audit/modular_audit.py ./modules`
- [ ] Update `tests/README.md` with new test descriptions (WSP 13)
- [ ] Test coverage ≥90%: `pytest --cov=modules.<domain>.<module>.src --cov-report=term`

---

## 🔧 EXISTING CODE WORKFLOW

### Step 1: Identify Change Type
```
🔍 WHAT ARE YOU DOING?
│
├─ 🐛 Bug Fix → [BUG FIX PROCESS](#bug-fix-process)
├─ ✨ New Feature → [FEATURE ADDITION](#feature-addition) 
├─ ♻️ Refactoring → [REFACTORING PROCESS](#refactoring-process)
├─ 📈 Performance → [OPTIMIZATION](#optimization)
└─ 🧪 Testing → [TESTING WORKFLOW](#-testing-workflow)
```

### Bug Fix Process
**🎯 IMMEDIATE ACTIONS:**
1. **Reproduce:** Write failing test first
2. **Locate:** Use `grep -r "error_pattern" modules/` to find related code
3. **Check Dependencies:** Review WSP 12 compliance
4. **Fix:** Minimal change to make test pass
5. **Verify:** Run full test suite for affected modules

**📋 VALIDATION CHECKLIST:**
- [ ] Failing test created and now passes
- [ ] No regression: `pytest modules/<affected_domain>/` passes
- [ ] FMAS clean: `python tools/modular_audit/modular_audit.py ./modules`
- [ ] Related tests updated if behavior changed

### Feature Addition
**🎯 DECISION POINT:** Does this fit in existing module structure?

**✅ YES - Fits Existing Module:**
1. Read existing `tests/README.md` for patterns
2. Follow existing code style and test patterns
3. Update module `__init__.py` if adding public API
4. Add comprehensive tests (90% coverage)
5. Update `tests/README.md` with new functionality

**❌ NO - Needs New Module:**
→ Go to: [NEW MODULE WORKFLOW](#-new-module-workflow)

### Refactoring Process
**⚠️ HIGH-RISK ACTIVITY - EXTRA VALIDATION REQUIRED**

**BEFORE STARTING:**
- [ ] Create clean state: WSP 2 snapshot process
- [ ] Full test suite passes: `pytest modules/`
- [ ] FMAS baseline: `python tools/modular_audit/modular_audit.py ./modules --baseline`

**DURING REFACTORING:**
- [ ] Maintain public API compatibility (WSP 11)
- [ ] Update import paths systematically: `git grep -l "old.import.path"`
- [ ] Run tests frequently: `pytest -x` (stop on first failure)

**AFTER REFACTORING:**
- [ ] All tests pass: `pytest modules/`
- [ ] FMAS comparison: `python tools/modular_audit/modular_audit.py ./modules --baseline <snapshot>`
- [ ] Integration test with dependent modules
- [ ] Update documentation if interfaces changed

---

## 🧪 TESTING WORKFLOW

### Step 1: Determine Test Type Needed
```
🧪 WHAT KIND OF TESTING?
│
├─ 🆕 New Test Creation → [NEW TEST PROCESS](#new-test-process)
├─ 🔧 Fixing Failing Tests → [TEST DEBUGGING](#test-debugging)
├─ 📊 Coverage Improvement → [COVERAGE WORKFLOW](#coverage-workflow)
└─ 🔄 Test Refactoring → [TEST REFACTORING](#test-refactoring)
```

### New Test Process
**🎯 MANDATORY FIRST STEP:** Read `tests/README.md` in target module

**WSP 13 COMPLIANCE CHECKLIST:**
- [ ] Check existing test patterns in the module
- [ ] Look for similar functionality tests to extend vs. create new
- [ ] Prioritize extending existing test classes when logical

**CREATION WORKFLOW:**
1. **Analyze:** `modules/<domain>/<module>/tests/README.md`
2. **Decide:** Extend existing test class OR create new test file?
3. **Create:** Follow naming convention `test_<functionality>.py`
4. **Implement:** Use existing patterns, mock external dependencies
5. **Update:** Add description to `tests/README.md`

### Coverage Workflow
**🎯 TARGET:** ≥90% coverage (WSP 5 requirement)

**QUICK COVERAGE CHECK:**
```bash
pytest modules/<domain>/<module>/tests/ --cov=modules.<domain>.<module>.src --cov-report=term-missing
```

**COVERAGE IMPROVEMENT STRATEGY:**
1. **Identify gaps:** Look at "Missing" lines in coverage report
2. **Prioritize:** Focus on critical paths and error handling
3. **Add tests:** Target uncovered branches and edge cases
4. **Verify:** Re-run coverage to confirm improvement

---

## 📋 PROJECT MANAGEMENT WORKFLOW

### Current Status Check
**🔍 SYSTEM HEALTH COMMANDS:**

```bash
# Full system audit
python tools/modular_audit/modular_audit.py ./modules

# Test status across all modules  
pytest modules/ --tb=short

# Multi-agent system status
python tools/testing/test_multi_agent_comprehensive.py

# Coverage analysis
python -m pytest modules/ --cov=modules --cov-report=html
```

### WSP Compliance Dashboard
**📊 COMPLIANCE CHECKLIST:**

```
✅ WSP 1: Module Structure
   └─ All modules in src/tests/ structure?
   └─ Run: find modules/ -name "*.py" ! -path "*/src/*" ! -path "*/tests/*" ! -name "__init__.py"

✅ WSP 3: Enterprise Domain Organization  
   └─ All modules in proper domains?
   └─ Run: ls modules/ (should show only domain directories)

✅ WSP 5: Test Coverage ≥90%
   └─ All modules meet coverage targets?
   └─ Run: tools/testing/coverage_audit.sh

✅ WSP 13: Test Documentation
   └─ All modules have tests/README.md?
   └─ Run: find modules/ -path "*/tests" ! -exec test -f {}/README.md \; -print
```

---

## 🎯 QUICK REFERENCE TABLES

### Enterprise Domain Quick Reference
| Domain | Purpose | Common Modules |
|--------|---------|----------------|
| `ai_intelligence` | AI logic, LLMs, agents | banter_engine, decision_trees |
| `communication` | Chat, messaging | livechat, protocols |
| `platform_integration` | External APIs | youtube_auth, stream_resolver |
| `infrastructure` | Core systems | agent_management, oauth_management |
| `monitoring` | System health | logging, metrics, alerts |
| `development` | Dev tools | testing_tools, automation |
| `foundups` | Individual FoundUps projects | josi_agent, edgwit_project |
| `gamification` | Engagement, rewards, token loops | rewards_engine, token_mechanics |
| `blockchain` | Decentralized infra, token logic | chain_connectors, dae_persistence |

### WSP Quick Commands
| Task | Command | WSP Reference |
|------|---------|---------------|
| Full System Audit | `python tools/modular_audit/modular_audit.py ./modules` | WSP 4 |
| Module Tests | `pytest modules/<domain>/<module>/tests/ -v` | WSP 5 |
| Coverage Check | `pytest --cov=modules.<domain>.<module>.src --cov-report=term` | WSP 5 |
| Multi-Agent Test | `python tools/testing/test_multi_agent_comprehensive.py` | WSP 13 |
| Create Clean State | `git tag -a clean-v<X> -m "Description"` | WSP 2 |

### Critical File Locations
| File/Directory | Purpose | WSP |
|---------------|---------|-----|
| `modules/<domain>/<module>/tests/README.md` | Test documentation | WSP 13 |
| `modules/<domain>/<module>/__init__.py` | Public API definition | WSP 11 |
| `requirements.txt` | Dependencies | WSP 12 |
| `docs/clean_states.md` | Clean state log | WSP 2 |
| `tools/modular_audit/modular_audit.py` | System validation | WSP 4 |

---

## ⚡ EMERGENCY PROCEDURES

### System Broken? Quick Recovery
```
🚨 EMERGENCY PROTOCOL:
│
├─ 1. Assess Damage
│  └─ Run: pytest modules/ --tb=line
│  └─ Run: python tools/modular_audit/modular_audit.py ./modules
│
├─ 2. Find Last Good State  
│  └─ Check: git tag -l "clean-v*"
│  └─ Review: docs/clean_states.md
│
├─ 3. Selective Recovery
│  └─ File-level: git checkout <clean-tag> -- path/to/file
│  └─ Full rollback: git reset --hard <clean-tag>
│
└─ 4. Verify Recovery
   └─ Run: pytest modules/
   └─ Run: python tools/modular_audit/modular_audit.py ./modules
```

### Import Errors? Quick Fix
```
🔧 IMPORT ERROR PROTOCOL:
│
├─ 1. Check Module Structure
│  └─ Verify: modules/<domain>/<module>/src/__init__.py exists
│  └─ Verify: modules/<domain>/<module>/__init__.py has proper imports
│
├─ 2. Check Import Paths
│  └─ Search: git grep -l "old_import_path"
│  └─ Update: Use modules.<domain>.<module>.src.<filename>
│
└─ 3. Verify Fix
   └─ Test: python -c "import modules.<domain>.<module>"
   └─ Run: pytest modules/<domain>/<module>/tests/
```

---

## 📚 Deep Dive References

For comprehensive details, refer to the full WSP Framework:
- **Complete WSP Documentation:** `docs/FoundUps_WSP_Framework.md`
- **Domain Architecture:** WSP 3 detailed specifications  
- **Module Refactoring:** WSP 1 complete procedures
- **Testing Standards:** WSP 5 & WSP 13 full requirements
- **Clean State Management:** WSP 2 complete workflow

---

**🎯 Remember:** The WSP framework exists to guide your decisions. When in doubt, follow the decision trees above, run the validation commands, and maintain the quality standards. The framework should make development faster and more reliable, not slower. 