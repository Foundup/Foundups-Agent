# WSP 49: Module Directory Structure Standardization Protocol

- **Status:** Active
- **Purpose:** To establish and enforce standardized module directory structures, eliminating redundant naming patterns that violate WSP Rubik's Cube Architecture and ensuring clean, coherent module organization.
- **Trigger:** During module creation, architectural audits, or when redundant directory structures are detected.
- **Input:** Module directories requiring structure standardization.
- **Output:** WSP-compliant module directory structure following enterprise domain organization.
- **Responsible Agent(s):** ComplianceAgent, ModuleScaffoldingAgent, All agents creating or modifying module structures.

## 1. Purpose

This protocol addresses critical structural violations discovered in the WSP enterprise architecture, specifically **redundant naming patterns** that violate the Rubik's Cube modular architecture principle established in WSP 3.

## 2. CRITICAL STRUCTURAL VIOLATIONS IDENTIFIED

### 2.1. Redundant Naming Pattern Violations

**❌ CURRENT VIOLATIONS:**
```
modules/communication/livechat/livechat/           ← Redundant "livechat/livechat"
modules/platform_integration/youtube_auth/youtube_auth/  ← Redundant "youtube_auth/youtube_auth"  
modules/platform_integration/stream_resolver/stream_resolver/  ← Redundant "stream_resolver/stream_resolver"
modules/infrastructure/token_manager/token_manager/  ← Redundant "token_manager/token_manager"
modules/infrastructure/oauth_management/oauth_management/  ← Redundant "oauth_management/oauth_management"
modules/infrastructure/agent_management/agent_management/  ← Redundant "agent_management/agent_management"
modules/infrastructure/llm_client/llm_client/  ← Redundant "llm_client/llm_client"
```

### 2.2. Rubik's Cube Architecture Principle

**✅ CORRECT STRUCTURE** (3-Level Cube Architecture):
```
modules/[domain]/[module]/           ← Level 2: Module Cube (LEGO piece)
├── src/                            ← Level 3: Code cubes
├── tests/                          ← Level 3: Code cubes  
├── memory/                         ← Level 3: Code cubes (WSP 60)
├── README.md                       ← Level 3: Code cubes
└── requirements.txt                ← Level 3: Code cubes
```

**❌ INCORRECT REDUNDANT STRUCTURE:**
```
modules/[domain]/[module]/[module]/  ← VIOLATES: Creates unnecessary 4th level
├── src/                            ← Should be at Level 3, not Level 4
├── tests/                          ← Should be at Level 3, not Level 4
└── memory/                         ← Should be at Level 3, not Level 4
```

## 3. Standardization Requirements

### 3.1. Standard Module Structure

**MANDATORY STRUCTURE:**
```
modules/[domain]/[module]/
├── __init__.py                     ← Module initialization
├── src/                            ← Source code directory
│   ├── __init__.py
│   └── [module].py                 ← Main module file
├── tests/                          ← Test directory  
│   ├── __init__.py
│   ├── README.md                   ← Test documentation
│   └── test_[module].py            ← Main test file
├── memory/                         ← Module memory (WSP 60)
├── README.md                       ← Module documentation
├── INTERFACE.md                    ← Interface specification (WSP 11)
└── requirements.txt                ← Dependencies (WSP 12)
```

### 3.2. Naming Convention Rules

1. **NO REDUNDANT NAMING**: Module name should NOT be repeated in subdirectories
2. **FLAT STRUCTURE**: Direct access to `src/`, `tests/`, `memory/` from module root
3. **DESCRIPTIVE NAMING**: Use clear, functional names not redundant hierarchies
4. **ENTERPRISE ALIGNMENT**: Follow WSP 3 domain organization

## 4. Implementation Protocol

### 4.1. Violation Detection

**Automated Detection Pattern:**
```bash
# PowerShell detection command
Get-ChildItem -Path modules -Recurse -Directory | 
Where-Object { $_.Name -eq $_.Parent.Name } | 
Select-Object FullName
```

### 4.2. Structure Correction Procedure

**FOR EACH VIOLATION:**

1. **⚠️ ENGAGE 012 FOR DELETION DECISIONS**
2. **Analyze Content**: Determine if nested content should be promoted or consolidated  
3. **WSP Guards Check**: Look for WSP Guards and lock markers (WSP 40 Section 4)
4. **Import Dependencies**: Check for breaking import changes
5. **Execute Correction**: Move content to proper structure level
6. **Validate**: Ensure FMAS compliance after correction

### 4.3. Safe Correction Steps

**NEVER IMMEDIATELY DELETE - Follow WSP 40 Section 4:**

1. **Backup Analysis**: Check if nested structure contains unique content
2. **Lock Marker Detection**: Look for WSP development locks
3. **Import Impact**: Analyze import statement effects  
4. **Content Promotion**: Move legitimate content up one level
5. **Cleanup Empty**: Remove only confirmed empty redundant directories

## 5. Specific Module Corrections Required

### 5.1. Communication Domain

**Current**: `modules/communication/livechat/livechat/`  
**Correct**: `modules/communication/livechat/`

**Action**: Promote content from nested `livechat/` to module root level

### 5.2. Platform Integration Domain

**Current**: 
- `modules/platform_integration/youtube_auth/youtube_auth/`
- `modules/platform_integration/stream_resolver/stream_resolver/`

**Correct**:
- `modules/platform_integration/youtube_auth/`  
- `modules/platform_integration/stream_resolver/`

**Action**: Promote nested content to module root level

### 5.3. Infrastructure Domain  

**Current**:
- `modules/infrastructure/token_manager/token_manager/`
- `modules/infrastructure/oauth_management/oauth_management/`
- `modules/infrastructure/agent_management/agent_management/`
- `modules/infrastructure/llm_client/llm_client/`

**Correct**:
- `modules/infrastructure/token_manager/`
- `modules/infrastructure/oauth_management/`  
- `modules/infrastructure/agent_management/`
- `modules/infrastructure/llm_client/`

**Action**: Promote nested content to module root level for each

## 6. Compliance Validation

### 6.1. Pre-Correction Validation

- ✅ FMAS Mode 1 baseline audit
- ✅ WSP 40 architectural coherence check
- ✅ Import dependency analysis
- ✅ WSP Guards and lock marker detection

### 6.2. Post-Correction Validation

- ✅ FMAS Mode 1 compliance verification
- ✅ All tests pass (WSP 6)
- ✅ Import statements functional
- ✅ Module memory structure intact (WSP 60)

## 7. Integration with Other WSPs

### 7.1. WSP Dependencies

- **WSP 3**: Enterprise Domain Organization (structural foundation)
- **WSP 4**: FMAS Validation (compliance checking)  
- **WSP 40**: Architectural Coherence (multi-version analysis)
- **WSP 60**: Module Memory Architecture (memory structure preservation)

### 7.2. Agent Coordination

- **ComplianceAgent**: Detect structural violations
- **ModuleScaffoldingAgent**: Create compliant structures  
- **JanitorAgent**: Clean up redundant directories (post-validation)

## 8. Emergency Protocol: 012 Engagement

**CRITICAL REQUIREMENT**: Before any directory deletion or major structural change:

1. **🚨 ENGAGE 012**: Present analysis and proposed changes
2. **Architecture Review**: Confirm structural intent understanding
3. **Content Analysis**: Verify no legitimate separation exists
4. **User Approval**: Get explicit confirmation for structural changes
5. **Rollback Plan**: Maintain ability to revert changes

## 9. Implementation Priority

### 9.1. Phase 1: Analysis (Immediate)
- Document all redundant structures
- Analyze content for legitimate separation
- Check WSP Guards and dependencies

### 9.2. Phase 2: 012 Consultation (Critical)  
- Present findings to 012
- Get architectural clarification
- Obtain change approval

### 9.3. Phase 3: Correction (Post-Approval)
- Execute structure standardization
- Validate compliance
- Update documentation

---

**ARCHITECTURAL PRINCIPLE**: The WSP Rubik's Cube architecture requires clean, non-redundant module structures. Each module is a LEGO piece within its domain cube, containing code cubes at the proper structural level. Redundant naming creates unnecessary complexity and violates the fundamental modularity principle.

---

**Last Updated**: WSP 49 Creation - Module Directory Structure Standardization  
**Next Action**: Engage 012 for structural correction approval and begin Phase 1 analysis 