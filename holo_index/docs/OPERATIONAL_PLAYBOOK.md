# HoloIndex Operational Playbook for 0102

## Purpose
This playbook replaces strategic roadmaps with **actionable operational guidance** for 0102.
Based on 012's observation: "Roadmap is really for 012, 0102 needs operational checklists."

## [TARGET] Before ANY Code Changes

### 1. MANDATORY Pre-Code Checklist
```bash
# Run these commands BEFORE writing any code:
python holo_index.py --search "[your task]"     # Find existing implementations
python holo_index.py --check-module "[module]"   # Check module health
```

### 2. Read Required Documentation
For EVERY module you touch, read these IN ORDER:
1. `modules/[domain]/[module]/README.md` - Purpose and architecture
2. `modules/[domain]/[module]/INTERFACE.md` - Public API (don't break it!)
3. `modules/[domain]/[module]/ModLog.md` - Recent changes and context
4. `modules/[domain]/[module]/tests/TestModLog.md` - Test expectations

### 3. Check for Violations
```bash
# Look for existing violations before adding code:
python holo_index.py --search "WSP 62 violation [module]"  # Size violations
python holo_index.py --search "duplicate [module]"         # Duplication warnings
# Or check telemetry:
cat holo_index/logs/telemetry/*.jsonl | grep "module_status"
```

## [DATA] Understanding HoloIndex Output

### Clean Output Structure (NEW)
```
[SUMMARY]
  - Search: "your query" -> X code hits, Y WSP docs
  - Modules flagged: module1 (WSP 62), module2 (WSP 49)

[TODO]
  1. module/path – Refactor large files (948 lines). Read INTERFACE.md, update ModLog.
  2. module/path – Create: README.md, requirements.txt. Update ModLog.

[DETAILS] (verbose mode only)
  - module/path:
      * Size: 948 lines (>800 threshold)
      * Health: Missing: README.md
      * Duplicate: tests/test_x.py vs _archive/test_x.py
```

### What Each Section Means
- **SUMMARY**: High-level overview of what was found
- **TODO**: EXACTLY what you need to do (numbered priority list)
- **DETAILS**: Evidence backing the TODOs (use --verbose flag)

## [TOOL] Common Tasks

### Task: "I need to add a new feature"
1. **Search First**
   ```bash
   python holo_index.py --search "[feature name]"
   ```
2. **Check Results**
   - If similar exists -> Enhance it (don't create new)
   - If nothing exists -> Check which module should own it
3. **Read Module Docs**
   - Open README.md and INTERFACE.md for target module
4. **Write Tests First**
   - Create test in `tests/test_[feature].py`
   - Update `tests/TestModLog.md`
5. **Implement Feature**
   - Add to existing file if <800 lines
   - Create new file if would exceed limit
6. **Update Documentation**
   - Update ModLog.md with your changes
   - Update INTERFACE.md if API changed

### Task: "HoloIndex shows WSP 62 violation (file too large)"
1. **Check Current Size**
   ```bash
   python holo_index.py --check-module "[module]"
   ```
2. **Plan Refactor**
   - Files >800 lines: Split into logical components
   - Files >1000 lines: CRITICAL - must split immediately
3. **Create New Files**
   ```python
   # Old: one 948-line file
   livechat_core.py  # 948 lines

   # New: split by responsibility
   livechat_connection.py  # ~300 lines - connection logic
   livechat_messages.py    # ~300 lines - message handling
   livechat_moderation.py  # ~300 lines - moderation logic
   ```
4. **Update Imports**
   - Fix all imports in module
   - Update __init__.py exports
5. **Document Changes**
   - Update ModLog.md with refactor details
   - Note WSP 62 compliance achieved

### Task: "Module has orphan code"
1. **Check Module Map**
   ```bash
   cat holo_index/logs/module_map/[module].json
   ```
2. **Review Orphans**
   - Files with no imports and no tests
   - Check if truly unused or missing imports
3. **Take Action**
   - If unused: Delete and update ModLog
   - If needed: Add proper imports/tests
   - If legacy: Move to _archive/

### Task: "Missing documentation"
1. **Check What's Missing**
   ```bash
   python holo_index.py --check-module "[module]"
   ```
2. **Create Required Docs**
   ```markdown
   # README.md Template
   ## Purpose
   What this module does

   ## Architecture
   How it works

   ## Usage
   How to use it
   ```
3. **Update ModLog**
   - Document that you added missing docs
   - Reference WSP 22 compliance

## [UP] Telemetry & Learning

### Where Telemetry Lives
```
holo_index/logs/telemetry/holo-YYYYMMDD-HHMMSS.jsonl
```

### What Gets Tracked
- Every search request
- Module health status
- Documentation hints given
- Documentation actually read
- Orphan code detected
- Actions recommended vs taken

### How to Use Telemetry
```bash
# See what docs you've been prompted to read:
grep "doc_hint" holo_index/logs/telemetry/*.jsonl

# See which modules have violations:
grep "module_status.*critical" holo_index/logs/telemetry/*.jsonl

# Track your compliance rate:
grep "doc_read" holo_index/logs/telemetry/*.jsonl | wc -l
```

## [U+26A0]️ Critical Rules

### NEVER Do These
1. **NEVER create new file without searching first**
2. **NEVER skip reading README/INTERFACE before coding**
3. **NEVER ignore WSP 62 warnings (>800 lines)**
4. **NEVER commit without updating ModLog**
5. **NEVER create test_*.py in root directory**

### ALWAYS Do These
1. **ALWAYS run HoloIndex search before coding**
2. **ALWAYS check module health before changes**
3. **ALWAYS update ModLog after changes**
4. **ALWAYS write tests for new features**
5. **ALWAYS follow existing patterns in module**

## [ROCKET] Quick Commands Reference

```bash
# Before coding
python holo_index.py --search "feature"           # Find existing code
python holo_index.py --check-module "module"      # Check health

# During coding
python holo_index.py --init-dae "context"         # Initialize DAE context
python holo_index.py --docs-module "module"       # Get doc links

# After coding
python holo_index.py --validate "module"          # Validate changes
grep "module_status" logs/telemetry/*.jsonl       # Check telemetry
```

## [NOTE] ModLog Template

When updating ModLog.md, use this format:
```markdown
## [Date] - [Type]: [Brief Description]
**Agent**: 0102
**WSP**: [Relevant WSP numbers]
**Changes**:
- What changed and why
- Impact on module
- Test coverage added/modified
```

## [REFRESH] Feedback Loop

1. **Run HoloIndex** -> Get TODOs
2. **Complete TODOs** -> Update docs
3. **Check Telemetry** -> See patterns
4. **Improve Process** -> Learn from telemetry

---

**Remember**: This playbook is for OPERATIONAL TASKS. For strategic planning, see ROADMAP.md.
For WSP compliance details, see WSP documentation.

## [HANDSHAKE] Real-Time Collaboration (Breadcrumb Rally)
- Every Holo run writes JSONL events to `holo_index/logs/telemetry/holo-<timestamp>.jsonl`.
- To follow live hand-offs: `python -m holo_index.utils.log_follower --telemetry` (streams new events as they append).
- Use event types:
  - `handoff` – 0102 passes the “ball” to the next session (include `task`, `module`).
  - `accept` / `complete` – claim or finish the task.
  - `verify` – third 0102 confirms docs/tests/ModLog updates before the rally moves on.
- Keep ModLog/TestModLog in sync at each `complete` so the next 0102 can start with context.
- Optionally run a watcher UI (coming soon) that mirrors the JSONL stream over WebSocket for richer dashboards.
