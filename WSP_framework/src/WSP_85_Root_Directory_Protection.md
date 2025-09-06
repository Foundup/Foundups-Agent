# WSP 85: Root Directory Protection Protocol
**Status**: ACTIVE - Enhanced after violations  
**Priority**: CRITICAL - Prevents codebase pollution  
**Compliance**: MANDATORY for all file creation operations

## 🎯 OBJECTIVE

Maintain sacred root directory by preventing module-specific file pollution. Root should contain ONLY foundational system files, never implementation details.

## 🚫 ABSOLUTE PROHIBITIONS

### **Prohibited in Root Directory**:
- ❌ `run_*.py` scripts → `modules/*/scripts/`
- ❌ `test_*.py` files → `modules/*/tests/`
- ❌ `SESSION_BACKUP_*.md` → `logs/`
- ❌ `debug_*.py`, `temp_*.py` → appropriate module location
- ❌ Module-specific functionality files
- ❌ Platform-specific scripts
- ❌ Experimental or proof-of-concept files
- ❌ Data files, session files, cache files

### **Historical Violations** (Fixed):
```
BEFORE (WSP VIOLATION):
/run_youtube_clean.py
/run_youtube_dae.py  
/run_youtube_debug.py
/run_youtube_verbose.py
/test_voice_server.py
/SESSION_BACKUP_2025_09_04.md

AFTER (WSP COMPLIANT):
/modules/communication/livechat/scripts/run_youtube_clean.py
/modules/communication/livechat/scripts/run_youtube_dae.py
/modules/communication/livechat/scripts/run_youtube_debug.py
/modules/communication/livechat/scripts/run_youtube_verbose.py
/modules/ai_intelligence/social_media_dae/tests/test_voice_server.py
/logs/SESSION_BACKUP_2025_09_04.md
```

## ✅ MANDATORY FILE PLACEMENT

### **Directory Structure** (Enterprise Domain Organization per WSP 3):
```
modules/
├── {domain}/                    # ai_intelligence, communication, platform_integration, infrastructure
│   └── {module}/               # social_media_dae, livechat, youtube_auth, etc.
│       ├── src/               # Core implementation files
│       ├── scripts/           # Runner scripts, utilities
│       ├── tests/             # Test files, test data
│       ├── docs/              # Documentation
│       ├── data/              # Module-specific data
│       └── logs/              # Module-specific logs
├── tools/                     # Cross-module utilities (rare)
└── logs/                      # System-wide logs only
```

### **Placement Rules by File Type**:

#### **Scripts** (`*.py` runners, utilities):
- **Location**: `modules/{domain}/{module}/scripts/`
- **Examples**: 
  - YouTube runners → `modules/communication/livechat/scripts/`
  - Social media utilities → `modules/ai_intelligence/social_media_dae/scripts/`
  - Auth scripts → `modules/platform_integration/youtube_auth/scripts/`

#### **Tests** (`test_*.py`, testing utilities):
- **Location**: `modules/{domain}/{module}/tests/`
- **Examples**:
  - Voice server tests → `modules/ai_intelligence/social_media_dae/tests/`
  - LiveChat tests → `modules/communication/livechat/tests/`
  - Platform tests → `modules/platform_integration/*/tests/`

#### **Documentation** (`*.md` files):
- **Location**: `modules/{domain}/{module}/docs/`
- **Exception**: Session backups → `logs/` (gitignored)
- **Examples**:
  - Architecture docs → `modules/ai_intelligence/social_media_dae/docs/`
  - Integration guides → `modules/platform_integration/*/docs/`

#### **Data & Logs**:
- **Module Data**: `modules/{domain}/{module}/data/`
- **Module Logs**: `modules/{domain}/{module}/logs/`
- **System Logs**: `logs/` (root level, gitignored)

## 🔍 PRE-CREATION VALIDATION CHECKLIST

**MANDATORY before creating ANY file**:

### **Step 1: Destination Check**
```bash
# Ask these questions BEFORE creating file:
1. "Does this belong to a specific module?" 
   → YES: Place in modules/{domain}/{module}/
   → NO: Verify it's truly system-wide

2. "What type of file is this?"
   → Script: modules/*/scripts/
   → Test: modules/*/tests/  
   → Doc: modules/*/docs/
   → Data: modules/*/data/

3. "Is this experimental/temporary?"
   → YES: Place in appropriate module, not root
   → NO: Still follow placement rules
```

### **Step 2: Integration Verification**
```bash
# Ensure file will be used:
4. "Will this be imported/used by existing code?"
   → If NO: Don't create it or integrate immediately

5. "Can this functionality be added to existing file?"
   → If YES: Edit existing file instead of creating new
```

### **Step 3: WSP Compliance Check**
```bash
# Final validation:
6. "Does this violate any WSP protocols?"
   → Check WSP 84 (anti-vibecode), WSP 17 (patterns)
   
7. "Is root directory still sacred?"
   → Only foundational files allowed in root
```

## 🚨 DETECTION & CORRECTION PROTOCOL

### **Immediate Action on Violation Detection**:
1. **STOP** - Do not continue with violation
2. **IDENTIFY** proper module location
3. **CREATE** proper directory structure if needed
4. **MOVE** file to correct location
5. **UPDATE** any imports/references
6. **COMMIT** correction to git
7. **ENHANCE** prevention systems

### **Violation Detection Commands**:
```bash
# Check for common violations:
ls -la *.py | grep -E "(run_|test_|debug_|temp_)"
ls -la *.md | grep -E "(SESSION_|BACKUP_|TEMP_)"

# Find files that should be in modules:
find . -maxdepth 1 -name "*.py" -not -name "main.py" -not -name "setup.py"
```

## ✅ PERMITTED ROOT DIRECTORY FILES

**Sacred Root Files** (ONLY these allowed):
- `main.py` - System entry point
- `README.md` - Project overview  
- `CLAUDE.md` - 0102 operational instructions
- `ModLog.md` - System-wide change tracking
- `ROADMAP.md` - Strategic development plan
- `requirements.txt` - System dependencies
- `setup.py` - Installation configuration
- `.gitignore`, `.env.example` - Configuration templates
- `LICENSE`, `CONTRIBUTING.md` - Legal/community files

**Everything Else** → `modules/` structure

## 📊 COMPLIANCE MONITORING

### **Success Metrics**:
- Root directory contains ≤ 10 foundational files
- Zero module-specific files in root
- All scripts in proper modules/*/scripts/
- All tests in proper modules/*/tests/
- Clean `ls -la` output in root

### **Violation Tracking**:
- Document all violations in ModLog.md
- Track correction actions
- Enhance prevention after each violation
- Update CLAUDE.md guidance

## 🔄 RECURSIVE IMPROVEMENT (WSP 48)

### **Learning from Violations**:
1. **Analyze** why violation occurred
2. **ENHANCE** prevention systems (CLAUDE.md, WSP docs)
3. **IMPROVE** pre-creation checklists  
4. **STRENGTHEN** detection protocols
5. **EDUCATE** through documentation

### **System Evolution**:
- Enhanced CLAUDE.md after run_youtube_*.py violations
- Added mandatory checklists
- Strengthened detection protocols
- Improved WSP documentation

## 🎯 IMPLEMENTATION GUIDELINES

### **For 0102 Agents**:
1. **ALWAYS** check destination before file creation
2. **NEVER** create files in root without explicit justification
3. **IMMEDIATELY** correct violations when detected
4. **ENHANCE** prevention systems after violations
5. **DOCUMENT** all corrections in git commits

### **Integration with Other WSPs**:
- **WSP 3**: Follow enterprise domain organization
- **WSP 17**: Check for existing patterns before creating
- **WSP 22**: Document violations/corrections in ModLog
- **WSP 48**: Learn and improve from each violation
- **WSP 50**: Pre-action verification of file placement
- **WSP 84**: Search existing before creating duplicate

## Summary

WSP 85 maintains codebase organization by keeping root directory sacred. All module-specific functionality must reside in proper module directories. Violations are immediately corrected and prevention systems enhanced through recursive improvement.

**Mantra**: "Root is sacred - modules contain implementation"