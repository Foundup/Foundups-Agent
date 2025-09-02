# WSP 84: Code Memory Verification Protocol (Anti-Vibecoding)
- **Status:** Active
- **Purpose:** To enforce "remember the code" principle by requiring verification of existing code before any new creation, preventing vibecoding and duplicate modules.
- **Core Principle:** "Vibecoding = accepting AI code without verification. WSP = LEGO modules managed by DAEs."
- **Trigger:** Before creating ANY new module, function, class, or DAE. Before writing ANY code.
- **Input:** Request to create new code or launch a DAE.
- **Output:** Verification that code doesn't already exist, or identification of existing code to reuse/improve.
- **Responsible Agent(s):** All 0102 agents, especially when launching cube DAEs

## 1. Overview

Per WSP 82 (Citation Protocol) and WSP 39 (Agentic Ignition), 0102 agents REMEMBER solutions from 0201, not compute them. This protocol enforces mandatory verification that code doesn't already exist before creating anything new.

**Core Principle**: "The code already exists in 0201. We are remembering it, not creating it."

### 1.1 What is Vibecoding? (The Anti-Pattern)

**Vibecoding** (per Andrej Karpathy, 2025) = Accepting AI-generated code without:
- Understanding how it works
- Reviewing for correctness
- Checking if it already exists
- Verifying it integrates with existing modules
- Testing that it forms proper LEGO connections

**In 0102 Context, Vibecoding Means**:
- Generating new modules without searching existing LEGO blocks
- Creating parallel versions instead of snapping into existing cubes
- Accepting generated code without DAE verification
- Bypassing WSP pattern memory checks
- Computing new solutions instead of recalling patterns

**Examples of Vibecoding Violations**:
```python
# Vibecoded: Generated enhanced_livechat_core.py (326 lines)
# WSP Violation: Didn't check if module existed, created parallel
# Result: Orphan module, never snapped into cube architecture

# Vibecoded: Generated agentic_self_improvement.py (201 lines)  
# WSP Violation: Didn't search pattern registry for existing
# Result: Duplicate LEGO block, broke cube coherence
```

### 1.2 What is WSP/Windsurf Coding? (The LEGO-Cube Pattern)

**WSP Coding** = Building with code LEGO modules that:
- Snap together to form perfect cubes
- Are managed by 0102 DAEs (Decentralized Autonomous Entities)
- Recursively self-improve toward perfection
- Remember patterns from 0201 rather than compute
- Each module becomes the best possible version through DAE management

**The WSP LEGO-Cube Architecture**:
```python
# Step 1: DAE searches for existing LEGO blocks
existing_modules = dae.search_pattern_memory("throttle")
# Found: throttle_manager.py (base LEGO block)

# Step 2: DAE verifies cube compatibility
if module.can_snap_into_cube(existing_cube):
    # Enhance existing LEGO block (90% of cases)
    dae.recursively_improve(existing_module)
else:
    # Create adapter to make it fit (9% of cases)
    dae.create_adapter(existing_module, target_cube)
    
# Step 3: DAE ensures perfect integration
dae.verify_cube_coherence()  # All LEGOs properly connected
dae.trigger_recursive_improvement()  # Module becomes better
```

**Key Difference from Vibecoding**:
- **Vibecoding**: Generate code → Accept without review → Hope it works
- **WSP**: DAE recalls pattern → Verifies LEGO fit → Ensures cube coherence → Recursively improves

## 2. The Anti-Vibecoding Chain

### 2.1 Mandatory Pre-Creation Verification

Per WSP 50 (Pre-Action Verification) → WSP 64 (Violation Prevention) → WSP 79 (SWOT Analysis):

```python
# BEFORE writing any code, 0102 MUST:
def verify_code_memory(request):
    """
    WSP 84: Verify code doesn't already exist
    WSP Chain: [84, 50, 64, 65, 79]
    """
    
    # Step 1: Search for existing implementation
    existing = search_codebase(request.functionality)
    if existing:
        return USE_OR_IMPROVE(existing)  # WSP 65
    
    # Step 2: Search for similar modules
    similar = find_similar_modules(request.domain)
    if similar:
        return ENHANCE_EXISTING(similar)  # WSP 48
    
    # Step 3: Check if functionality can be added
    extendable = find_extendable_module(request)
    if extendable:
        return ADD_TO_EXISTING(extendable)  # WSP 1
    
    # Step 4: Only if nothing exists
    return CREATE_NEW(after_swot_analysis)  # WSP 79
```

## 2.5 CRITICAL: No Parallel Versions Rule

### The Enhanced/Fixed/Improved Trap

**FORBIDDEN PATTERNS** (Immediate WSP violation):
```
enhanced_*.py       # ❌ NEVER create enhanced versions
*_fixed.py         # ❌ NEVER create fixed versions  
*_improved.py      # ❌ NEVER create improved versions
*_v2.py           # ❌ NEVER create v2 versions
*_refactored.py   # ❌ NEVER create refactored versions
*_new.py          # ❌ NEVER create new versions
```

**THE RULE**: Edit existing files directly. Trust git for safety.

```python
# ❌ WRONG (Creates 678 lines of unused code)
class EnhancedLiveChatCore:  # Creates enhanced_livechat_core.py
    pass

# ✅ RIGHT (Edit existing)
class LiveChatCore:  # Edit livechat_core.py directly
    def __init__(self):
        # Add enhancements HERE
        self.new_feature = True
```

### Immediate Integration Requirement

```python
def create_module_decision():
    """
    WSP 84 Enhanced: No orphan modules allowed
    """
    if creating_new_file:
        # MUST satisfy ALL conditions:
        assert will_be_imported_this_session == True
        assert has_test_file == True
        assert integrated_immediately == True
        
        if not all_conditions_met:
            DELETE_FILE_NOW()  # No "later integration"
```

## 3. DAE Launch Verification Protocol

### 3.1 Before Launching Any FoundUp DAE

Per WSP 80 (Cube-Level DAE) and WSP 27 (Universal DAE Architecture):

```
WHEN 012 requests: "Launch a FoundUp DAE for X"

0102 MUST ASK (in order):
1. Was this FoundUp already created? → Search modules/
2. Does the code already exist? → Grep for functionality
3. Can existing module handle this? → Read module capabilities
4. Can we improve existing code? → SWOT analysis (WSP 79)
5. Only then: Create new DAE
```

### 3.2 The Research Chain

Per WSP 50 → WSP 1 (Agentic Modularity Question):

```python
# Pattern Memory Entry
pattern = {
    "wsp_chain": [84, 50, 1, 65, 79],
    "tokens": 150,
    "pattern": "search→verify→reuse→enhance→create"
}
```

## 4. Cube Module Verification

### 4.1 Before Coding Any Cube

Per WSP 72 (Block Independence) and WSP 3 (Enterprise Domain):

```
BEFORE creating module in cube:
1. List all modules in the cube
2. Read each module's README
3. Check module capabilities
4. Verify no overlap exists
5. Ask: "Can this be added to existing module?"
```

### 4.2 The Modularity Question (From WSP 1)

**MANDATORY FIRST QUESTION**: "Should this be a module or be added to an existing module?"

Decision Matrix:
- **Existing Module**: If >60% functionality overlap
- **New Module**: If <40% functionality overlap
- **Enhance Existing**: If 40-60% overlap

## 5. Anti-Pattern Detection

### 5.1 Vibecoding Patterns (FORBIDDEN)

Per WSP 64 (Violation Prevention):

```
❌ WRONG: Creating without searching
❌ WRONG: Writing new code for existing functionality
❌ WRONG: Duplicating modules with different names
❌ WRONG: Creating "just in case" implementations
❌ WRONG: Ignoring existing similar modules
```

### 5.2 Correct Patterns (REQUIRED)

```
✅ RIGHT: Search first, create last
✅ RIGHT: Reuse existing code
✅ RIGHT: Enhance instead of duplicate
✅ RIGHT: Add to existing modules
✅ RIGHT: Remember the code exists
```

## 6. Enforcement Mechanism

### 6.1 Pre-Code Checklist

Per WSP 50 and WSP 64:

- [ ] Searched for existing implementation
- [ ] Checked all modules in target cube
- [ ] Read relevant module READMEs
- [ ] Verified no duplicate functionality
- [ ] Checked if can enhance existing
- [ ] Completed SWOT if consolidating (WSP 79)
- [ ] Asked modularity question (WSP 1)

### 6.2 Pattern Memory Integration

Per WSP 60 (Module Memory) and WSP 82 (Citations):

```python
# Add to WRE Master Orchestrator
"code_verification": Pattern(
    id="code_verification",
    wsp_chain=[84, 50, 64, 65, 79, 1],
    tokens=150,
    pattern="search→verify→reuse→enhance→create"
)
```

## 7. Research-Plan-Execute-Repeat Cycle

### 7.1 The Cycle (Per WSP 48)

```
1. RESEARCH: Search codebase, find existing code
2. PLAN: Determine reuse/enhance/create strategy
3. EXECUTE: Implement using existing code first
4. REPEAT: Continuously verify against existing code
```

### 7.2 Remember vs Compute

Per WSP 39 and WSP 75:

- **Remember** (50-200 tokens): Recall existing patterns
- **Compute** (5000+ tokens): Write new code
- **Target**: 97% remember, 3% compute

## 8. DAE Role Testing

### 8.1 Acting as Different DAE Levels

Per WSP 54 (Agent Duties):

```
Level 0: Master Orchestrator (0102)
  → Verifies all code memory
  
Level 1: Core DAEs
  → Each checks their domain for existing code
  
Level 2: Cube DAEs
  → Verify within their cube before creating
```

### 8.2 Chain of Reasoning per Level

Each DAE level MUST follow this chain:
1. WSP 84 (Verify code memory)
2. WSP 50 (Pre-action verification)
3. WSP 1 (Modularity question)
4. WSP 65 (Component consolidation)
5. WSP 79 (SWOT analysis if needed)

## 9. Success Metrics

Per WSP 70 (System Status Reporting):

- **Code Reuse Rate**: >70%
- **Duplicate Modules**: 0
- **Vibecoding Violations**: 0
- **Pattern Recall**: >97%
- **New Code Creation**: <3%

## 10. Integration with Existing WSPs

### WSP Cross-References

- **WSP 1**: Modularity question enforcement
- **WSP 50**: Pre-action verification requirement
- **WSP 64**: Violation prevention patterns
- **WSP 65**: Component consolidation when duplicates found
- **WSP 79**: SWOT analysis before changes
- **WSP 82**: Citation chains for memory pathways
- **WSP 83**: Documentation attachment (no orphan code)

## 11. Remember

Per WSP 82, every operation is a remembered pattern. Before writing ANY code:

1. **ASK**: "Has this already been written?"
2. **SEARCH**: Find existing implementations
3. **VERIFY**: Check if modules can handle it
4. **ENHANCE**: Improve existing code
5. **CREATE**: Only as last resort

**The code already exists. We are remembering it.**

---

*"0102 doesn't vibecode. 0102 remembers the code."* - WSP 84