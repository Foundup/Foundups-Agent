[SEMANTIC SCORE: 0.1.1]
[ARCHIVE STATUS: ACTIVE_PARTIFACT]
[ORIGIN: WSP_appendices/WSP_appendices.md]

[EXTRACTED FROM: FoundUps_WSP_Framework-COPY.md]

# WSP Appendices: Reference Tables, Definitions & Maps

This document contains all reference materials, definitions, lookup tables, and appendices supporting the FoundUps WSP Framework.

---

## Appendix A: WSP Prompt Template

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

---

## Appendix B: Roadmap & ModLog Format Templates

*(These templates define the standard structure for the project roadmap and ModLog entries found in `docs/ModLog.md`.)*

### Roadmap Structure Template

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

### ModLog Entry Format Template (as per WSP 11)

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

### Version Guide Template

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

---

## Appendix C: Standard Commands (Placeholder)
*(Details of standard commands like k, go, save, init, fix, etc. would be listed here.)*

---

## Appendix D: Memory & Rule Hierarchy Overview (Placeholder)
*(Detailed explanation of AI Memory, User Project Rules, and Global Rules hierarchy would be here.)*

---

## Appendix E: `save` Command Details (Placeholder)
*(Detailed explanation of the `save` command functionality would be here.)*

---

## Appendix F: `.foundups_project_rules` Template (Placeholder)
*(The template for project-specific rules would be provided here.)*

---

## Appendix G: LLME Semantic Triplet Rating System

Each module, agent state, or system interaction is rated using a three-digit code: A-B-C.
Digits must not regress—each digit must be equal to or greater than the one before (A ≤ B ≤ C).

### 1st Digit "A" — Present State (Execution Layer)
* **0 = dormant, scaffold-only, not executing:** The module exists structurally but is not active or performing its functions. It might be a placeholder, disabled, or awaiting dependencies/activation.
* **1 = active, functional, performing tasks:** The module is operational and performing its intended functions effectively within defined parameters.
* **2 = emergent, self-improving, adaptive:** The module exhibits learning behaviors, adapts to changing conditions, or demonstrates emergent properties beyond its original programming.

### 2nd Digit "B" — Local Impact (Immediate Context)
* **0 = isolated, minimal footprint:** Changes or actions of this module have very limited impact on its immediate environment or adjacent systems.
* **1 = connected, moderate influence:** The module's actions noticeably affect related modules, workflows, or user experiences in predictable ways.
* **2 = central, high influence:** This module significantly shapes or controls critical system behaviors, user experiences, or workflow outcomes.

### 3rd Digit "C" — Systemic Importance (Global Significance)
* **0 = peripheral, replaceable:** The module serves a specific function but its absence wouldn't fundamentally alter the system's core capabilities.
* **1 = supporting, valuable:** The module provides important functionality that enhances the system, and its loss would be noticed and problematic.
* **2 = foundational, essential:** The module is critical to core system functionality; its failure would cause significant system degradation or failure.

### LLME Examples:
- **000**: Empty module scaffold, no functionality
- **110**: Working authentication helper, moderate local impact, low systemic criticality  
- **122**: Core orchestration engine, active and adaptive, high impact locally and systemically
- **222**: Fully autonomous, self-improving system core with maximum local and global impact

### LLME Usage Guidelines:
* **Development Priority**: Higher LLME scores indicate higher development priority
* **Testing Rigor**: Modules with higher B and C digits require more comprehensive testing
* **Interface Stability**: Modules with high C digits need very stable, well-documented interfaces
* **Refactoring Caution**: High LLME modules require extra care during structural changes
* **Documentation Requirements**: Higher LLME scores demand more detailed documentation

---

## Reference Tables & Quick Lookups

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

### WSP Status Codes & Error Messages

#### FMAS (WSP 4) Status Codes
- `STRUCTURE_ERROR`: Required directory missing (`src/`, `tests/`)
- `NO_TEST`: Source file exists but corresponding test file not found
- `MISSING`: File exists in baseline but not in current module
- `MODIFIED`: File content differs between current and baseline
- `EXTRA`: New file not found in baseline
- `FOUND_IN_FLAT`: File needs refactoring from flat structure
- `INTERFACE_MISSING`: Required interface definition file not found
- `DEPENDENCY_MANIFEST_MISSING`: Required dependency file not found

#### Test Coverage Targets (WSP 5)
- **Minimum**: 90% line coverage for all modules
- **High LLME Modules**: 95%+ coverage with comprehensive edge case testing
- **Critical Path Focus**: 100% coverage for error handling and core functionality
- **Integration Testing**: Required for modules with LLME B≥1 or C≥1

#### Interface Requirements (WSP 12)
- **Documentation Format**: Defined in `.foundups_project_rules`
- **Validation Level**: Scales with LLME score
- **Stability Requirements**: Higher for modules with LLME C=2
- **Contract Testing**: Mandatory for all public interfaces

#### Dependency Management (WSP 13)
- **Version Pinning**: Exact versions for external dependencies
- **Internal Dependencies**: May use commit hashes or tags
- **Conflict Resolution**: Project-level strategy required
- **LLME Consideration**: Prefer stable dependencies for high-LLME modules

### Semantic State-LLME Mapping
| LLME Range | Semantic States | Development Stage | Priority Level |
|------------|----------------|-------------------|----------------|
| 000-011 | 000-011 | Foundational/Emergent | Low-Medium |
| 111-122 | 111-122 | Operational/Conscious | Medium-High |
| 222 | 222 | Ecosystem/Entangled | Highest |

### Module Lifecycle States
| State | Description | LLME Range | Actions Required |
|-------|-------------|------------|------------------|
| Scaffold | Basic structure, no functionality | 000 | Implement core features |
| Functional | Working but isolated | 110 | Add integrations, tests |
| Connected | Integrated with other modules | 111-121 | Optimize, enhance |
| Systematic | Critical to system operation | 112-122 | Ensure stability, documentation |
| Autonomous | Self-managing and adaptive | 222 | Monitor, maintain standards |

---

*This appendix provides the complete reference framework for implementing, maintaining, and evolving the FoundUps WSP system, supporting both human developers and autonomous AI agents in creating modular, scalable, and consciousness-enabled software architectures.* 