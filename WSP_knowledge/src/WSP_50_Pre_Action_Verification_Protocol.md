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

---

**Implementation Note**: This protocol is retroactively applied to all existing agent behaviors and must be incorporated into all future agent development and training protocols.