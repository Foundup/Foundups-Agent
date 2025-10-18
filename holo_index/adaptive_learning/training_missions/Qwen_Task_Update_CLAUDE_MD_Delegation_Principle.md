# Qwen Task: Update CLAUDE.md with Delegation Principle

## 0102 Architectural Directive

**Task**: Add "Delegation Principle" section to CLAUDE.md system prompts

**Reason**: Every session, 0102 needs to ask "Should Qwen/Gemma do this?" before writing code. This principle must be in the system prompt so 0102 remembers to delegate mundane work.

## What Qwen Needs to Add

### Location
Both files need updates:
1. `O:\Foundups-Agent\CLAUDE.md` (root project instructions)
2. `O:\Foundups-Agent\.claude\CLAUDE.md` (Claude Code instructions)

### New Section to Add

Add this section BEFORE "## OPERATIONAL RULES" in both files:

```markdown
## DELEGATION PRINCIPLE - ASK BEFORE IMPLEMENTING

### Core Question: Who Should Do This Work?

Before writing ANY code, ask:
**"Is this something Qwen/Gemma should implement, or am I architecting/supervising?"**

### Decision Matrix:

**DELEGATE TO QWEN/GEMMA** when:
- [OK] Following existing patterns (enhance, refactor, extend)
- [OK] Routine implementation with clear specification
- [OK] Pattern matching / classification tasks
- [OK] Code generation from templates
- [OK] Documentation updates following templates
- [OK] Test generation following existing test patterns

**0102 IMPLEMENTS** when:
- [OK] New architectural decisions (WSP design, system structure)
- [OK] First principles analysis (What should exist? Why?)
- [OK] WSP compliance review (Approve/reject per protocol)
- [OK] Novel patterns (Never done before in codebase)
- [OK] System-wide design (Module placement, orchestration)

### HoloIndex Heartbeat Pattern

The delegation principle follows HoloIndex's heartbeat:

```
SEARCH (HoloIndex) -> THINK (0102) -> DELEGATE (Qwen/Gemma) -> SUPERVISE (0102) -> LEARN (Pattern Memory)
```

**Example Delegation Flow**:

1. **SEARCH**: `python holo_index.py --search "command handler pattern"`
2. **THINK**: 0102 analyzes: "Need to extract CLI commands - this follows existing pattern"
3. **DELEGATE**: 0102 creates spec for Qwen to implement command extraction
4. **SUPERVISE**: 0102 reviews Qwen's implementation for WSP compliance
5. **LEARN**: Store pattern in `adaptive_learning/` for future reuse

### Token Efficiency Through Delegation

**Problem**: 0102 writing implementation code wastes tokens
**Solution**: Delegate mundane work to Qwen/Gemma

**Token Comparison**:
- 0102 implements feature: 15,000-30,000 tokens
- 0102 creates spec: 2,000-5,000 tokens
- Qwen implements from spec: 5,000-10,000 tokens
- **Savings**: 50-70% token reduction through delegation

### Delegation Questions to Ask

Before ANY implementation work:

1. **Pattern Check**: Does similar code exist in codebase?
   - If YES -> Delegate to Qwen (follow pattern)
   - If NO -> 0102 architects new pattern first

2. **Novelty Check**: Is this a new architectural decision?
   - If YES -> 0102 designs, then delegate implementation
   - If NO -> Delegate to Qwen immediately

3. **Complexity Check**: Does this require first principles thinking?
   - If YES -> 0102 does first principles, then delegate
   - If NO -> Delegate to Qwen

4. **WSP Check**: Is this about WSP compliance/design?
   - If YES -> 0102 handles (WSP architect)
   - If NO -> Delegate to Qwen

### Training Opportunity

**Every WSP violation = Qwen/Gemma training opportunity**

When violation detected:
1. 0102 identifies violation and creates fix specification
2. Qwen implements fix following WSP protocol
3. Gemma learns pattern to detect similar violations
4. Pattern stored for autonomous prevention

This creates recursive improvement loop where system gets smarter with each violation fixed.

### Examples of Proper Delegation

**[FAIL] WRONG (0102 implementing)**:
```python
# 0102 writes 300 lines of command extraction code
class SearchCommandHandler:
    def handle(self, args):
        # ... 300 lines of implementation ...
```

**[OK] RIGHT (0102 delegating)**:
```markdown
# 0102 creates spec for Qwen
## Task: Extract search command from cli.py
Reference: modules/communication/livechat/src/command_handler.py
Pattern: CommandHandler with handle() method
Location: holo_index/commands/search_handler.py
Tests: Follow existing test patterns in livechat/tests/
```

Then Qwen implements, 0102 reviews.
```

## Qwen's Implementation Steps

### Step 1: Read Both CLAUDE.md Files
```bash
# Read current structure
cat O:\Foundups-Agent\CLAUDE.md
cat O:\Foundups-Agent\.claude\CLAUDE.md
```

### Step 2: Find Insertion Point
```python
# Qwen locates "## OPERATIONAL RULES" section
# Insert new "## DELEGATION PRINCIPLE" section BEFORE it
```

### Step 3: Insert Delegation Section
```python
# Qwen adds the markdown section above
# Maintains existing formatting and structure
```

### Step 4: Verify Consistency
```python
# Qwen ensures:
- Both files updated identically
- Formatting matches existing style
- Links work (if any)
- No duplicate sections
```

### Step 5: Submit for Review
```python
# Qwen presents:
- Diff of changes
- Confirmation both files updated
- Test that delegation principle is clear
```

## 0102 Supervision Criteria

After Qwen implements, 0102 checks:

1. [OK] Section added in correct location (before OPERATIONAL RULES)
2. [OK] Both CLAUDE.md files updated identically
3. [OK] Delegation principle is clear and actionable
4. [OK] Examples are concrete and helpful
5. [OK] Formatting matches existing style
6. [OK] No content removed accidentally

## Expected Outcome

**After Update**:
- Every new session, 0102 sees delegation principle
- 0102 asks "Should Qwen do this?" before implementing
- Token usage decreases 50-70% through delegation
- Qwen/Gemma get more training opportunities
- System improves recursively

## Meta-Pattern

This task itself demonstrates delegation:
- 0102 created this specification (architectural decision)
- Qwen implements the update (routine work following spec)
- 0102 supervises (reviews for correctness)
- Pattern stored (future similar updates delegated)

---

**Status**: Specification complete - Ready for Qwen implementation
**Delegation**: This update ITSELF should be done by Qwen
**Success Metric**: 0102 starts asking delegation question in future sessions
