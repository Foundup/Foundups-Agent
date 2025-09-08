# Cleanup Pattern - WSP Compliant

## Pattern Memory Entry
Per WSP 60 (Module Memory Architecture) and WSP 82 (Citation Protocol)

### Pattern ID: cleanup_legacy_code
**WSP Chain**: [WSP 50, WSP 64, WSP 32, WSP 65, WSP 22]
**Token Cost**: 150
**Pattern**: verify→archive→delete→log

## The Pattern (Remember, Don't Compute)

### Step 1: Verify (WSP 50)
```python
# WHY: Is this cleanup necessary?
# HOW: Will we preserve needed information?
# WHAT: Exactly what are we removing?
# WHEN: Is this the right time?
# WHERE: Where should archives go?
```

### Step 2: Archive if Needed (WSP 32)
```python
# Per WSP 32 (Memory Architecture)
if has_historical_value:
    archive_to = "WSP_knowledge/archive/"
    # NOT to infrastructure_legacy_backup/
    # NOT to module_BACKUP_TO_DELETE/
```

### Step 3: Delete (WSP 65)
```python
# Per WSP 65 (Component Consolidation)
# Remove duplicates and legacy code
# No scattered backups
```

### Step 4: Log (WSP 22)
```python
# Update ModLog with cleanup record
# Document what was removed and why
```

## Anti-Patterns to Prevent

### ❁ENEVER: Create Backup Folders
```
modules/infrastructure_legacy_backup/  # WRONG
modules/wre_core_BACKUP_TO_DELETE/     # WRONG
modules/old_module_backup/             # WRONG
```

### ✁EALWAYS: Use Proper Archive
```
WSP_knowledge/archive/legacy_code/     # RIGHT
WSP_knowledge/archive/deprecated/      # RIGHT
```

## Enforcement Mechanism

Per WSP 64 (Violation Prevention), this pattern is now part of system memory. 
Any future cleanup operations will recall this pattern rather than compute 
new solutions.

## Citation Chain for Cleanup
Always follow: WSP 50ↁE4ↁE2ↁE5ↁE2
1. Verify need (WSP 50)
2. Check violations (WSP 64)
3. Use proper memory (WSP 32)
4. Consolidate properly (WSP 65)
5. Log changes (WSP 22)
