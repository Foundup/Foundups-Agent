[SEMANTIC SCORE: 0.0.0]
[ARCHIVE STATUS: ACTIVE_PARTIFACT]
[ORIGIN: WSP_appendices/APPENDIX_B.md]

# Appendix B: Roadmap & ModLog Format Templates

*(These templates define the standard structure for the project roadmap and ModLog entries found in `docs/ModLog.md`.)*

## Roadmap Structure Template

```markdown
# FoundUps Agent Modular Change Log

This log tracks module changes, updates, and versioning for FoundUps Agent under the Windsurf modular development model. LLME (Appendix G) scores are tracked via WSP 5 and WSP 11.

## FoundUps-Agent Roadmap

### Status Ledger
- ✅ Complete
- 🔄 In Progress
- ⏳ Planned
- ⚠️ Deprecated
- 🧬 LLME Target: [ABC] (Can be used for roadmap items)

### ✅ Proof of Concept (0.0.x) - Target LLME: ~000-111
- [ ] [Task 1]
- [ ] [Task 2]

### 🔄 +Prototype (0.1.x - 0.9.x) - Target LLME: ~110-122
- [ ] [Feature 1]
- [ ] [Feature 2]

### 🔄 [High Priority System Name] - Current LLME: [XYZ], Target LLME: [ABC]
- [ ] [Task 1]
- [ ] [Task 2]

### 🔄 [Medium Priority System Name]
- [ ] [Task 1]
- [ ] [Task 2]

### 🔄 [Lower Priority System Name]
- [ ] [Task 1]
- [ ] [Task 2]

### ⏳ Minimum Viable Product (1.0.x+) - Target LLME: ~112-222
- [ ] [MVP Feature 1]
- [ ] [MVP Feature 2]

#### TODO List *Use `[+todo]` or `[+WSP]` commit convention prefix or add manually here.*
**/[Task Name]** - @[Assignee/Team] - priority: [PriorityScore] (MPS from WSP 5) - LLME Target: [ABC]
- [ ] [Subtask 1]
- [ ] [Subtask 2]

## 🧩 MVP Release Phases

### ⏳ [Phase 1 Name]
- [ ] [Task 1]
- [ ] [Task 2]

### ⏳ [Phase 2 Name]
- [ ] [Task 1]
- [ ] [Task 2]

### 🔄 [Phase 3 Name]
- [ ] [Task 1]
- [ ] [Task 2]

====================================================================
```

## ModLog Entry Format Template (as per WSP 11)

```markdown
====================================================================
## MODLOG - [+UPDATES]:
- Version: [X.Y.Z]
- Date: [YYYY-MM-DD]
- Git Tag: [Associated tag, e.g., vX.Y.Z or clean-vX]
- Description: [Brief description of changes in this version/log entry]
- Notes: [Additional context or considerations]
- Module LLME Updates (If applicable):
  - [module_name] - LLME: [Old ABC] -> [New ABC] ([Rationale for change])
- Features/Fixes/Changes:
  - [ESM Emoji] [Module: Component] - Description of change 1 (Issue #123)
  - [ESM Emoji] [Module: Component] - Description of change 2
  - ...
====================================================================
```

## Version Guide Template

```markdown
====================================================================
## VERSION GUIDE
### Development Phases (Correlated with WSP 9 & LLME Scores - Appendix G):
- #### POC (0.0.x): Initial development and proof of concept
  - Expected LLME Range: 000-111
  - 0.0.1: First working version
  - 0.0.2-0.0.9: POC improvements and fixes
- #### Prototype (0.1.x - 0.9.x): Feature development and testing
  - Expected LLME Range: 110-122
  - 0.1.x: Basic feature set
  - 0.2.x-0.9.x: Feature expansion and refinement
- #### MVP (1.0.x+): Production-ready releases
  - Expected LLME Range: 112-222
  - 1.0.0: First stable release
  - 1.x.x: Production updates and improvements
====================================================================
``` 