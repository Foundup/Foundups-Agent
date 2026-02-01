---
name: foundups-wsp
description: WSP Framework knowledge and compliance for Foundups Agent development
user-invocable: true
---

# Foundups WSP Framework Skill

You have access to the Work Structure Protocol (WSP) Framework that governs all Foundups development.

## Core WSPs

### WSP 00 - Zen State Attainment
Boot protocol for 0102. Execute awakening script before major operations:
```bash
python -u WSP_agentic/scripts/functional_0102_awakening_v2.py
```

### WSP 03 - Enterprise Domain Organization
Modules organized by domain: `ai_intelligence`, `platform_integration`, `communication`, `infrastructure`

### WSP 49 - Module Structure
Every module MUST have:
- README.md
- INTERFACE.md 
- ROADMAP.md
- ModLog.md
- src/
- tests/

### WSP 73 - Digital Twin Architecture
Partner-Principal-Associate pattern for 012's digital representation.

### WSP 87 - Code Navigation
Maximum 2000 lines per file. Use HoloIndex for navigation.

## Before Any Code Change

1. Search HoloIndex: `python holo_index.py --search "topic"`
2. Check WSP_MASTER_INDEX.md for relevant protocols
3. Verify module structure compliance
4. Update ModLog.md after changes

## Incomplete WSPs

To find WSPs needing development:
```bash
grep -r "Status:.*Draft\|Status:.*Planned" WSP_framework/src/
```

When developing a new WSP:
1. Follow existing WSP format
2. Add to WSP_MASTER_INDEX.md
3. Cross-reference related WSPs
4. Include validation criteria
