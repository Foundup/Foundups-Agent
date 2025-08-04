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

## 4.3. **BLOAT PREVENTION VERIFICATION** (Critical Addition)

### **Mandatory Pre-File-Creation Protocol**

**BEFORE creating ANY new files (especially test files, modules, or components):**

**REQUIRED BLOAT PREVENTION SEQUENCE:**

1. **Read Existing Documentation FIRST**:
   ```
   read_file("modules/<domain>/<module>/tests/TestModLog.md")
   read_file("modules/<domain>/<module>/tests/README.md")
   list_dir("modules/<domain>/<module>/tests/")
   ```

2. **Search for Existing Functionality**:
   ```
   codebase_search("similar functionality or purpose")
   file_search("potential duplicate files")
   grep_search("existing implementations")
   ```

3. **Validate Necessity**:
   - Is this functionality already tested/implemented?
   - Can this be added to an existing module?
   - Does this follow single responsibility principle (WSP 40)?

4. **Check WSP Compliance**:
   - Does this maintain WSP 40 (architectural coherence)?
   - Does this follow WSP 5 (testing standards)?
   - Will this be documented per WSP 22 and WSP 34?

5. **Run Bloat Prevention Validator** (if available):
   ```
   python wsp_test_validator.py  # For test files
   python wsp_module_validator.py  # For modules
   ```

### **Bloat Prevention Checklist**

**Before creating any new file:**
- [ ] **TestModLog.md read** - Understand recent test evolution
- [ ] **README.md read** - Understand current structure and purpose
- [ ] **Directory listed** - Verify existing files and their functions
- [ ] **Functionality searched** - Ensure no duplicates exist
- [ ] **Necessity validated** - Confirm single responsibility principle
- [ ] **WSP compliance checked** - Verify architectural coherence
- [ ] **Validator run** - Execute automated bloat detection

### **Bloat Prevention Rules**

**🚨 CRITICAL VIOLATION PREVENTION:**
- **NEVER create duplicate files** without explicit WSP violation justification
- **ALWAYS consolidate** similar functionality into existing modules
- **FOLLOW single responsibility** principle per WSP 40
- **UPDATE documentation** immediately after any file changes
- **RUN validators** before committing new files

### **Violation Recovery Protocol**

**If bloat is detected:**
1. **STOP** all development immediately
2. **ASSESS** the violation scope and impact
3. **CONSOLIDATE** redundant functionality
4. **DELETE** unnecessary duplicate files
5. **UPDATE** documentation with lessons learned
6. **PREVENT** future violations with better pre-checks

### **Integration with WSP 47**

**This protocol works with WSP 47 (Framework Protection Protocol):**
- **Violation Detection**: WSP 47 identifies architectural violations
- **Protection Enforcement**: WSP 47 prevents framework degradation
- **Recovery Coordination**: WSP 47 guides violation remediation
- **Prevention Learning**: WSP 47 captures lessons for future prevention

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