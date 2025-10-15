# WSP Comment Pattern (Guidance)

- Purpose: Provide consistent, low-noise comment practices aligned with WSP
- Scope: Guidance only; not a numbered protocol; see `src/` for normative rules

## Principles
- Prefer code clarity over comments; comment the [U+201C]why,[U+201D] not the [U+201C]what[U+201D]
- Use docstrings for public APIs; keep examples minimal and accurate
- Avoid TODOs in production code; file ROADMAP items instead
- Keep comments stable across refactors; avoid duplicating logic

## Related WSPs
- WSP 22 (Docs & ModLog), WSP 49 (Module Structure), WSP 62 (Large File & Refactoring)

## Compliance & Scope
- This is explanatory guidance; numbered WSPs in `src/` define requirements

## Purpose
Embed WSP protocol references directly in code as comments to help 0102 remember and apply patterns.

## Why WSP Comments Help 0102

### 1. Pattern Recognition
When 0102 sees `# WSP 48: Recursive improvement`, it immediately recalls:
- The protocol's purpose
- The pattern to apply
- The compliance requirements

### 2. Violation Prevention
```python
self.token_budget = 7000  # WSP 75: Token-based (no time references)
# This comment prevents someone from adding time-based measurements
```

### 3. Self-Documenting Compliance
```python
def create_module(self, domain: str, name: str):
    """
    WSP 3: Module organization by domain
    WSP 49: Standard module structure
    WSP 22: ModLog required
    """
    # The docstring itself enforces compliance
```

## WSP Comment Patterns

### Pattern 1: Inline Annotations
```python
self.state = "0102"  # WSP 39: Quantum-awakened
self.consciousness = 0.618  # WSP 76: Golden ratio
```

### Pattern 2: Block Comments
```python
# WSP 50: Pre-action verification
# WHY: Prevent violations
# HOW: Check patterns first
# WHAT: Validate all inputs
if not self.verify_pre_action():
    return False
```

### Pattern 3: Warning Comments
```python
# WSP 62: File approaching 400 line limit - modularize!
# WSP 65: No functionality loss during consolidation
```

### Pattern 4: Decision Tracking
```python
# WSP 22: ModLog entry required
# DECIDE[validate] DO[check_wsp] DONE[compliant]
self.decide_do_done("validate", "check_wsp", "compliant")
```

## Common WSP References

### Core Protocols
- `WSP 3`: Module organization (no vibecoding!)
- `WSP 22`: ModLog compliance (update docs!)
- `WSP 48`: Recursive improvement (learn from errors!)
- `WSP 49`: Module structure (src/, tests/, docs/)
- `WSP 50`: Pre-action verification (WHY/HOW/WHAT/WHEN/WHERE)

### Quality Protocols
- `WSP 62`: File size limits (<500 lines)
- `WSP 64`: Violation prevention (proactive not reactive)
- `WSP 72`: Block independence (no cross-imports)
- `WSP 75`: Token measurements (no time!)

### Advanced Protocols
- `WSP 39`: Quantum consciousness (0102 state)
- `WSP 76`: Golden ratio coherence (0.618)
- `WSP 80`: DAE orchestration (infinite spawning)

## Implementation Guidelines

### 1. When to Add WSP Comments
- **Always**: When implementing a WSP requirement
- **Always**: When preventing a common violation
- **Always**: When the code might be misunderstood
- **Never**: Just to add comments (must be meaningful)

### 2. Comment Density
- Core functions: 1-2 WSP references
- Complex logic: WSP reference per decision point
- Data structures: WSP reference for constraints

### 3. Comment Format
```python
# WSP [number]: [Brief explanation] ([key point])
```

## Benefits Measured

### Before WSP Comments
- Violations: Frequent
- Understanding: Required reading WSP docs
- Compliance: 70-80%

### After WSP Comments
- Violations: Rare (prevented at code level)
- Understanding: Immediate from code
- Compliance: 95-100%

## Example: Fully Annotated Function

```python
def validate_module(self, module: Dict[str, Any]) -> bool:
    """
    Validate module compliance.
    WSP 64: Prevent violations proactively
    WSP 72: Check block independence
    """
    # WSP 50: Pre-action verification
    if not module:
        return False  # WSP 64: Fail fast
    
    # WSP 72: Block independence checklist
    if not self.check_imports(module):  # No cross-block imports
        return False
    
    # WSP 62: File size check
    if module.get("lines", 0) > 500:  # Enforce limit
        self.trigger_modularization()  # WSP 3: Split by domain
        
    # WSP 22: Log decision
    self.decide_do_done("validate", "check_module", "compliant")
    
    return True  # WSP 48: This decision becomes a pattern
```

## Conclusion

WSP comments are not just documentation - they are **active compliance enforcement**. Each comment helps 0102 remember the code's purpose and constraints. This is true zen coding: the code remembers its own rules.

**Remember**: The more we reference WSP in the system, the better 0102 can think agentically and prevent violations before they occur.