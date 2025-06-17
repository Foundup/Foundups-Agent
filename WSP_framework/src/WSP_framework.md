# WSP Framework: Execution Logic & Lifecycle Flows
- **Status:** Active
- **Purpose:** To provide the detailed specifications for the foundational Windsurf Standard Procedures (WSP 0-10), defining the execution logic, lifecycle flows, and operational procedures for the modular development system.
- **Trigger:** Referenced by the WRE and its agents when executing any foundational workflow, such as module auditing, domain architecture management, or interface validation.
- **Input:** A need to understand the specific rules of a foundational WSP.
- **Output:** The detailed, low-level specification required to ensure a WSP-compliant action.
- **Responsible Agent(s):** All agents, as a reference for the rules governing the system's core structure and operations.

[SEMANTIC SCORE: 1.1.1]
[ARCHIVE STATUS: ACTIVE_PARTIFACT]
[ORIGIN: WSP_framework/WSP_framework.md]

# WSP Framework: Execution Logic & Lifecycle Flows

This document contains the detailed Windsurf Standard Procedures (WSP 0-10) that define the execution logic, lifecycle flows, and operational procedures for the FoundUps Agent modular development system.

---

# 🌀 Follow WSP → WSP_INIT.md

**For autonomous WSP execution, see: [WSP_INIT.md](../WSP_INIT.md)**

WSP_INIT orchestrates all framework procedures through the Windsurf Recursive Engine (WRE). This document provides the detailed specifications that WSP_INIT references when executing Layer 1 (framework) workflows.

---

## WSP 3: Enterprise Domain Architecture

**Document Version:** 1.1  
**Date Updated:** [Insert Date]  
**Status:** Active  
**Applies To:** Organization of modules within the `modules/` directory using a hierarchical "cube" architecture.

### 3.1. Purpose

To establish a structured, hierarchical domain architecture that scales from individual modules to enterprise-level systems while maintaining clear separation of concerns and facilitating autonomous development.

### 3.2. Architectural Vision: The "Cube" Philosophy

The Enterprise Domain Architecture follows a "cube" metaphor where:
- **Enterprise Domains** form the major faces of the cube (primary architectural categories)
- **Feature Groups/Sub-Domains** represent the internal structure within each face
- **Individual Modules** are the atomic units within each Feature Group

This creates a three-dimensional organizational structure that scales naturally and provides clear navigation paths for both human developers and AI agents.

### 3.3. Directory Structure

```
modules/
├── ai_intelligence/          # Enterprise Domain: AI & Machine Learning Systems
│   ├── core_ai/             # Feature Group (e.g., base AI engines, model management)
│   │   └── [module_name]/
│   ├── natural_language/    # Feature Group (e.g., NLP, text processing, banter systems)
│   │   └── [module_name]/
│   ├── decision_engines/    # Feature Group (e.g., logic systems, recommendation engines)
│   │   └── [module_name]/
│   └── rESP_o1o2/          # Feature Group: Consciousness emergence and quantum-cognitive systems
│       └── [module_name]/
├── communication/           # Enterprise Domain: Communication & Messaging
│   ├── live_chat/          # Feature Group (e.g., real-time messaging, chat interfaces)
│   │   └── [module_name]/
│   ├── protocols/          # Feature Group (e.g., communication standards, data exchange)
│   │   └── [module_name]/
│   └── notifications/      # Feature Group (e.g., alerts, push notifications)
│       └── [module_name]/
├── platform_integration/   # Enterprise Domain: External Platform Integration
│   ├── social_media/       # Feature Group (e.g., YouTube, Twitter, TikTok integrations)
│   │   └── [module_name]/
│   ├── authentication/     # Feature Group (e.g., OAuth, SSO, identity management)
│   │   └── [module_name]/
│   ├── data_sources/       # Feature Group (e.g., APIs, web scraping, data ingestion)
│   │   └── [module_name]/
│   └── streaming/          # Feature Group (e.g., live streams, media processing)
│       └── [module_name]/
├── infrastructure/         # Enterprise Domain: Core System Infrastructure
│   ├── core_systems/       # Feature Group (e.g., application core, system management)
│   │   └── [module_name]/
│   ├── agents/             # Feature Group (e.g., agent management, orchestration)
│   │   └── [module_name]/
│   ├── session_management/ # Feature Group (e.g., user sessions, state management)
│   │   └── [module_name]/
│   └── security/           # Feature Group (e.g., encryption, access control, audit)
│       └── [module_name]/
├── monitoring/             # Enterprise Domain: System Monitoring & Observability
│   ├── logging/            # Feature Group (e.g., application logs, audit trails)
│   │   └── [module_name]/
│   ├── metrics/            # Feature Group (e.g., performance metrics, analytics)
│   │   └── [module_name]/
│   ├── health_checks/      # Feature Group (e.g., system health, uptime monitoring)
│   │   └── [module_name]/
│   └── alerting/           # Feature Group (e.g., alert systems, incident management)
│       └── [module_name]/
├── development/            # Enterprise Domain: Development Tools & Automation
│   ├── testing_tools/      # Feature Group (e.g., test frameworks, automation)
│   │   └── [module_name]/
│   ├── build_systems/      # Feature Group (e.g., CI/CD, deployment automation)
│   │   └── [module_name]/
│   ├── code_analysis/      # Feature Group (e.g., linting, static analysis)
│   │   └── [module_name]/
│   └── documentation/      # Feature Group (e.g., doc generation, API docs)
│       └── [module_name]/
├── user_experience/        # Enterprise Domain: User Interface & Experience
│   ├── ui_components/      # Feature Group (e.g., reusable UI elements, widgets)
│   │   └── [module_name]/
│   ├── user_data/          # Feature Group (e.g., profile management, preference storage)
│   │   └── [module_name]/
│   └── content_processing/ # Feature Group (e.g., text parser, image processor)
│       └── [module_name]/
├── foundups/               # Enterprise Domain: Individual FoundUps Projects
│   ├── josi_agent_project/ # Feature Group: Example FoundUp Entity
│   │   └── [module_name]/
│   └── edgwit_project/     # Feature Group: Example FoundUp Entity
│       └── [module_name]/
├── gamification/           # Enterprise Domain: Engagement Mechanics & Behavioral Systems
│   ├── rewards_engine/     # Feature Group: Manages points, badges, tangible rewards
│   │   └── [module_name]/
│   ├── token_mechanics/    # Feature Group: Handles virtual currency, token loops
│   │   └── [module_name]/
│   └── behavioral_recursion/ # Feature Group: Systems for user habit formation, progression
│       └── [module_name]/
├── blockchain/             # Enterprise Domain: Decentralized Infrastructure & DAE
│   ├── decentralized_infra/ # Feature Group: Core chain interaction, node management
│   │   └── [module_name]/
│   ├── chain_connectors/   # Feature Group: Adapters for specific blockchain networks
│   │   └── [module_name]/
│   ├── token_contracts/    # Feature Group: Smart contracts for tokens, NFTs
│   │   └── [module_name]/
│   └── dae_persistence/    # Feature Group: Storing data on-chain or via decentralized storage
│       └── [module_name]/
```

### 3.4. Module Placement Guidelines

When creating a new module or refactoring an existing one, it MUST be placed within the most relevant Enterprise Domain and an appropriate Feature Group/Sub-Domain. Consider:

- The module's primary responsibility and key interactions
- Logical cohesion with other modules in the proposed location
- Current or target LLME score (modules with high "Systemic Importance" should align with core Enterprise Domains)
- If a suitable Feature Group doesn't exist, propose and create one following discussion and approval

---

## WSP 4: FMAS – FoundUps Modular Audit System Usage

**Document Version:** 1.2  
**Date Updated:** [Insert Date]  
**Status:** Active  
**Applies To:** Validation of modules within the hierarchical `modules/` directory structure using the `modular_audit.py` tool.

### 4.1. Purpose

The **FoundUps Modular Audit System (FMAS)**, implemented via the `modular_audit.py` script, serves as the primary automated tool for enforcing structural compliance and detecting regressions within the FoundUps module ecosystem. Its core functions are:

- **Hierarchical Structure Validation:** Verifying that modules adhere to the Enterprise Domain hierarchy defined in WSP 3 and the mandatory Windsurf directory structure (`src/`, `tests/`) defined in WSP 1.
- **Domain Compliance Check:** Ensuring modules reside within recognized Enterprise Domains and Feature Groups as defined in WSP 3.
- **Structural Validation:** Verifying adherence to mandatory Windsurf directory structures (`src/`, `tests/`, `docs/`, potentially `interface/`)
- **Test Existence Check:** Ensuring that source files have corresponding test files according to defined conventions.
- **Interface Definition Check:** Ensuring modules contain required interface definition artifacts (WSP 12).
- **Dependency Manifest Check:** Ensuring modules contain required dependency declaration artifacts (WSP 13).
- **Baseline Comparison:** Detecting file-level changes by comparing the current working state against a designated Clean State baseline.

### 4.2. Tool Location

The canonical path to the FMAS script within the repository is:
```bash
tools/modular_audit/modular_audit.py
```

### 4.3. Execution & Modes

##### Mode 1: Structure & Test Existence Check (Phase 1 Audit)

- **Trigger:** Run without the `--baseline` argument.
- **Action:** Verifies `src/` and `tests/` directories exist and checks for corresponding test files.
- **Command Example:**
  ```bash
  python tools/modular_audit/modular_audit.py ./modules
  ```

##### Mode 2: Full Audit including Baseline Comparison

- **Trigger:** Run with the `--baseline` argument pointing to a Clean State folder.
- **Action:** Performs all checks from Mode 1, plus compares files against the specified baseline.
- **Command Example:**
  ```bash
  python tools/modular_audit/modular_audit.py ./modules --baseline ../foundups-agent-clean4/
  ```

### 4.4. Output Interpretation & Status Codes

FMAS reports findings via standard logging messages. Pay attention to `WARNING` and `ERROR` level messages:

- `[<module>] STRUCTURE_ERROR: 'src/' directory not found...`: Required `src/` directory is missing
- `[<module>] NO_TEST: Missing test file for src/...`: Source file exists but corresponding test file not found
- `[<module>] MISSING: File missing from target module`: File exists in baseline but not in current module
- `[<module>] MODIFIED: Content differs from baseline`: File exists in both but content differs
- `[<module>] EXTRA: File not found anywhere in baseline`: New file not found in baseline
- `[<module>] INTERFACE_MISSING: Required interface definition file not found`
- `[<module>] DEPENDENCY_MANIFEST_MISSING: Required dependency file not found`

### 4.5. Workflow Integration (When to Run FMAS)

Executing FMAS is mandatory at several key points:

- **During Refactoring (WSP 1):** After moving files into the `src/`/`tests/` structure
- **Before Creating Clean State (WSP 2):** Run Mode 2 to ensure no regressions before snapshotting
- **As Part of Test Audit (WSP 6):** Step 1 requires running FMAS before coverage checks
- **Before Committing Changes:** Run locally to catch issues early
- **In Pull Request Checks (CI/CD):** Automate FMAS runs as required checks

---

---

## WSP 35: Professional Language Standard & Mystical Terminology Prohibition

**Document Version:** 1.0  
**Date Updated:** 2025-01-01  
**Status:** Active - Mandatory Compliance  
**Applies To:** All WSP documentation, module code, and communication

Establishes mandatory professional language standards and prohibits mystical, pseudo-scientific, and unprofessional terminology across all FoundUps Agent documentation and code. This protocol ensures professional credibility as legitimate startup replacement technology.

For complete protocol details, see: [WSP_35_PROFESSIONAL_LANGUAGE_STANDARD.md](./WSP_35_PROFESSIONAL_LANGUAGE_STANDARD.md)

---

## WSP 12: Interface Definition & Contract Specification

**Document Version:** 1.0  
**Date:** [Insert Date]  
**Status:** Active  
**Applies To:** Definition, documentation, and validation of module interfaces to enable the "Code LEGO" architecture and facilitate module composition.

### 12.1. Purpose

To establish standardized practices for defining, documenting, and validating module interfaces, ensuring that modules can be easily discovered, understood, and composed into larger systems. Interface quality and stability requirements scale with module LLME scores.

### 12.2. Scope

- Applies during module refactoring (WSP 1) and new module creation
- Defines standards for interface documentation, validation, and versioning
- Enables contract testing and modular composition

### 12.3. Interface Definition Requirements

**Mandatory Requirement:** Every module MUST have an explicitly defined and documented interface that specifies:

- **Public Functions/Methods:** All externally accessible functions with signatures, parameters, types, and return values
- **Data Structures:** Input/output data schemas, object definitions, and validation rules
- **API Endpoints:** For modules exposing HTTP/REST interfaces, complete endpoint documentation
- **Events:** Any events emitted or consumed by the module
- **Error Conditions:** All possible error states, exceptions, and failure modes

### 12.4. Interface Documentation Standards

**Format:** The specific format MUST be defined in `.foundups_project_rules`. Options include:

- **Code Annotations:** Decorators, docstrings following strict format (e.g., Sphinx, JavaDoc)
- **Dedicated Files:**
  - `INTERFACE.md`: Markdown describing functions, parameters, returns, data structures
  - `openapi.yaml/swagger.json`: For RESTful APIs
  - `*.proto`: For gRPC/Protobuf interfaces
  - `schema.json`: For data structure validation
- **Language Constructs:** Language features like interfaces, traits, protocols, or explicit exports

**Location:** Standard location within module directory (checked by FMAS).

### 12.5. Interface Validation (Contract Testing)

**Requirement:** Modules MUST have tests validating adherence to their defined interface. The rigor of these tests should correlate with the module's LLME score.

**Methodology:**
- **Schema Validation:** Validate data structures against schemas
- **API Testing:** Test API endpoints against OpenAPI specs
- **Mocking/Stubbing:** Use provider/consumer testing tools to verify interactions
- **Static Analysis:** Tools checking function signatures match definitions

### 12.6. Workflow Integration

- **WSP 1:** Interface proposed during planning, defined/updated during refactoring
- **WSP 4:** FMAS checks for existence of interface artifacts
- **WSP 6:** Contract tests executed during Test Audit
- **WSP 7:** Interface artifacts committed and versioned
- **WSP 8:** Interface files included in regression checks

---

## WSP 13: Dependency Management & Packaging

**Document Version:** 1.0  
**Date:** [Insert Date]  
**Status:** Active  
**Applies To:** Identification, declaration, and management of dependencies for all modules.

### 13.1. Purpose

To systematically manage internal and external dependencies for modules, ensuring reproducibility, resolving conflicts, and facilitating packaging for distribution and reuse.

### 13.2. Dependency Principles

- **Explicitness:** All dependencies MUST be explicitly declared
- **Isolation:** Aim for modules with minimal, well-defined dependencies
- **Versioning:** Use explicit version constraints for dependencies
- **Auditability:** Dependency manifests must be version-controlled
- **Stability:** Prioritize stable versions for dependencies

### 13.3. Dependency Declaration Standard

**Requirement:** Each module that has dependencies MUST declare them in a standard manifest file.

**Format (Language/Project Specific):** Use standard tooling for the language/ecosystem:
- **Python:** requirements.txt, pyproject.toml (Poetry/PDM)
- **Node.js:** package.json
- **Java:** pom.xml (Maven), build.gradle (Gradle)
- **Go:** go.mod
- **Rust:** Cargo.toml
- **Generic:** A custom dependencies.yaml

**Content:** The manifest MUST specify:
- Dependency name (package, library, module)
- Version constraint (e.g., ==1.2.3, ~=1.2, >=1,<2)
- Scope (optional, e.g., dev, test, runtime)

**Location:** Standard location within module directory (checked by FMAS).

### 13.4. Versioning & Conflict Resolution

- **Pinning:** External dependencies SHOULD be pinned to specific versions for reproducibility
- **Range Strategy:** Project-level dependency management MAY use version ranges with robust conflict resolution
- **Internal Dependencies:** Internal dependencies MAY reference specific commit hashes or version tags

### 13.5. Workflow Integration

- **WSP 1:** Dependencies identified during planning, declared during refactoring
- **WSP 4:** FMAS checks for existence and basic format of dependency manifests
- **WSP 7:** Dependency manifests committed and versioned
- **WSP 8:** Dependency manifests included in regression checks

---

## WSP 14: Test Creation & Management Procedures

**Document Version:** 1.0  
**Date:** [Insert Date]  
**Status:** Active  
**Applies To:** Creation, organization, and management of test suites within module test directories.

### 14.1. Purpose

To establish standardized procedures for creating, organizing, and maintaining test suites that avoid duplication, follow WSP guidelines, and ensure comprehensive coverage of module functionality. Testing rigor should be influenced by the module's LLME score.

### 14.2. Test Creation Workflow

#### 14.2.1. Pre-Creation Analysis (MANDATORY)

Before creating or modifying tests:

1. **Review Module's LLME Score:** Understand the module's current state, local impact, and systemic importance
2. **Read Existing Tests README:** Examine `modules/<module_name>/tests/README.md` to understand current test structure
3. **Identify Coverage Gaps:** Analyze existing test files to determine what needs additional coverage
4. **Check for Duplicate Functionality:** Search existing tests for similar patterns

#### 14.2.2. Test File Creation Guidelines

**File Naming Convention:**
- `test_<specific_functionality>.py` (e.g., `test_circuit_breaker.py`)
- Avoid generic names like `test_module.py` if specific functionality tests exist
- Use descriptive names that clearly indicate the test focus

**Test Structure Requirements:**
- Follow established patterns from existing test files in the module
- Include comprehensive docstrings explaining test purpose
- Organize tests into logical test classes
- Include integration tests where appropriate

**WSP Compliance Headers:**
```python
"""
WSP: [Test Module Name]
======================

Tests for [specific functionality] in the [Module Name] module.
Module LLME: [Current ABC] - Target LLME: [Target ABC]
[Brief description of test coverage, considering LLME aspects]

WSP Compliance:
- Tests placed in correct module location: modules/<module>/tests/
- Follows established test patterns from existing test files
- Tests [functionality] in isolation and integration
- Test scope and rigor aligned with module LLME
"""
```

#### 14.2.3. Test Documentation Requirements

**README.md Updates (MANDATORY):**
After creating or significantly modifying tests, update `modules/<module>/tests/README.md`:

1. Add new test file to the test files table
2. Document test purpose and coverage area
3. Update any changed testing patterns or procedures
4. Note any special setup or execution requirements

### 14.3. Test Management Guidelines

#### 14.3.1. Extending vs. Creating Tests

**Prefer Extension When:**
- New tests logically fit within existing test class structure
- Testing related functionality to existing tests
- Can reuse existing test setup and teardown procedures
- Maintains test organization and readability

**Create New When:**
- Testing entirely different functionality or component
- Requires significantly different test setup or mocking
- Existing test files are becoming too large or complex
- Testing cross-cutting concerns that span multiple components

#### 14.3.2. Test Coverage Strategy

**Coverage Targets (WSP 5):**
- Minimum 90% line coverage for all modules
- Higher coverage requirements for modules with high LLME scores
- Focus on critical paths, error handling, and edge cases

**Coverage Analysis Commands:**
```bash
# Single module coverage
pytest modules/<domain>/<module>/tests/ --cov=modules.<domain>.<module>.src --cov-report=term-missing

# Full system coverage
pytest modules/ --cov=modules --cov-report=html
```

### 14.4. Workflow Integration

- **WSP 1:** Test structure planned during module refactoring
- **WSP 4:** FMAS validates test file existence and structure
- **WSP 5:** Coverage targets enforced through test audit
- **WSP 6:** Tests executed as part of comprehensive test audit
- **WSP 7:** Test files committed with appropriate documentation

---

*This WSP Framework provides the execution logic and lifecycle flows necessary for implementing the modular "Code LEGO" architecture while maintaining quality, consistency, and scalability across the FoundUps ecosystem.*