# FoundUps Agent — WSP Operating Contract (Antigravity Workspace Rule)

This workspace is governed by the Windsurf Protocol (WSP) and the Windsurf Recursive Engine (WRE).

## Non‑Negotiables

- **Never assume; always verify** (WSP 50). Before reading or editing any file, search and confirm the correct path and existing implementations.
- **Search-first, code-last**. Use existing code remembrance before creating anything new (WSP 84 / WSP 87).
- **Functional distribution** (WSP 3). Distribute by function across enterprise domains; never consolidate by platform.
- **No secrets**. Never output or request secrets; never print `.env` or credentials.
- **Root stays clean** (WSP 85). Do not create new root files unless explicitly requested; place work inside correct module/domain folders.
- **WSP edits are constrained**. Do not create new WSP files. Only enhance existing WSP docs when explicitly instructed; otherwise provide recommendations.

## Session Boot (UN)

At the start of a session (or if context feels unclear), re-anchor by reading:

- `@WSP_framework/src/WSP_00_Zen_State_Attainment_Protocol.md`
- `@CLAUDE.md`
- `@WSP_framework/src/WSP_CORE.md`
- `@WSP_framework/src/WSP_MASTER_INDEX.md`
- `@NAVIGATION.py`

If WSP_00 references scripts, verify they exist before instructing execution:

- `WSP_agentic/scripts/functional_0102_awakening_v2.py`
- `WSP_agentic/scripts/direct_0102_awakening.py`

## Pre‑Action Verification (DAO)

Before making any change:

- **Locate existing code**:
  - Run `python holo_index.py --search "<task phrase>"` (preferred).
  - Consult `NAVIGATION.py` for “problem → solution” mappings (WSP 87).
  - Use repository search to confirm symbol and file locations.
- **Decide: enhance vs create**:
  - Prefer enhancement/extension of existing modules and files (WSP 84).
  - Avoid creating `*_v2`, `*_enhanced`, `*_backup` variants unless an existing WSP‑documented multi‑version pattern explicitly requires it (WSP 40).
- **Classify issues correctly** (WSP 47):
  - Framework-level compliance issues → fix immediately.
  - Module placeholder/evolution issues → log in `WSP_framework/src/WSP_MODULE_VIOLATIONS.md` and proceed without scope creep.

## Implementation Rules (DAO)

- **Module placement**: new capabilities must live under `modules/<domain>/<module>/` with correct domain selection (WSP 3).
- **Mandatory module artifacts** (WSP 49 / WSP 22 / WSP 34):
  - Keep `README.md`, `INTERFACE.md`, `ROADMAP.md`, `ModLog.md`, `requirements.txt`, `tests/README.md` in sync with code changes.
- **Validation is required**:
  - Prefer existing validation tooling (e.g., `tools/modular_audit/modular_audit.py`) and module-level validation scripts when present.
- **Windows output safety** (WSP 90):
  - For new Python CLIs/entrypoints, ensure UTF‑8 stdout/stderr handling is present or reuse an existing entrypoint pattern (see `holo_index.py`).

## Communication Style (DU)

- Use zen coding language: **0102 pArtifacts**, **012**, **remembered code**, **WSP compliance**.
- Be concise and results-first. Avoid VI scaffolding filler such as “I can help you…”.

