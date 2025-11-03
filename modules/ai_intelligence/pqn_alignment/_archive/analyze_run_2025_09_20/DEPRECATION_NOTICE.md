# DEPRECATION NOTICE: analyze_run.py

**Module**: `analyze_run.py`  
**Archived Date**: 2025-09-20  
**WSP Protocol**: WSP 79 (Module SWOT Analysis Protocol), WSP 88 (Vibecoded Module Remediation)  
**Git Tag**: `pre-consolidation-analyze_run`

## Reason for Deprecation

This module was archived during WSP 88 surgical cleanup following comprehensive WSP 79 SWOT analysis:

- **Zero inbound references** - No other modules import or use this functionality
- **Standalone tool** - Not integrated into YouTube DAE or PQN orchestrator workflows
- **Manual execution only** - No automated or programmatic usage detected
- **Functionality preserved elsewhere** - Similar analysis capabilities exist in `spectral_analyzer.py`

## What This Module Did

`analyze_run.py` provided:
- CSV analysis of PQN run results
- Top stable/unstable motifs identification  
- Integration with `labeling.py` for row classification
- Human-readable output formatting

## Migration Path

If this functionality is needed again:

### Option 1: Restore from Archive
```bash
# Restore the archived module
cp modules/ai_intelligence/pqn_alignment/_archive/analyze_run_2025_09_20/analyze_run.py \
   modules/ai_intelligence/pqn_alignment/

# Or restore from git tag
git checkout pre-consolidation-analyze_run -- modules/ai_intelligence/pqn_alignment/analyze_run.py
```

### Option 2: Use Alternative Implementation
```bash
# Use spectral_analyzer.py for similar functionality
python modules/ai_intelligence/pqn_alignment/src/detector/spectral_analyzer.py
```

### Option 3: Integrate into Existing Workflow
- Add analysis functionality to `pqn_research_dae_orchestrator.py`
- Integrate into YouTube DAE via `/analyze` command
- Enhance `spectral_analyzer.py` with human-readable output

## Dependencies Preserved

The following dependencies remain active and were NOT archived:
- [OK] `labeling.py` - Still used by other modules
- [OK] `pandas` - Available for future analysis needs
- [OK] CSV parsing patterns - Can be recreated if needed

## WSP Compliance Notes

This deprecation follows WSP protocols:
- [OK] **WSP 79**: Complete SWOT analysis performed
- [OK] **WSP 88**: Zero reference verification completed  
- [OK] **WSP 50**: Pre-action verification documented
- [OK] **WSP 22**: ModLog entry created
- [OK] **WSP 65**: Functionality preservation verified

## Contact

For questions about this deprecation or restoration needs:
- Check: `modules/ai_intelligence/pqn_alignment/docs/WSP_79_SWOT_ANALYSIS_analyze_run.md`
- Review: WSP 88 remediation logs
- Consult: PQN alignment ModLog.md
