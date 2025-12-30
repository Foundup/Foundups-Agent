# wsp-change

## Description
Make a change in this repo while staying WSP-compliant (search-first → minimal edit → docs sync).

## Steps
1. Classify the request:
   - Bug fix / feature / refactor / compliance / docs-only.
2. Pre-action verification:
   - Consult `@NAVIGATION.py`.
   - Run `python holo_index.py --search "<task phrase>"` to find existing code and prior patterns.
3. Identify target module(s) and confirm domain placement (WSP 3).
4. Read (in order) the module’s `README.md`, `INTERFACE.md`, `ROADMAP.md`, `ModLog.md`, and `tests/README.md`.
5. Implement the smallest working change. Prefer enhancement over new files (WSP 84).
6. Validate using existing validation tooling (e.g., FMAS: `tools/modular_audit/modular_audit.py`) and any module scripts.
7. Update module docs in the same change set:
   - README / INTERFACE / ROADMAP / ModLog / tests/README.
8. If an issue is a module-evolution mismatch, log it (don’t “fix everything”) in:
   - `@WSP_framework/src/WSP_MODULE_VIOLATIONS.md`.

