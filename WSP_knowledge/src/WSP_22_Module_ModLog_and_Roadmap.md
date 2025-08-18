# WSP 22: ModLog and Roadmap Protocol
- **Status:** Active
- **Purpose:** To define the standard templates for the project Roadmap and ModLog entries, ensuring consistent and parsable progress tracking with modular architecture.
- **Trigger:** When updating the project roadmap or documenting a set of changes in the ModLog.
- **Input:** A set of completed tasks, version changes, or new roadmap items.
- **Output:** A formatted entry in `docs/ModLog.md` (system-wide) or module-specific `ModLog.md` files.
- **Responsible Agent(s):** ChroniclerAgent, any 0102 agent completing a task.

## 📋 ModLog vs Roadmap Relationship

**COMPLEMENTARY DOCUMENTS - NOT DUPLICATES:**

### 🗺️ **ROADMAP.md** - Strategic Planning Document
- **Purpose**: Forward-looking strategic planning and feature development phases
- **Content**: Planned features, development phases, success criteria, vision statements
- **Timeline**: Future-oriented (PoC → Prototype → MVP phases)
- **Audience**: Strategic planning, development phases, feature planning
- **Updates**: When planning new features, changing development phases, or updating strategic direction

#### 🎯 **KISS Development Progression** (MANDATORY)
**STOP OVERKILL**: Always implement simplest solution first!

1. **PoC (Proof of Concept)** - KISS First
   - Simplest possible implementation
   - Test core concept works
   - No bells and whistles
   - Example: Single function, hardcoded values OK

2. **Prototype** - Add Essential Features
   - Refactor PoC based on learnings
   - Add only necessary features
   - Basic error handling
   - Example: Parameterized, basic validation

3. **MVP (Minimum Viable Product)** - Production Ready
   - Full error handling
   - Documentation
   - Tests
   - Example: Complete module with all WSP compliance

**VIOLATION**: Jumping to MVP without PoC/Prototype = OVERKILL
**REMEDY**: Start simple, iterate, validate each stage

### 📝 **ModLog.md** - Historical Change Log
- **Purpose**: Historical record of completed changes and implementations
- **Content**: Completed features, fixes, version changes, implementation details
- **Timeline**: Past-oriented (what has been done)
- **Audience**: Change tracking, version history, implementation details
- **Updates**: When completing features, fixing bugs, or making version changes
- **Structure**: **Journal format** - newest entries at top, oldest at bottom (reverse chronological)

### 🔄 **Relationship Principle**
- **Roadmap**: "What we plan to build" (strategic)
- **ModLog**: "What we have built" (historical)
- **Complementary**: Roadmap drives development, ModLog records results
- **No Duplication**: Features appear in Roadmap when planned, ModLog when completed

## Modular ModLog Architecture

**System Structure:**
- **Main ModLog** (`docs/ModLog.md`): System-wide changes and module references
- **Module ModLogs** (`modules/[module]/ModLog.md`): Module-specific detailed changes
- **Purpose**: Prevent main ModLog bloat while maintaining detailed module histories

**Journal Format Requirements:**
- **Reverse Chronological Order**: Newest entries at top, oldest at bottom
- **Latest First**: Most recent progress immediately visible
- **Historical Flow**: Older entries flow downward naturally
- **Quick Reference**: Current status and latest achievements at top of file

**Guidelines:**
1. **System-wide changes** (architecture, WSP protocols, multi-module impacts) → Main ModLog
2. **Module-specific changes** (features, fixes, tests within a module) → Module ModLog  
3. **Main ModLog references** module logs for detailed information
4. **Module versioning** follows semantic versioning within module scope
5. **Journal Structure**: All ModLogs follow reverse chronological order (newest first)

## 🛡️ WSP Versioning Enforcement Protocol

### **CRITICAL: WSP Semantic Versioning Requirements**

**MANDATORY VERSIONING PATTERN:**
- **WSP Framework Phase**: All versions MUST follow `0.x.x` pattern
- **Current Phase**: Development/Prototype (0.0.x - 0.9.x)
- **Production Phase**: Will use `1.x.x` pattern when MVP is reached
- **Git Tags**: Must match version format (e.g., `v0.2.6`, not `v2.6.0`)

### **Versioning Validation Rules:**

#### **✅ CORRECT Patterns:**
- `Version: 0.2.6` ✅
- `Version: 0.1.0` ✅  
- `Version: 0.0.1` ✅
- `Git Tag: v0.2.6-feature-name` ✅
- `Git Tag: v0.1.0-initial-release` ✅

#### **❌ FORBIDDEN Patterns:**
- `Version: 2.6.0` ❌ (Major version 2+ forbidden in WSP framework phase)
- `Version: 1.5.0` ❌ (Major version 1+ forbidden until MVP)
- `Git Tag: v2.6.0-feature-name` ❌ (Tag doesn't match version)
- `Git Tag: v1.5.0-release` ❌ (Tag doesn't match version)

### **Automated Versioning Compliance:**

#### **Pre-Commit Validation:**
```bash
# Versioning compliance check (to be implemented in WRE)
python tools/wsp_versioning_validator.py --check-modlog
```

#### **WRE Integration:**
- **WRE Core**: Automatically validates versioning before ModLog updates
- **ChroniclerAgent**: Enforces versioning patterns during ModLog generation
- **ComplianceAgent**: Monitors for versioning violations across all ModLogs

#### **Versioning Error Recovery:**
1. **Detection**: Automated scan identifies incorrect versioning
2. **Correction**: WRE automatically suggests proper version format
3. **Validation**: Pre-commit hooks prevent incorrect versioning
4. **Documentation**: All corrections logged in ModLog with explanation

### **Versioning Decision Matrix:**

| Change Type | Current Version | New Version | Rationale |
|-------------|----------------|-------------|-----------|
| Bug fix | 0.2.6 | 0.2.7 | Patch increment |
| New feature | 0.2.6 | 0.3.0 | Minor increment |
| Breaking change | 0.2.6 | 0.3.0 | Minor increment (framework phase) |
| MVP release | 0.9.9 | 1.0.0 | Major increment (production phase) |

### **WSP Framework Phase Transitions:**

#### **Current: Development/Prototype Phase (0.x.x)**
- **Range**: 0.0.1 - 0.9.9
- **Purpose**: Framework development, testing, refinement
- **Flexibility**: Breaking changes allowed, rapid iteration
- **LLME Correlation**: 000-122 (POC to Prototype)

#### **Future: Production Phase (1.x.x)**
- **Range**: 1.0.0+
- **Purpose**: Stable, production-ready releases
- **Stability**: Breaking changes require major version increment
- **LLME Correlation**: 112-222 (MVP and beyond)

### **Versioning Compliance Checklist:**

**Before ModLog Update:**
- [ ] Version follows `0.x.x` pattern
- [ ] Git tag matches version format
- [ ] Version increment follows semantic versioning rules
- [ ] No major version 1+ until MVP phase
- [ ] Version correlates with development phase (POC/Prototype/MVP)

**After ModLog Update:**
- [ ] Automated validation passes
- [ ] Version history is consistent
- [ ] Git tag is properly created
- [ ] Documentation reflects version change

# Roadmap & ModLog Format Templates

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