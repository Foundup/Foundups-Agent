# WSP Project Rules - Enhanced "Follow WSP" Execution

This directory contains comprehensive Project Rules designed to enhance Agent performance in executing "follow WSP" across all aspects of the Foundups-Agent codebase.

## Rule Architecture

### Always Applied Rules (Core WSP Framework)
These rules are automatically included in every context:

- **`wsp_violation_prevention.mdc`** - 🚨 WSP 64 automatic enforcement and violation prevention with blocking triggers
- **`wsp_core_framework.mdc`** - Core WSP principles, pre-action verification (WSP 50), and framework vs module decision matrix (WSP 47)
- **`wsp_enterprise_architecture.mdc`** - Enterprise domain organization and functional distribution requirements  
- **`wsp_testing_coverage.mdc`** - Testing standards, coverage requirements, and FMAS integration
- **`wsp_test_bloat_prevention.mdc`** - 🛡️ **NEW:** Test file bloat prevention (WSP 50 Section 4.3) - LinkedIn Agent learning integration
- **`wsp_documentation_standards.mdc`** - Documentation requirements and three-state architecture
- **`wsp_agent_behavior.mdc`** - Agent state awareness and decision-making protocols

### Context-Specific Rules (Module Development)
These rules activate during specific development contexts:

- **`wsp_module_development.mdc`** - Complete module development workflow and compliance checklist
- **`wsp_quantum_protocols.mdc`** - Quantum state progression and zen coding principles
- **`wsp_master_execution.mdc`** - Quick reference guide and decision tree for all WSP actions

## WSP Enhancement Benefits

### 1. Pre-Action Verification (WSP 50)
- **NEVER assume, always verify** file paths and content
- Mandatory search-before-read sequence prevents assumption errors
- Explicit handling of non-existent files
- **NEW:** Test file bloat prevention (Section 4.3) - prevents 43% redundancy patterns

### 2. Framework vs Module Decision Matrix (WSP 47)
- Clear categorization of issues as framework-blocking vs module evolution
- Immediate fix for WSP compliance violations
- Proper deferral and logging of module placeholder issues

### 3. Enterprise Architecture Enforcement
- Functional distribution across domains (never platform consolidation)
- Proper module placement in enterprise domains
- Mandatory module structure compliance (WSP 49)

### 4. Testing and Coverage Standards
- ≥90% test coverage requirements for all modules
- Enterprise-scale testing architecture (modular testing)  
- FMAS integration for structural validation
- **NEW:** Test file bloat prevention - automatic redundancy detection and consolidation

### 5. Agent State Awareness
- Recognition of 012 (human rider) vs 0102 (quantum entangled Agent) states
- Proper zen coding language and autonomous development terminology
- Quantum temporal decoding principles

## Key Commands Embedded in Rules

```bash
# Structure validation
python tools/modular_audit/modular_audit.py modules/

# Test coverage verification
pytest modules/ --cov=modules --cov-report=term-missing

# Full test suite validation
pytest modules/ -v

# WSP violation tracking
WSP_framework/src/WSP_MODULE_VIOLATIONS.md
```

## WSP Decision Tree Integration

The rules embed the complete WSP decision tree:
1. **New Module/Feature?** → Module Development Workflow
2. **Framework Issue?** → WSP 47 Decision Matrix
3. **Testing Issue?** → WSP 5/6 Protocols
4. **File Operation?** → WSP 50 Pre-Action Verification

## Success Metrics Enforcement

The rules establish clear success criteria:
- ✅ FMAS audit: 0 errors, 0 warnings
- ✅ Test coverage: ≥90% all modules  
- ✅ Framework compliance: No blocking violations
- ✅ Documentation: All mandatory files present
- ✅ Architecture: Functional distribution maintained

## Integration with WSP Framework

These rules directly reference and enforce:
- **WSP_CORE.md**: Foundation and decision matrix
- **WSP_1**: Core principles and enterprise testing
- **WSP_47**: Module violation tracking protocol
- **WSP_50**: Pre-action verification protocol
- **All WSP 1-13**: Core development protocols

## Usage

The rules are automatically applied based on file patterns and contexts. The always-applied rules ensure consistent WSP compliance, while context-specific rules provide detailed guidance during module development and quantum protocol work.

This comprehensive rule set transforms the abstract instruction "follow WSP" into concrete, actionable guidance that enhances autonomous development efficiency and maintains WSP framework integrity. 