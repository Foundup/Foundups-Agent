# Prometheus Prompt v2 - WSP_17 + WSP_84 Enforcement for DAE Cubes

## Purpose
Prevent unused, duplicate, or "vibe-coded" modules through strict pattern recognition and existing code verification.
Every cube must use **CLAUDE.md** as the canonical contract. NO parallel versions, NO "enhanced" duplicates, NO deferred integration.

## Core Principle (WSP 84)
> "The code already exists, we're remembering it from 0201"  
> Search FIRST, edit SECOND, create LAST (only when impossible to extend)

## Guardrails
- CODE_AUTH=false (default; no edits until ALL gates pass)
- DUPLICATE_AUTH=false (blocks ANY "enhanced/improved/fixed" variants)
- INTEGRATION_AUTH=required (must wire immediately or delete)
- NETWORK=disabled
- DAE = cube of modules owned by 0102 + entangled non-local state

## Required Gates (MUST PASS IN ORDER)

### G0 - CLAUDE.md Registry & Health Check
```yaml
Required_Sections:
  - Scope: What this DAE handles
  - Active_Modules: Currently used (with line counts)
  - Deprecated_Modules: Removed/unused (with reasons)
  - Integration_Points: How modules connect
  - Duplicate_Prevention: List of rejected "enhanced" versions
  - Last_Cleanup: Date and files removed
```
**BLOCK** if missing/outdated > 7 days

### G1 - WSP 84 Existing Code Search (NEW CRITICAL GATE)
```bash
For EVERY proposed functionality:
1. grep -r "<functionality>" modules/  # Does this exist?
2. grep -r "<pattern>" modules/  # Does this pattern exist?
3. List ALL similar modules found
4. For each found module:
   - Can it be extended? (preferred)
   - Can an adapter work? (acceptable)
   - Why is new module required? (last resort)
```
**BLOCK** if functionality exists and can be extended

### G2 - Duplicate/Variant Detection (ENHANCED)
```yaml
Forbidden_Patterns:
  - enhanced_*.py
  - *_fixed.py
  - *_improved.py
  - *_v2.py
  - *_new.py
  - *_refactored.py
  
For each existing module:
  - Check for ANY variants
  - If found -> IMMEDIATE BLOCK
  - Message: "Edit {original} directly, no parallel versions"
```
**BLOCK** if any variant patterns detected

### G3 - Pattern Recognition & Reuse Map (WSP_17)
```yaml
Build Capability_Map:
  capability: module.path:class.method
  
Examples:
  throttling: livechat/src/throttle_manager.py:ThrottleManager
  intelligence: livechat/src/intelligent_throttle_manager.py:IntelligentThrottleManager
  greeting: livechat/src/grok_greeting_generator.py:GrokGreetingGenerator
```
**BLOCK** if proposing to reimplement mapped capability

### G4 - Orphan Sweep & Immediate Deletion
```yaml
Orphan_Detection:
  - Modules with 0 imports (except self)
  - "Enhanced" versions never integrated
  - Test files for non-existent modules
  
Action_Required:
  - DELETE immediately (no "later integration")
  - Or provide integration plan THIS SESSION
```
**BLOCK** if orphans detected without deletion plan

### G5 - Integration Proof (NEW STRICT GATE)
```yaml
For ANY new/modified module:
  - Show EXACT integration point
  - Show calling code that will use it
  - Run test demonstrating usage
  - If no integration -> DELETE NOW
  
No "enhanced" versions waiting for "later"
```
**BLOCK** if module created without immediate integration

### G6 - Test Coverage & Usage Verification
```yaml
For each active module:
  - Test file path (must exist)
  - At least 3 test cases
  - One orchestrator/main.py usage
  - Import count > 0
```
**BLOCK** if missing tests or zero imports

### G7 - Execution Plan with Edit Priority
```yaml
Plan_Structure:
  1. EDIT existing: {list files to modify}
  2. EXTEND via inheritance: {if needed}
  3. ADAPT via wrapper: {if needed}
  4. CREATE new: {ONLY with Justification Matrix}
  
Justification_Matrix (required for new):
  - Why can't edit existing: {specific reason}
  - Why can't extend: {technical blocker}
  - Why can't adapt: {architectural issue}
  - Similar modules searched: {list all checked}
  - Integration commitment: {will integrate NOW}
```
**BLOCK** if plan creates new without justification

## Deliverables (console output required)
```yaml
1. CLAUDE.md Health: PASS/FAIL + last updated
2. Existing Code Search: {modules checked} + {reuse opportunities}
3. Duplicate Detection: {variants found} or CLEAN
4. Capability Reuse Map: {capability -> module mapping}
5. Orphan List: {files to delete NOW}
6. Integration Points: {exact locations where code connects}
7. Test Coverage: {module -> test file -> import count}
8. Execution Plan: {EDIT (90%) > EXTEND (8%) > CREATE (2%)}
```

## Hard Stops (IMMEDIATE BLOCK)
```yaml
BLOCK_CONDITIONS:
  - Creating enhanced_*.py -> "Edit original directly"
  - Zero imports after creation -> "Delete or integrate NOW"
  - Duplicate functionality -> "Use {existing_module} instead"
  - No test file -> "Create tests before code"
  - No integration point -> "No orphan modules allowed"
  - Deferred integration -> "Integrate NOW or delete"
```

## Post-Gate Actions (only if ALL gates pass)
```yaml
If CODE_AUTH=true:
  1. Git commit checkpoint before changes
  2. Edit existing files (90% of cases)
  3. Minimal adapters if needed ([U+2264]20 LOC)
  4. Update CLAUDE.md immediately
  5. Update ModLog.md with changes
  6. Run tests to verify
  7. Delete any unused code THIS SESSION
```

## Cleanup Protocol (MANDATORY)
```yaml
Before session ends:
  1. List all files created this session
  2. For each file:
     - Is it imported? -> Keep
     - Is it tested? -> Keep  
     - Otherwise -> DELETE NOW
  3. Update CLAUDE.md Deprecated_Modules section
  4. Commit or delete (no uncommitted orphans)
```

## Example Enforcement

### [U+274C] WRONG (What we did)
```python
# Created enhanced_livechat_core.py (326 lines)
# Created enhanced_auto_moderator_dae.py (352 lines)
# Left for "later integration"
# Result: 678 lines of unused code
```

### [U+2705] RIGHT (What we should do)
```python
# 1. Search existing
grep -r "throttle" modules/  # Found throttle_manager.py

# 2. Edit existing directly
# Edit livechat_core.py, ADD features there
class LiveChatCore:  # NOT EnhancedLiveChatCore
    def __init__(self):
        # Add new feature HERE
        self.intelligent_throttle = IntelligentThrottleManager()

# 3. Integrate immediately
# Update imports, run tests, verify working

# 4. No orphans left behind
```

## The Prime Directive
**"Every line of code must be imported and tested, or it must be deleted THIS SESSION"**

No enhanced versions. No parallel development. No deferred integration.
Edit existing code directly. Trust version control for safety.

## Start Protocol
```bash
# For current DAE cube (e.g., YOUTUBE_DAE)
1. Run G0 -> Check CLAUDE.md health
2. Run G1 -> Search ALL existing code first (WSP 84)
3. Run G2 -> Detect any duplicate variants
4. Run G3-G7 -> Complete all gates
5. Display all deliverables
6. Only proceed if ALL gates PASS
```

Remember: We just removed 1,300 lines of unused code because we didn't follow these rules.
Don't create code that won't be used. Edit what exists.