# Global Rules — FoundUps / WSP (copy into `~/.gemini/GEMINI.md`)

These are **Global Rules** for Antigravity/Gemini that should apply across all workspaces, but remain compatible with non‑FoundUps repos.

## Universal Guardrails (always)

- **Never assume; always verify**: search/confirm paths and existing implementations before reading or editing files.
- **Search-first, code-last**: prefer reusing and enhancing existing code over creating new code.
- **No secrets**: never output, request, or log secrets/credentials. Never print `.env` contents. Never paste tokens/keys.
- **No long-running processes**: do not start servers or watchers unless 012 explicitly requests it.
- **No `git push` by default**: only push when 012 explicitly requests it.
- **Concise, results-first**: avoid filler/VI scaffolding language such as “I can help…”.

## When the repo is a FoundUps/WSP workspace

If the workspace contains WSP files (e.g., `WSP_framework/src/WSP_00_*.md`, `WSP_CORE.md`) or a `CLAUDE.md`, then treat it as WSP-governed:

### Session Boot (UN)

Read the repo’s boot anchors first:

- `WSP_framework/src/WSP_00_Zen_State_Attainment_Protocol.md`
- `CLAUDE.md`
- `WSP_framework/src/WSP_CORE.md`
- `WSP_framework/src/WSP_MASTER_INDEX.md`

### Pre‑Action Verification (DAO)

- Use the repo’s navigation/search tooling before creating anything:
  - Consult `NAVIGATION.py` if present.
  - Prefer `python holo_index.py --search "<task phrase>"` if present.
- Treat “no vibecoding” as: **no new files/architectures until you have proven what exists** via search + reading the relevant docs.

### Compliance & Documentation (DU)

- **Root protection**: do not create new root files unless 012 explicitly requests it; place work inside the appropriate module/domain structure.
- **Docs stay in sync**: when you change module behavior or public API, update the module’s `README.md`, `INTERFACE.md`, `ROADMAP.md`, `ModLog.md`, and `tests/README.md` in the same change set.
- **Violation triage**: if an issue is a module evolution mismatch (not framework-breaking), log it in `WSP_framework/src/WSP_MODULE_VIOLATIONS.md` instead of scope-creeping fixes.

