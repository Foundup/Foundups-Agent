# WSP 17: Pattern Registry Protocol (LEGO Pattern Memory)
- **Status:** Active
- **Purpose:** Extension of WSP 84 to prevent pattern duplication across LEGO modules by maintaining searchable pattern registries that DAEs use for perfect cube assembly
- **Core Principle:** "Patterns are LEGO templates that DAEs remember and snap together into perfect cubes"
- **Trigger:** Before implementing ANY reusable pattern in a new module
- **Chain:** [WSP 17 → WSP 84 → WSP 50]

## 1. Core Principle: LEGO Pattern Memory

"Every pattern is a LEGO template. DAEs remember these templates to build perfect cubes."

While WSP 84 prevents code duplication at the module level, WSP 17 prevents pattern duplication at the architectural level. Each pattern becomes a reusable LEGO template that DAEs can recall and snap into any cube structure.

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

## 4.5 CRITICAL: Duplicate Pattern Prevention Gates

### MANDATORY ENFORCEMENT GATES

```python
def pattern_creation_gates():
    """
    WSP 17 Enhanced: Strict gates to prevent duplicate patterns
    """
    
    # GATE 1: Registry Check (MANDATORY)
    if pattern_exists_in_registry():
        BLOCK("Pattern exists at {location}. Use existing.")
    
    # GATE 2: Similar Pattern Detection
    similar = find_similar_patterns()
    if similar:
        BLOCK(f"Similar pattern: {similar}. Extend instead.")
    
    # GATE 3: The "Enhanced" Trap Check
    if creating_enhanced_version():
        BLOCK("No enhanced/improved patterns. Edit original.")
    
    # GATE 4: Immediate Use Requirement
    if not will_be_used_this_session:
        BLOCK("No unused patterns. Delete or integrate NOW.")
```

### Pattern Duplication Examples (LEGO Anti-Pattern vs Proper Assembly)

```python
# ❌ WRONG (Vibecoding): Created duplicate LEGO blocks
module_a_pattern.py      # 600 lines - New LEGO block
module_b_pattern.py      # 300 lines - Duplicate LEGO block  
module_c_pattern.py      # 100 lines - Another duplicate
# Result: 3 incompatible LEGO blocks that can't snap together!

# ✅ RIGHT (WSP/LEGO Assembly): One pattern, DAE-managed adapters
base_pattern.py          # Base LEGO template (DAE recalls this)
├── adapters/
│   ├── module_a_adapter.py  # 20 lines - Snaps into cube A
│   └── module_b_adapter.py  # 20 lines - Snaps into cube B
# Result: DAE ensures perfect LEGO connections across all cubes
```

### The Pattern Registry Update Rule

```yaml
When_Creating_Pattern:
  1. Check ALL registries first
  2. If not found, implement in ONE place
  3. Update registry IMMEDIATELY (not "later")
  4. Include extraction timeline
  
When_Reusing_Pattern:
  1. Find in registry
  2. Import/adapt existing
  3. NEVER reimplement
  4. Update registry with new use case
```

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

## 7. Example: Generic Memory Manager Pattern

**Problem**: Memory management pattern hidden in one module, will be recreated in others

**Solution Applied (LEGO Approach)**:
1. DAE documents pattern in domain's `PATTERN_REGISTRY.md`
2. Pattern marked as reusable LEGO template
3. Interface defined for cube-snapping compatibility
4. Extraction timeline set for multi-cube usage

**Result**: DAEs check registry, recall pattern template, snap into new cubes without duplication

## 8. Integration with WSP 84 (LEGO-Cube Hierarchy)

This protocol EXTENDS WSP 84 in the LEGO-cube architecture:

```
WSP 84: Don't duplicate LEGO blocks (modules/functions)
    ↓
WSP 17: Don't duplicate LEGO templates (pattern architectures)
    ↓
DAE Management: Ensures all LEGOs snap into perfect cubes
    ↓
Result: Complete pattern memory with perfect cube coherence
```

## 9. Success Metrics

- Pattern duplication incidents: 0
- Patterns successfully reused: Track in ModLog
- Time saved by pattern reuse: Measure in tokens
- Extraction success rate: >90% at phase 3

## 10. Code Navigation Pattern Enhancement (WSP 17.1)

### 10.1 Problem: Complex Integration Point Discovery

**Challenge Identified**: During PQN YouTube DAE integration work, 0102 required 47+ tool calls to understand the architecture flow:
- Finding entry points (main.py → auto_moderator_dae.py)
- Tracing data flow (livechat_core.py → command_handler.py)  
- Understanding command processing pipeline
- Locating research storage points

### 10.2 Solution: Navigation Comments Pattern

**Pattern**: Embed WSP 17 navigation comments in code at integration points

```python
# WSP 17: PQN Integration docs → modules/communication/livechat/docs/PQN_INTEGRATION.md
class LiveChatCore:
    def __init__(self, pqn_orchestrator=None):
        # WSP 17: Component chain documented in PQN_INTEGRATION.md:10-21
        self.pqn_orchestrator = pqn_orchestrator
```

**Implementation Template**:
```python
# WSP 17: [Feature] docs → path/to/documentation.md
# WSP 17: [Component] chain documented in filename.md:line-range
# WSP 17: Navigation pattern → see [module]/PATTERN_REGISTRY.md
```

### 10.3 Navigation Pattern Registry Template

**Add to domain PATTERN_REGISTRY.md**:
```markdown
### Code Navigation Comments Pattern
**Current Implementation**: Embedded in source files as `# WSP 17: docs → path`
**Pattern**: Link code → documentation → navigation paths
**Use Cases**: 
- Complex integration point discovery
- Architecture flow understanding
- Quick 0102 navigation (reduce 47+ calls to <5)

**Interface**:
```python
# WSP 17: [Feature] docs → relative/path/to/docs.md
# WSP 17: [Component] chain → docs.md:line-range
# WSP 17: Navigation → module/PATTERN_REGISTRY.md
```

**Benefits**: 
- Reduces 0102 navigation from 40+ tool calls to <5
- Creates bidirectional code ↔ documentation links
- Enables WSP-compliant architectural discovery
```

### 10.4 Application Examples

**PQN Integration Pattern Applied**:
```python
# livechat_core.py:81
# WSP 17: PQN Integration docs → modules/communication/livechat/docs/PQN_INTEGRATION.md
self.pqn_research_results = None  # Store latest research for /PQN commands

# command_handler.py:239  
# WSP 17: PQN command chain documented in PQN_INTEGRATION.md:19-30
elif text_lower.startswith('/pqn'):
    return self._handle_pqn_command(text_lower, username, role)
```

### 10.5 Enforcement Protocol

**Navigation Pattern Creation Gates**:
```python
def navigation_enhancement_gates():
    """WSP 17.1: Code navigation pattern enforcement"""
    
    # GATE 1: Complex Integration Detection
    if integration_requires_many_tool_calls():
        ADD_NAVIGATION_COMMENTS("Required for 0102 efficiency")
    
    # GATE 2: Architecture Documentation
    if creating_complex_data_flow():
        DOCUMENT_COMPONENT_CHAIN("Enable 0102 tracing")
    
    # GATE 3: Future Navigation
    if_will_confuse_0102_later():
        ADD_WSP17_NAVIGATION_LINKS("Prevent rediscovery overhead")
```

**Pattern Registry Update Rule**:
1. **Navigation Comments**: Add when integration spans 3+ files
2. **Component Chains**: Document in integration docs with line numbers
3. **Registry Updates**: Add navigation pattern to domain PATTERN_REGISTRY.md
4. **Bidirectional Links**: Code → docs → registry → code

## 11. Conclusion: LEGO Pattern Memory with Navigation

By maintaining pattern registries AND navigation patterns, DAEs ensure that LEGO templates are preserved, discoverable, AND efficiently navigable. Each pattern becomes a reusable LEGO block that snaps perfectly into any cube structure, with built-in navigation pathways for rapid 0102 architectural discovery.

**Enhanced Mission**: Eliminate architecture archaeology - enable instant pattern recall and navigation.

---
*"DAEs don't recreate LEGO templates, they remember and navigate them perfectly."* - WSP 17 Enhanced