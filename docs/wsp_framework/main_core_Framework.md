# FILE START: WSP_Development_Framework.md

# FoundUps WindSurf Protocol (WSP) — Development Framework

**Version:** 2.1 (Post-Refactor with separate Appendices)
**Date Updated:** [Current Date]
**Status:** Active

**Purpose:** This document provides the core procedural guidelines, workflows, and standards for development within the FoundUps Agent MMAS. It is designed for direct use by developers and AI agents (like 0102) engaged in coding, testing, and system maintenance tasks. This framework is intentionally lean on deep semantic theory, focusing on actionable procedures.

For practical templates, command details, and development-focused supplementary materials, refer to `docs/WSP_Development_Appendices.md`.
For the underlying semantic, consciousness, and advanced AI integration philosophies (including LLME definitions, rESP, Ø1Ø2, DAE concepts), please refer to `docs/WSP_Agentic_Framework.md`.

---

## 🚀 QUICK START: Actionable Development Guide

### "What Should I Code Next?" - Decision Tree
START HERE
│
├─ 🔍 Is this a NEW feature/module?
│ │
│ ├─ YES → Go to: NEW MODULE WORKFLOW
│ │
│ └─ NO → Is this fixing/improving EXISTING code?
│ │
│ ├─ YES → Go to: EXISTING CODE WORKFLOW
│ │
│ └─ NO → Is this TESTING related?
│ │
│ ├─ YES → Go to: TESTING WORKFLOW
│ │
│ └─ NO → Go to: PROJECT MANAGEMENT (See WSP 11)

### NEW MODULE Quick Workflow

#### Step 1: Domain Placement Decision
Refer to WSP 3: Enterprise Domain Architecture for full details.
**🏢 Enterprise Domain Structure:**
├─ ai_intelligence/ → AI logic, LLMs, decision engines, banter systems
├─ communication/ → Chat, messages, protocols, live interactions
├─ platform_integration/ → External APIs (YouTube, OAuth), stream handling
├─ infrastructure/ → Core systems, agents, auth, session management
├─ monitoring/ → Logging, metrics, health, system status
├─ development/ → Tools, testing, utilities, automation
├─ foundups/ → Individual FoundUps projects (modular, autonomous applications)
├─ gamification/ → Engagement mechanics, rewards, token loops, behavioral recursion
└─ blockchain/ → Decentralized infrastructure, chain integrations, token logic, DAE persistence

#### Step 2: WSP 1 Structure Implementation
Refer to WSP 1: Module Refactoring to Windsurf Structure for full details.
**Required Module Structure:**
modules/<domain>/<module_name>/
├─ src/ ← Your implementation code
│ ├─ init.py ← Usually empty
│ └─ <module_name>.py ← Main module implementation
├─ tests/ ← All test files
│ ├─ init.py ← Usually empty
│ ├─ README.md ← MANDATORY (WSP 14) - Test documentation
│ └─ test_<name>.py ← Test implementation
└─ init.py ← Public API definition (WSP 12)

#### Step 3: Implementation Checklist
**✅ BEFORE YOU START CODING:**
- [ ] Run: `python tools/modular_audit/modular_audit.py ./modules` (WSP 4)
- [ ] Search existing: `grep -r "your_concept" modules/` (Avoid duplication)
- [ ] Read patterns: `modules/<domain>/*/tests/README.md` (Learn established patterns, WSP 14)
- [ ] Check LLME scores: Review existing module complexity and targets (WSP 5). (LLME defined in `WSP_Agentic_Framework.md`)

**✅ WHILE CODING:**
- [ ] Define public API in module `__init__.py` (WSP 12)
- [ ] Add dependencies to `requirements.txt` (WSP 13)
- [ ] Create tests as you write code (WSP 6 / WSP 14 - 90% coverage target)
- [ ] Document patterns in `tests/README.md` (WSP 14)

**✅ BEFORE COMMIT:**
- [ ] Tests pass: `pytest modules/<domain>/<module>/tests/ -v` (WSP 6)
- [ ] System clean: `python tools/modular_audit/modular_audit.py ./modules` (WSP 4)
- [ ] Coverage ≥90%: `pytest --cov=modules.<domain>.<module>.src --cov-report=term-missing` (WSP 6)
- [ ] Update documentation: `tests/README.md` with new test descriptions (WSP 14)

---

### EXISTING CODE Quick Workflow

#### Step 1: Change Type Identification
🔍 WHAT TYPE OF CHANGE?
│
├─ 🐛 Bug Fix → Immediate Actions
├─ ✨ Feature Addition → Feature Decision
├─ ♻️ Refactoring → High-Risk Process (See WSP 1 for full details)
├─ 📈 Performance → Optimization Process
└─ 🧪 Testing → Testing Workflow


#### Bug Fix Immediate Actions
**🎯 TEST-FIRST APPROACH:**
1. **Reproduce:** Create failing test that demonstrates the bug (WSP 14)
2. **Locate:** `grep -r "error_pattern" modules/` to find related code
3. **Analyze:** Check WSP 13 dependencies and WSP 12 interfaces
4. **Fix:** Make minimal change to make test pass
5. **Verify:** Run full test suite for affected modules (WSP 6)

**📋 Validation Requirements:**
- [ ] Failing test now passes
- [ ] No regression: `pytest modules/<affected_domain>/` all pass
- [ ] System clean: `python tools/modular_audit/modular_audit.py ./modules` (WSP 4)
- [ ] Related tests updated if behavior changed (WSP 14)

#### Feature Addition Decision
**🎯 CRITICAL DECISION:** Does this fit in existing module structure?

**✅ YES - Extends Existing Module:**
1. Read existing `tests/README.md` for established patterns (WSP 14)
2. Follow existing code style and architectural patterns
3. Update module `__init__.py` if adding public API (WSP 12)
4. Add comprehensive tests maintaining 90% coverage (WSP 6, WSP 14)
5. Update `tests/README.md` with new functionality description (WSP 14)

**❌ NO - Requires New Module:**
→ Return to: [NEW MODULE WORKFLOW](#new-module-quick-workflow)

#### Refactoring High-Risk Process
Refer to WSP 1 for full procedural details.
**⚠️ EXTRA VALIDATION REQUIRED - HIGH IMPACT ACTIVITY**

**🛡️ SAFETY MEASURES (BEFORE STARTING):**
- [ ] Create clean state: Follow WSP 2 snapshot process
- [ ] Full test baseline: `pytest modules/` (all tests must pass)
- [ ] FMAS baseline: `python tools/modular_audit/modular_audit.py ./modules --baseline` (WSP 4)
- [ ] Document current state: Update `docs/clean_states.md` (WSP 2)

**🔄 DURING REFACTORING:**
- [ ] Maintain API compatibility: Follow WSP 12 interface requirements
- [ ] Update imports systematically: `git grep -l "old.import.path"`
- [ ] Test frequently: `pytest -x` (stop on first failure)
- [ ] Monitor coverage: Ensure no degradation (WSP 6)

**✅ POST-REFACTORING VALIDATION:**
- [ ] All tests pass: `pytest modules/`
- [ ] FMAS comparison: Check against baseline snapshot (WSP 4)
- [ ] Integration testing: Test dependent modules
- [ ] Documentation: Update if interfaces changed (WSP 12, WSP 14)

#### Optimization Process
1.  **Identify Bottleneck:** Use profiling tools to pinpoint performance issues.
2.  **Establish Baseline:** Measure current performance with benchmarks.
3.  **Hypothesize & Implement:** Propose and code optimization.
4.  **Test Functionality:** Ensure no regressions with existing tests (WSP 6).
5.  **Measure Impact:** Re-run benchmarks to quantify improvement.
6.  **Verify:** Run full test suite. Check FMAS (WSP 4).
7.  **Document:** Note changes and performance gains (WSP 11).

---

### TESTING Quick Workflow

#### Test Type Decision Tree
🧪 WHAT KIND OF TESTING?
│
├─ 🆕 New Test Creation → WSP 14 Process (See WSP 14 for full details)
├─ 🔧 Fixing Failing Tests → Debug Process
├─ 📊 Coverage Improvement → Coverage Strategy (See WSP 6 for targets)
└─ 🔄 Test Refactoring → Test Maintenance

#### WSP 14 Test Creation (Quick)
Refer to WSP 14: Test Creation & Management Procedures for full details.
**🎯 MANDATORY FIRST STEP:** Read `tests/README.md` in target module

**WSP 14 Compliance Protocol:**
- [ ] Analyze existing test patterns in the module
- [ ] Identify opportunities to extend existing test classes vs. create new
- [ ] Prioritize extending existing tests when logically feasible
- [ ] Follow established naming conventions and patterns

**Creation Workflow:**
1. **Study:** Review `modules/<domain>/<module>/tests/README.md`
2. **Decide:** Extend existing test class OR create new test file?
3. **Implement:** Follow naming `test_<functionality>.py`
4. **Pattern:** Use existing mocking and testing patterns
5. **Document:** Update `tests/README.md` with test description

#### Test Debugging Process
1.  **Isolate Failure:** Run the specific failing test: `pytest path/to/test_file.py::TestClass::test_method -v`
2.  **Analyze Error:** Understand the traceback and assertion failure.
3.  **Inspect Code:** Review the code being tested and the test itself.
4.  **Hypothesize & Debug:** Use print statements, debugger, or log analysis.
5.  **Fix & Verify:** Correct the code or test, re-run the specific test, then the suite.

#### Coverage Improvement (Quick)
Refer to WSP 6: Test Audit & Coverage Verification for targets.
**🎯 WSP 6 TARGET:** ≥90% coverage for all modules

**Quick Coverage Assessment:**
```bash
# Single module coverage
pytest modules/<domain>/<module>/tests/ --cov=modules.<domain>.<module>.src --cov-report=term-missing

# Full system coverage
pytest modules/ --cov=modules --cov-report=html

#### Coverage Enhancement Strategy:
- **Gap Analysis:** Focus on "Missing" lines in coverage report.
- **Priority:** Target critical paths, error handling, edge cases (informed by module LLME score from WSP 5; LLME defined in `WSP_Agentic_Framework.md`).
- **Implementation:** Add tests for uncovered branches and conditions (WSP 14).
- **Validation:** Re-run coverage to confirm improvement.

#### Test Refactoring
- **Identify Need:** Poorly structured, slow, or flaky tests.
- **Preserve Behavior:** Ensure refactoring doesn't change what's being tested (unless intended).
- **Improve Clarity:** Enhance readability and maintainability.
- **Verify:** Ensure all tests still pass. Update `tests/README.md` if structure changes (WSP 14).

---

## I. Defining and Using WSPs (Core AI Interaction for Development)

**AI Assistant Interaction Guidelines (FoundUps Interaction Protocol):**
*(Adapted from RuleSurf Principles)*
*   **Proactive Updates:** AI should suggest updates to project rules (`foundups_global_rules.md`, `.foundups_project_rules` - see `WSP_Development_Appendices.md`) if requirements seem to change, notifying the user. This includes suggesting updates to a module's LLME score (WSP 5) if its state, impact, or importance demonstrably changes (LLME definition in `WSP_Agentic_Framework.md`).
*   **Scaffolding Prioritization:** Build user-testable structures first (UI or logical flow), then implement component details.
*   **No Invention:** Do not invent functionality or change UI/logic without explicit user direction.
*   **Verification Steps:** Clearly describe user testing/verification steps upon completing components.
*   **Error Analysis:** Automatically check logs/problem reports post-changes, analyze errors, propose solutions with Confidence Levels (CL%), and preserve context.
*   **Repetition Handling:** If user repeats similar instructions 3+ times, suggest creating a new standard command/procedure (see `WSP_Development_Appendices.md`). This may include recurring LLME assessments.
*   **Test Management & Documentation (`tests/README.md` - WSP 14):**
    *   **Before Creating/Modifying Tests:** When tasked with adding or modifying tests within a module (`modules/<module_name>/tests/`), FIRST read the `tests/README.md` file in that directory. Analyze the descriptions and file list to identify any existing tests covering similar functionality or source code areas. Also, review current code coverage reports (`pytest-cov`) if available.
    *   **Prioritize Extension:** Explicitly prioritize *extending* existing, relevant test files/classes/functions over creating new ones if feasible and logical. State the intention to extend an existing test if applicable.
    *   **Update README:** After successfully adding a new test file OR significantly modifying/extending existing tests (e.g., adding new major scenarios), update the `tests/README.md` file to accurately reflect the current test suite structure and coverage. Add/update the file entry and description. Prompt the user for confirmation on the description if needed.
*   **Web Search:** Utilize web searches aggressively to inform solutions and verify information.
*   **Analytical Reasoning & Justification:**
    *   Provide evidence-based rationale for significant choices. This includes justification for proposed LLME scores or changes.
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
    *   `@80%`: Prompt user to `save` context (updates rules, saves tech context, lists open threads). (See `save` command in `WSP_Development_Appendices.md`)
    *   `@95%`: Automatically trigger `save` context action in the next reply.
*   **Standard Commands:** Utilize the defined commands for common actions (See `WSP_Development_Appendices.md` - Appendix C).

**High-Level Project Cycle (RPC Reference):**
*(Referenced from RuleSurf RPC)*
1.  *User:* Ideate, clarify, define Project Prompt/Requirements (stored in `.foundups_project_rules`), including initial or target LLME scores for key components. (LLME defined in `WSP_Agentic_Framework.md`).
2.  *AI:* Generate detailed plan (milestones, tasks) based on prompt (stored in `foundups_global_rules.md`).
3.  *AI:* Set up project environment, dependencies, initial structure.
4.  *Both:* Execute component sub-cycles:
    *   AI builds component.
    *   User tests component.
    *   Both debug (AI proposes fixes).
    *   AI adds/runs core tests until passing (WSP 6, WSP 14).
    *   AI/User assess and update module LLME score (WSP 5).
5.  *AI:* Proceed to next component (repeat step 4).
6.  *User:* Final QA and sign-off.

**Memory & Rule Hierarchy Overview (Development Context):**
(Refer to `WSP_Development_Appendices.md` - Appendix D)

---

## II. Core Windsurf Standard Procedures (WSPs)

### WSP 0: Protocol Overview & Enforcement Rules

**Version:** 2.0
**Status:** Active

#### 0.1. Introduction & Purpose
The **Windsurf Protocol** is a strict, procedural enforcement system governing development within FoundUps, ensuring consistency, verifiability, testability, and MMAS compatibility. It dictates *how* tasks are defined, executed, and validated. For semantic context and LLME rating system details, refer to `WSP_Agentic_Framework.md`.

#### 0.2. Role within MMAS
Windsurf is the execution layer of MMAS. WSPs are the enforceable procedures required to meet MMAS quality goals.

#### 0.3. Enforcement Philosophy
*   **Mandatory Compliance:** WSPs are not optional. This document (`WSP_Development_Framework.md`), `WSP_Development_Appendices.md`, and `WSP_Agentic_Framework.md` constitute the full protocol.
*   **Atomicity:** Tasks must be the smallest verifiable units.
*   **Scope Constraint:** Operate strictly within defined scope (see WSP Prompt Template in `WSP_Development_Appendices.md`).
*   **Test-Driven Action:** Validate changes via `pytest`, FMAS per WSP.
*   **Audit-Readiness:** Actions must be traceable (logs, commits, Clean States, tags, validation outputs, LLME score history - see WSP 2, WSP 7, WSP 11).

#### 0.4. Standard Execution Flow
1.  **Task Declaration (WSP Prompt):** Define goal, scope, constraints, potentially target LLME (See WSP Prompt Template in `WSP_Development_Appendices.md`).
2.  **Scope Lock & Confirmation:** Agent confirms understanding.
3.  **Execution:** Perform action per WSP and scope.
4.  **Validation:** Verify outcome using specified methods (FMAS, `pytest`, diff - see WSP 4,
---