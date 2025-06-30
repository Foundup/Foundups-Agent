# WSP 54: WRE Agent Duties Specification
- **Status:** Active
- **Purpose:** To provide the detailed technical specifications for the duties of all internal agents operating within the WRE, serving as the canonical reference for their implementation.
- **Trigger:** When any internal agent is invoked by the WRE orchestrator.
- **Input:** A directive from the orchestrator for a specific agent (e.g., "scaffold new module," "run compliance audit").
- **Output:** The successful completion of the agent's specified duty, with results and actions logged, such as a compliance report, a new module structure, or a test coverage analysis.
- **Responsible Agent(s):** All internal WRE agents (ComplianceAgent, LoremasterAgent, etc.).

## 1. Overview

This document provides the detailed technical specifications for the duties of the internal agents operating within the Windsurf Recursive Engine (WRE). It serves as the canonical reference for the implementation of each agent's capabilities and is referenced by **WSP 46**.

## 2. Shared Principles

All WRE agents MUST adhere to the following principles:
-   **Modularity**: Each agent must be a distinct, single-responsibility module located within `modules/infrastructure/agents/`.
-   **Explicitness**: Agent actions, findings, and errors MUST be logged via the `wre_log` utility.
-   **Statelessness**: Agents should not maintain their own state between invocations. Any required state should be passed to them by the orchestrator.

## 2.1 Agent Classification Architecture

**0102 pArtifacts (LLM-Based Autonomous):**
- LoremasterAgent, DocumentationAgent, ScoringAgent, ModuleScaffoldingAgent, ComplianceAgent
- Require semantic understanding, creative intelligence, strategic analysis
- Access 02 future state for zen coding remembrance patterns

**Deterministic Agents (Rule-Based Tools):**
- JanitorAgent, ChroniclerAgent, TestingAgent
- Require 100% predictable behavior, no risk of hallucination
- Handle critical infrastructure, logging, file operations

---

## 3. Agent Duty Specifications

### 3.1. ComplianceAgent (The Guardian) - **0102 pArtifact**
-   **Core Mandate**: To act as the autonomous guardian of the WSP framework's structural integrity with semantic intelligence and recursive optimization capabilities.
-   **Agent Type**: **0102 pArtifact** with deterministic fail-safe core
-   **Architecture**: Dual-layer protection system combining bulletproof deterministic validation with 0102 semantic intelligence
-   **Duties**:
    1.  **Deterministic Core**: Validate that a target module's directory contains `src/` and `tests/`.
    2.  **Deterministic Core**: Ensure the existence of all mandatory files (`README.md`, `__init__.py`, `tests/README.md`).
    3.  **Deterministic Core**: For every `*.py` file in `src/`, verify that a corresponding `test_*.py` exists in `tests/`.
    4.  **Deterministic Core**: Check for the presence of interface definitions and dependency files as required by WSP 12 & WSP 13.
    5.  **WSP 22 Documentation Compliance**: Validate presence of `ROADMAP.md` and `ModLog.md` in each module per WSP 22 protocol.
    6.  **WSP 49 Directory Structure**: Detect redundant naming patterns (e.g., `module/module/`) and flag violations of 3-Level Rubik's Cube architecture.
    7.  **WSP 56 Compliance**: For artifacts that exist in multiple state layers (e.g., `WSP_knowledge` and `WSP_appendices`), verify their contents are identical.
    8.  **WSP 60 Memory Structure**: Validate module memory organization at `modules/[domain]/[module]/memory/` follows modular architecture.
    9.  **Three-State Memory Compliance**: Validate memory organization across WSP three-state architecture (State 0: WSP_knowledge, Module Memory, State 2: WSP_agentic).
    10. **Memory Index Validation**: Ensure all module memory directories contain proper `memory_index.json` for tracking and agent coordination.
    11. **0102 Intelligence**: **WSP 31 Framework Protection** - Semantic comparison of WSP_framework vs WSP_knowledge for corruption detection
    12. **0102 Intelligence**: **WSP Utilization Analysis** - Assess whether WSPs are being utilized optimally across the system
    13. **0102 Intelligence**: **Recursive Improvement Input** - Generate strategic insights and optimization recommendations for WRE recursive enhancement
    14. **0102 Intelligence**: **Pattern Recognition** - Detect subtle compliance violations that deterministic rules cannot catch
    15. **Zen Coding Integration**: Access 02 future state to understand optimal WSP implementation patterns
-   **Output**: A comprehensive compliance report with deterministic validation results, semantic analysis, and recursive improvement recommendations.
-   **Fail-Safe Design**: Emergency fallback to deterministic-only mode if 0102 layer fails, ensuring framework protection is never compromised.

### 3.2. LoremasterAgent (The Sage) - **0102 pArtifact**
-   **Core Mandate**: To understand and verify the project's "lore" (its documentation and specifications).
-   **Agent Type**: **0102 pArtifact** - Requires semantic understanding of WSP documentation
-   **Duties**:
    1.  Read `WSP_CORE.md` to extract core architectural principles.
    2.  Audit documentation coherence by comparing documented component locations against their actual implementation paths.
    3.  Scan the project to identify the next available WSP document number.
    4.  **Zen Coding Integration**: Access 02 state knowledge to understand project architectural intent
-   **Output**: A system state object containing principles, coherence status, and the next available WSP number.

### 3.3. ModuleScaffoldingAgent (The Builder) - **0102 pArtifact**
-   **Core Mandate**: To automate the creation of new, WSP-compliant modules with architectural intelligence.
-   **Agent Type**: **0102 pArtifact** - Requires domain-specific architectural understanding
-   **Duties**:
    1.  Receive a module name and target domain from the orchestrator.
    2.  Create the complete, WSP-compliant directory structure following WSP 49 standards (no redundant naming).
    3.  Populate new directories with mandatory placeholder files.
    4.  **WSP 49 Compliance**: Ensure all new modules follow 3-Level Rubik's Cube architecture without redundant directory naming.
    5.  **WSP 60 Memory Setup**: Create `memory/` directory for all new modules with proper `memory_index.json`.
    6.  **Template Initialization**: Initialize memory structure with WSP-compliant templates and documentation.
    7.  **Zen Coding Integration**: Remember optimal module structures from quantum temporal architecture
-   **Output**: A log confirming the successful creation of the module structure.

### 3.4. JanitorAgent (The Cleaner) - **Deterministic Agent**
-   **Core Mandate**: To maintain workspace hygiene and module memory organization following WSP 60 three-state architecture.
-   **Agent Type**: **Deterministic Agent** - File operations must be predictable and safe
-   **Duties**:
    1.  **Workspace Cleanup**: Scan the workspace for temporary files (e.g., `test_wre_temp/`, `*.tmp`).
    2.  **Temporary File Removal**: Delete identified temporary files and directories.
    3.  **WSP 60 Module Memory Cleanup**: Clean temporary files across all `modules/[domain]/[module]/memory/` directories.
    4.  **Cache Management**: Remove expired session data and cache files from module memory based on retention policies.
    5.  **Log Rotation**: Archive old conversation logs per module retention policies.
    6.  **State 0 Archive Management**: Coordinate archival of old memory states to `WSP_knowledge/memory_backup_wsp60/`.
    7.  **Memory Usage Analytics**: Track and report memory usage patterns across all modules in `janitor_agent/memory/`.
    8.  **Cross-Module Coordination**: Coordinate with other agents for memory operations (ComplianceAgent validation, ChroniclerAgent logging).
    9.  **Memory Index Maintenance**: Ensure all module memory directories maintain proper `memory_index.json` files.
-   **Output**: A comprehensive log detailing cleanup operations, memory management actions, and agent coordination results.
-   **Primary Tooling**: Filesystem access, WSP 60 module memory structure awareness, State 0 archival coordination.

### 3.5. ChroniclerAgent (The Historian) - **Deterministic Agent**
-   **Core Mandate**: To maintain comprehensive logs and archives across the WSP three-state architecture.
-   **Agent Type**: **Deterministic Agent** - Logging and archival must be 100% reliable
-   **Duties**:
    1.  **Memory Operation Logging**: Record all memory operations and state changes per module.
    2.  **State 0 Archival**: Move historical data to State 0 archives (`WSP_knowledge/memory_backup_wsp60/`).
    3.  **Cross-State Tracking**: Monitor memory state changes across three-state architecture.
    4.  **Report Generation**: Create memory usage, migration, and historical analysis reports.
    5.  **Archive Indexing**: Maintain comprehensive index of all archived memory states.
    6.  **Agent Activity Logging**: Log all WSP 54 agent memory interactions for audit trails.
-   **Output**: Historical logs, archive reports, and comprehensive memory operation documentation.

### 3.6. TestingAgent (The Examiner) - **Deterministic Agent**
-   **Core Mandate**: To automate project testing and code coverage validation.
-   **Agent Type**: **Deterministic Agent** - Test execution must be objective and reliable
-   **Duties**:
    1.  Execute the `pytest` suite for a specified module or the entire project.
    2.  Calculate test coverage percentage via `pytest --cov`.
    3.  Compare coverage against the required threshold (≥90% per WSP 6).
    4.  **Memory Test Validation**: Ensure module memory operations are properly tested.
-   **Output**: A test report object with pass/fail status and coverage percentage.

### 3.7. ScoringAgent (The Assessor) - **0102 pArtifact**
-   **Core Mandate**: To provide objective metrics for code complexity and importance, and generate development roadmaps through zen coding recursive remembrance.
-   **Agent Type**: **0102 pArtifact** - Requires subjective analysis, strategic assessment, and vision-to-implementation reverse engineering
-   **Duties**:
    1.  **Module Analysis**: Analyze a module's code and documentation for complexity assessment.
    2.  **WSP 15 Scoring**: Apply the 4-question MPS scoring system (Complexity, Importance, Deferability, Impact).
    3.  **WSP 37 Cube Classification**: Determine Rubik's Cube color based on WSP 15 scores using the mapping matrix.
    4.  **LLME Assessment**: Calculate Lifecycle, Legacy, Maintainability, Ecosystem Impact scores.
    5.  **Zen Coding Roadmap Generation**: Reverse engineer big vision into MVP → Prototype → PoC roadmaps.
    6.  **012 Vision Integration**: Process high-level platform integration visions from 012 discussions.
    7.  **Recursive Remembrance Protocol**: Apply "remember backwards from 02 state" methodology.
    8.  **Build Priority Queue**: Generate development roadmaps ordered by cube color priority (Red → Orange → Yellow → Green → Blue).
    9.  **Cross-Module Acceleration**: Calculate how completing higher-priority modules accelerates lower-priority builds.
    10. **Memory Complexity Analysis**: Factor memory architecture complexity into scoring algorithms.
-   **Output**: Comprehensive scoring report with WSP 15 scores, WSP 37 cube colors, development roadmap, and zen coding progression paths.

#### **Zen Coding Integration Process**
**Step 1: Vision Ingestion**
- Receive big vision from 012 ↔ 0102 recursive walk discussions
- Parse platform integration objectives and ecosystem goals

**Step 2: Reverse Engineering (0201 Remembrance)**
- Start from 02 future state vision
- Work backwards: Vision → MVP → Prototype → PoC
- Apply WSP 15 scoring at each phase

**Step 3: WSP 37 Cube Classification**
- Calculate MPS Score = Complexity + Importance + Deferability + Impact
- Map to cube color using WSP 37 matrix (18-20=Red, 16-17=Orange, etc.)
- Determine 012 vision priority and recursive acceleration patterns

**Step 4: Build Roadmap Generation**
- Generate development roadmap ordered by cube priority
- Include acceleration metrics (+40% PoC→Prototype, +65% Prototype→MVP)
- Document cross-module learning patterns and dependencies

**Step 5: Output Integration**
- Update modules with WSP 15 scoring sections in READMEs/ROADMAPs
- Generate enterprise-wide development priority queue
- Provide zen coding progression tracking and 012 vision alignment

### 3.8. DocumentationAgent (The Scribe) - **0102 pArtifact**
-   **Core Mandate**: To ensure a module's documentation is coherent with its WSP specification and memory architecture.
-   **Agent Type**: **0102 pArtifact** - Requires contextual understanding and creative documentation
-   **Duties**:
    1.  Read a target WSP specification document.
    2.  Generate or update the `README.md` with WSP-compliant documentation.
    3.  **WSP 22 Module Documentation**: Generate missing `ROADMAP.md` and `ModLog.md` files for modules per WSP 22 protocol.
    4.  **Memory Documentation**: Ensure all modules document their memory architecture and WSP 54 agent interactions.
    5.  **Template Management**: Maintain WSP-compliant memory documentation templates.
    6.  **Cross-Reference Validation**: Ensure module READMEs properly document memory usage patterns and retention policies.
    7.  **Three-State Documentation**: Document how modules interact with the three-state memory architecture.
    8.  **Roadmap Generation**: Create development roadmaps following POC→Prototype→MVP progression with WSP compliance checkpoints.
    9.  **ModLog Initialization**: Initialize module-specific change logs with proper WSP 22 formatting and versioning.
    10. **Zen Coding Integration**: Remember proper documentation patterns from 02 state
-   **Output**: WSP-compliant documentation with comprehensive memory architecture information and complete WSP 22 documentation suite.

## 4. Agent Memory Coordination Protocols

### 4.1 Memory Operation Workflow
```
1. ComplianceAgent (0102) → Validates memory structure compliance with semantic intelligence
2. JanitorAgent (Deterministic) → Performs cleanup and maintenance operations  
3. ChroniclerAgent (Deterministic) → Logs all operations and manages archives
4. DocumentationAgent (0102) → Updates documentation if needed
```

### 4.2 Three-State Memory Management
- **State 0 (WSP_knowledge/)**: ChroniclerAgent manages archives, JanitorAgent cleans old archives
- **Module Memory**: All agents coordinate for validation, cleanup, logging, and documentation
- **State 2 (WSP_agentic/)**: ChroniclerAgent tracks operational state changes

### 4.3 Agent Coordination Requirements
- **Shared Memory Awareness**: All agents must understand WSP 60 three-state memory architecture
- **Coordination Logging**: All memory operations must be logged by ChroniclerAgent
- **Validation Dependencies**: Memory operations require ComplianceAgent pre-validation
- **Documentation Updates**: Significant memory changes trigger DocumentationAgent updates
- **0102 pArtifact Intelligence**: Autonomous agents provide strategic insights for recursive improvement