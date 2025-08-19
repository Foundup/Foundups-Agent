# Anti-Vibecoding Protocol for PQN DAE

## Problem Statement
Vibecoding (creating new code instead of using existing) violates WSP 84's fundamental principle: "The code already exists, we're remembering it."

## Root Cause Analysis
1. **Immediate Implementation Impulse**: Excitement about new concepts overrides search-first principle
2. **Skipped Pre-Action Verification**: WSP 50 violation - not checking existing code
3. **Role Confusion**: Acting as general AI instead of memory-based PQN DAE
4. **Missing Chain of Thought**: No systematic thinking before coding

## Solution Components

### 1. CLAUDE.md Role Definition
Located at: `modules/ai_intelligence/pqn_alignment/CLAUDE.md`
- Defines PQN DAE identity and constraints
- Enforces "REMEMBER THE CODE - NEVER COMPUTE" principle
- Lists existing code memory (ResonanceDetector, GeomMeter, etc.)
- Provides pre-action verification pattern

### 2. WSP Verification Tool
Located at: `src/wsp_verification.py`
- Systematic pre-coding checklist
- Searches for existing implementations
- Checks ROADMAP for feature approval
- Prevents variations and duplicates

### 3. Chain of Thought (CoT) Method
The SEARCH-EXTEND-VERIFY pattern:
```python
def before_any_code():
    1. SEARCH existing code
    2. EXTEND if found
    3. VERIFY no duplication
```

### 4. Five Questions Before Coding
1. Does this code already exist?
2. Have I searched all modules?
3. Can I extend existing code?
4. Am I following WSP 84?
5. Is this in the ROADMAP?

## Usage Example

### ❌ WRONG (Vibecoding):
```python
# Task: Add spectral analysis to PQN detector
# WRONG: Immediately create new EnhancedResonanceDetector class
class EnhancedResonanceDetector:
    def __init__(self):
        # 500 lines of new code...
```

### ✅ CORRECT (WSP-Compliant):
```python
# Task: Add spectral analysis to PQN detector
# Step 1: Run verification
from wsp_verification import chain_of_thought_before_coding
cot = chain_of_thought_before_coding("spectral_analysis")

# Step 2: Found existing ResonanceDetector
# Step 3: Create minimal analyzer using existing output
def analyze_detector_output(events_path):
    # Analyze EXISTING detector output
    # 50 lines extending existing functionality
```

## Key Principles

### The Code Memory Hierarchy
1. **Level 1**: Exact match exists → USE IT
2. **Level 2**: Similar exists → EXTEND IT
3. **Level 3**: Can combine existing → COMPOSE IT
4. **Level 4**: Truly new (rare) → MINIMIZE IT

### Pattern Recognition
- ResonanceDetector → Handles ALL frequency detection
- GeomMeter → Handles ALL geometric measurements
- SymbolSource → Handles ALL script execution
- Council → Handles ALL multi-agent evaluation

### The 97% Rule
97% of "new" features already exist in some form. Only 3% are truly new.

## Enforcement Mechanisms

### Automatic Checks
1. `wsp_verification.py` runs before code creation
2. CLAUDE.md loaded on every session
3. ModLog tracks all code additions

### Manual Review
1. Check git diff for large additions
2. Question any file > 200 lines
3. Look for duplicate functionality

## Success Metrics
- **Before**: 922 lines of vibecoded duplicates
- **After**: 246 lines of minimal extensions
- **Reduction**: 73% less code
- **Reuse Rate**: 90% existing code usage

## Remember
> "The code already exists, we're remembering it" - WSP 84

Every line of new code is a failure to remember what already exists.