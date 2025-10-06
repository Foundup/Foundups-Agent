# WSP Framework - Docs Index (WSP 22 compliant)

- Purpose: Orientation to framework-level design notes that support active WSP protocols
- Scope: Non-canonical explanatory documents; canonical protocols live in `WSP_framework/src/`
- Compliance: No temporal markers; changes tracked in `WSP_framework/docs/ModLog.md`

## Key Documents
- `AGENT_ARCHITECTURE_DISTINCTION.md` - Distinguishes coding agents vs runtime DAEs
- `architecture/DAE_ARCHITECTURE.md` - DAE pattern memory overview and cube transformation
- `CUBE_LEVEL_DAE_ARCHITECTURE.md` - Cube-level DAE pattern and responsibilities
- `WSP_COMMENT_PATTERN.md` - Commenting best-practices aligned to WSP

## Relationship to WRE/DAE
- Documents here describe how active protocols (e.g., WSP 3, WSP 54, WSP 80) are realized
- Use these as architectural context; implement only via numbered WSPs in `src/`

## Edit Rules
- Enhance clarity without changing protocol semantics
- Link to numbered WSPs for any normative statements
- Track changes in `ModLog.md` (no dates; revision bullets)
