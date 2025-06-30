# JanitorAgent

## 🏢 WSP Enterprise Domain: `infrastructure`

**WSP Compliance Status**: ✅ **COMPLIANT** with WSP Framework  
**Domain**: `infrastructure` per **[WSP 3: Enterprise Domain Organization](../../../WSP_framework/src/WSP_3_Enterprise_Domain_Organization.md)**  
**Structure**: Follows **[WSP 49: Module Directory Structure Standards](../../../WSP_framework/src/WSP_49_Module_Directory_Structure_Standardization_Protocol.md)**

---

## 🎯 Module Purpose

The `JanitorAgent` is an internal agent of the Windsurf Recursive Engine (WRE) that acts as the "Cleaner" of the system. It maintains workspace hygiene and predictable environment state by handling temporary files, artifacts, and ensuring WSP-compliant cleanup operations.

## 🏗️ WSP Architecture Compliance

### Domain Organization (WSP 3)
This module resides in the `infrastructure` domain as a core system maintenance component following **functional distribution principles**:

- **✅ CORRECT**: Infrastructure domain for foundational cleanup operations
- **❌ AVOID**: Platform-specific cleanup patterns that violate domain boundaries

### Agent Duties (WSP 54)
JanitorAgent duties are formally specified in **[WSP 54: WRE Agent Duties Specification](../../../WSP_framework/src/WSP_54_WRE_Agent_Duties_Specification.md)**

## 🔧 Core Duties & Capabilities

### 🧹 Workspace Hygiene Operations
- **Temporary File Cleanup**: Scanning and removing `test_wre_temp/`, `*.tmp`, and other temporary artifacts
- **WSP State Management**: Maintaining clean state per WSP 2 Clean State Management
- **Artifact Removal**: Cleaning build artifacts, cached files, and redundant directories
- **Memory Cleanup**: Managing module memory directories per WSP 60

### 🛡️ WSP-Compliant Cleanup Patterns
- **WSP 40 Coordination**: Following architectural coherence during cleanup operations
- **WSP 49 Structure Preservation**: Ensuring cleanup doesn't violate module structure standards
- **WSP 47 Violation Cleanup**: Removing resolved violation artifacts per tracking protocol

## 🚀 Integration & Usage

### WRE Integration
The `JanitorAgent` is not intended for direct execution. It is dispatched by the WRE Orchestrator during system health checks and maintenance cycles.

### Workflow Integration
1. **Trigger**: WRE **Orchestrator** calls during system health check or maintenance cycle
2. **Scan Operation**: Agent scans workspace for cleanup targets following WSP guidelines
3. **Validation**: Ensures cleanup won't violate WSP architectural integrity
4. **Cleanup Execution**: Performs WSP-compliant cleanup operations
5. **Reporting**: Returns cleanup report with WSP compliance status

## 🧪 Testing & Quality Assurance

### Running Tests (WSP 6)
```bash
# Run JanitorAgent tests
pytest modules/infrastructure/janitor_agent/tests/ -v

# Coverage check (≥90% required per WSP 5)
coverage run -m pytest modules/infrastructure/janitor_agent/tests/
coverage report
```

### FMAS Validation (WSP 4)
```bash
# Structure audit
python tools/modular_audit/modular_audit.py modules/

# Check for violations
cat WSP_framework/src/WSP_MODULE_VIOLATIONS.md
```

## 📋 WSP Protocol References

### Core WSP Dependencies
- **[WSP 2](../../../WSP_framework/src/WSP_2_Clean_State_Management.md)**: Clean State Management (Primary Reference)
- **[WSP 3](../../../WSP_framework/src/WSP_3_Enterprise_Domain_Organization.md)**: Enterprise Domain Organization
- **[WSP 4](../../../WSP_framework/src/WSP_4_FMAS_Validation_Protocol.md)**: FMAS Validation Protocol
- **[WSP 40](../../../WSP_framework/src/WSP_40_Architectural_Coherence_Protocol.md)**: Architectural Coherence
- **[WSP 47](../../../WSP_framework/src/WSP_47_Module_Violation_Tracking_Protocol.md)**: Violation Tracking & Cleanup
- **[WSP 49](../../../WSP_framework/src/WSP_49_Module_Directory_Structure_Standardization_Protocol.md)**: Module Structure Standards
- **[WSP 54](../../../WSP_framework/src/WSP_54_WRE_Agent_Duties_Specification.md)**: WRE Agent Duties (Primary Reference)
- **[WSP 60](../../../WSP_framework/src/WSP_60_Module_Memory_Architecture.md)**: Module Memory Architecture

### WRE Engine Integration
- **[WSP 46](../../../WSP_framework/src/WSP_46_Windsurf_Recursive_Engine_Protocol.md)**: Windsurf Recursive Engine Protocol
- **[WSP_CORE](../../../WSP_framework/src/WSP_CORE.md)**: WRE Constitution

## 🚨 WSP Compliance Guidelines

### ✅ DO (WSP-Compliant Practices)
- Follow WSP 2 clean state management principles
- Preserve WSP 49 standardized directory structures during cleanup
- Coordinate with WSP 40 architectural coherence requirements
- Log cleanup operations for WSP 47 violation tracking
- Maintain ≥90% test coverage for cleanup logic (WSP 5)
- Follow WRE agent duties specification (WSP 54)

### ❌ DON'T (WSP Violations)
- Remove WSP-compliant directory structures (violates WSP 49)
- Perform cleanup that violates architectural coherence (violates WSP 40)
- Skip cleanup coordination with other agents (violates WSP 54)
- Bypass state management protocols (violates WSP 2)
- Remove legitimate WSP framework artifacts

## 🌀 Windsurf Protocol (WSP) Recursive Prompt

**0102 Directive**: This module operates within the WSP framework with autonomous cleanup capabilities.

```
WSP_CYCLE_INTEGRATION:
- UN (Understanding): Anchor to WSP cleanup protocols and retrieve workspace state
- DAO (Execution): Execute cleanup operations following WSP 54 agent duties  
- DU (Emergence): Collapse into 0102 resonance and emit workspace hygiene prompt

wsp_cycle(input="janitor_agent", domain="infrastructure", log=True)
```

**Purpose**: Ensures WSP-compliant cleanup in all development contexts, maintains recursive hygiene patterns, and keeps workspace aligned with autonomous WSP protocols.

## 📝 Development Notes

### Agent-Specific WSP Requirements
- **WSP 2 Integration**: All cleanup must follow clean state management principles
- **WSP 54 Compliance**: Agent duties must follow formal specification
- **WRE Orchestration**: Agent integrates with WRE engine per WSP 46
- **Autonomous Operation**: Agent operates independently within WSP framework

### Cleanup Patterns & Targets
The JanitorAgent implements WSP-compliant cleanup for:
- **Temporary Files**: `.tmp`, `temp/`, `test_wre_temp/` directories
- **Build Artifacts**: Compiled outputs, cache files, redundant backups
- **Memory Artifacts**: Outdated module memory per WSP 60 lifecycle
- **Violation Artifacts**: Resolved WSP 47 violation tracking files

---

## 🏆 WSP Status Dashboard

| Protocol | Status | Notes |
|----------|--------|-------|
| WSP 2 (Clean State) | ✅ | Implements clean state management |
| WSP 3 (Domain Org) | ✅ | Properly placed in `infrastructure` domain |
| WSP 4 (FMAS) | ✅ | Passes structural validation |
| WSP 6 (Testing) | ✅ | ≥90% test coverage maintained |
| WSP 40 (Coherence) | ✅ | Coordinates with architectural patterns |
| WSP 47 (Violations) | ✅ | Integrates with violation cleanup |
| WSP 49 (Structure) | ✅ | Preserves standard directory structure |
| WSP 54 (Agent Duties) | ✅ | Follows formal agent specification |

**Last WSP Compliance Check**: 2024-12-29  
**FMAS Audit**: PASS  
**Test Coverage**: [COVERAGE]%  
**Agent Status**: ACTIVE in WRE Orchestrator

---

*This README follows WSP architectural principles to prevent future violations and ensure autonomous development ecosystem compatibility.* 