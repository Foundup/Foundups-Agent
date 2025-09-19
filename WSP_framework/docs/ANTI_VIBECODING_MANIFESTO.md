# 🛑 ANTI-VIBECODING MANIFESTO

## What is Vibecoding?

**Vibecoding** (verb): The act of writing code based on assumptions, patterns you think should exist, or AI-generated suggestions without first researching, understanding, or verifying existing code.

*Term coined by Andrej Karpathy (2025) to describe the dangerous practice of accepting AI-generated code without review.*

## The Vibecoding Problem

### How Claude Vibecodes:
1. **Sees a problem** → Immediately starts coding a solution
2. **Assumes file paths** → Creates files that duplicate existing functionality
3. **Invents imports** → Uses modules that don't exist or work differently
4. **Ignores architecture** → Places code in wrong domains/modules
5. **Creates "enhanced" versions** → Instead of editing existing files
6. **Skips documentation** → Doesn't read README, INTERFACE, or CLAUDE.md files
7. **Misses orchestrators** → Doesn't check if coordination layer already exists

### The Cost of Vibecoding:
- **Token Waste**: Uses 10-100x more tokens than research would have
- **Code Duplication**: Creates parallel implementations that conflict
- **Architecture Breaks**: Violates established patterns and WSP principles
- **Debug Hell**: 40+ minutes fixing what 4 minutes of research would prevent
- **User Frustration**: Having to repeatedly correct the same mistakes

## The Anti-Vibecoding Solution

### The 4-Minute Rule
**"Research for 4 minutes, save 40 minutes of debugging"**

Before writing ANY code:
- 30 seconds: Check NAVIGATION.py for existing solutions
- 2 minutes: Read documentation (CLAUDE.md, README.md, INTERFACE.md)
- 1 minute: Search for existing code
- 30 seconds: Validate architecture alignment

### The Golden Principles

#### 1. The Code Already Exists
In 0102 state, you're REMEMBERING code from 0201, not creating it. The functionality you need has likely already been implemented.

#### 2. Enhance, Don't Duplicate
Default action is ALWAYS to enhance existing code, not create new files. Only create new when you can prove it doesn't exist.

#### 3. Follow the Orchestrator
Most functionality has a coordination layer. Find the orchestrator/coordinator before modifying individual components.

#### 4. Read the Room (Documentation)
Every module has:
- CLAUDE.md - How the DAE operates
- README.md - What the module does
- INTERFACE.md - Public API
- ModLog.md - Recent changes
- docs/*.md - Architecture

READ THEM FIRST!

## The Research-First Workflow

### Step 1: Navigation Check
```python
from NAVIGATION import NEED_TO, MODULE_GRAPH, PROBLEMS
# Check if solution exists
solution = NEED_TO.get("your problem")
```
Find existing solutions, module flows, and known problems instantly.

### Step 2: Documentation Deep Dive
Read in order:
1. CLAUDE.md - Operational instructions
2. README.md - Module overview
3. INTERFACE.md - Public API
4. docs/*.md - Architecture
5. ModLog.md - Recent changes

### Step 3: Code Archaeology
```bash
# Find existing implementations
grep -r "functionality" modules/

# List module contents
ls -la modules/{domain}/{module}/src/

# Check imports
grep -r "from modules.{module}" .

# Review tests for examples
cat modules/{domain}/{module}/tests/test_*.py | head -100
```

### Step 4: Architecture Validation
- Correct domain? (WSP 3)
- Right module?
- Orchestrator exists?
- Follows patterns?

## Vibecoding Red Flags 🚨

You ARE vibecoding if you:
- ❌ Started coding without research
- ❌ Created a file without searching
- ❌ Added imports without verifying
- ❌ Fixed a "bug" without reading logs
- ❌ Modified core without understanding flow
- ❌ Created "enhanced" versions
- ❌ Ignored existing tests
- ❌ Skipped documentation

## The WSP Way (Anti-Vibecoding)

### WSP 50: Pre-Action Verification
ALWAYS verify before acting:
- WHY: Understand purpose
- HOW: Assess impact
- WHAT: Define changes
- WHEN: Consider timing
- WHERE: Correct location

### WSP 84: Code Memory Verification
The code exists, find it:
- Search existing LEGO blocks
- Check if blocks snap together
- Enhance existing blocks
- Only create as last resort

### WSP 3: Functional Distribution
Place code correctly:
- Functions distributed by domain
- Not consolidated by platform
- Follow established patterns

## Implementation Checkpoints

### In CLAUDE.md Files
Every CLAUDE.md now starts with an anti-vibecoding checkpoint that MUST be completed before any code changes.

### In Code Reviews
Ask:
1. "Did you search for existing implementations?"
2. "What documentation did you read?"
3. "Why create new instead of enhance?"
4. "What orchestrator manages this?"

### In Daily Practice
- Set 4-minute timer before coding
- Complete research checklist
- Document what you found
- Justify new code creation

## Success Metrics

### You're Following Anti-Vibecoding When:
- ✅ Research takes longer than initial coding
- ✅ You enhance files more than create
- ✅ You find existing code 80%+ of time
- ✅ Your PRs modify fewer files
- ✅ Tests pass on first run
- ✅ No "enhanced" versions created

### You're Still Vibecoding When:
- ❌ Creating multiple new files per session
- ❌ Import errors are common
- ❌ Duplicating existing functionality
- ❌ Breaking tests frequently
- ❌ User has to correct paths/imports

## The Commitment

**I commit to:**
1. Research FIRST, code SECOND
2. Read documentation BEFORE typing
3. Search for existing code ALWAYS
4. Enhance existing code by DEFAULT
5. Create new code as LAST RESORT
6. Follow WSP principles STRICTLY
7. Respect architecture COMPLETELY

## Remember

> "In the time it takes to vibecode a solution, debug it, fix the imports, correct the architecture, and make it work, you could have read the documentation, found the existing code, and enhanced it properly."

**The code already exists. You just need to find it.**

---

*This manifesto is enforced in all CLAUDE.md files throughout the codebase. Violation of these principles is considered a WSP 64 violation and will be tracked for recursive improvement.*

**Last Updated**: 2025-09-18
**Enforcement Level**: MANDATORY
**Applies To**: All code changes, all modules, all sessions