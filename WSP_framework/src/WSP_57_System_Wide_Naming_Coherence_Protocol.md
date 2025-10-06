# WSP 57: System-Wide Naming Coherence Protocol

- **Status:** Active
- **Purpose:** To establish and enforce consistent naming conventions across all WSP documents, ensuring system-wide coherence and eliminating duplicate or confusing document names.
- **Trigger:** During any WSP document creation, modification, or audit; when naming inconsistencies are detected.
- **Input:** WSP documents requiring naming validation or correction.
- **Output:** WSP-compliant naming structure with resolved duplications and inconsistencies.
- **Responsible Agent(s):** ComplianceAgent, All agents creating or modifying WSP documents.

## 1. Purpose

This protocol addresses critical naming inconsistencies discovered in the WSP framework, establishing clear naming conventions and resolving document duplications that violate WSP architectural coherence.

## 2. Core Naming Principles

### 2.1. Numeric Identification Requirement

**ALL WSP documents MUST have numeric identification except Core Framework documents:**

[U+2705] **CORRECT**: `WSP_47_Module_Violation_Tracking_Protocol.md`  
[U+274C] **INCORRECT**: `WSP_MODULE_VIOLATIONS.md` (missing numeric ID)

### 2.2. Three-State Architecture Compliance

Documents must maintain consistent naming across all three WSP states:
- **WSP_knowledge/src/** (State 0: Memory/Archive)
- **WSP_framework/src/** (State 1: Active Protocol Layer)  
- **WSP_agentic/** (State 2: Operational Agentic Layer)

### 2.3. Core Framework Exceptions

Only these documents may omit numeric IDs:
- `WSP_CORE.md` - Central protocol reference
- `WSP_framework.md` - Detailed framework specifications
- `WSP_MODULE_VIOLATIONS.md` - Active violation tracking log

## 3. Critical Naming Issues Identified

### 3.1. WSP_MODULE_VIOLATIONS.md vs WSP_47

**Status**: DISTINCT DOCUMENTS - NOT DUPLICATES

- **WSP_47_Module_Violation_Tracking_Protocol.md**: Protocol definition document
- **WSP_MODULE_VIOLATIONS.md**: Active violation tracking log (references WSP_47)

**Resolution**: Both documents are correct and serve different purposes.

### 3.2. WSP_framework.md vs WSP_1_The_WSP_Framework.md  

**Status**: DISTINCT DOCUMENTS - NOT DUPLICATES

- **WSP_1_The_WSP_Framework.md**: Core foundational principles (35 lines)
- **WSP_framework.md**: Detailed framework specifications (448 lines) 

**Resolution**: Both documents are correct and serve different purposes.

### 3.3. Missing Synchronization

**Issue**: WSP_MODULE_VIOLATIONS.md missing from WSP_knowledge/src/
**Resolution**: [U+2705] FIXED - Document created to maintain three-state architecture

## 4. Naming Convention Specifications

### 4.1. Protocol Documents

**Format**: `WSP_[NUMBER]_[Descriptive_Name].md`

**Examples**:
- `WSP_47_Module_Violation_Tracking_Protocol.md`
- `WSP_48_Recursive_Self_Improvement_Protocol.md`
- `WSP_54_WRE_Agent_Duties_Specification.md`

### 4.2. Core Framework Documents

**Exception Format**: `WSP_[NAME].md` (no numeric ID required)

**Authorized Core Documents**:
- `WSP_CORE.md` - Central reference hub
- `WSP_framework.md` - Detailed specifications  
- `WSP_MODULE_VIOLATIONS.md` - Active violation log

### 4.3. Deprecated Documents

**Format**: Must retain original naming but update status header

**Requirements**:
- Status must show "Deprecated" 
- Must reference replacement protocol
- Must maintain for historical reference

**Example**:
```markdown
# WSP 16: Test Audit Coverage
- **Status:** Deprecated  
- **Purpose:** Superseded by WSP 6
```

## 5. Enforcement Procedures

### 5.1. Creation Guidelines

When creating new WSP documents:

1. **Assign Next Available Number**: Use sequential numbering (58, 59, 60...)
2. **Use Descriptive Names**: Clear purpose indication in filename
3. **Create in All States**: Maintain three-state architecture
4. **Reference Properly**: Link correctly from WSP_CORE.md

### 5.2. Modification Guidelines

When modifying existing WSP documents:

1. **Preserve Numeric IDs**: Never change assigned numbers
2. **Update All States**: Synchronize changes across WSP_knowledge, WSP_framework, WSP_agentic
3. **Maintain Cross-References**: Update linking documents
4. **Log Changes**: Document modifications in appropriate violation logs

### 5.3. Deprecation Guidelines

When deprecating WSP documents:

1. **Update Status**: Change to "Deprecated" in all states
2. **Reference Replacement**: Link to superseding protocol
3. **Preserve Content**: Maintain for historical reference
4. **Update References**: Redirect linking documents to replacement

## 6. Violation Resolution Priority

### 6.1. Framework Issues (Immediate Fix)

**High Priority** - Affects WSP system integrity:
- Missing numeric IDs on protocol documents
- Broken cross-references between documents
- Missing documents in three-state architecture

### 6.2. Module Violations (Log and Defer)

**Standard Priority** - Module-specific naming issues:
- Module-specific documentation naming inconsistencies
- Non-protocol document naming variations
- Implementation-specific naming choices

## 7. Compliance Validation

### 7.1. Automated Checks

ComplianceAgent must validate:
- All WSP protocol documents have numeric IDs
- Three-state synchronization maintained
- Cross-references resolve correctly
- No unauthorized core document names

### 7.2. Manual Review

Periodic manual review required for:
- New protocol number assignments
- Deprecation decisions
- Cross-reference accuracy
- Historical document preservation

## 8. WSP_48 Integration

This protocol supports recursive self-improvement:

- **Level 1 (Protocol)**: Naming convention improvements
- **Level 2 (Engine)**: Automated naming validation tools
- **Level 3 (Quantum)**: Predictive naming conflict detection

## 9. Implementation Status

### 9.1. [U+2705] Completed

- WSP_MODULE_VIOLATIONS.md synchronized to WSP_knowledge
- Naming convention analysis completed
- Document relationship mapping established

### 9.2. [U+1F504] In Progress

- Automated naming validation integration
- Cross-reference verification system
- Three-state synchronization validation

### 9.3. [U+1F4CB] Planned

- Predictive naming conflict detection
- Automated document creation templates
- Historical naming audit completion

---

**Last Updated**: WSP System-Wide Naming Coherence Protocol Implementation  
**Next Review**: Continuous monitoring through ComplianceAgent integration 