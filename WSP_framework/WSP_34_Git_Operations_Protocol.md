# WSP 34: Git Operations Protocol

**Document Version:** 1.0  
**Date Updated:** 2025-01-08  
**Status:** Active  
**Applies To:** All file creation, branch operations, and git workflows within FoundUps Agent

## 🎯 Purpose

Establish strict controls for file creation, branch management, and git operations to prevent:
- Temp file pollution in main branch
- Recursive build folder creation  
- Unauthorized direct commits to main
- WSP compliance violations

## 🚨 Main Branch Protection Rules

### ❌ **PROHIBITED in Main Branch:**
```
temp_*                  # All temp files
build/                  # Build directories  
*_clean*               # Clean state folders
backup_*               # Backup files
02_logs/               # Log directories
*.log                  # Log files
*_files.txt            # File listing outputs
__pycache__/           # Python cache
.coverage              # Coverage files
venv/                  # Virtual environments
```

### ✅ **ALLOWED in Main Branch:**
```
modules/               # WSP-compliant modules
docs/                  # Documentation
WSP_*/                 # WSP framework files
prompt/                # Prompt templates
tools/                 # Development tools
tests/                 # Test files
*.md                   # Markdown documentation
requirements.txt       # Dependencies
.gitignore            # Git ignore rules
```

## 🔄 Mandatory Workflow

### **File Creation Protocol:**
1. **Pre-Creation Check**: Validate against prohibited patterns
2. **Branch Validation**: Ensure appropriate branch for file type
3. **WSP Compliance**: Verify file follows WSP standards
4. **Approval Gate**: Get explicit approval for main branch files

### **Branch Strategy:**
```
main                   # Production-ready, WSP-compliant only
feature/*             # New development work
fix/*                 # Bug fixes  
refactor/*            # Code restructuring
temp/*                # Temporary work (auto-cleanup)
build/*               # Build/deployment branches (ephemeral)
```

## 🛡️ Enforcement Mechanisms

### **1. WSP_INIT Integration**
```python
# Before any file creation
def create_file(filepath, content):
    valid, message = validate_file_creation(filepath, current_branch())
    if not valid:
        raise WSPViolationError(message)
    
    # Proceed with creation
    write_file(filepath, content)
```

### **2. Pre-Commit Hooks**
```bash
#!/bin/bash
# .git/hooks/pre-commit
python tools/wsp34_validator.py --check-files
if [ $? -ne 0 ]; then
    echo "❌ WSP 34 violation detected. Commit blocked."
    exit 1
fi
```

### **3. Branch Protection Rules**
- **Main branch**: Require PR + review + WSP validation
- **Direct pushes**: BLOCKED
- **Force pushes**: BLOCKED  
- **Required checks**: FMAS, pytest, WSP 34 validation

## 🧹 Cleanup Protocol

### **Immediate Actions:**
1. **Move temp files** to appropriate branches or delete
2. **Clean recursive builds** - remove nested build folders
3. **Update .gitignore** with WSP 34 patterns
4. **Implement validation** in WSP_INIT

### **Ongoing Maintenance:**
```bash
# Daily cleanup script
find . -name "temp_*" -type f -delete
find . -name "*_clean*" -type d -exec rm -rf {} +
find . -path "*/build/foundups-agent-clean/build" -exec rm -rf {} +
```

## 🔗 Integration Points

- **WSP_INIT**: File creation validation
- **WSP 7**: Git branch discipline  
- **WSP 2**: Clean state management
- **0102 Completion**: Pre-commit validation

## 📋 Validation Checklist

Before any commit to main:
- [ ] No temp files present
- [ ] No recursive build folders
- [ ] All files follow WSP patterns
- [ ] FMAS audit passes
- [ ] Tests pass
- [ ] Coverage targets met

---

**🚀 Result**: Clean, disciplined git workflow with automatic temp file prevention and WSP compliance enforcement. 