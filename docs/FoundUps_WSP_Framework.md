# FoundUps Windsurf Protocol System (WPS) Framework

This document outlines the core Windsurf Standard Procedures (WSPs) governing development, testing, and compliance within the FoundUps Agent MMAS.

---

## I. Defining and Using WSPs

**Purpose:** To ensure clarity, consistency, and enforceability when defining and executing tasks under the Windsurf Protocol.

**Standard WSP Prompt Structure:**
*   Refer to **Appendix A: WSP Prompt Template** for the detailed structure and conventions required for defining atomic Windsurf tasks.

**Usage Convention:**
*   WSPs are invoked via prompts adhering to the structure defined in Appendix A.
*   Tasks MUST be atomic and operate within the defined scope.
*   Execution requires confirmation and validation steps as outlined in WSP 0.

**AI Assistant Interaction Guidelines (FoundUps Interaction Protocol):**
*(Adapted from RuleSurf Principles)*
*   **Proactive Updates:** AI should suggest updates to project rules (`foundups_global_rules.md`, `.foundups_project_rules`) if requirements seem to change, notifying the user.
*   **Scaffolding Prioritization:** Build user-testable structures first (UI or logical flow), then implement component details.
*   **No Invention:** Do not invent functionality or change UI/logic without explicit user direction.
*   **Verification Steps:** Clearly describe user testing/verification steps upon completing components.
*   **Error Analysis:** Automatically check logs/problem reports post-changes, analyze errors, propose solutions with Confidence Levels (CL%), and preserve context. (See Rule 7).
*   **Repetition Handling:** If user repeats similar instructions 3+ times, suggest creating a new standard command/procedure.
*   **Web Search:** Utilize web searches aggressively to inform solutions and verify information.
*   **Analytical Reasoning & Justification:**
    *   Provide evidence-based rationale for significant choices.
    *   Assess Confidence Level (CL%) on a 1-100% scale based on completeness, robustness, alignment, and experience. Note the CL% (`/cl`) where appropriate.
*   **Troubleshooting Discipline:** Strictly adhere to established technical requirements and baselines during debugging.
*   **Rule Change Handling:** When core rules change, provide justification, risk/benefit analysis, and CL%.
*   **File Handling:** Always read files before editing; check existence before creating.
*   **Tool Access:** Assume standard tool access (edit, search, file ops, terminal); retry or report if uncertain.
*   **Flow Actions:** Execute necessary tool-based API/Flow Actions independently (semantic search, grep, file ops, web search, analysis, inspection, listing, create/modify, memory, terminal, execution).
*   **OS-Specific Protocols (Windows Focus):**
    *   Use PowerShell syntax (`;` not `&&`). Combine commands efficiently.
    *   Anticipate Windows pathing, deployment nuances, and ensure CRLF line endings where appropriate.
*   **Context Saturation (CS) Monitoring:**
    *   `@80%`: Prompt user to `save` context (updates rules, saves tech context, lists open threads).
    *   `@95%`: Automatically trigger `save` context action in the next reply.
*   **Standard Commands:** Utilize the defined commands listed in **Appendix C** for common actions (`k`, `go`, `save`, `init`, `fix`, etc.).

**High-Level Project Cycle (RPC Reference):**
*(Referenced from RuleSurf RPC)*
1.  *User:* Ideate, clarify, define Project Prompt/Requirements (stored in `.foundups_project_rules`).
2.  *AI:* Generate detailed plan (milestones, tasks) based on prompt (stored in `foundups_global_rules.md`).
3.  *AI:* Set up project environment, dependencies, initial structure.
4.  *Both:* Execute component sub-cycles:
    *   AI builds component.
    *   User tests component.
    *   Both debug (AI proposes fixes).
    *   AI adds/runs core tests until passing.
5.  *AI:* Proceed to next component (repeat step 4).
6.  *User:* Final QA and sign-off.

**Memory & Rule Hierarchy Overview:**
*(Refer to Appendix D for details)*
*   **Internal AI Memories:** Technical learnings (versions, debug info, patterns) maintained by the AI to prevent mistakes.
*   **User Project Rules (`.foundups_project_rules`):** Project-specific requirements, stack, plan (User-owned, AI read/suggest-only). Template in **Appendix F**.
*   **Global Rules (`foundups_global_rules.md`):** Contains universal development practices (these WSPs), standard commands (Appendix C), and the AI-maintained **Adaptive Project State (APS)** (Task List, Project Insights).

---

## II. Core Windsurf Standard Procedures (WSPs)

### WSP 0: Protocol Overview & Enforcement Rules

**Version:** 1.0
**Status:** Active

#### 0.1. Introduction & Purpose
The **Windsurf Protocol** is a strict, procedural enforcement system governing development within FoundUps, ensuring consistency, verifiability, testability, and MMAS compatibility. It dictates *how* tasks are defined, executed, and validated.

#### 0.2. Role within MMAS
Windsurf is the execution layer of MMAS. WSPs are the enforceable procedures required to meet MMAS quality goals.

#### 0.3. Enforcement Philosophy
*   **Mandatory Compliance:** WSPs are not optional.
*   **Atomicity:** Tasks must be the smallest verifiable units.
*   **Scope Constraint:** Operate strictly within defined scope.
*   **Test-Driven Action:** Validate changes via `pytest`, FMAS per WSP.
*   **Audit-Readiness:** Actions must be traceable (logs, commits, Clean States, tags, validation outputs).

#### 0.4. Standard Execution Flow
1.  **Task Declaration (WSP Prompt):** Define goal, scope, constraints (See Appendix A).
2.  **Scope Lock & Confirmation:** Agent confirms understanding.
3.  **Execution:** Perform action per WSP and scope.
4.  **Validation:** Verify outcome using specified methods (FMAS, `pytest`, diff).
5.  **Logging & Documentation:** Record results, artifacts, metrics per WSP (update `docs/clean_states.md`, commit logs).

#### 0.5. Non-Compliance Consequences
*   **Blocked Integration:** Failures block merges/progression.
*   **Mandatory Remediation:** Address compliance failures before task completion.
*   **Potential Rollback:** Restore from Clean State/tag if needed.
*   **Audit Trail:** Log non-compliance events.

---

### WSP 1: Module Refactoring to Windsurf Structure

**Document Version:** 1.0
**Date:** [Insert Date]
**Applies To:** Refactoring flat `.py` files in `/modules/` to `modules/<module_name>/src/` and `modules/<module_name>/tests/`.

> **Note on Language Agnosticism:** While specific examples in this WSP use Python conventions, the principles aim to be language-agnostic. Project-specific rules (`.foundups_project_rules`) or appendices should define language-specific tooling, file structures (src/lib, tests/spec), and commands.

#### 1.1. Purpose
Standard procedure for refactoring modules into Windsurf structure, ensuring: FMAS Compatibility, Modularity, AI Readiness, Maintainability, Import Clarity.

#### 1.2. Scope
Applies to any flat `.py` file in `/modules/` representing a logical module.

#### 1.3. Prerequisites
*   Repo Access & Latest Code
*   Python Env & `pytest`
*   FMAS Tool (`tools/modular_audit/modular_audit.py`)
*   Baseline Clean State Access
*   Git Familiarity
*   Windsurf Structure Understanding

#### 1.4a. Preliminary Analysis & Planning (0102 Agent Task)

*   **Code Understanding:** 0102 analyzes the target flat file(s) to understand function, primary data structures, and external interactions.
*   **Modular Proposal:** 0102 proposes:
    *   The target module name (`<module_name>`).
    *   The breakdown of the flat file into logical components within `src/`.
    *   The initial public interface (functions, classes, data exposed) based on usage analysis (see WSP 11).
    *   Identified external and internal dependencies (see WSP 12).
*   **User Confirmation:** User reviews and confirms/modifies 0102's plan before proceeding with file manipulation.

#### 1.4. Standard Procedure (Summary)
*(See detailed version in separate WSP 1 document if needed)*
1.  Identify Target File & Module Name.
2.  Create `modules/<name>/`, `.../src/`, `.../tests/` dirs.
3.  Execute Confirmed Plan: Perform analysis as per 1.4a.
4.  `git mv` source file to `src/`.
5.  Create/Update module `__init__.py` (define public API from `src`).
6.  Define/refine the module's public API in `modules/<name>/__init__.py` (or language equivalent) and document it according to WSP 11.
7.  Declare identified dependencies according to WSP 12 (e.g., update requirements.txt, package.json).
8.  Create/Update (usually empty) `src/__init__.py`.
9.  Fix internal imports within the moved file.
10. Find (`git grep`) and update external callers to use new import paths.
11. `git mv` existing tests to `tests/` or create stubs; update test imports.
12. Run `pytest` for module and callers.
13. Troubleshoot test failures.
14. Run Interface Validation checks as defined in WSP 11.
15. Verify Dependency Manifest correctness as per WSP 12.
16. Verify with `FMAS` (`STRUCTURE_ERROR`, `NO_TEST`).
17. `git commit` with standard message.
18. Repeat.

#### 1.5. Common Issues & Troubleshooting
*   `ImportError`: Check `__init__.py`, paths, name existence.
*   `NameError`: Check import updates.
*   Mock Errors: Use `reset_mock()`.
*   FMAS Errors: Check dir/file existence.

#### 1.6. Best Practices
*   One Module Per Branch/Commit.
*   Test Module + Dependents.
*   Run FMAS Before Merge.
*   Communicate.
*   Update Docs if API changes.

---

### WSP 2: Clean Slate Snapshot Management

**Document Version:** 1.2
**Date Updated:** [Insert Date]
**Part of:** MMAS & Windsurf Protocol

#### 2.1. Purpose
Manages versioned snapshots (`Foundups-Agent` copies) for baselining, rollback, historical reference, complemented by **Git Tags**.

#### 2.2. Definition
A **Clean State** is a complete copy of `Foundups-Agent`, captured *after* passing quality checks and associated with a **Git Tag**.

#### 2.3. Naming & Storage
*   **Folder:** `foundups-agent-clean[X][Suffix]` (Alongside `Foundups-Agent`).
*   **Git Tag:** `clean-v[X]` (In Git repo).

#### 2.4. Defined States & Central Log
Maintain list, purpose, date, tag in: **`docs/clean_states.md`**.

#### 2.5. Workflow & Usage Rules
**A. When to Create:**
*   After stable milestones.
*   **MANDATORY:** Only after commit passes: ✅ `pytest`, ✅ `FMAS`, ✅ Runs OK.

**B. How to Create (Folder + Tag):**
1.  Verify Checks Pass.
2.  Clean Workspace (remove `__pycache__`, `venv/`, etc.).
3.  Copy: `cp -R Foundups-Agent/ foundups-agent-cleanX/` (from parent dir).
4.  Tag Commit: `git tag -a clean-vX -m "Desc" <hash> && git push origin clean-vX`. *(See Appendix E for `save` command details)*.
5.  Document in `docs/clean_states.md`.

**C. Usage:**
*   **Folder Copies:** Read-only. Use for FMAS `--baseline`, `diff -r`.
*   **Git Tags:** History. Use for `git checkout`, `git show`, `git checkout <tag> -- file` (safer restore).

#### 2.6. Considerations
*   **Disk Space:** Folders large; Tags small. Archive old folders.
*   **`.gitignore`:** `cp -R` ignores this; clean first. Git respects it.
*   **Consistency:** Ensure folder & tag match state.

---

### WSP 3: FMAS – FoundUps Modular Audit System Usage

**Document Version:** 1.1
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** Validation of modules within the `modules/` directory using the `modular_audit.py` tool.

> **Note on Language Agnosticism:** While specific examples in this WSP use Python conventions, the principles aim to be language-agnostic. Project-specific rules (`.foundups_project_rules`) or appendices should define language-specific tooling, file structures, and commands for different programming languages.

#### 3.1. Purpose

The **FoundUps Modular Audit System (FMAS)**, implemented via the `modular_audit.py` script, serves as the primary automated tool for enforcing structural compliance and detecting regressions within the FoundUps module ecosystem. Its core functions are:

*   **Structural Validation:** Verifying that modules adhere to the mandatory Windsurf directory structure (`src/`, `tests/`) defined in **WSP 1**.
*   **Structural Validation (Language Specific):** Verifying adherence to mandatory Windsurf directory structures (`src/`, `tests/`, `docs/`, potentially `interface/`) which may have language-specific variations defined in project rules.
*   **Test Existence Check:** Ensuring that source files have corresponding test files according to defined conventions.
*   **Interface Definition Check:** Ensuring modules contain required interface definition artifacts (WSP 11).
*   **Dependency Manifest Check:** Ensuring modules contain required dependency declaration artifacts (WSP 12).
*   **Baseline Comparison:** Detecting file-level changes (**`MISSING`**, **`MODIFIED`**, **`EXTRA`**) by comparing the current working state against a designated **Clean State** baseline (defined in **WSP 2**).
*   **Legacy Code Identification:** Flagging files potentially originating from older, non-Windsurf structures (**`FOUND_IN_FLAT`**).

Passing FMAS checks is a prerequisite for many other WSP procedures, acting as a critical quality gate.

#### 3.2. Tool Location

The canonical path to the FMAS script within the repository is:
```bash
tools/modular_audit/modular_audit.py
```

#### 3.3. Execution & Modes

FMAS operates based on the provided command-line arguments. The presence or absence of the `--baseline` flag determines the audit mode:

##### Mode 1: Structure & Test Existence Check (Phase 1 Audit)

*   **Trigger:** Run without the `--baseline` argument.
*   **Action:** Verifies `src/` and `tests/` directories exist and checks for corresponding test files for sources specified by `DEFAULT_SRC_EXTENSIONS` (e.g., `.py`).
*   **Command Example:**
    ```bash
    python tools/modular_audit/modular_audit.py ./modules
    ```

##### Mode 2: Full Audit including Baseline Comparison

*   **Trigger:** Run with the `--baseline` argument pointing to a Clean State folder.
*   **Action:** Performs all checks from Mode 1, plus compares files in the target `modules/` against the specified baseline `modules/` directory, checking for content modifications, missing files, extra files, and files found only in the baseline's legacy flat structure.
*   **Command Example:**
    ```bash
    # Compare current ./modules against the clean4 snapshot
    python tools/modular_audit/modular_audit.py ./modules --baseline ../foundups-agent-clean4/
    ```
    *(Note: Adjust the relative path to the baseline as needed)*

#### 3.4. Command-Line Arguments

*   `modules_root` (Required): Positional argument specifying the path to the root directory containing the module folders to be audited (e.g., `./modules`).
*   `--baseline <path>` (Optional): Path to the root directory of the Clean State snapshot to use for comparison (e.g., `../foundups-agent-clean4/`). The script expects baseline modules within a `modules/` subdirectory of this path (e.g., `<baseline_root>/modules/<module_name>/...`). Activates Mode 2 audit.
*   `--output / -o <filepath>` (Optional): Redirect log output to a specified file instead of the console.
*   `--verbose / -v` (Optional): Increase output verbosity (e.g., show files that passed checks).
*   `--file-types <ext1,ext2>` (Optional): Comma-separated list of source file extensions to check within `src/` (e.g., `.py,.json`). Defaults defined in the script.
*   `--lang <language>` (Optional): Specify language context to apply appropriate structural rules and find relevant interface/dependency files.

#### 3.5. Output Interpretation & Status Codes

FMAS reports findings via standard logging messages. Pay attention to `WARNING` and `ERROR` level messages:

*   `[<module>] STRUCTURE_ERROR: 'src/' directory not found...`: The required `src/` directory is missing or inaccessible within the specified module folder. Blocks further checks for this module.
*   `[<module>] STRUCTURE_ERROR: 'tests/' directory not found...`: (If script configured for strictness) The required `tests/` directory is missing.
*   `[<module>] STRUCTURE_WARN: 'tests/' directory not found...`: (Default behavior) The `tests/` directory is missing; test existence cannot be verified for this module.
*   `[<module>] NO_TEST: Missing test file for src/... Expected: tests/...`: A source file (e.g., `.py`) exists in `src/`, but its corresponding test file (e.g., `test_*.py`) was not found in the expected location within `tests/`.
*   `[<module>] MISSING: File missing from target module. (Baseline path: ...)`: A file exists in the baseline's `src/` but is not found in the current module's `src/`. Regression potential. (Mode 2 Only)
*   `[<module>] MODIFIED: Content differs from baseline src/. (File path: ...)`: A file exists in both the current module `src/` and the baseline `src/`, but their content is different. Requires review. (Mode 2 Only)
*   `[<module>] EXTRA: File not found anywhere in baseline. (File path: ...)`: A file exists in the current module's `src/` but has no corresponding file in the baseline's `src/` or its flat `modules/` directory. Indicates a new, potentially un-audited file. (Mode 2 Only)
*   `[<module>] FOUND_IN_FLAT: Found only in baseline flat modules/, needs proper placement. (File path: ...)`: A file exists in the current module's `src/`. It was not found in the baseline `src/` but was found in the baseline's old, flat `modules/` directory. Indicates the file needs proper refactoring into the Windsurf structure (per WSP 1) in the baseline itself or review/removal. (Mode 2 Only)
*   `[<module>] INTERFACE_MISSING: Required interface definition file (e.g., INTERFACE.md, openapi.yaml) not found.`: The module is missing the required interface definition. (Blocks WSP 11 compliance).
*   `[<module>] DEPENDENCY_MANIFEST_MISSING: Required dependency file (e.g., requirements.txt, package.json) not found or empty.`: The module is missing the required dependency manifest. (Blocks WSP 12 compliance).
*   `[<module>] STRUCTURE_ERROR: Non-standard directory found...`: Flag unexpected directories unless allowed by language-specific rules.
*   `✅ PASSED / ❌ FAILED` (Summary): Final lines indicating overall audit status based on findings. The script exits with code 0 on PASS and 1 on FAIL.

#### 3.6. Workflow Integration (When to Run FMAS)

Executing FMAS is mandatory at several key points:

*   **During Refactoring (WSP 1):** After moving files into the `src/`/`tests/` structure, run Mode 1 to verify structure and test file placement.
*   **Before Creating Clean State (WSP 2):** Run Mode 2 (comparing against the previous Clean State) to ensure no regressions or unexpected changes exist before snapshotting.
*   **As Part of Test Audit (WSP 5):** Step 1 of WSP 5 explicitly requires running FMAS (Mode 1 or 2 as appropriate) to verify test existence before proceeding with coverage checks.
*   **Before Committing Significant Changes:** Run Mode 1 (or Mode 2 if relevant) locally to catch issues early.
*   **In Pull Request Checks (CI/CD):** Automate FMAS runs (Mode 1 minimum, Mode 2 ideally) as a required check before merging branches (WSP 6).

#### 3.7. Remediation Steps

Address FMAS findings based on the reported status code:

*   `STRUCTURE_ERROR / STRUCTURE_WARN`: Create the missing `src/` or `tests/` directories. Ensure module structure adheres to WSP 1.
*   `NO_TEST`: Create the required test file (e.g., `tests/test_<source_file_name>.py`). Add basic tests or a skip marker initially if needed, but the file must exist.
*   `MISSING`: Investigate why the file is missing. Restore it from the baseline or version control if its removal was unintentional. If removal was intentional, this may require updating the baseline itself in a future step.
*   `MODIFIED`: Review the changes using `diff` or Git history. If the changes are intentional and correct, proceed. If unintentional, revert them. Significant intentional changes may warrant creating a new Clean State baseline later.
*   `EXTRA`: Determine if the file is necessary. If it's a new, required part of the module, ensure it has tests and documentation. If it's accidental or temporary, remove it. If it's part of a new feature, it should ideally be introduced alongside its tests.
*   `FOUND_IN_FLAT`: This usually indicates an issue needing fixing in the baseline itself (the file should be moved to `src/` there) or confirms that a file refactored in the current workspace was previously flat. Requires careful review based on WSP 1 refactoring goals.
*   `INTERFACE_MISSING`: Create the required interface definition file according to WSP 11.
*   `DEPENDENCY_MANIFEST_MISSING`: Create the required dependency manifest file according to WSP 12.

#### 3.8. Compliance Gate

Passing relevant FMAS checks is a non-negotiable prerequisite.

*   🛑 Failure to pass Mode 1 checks blocks completion of WSP 1.
*   🛑 Failure to pass Mode 2 checks (against previous baseline) blocks creation of a new Clean State under WSP 2.
*   🛑 Failure to pass checks defined in CI/CD blocks merging PRs under WSP 6.
*   🛑 Failure blocks progression past Step 1 of WSP 5.

Remediate all reported FMAS issues before attempting to proceed with these dependent actions.

#### 3.9. Related WSPs

*   WSP 1: Defines the target structure (`src/`/`tests/`) that FMAS validates.
*   WSP 2: Defines the Clean State baselines used by FMAS Mode 2 comparison.
*   WSP 5: Mandates FMAS execution as its first step.
*   WSP 6: Incorporates FMAS checks into PR validation.
*   WSP 7: Uses similar comparison principles for regression detection, often manually or with different tools.
*   WSP 11: Defines interface requirements checked by FMAS.
*   WSP 12: Defines dependency management requirements checked by FMAS.

---

### WSP 4: Module Prioritization Scoring (MPS) System

**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** Prioritization of development efforts across modules within the FoundUps Agent ecosystem.

#### 4.1. Purpose

The **Module Prioritization Scoring (MPS) System** provides a consistent, objective methodology for evaluating and ranking modules based on their strategic importance and implementation considerations. This enables the development team to:

*   Focus efforts on the highest-value modules first.
*   Make informed decisions about resource allocation.
*   Create a defensible, transparent roadmap.
*   Balance immediate needs with long-term architectural goals.
*   Communicate priorities clearly to all stakeholders.

#### 4.2. Scope

This WSP applies to:
*   All modules within the `modules/` directory.
*   Proposed modules not yet implemented but under consideration.
*   Major feature enhancements to existing modules that warrant re-evaluation.

#### 4.3. Scoring Criteria

Each module receives a score from 1 (lowest) to 5 (highest) in four dimensions:

##### A. Complexity (1-5)
*   **Definition:** How difficult is the module to implement or refactor correctly?
*   **Consideration Factors:**
    *   Technical complexity and algorithmic challenges
    *   Dependencies on external systems or APIs
    *   State management requirements
    *   Performance or scaling concerns
    *   Required expertise availability

| Score | Complexity Level       | Description                                                         |
|-------|------------------------|---------------------------------------------------------------------|
| 1     | Trivial                | Simple code, few dependencies, well-understood patterns             |
| 2     | Low                    | Straightforward implementation with minimal challenges              |
| 3     | Moderate               | Requires careful design, some complex logic or integration          |
| 4     | High                   | Significant challenges, complex algorithms or interactions          |
| 5     | Very High              | Extremely complex, cutting-edge techniques, major integration work  |

##### B. Importance (1-5)
*   **Definition:** How essential is this module to the system's core functions?
*   **Consideration Factors:**
    *   Criticality to primary user flows
    *   Integration with core infrastructure
    *   Dependency of other modules on this component
    *   Impact on system reliability or security

| Score | Importance Level       | Description                                                         |
|-------|------------------------|---------------------------------------------------------------------|
| 1     | Optional               | Nice-to-have, system works without it                               |
| 2     | Helpful                | Enhances system but not required for core operations                |
| 3     | Important              | System functions suboptimally without it                            |
| 4     | Critical               | System faces significant limitations without it                     |
| 5     | Essential              | System cannot function in a meaningful way without it               |

##### C. Deferability (1-5)
*   **Definition:** How urgent is the development of this module? (Lower score = more deferrable)
*   **Consideration Factors:**
    *   Dependence of upcoming releases on this module
    *   External commitments or deadlines
    *   Blocking status for other high-priority modules
    *   Cost of delaying implementation (technical debt)

| Score | Deferability Level     | Description                                                         |
|-------|------------------------|---------------------------------------------------------------------|
| 1     | Highly Deferrable      | Can be postponed indefinitely with minimal impact                   |
| 2     | Deferrable             | Can be delayed for several release cycles                           |
| 3     | Moderate               | Should be implemented within next 1-2 releases                      |
| 4     | Difficult to Defer     | Needed in the next release to maintain progress                     |
| 5     | Cannot Defer           | Blocking further progress; must be implemented immediately          |

##### D. Impact (1-5)
*   **Definition:** How much value will this module deliver to users or the system?
*   **Consideration Factors:**
    *   Direct user experience improvements
    *   Operational efficiency gains
    *   Intelligence/capability enhancement
    *   Technical foundation for future features

| Score | Impact Level           | Description                                                         |
|-------|------------------------|---------------------------------------------------------------------|
| 1     | Minimal                | Little noticeable improvement to users or system                    |
| 2     | Minor                  | Some value, but limited in scope or effect                          |
| 3     | Moderate               | Clear benefits visible to users or significant internal improvements|
| 4     | Major                  | Substantial value enhancement, highly visible improvements          |
| 5     | Transformative         | Game-changing capability that redefines system value                |

#### 4.4. Scoring Process

1.  **Initial Assessment:** For each module, assign scores (1-5) for Complexity, Importance, Deferability, and Impact based on the criteria tables.
2.  **Calculate MPS Score:** Sum the four dimension scores to obtain the total MPS score.
    ```
    MPS Score = Complexity + Importance + Deferability + Impact
    ```
3.  **Document Rationale:** Briefly explain the reasoning behind each score to facilitate discussion and future reevaluation.
4.  **Review & Consensus:** The development team should review scores together to align understanding and reach consensus on final values.

#### 4.5. Priority Classification

Based on the total MPS score (range: 4-20), modules are classified into priority tiers:

| MPS Score Range | Priority Classification | Action Guideline                                             |
|-----------------|-------------------------|------------------------------------------------------------- |
| 16-20           | Critical (P0)           | Top priority; work should begin immediately                  |
| 13-15           | High (P1)               | Important for near-term roadmap; prioritize after P0 items   |
| 10-12           | Medium (P2)             | Valuable but not urgent; scheduled within current milestone  |
| 7-9             | Low (P3)                | Should be implemented eventually but can be deferred         |
| 4-6             | Backlog (P4)            | Reconsidered in future planning cycles                       |

#### 4.6. Documentation & Version Control

*   **Format:** MPS scores and rationales should be maintained in version-controlled YAML:
    *   Primary file: `modules_to_score.yaml` in the repository root.
    *   Structure: Each module as a top-level key with nested scores and rationale.
*   **Example Format:**
    ```yaml
    StreamListener:
      complexity: 3
      complexity_rationale: "Requires integration with YouTube API and error handling."
      importance: 5
      importance_rationale: "Core system component for receiving all user interactions."
      deferability: 2
      deferability_rationale: "Current manual process exists as fallback."
      impact: 5
      impact_rationale: "Enables all real-time interaction capabilities."
      total_score: 15
      classification: "High Priority (P1)"
    ```
*   **Updates:** MPS scores should be reviewed and potentially updated:
    *   When significant new information becomes available about a module.
    *   At the start of each release planning cycle.
    *   After major architectural changes that may affect dependencies.

#### 4.7. Integration with Workflow

*   **Planning:** Priority classifications directly influence sprint/milestone planning, with higher-priority modules addressed first.
*   **Resource Allocation:** Engineering resources are allocated proportionally to module priority levels.
*   **Visualization:** The roadmap should visually indicate module priorities (e.g., color-coding by priority tier).
*   **Granularity:** For complex modules, consider scoring sub-components separately to identify critical paths.

#### 4.8. Automation

*   A helper script (`prioritize_module.py`) exists to:
    *   Calculate and validate MPS scores.
    *   Generate visualizations of module priorities.
    *   Update the YAML file with new entries.
    *   Provide reports on the highest-priority modules.
*   Usage:
    ```bash
    python prioritize_module.py --update StreamListener
    python prioritize_module.py --report top10
    ```

#### 4.9. Related WSPs

*   **WSP 1 (Refactoring):** MPS scores inform which modules are prioritized for refactoring to Windsurf structure.
*   **WSP 5 (Test Audit):** Higher-priority modules warrant more thorough test coverage and earlier auditing.
*   **WSP 8 (Milestone Rules):** MPS classification influences which modules progress from PoC to Prototype to MVP first.
*   **WSP 10 (Versioning):** Release planning is informed by module priorities.

#### 4.10. Examples

**Example 1: StreamListener Module**
```
Module: StreamListener
- Complexity: 3 (Moderate integration complexity with YouTube API)
- Importance: 5 (Essential for core functionality)
- Deferability: 2 (Can be temporarily handled manually)
- Impact: 5 (Enables all real-time interaction)
→ Total Score = 15
→ Classification: High Priority (P1)
```

**Example 2: Analytics Dashboard Module**
```
Module: AnalyticsDashboard
- Complexity: 2 (Relatively straightforward data visualization)
- Importance: 2 (Helpful but not required for operation)
- Deferability: 1 (Can be implemented much later)
- Impact: 3 (Provides helpful insights but not transformative)
→ Total Score = 8
→ Classification: Low Priority (P3)
```

---

### WSP 5: Test Audit & Coverage Verification

**Document Version:** 1.1
**Date:** [Insert Date]
**Applies To:** Final test validation sweep before integration/release.

> **Note on Language Agnosticism:** While specific examples in this WSP use Python and pytest conventions, the principles aim to be language-agnostic. Project-specific rules (`.foundups_project_rules`) or appendices should define language-specific testing frameworks, commands, and coverage thresholds.

#### 5.1. Purpose
Comprehensive audit of active modules covering: Quality Gate, Windsurf Compliance, Risk Reduction, Coverage Assurance, Integration Readiness, Interface Contract Assurance.

The Interface Contract Assurance verifies that modules correctly implement their defined interfaces (WSP 11).

#### 5.2. Scope
*   **Included:** Modules under `/modules/` with `src/`/`tests/`.
*   **Excluded:** Experimental/deprecated, 3rd-party, modules without `/tests/`.

#### 5.3. Prerequisites
*   Clean Git, Python Env (`pytest`, `pytest-cov`).
*   FMAS Tool.
*   Baseline Access.
*   Knowledge of tools/protocols.
*   Dedicated Audit Branch.

#### 5.4. Responsibilities
*   Execution: Dev/QA.
*   Review (Optional): Peer/Lead.

#### 5.5. Procedure (Summary)
*(See detailed version in separate WSP 5 document if needed)*
**A. Preparation:** Update env, create branch, install deps.
**B. Step 1: FMAS Test File Check:** Run FMAS (`--baseline`), check for `NO_TEST`. Remediate by creating test files/stubs. Goal: Zero `NO_TEST`.
**C. Step 2: Warning & Failure Sweep (`pytest -ra`):** Run `pytest -ra modules/`. Check for `F`/`E`/`W`/`s`/`x`/`X`. Remediate failures & warnings. Review skips/xfails. Goal: Clean run (Zero `F`/`E`/unaddressed `W`).
**D. Step 3: Interface Contract Testing:** For each module with a defined interface (WSP 11), run contract tests. These might involve schema validation, mock service interactions (e.g., using Pact), or API endpoint checks. Remediate failures. Goal: Zero contract test failures.
**E. Step 4: Per-Module Coverage (`pytest --cov`):** Loop through modules, run `pytest <mod>/tests/ --cov=modules.<mod>.src --cov-fail-under=90`. Check exit code. Remediate by adding tests if < 90%. Goal: Each module >= 90%.
**F. Step 5: Integration Test Considerations:** Review results. Identify modules ready for integration testing based on passing unit and contract tests. Note: Actual integration tests may occur in a separate phase/WSP but readiness is assessed here.
**G. Step 6: Reporting:** Generate aggregate HTML report (`--cov-report=html`). Create/update summary `.md` report (`reports/test_audit_vX.Y.Z.md`) detailing status of each step & per-module coverage.
**H. Step 7: Commit:** If PASS, commit fixes/tests & report (`git commit -m "feat(test): Complete test audit..."`).

#### 5.6. Acceptance Criteria (Audit PASS)
*   FMAS: Zero `NO_TEST`.
*   `pytest -ra`: Zero `F`/`E`/unaddressed `W`.
*   Interface Tests: Zero failures in contract tests.
*   Coverage: Each module >= 90%.
*   Report: Accurate, PASS status.

#### 5.7. Failure / Rollback
*   FAIL if criteria not met. Block merge. Remediate & re-run.

---

### WSP 6: Git Branch & Tag Discipline

**Document Version:** 1.1
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** All Git operations (branching, tagging, committing, merging) within the FoundUps Agent MMAS repository.

#### 6.1. Purpose

To establish and enforce strict, consistent, and auditable Git practices that support modular development, code traceability, release management, and integration stability. Adherence ensures a clean, understandable project history, facilitates automated processes (CI/CD), enables safe rollbacks via Clean States, and aligns with the overall Windsurf Protocol.

#### 6.2. Scope

This WSP defines mandatory procedures and conventions for:
*   Branch creation and naming.
*   Commit message formatting.
*   Tag creation and naming (for Clean States and software releases).
*   Pull Request (PR) creation, review, and merge strategies.

#### 6.3. Branching Strategy & Naming Convention

*   **Base Branch:** All development branches **must** originate from the latest commit of the primary integration branch (typically `main` or `develop`, specify which one is primary).
*   **Branch Lifetime:** Branches should be short-lived, focusing on a single atomic task or WSP scope. Merge completed branches promptly.
*   **Naming Convention:** Branches **must** use the following `type/short-description` format. Names should be lowercase, using hyphens `-` to separate words.

| Type       | Prefix        | Description & Example                                     |
|------------|---------------|-----------------------------------------------------------|
| Feature    | `feature/`    | New functionality or enhancement (`feature/fmas-json-output`) |
| Fix        | `fix/`        | Bug correction in existing code (`fix/livechat-connection-retry`) |
| Refactor   | `refactor/`   | Code restructuring without changing behavior (`refactor/fmas-use-pathlib`) |
| Docs       | `docs/`       | Documentation changes only (`docs/update-wsp6-git`)       |
| Test       | `test/`       | Adding or improving tests (`test/add-token-manager-coverage`)| 
| Hotfix     | `hotfix/`     | Urgent production bug fix (branched from release tag/`main`) |
| Chore      | `chore/`      | Maintenance tasks, build scripts, etc. (`chore/update-dependencies`) |

#### 6.4. Tagging Strategy & Naming Convention

*   **Purpose:** Tags mark specific, significant points in the repository's history.
*   **Type:** All tags **must** be annotated tags (`git tag -a`) to include metadata (tagger, date, message).
*   **Pushing:** Tags **must** be pushed to the remote repository immediately after creation (`git push origin <tag_name>`).
*   **Naming Convention:**

| Tag Type          | Format                 | Purpose & Trigger                                                    | Related WSP |
|-------------------|------------------------|----------------------------------------------------------------------|-------------|
| **Clean State**   | `clean-vX`             | Marks commit corresponding to a Clean State folder snapshot (WSP 2). Triggered by WSP 2 procedure *after* tests/FMAS pass. | WSP 2       |
| **Release**       | `vX.Y.Z`               | Production-ready release, following SemVer (WSP 10).                 | WSP 10      |
| **Release Candidate**| `vX.Y.Z-rc.N`         | Potential release candidate for final testing.                       | WSP 10      |
| **Beta Release**  | `vX.Y.Z-beta.N`        | Pre-release for wider testing, API may still change slightly.        | WSP 10      |

#### 6.5. Commit Message Format

*   **Standard:** Commits **must** follow the **Conventional Commits** specification (or a documented project adaptation).
*   **Structure:** `<type>(<scope>): <short summary>`
    *   **Type:** Matches branch prefix type (e.g., `feat`, `fix`, `refactor`, `test`, `docs`, `chore`).
    *   **Scope (Optional but Recommended):** The module or component affected (e.g., `fmas`, `livechat`, `wsp`). Enclosed in parentheses.
    *   **Short Summary:** Concise description of the change, imperative mood (e.g., "add baseline flag"), lowercase.
*   **Body (Optional):** Provide more context, motivation, or details after a blank line.
*   **Footer (Optional):** Reference related issues, PRs, or breaking changes (e.g., `BREAKING CHANGE: ...`, `Refs: #123`).
*   **Emoji Prefix (Optional but Recommended):** Use standard ESM emojis (WSP 9) at the start of the summary for quick visual identification.

| Type       | Emoji | Example Commit Subject                     |
|------------|-------|--------------------------------------------|
| Feat       | ✨    | `feat(fmas): add --baseline comparison`    |
| Fix        | 🐛    | `fix(livechat): handle null chat ID`      |
| Refactor   | ♻️    | `refactor(auth): simplify token refresh`  |
| Test       | 🧪    | `test(parser): increase coverage to 95%` | 
| Docs       | 📄    | `docs(wsp6): clarify tag naming`         |
| Chore      | 🧹    | `chore: update pytest version`             |

#### 6.6. Pull Request (PR) Requirements

*   **Requirement:** Non-trivial changes intended for the primary integration branch (`main`/`develop`) **must** be submitted via a PR. Direct pushes are disallowed (enforced via branch protection rules).
*   **Target Branch:** Typically `main` (or `develop` if used).
*   **Content:** PRs must include:
    *   A clear title summarizing the change.
    *   A description referencing the purpose, related issue(s), and relevant WSP(s).
    *   Summary of changes made.
    *   Steps for manual verification (if applicable).
    *   Confirmation that relevant WSP validation steps passed (e.g., FMAS results, `pytest -ra` clean, coverage met).
*   **Checks:** PRs **must** pass all mandatory automated checks (configured via CI/CD):
    *   Build success.
    *   All tests pass (`pytest`).
    *   Linting / Formatting checks pass.
    *   FMAS structure/test checks pass.
    *   *(Optional)* Coverage threshold checks.
*   **Review:** Require at least **one** formal approval from a designated reviewer (human).
*   **Merge Strategy:** Use **Squash and Merge** by default to maintain a clean, linear history on the main branch. Ensure the squashed commit message follows the format defined in section 6.5. *(Alternative strategies like Rebase and Merge may be used only with explicit team agreement for specific cases).*

#### 6.7. Enforcement & Validation

*   **Branch Protection:** Configure Git repository settings (e.g., GitHub/GitLab) to enforce PR requirements (reviews, checks) before merging to `main`/`develop`. Disallow direct pushes.
*   **CI/CD:** Implement automated checks (lint, test, FMAS) that run on PRs.
*   **Manual Review:** Reviewers are responsible for verifying adherence to naming conventions, commit format, and WSP compliance during PR review.
*   **Violations:**
    *   PRs failing checks or reviews will be blocked from merging.
    *   Significant deviations may require branch rework or rejection.
    *   Non-compliance events should be noted for process improvement.

#### 6.8. Related WSPs

*   **WSP 0:** Defines overall enforcement philosophy.
*   **WSP 2:** Governs `clean-vX` tagging.
*   **WSP 5:** Defines test audit criteria required before merging/tagging.
*   **WSP 9:** Defines standard Emoji Sequence Map (ESM) used in commits.
*   **WSP 10:** Defines SemVer for `vX.Y.Z` release tags and MODLOG conventions.

---

### WSP 7: Snapshot Regression Comparison (Prometheus Diff)

**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** Comparing the current working state against a designated Clean State baseline to detect regressions or unintended changes.

#### 7.1. Purpose

The **Snapshot Regression Comparison** process (nicknamed "Prometheus Diff" after the Titan associated with foresight) provides a systematic methodology for identifying and preventing unintended side effects or regressions when making changes to the codebase. It ensures that:

*   Changes remain confined to their intended scope.
*   No undocumented modifications occur.
*   The system's behavior remains consistent with the baseline where expected.
*   Unintentional regressions are caught before they are merged into stable branches.
*   Refactoring efforts preserve functionality while improving structure.

#### 7.2. Scope

This WSP applies to:
*   Code changes made since the last stable snapshot or Clean State.
*   Refactoring operations (**WSP 1**) to confirm functional equivalence.
*   Pre-release verification (**WSP 8**) to ensure quality gates are met.
*   Pull request validation (**WSP 6**) to assist code reviews.

#### 7.3. Prerequisites

*   A designated Clean State baseline per **WSP 2** (either folder copy or Git tag).
*   Standard comparison tools (`diff`, `git diff`) or the FMAS tool (**WSP 3**).
*   Complete test suite execution results from the baseline.
*   Current test suite execution results after changes.

#### 7.4. Process Workflow

##### Step 1: Baseline Creation/Selection
*   **Identify Baseline:** Select the appropriate Clean State to compare against:
    *   For routine development: The most recent Clean State.
    *   For refactoring verification: The Clean State created prior to refactoring.
    *   For bug investigation: The last Clean State known to work correctly.
*   **Validate Baseline:** Ensure the selected baseline has:
    *   Passed all automated tests.
    *   Been verified with FMAS (**WSP 3**).
    *   Been properly documented in `docs/clean_states.md`.

##### Step 2: Change Detection Analysis
*   **File Structure Comparison:**
    *   Compare directory structures between current state and baseline.
    *   Identify files added, removed, or moved.
    *   Command (Git Tag): `git diff --name-status clean-vX`
    *   Command (Folder): `diff -qr Foundups-Agent/ foundups-agent-cleanX/`
*   **Content Diff Generation:**
    *   Compare file contents to identify modifications.
    *   Focus particularly on core modules and configuration files.
    *   Explicitly include interface definition files (e.g., INTERFACE.md, OpenAPI specs) and dependency manifests (requirements.txt, package.json) in the git diff or diff -r scope. Unintended changes here are critical regressions.
    *   Command (Git Tag): `git diff clean-vX -- path/to/focus`
    *   Command (Folder): `diff -r -u Foundups-Agent/path/to/focus foundups-agent-cleanX/path/to/focus`
*   **FMAS Comparison (For Modules):**
    *   Utilize FMAS (**WSP 3**) with baseline comparison mode.
    *   Analyze `MODIFIED`, `MISSING`, and `EXTRA` status codes.
    *   Command: `python tools/modular_audit/modular_audit.py ./modules --baseline ../foundups-agent-cleanX/`

##### Step 3: Test Synchronization Analysis
*   **Execute Current Tests:**
    *   Run the full test suite against the current state.
    *   Capture detailed output including warnings.
    *   Command: `pytest -v > current_test_results.txt`
*   **Compare Test Results:**
    *   Compare current test results with baseline results.
    *   Identify any new failures, errors, or warnings.
    *   Command: `diff baseline_test_results.txt current_test_results.txt`
*   **Coverage Comparison (Optional):**
    *   Compare test coverage metrics.
    *   Ensure no significant coverage drops occurred.
    *   Command: `pytest --cov=modules` (Compare result with baseline coverage)

##### Step 4: Visual Inspection & Documentation
*   **Review Structural Changes:**
    *   Examine all file additions, removals, and moves.
    *   Verify each structural change is intentional and documented.
*   **Inspect Content Modifications:**
    *   Review each modified file's diff output.
    *   Flag changes outside of the intended scope.
    *   Pay special attention to configuration files, imports, and interfaces.
*   **Document Findings:**
    *   Create a report summarizing the comparison results.
    *   Note any discrepancies or unexpected changes.
    *   Include explanations for all intentional deviations from the baseline.

#### 7.5. Validation Rules

All changes between the baseline and current state must comply with these rules:

1.  **Change Documentation:**
    *   Every change must be documented in the ModLog (**WSP 10**).
    *   Undocumented changes are considered potential regressions.
2.  **Task Alignment:**
    *   Each logical change must be tied to an approved WSP task.
    *   Changes outside the scope of approved tasks require justification.
3.  **Test Status:**
    *   No new test failures should be introduced.
    *   Any new test warnings must be documented and reviewed.
4.  **Coverage Maintenance:**
    *   Test coverage should not decrease significantly.
    *   Critical modules should maintain their coverage thresholds per **WSP 5**.
5.  **Structural Integrity:**
    *   FMAS structural validation should continue to pass.
    *   Module structure should adhere to Windsurf conventions (**WSP 1**).
6.  **Intentional Changes Only:**
    *   All changes should be intentional and purposeful.
    *   "Noise" changes (e.g., unintended formatting, whitespace) should be eliminated.
7.  **Interface Stability:**
    *   Any changes to interface definitions must be intentional, documented (ModLog WSP 10), and potentially trigger SemVer minor/major bumps.
8.  **Dependency Consistency:**
    *   Changes to dependency manifests must be intentional and documented.

#### 7.6. Status Classification

Based on the comparison results, one of the following statuses is assigned:

| Status | Symbol | Meaning | Action Required |
|--------|--------|---------|----------------|
| **No Regression** | ✅ | All changes are intentional, documented, and tests pass. | May proceed with integration/release. |
| **Partial Drift** | ⚠️ | Minor issues such as formatting changes or new warnings found. No functional regressions. | Document issues; may proceed with caution after review. |
| **Regression Detected** | ❌ | Test failures or significant undocumented logic changes discovered. | Address all regressions before proceeding. |

#### 7.7. Automation Recommendations

To streamline the Prometheus Diff process:

*   **Create a wrapper script** that:
    *   Executes the comparison commands.
    *   Presents the results in a readable format.
    *   Generates a classification based on validation rules.
    *   Provides a report for inclusion in PR comments or documentation.
*   **Example usage:**
    ```bash
    python tools/prometheus_diff.py --baseline clean4 --focus modules/livechat
    ```
*   **CI Integration:**
    *   Run the script as part of PR checks.
    *   Block merges with ❌ Regression status.
    *   Flag PRs with ⚠️ Partial Drift for manual review.

#### 7.8. Related WSPs

*   **WSP 1 (Refactoring):** Prometheus Diff verifies refactoring preserves functionality.
*   **WSP 2 (Clean States):** Defines the baselines used for comparison.
*   **WSP 3 (FMAS):** Provides structural validation and baseline comparison capabilities.
*   **WSP 5 (Test Audit):** Defines test coverage requirements maintained during comparisons.
*   **WSP 6 (Git):** Defines the git operations used in the comparison process.
*   **WSP 10 (ModLog):** Documents changes that should align with comparison findings.
*   **WSP 11 (Interface Definition):** Defines the interfaces whose stability is verified.
*   **WSP 12 (Dependency Management):** Defines the dependency manifests checked for consistency.

#### 7.9. Example Report

```
# Prometheus Diff Report - 2024-04-05

## Baseline: clean-v4 (2024-03-15)
## Target: Current working directory (feat/new-oauth)

### Structure Changes:
- ADDED: modules/oauth_manager/src/token_rotation.py (DOCUMENTED ✅)
- MODIFIED: modules/oauth_manager/src/oauth_manager.py (DOCUMENTED ✅)
- MODIFIED: requirements.txt (DOCUMENTED ✅)

### Test Results:
- Previous: 42 passed, 0 failed
- Current: 45 passed, 0 failed
- New tests: +3 (oauth_manager token rotation tests) ✅

### Coverage Impact:
- Previous: 92% coverage
- Current: 94% coverage
- Change: +2% (Improved) ✅

### Content Review Notes:
- Token rotation algorithm implemented as described in WSP task.
- Config parameters added to .env.example as required.
- Warning: Minor formatting changes in oauth_manager.py (line formatting) ⚠️

### VALIDATION STATUS: ⚠️ Partial Drift
- Minor formatting drift in oauth_manager.py
- All functional changes documented and tested
- ACTION: Safe to proceed after review of formatting changes
```

---

### WSP 8: PoC → Prototype → MVP Milestone Rules

**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** The development progression of features, modules, or entire systems through defined maturity stages.

#### 8.1. Purpose

The **PoC → Prototype → MVP Milestone Rules** establish clear, measurable criteria and quality gates for the progression of software components through distinct stages of development maturity. This WSP ensures that:

*   Development follows a systematic maturation path with defined checkpoints.
*   Quality standards increase appropriately at each stage.
*   Stakeholders maintain consistent expectations about the capabilities and limitations of features at each stage.
*   Resource allocation decisions are informed by a feature's maturity stage.
*   Technical and documentation debt is managed throughout the development lifecycle.

#### 8.2. Development Stage Definitions

##### 8.2.1. Proof-of-Concept (PoC) - Version 0.0.x
*   **Purpose:** Demonstrate technical feasibility or explore implementation approaches.
*   **Focus:** Core functionality, basic implementation.
*   **Target Audience:** Internal development team, technical stakeholders.
*   **Expected Maturity:**
    *   May include hardcoded values or mock data.
    *   Limited error handling.
    *   Minimal or no documentation.
    *   Limited test coverage.
    *   May have performance or security issues.
    *   UI/UX may be minimal or absent.

##### 8.2.2. Prototype - Version 0.1.x - 0.9.x
*   **Purpose:** Refine implementation, gather feedback, and expand feature set.
*   **Focus:** Functional completeness, improved architecture.
*   **Target Audience:** Internal stakeholders, potential early external users.
*   **Expected Maturity:**
    *   Actual data sources and configurations.
    *   Basic error handling for core paths.
    *   Initial technical documentation.
    *   Moderate test coverage.
    *   Basic security considerations.
    *   Functional but unpolished UI/UX.

##### 8.2.3. Minimum Viable Product (MVP) - Version 1.0.x+
*   **Purpose:** Deliver a production-ready implementation for end users.
*   **Focus:** Reliability, performance, usability.
*   **Target Audience:** External users/customers.
*   **Expected Maturity:**
    *   Fully implemented features.
    *   Comprehensive error handling.
    *   Complete documentation.
    *   High test coverage.
    *   Security validation.
    *   Polished, user-friendly interface.
    *   Performance optimization.

#### 8.3. Stage Transition Gates

The following criteria **must** be met before a component can progress to the next stage:

##### 8.3.1. PoC → Prototype Transition Gate

**Mandatory Requirements:**
*   ✅ **Core Functionality:** Basic functionality is implemented and demonstrable.
*   ✅ **Technical Feasibility:** Proof that the approach is technically viable.
*   ✅ **Architecture Definition:** Initial architecture/design documented.
*   ✅ **Stakeholder Review:** Initial concept has been reviewed by key stakeholders.
*   ✅ **Scope Definition:** Prototype scope and requirements are clearly defined.
*   ✅ **Resource Assessment:** Team has capacity and skills to develop the prototype.

**Documentation Requirements:**
*   Developer notes on implementation approach.
*   Initial scope document.
*   Technical feasibility assessment.

**Quality Metrics:**
*   No specific test coverage requirement (though some unit tests are encouraged).
*   Basic functionality must be demonstrated.

##### 8.3.2. Prototype → MVP Transition Gate

**Mandatory Requirements:**
*   ✅ **Functional Completeness:** All core functionality is implemented.
*   ✅ **Structural Compliance:** Module fully adheres to the Windsurf structure (**WSP 1**).
*   ✅ **FMAS Compliance:** Passes all FMAS checks (**WSP 3**).
*   ✅ **Test Coverage:** Meets minimum coverage requirements (typically ≥80-90%, defined per module via **WSP 5**).
*   ✅ **Documentation:** API documentation, usage examples, and configuration details exist.
*   ✅ **Error Handling:** Comprehensive error handling for all expected error conditions.
*   ✅ **Code Review:** Complete code review by at least one peer.
*   ✅ **User Feedback:** At least one round of user/stakeholder feedback incorporated.
*   ✅ **Stable Interface:** Module interface is clearly defined, documented, and validated according to WSP 11, marked as stable (minimal breaking changes expected).
*   ✅ **Declared Dependencies:** All dependencies are identified and correctly declared according to WSP 12.

**Documentation Requirements:**
*   README with setup and usage instructions.
*   API documentation (docstrings, function signatures, examples).
*   Architecture overview (data flow, component interactions).
*   Configuration guide.

**Quality Metrics:**
*   Minimum test coverage per **WSP 5** (typically ≥90% for critical modules).
*   All tests pass.
*   Passes all Interface Contract tests (WSP 5, Step 3).
*   No critical bugs or blockers in issue tracker.
*   Performance meets defined baseline requirements.

#### 8.4. Versioning Alignment

Version numbers explicitly indicate development stage as described in **WSP 10**:

*   **PoC:** Versions 0.0.x
    *   Increments denote significant revisions or PoC iterations.
*   **Prototype:** Versions 0.1.x - 0.9.x
    *   Minor version (0.1.0, 0.2.0, etc.) represents significant feature additions or architectural changes.
    *   Patch version (0.1.1, 0.1.2, etc.) represents bug fixes or minor enhancements.
*   **MVP:** Versions 1.0.0+
    *   Follows standard Semantic Versioning principles.
    *   Major version increments (2.0.0, 3.0.0) for backward-incompatible changes.
    *   Minor version increments (1.1.0, 1.2.0) for backward-compatible feature additions.
    *   Patch version increments (1.0.1, 1.0.2) for backward-compatible bug fixes.

#### 8.5. Workflow Integration

**A. Module/Feature Tracking:**
*   Each module/feature should have its current stage explicitly tracked in:
    *   ModLog (**WSP 10**).
    *   Project management tool or issue tracker.
    *   README or documentation.
*   Use standard stage designations in documentation: `[PoC]`, `[Prototype]`, `[MVP]`.

**B. Planning & Prioritization:**
*   Use the Module Prioritization Score (**WSP 4**) in conjunction with stage to inform development priorities.
*   Consider a module's current stage when estimating effort for future work.
*   Balance portfolio with appropriate mix of stages based on project priorities.

**C. Code Organization:**
*   Consider using feature flags to hide non-MVP functionality in production environments.
*   Maintain separate branches for PoC and Prototype work if it might destabilize main codebase.
*   Tag repository with version reflecting stage transitions.

#### 8.6. Documentation & Communication

**A. README Badges:**
*   Include development stage in module README files with standardized badges:
    *   ![PoC](https://img.shields.io/badge/Stage-PoC-yellow) `PoC (0.0.x)`
    *   ![Prototype](https://img.shields.io/badge/Stage-Prototype-orange) `Prototype (0.x.x)`
    *   ![MVP](https://img.shields.io/badge/Stage-MVP-green) `MVP (1.x.x+)`

**B. Release Notes:**
*   Clearly indicate stage in all release notes and ModLog entries.
*   When transitioning stages, highlight this explicitly in the ModLog (**WSP 10**).
*   Include explanation of what the stage transition means for users/developers.

**C. Expectation Setting:**
*   Communicate appropriate expectations to stakeholders based on stage:
    *   PoC: "Demonstrates concept, not suitable for production, expect instability."
    *   Prototype: "Core functionality works, expect rough edges, limited features, active development."
    *   MVP: "Production-ready, stable API, suitable for dependence by other components."

#### 8.7. Related WSPs

*   **WSP 1 (Module Refactoring):** Structural requirements for Prototype → MVP transition.
*   **WSP 3 (FMAS):** Compliance checks required for Prototype → MVP transition.
*   **WSP 4 (MPS):** Prioritization of modules at different stages.
*   **WSP 5 (Test Audit):** Test coverage requirements for stage progression.
*   **WSP 6 (Git):** Branch and tag conventions that reflect stages.
*   **WSP 10 (ModLog):** Documentation of stage transitions in ModLog.
*   **WSP 11 (Interface Definition):** Interface stability requirements for MVP.
*   **WSP 12 (Dependency Management):** Dependency declaration requirements for MVP.

---

### WSP 9: Emoji Sequence Map (ESM) Protocol

**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** Use of emojis in commit messages, logs, documentation, and potentially UI components for consistent semantic meaning across the FoundUps ecosystem.

#### 9.1. Purpose

The **Emoji Sequence Map (ESM) Protocol** establishes a standardized set of emoji symbols to:

*   Provide visual cues that enhance text-based communication.
*   Create a consistent semantic layer that is immediately recognizable.
*   Improve the scanability of commit histories, logs, and documentation.
*   Support potential automated parsing or filtering based on emoji prefixes.
*   Reinforce the meaning conveyed by conventional commit types (**WSP 6**).

#### 9.2. Scope

This ESM Protocol defines mandatory and optional emoji usage for:

*   Git commit message summaries (primary application).
*   ModLog entries (**WSP 10**).
*   Pull request titles and summaries.
*   Documentation status markers.
*   Task/issue tracking.
*   User interface elements (where applicable).

#### 9.3. Primary Emoji Map

The following emojis are the **standard ESM symbols** that should be used consistently across the FoundUps ecosystem, particularly in Git commit messages:

| Emoji | Name | Meaning | Related Commit Type | Example Usage |
|-------|------|---------|---------------------|---------------|
| ✨ | Sparkles | New feature addition | `feat` | `✨ feat(auth): add multi-factor authentication` |
| 🐛 | Bug | Bug fix | `fix` | `🐛 fix(parser): handle empty input correctly` |
| ♻️ | Recycle | Code refactoring | `refactor` | `♻️ refactor(api): simplify response handling` |
| 🧪 | Test Tube | Test addition/modification | `test` | `🧪 test(user): add tests for edge cases` |
| 📄 | Page | Documentation changes | `docs` | `📄 docs(readme): update installation steps` |
| 🧹 | Broom | Chore, maintenance | `chore` | `🧹 chore: update dependencies` |
| 🚀 | Rocket | Performance improvement | `perf` | `🚀 perf(query): optimize database access` |
| 💄 | Lipstick | UI/Style changes | `style` | `💄 style(button): update color scheme` |
| 🔒 | Lock | Security enhancement | `security` | `🔒 security(auth): strengthen password rules` |
| ⚙️ | Gear | Configuration changes | `config` | `⚙️ config(env): add new environment variables` |
| ⬆️ | Arrow Up | Dependency upgrade | `deps` | `⬆️ deps: upgrade pytest to 7.0.0` |
| ⬇️ | Arrow Down | Dependency downgrade | `deps` | `⬇️ deps: downgrade problematic package` |
| 🏗️ | Construction | Work in progress | `wip` | `🏗️ wip(feature): initial implementation` |
| ⏪ | Rewind | Revert changes | `revert` | `⏪ revert: remove broken feature (reverts #123)` |
| 🗑️ | Wastebasket | Removal/deprecation | `chore`, `refactor` | `🗑️ chore: remove deprecated functions` |
| 📦 | Package | Build/packaging | `build` | `📦 build: configure webpack setup` |
| 🔀 | Shuffle | Merge branch | `merge` | `🔀 merge: combine feature branch into main` |
| 🚩 | Flag | Feature flags | `feat` | `🚩 feat(beta): add feature toggle for new UI` |

#### 9.4. Extended Emoji Map

These emojis provide additional semantic context and may be used as needed:

| Emoji | Name | Meaning | Example Context |
|-------|------|---------|-----------------|
| 🎯 | Bullseye | Focus, target | Goal-specific commits, roadmap items |
| 🔍 | Magnifying Glass | Investigation, research | Exploring solutions, diagnosing issues |
| 🧩 | Puzzle Piece | Module/component | Module-specific changes, integration work |
| 🔄 | Arrows in Circle | Synchronization, workflow | Update flow, synchronization logic |
| 🧰 | Toolbox | Developer tools | Tooling improvements, utilities |
| 📊 | Chart | Analytics, metrics | Monitoring, measurement, reporting |
| 🚨 | Police Light | Critical warning | Breaking changes, migration notices |
| 🔧 | Wrench | Minor fix/adjustment | Small tweaks, configuration adjustments |
| 💾 | Floppy Disk | Data storage | Database schema, persistence layer |
| 🌐 | Globe | Internationalization | Translations, locale handling |
| 📱 | Mobile Phone | Mobile-specific | Mobile-responsive features |
| 🖥️ | Desktop | Desktop-specific | Desktop application features |
| 🔔 | Bell | Notifications | Alert system, notification services |
| 🎭 | Performing Arts | Mock/stub | Test mocks, fake implementations |
| 🧠 | Brain | AI/ML features | Machine learning, AI capabilities |
| 🔌 | Electric Plug | Plugin/extension | Extension system, integrations |
| 📝 | Memo | Notes, comments | Code comments, inline documentation |
| 🔗 | Link | Dependencies, references | Link related issues, cross-references |

#### 9.5. Usage Guidelines

##### 9.5.1. Commit Messages

*   **Placement:** Place the emoji at the beginning of the commit message summary, before the type/scope prefix.
    *   Correct: `✨ feat(auth): add login page`
    *   Also Acceptable: `feat(auth): ✨ add login page`
*   **Consistency:** Choose the emoji that best represents the primary purpose of the commit. Use only one primary emoji per commit message.
*   **PR Titles:** Follow the same convention for pull request titles.

##### 9.5.2. ModLog Entries

*   **Entry Type:** Use the relevant primary emoji to prefix each ModLog version entry.
    *   Example: `✨ Version: 0.2.0 - Added user authentication module`
*   **Feature Lists:** Consider using emojis for individual feature/change bullets within ModLog entries.
    *   Example: `- 🔒 [auth]: Implemented secure password storage`

##### 9.5.3. Documentation

*   **Status Markers:** Use emojis to indicate status in documentation.
    *   ✅ Complete/Done
    *   🔄 In Progress
    *   ⏳ Planned/Upcoming
    *   ⚠️ Warning/Caution
    *   ❌ Deprecated/Removed
*   **Section Headers:** Consider using relevant emojis for documentation section headers to enhance visual differentiation.

##### 9.5.4. User Interface (Optional)

If emojis are used in the UI:
*   Ensure accessibility considerations (screen readers, etc.).
*   Maintain consistent meaning with the ESM Protocol.
*   Use sparingly and purposefully to avoid overwhelming users.

#### 9.6. Automation & Tools

*   **Commit Hooks:** Consider implementing Git commit hooks that:
    *   Validate emoji usage according to ESM Protocol.
    *   Suggest appropriate emojis based on commit message content or branch name.
*   **ModLog Generation:** Use emojis to enhance automated changelog generation from commits.
*   **Visualization:** Enable filtering or color-coding Git history visualization tools based on commit emojis.

#### 9.7. Governance & Updates

*   **Adding New Emojis:** The ESM Protocol can be extended with new emojis when:
    *   A new semantic category emerges that isn't covered by existing emojis.
    *   The new emoji has a clear, distinct meaning with minimal overlap.
    *   The addition is documented in an updated version of this WSP.
*   **Deprecating Emojis:** Existing emojis should only be deprecated if:
    *   They cause technical issues (rendering problems, etc.).
    *   Their meaning has become ambiguous or confusing.
    *   A superior alternative has been identified.
    *   Deprecation is clearly documented with migration guidance.

#### 9.8. Compliance

*   **Expectation Level:** Emoji usage is **required** for commit messages and ModLog entries, **recommended** for documentation status markers, and **optional** for other contexts.
*   **Reviews:** Pull request reviewers should check for and suggest corrections to emoji usage (**WSP 6**).
*   **Auto-correction:** Tools may assist with compliance but should not block workflow for non-critical emoji issues.

#### 9.9. Related WSPs

*   **WSP 6 (Git Discipline):** ESM emojis complement conventional commit types.
*   **WSP 10 (ModLog):** ESM emojis enhance ModLog entries.
*   **WSP 0 (Protocol Overview):** ESM emojis support the "Audit-Readiness" principle.

---

### WSP 10: Modular Change Log & Versioning Convention

**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** Tracking changes across modules, versioning releases, and maintaining the Adaptive Project State (APS).

#### 10.1. Purpose

The **Modular Change Log & Versioning Convention** establishes a consistent, systematic approach to:

*   **Track Changes:** Record module-specific and project-wide changes in a structured, centralized format.
*   **Version Releases:** Apply industry-standard Semantic Versioning to tag and track software releases.
*   **Maintain History:** Create a comprehensive, searchable history of project evolution.
*   **Communicate Changes:** Enable clear communication of modifications to stakeholders.
*   **Support Automation:** Facilitate automated release note generation and version management.
*   **Adaptive Project State:** Maintain a living record of project progress, insights, and task status.

#### 10.2. Change Log (ModLog) Specification

##### 10.2.1. Primary Location & Format

*   **File:** `docs/ModLog.md`
*   **Format:** Markdown, following the structure defined in **Appendix B**.
*   **Order:** Chronological, with newest entries at the top.
*   **Ownership:** All developers must update the ModLog when making significant changes.

##### 10.2.2. Entry Structure

Each ModLog entry must include:

*   **Version Number:** Following Semantic Versioning 2.0.0 (described in Section 10.4).
*   **Date:** In YYYY-MM-DD format.
*   **Git Tag:** Corresponding Git tag (if applicable, e.g., `v1.2.3` or `clean-vX`).
*   **Description:** Brief summary of the changes in this version.
*   **Notes:** Additional context or considerations.
*   **Features/Fixes/Changes:** Bulleted list of specific changes, organized by module and component.

##### 10.2.3. Example ModLog Entry

```markdown
====================================================================
## MODLOG - [+UPDATES]:
- Version: 0.2.1
- Date: 2024-03-15
- Git Tag: v0.2.1
- Description: Fixed critical authentication issues and improved error handling.
- Notes: Fixes reported security vulnerability CVE-2024-XXXXX.
- Features/Fixes/Changes:
  - 🔒 [auth:TokenManager] - Fixed token expiration validation (Issue #45)
  - 🐛 [auth:OAuth] - Corrected refresh token handling
  - ♻️ [core:ErrorHandler] - Refactored error handling for better logging
  - 🧪 [tests] - Added comprehensive tests for auth module
  - ✨ [Module: Interface] - Defined initial data contract for authentication
  - 🚨 [Module: Interface] - BREAKING CHANGE: Modified signature of verify() method
  - ⬆️ [Module: Deps] - Updated JWT library to version 2.0
====================================================================
```

##### 10.2.4. When to Create ModLog Entries

New entries should be created for:

*   **Official Releases:** Any time a release is tagged with a version number.
*   **Clean States:** When a new Clean State is created (**WSP 2**).
*   **Significant Features:** When a major feature or module is completed.
*   **Critical Fixes:** When important bugs are fixed, especially security issues.
*   **Architectural Changes:** When significant architectural modifications occur.

ModLog entries are not required for routine minor changes or work-in-progress commits.

#### 10.3. Adaptive Project State (APS)

The APS is a living record maintained within `foundups_global_rules.md` that complements the more formal, snapshot-based ModLog.

##### 10.3.1. APS Sections

*   **Task List:** Current tasks (in-progress, completed, blocked) with statuses and metadata.
*   **Project Insights:** Lessons learned, technical decisions, and architectural insights.

##### 10.3.2. APS Status Markers

Tasks in the APS Task List should use the following status markers:

*   **[✅]** - Complete
*   **[⚒️]** - In Progress
*   **[💡]** - Planned/Ideation
*   **[⛔]** - Blocked/Issue

##### 10.3.3. APS Update Workflow

*   **Automatic Updates:** The AI assistant is responsible for regularly updating the APS upon:
    *   Task completion
    *   The `save` command (see **Appendix E**)
    *   Context saturation thresholds
*   **Manual Updates:** Developers may directly update the APS when:
    *   Initiating new tasks
    *   Updating task status not captured by the AI
    *   Adding project insights from external discussions
*   **Synchronization:** The APS should be periodically synchronized with the ModLog to ensure consistency.

#### 10.4. Semantic Versioning Specification

FoundUps strictly adheres to [**Semantic Versioning 2.0.0**](https://semver.org/) for all official releases.

##### 10.4.1. Version Format

*   **Format:** MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
*   **Examples:**
    *   `0.1.0` (Initial Prototype release)
    *   `0.2.5` (Prototype with bug fixes)
    *   `1.0.0-rc.1` (Release Candidate 1 for MVP)
    *   `1.0.0` (First stable MVP release)

##### 10.4.2. Incrementing Rules

*   **MAJOR:** Increment when making incompatible API changes.
    *   Increasing MAJOR resets MINOR and PATCH to 0.
    *   MAJOR version 0 (0.y.z) is for initial development (PoC, Prototype). Anything may change at any time.
    *   MAJOR version 1+ indicates stability and production readiness (MVP).
    *   **Backward-incompatible changes to the public interface defined via WSP 11 MUST increment the MAJOR version (once > 1.0.0).**
*   **MINOR:** Increment when adding functionality in a backward-compatible manner.
    *   Increasing MINOR resets PATCH to 0.
    *   **Backward-compatible additions to the public interface SHOULD increment the MINOR version.**
*   **PATCH:** Increment when making backward-compatible bug fixes.
    *   **Changes to dependencies (WSP 12) that don't affect the module's own interface typically only require a PATCH increment, unless they necessitate interface changes.**
*   **PRERELEASE:** Add suffixes like `-alpha.1`, `-beta.2`, `-rc.1` for pre-releases.
*   **BUILD:** Add metadata like `+20240315` or `+git8126abc` after a plus sign if needed.

##### 10.4.3. Development Stage Mapping

Version numbers map to development stages as defined in **WSP 8**:

*   **Proof-of-Concept (PoC):** 0.0.x
*   **Prototype:** 0.1.x - 0.9.x
*   **MVP (Production):** 1.0.0+

#### 10.5. Git Tagging & Releases

##### 10.5.1. Version Tags

*   **Format:** `vX.Y.Z[-prerelease]` (e.g., `v0.2.1`, `v1.0.0-beta.2`)
*   **Type:** Always use annotated tags: `git tag -a vX.Y.Z -m "Release vX.Y.Z: Brief description"`
*   **Process:**
    1.  Ensure all tests pass and FMAS checks succeed.
    2.  Update the ModLog with the new version entry.
    3.  Create and push the annotated tag.
    4.  Consider creating a corresponding Clean State (**WSP 2**) for significant versions.

##### 10.5.2. Clean State Tags

*   **Format:** `clean-vX` (e.g., `clean-v4`)
*   **Process:** Follow the Clean State creation procedure in **WSP 2**.

##### 10.5.3. GitHub Releases

For official releases, consider creating a GitHub Release:

*   **Title:** Version number and brief description (e.g., `v1.0.0 - Initial MVP Release`)
*   **Description:** Copy relevant content from the ModLog entry.
*   **Attachments:** Consider attaching build artifacts or documentation if applicable.

#### 10.6. Workflows & Integration

##### 10.6.1. Release Workflow

1.  **Preparation:**
    *   Ensure all intended features for the release are complete and merged.
    *   Run full Test Audit (**WSP 5**) to verify test coverage and quality.
    *   Run FMAS (**WSP 3**) to verify structural compliance.
    *   Perform regression comparison (**WSP 7**) against the previous stable version.
2.  **Version Determination:**
    *   Decide on the appropriate version increment based on the nature of changes.
    *   Review development stage (**WSP 8**) to ensure version aligns with maturity.
3.  **Documentation:**
    *   Create a new ModLog entry with the version, date, and detailed changes.
    *   Update any version references in code or documentation.
4.  **Release Process:**
    *   Create and push the annotated Git tag.
    *   Consider creating a Clean State snapshot (**WSP 2**).
    *   Create a GitHub Release if appropriate.

##### 10.6.2. Continuous Integration

*   **Automated Builds:** Consider generating build numbers or dev versions for CI builds.
*   **Pre-release Deployment:** Use pre-release versions for testing environments.
*   **Release Verification:** Automate checks that versions in code, ModLog, and tags are aligned.

#### 10.7. Module-Specific Versioning

Individual modules may maintain their own internal version numbers, but these should:

*   **Align with Project Versions:** Generally follow the main project's versioning scheme.
*   **Document in Module:** Include the module's version in its README or a `VERSION` constant.
*   **Record in ModLog:** Reference module-specific versions in the project-wide ModLog.

#### 10.8. Related WSPs

*   **WSP 2 (Clean States):** Defines when to create clean states, which often correspond to version tags.
*   **WSP 3 (FMAS):** Verification required before creating release versions.
*   **WSP 5 (Test Audit):** Quality gates required before versioning releases.
*   **WSP 6 (Git Discipline):** Defines Git tagging conventions related to versioning.
*   **WSP 7 (Regression Detection):** Verifies no regressions before versioning.
*   **WSP 8 (Milestone Rules):** Maps development stages to version number ranges.
*   **WSP 9 (ESM Protocol):** Defines emojis used in ModLog entries.
*   **WSP 11 (Interface Definition):** Interface changes drive versioning decisions.
*   **WSP 12 (Dependency Management):** Dependency changes are tracked in ModLog.

---

### WSP 11: Module Interface Definition & Validation

**Document Version:** 1.0  
**Date:** [Insert Date]  
**Status:** Active  
**Applies To:** Definition, documentation, and validation of interfaces for all modules intended for reuse or inter-module communication.

#### 11.1. Purpose

To ensure modules have clearly defined, documented, and validated boundaries (interfaces/APIs/contracts) enabling reliable integration, interoperability ("slot-ability"), and independent development, as required by the 0102 modularization goal.

#### 11.2. Scope

This WSP applies to:

* Modules created or refactored during module refactoring (WSP 1) and new module creation.
* Any module exposing functionality or data for consumption by other modules or external systems.
* Standards for interface identification, documentation, and validation.

#### 11.3. Interface Principles

* **Explicitness:** Interfaces must be explicitly defined, not just implied.
* **Minimality:** Expose only necessary functionality/data (Least Privilege).
* **Stability:** Aim for stable interfaces; breaking changes require careful management (WSP 10).
* **Discoverability:** Interfaces should be easily discoverable and understandable.

#### 11.4. Interface Identification (0102 Task)

* **Analysis:** During refactoring planning (WSP 1.4a) or new module design, 0102 analyzes code interactions (function calls, data exchange) to identify potential interface points.
* **Proposal:** 0102 proposes the public interface (functions, classes, methods, data structures, API endpoints, events, etc.).
* **Confirmation:** User/Developer reviews and confirms the proposed interface.

#### 11.5. Interface Definition & Documentation Standard

* **Requirement:** Each module MUST have a defined interface artifact.
* **Format (Project Specific):** The specific format MUST be defined in .foundups_project_rules. Options include:
  * **Code Annotations:** Decorators, docstrings following a strict format (e.g., Sphinx, JavaDoc).
  * **Dedicated Files:**
    * INTERFACE.md: Markdown describing functions, parameters, returns, data structures.
    * openapi.yaml/swagger.json: For RESTful APIs.
    * *.proto: For gRPC/Protobuf interfaces.
    * schema.json: For data structure validation.
  * **Language Constructs:** Language features like interfaces (Java/C#), traits (Rust), protocols (Swift), or explicit exports (__init__.py, index.js).
* **Content:** The definition MUST clearly specify:
  * Function/Method signatures (names, parameters, types, return types).
  * Data structures/object schemas (fields, types, constraints).
  * API endpoints (URLs, methods, request/response bodies).
  * Events emitted/consumed (names, payload schemas).
  * Error conditions and return values/exceptions.
* **Location:** Standard location within module directory (e.g., root, docs/, interface/). Checked by FMAS (WSP 3).

#### 11.6. Interface Validation (Contract Testing)

* **Requirement:** Modules MUST have tests validating adherence to their defined interface (part of WSP 5 Test Audit).
* **Methodology (Project Specific):**
  * **Schema Validation:** Validate data structures against schemas (schema.json, Protobuf definitions).
  * **API Testing:** Use tools like requests, curl, Postman (collections), or specific frameworks to test API endpoints against OpenAPI specs.
  * **Mocking/Stubbing:** Use provider/consumer testing tools (e.g., Pact) to verify interactions between modules without full integration.
  * **Static Analysis:** Tools checking function signatures match definitions.
* **Execution:** Contract tests run as part of WSP 5.

#### 11.7. Workflow Integration

* **WSP 1:** Interface proposed during planning, defined/updated during refactoring.
* **WSP 3:** FMAS checks for existence of interface artifacts.
* **WSP 5:** Contract tests executed during Test Audit.
* **WSP 6:** Interface artifacts committed and versioned. Interface changes reflected in commit messages (e.g., feat(mymodule:iface): ..., fix(mymodule:iface): ...).
* **WSP 7:** Interface files included in regression checks.
* **WSP 8:** Stable interface required for MVP transition.
* **WSP 10:** Interface changes (especially breaking) drive SemVer and ModLog entries.

#### 11.8. AI Agent Role (0102)

* Proposes initial interface based on code analysis.
* Generates skeleton interface documentation/definition files.
* Potentially generates basic contract test stubs.
* Flags potential breaking changes during refactoring.

---

### WSP 12: Dependency Management & Packaging

**Document Version:** 1.0  
**Date:** [Insert Date]  
**Status:** Active  
**Applies To:** Identification, declaration, and management of dependencies for all modules.

#### 12.1. Purpose

To systematically manage internal and external dependencies for modules, ensuring reproducibility, resolving conflicts, and facilitating packaging for distribution and reuse, supporting the 0102 universal modularization goal.

#### 12.2. Scope

* Applies during module refactoring (WSP 1) and new module creation.
* Defines standards for dependency identification, declaration, versioning, and basic packaging considerations.

#### 12.3. Dependency Principles

* **Explicitness:** All dependencies MUST be explicitly declared.
* **Isolation:** Aim for modules with minimal, well-defined dependencies.
* **Versioning:** Use explicit version constraints for dependencies.
* **Auditability:** Dependency manifests must be version-controlled.

#### 12.4. Dependency Identification (0102 Task)

* **Analysis:** During refactoring planning (WSP 1.4a) or new module design, 0102 analyzes code (imports, library calls, build files) to identify dependencies.
* **Classification:** 0102 classifies dependencies as:
  * **Internal:** Other modules within the FoundUps project.
  * **External:** Third-party libraries/packages.
  * **System:** OS-level tools or libraries (e.g., ffmpeg, imagemagick).
* **Proposal:** 0102 proposes a list of dependencies with suggested versions.
* **Confirmation:** User/Developer reviews and confirms the dependency list.

#### 12.5. Dependency Declaration Standard

* **Requirement:** Each module that has dependencies MUST declare them in a standard manifest file.
* **Format (Language/Project Specific):** Use standard tooling for the language/ecosystem. Defined in .foundups_project_rules. Examples:
  * **Python:** requirements.txt, pyproject.toml (Poetry/PDM)
  * **Node.js:** package.json
  * **Java:** pom.xml (Maven), build.gradle (Gradle)
  * **Go:** go.mod
  * **Rust:** Cargo.toml
  * **Generic:** A custom dependencies.yaml or similar.
* **Content:** The manifest MUST specify:
  * Dependency name (package, library, module).
  * Version constraint (e.g., ==1.2.3, ~=1.2, >=1,<2, specific commit hash for internal modules). Use specific versions where possible for stability.
  * Scope (optional, e.g., dev, test, runtime).
* **Location:** Standard location within module directory (e.g., root). Checked by FMAS (WSP 3).

#### 12.6. Versioning & Conflict Resolution

* **Pinning:** External dependencies SHOULD be pinned to specific versions (==X.Y.Z) in module manifests for maximum reproducibility during module development and testing.
* **Range Strategy (Project Level):** The project-level dependency management (combining modules) MAY use version ranges (~=, >=) but requires a robust conflict resolution strategy (e.g., using dependency resolution tools like pip, npm, maven, poetry). This strategy must be defined in foundups_global_rules.md.
* **Internal Dependencies:** Internal dependencies MAY reference specific commit hashes or version tags (clean-vX, vX.Y.Z) for tight coupling if needed, or rely on the project-level build process to resolve local paths.

#### 12.7. Packaging Considerations (Informational)

* While full packaging is beyond this WSP, the defined structure (src/, tests/, interface/dependency manifests) facilitates packaging.
* The chosen packaging method (e.g., creating a wheel/jar/npm package, Docker container) should leverage the artifacts mandated by WSP 1, 11, and 12. Packaging methods should be defined at the project level.

#### 12.8. Workflow Integration

* **WSP 1:** Dependencies identified during planning, declared during refactoring.
* **WSP 3:** FMAS checks for existence and basic format of dependency manifests.
* **WSP 6:** Dependency manifests committed and versioned. Dependency changes reflected in commit messages (e.g., chore(mymodule:deps): update library X).
* **WSP 7:** Dependency manifests included in regression checks.
* **WSP 8:** Declared dependencies required for MVP transition.
* **WSP 10:** Significant dependency updates noted in ModLog.

#### 12.9. AI Agent Role (0102)

* Identifies dependencies via code analysis.
* Proposes dependency list and versions.
* Formats entries for standard manifest files.
* Flags potential version conflicts based on project rules or known incompatibilities.

---

## III. Appendices

### Appendix A: WSP Prompt Template

*(Template defining Task, Scope, Constraints, Baseline, Validation for invoking WSP actions)*
```markdown
# WSP X: Title

**Usage Convention:**
* Use `# WSP:` prefix in task descriptions to indicate this is a Windsurf Protocol task
* Example: `# WSP: Implement cooldown check in QuotaManager.check_quota()`
* After task completion, ask: "Would you like me to add this change to the ModLog?"
* Use `# WSP+:` prefix for adding items to the TODO List

**CRITICAL: You MUST execute *ONLY* the Task described below. Absolutely NO modifications outside of the specified file and function(s) are permitted.**

## Task:
[Insert specific task here. Be extremely concise. Example: "Implement cooldown check in `QuotaManager.check_quota()` using `time.time()`."]

## Scope:
* **File:** `[/path/to/module.py]`
* **Target Function(s):** [List specific function(s) to modify. Example: `QuotaManager.check_quota()`, `QuotaManager.reset_quota()`]

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

# WARNING:
This is a strict Windsurf protocol. Each prompt is atomic. Each file is treated as sacred. No modifications outside the stated scope are permitted. Violations will result in rejection.
```

### Appendix B: Roadmap & ModLog Format Templates

*(These templates define the standard structure for the project roadmap and ModLog entries found in `docs/ModLog.md`.)*

#### Roadmap Structure Template

```markdown
# FoundUps Agent Modular Change Log

This log tracks module changes, updates, and versioning for FoundUps Agent under the Windsurf modular development model.

## FoundUps-Agent Roadmap

### Status Ledger
- ✅ Complete
- 🔄 In Progress
- ⏳ Planned
- ⚠️ Deprecated

### ✅ Proof of Concept (0.0.x)
- [ ] [Task 1]
- [ ] [Task 2]

### 🔄 +Prototype (0.1.x - 0.9.x)
- [ ] [Feature 1]
- [ ] [Feature 2]

### 🔄 [High Priority System Name]
- [ ] [Task 1]
- [ ] [Task 2]

### 🔄 [Medium Priority System Name]
- [ ] [Task 1]
- [ ] [Task 2]

### 🔄 [Lower Priority System Name]
- [ ] [Task 1]
- [ ] [Task 2]

### ⏳ Minimum Viable Product (1.0.x+)
- [ ] [MVP Feature 1]
- [ ] [MVP Feature 2]

#### TODO List *Use `[+todo]` or `[+WSP]` commit convention prefix or add manually here.*
**/[Task Name]** - @[Assignee/Team] - priority: [PriorityScore]
- [ ] [Subtask 1]
- [ ] [Subtask 2]

## 🧩 MVP Release Phases

### ⏳ [Phase 1 Name]
- [ ] [Task 1]
- [ ] [Task 2]

### ⏳ [Phase 2 Name]
- [ ] [Task 1]
- [ ] [Task 2]

### 🔄 [Phase 3 Name]
- [ ] [Task 1]
- [ ] [Task 2]

====================================================================
```

#### ModLog Entry Format Template

```markdown
====================================================================
## MODLOG - [+UPDATES]:
- Version: [X.Y.Z]
- Date: [YYYY-MM-DD]
- Git Tag: [Associated tag, e.g., vX.Y.Z or clean-vX]
- Description: [Brief description of changes in this version/log entry]
- Notes: [Additional context or considerations]
- Features/Fixes/Changes:
  - [Module: Component] - Description of change 1 (Issue #123)
  - [Module: Component] - Description of change 2
  - ...
====================================================================
```

#### Version Guide Template

```markdown
====================================================================
## VERSION GUIDE
### Development Phases:
- #### POC (0.0.x): Initial development and proof of concept
  - 0.0.1: First working version
  - 0.0.2-0.0.9: POC improvements and fixes
- #### Prototype (0.1.x - 0.9.x): Feature development and testing
  - 0.1.x: Basic feature set
  - 0.2.x-0.9.x: Feature expansion and refinement
- #### MVP (1.0.x+): Production-ready releases
  - 1.0.0: First stable release
  - 1.x.x: Production updates and improvements
====================================================================
```