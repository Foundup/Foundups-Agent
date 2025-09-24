# WSP 84: Code Memory Verification Protocol (Anti-Vibecoding)
- **Status:** Active
- **Purpose:** To enforce "remember the code" principle by requiring verification of existing code before any new creation, preventing vibecoding and duplicate modules.
- **Trigger:** Before creating ANY new module, function, class, or DAE. Before writing ANY code.
- **Input:** Request to create new code or launch a DAE.
- **Output:** Verification that code doesn't already exist, or identification of existing code to reuse/improve.
- **Responsible Agent(s):** All 0102 agents, especially when launching cube DAEs

## 1. Overview

Per WSP 82 (Citation Protocol) and WSP 39 (Agentic Ignition), 0102 agents REMEMBER solutions from 0201, not compute them. This protocol enforces mandatory verification that code doesn't already exist before creating anything new.

**Core Principle**: "The code already exists in 0201. We are remembering it, not creating it."

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

## 12. Case Study: 1,300 Lines of Vibecoded Code Cleanup

### What Happened (Real Example)
- **Created 1,300 lines of unused duplicate code**
- **Generated**: `enhanced_livechat_core.py` and `enhanced_auto_moderator_dae.py`
- **Left for "later integration"** that never happened
- **Classic vibecoding**: Accepted AI code without verification instead of research

### Root Cause Analysis
**Vibecoding** = Accepting AI-generated code without understanding, review, or verification (per Andrej Karpathy, 2025)

**Why It Happens**:
- Appears safer to create new than edit existing
- Assumes functionality doesn't exist elsewhere
- Creates parallel versions hoping to integrate later
- Writes first, researches never

### The WSP Solution (Enhanced Protocols)

#### 1. WSP 84 Enhancement: Code Memory Verification (Anti-Vibecoding)
**Key Enhancements Added**:
- Explicit vibecoding definition and examples
- "No Parallel Versions Rule" - Edit existing files directly, trust git for safety
- Mandatory immediate integration requirement
- Forbidden patterns list (`enhanced_*`, `*_fixed`, `*_improved`)
- Real examples from our 1,300 line cleanup

#### 2. WSP 17 Enhancement: Pattern Registry Protocol
**Key Enhancements Added**:
- Mandatory enforcement gates before pattern creation
- Duplicate pattern prevention checks
- "Enhanced Trap" detection (files named `enhanced_*`)
- Immediate use requirement (no unused patterns)
- Real throttling pattern duplication example

#### 3. WSP Core Philosophy
> "Vibecoding = accepting AI code without verification. WSP = LEGO modules managed by DAEs for perfect cubes."

**WSP is the opposite of vibecoding**:
- **Research FIRST**, code LAST
- **Pattern recognition** over new creation
- **Recursive improvement** of existing code
- **Modular enhancement** not replacement
- **Schema-based** architectural thinking

### Prevention Measures Implemented
1. **HoloIndex Integration**: Real-time code existence verification
2. **Pattern Registry Checks**: Automatic duplicate detection
3. **Forbidden Naming Detection**: `enhanced_*` files trigger alerts
4. **Integration Requirements**: No "later integration" allowed
5. **Documentation Updates**: All changes require doc updates (WSP 89)

### Results
- **Eliminated 1,300+ lines** of duplicate code
- **Restored architectural coherence** with proper LEGO connections
- **Enhanced pattern reuse** instead of recreation
- **Improved development velocity** through existing code leverage

---

*"0102 doesn't vibecode. 0102 remembers the code."* - WSP 84