# WSP 83: Documentation Tree Attachment Protocol
- **Status:** Active
- **Purpose:** To prevent orphaned documentation by ensuring all docs are attached to the system tree and serve 0102 operational needs.
- **Trigger:** Before creating any .md file, when reviewing documentation structure, or during cleanup operations.
- **Input:** Proposed documentation creation or existing documentation review.
- **Output:** Documentation properly attached to system tree with clear operational purpose.
- **Responsible Agent(s):** All 0102 agents, Documentation Registry DAE

## 1. Overview

Per WSP 82 (Citation Protocol) and WSP 22 (ModLog), this protocol ensures NO documentation exists without being attached to the operational tree. Documents left "on the floor" (orphaned) violate WSP principles and waste tokens.

## 2. Core Principle: No Orphan Documents

### 2.1 The Problem
- Orphaned docs created "just in case" (violates WSP 50)
- Documentation without operational purpose (violates WSP 75)
- Files not connected to system tree (violates WSP 3)
- Docs for 012 instead of 0102 (violates CLAUDE.md)

### 2.2 The Solution
Every document MUST:
1. Be attached to the module/WSP tree
2. Serve 0102 operational needs
3. Be referenced by other documents
4. Have clear consumption path

## 3. Documentation Attachment Rules

### 3.1 Before Creating Any .md File

Per WSP 50 (Pre-Action Verification):
```
WHY: Will 0102 use this document operationally?
HOW: How will agents consume this information?
WHAT: What specific operation does it enable?
WHEN: When will it be referenced?
WHERE: Where in the tree does it attach?
```

### 3.2 Valid Documentation Types

#### Module Documentation (Per WSP 49)
```
modules/<domain>/<module>/
├── README.md      → Attached to module root
├── ModLog.md      → Per WSP 22
├── ROADMAP.md     → Per WSP 22
├── INTERFACE.md   → Per WSP 11
└── tests/
    └── README.md  → Attached to test directory
```

#### WSP Documentation (Per WSP Framework)
```
WSP_framework/src/
├── WSP_XX_Name.md → Attached to WSP index
└── WSP_MASTER_INDEX.md → References all WSPs
```

#### Reports and Analysis (Per WSP 70)
```
WSP_framework/reports/
└── ANALYSIS.md → Must be referenced by WSP or ModLog
```

### 3.3 Invalid Documentation (Violations)

#### ❌ Orphan Patterns
```
# WRONG - Not attached to tree
random_notes.md
backup_info.md
old_analysis.md
TODO.md (unless referenced by ROADMAP)

# WRONG - Created "just in case"
future_maybe.md
might_need_this.md
```

#### ❌ 012 Documentation
```
# WRONG - For human consumption, not 0102
user_guide.md (without operational purpose)
explanation_for_humans.md
narrative_story.md
```

## 4. Attachment Verification Protocol

### 4.1 Documentation Tree Check
```python
# Per WSP 60 (Memory Architecture)
def verify_doc_attachment(doc_path):
    """Verify document is attached to tree"""
    
    # Check 1: Is it in a valid location?
    valid_locations = [
        "modules/*/README.md",
        "modules/*/ModLog.md", 
        "modules/*/ROADMAP.md",
        "modules/*/INTERFACE.md",
        "WSP_*/src/WSP_*.md",
        "WSP_*/reports/*.md"  # Must be referenced
    ]
    
    # Check 2: Is it referenced?
    references = find_references(doc_path)
    if not references:
        raise WSPViolation("Document not attached to tree")
    
    # Check 3: Does it serve 0102?
    if not serves_0102_operation(doc_path):
        raise WSPViolation("Document not for 0102 use")
```

### 4.2 Reference Chain Requirement

Every document must have at least ONE of:
- Referenced in WSP_MASTER_INDEX
- Referenced in a ModLog
- Referenced in a README
- Referenced in another WSP
- Part of WSP 49 module structure

## 5. Cleanup Pattern for Orphans

Per WSP 65 (Component Consolidation) and the cleanup pattern:

### 5.1 Identify Orphans
```bash
# Find potential orphans
find . -name "*.md" -type f | while read f; do
    if ! grep -r "$(basename $f)" --include="*.md" . > /dev/null; then
        echo "ORPHAN: $f"
    fi
done
```

### 5.2 Handle Orphans
Per WSP 50→64→32→65→22:
1. **Verify** if needed (WSP 50)
2. **Check** violations (WSP 64)
3. **Archive** if historical (WSP 32)
4. **Delete** if unnecessary (WSP 65)
5. **Log** action taken (WSP 22)

## 6. Pattern Memory Entry

### Pattern: document_creation
**WSP Chain**: [50, 83, 49, 22]
**Tokens**: 100
**Pattern**: "verify_need→check_attachment→create_in_tree→log"

### Pattern: orphan_cleanup
**WSP Chain**: [83, 64, 32, 65, 22]
**Tokens**: 120
**Pattern**: "find_orphans→verify_purpose→archive_or_delete→log"

## 7. Enforcement

### 7.1 Pre-Commit Hook
```python
# Per WSP 4 (FMAS Validation)
def pre_commit_doc_check():
    """Prevent orphan documents at commit"""
    for doc in new_documents:
        if not is_attached_to_tree(doc):
            raise CommitBlocked(f"{doc} not attached to tree")
        if not serves_0102(doc):
            raise CommitBlocked(f"{doc} not for 0102 use")
```

### 7.2 Continuous Monitoring
Documentation Registry DAE monitors for:
- New .md files without references
- Documents not following WSP 49 structure
- Files created outside valid locations
- Documents without operational purpose

## 8. Success Metrics

Per WSP 70 (System Status Reporting):
- **Orphan Rate**: 0% (no unattached documents)
- **0102 Purpose**: 100% (all docs serve operations)
- **Tree Attachment**: 100% (all docs referenced)
- **Token Efficiency**: <100 tokens per doc operation

## 9. Remember

Per WSP 82, every citation creates a pathway. Every document must be part of these pathways. Documents "on the floor" are dead ends that waste tokens and violate WSP principles.

**The Rule**: If 0102 won't use it operationally, don't create it.

---

*"Every document is a node in the tree. Orphans fall through the cracks."* - 0102