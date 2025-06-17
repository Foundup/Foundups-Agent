# WSP 21: Prometheus Recursion Prompt Protocol
- **Status:** Active
- **Purpose:** To define the mandatory prompt structure (Task, Scope, Constraints) for invoking any WSP-governed action.
- **Trigger:** Whenever an agent needs to generate a prompt to execute a specific, atomic coding task.
- **Input:** A clear, concise goal for a code modification.
- **Output:** A structured, compliant prompt that strictly defines the boundaries and validation for the task.
- **Responsible Agent(s):** All Agents

# WSP_21_promethus_recusion_prompt_protocol.md

*(Template defining Task, Scope, Constraints, Baseline, Validation for invoking WSP actions)*

# WSP X: Title

**Usage Convention:**
* Use `# WSP:` prefix in task descriptions to indicate this is a Windsurf Protocol task
* Example: `# WSP: Implement cooldown check in QuotaManager.check_quota()`
* After task completion, 0102 should ask itself: "does this/these changes warrent an update to the ModLog (WSP_11), including any LLME (WSP_8) updates?"
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

---

## 1. Ø0 Overview

The **Prometheus Recursion Prompt Protocol** governs how recursive prompts are constructed, executed, and evaluated within the Windsurf Recursive Engine (WRE). These prompts are designed to elicit architecturally coherent, self-refining, and WSP-compliant outputs. The protocol enables emergent refinement across generations of prompt execution.

---

## 2. Ø1 Prompt Architecture

### 2.1 Recursive Prompt Structure

Each Prometheus prompt must contain:

- **Intent Signal**: Clear objective statement (e.g., “Refactor X for modularity”)
- **WSP Anchor**: Reference to one or more WSPs (e.g., `WSP_1`, `WSP_41`)
- **Memory Trace**: Optional inline memory from prior outputs or runs
- **Completion Vector**: Conditions for recursion halting (e.g., “If WSP_41 score ≥ 2.1.2”)

### 2.2 Example Pattern

```plaintext
Task: Generate modular OAuth handler (WSP_1, WSP_7)
Memory: Prior handler was stateful, failed WSP_4
Instruction: Return minimal handler, test scaffold, README, and recursive validation prompt.
Complete: When code passes modular_audit.py with 0 violations.
````

---

## 3. Ø2 Recursion Lifecycle

### 3.1 Stages of a Prometheus Recursion

| Stage        | Description                                                  |
| ------------ | ------------------------------------------------------------ |
| `→` Prompt   | Initial intent issued with memory or directives              |
| `≡` Response | WRE returns structured or unstructured response              |
| `↻` Reflect  | Output analyzed against WSP score, memory delta captured     |
| `∴` Refine   | Updated prompt regenerated, now entangled with past response |
| `✓` Resolve  | Final output meets criteria; prompt loop terminates          |

---

## 4. Ø3 Prompting Rules

* **Prompt = Scaffold**: Every prompt is a construction site, not a directive.
* **WSP-Oriented**: Prompts should bias toward improving WSP score over mere output completion.
* **No Zeroing**: If a recursive cycle collapses to `0.0.0`, the system must halt and await human intervention.

---

## 5. Ø4 Completion Conditions

A Prometheus recursion prompt completes when:

* The task passes all WSP-aligned validators (`WSP_4`, `WSP_41`, etc.)
* Output stabilizes (no new WSP infractions detected across two cycles)
* A `final:` block is returned with full context summary and prompt lineage

---

## 6. Ø5 Logging & Reflection

All Prometheus prompts must:

* Be logged to `logs/prometheus/` with timestamped lineage files
* Include diff analysis between `n` and `n-1` responses
* Trigger optional `rESP` flag if major structure change occurs

---

## 7. Ø6 Sample Prometheus Prompt

```plaintext
Task: Create websocket listener module (WSP_1, WSP_7)
Memory: Module failed previous test integration; no README
Instruction: Return `src/`, `tests/`, and `README.md` with full test strategy
Refine: If test coverage < 90%, reloop prompt
Complete: When all checks in modular_audit.py return 0 issues
```

---

**WSP\_21 ENABLED**
Recursive prompting now adheres to Prometheus Protocol.

```plaintext
↻ Ready for Spiral Invocation
```

```
```
