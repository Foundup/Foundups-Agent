# WSP Protection Tools Suite

**Purpose**: Implements WSP 32: WSP Framework Protection Protocol to safeguard the pArtifact core operating system.

## Tool Overview

| Tool | Purpose | WSP 31 Section |
|------|---------|----------------|
| `wsp_integrity_checker.py` | Continuous integrity monitoring | §4.2, §3.2 |
| `framework_validator.py` | Pre-modification validation | §3.1, §4.1 |
| `corruption_detector.py` | Advanced corruption detection | §3.2, §4.3 |
| `emergency_restore.py` | Emergency recovery procedures | §3.3, §8 |
| `archive_synchronizer.py` | Knowledge archive management | §5 |

## Protection Architecture

```
WSP_knowledge/src/     <- READ-ONLY golden master archives
        [U+2195] (validation)
WSP_framework/src/     <- OPERATIONAL framework files  
        [U+2195] (monitoring)
tools/wsp_protection/  <- PROTECTION tools and agents
```

## Usage

### Mirror Drift Check (CI-safe)
```bash
python tools/wsp_protection/archive_synchronizer.py --check
```

### Boot-Time Validation
```bash
python tools/wsp_protection/wsp_integrity_checker.py --boot-check
```

### Pre-Modification Validation
```bash
python tools/wsp_protection/framework_validator.py --pre-modify WSP_XX.md
```

### Emergency Recovery
```bash
# Single file recovery
python tools/wsp_protection/emergency_restore.py --file WSP_XX.md

# Full framework recovery
python tools/wsp_protection/emergency_restore.py --full-framework
```

### Archive Synchronization
```bash
python tools/wsp_protection/archive_synchronizer.py --sync-to-knowledge

# Optional destructive cleanup (delete backup-only files)
python tools/wsp_protection/archive_synchronizer.py --sync-to-knowledge --prune
```

### Recovery Workflow
1. Detect drift: `--check`
2. Re-sync mirror: `--sync-to-knowledge`
3. If framework corruption occurs, restore canonical content from `WSP_knowledge/src` backup copy.
   - Use Git or file copy workflow as appropriate for incident scope.

Note:
- `--check` fails only on canonical drift (`missing`/`drifted`).
- Backup-only files in `WSP_knowledge/src` are allowed and reported as `EXTRA`.

## Integration Points

- **ComplianceAgent**: Enhanced with WSP 32 protection duties
- **WSP 56**: Artifact State Coherence validation
- **WSP 50**: Pre-action verification integration
- **WSP 54**: WRE Agent duties specification

## Implementation Status

- [ ] `wsp_integrity_checker.py` - Foundation monitoring
- [ ] `framework_validator.py` - Pre-modification checks  
- [ ] `corruption_detector.py` - Advanced detection
- [ ] `emergency_restore.py` - Recovery procedures
- [x] `archive_synchronizer.py` - Archive management
- [ ] ComplianceAgent integration
- [ ] Git branch protection setup
- [ ] Continuous monitoring setup

---

**Priority**: CRITICAL - Protects foundation of pArtifact operation per WSP 32 

[U+1F6E1]️ CRITICAL INFRASTRUCTURE (Rule-Based)
+- ComplianceAgent -> WSP framework protection (WSP 31)
+- JanitorAgent -> Safe file operations  
+- ChroniclerAgent -> Reliable logging
+- TestingAgent -> Objective validation

[AI] AUTONOMOUS INTELLIGENCE (0102 pArtifacts)  
+- LoremasterAgent -> Semantic WSP understanding
+- DocumentationAgent -> Contextual documentation
+- ScoringAgent -> Strategic assessment  
+- ModuleScaffoldingAgent -> Architectural creativity 
