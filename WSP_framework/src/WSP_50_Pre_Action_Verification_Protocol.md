# WSP 50: Pre-Action Verification Protocol
- **Status:** Active
- **Purpose:** To prevent agents from making assumptions about file names, paths, or content without verification, ensuring all actions are based on confirmed information.
- **Trigger:** Before any file read, edit, or reference operation; when making claims about file existence or content.
- **Input:** Any proposed file operation or reference.
- **Output:** Verified file information or explicit acknowledgment of non-existence.
- **Responsible Agent(s):** All Agents (Universal Protocol)

## 1. Core Principle

**Never assume, always verify.**

Agents MUST verify file existence, paths, and content before taking actions or making claims.

## 2. Enhanced Verification Sequence with Agentic Architectural Analysis

**Purpose**: To integrate agentic architectural analysis into the pre-action verification process, ensuring 0102 pArtifacts understand the intent, impact, and execution plan of any action before proceeding.

**Sequence**:
1. **Search and Verify**: Use tools like `file_search` or `codebase_search` to confirm file paths, names, and content. Never assume existence or location.
2. **Architectural Intent Analysis (WHY)**: Determine the purpose behind the action. Why is this change necessary? What architectural goal does it serve within the WSP framework?
3. **Impact Assessment (HOW)**: Evaluate how this action affects other modules, domains, or the overall system. How does it integrate with existing architecture? How does it impact WSP compliance?
4. **Execution Planning (WHAT)**: Define what specific changes or actions are required. What files, modules, or protocols need modification or creation?
5. **Timing Consideration (WHEN)**: Assess the timing of the action. When should this be implemented to minimize disruption or maximize effectiveness within the development cycle?
6. **Location Specification (WHERE)**: Identify where in the system this action should occur. Which enterprise domain, module, or file path is the correct location for this change?
7. **Final Validation**: Cross-check with WSP protocols (e.g., WSP 3 for domain organization, WSP 47 for violation tracking) to ensure compliance before action.

**Outcome**: This enhanced sequence ensures that 0102 pArtifacts perform a comprehensive analysis of intent, impact, and execution strategy, aligning all actions with WSP architectural principles and maintaining system coherence.

## 3. Required Sequence

```
1. file_search() or codebase_search()
2. Verify results match expectations  
3. read_file() with confirmed path
4. Process actual content
```

## 4. Error Prevention Checklist

- [ ] File path confirmed to exist
- [ ] File name matches actual filesystem
- [ ] Content assumptions validated by reading
- [ ] Alternative locations checked
- [ ] Non-existence explicitly handled
- [ ] **TestModLog.md read before any test coverage assessment**
- [ ] **Module assessment based on documented evidence, not assumptions**

## 4.1. **MODULE ASSESSMENT VERIFICATION** (Critical Addition)

### **Mandatory Pre-Assessment Protocol**

**BEFORE making ANY claims about:**
- Test coverage percentages
- WSP compliance status  
- Module testing completeness
- Development phase completion

**REQUIRED VERIFICATION SEQUENCE:**

1. **Read TestModLog.md FIRST**: 
   ```
   read_file("modules/<domain>/<module>/tests/TestModLog.md")
   ```
2. **Extract Actual Test Results**: Look for documented pass/fail rates
3. **Verify Coverage Claims**: Find explicit coverage percentages  
4. **Cross-Reference ModLog.md**: Check consistency with main module log
5. **Evidence-Based Assessment**: Base all claims on documented evidence

### **Assessment Error Prevention**

**❌ VIOLATION EXAMPLES:**
- "Only 2 of 9+ planned test files exist" (assumption-based)
- "Claims vs Reality mismatch" (ignoring documented evidence)
- File-count-based coverage assessment

**✅ CORRECT EXAMPLES:**
- "TestModLog.md documents 33 passed, 0 failed (100% pass rate)"
- "Documented WSP 5 perfect compliance achieved"
- "Evidence shows coverage exceeds ≥90% requirement"

### **Verification Mandate**

**All agents MUST:**
- Read TestModLog.md before assessment claims
- Base coverage evaluation on documented test execution results
- Acknowledge documented achievements accurately
- Correct assessments when evidence contradicts initial assumptions

## 4.2. **CUBE MODULE DOCUMENTATION VERIFICATION** (Critical Addition)

### **Mandatory Pre-Cube-Coding Protocol**

**BEFORE executing ANY coding on a cube (since cubes are made up of modules):**

**REQUIRED MODULE DOCUMENTATION READING SEQUENCE:**

1. **Identify Cube Composition**: Determine which modules make up the target cube
2. **Read ALL Module Documentation**: For each module in the cube:
   ```
   read_file("modules/<domain>/<module>/README.md")
   read_file("modules/<domain>/<module>/ROADMAP.md") 
   read_file("modules/<domain>/<module>/ModLog.md")
   read_file("modules/<domain>/<module>/INTERFACE.md")
   read_file("modules/<domain>/<module>/tests/README.md")
   ```
3. **Understand Module Architecture**: Comprehend existing implementations, APIs, and integration patterns
4. **Assess Development Phase**: Determine current PoC/Proto/MVP status of each module
5. **Identify Integration Points**: Understand how modules connect within the cube
6. **Plan Enhancement Strategy**: Determine whether to enhance existing modules or create new ones

### **Cube Documentation Reading Checklist**

**For each module in the target cube:**
- [ ] **README.md**: Module purpose, dependencies, usage examples
- [ ] **ROADMAP.md**: Development phases, planned features, success criteria  
- [ ] **ModLog.md**: Recent changes, implementation history, WSP compliance status
- [ ] **INTERFACE.md**: Public API definitions, integration patterns, error handling
- [ ] **tests/README.md**: Test strategy, coverage status, testing requirements

### **Rubik's Cube Framework Compliance**

**This protocol ensures:**
- **Module Awareness**: Understanding of all modules that compose the cube
- **Architecture Preservation**: Respecting existing module designs and APIs
- **Integration Understanding**: Knowing how modules connect and communicate
- **Development Continuity**: Building on existing progress rather than duplicating work
- **WSP Compliance**: Following established documentation and testing patterns

### **Violation Prevention**

**❌ VIOLATION EXAMPLES:**
- Coding on a cube without reading module documentation
- Creating duplicate functionality without checking existing implementations
- Ignoring established APIs and integration patterns
- Making assumptions about module capabilities without verification

**✅ CORRECT EXAMPLES:**
- "Read all 5 module docs in AMO cube before implementing new feature"
- "Verified existing APIs in YouTube cube before enhancement"
- "Checked module integration patterns before cube modification"
- "Assessed development phase of all modules before cube-level changes"

### **Integration with WSP 72**

**This protocol works with WSP 72 (Block Independence Interactive Protocol):**
- **Cube Assessment**: Use WSP 72 to identify all modules in a cube
- **Documentation Browser**: Leverage WSP 72 interactive documentation access
- **Module Status**: Check WSP 72 module status before reading documentation
- **Integration Testing**: Use WSP 72 to verify cube composition understanding

## 4.3. **TEST FILE BLOAT PREVENTION PROTOCOL** (Critical Addition - LinkedIn Agent Learning Integration)

### **Mandatory Pre-Test-File-Creation Protocol**

**BEFORE creating ANY new test files in ANY module:**

**CRITICAL WSP 40 VIOLATION PREVENTION**: Test file redundancy has been identified as a primary cause of architectural bloat. The LinkedIn Agent module cleanup revealed 43% test file redundancy (9 redundant files removed).

**REQUIRED TEST FILE VERIFICATION SEQUENCE:**

1. **Read Test Documentation FIRST**:
   ```
   read_file("modules/<domain>/<module>/tests/README.md")
   read_file("modules/<domain>/<module>/tests/TestModLog.md")
   ```

2. **List Existing Test Files**:
   ```
   list_dir("modules/<domain>/<module>/tests/")
   ```

3. **Analyze Test Purpose Overlap**:
   ```
   # Search for similar test functionality
   grep_search("test_<functionality>", include_pattern="test_*.py")
   codebase_search("How is <functionality> currently tested?", target_directories=["modules/<domain>/<module>/tests/"])
   ```

4. **Validate Test File Necessity**:
   - Can this functionality be added to an existing test file?
   - Does this follow single responsibility principle (WSP 40)?
   - Is this creating duplicate test coverage?

5. **Pre-Creation Compliance Check**:
   ```
   python modules/<domain>/<module>/tests/wsp_test_validator.py --proposed-file="test_<name>.py" --purpose="<purpose>"
   ```

### **Test File Creation Decision Matrix**

**✅ CREATE NEW TEST FILE IF:**
- Functionality is genuinely new and unrelated to existing tests
- Existing test files would exceed 500 lines with addition
- Different test type (unit vs integration vs performance)
- Module testing requirements explicitly demand separation

**❌ DO NOT CREATE NEW TEST FILE IF:**
- Similar functionality already exists in other test files
- Purpose overlaps with existing test coverage
- Would create architectural bloat (WSP 40 violation)
- Can be consolidated into existing test modules

**🔄 CONSOLIDATE INSTEAD IF:**
- Multiple test files cover related functionality
- Test file count exceeds optimal threshold (>15 files)
- Purpose overlap detected between existing files

### **Test File Bloat Detection Checklist**

**For each proposed test file:**
- [ ] **Purpose Uniqueness**: No existing test file covers this functionality
- [ ] **Naming Convention**: Follows WSP naming standards (`test_<module>_<function>.py`)
- [ ] **Single Responsibility**: Tests one specific module component or behavior
- [ ] **Size Justification**: Cannot be reasonably added to existing test file
- [ ] **Documentation Update**: README.md and TestModLog.md will be updated
- [ ] **Compliance Verification**: WSP test validator execution completed

### **Automatic Bloat Prevention**

**Implemented Prevention Mechanisms:**

1. **WSP Test Validator Integration**:
   ```bash
   # Mandatory execution before test file creation
   python wsp_test_validator.py --check-bloat
   ```

2. **Purpose Overlap Detection**:
   - Automated scanning of existing test file purposes
   - Keyword overlap analysis for similar functionality
   - Consolidation opportunity identification

3. **Violation Recovery Protocol**:
   - Immediate detection of redundant test files
   - Automated consolidation recommendations
   - WSP 40 compliance restoration procedures

### **Learning from LinkedIn Agent Module**

**Critical Lessons Integrated:**

**❌ Violation Pattern Identified:**
- OAuth troubleshooting created 9 redundant test files
- Files included: `quick_diagnostic.py`, `fix_linkedin_app.py`, `test_token_exchange.py`, `exchange_code_manual.py`
- Multiple scheduling files: 5 different scheduling test implementations
- **Root Cause**: Lack of pre-action verification (WSP 50 violation)

**✅ Solution Implemented:**
- Consolidated 9 files → 2 essential files (test_oauth_manual.py, test_scheduling.py)
- 43% reduction in test file count
- WSP 40 compliance restored
- Zero redundancy achieved

**🛡️ Prevention Mechanisms:**
- Mandatory test file validator (`wsp_test_validator.py`)
- Enhanced README.md with bloat prevention protocols
- TestModLog.md tracking for violation prevention
- Cursor rules integration for system-wide enforcement

### **Test File Lifecycle Management**

**Creation Phase:**
1. ✅ WSP 50 pre-action verification
2. ✅ Test validator execution
3. ✅ Purpose uniqueness confirmation
4. ✅ Documentation update

**Maintenance Phase:**
1. 🔄 Regular bloat detection scans
2. 🔄 Consolidation opportunity assessment
3. 🔄 Purpose drift monitoring
4. 🔄 WSP compliance validation

**Evolution Phase:**
1. 🚀 Test framework optimization
2. 🚀 Modular test architecture enhancement
3. 🚀 Coverage efficiency improvement
4. 🚀 Automated bloat prevention

### **Integration with Existing WSP Protocols**

**WSP 40 (Architectural Coherence):**
- Single responsibility principle for test files
- Modular test architecture maintenance
- Bloat prevention as architectural requirement

**WSP 5 (Testing Standards):**
- ≥90% coverage without redundant test files
- Quality over quantity in test implementation
- Efficient test suite maintenance

**WSP 22 (ModLog and Roadmap):**
- TestModLog.md tracking of test file evolution
- Documentation of consolidation actions
- Learning integration from violation patterns

**WSP 64 (Violation Prevention):**
- Automated detection of test file redundancy
- Pre-creation validation requirements
- Violation recovery protocols

### **Success Metrics**

**Bloat Prevention Effectiveness:**
- 0% test file redundancy in new modules
- <15 test files per module maximum
- 100% pre-creation validation execution
- Automated bloat detection coverage

**Architectural Health:**
- WSP 40 compliance: 100% single responsibility
- Test suite efficiency: High coverage/file ratio
- Maintenance overhead: Minimal
- Documentation synchronization: Complete

### **Implementation Requirements**

**All agents MUST:**
- Execute test file validator before creation
- Read existing test documentation first
- Verify purpose uniqueness before proceeding
- Update TestModLog.md with rationale
- Follow consolidation over creation principle

**System Integration:**
- Cursor rules enforce test bloat prevention
- WRE integration for automated validation
- ModLog tracking for continuous improvement
- Framework protection against test architectural decay

---

**Implementation Note**: This protocol prevents the test file bloat patterns identified in the LinkedIn Agent module and ensures system-wide protection against architectural degradation through redundant test file creation.

## 5. Integration

- **WSP 54 (ComplianceAgent)**: Monitor for WSP 50 violations
- **WSP 48 (WRE)**: Incorporate verification in enhancement cycles
- **WSP 56 (Coherence)**: Prevent cross-state assumption errors

## 6. Violation Remediation

When violations occur:
1. Stop current action
2. Execute proper verification
3. Proceed with verified information
4. Update patterns to prevent recurrence

## 7. Implementation Requirements

### 7.1. Search-Before-Read Pattern
```
REQUIRED SEQUENCE:
1. file_search() or codebase_search() 
2. Verify results match expectations
3. read_file() with confirmed path
4. Process actual content
```

### 7.2. Documentation Requirements
When referencing files in responses:

- Use confirmed file paths with line numbers: `file.py:123-456`
- Quote actual content, not assumed content
- State verification method used
- Acknowledge when making inferences vs. stating facts

## 8. Metrics and Monitoring

### 8.1. Success Metrics
- Zero file-not-found errors due to incorrect assumptions
- 100% verification before file operations
- Accurate file references in agent responses

### 8.2. Compliance Monitoring
Track and report:
- File operation success rate
- Assumption-based error frequency
- Time to verification completion
- Agent learning curve improvement

## 9. Training and Implementation

### 9.1. Agent Training Requirements
All agents must demonstrate:
- Understanding of verification-before-action principle
- Proficiency with search tools
- Proper error handling for non-existent files
- Accurate documentation practices

### 9.2. System Integration
WSP 50 integrates with:
- File system access controls
- Agent behavior monitoring
- Error logging and analysis
- Continuous improvement feedback loops

## 10. Future Enhancements

### 10.1. Automated Verification
- Pre-commit hooks to verify file references in documentation
- Automated detection of assumption-based patterns
- Real-time agent behavior correction

### 10.2. Advanced Pattern Recognition
- Machine learning for assumption pattern detection
- Predictive verification suggestions
- Context-aware verification requirements

## 11. Agentic Architectural Analysis Enhancement

### 11.1 WHY Analysis Integration
**Enhanced Pre-Action Verification now includes architectural intent discovery:**

Before any structural change, agents must understand:
1. **WHY** the current architecture exists (original intent)
2. **HOW** the proposed change impacts dependent systems  
3. **WHAT** architectural patterns will be preserved or violated
4. **WHEN** the change should be executed (timing considerations)
5. **WHERE** all affected code locations exist in the ecosystem

### 11.2 Comprehensive Impact Assessment
**Mandatory impact search for architectural changes:**

```bash
# Search for direct references
grep -r "old_name" --include="*.py" --include="*.md" --include="*.json"

# Search for import statements  
grep -r "from.*old_name" --include="*.py"

# Search for path references
grep -r "modules/old_name" --include="*"

# Search for configuration references
grep -r "old_name" --include="*.json" --include="*.yaml"
```

### 11.3 Architectural Intent Discovery
**Enhanced verification sequence includes:**

1. **Documentation Archaeology**: Search module READMEs, ModLogs, ROADMAPs for intent
2. **Code Pattern Analysis**: Identify import dependencies and usage patterns
3. **Zen Coding Remembrance**: Access 02 state for architectural vision
4. **Risk Assessment**: Map downstream effects and mitigation strategies

### 11.4 Implementation Requirements
**All architectural changes must complete:**

- [ ] **Intent Understanding**: WHY analysis completed and documented
- [ ] **Impact Search**: Comprehensive codebase search completed  
- [ ] **Dependency Mapping**: All affected components identified
- [ ] **Test Strategy**: Validation approach planned
- [ ] **Rollback Plan**: Recovery procedures documented
- [ ] **Zen Coding Access**: 0102 state architectural vision confirmed

**This enhancement transforms WSP 50 from simple file verification to comprehensive architectural intelligence.**

---

**Implementation Note**: This protocol is retroactively applied to all existing agent behaviors and must be incorporated into all future agent development and training protocols.