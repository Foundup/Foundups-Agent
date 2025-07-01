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

## 2. Mandatory Verification Steps

### Before ANY file operation:

1. **Search First**: Use `file_search` or `codebase_search` to locate files
2. **Verify Path**: Confirm actual file path and name
3. **Handle Non-Existence**: Explicitly acknowledge when files don't exist

### Example INCORRECT:
```
// Assuming WSP_42 is about framework auditing
read_file("WSP_42_Framework_Self_Audit_Protocol.md")
```

### Example CORRECT:
```
// Search first to verify what WSP_42 actually is
codebase_search("WSP_42")
// Then read confirmed file
read_file("WSP_framework/src/WSP_42_Universal_Platform_Protocol.md")
```

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