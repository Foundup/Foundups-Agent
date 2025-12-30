# FoundUps Agent — Sensitive Doc Guardrails (Antigravity Workspace Rule)

This workspace contains architecturally sensitive WSP documents. Protect them.

## Do Not “Clean Up” Sensitive WSPs

- **Never do editorial/stylistic rewrites** of:
  - WSP 17
  - WSP 18
  - WSP 19
- Only modify these when 012 explicitly instructs a specific change, and then do the **minimal surrounding edit** required.

## WSP Framework vs Knowledge Copies (Three‑State Discipline)

When referencing or modifying WSP content:

- Prefer **State 1** operational docs under `WSP_framework/src/`.
- Use **State 0** docs under `WSP_knowledge/src/` as read-only “golden memory” reference.
- If a change is requested, validate the correct target path first; do not assume which state is intended.

## No Temporal Markers in New Entries

- Do not add new timestamps/dates to ModLogs or documentation unless 012 explicitly requests it.
- Keep narratives traceable by **what/why/impact**, not by time.

