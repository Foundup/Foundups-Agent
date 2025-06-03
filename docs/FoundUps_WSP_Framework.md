# FoundUps WindSurf Protocol system (WSP) Framework


This document outlines the core Windsurf Standard Procedures (WSPs) governing development, testing, and compliance within the FoundUps Agent MMAS. This version integrates the **LLME Semantic Triplet Rating System (see Appendix G)** to provide a deeper semantic understanding of module state, impact, and importance.


---


## 🚀 QUICK START: Actionable Development Guide


### "What Should I Code Next?" - Decision Tree


```
START HERE
│
├─ 🔍 Is this a NEW feature/module?
│  │
│  ├─ YES → Go to: [NEW MODULE WORKFLOW](#new-module-quick-workflow)
│  │
│  └─ NO → Is this fixing/improving EXISTING code?
│     │
│     ├─ YES → Go to: [EXISTING CODE WORKFLOW](#existing-code-quick-workflow)
│     │
│     └─ NO → Is this TESTING related?
│        │
│        ├─ YES → Go to: [TESTING WORKFLOW](#testing-quick-workflow)
│        │
│        └─ NO → Go to: [PROJECT MANAGEMENT](#project-status-workflow)
```


### NEW MODULE Quick Workflow


#### Step 1: Domain Placement Decision
**🏢 Enterprise Domain Structure:**
```
├─ ai_intelligence/          → AI logic, LLMs, decision engines, banter systems
├─ communication/           → Chat, messages, protocols, live interactions
├─ platform_integration/    → External APIs (YouTube, OAuth), stream handling
├─ infrastructure/          → Core systems, agents, auth, session management
├─ monitoring/             → Logging, metrics, health, system status
├─ development/            → Tools, testing, utilities, automation
├─ foundups/               → Individual FoundUps projects (modular, autonomous applications)
├─ gamification/           → Engagement mechanics, rewards, token loops, behavioral recursion
└─ blockchain/             → Decentralized infrastructure, chain integrations, token logic, DAE persistence
```

#### Step 2: WSP 1 Structure Implementation
**Required Module Structure:**
```
modules/<domain>/<module_name>/
├─ src/                 ← Your implementation code
│  ├─ __init__.py      ← Usually empty
│  └─ <module_name>.py ← Main module implementation
├─ tests/              ← All test files
│  ├─ __init__.py      ← Usually empty
│  ├─ README.md        ← MANDATORY (WSP 13) - Test documentation
│  └─ test_<name>.py   ← Test implementation
└─ __init__.py         ← Public API definition (WSP 11)
```

#### Step 3: Implementation Checklist
**✅ BEFORE YOU START CODING:**
- [ ] Run: `python tools/modular_audit/modular_audit.py ./modules` (WSP 4)
- [ ] Search existing: `grep -r "your_concept" modules/` (Avoid duplication)
- [ ] Read patterns: `modules/<domain>/*/tests/README.md` (Learn established patterns)
- [ ] Check LLME scores: Review existing module complexity and targets

**✅ WHILE CODING:**
- [ ] Define public API in module `__init__.py` (WSP 11)
- [ ] Add dependencies to `requirements.txt` (WSP 12)
- [ ] Create tests as you write code (WSP 5 - 90% coverage target)
- [ ] Document patterns in `tests/README.md` (WSP 13)

**✅ BEFORE COMMIT:**
- [ ] Tests pass: `pytest modules/<domain>/<module>/tests/ -v`
- [ ] System clean: `python tools/modular_audit/modular_audit.py ./modules`
- [ ] Coverage ≥90%: `pytest --cov=modules.<domain>.<module>.src --cov-report=term-missing`
- [ ] Update documentation: `tests/README.md` with new test descriptions

---

### EXISTING CODE Quick Workflow

#### Step 1: Change Type Identification
```
🔍 WHAT TYPE OF CHANGE?
│
├─ 🐛 Bug Fix → [Immediate Actions](#bug-fix-immediate-actions)
├─ ✨ Feature Addition → [Feature Decision](#feature-addition-decision)
├─ ♻️ Refactoring → [High-Risk Process](#refactoring-high-risk-process)
├─ 📈 Performance → [Optimization Process](#optimization-process)
└─ 🧪 Testing → [Testing Workflow](#testing-quick-workflow)
```

#### Bug Fix Immediate Actions
**🎯 TEST-FIRST APPROACH:**
1. **Reproduce:** Create failing test that demonstrates the bug
2. **Locate:** `grep -r "error_pattern" modules/` to find related code
3. **Analyze:** Check WSP 12 dependencies and WSP 11 interfaces
4. **Fix:** Make minimal change to make test pass
5. **Verify:** Run full test suite for affected modules

**📋 Validation Requirements:**
- [ ] Failing test now passes
- [ ] No regression: `pytest modules/<affected_domain>/` all pass
- [ ] System clean: `python tools/modular_audit/modular_audit.py ./modules`
- [ ] Related tests updated if behavior changed

#### Feature Addition Decision
**🎯 CRITICAL DECISION:** Does this fit in existing module structure?

**✅ YES - Extends Existing Module:**
1. Read existing `tests/README.md` for established patterns
2. Follow existing code style and architectural patterns
3. Update module `__init__.py` if adding public API (WSP 11)
4. Add comprehensive tests maintaining 90% coverage (WSP 5)
5. Update `tests/README.md` with new functionality description

**❌ NO - Requires New Module:**
→ Return to: [NEW MODULE WORKFLOW](#new-module-quick-workflow)

#### Refactoring High-Risk Process
**⚠️ EXTRA VALIDATION REQUIRED - HIGH IMPACT ACTIVITY**

**🛡️ SAFETY MEASURES (BEFORE STARTING):**
- [ ] Create clean state: Follow WSP 2 snapshot process
- [ ] Full test baseline: `pytest modules/` (all tests must pass)
- [ ] FMAS baseline: `python tools/modular_audit/modular_audit.py ./modules --baseline`
- [ ] Document current state: Update `docs/clean_states.md`

**🔄 DURING REFACTORING:**
- [ ] Maintain API compatibility: Follow WSP 11 interface requirements
- [ ] Update imports systematically: `git grep -l "old.import.path"`
- [ ] Test frequently: `pytest -x` (stop on first failure)
- [ ] Monitor coverage: Ensure no degradation

**✅ POST-REFACTORING VALIDATION:**
- [ ] All tests pass: `pytest modules/`
- [ ] FMAS comparison: Check against baseline snapshot
- [ ] Integration testing: Test dependent modules
- [ ] Documentation: Update if interfaces changed

---

### TESTING Quick Workflow

#### Test Type Decision Tree
```
🧪 WHAT KIND OF TESTING?
│
├─ 🆕 New Test Creation → [WSP 13 Process](#wsp-13-test-creation)
├─ 🔧 Fixing Failing Tests → [Debug Process](#test-debugging-process)
├─ 📊 Coverage Improvement → [Coverage Strategy](#coverage-improvement)
└─ 🔄 Test Refactoring → [Test Maintenance](#test-refactoring)
```

#### WSP 13 Test Creation
**🎯 MANDATORY FIRST STEP:** Read `tests/README.md` in target module

**WSP 13 Compliance Protocol:**
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

#### Coverage Improvement
**🎯 WSP 5 TARGET:** ≥90% coverage for all modules

**Quick Coverage Assessment:**
```bash
# Single module coverage
pytest modules/<domain>/<module>/tests/ --cov=modules.<domain>.<module>.src --cov-report=term-missing

# Full system coverage
pytest modules/ --cov=modules --cov-report=html
```

**Coverage Enhancement Strategy:**
1. **Gap Analysis:** Focus on "Missing" lines in coverage report
2. **Priority:** Target critical paths, error handling, edge cases
3. **Implementation:** Add tests for uncovered branches and conditions
4. **Validation:** Re-run coverage to confirm improvement

---

### PROJECT STATUS Workflow

#### System Health Dashboard
**🔍 COMPREHENSIVE SYSTEM AUDIT:**

```bash
# Full WSP compliance audit
python tools/modular_audit/modular_audit.py ./modules

# Complete test suite status
pytest modules/ --tb=short

# Multi-agent system validation
python tools/testing/test_multi_agent_comprehensive.py

# Coverage analysis across all modules
python -m pytest modules/ --cov=modules --cov-report=html

# WSP structure validation
find modules/ -name "*.py" ! -path "*/src/*" ! -path "*/tests/*" ! -name "__init__.py"
```

#### WSP Compliance Checklist
**📊 REAL-TIME COMPLIANCE STATUS:**

```
✅ WSP 1: Module Structure Compliance
   └─ All modules follow src/tests/ structure?
   └─ Command: find modules/ -name "*.py" ! -path "*/src/*" ! -path "*/tests/*" ! -name "__init__.py"
   └─ Expected: No output (all files in proper locations)

✅ WSP 3: Enterprise Domain Organization
   └─ All modules properly categorized in domains?
   └─ Command: ls modules/
   └─ Expected: Only domain directories (ai_intelligence, communication, etc.)

✅ WSP 5: Test Coverage ≥90%
   └─ All modules meet coverage requirements?
   └─ Command: pytest modules/ --cov=modules --cov-report=term
   └─ Expected: All modules ≥90% coverage

✅ WSP 11: Interface Definition
   └─ All modules have proper public APIs?
   └─ Command: find modules/ -name "__init__.py" -path "*/modules/*" -not -path "*/src/*" -not -path "*/tests/*"
   └─ Expected: Each module has main __init__.py

✅ WSP 13: Test Documentation
   └─ All test directories have README.md?
   └─ Command: find modules/ -path "*/tests" ! -exec test -f {}/README.md \; -print
   └─ Expected: No output (all have README.md)
```

---

## 🎯 QUICK REFERENCE TABLES

### Enterprise Domain Reference
| Domain | Purpose | Example Modules | LLME Focus |
|--------|---------|----------------|------------|
| `ai_intelligence` | AI logic, LLMs, decision engines | banter_engine, semantic_analyzer | High complexity, evolving |
| `communication` | Chat, messaging, protocols | livechat, message_processor | Medium complexity, stable |
| `platform_integration` | External APIs, services | youtube_auth, stream_resolver | Low complexity, stable |
| `infrastructure` | Core systems, management | agent_management, oauth_management | High complexity, stable |
| `monitoring` | System health, metrics | logging, health_check | Low complexity, stable |
| `development` | Tools, testing, automation | testing_tools, build_scripts | Medium complexity, evolving |
| `foundups` | Individual FoundUps projects | josi_agent, edgwit_project | Varies per project |
| `gamification` | Engagement, rewards, token loops | rewards_engine, token_mechanics | Medium complexity, evolving |
| `blockchain` | Decentralized infra, token logic | chain_connectors, dae_persistence | High complexity, foundational |

### WSP Command Quick Reference
| Task | Command | WSP | Expected Result |
|------|---------|-----|----------------|
| Full System Audit | `python tools/modular_audit/modular_audit.py ./modules` | WSP 4 | No violations |
| Module Test Suite | `pytest modules/<domain>/<module>/tests/ -v` | WSP 5 | All tests pass |
| Coverage Check | `pytest --cov=modules.<domain>.<module>.src --cov-report=term` | WSP 5 | ≥90% coverage |
| Multi-Agent Validation | `python tools/testing/test_multi_agent_comprehensive.py` | WSP 13 | System functional |
| Clean State Creation | `git tag -a clean-v<X> -m "Description"` | WSP 2 | Tagged snapshot |

### Critical WSP Files
| File/Directory | Purpose | WSP | Maintenance |
|---------------|---------|-----|-------------|
| `modules/<domain>/<module>/tests/README.md` | Test documentation | WSP 13 | Update after test changes |
| `modules/<domain>/<module>/__init__.py` | Public API definition | WSP 11 | Update when adding public functions |
| `requirements.txt` | Project dependencies | WSP 12 | Update when adding packages |
| `docs/clean_states.md` | Clean state history | WSP 2 | Update when creating snapshots |
| `tools/modular_audit/modular_audit.py` | System validation | WSP 4 | Run before commits |

---

## ⚡ EMERGENCY PROCEDURES

### System Recovery Protocol
```
🚨 EMERGENCY: System Broken or Non-Functional
│
├─ 1. ASSESS DAMAGE
│  ├─ Quick test: pytest modules/ --tb=line
│  ├─ Structure: python tools/modular_audit/modular_audit.py ./modules
│  └─ Multi-agent: python tools/testing/test_multi_agent_comprehensive.py
│
├─ 2. IDENTIFY LAST GOOD STATE
│  ├─ Review tags: git tag -l "clean-v*"
│  ├─ Check history: git log --oneline -10
│  └─ Consult: docs/clean_states.md
│
├─ 3. SELECTIVE RECOVERY
│  ├─ Single file: git checkout <clean-tag> -- path/to/file
│  ├─ Module restore: git checkout <clean-tag> -- modules/<domain>/<module>/
│  └─ Full rollback: git reset --hard <clean-tag> (DESTRUCTIVE)
│
└─ 4. VERIFY RECOVERY
   ├─ Test suite: pytest modules/
   ├─ System audit: python tools/modular_audit/modular_audit.py ./modules
   └─ Functionality: Run main application
```

### Import Error Recovery
```
🔧 IMPORT ERROR: Module Not Found or Import Failures
│
├─ 1. STRUCTURE VERIFICATION
│  ├─ Check: modules/<domain>/<module>/src/__init__.py exists
│  ├─ Check: modules/<domain>/<module>/__init__.py has proper imports
│  └─ Verify: Python path includes project root
│
├─ 2. IMPORT PATH ANALYSIS
│  ├─ Search old paths: git grep -l "old_import_path"
│  ├─ Verify new paths: Use modules.<domain>.<module>.src.<filename>
│  └─ Test import: python -c "import modules.<domain>.<module>"
│
├─ 3. SYSTEMATIC REPAIR
│  ├─ Update imports: Find and replace systematically
│  ├─ Check __init__.py: Ensure proper API exposure
│  └─ Test changes: pytest modules/<domain>/<module>/tests/
│
└─ 4. VALIDATION
   ├─ Module import: python -c "import modules.<domain>.<module>"
   ├─ Test suite: pytest modules/<domain>/<module>/tests/
   └─ System check: python tools/modular_audit/modular_audit.py ./modules
```

**🎯 Remember:** This framework exists to guide your decisions and make development faster. When unsure, follow the decision trees above, run the validation commands, and maintain the quality standards defined in the WSPs below.


---


## WSP Philosophy: Building Code LEGO Architecture


### The Vision: Modular Composability


The Windsurf Standard Procedures (WSPs) are designed with a fundamental vision: **creating a "Code LEGO" architecture** where modules can be easily discovered, understood, connected, and composed into larger systems. Just as LEGO bricks have standardized connection points that allow infinite creative combinations, our modules follow strict structural and interface standards that enable seamless integration.


### How WSP Facilitates "Code LEGO"


#### 🧱 Strict Modular Structure (WSP 1 & WSP 3)


**WSP 1 (Module Refactoring to Windsurf Structure):** Enforces a consistent internal structure for every module (`src/`, `tests/`, `__init__.py` for public API). This uniformity is like ensuring all LEGO bricks have compatible studs and tubes—every developer knows exactly where to find implementation code, tests, and public interfaces.


**WSP 3 (Enterprise Domain Architecture):** Organizes these "LEGO pieces" into logical "bins" (Enterprise Domains and Feature Groups), making them easier to find, understand, and manage. Just as LEGO sets are organized by theme and function, our modules are categorized by their architectural purpose.


#### 🔌 Clearly Defined Interfaces (WSP 12)


This is the **absolute cornerstone** of the LEGO analogy. WSP 12 mandates that each module has an explicit, documented, and validated interface (API, contract). These interfaces are the "studs and anti-studs" that define precisely how modules connect and interact.


**LLME-Driven Interface Quality:** The LLME score (especially Digit B - Local Impact, and C - Systemic Importance) influences the robustness and stability requirements of these interfaces. A module intended to be a widely used "LEGO brick" (high B or C) will have a very stable and well-defined interface, just as structural LEGO pieces have more precise tolerances than decorative ones.


#### 📦 Explicit Dependency Management (WSP 13)


Modules explicitly declare what other "LEGO bricks" they need to function. This prevents hidden or tangled dependencies that would make snapping pieces together difficult or unpredictable.


**Smart Dependency Choices:** LLME scores inform dependency selection—preferring to depend on stable, "essential" (LLME C=2) core bricks rather than experimental or volatile modules. This creates a stable foundation for the architecture.


#### 🧪 Standardized Testing and Validation (WSP 4, WSP 6, WSP 14)


Ensures each "LEGO brick" is individually sound and meets quality standards before it's snapped into the larger structure. Contract tests (part of WSP 6 and WSP 12) specifically verify that the "snapping mechanism" (the interface) works as expected.


**Quality Scales with Importance:** Testing rigor scales with LLME scores—modules with high systemic importance (C=2) receive more comprehensive testing, ensuring the most critical "bricks" are the most reliable.


### 🤖 AI & Blockchain Integration Hooks


#### AI Hooks (Implicit and Explicit)


**Implicit:** The entire WSP framework is designed for AI agents (like 0102) to understand and operate upon. The structured nature, clear WSPs, and LLME scores are all "hooks" for AI-driven development, refactoring, and analysis.


**Explicit:** Modules within the `ai_intelligence` domain would inherently be designed with AI capabilities. Their WSP 12 interfaces would expose AI functionalities (e.g., `semantic_analyzer.analyze_text(text)`). Other modules can then "snap in" these AI capabilities by interacting with these well-defined interfaces.


#### Blockchain Hooks (Conceptual Integration)


**Modular Blockchain Services:** Blockchain functionalities would reside in specific modules (e.g., within `infrastructure` or a new `blockchain_services` domain). These modules would expose blockchain operations (e.g., `ledger_writer.record_transaction(data)`, `asset_tokenizer.create_token(details)`) via WSP 12 interfaces.


**High-Value Integration:** The LLME score of blockchain modules would likely be high in importance (B and C digits) due to their foundational and often critical nature, ensuring they receive appropriate architectural attention and stability requirements.


### 🧬 LLME for Semantic Compatibility


LLME scores help assess not just if modules *can* technically connect, but if they *should* from a semantic or architectural perspective. An AI agent might flag an attempt to snap a "dormant, irrelevant" (LLME 000) module into a "system-critical" (LLME XX2) workflow, preventing architectural mismatches.


### ✅ Achieving the Code LEGO Vision


#### Technical Feasibility: **YES** (with rigor)
The WSP framework provides the necessary structural and procedural foundation. If WSP 1, WSP 12, and WSP 13 are strictly adhered to, modules will become increasingly interchangeable and composable.


#### Success Factors:


1. **Disciplined Application:** Consistent adherence to WSPs by both human developers and AI agents
2. **Interface Design Quality:** Well-designed interfaces that are both technically sound and semantically meaningful
3. **Appropriate Granularity:** Right-sizing modules—not too small (too many tiny pieces) or too large (loses reusability)
4. **Evolution Management:** Robust versioning (WSP 11) to handle interface changes without breaking existing compositions


#### Key Challenges:


- **Legacy Code:** Refactoring existing code into perfect "LEGO bricks" requires significant effort
- **Complex Interactions:** Some interactions are inherently more complex than simple snapping
- **State Management:** Modules with significant internal state require careful interface design
- **Human Factor:** Ensuring consistent WSP adherence across all development


### 🎯 The Ultimate Goal


**Composable Intelligence:** By following the WSP framework rigorously, we create a system where:
- New features can be built by combining existing, well-tested modules
- AI capabilities can be seamlessly integrated into any workflow through standard interfaces
- Blockchain functionality becomes a "snap-in" service rather than a fundamental rewrite
- System complexity is managed through clear architectural boundaries
- Innovation happens through novel combinations rather than monolithic rebuilds


The WSP framework transforms software development from custom craftsmanship into **intelligent architecture**—where the building blocks are so well-designed and standardized that the creative focus shifts to how they're combined rather than how they're built.


---


## I. Defining and Using WSPs


**AI Assistant Interaction Guidelines (FoundUps Interaction Protocol):**
*(Adapted from RuleSurf Principles)*
*   **Proactive Updates:** AI should suggest updates to project rules (`foundups_global_rules.md`, `.foundups_project_rules`) if requirements seem to change, notifying the user. This includes suggesting updates to a module's LLME score (see Appendix G) if its state, impact, or importance demonstrably changes.
*   **Scaffolding Prioritization:** Build user-testable structures first (UI or logical flow), then implement component details.
*   **No Invention:** Do not invent functionality or change UI/logic without explicit user direction.
*   **Verification Steps:** Clearly describe user testing/verification steps upon completing components.
*   **Error Analysis:** Automatically check logs/problem reports post-changes, analyze errors, propose solutions with Confidence Levels (CL%), and preserve context. (See Rule 7).
*   **Repetition Handling:** If user repeats similar instructions 3+ times, suggest creating a new standard command/procedure. This may include recurring LLME assessments.
*   **Test Management & Documentation (tests/README.md):**
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
    *   `@80%`: Prompt user to `save` context (updates rules, saves tech context, lists open threads).
    *   `@95%`: Automatically trigger `save` context action in the next reply.
*   **Standard Commands:** Utilize the defined commands listed in **Appendix C** for common actions (`k`, `go`, `save`, `init`, `fix`, etc.).


**High-Level Project Cycle (RPC Reference):**
*(Referenced from RuleSurf RPC)*
1.  *User:* Ideate, clarify, define Project Prompt/Requirements (stored in `.foundups_project_rules`), including initial or target LLME scores for key components.
2.  *AI:* Generate detailed plan (milestones, tasks) based on prompt (stored in `foundups_global_rules.md`).
3.  *AI:* Set up project environment, dependencies, initial structure.
4.  *Both:* Execute component sub-cycles:
    *   AI builds component.
    *   User tests component.
    *   Both debug (AI proposes fixes).
    *   AI adds/runs core tests until passing.
    *   AI/User assess and update module LLME score.
5.  *AI:* Proceed to next component (repeat step 4).
6.  *User:* Final QA and sign-off.


**Memory & Rule Hierarchy Overview:**
*(Refer to Appendix D for details)*
*   **Internal AI Memories:** Technical learnings (versions, debug info, patterns) maintained by the AI to prevent mistakes. This includes understanding of LLME score implications.
*   **User Project Rules (`.foundups_project_rules`):** Project-specific requirements, stack, plan (User-owned, AI read/suggest-only). May include target LLME scores for modules. Template in **Appendix F**.
*   **Global Rules (`foundups_global_rules.md`):** Contains universal development practices (these WSPs), standard commands (Appendix C), the LLME Rating System definition (or reference to Appendix G), and the AI-maintained **Adaptive Project State (APS)** (Task List, Project Insights, current module LLME scores).


---


## II. Core Windsurf Standard Procedures (WSPs)


### WSP 0: Protocol Overview & Enforcement Rules


**Version:** 1.0
**Status:** Active


#### 0.1. Introduction & Purpose
The **Windsurf Protocol** is a strict, procedural enforcement system governing development within FoundUps, ensuring consistency, verifiability, testability, and MMAS compatibility. It dictates *how* tasks are defined, executed, and validated, incorporating the LLME Semantic Triplet Rating (see Appendix G) for module evaluation.


#### 0.2. Role within MMAS
Windsurf is the execution layer of MMAS. WSPs are the enforceable procedures required to meet MMAS quality goals. LLME scores provide a semantic context for these goals.


#### 0.3. Enforcement Philosophy
*   **Mandatory Compliance:** WSPs are not optional.
*   **Atomicity:** Tasks must be the smallest verifiable units.
*   **Scope Constraint:** Operate strictly within defined scope.
*   **Test-Driven Action:** Validate changes via `pytest`, FMAS per WSP.
*   **Audit-Readiness:** Actions must be traceable (logs, commits, Clean States, tags, validation outputs, LLME score history).


#### 0.4. Standard Execution Flow
1.  **Task Declaration (WSP Prompt):** Define goal, scope, constraints, potentially target LLME (See Appendix A).
2.  **Scope Lock & Confirmation:** Agent confirms understanding.
3.  **Execution:** Perform action per WSP and scope.
4.  **Validation:** Verify outcome using specified methods (FMAS, `pytest`, diff).
5.  **Logging & Documentation:** Record results, artifacts, metrics per WSP (update `docs/clean_states.md`, commit logs, ModLog with LLME updates per WSP 11).


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
Standard procedure for refactoring modules into Windsurf structure, ensuring: FMAS Compatibility, Modularity, AI Readiness, Maintainability, Import Clarity. Refactoring goals may include achieving a target LLME score (see Appendix G).


#### 1.2. Scope
Applies to any flat `.py` file in `/modules/` representing a logical module.


#### 1.3. Prerequisites
*   Repo Access & Latest Code
*   Python Env & `pytest`
*   FMAS Tool (`tools/modular_audit/modular_audit.py`)
*   Baseline Clean State Access
*   Git Familiarity
*   Windsurf Structure Understanding
*   Understanding of LLME Rating System (Appendix G) for assessing module state.


#### 1.4a. Preliminary Analysis & Planning (0102 Agent Task)


*   **Code Understanding:** 0102 analyzes the target flat file(s) to understand function, primary data structures, and external interactions.
*   **LLME Assessment:** 0102 assesses (or is provided with) the module's current LLME score and any target LLME score. This informs the refactoring's strategic importance and depth.
*   **Modular Proposal:** 0102 proposes:
    *   The target module name (`<module_name>`).
    *   The breakdown of the flat file into logical components within `src/`.
    *   The initial public interface (functions, classes, data exposed) based on usage analysis (see WSP 12).
    *   Identified external and internal dependencies (see WSP 13).
*   **User Confirmation:** User reviews and confirms/modifies 0102's plan, including LLME considerations, before proceeding with file manipulation.


#### 1.4. Standard Procedure (Summary)
*(See detailed version in separate WSP 1 document if needed)*
1.  Identify Target File & Module Name.
2.  Create `modules/<n>/`, `.../src/`, `.../tests/` dirs.
3.  Execute Confirmed Plan: Perform analysis as per 1.4a (including LLME assessment).
4.  `git mv` source file to `src/`.
5.  Create/Update module `__init__.py` (define public API from `src`).
6.  Define/refine the module's public API in `modules/<n>/__init__.py` (or language equivalent) and document it according to WSP 12.
7.  Declare identified dependencies according to WSP 13 (e.g., update requirements.txt, package.json).
8.  Create/Update (usually empty) `src/__init__.py`.
9.  Fix internal imports within the moved file.
10. Find (`git grep`) and update external callers to use new import paths.
11. `git mv` existing tests to `tests/` or create stubs; update test imports.
12. **Create/Update `tests/README.md`:** Add a `modules/<name>/tests/README.md` file. List any tests moved in step 11 with brief descriptions. If no tests exist yet, create a placeholder README indicating this. (See Section I AI Guidelines for ongoing updates).
13. Run `pytest` for module and callers.
14. Troubleshoot test failures.
15. Run Interface Validation checks as defined in WSP 12.
16. Verify Dependency Manifest correctness as per WSP 13.
17. Verify with `FMAS` (Check for `TEST_README_MISSING` warning, WSP 4).
18. `git commit` with standard message (potentially noting LLME impact if significant).
19. Repeat.


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
*   Document any change in the module's LLME score in the ModLog (WSP 11).


---


### WSP 2: Clean Slate Snapshot Management


**Document Version:** 1.2
**Date Updated:** [Insert Date]
**Part of:** MMAS & Windsurf Protocol


#### 2.1. Purpose
Manages versioned snapshots (`Foundups-Agent` copies) for baselining, rollback, historical reference, complemented by **Git Tags**. Clean States represent a point where module LLME scores (Appendix G) are assessed as stable for that snapshot.


#### 2.2. Definition
A **Clean State** is a complete copy of `Foundups-Agent`, captured *after* passing quality checks and associated with a **Git Tag**. The state of module LLME scores should be considered stable at this point.


#### 2.3. Naming & Storage
*   **Folder:** `foundups-agent-clean[X][Suffix]` (Alongside `Foundups-Agent`).
*   **Git Tag:** `clean-v[X]` (In Git repo).


#### 2.4. Defined States & Central Log
Maintain list, purpose, date, tag in: **`docs/clean_states.md`**. This log may also note the overall system's key module LLME states at the time of snapshot.


#### 2.5. Workflow & Usage Rules
**A. When to Create:**
*   After stable milestones.
*   **MANDATORY:** Only after commit passes: ✅ `pytest`, ✅ `FMAS`, ✅ Runs OK.
*   Key module LLME scores have been reviewed and are stable.


**B. How to Create (Folder + Tag):**
1.  Verify Checks Pass.
2.  Clean Workspace (remove `__pycache__`, `venv/`, etc.).
3.  Copy: `cp -R Foundups-Agent/ foundups-agent-cleanX/` (from parent dir).
4.  Tag Commit: `git tag -a clean-vX -m "Desc" <hash> && git push origin clean-vX`. *(See Appendix E for `save` command details)*.
5.  Document in `docs/clean_states.md` (and potentially in `docs/ModLog.md` per WSP 11, noting any significant LLME state).


**C. Usage:**
*   **Folder Copies:** Read-only. Use for FMAS `--baseline`, `diff -r`.
*   **Git Tags:** History. Use for `git checkout`, `git show`, `git checkout <tag> -- file` (safer restore).


#### 2.6. Considerations
*   **Disk Space:** Folders large; Tags small. Archive old folders.
*   **`.gitignore`:** `cp -R` ignores this; clean first. Git respects it.
*   **Consistency:** Ensure folder & tag match state, including the implicit LLME context.


---


### WSP 3: Enterprise Domain Architecture & Hierarchical Module Organization


**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** All module creation, organization, and refactoring within the FoundUps Agent ecosystem.


#### 3.1. Purpose


To overcome the limitations of a flat module structure as the system scales.
To provide a clear and logical organization for a large number of modules (e.g., 100+).
To facilitate team-based ownership and specialized development by domain.
To improve separation of concerns, reduce cognitive load, and enhance modularity.
To support the structured development of autonomous agents and features within well-defined domains, considering their LLME scores (Appendix G) for strategic placement.
To establish a scalable architectural framework ("cube-based philosophy") that supports long-term growth and evolution of the FoundUps platform.


#### 3.2. Scope


Defines the new mandatory top-level directory structure (Enterprise Domains) within the main modules/ directory.
Outlines principles for classifying modules into Enterprise Domains and further into Feature Groups/Sub-Domains.
Impacts all new module creation, requiring placement within this hierarchy.
Mandates the refactoring of existing modules from a flat structure into this hierarchy.
Requires updates to tooling, particularly FMAS (see WSP 4 - FMAS Usage), to support and validate the new structure.


#### 3.3. Core Principles: The Cube-Based Philosophy


This WSP adopts a "cube-based" philosophy to visualize and organize the system's architecture in layers of increasing granularity:


**Enterprise Domains (Level 1 "Enterprise Cubes"):**
These are the broadest, high-level strategic areas of functionality or business capability within the FoundUps ecosystem.
They form the primary top-level directories directly under modules/.
Each Enterprise Domain represents a major area of concern and potential team ownership. Modules with high "Systemic Importance" (LLME Digit C=2) are likely to reside in or define these domains.


**Feature Groups / Sub-Domains (Level 2 "Feature Cubes"):**
These are logical groupings of related modules that collectively deliver a significant feature set or address a specific sub-problem within an Enterprise Domain.
They form subdirectories within their respective Enterprise Domain directories.
This level helps further organize modules and can map to specific epics or larger features.


**Modules (Level 3 "Component Cubes"):**
These are individual, self-contained units of functionality, each adhering to the structure defined in WSP 1 (Module Refactoring to Windsurf Structure) (e.g., containing src/, tests/, interface definitions, dependency manifests).
Modules reside within the most appropriate Feature Group/Sub-Domain directory. Each module has an LLME score.


**Code Components (Level 4 "Code Cubes"):**
These are the fundamental building blocks within a module, such as functions, classes, and other code elements located in the module's src/ directory. Their organization is internal to the module.


#### 3.4. Defined Enterprise Domains & Example Structure


The initial set of Enterprise Domains is defined as follows. This list can evolve through a formal architectural review process, documented in foundups_global_rules.md or an equivalent architecture decision record (ADR).


```
modules/
├── ai_intelligence/          # Enterprise Domain: AI & LLM Core Capabilities (Likely high LLME modules)
│   ├── llm_agents/           # Feature Group: Foundational LLM Agent implementations
│   │   └── [module_name]/    # Module (WSP 1 compliant, has LLME score)
│   ├── sentiment_analysis/   # Feature Group
│   │   └── [module_name]/
│   ├── banter_engine/        # Feature Group
│   │   └── [module_name]/
│   └── prompt_management/    # Feature Group
│       └── [module_name]/
├── communication/            # Enterprise Domain: User Interaction & Presentation
│   ├── livechat/             # Feature Group
│   │   └── [module_name]/
│   ├── voice_interface/      # Feature Group
│   │   └── [module_name]/
│   └── ui_components/        # Feature Group
│       └── [module_name]/
├── platform_integration/     # Enterprise Domain: External Systems & Services
│   ├── youtube_auth/         # Feature Group
│   │   └── [module_name]/
│   ├── stream_resolver/      # Feature Group
│   │   └── [module_name]/
│   └── social_platforms/     # Feature Group (e.g., twitter_api, discord_bot)
│       └── [module_name]/
├── infrastructure/           # Enterprise Domain: Core Systems, Security, & Operations (Likely high LLME modules)
│   ├── token_manager/        # Feature Group
│   │   └── [module_name]/
│   ├── security/             # Feature Group (e.g., access_control, encryption_services)
│   │   └── [module_name]/
│   └── monitoring/           # Feature Group (e.g., logging_service, metrics_collector)
│       └── [module_name]/
├── data_processing/          # Enterprise Domain: Data Handling, Analytics, & Persistence
│   ├── analytics/            # Feature Group
│   │   └── [module_name]/
│   ├── user_data/            # Feature Group (e.g., profile_management, preference_storage)
│   │   └── [module_name]/
│   └── content_processing/   # Feature Group (e.g., text_parser, image_processor)
│       └── [module_name]/
├── foundups/                 # Enterprise Domain: Individual FoundUps Projects
│   ├── josi_agent_project/   # Feature Group: Example FoundUp Entity
│   │   └── [module_name]/
│   └── edgwit_project_project/ # Feature Group: Example FoundUp Entity
│       └── [module_name]/
├── gamification/             # Enterprise Domain: Engagement Mechanics & Behavioral Systems
│   ├── rewards_engine/       # Feature Group: Manages points, badges, tangible rewards
│   │   └── [module_name]/
│   ├── token_mechanics/      # Feature Group: Handles virtual currency, token loops
│   │   └── [module_name]/
│   └── behavioral_recursion/ # Feature Group: Systems for user habit formation, progression
│       └── [module_name]/
├── blockchain/               # Enterprise Domain: Decentralized Infrastructure & DAE
│   ├── decentralized_infra/  # Feature Group: Core chain interaction, node management
│   │   └── [module_name]/
│   ├── chain_connectors/     # Feature Group: Adapters for specific blockchain networks
│   │   └── [module_name]/
│   ├── token_contracts/      # Feature Group: Smart contracts for tokens, NFTs
│   │   └── [module_name]/
│   └── dae_persistence/      # Feature Group: Storing data on-chain or via decentralized storage
│       └── [module_name]/
```


#### 3.5. Module Placement & Classification


**Guidelines:**
When creating a new module or refactoring an existing one, it MUST be placed within the most relevant Enterprise Domain and an appropriate Feature Group/Sub-Domain.
The module's current or target LLME score (Appendix G) should be considered. For example, modules with high "Systemic Importance" (Digit C = 2) should align with core Enterprise Domains.
If a suitable Feature Group/Sub-Domain does not exist, one should be proposed and created following discussion and approval (documented via ADR or project rules).
Consider the module's primary responsibility, its key interactions, and the logical cohesion with other modules in the proposed location.


**Domain Analyzer Tool:** A (to-be-developed or designated AI agent) "Domain Analyzer" tool (see section 3.7) should be utilized to suggest or assist in the classification of modules, potentially using LLME scores as an input factor.


**Review Process:** Module placement decisions, particularly for new Feature Groups or debatable classifications, should be reviewed by the relevant domain owners or technical leads. LLME assessment can be part of this review.


#### 3.6. Migration Strategy (for existing flat modules)


The transition from a flat modules/ structure to the hierarchical domain-based architecture will be conducted in phases:


**Phase 1: Audit, Classification & Planning:**
Conduct a comprehensive audit of all existing modules in the current flat /modules/ directory.
For each module, determine its most appropriate Enterprise Domain and Feature Group/Sub-Domain. Assign or review its current LLME score.
Utilize the (future) Domain Analyzer tool or manual analysis based on module purpose, dependencies, and LLME score to aid classification.
Document the proposed new hierarchical path for every existing module (e.g., in a migration plan or spreadsheet).
Prioritize modules for migration based on MPS (WSP 5, which now incorporates LLME) or strategic importance (which can also be informed by target LLME).


**Phase 2: Structural Refactoring & Tool Updates:**
Incrementally refactor modules according to the migration plan:
Create the target domain and sub-domain directories if they don't exist.
Use git mv modules/<old_module_name> modules/<domain_name>/<sub_domain_name>/<module_name>/ to move the module directory. Note: the module itself might need to be renamed if its old name was too generic.
Update all import paths across the entire codebase that referenced the moved module. This is a critical and potentially extensive step. Tools like grep and IDE refactoring capabilities will be essential.
Update FMAS (see WSP 4) to become "Domain-Aware FMAS." This includes validating the new hierarchical structure, checking for modules outside recognized domains, and potentially enforcing rules about module placement.
After each significant batch of module moves, run comprehensive tests (all relevant WSPs, especially WSP 6 - Test Audit) and regression checks (WSP 8 - Snapshot Regression) to ensure system integrity. Update LLME scores if refactoring significantly altered module characteristics.


**Phase 3: Ongoing Management & Future Modules:**
All newly created modules MUST adhere to this hierarchical domain structure from their inception.
The Domain Analyzer tool should be used to guide the placement of new modules, considering their intended LLME characteristics.
Periodically review the domain structure itself (Enterprise Domains and Feature Groups) for continued relevance and make adjustments as the system evolves (via a formal ADR process).


#### 3.7. Tooling Enhancements


To support this architecture, the following tooling capabilities are required or highly recommended:


**Domain-Aware FMAS (Update to WSP 4 - FMAS Usage):**
FMAS must be enhanced to understand and validate the hierarchical structure.
It should verify that all modules reside within a recognized Enterprise Domain.
It can optionally check if modules are within defined Feature Groups/Sub-Domains (if these are strictly cataloged).
It should report on modules found directly under modules/ (violating the hierarchy, except for special cases like a shared common/ or utils/ if explicitly allowed).


**Domain Analyzer Tool (New Tool Development):**
An AI-powered tool (or an extension of 0102 Agent capabilities) designed to:
Analyze a module's code (functions, classes, dependencies, comments, naming).
Consider the module's current or target LLME score.
Suggest the most appropriate Enterprise Domain and Feature Group/Sub-Domain for its placement.
Potentially identify modules with low cohesion that might be candidates for splitting across domains.
Assist in auditing the current structure for consistency.


**Cross-Domain Dependency Management & Visualization:**
While modules in different domains can interact (ideally through well-defined interfaces per WSP 13), it's crucial to manage and understand these cross-domain dependencies.
Tools or practices should be established to:
Clearly document cross-domain interfaces.
Potentially visualize the dependency graph between domains and sub-domains to identify unwanted tight coupling or circular dependencies at a higher architectural level. LLME scores of dependent modules can highlight critical paths.
Enforce stricter rules or review processes for introducing new cross-domain dependencies, especially those involving high-LLME (Digit C=2) modules.


#### 3.8. Benefits for Enterprise Scalability


**Improved Organization & Clarity:** Provides a clean, understandable structure for potentially hundreds of modules, making the system easier to navigate and comprehend.
**Enhanced Team Ownership & Autonomy:** Allows for clear assignment of Enterprise Domains (and their sub-groups) to specific development teams, fostering expertise and accountability.
**Reduced Cognitive Load:** Developers can more easily focus on a specific domain or sub-domain relevant to their current task without needing to understand the entire system at once.
**Stronger Separation of Concerns:** Enforces logical boundaries between different parts of the system, leading to more robust and maintainable code.
**Scalable Autonomous Development:** Offers a structured environment for developing and integrating new AI agents or complex features (potentially with high LLME aspirations) within their respective domains.
**Clear Architectural Roadmap:** The "cube" philosophy provides a tangible model for discussing and planning future architectural evolution and growth.
**Simplified Onboarding:** New team members can be introduced to specific domains first, making the learning curve more manageable.


#### 3.9. Related WSPs


This WSP has a broad impact on how other WSPs are applied:
**WSP 1 (Module Refactoring):** The fundamental structure of individual modules (src/, tests/) defined in WSP 1 still applies, but these modules now reside within the domain hierarchy. LLME assessment is part of refactoring planning.
**WSP 2 (Clean Slate Snapshot Management):** Clean states capture the entire Foundups-Agent repository, including this new hierarchical structure.
**WSP 4 (FMAS):** Must be updated to validate the hierarchical domain structure.
**WSP 5 (MPS):** Module prioritization now considers domain context, cross-domain dependencies, and LLME scores.
**WSP 6 (Test Audit):** Test execution must account for the new module paths.
**WSP 12 (Interface Definition):** Cross-domain interfaces become particularly important, especially for high-LLME modules.
**WSP 13 (Dependency Management):** Dependencies between domains require special attention.


---


### WSP 4: FMAS – FoundUps Modular Audit System Usage


**Document Version:** 1.2
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** Validation of modules within the hierarchical `modules/` directory structure using the `modular_audit.py` tool.


> **Note on Language Agnosticism:** While specific examples in this WSP use Python conventions, the principles aim to be language-agnostic. Project-specific rules (`.foundups_project_rules`) or appendices should define language-specific tooling, file structures, and commands for different programming languages.


#### 4.1. Purpose


The **FoundUps Modular Audit System (FMAS)**, implemented via the `modular_audit.py` script, serves as the primary automated tool for enforcing structural compliance and detecting regressions within the FoundUps module ecosystem. Its core functions are:


*   **Hierarchical Structure Validation:** Verifying that modules adhere to the Enterprise Domain hierarchy defined in **WSP 3** and the mandatory Windsurf directory structure (`src/`, `tests/`) defined in **WSP 1**.
*   **Domain Compliance Check:** Ensuring modules reside within recognized Enterprise Domains and Feature Groups as defined in **WSP 3**.
*   **Structural Validation (Language Specific):** Verifying adherence to mandatory Windsurf directory structures (`src/`, `tests/`, `docs/`, potentially `interface/`) which may have language-specific variations defined in project rules.
*   **Test Existence Check:** Ensuring that source files have corresponding test files according to defined conventions.
*   **Interface Definition Check:** Ensuring modules contain required interface definition artifacts (WSP 12).
*   **Dependency Manifest Check:** Ensuring modules contain required dependency declaration artifacts (WSP 13).
*   **Baseline Comparison:** Detecting file-level changes (**`MISSING`**, **`MODIFIED`**, **`EXTRA`**) by comparing the current working state against a designated **Clean State** baseline (defined in **WSP 2**).
*   **Legacy Code Identification:** Flagging files potentially originating from older, non-Windsurf structures (**`FOUND_IN_FLAT`**) or flat module structures that violate the Enterprise Domain hierarchy.


Passing FMAS checks is a prerequisite for many other WSP procedures, acting as a critical quality gate. (Note: FMAS validates structure, not semantic LLME scores, which are assessed separately.)


#### 4.2. Tool Location


The canonical path to the FMAS script within the repository is:
```bash
tools/modular_audit/modular_audit.py
```


#### 4.3. Execution & Modes


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


#### 4.4. Command-Line Arguments


*   `modules_root` (Required): Positional argument specifying the path to the root directory containing the module folders to be audited (e.g., `./modules`).
*   `--baseline <path>` (Optional): Path to the root directory of the Clean State snapshot to use for comparison (e.g., `../foundups-agent-clean4/`). The script expects baseline modules within a `modules/` subdirectory of this path (e.g., `<baseline_root>/modules/<module_name>/...`). Activates Mode 2 audit.
*   `--output / -o <filepath>` (Optional): Redirect log output to a specified file instead of the console.
*   `--verbose / -v` (Optional): Increase output verbosity (e.g., show files that passed checks).
*   `--file-types <ext1,ext2>` (Optional): Comma-separated list of source file extensions to check within `src/` (e.g., `.py,.json`). Defaults defined in the script.
*   `--lang <language>` (Optional): Specify language context to apply appropriate structural rules and find relevant interface/dependency files.


#### 4.5. Output Interpretation & Status Codes


FMAS reports findings via standard logging messages. Pay attention to `WARNING` and `ERROR` level messages:


*   `[<module>] STRUCTURE_ERROR: 'src/' directory not found...`: The required `src/` directory is missing or inaccessible within the specified module folder. Blocks further checks for this module.
*   `[<module>] STRUCTURE_ERROR: 'tests/' directory not found...`: (If script configured for strictness) The required `tests/` directory is missing.
*   `[<module>] STRUCTURE_WARN: 'tests/' directory not found...`: (Default behavior) The `tests/` directory is missing; test existence cannot be verified for this module.
*   `[<module>] NO_TEST: Missing test file for src/... Expected: tests/...`: A source file (e.g., `.py`) exists in `src/`, but its corresponding test file (e.g., `test_*.py`) was not found in the expected location within `tests/`.
*   `[<module>] MISSING: File missing from target module. (Baseline path: ...)`: A file exists in the baseline's `src/` but is not found in the current module's `src/`. Regression potential. (Mode 2 Only)
*   `[<module>] MODIFIED: Content differs from baseline src/. (File path: ...)`: A file exists in both the current module `src/` and the baseline `src/`, but their content is different. Requires review. (Mode 2 Only)
*   `[<module>] EXTRA: File not found anywhere in baseline. (File path: ...)`: A file exists in the current module's `src/` but has no corresponding file in the baseline's `src/` or its flat `modules/` directory. Indicates a new, potentially un-audited file. (Mode 2 Only)
*   `[<module>] FOUND_IN_FLAT: Found only in baseline flat modules/, needs proper placement. (File path: ...)`: A file exists in the current module's `src/`. It was not found in the baseline `src/` but was found in the baseline's old, flat `modules/` directory. Indicates the file needs proper refactoring into the Windsurf structure (per WSP 1) in the baseline itself or review/removal. (Mode 2 Only)
*   `[<module>] INTERFACE_MISSING: Required interface definition file (e.g., INTERFACE.md, openapi.yaml) not found.`: The module is missing the required interface definition. (Blocks WSP 12 compliance).
*   `[<module>] DEPENDENCY_MANIFEST_MISSING: Required dependency file (e.g., requirements.txt, package.json) not found or empty.`: The module is missing the required dependency manifest. (Blocks WSP 13 compliance).
*   `[<module>] STRUCTURE_ERROR: Non-standard directory found...`: Flag unexpected directories unless allowed by language-specific rules.
*   `[<module>] TEST_README_MISSING: 'tests/README.md' file not found.`: (WARN Level) The recommended test documentation file is missing from the `tests/` directory. See WSP standard.
*   `✅ PASSED / ❌ FAILED` (Summary): Final lines indicating overall audit status based on findings. The script exits with code 0 on PASS and 1 on FAIL.


#### 4.6. Workflow Integration (When to Run FMAS)


Executing FMAS is mandatory at several key points:


*   **During Refactoring (WSP 1):** After moving files into the `src/`/`tests/` structure, run Mode 1 to verify structure and test file placement.
*   **Before Creating Clean State (WSP 2):** Run Mode 2 (comparing against the previous Clean State) to ensure no regressions or unexpected changes exist before snapshotting.
*   **As Part of Test Audit (WSP 6):** Step 1 of WSP 6 explicitly requires running FMAS (Mode 1 or 2 as appropriate) to verify test existence before proceeding with coverage checks.
*   **Before Committing Significant Changes:** Run Mode 1 (or Mode 2 if relevant) locally to catch issues early.
*   **In Pull Request Checks (CI/CD):** Automate FMAS runs (Mode 1 minimum, Mode 2 ideally) as a required check before merging branches (WSP 7).


#### 4.7. Remediation Steps


Address FMAS findings based on the reported status code:


*   `STRUCTURE_ERROR / STRUCTURE_WARN`: Create the missing `src/` or `tests/` directories. Ensure module structure adheres to WSP 1.
*   `NO_TEST`: Create the required test file (e.g., `tests/test_<source_file_name>.py`). Add basic tests or a skip marker initially if needed, but the file must exist.
*   `MISSING`: Investigate why the file is missing. Restore it from the baseline or version control if its removal was unintentional. If removal was intentional, this may require updating the baseline itself in a future step.
*   `MODIFIED`: Review the changes using `diff` or Git history. If the changes are intentional and correct, proceed. If unintentional, revert them. Significant intentional changes may warrant creating a new Clean State baseline later.
*   `EXTRA`: Determine if the file is necessary. If it's a new, required part of the module, ensure it has tests and documentation. If it's accidental or temporary, remove it. If it's part of a new feature, it should ideally be introduced alongside its tests.
*   `FOUND_IN_FLAT`: This usually indicates an issue needing fixing in the baseline itself (the file should be moved to `src/` there) or confirms that a file refactored in the current workspace was previously flat. Requires careful review based on WSP 1 refactoring goals.
*   `INTERFACE_MISSING`: Create the required interface definition file according to WSP 12.
*   `DEPENDENCY_MANIFEST_MISSING`: Create the required dependency manifest file according to WSP 13.
*   `TEST_README_MISSING`: Create a `tests/README.md` file. Populate it by listing existing test files and their purpose, following the standard defined in Section I AI Guidelines and WSP 1.


#### 4.8. Compliance Gate


Passing relevant FMAS checks is a non-negotiable prerequisite.


*   🛑 Failure to pass Mode 1 checks blocks completion of WSP 1.
*   🛑 Failure to pass Mode 2 checks (against previous baseline) blocks creation of a new Clean State under WSP 2.
*   🛑 Failure to pass checks defined in CI/CD blocks merging PRs under WSP 7.
*   🛑 Failure blocks progression past Step 1 of WSP 6.


Remediate all reported FMAS issues before attempting to proceed with these dependent actions.


#### 4.9. Related WSPs


*   WSP 1: Defines the target structure (`src/`/`tests/`) that FMAS validates.
*   WSP 2: Defines the Clean State baselines used by FMAS Mode 2 comparison.
*   WSP 3: Defines the Enterprise Domain hierarchy that FMAS validates.
*   WSP 6: Mandates FMAS execution as its first step.
*   WSP 7: Incorporates FMAS checks into PR validation.
*   WSP 8: Uses similar comparison principles for regression detection, often manually or with different tools.
*   WSP 12: Defines interface requirements checked by FMAS.
*   WSP 13: Defines dependency management requirements checked by FMAS.


---


### WSP 5: Module Prioritization Scoring (MPS) System


**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** Prioritization of development efforts across modules within the FoundUps Agent ecosystem.


#### 5.1. Purpose


The **Module Prioritization Scoring (MPS) System** provides a consistent, objective methodology for evaluating and ranking modules based on their strategic importance and implementation considerations. This is augmented by the **LLME Semantic Triplet Rating (see Appendix G)**, which provides a qualitative layer for understanding a module's state, local impact, and systemic importance. This combined approach enables the development team to:


*   Focus efforts on the highest-value modules first.
*   Make informed decisions about resource allocation.
*   Create a defensible, transparent roadmap.
*   Balance immediate needs with long-term architectural goals.
*   Communicate priorities clearly to all stakeholders.
*   Align development effort with desired semantic states of modules (as defined by LLME).


#### 5.2. Scope


This WSP applies to:
*   All modules within the hierarchical `modules/` directory structure.
*   Proposed modules not yet implemented but under consideration.
*   Major feature enhancements to existing modules that warrant re-evaluation.
*   Assessment and tracking of module LLME scores alongside MPS.


#### 5.3. Scoring Criteria (MPS Dimensions)


Each module receives a score from 1 (lowest) to 5 (highest) in four dimensions:


##### A. Complexity (1-5)
*   **Definition:** How difficult is the module to implement or refactor correctly?
*   **Consideration Factors:**
    *   Technical complexity and algorithmic challenges
    *   Dependencies on external systems or APIs
    *   State management requirements
    *   Performance or scaling concerns
    *   Required expertise availability
    *   *LLME Influence:* A module's current LLME 'Present State' (Digit A) might influence complexity (e.g., a dormant module 'A=0' might be more complex to activate).


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
    *   *LLME Influence:* LLME 'Local Impact' (Digit B) and 'Systemic Importance' (Digit C) directly inform this. A module with B=2 or C=2 is inherently more important.


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
    *   *LLME Influence:* An active module (LLME Digit A=1 or A=2) may be less deferrable than a dormant one (A=0), unless activating it is the urgent task.


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
    *   *LLME Influence:* LLME 'Local Impact' (Digit B) and 'Systemic Importance' (Digit C) directly inform this. A module with B=2 or C=2 has higher potential impact. An 'emergent' state (Digit A=2) could also signify high impact.


| Score | Impact Level           | Description                                                         |
|-------|------------------------|---------------------------------------------------------------------|
| 1     | Minimal                | Little noticeable improvement to users or system                    |
| 2     | Minor                  | Some value, but limited in scope or effect                          |
| 3     | Moderate               | Clear benefits visible to users or significant internal improvements|
| 4     | Major                  | Substantial value enhancement, highly visible improvements          |
| 5     | Transformative         | Game-changing capability that redefines system value                |


#### 5.3bis. LLME Semantic Score (A-B-C)
Refer to **Appendix G** for the full LLME Semantic Triplet Rating System.
*   **Digit A: Present State** (0=dormant, 1=active, 2=emergent)
*   **Digit B: Local/Module Impact** (0=passive, 1=relevant, 2=contributive)
*   **Digit C: Systemic Importance** (0=irrelevant, 1=conditional, 2=essential)
*   *Constraint: Digits must be non-regressive (A ≤ B ≤ C).*

The LLME score is a semantic fingerprint, not a direct numerical input to the MPS sum, but it provides critical context and can refine prioritization.

#### 5.4. Scoring Process


1.  **Initial MPS Assessment:** For each module, assign scores (1-5) for Complexity, Importance, Deferability, and Impact based on the criteria tables.
2.  **LLME Score Assignment/Review:** Assign or review the module's current LLME score (e.g., "112") and, if applicable, a target LLME score. Justify the LLME score based on its definitions (Appendix G).
3.  **Calculate MPS Score:** Sum the four dimension scores to obtain the total MPS score.
    ```
    MPS Score = Complexity + Importance + Deferability + Impact
    ```
4.  **Document Rationale:** Briefly explain the reasoning behind each MPS dimension score and the LLME score.
5.  **Review & Consensus:** The development team should review scores (both MPS and LLME) together to align understanding and reach consensus on final values.


#### 5.5. Priority Classification & LLME Refinement


Based on the total MPS score (range: 4-20), modules are classified into priority tiers. The LLME score provides a crucial secondary layer for refining priority within these tiers.


| MPS Score Range | Priority Classification | Action Guideline & LLME Considerations                                                                    |
|-----------------|-------------------------|-----------------------------------------------------------------------------------------------------------|
| 16-20           | Critical (P0)           | Top priority; work should begin immediately. <br/>*LLME Refinement:* Modules with LLME `X22` or target `X22` are paramount. Effort may focus on achieving/maintaining high LLME within P0. |
| 13-15           | High (P1)               | Important for near-term roadmap; prioritize after P0 items. <br/>*LLME Refinement:* Consider LLME to sequence P1s. A module evolving to a higher LLME state (e.g. from `011` to `122`) might be prioritized. |
| 10-12           | Medium (P2)             | Valuable but not urgent; scheduled within current milestone. <br/>*LLME Refinement:* LLME can help differentiate between P2s. Development might target improving a specific LLME digit. |
| 7-9             | Low (P3)                | Should be implemented eventually but can be deferred. <br/>*LLME Refinement:* Modules with low current and target LLME (e.g., `000`, `001`) typically remain here unless strategic shift. |
| 4-6             | Backlog (P4)            | Reconsidered in future planning cycles. <br/>*LLME Refinement:* Typically modules with low LLME and low MPS. May be candidates for deprecation if LLME remains `000`. |

**LLME as a Strategic Driver:**
*   **Increasing LLME:** Development effort can be explicitly aimed at increasing a module's LLME score (e.g., moving a module from `011` (dormant, relevant, conditional) to `122` (active, contributive, essential)). This goal can elevate a module's priority even if its raw MPS is moderate.
*   **Maintaining LLME:** For critical modules already at a high LLME (e.g., `122`, `222`), effort will focus on maintaining this state, which also implies high priority.


#### 5.6. Documentation & Version Control


*   **Format:** MPS scores, LLME scores, and rationales should be maintained in version-controlled YAML:
    *   Primary file: `modules_to_score.yaml` in the repository root.
    *   Structure: Each module as a top-level key with nested scores and rationale.
*   **Example Format:**
    ```yaml
    StreamListener:
      complexity: 3
      complexity_rationale: "Requires integration with YouTube API and error handling."
      importance: 5 # Influenced by high target LLME C digit
      importance_rationale: "Core system component for receiving all user interactions."
      deferability: 2
      deferability_rationale: "Current manual process exists as fallback."
      impact: 5 # Influenced by high target LLME B and C digits
      impact_rationale: "Enables all real-time interaction capabilities."
      mps_score: 15 # Calculated: 3+5+2+5
      classification: "High (P1)"
      llme_current: "011" # Example: Currently dormant but with some local relevance and conditional systemic importance
      llme_target: "122"  # Example: Aiming for active, contributive, and system-essential
      llme_rationale: "Currently a manual fallback exists (011). Target is to make it fully active, deeply integrated, and essential for live operations (122)."
    ```
*   **Updates:** MPS and LLME scores should be reviewed and potentially updated:
    *   When significant new information becomes available about a module.
    *   At the start of each release planning cycle.
    *   After major architectural changes or feature completion that may affect dependencies or capabilities.
    *   When a module transitions between development stages (PoC, Prototype, MVP - see WSP 9).


#### 5.7. Integration with Workflow


*   **Planning:** Priority classifications, refined by LLME considerations, directly influence sprint/milestone planning.
*   **Resource Allocation:** Engineering resources are allocated proportionally to module priority levels, considering LLME targets.
*   **Visualization:** The roadmap should visually indicate module priorities and perhaps their current/target LLME states.
*   **Granularity:** For complex modules, consider scoring sub-components separately. LLME can also apply at a sub-component level if meaningful.


#### 5.8. Automation


*   A helper script (`prioritize_module.py`) exists to:
    *   Calculate and validate MPS scores.
    *   Potentially validate LLME non-regressive rule (A<=B<=C).
    *   Generate visualizations of module priorities, possibly incorporating LLME.
    *   Update the YAML file with new entries.
    *   Provide reports on the highest-priority modules.
*   Usage:
    ```bash
    python prioritize_module.py --update StreamListener # This would prompt for MPS dimensions and LLME scores
    python prioritize_module.py --report top10
    ```


#### 5.9. Related WSPs


*   **WSP 1 (Refactoring):** MPS and LLME scores inform which modules are prioritized for refactoring.
*   **WSP 3 (Enterprise Domains):** Module prioritization (MPS & LLME) now considers domain context and cross-domain dependencies.
*   **WSP 6 (Test Audit):** Higher-priority modules (high MPS and/or critical LLME) warrant more thorough test coverage and earlier auditing.
*   **WSP 9 (Milestone Rules):** MPS classification and target LLME influence which modules progress from PoC to Prototype to MVP first. LLME scores evolve with these stages.
*   **WSP 11 (ModLog & Versioning):** Changes in MPS or LLME scores should be noted in the ModLog if significant.


#### 5.10. Examples


**Example 1: StreamListener Module**
```
Module: StreamListener
- Complexity: 3 (Moderate integration complexity with YouTube API)
- Importance: 5 (Essential for core functionality, driven by target LLME C=2)
- Deferability: 2 (Can be temporarily handled manually)
- Impact: 5 (Enables all real-time interaction, driven by target LLME B=2, C=2)
→ MPS Score = 15
→ Classification: High (P1)
- LLME Current: "011" (Dormant, Relevant, Conditional)
- LLME Target: "122" (Active, Contributive, Essential)
- Rationale: Needs to be fully activated and made central to operations.
```


**Example 2: Analytics Dashboard Module**
```
Module: AnalyticsDashboard
- Complexity: 2 (Relatively straightforward data visualization)
- Importance: 2 (Helpful but not required for operation)
- Deferability: 1 (Can be implemented much later)
- Impact: 3 (Provides helpful insights but not transformative)
→ MPS Score = 8
→ Classification: Low (P3)
- LLME Current: "000" (Dormant, Passive, Irrelevant)
- LLME Target: "111" (Active, Relevant, Conditional)
- Rationale: Currently not built. Target is a functional, informative dashboard.
```


---


### WSP 6: Test Audit & Coverage Verification


**Document Version:** 1.2
**Date Updated:** 2024-05-24
**Applies To:** Final test validation sweep before integration/release.


> **Note on Language Agnosticism:** While specific examples in this WSP use Python and pytest conventions, the principles aim to be language-agnostic. Project-specific rules (`.foundups_project_rules`) or appendices should define language-specific testing frameworks, commands, and coverage thresholds. The rigor of this audit may be influenced by the module's LLME score (Appendix G).


#### 6.1. Purpose


Comprehensive audit of active modules covering: Quality Gate, Windsurf Compliance, Risk Reduction, Coverage Assurance, Integration Readiness, Interface Contract Assurance. The depth and urgency of this audit can be scaled based on the module's LLME score, particularly its 'Systemic Importance' (Digit C).


The Interface Contract Assurance verifies that modules correctly implement their defined interfaces (WSP 12).

##### 6.1.1. Production Override Provision
**(Content moved from original WSP 5.1.1 for structural consistency with WSP 6 header)**

**When the production system is demonstrably working** (successful authentication, core functionality operational, live user interactions functioning), test failures that stem from **infrastructure issues** (import problems, test environment setup, legacy test compatibility) rather than **functional regressions** may be bypassed to prevent blocking critical development progress.

**Production Override Criteria:**
- ✅ Production system demonstrably functional (authentication working, core features operational)
- ✅ Test failures are infrastructure-related (imports, environment, test setup) NOT functional regressions
- ✅ Core business logic validated through live testing or manual verification
- ✅ Override decision documented in ModLog (WSP 11) with justification and timeline for test remediation

**Usage:** Production Override should be used sparingly and only when strict test adherence would block critical system progression despite functional correctness. This is especially critical to evaluate for modules with high LLME scores (e.g., C=2).


#### 6.2. Scope
*   **Included:** Modules under `/modules/` with `src/`/`tests/`. Particular focus on modules with high LLME scores or those transitioning to higher LLME states.
*   **Excluded:** Experimental/deprecated (typically LLME `000` or low target), 3rd-party, modules without `/tests/`.


#### 6.3. Prerequisites
*   Clean Git, Python Env (`pytest`, `pytest-cov`).
*   FMAS Tool.
*   Baseline Access.
*   Knowledge of tools/protocols.
*   Dedicated Audit Branch.


#### 6.4. Responsibilities
*   Execution: Dev/QA.
*   Review (Optional): Peer/Lead.


#### 6.5. Procedure (Summary)
*(See detailed version in separate WSP 6 document if needed)*
**A. Preparation:** Update env, create branch, install deps.
**B. Step 1: FMAS Test File Check:** Run FMAS (`--baseline`), check for `NO_TEST`. Remediate by creating test files/stubs. Goal: Zero `NO_TEST`.
**C. Step 2: Warning & Failure Sweep (`pytest -ra`):** Run `pytest -ra modules/`. Check for `F`/`E`/`W`/`s`/`x`/`X`. Remediate failures & warnings. Review skips/xfails. Goal: Clean run (Zero `F`/`E`/unaddressed `W`).
**D. Step 3: Interface Contract Testing:** For each module with a defined interface (WSP 12), run contract tests. These might involve schema validation, mock service interactions (e.g., using Pact), or API endpoint checks. Remediate failures. Goal: Zero contract test failures. (Critical for modules with LLME B=2 or C=2).
**E. Step 4: Per-Module Coverage (`pytest --cov`):** Loop through modules, run `pytest <mod>/tests/ --cov=modules.<mod>.src --cov-fail-under=90`. Check exit code. Remediate by adding tests if < 90%. Goal: Each module >= 90%. Higher thresholds may apply for modules with high LLME scores.
**F. Step 5: Integration Test Considerations:** Review results. Identify modules ready for integration testing based on passing unit and contract tests. Note: Actual integration tests may occur in a separate phase/WSP but readiness is assessed here.
**G. Step 6: Reporting:** Generate aggregate HTML report (`--cov-report=html`). Create/update summary `.md` report (`reports/test_audit_vX.Y.Z.md`) detailing status of each step & per-module coverage.
**H. Step 7: Commit:** If PASS, commit fixes/tests & report (`git commit -m "feat(test): Complete test audit..."`).


#### 6.6. Acceptance Criteria (Audit PASS)
*   FMAS: Zero `NO_TEST`.
*   `pytest -ra`: Zero `F`/`E`/unaddressed `W`.
*   Interface Tests: Zero failures in contract tests.
*   Coverage: Each module >= 90% (potentially higher for high-LLME modules).
*   Report: Accurate, PASS status.

**Production Override Alternative:**
If Production Override criteria are met, audit may PASS despite test failures when:
*   Production system demonstrably functional
*   Test failures are infrastructure-related (not functional regressions)
*   Override documented in ModLog (WSP 11) with remediation timeline


#### 6.7. Failure / Rollback
*   FAIL if criteria not met. Block merge. Remediate & re-run.


---


### WSP 7: Git Branch & Tag Discipline (Previously WSP 6)


**Document Version:** 1.1
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** All Git operations (branching, tagging, committing, merging) within the FoundUps Agent MMAS repository.


#### 7.1. Purpose


To establish and enforce strict, consistent, and auditable Git practices that support modular development, code traceability, release management, and integration stability. Adherence ensures a clean, understandable project history, facilitates automated processes (CI/CD), enables safe rollbacks via Clean States, and aligns with the overall Windsurf Protocol. Commit messages may optionally reference changes to module LLME scores (Appendix G).


#### 7.2. Scope


This WSP defines mandatory procedures and conventions for:
*   Branch creation and naming.
*   Commit message formatting.
*   Tag creation and naming (for Clean States and software releases).
*   Pull Request (PR) creation, review, and merge strategies.


#### 7.3. Branching Strategy & Naming Convention


*   **Base Branch:** All development branches **must** originate from the latest commit of the primary integration branch (typically `main` or `develop`, specify which one is primary).
*   **Branch Lifetime:** Branches should be short-lived, focusing on a single atomic task or WSP scope. Merge completed branches promptly.
*   **Naming Convention:** Branches **must** use the following `type/short-description` format. Names should be lowercase, using hyphens `-` to separate words.


| Type       | Prefix        | Description & Example                                     |
|------------|---------------|-----------------------------------------------------------|
| Feature    | `feature/`    | New functionality or enhancement (`feature/fmas-json-output`) |
| Fix        | `fix/`        | Bug correction in existing code (`fix/livechat-connection-retry`) |
| Refactor   | `refactor/`   | Code restructuring without changing behavior (`refactor/fmas-use-pathlib`) |
| Docs       | `docs/`       | Documentation changes only (`docs/update-wsp7-git`)       |
| Test       | `test/`       | Adding or improving tests (`test/add-token-manager-coverage`)| 
| Hotfix     | `hotfix/`     | Urgent production bug fix (branched from release tag/`main`) |
| Chore      | `chore/`      | Maintenance tasks, build scripts, etc. (`chore/update-dependencies`) |


#### 7.4. Tagging Strategy & Naming Convention


*   **Purpose:** Tags mark specific, significant points in the repository's history.
*   **Type:** All tags **must** be annotated tags (`git tag -a`) to include metadata (tagger, date, message).
*   **Pushing:** Tags **must** be pushed to the remote repository immediately after creation (`git push origin <tag_name>`).
*   **Naming Convention:**


| Tag Type          | Format                 | Purpose & Trigger                                                    | Related WSP |
|-------------------|------------------------|----------------------------------------------------------------------|-------------|
| **Clean State**   | `clean-vX`             | Marks commit corresponding to a Clean State folder snapshot (WSP 2). Triggered by WSP 2 procedure *after* tests/FMAS pass. | WSP 2       |
| **Release**       | `vX.Y.Z`               | Production-ready release, following SemVer (WSP 11).                 | WSP 11      |
| **Release Candidate**| `vX.Y.Z-rc.N`         | Potential release candidate for final testing.                       | WSP 11      |
| **Beta Release**  | `vX.Y.Z-beta.N`        | Pre-release for wider testing, API may still change slightly.        | WSP 11      |


#### 7.5. Commit Message Format


*   **Standard:** Commits **must** follow the **Conventional Commits** specification (or a documented project adaptation).
*   **Structure:** `<type>(<scope>): <short summary>`
    *   **Type:** Matches branch prefix type (e.g., `feat`, `fix`, `refactor`, `test`, `docs`, `chore`).
    *   **Scope (Optional but Recommended):** The module or component affected (e.g., `fmas`, `livechat`, `wsp`). Enclosed in parentheses.
    *   **Short Summary:** Concise description of the change, imperative mood (e.g., "add baseline flag"), lowercase.
*   **Body (Optional):** Provide more context, motivation, or details after a blank line. Can include notes on LLME score changes if relevant (e.g., "Refactored module for increased contributiveness (LLME B: 1->2)").
*   **Footer (Optional):** Reference related issues, PRs, or breaking changes (e.g., `BREAKING CHANGE: ...`, `Refs: #123`).
*   **Emoji Prefix (Optional but Recommended):** Use standard ESM emojis (WSP 10) at the start of the summary for quick visual identification.


| Type       | Emoji | Example Commit Subject                     |
|------------|-------|--------------------------------------------|
| Feat       | ✨    | `feat(fmas): add --baseline comparison`    |
| Fix        | 🐛    | `fix(livechat): handle null chat ID`      |
| Refactor   | ♻️    | `refactor(auth): simplify token refresh; LLME B: 1->2`  |
| Test       | 🧪    | `test(parser): increase coverage to 95%` | 
| Docs       | 📄    | `docs(wsp7): clarify tag naming`         |
| Chore      | 🧹    | `chore: update pytest version`             |


#### 7.6. Pull Request (PR) Requirements


*   **Requirement:** Non-trivial changes intended for the primary integration branch (`main`/`develop`) **must** be submitted via a PR. Direct pushes are disallowed (enforced via branch protection rules).
*   **Target Branch:** Typically `main` (or `develop` if used).
*   **Content:** PRs must include:
    *   A clear title summarizing the change.
    *   A description referencing the purpose, related issue(s), and relevant WSP(s).
    *   Summary of changes made, including any impact on module LLME scores.
    *   Steps for manual verification (if applicable).
    *   Confirmation that relevant WSP validation steps passed (e.g., FMAS results, `pytest -ra` clean, coverage met).
*   **Checks:** PRs **must** pass all mandatory automated checks (configured via CI/CD):
    *   Build success.
    *   All tests pass (`pytest`).
    *   Linting / Formatting checks pass.
    *   FMAS structure/test checks pass.
    *   *(Optional)* Coverage threshold checks.
*   **Review:** Require at least **one** formal approval from a designated reviewer (human). Review should consider LLME impact if noted.
*   **Merge Strategy:** Use **Squash and Merge** by default to maintain a clean, linear history on the main branch. Ensure the squashed commit message follows the format defined in section 7.5. *(Alternative strategies like Rebase and Merge may be used only with explicit team agreement for specific cases).*


#### 7.7. Enforcement & Validation


*   **Branch Protection:** Configure Git repository settings (e.g., GitHub/GitLab) to enforce PR requirements (reviews, checks) before merging to `main`/`develop`. Disallow direct pushes.
*   **CI/CD:** Implement automated checks (lint, test, FMAS) that run on PRs.
*   **Manual Review:** Reviewers are responsible for verifying adherence to naming conventions, commit format, and WSP compliance during PR review.
*   **Violations:**
    *   PRs failing checks or reviews will be blocked from merging.
    *   Significant deviations may require branch rework or rejection.
    *   Non-compliance events should be noted for process improvement.


#### 7.8. Related WSPs


*   **WSP 0:** Defines overall enforcement philosophy.
*   **WSP 2:** Governs `clean-vX` tagging.
*   **WSP 6:** Defines test audit criteria required before merging/tagging.
*   **WSP 10:** Defines standard Emoji Sequence Map (ESM) used in commits.
*   **WSP 11:** Defines SemVer for `vX.Y.Z` release tags and MODLOG conventions (which may include LLME updates).


---


### WSP 8: Snapshot Regression Comparison (Prometheus Diff) (Previously WSP 7)


**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** Comparing the current working state against a designated Clean State baseline to detect regressions or unintended changes.


#### 8.1. Purpose


The **Snapshot Regression Comparison** process (nicknamed "Prometheus Diff" after the Titan associated with foresight) provides a systematic methodology for identifying and preventing unintended side effects or regressions when making changes to the codebase. It ensures that:


*   Changes remain confined to their intended scope.
*   No undocumented modifications occur.
*   The system's behavior remains consistent with the baseline where expected.
*   Unintentional regressions are caught before they are merged into stable branches.
*   Refactoring efforts preserve functionality while improving structure (this includes ensuring that changes intended to improve a module's LLME score (Appendix G) do not negatively impact existing functionality).


#### 8.2. Scope


This WSP applies to:
*   Code changes made since the last stable snapshot or Clean State.
*   Refactoring operations (**WSP 1**) to confirm functional equivalence.
*   Pre-release verification (**WSP 9**) to ensure quality gates are met.
*   Pull request validation (**WSP 7**) to assist code reviews.


#### 8.3. Prerequisites


*   A designated Clean State baseline per **WSP 2** (either folder copy or Git tag).
*   Standard comparison tools (`diff`, `git diff`) or the FMAS tool (**WSP 4**).
*   Complete test suite execution results from the baseline.
*   Current test suite execution results after changes.


#### 8.4. Process Workflow


##### Step 1: Baseline Creation/Selection
*   **Identify Baseline:** Select the appropriate Clean State to compare against:
    *   For routine development: The most recent Clean State.
    *   For refactoring verification: The Clean State created prior to refactoring.
    *   For bug investigation: The last Clean State known to work correctly.
*   **Validate Baseline:** Ensure the selected baseline has:
    *   Passed all automated tests.
    *   Been verified with FMAS (**WSP 4**).
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
    *   Explicitly include interface definition files (e.g., INTERFACE.md, OpenAPI specs defined in WSP 12) and dependency manifests (requirements.txt, package.json defined in WSP 13) in the git diff or diff -r scope. Unintended changes here are critical regressions.
    *   Command (Git Tag): `git diff clean-vX -- path/to/focus`
    *   Command (Folder): `diff -r -u Foundups-Agent/path/to/focus foundups-agent-cleanX/path/to/focus`
*   **FMAS Comparison (For Modules):**
    *   Utilize FMAS (**WSP 4**) with baseline comparison mode.
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
    *   Include explanations for all intentional deviations from the baseline, including any relation to LLME score changes.


#### 8.5. Validation Rules


All changes between the baseline and current state must comply with these rules:


1.  **Change Documentation:**
    *   Every change must be documented in the ModLog (**WSP 11**).
    *   Undocumented changes are considered potential regressions.
2.  **Task Alignment:**
    *   Each logical change must be tied to an approved WSP task.
    *   Changes outside the scope of approved tasks require justification.
3.  **Test Status:**
    *   No new test failures should be introduced.
    *   Any new test warnings must be documented and reviewed.
4.  **Coverage Maintenance:**
    *   Test coverage should not decrease significantly.
    *   Critical modules should maintain their coverage thresholds per **WSP 6**.
5.  **Structural Integrity:**
    *   FMAS structural validation should continue to pass.
    *   Module structure should adhere to Windsurf conventions (**WSP 1**).
6.  **Intentional Changes Only:**
    *   All changes should be intentional and purposeful.
    *   "Noise" changes (e.g., unintended formatting, whitespace) should be eliminated.
7.  **Interface Stability:**
    *   Any changes to interface definitions must be intentional, documented (ModLog WSP 11), and potentially trigger SemVer minor/major bumps.
8.  **Dependency Consistency:**
    *   Changes to dependency manifests must be intentional and documented.


#### 8.6. Status Classification


Based on the comparison results, one of the following statuses is assigned:


| Status | Symbol | Meaning | Action Required |
|--------|--------|---------|----------------|
| **No Regression** | ✅ | All changes are intentional, documented, and tests pass. | May proceed with integration/release. |
| **Partial Drift** | ⚠️ | Minor issues such as formatting changes or new warnings found. No functional regressions. | Document issues; may proceed with caution after review. |
| **Regression Detected** | ❌ | Test failures or significant undocumented logic changes discovered. | Address all regressions before proceeding. |


#### 8.7. Automation Recommendations


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


#### 8.8. Related WSPs


*   **WSP 1 (Refactoring):** Prometheus Diff verifies refactoring preserves functionality.
*   **WSP 2 (Clean States):** Defines the baselines used for comparison.
*   **WSP 4 (FMAS):** Provides structural validation and baseline comparison capabilities.
*   **WSP 6 (Test Audit):** Defines test coverage requirements maintained during comparisons.
*   **WSP 7 (Git):** Defines the git operations used in the comparison process.
*   **WSP 11 (ModLog):** Documents changes that should align with comparison findings.
*   **WSP 12 (Interface Definition):** Defines the interfaces whose stability is verified.
*   **WSP 13 (Dependency Management):** Defines the dependency manifests checked for consistency.


#### 8.9. Example Report


```
# Prometheus Diff Report - 2024-04-05


## Baseline: clean-v4 (2024-03-15)
## Target: Current working directory (feat/new-oauth)


### Structure Changes:
- ADDED: modules/oauth_manager/src/token_rotation.py (DOCUMENTED ✅)
- MODIFIED: modules/oauth_manager/src/oauth_manager.py (DOCUMENTED ✅, LLME A: 0->1)
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


### WSP 9: PoC → Prototype → MVP Milestone Rules (Previously WSP 8)


**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** The development progression of features, modules, or entire systems through defined maturity stages, correlated with LLME Semantic Triplet Ratings (Appendix G).


#### 9.1. Purpose


The **PoC → Prototype → MVP Milestone Rules** establish clear, measurable criteria and quality gates for the progression of software components through distinct stages of development maturity. This WSP ensures that:


*   Development follows a systematic maturation path with defined checkpoints.
*   Quality standards increase appropriately at each stage.
*   Stakeholders maintain consistent expectations about the capabilities and limitations of features at each stage.
*   Resource allocation decisions are informed by a feature's maturity stage and its current/target LLME score.
*   Technical and documentation debt is managed throughout the development lifecycle.
*   Module LLME scores evolve predictably with maturity stages.


#### 9.2. Development Stage Definitions & Expected LLME Evolution


##### 9.2.1. Proof-of-Concept (PoC) - Version 0.0.x
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
*   **Expected LLME Range (Appendix G):** Typically `000` (dormant, passive, irrelevant) to `111` (active, relevant, conditional). The goal is often to prove basic activation (Digit A=1) and some relevance (Digit B=1).

##### 9.2.2. Prototype - Version 0.1.x - 0.9.x
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
*   **Expected LLME Range:** Typically `110` (active, relevant, irrelevant systemically yet) to `122` (active, contributive, essential). Focus on enhancing local impact (Digit B=2) and demonstrating conditional or essential systemic importance (Digit C=1 or C=2).

##### 9.2.3. Minimum Viable Product (MVP) - Version 1.0.x+
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
*   **Expected LLME Range:** Typically `112` (active, relevant, essential) to `222` (emergent, contributive, essential). MVP implies essential systemic role (Digit C=2) and often active contribution (Digit B=2). Emergence (Digit A=2) is an advanced goal.


#### 9.3. Stage Transition Gates


The following criteria **must** be met before a component can progress to the next stage:


##### 9.3.1. PoC → Prototype Transition Gate


**Mandatory Requirements:**
*   ✅ **Core Functionality:** Basic functionality is implemented and demonstrable.
*   ✅ **Technical Feasibility:** Proof that the approach is technically viable.
*   ✅ **Architecture Definition:** Initial architecture/design documented.
*   ✅ **Stakeholder Review:** Initial concept has been reviewed by key stakeholders.
*   ✅ **Scope Definition:** Prototype scope and requirements are clearly defined.
*   ✅ **Resource Assessment:** Team has capacity and skills to develop the prototype.
*   ✅ **LLME Assessment:** Current LLME score documented (e.g., `000`, `010`) and target LLME for Prototype defined (e.g., `111`, `112`).

**Documentation Requirements:**
*   Developer notes on implementation approach.
*   Initial scope document.
*   Technical feasibility assessment.
*   LLME assessment and rationale.

**Quality Metrics:**
*   No specific test coverage requirement (though some unit tests are encouraged).
*   Basic functionality must be demonstrated.


##### 9.3.2. Prototype → MVP Transition Gate


**Mandatory Requirements:**
*   ✅ **Functional Completeness:** All core functionality is implemented.
*   ✅ **Structural Compliance:** Module fully adheres to the Windsurf structure (**WSP 1**).
*   ✅ **FMAS Compliance:** Passes all FMAS checks (**WSP 4**).
*   ✅ **Test Coverage:** Meets minimum coverage requirements (typically ≥80-90%, defined per module via **WSP 5**, influenced by LLME).
*   ✅ **Documentation:** API documentation, usage examples, and configuration details exist.
*   ✅ **Error Handling:** Comprehensive error handling for all expected error conditions.
*   ✅ **Code Review:** Complete code review by at least one peer.
*   ✅ **User Feedback:** At least one round of user/stakeholder feedback incorporated.
*   ✅ **Stable Interface:** Module interface is clearly defined, documented, and validated according to WSP 12, marked as stable (minimal breaking changes expected).
*   ✅ **Declared Dependencies:** All dependencies are identified and correctly declared according to WSP 13.
*   ✅ **LLME Target Achieved:** Module has achieved its target LLME score for MVP (e.g., `122`, `112`), demonstrating required activation, contribution, and systemic importance.

**Documentation Requirements:**
*   README with setup and usage instructions.
*   API documentation (docstrings, function signatures, examples).
*   Architecture overview (data flow, component interactions).
*   Configuration guide.
*   Updated LLME score and rationale in module documentation/`modules_to_score.yaml`.

**Quality Metrics:**
*   Minimum test coverage per **WSP 6** (typically ≥90% for critical modules, especially those with high LLME C-digit).
*   All tests pass.
*   Passes all Interface Contract tests (WSP 6, Step D).
*   No critical bugs or blockers in issue tracker.
*   Performance meets defined baseline requirements.


#### 9.4. Versioning Alignment


Version numbers explicitly indicate development stage as described in **WSP 11**:


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


#### 9.5. Workflow Integration


**A. Module/Feature Tracking:**
*   Each module/feature should have its current stage explicitly tracked in:
    *   ModLog (**WSP 11**), including LLME score.
    *   Project management tool or issue tracker, including LLME score.
    *   README or documentation, including LLME score.
*   Use standard stage designations in documentation: `[PoC]`, `[Prototype]`, `[MVP]`.


**B. Planning & Prioritization:**
*   Use the Module Prioritization Score (**WSP 5**), which incorporates LLME, in conjunction with stage to inform development priorities.
*   Consider a module's current stage and LLME when estimating effort for future work.
*   Balance portfolio with appropriate mix of stages based on project priorities and LLME evolution goals.


**C. Code Organization:**
*   Consider using feature flags to hide non-MVP functionality in production environments.
*   Maintain separate branches for PoC and Prototype work if it might destabilize main codebase.
*   Tag repository with version reflecting stage transitions.


#### 9.6. Documentation & Communication


**A. README Badges:**
*   Include development stage and current LLME score in module README files with standardized badges:
    *   ![PoC](https://img.shields.io/badge/Stage-PoC-yellow) `PoC (0.0.x)` - `LLME: [ABC]`
    *   ![Prototype](https://img.shields.io/badge/Stage-Prototype-orange) `Prototype (0.x.x)` - `LLME: [ABC]`
    *   ![MVP](https://img.shields.io/badge/Stage-MVP-green) `MVP (1.x.x+)` - `LLME: [ABC]`


**B. Release Notes:**
*   Clearly indicate stage and relevant LLME score(s) in all release notes and ModLog entries (WSP 11).
*   When transitioning stages, highlight this explicitly in the ModLog, including the new LLME state.
*   Include explanation of what the stage and LLME transition means for users/developers.


**C. Expectation Setting:**
*   Communicate appropriate expectations to stakeholders based on stage and LLME:
    *   PoC (e.g., LLME `010`): "Demonstrates concept, active but passive locally, not systemically relevant yet, expect instability."
    *   Prototype (e.g., LLME `111`): "Core functionality works, active & relevant, conditionally important, expect rough edges, active development."
    *   MVP (e.g., LLME `122`): "Production-ready, active, contributive, and essential, stable API, suitable for dependence by other components."


#### 9.7. Related WSPs


*   **WSP 1 (Module Refactoring):** Structural requirements for Prototype → MVP transition. LLME assessment part of planning.
*   **WSP 4 (FMAS):** Compliance checks required for Prototype → MVP transition.
*   **WSP 5 (MPS):** Prioritization of modules at different stages, incorporating LLME.
*   **WSP 6 (Test Audit):** Test coverage requirements for stage progression, influenced by LLME.
*   **WSP 7 (Git):** Branch and tag conventions that reflect stages. Commits may note LLME changes.
*   **WSP 11 (ModLog):** Documentation of stage and LLME transitions in ModLog.
*   **WSP 12 (Interface Definition):** Interface stability requirements for MVP, critical for high LLME modules.
*   **WSP 13 (Dependency Management):** Dependency declaration requirements for MVP.


---


### WSP 10: Emoji Sequence Map (ESM) Protocol (Previously WSP 9)


**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** Use of emojis in commit messages, logs, documentation, and potentially UI components for consistent semantic meaning across the FoundUps ecosystem.


#### 10.1. Purpose


The **Emoji Sequence Map (ESM) Protocol** establishes a standardized set of emoji symbols to:


*   Provide visual cues that enhance text-based communication.
*   Create a consistent semantic layer that is immediately recognizable.
*   Improve the scanability of commit histories, logs, and documentation.
*   Support potential automated parsing or filtering based on emoji prefixes.
*   Reinforce the meaning conveyed by conventional commit types (**WSP 7**).


#### 10.2. Scope


This ESM Protocol defines mandatory and optional emoji usage for:


*   Git commit message summaries (primary application).
*   ModLog entries (**WSP 11**).
*   Pull request titles and summaries.
*   Documentation status markers.
*   Task/issue tracking.
*   User interface elements (where applicable).


#### 10.3. Primary Emoji Map


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
| 🧬 | DNA | Semantic/State Change | `refactor`, `feat` | `🧬 refactor(core): update module LLME to 122 after integration` |


*(Added 🧬 for LLME/Semantic state changes)*


#### 10.4. Extended Emoji Map


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


#### 10.5. Usage Guidelines


##### 10.5.1. Commit Messages


*   **Placement:** Place the emoji at the beginning of the commit message summary, before the type/scope prefix.
    *   Correct: `✨ feat(auth): add login page`
    *   Also Acceptable: `feat(auth): ✨ add login page`
*   **Consistency:** Choose the emoji that best represents the primary purpose of the commit. Use only one primary emoji per commit message.
*   **PR Titles:** Follow the same convention for pull request titles.


##### 10.5.2. ModLog Entries


*   **Entry Type:** Use the relevant primary emoji to prefix each ModLog version entry (see WSP 11).
    *   Example: `✨ Version: 0.2.0 - Added user authentication module`
*   **Feature Lists:** Consider using emojis for individual feature/change bullets within ModLog entries.
    *   Example: `- 🧬 [auth:LLME] - Updated LLME score to 112 post-refactor`


##### 10.5.3. Documentation


*   **Status Markers:** Use emojis to indicate status in documentation.
    *   ✅ Complete/Done
    *   🔄 In Progress
    *   ⏳ Planned/Upcoming
    *   ⚠️ Warning/Caution
    *   ❌ Deprecated/Removed
    *   🧬 LLME: [ABC] (To denote current semantic state)
*   **Section Headers:** Consider using relevant emojis for documentation section headers to enhance visual differentiation.


##### 10.5.4. User Interface (Optional)


If emojis are used in the UI:
*   Ensure accessibility considerations (screen readers, etc.).
*   Maintain consistent meaning with the ESM Protocol.
*   Use sparingly and purposefully to avoid overwhelming users.


#### 10.6. Automation & Tools


*   **Commit Hooks:** Consider implementing Git commit hooks that:
    *   Validate emoji usage according to ESM Protocol.
    *   Suggest appropriate emojis based on commit message content or branch name.
*   **ModLog Generation:** Use emojis to enhance automated changelog generation from commits.
*   **Visualization:** Enable filtering or color-coding Git history visualization tools based on commit emojis.


#### 10.7. Governance & Updates


*   **Adding New Emojis:** The ESM Protocol can be extended with new emojis when:
    *   A new semantic category emerges that isn't covered by existing emojis.
    *   The new emoji has a clear, distinct meaning with minimal overlap.
    *   The addition is documented in an updated version of this WSP.
*   **Deprecating Emojis:** Existing emojis should only be deprecated if:
    *   They cause technical issues (rendering problems, etc.).
    *   Their meaning has become ambiguous or confusing.
    *   A superior alternative has been identified.
    *   Deprecation is clearly documented with migration guidance.


#### 10.8. Compliance


*   **Expectation Level:** Emoji usage is **required** for commit messages and ModLog entries, **recommended** for documentation status markers, and **optional** for other contexts.
*   **Reviews:** Pull request reviewers should check for and suggest corrections to emoji usage (**WSP 7**).
*   **Auto-correction:** Tools may assist with compliance but should not block workflow for non-critical emoji issues.


#### 10.9. Related WSPs


*   **WSP 7 (Git Discipline):** ESM emojis complement conventional commit types.
*   **WSP 11 (ModLog):** ESM emojis enhance ModLog entries. LLME updates in ModLog may use the 🧬 emoji.
*   **WSP 0 (Protocol Overview):** ESM emojis support the "Audit-Readiness" principle.


---


### WSP 11: Modular Change Log & Versioning Convention (Previously WSP 10)


**Document Version:** 1.0
**Date Updated:** [Insert Date]
**Status:** Active
**Applies To:** Tracking changes across modules, versioning releases, and maintaining the Adaptive Project State (APS), including changes to module LLME Semantic Triplet Ratings (Appendix G).


#### 11.1. Purpose


The **Modular Change Log & Versioning Convention** establishes a consistent, systematic approach to:


*   **Track Changes:** Record module-specific and project-wide changes, including LLME score evolution, in a structured, centralized format.
*   **Version Releases:** Apply industry-standard Semantic Versioning to tag and track software releases.
*   **Maintain History:** Create a comprehensive, searchable history of project evolution.
*   **Communicate Changes:** Enable clear communication of modifications to stakeholders.
*   **Support Automation:** Facilitate automated release note generation and version management.
*   **Adaptive Project State:** Maintain a living record of project progress, insights, task status, and module LLME scores.


#### 11.2. Change Log (ModLog) Specification


##### 11.2.1. Primary Location & Format


*   **File:** `docs/ModLog.md`
*   **Format:** Markdown, following the structure defined in **Appendix B**.
*   **Order:** Chronological, with newest entries at the top.
*   **Ownership:** All developers must update the ModLog when making significant changes.


##### 11.2.2. Entry Structure


Each ModLog entry must include:


*   **Version Number:** Following Semantic Versioning 2.0.0 (described in Section 11.4).
*   **Date:** In YYYY-MM-DD format.
*   **Git Tag:** Corresponding Git tag (if applicable, e.g., `v1.2.3` or `clean-vX`).
*   **Description:** Brief summary of the changes in this version.
*   **Notes:** Additional context or considerations.
*   **Module LLME Updates (If applicable):** Summary of significant LLME score changes for key modules.
*   **Features/Fixes/Changes:** Bulleted list of specific changes, organized by module and component. Use ESM emojis (WSP 10).


##### 11.2.3. Example ModLog Entry


```markdown
====================================================================
## MODLOG - [+UPDATES]:
- Version: 0.2.1
- Date: 2024-03-15
- Git Tag: v0.2.1
- Description: Fixed critical authentication issues and improved error handling. Auth module LLME upgraded.
- Notes: Fixes reported security vulnerability CVE-2024-XXXXX.
- Module LLME Updates:
  - [auth:TokenManager] - LLME: 011 -> 122 (Became active, contributive, and essential)
- Features/Fixes/Changes:
  - 🧬 [auth:TokenManager] - Refactored for full activation and integration (LLME 011 -> 122)
  - 🔒 [auth:TokenManager] - Fixed token expiration validation (Issue #45)
  - 🐛 [auth:OAuth] - Corrected refresh token handling
  - ♻️ [core:ErrorHandler] - Refactored error handling for better logging
  - 🧪 [tests] - Added comprehensive tests for auth module
  - ✨ [Module: Interface] - Defined initial data contract for authentication
  - 🚨 [Module: Interface] - BREAKING CHANGE: Modified signature of verify() method
  - ⬆️ [Module: Deps] - Updated JWT library to version 2.0
====================================================================
```


##### 11.2.4. When to Create ModLog Entries


New entries should be created for:


*   **Official Releases:** Any time a release is tagged with a version number.
*   **Clean States:** When a new Clean State is created (**WSP 2**).
*   **Significant Features:** When a major feature or module is completed.
*   **Critical Fixes:** When important bugs are fixed, especially security issues.
*   **Architectural Changes:** When significant architectural modifications occur.
*   **Significant LLME Changes:** When a module's LLME score changes in a way that reflects a notable shift in its state, impact, or importance (e.g., transition between PoC/Prototype/MVP stages, or a digit increasing by 1 or more).


ModLog entries are not required for routine minor changes or work-in-progress commits unless they significantly alter an LLME score.


#### 11.3. Adaptive Project State (APS)


The APS is a living record maintained within `foundups_global_rules.md` that complements the more formal, snapshot-based ModLog.


##### 11.3.1. APS Sections


*   **Task List:** Current tasks (in-progress, completed, blocked) with statuses and metadata. May include target LLME for tasks related to specific modules.
*   **Project Insights:** Lessons learned, technical decisions, and architectural insights.
*   **Module LLME Tracker (Optional):** A section summarizing current LLME scores for key modules, or a link to `modules_to_score.yaml` (WSP 5).


##### 11.3.2. APS Status Markers


Tasks in the APS Task List should use the following status markers:


*   **[✅]** - Complete
*   **[⚒️]** - In Progress
*   **[💡]** - Planned/Ideation
*   **[⛔]** - Blocked/Issue


##### 11.3.3. APS Update Workflow


*   **Automatic Updates:** The AI assistant is responsible for regularly updating the APS upon:
    *   Task completion (potentially prompting for LLME update confirmation).
    *   The `save` command (see **Appendix E**)
    *   Context saturation thresholds
*   **Manual Updates:** Developers may directly update the APS when:
    *   Initiating new tasks
    *   Updating task status not captured by the AI
    *   Adding project insights from external discussions
    *   Noting observed changes in module LLME.
*   **Synchronization:** The APS should be periodically synchronized with the ModLog and `modules_to_score.yaml` to ensure consistency in LLME scores.


#### 11.4. Semantic Versioning Specification


FoundUps strictly adheres to [**Semantic Versioning 2.0.0**](https://semver.org/) for all official releases.


##### 11.4.1. Version Format


*   **Format:** MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
*   **Examples:**
    *   `0.1.0` (Initial Prototype release)
    *   `0.2.5` (Prototype with bug fixes)
    *   `1.0.0-rc.1` (Release Candidate 1 for MVP)
    *   `1.0.0` (First stable MVP release)


##### 11.4.2. Incrementing Rules


*   **MAJOR:** Increment when making incompatible API changes.
    *   Increasing MAJOR resets MINOR and PATCH to 0.
    *   MAJOR version 0 (0.y.z) is for initial development (PoC, Prototype). Anything may change at any time.
    *   MAJOR version 1+ indicates stability and production readiness (MVP).
    *   **Backward-incompatible changes to the public interface defined via WSP 12 MUST increment the MAJOR version (once > 1.0.0).** This is especially true for modules with high LLME C-digit scores.
*   **MINOR:** Increment when adding functionality in a backward-compatible manner.
    *   Increasing MINOR resets PATCH to 0.
    *   **Backward-compatible additions to the public interface SHOULD increment the MINOR version.**
*   **PATCH:** Increment when making backward-compatible bug fixes.
    *   **Changes to dependencies (WSP 13) that don't affect the module's own interface typically only require a PATCH increment, unless they necessitate interface changes.**


##### 11.4.3. Development Stage Mapping


Version numbers map to development stages as defined in **WSP 9**, which also correlates with expected LLME scores:


*   **Proof-of-Concept (PoC):** 0.0.x (LLME typically 000-111)
*   **Prototype:** 0.1.x - 0.9.x (LLME typically 110-122)
*   **MVP (Production):** 1.0.0+ (LLME typically 112-222)


#### 11.5. Git Tagging & Releases


##### 11.5.1. Version Tags


*   **Format:** `vX.Y.Z[-prerelease]` (e.g., `v0.2.1`, `v1.0.0-beta.2`)
*   **Type:** Always use annotated tags: `git tag -a vX.Y.Z -m "Release vX.Y.Z: Brief description"`
*   **Process:**
    1.  Ensure all tests pass and FMAS checks succeed.
    2.  Update the ModLog with the new version entry (including any relevant LLME updates).
    3.  Create and push the annotated tag.
    4.  Consider creating a corresponding Clean State (**WSP 2**) for significant versions.


##### 11.5.2. Clean State Tags


*   **Format:** `clean-vX` (e.g., `clean-v4`)
*   **Process:** Follow the Clean State creation procedure in **WSP 2**.


##### 11.5.3. GitHub Releases


For official releases, consider creating a GitHub Release:


*   **Title:** Version number and brief description (e.g., `v1.0.0 - Initial MVP Release`)
*   **Description:** Copy relevant content from the ModLog entry.
*   **Attachments:** Consider attaching build artifacts or documentation if applicable.


#### 11.6. Workflows & Integration


##### 11.6.1. Release Workflow


1.  **Preparation:**
    *   Ensure all intended features for the release are complete and merged.
    *   Run full Test Audit (**WSP 6**) to verify test coverage and quality.
    *   Run FMAS (**WSP 4**) to verify structural compliance.
    *   Perform regression comparison (**WSP 8**) against the previous stable version.
    *   Review and confirm LLME scores of key modules are accurate for the release.
2.  **Version Determination:**
    *   Decide on the appropriate version increment based on the nature of changes.
    *   Review development stage (**WSP 9**) to ensure version aligns with maturity and LLME state.
3.  **Documentation:**
    *   Create a new ModLog entry with the version, date, detailed changes, and LLME updates.
    *   Update any version references in code or documentation.
4.  **Release Process:**
    *   Create and push the annotated Git tag.
    *   Consider creating a Clean State snapshot (**WSP 2**).
    *   Create a GitHub Release if appropriate.


##### 11.6.2. Continuous Integration


*   **Automated Builds:** Consider generating build numbers or dev versions for CI builds.
*   **Pre-release Deployment:** Use pre-release versions for testing environments.
*   **Release Verification:** Automate checks that versions in code, ModLog, and tags are aligned.


#### 11.7. Module-Specific Versioning


Individual modules may maintain their own internal version numbers, but these should:


*   **Align with Project Versions:** Generally follow the main project's versioning scheme.
*   **Document in Module:** Include the module's version in its README or a `VERSION` constant.
*   **Record in ModLog:** Reference module-specific versions in the project-wide ModLog. The module's LLME score should also be documented in its README and tracked via `modules_to_score.yaml`.


#### 11.8. Related WSPs


*   **WSP 2 (Clean States):** Defines when to create clean states, which often correspond to version tags.
*   **WSP 4 (FMAS):** Verification required before creating release versions.
*   **WSP 5 (MPS):** Module LLME scores are tracked alongside MPS and influence prioritization.
*   **WSP 6 (Test Audit):** Quality gates required before versioning releases.
*   **WSP 7 (Git Discipline):** Defines Git tagging conventions related to versioning.
*   **WSP 8 (Regression Detection):** Verifies no regressions before versioning.
*   **WSP 9 (Milestone Rules):** Maps development stages and LLME scores to version number ranges.
*   **WSP 10 (ESM Protocol):** Defines emojis used in ModLog entries, including for LLME updates.
*   **WSP 12 (Interface Definition):** Interface changes drive versioning decisions.
*   **WSP 13 (Dependency Management):** Dependency changes are tracked in ModLog.
*   **Appendix G (LLME):** Defines the semantic scoring system tracked by this WSP.


---


### WSP 12: Module Interface Definition & Validation (Previously WSP 11)


**Document Version:** 1.0  
**Date:** [Insert Date]  
**Status:** Active  
**Applies To:** Definition, documentation, and validation of interfaces for all modules intended for reuse or inter-module communication. The criticality and stability requirements for interfaces are influenced by the module's LLME score (Appendix G).


#### 12.1. Purpose


To ensure modules have clearly defined, documented, and validated boundaries (interfaces/APIs/contracts) enabling reliable integration, interoperability ("slot-ability"), and independent development, as required by the 0102 modularization goal. Modules with high LLME "Systemic Importance" (Digit C=2) require exceptionally robust and stable interfaces.


#### 12.2. Scope


This WSP applies to:


* Modules created or refactored during module refactoring (WSP 1) and new module creation.
* Any module exposing functionality or data for consumption by other modules or external systems.
* Standards for interface identification, documentation, and validation.


#### 12.3. Interface Principles


* **Explicitness:** Interfaces must be explicitly defined, not just implied.
* **Minimality:** Expose only necessary functionality/data (Least Privilege).
* **Stability:** Aim for stable interfaces; breaking changes require careful management (WSP 11). Modules with LLME C=2 must prioritize interface stability.
* **Discoverability:** Interfaces should be easily discoverable and understandable.
* **Clarity:** Interface definitions must clearly articulate expectations, especially for modules with high "Local Impact" (LLME B=2) or "Systemic Importance" (LLME C=2).


#### 12.4. Interface Identification (0102 Task)


* **Analysis:** During refactoring planning (WSP 1.4a) or new module design, 0102 analyzes code interactions (function calls, data exchange) to identify potential interface points. The module's target LLME score informs the expected scope and stability of these interfaces.
* **Proposal:** 0102 proposes the public interface (functions, classes, methods, data structures, API endpoints, events, etc.).
* **Confirmation:** User/Developer reviews and confirms the proposed interface, considering LLME implications.


#### 12.5. Interface Definition & Documentation Standard


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
* **Location:** Standard location within module directory (e.g., root, docs/, interface/). Checked by FMAS (WSP 4).


#### 12.6. Interface Validation (Contract Testing)


* **Requirement:** Modules MUST have tests validating adherence to their defined interface (part of WSP 6 Test Audit). The rigor of these tests should correlate with the module's LLME score (especially B and C digits).
* **Methodology (Project Specific):**
  * **Schema Validation:** Validate data structures against schemas (schema.json, Protobuf definitions).
  * **API Testing:** Use tools like requests, curl, Postman (collections), or specific frameworks to test API endpoints against OpenAPI specs.
  * **Mocking/Stubbing:** Use provider/consumer testing tools (e.g., Pact) to verify interactions between modules without full integration.
  * **Static Analysis:** Tools checking function signatures match definitions.
* **Execution:** Contract tests run as part of WSP 6.


#### 12.7. Workflow Integration


* **WSP 1:** Interface proposed during planning, defined/updated during refactoring, considering LLME.
* **WSP 4:** FMAS checks for existence of interface artifacts.
* **WSP 6:** Contract tests executed during Test Audit. Rigor influenced by LLME.
* **WSP 7:** Interface artifacts committed and versioned. Interface changes reflected in commit messages (e.g., feat(mymodule:iface): ..., fix(mymodule:iface): ...).
* **WSP 8:** Interface files included in regression checks.
* **WSP 9:** Stable interface required for MVP transition, especially for high LLME modules.
* **WSP 11:** Interface changes (especially breaking) drive SemVer and ModLog entries. Critical for modules with high LLME C-digit scores.


#### 12.8. AI Agent Role (0102)


* Proposes initial interface based on code analysis and target LLME score.
* Generates skeleton interface documentation/definition files.
* Potentially generates basic contract test stubs, with complexity aligned to LLME.
* Flags potential breaking changes during refactoring, especially for high LLME modules.


---


### WSP 13: Dependency Management & Packaging (Previously WSP 12)


**Document Version:** 1.0  
**Date:** [Insert Date]  
**Status:** Active  
**Applies To:** Identification, declaration, and management of dependencies for all modules. The nature and criticality of dependencies can be informed by the LLME scores (Appendix G) of both the depending and depended-upon modules.


#### 13.1. Purpose


To systematically manage internal and external dependencies for modules, ensuring reproducibility, resolving conflicts, and facilitating packaging for distribution and reuse, supporting the 0102 universal modularization goal. Careful management is crucial when depending on or being depended upon by modules with high LLME "Systemic Importance" (Digit C=2).


#### 13.2. Scope


* Applies during module refactoring (WSP 1) and new module creation.
* Defines standards for dependency identification, declaration, versioning, and basic packaging considerations.


#### 13.3. Dependency Principles


* **Explicitness:** All dependencies MUST be explicitly declared.
* **Isolation:** Aim for modules with minimal, well-defined dependencies. Modules striving for high LLME "Emergence" (Digit A=2) might need carefully curated dependencies.
* **Versioning:** Use explicit version constraints for dependencies.
* **Auditability:** Dependency manifests must be version-controlled.
* **Stability:** Prioritize stable versions for dependencies, especially when interacting with modules with high LLME C-digits.


#### 13.4. Dependency Identification (0102 Task)


* **Analysis:** During refactoring planning (WSP 1.4a) or new module design, 0102 analyzes code (imports, library calls, build files) to identify dependencies. The LLME scores of potential dependencies can be a factor in selection (e.g., preferring stable, high-LLME foundational modules).
* **Classification:** 0102 classifies dependencies as:
  * **Internal:** Other modules within the FoundUps project (note their LLME scores).
  * **External:** Third-party libraries/packages.
  * **System:** OS-level tools or libraries (e.g., ffmpeg, imagemagick).
* **Proposal:** 0102 proposes a list of dependencies with suggested versions.
* **Confirmation:** User/Developer reviews and confirms the dependency list, considering LLME implications.


#### 13.5. Dependency Declaration Standard


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
* **Location:** Standard location within module directory (e.g., root). Checked by FMAS (WSP 4).


#### 13.6. Versioning & Conflict Resolution


* **Pinning:** External dependencies SHOULD be pinned to specific versions (==X.Y.Z) in module manifests for maximum reproducibility during module development and testing.
* **Range Strategy (Project Level):** The project-level dependency management (combining modules) MAY use version ranges (~=, >=) but requires a robust conflict resolution strategy (e.g., using dependency resolution tools like pip, npm, maven, poetry). This strategy must be defined in foundups_global_rules.md.
* **Internal Dependencies:** Internal dependencies MAY reference specific commit hashes or version tags (clean-vX, vX.Y.Z) for tight coupling if needed, or rely on the project-level build process to resolve local paths. Dependencies on internal modules with high LLME scores (especially C=2) should be treated with similar rigor to external dependencies, preferring tagged versions.


#### 13.7. Packaging Considerations (Informational)


* While full packaging is beyond this WSP, the defined structure (src/, tests/, interface/dependency manifests) facilitates packaging.
* The chosen packaging method (e.g., creating a wheel/jar/npm package, Docker container) should leverage the artifacts mandated by WSP 1, 12, and 13. Packaging methods should be defined at the project level.


#### 13.8. Workflow Integration


* **WSP 1:** Dependencies identified during planning, declared during refactoring, considering LLME.
* **WSP 4:** FMAS checks for existence and basic format of dependency manifests.
* **WSP 7:** Dependency manifests committed and versioned. Dependency changes reflected in commit messages (e.g., chore(mymodule:deps): update library X).
* **WSP 8:** Dependency manifests included in regression checks.
* **WSP 9:** Declared dependencies required for MVP transition.
* **WSP 11:** Significant dependency updates noted in ModLog. Changes to dependencies that are themselves high-LLME modules should be highlighted.


#### 13.9. AI Agent Role (0102)


* Identifies dependencies via code analysis.
* Proposes dependency list and versions, potentially considering LLME of internal dependencies.
* Formats entries for standard manifest files.
* Flags potential version conflicts based on project rules or known incompatibilities.


---


### WSP 14: Test Creation & Management Procedures (Previously WSP 13)


**Document Version:** 1.0  
**Date:** [Insert Date]  
**Status:** Active  
**Applies To:** Creation, organization, and management of test suites within module test directories. The rigor and scope of testing should be influenced by the module's current and target LLME score (Appendix G).


#### 14.1. Purpose


To establish standardized procedures for creating, organizing, and maintaining test suites that avoid duplication, follow WSP guidelines, and ensure comprehensive coverage of module functionality. Modules with higher LLME scores (especially B and C digits) require more comprehensive and robust testing.


#### 14.2. Scope


This WSP applies to:
* Creation of new test files within module test directories
* Extension of existing test suites
* Management of test documentation and coverage
* Integration with WSP compliance requirements


#### 14.3. Test Creation Workflow


##### 14.3.1. Pre-Creation Analysis (MANDATORY)


Before creating or modifying tests:


1. **Review Module's LLME Score:** Understand the module's current state, local impact, and systemic importance (WSP 5, Appendix G). This informs the required depth and breadth of testing.
2. **Read Existing Tests README:** Examine `modules/<module_name>/tests/README.md` to understand:
   - Current test file structure and purpose
   - Existing test coverage areas
   - Test execution procedures
3. **Identify Coverage Gaps:** Analyze existing test files to determine:
   - What functionality is already tested
   - What areas need additional coverage, prioritizing based on LLME characteristics (e.g., core functions for C=2 modules, interaction points for B=2 modules).
   - Whether new tests should extend existing files or create new ones
4. **Check for Duplicate Functionality:** Search existing tests for similar patterns:
   ```bash
   grep -r "circuit.*breaker\|breaker.*circuit" modules/<module>/tests/
   grep -r "credential.*rotation\|rotation.*credential" modules/<module>/tests/
   ```


##### 14.3.2. Test File Creation Guidelines


**File Naming Convention:**
- `test_<specific_functionality>.py` (e.g., `test_circuit_breaker.py`)
- Avoid generic names like `test_module.py` if specific functionality tests exist
- Use descriptive names that clearly indicate the test focus


**Test Structure Requirements:**
- Follow established patterns from existing test files in the module
- Include comprehensive docstrings explaining test purpose
- Organize tests into logical test classes
- Include integration tests where appropriate, especially for modules with LLME B>=1 or C>=1.


**WSP Compliance Headers:**
```python
"""
WSP: [Test Module Name]
======================


Tests for [specific functionality] in the [Module Name] module.
Module LLME: [Current ABC] - Target LLME: [Target ABC]
[Brief description of what this test module covers, considering LLME aspects]


WSP Compliance:
- Tests placed in correct module location: modules/<module>/tests/
- Follows established test patterns from existing test files
- Tests [functionality] in isolation and integration
- Test scope and rigor aligned with module LLME.
- [Additional compliance notes]
"""
```


##### 14.3.3. Test Documentation Requirements


**README.md Updates (MANDATORY):**
After creating or significantly modifying tests, update `modules/<module>/tests/README.md`:


1. Add new test file to the test files table:
   ```markdown
   | test_new_functionality.py | Description of what this test file covers |
   ```


2. Update test coverage section if applicable, noting how it supports the module's LLME characteristics.
3. Add any new running instructions for specific test files
4. Update "Recent Updates" section with brief description


**Test Coverage Documentation:**
- Document what functionality the tests cover
- Note any integration points with other modules
- Specify any special setup or teardown requirements


#### 14.4. Existing Test Extension Guidelines


##### 14.4.1. When to Extend vs Create New


**Extend Existing Test Files When:**
- The new tests cover the same core functionality as existing tests
- Tests logically belong in the same test class
- The existing file has fewer than 500 lines and good organization


**Create New Test Files When:**
- Testing a distinct, separate functionality (e.g., circuit breaker vs stream resolution)
- Existing files are large and would benefit from separation
- Tests require significantly different setup/teardown procedures
- Testing aspects related to a specific LLME characteristic not well covered by existing files.


##### 14.4.2. Extension Procedures


1. **Read Existing Test File:** Understand current test patterns and structure
2. **Follow Existing Patterns:** Use similar naming conventions, setup methods, and assertion styles
3. **Add to Appropriate Test Class:** Extend existing test classes where logical
4. **Update Docstrings:** Ensure class and method docstrings reflect new functionality


#### 14.5. Test Quality Standards


##### 14.5.1. Test Coverage Requirements


- **Functional Coverage:** Test primary functionality paths. For high LLME modules (B=2 or C=2), this must be exhaustive.
- **Error Handling:** Test error conditions and exception handling.
- **Integration Points:** Test interactions with other modules/components, especially if LLME B>=1.
- **Edge Cases:** Test boundary conditions and unusual inputs. More rigorous for high LLME.
- **Emergence Testing (for LLME A=2):** If applicable, tests that verify autonomous or reflexive behaviors.


##### 14.5.2. Test Independence


- **Isolation:** Tests should not depend on execution order
- **Cleanup:** Proper setup and teardown to avoid test interference
- **Mocking:** Use appropriate mocking for external dependencies


##### 14.5.3. Test Documentation


- **Clear Test Names:** Test method names should clearly describe what is being tested
- **Comprehensive Docstrings:** Explain test purpose, setup, and expected outcomes
- **Assertion Messages:** Include meaningful messages in assertions where helpful


#### 14.6. Integration with Other WSPs


##### 14.6.1. WSP 1 (Module Refactoring)
- Tests are created/moved during module refactoring. Test scope considers target LLME.
- Test README.md is created as part of refactoring process.


##### 14.6.2. WSP 4 (FMAS)
- FMAS checks for presence of tests/README.md
- Test organization compliance verified by FMAS


##### 14.6.3. WSP 6 (Test Audit)
- Created tests must meet coverage requirements, influenced by LLME.
- Test quality standards enforced during audit.


#### 14.7. AI Agent Responsibilities


When tasked with test creation:


1. **ALWAYS** review the module's current and target LLME score.
2. **ALWAYS** read existing tests/README.md first.
3. **ALWAYS** analyze existing test files for similar functionality.
4. **PRIORITIZE** extending existing tests over creating new ones when logical.
5. **ADJUST** test scope and rigor based on the module's LLME score.
6. **UPDATE** tests/README.md after creating or modifying tests.
7. **FOLLOW** established patterns and naming conventions.
8. **VERIFY** tests run successfully before completion.


#### 14.8. Example Test Creation Process


**Scenario:** Adding circuit breaker tests to stream resolver module (LLME target: 122 - Active, Contributive, Essential)


1. **Pre-Analysis:**
   ```bash
   # Review LLME for stream_resolver (assume it's 111, target 122)
   # Check existing tests
   ls modules/platform_integration/stream_resolver/tests/ # Note: Path adjusted from original example
   cat modules/platform_integration/stream_resolver/tests/README.md
   
   # Search for existing circuit breaker tests
   grep -r "circuit" modules/platform_integration/stream_resolver/tests/
   ```


2. **Decision:** No existing circuit breaker tests found → Create new test file. Given target LLME 122, these tests need to be thorough, covering various states of the breaker and its impact on the module's contribution.


3. **Creation:** Create `test_circuit_breaker.py` with WSP-compliant structure, including LLME in header.


4. **Documentation:** Update `tests/README.md` to include new test file and how it supports the module's resilience (contributing to LLME B=2 and C=2).


5. **Verification:** Run tests to ensure they pass.


This process ensures no duplication and maintains WSP compliance, with test rigor appropriate for the module's semantic importance.


---


## III. Appendices


### Appendix A: WSP Prompt Template


*(Template defining Task, Scope, Constraints, Baseline, Validation for invoking WSP actions)*
```markdown
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
```


### Appendix B: Roadmap & ModLog Format Templates


*(These templates define the standard structure for the project roadmap and ModLog entries found in `docs/ModLog.md`.)*


#### Roadmap Structure Template


```markdown
# FoundUps Agent Modular Change Log


This log tracks module changes, updates, and versioning for FoundUps Agent under the Windsurf modular development model. LLME (Appendix G) scores are tracked via WSP 5 and WSP 11.


## FoundUps-Agent Roadmap


### Status Ledger
- ✅ Complete
- 🔄 In Progress
- ⏳ Planned
- ⚠️ Deprecated
- 🧬 LLME Target: [ABC] (Can be used for roadmap items)


### ✅ Proof of Concept (0.0.x) - Target LLME: ~000-111
- [ ] [Task 1]
- [ ] [Task 2]


### 🔄 +Prototype (0.1.x - 0.9.x) - Target LLME: ~110-122
- [ ] [Feature 1]
- [ ] [Feature 2]


### 🔄 [High Priority System Name] - Current LLME: [XYZ], Target LLME: [ABC]
- [ ] [Task 1]
- [ ] [Task 2]


### 🔄 [Medium Priority System Name]
- [ ] [Task 1]
- [ ] [Task 2]


### 🔄 [Lower Priority System Name]
- [ ] [Task 1]
- [ ] [Task 2]


### ⏳ Minimum Viable Product (1.0.x+) - Target LLME: ~112-222
- [ ] [MVP Feature 1]
- [ ] [MVP Feature 2]


#### TODO List *Use `[+todo]` or `[+WSP]` commit convention prefix or add manually here.*
**/[Task Name]** - @[Assignee/Team] - priority: [PriorityScore] (MPS from WSP 5) - LLME Target: [ABC]
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


#### ModLog Entry Format Template (as per WSP 11)


```markdown
====================================================================
## MODLOG - [+UPDATES]:
- Version: [X.Y.Z]
- Date: [YYYY-MM-DD]
- Git Tag: [Associated tag, e.g., vX.Y.Z or clean-vX]
- Description: [Brief description of changes in this version/log entry]
- Notes: [Additional context or considerations]
- Module LLME Updates (If applicable):
  - [module_name] - LLME: [Old ABC] -> [New ABC] ([Rationale for change])
- Features/Fixes/Changes:
  - [ESM Emoji] [Module: Component] - Description of change 1 (Issue #123)
  - [ESM Emoji] [Module: Component] - Description of change 2
  - ...
====================================================================
```


#### Version Guide Template


```markdown
====================================================================
## VERSION GUIDE
### Development Phases (Correlated with WSP 9 & LLME Scores - Appendix G):
- #### POC (0.0.x): Initial development and proof of concept
  - Expected LLME Range: 000-111
  - 0.0.1: First working version
  - 0.0.2-0.0.9: POC improvements and fixes
- #### Prototype (0.1.x - 0.9.x): Feature development and testing
  - Expected LLME Range: 110-122
  - 0.1.x: Basic feature set
  - 0.2.x-0.9.x: Feature expansion and refinement
- #### MVP (1.0.x+): Production-ready releases
  - Expected LLME Range: 112-222
  - 1.0.0: First stable release
  - 1.x.x: Production updates and improvements
====================================================================
```

*(Appendices C, D, E, F are mentioned in the original text but their content was not provided. They are retained as placeholders if referenced.)*

### Appendix C: Standard Commands (Placeholder)
*(Details of standard commands like k, go, save, init, fix, etc. would be listed here.)*

### Appendix D: Memory & Rule Hierarchy Overview (Placeholder)
*(Detailed explanation of AI Memory, User Project Rules, and Global Rules hierarchy would be here.)*

### Appendix E: `save` Command Details (Placeholder)
*(Detailed explanation of the `save` command functionality would be here.)*

### Appendix F: `.foundups_project_rules` Template (Placeholder)
*(The template for project-specific rules would be provided here.)*

### Appendix G: LLME Semantic Triplet Rating System

Each module, agent state, or system interaction is rated using a three-digit code: A-B-C.
Digits must not regress—each digit must be equal to or greater than the one before (A ≤ B ≤ C).

**1st Digit "A" — Present State (Execution Layer)**
*   **0 = dormant, scaffold-only, not executing:** The module exists structurally but is not active or performing its functions. It might be a placeholder, disabled, or awaiting dependencies/activation.
*   **1 = active, functional:** The module is executing its defined functions and operating as expected under normal conditions. It responds to inputs and produces outputs according to its design.
*   **2 = emergent, reflexive, autonomous:** The module exhibits behaviors beyond its explicitly programmed functional responses. It might adapt to new situations, self-optimize, learn from interactions, or operate with a degree of autonomy without direct, continuous instruction for every action.

**2nd Digit "B" — Local/Module Impact (Contextual Layer)**
*   **0 = passive, no contribution:** The module, even if active, does not significantly interact with or contribute data/state/functionality to other modules within its immediate ecosystem or feature group. It's isolated in its impact.
*   **1 = tied to nearby logic, contextual relevance:** The module interacts with and has relevance to other closely related modules or components. It exchanges data, triggers, or is triggered by local peers, fulfilling a role within a specific feature set or sub-domain.
*   **2 = actively feeding/contributing to the module ecosystem:** The module is a significant contributor to its broader local ecosystem. It provides essential data, services, or state changes that many other modules within its Enterprise Domain or multiple Feature Groups rely on or benefit from. Its outputs are foundational or highly leveraged.

**3rd Digit "C" — Systemic Importance (Ecosystem Layer)**
*   **0 = irrelevant, no downstream effect:** The module's functionality, however complex or active, has no significant bearing on the core objectives or overall functionality of the FoundUps system. Its absence would not critically impair the larger system.
*   **1 = conditionally relevant in the wider system:** The module plays a role in specific system-wide scenarios or for particular overarching features but is not universally critical. Its importance is contextual to certain operational modes or user journeys.
*   **2 = core or essential to Foundup's systemic function:** The module is fundamental to the core purpose or critical operations of the entire FoundUps system. Its failure or absence would lead to significant degradation or failure of key system-wide capabilities. It underpins one or more primary value propositions of the platform.

**Examples:**
-   `000` = non-functional, irrelevant, inert
-   `011` = running (but actually `0` implies not running, so this should be `111` if running & relevant), minor module value, limited relevance. (If `011` means scaffold-only, relevant, conditionally relevant systemically)
-   `111` = functional, relevant locally, conditionally relevant systemically
-   `122` = functional, deeply contributive locally, system-critical
-   `222` = emergent, recursive, universally entangled (highly contributive and essential)

This LLME score is non-numeric. It is a **semantic fingerprint**.

**Usage:**
-   As filter in module selection (WSP 5).
-   As a modifier for MPS weighting in WSP (WSP 5).
-   As a persistent marker in logs (WSP 11) and updates (WSP 9).
-   To guide architectural decisions (WSP 3) and interface design (WSP 12).
-   To inform testing rigor (WSP 6, WSP 14)
