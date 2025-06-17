# WSP 34: Git Operations and Documentation Protocol
- **Status:** Active
- **Purpose:** To establish a single, authoritative protocol for all Git-related activities, ensuring a clean history and standardized test documentation.
- **Trigger:** On any Git operation (commit, push, branch creation); during CI validation.
- **Input:** A proposed Git action (e.g., a commit with staged files).
- **Output:** A compliant Git history, with all actions adhering to branching, commit message, and test documentation standards.
- **Responsible Agent(s):** ComplianceAgent, all agents interacting with the repository.

**Supersedes**: WSP 13

## 1. Purpose

To establish a single, authoritative protocol for all Git-related activities and associated documentation standards. This ensures a clean, navigable project history, prevents repository pollution, enforces development best practices, and standardizes the documentation of test strategies.

## 2. Branching Strategy

All branches **must** follow a standardized naming convention based on their purpose. The `main` branch is protected and must not be committed to directly.

-   **`main`**: The current stable, production-ready state.
-   **`feature/<description>`**: For new features (e.g., `feature/linkedin-agent-poc`).
-   **`fix/<description>`**: For bug fixes (e.g., `fix/unicode-encode-error`).
-   **`refactor/<description>`**: For code refactoring (e.g., `refactor/modularize-llm-client`).
-   **`docs/<description>`**: For documentation-only changes (e.g., `docs/update-wsp-34`).
-   **`test/<description>`**: For adding or improving tests (e.g., `test/add-coverage-for-oauth`).
-   **`temp/<description>`**: For temporary experiments (must be deleted after use).

## 3. Commit Message Formatting (Conventional Commits)

All commit messages **must** follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

-   **Format**: `<type>(<scope>): <subject>`
-   **Type**: Must be one of `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `build`, `ci`, `chore`, `perf`.
-   **Scope**: The name of the module or component affected (e.g., `WRE`, `LLMClient`, `WSP-34`).
-   **Subject**: Must be lowercase, present tense, and without a period.
-   **Example**: `feat(agent): implement git operations protocol`

## 4. Test Documentation Protocol

-   **Requirement**: Every module's `tests/` directory **must** contain a `README.md` file.
-   **Content**: This file must clearly document the testing strategy for the module, explain the purpose of each test file, and describe any common patterns, mocks, or fixtures used. It serves as the primary reference for understanding how to validate the module.
-   **Verification**: The existence of this file is validated by the **FMAS Validation Protocol (WSP 4)**.

## 5. Main Branch Protection & Prohibited Patterns

The `main` branch is protected by the rules defined in the repository's `.gitignore` file. Any temporary files, logs, or build artifacts must be added to `.gitignore` and are strictly prohibited from being committed.

## 6. Enforcement Mechanisms

-   **Pre-Commit Hooks**: Local hooks must be used to lint commit messages and run the **Comprehensive Test Audit (WSP 6)**. A failing audit will block the commit.
-   **Pull Requests (PRs)**: All changes targeting `main` must be submitted via a PR.
-   **CI Pipeline**: The CI pipeline will enforce all checks, including the `FMAS Validation (WSP 4)` and the `Comprehensive Test Audit (WSP 6)`, before a PR can be merged.

## 7. Integration Points

This protocol is a dependency for, or is depended on by:
-   **WSP 4**: FMAS Validation Protocol
-   **WSP 6**: Comprehensive Test Audit Protocol
-   **WSP 7**: Test-Validated Commit Protocol
-   `ComplianceAgent`: Responsible for auditing compliance with this protocol.

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