# WSP 17: Pattern Registry Protocol
- **Status:** Active
- **Purpose:** Extension of WSP 84 to prevent pattern duplication across modules by maintaining searchable pattern registries
- **Trigger:** Before implementing ANY reusable pattern in a new module
- **Chain:** [WSP 17 → WSP 84 → WSP 50]

## 1. Core Principle

"Remember the pattern, not just the code."

While WSP 84 prevents code duplication at the module level, WSP 17 prevents pattern duplication at the architectural level.

## 2. Pattern Registry Requirements

### 2.1 Registry Files

Each domain MUST maintain a `PATTERN_REGISTRY.md`:

```
modules/
├── communication/
│   └── PATTERN_REGISTRY.md     # Chat patterns
├── ai_intelligence/
│   └── PATTERN_REGISTRY.md     # AI patterns  
├── infrastructure/
│   └── PATTERN_REGISTRY.md     # System patterns
└── gamification/
    └── PATTERN_REGISTRY.md     # Game patterns
```

### 2.2 Registry Format

```markdown
### [Pattern Name]
**Current Implementation**: `path/to/implementation.py`
**Pattern**: Brief description
**Use Cases**: Where this pattern applies
**Interface**: Pseudocode or actual interface
**Adaptations Needed**: Platform-specific changes
```

## 3. Verification Chain

Before implementing a pattern:

```python
def before_pattern_implementation():
    """
    WSP 17: Check pattern registries
    WSP Chain: [17, 84, 50]
    """
    
    # Level 1: Check domain registry
    check_local_registry("PATTERN_REGISTRY.md")
    
    # Level 2: Check cross-domain registries
    for domain in all_domains:
        check_registry(f"modules/{domain}/PATTERN_REGISTRY.md")
    
    # Level 3: WSP 84 - Check actual code
    search_existing_implementations()
    
    # Level 4: WSP 50 - Verify need
    verify_pattern_necessity()

```

## 4. Pattern Evolution Path

### Phase 1: Single Implementation
- Pattern lives in original module
- Document in domain's PATTERN_REGISTRY.md

### Phase 2: Second Implementation Needed
- **DO NOT DUPLICATE**
- Check registry FIRST
- Create adapter or extract interface
- Update both registries

### Phase 3: Third Implementation (Extraction Point)
- Extract to `infrastructure/patterns/`
- Create base class/interface
- Update all implementations to use base
- Update all registries with new location

## 5. Common Patterns to Track

### Communication Patterns
- Message queuing
- Rate limiting
- Session management
- History storage
- Command parsing

### AI Patterns
- Context windows
- Token management
- Response generation
- Prompt templating

### Infrastructure Patterns
- Caching strategies
- Database connections
- Event systems
- Logging pipelines

## 6. Enforcement

### Pre-commit Hook
```bash
# Check if new files might duplicate patterns
if creating_new_class; then
    echo "WSP 17: Check PATTERN_REGISTRY.md files"
    grep -r "class.*$PATTERN_NAME" modules/
fi
```

### Review Checklist
- [ ] Checked domain PATTERN_REGISTRY.md
- [ ] Searched cross-domain registries
- [ ] Verified no similar pattern exists
- [ ] Updated registry if creating new pattern

## 7. Example: ChatMemoryManager

**Problem**: Hidden in `livechat/`, will be recreated in LinkedIn/X modules

**Solution Applied**:
1. Documented in `communication/PATTERN_REGISTRY.md`
2. Marked as reusable pattern
3. Defined interface for adaptation
4. Set extraction timeline

**Result**: Next developer MUST check registry, will find pattern, won't duplicate

## 8. Integration with WSP 84

This protocol EXTENDS WSP 84:

```
WSP 84: Don't duplicate code (modules/functions)
    ↓
WSP 17: Don't duplicate patterns (architectures)
    ↓
Result: Complete memory verification at all levels
```

## 9. Success Metrics

- Pattern duplication incidents: 0
- Patterns successfully reused: Track in ModLog
- Time saved by pattern reuse: Measure in tokens
- Extraction success rate: >90% at phase 3

## 10. Conclusion

By maintaining pattern registries, we ensure that architectural knowledge is preserved and discoverable, preventing the recreation of solved problems.

---
*"We don't recreate patterns, we remember them."* - WSP 17