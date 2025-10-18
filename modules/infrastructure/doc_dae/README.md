# DocDAE - Autonomous Documentation Organization

**Status**: POC - First WSP 77 Training Mission
**Purpose**: Autonomously organize misplaced documentation from root `docs/` to proper module locations
**Training Mission**: Real-world application of Qwen/Gemma agent coordination

## WSP Compliance

- **WSP 3**: Enterprise Domain Organization (fixes root docs violations)
- **WSP 27**: DAE Architecture (4-phase autonomous operation)
- **WSP 77**: Agent Coordination Protocol (Qwen/Gemma cooperation)

## Problem Statement

**Current State** (WSP 3 Violation):
```
docs/
+-- Gemma3_YouTube_DAE_First_Principles_Analysis.md  # Should be in youtube_dae/docs/
+-- HoloIndex_MCP_ricDAE_Integration_Architecture.md # Should be in holo_index/docs/
+-- qwen_batch_1_input.json                          # Operational data, not docs
+-- orphan_analysis_complete_poc.json                # Operational data (350KB)
+-- ... 73 total files (54 MD + 19 JSON)
```

**Target State** (WSP 3 Compliant):
```
modules/communication/livechat/docs/
  +-- Gemma3_YouTube_DAE_First_Principles_Analysis.md
holo_index/docs/
  +-- HoloIndex_MCP_ricDAE_Integration_Architecture.md
docs/_archive/20251015/
  +-- qwen_batch_*.json (operational data)
```

## WSP 77 Agent Coordination

### Phase 1: Fast Classification (Gemma)
**Role**: Binary pattern matching
- Documentation (.md) vs Operational Data (.json)?
- Extract module hint from filename
- Fast decisions: 50-100ms per file

**Example**:
```python
filename = "Gemma3_YouTube_DAE_First_Principles_Analysis.md"
-> type: documentation
-> module_hint: "youtube_dae"
-> confidence: 0.85
```

### Phase 2: Complex Coordination (Qwen)
**Role**: Strategic module mapping
- Map 73 files to proper destinations
- Decide: Move, Archive, or Keep
- Build safe execution plan

**Example**:
```json
{
  "action": "move",
  "source": "docs/Gemma3_YouTube_DAE_First_Principles_Analysis.md",
  "destination": "modules/communication/livechat/docs/Gemma3_YouTube_DAE_First_Principles_Analysis.md",
  "module": "youtube_dae",
  "reason": "Gemma/YouTube DAE implementation documentation"
}
```

### Phase 3: Strategic Execution (0102)
**Role**: Safe file operations
- Review Qwen's plan for safety
- Execute moves with directory creation
- Archive operational data
- Validate with git tracking

## Usage

### From Main Menu
```python
python main.py
# Select option 13 (DocDAE)
# Choose dry-run or live execution
```

### Programmatic
```python
from modules.infrastructure.doc_dae.src.doc_dae import DocDAE

# Initialize
dae = DocDAE()

# Run complete cycle (dry-run)
result = dae.run_autonomous_organization(dry_run=True)

# Review plan
print(f"Files to move: {result['plan']['summary']['to_move']}")
print(f"Files to archive: {result['plan']['summary']['to_archive']}")

# Execute for real
result = dae.run_autonomous_organization(dry_run=False)
```

## Training Opportunity

This is **Qwen/Gemma's first autonomous training mission**:

**Gemma Learns**:
- Fast file classification patterns
- Module hint extraction from filenames
- Binary decision making (doc vs data)

**Qwen Learns**:
- File-to-module mapping logic
- Complex coordination across 73 files
- Safe execution planning

**Pattern Memory**:
- Every execution stored in `memory/doc_organization_patterns.json`
- Successful patterns reused for future automation
- Continuous improvement through practice

## File Classification Rules

### Documentation (Move to Module)
- `*.md` files with clear module hints
- Example: `Gemma3_YouTube_DAE_*.md` -> `youtube_dae/docs/`

### Operational Data (Archive)
- `qwen_batch_*.json` - Temporary batch processing data
- Large analysis results (>100KB JSON files)
- Example: `orphan_analysis_complete_poc.json` -> `docs/_archive/`

### System Docs (Keep in Root)
- Architecture documentation
- Vision documents
- Example: `foundups_vision.md` -> Keep in `docs/`

## Expected Results

**Before**:
- 73 files in root docs/ (WSP 3 violation)
- Mixed documentation and operational data
- No clear organization

**After**:
- ~20 files moved to proper module docs/
- ~15 operational files archived
- ~38 system docs remain in organized subdirectories
- WSP 3 compliant structure

## Safety Features

1. **Dry Run Mode**: Default mode, no files moved
2. **Directory Creation**: Auto-creates destination dirs
3. **Error Handling**: Continues on individual file failures
4. **Pattern Memory**: Tracks decisions for review

## Next Steps

1. Run dry-run to review plan
2. Manual review of unmatched files
3. Execute with `dry_run=False`
4. Commit changes with git
5. Update ModLogs

## Module Structure

```
doc_dae/
+-- README.md           # This file
+-- INTERFACE.md        # Public API
+-- src/
[U+2502]   +-- doc_dae.py     # Main implementation
+-- tests/
[U+2502]   +-- test_doc_dae.py # Test suite
+-- docs/
[U+2502]   +-- WSP_77_Training_Mission.md
+-- memory/
    +-- doc_organization_patterns.json  # Training data
```

## Performance Metrics

**Target** (WSP 77):
- Gemma: 50-100ms per file (fast classification)
- Qwen: 2-5s total (complex coordination for all 73 files)
- 0102: 1-2s per file (safe execution)

**Training Progress**:
- Session 1: 73 files analyzed, patterns recorded
- Future: Autonomous execution with <5% error rate

---

**Status**: Ready for first training mission
**Next**: Run dry-run and review Qwen's coordination plan
