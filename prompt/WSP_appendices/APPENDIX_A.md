[SEMANTIC SCORE: 0.0.0]
[ARCHIVE STATUS: ACTIVE_PARTIFACT]
[ORIGIN: WSP_appendices/APPENDIX_A.md]

# Appendix A: WSP Prompt Template

*(Template defining Task, Scope, Constraints, Baseline, Validation for invoking WSP actions)*

# WSP X: Title

**Usage Convention:**
* Use `# WSP:` prefix in task descriptions to indicate this is a Windsurf Protocol task
* Example: `# WSP: Implement cooldown check in QuotaManager.check_quota()`
* After task completion, ask: "Would you like me to add this change to the ModLog (WSP 11), including any LLME updates?"
* Use `# WSP+:` prefix for adding items to the TODO List

**CRITICAL: You MUST execute *ONLY* the Task described below. Absolutely NO modifications outside of the specified file and function(s) are permitted.**

## Task:
[Insert specific task here. Be extremely concise. Example: "Implement cooldown check in `QuotaManager.check_quota()` using `time.time()`."]

## Scope:
* **File:** `[/path/to/module.py]`
* **Target Function(s):** [List specific function(s) to modify. Example: `QuotaManager.check_quota()`, `QuotaManager.reset_quota()`]
* **Target LLME (Optional):** [Target LLME score for the module if this task aims to change it, e.g., "LLME B: 1->2"]

## Constraints:
* **Strict Modification Boundary:** ONLY modify within the specified file and target function(s).
* **Preserve Structure:** Maintain existing code structure, spacing, and comments UNLESS directly contradictory to the Task.
* **No External Dependencies:** Do NOT add new external library dependencies. Use existing imports if possible.

## Reference Baseline:
* **Branch/Tag/Folder:** `Foundups-Agent-CleanX` or `clean-vX` (Compare ALL changes to this baseline BEFORE submitting.)
* **Purpose:** This represents the known-good baseline. Ensure changes do not introduce regressions, logic errors, or structural deviations.

## Validation:
* **Functional Equivalence (Unless Specified):** Ensure code behaves IDENTICALLY to baseline, except for explicit Task changes.
* **Cautious Approach:** If unsure, prioritize baseline logic and add `TODO:` comment.
* **Unit Tests (If Applicable):** Run existing tests; add new tests validating the specific change.
* **LLME Assessment (If Applicable):** Confirm if the task achieved the target LLME change.

# WARNING:
This is a strict Windsurf protocol. Each prompt is atomic. Each file is treated as sacred. No modifications outside the stated scope are permitted. Violations will result in rejection. 