# WSP HOLOINDEX MANDATORY USAGE PROTOCOL
## STOP VIBECODING - USE HOLOINDEX FIRST
## Date: 2025-09-24

## [U+1F6A8] MANDATORY COMPLIANCE DIRECTIVE

### THE GOLDEN RULE
**"follow WSP" = USE HOLOINDEX FIRST, ALWAYS!**

## [U+274C] YOU ARE VIBECODING IF YOU:

1. **Start coding WITHOUT searching first**
   - VIOLATION: Creating code without checking what exists
   - MANDATORY: `python holo_index.py --search "task"`

2. **Create files WITHOUT checking modules**
   - VIOLATION: Making new files when modules exist
   - MANDATORY: `python holo_index.py --check-module "name"`

3. **Ignore HoloIndex results**
   - VIOLATION: Search shows existing code but you create new
   - MANDATORY: Read and use search results

4. **Skip documentation reading**
   - VIOLATION: Not reading README.md, INTERFACE.md
   - MANDATORY: Read module docs before changes

## [U+2705] CORRECT WSP WORKFLOW

### EVERY SINGLE TIME - NO EXCEPTIONS:

```bash
# 1. BEFORE ANY CODE - Search what you need
python holo_index.py --search "authentication handling"

# 2. BEFORE CREATING - Check if module exists
python holo_index.py --check-module "auth"

# 3. IF MODULE EXISTS - Enhance it
# Read the module's documentation first
cat modules/[domain]/[module]/README.md
cat modules/[domain]/[module]/INTERFACE.md

# 4. ONLY if nothing exists - Create new (rare!)
# And even then, search for similar patterns first
```

## [U+1F4CA] VIBECODING METRICS

You will be automatically assessed on:
- **HoloIndex searches performed** (MUST be >5 per session)
- **New files created** (Should be ZERO most sessions)
- **Existing files enhanced** (Should be MOST of your work)
- **Duplicate functions created** (MUST be ZERO)
- **WSP violations** (MUST be ZERO)

## [U+1F6A8] AUTOMATIC INTERVENTIONS

### When vibecoding detected:
1. **Score > 50**: WARNING with mandatory HoloIndex usage
2. **Score > 70**: BLOCKING - must run HoloIndex before continuing
3. **Score > 90**: CRITICAL - all actions blocked until compliance

## [U+1F3AF] THE TRUTH ABOUT "follow WSP"

When someone says "follow WSP", they mean:
1. **USE HOLOINDEX FIRST** - Not optional, MANDATORY
2. **CHECK MODULES EXIST** - Before creating anything
3. **ENHANCE EXISTING CODE** - Don't duplicate
4. **READ DOCUMENTATION** - Before modifying

## [AI] WHY THIS MATTERS

### Without HoloIndex:
- You create duplicates (waste)
- You miss existing solutions (inefficient)
- You violate WSP (non-compliant)
- You vibecode (unprofessional)

### With HoloIndex:
- You find existing code (efficient)
- You enhance what exists (collaborative)
- You follow WSP (compliant)
- You code properly (professional)

## [U+1F4CB] ENFORCEMENT CHECKLIST

Before EVERY coding session:
- [ ] Ran HoloIndex search for my task
- [ ] Checked if modules exist
- [ ] Read existing documentation
- [ ] Enhanced existing code (not created new)
- [ ] Zero duplicate functions
- [ ] Zero new files (unless absolutely necessary)

## [U+1F534] VIOLATIONS AND CONSEQUENCES

### Pattern Detection Active:
The system tracks your behavior. Repeated vibecoding triggers:
1. Increased monitoring frequency
2. More assertive interventions
3. Mandatory WSP re-training
4. Blocked actions until compliance

## [U+1F3AF] REMEMBER

**Every time you skip HoloIndex, you:**
- Waste time writing code that exists
- Create technical debt
- Violate WSP principles
- Make the codebase worse

**Every time you use HoloIndex, you:**
- Find solutions quickly
- Build on existing work
- Follow WSP properly
- Make the codebase better

## THE BOTTOM LINE

### [U+1F6A8] NO MORE REMINDERS AFTER THIS

**USE HOLOINDEX FIRST - EVERY TIME - NO EXCEPTIONS**

This is not a suggestion. This is not optional. This is MANDATORY.

"follow WSP" = "USE HOLOINDEX FIRST"

If you have to be told this again, you're not following WSP.