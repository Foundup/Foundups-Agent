# WSP 47: Module Violation Tracking Protocol
- **Status:** Active
- **Purpose:** To systematically track and categorize module-specific violations that should be deferred during WSP framework work, ensuring clean separation between framework compliance and module development.
- **Trigger:** During WSP compliance audits when module-specific failures are detected that are not framework-blocking.
- **Input:** Test failure analysis, FMAS output, and module behavior discrepancies.
- **Output:** Structured violation log with categorization, impact assessment, and deferred resolution strategy.
- **Responsible Agent(s):** ComplianceAgent, 012 Rider

## 1. Overview

This protocol establishes the systematic tracking of **Module Placeholder Violations** - issues that arise from module evolution, placeholder drift, or platform-specific implementation gaps that do not impact WSP framework compliance but should be addressed when working on specific modules.

The protocol ensures [WSP focus on framework integrity][[memory:8051426004025697311]] while maintaining comprehensive system health tracking.

## 2. Violation Categories

### 2.1. Interface Parameter Drift
**Definition**: Module interfaces evolving independently of their test implementations
**Example**: Tests using `chat_id` while implementation expects `live_chat_id`
**Trigger**: `TypeError: unexpected keyword argument`

### 2.2. Behavioral Evolution Mismatch  
**Definition**: Module behavior improving while tests expect legacy responses
**Example**: Tests expecting `None` while module generates dynamic responses
**Trigger**: `AssertionError: Expected None but got dynamic content`

### 2.3. Module Structure Drift
**Definition**: Module API changes not reflected in dependent modules
**Example**: Missing attributes or methods in module interfaces
**Trigger**: `AttributeError: module has no attribute`

### 2.4. Platform Integration Placeholders
**Definition**: Incomplete platform-specific implementations in placeholder modules
**Example**: YouTube, LinkedIn, Twitter module placeholders with basic functionality
**Trigger**: Platform-specific test failures in non-critical paths

## 3. WSP vs Module Decision Matrix

| Violation Type | WSP Framework Impact | Resolution Strategy |
|----------------|---------------------|-------------------|
| **Framework Compliance** | BLOCKS WSP protocols | **IMMEDIATE FIX** |
| **Module Evolution** | No framework impact | **DEFER TO MODULE WORK** |
| **Interface Contract** | Affects system integration | **ASSESS IMPACT LEVEL** |
| **Platform Placeholder** | Isolated to platform | **LOG AND DEFER** |

## 4. Violation Tracking Protocol

### 4.1. Detection and Classification
When violations are detected during WSP audits:

1. **Impact Analysis**: Determine if violation affects WSP framework compliance
2. **Category Assignment**: Classify using Section 2 categories  
3. **Severity Assessment**: P0 (Blocking), P1 (High), P2 (Medium), P3 (Low)
4. **Resolution Strategy**: Immediate fix vs. deferred resolution

### 4.2. Violation Documentation Standard
Each tracked violation must include:

```markdown
### **V{ID}: {Violation Title}**
- **Module**: `path/to/module/`
- **File**: `specific_file.py:line_numbers`  
- **Issue**: Brief description of the problem
- **Error**: Exact error message or symptom
- **Impact**: Number and type of affected tests
- **Resolution**: Strategy for when module is actively developed
- **WSP Status**: DEFERRED - Justification for deferral
```

### 4.3. Violation Log Management
- **Location**: `WSP_framework/src/WSP_MODULE_VIOLATIONS.md` in framework directory
- **Updates**: Add new violations during WSP audits
- **Reviews**: Update status when modules are actively developed
- **Cleanup**: Remove resolved violations and update affected counts

## 5. Integration with WSP Framework

### 5.1. FMAS Integration (WSP_4)
FMAS should detect and categorize violations but NOT fail WSP compliance for module-specific issues:

```bash
# Enhanced FMAS command for violation categorization
python tools/modular_audit/modular_audit.py modules/ --wsp-focus --defer-module-violations
```

### 5.2. Test Audit Integration (WSP_6)  
Test failure analysis should distinguish framework vs. module issues:

```bash
# Categorized test failure analysis
pytest modules/ --tb=short | python tools/categorize_failures.py --wsp-framework-focus
```

### 5.3. Architectural Coherence Integration (WSP_40)
WSP_40 should identify when violations represent legitimate module evolution vs. architectural drift.

## 6. Module Development Integration

### 6.1. Module Work Trigger
When beginning work on a specific module:
1. **Review WSP_framework/src/WSP_MODULE_VIOLATIONS.md** for related violations
2. **Prioritize resolution** based on severity and impact
3. **Update violation status** as issues are resolved
4. **Remove resolved violations** from tracking log

### 6.2. Module Evolution Protocol
When modules evolve interfaces or behavior:
1. **Update dependent modules** that rely on changed interfaces
2. **Validate cross-module compatibility** for interface changes
3. **Update test expectations** for intentional behavior evolution
4. **Document evolution** in module CHANGELOG and INTERFACE.md

## 7. Violation Resolution Strategies

### 7.1. Interface Parameter Drift Resolution
- Update test parameter names to match current interface
- Verify interface documentation reflects actual implementation
- Check for other modules using deprecated parameters

### 7.2. Behavioral Evolution Resolution  
- Replace fixed assertions with pattern-based testing
- Update test expectations to accommodate dynamic responses
- Ensure backward compatibility for critical behavior

### 7.3. Module Structure Resolution
- Implement missing API methods or attributes
- Update import statements for renamed components
- Validate module initialization and dependency loading

### 7.4. Platform Integration Resolution
- Complete placeholder implementations for active platforms
- Add proper error handling for unsupported features
- Update documentation to reflect implementation status

## 8. Success Metrics

### 7.5. Functionality Loss Resolution (WSP 79)
- Perform WSP 79 SWOT analysis for all modules implicated in functionality[U+2011]loss violations
- Create a comparative feature matrix and preservation checklist
- Block deletion until preservation criteria are met and migration plans exist
- Link artifacts in `WSP_MODULE_VIOLATIONS.md` and the module ModLog (WSP 22)

### 8.1. WSP Framework Health
- **Zero P0 violations** blocking WSP protocol compliance
- **Clean separation** between framework and module concerns
- **Efficient prioritization** of development effort

### 8.2. Module Development Efficiency
- **Comprehensive violation tracking** for informed module work
- **Systematic resolution** reducing unexpected failures
- **Clear documentation** of module evolution requirements

### 8.3. System Integration Health
- **Maintained interface contracts** during module evolution
- **Backward compatibility** for critical system components
- **Coordinated updates** across dependent modules

---

**Implementation Note**: This protocol recognizes that [autonomous development ecosystem][[memory:1550040433202746122]] requires strategic focus allocation, ensuring WSP framework work remains efficient while comprehensive system health is maintained through systematic violation tracking. 